"""
idle_planner.py
---------------
Point d'attente d'un robot inoccupe pour mission_executor_node (idle_mode),
sans dependance ROS. Reprend exactement la decision du banc v4
(drl/v4_sim.py, PROTOCOLE_V4.md §3.2) :

  - 'stay'   : le robot reste ou il est (comportement historique) ;
  - 'centre' : centre_de_demande, le noeud qui minimise E_p[d(n, rack)] ;
  - 'drl'    : politique drl_idle, argmax de Q sur les K = 6 candidats de
               BenchmarkV4.idle_candidates (memes caracteristiques).

Demande p(rack) : comptage EN LIGNE des cibles des taches deja vues sur
/warehouse/tasks/new, avec lissage de Laplace (+1), comme la condition Zipf
du protocole. Aucune information future n'est utilisee. Les distances sont
celles du graphe sur les longueurs seules (static_tables).
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np

from warehouse_marl.allocation_benchmark import Task

IDLE_MODES_ROS = ('stay', 'centre', 'drl')


def _view(graph, robot_id: str, robots: Dict[str, dict], speed: float,
          demand_counts: Dict[str, int], n_open: int):
    """BenchmarkV4 dont l'etat reproduit la flotte ROS. ``robots`` :
    {id: {'node': str, 'park': str|None, 'idle': bool}} (ordre conserve)."""
    from warehouse_marl.drl.v4_sim import BenchmarkV4
    ids = list(robots)
    sim = BenchmarkV4('greedy_pair', graph, len(ids), 1.0, 1, seed=0, speed=speed,
                      idle_mode='centre_de_demande')
    by_id = {}
    for rid, r in zip(ids, sim.robots):
        st = robots[rid]
        r.node, r.edge, r.speed, r.queue = st['node'], None, speed, []
        r.park = st.get('park')
        r.task = None if st.get('idle', True) else Task(f'occupe_{rid}', st['node'], 1.0, 0.0)
        by_id[rid] = r
    sim.open = [Task(f'ouverte_{i}', 'charging_dock', 1.0, 0.0) for i in range(n_open)]
    sim.tasks = []
    sim._counted_tasks = 0
    sim._online_counts = np.array(
        [1.0 + float(demand_counts.get(s, 0)) for s in sim.shelf_list])
    return sim, by_id[robot_id]


def choose_idle_point(graph, robot_id: str, robots: Dict[str, dict], mode: str,
                      agent=None, speed: float = 0.5,
                      demand_counts: Optional[Dict[str, int]] = None,
                      n_open: int = 0) -> Tuple[str, dict]:
    """(noeud d'attente, informations de la decision pour le journal)."""
    if mode not in IDLE_MODES_ROS:
        raise ValueError(f'idle_mode inconnu : {mode}')
    here = robots[robot_id]['node']
    if mode == 'stay':
        return here, {'mode': mode, 'choix': here}
    sim, r = _view(graph, robot_id, robots, speed, demand_counts or {}, n_open)
    ed = sim.expected_dist()
    center = sim.nodes[int(np.argmin(ed))]
    info = {'mode': mode, 'centre': center,
            'demande_vue': int(sum((demand_counts or {}).values()))}
    if mode == 'centre' or agent is None:
        info['choix'] = center
        return center, info
    cands, feats = sim.idle_candidates(r, ed, center)
    q = agent.scores(feats)
    j = int(np.argmax(q))
    info.update({'candidats': list(cands), 'q': [round(float(x), 4) for x in q],
                 'a_priori': [round(float(x), 4) for x in feats[:, 0]], 'choix': cands[j]})
    return cands[j], info
