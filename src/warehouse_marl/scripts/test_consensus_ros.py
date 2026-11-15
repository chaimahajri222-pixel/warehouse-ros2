"""Tests fonctionnels courts du consensus dans ROS 2, sans Gazebo ni Nav2
(domaine ROS isole, voir test_consensus_ros.sh). Les robots sont simules :
position fixe par TF statique map -> robotX/base_link.

  pertes  : N taches publiees sur /warehouse/tasks/new ; consensus_node
            (un par robot, msg_loss donne) + mission_executor_node + faux
            serveurs NavigateToPose (NAV_S s par mission). Compte, par tache,
            les revendications (conflits = >= 2 robots revendiquent la meme
            tache), les mises en file et les executions.
  blocage : graph_publisher_node + 2 consensus_node. Enchere de reference,
            puis blocage d'une arete du chemin de robot1 (son cout doit
            augmenter), puis isolement de robot1 (toutes ses aretes bloquees :
            il ne doit plus encherir, robot2 gagne), puis deblocage (robot1
            encherit de nouveau). Verifie aussi /warehouse/graph_state.
"""
import json
import random
import sys
import threading
import time

import rclpy
from geometry_msgs.msg import TransformStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String
from tf2_ros import StaticTransformBroadcaster

from warehouse_marl.warehouse_graph import build_demo_warehouse

POSITIONS = {'robot1': 'shelf_0_0', 'robot2': 'shelf_2_2', 'robot3': 'station_B'}
NAV_S = 2.0


class Harness(Node):
    def __init__(self, robots, nav_servers):
        super().__init__('consensus_harness')
        self.graph = build_demo_warehouse(-1.5, -1.0)
        self.lock = threading.Lock()
        self.bids, self.claims, self.status, self.graph_msgs = [], [], [], []
        self.nav_goals = []
        tf = StaticTransformBroadcaster(self)
        msgs = []
        for r in robots:
            d = self.graph.G.nodes[POSITIONS[r]]
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = 'map'
            t.child_frame_id = f'{r}/base_link'
            t.transform.translation.x, t.transform.translation.y = float(d['x']), float(d['y'])
            t.transform.rotation.w = 1.0
            msgs.append(t)
        tf.sendTransform(msgs)
        cg = ReentrantCallbackGroup()
        if nav_servers:
            for r in robots:
                ActionServer(self, NavigateToPose, f'/{r}/navigate_to_pose',
                             lambda h, r=r: self._execute(r, h), callback_group=cg)
        self.create_subscription(String, '/warehouse/consensus/bids',
                                 lambda m: self._rec(self.bids, m), 100)
        self.create_subscription(String, '/warehouse/consensus/assignments',
                                 lambda m: self._rec(self.claims, m), 100)
        self.create_subscription(String, '/warehouse/tasks/status',
                                 lambda m: self._rec(self.status, m), 100)
        self.create_subscription(String, '/warehouse/graph_state',
                                 lambda m: self._rec(self.graph_msgs, m), 10)
        self.new_pub = self.create_publisher(String, '/warehouse/tasks/new', 10)
        self.status_pub = self.create_publisher(String, '/warehouse/tasks/status', 10)
        self.block_pub = self.create_publisher(String, '/warehouse/blocked_edges', 10)

    def _rec(self, store, msg):
        with self.lock:
            store.append((time.time(), json.loads(msg.data)))

    def _execute(self, robot, handle):
        p = handle.request.pose.pose.position
        with self.lock:
            self.nav_goals.append((robot, round(p.x, 2), round(p.y, 2)))
        time.sleep(NAV_S)
        handle.succeed()
        return NavigateToPose.Result()

    def new_task(self, tid, target):
        self.new_pub.publish(String(data=json.dumps(
            {'task_id': tid, 'target_node': target, 'priority': 1.0,
             'created_at': time.time()})))

    def bids_for(self, tid):
        with self.lock:
            return {d['robot_id']: d['cost'] for _, d in self.bids if d['task_id'] == tid}

    def claims_for(self, tid):
        with self.lock:
            return {d['robot_id']: d['cost'] for _, d in self.claims if d['task_id'] == tid}


def wait(cond, timeout):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if cond():
            return True
        time.sleep(0.05)
    return False


def start(robots, nav_servers):
    rclpy.init()
    h = Harness(robots, nav_servers)
    ex = MultiThreadedExecutor(num_threads=8)
    ex.add_node(h)
    th = threading.Thread(target=ex.spin, daemon=True)
    th.start()
    return h, ex, th


