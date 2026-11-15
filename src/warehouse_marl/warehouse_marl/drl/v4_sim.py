"""
v4_sim.py
---------
Simulateur v4 (PROTOCOLE_V4.md) : sous-classe de ``allocation_benchmark.Benchmark``
qui ajoute
  - le ROUTAGE au niveau du graphe (``route_mode``) :
      dijkstra_dynamique : replanification a chaque noeud, couts en direct
                           (= ancien Benchmark.move, a l'identique) ;
      dijkstra_statique  : route calculee au depart de la tache sur les
                           longueurs (aretes bloquees exclues), suivie ;
                           replanifiee seulement si l'arete suivante est bloquee ;
      drl_route          : a chaque noeud, choix de l'arete suivante (ou attente)
                           par le DQN residuel (route_dqn) ;
  - le POINT D'ATTENTE des robots inoccupes (``idle_mode``) :
      rester_sur_place (= ancien comportement), retour_au_depot,
      centre_de_demande, drl_idle ;
  - des metriques supplementaires (trajet, approche, conflits, attentes,
    temps de calcul par decision).

Avec route_mode='dijkstra_dynamique' et idle_mode='rester_sur_place', les
resultats sont identiques a ceux de Benchmark (teste dans test_v4.py).

Les transitions d'apprentissage sont envoyees a ``on_route_transition`` /
``on_idle_transition`` (feat, recompense, feats_suivantes, terminal) si ces
fonctions sont fournies (entrainement), sinon ignorees.
"""

from __future__ import annotations

import heapq
import math
import random
import statistics
import time
from typing import Callable, Dict, List, Optional

import numpy as np

from warehouse_marl.allocation_benchmark import Benchmark

ROUTE_MODES = ('dijkstra_statique', 'dijkstra_dynamique', 'drl_route')
IDLE_MODES = ('rester_sur_place', 'retour_au_depot', 'centre_de_demande', 'drl_idle')
HOLD = '__attente__'
HOLD_TICKS = 4                # attente choisie : 1 s (4 pas), interrompue si un blocage change
BLOCK_PENALTY_M = 1000.0      # cout d'une arete bloquee dans le terme a priori (metres)
WAIT_DELTA_M = 0.01           # cout additionnel de l'attente dans le terme a priori
TIE_BONUS = 1e-3              # bonus (unites de Q) a l'action de l'heuristique de depart
REWARD_NORM_S = 60.0
K_IDLE = 6

N_ROUTE_FEATURES = 16
ROUTE_FEATURE_NAMES = (
    'prior_q', 'longueur', 'robots_sur_arete', 'robots_vers_voisin', 'robots_au_voisin',
    'bloquee', 'blocage_ecoule', 'dist_but_voisin_direct', 'dist_but_voisin_longueurs',
    'charge_file_destination', 'vitesse', 'demi_tour', 'attente', 'dist_but_ici',
    'part_aretes_bloquees', 'choix_dijkstra')
N_IDLE_FEATURES = 13
IDLE_FEATURE_NAMES = (
    'prior_q', 'dist_robot_candidat', 'inoccupes_au_candidat', 'dist_inoccupe_plus_proche',
    'masse_demande_voisinage', 'est_position', 'est_depot', 'est_centre', 'part_libres',
    'file_par_robot', 'vitesse', 'ecart_au_centre', 'taille_flotte')

_DIST_CACHE: Dict[tuple, tuple] = {}


