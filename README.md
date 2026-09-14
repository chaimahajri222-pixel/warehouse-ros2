# Warehouse ROS 2 Multi-Robot Project

ROS 2 project for a warehouse environment with TurtleBot3 robots, Gazebo simulation, RViz2, SLAM, TF management and Nav2 navigation.

## Project status

The simulation is currently working in ROS 2 Humble.

The project includes:

- Gazebo warehouse simulation
- TurtleBot3 Waffle robots
- RViz2 visualization
- TF management
- Laser scan relay
- Map / odometry transformation
- Nav2 navigation
- SLAM configuration
- Multi-robot components
- Multi-agent / MARL components

## Architecture

```text
                    ┌─────────────────────┐
                    │       Gazebo        │
                    │  Warehouse World    │
                    │   TurtleBot3(s)     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ warehouse_description│
                    │ Robot models / TF    │
                    │ Sensors / World      │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐       ┌──────────────────┐
       │ warehouse_slam   │       │ TF / Scan tools  │
       │      SLAM        │       │                  │
       └────────┬─────────┘       └────────┬─────────┘
                │                          │
                └────────────┬─────────────┘
                             ▼
                  ┌─────────────────────┐
                  │ warehouse_navigation│
                  │        Nav2         │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │       RViz2         │
                  │ Visualization / Goal│
                  └─────────────────────┘

                  ┌─────────────────────┐
                  │   warehouse_marl    │
                  │ Multi-Agent / DRL    │
                  └─────────────────────┘
