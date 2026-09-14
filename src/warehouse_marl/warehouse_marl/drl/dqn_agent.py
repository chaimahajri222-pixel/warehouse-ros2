"""
dqn_agent.py
------------
Implementation volontairement legere d'un Deep Q-Network (DQN), suffisante
pour un premier prototype de Master (pas de dependance a stable-baselines3,
tout est transparent et modifiable pour ton rapport). Comprend :
    - un reseau de neurones simple (MLP) qui approx. Q(s, a) pour chaque
      agent candidat,
    - un replay buffer,
    - une boucle d'entrainement standard DQN avec reseau cible (target net).

Utilise par drl/train_drl.py (entrainement hors-ligne) puis charge en
inference dans drl_allocator_node.py (deploiement temps-reel).
"""

from __future__ import annotations

import random
from collections import deque, namedtuple
from typing import Deque, Tuple

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyTorch est requis : pip install torch --break-system-packages"
    ) from exc


Transition = namedtuple('Transition', ('state', 'action', 'reward', 'next_state', 'done'))


class QNetwork(nn.Module):
    def __init__(self, obs_dim: int, n_actions: int, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_actions),
        )

    def forward(self, x):
        return self.net(x)


class ReplayBuffer:
    def __init__(self, capacity: int = 50_000):
        self.buffer: Deque[Transition] = deque(maxlen=capacity)

    def push(self, *args):
        self.buffer.append(Transition(*args))

    def sample(self, batch_size: int) -> Tuple[np.ndarray, ...]:
        batch = random.sample(self.buffer, batch_size)
        return Transition(*zip(*batch))

    def __len__(self):
        return len(self.buffer)


class DQNAgent:
    def __init__(self, obs_dim: int, n_actions: int, lr: float = 1e-3,
                 gamma: float = 0.95, device: str = None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.n_actions = n_actions
        self.gamma = gamma

        self.q_net = QNetwork(obs_dim, n_actions).to(self.device)
        self.target_net = QNetwork(obs_dim, n_actions).to(self.device)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.target_net.eval()

        self.optimizer = torch.optim.Adam(self.q_net.parameters(), lr=lr)
        self.buffer = ReplayBuffer()

        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995

    # ------------------------------------------------------------------ #
    def select_action(self, obs: np.ndarray, greedy: bool = False) -> int:
        if not greedy and random.random() < self.epsilon:
            return random.randrange(self.n_actions)
        with torch.no_grad():
            state = torch.as_tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
            q_values = self.q_net(state)
            return int(torch.argmax(q_values, dim=1).item())

    def q_values(self, obs: np.ndarray) -> np.ndarray:
        """Renvoie le vecteur complet des Q-values (une par agent). Utilise
        en deploiement pour construire le 'biais DRL' envoye au consensus
        distribue (voir drl_allocator_node.py)."""
        with torch.no_grad():
            state = torch.as_tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
            return self.q_net(state).squeeze(0).cpu().numpy()

    def remember(self, state, action, reward, next_state, done):
        self.buffer.push(state, action, reward, next_state, done)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def update_target(self):
        self.target_net.load_state_dict(self.q_net.state_dict())

    def train_step(self, batch_size: int = 64) -> float:
        if len(self.buffer) < batch_size:
            return 0.0

        batch = self.buffer.sample(batch_size)
        states = torch.as_tensor(np.array(batch.state), dtype=torch.float32, device=self.device)
        actions = torch.as_tensor(batch.action, dtype=torch.int64, device=self.device).unsqueeze(1)
        rewards = torch.as_tensor(batch.reward, dtype=torch.float32, device=self.device).unsqueeze(1)
        next_states = torch.as_tensor(np.array(batch.next_state), dtype=torch.float32, device=self.device)
        dones = torch.as_tensor(batch.done, dtype=torch.float32, device=self.device).unsqueeze(1)

        q_pred = self.q_net(states).gather(1, actions)
        with torch.no_grad():
            q_next = self.target_net(next_states).max(dim=1, keepdim=True)[0]
            q_target = rewards + self.gamma * q_next * (1.0 - dones)

        loss = F.smooth_l1_loss(q_pred, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_net.parameters(), 10.0)
        self.optimizer.step()
        return float(loss.item())

    # ------------------------------------------------------------------ #
    def save(self, path: str):
        torch.save(self.q_net.state_dict(), path)

    def load(self, path: str):
        state_dict = torch.load(path, map_location=self.device)
        self.q_net.load_state_dict(state_dict)
        self.target_net.load_state_dict(state_dict)
