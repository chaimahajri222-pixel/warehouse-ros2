import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node

def generate_launch_description():
    # Chemins des packages
    pkg_warehouse_bringup = get_package_share_directory('warehouse_bringup')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Fichier de monde (Warehouse)
    world_file = os.path.join(pkg_warehouse_bringup, 'worlds', 'warehouse.sdf')
    
    # Si le fichier warehouse.sdf n'existe pas dans warehouse_bringup, on utilise empty.sdf
    if not os.path.exists(world_file):
        world_arg = '-r empty.sdf'
    else:
        world_arg = f'-r {world_file}'

    # Arguments de lancement
    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Activer l interface graphique Gazebo (true/false)'
    )

    # Démarrage de Gazebo Sim avec le monde entrepôt
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': world_arg}.items(),
    )

    # Pont (Bridge) de communication entre ROS 2 et Gazebo Sim
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen'
    )

    return LaunchDescription([
        gui_arg,
        gazebo,
        ros_gz_bridge
    ])
