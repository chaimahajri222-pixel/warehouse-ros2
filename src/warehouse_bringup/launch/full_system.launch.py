#!/usr/bin/env python3
"""
Launch file principal : Gazebo + SLAM + Nav2 + RViz.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_warehouse_description = get_package_share_directory('warehouse_description')
    pkg_warehouse_navigation = get_package_share_directory('warehouse_navigation')
    pkg_warehouse_slam = get_package_share_directory('warehouse_slam')
    pkg_warehouse_bringup = get_package_share_directory('warehouse_bringup')

    spawn_robots = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_warehouse_description, 'launch', 'spawn_robots.launch.py')
        )
    )

    slam = TimerAction(
        period=20.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_warehouse_slam, 'launch', 'slam_multi_robot.launch.py')
                )
            )
        ]
    )

    nav2 = TimerAction(
        period=40.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_warehouse_navigation, 'launch', 'nav2_multi_robot.launch.py')
                )
            )
        ]
    )

    rviz_config = os.path.join(pkg_warehouse_bringup, 'config', 'multi_robot.rviz')

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        spawn_robots,
        slam,
        nav2,
        rviz,
    ])
