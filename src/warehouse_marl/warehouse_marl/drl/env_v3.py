"""
env_v3.py
---------
Environnement du DRL v3 (residuel), construit comme env_v2 sur la
simulation du banc d'essai, avec trois differences :

1. Caracteristiques relatives v3 (features_v3), normalisees par le
   diametre du graphe.
2. Recompense sur le temps de service MESURE dans la simulation : la
   transition d'une decision n'est livree a l'apprenant qu'une fois sa
   tache terminee. Pour la decision k :
       r_k = -( attente cumulee des taches en file entre k et k+1
                + (fin - attribution) de la tache choisie, mesure
                + penalite si la tache echoue ou n'est pas finie
                + penalite de retard optionnelle ) / REWARD_NORM_S
             - reference
   La somme des r_k (hors reference) vaut moins la somme des temps de
   traitement des taches. Aucun terme ne regarde le choix de greedy_pair.
3. Reference de centrage FIGEE : ``reward_center`` est fixee une fois
   (train_drl_v3 la calcule avant l'entrainement avec la politique
   greedy_pair) et ne bouge plus ; None = pas de centrage.

``step()`` retourne les transitions finalisees dans ``info['transitions']``
: liste de (caracteristiques du couple choisi, recompense, couples de la
decision suivante, terminal, recompense brute).
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Sequence

import numpy as np

from warehouse_marl.drl.env_v2 import REWARD_NORM_S, make_benchmark
from warehouse_marl.drl.features_v3 import N_FEATURES_V3

# Distribution d'entrainement : (dims, plage de robots, poids)
TRAIN_SIZES = (((5, 3), (3, 4), 0.30), ((8, 5), (4, 8), 0.30),
               ((10, 8), (6, 12), 0.22), ((15, 10), (10, 20), 0.18))
TRAIN_RHOS = (0.5, 0.7, 0.9)
TRAIN_SPEEDS = (None, (0.4, 0.5, 0.6), (0.3, 0.5, 0.7), (0.25, 0.5, 0.75))
TRAIN_SKEWS = (0.0, 0.8, 1.5)
TRAIN_BLOCKS = ((0.0, 30.0, 120.0), (1.0 / 60, 30.0, 120.0), (1.0 / 60, 60.0, 300.0),
                (2.0 / 60, 60.0, 300.0))


def sample_training_scenario(rng: random.Random, n_tasks: int, sizes=TRAIN_SIZES) -> Dict:
    dims, (lo, hi), _ = rng.choices(sizes, weights=[w for _, _, w in sizes])[0]
    rate, bmin, bmax = rng.choice(TRAIN_BLOCKS)
    return {'dims': dims, 'robots': rng.randint(lo, hi), 'rho': rng.choice(TRAIN_RHOS),
            'speeds': rng.choice(TRAIN_SPEEDS), 'skew': rng.choice(TRAIN_SKEWS),
            'block_rate': rate, 'block_min': bmin, 'block_max': bmax,
            'deadline_base': 60.0, 'tasks': n_tasks, 'seed': rng.randrange(10 ** 9)}


class AllocationEnvV3:
    def __init__(self, seed: int = 0, n_tasks: int = 80, reward_center: Optional[float] = None,
                 failure_penalty_s: float = 120.0, late_penalty_s: float = 0.0,
                 sizes=TRAIN_SIZES, tasks_from: str = '', data_dir: Optional[str] = None):
        self._rng = random.Random(seed)
        self.n_tasks, self.sizes = n_tasks, sizes
        # tasks_from='footwear' : taches des vagues reelles de la partie
        # 'train_fit' du jeu de donnees (jamais de vague de test)
        self.tasks_from, self.data_dir = tasks_from, data_dir
        self._starts = None
        self.reward_center = reward_center
        self.failure_penalty_s, self.late_penalty_s = failure_penalty_s, late_penalty_s
        self.bench = None
        self.pairs: List = []
        self.scenario: Dict = {}
        self._pending: List[Dict] = []
        self._alloc_phase = False

    # ------------------------------------------------------------------ #
    def sample_scenario(self) -> Dict:
        sc = sample_training_scenario(self._rng, self.n_tasks, self.sizes)
        if self.tasks_from == 'footwear':
            if self._starts is None:
                from warehouse_marl.dataset_footwear import load_dataset
                self._starts = load_dataset(self.data_dir).window_starts('train_fit',
                                                                         self.n_tasks)
            sc['skew'] = 0.0                       # la demande vient des donnees
            sc['footwear'] = {'split': 'train_fit', 'start': self._rng.choice(self._starts),
                              'data_dir': self.data_dir}
        return sc

    def reset(self, scenario: Optional[Dict] = None):
        self.scenario = dict(scenario) if scenario else self.sample_scenario()
        self.bench = make_benchmark('drl3_direct', self.scenario)
        self._alloc_phase = False
        self._pending = []
        self.pairs, _, done = self._advance()
        return self.observation(), {'scenario': self.scenario, 'done': done}

    def observation(self) -> np.ndarray:
        if not self.pairs:
            return np.zeros((0, N_FEATURES_V3), dtype=np.float32)
        return np.array([f for _, _, f in self.pairs], dtype=np.float32)

    def _advance(self):
        b, wait = self.bench, 0.0
        while True:
            if self._alloc_phase:
                pairs = b.candidate_pairs_v3()
                if pairs:
                    return pairs, wait, False
                wait += len(b.open) * b.dt
                finished = b.end_tick()
                self._alloc_phase = False
                if finished or b.t >= b.horizon:
                    return [], wait, True
            b.begin_tick()
            self._alloc_phase = True

    def _service_seconds(self, task) -> Optional[float]:
        """Temps de service mesure (attribution -> fin) + penalites, ou None
        si la tache n'est pas encore terminee."""
        if task.done is None:
            return None
        s = task.done - task.assigned
        if task.failed:
            s += self.failure_penalty_s
        elif self.late_penalty_s and task.due is not None and task.done > task.due:
            s += self.late_penalty_s
        return s

    def _finalize(self, episode_over: bool) -> List[tuple]:
        out, keep = [], []
        for rec in self._pending:
            if rec['next'] is None:
                keep.append(rec)
                continue
            service = self._service_seconds(rec['task'])
            if service is None and episode_over:     # coupe a l'horizon : non finie
                service = self.bench.t - rec['task'].assigned + self.failure_penalty_s
            if service is None:
                keep.append(rec)
                continue
            raw = -(rec['wait'] + service) / REWARD_NORM_S
            reward = raw - (self.reward_center or 0.0)
            out.append((rec['feat'], reward, rec['next'], rec['terminal'], raw))
        self._pending = keep
        return out

    def step(self, action: int):
        robot, task, feat = self.pairs[action]
        self.bench.assign_pair(robot, task)
        rec = {'feat': np.asarray(feat, dtype=np.float32), 'task': task, 'wait': 0.0,
               'next': None, 'terminal': False}
        self._pending.append(rec)
        self.pairs, wait, done = self._advance()
        rec['wait'] = wait
        rec['next'] = self.observation()
        rec['terminal'] = done
        info = {'transitions': self._finalize(done)}
        if done:
            info['metrics'] = self.bench.metrics()
        return self.observation(), done, info


def greedy_reward_center(seed: int, episodes: int, n_tasks: int, sizes=TRAIN_SIZES,
                         tasks_from: str = '', data_dir: Optional[str] = None) -> float:
    """Recompense brute moyenne de la politique greedy_pair (Q residuel a
    correction nulle) sur la distribution d'entrainement : reference figee."""
    env = AllocationEnvV3(seed=seed, n_tasks=n_tasks, reward_center=None, sizes=sizes,
                          tasks_from=tasks_from, data_dir=data_dir)
    raws: List[float] = []
    for _ in range(episodes):
        obs, info = env.reset()
        done = info['done']
        while not done:
            a = int(np.argmax(-obs[:, 0]))
            obs, done, inf = env.step(a)
            raws.extend(t[4] for t in inf['transitions'])
    return float(np.mean(raws)) if raws else 0.0


def greedy_action(obs: Sequence) -> int:
    return int(np.argmax(-np.asarray(obs)[:, 0]))