def _dijkstra_lengths(G, src):
    """Distances sur les longueurs seules (sans blocage ni congestion)."""
    dist = {src: 0.0}
    heap = [(0.0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, data in G._adj[u].items():
            nd = d + data['base_weight']
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist


def static_tables(graph):
    """(noeuds, racks, matrice noeuds x racks des distances sur longueurs,
    dict distance(src)[dst], diametre). Mis en cache par topologie."""
    key = tuple(sorted(graph.G.nodes))
    if key not in _DIST_CACHE:
        nodes = list(graph.G.nodes)
        shelves = [n for n, d in graph.G.nodes(data=True) if d['node_type'] == 'shelf']
        full = {n: _dijkstra_lengths(graph.G, n) for n in nodes}
        mat = np.array([[full[n][s] for s in shelves] for n in nodes], dtype=np.float64)
        diam = max(max(d.values()) for d in full.values())
        _DIST_CACHE[key] = (nodes, shelves, mat, full, diam)
    return _DIST_CACHE[key]


class BenchmarkV4(Benchmark):
    def __init__(self, method, graph, n_robots, rate, n_tasks, seed,
                 route_mode='dijkstra_dynamique', idle_mode='rester_sur_place',
                 route_agent=None, idle_agent=None, demand_prior=None,
                 epsilon=0.0, explore_seed=None,
                 on_route_transition: Optional[Callable] = None,
                 on_idle_transition: Optional[Callable] = None, **kw):
        super().__init__(method, graph, n_robots, rate, n_tasks, seed, **kw)
        assert route_mode in ROUTE_MODES and idle_mode in IDLE_MODES
        self.route_mode, self.idle_mode = route_mode, idle_mode
        self.route_agent, self.idle_agent = route_agent, idle_agent
        self.epsilon = epsilon
        self.rng_explore = random.Random((explore_seed if explore_seed is not None else seed)
                                         * 7_919 + 3)
        self.on_route_transition = on_route_transition
        self.on_idle_transition = on_idle_transition
        self.nodes, self.shelf_list, self.shelf_dist, self.len_dist, self.diameter = \
            static_tables(graph)
        self.node_index = {n: i for i, n in enumerate(self.nodes)}
        self.n_nodes = len(self.nodes)
        self.n_edges = sum(1 for _ in graph.G.edges)
        # demande : vecteur fixe sur les racks (train_fit) ou None = en ligne
        self.demand_prior = (np.array([demand_prior.get(s, 0.0) for s in self.shelf_list])
                             if demand_prior is not None else None)
        self._online_counts = np.ones(len(self.shelf_list))
        self._counted_tasks = 0
        self.shelf_index = {s: i for i, s in enumerate(self.shelf_list)}
        self.dock = 'charging_dock'
        self.block_start: Dict[tuple, float] = {}
        self._pen_cache: Dict[str, Dict[str, float]] = {}
        # compteurs
        self.edge_conflicts = 0
        self.route_decisions = 0
        self.route_time = 0.0
        self.idle_decisions = 0
        self.idle_time = 0.0
        self.fallbacks = 0
        self.holds = 0
        self.block_version = 0
        self.squash_p0 = 3.0 * self.diameter
        for r in self.robots:
            r.hold_left = 0
            r.hold_version = -1
            r.prev = None
            r.route = []
            r.n_moves = 0
            r.node_wait = 0.0
            r.park = None
            r.need_idle = True
            r.route_pending = None      # (feat, t_decision)
            r.idle_pending = None       # [feat, t_decision, reward or None]

    # ------------------------------------------------------------------ #
    def _invalidate(self):
        super()._invalidate()
        self._pen_cache.clear()

    def blockages(self):
        before = set(self.blocked)
        super().blockages()
        if set(self.blocked) != before:
            self.block_version += 1
        for e in set(self.blocked) - before:
            self.block_start[e] = self.t
        for e in before - set(self.blocked):
            self.block_start.pop(e, None)

    def squash(self, x):
        """Fonction strictement croissante : identite jusqu'a 3 x diametre,
        pente 0,001 au-dela (couts des aretes bloquees). L'argmax du terme a
        priori est inchange ; les valeurs restent a l'echelle du retour."""
        p0 = self.squash_p0
        return x if x <= p0 else p0 + 0.001 * (x - p0)

    def _is_blocked(self, u, v):
        return bool(self.g.G[u][v].get('blocked', False))

    def _block_elapsed(self, u, v):
        e = (u, v) if (u, v) in self.block_start else (v, u)
        return self.t - self.block_start[e] if e in self.block_start else 0.0

    def dist_pen(self, goal):
        """Distance au but (couts en direct, arete bloquee = longueur + P)
        pour tous les noeuds : Dijkstra inverse depuis ``goal``."""
        if goal in self._pen_cache:
            return self._pen_cache[goal]
        G = self.g.G
        dist = {goal: 0.0}
        heap = [(0.0, goal)]
        while heap:
            d, y = heapq.heappop(heap)
            if d > dist[y]:
                continue
            for x in G._adj[y]:            # graphe symetrique : x -> y existe
                data = G[x][y]
                c = (data['base_weight'] + BLOCK_PENALTY_M if data.get('blocked')
                     else data['base_weight'] + 2.0 * data.get('congestion', 0.0))
                nd = d + c
                if nd < dist.get(x, math.inf):
                    dist[x] = nd
                    heapq.heappush(heap, (nd, x))
        self._pen_cache[goal] = dist
        return dist

    def static_path(self, src, dst):
        """Plus court chemin sur les longueurs, aretes bloquees exclues."""
        G = self.g.G
        dist, prev = {src: 0.0}, {}
        heap = [(0.0, src)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            if u == dst:
                path = [dst]
                while path[-1] != src:
                    path.append(prev[path[-1]])
                return path[::-1]
            for v, data in G._adj[u].items():
                if data.get('blocked'):
                    continue
                nd = d + data['base_weight']
                if nd < dist.get(v, math.inf):
                    dist[v], prev[v] = nd, u
                    heapq.heappush(heap, (nd, v))
        return []

    # ------------------------------------------------------------------ #
    def assign(self, task, r):
        super().assign(task, r)

    def start(self, r, task):
        super().start(r, task)
        r.route, r.n_moves = [], 0
        r.route_pending = None

    def _enter_edge(self, r, u, v):
        G = self.g.G
        cong = G[u][v].get('congestion', 0.0)
        if cong > 0 or G[v][u].get('congestion', 0.0) > 0:
            self.edge_conflicts += 1
        base = G[u][v]['base_weight']
        r.edge, r.edge_left = (u, v), base / r.speed * (1.0 + self.slow * cong)
        r.distance += base
        self.g.update_congestion(u, v, 1.0)
        self._invalidate()

    def _advance_edge(self, r):
        r.edge_left -= self.dt
        if r.edge_left <= 0:
            u, v = r.edge
            self.g.update_congestion(u, v, -1.0)
            self._invalidate()
            r.prev, r.node, r.edge = u, v, None

    def move(self, r):
        if r.task is None:
            if r.queue:
                self.start(r, r.queue.pop(0))
            else:
                self._idle_tick(r)
                return
        r.busy_time += self.dt
        if r.pick_left > 0:
            r.pick_left -= self.dt
            if r.pick_left <= 0:
                r.task.done = self.t
                r.n_done += 1
                r.task = None
                r.need_idle = True
            return
        if r.edge is not None:
            self._advance_edge(r)
            return
        if r.node == r.task.target:
            r.task.arrived = self.t
            self._route_close(r, terminal=True)
            self._idle_reward(r, r.task)
            r.pick_left = self.pick_time
            return
        if r.hold_left > 0 and r.hold_version == self.block_version:
            v = HOLD                     # attente choisie en cours (au plus 1 s)
            r.hold_left -= 1
        else:
            r.hold_left = 0
            t0 = time.perf_counter()
            v = self._next_hop(r)
            self.route_time += time.perf_counter() - t0
            self.route_decisions += 1
            if v == HOLD:
                self.holds += 1
                r.hold_left = HOLD_TICKS - 1
                r.hold_version = self.block_version
        if v is None or v == HOLD:
            r.wait += self.dt
            r.node_wait += self.dt
            if r.wait >= self.timeout:
                r.task.failed, r.task.done = True, self.t
                self._route_close(r, terminal=True)
                r.hold_left = 0
                r.task = None
                r.need_idle = True
            return
        r.n_moves += 1
        self._enter_edge(r, r.node, v)

    # ----- routage ------------------------------------------------------- #
    def _next_hop(self, r):
        goal = r.task.target
        if self.route_mode == 'dijkstra_dynamique':
            path, _ = self.g.shortest_path(r.node, goal)
            return path[1] if len(path) >= 2 else None
        if self.route_mode == 'dijkstra_statique':
            ok = (len(r.route) >= 2 and r.route[0] == r.node
                  and not self._is_blocked(r.route[0], r.route[1]))
            if not ok:
                r.route = self.static_path(r.node, goal)
                if len(r.route) < 2:
                    r.route = []
                    return None
            r.route = r.route[1:]
            return r.route[0]
        # drl_route
        if r.n_moves > 3 * self.n_nodes:
            self.fallbacks += 1
            self._route_close(r, terminal=True)
            path, _ = self.g.shortest_path(r.node, goal)
            return path[1] if len(path) >= 2 else None
        cands, feats = self.route_candidates(r)
        if len(cands) == 1:
            j = 0
        elif self.epsilon > 0 and self.rng_explore.random() < self.epsilon:
            j = self.rng_explore.randrange(len(cands))
        else:
            q = self.route_agent.scores(feats)
            j = int(np.argmax(q))
        if self.on_route_transition is not None:
            if r.route_pending is not None:
                f0, t0 = r.route_pending
                self.on_route_transition(f0, -(self.t - t0) / REWARD_NORM_S, feats, False)
            r.route_pending = (feats[j], self.t)
        c = cands[j]
        if c == HOLD or self._is_blocked(r.node, c):
            return HOLD
        return c

    def _route_close(self, r, terminal):
        if r.route_pending is not None and self.on_route_transition is not None:
            f0, t0 = r.route_pending
            self.on_route_transition(f0, -(self.t - t0) / REWARD_NORM_S,
                                     np.zeros((0, N_ROUTE_FEATURES), dtype=np.float32), terminal)
        r.route_pending = None

    def route_candidates(self, r):
        """Candidats (voisins tries + attente) et leurs caracteristiques."""
        G = self.g.G
        u, goal = r.node, r.task.target
        D = REWARD_NORM_S * r.speed
        dpen = self.dist_pen(goal)
        dlen = self.len_dist[goal]
        path, _ = self.g.shortest_path(u, goal)
        h = path[1] if len(path) >= 2 else HOLD
        others = [o for o in self.robots if o is not r]
        cap = max(1, int(G.nodes[goal].get('capacity', 1)))
        goal_load = sum(1 for o in others
                        if (o.task is not None and o.task.target == goal)
                        or any(k.target == goal for k in o.queue)) / cap
        n_blk = sum(1 for _ in self.blocked) * 2 / max(1, self.n_edges)
        sq = self.squash
        d_here = sq(min(dpen.get(u, math.inf), 3 * BLOCK_PENALTY_M))
        cands, feats = [], []
        for v in sorted(G._adj[u]):
            data = G[u][v]
            blk = bool(data.get('blocked'))
            base = data['base_weight']
            c = base + BLOCK_PENALTY_M if blk else base + 2.0 * data.get('congestion', 0.0)
            dv_raw = min(dpen.get(v, math.inf), 3 * BLOCK_PENALTY_M)
            dv = sq(dv_raw)
            prior = -sq(c + dv_raw) / D + (TIE_BONUS if v == h else 0.0)
            on_edge = data.get('congestion', 0.0) + G[v][u].get('congestion', 0.0)
            toward = sum(1 for o in others if o.edge is not None and o.edge[1] == v)
            at_v = sum(1 for o in others if o.edge is None and o.node == v)
            feats.append([
                prior, base / 10.0, on_edge / 3.0, toward / 3.0, at_v / 3.0, float(blk),
                self._block_elapsed(u, v) / 120.0 if blk else 0.0,
                dv / D, dlen.get(v, 0.0) / D, goal_load,
                r.speed / 0.5, float(v == r.prev), 0.0, d_here / D,
                n_blk, float(v == h)])
            cands.append(v)
        d_here_raw = min(dpen.get(u, math.inf), 3 * BLOCK_PENALTY_M)
        prior_w = -sq(d_here_raw + WAIT_DELTA_M) / D + (TIE_BONUS if h == HOLD else 0.0)
        feats.append([prior_w, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d_here / D,
                      dlen.get(u, 0.0) / D, goal_load, r.speed / 0.5, 0.0, 1.0,
                      d_here / D, n_blk, float(h == HOLD)])
        cands.append(HOLD)
        return cands, np.asarray(feats, dtype=np.float32)

    # ----- robots inoccupes ---------------------------------------------- #
    def demand(self):
        if self.demand_prior is not None:
            p = self.demand_prior
        else:
            while self._counted_tasks < len(self.tasks):
                k = self.tasks[self._counted_tasks]
                if k.target in self.shelf_index:
                    self._online_counts[self.shelf_index[k.target]] += 1
                self._counted_tasks += 1
            p = self._online_counts
        return p / p.sum()

    def _idle_tick(self, r):
        if r.edge is not None:
            self._advance_edge(r)
            return
        if r.need_idle:
            r.need_idle = False
            if self.idle_mode != 'rester_sur_place':
                t0 = time.perf_counter()
                r.park = self._choose_park(r)
                self.idle_time += time.perf_counter() - t0
                self.idle_decisions += 1
        if r.park is not None and r.park != r.node:
            path, _ = self.g.shortest_path(r.node, r.park)
            if len(path) >= 2:
                self._enter_edge(r, r.node, path[1])

    def expected_dist(self):
        """E_p[d(n, rack)] pour chaque noeud (vecteur indexe comme self.nodes)."""
        return self.shelf_dist @ self.demand()

    def _choose_park(self, r):
        if self.idle_mode == 'retour_au_depot':
            return self.dock
        ed = self.expected_dist()
        center = self.nodes[int(np.argmin(ed))]
        if self.idle_mode == 'centre_de_demande':
            return center
        cands, feats = self.idle_candidates(r, ed, center)
        if self.epsilon > 0 and self.rng_explore.random() < self.epsilon:
            j = self.rng_explore.randrange(len(cands))
        else:
            j = int(np.argmax(self.idle_agent.scores(feats)))
        if self.on_idle_transition is not None:
            if r.idle_pending is not None:
                f0, _, rew = r.idle_pending
                self.on_idle_transition(f0, rew if rew is not None else 0.0, feats, False)
            r.idle_pending = [feats[j], self.t, None]
        return cands[j]

    def _idle_reward(self, r, task):
        """Recompense de la derniere decision d'attente : -(approche)/60."""
        if r.idle_pending is not None and r.idle_pending[2] is None and task.assigned is not None:
            r.idle_pending[2] = -(task.arrived - task.assigned) / REWARD_NORM_S

    def idle_candidates(self, r, ed, center):
        order = list(np.argsort(ed, kind='stable'))
        cands = []
        for n in [r.node, self.dock, center] + [self.nodes[i] for i in order]:
            if n not in cands:
                cands.append(n)
            if len(cands) == K_IDLE:
                break
        D = REWARD_NORM_S * r.speed
        p = self.demand()
        others_idle = [o for o in self.robots if o is not r and self.idle(o)]
        spots = [o.park if o.park is not None else o.node for o in others_idle]
        n_free = sum(1 for o in self.robots if self.idle(o))
        e_center = ed[self.node_index[center]]
        feats = []
        for c in cands:
            i = self.node_index[c]
            dc = self.len_dist[c]
            near = [dc[s] for s in spots]
            mass = sum(p[self.shelf_index[s]] for s in [c] + list(self.g.G._adj[c])
                       if s in self.shelf_index)
            feats.append([
                -ed[i] / D + (TIE_BONUS if c == center else 0.0),
                dc[r.node] / D, sum(1 for s in spots if s == c) / 3.0,
                min(min(near), 2 * D) / D if near else 2.0, mass,
                float(c == r.node), float(c == self.dock), float(c == center),
                n_free / len(self.robots), len(self.open) / len(self.robots), r.speed / 0.5,
                (ed[i] - e_center) / D, len(self.robots) / 20.0])
        return cands, np.asarray(feats, dtype=np.float32)

    # ------------------------------------------------------------------ #
    def run(self):
        out = super().run()
        if self.on_idle_transition is not None:
            for r in self.robots:
                if r.idle_pending is not None:
                    f0, _, rew = r.idle_pending
                    self.on_idle_transition(f0, rew if rew is not None else 0.0,
                                            np.zeros((0, N_IDLE_FEATURES), dtype=np.float32),
                                            True)
                    r.idle_pending = None
        for r in self.robots:
            self._route_close(r, terminal=True)
        return out

    def metrics(self):
        m = super().metrics()
        done = [k for k in self.tasks if k.done is not None and not k.failed]
        n = max(1, len(done))
        trav = [k.arrived - k.started for k in done if getattr(k, 'arrived', None) is not None]
        appr = [k.arrived - k.assigned for k in done if getattr(k, 'arrived', None) is not None]
        m.update({
            'temps_trajet_moy_s': statistics.mean(trav) if trav else math.nan,
            'approche_moy_s': statistics.mean(appr) if appr else math.nan,
            'conflits_aretes_pour_100_taches': 100.0 * self.edge_conflicts / n,
            'attente_noeud_par_tache_s': sum(r.node_wait for r in self.robots) / n,
            'ms_par_decision_route': 1000.0 * self.route_time / max(1, self.route_decisions),
            'ms_par_decision_attente': (1000.0 * self.idle_time / self.idle_decisions
                                        if self.idle_decisions else 0.0),
            'decisions_route': self.route_decisions,
            'decisions_attente': self.idle_decisions,
            'replis_dijkstra': self.fallbacks,
            'attentes_choisies': self.holds,
        })
        return m
