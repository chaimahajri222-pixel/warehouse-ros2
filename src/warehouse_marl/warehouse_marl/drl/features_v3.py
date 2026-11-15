"""
features_v3.py
--------------
Caracteristiques RELATIVES du DRL v3, calculees sur l'ensemble des couples
(robot libre, tache candidate) d'une meme decision.

Par rapport a features_v2 :
  - les couts sont normalises par le DIAMETRE du graphe (plus long plus
    court chemin, aretes non bloquees) et non par 20 m : un modele entraine
    sur 15 racks voit des valeurs comparables sur 150 racks ;
  - rang du cout et ecart au cout minimal (sur tous les couples, pour la
    tache, pour le robot), rang d'age des taches : le reseau compare les
    couples entre eux au lieu de lire des valeurs absolues ;
  - vitesse du robot et temps de trajet (robots heterogenes), marge par
    rapport au delai de la tache, taille de l'entrepot.

La caracteristique 0 (cout / diametre, inaccessible = 50 m comme en v2) sert
de terme de base au Q residuel (drl/residual_dqn.py) : Q = -cout + correction.
Avec une correction nulle, l'argmax est exactement le choix de greedy_pair.

Aucune caracteristique ne depend de l'index ou du nom d'un robot (rangs
avec ex-aequo moyennes). Pas de dependance a ROS 2 ni a PyTorch.
"""

from __future__ import annotations

import heapq
import math
from typing import Dict, List, Optional, Sequence

from warehouse_marl.drl.features_v2 import AGE_NORM, finite_cost

FEATURE_NAMES_V3 = (
    'cout_diametre',          # 0  cout du chemin / diametre (base du Q residuel)
    'accessible',             # 1  1 si un chemin existe
    'temps_trajet_rel',       # 2  (cout / vitesse) / (diametre / vitesse moyenne)
    'vitesse_rel',            # 3  vitesse du robot / vitesse moyenne de la flotte
    'rang_cout',              # 4  rang du cout parmi tous les couples (0 = moins cher)
    'ecart_cout_min',         # 5  (cout - cout min. de tous les couples) / diametre
    'ecart_cout_min_tache',   # 6  (cout - cout min. pour cette tache) / diametre
    'ecart_temps_min_tache',  # 7  (temps - temps min. pour cette tache), relatif
    'ecart_cout_min_robot',   # 8  (cout - cout min. de ce robot) / diametre
    'rang_age',               # 9  rang d'age de la tache (0 = la plus ancienne)
    'age_tache',              # 10 age / 60 s
    'priorite',               # 11 priorite / 2
    'marge_delai',            # 12 (delai restant - trajet - prelevement) / 60 s
    'congestion_chemin',      # 13 somme des congestions du chemin / 3
    'part_robots_libres',     # 14 robots libres / flotte
    'file_par_robot',         # 15 taches en attente / flotte
    'charge_robot',           # 16 taches actives / max_active
    'taille_entrepot',        # 17 diametre / 100 m
)
N_FEATURES_V3 = len(FEATURE_NAMES_V3)
FEATURE_VERSION_V3 = 'v3'

_DIAMETER_CACHE: Dict[tuple, float] = {}


def _clip(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def graph_diameter(graph) -> float:
    """Plus long des plus courts chemins (poids de base, blocages ignores)."""
    G = graph.G
    key = (len(G.nodes), len(G.edges),
           round(sum(G.nodes[n]['x'] for n in G.nodes), 3),
           round(sum(G.nodes[n]['y'] for n in G.nodes), 3))
    if key in _DIAMETER_CACHE:
        return _DIAMETER_CACHE[key]
    best = 0.0
    for src in G.nodes:
        dist = {src: 0.0}
        heap = [(0.0, src)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            for v in G._adj[u]:
                nd = d + G[u][v]['base_weight']
                if nd < dist.get(v, math.inf):
                    dist[v] = nd
                    heapq.heappush(heap, (nd, v))
        best = max(best, max(dist.values()))
    _DIAMETER_CACHE[key] = max(best, 1.0)
    return _DIAMETER_CACHE[key]


def _avg_rank(values: Sequence[float]) -> List[float]:
    """Rang dans [0, 1] (0 = plus petit), ex-aequo au rang moyen."""
    n = len(values)
    if n <= 1:
        return [0.0] * n
    out = []
    for v in values:
        below = sum(1 for w in values if w < v)
        equal = sum(1 for w in values if w == v) - 1
        out.append((below + 0.5 * equal) / (n - 1))
    return out


def decision_features(pairs: Sequence[Dict], tasks: Dict[str, Dict], n_robots: int,
                      n_free: int, queue_len: int, diameter: float, mean_speed: float,
                      max_active: int, pick_time: float) -> List[List[float]]:
    """Caracteristiques v3 de chaque couple d'une decision.

    ``pairs`` : dicts {robot, task, cost (peut etre +inf), speed, congestion,
    load} ; ``tasks`` : task_id -> {age, priority, due_in (s ou None)}.
    """
    if not pairs:
        return []
    diam = max(diameter, 1.0)
    t_norm = diam / max(mean_speed, 1e-6)
    costs = [finite_cost(p['cost']) for p in pairs]
    times = [c / max(p['speed'], 1e-6) for c, p in zip(costs, pairs)]
    rank_cost = _avg_rank(costs)
    min_all = min(costs)
    min_task: Dict[str, float] = {}
    min_time_task: Dict[str, float] = {}
    min_robot: Dict[str, float] = {}
    for c, t, p in zip(costs, times, pairs):
        min_task[p['task']] = min(min_task.get(p['task'], math.inf), c)
        min_time_task[p['task']] = min(min_time_task.get(p['task'], math.inf), t)
        min_robot[p['robot']] = min(min_robot.get(p['robot'], math.inf), c)
    task_ids = list(tasks)
    age_rank = dict(zip(task_ids, _avg_rank([-tasks[k]['age'] for k in task_ids])))
    n = max(n_robots, 1)
    out = []
    for c, t, rc, p in zip(costs, times, rank_cost, pairs):
        k = tasks[p['task']]
        due_in = k.get('due_in')
        margin = 0.0 if due_in is None else _clip((due_in - t - pick_time) / AGE_NORM, -5.0, 5.0)
        out.append([
            c / diam,
            0.0 if math.isinf(p['cost']) else 1.0,
            _clip(t / t_norm, 0.0, 10.0),
            p['speed'] / max(mean_speed, 1e-6),
            rc,
            (c - min_all) / diam,
            (c - min_task[p['task']]) / diam,
            _clip((t - min_time_task[p['task']]) / t_norm, 0.0, 10.0),
            (c - min_robot[p['robot']]) / diam,
            age_rank[p['task']],
            _clip(k['age'] / AGE_NORM, 0.0, 10.0),
            k['priority'] / 2.0,
            margin,
            _clip(p['congestion'] / 3.0, 0.0, 5.0),
            n_free / n,
            _clip(queue_len / n, 0.0, 5.0),
            _clip(p['load'] / max(max_active, 1), 0.0, 2.0),
            diam / 100.0,
        ])
    return out


def due_in(due: Optional[float], now: float) -> Optional[float]:
    return None if due is None else due - now
