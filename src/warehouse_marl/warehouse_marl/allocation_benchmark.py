"""
allocation_benchmark.py
------------------------
Banc d'essai HORS-LIGNE de l'allocation de taches (sans ROS 2 ni Gazebo),
pendant de ``rfid_experiment.py`` pour la couche coordination.

Il reutilise le code du package :
  - ``WarehouseGraph`` / ``build_demo_warehouse`` (graphe dynamique, Dijkstra
    sur le cout distance + congestion, aretes bloquees) ;
  - la regle d'enchere de ``consensus_node`` (cout = chemin / priorite + biais
    DRL, fenetre de 1,5 s, une enchere ouverte par robot, capacite des racks,
    gagnant = cout minimal puis robot_id, resolution des revendications) ;
  - la politique de ``drl_allocator_node`` (meme observation, modes ``direct``
    et ``hybrid``), si un modele .pt et PyTorch sont disponibles.

Methodes comparees :
  random      : robot libre tire au hasard (borne basse) ;
  fifo        : tache la plus ancienne -> robot libre le plus proche
                (dispatcher CENTRALISE, reference classique) ;
  consensus   : encheres distribuees, mode ``heuristic`` du systeme ;
  drl_hybrid  : encheres distribuees + biais -Q du DQN (mode ``hybrid``) ;
  drl_direct  : argmax des Q-values, file par robot (mode ``direct``) ;
  greedy_pair : temoin centralise SANS apprentissage dans l'espace de
                decision du DRL v2 : couple (robot libre, tache parmi les 5
                plus anciennes) de cout de chemin minimal ;
  drl2_hybrid : encheres distribuees + biais calibre du DRL v2
                (-w * (Q - moyenne des Q) * echelle en metres) ;
  drl2_direct : DRL v2 centralise, couple (robot libre, tache) de Q maximale.
  Le modele v2 (--model2, produit par train_drl_v2) sert pour toutes les
  tailles de flotte.

Le monde simule : les robots se deplacent sur les aretes du graphe a vitesse
constante, ralentis par la congestion (robots deja sur l'arete) ; des aretes
peuvent etre bloquees temporairement (obstacle) -> replanification ; les
messages du consensus (encheres, revendications) peuvent etre perdus ou
retardes (couche IoT).

Exemples :
    ros2 run warehouse_marl allocation_benchmark --exp all --seeds 10
    ros2 run warehouse_marl allocation_benchmark --exp load --model warehouse_dqn_3robots.pt
    ros2 run warehouse_marl allocation_benchmark --exp all --seeds 10 --model2 drl_v2/drl2_best.pt
    python3 -m warehouse_marl.allocation_benchmark --exp scale --seeds 5

Sorties (prefixe --out) : CSV des essais, tableau statistique (moyenne,
IC 95 % bootstrap, test de Wilcoxon apparie contre FIFO et contre le
consensus), figures PNG.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import random
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from warehouse_marl.warehouse_graph import (
    WarehouseGraph, WarehouseNode, build_demo_warehouse)

METHODS = ('random', 'fifo', 'consensus', 'greedy_pair', 'greedy_time', 'drl_hybrid',
           'drl_direct', 'drl2_hybrid', 'drl2_direct', 'drl3_direct')
REFERENCES = ('fifo', 'consensus', 'greedy_pair', 'greedy_time')
LABELS = {
    'random': 'Aleatoire',
    'fifo': 'FIFO + plus proche (centralise)',
    'consensus': 'Consensus heuristique',
    'greedy_pair': 'Couple de cout min. (centralise, sans apprentissage)',
    'drl_hybrid': 'DRL hybride (consensus + biais)',
    'drl_direct': 'DRL direct',
    'drl2_hybrid': 'DRL v2 hybride (consensus + biais calibre)',
    'drl2_direct': 'DRL v2 direct (Q par couple)',
    'greedy_time': 'Couple de temps de trajet min. (vitesses, sans apprentissage)',
    'drl3_direct': 'DRL v3 direct (residuel sur greedy_pair)',
}


# ---------------------------------------------------------------------- #
# Entrepots de taille variable (passage a l'echelle)
# ---------------------------------------------------------------------- #
def build_grid_warehouse(rows: int, cols: int, spacing_x: float = 3.5,
                         spacing_y: float = 3.0) -> WarehouseGraph:
    """Meme topologie que build_demo_warehouse (grille de racks reliee a un
    quai central et a deux stations), etendue a rows x cols racks."""
    if (rows, cols) == (5, 3):
        return build_demo_warehouse()
    g = WarehouseGraph()
    for r in range(rows):
        for c in range(cols):
            g.add_node(WarehouseNode(f'shelf_{r}_{c}', c * spacing_x, (rows / 2 - r) * spacing_y,
                                     node_type='shelf', capacity=1,
                                     rfid_tag=f'RFID-SHELF-{r}{c}'))
    mid = rows // 2
    g.add_node(WarehouseNode('station_A', -7.0, 4.0, node_type='station', capacity=2))
    g.add_node(WarehouseNode('station_B', -7.0, -4.0, node_type='station', capacity=2))
    g.add_node(WarehouseNode('charging_dock', -2.15, (rows / 2 - mid) * spacing_y,
                             node_type='station', capacity=4))
    for r in range(rows):
        for c in range(cols):
            if c < cols - 1:
                g.add_edge(f'shelf_{r}_{c}', f'shelf_{r}_{c + 1}')
            if r < rows - 1:
                g.add_edge(f'shelf_{r}_{c}', f'shelf_{r + 1}_{c}')
    g.add_edge('station_A', 'charging_dock')
    g.add_edge('station_B', 'charging_dock')
    g.add_edge('charging_dock', f'shelf_{mid}_0')
    return g


# ---------------------------------------------------------------------- #
# Etat de la simulation
# ---------------------------------------------------------------------- #
@dataclass
class Task:
    task_id: str
    target: str
    priority: float
    created: float
    assigned: Optional[float] = None
    started: Optional[float] = None
    done: Optional[float] = None
    robot: Optional[str] = None
    failed: bool = False
    bids: Dict[str, float] = field(default_factory=dict)
    bid_time: Dict[str, float] = field(default_factory=dict)
    deadline: Optional[float] = None          # fin de la fenetre d'enchere
    claim_until: Optional[float] = None
    due: Optional[float] = None               # delai de livraison (creation + base / priorite)


@dataclass
class Robot:
    rid: str
    node: str
    queue: List[Task] = field(default_factory=list)   # mode direct : file locale
    task: Optional[Task] = None
    edge: Optional[tuple] = None        # (u, v) arete en cours
    edge_left: float = 0.0              # temps restant sur l'arete
    pick_left: float = 0.0
    wait: float = 0.0                   # temps passe sans chemin
    distance: float = 0.0
    busy_time: float = 0.0
    open_bid: Optional[str] = None
    n_done: int = 0
    speed: Optional[float] = None       # None = vitesse commune du banc


class Benchmark:
    def __init__(self, method, graph, n_robots, rate, n_tasks, seed, agent=None,
                 bias_weight=1.0, speed=0.5, pick_time=10.0, slowdown=0.5,
                 block_rate=0.0, block_min=30.0, block_max=120.0,
                 msg_loss=0.0, msg_delay=0.05, window=1.5, bid_delay=0.2,
                 claim_window=0.5, max_active=3, dt=0.25, timeout=90.0, agent2=None,
                 demand_skew=0.0, speeds=None, deadline_base=60.0, agent3=None):
        self.m, self.g, self.rng = method, graph, random.Random(seed)
        self.agent, self.bias_w = agent, bias_weight
        self.agent2 = agent2                  # modele DRL v2 (drl/pair_dqn.py)
        self.agent3 = agent3                  # modele DRL v3 (drl/residual_dqn.py)
        self.demand_skew, self.deadline_base = demand_skew, deadline_base
        self.speed, self.pick_time, self.slow = speed, pick_time, slowdown
        self.block_rate, self.block_min, self.block_max = block_rate, block_min, block_max
        self.loss, self.delay = msg_loss, msg_delay
        self.window, self.bid_delay, self.claim_window = window, bid_delay, claim_window
        self.max_active, self.dt, self.timeout = max_active, dt, timeout
        stations = [n for n, d in graph.G.nodes(data=True) if d['node_type'] == 'station']
        self.shelves = [n for n, d in graph.G.nodes(data=True) if d['node_type'] == 'shelf']
        self.robots = [Robot(f'robot{i + 1}', stations[i % len(stations)]) for i in range(n_robots)]
        # Robots heterogenes : vitesses attribuees cycliquement (robot1 <- speeds[0]...)
        for i, r in enumerate(self.robots):
            r.speed = float(speeds[i % len(speeds)]) if speeds else speed
        self.names = [r.rid for r in self.robots]
        # Demande de type Zipf par rack : quelques racks tres sollicites. Le
        # classement de popularite vient d'un generateur separe, et la
        # demande uniforme (skew=0) garde exactement les tirages d'origine.
        if demand_skew > 0:
            popular = list(self.shelves)
            random.Random(seed + 2000).shuffle(popular)
            weights = [1.0 / (k + 1) ** demand_skew for k in range(len(popular))]
        t, self.arrivals = 0.0, []
        for k in range(n_tasks):
            t += self.rng.expovariate(rate)
            target = (self.rng.choices(popular, weights)[0] if demand_skew > 0
                      else self.rng.choice(self.shelves))
            task = Task(f't{k}', target, round(self.rng.uniform(0.5, 2.0), 2), t)
            task.due = t + deadline_base / task.priority
            self.arrivals.append(task)
        self.open: List[Task] = []
        self.tasks: List[Task] = []
        self.blocked: Dict[tuple, float] = {}
        self.msgs = 0
        self.conflicts = 0
        self.t = 0.0
        self.pc_cache: Dict[tuple, float] = {}
        self.cong_cache: Dict[tuple, float] = {}
        self.next_arrival = 0
        self.horizon = self.arrivals[-1].created + 3600.0
        self.k_candidates = 5             # DRL v2 : taches candidates par decision
        self.n_decisions = 0

    # ----- outils ---------------------------------------------------------
    def _invalidate(self):
        self.pc_cache.clear()
        self.cong_cache.clear()

    def path_cost(self, src, dst):
        key = (src, dst)
        if key not in self.pc_cache:
            self.pc_cache[key] = self.g.shortest_path(src, dst)[1]
        return self.pc_cache[key]

    def path_congestion(self, src, dst):
        """Somme des congestions (robots presents) sur le plus court chemin."""
        key = (src, dst)
        if key not in self.cong_cache:
            path, _ = self.g.shortest_path(src, dst)
            self.cong_cache[key] = sum(self.g.G[u][v].get('congestion', 0.0)
                                       for u, v in zip(path, path[1:]))
        return self.cong_cache[key]

    def idle(self, r: Robot):
        return r.task is None and not r.queue

    def target_full(self, target):
        used = sum(1 for k in self.tasks if k.robot and k.done is None and not k.failed
                   and k.target == target)
        return used >= int(self.g.G.nodes[target].get('capacity', 1))

    def load(self, r: Robot):
        return (1 if r.task else 0) + len(r.queue)

    def observation(self, task: Task):
        """Exactement drl_allocator_node._build_observation."""
        feats = []
        for idx, r in enumerate(self.robots):
            c = self.path_cost(r.node, task.target)
            c = c if c != math.inf else 50.0
            feats.extend([c / 20.0, self.load(r) / max(self.max_active, 1), idx / len(self.robots)])
        feats.append(task.priority / 2.0)
        return feats

    def q_values(self, task: Task):
        import numpy as np
        return self.agent.q_values(np.array(self.observation(task), dtype=np.float32))

    def hybrid_bias_v2(self, task: Task):
        """Biais calibre du DRL v2 pour ``task`` : rid -> metres (robots libres)."""
        from warehouse_marl.drl.features_v2 import bias_scale_from_meta, calibrated_bias
        free = [r for r in self.robots if self.idle(r)]
        if not free:
            return {}
        feats = self.pair_features(free, task, free, self.candidate_tasks())
        q = self.agent2.scores([feats[r.rid] for r in free])
        scale = bias_scale_from_meta(getattr(self.agent2, 'meta', {}), self.speed)
        return dict(zip([r.rid for r in free], calibrated_bias(q, self.bias_w, scale)))

    def assign(self, task: Task, r: Robot):
        task.robot, task.assigned = r.rid, self.t
        if r.task is None:
            self.start(r, task)
        else:
            r.queue.append(task)

    def start(self, r: Robot, task: Task):
        r.task, task.started, r.wait = task, self.t, 0.0

    # ----- allocation -------------------------------------------------------
    def allocate(self):
        if self.m == 'random':
            for task in list(self.open):
                free = [r for r in self.robots if self.idle(r)]
                if not free or self.target_full(task.target):
                    continue
                self.open.remove(task); self.assign(task, self.rng.choice(free)); self.msgs += 1
        elif self.m == 'fifo':
            for task in sorted(self.open, key=lambda k: k.created):
                free = [r for r in self.robots if self.idle(r)]
                if not free:
                    break
                if self.target_full(task.target):
                    continue
                r = min(free, key=lambda x: (self.path_cost(x.node, task.target), x.rid))
                self.open.remove(task); self.assign(task, r)
                self.msgs += len(self.robots) + 1      # interrogation des etats + ordre
        elif self.m == 'drl3_direct':
            # DRL v3 residuel : Q = -cout/diametre + correction apprise, couple
            # de Q maximale (correction nulle -> meme choix que greedy_pair).
            while True:
                pairs = self.candidate_pairs_v3()
                if not pairs:
                    break
                q = self.agent3.scores([f for _, _, f in pairs])
                r, task, _ = pairs[int(max(range(len(q)), key=lambda j: q[j]))]
                self.assign_pair(r, task)
        elif self.m == 'greedy_time':
            # Temoin sans apprentissage tenant compte de la vitesse de chaque
            # robot : couple de temps de trajet estime minimal.
            from warehouse_marl.drl.features_v2 import finite_cost
            while True:
                pairs = self.candidate_pairs()
                if not pairs:
                    break
                q = [-finite_cost(self.path_cost(r.node, k.target)) / r.speed
                     for r, k, _ in pairs]
                r, task, _ = pairs[int(max(range(len(q)), key=lambda j: q[j]))]
                self.assign_pair(r, task)
        elif self.m in ('drl2_direct', 'greedy_pair'):
            # Centralise, couple par couple (meme regle que drl/env_v2.py) :
            #   drl2_direct : couple (robot libre, tache) de Q maximale ;
            #   greedy_pair : temoin SANS apprentissage, meme espace de decision,
            #                 couple de cout de chemin minimal (egalite -> la
            #                 tache la plus ancienne).
            while True:
                pairs = self.candidate_pairs()
                if not pairs:
                    break
                if self.m == 'drl2_direct':
                    q = self.agent2.scores([f for _, _, f in pairs])
                else:
                    q = [-f[0] for _, _, f in pairs]
                r, task, _ = pairs[int(max(range(len(q)), key=lambda j: q[j]))]
                self.assign_pair(r, task)
        elif self.m == 'drl_direct':
            for task in list(self.open):
                q = self.q_values(task)
                order = sorted(range(len(self.robots)), key=lambda i: -q[i])
                for i in order:
                    r = self.robots[i]
                    if self.load(r) < self.max_active:
                        self.open.remove(task); self.assign(task, r); self.msgs += 1
                        break
        else:
            self.auction()

    def auction(self):
        """Regle de consensus_node : chaque robot libre encherit sur la tache
        ouverte la plus prioritaire (une a la fois), fenetre de 1,5 s, cout
        minimal puis robot_id ; les messages perdus creent des conflits."""
        by_prio = sorted(self.open, key=lambda k: -k.priority)
        bias = {}
        for r in self.robots:
            if not self.idle(r) or r.open_bid is not None:
                continue
            for task in by_prio:
                if r.rid in task.bids or self.target_full(task.target) or task.claim_until:
                    continue
                if self.t < task.created + self.bid_delay:
                    continue
                c = self.path_cost(r.node, task.target)
                if c == math.inf:
                    continue
                cost = c / max(task.priority, 1e-3)
                if self.m == 'drl_hybrid':
                    if task.task_id not in bias:
                        bias[task.task_id] = self.q_values(task)
                    cost += self.bias_w * -float(bias[task.task_id][self.names.index(r.rid)])
                elif self.m == 'drl2_hybrid':
                    if task.task_id not in bias:
                        bias[task.task_id] = self.hybrid_bias_v2(task)
                    cost += bias[task.task_id].get(r.rid, 0.0)
                task.bids[r.rid], task.bid_time[r.rid] = cost, self.t
                r.open_bid = task.task_id
                self.msgs += 1
                if task.deadline is None:
                    task.deadline = self.t + self.window
                break
        for task in list(self.open):
            if task.claim_until is not None:
                if self.t >= task.claim_until:
                    winner = min(task.bids.items(), key=lambda kv: (kv[1], kv[0]))[0]
                    self.finish_auction(task, winner)
                continue
            if task.deadline is None or self.t < task.deadline:
                continue
            # chaque agent decide avec les encheres qu'il a recues
            claimants = []
            for rid, cost in task.bids.items():
                seen = {o: c for o, c in task.bids.items()
                        if o == rid or (self.rng.random() >= self.loss
                                        and task.bid_time[o] + self.delay <= task.deadline)}
                if min(seen.items(), key=lambda kv: (kv[1], kv[0]))[0] == rid:
                    claimants.append(rid)
            self.msgs += len(claimants)
            if len(claimants) > 1:          # revendications concurrentes
                self.conflicts += 1
                task.bids = {r: task.bids[r] for r in claimants}
                task.claim_until = self.t + self.claim_window
            else:
                winner = claimants[0] if claimants else min(task.bids.items(), key=lambda kv: (kv[1], kv[0]))[0]
                self.finish_auction(task, winner)

    def finish_auction(self, task, winner):
        for r in self.robots:
            if r.open_bid == task.task_id:
                r.open_bid = None
        r = next(x for x in self.robots if x.rid == winner)
        self.open.remove(task)
        if self.idle(r):
            self.assign(task, r)
        else:                                  # le gagnant a deja ete pris : on relance
            task.bids, task.bid_time, task.deadline, task.claim_until = {}, {}, None, None
            self.open.append(task)

    # ----- monde ------------------------------------------------------------
    def blockages(self):
        if self.block_rate > 0 and self.rng.random() < self.block_rate * self.dt:
            edges = [(u, v) for u, v in self.g.G.edges
                     if u.startswith('shelf') and v.startswith('shelf') and u < v
                     and (u, v) not in self.blocked]
            if edges:
                u, v = self.rng.choice(edges)
                self.blocked[(u, v)] = self.t + self.rng.uniform(self.block_min, self.block_max)
                self.g.set_blocked(u, v, True); self.g.set_blocked(v, u, True)
                self._invalidate()
        for (u, v), end in list(self.blocked.items()):
            if self.t >= end:
                del self.blocked[(u, v)]
                self.g.set_blocked(u, v, False); self.g.set_blocked(v, u, False)
                self._invalidate()

    def move(self, r: Robot):
        if r.task is None:
            if r.queue:
                self.start(r, r.queue.pop(0))
            else:
                return
        r.busy_time += self.dt
        if r.pick_left > 0:
            r.pick_left -= self.dt
            if r.pick_left <= 0:
                r.task.done = self.t; r.n_done += 1; r.task = None
            return
        if r.edge is not None:
            r.edge_left -= self.dt
            if r.edge_left <= 0:
                u, v = r.edge
                self.g.update_congestion(u, v, -1.0); self._invalidate()
                r.node, r.edge = v, None
            return
        if r.node == r.task.target:
            r.pick_left = self.pick_time
            return
        path, _ = self.g.shortest_path(r.node, r.task.target)   # replanification a chaque noeud
        if len(path) < 2:
            r.wait += self.dt
            if r.wait >= self.timeout:                          # comme mission_executor : echec
                r.task.failed, r.task.done = True, self.t; r.task = None
            return
        u, v = path[0], path[1]
        cong = self.g.G[u][v].get('congestion', 0.0)
        base = self.g.G[u][v]['base_weight']
        r.edge, r.edge_left = (u, v), base / r.speed * (1.0 + self.slow * cong)
        r.distance += base
        self.g.update_congestion(u, v, 1.0); self._invalidate()

    # Un pas de simulation = begin_tick() ; allocate() ; end_tick().
    # Decoupe pour que drl/env_v2.py puisse s'arreter entre deux decisions
    # d'allocation sans dupliquer le monde simule.
    def begin_tick(self):
        """Arrivees de taches puis blocages/deblocages d'aretes."""
        while (self.next_arrival < len(self.arrivals)
               and self.arrivals[self.next_arrival].created <= self.t):
            k = self.arrivals[self.next_arrival]
            self.open.append(k); self.tasks.append(k); self.next_arrival += 1
        self.blockages()

    def end_tick(self):
        """Deplace les robots, avance le temps ; True si l'essai est fini."""
        for r in self.robots:
            self.move(r)
        self.t += self.dt
        return self.all_arrived() and not self.open and all(
            r.task is None and not r.queue for r in self.robots)

    def all_arrived(self):
        return self.next_arrival == len(self.arrivals)

    def run(self):
        while self.t < self.horizon:
            self.begin_tick()
            self.allocate()
            if self.end_tick():
                break
        return self.metrics()

    # ----- DRL v2 : couples (robot libre, tache candidate) --------------------
    def candidate_tasks(self):
        """Les K taches ouvertes les plus anciennes dont la cible a de la place."""
        out = []
        for k in sorted(self.open, key=lambda x: (x.created, x.task_id)):
            if not self.target_full(k.target):
                out.append(k)
                if len(out) == self.k_candidates:
                    break
        return out

    def task_dict(self, k: Task):
        return {'id': k.task_id, 'target': k.target, 'priority': k.priority,
                'created': k.created}

    def pair_features(self, robots, task: Task, free, cand):
        """Caracteristiques v2 de ``task`` pour chaque robot de ``robots``
        (dict rid -> vecteur), voir drl/features_v2.py."""
        from warehouse_marl.drl.features_v2 import features_for_robots
        node = {r.rid: r.node for r in self.robots}
        return features_for_robots(
            [r.rid for r in robots], [r.rid for r in free], self.task_dict(task),
            [self.task_dict(k) for k in cand],
            cost=lambda rid, tgt: self.path_cost(node[rid], tgt),
            congestion=lambda rid, tgt: self.path_congestion(node[rid], tgt),
            load={r.rid: self.load(r) for r in self.robots},
            n_robots=len(self.robots), queue_len=len(self.open),
            max_active=self.max_active, now=self.t)

    def candidate_pairs(self):
        """Liste [(robot, tache, caracteristiques)] des couples possibles."""
        free = [r for r in self.robots if self.idle(r)]
        if not free:
            return []
        cand = self.candidate_tasks()
        pairs = []
        for task in cand:
            feats = self.pair_features(free, task, free, cand)
            for r in free:
                pairs.append((r, task, feats[r.rid]))
        return pairs

    def candidate_pairs_v3(self):
        """Comme candidate_pairs, avec les caracteristiques relatives v3
        (drl/features_v3.py), calculees sur l'ensemble des couples."""
        from warehouse_marl.drl.features_v3 import decision_features, due_in, graph_diameter
        free = [r for r in self.robots if self.idle(r)]
        if not free:
            return []
        cand = self.candidate_tasks()
        if not cand:
            return []
        if getattr(self, '_diameter', None) is None:
            self._diameter = graph_diameter(self.g)
        specs, keys = [], []
        for task in cand:
            for r in free:
                c = self.path_cost(r.node, task.target)
                specs.append({'robot': r.rid, 'task': task.task_id, 'cost': c, 'speed': r.speed,
                              'congestion': 0.0 if math.isinf(c)
                              else self.path_congestion(r.node, task.target),
                              'load': self.load(r)})
                keys.append((r, task))
        tasks = {k.task_id: {'age': self.t - k.created, 'priority': k.priority,
                             'due_in': due_in(k.due, self.t)} for k in cand}
        feats = decision_features(
            specs, tasks, n_robots=len(self.robots), n_free=len(free),
            queue_len=len(self.open), diameter=self._diameter,
            mean_speed=statistics.mean(r.speed for r in self.robots),
            max_active=self.max_active, pick_time=self.pick_time)
        return [(r, k, f) for (r, k), f in zip(keys, feats)]

    def assign_pair(self, r: Robot, task: Task):
        """Attribution centralisee d'un couple (drl2_direct / env_v2)."""
        self.open.remove(task)
        self.assign(task, r)
        self.msgs += len(self.robots) + 1      # comme fifo : etats + ordre
        self.n_decisions += 1

    def metrics(self):
        done = [k for k in self.tasks if k.done is not None and not k.failed]
        n = max(1, len(done))
        tct = [k.done - k.created for k in done]
        wait = [k.assigned - k.created for k in done]
        counts = [r.n_done for r in self.robots]
        tct_sorted = sorted(tct) or [math.nan]
        return {
            'taches_finies': len(done),
            'taches_echouees': sum(1 for k in self.tasks if k.failed),
            'taches_non_finies': sum(1 for k in self.tasks if k.done is None),
            'temps_traitement_moy_s': statistics.mean(tct) if tct else math.nan,
            'temps_traitement_p90_s': tct_sorted[int(0.9 * (len(tct_sorted) - 1))],
            # pondere par la priorite : critere optimise par consensus_node (cout / priorite)
            'temps_pondere_priorite_s': (sum(k.priority * (k.done - k.created) for k in done)
                                         / sum(k.priority for k in done)) if done else math.nan,
            'attente_attribution_moy_s': statistics.mean(wait) if wait else math.nan,
            'debit_taches_h': 3600.0 * len(done) / max(self.t, 1e-6),
            'distance_par_tache_m': sum(r.distance for r in self.robots) / n,
            'messages_par_tache': self.msgs / n,
            'conflits_pour_100_taches': 100.0 * self.conflicts / n,
            'utilisation_robots_pct': 100.0 * statistics.mean(r.busy_time for r in self.robots) / max(self.t, 1e-6),
            'desequilibre_charge': (statistics.pstdev(counts) / statistics.mean(counts)) if statistics.mean(counts) > 0 else 0.0,
            'duree_simulee_s': self.t,
            # tache en retard : finie apres son delai (creation + base / priorite),
            # echouee ou jamais finie ; en % de toutes les taches
            'taches_en_retard_pct': 100.0 * sum(
                1 for k in self.tasks if k.failed or k.done is None
                or (k.due is not None and k.done > k.due)) / max(1, len(self.tasks)),
        }