def stop(h, ex, th):
    sys.stdout.flush()
    ex.shutdown(timeout_sec=2.0)
    th.join(timeout=2.0)
    h.destroy_node()
    rclpy.try_shutdown()


# --------------------------------------------------------------------------- #
def run_pertes(n_tasks, period, seed, label):
    robots = ['robot1', 'robot2', 'robot3']
    h, ex, th = start(robots, nav_servers=True)
    shelves = [n for n, d in h.graph.G.nodes(data=True) if d['node_type'] == 'shelf']
    rng = random.Random(seed)
    targets = [rng.choice(shelves) for _ in range(n_tasks)]
    # attente des noeuds : une tache de chauffe, renvoyee jusqu'a sa mise en file
    t0 = time.time()
    ok_warm = False
    while time.time() - t0 < 60 and not ok_warm:
        h.new_task('chauffe', 'shelf_1_1')
        ok_warm = wait(lambda: any(d.get('task_id') == 'chauffe' and d['state'] == 'succeeded'
                                   for _, d in h.status), 6.0)
    created = {}
    for i, tgt in enumerate(targets):
        tid = f'p{i:02d}'
        created[tid] = time.time()
        h.new_task(tid, tgt)
        time.sleep(period)
    ids = list(created)

    def finished():
        with h.lock:
            done = {d['task_id'] for _, d in h.status if d['state'] == 'succeeded'}
        return all(t in done for t in ids)
    all_done = wait(finished, 120)
    time.sleep(1.5)
    with h.lock:
        status = [d for _, d in h.status]
        claims = [d for _, d in h.claims]
        bids = [d for _, d in h.bids]
    per = []
    for tid in ids:
        cl = {}
        for d in claims:
            if d['task_id'] == tid:
                cl[d['robot_id']] = d['cost']
        queued = [d['robot_id'] for d in status if d['task_id'] == tid and d['state'] == 'queued']
        nav = {d['robot_id'] for d in status if d['task_id'] == tid and d['state'] == 'navigating'}
        succ = [d['robot_id'] for d in status if d['task_id'] == tid and d['state'] == 'succeeded']
        bid_robots = {d['robot_id'] for d in bids if d['task_id'] == tid}
        best = min(cl.items(), key=lambda kv: (kv[1], kv[0]))[0] if cl else None
        t_q = min((t for t, d in h.status if d['task_id'] == tid and d['state'] == 'queued'),
                  default=None)
        per.append({'tache': tid, 'cible': targets[ids.index(tid)],
                    'encherisseurs': len(bid_robots), 'revendications': len(cl),
                    'conflit': len(cl) >= 2, 'mises_en_file': len(queued),
                    'robots_executant': len(nav), 'reussites': len(succ),
                    'robot': queued[0] if queued else '',
                    'robot_revendication_min': best or '',
                    'delai_attribution_s': round(t_q - created[tid], 3) if t_q else None})
    res = {
        'essai': label, 'taches': len(ids),
        'attribuees': sum(1 for p in per if p['mises_en_file'] >= 1),
        'attribuees_une_seule_fois': sum(1 for p in per if p['mises_en_file'] == 1),
        'mises_en_file_multiples': sum(1 for p in per if p['mises_en_file'] > 1),
        'executions_multiples': sum(1 for p in per if p['robots_executant'] > 1),
        'reussies_une_fois': sum(1 for p in per if p['reussites'] == 1),
        'non_attribuees': sum(1 for p in per if p['mises_en_file'] == 0),
        'conflits': sum(1 for p in per if p['conflit']),
        'executant_different_du_meilleur': sum(
            1 for p in per if p['robot'] and p['robot'] != p['robot_revendication_min']),
        'encheres_publiees': sum(1 for d in bids if d['task_id'] in created),
        'delai_attribution_moy_s': round(
            sum(p['delai_attribution_s'] for p in per if p['delai_attribution_s'] is not None)
            / max(1, sum(1 for p in per if p['delai_attribution_s'] is not None)), 3),
        'toutes_terminees': all_done,
    }
    res['reussi'] = (res['attribuees_une_seule_fois'] == len(ids)
                     and res['executions_multiples'] == 0 and res['reussies_une_fois'] == len(ids))
    print(json.dumps({'resume': res, 'par_tache': per}, ensure_ascii=False))
    stop(h, ex, th)
    return 0 if res['reussi'] else 1


