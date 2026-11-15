"""
residual_dqn.py
---------------
DQN du DRL v3 : APPRENTISSAGE RESIDUEL sur la regle greedy_pair.

    Q(couple) = -beta * cout_diametre + correction(caracteristiques v3)

``cout_diametre`` est la caracteristique 0 de features_v3 (cout du chemin /
diametre du graphe). La derniere couche de ``correction`` est initialisee a
ZERO : un modele non entraine choisit exactement le couple de greedy_pair
(meme ordre, meme depart des egalites). L'entrainement n'apprend que
l'ecart a cette regle ; en conservant le meilleur modele en validation,
episode 0 compris, on ne retient jamais un modele moins bon que greedy_pair
SUR LES SCENARIOS DE VALIDATION (ce n'est pas une garantie sur d'autres
scenarios).

Reprend PairDQN (memoire de rejeu, reseau cible, Huber, Double DQN) et
ajoute la mise a jour douce du reseau cible (tau).
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError as exc:  # pragma: no cover
    raise ImportError('PyTorch est requis : pip install torch') from exc

from warehouse_marl.drl.features_v3 import FEATURE_NAMES_V3, FEATURE_VERSION_V3, N_FEATURES_V3
from warehouse_marl.drl.pair_dqn import PairDQN

MODEL_FORMAT_V3 = 'warehouse_marl_residual_dqn'


class ResidualQNet(nn.Module):
    def __init__(self, n_features: int = N_FEATURES_V3, hidden: int = 64, beta: float = 1.0):
        super().__init__()
        self.beta = beta
        self.correction = nn.Sequential(
            nn.Linear(n_features, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 1))
        nn.init.zeros_(self.correction[-1].weight)
        nn.init.zeros_(self.correction[-1].bias)

    def forward(self, x):
        return -self.beta * x[..., 0] + self.correction(x).squeeze(-1)


class ResidualDQN(PairDQN):
    def __init__(self, n_features: int = N_FEATURES_V3, hidden: int = 64, lr: float = 3e-4,
                 gamma: float = 0.95, double: bool = True, buffer_size: int = 100_000,
                 batch_size: int = 64, target_every: int = 500, warmup: int = 1000,
                 grad_clip: float = 5.0, seed: int = 0, beta: float = 1.0, tau: float = 0.005):
        super().__init__(n_features=n_features, hidden=hidden, lr=lr, gamma=gamma, double=double,
                         buffer_size=buffer_size, batch_size=batch_size,
                         target_every=target_every, warmup=warmup, grad_clip=grad_clip,
                         seed=seed)
        torch.manual_seed(seed)
        self.beta, self.tau = beta, tau
        self.q = ResidualQNet(n_features, hidden, beta)
        self.target = ResidualQNet(n_features, hidden, beta)
        self.target.load_state_dict(self.q.state_dict())
        self.target.eval()
        self.opt = torch.optim.Adam(self.q.parameters(), lr=lr)

    def correction(self, feats) -> np.ndarray:
        feats = np.asarray(feats, dtype=np.float32)
        with torch.no_grad():
            return self.q.correction(torch.from_numpy(feats)).squeeze(-1).numpy()

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
        if self.tau > 0:
            with torch.no_grad():
                for p_t, p in zip(self.target.parameters(), self.q.parameters()):
                    p_t.mul_(1.0 - self.tau).add_(self.tau * p)
        elif self.updates % self.target_every == 0:
            self.target.load_state_dict(self.q.state_dict())
        with torch.no_grad():
            corr = self.q.correction(s).squeeze(-1)
        return {'loss': float(loss.item()), 'q': float(q_pred.mean().item()), 'grad': grad,
                'correction': float(corr.abs().mean().item())}

    def state(self, **meta) -> Dict:
        ckpt = super().state(**meta)
        ckpt['meta'].update({'format': MODEL_FORMAT_V3, 'feature_version': FEATURE_VERSION_V3,
                             'feature_names': list(FEATURE_NAMES_V3), 'beta': self.beta,
                             'tau': self.tau})
        ckpt['meta'].update(meta)
        return ckpt


def load_residual_model(path: str) -> ResidualDQN:
    ckpt = torch.load(path, map_location='cpu', weights_only=False)
    meta = ckpt.get('meta', {}) if isinstance(ckpt, dict) else {}
    if meta.get('format') != MODEL_FORMAT_V3:
        raise ValueError(f'{path} n est pas un modele DRL v3 (train_drl_v3)')
    if meta['n_features'] != N_FEATURES_V3:
        raise ValueError(f'{path} : {meta["n_features"]} caracteristiques, '
                         f'{N_FEATURES_V3} attendues')
    agent = ResidualDQN(n_features=meta['n_features'], hidden=meta['hidden'],
                        gamma=meta.get('gamma', 0.95), double=meta.get('double', True),
                        beta=meta.get('beta', 1.0), tau=meta.get('tau', 0.005))
    agent.q.load_state_dict(ckpt['state_dict'])
    agent.target.load_state_dict(ckpt['state_dict'])
    agent.q.eval()
    agent.meta = meta
    return agent
