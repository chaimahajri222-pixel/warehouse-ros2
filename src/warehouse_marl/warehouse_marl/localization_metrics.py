"""
localization_metrics.py
-----------------------
Mesures dans Gazebo pour comparer la flotte avec et sans le module de
localisation par cameras (camera_localization_node), dans l'esprit des
tests de Yumbla et al. (IEEE Access 2025, section IV) :

  A. localisation : erreur entre la pose estimee (TF map -> <robot>/base_link)
     et la pose reelle dans Gazebo (ramenee au repere map) ;
  B. navigation sans collision : ecart minimal entre les carrosseries des
     robots (poses Gazebo), nombre de contacts et de quasi-contacts ;
  C. taches : etats finaux publies sur /warehouse/tasks/status ;
  + corrections envoyees par les cameras (/camera_localization/corrections).

    ros2 run warehouse_marl localization_metrics --ros-args \
        -p output_dir:=/chemin -p label:=cameras -p duration:=900.0

Sorties dans output_dir : loc_<label>.csv (erreurs, 5 Hz), gaps_<label>.csv
(ecart par paire, 5 Hz), contacts_<label>.csv (un episode par ligne),
synthese_<label>.json. La synthese est ecrite a la fin (duration atteinte
ou Ctrl+C).
"""

import csv
import json
import math
import os
import statistics
import threading
import time

import rclpy
import tf2_ros
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

try:
    from gz.transport13 import Node as GzNode
    from gz.msgs10.pose_v_pb2 import Pose_V
except ImportError:  # pragma: no cover
    GzNode = None
    Pose_V = None

# Carrosserie dans base_link (robot_core.xacro), comme fleet_obstacles.py.
BODY = [(0.46, 0.25), (0.46, -0.25), (-0.28, -0.25), (-0.28, 0.25)]
CONTACT = 0.02      # m : carrosseries en contact (resolution de la mesure)
NEAR = 0.15         # m : quasi-contact
FINAL = ('succeeded', 'failed', 'rejected', 'canceled')


