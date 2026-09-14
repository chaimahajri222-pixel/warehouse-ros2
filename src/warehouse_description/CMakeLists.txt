cmake_minimum_required(VERSION 3.8)
project(warehouse_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch worlds urdf
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/odom_to_tf.py
  scripts/scan_relay.py
  scripts/map_to_odom.py
  scripts/base_link_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
