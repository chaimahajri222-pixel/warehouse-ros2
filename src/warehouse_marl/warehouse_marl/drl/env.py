"""
env.py
-------
Environnement Gymnasium pour entrainer une politique DRL d'ALLOCATION DE
TACHES ET AIDE A LA DECISION, conformement au sujet :

    "Implementation of a DRL framework for task allocation and path
    planning ... Reduction in inventory processing time and error rates
    compared to heuristic methods."

Simplification pedagogique (raisonnable pour un premier prototype de
Master) : on n'entraine PAS directement une politique de bas niveau
(vitesses/roues), qui reste geree par Nav2/MPPI dans la simulation Gazebo.
On entraine une politique de HAUT NIVEAU qui, a chaque tache a assigner,
choisit QUEL agent doit la prendre en charge, en observant :
    - la position (noeud le plus proche) de chaque agent sur le graphe,
    - la charge courante de chaque agent (nb de taches actives),
    - le cout du plus court chemin dynamique agent -> cible pour chacun,
    - la priorite de la tache.

L'observation etant continue et de taille fixe, l'action est discrete
(indice de l'agent choisi), ce qui permet d'utiliser un DQN simple tout en
restant fidele a l'esprit "distribue" : en deploiement, le SCORE produit
par le reseau (une valeur par agent) est diffuse comme "biais" aux noeuds
consensus_node.py, qui restent responsables de la decision finale
(hybridation apprentissage + consensus, cf. drl_allocator_node.py).
"""

from __future__ import annotations

import random
from typing import List, Optional

import numpy as np

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "gymnasium est requis : pip install gymnasium --break-system-packages"
    ) from exc

from warehouse_marl.warehouse_graph import build_demo_warehouse, WarehouseGraph


class WarehouseTaskAllocationEnv(gym.Env):
    """Un episode = une sequence de N taches a router vers n_agents agents.

    Observation (par agent, concatenee) :
        [dx_agent_target, dy_agent_target, path_cost_norm, agent_load_norm]
    + [task_priority_norm] partage.

    Action : indice de l'agent choisi pour la tache courante (Discrete).

    Recompense : -cout_du_chemin_normalise - penalite_de_surcharge
                 + bonus si la tache est traitee rapidement / a temps.
    Cette forme de recompense pousse directement a MINIMISER le temps de
    traitement d'inventaire, comme demande dans les resultats attendus.
    """

    metadata = {"render_modes": []}

    def __init__(self, n_agents: int = 3, n_tasks_per_episode: int = 40,
                 max_active_tasks_per_agent: int = 3, seed: Optional[int] = None):
        super().__init__()
        self.n_agents = n_agents
        self.n_tasks_per_episode = n_tasks_per_episode
        self.max_active = max_active_tasks_per_agent

        self.graph: WarehouseGraph = build_demo_warehouse()
        self.node_ids: List[str] = list(self.graph.G.nodes)
        self.shelf_nodes = [
            n for n, d in self.graph.G.nodes(data=True) if d['node_type'] == 'shelf'
        ]
        # Points de depart possibles pour les agents (stations)
        self.station_nodes = [
            n for n, d in self.graph.G.nodes(data=True) if d['node_type'] == 'station'
        ]

        obs_dim = self.n_agents * 3 + 1  # (cost_norm, load_norm, dist_norm) par agent + priorite
        self.observation_space = spaces.Box(
            low=-1.0, high=10.0, shape=(obs_dim,), dtype=np.float32
        )
        self.action_space = spaces.Discrete(self.n_agents)

        self._rng = random.Random(seed)
        self.reset(seed=seed)

    # ------------------------------------------------------------------ #
    def reset(self, *, seed: Optional[int] = None, options=None):
        if seed is not None:
            self._rng.seed(seed)

        self.agent_positions = [
            self._rng.choice(self.station_nodes) for _ in range(self.n_agents)
        ]
        self.agent_load = [0] * self.n_agents
        self._task_count = 0
        self._current_task = self._sample_task()

        obs = self._build_observation()
        info = {}
        return obs, info

    def _sample_task(self):
        target = self._rng.choice(self.shelf_nodes)
        priority = round(self._rng.uniform(0.5, 2.0), 2)
        return {"target": target, "priority": priority}

    def _path_cost(self, agent_idx: int, target: str) -> float:
        src = self.agent_positions[agent_idx]
        _, cost = self.graph.shortest_path(src, target)
        return cost if cost != float('inf') else 50.0  # penalite si pas de chemin

    def _build_observation(self) -> np.ndarray:
        feats = []
        for i in range(self.n_agents):
            cost = self._path_cost(i, self._current_task["target"]) / 20.0
            load = self.agent_load[i] / max(self.max_active, 1)
            # "distance directe" normalisee grossierement (proxy simple)
            feats.extend([cost, load, float(i) / self.n_agents])
        feats.append(self._current_task["priority"] / 2.0)
        return np.array(feats, dtype=np.float32)

    def step(self, action: int):
        assert self.action_space.contains(action)

        cost = self._path_cost(action, self._current_task["target"])
        overload_penalty = 3.0 if self.agent_load[action] >= self.max_active else 0.0

        reward = -0.1 * cost - overload_penalty
        # bonus si l'agent choisi est bien celui de cout minimal (encourage
        # a converger vers un comportement proche-optimal, exploitable
        # ensuite comme "biais" pour le consensus)
        costs_all = [self._path_cost(i, self._current_task["target"])
                     for i in range(self.n_agents)]
        if cost <= min(costs_all) + 1e-6:
            reward += 1.0

        # Effectue "virtuellement" la tache : deplace l'agent, incremente sa charge
        self.agent_positions[action] = self._current_task["target"]
        self.agent_load[action] += 1
        # Decharge aleatoire des autres agents (simule des taches terminees ailleurs)
        for i in range(self.n_agents):
            if i != action and self.agent_load[i] > 0 and self._rng.random() < 0.3:
                self.agent_load[i] -= 1

        self._task_count += 1
        terminated = self._task_count >= self.n_tasks_per_episode
        truncated = False

        self._current_task = self._sample_task() if not terminated else self._current_task
        obs = self._build_observation()
        info = {"path_cost": cost}
        return obs, reward, terminated, truncated, info
