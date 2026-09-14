"""
graph_publisher_node.py
------------------------
Noeud ROS2 qui :
  1) construit/maintient le WarehouseGraph (graphe dynamique) ;
  2) ecoute l'odometrie de chaque robot de la flotte (/robotX/odom) pour
     mettre a jour l'occupation des noeuds et la congestion des aretes ;
  3) ecoute les detections RFID publiees par rfid_sensor_node sur
     /rfid/detections pour recaler la position logique d'un robot sur un
     noeud precis du graphe (RFID = verite terrain, l'odometrie derive) ;
  4) publie periodiquement l'etat complet du graphe (JSON) sur
     /warehouse/graph_state, consomme par consensus_node.py et
     drl_allocator_node.py.

Ce noeud fait le pont entre la simulation Gazebo/Nav2 (rosnav) et la
couche de coordination multi-agents (consensus + DRL).
"""

import json
import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav_msgs.msg import Odometry

from warehouse_marl.warehouse_graph import build_demo_warehouse


class GraphPublisherNode(Node):

    def __init__(self):
        super().__init__('graph_publisher_node')

        self.declare_parameter('robot_names', ['robot1', 'robot2', 'robot3'])
        self.declare_parameter('publish_period_sec', 1.0)
        self.declare_parameter('node_snap_radius', 1.5)  # m

        self.robot_names = self.get_parameter('robot_names').value
        period = self.get_parameter('publish_period_sec').value
        self.snap_radius = self.get_parameter('node_snap_radius').value

        self.graph = build_demo_warehouse()
        self._robot_last_node = {name: None for name in self.robot_names}

        # Abonnement a l'odometrie de chaque robot
        self._odom_subs = []
        for name in self.robot_names:
            topic = f'/{name}/odom'
            sub = self.create_subscription(
                Odometry, topic,
                lambda msg, n=name: self._on_odom(n, msg), 10
            )
            self._odom_subs.append(sub)
            self.get_logger().info(f"Abonne a {topic}")

        # Abonnement aux detections RFID (recalage position logique)
        self.create_subscription(
            String, '/rfid/detections', self._on_rfid, 10
        )

        # Publication de l'etat du graphe
        self.graph_pub = self.create_publisher(String, '/warehouse/graph_state', 10)
        self.create_timer(period, self._publish_graph)

        self.get_logger().info(
            f"GraphPublisherNode demarre avec {len(self.graph.G.nodes)} noeuds "
            f"et {len(self.graph.G.edges)} aretes."
        )

    # ------------------------------------------------------------------ #
    def _nearest_node(self, x: float, y: float):
        best, best_d = None, math.inf
        for nid, data in self.graph.G.nodes(data=True):
            d = math.hypot(data['x'] - x, data['y'] - y)
            if d < best_d:
                best, best_d = nid, d
        return best, best_d

    def _on_odom(self, robot_name: str, msg: Odometry):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        nearest, dist = self._nearest_node(x, y)
        if nearest is None or dist > self.snap_radius:
            return

        prev = self._robot_last_node[robot_name]
        if prev == nearest:
            return  # pas de changement de noeud

        # Libere le noeud precedent, occupe le nouveau
        if prev is not None:
            self.graph.set_node_occupancy(prev, robot_name, occupied=False)
            if self.graph.G.has_edge(prev, nearest):
                self.graph.update_congestion(prev, nearest, delta=-0.5)
        self.graph.set_node_occupancy(nearest, robot_name, occupied=True)
        self._robot_last_node[robot_name] = nearest

        self.get_logger().debug(f"{robot_name} -> noeud {nearest} (d={dist:.2f}m)")

    def _on_rfid(self, msg: String):
        """Recale la position logique d'un robot quand un tag RFID est lu :
        c'est la verite terrain qui corrige la derive d'odometrie."""
        try:
            data = json.loads(msg.data)
            robot_name = data['robot_id']
            node_id = data['node_id']
            tag = data['rfid_tag']
        except (json.JSONDecodeError, KeyError):
            self.get_logger().warn("Message RFID mal forme, ignore.")
            return

        if node_id not in self.graph.G.nodes:
            return

        self.graph.register_rfid_read(node_id, tag)

        prev = self._robot_last_node[robot_name] if robot_name in self._robot_last_node else None
        if prev != node_id:
            if prev is not None:
                self.graph.set_node_occupancy(prev, robot_name, occupied=False)
            self.graph.set_node_occupancy(node_id, robot_name, occupied=True)
            self._robot_last_node[robot_name] = node_id
            self.get_logger().info(
                f"[RFID] Recalage {robot_name} -> {node_id} (tag {tag})"
            )

    def _publish_graph(self):
        msg = String()
        msg.data = self.graph.to_json()
        self.graph_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = GraphPublisherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
