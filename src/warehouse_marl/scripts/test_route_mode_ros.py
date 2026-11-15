"""Test fonctionnel court (protocole v4, etape 3) : faux serveur Nav2
FollowWaypoints pour robot1 + envoi d'une assignation ; verifie que
mission_executor_node (route_mode dijkstra|drl) publie une route du graphe,
envoie des points de passage coherents et termine la mission.
A lancer sur un domaine ROS isole (voir test_route_mode_ros.sh)."""
import json
import sys
import time

import rclpy
from nav2_msgs.action import FollowWaypoints
from rclpy.action import ActionServer
from rclpy.node import Node
from std_msgs.msg import String


class Harness(Node):
    def __init__(self):
        super().__init__('route_mode_harness')
        self.goals, self.routes, self.status = [], [], []
        ActionServer(self, FollowWaypoints, '/robot1/follow_waypoints', self._execute)
        self.create_subscription(String, '/warehouse/routes',
                                 lambda m: self.routes.append(json.loads(m.data)), 10)
        self.create_subscription(String, '/warehouse/tasks/status',
                                 lambda m: self.status.append(json.loads(m.data)), 10)
        self.pub = self.create_publisher(String, '/warehouse/tasks/direct_assignment', 10)

    def _execute(self, handle):
        self.goals.append([(p.pose.position.x, p.pose.position.y) for p in handle.request.poses])
        handle.succeed()
        return FollowWaypoints.Result()


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else 'shelf_4_2'
    rclpy.init()
    h = Harness()
    t0 = time.time()
    last = 0.0
    while time.time() - t0 < 60:
        rclpy.spin_once(h, timeout_sec=0.1)
        # renvoi toutes les 2 s tant qu'aucune route n'est publiee (le noeud
        # peut mettre plusieurs secondes a demarrer ; les doublons sont ignores)
        if not h.routes and time.time() - last > 2.0:
            h.pub.publish(String(data=json.dumps(
                {'task_id': 'ros_t0', 'robot_id': 'robot1', 'target_node': target, 'cost': 0.0})))
            last = time.time()
        if any(s.get('state') == 'succeeded' for s in h.status):
            break
    states = [s.get('state') for s in h.status]
    out = {'route': h.routes[0]['route'] if h.routes else None,
           'route_mode': h.routes[0]['route_mode'] if h.routes else None,
           'n_points': len(h.goals[0]) if h.goals else 0,
           'points': [[round(x, 2), round(y, 2)] for x, y in h.goals[0]] if h.goals else [],
           'etats': states, 'reussi': 'succeeded' in states}
    print(json.dumps(out))
    rclpy.shutdown()
    sys.exit(0 if out['reussi'] and out['route'] and out['route'][-1] == target else 1)


if __name__ == '__main__':
    main()
