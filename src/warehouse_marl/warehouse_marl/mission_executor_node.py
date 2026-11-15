"""Execute warehouse task assignments through each robot's Nav2 action.

The allocation layer intentionally decides *who* should perform a task.  This
node is the missing physical bridge: it resolves the logical graph target to a
safe map-frame pose, queues one mission per robot, sends NavigateToPose goals,
and publishes lifecycle status used to release allocator capacity.
"""

from collections import deque
import math
from dataclasses import dataclass
import json
from typing import Deque, Dict, Optional

import rclpy
from action_msgs.msg import GoalStatus, GoalStatusArray
from action_msgs.srv import CancelGoal
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import FollowWaypoints, NavigateToPose
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Bool, String

from warehouse_marl.dynamic_blocking import (
    EdgeBlockManager, FailureTracker, access_edge, block_message, edge_key, parse_block_message)
from warehouse_marl.route_planner import plan_route, route_to_waypoints
from warehouse_marl.warehouse_graph import build_demo_warehouse


@dataclass
class Mission:
    task_id: str
    robot_id: str
    target_node: str
    created_at: Optional[float] = None
    retries: int = 0


class MissionExecutorNode(Node):

    def __init__(self):
        super().__init__('mission_executor_node')

        self.declare_parameter('robot_names', ['robot1', 'robot2'])
        self.declare_parameter('map_origin_x', -1.5)
        self.declare_parameter('map_origin_y', -1.0)
        self.declare_parameter('dispatch_period_sec', 0.25)
        self.declare_parameter('max_retries', 1)
        self.declare_parameter('pause_exploration', True)
        # Claims for one task are collected this long before dispatching the
        # best one (cost, then robot_id), the same rule consensus_node uses.
        self.declare_parameter('claim_window_sec', 0.5)
        # Graphe dynamique : apres N echecs Nav2 sur la meme cible, l'arete
        # d'acces a cette cible est annoncee bloquee pendant block_duration_sec
        # sur /warehouse/blocked_edges (0 = desactive).
        self.declare_parameter('block_after_failures', 2)
        self.declare_parameter('block_duration_sec', 60.0)
        self.declare_parameter('failure_window_sec', 300.0)
        # Routage (protocole v4, etape 3) :
        #   direct   : un seul NavigateToPose vers la cible (comportement historique) ;
        #   dijkstra : route du graphe dynamique -> points de passage FollowWaypoints ;
        #   drl      : route deroulee par la politique drl_route (route_model .pt).
        self.declare_parameter('route_mode', 'direct')
        self.declare_parameter('route_model', '')
        self.declare_parameter('robot_start_nodes', [''])
        self.declare_parameter('robot_speed', 0.5)
        # Point d'attente d'un robot inoccupe (protocole v4, drl_idle, en ROS) :
        #   stay   : reste sur place (comportement historique) ;
        #   centre : centre_de_demande (demande observee en ligne, Laplace +1) ;
        #   drl    : politique drl_idle (idle_model .pt).
        # Le trajet vers le point d'attente est un NavigateToPose, annule des
        # qu'une mission arrive pour ce robot (il reste attribuable).
        self.declare_parameter('idle_mode', 'stay')
        self.declare_parameter('idle_model', '')

        self.robot_names = list(self.get_parameter('robot_names').value)
        self.max_retries = int(self.get_parameter('max_retries').value)
        self.pause_exploration = bool(
            self.get_parameter('pause_exploration').value)
        self.graph = build_demo_warehouse(
            float(self.get_parameter('map_origin_x').value),
            float(self.get_parameter('map_origin_y').value),
        )

        self.route_mode = str(self.get_parameter('route_mode').value)
        if self.route_mode not in ('direct', 'dijkstra', 'drl'):
            raise ValueError(f'route_mode inconnu : {self.route_mode}')
        self.robot_speed = float(self.get_parameter('robot_speed').value)
        self.route_agent = None
        if self.route_mode == 'drl':
            from warehouse_marl.drl.v4_dqn import load_v4_model
            model = str(self.get_parameter('route_model').value)
            self.route_agent = load_v4_model(model, 'route')
            self.get_logger().info(f'Politique drl_route chargee : {model}')
        self.idle_mode = str(self.get_parameter('idle_mode').value)
        if self.idle_mode not in ('stay', 'centre', 'drl'):
            raise ValueError(f'idle_mode inconnu : {self.idle_mode}')
        self.idle_agent = None
        if self.idle_mode == 'drl':
            from warehouse_marl.drl.v4_dqn import load_v4_model
            model = str(self.get_parameter('idle_model').value)
            self.idle_agent = load_v4_model(model, 'idle')
            self.get_logger().info(f'Politique drl_idle chargee : {model}')
        self._demand_counts: Dict[str, int] = {}
        self._park_target = {robot: None for robot in self.robot_names}
        self._park_handle = {robot: None for robot in self.robot_names}
        self._park_cancel_sent = {robot: False for robot in self.robot_names}
        self._need_idle = {robot: False for robot in self.robot_names}
        self.idle_pub = self.create_publisher(String, '/warehouse/idle_points', 10)
        starts = [s for s in self.get_parameter('robot_start_nodes').value if s]
        self._robot_node = {
            robot: (starts[i] if i < len(starts) else 'charging_dock')
            for i, robot in enumerate(self.robot_names)}
        self.blocks = EdgeBlockManager(self.graph)
        self._block_since: Dict[tuple, float] = {}
        self._wp_clients = {}
        if self.route_mode != 'direct':
            self._wp_clients = {
                robot: ActionClient(self, FollowWaypoints, f'/{robot}/follow_waypoints')
                for robot in self.robot_names}
            self.create_subscription(
                String, '/warehouse/blocked_edges', self._on_blocked_edge, 10)
        self.route_pub = self.create_publisher(String, '/warehouse/routes', 10)

        # Avoid rclpy.Node's internal ``_clients`` attribute.
        self._nav_clients = {
            robot: ActionClient(
                self, NavigateToPose, f'/{robot}/navigate_to_pose')
            for robot in self.robot_names
        }
        self._queues: Dict[str, Deque[Mission]] = {
            robot: deque() for robot in self.robot_names
        }
        self._active: Dict[str, Optional[Mission]] = {
            robot: None for robot in self.robot_names
        }
        # Goals another client (frontier exploration) is running on each robot.
        # Nav2 refuses to preempt a goal that uses a different behavior tree,
        # so a mission is only sent once the robot is idle (see _dispatch).
        self._cancel_clients = {
            robot: self.create_client(
                CancelGoal, f'/{robot}/navigate_to_pose/_action/cancel_goal')
            for robot in self.robot_names
        }
        self._nav_busy = {robot: False for robot in self.robot_names}
        self._cancel_sent = {robot: False for robot in self.robot_names}
        status_qos = QoSProfile(
            depth=1,
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL)
        for robot in self.robot_names:
            self.create_subscription(
                GoalStatusArray, f'/{robot}/navigate_to_pose/_action/status',
                lambda msg, r=robot: self._on_nav_status(r, msg), status_qos)
        self._task_metadata = {}
        self._claimed_tasks = set()
        self.claim_window = float(self.get_parameter('claim_window_sec').value)
        self._pending_claims: Dict[str, dict] = {}
        self._last_server_warning = {robot: -float('inf') for robot in self.robot_names}
        self._missions_active = None

        self.create_subscription(
            String, '/warehouse/tasks/new', self._on_new_task, 10)
        self.create_subscription(
            String, '/warehouse/consensus/assignments', self._on_assignment, 10)
        self.create_subscription(
            String, '/warehouse/tasks/direct_assignment', self._on_assignment, 10)
        self.status_pub = self.create_publisher(
            String, '/warehouse/tasks/status', 10)
        self.block_after = int(self.get_parameter('block_after_failures').value)
        self.block_duration = float(self.get_parameter('block_duration_sec').value)
        self.failures = FailureTracker(
            self.block_after, float(self.get_parameter('failure_window_sec').value))
        self.block_pub = self.create_publisher(String, '/warehouse/blocked_edges', 10)

        state_qos = QoSProfile(depth=1)
        state_qos.reliability = ReliabilityPolicy.RELIABLE
        state_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.mission_state_pub = self.create_publisher(
            Bool, '/warehouse/missions_active', state_qos)
        self._publish_mission_state(force=True)

        self.create_timer(
            float(self.get_parameter('dispatch_period_sec').value),
            self._dispatch)
        self.get_logger().info(
            f'MissionExecutorNode pret pour {self.robot_names}; '
            f'cibles Nav2 dans frame map.')

    def _now(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def _on_blocked_edge(self, msg: String):
        try:
            data = parse_block_message(msg.data)
        except ValueError as exc:
            self.get_logger().warn(f'/warehouse/blocked_edges ignore : {exc}')
            return
        now = self._now()
        self.blocks.apply(data, now)
        key = edge_key(data['u'], data['v'])
        if data['blocked']:
            self._block_since.setdefault(key, now)
        else:
            self._block_since.pop(key, None)

    def _plan(self, robot_id: str, target: str):
        """Route du graphe (liste de noeuds) pour route_mode dijkstra|drl."""
        now = self._now()
        for key in self.blocks.expire(now):
            self._block_since.pop(key, None)
        elapsed = {k: now - t0 for k, t0 in self._block_since.items()}
        start = self._robot_node[robot_id]
        return plan_route(self.graph, start, target,
                          'drl' if self.route_mode == 'drl' else 'dijkstra',
                          agent=self.route_agent, speed=self.robot_speed,
                          block_elapsed=elapsed)

    def _waypoint_goal(self, route):
        goal = FollowWaypoints.Goal()
        stamp = self.get_clock().now().to_msg()
        last = self.graph.G.nodes[route[-1]]
        points = route_to_waypoints(self.graph, route) or [(last['x'], last['y'], 0.0)]
        for x, y, yaw in points:
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.header.stamp = stamp
            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)
            pose.pose.orientation.z = math.sin(yaw / 2.0)
            pose.pose.orientation.w = math.cos(yaw / 2.0)
            goal.poses.append(pose)
        return goal

    def _on_new_task(self, msg: String):
        try:
            data = json.loads(msg.data)
            self._task_metadata[data['task_id']] = data
            target = data.get('target_node')
            if target in self.graph.G:      # demande observee (idle_mode centre|drl)
                self._demand_counts[target] = self._demand_counts.get(target, 0) + 1
        except (json.JSONDecodeError, KeyError):
            self.get_logger().warn('Tache JSON mal formee; ignoree.')

    def _on_assignment(self, msg: String):
        try:
            data = json.loads(msg.data)
            task_id = str(data['task_id'])
            robot_id = str(data['robot_id'])
            target_node = str(data['target_node'])
        except (json.JSONDecodeError, KeyError):
            self.get_logger().warn('Assignation JSON mal formee; ignoree.')
            return

        if task_id in self._claimed_tasks:
            return
        if robot_id not in self._queues:
            self.get_logger().error(
                f'Assignation {task_id}: robot inconnu {robot_id!r}.')
            return
        if target_node not in self.graph.G:
            self.get_logger().error(
                f'Assignation {task_id}: cible inconnue {target_node!r}.')
            self._emit_status_fields(
                task_id, robot_id, target_node, 'rejected',
                detail='unknown target node')
            return

        try:
            cost = float(data.get('cost', 0.0))
        except (TypeError, ValueError):
            cost = 0.0
        pending = self._pending_claims.setdefault(
            task_id, {'first': self._now(), 'claims': {}})
        pending['claims'][robot_id] = (cost, target_node)

    def _resolve_claims(self):
        """Dispatch each task to its best claim once the claim window has
        passed, so simultaneous claims from late auctions cannot send two
        robots (or the wrong one) to the same task."""
        now = self._now()
        for task_id, pending in list(self._pending_claims.items()):
            if now - pending['first'] < self.claim_window:
                continue
            del self._pending_claims[task_id]
            claims = pending['claims']
            robot_id = min(claims, key=lambda r: (claims[r][0], r))
            if len(claims) > 1:
                self.get_logger().info(
                    f'{task_id}: {len(claims)} revendications, retenu {robot_id}.')
            self._queue_mission(task_id, robot_id, claims[robot_id][1])

    def _queue_mission(self, task_id: str, robot_id: str, target_node: str):
        metadata = self._task_metadata.get(task_id, {})
        mission = Mission(
            task_id=task_id,
            robot_id=robot_id,
            target_node=target_node,
            created_at=metadata.get('created_at'),
        )
        self._claimed_tasks.add(task_id)
        self._queues[robot_id].append(mission)
        self._emit_status(mission, 'queued')
        self._publish_mission_state()
        self.get_logger().info(
            f'{task_id} en file pour {robot_id} -> {target_node}.')

    def _on_nav_status(self, robot_id: str, msg: GoalStatusArray):
        busy_states = (GoalStatus.STATUS_ACCEPTED, GoalStatus.STATUS_EXECUTING,
                       GoalStatus.STATUS_CANCELING)
        self._nav_busy[robot_id] = any(s.status in busy_states for s in msg.status_list)
        if not self._nav_busy[robot_id]:
            self._cancel_sent[robot_id] = False

    # ----- point d'attente (idle_mode) ------------------------------------ #
    def _is_idle(self, robot_id: str) -> bool:
        return self._active[robot_id] is None and not self._queues[robot_id]

    def _park(self, robot_id: str):
        """Decision d'attente d'un robot qui vient de devenir inoccupe, puis
        NavigateToPose vers le noeud choisi (rien si c'est sa position)."""
        from warehouse_marl.idle_planner import choose_idle_point
        robots = {r: {'node': self._robot_node[r], 'park': self._park_target[r],
                      'idle': self._is_idle(r)} for r in self.robot_names}
        n_open = len(self._pending_claims) + sum(len(q) for q in self._queues.values())
        park, info = choose_idle_point(
            self.graph, robot_id, robots, self.idle_mode, agent=self.idle_agent,
            speed=self.robot_speed, demand_counts=self._demand_counts, n_open=n_open)
        info.update({'robot_id': robot_id, 'depuis': self._robot_node[robot_id]})
        self.idle_pub.publish(String(data=json.dumps(info)))
        self.get_logger().info(
            f'{robot_id} inoccupe en {self._robot_node[robot_id]} : attente '
            f'{self.idle_mode} -> {park}.')
        if park == self._robot_node[robot_id]:
            return
        client = self._nav_clients[robot_id]
        if not client.server_is_ready():
            self.get_logger().warn(f'{robot_id}: navigate_to_pose absent, reste sur place.')
            return
        node = self.graph.G.nodes[park]
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = float(node['x'])
        goal.pose.pose.position.y = float(node['y'])
        goal.pose.pose.orientation.w = 1.0
        self._park_target[robot_id] = park
        self._park_handle[robot_id] = 'en_attente'      # reponse du serveur pas encore recue
        self._park_cancel_sent[robot_id] = False
        future = client.send_goal_async(goal)
        future.add_done_callback(lambda f, r=robot_id, p=park: self._on_park_response(f, r, p))
        self._publish_mission_state()

    def _on_park_response(self, future, robot_id: str, park: str):
        try:
            handle = future.result()
        except Exception as exc:
            self.get_logger().warn(f'{robot_id}: envoi vers {park} en erreur : {exc}')
            handle = None
        if handle is None or not handle.accepted:
            self._park_handle[robot_id] = None
            self._publish_mission_state()
            return
        self._park_handle[robot_id] = handle
        handle.get_result_async().add_done_callback(
            lambda f, r=robot_id, p=park: self._on_park_result(f, r, p))

    def _on_park_result(self, future, robot_id: str, park: str):
        try:
            status = int(future.result().status)
        except Exception:
            status = GoalStatus.STATUS_UNKNOWN
        self._park_handle[robot_id] = None
        if status == GoalStatus.STATUS_SUCCEEDED:
            self._robot_node[robot_id] = park
            self.get_logger().info(f'{robot_id} arrive au point d attente {park}.')
        else:
            # Interrompu (mission arrivee) : la position reste le dernier noeud
            # atteint ; limite connue, le robot est quelque part sur le trajet.
            self.get_logger().info(f'{robot_id}: trajet vers {park} interrompu (statut {status}).')
        self._publish_mission_state()

    def _dispatch(self):
        self._resolve_claims()
        if self.idle_mode != 'stay':
            for robot_id in self.robot_names:
                if self._need_idle[robot_id] and self._is_idle(robot_id):
                    self._need_idle[robot_id] = False
                    self._park(robot_id)
        for robot_id in self.robot_names:
            if self._active[robot_id] is not None or not self._queues[robot_id]:
                continue
            if self._park_handle[robot_id] is not None:
                # Mission arrivee pendant le trajet d'attente : on l'annule et
                # on attend la fin de l'annulation avant d'envoyer la mission.
                handle = self._park_handle[robot_id]
                if not isinstance(handle, str) and not self._park_cancel_sent[robot_id]:
                    handle.cancel_goal_async()
                    self._park_cancel_sent[robot_id] = True
                    self.get_logger().info(
                        f'{robot_id}: annule le trajet d attente pour la mission.')
                continue
            client = (self._wp_clients[robot_id] if self.route_mode != 'direct'
                      else self._nav_clients[robot_id])
            if not client.server_is_ready():
                now = self._now()
                if now - self._last_server_warning[robot_id] >= 10.0:
                    action = ('follow_waypoints' if self.route_mode != 'direct'
                              else 'navigate_to_pose')
                    self.get_logger().warn(f'Attend /{robot_id}/{action}.')
                    self._last_server_warning[robot_id] = now
                continue

            if self._nav_busy[robot_id]:
                # An exploration goal is still running: cancel every goal on
                # this robot once, then wait until Nav2 reports it idle.
                if not self._cancel_sent[robot_id] and \
                        self._cancel_clients[robot_id].service_is_ready():
                    self._cancel_clients[robot_id].call_async(CancelGoal.Request())
                    self._cancel_sent[robot_id] = True
                    self.get_logger().info(
                        f'{robot_id}: annule l objectif en cours avant la mission.')
                continue

            mission = self._queues[robot_id].popleft()
            self._active[robot_id] = mission
            node = self.graph.G.nodes[mission.target_node]
            if self.route_mode != 'direct':
                route = self._plan(robot_id, mission.target_node)
                if len(route) < 2 and route != [mission.target_node]:
                    self.get_logger().warn(
                        f'{mission.task_id}: aucune route de '
                        f'{self._robot_node[robot_id]} a {mission.target_node}.')
                    self._finish_or_retry(mission, GoalStatus.STATUS_ABORTED)
                    continue
                if route == [mission.target_node]:
                    route = [mission.target_node, mission.target_node]
                self.route_pub.publish(String(data=json.dumps({
                    'task_id': mission.task_id, 'robot_id': robot_id,
                    'route_mode': self.route_mode, 'route': route})))
                self.get_logger().info(
                    f'{mission.task_id}: route {self.route_mode} {" -> ".join(route)}')
                future = client.send_goal_async(self._waypoint_goal(route))
                future.add_done_callback(
                    lambda result, item=mission: self._on_goal_response(result, item))
                continue
            goal = NavigateToPose.Goal()
            goal.pose = PoseStamped()
            goal.pose.header.frame_id = 'map'
            goal.pose.header.stamp = self.get_clock().now().to_msg()
            goal.pose.pose.position.x = float(node['x'])
            goal.pose.pose.position.y = float(node['y'])
            goal.pose.pose.orientation.w = 1.0

            future = client.send_goal_async(goal)
            future.add_done_callback(
                lambda result, item=mission: self._on_goal_response(result, item))

    def _on_goal_response(self, future, mission: Mission):
        try:
            handle = future.result()
        except Exception as exc:
            self.get_logger().error(
                f'{mission.task_id}: erreur envoi Nav2: {exc}')
            self._finish_or_retry(mission, GoalStatus.STATUS_UNKNOWN)
            return

        if not handle.accepted:
            self.get_logger().warn(
                f'{mission.task_id}: objectif refuse par {mission.robot_id}.')
            self._finish(mission, 'rejected', GoalStatus.STATUS_UNKNOWN)
            return

        self._emit_status(mission, 'navigating')
        node = self.graph.G.nodes[mission.target_node]
        self.get_logger().info(
            f'{mission.robot_id} execute {mission.task_id} -> '
            f'({node["x"]:.2f}, {node["y"]:.2f}).')
        result = handle.get_result_async()
        result.add_done_callback(
            lambda response, item=mission: self._on_result(response, item))

    def _on_result(self, future, mission: Mission):
        try:
            status = int(future.result().status)
        except Exception as exc:
            self.get_logger().error(
                f'{mission.task_id}: resultat Nav2 indisponible: {exc}')
            status = GoalStatus.STATUS_UNKNOWN

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(
                f'{mission.robot_id} a termine {mission.task_id}.')
            self.failures.record_success(mission.target_node)
            self._robot_node[mission.robot_id] = mission.target_node
            self._finish(mission, 'succeeded', status)
        else:
            if status != GoalStatus.STATUS_CANCELED:
                self._note_failure(mission)
            self._finish_or_retry(mission, status)

    def _note_failure(self, mission: Mission):
        """Echecs repetes sur une cible -> blocage temporaire de son arete
        d'acces dans le graphe dynamique (graph_publisher_node)."""
        if self.block_after <= 0 or self.block_duration <= 0:
            return
        if not self.failures.record_failure(mission.target_node, self._now()):
            return
        edge = access_edge(self.graph, mission.target_node)
        if edge is None:
            return
        msg = String()
        msg.data = block_message(
            edge[0], edge[1], self.block_duration, 'mission_executor',
            f'{self.block_after} echecs Nav2 vers {mission.target_node}')
        self.block_pub.publish(msg)
        self.get_logger().warn(
            f'Arete d acces {edge[0]} <-> {edge[1]} annoncee bloquee '
            f'{self.block_duration:.0f} s ({self.block_after} echecs vers '
            f'{mission.target_node}).')

    def _finish_or_retry(self, mission: Mission, nav_status: int):
        if mission.retries < self.max_retries:
            mission.retries += 1
            self._active[mission.robot_id] = None
            self._queues[mission.robot_id].appendleft(mission)
            self._emit_status(
                mission, 'retrying', nav_status=nav_status,
                detail=f'retry {mission.retries}/{self.max_retries}')
            self.get_logger().warn(
                f'{mission.task_id} echoue (Nav2={nav_status}); '
                f'nouvel essai {mission.retries}/{self.max_retries}.')
            return

        state = ('canceled' if nav_status == GoalStatus.STATUS_CANCELED
                 else 'failed')
        self.get_logger().error(
            f'{mission.task_id} termine en echec (Nav2={nav_status}).')
        self._finish(mission, state, nav_status)

    def _finish(self, mission: Mission, state: str, nav_status: int):
        self._emit_status(mission, state, nav_status=nav_status)
        self._active[mission.robot_id] = None
        self._need_idle[mission.robot_id] = True     # decision d'attente si la file est vide
        self._task_metadata.pop(mission.task_id, None)
        self._publish_mission_state()

    def _emit_status(
        self,
        mission: Mission,
        state: str,
        nav_status: Optional[int] = None,
        detail: str = '',
    ):
        self._emit_status_fields(
            mission.task_id, mission.robot_id, mission.target_node, state,
            created_at=mission.created_at, retries=mission.retries,
            nav_status=nav_status, detail=detail)

    def _emit_status_fields(
        self,
        task_id: str,
        robot_id: str,
        target_node: str,
        state: str,
        created_at: Optional[float] = None,
        retries: int = 0,
        nav_status: Optional[int] = None,
        detail: str = '',
    ):
        now = self._now()
        payload = {
            'task_id': task_id,
            'robot_id': robot_id,
            'target_node': target_node,
            'state': state,
            'stamp': now,
            'retries': retries,
        }
        if created_at is not None:
            payload['created_at'] = created_at
            payload['elapsed_sec'] = max(0.0, now - float(created_at))
        if nav_status is not None:
            payload['nav_status'] = nav_status
        if detail:
            payload['detail'] = detail
        msg = String()
        msg.data = json.dumps(payload)
        self.status_pub.publish(msg)

    def _publish_mission_state(self, force: bool = False):
        active = any(self._queues.values()) or any(
            mission is not None for mission in self._active.values()) or any(
            h is not None for h in self._park_handle.values())
        if not self.pause_exploration:
            active = False
        if not force and active == self._missions_active:
            return
        self._missions_active = active
        msg = Bool()
        msg.data = active
        self.mission_state_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = MissionExecutorNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
