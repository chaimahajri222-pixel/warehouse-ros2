"""Test fonctionnel court de idle_mode (stay|centre|drl) dans mission_executor_node,
sur un domaine ROS isole (voir test_idle_mode_ros.sh). Sans Gazebo ni Nav2 :
un faux serveur NavigateToPose pour robot1.

Scenario :
  1. historique de demande publie sur /warehouse/tasks/new (racks du fond) ;
  2. mission t0 -> shelf_4_2 par defaut, ou la cible donnee en 2e argument
     (le faux serveur reussit tout de suite) ;
  3. robot1 devient inoccupe : decision d'attente (/warehouse/idle_points) et,
     si le point differe de sa position, NavigateToPose vers ce point ; le faux
     serveur garde ce but 4 s (annulable) ;
  4. pendant ce trajet, mission t1 -> shelf_0_0 : le trajet d'attente doit etre
     annule, puis t1 executee ;
  5. nouvelle decision d'attente apres t1.

Verifications (stay) : aucun but d'attente. (centre|drl) : decision publiee,
but d'attente aux coordonnees du noeud choisi, annulation du trajet a l'arrivee
de t1, t1 et t0 reussies une seule fois.
"""
import json
import sys
import threading
import time

import rclpy
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionServer, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String

from warehouse_marl.warehouse_graph import build_demo_warehouse

HOLD_S = 4.0
HISTORY = ['shelf_4_1', 'shelf_4_2', 'shelf_4_2', 'shelf_3_2', 'shelf_4_0', 'shelf_4_2']


class Harness(Node):
    def __init__(self, graph):
        super().__init__('idle_mode_harness')
        self.graph = graph
        self.lock = threading.Lock()
        self.goals, self.status, self.idle = [], [], []
        self.canceled = 0
        self.mission_xy = {}
        cg = ReentrantCallbackGroup()
        ActionServer(self, NavigateToPose, '/robot1/navigate_to_pose', self._execute,
                     cancel_callback=lambda _h: CancelResponse.ACCEPT, callback_group=cg)
        self.create_subscription(String, '/warehouse/tasks/status',
                                 lambda m: self.status.append(json.loads(m.data)), 10)
        self.create_subscription(String, '/warehouse/idle_points',
                                 lambda m: self.idle.append(json.loads(m.data)), 10)
        self.new_pub = self.create_publisher(String, '/warehouse/tasks/new', 10)
        self.asg_pub = self.create_publisher(String, '/warehouse/tasks/direct_assignment', 10)

    def xy(self, node):
        d = self.graph.G.nodes[node]
        return round(d['x'], 2), round(d['y'], 2)

    def _execute(self, handle):
        p = handle.request.pose.pose.position
        xy = (round(p.x, 2), round(p.y, 2))
        kind = 'mission' if xy in self.mission_xy.values() else 'attente'
        with self.lock:
            self.goals.append({'type': kind, 'xy': list(xy), 't': round(time.time(), 2)})
        if kind == 'attente':
            t_end = time.time() + HOLD_S
            while time.time() < t_end:
                if handle.is_cancel_requested:
                    handle.canceled()
                    with self.lock:
                        self.canceled += 1
                        self.goals[-1]['annule'] = True
                    return NavigateToPose.Result()
                time.sleep(0.05)
        handle.succeed()
        return NavigateToPose.Result()

    def new_task(self, tid, target):
        self.new_pub.publish(String(data=json.dumps(
            {'task_id': tid, 'target_node': target, 'created_at': time.time()})))

    def assign(self, tid, target):
        self.mission_xy[tid] = self.xy(target)
        self.asg_pub.publish(String(data=json.dumps(
            {'task_id': tid, 'robot_id': 'robot1', 'target_node': target, 'cost': 0.0})))

    def states(self, tid):
        return [s['state'] for s in self.status if s.get('task_id') == tid]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'stay'
    t0_target = sys.argv[2] if len(sys.argv) > 2 else 'shelf_4_2'
    rclpy.init()
    graph = build_demo_warehouse(-1.5, -1.0)
    h = Harness(graph)
    ex = MultiThreadedExecutor(num_threads=4)
    ex.add_node(h)
    spin = threading.Thread(target=ex.spin, daemon=True)
    spin.start()

    def wait(cond, timeout):
        t0 = time.time()
        while time.time() - t0 < timeout:
            if cond():
                return True
            time.sleep(0.05)
        return False

    # 1. le noeud demarre : on renvoie t0 jusqu'a la mise en file (doublons ignores)
    t_start = time.time()
    ready = False
    while time.time() - t_start < 60 and not ready:
        for i, s in enumerate(HISTORY):
            h.new_task(f'hist_{i}', s)
        h.new_task('t0', t0_target)
        h.assign('t0', t0_target)
        ready = wait(lambda: 'queued' in h.states('t0'), 2.0)
    ok_t0 = wait(lambda: 'succeeded' in h.states('t0'), 15)
    # 2. decision d'attente apres t0
    got_idle = wait(lambda: len(h.idle) >= 1, 5) if mode != 'stay' else False
    park_goal = wait(lambda: any(g['type'] == 'attente' for g in h.goals), 3)
    # 3. mission t1 pendant le trajet d'attente
    time.sleep(0.5)
    h.new_task('t1', 'shelf_0_0')
    h.assign('t1', 'shelf_0_0')
    ok_t1 = wait(lambda: 'succeeded' in h.states('t1'), 20)
    second_idle = wait(lambda: len(h.idle) >= 2, 5) if mode != 'stay' else False
    time.sleep(1.0)

    park_goals = [g for g in h.goals if g['type'] == 'attente']
    first = h.idle[0] if h.idle else {}
    choice_xy = list(h.xy(first['choix'])) if first.get('choix') else None
    checks = {
        't0_reussie_une_fois': h.states('t0').count('succeeded') == 1 and ok_t0,
        't1_reussie_une_fois': h.states('t1').count('succeeded') == 1 and ok_t1,
    }
    if mode == 'stay':
        checks['aucun_but_attente'] = not park_goals and not h.idle
    else:
        moved = first.get('choix') not in (None, first.get('depuis'))
        checks['decision_publiee'] = got_idle
        checks['but_attente_au_noeud_choisi'] = (
            (park_goals and park_goals[0]['xy'] == choice_xy) if moved else not park_goal)
        checks['trajet_annule_par_t1'] = (h.canceled >= 1) if moved else None
        checks['seconde_decision_apres_t1'] = second_idle
    out = {'idle_mode': mode, 'cible_t0': t0_target, 'decisions': h.idle, 'buts_nav2': h.goals,
           'annulations': h.canceled, 'etats_t0': h.states('t0'), 'etats_t1': h.states('t1'),
           'verifications': checks,
           'reussi': all(v for v in checks.values() if v is not None)}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    sys.stdout.flush()
    ex.shutdown(timeout_sec=2.0)
    spin.join(timeout=2.0)
    h.destroy_node()
    rclpy.try_shutdown()
    sys.exit(0 if out['reussi'] else 1)


if __name__ == '__main__':
    main()
