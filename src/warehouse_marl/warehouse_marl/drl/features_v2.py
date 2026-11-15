"""
features_v2.py
--------------
Caracteristiques "par couple (robot libre, tache candidate)" du DRL v2.

Une seule fonction pure (``pair_features``) construit le vecteur ; elle est
utilisee a l'identique par :
  - drl/env_v2.py            (entrainement, simulation allocation_benchmark) ;
  - allocation_benchmark.py  (methodes drl2_hybrid / drl2_direct) ;
  - drl_allocator_node.py    (deploiement ROS 2, obs_version='v2').

Aucune caracteristique ne depend de l'index ou du nom du robot : le reseau
Q(couple) a une seule sortie et s'applique a n'importe quelle taille de
flotte (3, 4, 20 robots...). Pas de dependance a ROS 2 ni a PyTorch.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Sequence

FEATURE_NAMES = (
    'cout_chemin',            # cout dynamique robot -> cible / 20 (50 m si inaccessible)
    'accessible',             # 1 si un chemin existe, 0 sinon
    'congestion_chemin',      # somme des congestions des aretes du chemin / 3
    'age_tache',              # (t - creation) / 60 s
    'priorite',               # priorite / 2
    'part_robots_libres',     # robots libres / taille de la flotte
    'file_par_robot',         # taches en attente / taille de la flotte
    'cout_concurrent',        # cout du robot libre concurrent le plus proche / 20
    'avantage_concurrent',    # (cout concurrent - cout) / 20
    'cout_alternative',       # cout de ce robot vers une autre tache candidate / 20
    'charge_robot',           # taches actives du robot / max_active
)
N_FEATURES = len(FEATURE_NAMES)

COST_NORM = 20.0           # m
UNREACHABLE_COST = 50.0    # m, comme l'observation v1
AGE_NORM = 60.0            # s
FEATURE_VERSION = 'v2'


def _clip(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def finite_cost(cost: float) -> float:
    return UNREACHABLE_COST if cost is None or math.isinf(cost) else cost


def pair_features(cost: float, path_congestion: float, age_s: float, priority: float,
                  n_free: int, n_robots: int, queue_len: int,
                  competitor_cost: Optional[float], alt_cost: Optional[float],
                  load: int, max_active: int) -> List[float]:
    """Vecteur de ``N_FEATURES`` valeurs pour un couple (robot, tache).

    ``cost`` peut valoir +inf (cible inaccessible). ``competitor_cost`` /
    ``alt_cost`` valent None s'il n'y a pas d'autre robot libre / d'autre
    tache candidate.
    """
    reachable = not math.isinf(cost)
    c = finite_cost(cost)
    comp = finite_cost(competitor_cost if competitor_cost is not None else math.inf)
    alt = finite_cost(alt_cost if alt_cost is not None else math.inf)
    n = max(n_robots, 1)
    return [
        c / COST_NORM,
        1.0 if reachable else 0.0,
        _clip(path_congestion / 3.0, 0.0, 5.0),
        _clip(age_s / AGE_NORM, 0.0, 10.0),
        priority / 2.0,
        n_free / n,
        _clip(queue_len / n, 0.0, 5.0),
        comp / COST_NORM,
        _clip((comp - c) / COST_NORM, -2.5, 2.5),
        alt / COST_NORM,
        _clip(load / max(max_active, 1), 0.0, 2.0),
    ]


def features_for_robots(robots: Sequence[str], free: Iterable[str], task: Dict,
                        tasks: Sequence[Dict], cost, congestion, load: Dict[str, int],
                        n_robots: int, queue_len: int, max_active: int,
                        now: float) -> Dict[str, List[float]]:
    """Caracteristiques de ``task`` pour chaque robot de ``robots``.

    ``cost(robot, target)`` et ``congestion(robot, target)`` sont des
    fonctions fournies par l'appelant (simulation ou noeud ROS) ; ``tasks``
    est la liste des taches candidates (dict avec 'id', 'target',
    'priority', 'created') ; ``free`` l'ensemble des robots libres.
    """
    free = list(free)
    out = {}
    for r in robots:
        c = cost(r, task['target'])
        others = [cost(o, task['target']) for o in free if o != r]
        alts = [cost(r, k['target']) for k in tasks if k['id'] != task['id']]
        out[r] = pair_features(
            c, congestion(r, task['target']) if not math.isinf(c) else 0.0,
            now - task['created'], task['priority'], len(free), n_robots, queue_len,
            min(others) if others else None, min(alts) if alts else None,
            load.get(r, 0), max_active)
    return out
