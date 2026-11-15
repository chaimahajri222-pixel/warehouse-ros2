"""
train_v4.py
-----------
Entrainement des DQN residuels v4 (PROTOCOLE_V4.md, section 3 et 5) :
une graine par processus, budget en temps reel, validation periodique (et a
l'instant 0), sauvegarde du meilleur point de controle en VALIDATION.

    python -m warehouse_marl.drl.train_v4 --kind route --seed 0 --budget-min 120 \
        --out-dir ~/warehouse_ws/drl_v4/route
    python -m warehouse_marl.drl.train_v4 --kind idle --seed 1 ...

Sorties (--out-dir) : train_log_seed<k>.csv (par episode), val_log_seed<k>.csv
(par validation), ckpt_seed<k>_t<min>.pt, best_seed<k>.pt.
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import statistics
import time

import numpy as np
import torch

from warehouse_marl.allocation_benchmark import build_grid_warehouse, mean_service_time
from warehouse_marl.drl.v4_dqn import V4DQN
from warehouse_marl.drl.v4_sim import BenchmarkV4, N_IDLE_FEATURES, N_ROUTE_FEATURES

TEST_SEEDS = frozenset(1000 * k + 7 for k in range(20))
VAL_SEEDS = tuple(500_000 + 1009 * i for i in range(100))
assert not TEST_SEEDS & set(VAL_SEEDS)

SIZES = {3: (5, 3), 6: (8, 5), 10: (10, 8), 20: (15, 10)}
# configurations des 4 conditions dataset du banc (robots, dims, rho, vitesses)
DATASET_CONFIGS = [
    dict(label='15 racks, 3 r., rho=0.7', robots=3, dims=(5, 3), rho=0.7, speeds=None),
    dict(label='15 racks, 3 r., rho=0.9', robots=3, dims=(5, 3), rho=0.9, speeds=None),
    dict(label='40 racks, 6 r., vit. var.', robots=6, dims=(8, 5), rho=0.9,
         speeds=(0.3, 0.5, 0.7)),
    dict(label='150 racks, 20 r., rho=0.7', robots=20, dims=(15, 10), rho=0.7, speeds=None),
]
SPEED, PICK = 0.5, 10.0


def train_seed_stream(seed):
    """Graines de simulation d'entrainement, disjointes de validation et test."""
    rng = random.Random(10_007 * seed + 1)
    forbidden = TEST_SEEDS | set(VAL_SEEDS)
    while True:
        s = rng.randrange(10_000_000, 10 ** 9)
        assert s not in forbidden
        yield s, rng


_DS = None


def dataset():
    global _DS
    if _DS is None:
        from warehouse_marl.dataset_footwear import load_dataset
        _DS = load_dataset()
    return _DS


def train_fit_demand(graph):
    ds = dataset()
    proj = ds.projection(graph)
    f = {}
    for p in ds.lines['train_fit']:
        f[proj[p.location]] = f.get(proj[p.location], 0) + 1
    return f


def make_sim(sc, kind, agent, epsilon=0.0, cb=None, explore_seed=None):
    """Construit un BenchmarkV4 a partir d'un dictionnaire de scenario."""
    dims, R = sc['dims'], sc['robots']
    g = build_grid_warehouse(*dims)
    speeds = sc.get('speeds')
    mean_speed = statistics.mean(speeds) if speeds else SPEED
    targets, demand = None, None
    if sc.get('split'):
        ds = dataset()
        service = ds.service_time(g, mean_speed, PICK)
        targets = ds.targets(g, sc['split'], sc['start'], sc['tasks'])
    else:
        service = mean_service_time(g, mean_speed, PICK)
    rate = sc['rho'] * R / service
    kw = dict(route_mode='dijkstra_dynamique', idle_mode='rester_sur_place')
    if kind == 'route':
        kw.update(route_mode='drl_route', route_agent=agent, on_route_transition=cb)
    else:
        demand = train_fit_demand(g)
        kw.update(idle_mode='drl_idle', idle_agent=agent, demand_prior=demand,
                  on_idle_transition=cb)
    return BenchmarkV4(sc['alloc'], g, R, rate, sc['tasks'], seed=sc['seed'],
                       speed=SPEED, pick_time=PICK, speeds=speeds,
                       block_rate=sc.get('block_rate', 0.0), targets=targets,
                       epsilon=epsilon, explore_seed=explore_seed, **kw)


def val_scenarios(kind):
    out, i = [], 0
    if kind == 'route':
        base = [dict(robots=3, block_rate=1 / 60), dict(robots=3, block_rate=3 / 60),
                dict(robots=3, block_rate=6 / 60), dict(robots=6, block_rate=3 / 60),
                dict(robots=10, block_rate=1 / 60)]
        for b in base:
            for s in range(2):
                out.append(dict(b, dims=SIZES[b['robots']], rho=0.7, tasks=150,
                                alloc='greedy_pair', seed=VAL_SEEDS[i]))
                i += 1
        ds = dataset()
        for s in range(2):
            out.append(dict(robots=3, dims=(5, 3), rho=0.9, tasks=150, alloc='greedy_pair',
                            seed=VAL_SEEDS[i], split='train_val',
                            start=ds.evenly_spaced_start('train_val', 150, s, 2)))
            i += 1
    else:
        ds = dataset()
        for cfg in DATASET_CONFIGS:
            for alloc in ('greedy_pair', 'greedy_time'):
                for s in range(2):
                    out.append(dict(cfg, tasks=150, alloc=alloc, seed=VAL_SEEDS[i],
                                    split='train_val',
                                    start=ds.evenly_spaced_start('train_val', 150, s, 2)))
                    i += 1
    return out


