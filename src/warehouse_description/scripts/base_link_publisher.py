#!/usr/bin/env python3
"""
Publie les TF robot1/base_footprint -> robot1/base_link et robot1/base_link -> robot1/base_scan.
Utilise pour completer robot_state_publisher si necessaire.
"""

import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped


class BaseLinkPublisher(Node):
    def __init__(self):
        super().__init__('base_link_publisher')
        
        self.declare_parameter('robot_name', 'robot1')
        self.robot_name = self.get_parameter('robot_name').value
        
        self.tf_broadcaster = TransformBroadcaster(self)
        
        self.timer = self.create_timer(0.05, self.publish_tf)
        
        self.get_logger().info(f'BaseLinkPublisher demarre pour {self.robot_name}')
    
    def publish_tf(self):
        now = self.get_clock().now().to_msg()
        
        # 1. base_footprint -> base_link
        t1 = TransformStamped()
        t1.header.stamp = now
        t1.header.frame_id = f'{self.robot_name}/base_footprint'
        t1.child_frame_id = f'{self.robot_name}/base_link'
        t1.transform.translation.x = 0.0
        t1.transform.translation.y = 0.0
        t1.transform.translation.z = 0.010
        t1.transform.rotation.x = 0.0
        t1.transform.rotation.y = 0.0
        t1.transform.rotation.z = 0.0
        t1.transform.rotation.w = 1.0
        self.tf_broadcaster.sendTransform(t1)
        
        # 2. base_link -> base_scan
        t2 = TransformStamped()
        t2.header.stamp = now
        t2.header.frame_id = f'{self.robot_name}/base_link'
        t2.child_frame_id = f'{self.robot_name}/base_scan'
        t2.transform.translation.x = -0.064
        t2.transform.translation.y = 0.0
        t2.transform.translation.z = 0.122
        t2.transform.rotation.x = 0.0
        t2.transform.rotation.y = 0.0
        t2.transform.rotation.z = 0.0
        t2.transform.rotation.w = 1.0
        self.tf_broadcaster.sendTransform(t2)


def main(args=None):
    rclpy.init(args=args)
    node = BaseLinkPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
