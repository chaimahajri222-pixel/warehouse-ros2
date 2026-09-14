#!/usr/bin/env python3
"""
Nœud qui convertit l'odométrie en TF préfixés.
Publie robot1/odom -> robot1/base_footprint à partir de /robot1/odom.
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class OdomToTf(Node):
    def __init__(self):
        super().__init__('odom_to_tf')
        
        # Paramètre : préfixe du robot (robot1, robot2, robot3)
        self.declare_parameter('robot_name', 'robot1')
        self.robot_name = self.get_parameter('robot_name').value
        
        # Broadcaster TF
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # S'abonner à l'odométrie
        self.subscription = self.create_subscription(
            Odometry,
            f'/{self.robot_name}/odom',
            self.odom_callback,
            10
        )
        
        self.get_logger().info(f'OdomToTf démarré pour {self.robot_name}')
    
    def odom_callback(self, msg):
        t = TransformStamped()
        
        t.header.stamp = msg.header.stamp
        t.header.frame_id = f'{self.robot_name}/odom'
        t.child_frame_id = f'{self.robot_name}/base_footprint'
        
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        
        t.transform.rotation = msg.pose.pose.orientation
        
        self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = OdomToTf()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