# ---------------------------------------------------------------------- #
# Experiences
# ---------------------------------------------------------------------- #
def mean_service_time(graph, speed, pick_time):
    shelves = [n for n, d in graph.G.nodes(data=True) if d['node_type'] == 'shelf']
    costs = [graph.shortest_path(a, b)[1] for a in shelves for b in shelves if a != b]
    return statistics.mean(costs) / speed + pick_time


def load_agent(model_path, n_robots):
    if not model_path:
        return None
    if not os.path.isfile(model_path):
        print(f'Modele {model_path} introuvable : methodes DRL ignorees.')
        return None
    try:
        from warehouse_marl.drl.dqn_agent import DQNAgent
        agent = DQNAgent(obs_dim=n_robots * 3 + 1, n_actions=n_robots)
        agent.load(model_path)
        agent.epsilon = 0.0
        return agent
    except Exception as exc:   # torch absent, dimensions differentes...
        print(f'Impossible de charger {model_path} pour {n_robots} robots ({exc}) : methodes DRL ignorees.')
        return None


def load_agent2(model_path):
    """Modele DRL v2 (independant du nombre de robots)."""
    if not model_path:
        return None
    if not os.path.isfile(model_path):
        print(f'Modele v2 {model_path} introuvable : methodes drl2 ignorees.')
        return None
    try:
        from warehouse_marl.drl.pair_dqn import load_pair_model
        return load_pair_model(model_path)
    except Exception as exc:   # torch absent, mauvais format...
        print(f'Impossible de charger le modele v2 {model_path} ({exc}) : methodes drl2 ignorees.')
        return None


