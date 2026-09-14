"""
task_generator_node.py
------------------------
Simule le flux de commandes / operations d'inventaire a traiter dans
l'entrepot (equivalent d'un WMS - Warehouse Management System - qui
emettrait des ordres de picking). Publie de nouvelles taches sur
/warehouse/tasks/new, consommees a la fois par consensus_node.py
(enchere distribuee) et par drl_allocator_node.py (politique apprise).

Chaque tache = "aller chercher / deposer un article a tel noeud du
graphe" (rack ou station). Permet de mesurer, comme demande dans le
sujet, le "temps de traitement d'inventaire" et le "taux d'erreur"
en comparant :
    - le mode heuristique (consensus seul, cout = plus court chemin),
    - le mode DRL (drl_allocator_node),
    - le mode hybride (consensus + biais DRL).
"""

import json
import random
import time
import uuid

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from warehouse_marl.warehouse_graph import build_demo_warehouse


class TaskGeneratorNode(Node):

    def __init__(self):
        super().__init__('task_generator_node')

        self.declare_parameter('mean_period_sec', 4.0)
        self.declare_parameter('priority_min', 0.5)
        self.declare_parameter('priority_max', 2.0)
        self.declare_parameter('seed', 42)

        self.mean_period = self.get_parameter('mean_period_sec').value
        self.priority_min = self.get_parameter('priority_min').value
        self.priority_max = self.get_parameter('priority_max').value
        random.seed(self.get_parameter('seed').value)

        self.graph = build_demo_warehouse()
        self.shelf_nodes = [
            n for n, d in self.graph.G.nodes(data=True) if d['node_type'] == 'shelf'
        ]

        self.task_pub = self.create_publisher(String, '/warehouse/tasks/new', 10)
        self._schedule_next()

        self.get_logger().info(
            f"TaskGeneratorNode pret : {len(self.shelf_nodes)} emplacements possibles."
        )

    def _schedule_next(self):
        # Loi exponentielle -> arrivees de type processus de Poisson,
        # realiste pour un flux de commandes en entrepot.
        delay = random.expovariate(1.0 / self.mean_period)
        self.create_timer(delay, self._emit_task_once)

    def _emit_task_once(self):
        self._emit_task()
        self._schedule_next()

    def _emit_task(self):
        target = random.choice(self.shelf_nodes)
        priority = round(random.uniform(self.priority_min, self.priority_max), 2)
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        payload = {
            'task_id': task_id,
            'target_node': target,
            'priority': priority,
            'created_at': time.time(),
        }
        msg = String()
        msg.data = json.dumps(payload)
        self.task_pub.publish(msg)
        self.get_logger().info(
            f"Nouvelle tache {task_id} -> {target} (priorite {priority})"
        )


def main(args=None):
    rclpy.init(args=args)
    node = TaskGeneratorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
