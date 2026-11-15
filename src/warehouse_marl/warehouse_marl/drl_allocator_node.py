"""
drl_allocator_node.py
-----------------------
Deploie la POLITIQUE DRL entrainee hors-ligne (drl/train_drl.py) dans la
boucle ROS2 temps-reel. Deux modes d'usage possibles (parametre 'mode') :

  - mode='direct'  : ce noeud agit comme un allocateur CENTRALISE qui
                      choisit lui-meme l'agent gagnant pour chaque tache
                      (via argmax des Q-values) et publie directement
                      l'assignation. Simple, mais reintroduit un point
                      unique de decision.

  - mode='hybrid'  : ce noeud NE DECIDE PAS ; il calcule les Q-values pour
                      la tache courante et publie un "biais" par tache sur
                      /warehouse/consensus/bid_bias, lu par CHAQUE
                      consensus_node.py (un par agent). La decision finale
                      reste prise de facon DISTRIBUEE par consensus, mais
                      orientee par ce que la politique apprise juge
                      favorable. C'est le mode recommande pour rester
                      fidele au sujet ("distributed... consensus-based").

Le modele attend l'observation definie dans drl/env.py : reconstruite ici
a partir de l'etat du graphe (/warehouse/graph_state) et de la charge de
chaque agent (suivie localement via les assignations de consensus).

Parametre 'obs_version' :
  - 'v1' (defaut) : comportement historique, observation drl/env.py et
                    modele DQNAgent (taille liee au nombre de robots) ;
  - 'v2'          : modele train_drl_v2 (Q par couple robot/tache,
                    drl/features_v2.py), valable pour toute taille de flotte.
                    En mode hybrid, le biais publie est calibre :
                    bias = -bias_weight * (Q - moyenne des Q) * echelle (m),
                    echelle = bias_scale_m, ou REWARD_NORM_S x vitesse du
                    modele si bias_scale_m <= 0.
"""

import json
import math
import os

import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from warehouse_marl.warehouse_graph import WarehouseGraph
from warehouse_marl.drl.dqn_agent import DQNAgent


