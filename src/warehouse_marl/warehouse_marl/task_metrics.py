"""
task_metrics.py
---------------
Mesures des missions dans la simulation complete (Gazebo + Nav2).

1) Noeud ``task_metrics_logger`` : enregistre chaque message de
   /warehouse/tasks/status (publie par mission_executor_node) dans un CSV :
   horodatage mur, temps ROS, mode, task_id, robot, cible, etat,
   elapsed_sec, retries, nav_status, detail.

       ros2 run warehouse_marl task_metrics_logger --ros-args \\
           -p output:=heuristic.csv -p mode_label:=heuristic

2) Script ``summarize_task_metrics`` : synthese d'un ou plusieurs CSV, par
   mode : taches vues, terminees (succeeded), echouees (failed / rejected /
   canceled), encore en cours a la fin, temps moyen creation -> fin des
   taches reussies avec IC 95 % (bootstrap), mediane.

       ros2 run warehouse_marl summarize_task_metrics heuristic.csv hybrid.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import statistics
import time
from typing import Dict, Iterable, List, Optional

FIELDS = ('wall_time', 'ros_time', 'mode', 'task_id', 'robot_id', 'target_node', 'state',
          'elapsed_sec', 'retries', 'nav_status', 'detail')
TERMINAL_OK = ('succeeded',)
TERMINAL_FAIL = ('failed', 'rejected', 'canceled')


def parse_status(text: str, mode: str, wall_time: float) -> Optional[Dict]:
    try:
        d = json.loads(text)
        task_id, state = str(d['task_id']), str(d['state'])
    except (json.JSONDecodeError, KeyError, TypeError):
        return None
    return {'wall_time': round(wall_time, 3), 'ros_time': d.get('stamp', ''), 'mode': mode,
            'task_id': task_id, 'robot_id': d.get('robot_id', ''),
            'target_node': d.get('target_node', ''), 'state': state,
            'elapsed_sec': d.get('elapsed_sec', ''), 'retries': d.get('retries', ''),
            'nav_status': d.get('nav_status', ''), 'detail': d.get('detail', '')}


def _ci(xs: List[float], n: int = 2000, seed: int = 0):
    if len(xs) < 2:
        return (math.nan, math.nan)
    rng = random.Random(seed)
    means = sorted(statistics.mean(rng.choices(xs, k=len(xs))) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


def summarize(rows: Iterable[Dict]) -> List[Dict]:
    """Une ligne par mode. L'etat final d'une tache est son dernier etat
    terminal (sinon : en cours a la fin de l'enregistrement)."""
    by_mode: Dict[str, Dict[str, Dict]] = {}
    for r in rows:
        tasks = by_mode.setdefault(r['mode'], {})
        t = tasks.setdefault(r['task_id'], {'final': None, 'elapsed': None, 'robot': ''})
        if r['state'] in TERMINAL_OK + TERMINAL_FAIL:
            t['final'] = r['state']
            t['robot'] = r.get('robot_id', '')
            try:
                t['elapsed'] = float(r['elapsed_sec'])
            except (TypeError, ValueError):
                t['elapsed'] = None
    out = []
    for mode, tasks in by_mode.items():
        ok = [t['elapsed'] for t in tasks.values()
              if t['final'] in TERMINAL_OK and t['elapsed'] is not None]
        lo, hi = _ci(ok)
        out.append({
            'mode': mode, 'taches_vues': len(tasks),
            'terminees': sum(1 for t in tasks.values() if t['final'] in TERMINAL_OK),
            'echouees': sum(1 for t in tasks.values() if t['final'] in TERMINAL_FAIL),
            'en_cours_a_la_fin': sum(1 for t in tasks.values() if t['final'] is None),
            'temps_moyen_s': round(statistics.mean(ok), 2) if ok else math.nan,
            'ic95_bas_s': round(lo, 2), 'ic95_haut_s': round(hi, 2),
            'temps_median_s': round(statistics.median(ok), 2) if ok else math.nan,
            'robots': ','.join(sorted({t['robot'] for t in tasks.values() if t['robot']})),
        })
    return out


def read_csv(path: str) -> List[Dict]:
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def summarize_main(argv=None):
    p = argparse.ArgumentParser(description='Synthese des CSV de task_metrics_logger.')
    p.add_argument('csv', nargs='+')
    p.add_argument('--out', default='', help='CSV de synthese (optionnel)')
    args = p.parse_args(argv)
    rows = [r for path in args.csv for r in read_csv(path)]
    table = summarize(rows)
    for r in table:
        print(f"  {r['mode']:12s} vues {r['taches_vues']:4d}  terminees {r['terminees']:4d}  "
              f"echouees {r['echouees']:3d}  en cours {r['en_cours_a_la_fin']:3d}  "
              f"temps moyen {r['temps_moyen_s']} s [{r['ic95_bas_s']} ; {r['ic95_haut_s']}]  "
              f"median {r['temps_median_s']} s")
    if args.out:
        with open(args.out, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(table[0]) if table else ['mode'])
            w.writeheader()
            w.writerows(table)
        print(f'Synthese : {args.out}')
    return table


def logger_main(args=None):
    import rclpy
    from rclpy.executors import ExternalShutdownException
    from rclpy.node import Node
    from std_msgs.msg import String

    class TaskMetricsLogger(Node):
        def __init__(self):
            super().__init__('task_metrics_logger')
            self.declare_parameter('output', 'task_metrics.csv')
            self.declare_parameter('mode_label', 'inconnu')
            path = str(self.get_parameter('output').value)
            self.mode = str(self.get_parameter('mode_label').value)
            new = not os.path.exists(path) or os.path.getsize(path) == 0
            self._file = open(path, 'a', newline='')
            self._writer = csv.DictWriter(self._file, fieldnames=FIELDS)
            if new:
                self._writer.writeheader()
            self.count = 0
            self.create_subscription(String, '/warehouse/tasks/status', self._on_status, 50)
            self.get_logger().info(f'Statuts de taches -> {path} (mode {self.mode})')

        def _on_status(self, msg):
            row = parse_status(msg.data, self.mode, time.time())
            if row is None:
                return
            self._writer.writerow(row)
            self._file.flush()
            self.count += 1

        def close(self):
            self._file.close()

    rclpy.init(args=args)
    node = TaskMetricsLogger()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