# --------------------------------------------------------------------------- #
def run_blocage():
    robots = ['robot1', 'robot2']
    h, ex, th = start(robots, nav_servers=False)
    log = []
    checks = {}

    def auction(tid, target, timeout=8.0):
        h.new_task(tid, target)
        wait(lambda: len(h.claims_for(tid)) >= 1, timeout)
        time.sleep(1.0)                      # encheres et revendications tardives
        bids, claims = h.bids_for(tid), h.claims_for(tid)
        winner = min(claims.items(), key=lambda kv: (kv[1], kv[0]))[0] if claims else None
        # fin simulee de la tache : libere la capacite du rack et le robot
        if winner:
            h.status_pub.publish(String(data=json.dumps(
                {'task_id': tid, 'robot_id': winner, 'target_node': target,
                 'state': 'succeeded'})))
        time.sleep(0.5)
        log.append({'tache': tid, 'cible': target,
                    'encheres': {r: round(c, 3) for r, c in bids.items()}, 'gagnant': winner})
        return bids, winner

    def block(u, v, blocked=True):
        h.block_pub.publish(String(data=json.dumps(
            {'u': u, 'v': v, 'blocked': blocked, 'duration_s': 0.0 if not blocked else 120.0,
             'source': 'test', 'reason': 'test blocage en direct'})))

    def edge_state(u, v):
        with h.lock:
            if not h.graph_msgs:
                return None
            g = h.graph_msgs[-1][1]
        for e in g['edges']:
            if {e['u'], e['v']} == {u, v}:
                return bool(e['blocked'])
        return None

    # 0. demarrage : attendre graph_state et une premiere enchere des deux robots
    wait(lambda: len(h.graph_msgs) > 0, 30)
    t0 = time.time()
    while time.time() - t0 < 60:
        b, _ = auction(f'chauffe_{int(time.time())}', 'shelf_1_1')
        if len(b) == 2:
            break
    # 1. reference : robot1 (shelf_0_0) vers shelf_0_2
    ref, _ = auction('ref', 'shelf_0_2')
    # 2. blocage d'une arete de son plus court chemin : shelf_0_1 <-> shelf_0_2
    block('shelf_0_1', 'shelf_0_2')
    seen_block = wait(lambda: edge_state('shelf_0_1', 'shelf_0_2') is True, 5)
    time.sleep(1.2)                          # au moins une publication du graphe
    partial, _ = auction('detour', 'shelf_0_2')
    checks['graph_state_arete_bloquee'] = seen_block
    checks['cout_robot1_augmente_apres_blocage'] = (
        'robot1' in ref and 'robot1' in partial and partial['robot1'] > ref['robot1'] + 1e-6)
    # 3. isolement de robot1 : toutes les aretes de shelf_0_0
    block('shelf_0_0', 'shelf_0_1')
    block('shelf_0_0', 'shelf_1_0')
    seen_iso = wait(lambda: edge_state('shelf_0_0', 'shelf_0_1') is True
                    and edge_state('shelf_0_0', 'shelf_1_0') is True, 5)
    time.sleep(1.2)
    iso, win_iso = auction('isole', 'shelf_1_1')
    checks['graph_state_robot1_isole'] = seen_iso
    checks['robot1_n_encherit_plus'] = 'robot1' not in iso
    checks['robot2_encherit_et_gagne'] = 'robot2' in iso and win_iso == 'robot2'
    # 4. deblocage
    for u, v in (('shelf_0_1', 'shelf_0_2'), ('shelf_0_0', 'shelf_0_1'), ('shelf_0_0', 'shelf_1_0')):
        block(u, v, blocked=False)
    seen_free = wait(lambda: edge_state('shelf_0_0', 'shelf_0_1') is False
                     and edge_state('shelf_0_0', 'shelf_1_0') is False
                     and edge_state('shelf_0_1', 'shelf_0_2') is False, 5)
    time.sleep(1.2)
    free, _ = auction('debloque', 'shelf_0_2')
    checks['graph_state_debloque'] = seen_free
    checks['robot1_encherit_de_nouveau'] = 'robot1' in free
    checks['cout_robot1_revenu_a_la_reference'] = (
        'robot1' in free and 'robot1' in ref and abs(free['robot1'] - ref['robot1']) < 0.5)
    out = {'encheres': log, 'verifications': checks, 'reussi': all(checks.values())}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    stop(h, ex, th)
    return 0 if out['reussi'] else 1


if __name__ == '__main__':
    if sys.argv[1] == 'pertes':
        sys.exit(run_pertes(int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]))
    sys.exit(run_blocage())