def run_experiment(name, configs, methods, seeds, args, agents, agent2=None, agent3=None):
    rows = []
    for cfg in configs:
        graph_dims = cfg.get('dims', (5, 3))
        n_robots = cfg['robots']
        speeds = cfg.get('speeds', args.speeds)
        base_graph = build_grid_warehouse(*graph_dims)
        mean_speed = statistics.mean(speeds) if speeds else args.speed
        service = mean_service_time(base_graph, mean_speed, args.pick_time)
        rate = cfg['rho'] * n_robots / service
        for seed in range(seeds):
            for m in methods:
                if m.startswith('drl3'):
                    if agent3 is None:
                        continue
                elif m.startswith('drl2'):
                    if agent2 is None:
                        continue
                elif m.startswith('drl') and agents.get(n_robots) is None:
                    continue
                graph = build_grid_warehouse(*graph_dims)
                b = Benchmark(m, graph, n_robots, rate, args.tasks, seed=1000 * seed + 7,
                              agent=agents.get(n_robots), agent2=agent2, agent3=agent3,
                              bias_weight=args.bias_weight,
                              speed=args.speed, pick_time=args.pick_time,
                              block_rate=cfg.get('block_rate', args.block_rate),
                              block_min=cfg.get('block_min', args.block_min),
                              block_max=cfg.get('block_max', args.block_max),
                              demand_skew=cfg.get('skew', args.demand_skew), speeds=speeds,
                              deadline_base=cfg.get('deadline_base', args.deadline_base),
                              msg_loss=cfg.get('loss', args.msg_loss), msg_delay=cfg.get('delay', 0.05))
                res = b.run()
                res.update(experience=name, methode=m, graine=seed, robots=n_robots,
                           racks=graph_dims[0] * graph_dims[1], rho=cfg['rho'],
                           condition=cfg['label'], block_rate=cfg.get('block_rate', args.block_rate),
                           perte_msg=cfg.get('loss', args.msg_loss))
                rows.append(res)
        print(f'  [{name}] {cfg["label"]} termine')
    return rows


