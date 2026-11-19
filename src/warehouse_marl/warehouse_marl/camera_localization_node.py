"""
camera_localization_node.py
---------------------------
Module de localisation externe par cameras au plafond, sur le modele de
Yumbla et al., "An Open-Source Multi-Robot Framework System for
Collaborative Environments Based on ROS2", IEEE Access 13 (2025),
section III-A et IV-A.

Dans l'article, des cameras fixes (3,5 m de haut) detectent des marqueurs
ArUco poses sur les robots ; un filtre garde la detection de la camera la
plus proche ; la pose obtenue est publiee comme ``initialpose`` de l'AMCL
du robot pour corriger sa localisation, a l'initialisation et apres chaque
tache terminee ou echouee. Erreur mesuree dans l'article : 0,0244 m en XY,
0,29 deg en lacet (Table 1).

Ici les cameras sont SIMULEES : le noeud lit la pose reelle des robots dans
Gazebo (/world/<monde>/dynamic_pose/info, via gz-transport), ne garde que
les robots situes dans le champ d'au moins une camera, et ajoute un bruit
gaussien de l'ordre de celui de l'article. Il n'y a ni rendu d'image ni
detection ArUco (trop couteux sur la machine de test) : seule la sortie du
module de l'article est reproduite, pas sa chaine de traitement d'image.

Sorties :
  /camera_localization/poses        std_msgs/String (JSON), poses vues par
                                    les cameras, repere map ; consommees par
                                    fleet_obstacles (rosnav_bot) et le
                                    tableau de bord.
  /<robot>/initialpose              geometry_msgs/PoseWithCovarianceStamped,
                                    correction de l'AMCL du robot.
  /camera_localization/corrections  std_msgs/String (JSON), une ligne par
                                    correction (robot, motif, ecart corrige).

Corrections (comme l'article, plus un garde-fou) :
  - au demarrage, des que le robot est vu et localise ;
  - a chaque fin de tache (succeeded, failed, retrying, canceled) ;
  - quand l'ecart entre la pose AMCL et la pose camera depasse
    ``drift_threshold`` (m) ou ``yaw_threshold_deg`` pendant
    ``drift_persist`` controles consecutifs.

Repere : la carte (map) a son origine au point de depart de robot1 :
map = monde - (spawn_x, spawn_y), sans rotation (multi_robot.launch.py).
"""

import json
import math
import random
import threading

import rclpy
import tf2_ros
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

try:
    from gz.transport13 import Node as GzNode
    from gz.msgs10.pose_v_pb2 import Pose_V
except ImportError:  # pragma: no cover - depend de l'installation Gazebo
    GzNode = None
    Pose_V = None

END_STATES = ('succeeded', 'failed', 'retrying', 'canceled')


