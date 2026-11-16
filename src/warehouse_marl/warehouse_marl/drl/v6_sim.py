"""
v6_sim.py
---------
Simulateur v6 (PROTOCOLE_V6.md) : sous-classe de ``BenchmarkV4`` qui ajoute

Phase A (point d'attente des robots inoccupes, taille variable)
  idle_mode 'couverture'  : heuristique de couverture gloutonne. Le robot
        inoccupe va au noeud c qui minimise
            cov(c) = E_p[ min( d(c, rack), min_{o inoccupe} d(o, rack) ) ]
        (o : points d'attente des AUTRES robots inoccupes) ; il reste sur place
        si sa position fait aussi bien. Sert de terme a priori a drl_idle6
        (f_theta = 0 -> couverture, a l'identique) ; rapportee a titre
        DESCRIPTIF, ce n'est pas un des trois concurrents du protocole.
  idle_mode 'drl_idle6'   : DQN residuel, Q(c) = -cov(c)/diametre + f_theta(x_c),
        entrees independantes de la taille (distances / diametre du graphe,
        ratio robots/racks, demande locale en fraction).

Phase B (routage avec congestion)
  edge_capacity=1 : un segment d'allee (arete, les deux sens confondus)
        accueille au plus 1 robot ; un robot qui veut entrer dans un segment
        occupe attend au noeud, dans une file FIFO propre au segment. Les
        noeuds n'ont pas de capacite : il ne peut donc pas y avoir
        d'interblocage (tout segment occupe se libere en temps fini).
  route_mode 'dijkstra_congestion' : replanification a chaque pas de temps
        passe a un noeud ; cout d'une arete = longueur + v x (temps restant
        de l'occupant) + longueur x (robots en file devant soi).
  route_mode 'drl_route6' : DQN residuel, Q(u->v) = -(c(u,v) + d_cong(v))/D
        + f_theta(x), entrees : occupation des prochains segments et
        reservations des autres robots (leurs prochains segments prevus, avec
        heures d'arrivee estimees). f_theta = 0 -> dijkstra_congestion.

Avec edge_capacity=None et les modes v4, le comportement est celui de
BenchmarkV4 a l'identique (teste dans test_v6.py).
"""

from __future__ import annotations

import heapq
import math
import time
from typing import Dict, List, Optional

import numpy as np

from warehouse_marl.drl.v4_sim import (
    BLOCK_PENALTY_M, HOLD, HOLD_TICKS, REWARD_NORM_S, TIE_BONUS, WAIT_DELTA_M, BenchmarkV4,
    static_tables)

ROUTE_MODES_V6 = ('dijkstra_statique', 'dijkstra_dynamique', 'dijkstra_congestion',
                  'drl_route', 'drl_route6')
IDLE_MODES_V6 = ('rester_sur_place', 'retour_au_depot', 'centre_de_demande', 'drl_idle',
                 'couverture', 'drl_idle6')

K_IDLE6 = 6
LOCAL_RADIUS = 0.15          # rayon "local" en fraction du diametre
N_IDLE6_FEATURES = 20
IDLE6_FEATURE_NAMES = (
    'prior_q', 'dist_attendue_seul', 'ecart_au_centre', 'gain_vs_rester', 'ecart_au_meilleur',
    'dist_robot_candidat', 'inoccupes_au_candidat', 'dist_inoccupe_plus_proche',
    'demande_locale', 'demande_locale_vs_uniforme', 'inoccupes_locaux', 'occupes_cibles_locales',
    'est_position', 'est_depot', 'est_centre', 'est_couverture', 'part_libres',
    'taches_ouvertes_par_robot', 'vitesse_relative', 'ratio_robots_racks')

N_ROUTE6_FEATURES = 22
ROUTE6_FEATURE_NAMES = (
    'prior_q', 'longueur', 'segment_occupe', 'reste_occupant', 'occupant_meme_sens',
    'file_devant', 'reservations_segment', 'reservations_sens_inverse', 'occupation_chemin',
    'file_chemin', 'reservations_chemin', 'dist_but_voisin_congestion',
    'dist_but_voisin_longueurs', 'dist_but_ici', 'robots_au_voisin', 'robots_vers_voisin',
    'demi_tour', 'attente', 'choix_heuristique', 'densite_robots', 'attente_file_cumulee',
    'vitesse')
