#!/usr/bin/env python3
"""
fleet_obstacles.py
------------------
Makes the robots visible to each other in Nav2.

The robots' lidars sit 0.25 m above the floor, while the robot bodies end at
0.225 m: each lidar's beams pass just over the other robots, so the costmaps
did not contain them and robots bumped into each other (pushes corrupt
odometry and make the estimated pose drift away from the real one).

This node shares positions across the fleet: for every robot it publishes a
point cloud of the *other* robots' footprints (``/<robot>/fleet_obstacles``,
``map`` frame), which each robot's costmap obstacle layers consume as an
extra observation source. Started by multi_robot.launch.py.

Costmaps alone react too late when two robots meet (they replan around a
footprint that moves). So the node also publishes, for every robot, a
second cloud ``/<robot>/fleet_priority_obstacles`` in the robot's own
``<robot>/base_link`` frame. It holds only the robots that have priority
over it (order of ``robot_names``: robot1 > robot2 > robot3 ...), and feeds
the robot's collision_monitor ("approach" polygon): a robot slows down and
stops before driving into a robot with higher priority, while that robot
keeps moving and steers around it with its costmaps. robot1's cloud is
always empty. Since the rule is one-way, two robots cannot both wait for
each other (the symmetric version deadlocked, see FIXES.md).

Points that fall inside the receiving robot's own (padded) footprint are
dropped: two bodies cannot overlap, so such points come from a
localization error, and the collision_monitor would otherwise freeze the
robot (every motion "collides" at t=0).

The priority cloud is published at every tick, even when empty: the
collision_monitor stops a robot whose source goes silent.

External poses (``external_pose_topic``, e.g. ``/camera_localization/poses``
from warehouse_marl's camera_localization_node): the robots' own estimates
(AMCL) can drift by a metre or more, so a robot would avoid where another
robot *thinks* it is. With an external source (fixed cameras, as in Yumbla et
al., IEEE Access 2025), each robot receives the other robots at their
*measured* position relative to its own measured position, placed around its
own estimated pose: what the costmaps and the collision_monitor need is the
relative geometry, which is then right even while the robot's own estimate is
off. Robots the cameras do not see fall back to their TF estimate.
"""

import json
import math
import struct

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import String
import tf2_ros

# Robot body in base_link (see robot_core.xacro): x -0.28..0.46, y +/-0.25.
BODY_X = (-0.28, 0.46)
BODY_Y = (-0.25, 0.25)
STEP = 0.08


def _footprint_points():
    pts = []
    nx = int(round((BODY_X[1] - BODY_X[0]) / STEP))
    ny = int(round((BODY_Y[1] - BODY_Y[0]) / STEP))
    for i in range(nx + 1):
        for j in range(ny + 1):
            pts.append((BODY_X[0] + i * (BODY_X[1] - BODY_X[0]) / nx,
                        BODY_Y[0] + j * (BODY_Y[1] - BODY_Y[0]) / ny))
    return pts