def _yaw(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def _angle_diff(a, b):
    return math.atan2(math.sin(a - b), math.cos(a - b))


class CameraLocalizationNode(Node):

    def __init__(self):
        super().__init__('camera_localization')
        self.declare_parameter('robot_names', ['robot1', 'robot2', 'robot3'])
        self.declare_parameter('world_name', 'warehouse')
        # Origine de la carte dans le monde Gazebo (= depart de robot1).
        self.declare_parameter('spawn_x', -2.0)
        self.declare_parameter('spawn_y', -1.0)
        # Cameras : liste plate [x1, y1, x2, y2, ...] dans le monde. Vide =
        # grille reguliere couvrant coverage_bounds avec camera_spacing.
        self.declare_parameter('cameras', [0.0])
        self.declare_parameter('coverage_bounds', [-12.0, 17.0, -10.0, 10.0])
        self.declare_parameter('camera_spacing', 5.0)
        # Rayon au sol vu par une camera a 3,5 m (champ ~90 deg).
        self.declare_parameter('camera_radius', 3.6)
        # Bruit de mesure (article, Table 1 : 0,0244 m, 0,29 deg).
        self.declare_parameter('noise_xy', 0.025)
        self.declare_parameter('noise_yaw_deg', 0.3)
        self.declare_parameter('rate_hz', 5.0)
        self.declare_parameter('correct', True)
        self.declare_parameter('correct_on_task_end', True)
        self.declare_parameter('drift_threshold', 0.30)
        self.declare_parameter('yaw_threshold_deg', 10.0)
        self.declare_parameter('drift_persist', 3)
        self.declare_parameter('correction_cooldown', 4.0)
        # Robots dont la localisation ne doit pas etre corrigee (robot SLAM).
        self.declare_parameter('skip_correction', [''])
        self.declare_parameter('seed', 7)

        gp = self.get_parameter
        self.robots = list(gp('robot_names').value)
        self.ox = float(gp('spawn_x').value)
        self.oy = float(gp('spawn_y').value)
        self.radius = float(gp('camera_radius').value)
        self.noise_xy = float(gp('noise_xy').value)
        self.noise_yaw = math.radians(float(gp('noise_yaw_deg').value))
        self.correct = bool(gp('correct').value)
        self.on_task_end = bool(gp('correct_on_task_end').value)
        self.drift = float(gp('drift_threshold').value)
        self.yaw_thr = math.radians(float(gp('yaw_threshold_deg').value))
        self.persist = int(gp('drift_persist').value)
        self.cooldown = float(gp('correction_cooldown').value)
        self.skip = {s for s in gp('skip_correction').value if s}
        self.rng = random.Random(int(gp('seed').value))
        self.cameras = self._cameras()

        self._lock = threading.Lock()
        self._truth = {}            # robot -> (x_monde, y_monde, yaw, stamp_ns)
        self._drift_count = {r: 0 for r in self.robots}
        self._last_corr = {}        # robot -> temps ROS (s) de la derniere correction
        self._initialised = set()
        self._pending = {}          # robot -> motif (fin de tache)
        self.n_corr = 0

        self.tf = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf, self)
        self.poses_pub = self.create_publisher(String, '/camera_localization/poses', 10)
        self.corr_pub = self.create_publisher(String, '/camera_localization/corrections', 10)
        self.init_pubs = {
            r: self.create_publisher(PoseWithCovarianceStamped, f'/{r}/initialpose', 5)
            for r in self.robots}
        self.create_subscription(String, '/warehouse/tasks/status', self._on_status, 50)

        if GzNode is None:
            self.get_logger().error(
                'gz.transport13 introuvable : la localisation par cameras est inactive.')
            self._gz = None
        else:
            self._gz = GzNode()
            topic = f'/world/{gp("world_name").value}/dynamic_pose/info'
            if not self._gz.subscribe(Pose_V, topic, self._on_gz):
                self.get_logger().error(f'abonnement Gazebo impossible : {topic}')
        self.create_timer(1.0 / float(gp('rate_hz').value), self._tick)
        self.get_logger().info(
            f'Localisation par cameras : {len(self.cameras)} cameras simulees '
            f'(rayon {self.radius:.1f} m, bruit {self.noise_xy:.3f} m / '
            f'{math.degrees(self.noise_yaw):.2f} deg), correction AMCL '
            f'{"active" if self.correct else "inactive"}'
            f'{" sauf " + ",".join(sorted(self.skip)) if self.skip else ""}.')

    # ------------------------------------------------------------------ cameras
    def _cameras(self):
        flat = [float(v) for v in self.get_parameter('cameras').value]
        if len(flat) >= 2 and len(flat) % 2 == 0:
            return [(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]
        x0, x1, y0, y1 = [float(v) for v in self.get_parameter('coverage_bounds').value]
        step = float(self.get_parameter('camera_spacing').value)
        nx = max(1, int(math.ceil((x1 - x0) / step)))
        ny = max(1, int(math.ceil((y1 - y0) / step)))
        dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
        return [(x0 + (i + 0.5) * dx, y0 + (j + 0.5) * dy)
                for i in range(nx) for j in range(ny)]

    def _nearest_camera(self, x, y):
        best, best_d = None, math.inf
        for k, (cx, cy) in enumerate(self.cameras):
            d = math.hypot(x - cx, y - cy)
            if d < best_d:
                best, best_d = k, d
        return (best, best_d) if best_d <= self.radius else (None, best_d)

    # ------------------------------------------------------------------ entrees
    def _on_gz(self, msg):
        stamp_ns = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nsec
        poses = {}
        for p in msg.pose:
            if p.name in self.init_pubs:
                poses[p.name] = (p.position.x, p.position.y, _yaw(p.orientation), stamp_ns)
        if poses:
            with self._lock:
                self._truth.update(poses)

    def _on_status(self, msg):
        if not self.on_task_end:
            return
        try:
            d = json.loads(msg.data)
        except ValueError:
            return
        robot, state = d.get('robot_id', ''), d.get('state', '')
        if robot in self.init_pubs and state in END_STATES:
            self._pending[robot] = f'fin de tache ({state})'

    def _estimate(self, robot):
        try:
            t = self.tf.lookup_transform('map', f'{robot}/base_link', rclpy.time.Time())
        except Exception:
            return None
        return (t.transform.translation.x, t.transform.translation.y, _yaw(t.transform.rotation))

    # ------------------------------------------------------------------ boucle
    def _tick(self):
        with self._lock:
            truth = dict(self._truth)
        if not truth:
            return
        now_s = self.get_clock().now().nanoseconds * 1e-9
        seen = {}
        for r, (wx, wy, wyaw, stamp_ns) in truth.items():
            cam, _ = self._nearest_camera(wx, wy)
            if cam is None:
                continue
            mx = wx - self.ox + self.rng.gauss(0.0, self.noise_xy)
            my = wy - self.oy + self.rng.gauss(0.0, self.noise_xy)
            myaw = wyaw + self.rng.gauss(0.0, self.noise_yaw)
            seen[r] = {'x': round(mx, 4), 'y': round(my, 4), 'yaw': round(myaw, 4),
                       'camera': cam, 'stamp_ns': stamp_ns}
        self.poses_pub.publish(String(data=json.dumps(
            {'frame': 'map', 'time': round(now_s, 3), 'robots': seen})))
        if not self.correct:
            return
        for r, cam_pose in seen.items():
            if r in self.skip:
                continue
            est = self._estimate(r)
            if est is None:
                continue
            err = math.hypot(est[0] - cam_pose['x'], est[1] - cam_pose['y'])
            yaw_err = abs(_angle_diff(est[2], cam_pose['yaw']))
            reason = None
            if r not in self._initialised:
                reason = 'initialisation'
            elif r in self._pending:
                reason = self._pending[r]
            elif err > self.drift or yaw_err > self.yaw_thr:
                self._drift_count[r] += 1
                if self._drift_count[r] >= self.persist:
                    reason = f'derive {err:.2f} m / {math.degrees(yaw_err):.0f} deg'
            else:
                self._drift_count[r] = 0
            if reason is None:
                continue
            if now_s - self._last_corr.get(r, -math.inf) < self.cooldown:
                continue
            self._publish_correction(r, cam_pose, reason, err, yaw_err, now_s)

    def _publish_correction(self, robot, cam_pose, reason, err, yaw_err, now_s):
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        # Horodatage de la mesure (temps simule de Gazebo) : l'AMCL de Nav2
        # reporte la pose a l'instant present avec l'odometrie.
        ns = cam_pose['stamp_ns']
        msg.header.stamp.sec = ns // 1_000_000_000
        msg.header.stamp.nanosec = ns % 1_000_000_000
        msg.pose.pose.position.x = cam_pose['x']
        msg.pose.pose.position.y = cam_pose['y']
        msg.pose.pose.orientation.z = math.sin(cam_pose['yaw'] / 2.0)
        msg.pose.pose.orientation.w = math.cos(cam_pose['yaw'] / 2.0)
        var_xy = max(self.noise_xy, 0.02) ** 2
        var_yaw = max(self.noise_yaw, math.radians(1.0)) ** 2
        msg.pose.covariance[0] = var_xy
        msg.pose.covariance[7] = var_xy
        msg.pose.covariance[35] = var_yaw
        self.init_pubs[robot].publish(msg)
        self._initialised.add(robot)
        self._pending.pop(robot, None)
        self._drift_count[robot] = 0
        self._last_corr[robot] = now_s
        self.n_corr += 1
        self.corr_pub.publish(String(data=json.dumps({
            'time': round(now_s, 3), 'robot': robot, 'reason': reason,
            'error_m': round(err, 3), 'yaw_error_deg': round(math.degrees(yaw_err), 1),
            'camera': cam_pose['camera']})))
        self.get_logger().info(
            f'{robot} : pose corrigee par la camera {cam_pose["camera"]} ({reason}, '
            f'ecart {err:.2f} m / {math.degrees(yaw_err):.0f} deg).')


def main(args=None):
    rclpy.init(args=args)
    node = CameraLocalizationNode()
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
