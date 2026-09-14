#!/usr/bin/env python3
"""
Launch file SLAM pour robot1 avec scan relai.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_warehouse_slam = get_package_share_directory('warehouse_slam')
    slam_params = os.path.join(pkg_warehouse_slam, 'config', 'slam_params.yaml')

    # Nœud de relais pour réécrire le frame_id du scan
    scan_relay = Node(
        package='warehouse_description',
        executable='scan_relay.py',
        name='scan_relay',
        parameters=[{
            'robot_name': 'robot1',
            'input_topic': '/robot1/scan',
            'output_topic': '/robot1/scan_fixed',
        }],
        output='screen'
    )

    # Nœud SLAM
    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        namespace='robot1',
        parameters=[
            slam_params,
            {
                'use_sim_time': True,
                'odom_frame': 'robot1/odom',
                'map_frame': 'robot1/map',
                'base_frame': 'robot1/base_footprint',
                'scan_topic': '/robot1/scan_fixed',
            }
        ],
        remappings=[
            ('/map', '/robot1/map'),
            ('/map_metadata', '/robot1/map_metadata'),
            ('/map_updates', '/robot1/map_updates'),
        ],
        output='screen'
    )

    return LaunchDescription([scan_relay, slam_node])
