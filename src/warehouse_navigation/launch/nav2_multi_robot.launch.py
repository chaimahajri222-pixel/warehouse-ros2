#!/usr/bin/env python3
"""
Launch file pour Nav2 sur 3 robots.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, GroupAction, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import PushRosNamespace


def generate_launch_description():
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    robots = ['robot1', 'robot2', 'robot3']
    actions = []

    for i, robot_name in enumerate(robots):
        nav2_group = GroupAction([
            PushRosNamespace(robot_name),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
                ),
                launch_arguments={
                    'use_sim_time': 'true',
                    'autostart': 'true',
                }.items()
            ),
        ])

        delayed_nav2 = TimerAction(
            period=10.0 + i * 5.0,
            actions=[nav2_group]
        )
        actions.append(delayed_nav2)

    return LaunchDescription(actions)
