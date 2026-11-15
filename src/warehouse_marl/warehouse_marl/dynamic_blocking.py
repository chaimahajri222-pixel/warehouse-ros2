"""
dynamic_blocking.py
-------------------
Graphe dynamique EN LIGNE : logique, sans ROS 2, des blocages d'aretes
annonces sur le topic /warehouse/blocked_edges.

Message (JSON dans un std_msgs/String) :
    {"u": "shelf_1_0", "v": "shelf_2_0", "blocked": true, "duration_s": 60,
     "source": "mission_executor", "reason": "..."}
  - blocked=true  : l'arete est bloquee dans les DEUX sens ; si duration_s > 0
    elle est debloquee automatiquement a l'echeance (sinon jusqu'a un
    message blocked=false) ;
  - blocked=false : deblocage immediat.

- EdgeBlockManager : applique les messages a un WarehouseGraph et gere les
  echeances (utilise par graph_publisher_node).
- FailureTracker : compte les echecs Nav2 par cible ; au-dela d'un seuil
  dans une fenetre de temps, signale qu'il faut bloquer l'arete d'acces
  (utilise par mission_executor_node).
- access_edge : arete d'acces a une cible = derniere arete du plus court
  chemin depuis le noeud d'entree (quai) vers la cible.
"""

from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Tuple


def edge_key(u: str, v: str) -> Tuple[str, str]:
    return (u, v) if u <= v else (v, u)


def parse_block_message(text: str) -> Dict:
    """Valide un message /warehouse/blocked_edges ; ValueError si invalide."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f'JSON invalide : {exc}') from exc
    if not isinstance(data, dict) or 'u' not in data or 'v' not in data:
        raise ValueError('champs u et v requis')
    blocked = data.get('blocked', True)
    if not isinstance(blocked, bool):
        raise ValueError('blocked doit etre un booleen')
    duration = float(data.get('duration_s', 0.0) or 0.0)
    if duration < 0 or math.isnan(duration):
        raise ValueError('duration_s doit etre >= 0')
    return {'u': str(data['u']), 'v': str(data['v']), 'blocked': blocked,
            'duration_s': duration, 'source': data.get('source', ''),
            'reason': data.get('reason', '')}


class EdgeBlockManager:
    def __init__(self, graph):
        self.graph = graph
        self.until: Dict[Tuple[str, str], float] = {}     # echeance (inf = sans fin)

    def _set(self, u: str, v: str, blocked: bool):
        self.graph.set_blocked(u, v, blocked)
        self.graph.set_blocked(v, u, blocked)

    def apply(self, msg: Dict, now: float) -> bool:
        """Applique un message valide ; True si le graphe a change."""
        u, v = msg['u'], msg['v']
        if not (self.graph.G.has_edge(u, v) or self.graph.G.has_edge(v, u)):
            return False
        key = edge_key(u, v)
        if msg['blocked']:
            end = now + msg['duration_s'] if msg['duration_s'] > 0 else math.inf
            changed = key not in self.until
            self.until[key] = max(end, self.until.get(key, -math.inf))
            self._set(u, v, True)
            return changed
        if key in self.until:
            del self.until[key]
            self._set(u, v, False)
            return True
        return False

    def expire(self, now: float) -> List[Tuple[str, str]]:
        """Debloque les aretes arrivees a echeance ; retourne la liste."""
        done = [k for k, end in self.until.items() if now >= end]
        for k in done:
            del self.until[k]
            self._set(*k, False)
        return done

    def active(self) -> Dict[Tuple[str, str], float]:
        return dict(self.until)


class FailureTracker:
    """Echecs Nav2 par cible ; ``record_failure`` renvoie True quand le
    seuil est atteint dans la fenetre (le compteur repart alors a zero)."""

    def __init__(self, threshold: int = 2, window_s: float = 300.0):
        self.threshold, self.window_s = max(1, int(threshold)), float(window_s)
        self.failures: Dict[str, List[float]] = {}

    def record_failure(self, target: str, now: float) -> bool:
        times = [t for t in self.failures.get(target, []) if now - t <= self.window_s]
        times.append(now)
        if len(times) >= self.threshold:
            self.failures[target] = []
            return True
        self.failures[target] = times
        return False

    def record_success(self, target: str):
        self.failures.pop(target, None)


def access_edge(graph, target: str, entry: str = 'charging_dock') -> Optional[Tuple[str, str]]:
    """Derniere arete du plus court chemin ``entry`` -> ``target`` (aretes
    bloquees evitees) ; a defaut, l'arete vers le voisin le plus proche."""
    if target not in graph.G:
        return None
    if entry in graph.G and entry != target:
        path, cost = graph.shortest_path(entry, target)
        if len(path) >= 2 and math.isfinite(cost):
            return path[-2], path[-1]
    nbrs = [(graph.G[target][n]['base_weight'], n) for n in graph.G[target]
            if not graph.G[target][n].get('blocked', False)]
    if not nbrs:
        return None
    return min(nbrs)[1], target


def block_message(u: str, v: str, duration_s: float, source: str, reason: str) -> str:
    return json.dumps({'u': u, 'v': v, 'blocked': True, 'duration_s': duration_s,
                       'source': source, 'reason': reason})
