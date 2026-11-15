"""
env_v2.py
---------
Environnement d'entrainement du DRL v2, construit SUR la simulation de
``allocation_benchmark.Benchmark`` : l'entrainement et l'evaluation voient le
meme monde (graphe dynamique, congestion, blocages d'aretes, arrivees de
Poisson, file d'attente, temps de prelevement).

Ce qui change par rapport a drl/env.py (v1)
  - Decision : des qu'il y a au moins un robot libre et une tache en
    attente, l'agent choisit UN couple (robot libre, tache candidate) parmi
    les K=5 taches les plus anciennes dont la cible a de la place. Plusieurs
    decisions peuvent avoir lieu au meme instant (plusieurs robots libres).
  - Observation : une matrice (nombre de couples x N_FEATURES), voir
    features_v2.py. Aucune caracteristique ne contient l'index du robot ; le
    reseau Q(couple) a une sortie et sert pour n'importe quelle flotte.
  - Recompense : liee au temps de traitement, sans imitation de
    l'heuristique :
        r = -(temps d'attente cumule de toutes les taches en file entre
              cette decision et la suivante
              + duree estimee de la tache choisie : chemin / vitesse + prelevement)
            / REWARD_NORM_S
    La somme sur un episode vaut (au facteur pres) moins la somme des temps
    de traitement des taches : attente avant attribution + service. Aucun
    terme ne regarde si le robot choisi est le moins couteux. La
    recompense est centree par une moyenne glissante (Q bornees).
  - Episodes : charge rho dans {0.5, 0.7, 0.9}, 3 a 6 robots, entrepot 5x3
    ou 8x5, blocages aleatoires d'aretes (0, 1 ou 3 par minute).

Pas de dependance a gymnasium (le nombre d'actions varie a chaque decision)
ni a PyTorch : l'API reprend reset()/step() de Gymnasium.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

import numpy as np

from warehouse_marl.allocation_benchmark import (
    Benchmark, build_grid_warehouse, mean_service_time)
from warehouse_marl.drl.features_v2 import N_FEATURES, finite_cost

REWARD_NORM_S = 60.0
RHOS = (0.5, 0.7, 0.9)
ROBOTS = (3, 4, 5, 6)
DIMS = ((5, 3), (8, 5))
BLOCK_RATES = (0.0, 1.0 / 60.0, 3.0 / 60.0)

_SERVICE_CACHE: Dict[tuple, float] = {}


def service_time(dims, speed, pick_time) -> float:
    key = (tuple(dims), speed, pick_time)
    if key not in _SERVICE_CACHE:
        _SERVICE_CACHE[key] = mean_service_time(build_grid_warehouse(*dims), speed, pick_time)
    return _SERVICE_CACHE[key]


def make_benchmark(method: str, scenario: Dict, speed=0.5, pick_time=10.0, agent2=None,
                   bias_weight=1.0, agent3=None) -> Benchmark:
    """Construit un Benchmark a partir d'un scenario
    {dims, robots, rho, block_rate, tasks, seed, [loss, skew, speeds,
    deadline_base, block_min, block_max, footwear]} (cles optionnelles :
    valeurs par defaut du banc). ``footwear`` = {split, start, [data_dir]} :
    taches prises dans le jeu de donnees reel (dataset_footwear)."""
    dims = tuple(scenario['dims'])
    speeds = scenario.get('speeds')
    mean_speed = sum(speeds) / len(speeds) if speeds else speed
    loss = scenario.get('loss', 0.0)
    graph = build_grid_warehouse(*dims)
    targets = None
    service = service_time(dims, mean_speed, pick_time)
    if scenario.get('footwear'):          # taches du jeu de donnees reel
        from warehouse_marl.dataset_footwear import load_dataset
        fw = scenario['footwear']
        ds = load_dataset(fw.get('data_dir'))
        targets = ds.targets(graph, fw['split'], fw['start'], scenario['tasks'])
        service = ds.service_time(graph, mean_speed, pick_time)   # meme charge rho
    rate = scenario['rho'] * scenario['robots'] / service
    return Benchmark(method, graph, scenario['robots'], rate,
                     scenario['tasks'], seed=scenario['seed'], speed=speed,
                     pick_time=pick_time, block_rate=scenario.get('block_rate', 0.0),
                     block_min=scenario.get('block_min', 30.0),
                     block_max=scenario.get('block_max', 120.0),
                     msg_loss=loss, msg_delay=0.05 + 2 * loss, agent2=agent2,
                     bias_weight=bias_weight, demand_skew=scenario.get('skew', 0.0),
                     speeds=speeds, deadline_base=scenario.get('deadline_base', 60.0),
                     agent3=agent3, targets=targets)


class AllocationEnvV2:
    """Un episode = un essai complet du banc d'essai, pilote couple par couple."""

    def __init__(self, seed: int = 0, n_tasks: int = 80, robots=ROBOTS, rhos=RHOS,
                 dims=DIMS, block_rates=BLOCK_RATES, speed: float = 0.5,
                 pick_time: float = 10.0, center: bool = True, center_alpha: float = 0.01):
        self._rng = random.Random(seed)
        self.n_tasks, self.robots, self.rhos = n_tasks, tuple(robots), tuple(rhos)
        self.dims, self.block_rates = tuple(dims), tuple(block_rates)
        self.speed, self.pick_time = speed, pick_time
        self.center, self.center_alpha = center, center_alpha
        self.reward_mean: Optional[float] = None
        self.bench: Optional[Benchmark] = None
        self.pairs: List[Tuple] = []
        self.scenario: Dict = {}
        self._alloc_phase = False

    # ------------------------------------------------------------------ #
    def sample_scenario(self) -> Dict:
        return {'dims': self._rng.choice(self.dims), 'robots': self._rng.choice(self.robots),
                'rho': self._rng.choice(self.rhos),
                'block_rate': self._rng.choice(self.block_rates),
                'tasks': self.n_tasks, 'seed': self._rng.randrange(10 ** 9)}

    def reset(self, seed: Optional[int] = None, scenario: Optional[Dict] = None):
        if seed is not None:
            self._rng.seed(seed)
        self.scenario = dict(scenario) if scenario else self.sample_scenario()
        self.bench = make_benchmark('drl2_direct', self.scenario, self.speed, self.pick_time)
        self._alloc_phase = False
        self.pairs, _, done = self._advance()
        return self.observation(), {'scenario': self.scenario, 'done': done}

    def observation(self) -> np.ndarray:
        if not self.pairs:
            return np.zeros((0, N_FEATURES), dtype=np.float32)
        return np.array([f for _, _, f in self.pairs], dtype=np.float32)

    def _advance(self):
        """Fait avancer la simulation jusqu'a la prochaine decision.
        Retourne (couples, attente cumulee des taches en file, fini)."""
        b, wait = self.bench, 0.0
        while True:
            if self._alloc_phase:
                pairs = b.candidate_pairs()
                if pairs:
                    return pairs, wait, False
                wait += len(b.open) * b.dt
                finished = b.end_tick()
                self._alloc_phase = False
                if finished or b.t >= b.horizon:
                    return [], wait, True
            b.begin_tick()
            self._alloc_phase = True

    def service_estimate(self, robot, task) -> float:
        """Duree estimee de la tache si ``robot`` la prend (s)."""
        cost = self.bench.path_cost(robot.node, task.target)
        return finite_cost(cost) / self.bench.speed + self.bench.pick_time

    def step(self, action: int):
        robot, task, _ = self.pairs[action]
        b = self.bench
        service = self.service_estimate(robot, task)
        costs = [b.path_cost(r.node, task.target) for r, k, _ in self.pairs if k is task]
        is_min = b.path_cost(robot.node, task.target) <= min(costs) + 1e-9   # diagnostic seul
        b.assign_pair(robot, task)
        self.pairs, wait, done = self._advance()
        raw = -(service + wait) / REWARD_NORM_S
        reward = raw
        if self.center:
            if self.reward_mean is None:
                self.reward_mean = raw
            reward = raw - self.reward_mean
            self.reward_mean += self.center_alpha * (raw - self.reward_mean)
        info = {'service_s': service, 'queue_wait_s': wait, 'raw_reward': raw,
                'chosen_is_min_cost': is_min}
        if done:
            info['metrics'] = b.metrics()
        return self.observation(), float(reward), done, info