def _yaw(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def _poly(x, y, yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    return [(x + c * bx - s * by, y + s * bx + c * by) for bx, by in BODY]


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def _inside(p, poly):
    sign = None
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        cr = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        if sign is None:
            sign = cr > 0
        elif (cr > 0) != sign:
            return False
    return True


def body_gap(pa, pb):
    """Ecart (m) entre deux carrosseries rectangulaires ; 0 si elles se chevauchent."""
    P, Q = _poly(*pa), _poly(*pb)
    if any(_inside(p, Q) for p in P) or any(_inside(q, P) for q in Q):
        return 0.0
    d = math.inf
    for A, B in ((P, Q), (Q, P)):
        for p in A:
            for i in range(len(B)):
                d = min(d, _seg_dist(p, B[i], B[(i + 1) % len(B)]))
    return d


def _stats(values):
    if not values:
        return None
    v = sorted(values)
    return {
        'n': len(v),
        'moyenne': round(statistics.fmean(v), 3),
        'mediane': round(statistics.median(v), 3),
        'p95': round(v[min(len(v) - 1, int(0.95 * len(v)))], 3),
        'max': round(v[-1], 3),
    }


class LocalizationMetrics(Node):

    def __init__(self):
        super().__init__('localization_metrics')
        self.declare_parameter('robot_names', ['robot1', 'robot2', 'robot3'])
        self.declare_parameter('world_name', 'warehouse')
        self.declare_parameter('map_origin_x', -1.5)
        self.declare_parameter('map_origin_y', -1.0)
        self.declare_parameter('output_dir', os.path.expanduser('~/warehouse_ws/mesures_cameras'))
        self.declare_parameter('label', 'run')
        anynum = ParameterDescriptor(dynamic_typing=True)   # 900 ou 900.0
        self.declare_parameter('duration', 0.0, anynum)  # s (horloge murale) ; 0 = jusqu'a Ctrl+C
        self.declare_parameter('warmup', 0.0, anynum)    # s ignorees au debut (demarrage Nav2)
        gp = self.get_parameter
        self.robots = list(gp('robot_names').value)
        self.ox = float(gp('map_origin_x').value)
        self.oy = float(gp('map_origin_y').value)
        self.out = str(gp('output_dir').value)
        self.label = str(gp('label').value)
        self.duration = float(gp('duration').value)
        self.warmup = float(gp('warmup').value)
        os.makedirs(self.out, exist_ok=True)

        self._lock = threading.Lock()
        self._truth = {}
        self.t0 = time.time()
        self.loc_err = {r: [] for r in self.robots}
        self.yaw_err = {r: [] for r in self.robots}
        pairs = [(a, b) for i, a in enumerate(self.robots) for b in self.robots[i + 1:]]
        self.pairs = pairs
        self.min_gap = {f'{a}-{b}': math.inf for a, b in pairs}
        self.in_contact = {k: False for k in self.min_gap}
        self.in_near = {k: False for k in self.min_gap}
        self.n_contact = {k: 0 for k in self.min_gap}
        self.n_near = {k: 0 for k in self.min_gap}
        self.tasks = {}
        self.corrections = []

        self.loc_f = open(os.path.join(self.out, f'loc_{self.label}.csv'), 'w', newline='')
        self.loc_w = csv.writer(self.loc_f)
        self.loc_w.writerow(['t', 'robot', 'x_reel', 'y_reel', 'x_estime', 'y_estime',
                             'erreur_m', 'erreur_lacet_deg'])
        self.gap_f = open(os.path.join(self.out, f'gaps_{self.label}.csv'), 'w', newline='')
        self.gap_w = csv.writer(self.gap_f)
        self.gap_w.writerow(['t', 'paire', 'ecart_m'])
        self.con_f = open(os.path.join(self.out, f'contacts_{self.label}.csv'), 'w', newline='')
        self.con_w = csv.writer(self.con_f)
        self.con_w.writerow(['t', 'paire', 'type', 'xa', 'ya', 'xb', 'yb'])

        self.tf = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf, self)
        self.create_subscription(String, '/warehouse/tasks/status', self._on_status, 50)
        self.create_subscription(String, '/camera_localization/corrections', self._on_corr, 20)
        if GzNode is None:
            raise RuntimeError('gz.transport13 introuvable : mesure impossible')
        self._gz = GzNode()
        self._gz.subscribe(Pose_V, f'/world/{gp("world_name").value}/dynamic_pose/info',
                           self._on_gz)
        self.create_timer(0.2, self._tick)
        self.done = False
        self.get_logger().info(f'Mesures [{self.label}] -> {self.out}')

    def _on_gz(self, msg):
        poses = {}
        for p in msg.pose:
            if p.name in self.loc_err:
                poses[p.name] = (p.position.x, p.position.y, _yaw(p.orientation))
        if poses:
            with self._lock:
                self._truth.update(poses)

    def _on_status(self, msg):
        try:
            d = json.loads(msg.data)
        except ValueError:
            return
        tid, state = d.get('task_id'), d.get('state', '')
        if tid:
            t = self.tasks.setdefault(tid, {'robot': d.get('robot_id', ''), 'final': None})
            if state in FINAL:
                t['final'] = state

    def _on_corr(self, msg):
        try:
            self.corrections.append(json.loads(msg.data))
        except ValueError:
            pass

    def _tick(self):
        el = time.time() - self.t0
        if self.duration > 0 and el >= self.duration:
            self.done = True
            return
        if el < self.warmup:
            return
        with self._lock:
            truth = dict(self._truth)
        t = round(el, 2)
        for r, (wx, wy, wyaw) in truth.items():
            try:
                tr = self.tf.lookup_transform('map', f'{r}/base_link', rclpy.time.Time())
            except Exception:
                continue
            ex, ey = tr.transform.translation.x, tr.transform.translation.y
            mx, my = wx - self.ox, wy - self.oy
            e = math.hypot(ex - mx, ey - my)
            ye = abs(math.degrees(math.atan2(math.sin(_yaw(tr.transform.rotation) - wyaw),
                                             math.cos(_yaw(tr.transform.rotation) - wyaw))))
            self.loc_err[r].append(e)
            self.yaw_err[r].append(ye)
            self.loc_w.writerow([t, r, round(mx, 3), round(my, 3), round(ex, 3), round(ey, 3),
                                 round(e, 3), round(ye, 1)])
        for a, b in self.pairs:
            if a not in truth or b not in truth:
                continue
            k = f'{a}-{b}'
            g = body_gap(truth[a], truth[b])
            self.min_gap[k] = min(self.min_gap[k], g)
            self.gap_w.writerow([t, k, round(g, 3)])
            contact, near = g <= CONTACT, g <= NEAR
            if contact and not self.in_contact[k]:
                self.n_contact[k] += 1
                self._log_episode(t, k, 'contact', truth[a], truth[b])
            elif near and not contact and not self.in_near[k]:
                self.n_near[k] += 1
                self._log_episode(t, k, 'quasi-contact', truth[a], truth[b])
            self.in_contact[k] = contact
            self.in_near[k] = near

    def _log_episode(self, t, k, kind, pa, pb):
        self.con_w.writerow([t, k, kind, round(pa[0] - self.ox, 2), round(pa[1] - self.oy, 2),
                             round(pb[0] - self.ox, 2), round(pb[1] - self.oy, 2)])
        self.con_f.flush()
        self.get_logger().warn(f'{kind} {k} a t={t:.0f} s')

    def summary(self):
        finals = [t['final'] for t in self.tasks.values()]
        reasons = {}
        for c in self.corrections:
            key = c.get('reason', '').split(' ')[0]
            reasons[key] = reasons.get(key, 0) + 1
        corr_err = [c.get('error_m', 0.0) for c in self.corrections
                    if not str(c.get('reason', '')).startswith('initialisation')]
        all_err = [e for r in self.robots for e in self.loc_err[r]]
        return {
            'label': self.label,
            'duree_mesuree_s': round(max(0.0, time.time() - self.t0 - self.warmup), 1),
            'A_localisation_erreur_m': {r: _stats(self.loc_err[r]) for r in self.robots},
            'A_localisation_erreur_m_flotte': _stats(all_err),
            'A_localisation_erreur_lacet_deg': {r: _stats(self.yaw_err[r]) for r in self.robots},
            'B_ecart_min_m': {k: (None if v == math.inf else round(v, 3))
                              for k, v in self.min_gap.items()},
            'B_contacts': sum(self.n_contact.values()),
            'B_contacts_par_paire': self.n_contact,
            'B_quasi_contacts_moins_15cm': sum(self.n_near.values()),
            'C_taches_creees': len(self.tasks),
            'C_taches_reussies': finals.count('succeeded'),
            'C_taches_echouees': finals.count('failed'),
            'C_taches_annulees': finals.count('canceled'),
            'C_taches_non_terminees': finals.count(None),
            'C_reussies_par_robot': {r: sum(1 for t in self.tasks.values()
                                            if t['robot'] == r and t['final'] == 'succeeded')
                                     for r in self.robots},
            'corrections_cameras': len(self.corrections),
            'corrections_par_motif': reasons,
            'ecart_corrige_m': _stats(corr_err),
        }

    def close(self):
        s = self.summary()
        path = os.path.join(self.out, f'synthese_{self.label}.json')
        with open(path, 'w') as f:
            json.dump(s, f, indent=2, ensure_ascii=False)
        for fh in (self.loc_f, self.gap_f, self.con_f):
            fh.close()
        print(json.dumps(s, indent=2, ensure_ascii=False), flush=True)
        print(f'Synthese : {path}', flush=True)


def main(args=None):
    rclpy.init(args=args)
    node = LocalizationMetrics()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.2)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
