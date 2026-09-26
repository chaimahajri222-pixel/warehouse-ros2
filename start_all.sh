#!/bin/bash

# 1. Fenêtre Simulation & Gazebo Harmonic + Nav2
gnome-terminal --title="1. Simulation Gazebo & Nav2" -- bash -c \
  "cd ~/warehouse-ros2; source /opt/ros/jazzy/setup.bash; source .venv/bin/activate; source install/setup.bash; ros2 launch rosnav_bot multi_robot.launch.py world:=warehouse robot_count:=2 explore:=true slam_mode:=single merge_scans:=true fleet_mgmt:=false; exec bash"

echo "Patientez pendant l'initialisation de Gazebo et Nav2 (15 secondes)..."
sleep 15

# 2. Fenêtre Coordination MARL (Task Allocator & Mission Executor)
gnome-terminal --title="2. Coordination MARL" -- bash -c \
  "cd ~/warehouse-ros2; source /opt/ros/jazzy/setup.bash; source .venv/bin/activate; source install/setup.bash; ros2 launch warehouse_marl warehouse_marl.launch.py robot_names:=\"['robot1','robot2']\" drl_mode:=heuristic; exec bash"

# 3. Fenêtre Moniteur de Statut des Tâches
gnome-terminal --title="3. Moniteur de Missions" -- bash -c \
  "cd ~/warehouse-ros2; source /opt/ros/jazzy/setup.bash; source .venv/bin/activate; source install/setup.bash; ros2 topic echo /warehouse/tasks/status; exec bash"