def bootstrap_ci(xs, n=2000, seed=0):
    rng = random.Random(seed)
    means = sorted(statistics.mean(rng.choices(xs, k=len(xs))) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


def wilcoxon_p(a, b):
    try:
        from scipy.stats import wilcoxon
        if all(abs(x - y) < 1e-12 for x, y in zip(a, b)):
            return 1.0
        return float(wilcoxon(a, b).pvalue)
    except Exception:
        return math.nan


def stats_table(rows, metric='temps_traitement_moy_s'):
    out = []
    conds = list(dict.fromkeys((r['experience'], r['condition']) for r in rows))
    for exp, cond in conds:
        sub = [r for r in rows if r['experience'] == exp and r['condition'] == cond]
        by_m = {}
        for r in sub:
            by_m.setdefault(r['methode'], {})[r['graine']] = r[metric]
        for m, vals in by_m.items():
            seeds = sorted(vals)
            xs = [vals[s] for s in seeds if not math.isnan(vals[s])]
            if not xs:
                continue
            lo, hi = bootstrap_ci(xs)
            row = {'experience': exp, 'condition': cond, 'methode': m,
                   'moyenne': round(statistics.mean(xs), 2), 'ic95_bas': round(lo, 2),
                   'ic95_haut': round(hi, 2)}
            for ref_name in REFERENCES:
                ref = by_m.get(ref_name, {})
                common = [s for s in seeds if s in ref]
                if m != ref_name and len(common) >= 5:
                    a = [vals[s] for s in common]; b = [ref[s] for s in common]
                    mb = statistics.mean(b)
                    row[f'gain_vs_{ref_name}_pct'] = (round(100 * (mb - statistics.mean(a)) / mb, 1)
                                                      if mb else math.nan)
                    row[f'gagne_vs_{ref_name}'] = f'{sum(x < y for x, y in zip(a, b))}/{len(common)}'
                    row[f'p_wilcoxon_vs_{ref_name}'] = round(wilcoxon_p(a, b), 4)
            out.append(row)
    return out


def write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows)


