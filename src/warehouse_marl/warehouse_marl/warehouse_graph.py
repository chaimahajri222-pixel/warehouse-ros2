"""
warehouse_graph.py
-------------------
Modelise l'entrepot comme un GRAPHE DYNAMIQUE, conformement a la description
du sujet de Master :

    "The warehouse will be modeled as a dynamic graph where autonomous
    agents collaborate through consensus-based protocols."

Un noeud represente soit :
    - une station de stockage / un rack (type='shelf')
    - une station de picking / un quai de chargement (type='station')
    - un point de passage (type='waypoint')

Une arete represente un chemin navigable entre deux noeuds, avec un poids
qui evolue dynamiquement en fonction :
    - de la distance euclidienne,
    - du niveau de congestion (nombre de robots presents / recents),
    - d'un etat bloque/libre (issu par ex. d'une detection RFID ou d'un
      obstacle detecte par le stack de navigation).

Cette classe est volontairement independante de ROS2 (aucune dependance a
rclpy) afin de pouvoir etre :
    1) utilisee telle quelle dans l'environnement Gymnasium d'entrainement
       DRL (drl/env.py), sans lancer de noeud ROS2 ;
    2) enveloppee par un noeud ROS2 (graph_publisher_node.py) qui la publie
       et la met a jour a partir des topics de simulation.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

try:
    import networkx as nx
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "networkx est requis : pip install networkx --break-system-packages"
    ) from exc


@dataclass
class WarehouseNode:
    node_id: str
    x: float
    y: float
    node_type: str = "waypoint"      # 'shelf' | 'station' | 'waypoint'
    capacity: int = 1                # nb de robots simultanes autorises
    occupied_by: List[str] = field(default_factory=list)
    rfid_tag: Optional[str] = None   # identifiant du tag RFID associe


class WarehouseGraph:
    """Graphe dynamique pondere de l'entrepot, base sur networkx.DiGraph."""

    def __init__(self):
        self.G = nx.DiGraph()
        self._last_update = time.time()

    # ------------------------------------------------------------------ #
    # Construction du graphe
    # ------------------------------------------------------------------ #
    def add_node(self, node: WarehouseNode) -> None:
        self.G.add_node(
            node.node_id,
            x=node.x,
            y=node.y,
            node_type=node.node_type,
            capacity=node.capacity,
            occupied_by=list(node.occupied_by),
            rfid_tag=node.rfid_tag,
        )

    def add_edge(self, u: str, v: str, bidirectional: bool = True) -> None:
        """Ajoute une arete ponderee par la distance euclidienne (poids de base)."""
        w = self._euclidean(u, v)
        self.G.add_edge(u, v, base_weight=w, congestion=0.0, blocked=False)
        if bidirectional:
            self.G.add_edge(v, u, base_weight=w, congestion=0.0, blocked=False)

    def _euclidean(self, u: str, v: str) -> float:
        xu, yu = self.G.nodes[u]["x"], self.G.nodes[u]["y"]
        xv, yv = self.G.nodes[v]["x"], self.G.nodes[v]["y"]
        return math.hypot(xv - xu, yv - yu)

    # ------------------------------------------------------------------ #
    # Mise a jour dynamique (appelee a chaque tick de simulation)
    # ------------------------------------------------------------------ #
    def update_congestion(self, u: str, v: str, delta: float) -> None:
        """Augmente/diminue le niveau de congestion d'une arete (ex: un robot
        vient de l'emprunter -> +delta ; un robot vient de la liberer -> -delta)."""
        if self.G.has_edge(u, v):
            c = self.G[u][v].get("congestion", 0.0) + delta
            self.G[u][v]["congestion"] = max(0.0, c)

    def set_blocked(self, u: str, v: str, blocked: bool) -> None:
        """Marque une arete comme bloquee (obstacle detecte, robot en panne...)."""
        if self.G.has_edge(u, v):
            self.G[u][v]["blocked"] = blocked

    def set_node_occupancy(self, node_id: str, robot_id: str, occupied: bool) -> None:
        occ = self.G.nodes[node_id]["occupied_by"]
        if occupied and robot_id not in occ:
            occ.append(robot_id)
        elif not occupied and robot_id in occ:
            occ.remove(robot_id)

    def register_rfid_read(self, node_id: str, rfid_tag: str) -> None:
        """Associe/confirme un tag RFID lu physiquement a un noeud du graphe.
        Permet de recaler la position logique d'un agent avec la realite
        physique (voir rfid_sensor_node.py)."""
        if node_id in self.G.nodes:
            self.G.nodes[node_id]["rfid_tag"] = rfid_tag

    def edge_cost(self, u: str, v: str, congestion_weight: float = 2.0) -> float:
        """Cout effectif d'une arete = distance + penalite de congestion,
        ou +infini si l'arete est bloquee. Utilise par le planificateur de
        chemin ET par l'environnement DRL comme composante de la fonction
        de recompense/etat."""
        if not self.G.has_edge(u, v):
            return math.inf
        data = self.G[u][v]
        if data.get("blocked", False):
            return math.inf
        return data["base_weight"] + congestion_weight * data.get("congestion", 0.0)

    def shortest_path(self, source: str, target: str) -> Tuple[List[str], float]:
        """Plus court chemin en tenant compte de la congestion courante
        (Dijkstra sur le cout dynamique edge_cost)."""
        def weight_fn(u, v, _d):
            return self.edge_cost(u, v)

        try:
            path = nx.shortest_path(self.G, source, target, weight=weight_fn)
            cost = nx.shortest_path_length(self.G, source, target, weight=weight_fn)
            return path, cost
        except nx.NetworkXNoPath:
            return [], math.inf

    # ------------------------------------------------------------------ #
    # (Se)Serialisation -> utilise pour publier l'etat sur un topic ROS2
    # ------------------------------------------------------------------ #
    def to_json(self) -> str:
        payload = {
            "timestamp": time.time(),
            "nodes": [
                {"id": n, **self.G.nodes[n]} for n in self.G.nodes
            ],
            "edges": [
                {"u": u, "v": v, **self.G[u][v]} for u, v in self.G.edges
            ],
        }
        return json.dumps(payload)

    @classmethod
    def from_json(cls, payload: str) -> "WarehouseGraph":
        data = json.loads(payload)
        g = cls()
        for n in data["nodes"]:
            node = WarehouseNode(
                node_id=n["id"], x=n["x"], y=n["y"],
                node_type=n.get("node_type", "waypoint"),
                capacity=n.get("capacity", 1),
                occupied_by=n.get("occupied_by", []),
                rfid_tag=n.get("rfid_tag"),
            )
            g.add_node(node)
        for e in data["edges"]:
            g.G.add_edge(e["u"], e["v"], base_weight=e["base_weight"],
                         congestion=e["congestion"], blocked=e["blocked"])
        return g


