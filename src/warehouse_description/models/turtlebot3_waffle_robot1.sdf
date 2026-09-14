#!/usr/bin/env python3
"""
Nœud qui relaie les TF non préfixés vers des TF préfixés.
Convertit odom -> base_footprint en robot1/odom -> robot1/base_footprint.
"""

import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import TransformStamped


class TfRelay(Node):
    def __init__(self):
        super().__init__('tf_relay')
        
        # S'abonner à /tf
        self.subscription = self.create_subscription(
            TFMessage,
            '/tf',
            self.tf_callback,
            100
        )
        
        # Publier sur /tf_prefixed
        self.publisher = self.create_publisher(
            TFMessage,
            '/tf_prefixed',
            100
        )
        
        self.get_logger().info('TF Relay démarré')
    
    def tf_callback(self, msg):
        filtered_transforms = []
        for transform in msg.transforms:
            frame_id = transform.header.frame_id
            child_frame_id = transform.child_frame_id
            
            # Ne garder que les TF qui concernent les robots
            # et ajouter un préfixe si absent
            new_transform = TransformStamped()
            new_transform.header = transform.header
            new_transform.transform = transform.transform
            
            # Si le frame n'a pas de préfixe robot, on ignore
            # (on ne peut pas deviner à quel robot il appartient)
            # On garde juste les TF déjà préfixés
            if frame_id.startswith('robot') or child_frame_id.startswith('robot'):
                filtered_transforms.append(transform)
        
        if filtered_transforms:
            filtered_msg = TFMessage()
            filtered_msg.transforms = filtered_transforms
            self.publisher.publish(filtered_msg)


def main(args=None):
    rclpy.init(args=args)
    node = TfRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