def plots(rows, out):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib absent : pas de figure.')
        return
    plt.rcParams.update({'axes.grid': True, 'grid.alpha': 0.3,
                         'axes.spines.top': False, 'axes.spines.right': False})
    methods = [m for m in METHODS if any(r['methode'] == m for r in rows)]

    def agg(sub, metric):
        res = {}
        for m in methods:
            xs = [r[metric] for r in sub if r['methode'] == m and not math.isnan(r[metric])]
            if xs:
                lo, hi = bootstrap_ci(xs)
                res[m] = (statistics.mean(xs), lo, hi)
        return res

    for exp in dict.fromkeys(r['experience'] for r in rows):
        sub = [r for r in rows if r['experience'] == exp]
        conds = list(dict.fromkeys(r['condition'] for r in sub))
        metrics = [('temps_traitement_moy_s', 'Temps de traitement moyen (s)'),
                   ('temps_pondere_priorite_s', 'Temps pondere par la priorite (s)'),
                   ('attente_attribution_moy_s', "Attente avant attribution (s)"),
                   ('messages_par_tache', 'Messages par tache'),
                   ('conflits_pour_100_taches', 'Conflits pour 100 taches'),
                   ('desequilibre_charge', 'Desequilibre de charge (CV)'),
                   ('taches_en_retard_pct', 'Taches en retard (%)'),
                   ('distance_par_tache_m', 'Distance par tache (m)')]
        fig, axs = plt.subplots(2, 4, figsize=(19, 8))
        axs = axs.ravel()
        for ax, (metric, lab) in zip(axs, metrics):
            w = 0.8 / len(methods)
            for j, m in enumerate(methods):
                ys, err_lo, err_hi = [], [], []
                for c in conds:
                    a = agg([r for r in sub if r['condition'] == c], metric).get(m)
                    ys.append(a[0] if a else math.nan)
                    err_lo.append(a[0] - a[1] if a else 0); err_hi.append(a[2] - a[0] if a else 0)
                xs = [k + (j - (len(methods) - 1) / 2) * w for k in range(len(conds))]
                ax.bar(xs, ys, w, yerr=[err_lo, err_hi], capsize=2, label=LABELS[m])
            ax.set_xticks(range(len(conds))); ax.set_xticklabels(conds, fontsize=8)
            ax.set_title(lab, fontsize=10)
        axs[0].legend(fontsize=7)
        fig.suptitle(f'Experience : {exp} (moyenne et IC 95 %)')
        fig.tight_layout()
        fig.savefig(f'{out}_{exp}.png', dpi=150)
        plt.close(fig)
        print(f'Figure : {out}_{exp}.png')


