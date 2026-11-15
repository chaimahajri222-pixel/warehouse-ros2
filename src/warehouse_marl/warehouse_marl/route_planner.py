"""
route_planner.py
----------------
Routes sur le graphe de l'entrepot pour mission_executor_node (etape 3 du
protocole v4), sans dependance ROS :

  - plan_route(..., mode='dijkstra') : plus court chemin du graphe dynamique
    (couts en direct, aretes bloquees exclues) ;
  - plan_route(..., mode='drl')      : deroulement de la politique drl_route
    (meme caracteristiques que drl/v4_sim.py) noeud par noeud, a partir de
    l'etat courant du graphe ;
  - route_to_waypoints(graph, route)  : points de passage (x, y, cap) pour
    l'action Nav2 FollowWaypoints.

Limite connue : dans ROS la route est calculee UNE fois, a l'envoi de la
mission (Nav2 suit ensuite les points de passage) ; dans le banc, drl_route
decide a chaque noeud. Une attente choisie par la politique n'a pas de sens
dans une route calculee d'avance : on prend alors la meilleure arete libre.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

from warehouse_marl.allocation_benchmark import Task


def _view(graph, start, goal, speed, block_elapsed):
    from warehouse_marl.drl.v4_sim import BenchmarkV4
    sim = BenchmarkV4('greedy_pair', graph, 1, 1.0, 1, seed=0, speed=speed)
    r = sim.robots[0]
    r.node, r.speed = start, speed
    r.task = Task('ros', goal, 1.0, 0.0)
    sim.t = 1e6
    for (u, v), elapsed in (block_elapsed or {}).items():
        sim.blocked[(u, v)] = math.inf
        sim.block_start[(u, v)] = sim.t - elapsed
    return sim, r


def plan_route(graph, start: str, goal: str, mode: str = 'dijkstra', agent=None,
               speed: float = 0.5,
               block_elapsed: Optional[Dict[Tuple[str, str], float]] = None) -> List[str]:
    """Liste des noeuds de ``start`` a ``goal`` (vide si inaccessible en dijkstra)."""
    if start == goal:
        return [start]
    if mode == 'dijkstra' or agent is None:
        return graph.shortest_path(start, goal)[0]
    from warehouse_marl.drl.v4_sim import HOLD
    sim, r = _view(graph, start, goal, speed, block_elapsed)
    route = [start]
    limit = 3 * sim.n_nodes
    while r.node != goal and len(route) <= limit:
        cands, feats = sim.route_candidates(r)
        q = agent.scores(feats)
        order = sorted(range(len(cands)), key=lambda j: -q[j])
        nxt = next((cands[j] for j in order if cands[j] != HOLD
                    and not graph.G[r.node][cands[j]].get('blocked', False)), None)
        if nxt is None:
            break
        r.prev, r.node = r.node, nxt
        route.append(nxt)
    if r.node != goal:                       # garde-fou : comme dans le banc
        tail = graph.shortest_path(r.node, goal)[0]
        if not tail:
            return graph.shortest_path(start, goal)[0]
        route += tail[1:]
    return route


def route_to_waypoints(graph, route: List[str]) -> List[Tuple[float, float, float]]:
    """(x, y, cap en radians) de chaque noeud apres le depart ; le cap pointe
    vers le noeud suivant (le dernier garde le cap du dernier segment). Les
    noeuds consecutifs de meme position ne donnent qu'un point."""
    pts = []
    for n in route:                     # noeuds confondus (allee partagee) : un seul point
        p = (graph.G.nodes[n]['x'], graph.G.nodes[n]['y'])
        if not pts or math.hypot(p[0] - pts[-1][0], p[1] - pts[-1][1]) > 1e-6:
            pts.append(p)
    out = []
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        if i + 1 < len(pts):
            x2, y2 = pts[i + 1]
            yaw = math.atan2(y2 - y1, x2 - x1)
        else:
            yaw = math.atan2(y1 - y0, x1 - x0)
        out.append((x1, y1, yaw))
    return out
