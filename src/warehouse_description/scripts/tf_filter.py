#!/usr/bin/env python3
"""
Nœud pour filtrer les TF non préfixés.
Empêche la publication de base_footprint global.
"""

import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage


class TFFilter(Node):
    def __init__(self):
        super().__init__('tf_filter')
        
        # S'abonner à /tf
        self.subscription = self.create_subscription(
            TFMessage,
            '/tf',
            self.tf_callback,
            10
        )
        
        # Publier sur /tf_filtered
        self.publisher = self.create_publisher(
            TFMessage,
            '/tf_filtered',
            10
        )
        
        self.get_logger().info('TF Filter démarré')
    
    def tf_callback(self, msg):
        # Filtrer les transforms non préfixés
        filtered_transforms = []
        for transform in msg.transforms:
            frame_id = transform.header.frame_id
            child_frame_id = transform.child_frame_id
            
            # Garder seulement les TF préfixés ou globaux (map, odom)
            if (frame_id.startswith('robot') or 
                child_frame_id.startswith('robot') or
                frame_id in ['map', 'odom', 'world'] or
                child_frame_id in ['map', 'odom', 'world']):
                filtered_transforms.append(transform)
        
        if filtered_transforms:
            filtered_msg = TFMessage()
            filtered_msg.transforms = filtered_transforms
            self.publisher.publish(filtered_msg)


def main(args=None):
    rclpy.init(args=args)
    node = TFFilter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
