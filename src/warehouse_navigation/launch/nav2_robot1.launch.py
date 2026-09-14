#!/usr/bin/env python3
"""
Launch file Nav2 pour robot1 - SANS namespace.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    pkg_warehouse_navigation = get_package_share_directory('warehouse_navigation')

    nav2_params = os.path.join(
        pkg_warehouse_navigation, 'config', 'nav2_params_robot1.yaml'
    )

    map_file = os.path.join(
        pkg_warehouse_navigation, 'maps', 'warehouse_map.yaml'
    )

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server_robot1',
        output='screen',
        parameters=[
            nav2_params,
            {
                'use_sim_time': True,
                'yaml_filename': map_file,
                'topic_name': '/robot1/map',
                'frame_id': 'robot1/map',
            }
        ],
        remappings=[
            ('map', '/robot1/map'),
            ('map_metadata', '/robot1/map_metadata'),
        ],
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl_robot1',
        output='screen',
        parameters=[nav2_params, {'use_sim_time': True}],
    )

    lifecycle_manager_localization = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization_robot1',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server_robot1', 'amcl_robot1'],
        }],
    )

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server_robot1',
        output='screen',
        parameters=[
            nav2_params,
            {
                'use_sim_time': True,
                'FollowPath.critics': [
                    'RotateToGoal', 'Oscillation', 'BaseObstacle',
                    'GoalAlign', 'PathAlign', 'PathDist', 'GoalDist'
                ],
            }
        ],
        remappings=[('cmd_vel', '/robot1/cmd_vel_nav')],
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server_robot1',
        output='screen',
        parameters=[nav2_params, {'use_sim_time': True}],
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server_robot1',
        output='screen',
        parameters=[nav2_params, {'use_sim_time': True}],
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator_robot1',
        output='screen',
        parameters=[nav2_params, {'use_sim_time': True}],
    )

    waypoint_follower = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        name='waypoint_follower_robot1',
        output='screen',
        parameters=[nav2_params, {'use_sim_time': True}],
    )

    velocity_smoother = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother_robot1',
        output='screen',
        parameters=[nav2_params, {'use_sim_time': True}],
        remappings=[
            ('cmd_vel', '/robot1/cmd_vel_nav'),
            ('cmd_vel_smoothed', '/robot1/cmd_vel'),
        ],
    )

    lifecycle_manager_navigation = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation_robot1',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [
                'controller_server_robot1',
                'planner_server_robot1',
                'behavior_server_robot1',
                'bt_navigator_robot1',
                'waypoint_follower_robot1',
                'velocity_smoother_robot1',
            ],
        }],
    )

    return LaunchDescription([
        TimerAction(period=2.0, actions=[map_server]),
        TimerAction(period=4.0, actions=[amcl]),
        TimerAction(period=6.0, actions=[lifecycle_manager_localization]),
        TimerAction(period=10.0, actions=[controller_server]),
        TimerAction(period=11.0, actions=[planner_server]),
        TimerAction(period=12.0, actions=[behavior_server]),
        TimerAction(period=13.0, actions=[bt_navigator]),
        TimerAction(period=14.0, actions=[waypoint_follower]),
        TimerAction(period=15.0, actions=[velocity_smoother]),
        TimerAction(period=18.0, actions=[lifecycle_manager_navigation]),
    ])