def _speeds(text):
    """'0.3,0.5,0.7' -> (0.3, 0.5, 0.7) ; '' -> None (vitesse commune)."""
    vals = tuple(float(x) for x in str(text).split(',') if x.strip())
    if any(v <= 0 for v in vals):
        raise argparse.ArgumentTypeError('les vitesses doivent etre > 0')
    return vals or None


# Experience 'structured' : scenarios ou anticiper peut payer (demande de
# Zipf, robots heterogenes, delais par priorite, blocages longs), sur 3
# niveaux de difficulte, 6 robots et 40 racks.
STRUCTURED_LEVELS = [
    dict(label='facile', rho=0.6, skew=0.5, speeds=(0.4, 0.5, 0.6), block_rate=0.5 / 60.0),
    dict(label='moyen', rho=0.75, skew=1.0, speeds=(0.3, 0.5, 0.7), block_rate=1.0 / 60.0),
    dict(label='difficile', rho=0.9, skew=1.5, speeds=(0.25, 0.5, 0.75), block_rate=2.0 / 60.0),
]


def _print_table(title, table):
    print(title)
    for r in table:
        extra = ''
        for ref, lab in (('fifo', 'FIFO'), ('consensus', 'consensus'),
                         ('greedy_pair', 'greedy_pair'), ('greedy_time', 'greedy_time')):
            if f'gain_vs_{ref}_pct' in r:
                extra += (f"  vs {lab} {r[f'gain_vs_{ref}_pct']:+.1f} % "
                          f"({r[f'gagne_vs_{ref}']}, p={r[f'p_wilcoxon_vs_{ref}']})")
        print(f"  {r['experience']:10s} {r['condition']:22s} {r['methode']:11s} "
              f"{r['moyenne']:7.1f} [{r['ic95_bas']:.1f} ; {r['ic95_haut']:.1f}]{extra}")


