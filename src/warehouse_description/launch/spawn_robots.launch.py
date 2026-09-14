#!/usr/bin/env python3
"""
Launch file pour spawner 3 TurtleBot3 dans Gazebo.
Mode headless pour reduire la charge CPU.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    turtlebot3_model = os.environ.get('TURTLEBOT3_MODEL', 'waffle')

    world_file = os.path.join(
        pkg_turtlebot3_gazebo, 'worlds', 'turtlebot3_world.world'
    )

    robots_config = [
        {'name': 'robot1', 'x': '-2.0', 'y': '-0.5', 'theta': '0.0'},
        {'name': 'robot2', 'x': '0.0', 'y': '-0.5', 'theta': '0.0'},
        {'name': 'robot3', 'x': '2.0', 'y': '-0.5', 'theta': '0.0'},
    ]

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': world_file,
            'verbose': 'false',
        }.items()
    )

    actions = [gazebo]

    urdf_file = os.path.join(
        pkg_turtlebot3_gazebo,
        'models',
        f'turtlebot3_{turtlebot3_model}',
        'model.sdf'
    )

    for i, robot in enumerate(robots_config):
        spawn_entity = Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            name=f'spawn_{robot["name"]}',
            arguments=[
                '-entity', robot['name'],
                '-file', urdf_file,
                '-x', robot['x'],
                '-y', robot['y'],
                '-z', '0.01',
                '-Y', robot['theta'],
                '-robot_namespace', robot['name'],
            ],
            output='screen'
        )

        delayed_spawn = TimerAction(
            period=5.0 + i * 3.0,
            actions=[spawn_entity]
        )

        actions.append(delayed_spawn)

    return LaunchDescription(actions)
