"""
alloc6.py
---------
Phase C du protocole v6 : allocation avec anticipation (``drl_alloc6``).

Decision (a chaque pas de temps, tant qu'il reste un robot libre non retenu et
une tache candidate) : parmi
  - les couples (robot libre, tache parmi les 5 plus anciennes dont la cible a
    de la place), comme greedy_pair ;
  - une action "attendre un pas" par robot libre : le robot n'est pas attribue
    pendant HOLD_S = 1 s (il garde sa place pour une tache attendue).
Q residuel (V4DQN, Q = x[0] + f_theta) :
  couple   x[0] = -cout / diametre                       (= greedy_pair)
  attente  x[0] = -(meilleur cout du robot + 0,05 diametre) / diametre
Avec f_theta = 0, la politique est exactement greedy_pair (meme ordre des
couples, meme depart des egalites ; l'attente n'est jamais la meilleure).

Entrees : les 18 caracteristiques v3 (features_v3, premiere negee) + 9
caracteristiques d'anticipation, dont une PREVISION DE LA DEMANDE PAR ZONE
(zone = rayon 0,15 x diametre autour d'un noeud) apprise sur la partie
ENTRAINEMENT (train_fit) du decoupage chronologique 70/30 de Footwear.

Recompense (comme env_v3) de la decision k :
  -( attente cumulee des taches ouvertes jusqu'a la decision suivante
     + temps de service (attribution -> fin) de la tache attribuee, ou 0 pour
       une attente ; +120 s si la tache echoue ou n'est pas finie ) / 60.
La somme des recompenses d'un episode vaut -(somme des temps de traitement)/60.
"""

from __future__ import annotations

import math
import statistics

import numpy as np

from warehouse_marl.drl.features_v3 import N_FEATURES_V3
from warehouse_marl.drl.v6_sim import LOCAL_RADIUS, BenchmarkV6

HOLD_S = 1.0
HOLD_MARGIN = 0.05            # fraction du diametre ajoutee au cout de l'attente
REWARD_NORM_S = 60.0
FAILURE_PENALTY_S = 120.0
N_EXTRA = 9
N_ALLOC6_FEATURES = N_FEATURES_V3 + N_EXTRA
EXTRA_NAMES = ('est_attente', 'prevision_zone_robot', 'prevision_zone_cible',
               'temps_prochaine_arrivee_zone', 'arrivees_par_traversee', 'cout_vs_attendu',
               'meilleur_cout_robot', 'libres_dans_zone', 'attentes_consecutives')