def main(argv=None):
    p = argparse.ArgumentParser(description='Banc d essai hors-ligne de l allocation de taches.')
    p.add_argument('--exp', default='all',
                   choices=['load', 'scale', 'blocking', 'network', 'structured', 'all'])
    p.add_argument('--seeds', type=int, default=10)
    p.add_argument('--tasks', type=int, default=150, help='taches par essai')
    p.add_argument('--robots', type=int, default=3)
    p.add_argument('--model', default='', help='modele DQN .pt (pour drl_hybrid / drl_direct)')
    p.add_argument('--model2', default='', help='modele DRL v2 .pt (train_drl_v2) pour drl2_*')
    p.add_argument('--bias-weight', type=float, default=1.0,
                   help='poids du biais DRL (v1 : -Q ; v2 : biais calibre)')
    p.add_argument('--speed', type=float, default=0.5, help='vitesse des robots (m/s)')
    p.add_argument('--pick-time', type=float, default=10.0)
    p.add_argument('--block-rate', type=float, default=0.0, help='blocages d aretes par seconde')
    p.add_argument('--msg-loss', type=float, default=0.0)
    p.add_argument('--block-min', type=float, default=30.0, help='duree min. d un blocage (s)')
    p.add_argument('--block-max', type=float, default=120.0, help='duree max. d un blocage (s)')
    p.add_argument('--demand-skew', type=float, default=0.0,
                   help='demande de Zipf par rack (0 = uniforme)')
    p.add_argument('--speeds', type=_speeds, default=None,
                   help='vitesses des robots, attribuees cycliquement, ex. "0.3,0.5,0.7"')
    p.add_argument('--deadline-base', type=float, default=60.0,
                   help='delai d une tache = base / priorite (s)')
    p.add_argument('--methods', default=','.join(METHODS))
    p.add_argument('--out', default='allocation_benchmark')
    args = p.parse_args(argv)
    methods = [m for m in args.methods.split(',') if m in METHODS]
    R = args.robots

    plans = {
        'load': [dict(label=f'rho={x}', rho=x, robots=R) for x in (0.5, 0.7, 0.9)],
        'scale': [dict(label='3 robots, 15 racks', rho=0.7, robots=3, dims=(5, 3)),
                  dict(label='6 robots, 40 racks', rho=0.7, robots=6, dims=(8, 5)),
                  dict(label='10 robots, 80 racks', rho=0.7, robots=10, dims=(10, 8)),
                  dict(label='20 robots, 150 racks', rho=0.7, robots=20, dims=(15, 10))],
        'blocking': [dict(label=f'{x:g} blocage/min', rho=0.7, robots=R, block_rate=x / 60.0)
                     for x in (0, 1, 3, 6)],
        'network': [dict(label=f'perte {int(100 * x)} %', rho=0.7, robots=R, loss=x, delay=0.05 + 2 * x)
                    for x in (0.0, 0.1, 0.3, 0.5)],
        'structured': [dict(lvl, robots=6, dims=(8, 5), block_min=60.0, block_max=300.0,
                            deadline_base=60.0) for lvl in STRUCTURED_LEVELS],
    }
    exps = list(plans) if args.exp == 'all' else [args.exp]
    needed = {c['robots'] for e in exps for c in plans[e]}
    agents = ({n: load_agent(args.model, n) for n in needed}
              if any(m.startswith('drl_') for m in methods) else {})
    agent2 = load_agent2(args.model2) if any(m.startswith('drl2') for m in methods) else None

    rows = []
    for e in exps:
        print(f'Experience {e} ...')
        rows += run_experiment(e, plans[e], methods, args.seeds, args, agents, agent2)
    write_csv(f'{args.out}_essais.csv', rows)
    table = stats_table(rows)
    write_csv(f'{args.out}_statistiques.csv', table)
    late = stats_table(rows, metric='taches_en_retard_pct')
    write_csv(f'{args.out}_statistiques_retard.csv', late)
    print(f'\nCSV : {args.out}_essais.csv, {args.out}_statistiques.csv, '
          f'{args.out}_statistiques_retard.csv\n')
    _print_table('Temps de traitement moyen (s), IC 95 %, gain et test de Wilcoxon apparie :',
                 table)
    if 'structured' in exps:
        _print_table('\nTaux de taches en retard (%), experience structured :',
                     [r for r in late if r['experience'] == 'structured'])
    plots(rows, args.out)


if __name__ == '__main__':
    main()
