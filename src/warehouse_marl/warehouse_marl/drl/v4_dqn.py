"""
v4_dqn.py
---------
DQN residuel v4 (PROTOCOLE_V4.md, drl_route et drl_idle) :

    Q(action) = x[0] + f_theta(x)

x[0] est le terme a priori calcule par le simulateur (route : -(cout + distance
de Dijkstra du voisin au but)/D ; attente : -E_p[d(candidat, rack)]/D), avec
D = 60 s x vitesse du robot. La derniere couche de f_theta est initialisee a
zero : un modele non entraine reproduit l'heuristique de depart
(dijkstra_dynamique / centre_de_demande).

Reprend ResidualDQN (Double DQN, Huber, cible douce tau, memoire de rejeu)
avec beta = -1 (Q = +x[0] + correction) et un nombre de caracteristiques libre.
"""

from __future__ import annotations

import torch

from warehouse_marl.drl.residual_dqn import ResidualDQN

MODEL_FORMAT_V4 = 'warehouse_marl_v4_residual'


class V4DQN(ResidualDQN):
    def __init__(self, kind: str, n_features: int, hidden: int = 64, lr: float = 3e-4,
                 gamma: float = 0.99, seed: int = 0, tau: float = 0.005,
                 buffer_size: int = 100_000, batch_size: int = 64, warmup: int = 1000,
                 grad_clip: float = 5.0):
        super().__init__(n_features=n_features, hidden=hidden, lr=lr, gamma=gamma, double=True,
                         buffer_size=buffer_size, batch_size=batch_size, warmup=warmup,
                         grad_clip=grad_clip, seed=seed, beta=-1.0, tau=tau)
        self.kind = kind

    def state(self, **meta):
        ckpt = {'meta': {'format': MODEL_FORMAT_V4, 'kind': self.kind,
                         'n_features': self.n_features, 'hidden': self.hidden,
                         'gamma': self.gamma, 'tau': self.tau, 'beta': -1.0},
                'state_dict': {k: v.detach().clone() for k, v in self.q.state_dict().items()}}
        ckpt['meta'].update(self.meta)
        ckpt['meta'].update(meta)
        return ckpt


def load_v4_model(path: str, kind: str = None) -> V4DQN:
    ckpt = torch.load(path, map_location='cpu', weights_only=False)
    meta = ckpt.get('meta', {})
    if meta.get('format') != MODEL_FORMAT_V4:
        raise ValueError(f'{path} n est pas un modele v4')
    if kind is not None and meta.get('kind') != kind:
        raise ValueError(f'{path} : modele {meta.get("kind")}, {kind} attendu')
    agent = V4DQN(meta['kind'], meta['n_features'], hidden=meta['hidden'],
                  gamma=meta.get('gamma', 0.99), tau=meta.get('tau', 0.005))
    agent.q.load_state_dict(ckpt['state_dict'])
    agent.target.load_state_dict(ckpt['state_dict'])
    agent.q.eval()
    agent.meta = meta
    return agent