class FleetObstaclesNode(Node):

    def __init__(self):
        super().__init__('fleet_obstacles')
        self.declare_parameter('robot_names', ['robot1', 'robot2', 'robot3'])
        self.declare_parameter('rate_hz', 10.0)
        # Same height as the lidar beams (0.175 m in base_link) so the laser
        # clears a robot's old position once it has moved away.
        self.declare_parameter('point_height', 0.175)
        # Priority cloud: margin around the own body inside which points are
        # dropped (>= costmap footprint_padding), and maximum age of another
        # robot's pose (older = robot not localized any more, ignored).
        self.declare_parameter('own_margin', 0.12)
        self.declare_parameter('max_pose_age', 2.0)
        # JSON {"frame": "map", "robots": {name: {x, y, yaw}}}; '' = TF only.
        self.declare_parameter('external_pose_topic', '')
        self.robots = list(self.get_parameter('robot_names').value)
        self.z = float(self.get_parameter('point_height').value)
        self.margin = float(self.get_parameter('own_margin').value)
        self.max_age = float(self.get_parameter('max_pose_age').value)
        self.body = _footprint_points()
        self.external = {}          # robot -> (x, y, yaw, rclpy Time of receipt)
        ext_topic = str(self.get_parameter('external_pose_topic').value).strip()
        if ext_topic:
            self.create_subscription(String, ext_topic, self._on_external, 10)
        self.tf = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf, self)
        self.pubs = {r: self.create_publisher(PointCloud2, f'/{r}/fleet_obstacles', 5)
                     for r in self.robots}
        self.prio_pubs = {
            r: self.create_publisher(PointCloud2, f'/{r}/fleet_priority_obstacles', 5)
            for r in self.robots}
        self.create_timer(1.0 / float(self.get_parameter('rate_hz').value), self._tick)
        self.get_logger().info(
            f'Fleet obstacles for {self.robots} (priority order for the '
            f'collision_monitor: {" > ".join(self.robots)}; poses: '
            f'{"external " + ext_topic + " + TF" if ext_topic else "TF"}).')

    def _on_external(self, msg):
        try:
            robots = json.loads(msg.data).get('robots', {})
        except (ValueError, AttributeError):
            return
        now = self.get_clock().now()
        for r, p in robots.items():
            if r in self.pubs:
                self.external[r] = (float(p['x']), float(p['y']), float(p['yaw']), now)

    def _pose(self, robot):
        try:
            t = self.tf.lookup_transform('map', f'{robot}/base_link', rclpy.time.Time())
        except Exception:
            return None
        q = t.transform.rotation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        stamp = rclpy.time.Time.from_msg(t.header.stamp, clock_type=self.get_clock().clock_type)
        return t.transform.translation.x, t.transform.translation.y, yaw, stamp

    def _tick(self):
        now = self.get_clock().now()
        est = {r: self._pose(r) for r in self.robots}
        est = {r: p for r, p in est.items() if p is not None}
        ext = {r: p for r, p in self.external.items() if self._fresh(p, now)}
        stamp = now.to_msg()
        for i, r in enumerate(self.robots):
            view = self._view(r, est, ext)
            pts = [pt for other, pose in view.items() if other != r
                   for pt in self._body_points(pose)]
            self.pubs[r].publish(self._cloud(pts, stamp))
            higher = [o for o in self.robots[:i] if o in view and self._fresh(view[o], now)]
            pts = self._priority_points(view.get(r), higher, view)
            self.prio_pubs[r].publish(self._cloud(pts, stamp, f'{r}/base_link'))

    def _view(self, robot, est, ext):
        """Poses of all robots as seen in robot's own map frame.

        With an external measure of robot itself, the others are placed by
        their measured offset from it, around robot's estimated pose.
        """
        view = {}
        own_est, own_ext = est.get(robot), ext.get(robot)
        if own_est is not None and own_ext is not None:
            x0, y0, yaw0, _ = own_ext
            x1, y1, yaw1, _ = own_est
            c0, s0 = math.cos(yaw0), math.sin(yaw0)
            c1, s1 = math.cos(yaw1), math.sin(yaw1)
            for o, (x, y, yaw, t) in ext.items():
                dx, dy = x - x0, y - y0
                lx, ly = c0 * dx + s0 * dy, -s0 * dx + c0 * dy      # in robot's frame
                view[o] = (x1 + c1 * lx - s1 * ly, y1 + s1 * lx + c1 * ly,
                           yaw1 + (yaw - yaw0), t)
        else:
            view.update(ext)
        for o, p in est.items():
            view.setdefault(o, p)
        if own_est is not None:
            view[robot] = own_est
        return view

    def _body_points(self, pose):
        x, y, yaw, _ = pose
        c, s = math.cos(yaw), math.sin(yaw)
        return [(x + c * bx - s * by, y + s * bx + c * by) for bx, by in self.body]

    def _fresh(self, pose, now):
        age = (now - pose[3]).nanoseconds
        return age * 1e-9 <= self.max_age

    def _priority_points(self, own, higher, view):
        """Footprints of the higher-priority robots, in the robot's base_link."""
        if own is None or not higher:
            return []
        x0, y0, yaw0, _ = own
        c, s = math.cos(yaw0), math.sin(yaw0)
        out = []
        for other in higher:
            for px, py in self._body_points(view[other]):
                dx, dy = px - x0, py - y0
                bx, by = c * dx + s * dy, -s * dx + c * dy
                if (BODY_X[0] - self.margin <= bx <= BODY_X[1] + self.margin
                        and BODY_Y[0] - self.margin <= by <= BODY_Y[1] + self.margin):
                    continue
                out.append((bx, by))
        return out

    def _cloud(self, pts, stamp, frame='map'):
        msg = PointCloud2()
        msg.header.frame_id = frame
        msg.header.stamp = stamp
        msg.height = 1
        msg.width = len(pts)
        msg.fields = [PointField(name=n, offset=4 * i, datatype=PointField.FLOAT32, count=1)
                      for i, n in enumerate('xyz')]
        msg.is_bigendian = False
        msg.point_step = 12
        msg.row_step = 12 * len(pts)
        msg.is_dense = True
        msg.data = b''.join(struct.pack('<fff', px, py, self.z) for px, py in pts)
        return msg


def main(args=None):
    rclpy.init(args=args)
    node = FleetObstaclesNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