def train_scenario(kind, sim_seed, rng):
    if kind == 'route':
        R = rng.choice([3, 6, 10, 20])
        sc = dict(robots=R, dims=SIZES[R], rho=rng.choice([0.7, 0.9]),
                  block_rate=rng.choice([0, 1, 3, 6]) / 60.0, tasks=100,
                  alloc='greedy_pair', seed=sim_seed)
        if rng.random() < 0.5:
            ds = dataset()
            starts = ds.window_starts('train_fit', 100)
            sc.update(split='train_fit', start=rng.choice(starts))
        return sc
    cfg = rng.choice(DATASET_CONFIGS)
    ds = dataset()
    starts = ds.window_starts('train_fit', 100)
    return dict(cfg, tasks=100, alloc=rng.choice(['greedy_pair', 'greedy_time']),
                seed=sim_seed, split='train_fit', start=rng.choice(starts))


def evaluate(kind, agent, scenarios):
    vals = []
    for sc in scenarios:
        m = make_sim(sc, kind, agent).run()
        vals.append(m['temps_traitement_moy_s'])
    return vals


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--kind', choices=['route', 'idle'], required=True)
    p.add_argument('--seed', type=int, required=True)
    p.add_argument('--budget-min', type=float, default=120.0)
    p.add_argument('--val-every-min', type=float, default=10.0)
    p.add_argument('--out-dir', required=True)
    args = p.parse_args(argv)
    torch.set_num_threads(1)
    random.seed(args.seed)
    np.random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    kind, seed = args.kind, args.seed
    nf = N_ROUTE_FEATURES if kind == 'route' else N_IDLE_FEATURES
    gamma = 1.0 if kind == 'route' else 0.9   # ecart 2 (PROTOCOLE_V4.md)
    agent = V4DQN(kind, nf, gamma=gamma, seed=seed)
    agent.meta = {'train_seed': seed, 'reward_norm_s': 60.0}
    val_sc = val_scenarios(kind)
    budget = args.budget_min * 60.0
    t_start = time.time()

    def elapsed():
        return time.time() - t_start

    stats = {'loss': [], 'corr': [], 'n': 0}

    def cb(feat, reward, next_feats, done):
        agent.remember(feat, reward, next_feats, done)
        stats['n'] += 1
        info = agent.train_step()
        if info:
            stats['loss'].append(info['loss'])
            stats['corr'].append(info['correction'])

    tlog = open(os.path.join(args.out_dir, f'train_log_seed{seed}.csv'), 'w', newline='')
    vlog = open(os.path.join(args.out_dir, f'val_log_seed{seed}.csv'), 'w', newline='')
    tw = csv.writer(tlog)
    tw.writerow(['graine', 'episode', 'temps_min', 'epsilon', 'transitions', 'perte_td_moy',
                 'correction_abs_moy', 'robots', 'block_rate_min', 'source', 'allocation',
                 'temps_traitement_moy_s'])
    vw = csv.writer(vlog)
    vw.writerow(['graine', 'episode', 'temps_min', 'val_temps_traitement_moy_s']
                + [f'sc{i}' for i in range(len(val_sc))])
    best = (float('inf'), None)

    def validate(ep):
        nonlocal best
        t0 = elapsed()
        vals = evaluate(kind, agent, val_sc)
        v = statistics.mean(vals)
        tmin = round(t0 / 60.0, 2)
        vw.writerow([seed, ep, tmin, round(v, 4)] + [round(x, 4) for x in vals])
        vlog.flush()
        path = os.path.join(args.out_dir, f'ckpt_seed{seed}_t{int(round(tmin))}.pt')
        agent.save(path, val_temps_traitement_moy_s=v, episode=ep, temps_min=tmin)
        if v < best[0]:
            best = (v, path)
            agent.save(os.path.join(args.out_dir, f'best_seed{seed}.pt'),
                       val_temps_traitement_moy_s=v, episode=ep, temps_min=tmin)
        print(f'[{kind} graine {seed}] t={tmin:6.1f} min ep={ep:5d} val={v:.3f} s '
              f'(meilleur {best[0]:.3f}) ({elapsed() - t0:.0f} s de validation)', flush=True)

    validate(0)
    next_val = args.val_every_min * 60.0
    stream = train_seed_stream(seed)
    ep = 0
    while elapsed() < budget:
        frac = min(1.0, elapsed() / (0.6 * budget))
        eps = 0.3 - 0.28 * frac
        sim_seed, rng = next(stream)
        sc = train_scenario(kind, sim_seed, rng)
        stats.update(loss=[], corr=[], n=0)
        sim = make_sim(sc, kind, agent, epsilon=eps, cb=cb, explore_seed=sim_seed)
        sim.horizon = min(sim.horizon, sim.arrivals[-1].created + 1800.0)
        m = sim.run()
        ep += 1
        tw.writerow([seed, ep, round(elapsed() / 60.0, 2), round(eps, 4), stats['n'],
                     round(statistics.mean(stats['loss']), 6) if stats['loss'] else '',
                     round(statistics.mean(stats['corr']), 6) if stats['corr'] else '',
                     sc['robots'], round(sc.get('block_rate', 0.0) * 60), sc.get('split', 'synth'),
                     sc['alloc'], round(m['temps_traitement_moy_s'], 4)])
        if ep % 10 == 0:
            tlog.flush()
        if elapsed() >= next_val:
            validate(ep)
            next_val += args.val_every_min * 60.0
    # derniere validation si la precedente date de plus de 2 minutes
    if next_val - args.val_every_min * 60.0 < elapsed() - 120:
        validate(ep)
    tlog.close()
    vlog.close()
    print(f'[{kind} graine {seed}] fin : {ep} episodes, meilleur val {best[0]:.3f} s '
          f'({best[1]})', flush=True)


if __name__ == '__main__':
    main()
