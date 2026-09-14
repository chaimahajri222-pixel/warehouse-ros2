#!/usr/bin/env python3
"""
Publie une TF initiale robot1/map -> robot1/odom.
Decalee pour correspondre a la carte sauvegardee.
"""

import rclpy
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped


class MapToOdom(Node):
    def __init__(self):
        super().__init__('map_to_odom')
        
        self.declare_parameter('robot_name', 'robot1')
        self.declare_parameter('offset_x', 2.95)   # Origine carte
        self.declare_parameter('offset_y', 2.58)
        
        self.robot_name = self.get_parameter('robot_name').value
        self.offset_x = self.get_parameter('offset_x').value
        self.offset_y = self.get_parameter('offset_y').value
        
        self.tf_broadcaster = StaticTransformBroadcaster(self)
        
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = f'{self.robot_name}/map'
        t.child_frame_id = f'{self.robot_name}/odom'
        
        # Decalage pour aligner la position du robot avec la carte
        t.transform.translation.x = self.offset_x
        t.transform.translation.y = self.offset_y
        t.transform.translation.z = 0.0
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0
        
        self.tf_broadcaster.sendTransform(t)
        self.get_logger().info(
            f'TF initiale publiee: {self.robot_name}/map -> {self.robot_name}/odom '
            f'(offset: {self.offset_x}, {self.offset_y})'
        )


def main(args=None):
    rclpy.init(args=args)
    node = MapToOdom()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
