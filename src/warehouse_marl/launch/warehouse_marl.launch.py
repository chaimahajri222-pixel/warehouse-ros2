"""
warehouse_marl.launch.py
--------------------------
Lance toute la couche "coordination distribuee + RFID + DRL" par-dessus
la simulation Nav2/Gazebo deja fournie par rosnav.

Usage typique (2 terminaux) :

    # Terminal 1 - simulation + navigation (package rosnav) :
    ros2 launch diff_drive_robot multi_robot.launch.py \\
        world:=warehouse explore:=false fleet_mgmt:=false

    # Terminal 2 - couche coordination multi-agents (ce package) :
    ros2 launch warehouse_marl warehouse_marl.launch.py \\
        robot_names:="['robot1','robot2','robot3']" \\
        drl_mode:=hybrid model_path:=/absolute/path/warehouse_dqn.pt

Ce launch file demarre, pour N robots :
    - 1x graph_publisher_node       (etat partage du graphe dynamique)
    - 1x rfid_sensor_node           (couche capteurs RFID/IoT simulee)
    - 1x task_generator_node        (flux de commandes a traiter)
    - 1x drl_allocator_node         (politique DRL -> biais de consensus)
    - Nx consensus_node             (un par robot -> decision distribuee)
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    robot_names_str = LaunchConfiguration('robot_names').perform(context)
    # Autorise soit une liste Python ("['robot1','robot2']"), soit une
    # chaine separee par des virgules ("robot1,robot2").
    if robot_names_str.strip().startswith('['):
        robot_names = eval(robot_names_str)  # noqa: S307 - usage local/CLI uniquement
    else:
        robot_names = [r.strip() for r in robot_names_str.split(',') if r.strip()]

    drl_mode = LaunchConfiguration('drl_mode').perform(context)
    model_path = LaunchConfiguration('model_path').perform(context)

    nodes = []

    nodes.append(Node(
        package='warehouse_marl',
        executable='graph_publisher_node',
        name='graph_publisher_node',
        output='screen',
        parameters=[{'robot_names': robot_names}],
    ))

    nodes.append(Node(
        package='warehouse_marl',
        executable='rfid_sensor_node',
        name='rfid_sensor_node',
        output='screen',
        parameters=[{'robot_names': robot_names}],
    ))

    nodes.append(Node(
        package='warehouse_marl',
        executable='task_generator_node',
        name='task_generator_node',
        output='screen',
    ))

    nodes.append(Node(
        package='warehouse_marl',
        executable='drl_allocator_node',
        name='drl_allocator_node',
        output='screen',
        parameters=[{
            'robot_names': robot_names,
            'mode': drl_mode,
            'model_path': model_path,
        }],
    ))

    for name in robot_names:
        nodes.append(Node(
            package='warehouse_marl',
            executable='consensus_node',
            name=f'consensus_node_{name}',
            namespace=name,
            output='screen',
            parameters=[{'robot_id': name}],
        ))

    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_names', default_value="['robot1','robot2','robot3']",
            description="Liste des noms de robots, ex: \"['robot1','robot2']\""
        ),
        DeclareLaunchArgument(
            'drl_mode', default_value='hybrid',
            description="Mode de l'allocateur DRL : 'hybrid' (recommande) ou 'direct'"
        ),
        DeclareLaunchArgument(
            'model_path', default_value='warehouse_dqn.pt',
            description="Chemin vers le modele DQN entraine (.pt)"
        ),
        OpaqueFunction(function=launch_setup),
    ])