def build_demo_warehouse() -> WarehouseGraph:
    """Construit un petit entrepot de demonstration (grille 4x3 + 2 stations
    de depot), compatible avec le monde 'warehouse' du package rosnav
    (24x20 m, 5 rangees d'etageres, quai de chargement).

    Adapte les coordonnees (x, y) a la geometrie exacte de ton monde SDF
    si tu veux un alignement parfait avec la simulation Gazebo.
    """
    g = WarehouseGraph()

    # Racks / etageres (5 rangees x 4 emplacements, comme le monde 'warehouse')
    for row in range(5):
        for col in range(4):
            nid = f"shelf_{row}_{col}"
            g.add_node(WarehouseNode(
                node_id=nid, x=col * 4.0, y=row * 3.5,
                node_type="shelf", capacity=1,
                rfid_tag=f"RFID-SHELF-{row}{col}",
            ))

    # Stations de picking / quai de chargement
    g.add_node(WarehouseNode(node_id="station_A", x=-3.0, y=0.0,
                              node_type="station", capacity=2,
                              rfid_tag="RFID-STATION-A"))
    g.add_node(WarehouseNode(node_id="station_B", x=-3.0, y=14.0,
                              node_type="station", capacity=2,
                              rfid_tag="RFID-STATION-B"))
    g.add_node(WarehouseNode(node_id="charging_dock", x=-3.0, y=7.0,
                              node_type="station", capacity=4,
                              rfid_tag="RFID-DOCK"))

    # Aretes : chaque rack relie a ses voisins directs + aux stations via
    # l'allee correspondante (topologie simplifiee en grille)
    for row in range(5):
        for col in range(4):
            nid = f"shelf_{row}_{col}"
            if col < 3:
                g.add_edge(nid, f"shelf_{row}_{col+1}")
            if row < 4:
                g.add_edge(nid, f"shelf_{row+1}_{col}")

    g.add_edge("station_A", "shelf_0_0")
    g.add_edge("station_B", "shelf_4_0")
    g.add_edge("charging_dock", "shelf_2_0")

    return g