class DRLAllocatorNode(Node):

    def __init__(self):
        super().__init__('drl_allocator_node')

        self.declare_parameter('robot_names', ['robot1', 'robot2', 'robot3'])
        self.declare_parameter('model_path', 'warehouse_dqn.pt')
        self.declare_parameter('mode', 'hybrid')  # 'hybrid' | 'direct'
        self.declare_parameter('max_active_tasks_per_agent', 3)
        self.declare_parameter('obs_version', 'v1')       # 'v1' | 'v2'
        self.declare_parameter('bias_weight', 1.0)        # v2 hybrid
        self.declare_parameter('bias_scale_m', 0.0)       # v2 : 0 = depuis le modele
        self.declare_parameter('k_candidates', 5)         # v2 : taches candidates

        self.robot_names = self.get_parameter('robot_names').value
        self.model_path = self.get_parameter('model_path').value
        self.mode = self.get_parameter('mode').value
        self.max_active = self.get_parameter('max_active_tasks_per_agent').value
        self.obs_version = str(self.get_parameter('obs_version').value)
        self.bias_weight = float(self.get_parameter('bias_weight').value)
        self.k_candidates = int(self.get_parameter('k_candidates').value)
        if self.obs_version not in ('v1', 'v2'):
            raise ValueError(f"obs_version doit valoir 'v1' ou 'v2', pas {self.obs_version!r}")
        self.open_tasks = {}   # v2 : task_id -> dict(id, target, priority, created)

        self.graph: WarehouseGraph = None
        self.agent_load = {name: 0 for name in self.robot_names}
        self.agent_node = {name: None for name in self.robot_names}

        self.model_loaded = os.path.isfile(self.model_path)
        if self.obs_version == 'v2':
            self.agent = None
            if self.model_loaded:
                from warehouse_marl.drl.features_v2 import bias_scale_from_meta
                from warehouse_marl.drl.pair_dqn import load_pair_model
                self.agent = load_pair_model(self.model_path)
                scale = float(self.get_parameter('bias_scale_m').value)
                self.bias_scale = scale if scale > 0 else bias_scale_from_meta(self.agent.meta)
                self.get_logger().info(
                    f"Modele DRL v2 charge depuis {self.model_path} "
                    f"(echelle du biais {self.bias_scale:.1f} m, poids {self.bias_weight})")
        else:
            obs_dim = len(self.robot_names) * 3 + 1
            self.agent = DQNAgent(obs_dim=obs_dim, n_actions=len(self.robot_names))
            if self.model_loaded:
                self.agent.load(self.model_path)
                self.get_logger().info(f"Modele DRL charge depuis {self.model_path}")

        if not self.model_loaded:
            message = (
                f"Modele {self.model_path} introuvable; aucun poids aleatoire "
                f"ne sera utilise. Entraine d abord via train_drl.")
            if self.mode == 'direct':
                raise FileNotFoundError(message)
            self.get_logger().warn(message + ' Consensus heuristique conserve.')

        self.create_subscription(
            String, '/warehouse/graph_state', self._on_graph_state, 10
        )
        self.create_subscription(
            String, '/warehouse/consensus/assignments', self._on_assignment, 10
        )
        self.create_subscription(
            String, '/warehouse/tasks/direct_assignment', self._on_assignment, 10
        )
        self.create_subscription(
            String, '/warehouse/tasks/status', self._on_task_status, 10
        )
        self.create_subscription(
            String, '/warehouse/tasks/new', self._on_new_task, 10
        )

        self.bias_pub = self.create_publisher(
            String, '/warehouse/consensus/bid_bias', 10
        )
        self.direct_assign_pub = self.create_publisher(
            String, '/warehouse/tasks/direct_assignment', 10
        )

        self.get_logger().info(f"DRLAllocatorNode demarre en mode '{self.mode}'.")

    # ------------------------------------------------------------------ #
    def _on_graph_state(self, msg: String):
        self.graph = WarehouseGraph.from_json(msg.data)
        for name in self.robot_names:
            for nid, data in self.graph.G.nodes(data=True):
                if name in data.get('occupied_by', []):
                    self.agent_node[name] = nid

    def _on_assignment(self, msg: String):
        try:
            data = json.loads(msg.data)
            robot_id = data['robot_id']
        except (json.JSONDecodeError, KeyError):
            return
        self.open_tasks.pop(data.get('task_id'), None)
        if robot_id in self.agent_load:
            self.agent_load[robot_id] += 1

    def _on_task_status(self, msg: String):
        try:
            data = json.loads(msg.data)
            robot_id = data['robot_id']
            terminal = data['state'] in (
                'succeeded', 'failed', 'rejected', 'canceled')
        except (json.JSONDecodeError, KeyError):
            return
        if terminal:
            self.open_tasks.pop(data.get('task_id'), None)
        if terminal and robot_id in self.agent_load:
            self.agent_load[robot_id] = max(0, self.agent_load[robot_id] - 1)

    def _on_new_task(self, msg: String):
        if self.graph is None or not self.model_loaded:
            return  # graphe pas encore recu

        try:
            data = json.loads(msg.data)
            task_id = data['task_id']
            target = data['target_node']
            priority = data.get('priority', 1.0)
        except (json.JSONDecodeError, KeyError):
            return

        if self.obs_version == 'v2':
            self._on_new_task_v2(task_id, target, priority)
            return

        obs = self._build_observation(target, priority)
        q_values = self.agent.q_values(obs)

        if self.mode == 'direct':
            self._publish_direct_assignment(task_id, target, q_values)
        else:
            self._publish_bias(task_id, q_values)

    # ------------------------------------------------------------------ #
    # DRL v2 : Q par couple (robot, tache), voir drl/features_v2.py
    # ------------------------------------------------------------------ #
    def _now(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def _robot_cost(self, name: str, target: str) -> float:
        src = self.agent_node.get(name)
        if src is None or not self.graph.G.has_node(src):
            return math.inf
        return self.graph.shortest_path(src, target)[1]

    def _robot_congestion(self, name: str, target: str) -> float:
        src = self.agent_node.get(name)
        if src is None or not self.graph.G.has_node(src):
            return 0.0
        path, _ = self.graph.shortest_path(src, target)
        return sum(self.graph.G[u][v].get('congestion', 0.0) for u, v in zip(path, path[1:]))

    def _pair_features_v2(self, task: dict):
        """(robots evalues, matrice de caracteristiques) pour ``task``.
        Robots evalues = robots libres (charge nulle), ou toute la flotte si
        aucun n'est libre -- comme allocation_benchmark.hybrid_bias_v2."""
        from warehouse_marl.drl.features_v2 import features_for_robots
        free = [n for n in self.robot_names if self.agent_load.get(n, 0) == 0]
        robots = free or list(self.robot_names)
        cand = sorted(self.open_tasks.values(), key=lambda k: (k['created'], k['id']))
        cand = cand[:self.k_candidates]
        if all(k['id'] != task['id'] for k in cand):
            cand.append(task)
        feats = features_for_robots(
            robots, free, task, cand, cost=self._robot_cost,
            congestion=self._robot_congestion, load=self.agent_load,
            n_robots=len(self.robot_names), queue_len=len(self.open_tasks),
            max_active=self.max_active, now=self._now())
        return robots, np.array([feats[r] for r in robots], dtype=np.float32)

    def _on_new_task_v2(self, task_id: str, target: str, priority: float):
        from warehouse_marl.drl.features_v2 import calibrated_bias
        if not self.graph.G.has_node(target):
            return
        task = {'id': task_id, 'target': target, 'priority': float(priority),
                'created': self._now()}
        self.open_tasks[task_id] = task
        robots, feats = self._pair_features_v2(task)
        q_values = self.agent.scores(feats)
        if self.mode == 'direct':
            best = int(np.argmax(q_values))
            payload = {'task_id': task_id, 'robot_id': robots[best], 'target_node': target,
                       'q_values': {r: float(q) for r, q in zip(robots, q_values)}}
            msg = String()
            msg.data = json.dumps(payload)
            self.direct_assign_pub.publish(msg)
            self.get_logger().info(f"[DRL v2 direct] {task_id} -> {robots[best]}")
            return
        bias = calibrated_bias(q_values, self.bias_weight, self.bias_scale)
        msg = String()
        msg.data = json.dumps({f"{task_id}:{r}": float(b) for r, b in zip(robots, bias)})
        self.bias_pub.publish(msg)

    # ------------------------------------------------------------------ #
    def _build_observation(self, target: str, priority: float) -> np.ndarray:
        """Reconstruit exactement le format d'observation utilise a
        l'entrainement (voir drl/env.py::_build_observation)."""
        feats = []
        for idx, name in enumerate(self.robot_names):
            src = self.agent_node.get(name)
            if src is not None and self.graph.G.has_node(src):
                _, cost = self.graph.shortest_path(src, target)
                cost = cost if cost != float('inf') else 50.0
            else:
                cost = 50.0
            cost_norm = cost / 20.0
            load_norm = self.agent_load.get(name, 0) / max(self.max_active, 1)
            feats.extend([cost_norm, load_norm, float(idx) / len(self.robot_names)])
        feats.append(priority / 2.0)
        return np.array(feats, dtype=np.float32)

    def _publish_bias(self, task_id: str, q_values: np.ndarray):
        """Convertit les Q-values (plus grand = meilleur) en un cout
        additif (plus petit = meilleur) pour rester homogene avec le cout
        utilise par consensus_node.py. On normalise par agent pour ne
        biaiser QUE le classement relatif, pas l'echelle absolue."""
        costs_bias = -q_values  # inversion : Q eleve -> biais negatif -> cout plus faible
        # Cle composite "task_id:robot_id" -> chaque consensus_node (un par
        # robot) ne retient que les cles qui le concernent (voir
        # consensus_node._on_drl_bias). Evite toute ambiguite d'agregation.
        payload = {
            f"{task_id}:{self.robot_names[i]}": float(costs_bias[i])
            for i in range(len(self.robot_names))
        }
        msg = String()
        msg.data = json.dumps(payload)
        self.bias_pub.publish(msg)

    def _publish_direct_assignment(self, task_id: str, target: str, q_values: np.ndarray):
        best_idx = int(np.argmax(q_values))
        payload = {
            'task_id': task_id,
            'robot_id': self.robot_names[best_idx],
            'target_node': target,
            'q_values': q_values.tolist(),
        }
        msg = String()
        msg.data = json.dumps(payload)
        self.direct_assign_pub.publish(msg)
        self.get_logger().info(
            f"[DRL direct] {task_id} -> {self.robot_names[best_idx]} "
            f"(Q={q_values.round(2).tolist()})"
        )


def main(args=None):
    rclpy.init(args=args)
    node = DRLAllocatorNode()
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
