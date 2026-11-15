"""
pair_dqn.py
-----------
DQN du DRL v2 : un reseau PARTAGE Q(couple robot/tache) a une seule sortie.
A chaque decision, le reseau note chaque couple candidat (features_v2) ; la
politique choisit le couple de Q maximale. La taille de l'entree ne depend
pas du nombre de robots.

Apprentissage : memoire de rejeu, reseau cible (copie periodique), perte de
Huber, gradient borne, option Double DQN. La cible d'une transition est
    y = r + gamma * max_{couples suivants} Q_cible(couple')
(Double DQN : argmax par le reseau en ligne, valeur par le reseau cible).
"""

from __future__ import annotations

import random
from collections import deque
from typing import Dict, Optional

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError as exc:  # pragma: no cover
    raise ImportError('PyTorch est requis : pip install torch') from exc

from warehouse_marl.drl.features_v2 import FEATURE_NAMES, FEATURE_VERSION, N_FEATURES

MODEL_FORMAT = 'warehouse_marl_pair_dqn'


class PairQNet(nn.Module):
    def __init__(self, n_features: int = N_FEATURES, hidden: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 1))

    def forward(self, x):
        return self.net(x).squeeze(-1)


class PairDQN:
    def __init__(self, n_features: int = N_FEATURES, hidden: int = 64, lr: float = 5e-4,
                 gamma: float = 0.95, double: bool = True, buffer_size: int = 50_000,
                 batch_size: int = 64, target_every: int = 250, warmup: int = 500,
                 grad_clip: float = 10.0, seed: int = 0):
        torch.manual_seed(seed)
        self.rng = random.Random(seed)
        self.n_features, self.hidden = n_features, hidden
        self.gamma, self.double = gamma, double
        self.batch_size, self.target_every, self.warmup = batch_size, target_every, warmup
        self.grad_clip = grad_clip
        self.q = PairQNet(n_features, hidden)
        self.target = PairQNet(n_features, hidden)
        self.target.load_state_dict(self.q.state_dict())
        self.target.eval()
        self.opt = torch.optim.Adam(self.q.parameters(), lr=lr)
        self.buffer = deque(maxlen=buffer_size)
        self.updates = 0
        self.meta: Dict = {}

    # ------------------------------------------------------------------ #
    def scores(self, feats) -> np.ndarray:
        """Q de chaque couple (matrice n_couples x n_features)."""
        feats = np.asarray(feats, dtype=np.float32)
        if feats.shape[0] == 0:
            return np.zeros(0, dtype=np.float32)
        with torch.no_grad():
            return self.q(torch.from_numpy(feats)).numpy()

    def act(self, feats, epsilon: float = 0.0) -> int:
        if epsilon > 0 and self.rng.random() < epsilon:
            return self.rng.randrange(len(feats))
        return int(np.argmax(self.scores(feats)))

    def remember(self, feat, reward, next_feats, done):
        self.buffer.append((np.asarray(feat, dtype=np.float32), float(reward),
                            np.asarray(next_feats, dtype=np.float32).reshape(-1, self.n_features),
                            bool(done)))

    def train_step(self) -> Optional[Dict[str, float]]:
        if len(self.buffer) < max(self.warmup, self.batch_size):
            return None
        batch = [self.buffer[self.rng.randrange(len(self.buffer))]
                 for _ in range(self.batch_size)]
        s = torch.from_numpy(np.stack([b[0] for b in batch]))
        r = torch.tensor([b[1] for b in batch], dtype=torch.float32)
        d = torch.tensor([b[3] or len(b[2]) == 0 for b in batch], dtype=torch.float32)
        m = max(1, max(len(b[2]) for b in batch))
        nxt = np.zeros((self.batch_size, m, self.n_features), dtype=np.float32)
        mask = np.zeros((self.batch_size, m), dtype=bool)
        for i, b in enumerate(batch):
            nxt[i, :len(b[2])] = b[2]
            mask[i, :len(b[2])] = True
        nxt_t, mask_t = torch.from_numpy(nxt), torch.from_numpy(mask)

        q_pred = self.q(s)
        with torch.no_grad():
            q_tgt_all = self.target(nxt_t).masked_fill(~mask_t, -1e9)
            if self.double:
                idx = self.q(nxt_t).masked_fill(~mask_t, -1e9).argmax(dim=1, keepdim=True)
                q_next = q_tgt_all.gather(1, idx).squeeze(1)
            else:
                q_next = q_tgt_all.max(dim=1).values
            q_next = torch.where(d > 0, torch.zeros_like(q_next), q_next)
            y = r + self.gamma * q_next
        loss = F.smooth_l1_loss(q_pred, y)
        self.opt.zero_grad()
        loss.backward()
        grad = float(torch.nn.utils.clip_grad_norm_(self.q.parameters(), self.grad_clip))
        self.opt.step()
        self.updates += 1
        if self.updates % self.target_every == 0:
            self.target.load_state_dict(self.q.state_dict())
        return {'loss': float(loss.item()), 'q': float(q_pred.mean().item()), 'grad': grad}

    # ------------------------------------------------------------------ #
    def state(self, **meta) -> Dict:
        info = {'format': MODEL_FORMAT, 'feature_version': FEATURE_VERSION,
                'n_features': self.n_features, 'feature_names': list(FEATURE_NAMES),
                'hidden': self.hidden, 'gamma': self.gamma, 'double': self.double}
        info.update(self.meta)
        info.update(meta)
        return {'meta': info,
                'state_dict': {k: v.detach().clone() for k, v in self.q.state_dict().items()}}

    def save(self, path: str, **meta):
        torch.save(self.state(**meta), path)


def load_pair_model(path: str) -> PairDQN:
    """Charge un modele v2 (format produit par train_drl_v2)."""
    ckpt = torch.load(path, map_location='cpu', weights_only=False)
    if not isinstance(ckpt, dict) or ckpt.get('meta', {}).get('format') != MODEL_FORMAT:
        raise ValueError(f'{path} n est pas un modele DRL v2 (train_drl_v2)')
    meta = ckpt['meta']
    if meta['n_features'] != N_FEATURES:
        raise ValueError(f'{path} : {meta["n_features"]} caracteristiques, {N_FEATURES} attendues')
    agent = PairDQN(n_features=meta['n_features'], hidden=meta['hidden'],
                    gamma=meta.get('gamma', 0.95), double=meta.get('double', True))
    agent.q.load_state_dict(ckpt['state_dict'])
    agent.target.load_state_dict(ckpt['state_dict'])
    agent.q.eval()
    agent.meta = meta
    return agent
