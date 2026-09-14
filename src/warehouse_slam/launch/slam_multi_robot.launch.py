#!/usr/bin/env python3
"""
Launch file pour SLAM Toolbox sur 3 robots.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction, TimerAction
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    pkg_warehouse_slam = get_package_share_directory('warehouse_slam')
    slam_params = os.path.join(pkg_warehouse_slam, 'config', 'slam_params.yaml')

    robots = ['robot1', 'robot2', 'robot3']
    actions = []

    for i, robot_name in enumerate(robots):
        slam_node = GroupAction([
            PushRosNamespace(robot_name),
            Node(
                package='slam_toolbox',
                executable='async_slam_toolbox_node',
                name='slam_toolbox',
                parameters=[
                    slam_params,
                    {'use_sim_time': True},
                ],
                output='screen'
            ),
        ])

        delayed_slam = TimerAction(
            period=15.0 + i * 5.0,
            actions=[slam_node]
        )
        actions.append(delayed_slam)

    return LaunchDescription(actions)