class AllocBenchmark(BenchmarkV6):
    """Banc v6 (sans capacite, dijkstra_dynamique, rester_sur_place) avec
    l'allocation drl_alloc6."""

    def __init__(self, method, graph, n_robots, rate, n_tasks, seed, alloc6_agent=None,
                 forecast=None, on_alloc6_transition=None, **kw):
        self.alloc6 = method == 'drl_alloc6'
        super().__init__('greedy_pair' if self.alloc6 else method, graph, n_robots, rate,
                         n_tasks, seed, **kw)
        self.rate = rate
        self.agent6 = alloc6_agent
        self.cb6 = on_alloc6_transition
        # prevision par rack (train_fit) ; uniforme si absente
        if forecast is not None:
            f = np.array([forecast.get(s, 0.0) for s in self.shelf_list], dtype=np.float64)
        else:
            f = np.ones(self.n_shelves)
        self.forecast = f / f.sum()
        rad = LOCAL_RADIUS * self.diameter
        # masse prevue dans la zone de chaque noeud
        self.zone_mass = (self.shelf_dist <= rad + 1e-9).astype(np.float64) @ self.forecast
        self.exp_dist = self.shelf_dist @ self.forecast
        self.hold_until = {}
        self.n_holds6 = 0
        self.consec = {}
        self._pending6 = []          # decisions dont la transition n'est pas finalisee
        self._last6 = None

    # ------------------------------------------------------------------ #
    def allocate(self):
        if not self.alloc6:
            return super().allocate()
        if self._last6 is not None:
            self._last6['wait'] += len(self.open) * self.dt
        while True:
            free = [r for r in self.robots if self.idle(r)
                    and self.hold_until.get(r.rid, -1.0) <= self.t + 1e-9]
            if not free:
                break
            cand = self.candidate_tasks()
            if not cand:
                break
            acts, feats = self.alloc6_candidates(free, cand)
            if self.epsilon > 0 and self.rng_explore.random() < self.epsilon:
                j = self.rng_explore.randrange(len(acts))
            else:
                j = int(np.argmax(self.agent6.scores(feats)))
            self._record(feats, j)
            r, task = acts[j]
            if task is None:
                self.hold_until[r.rid] = self.t + HOLD_S
                self.consec[r.rid] = self.consec.get(r.rid, 0) + 1
                self.n_holds6 += 1
            else:
                self.consec[r.rid] = 0
                self.assign_pair(r, task)
                self._last6['task'] = task

    def alloc6_candidates(self, free, cand):
        pairs = self._pairs_v3(free, cand)
        diam = max(self.diameter, 1.0)
        t_norm = diam / max(self.mean_speed, 1e-6)
        rad = LOCAL_RADIUS * self.diameter
        best = {}
        for r, k, f in pairs:
            best[r.rid] = min(best.get(r.rid, math.inf), f[0] * diam)
        free_idx = {r.rid: self.node_index[r.node] for r in free}
        nm = self.node_mat
        arrivals = self.rate * t_norm

        def extra(r, k, cost, hold):
            i = self.node_index[r.node]
            zm = self.zone_mass[i]
            nxt = 1.0 / max(self.rate * zm, 1e-9)
            near = sum(1 for o, j in free_idx.items() if o != r.rid and nm[i][j] <= rad + 1e-9)
            return [float(hold), zm,
                    0.0 if k is None else self.zone_mass[self.node_index[k.target]],
                    min(nxt / t_norm, 10.0) / 10.0, min(arrivals, 10.0) / 10.0,
                    0.0 if k is None else (cost - self.exp_dist[i]) / diam,
                    best[r.rid] / diam, near / len(self.robots),
                    min(self.consec.get(r.rid, 0), 5) / 5.0]

        acts, feats = [], []
        for r, k, f in pairs:
            x = list(f)
            x[0] = -f[0]
            feats.append(x + extra(r, k, f[0] * diam, False))
            acts.append((r, k))
        n = max(len(self.robots), 1)
        for r in free:
            x = [0.0] * N_FEATURES_V3
            x[0] = -(best[r.rid] + HOLD_MARGIN * diam) / diam
            x[3] = r.speed / max(self.mean_speed, 1e-6)
            x[14] = len(free) / n
            x[15] = min(len(self.open) / n, 5.0)
            x[17] = diam / 100.0
            feats.append(x + extra(r, None, 0.0, True))
            acts.append((r, None))
        return acts, np.asarray(feats, dtype=np.float32)

    # ----- transitions (comme env_v3) ----------------------------------- #
    def _record(self, feats, j):
        if self._last6 is not None:
            self._last6['next'] = feats
        rec = {'feat': feats[j], 'task': None, 'wait': 0.0, 'next': None, 'terminal': False}
        if self.cb6 is not None:
            self._pending6.append(rec)
        self._last6 = rec
        self._flush(False)

    def _service(self, rec, over):
        k = rec['task']
        if k is None:
            return 0.0
        if k.done is None:
            return (self.t - k.assigned + FAILURE_PENALTY_S) if over else None
        return k.done - k.assigned + (FAILURE_PENALTY_S if k.failed else 0.0)

    def _flush(self, over):
        if self.cb6 is None:
            return
        keep = []
        for rec in self._pending6:
            if rec['next'] is None and not over:
                keep.append(rec)
                continue
            s = self._service(rec, over)
            if s is None:
                keep.append(rec)
                continue
            nxt = rec['next'] if rec['next'] is not None else \
                np.zeros((0, N_ALLOC6_FEATURES), dtype=np.float32)
            self.cb6(rec['feat'], -(rec['wait'] + s) / REWARD_NORM_S, nxt,
                     rec['next'] is None)
        self._pending6 = keep

    def end_tick(self):
        fin = super().end_tick()
        if self.cb6 is not None and self._pending6 and int(self.t / self.dt) % 20 == 0:
            self._flush(False)
        return fin

    def run(self):
        out = super().run()
        self._flush(True)
        return out

    def metrics(self):
        m = super().metrics()
        m['attentes_allocation'] = self.n_holds6
        return m


def make_alloc_sim(sc, method, agent=None, epsilon=0.0, cb=None, explore_seed=None):
    from warehouse_marl.allocation_benchmark import build_grid_warehouse, mean_service_time
    from warehouse_marl.drl.train_v4 import PICK, SPEED, dataset, train_fit_demand
    dims, R = sc['dims'], sc['robots']
    g = build_grid_warehouse(*dims)
    speeds = sc.get('speeds')
    mean_speed = statistics.mean(speeds) if speeds else SPEED
    targets = None
    if sc.get('split'):
        ds = dataset()
        service = ds.service_time(g, mean_speed, PICK)
        targets = ds.targets(g, sc['split'], sc['start'], sc['tasks'])
    else:
        service = mean_service_time(g, mean_speed, PICK)
    rate = sc['rho'] * R / service
    return AllocBenchmark(method, g, R, rate, sc['tasks'], seed=sc['seed'], speed=SPEED,
                          pick_time=PICK, speeds=speeds, block_rate=sc.get('block_rate', 0.0),
                          targets=targets, alloc6_agent=agent, forecast=train_fit_demand(g),
                          on_alloc6_transition=cb, epsilon=epsilon, explore_seed=explore_seed)
