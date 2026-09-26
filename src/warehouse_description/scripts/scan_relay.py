#!/usr/bin/env python3
"""
Nœud qui réécrit le frame_id du scan.
Convertit base_scan en robot1/base_scan.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class ScanRelay(Node):
    def __init__(self):
        super().__init__('scan_relay')
        
        self.declare_parameter('robot_name', 'robot1')
        self.declare_parameter('input_topic', '/robot1/scan')
        self.declare_parameter('output_topic', '/robot1/scan_fixed')
        
        self.robot_name = self.get_parameter('robot_name').value
        self.input_topic = self.get_parameter('input_topic').value
        self.output_topic = self.get_parameter('output_topic').value
        
        self.subscription = self.create_subscription(
            LaserScan,
            self.input_topic,
            self.scan_callback,
            10
        )
        
        self.publisher = self.create_publisher(
            LaserScan,
            self.output_topic,
            10
        )
        
        self.get_logger().info(f'ScanRelay: {self.input_topic} -> {self.output_topic}')
        self.get_logger().info(f'Frame ID: {self.robot_name}/base_scan')
    
    def scan_callback(self, msg):
        # Modifier le frame_id
        msg.header.frame_id = f'{self.robot_name}/base_scan'
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ScanRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