RES_HORIZON = 4              # segments prevus par robot pour les reservations
PATH_LOOKAHEAD = 3           # segments regardes sur le chemin depuis le voisin

_NODE_MAT: Dict[tuple, np.ndarray] = {}


def node_matrix(graph):
    """Matrice noeuds x noeuds des distances sur longueurs (ordre static_tables)."""
    nodes, _, _, full, _ = static_tables(graph)
    key = tuple(sorted(graph.G.nodes))
    if key not in _NODE_MAT:
        _NODE_MAT[key] = np.array([[full[a][b] for b in nodes] for a in nodes])
    return _NODE_MAT[key]


def seg_key(u, v):
    return (u, v) if u < v else (v, u)


class BenchmarkV6(BenchmarkV4):
    def __init__(self, method, graph, n_robots, rate, n_tasks, seed,
                 route_mode='dijkstra_dynamique', idle_mode='rester_sur_place',
                 edge_capacity: Optional[int] = None, route6_agent=None, idle6_agent=None,
                 on_route6_transition=None, on_idle6_transition=None, **kw):
        v4_route = route_mode if route_mode in ('dijkstra_statique', 'dijkstra_dynamique',
                                                'drl_route') else 'dijkstra_dynamique'
        v4_idle = idle_mode if idle_mode in ('rester_sur_place', 'retour_au_depot',
                                             'centre_de_demande', 'drl_idle') \
            else 'centre_de_demande'
        super().__init__(method, graph, n_robots, rate, n_tasks, seed,
                         route_mode=v4_route, idle_mode=v4_idle, **kw)
        assert route_mode in ROUTE_MODES_V6 and idle_mode in IDLE_MODES_V6
        assert edge_capacity in (None, 1)
        self.route_mode, self.idle_mode = route_mode, idle_mode
        self.capacity = edge_capacity
        self.route6_agent, self.idle6_agent = route6_agent, idle6_agent
        self.on_route6_transition = on_route6_transition
        self.on_idle6_transition = on_idle6_transition
        # Ecart 4 (PROTOCOLE_V6.md) : decision d'attente non suivie d'une tache
        # (fin d'episode, ou tache echouee) : 'zero' = recompense 0 (modele
        # petit, comme la v4) ; 'ignorer' = transition non apprise (tronquee).
        self.idle6_unrewarded = 'zero'
        # Ecart 5 : 'individuelle' (approche des taches du robot) ou 'equipe'
        # (approches de TOUTES les taches attribuees dans la fenetre de la
        # decision, / R) ; en 'equipe', les decisions sans decision suivante du
        # meme robot sont tronquees (non apprises).
        self.idle6_reward = 'individuelle'
        self._team_open: Dict[str, dict] = {}
        self._team_wait: List[dict] = []
        self.node_mat = node_matrix(graph)
        self.n_shelves = len(self.shelf_list)
        self.mean_speed = float(np.mean([r.speed for r in self.robots]))
        # capacite des segments
        self.seg_occ: Dict[tuple, object] = {}
        self.seg_queue: Dict[tuple, List] = {}
        self.queue_wait_total = 0.0
        self._cong_cache: Dict[str, tuple] = {}
        self._cong_tick = -1.0
        self._res_tick = -1.0
        self._res_table: Dict[tuple, list] = {}
        self._nh_cache: Dict[tuple, Optional[str]] = {}
        self.route6_fallbacks = 0
        for r in self.robots:
            r.queued_seg = None
            r.queue_req_t = -1.0
            r.queue_wait = 0.0
            r.n_decisions = 0
            r.goal = None

    # ================================================================== #
    # Capacite des segments (phase B)
    # ================================================================== #
    def _active_queue(self, seg):
        """File du segment, sans les entrees perimees (robot qui ne demande
        plus ce segment depuis plus d'un pas)."""
        q = self.seg_queue.get(seg)
        if not q:
            return []
        live = [o for o in q if o.queued_seg == seg and o.edge is None
                and o.queue_req_t >= self.t - self.dt - 1e-9]
        if len(live) != len(q):
            self.seg_queue[seg] = live
        return live

    def _leave_queue(self, r):
        if r.queued_seg is not None:
            q = self.seg_queue.get(r.queued_seg)
            if q and r in q:
                q.remove(r)
            r.queued_seg = None

    def _can_enter(self, r, u, v):
        """True si r peut entrer dans (u, v) maintenant ; sinon r est (ou
        reste) dans la file du segment."""
        if self.capacity is None:
            return True
        seg = seg_key(u, v)
        if r.queued_seg != seg:
            self._leave_queue(r)
            self.seg_queue.setdefault(seg, []).append(r)
            r.queued_seg = seg
        r.queue_req_t = self.t
        q = self._active_queue(seg)
        return self.seg_occ.get(seg) is None and q and q[0] is r

    def _enter_edge(self, r, u, v):
        if self.capacity is not None:
            self._leave_queue(r)
            self.seg_occ[seg_key(u, v)] = r
        super()._enter_edge(r, u, v)

    def _advance_edge(self, r):
        e = r.edge
        super()._advance_edge(r)
        if self.capacity is not None and r.edge is None:
            seg = seg_key(*e)
            if self.seg_occ.get(seg) is r:
                del self.seg_occ[seg]

    def _queue_wait_tick(self, r):
        r.node_wait += self.dt
        r.queue_wait += self.dt
        self.queue_wait_total += self.dt

    # ================================================================== #
    # Deplacement (copie de BenchmarkV4.move avec la capacite)
    # ================================================================== #
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
            self._leave_queue(r)
            self._route_close(r, terminal=True)
            self._route6_close(r, terminal=True)
            self._idle_reward(r, r.task)
            self._idle6_reward(r, r.task)
            r.pick_left = self.pick_time
            return
        if r.hold_left > 0 and r.hold_version == self.block_version:
            v = HOLD
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
            self._leave_queue(r)
            r.wait += self.dt
            r.node_wait += self.dt
            if r.wait >= self.timeout:
                r.task.failed, r.task.done = True, self.t
                self._route_close(r, terminal=True)
                self._route6_close(r, terminal=True)
                r.hold_left = 0
                r.task = None
                r.need_idle = True
            return
        if not self._can_enter(r, r.node, v):
            self._queue_wait_tick(r)
            return
        r.n_moves += 1
        self._enter_edge(r, r.node, v)

    def start(self, r, task):
        super().start(r, task)
        r.n_decisions = 0
        r.route6_pending = None

    # ================================================================== #
    # Routage v6
    # ================================================================== #
    def _next_hop(self, r):
        if self.route_mode == 'dijkstra_congestion':
            return self._cong_next_hop(r, r.task.target)
        if self.route_mode == 'drl_route6':
            return self._drl6_next_hop(r)
        return super()._next_hop(r)

    def _seg_cost(self, x, y, r=None):
        """Cout (m) d'entree dans x->y : longueur + attente estimee convertie
        en metres (temps restant de l'occupant + longueur par robot en file
        devant). ``r`` : robot qui decide (seulement les robots devant lui) ;
        None : file entiere, vitesse moyenne de la flotte."""
        data = self.g.G[x][y]
        if data.get('blocked'):
            return math.inf
        L = data['base_weight']
        if self.capacity is None:
            return L + 2.0 * data.get('congestion', 0.0)
        seg = seg_key(x, y)
        occ = self.seg_occ.get(seg)
        q = self._active_queue(seg)
        if r is not None and r in q:
            nq = q.index(r)
        else:
            nq = len(q)
        if occ is r:
            occ = None
        sp = r.speed if r is not None else self.mean_speed
        rem = occ.edge_left if occ is not None else 0.0
        return L + sp * max(0.0, rem) + L * nq

    def _cong_dist(self, goal):
        """Distance a ``goal`` sur les couts _seg_cost generiques (Dijkstra
        inverse) et successeur sur ce chemin. Cache valable un pas de temps."""
        if self._cong_tick != self.t:
            self._cong_cache.clear()
            self._cong_tick = self.t
        if goal in self._cong_cache:
            return self._cong_cache[goal]
        G = self.g.G
        dist, succ = {goal: 0.0}, {goal: None}
        heap = [(0.0, goal)]
        while heap:
            d, y = heapq.heappop(heap)
            if d > dist[y]:
                continue
            for x in G._adj[y]:
                c = self._seg_cost(x, y)
                if c == math.inf:
                    continue
                nd = d + c
                if nd < dist.get(x, math.inf) - 1e-12:
                    dist[x], succ[x] = nd, y
                    heapq.heappush(heap, (nd, x))
        self._cong_cache[goal] = (dist, succ)
        return dist, succ

    def _cong_values(self, r, goal):
        """[(v, c(u,v;r), d_cong(v))] pour les voisins de r.node, tries."""
        dist, _ = self._cong_dist(goal)
        out = []
        for v in sorted(self.g.G._adj[r.node]):
            c = self._seg_cost(r.node, v, r)
            out.append((v, c, dist.get(v, math.inf)))
        return out

    def _cong_next_hop(self, r, goal):
        best, bv = math.inf, None
        for v, c, dv in self._cong_values(r, goal):
            tot = c + dv
            if tot < best - 1e-12:
                best, bv = tot, v
        return bv

    def _idle_tick(self, r):
        """Comme BenchmarkV4._idle_tick, avec les modes v6 et la capacite."""
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
            if self.capacity is not None and self.route_mode == 'dijkstra_congestion':
                v = self._cong_next_hop(r, r.park)
            else:
                path, _ = self.g.shortest_path(r.node, r.park)
                v = path[1] if len(path) >= 2 else None
            if v is None:
                self._leave_queue(r)
                return
            if not self._can_enter(r, r.node, v):
                self._queue_wait_tick(r)
                return
            self._enter_edge(r, r.node, v)
        else:
            self._leave_queue(r)

    # ----- reservations des autres robots -------------------------------- #
    def _static_next(self, src, dst):
        key = (src, dst)
        if key not in self._nh_cache:
            dl = self.len_dist[dst]
            best, bv = math.inf, None
            for w, data in sorted(self.g.G._adj[src].items()):
                c = data['base_weight'] + dl.get(w, math.inf)
                if c < best - 1e-12:
                    best, bv = c, w
            self._nh_cache[key] = bv
        return self._nh_cache[key]

    def _goal_of(self, o):
        if o.task is not None:
            return o.task.target
        if o.queue:
            return o.queue[0].target
        return o.park

    def reservations(self):
        """seg -> [(debut, fin, (de, vers), robot)] : prochains segments prevus
        des robots (chemin le plus court sur les longueurs depuis leur prochain
        noeud), avec heures estimees ; recalcule une fois par pas de temps."""
        if self._res_tick == self.t:
            return self._res_table
        self._res_tick = self.t
        table: Dict[tuple, list] = {}
        for o in self.robots:
            goal = self._goal_of(o)
            if goal is None:
                continue
            if o.edge is not None:
                node, t = o.edge[1], max(0.0, o.edge_left)
            else:
                node, t = o.node, (o.pick_left if o.pick_left > 0 else 0.0)
            for _ in range(RES_HORIZON):
                if node == goal:
                    break
                nxt = self._static_next(node, goal)
                if nxt is None:
                    break
                dur = self.g.G[node][nxt]['base_weight'] / o.speed
                table.setdefault(seg_key(node, nxt), []).append((t, t + dur, (node, nxt), o))
                node, t = nxt, t + dur
        self._res_table = table
        return table

    def _res_count(self, table, seg, t0, t1, me, direction=None):
        n = 0
        for a, b, d, o in table.get(seg, ()):
            if o is me or b < t0 or a > t1:
                continue
            if direction is not None and d != direction:
                continue
            n += 1
        return n

    # ----- drl_route6 ------------------------------------------------------ #
    def _drl6_next_hop(self, r):
        goal = r.task.target
        r.n_decisions += 1
        if r.n_decisions > 20 * self.n_nodes or r.n_moves > 3 * self.n_nodes:
            self.route6_fallbacks += 1
            self._route6_close(r, terminal=True)
            return self._cong_next_hop(r, goal)
        cands, feats = self.route6_candidates(r, goal)
        if self.epsilon > 0 and self.rng_explore.random() < self.epsilon:
            j = self.rng_explore.randrange(len(cands))
        else:
            j = int(np.argmax(self.route6_agent.scores(feats)))
        if self.on_route6_transition is not None:
            if getattr(r, 'route6_pending', None) is not None:
                f0, t0 = r.route6_pending
                self.on_route6_transition(f0, -(self.t - t0) / REWARD_NORM_S, feats, False)
            r.route6_pending = (feats[j], self.t)
        c = cands[j]
        if c == HOLD or self._is_blocked(r.node, c):
            return HOLD
        return c

    def _route6_close(self, r, terminal):
        pend = getattr(r, 'route6_pending', None)
        if pend is not None and self.on_route6_transition is not None:
            f0, t0 = pend
            self.on_route6_transition(f0, -(self.t - t0) / REWARD_NORM_S,
                                      np.zeros((0, N_ROUTE6_FEATURES), dtype=np.float32),
                                      terminal)
        r.route6_pending = None

    def route6_candidates(self, r, goal):
        G = self.g.G
        u = r.node
        D = REWARD_NORM_S * r.speed
        sq = self.squash
        dist, succ = self._cong_dist(goal)
        dlen = self.len_dist[goal]
        vals = self._cong_values(r, goal)
        best, h = math.inf, HOLD
        for v, c, dv in vals:
            if c + dv < best - 1e-12:
                best, h = c + dv, v
        table = self.reservations()
        cap = 3 * BLOCK_PENALTY_M
        d_here_raw = min(best, cap)
        d_here = sq(d_here_raw)
        dens = len(self.robots) / max(1, self.n_nodes)
        at_node = {}
        toward = {}
        for o in self.robots:
            if o is r:
                continue
            if o.edge is None:
                at_node[o.node] = at_node.get(o.node, 0) + 1
            else:
                toward[o.edge[1]] = toward.get(o.edge[1], 0) + 1
        cands, feats = [], []
        for v, c, dv in vals:
            data = G[u][v]
            L = data['base_weight']
            seg = seg_key(u, v)
            occ = self.seg_occ.get(seg) if self.capacity is not None else None
            if occ is r:
                occ = None
            q = self._active_queue(seg) if self.capacity is not None else []
            nq = q.index(r) if r in q else len(q)
            c_fin = min(c, cap)
            t_in = max(0.0, (c_fin - L)) / r.speed
            t_out = t_in + L / r.speed
            res_seg = self._res_count(table, seg, 0.0, t_out, r)
            res_inv = self._res_count(table, seg, 0.0, t_out, r, direction=(v, u))
            # chemin prevu depuis v (successeurs du Dijkstra de congestion)
            occ_p = que_p = res_p = 0
            node, t = v, t_out
            for _ in range(PATH_LOOKAHEAD):
                nxt = succ.get(node)
                if nxt is None:
                    break
                s2 = seg_key(node, nxt)
                if self.capacity is not None:
                    occ_p += 1 if self.seg_occ.get(s2) not in (None, r) else 0
                    que_p += len(self._active_queue(s2))
                dur = G[node][nxt]['base_weight'] / r.speed
                res_p += self._res_count(table, s2, t, t + dur, r)
                node, t = nxt, t + dur
            dv_raw = min(dv, cap)
            prior = -sq(c_fin + dv_raw) / D + (TIE_BONUS if v == h else 0.0)
            feats.append([
                prior, L / 10.0, float(occ is not None),
                (max(0.0, occ.edge_left) / 10.0) if occ is not None else 0.0,
                float(occ is not None and occ.edge == (u, v)), nq / 3.0,
                res_seg / 3.0, res_inv / 3.0, occ_p / 3.0, que_p / 3.0, res_p / 3.0,
                sq(dv_raw) / D, dlen.get(v, 0.0) / D, d_here / D,
                at_node.get(v, 0) / 3.0, toward.get(v, 0) / 3.0, float(v == r.prev), 0.0,
                float(v == h), dens, min(r.queue_wait, 120.0) / 60.0, r.speed / 0.5])
            cands.append(v)
        prior_w = -sq(d_here_raw + WAIT_DELTA_M) / D + (TIE_BONUS if h == HOLD else 0.0)
        feats.append([prior_w, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                      d_here / D, dlen.get(u, 0.0) / D, d_here / D, 0.0, 0.0, 0.0, 1.0,
                      float(h == HOLD), dens, min(r.queue_wait, 120.0) / 60.0, r.speed / 0.5])
        cands.append(HOLD)
        return cands, np.asarray(feats, dtype=np.float32)

    # ================================================================== #
    # Point d'attente v6 (phase A)
    # ================================================================== #
    def _others_cover(self, r):
        """min_{o inoccupe != r} d(o, rack) pour chaque rack (inf s'il n'y en a pas)."""
        spots = [o.park if o.park is not None else o.node
                 for o in self.robots if o is not r and self.idle(o)]
        if not spots:
            return spots, np.full(self.n_shelves, np.inf)
        idx = [self.node_index[s] for s in spots]
        return spots, np.min(self.shelf_dist[idx], axis=0)

    def coverage(self, r, p=None):
        """cov(c) pour tous les noeuds c (vecteur indexe comme self.nodes)."""
        if p is None:
            p = self.demand()
        spots, m = self._others_cover(r)
        return np.minimum(self.shelf_dist, m[None, :]) @ p, spots

    def _cov_choice(self, cov, r):
        i_best = int(np.argmin(cov))
        i_here = self.node_index[r.node]
        return r.node if cov[i_here] <= cov[i_best] + 1e-9 else self.nodes[i_best]

    def _choose_park(self, r):
        if self.idle_mode == 'couverture':
            cov, _ = self.coverage(r)
            return self._cov_choice(cov, r)
        if self.idle_mode == 'drl_idle6':
            cands, feats = self.idle6_candidates(r)
            if self.epsilon > 0 and self.rng_explore.random() < self.epsilon:
                j = self.rng_explore.randrange(len(cands))
            else:
                j = int(np.argmax(self.idle6_agent.scores(feats)))
            if self.on_idle6_transition is not None and self.idle6_reward == 'equipe':
                rec = self._team_open.pop(r.rid, None)
                if rec is not None:
                    rec['next'] = feats
                    self._team_wait.append(rec)
                self._team_open[r.rid] = {'feat': feats[j], 'tasks': [], 'next': None}
                self._team_finalize(False)
            elif self.on_idle6_transition is not None:
                pend = getattr(r, 'idle6_pending', None)
                if pend is not None:
                    f0, _, rew = pend
                    if rew is not None or self.idle6_unrewarded == 'zero':
                        self.on_idle6_transition(f0, rew if rew is not None else 0.0, feats,
                                                 False)
                r.idle6_pending = [feats[j], self.t, None]
            return cands[j]
        return super()._choose_park(r)

    # ----- recompense d'equipe (ecart 5) --------------------------------- #
    def assign(self, task, r):
        super().assign(task, r)
        if self.idle6_reward == 'equipe' and self.on_idle6_transition is not None:
            for rec in self._team_open.values():
                rec['tasks'].append(task)

    def _team_approach(self, k, over):
        if getattr(k, 'arrived', None) is not None:
            return k.arrived - k.assigned
        if k.done is not None:                    # echouee
            return k.done - k.assigned
        return (self.t - k.assigned) if over else None

    def _team_finalize(self, over):
        """Transitions dont toutes les taches de la fenetre sont arrivees :
        recompense -(somme des approches) / (R x T_ref)."""
        keep = []
        scale = len(self.robots) * self.reward_scale_s()
        for rec in self._team_wait:
            appr = [self._team_approach(k, over) for k in rec['tasks']]
            if any(a is None for a in appr):
                keep.append(rec)
                continue
            self.on_idle6_transition(rec['feat'], -sum(appr) / scale, rec['next'], False)
        self._team_wait = keep

    def reward_scale_s(self):
        """Temps de reference de la recompense de drl_idle6 : diametre / vitesse
        moyenne (la recompense -approche/T_ref ne depend pas de la taille)."""
        return self.diameter / self.mean_speed

    def _idle6_reward(self, r, task):
        pend = getattr(r, 'idle6_pending', None)
        if pend is not None and pend[2] is None and task.assigned is not None:
            pend[2] = -(task.arrived - task.assigned) / self.reward_scale_s()

    def idle6_candidates(self, r):
        p = self.demand()
        cov, spots = self.coverage(r, p)
        ed = self.shelf_dist @ p
        center = self.nodes[int(np.argmin(ed))]
        h = self._cov_choice(cov, r)
        i_best = int(np.argmin(cov))
        order = list(np.argsort(cov, kind='stable'))
        cands = []
        for n in [r.node, self.dock, center, h] + [self.nodes[i] for i in order]:
            if n not in cands:
                cands.append(n)
            if len(cands) == K_IDLE6:
                break
        diam = self.diameter
        nm = self.node_mat
        rad = LOCAL_RADIUS * diam
        i_r = self.node_index[r.node]
        cov_here, cov_best = cov[i_r], cov[i_best]
        e_center = ed[self.node_index[center]]
        spot_idx = [self.node_index[s] for s in spots]
        busy_t = [self.node_index[o.task.target] for o in self.robots
                  if o is not r and o.task is not None]
        n_free = sum(1 for o in self.robots if self.idle(o))
        R = len(self.robots)
        shelf_rows = [self.node_index[s] for s in self.shelf_list]
        feats = []
        for c in cands:
            i = self.node_index[c]
            dvec = nm[i]
            local = self.shelf_dist[i] <= rad + 1e-9
            mass = float(p[local].sum())
            frac_racks = local.sum() / self.n_shelves
            near = [dvec[j] for j in spot_idx]
            feats.append([
                -cov[i] / diam + (TIE_BONUS if c == h else 0.0),
                ed[i] / diam, (ed[i] - e_center) / diam, (cov[i] - cov_here) / diam,
                (cov[i] - cov_best) / diam, nm[i_r][i] / diam,
                sum(1 for j in spot_idx if j == i) / R,
                min(min(near), diam) / diam if near else 1.0,
                mass, min(5.0, mass / frac_racks) / 5.0 if frac_racks > 0 else 0.0,
                sum(1 for j in spot_idx if dvec[j] <= rad + 1e-9) / R,
                sum(1 for j in busy_t if dvec[j] <= rad + 1e-9) / R,
                float(c == r.node), float(c == self.dock), float(c == center), float(c == h),
                n_free / R, min(3.0, len(self.open) / R) / 3.0, r.speed / self.mean_speed,
                5.0 * R / self.n_shelves])
        del shelf_rows
        return cands, np.asarray(feats, dtype=np.float32)

    # ================================================================== #
    def run(self):
        out = super().run()
        if self.on_idle6_transition is not None and self.idle6_reward == 'equipe':
            self._team_finalize(True)
            self._team_open.clear()
        elif self.on_idle6_transition is not None:
            for r in self.robots:
                pend = getattr(r, 'idle6_pending', None)
                if pend is not None:
                    f0, _, rew = pend
                    if rew is not None or self.idle6_unrewarded == 'zero':
                        self.on_idle6_transition(
                            f0, rew if rew is not None else 0.0,
                            np.zeros((0, N_IDLE6_FEATURES), dtype=np.float32), True)
                    r.idle6_pending = None
        for r in self.robots:
            self._route6_close(r, terminal=True)
        return out

    def metrics(self):
        m = super().metrics()
        done = [k for k in self.tasks if k.done is not None and not k.failed]
        n = max(1, len(done))
        m.update({'attente_file_par_tache_s': self.queue_wait_total / n,
                  'replis_route6': self.route6_fallbacks})
        return m
