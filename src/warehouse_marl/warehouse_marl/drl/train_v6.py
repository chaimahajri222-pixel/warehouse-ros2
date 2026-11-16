"""
train_v6.py
-----------
Entrainement des DQN residuels v6 (PROTOCOLE_V6.md) : une graine par
processus, UN SEUL entrainement a la fois, torch.set_num_threads(2), budget
en temps reel, validation ET sauvegarde complete toutes les 10 minutes
(reprise possible apres un crash : relancer la meme commande).

    python -m warehouse_marl.drl.train_v6 --kind idle6 --seed 0 --budget-min 90 \
        --out-dir ~/warehouse_ws/drl_v6/idle6
    python -m warehouse_marl.drl.train_v6 --kind route6 --seed 0 ...

Sorties (--out-dir) :
  train_log_seed<k>.csv  par episode d'entrainement ;
  val_log_seed<k>.csv    par validation (moyenne absolue, ecart relatif moyen a
                         la meilleure heuristique de chaque scenario, critere de
                         selection) ;
  val_ref.csv            heuristiques concurrentes sur les scenarios de validation ;
  ckpt_seed<k>_t<min>.pt modele a chaque validation ;
  etat_seed<k>.pt        etat complet (reseaux, Adam, memoire de rejeu, generateurs,
                         episode, temps consomme) pour la reprise ;
  fini_seed<k>.txt       marqueur de fin.
"""

from __future__ import annotations

import argparse
import csv
import os
import pickle
import random
import statistics
import time

import numpy as np
import torch

from warehouse_marl.allocation_benchmark import build_grid_warehouse, mean_service_time
from warehouse_marl.drl.train_v4 import DATASET_CONFIGS, PICK, SPEED, dataset, train_fit_demand
from warehouse_marl.drl.train_v4 import TEST_SEEDS as TEST_SEEDS_V4
from warehouse_marl.drl.train_v4 import VAL_SEEDS as VAL_SEEDS_V4
from warehouse_marl.drl.v4_dqn import V4DQN
from warehouse_marl.drl.v6_sim import N_IDLE6_FEATURES, N_ROUTE6_FEATURES, BenchmarkV6

# ---------------------------------------------------------------------- #
# Graines (PROTOCOLE_V6.md, section 4)
# ---------------------------------------------------------------------- #
N_TEST6 = 20
TEST6_SEEDS = tuple(2_000_003 + 1_013 * k for k in range(N_TEST6))
VAL6_SEEDS = tuple(3_000_017 + 1_019 * i for i in range(400))
FORBIDDEN = frozenset(TEST6_SEEDS) | frozenset(VAL6_SEEDS) | TEST_SEEDS_V4 | frozenset(VAL_SEEDS_V4)
assert not set(TEST6_SEEDS) & set(VAL6_SEEDS)
assert not set(TEST6_SEEDS) & (TEST_SEEDS_V4 | set(VAL_SEEDS_V4))

IDLE_HEURISTICS = ('rester_sur_place', 'retour_au_depot', 'centre_de_demande')
ROUTE_HEURISTICS = ('dijkstra_statique', 'dijkstra_dynamique', 'dijkstra_congestion')
ALLOC_HEURISTICS = ('greedy_pair', 'greedy_time')
# Ecart 2 (PROTOCOLE_V6.md) : la couverture est aussi un concurrent de la phase A,
# donc aussi dans la reference de validation (critere de selection).
HEURISTICS = {'idle6': IDLE_HEURISTICS + ('couverture',), 'route6': ROUTE_HEURISTICS,
              'alloc6': ALLOC_HEURISTICS}

# conditions du banc de routage avec congestion (phase B)
ROUTE6_TRAIN_FLEETS = [(10, (10, 8)), (20, (10, 8)), (20, (15, 10))]
# conditions de test de la phase B (PROTOCOLE_V6.md, section 6.2)
ROUTE6_CONDITIONS = [
    dict(label='B1 10 r., 80 racks, rho=0.9', robots=10, dims=(10, 8), rho=0.9),
    dict(label='B2 20 r., 80 racks, rho=0.9', robots=20, dims=(10, 8), rho=0.9),
    dict(label='B3 20 r., 150 racks, rho=0.9', robots=20, dims=(15, 10), rho=0.9),
    dict(label='B4 20 r., 150 racks, rho=0.7, vagues', robots=20, dims=(15, 10), rho=0.7,
         footwear=True),
]


class SeedStream:
    """Graines de simulation d'entrainement (picklable, pour la reprise),
    disjointes de la validation et du test (v4 et v6)."""

    def __init__(self, seed):
        self.rng = random.Random(10_007 * seed + 6)

    def next(self):
        s = self.rng.randrange(10_000_000, 10 ** 9)
        assert s not in FORBIDDEN
        return s, self.rng


def test_window_start(ds, k, n_tasks=150):
    """Fenetre de TEST v6 : milieu du k-ieme de 20 intervalles reguliers
    (les fenetres v4 etaient au debut de chaque intervalle)."""
    starts = ds.window_starts('test', n_tasks)
    return starts[((2 * k + 1) * len(starts)) // (2 * N_TEST6)]


# ---------------------------------------------------------------------- #
def make_sim6(sc, mode, agent=None, epsilon=0.0, cb=None, explore_seed=None, phase=None):
    """BenchmarkV6 d'un scenario. ``mode`` : methode d'attente (phase A) ou
    de routage (phase B)."""
    phase = phase or sc.get('phase', 'A')
    if phase == 'C':
        from warehouse_marl.drl.alloc6 import make_alloc_sim
        return make_alloc_sim(sc, mode, agent, epsilon=epsilon, cb=cb, explore_seed=explore_seed)
    dims, R = sc['dims'], sc['robots']
    g = build_grid_warehouse(*dims)
    speeds = sc.get('speeds')
    mean_speed = statistics.mean(speeds) if speeds else SPEED
    targets, demand = None, None
    if sc.get('split'):
        ds = dataset()
        service = ds.service_time(g, mean_speed, PICK)
        targets = ds.targets(g, sc['split'], sc['start'], sc['tasks'])
        if phase == 'A':
            demand = train_fit_demand(g)
    else:
        service = mean_service_time(g, mean_speed, PICK)
    rate = sc['rho'] * R / service
    kw = {}
    if phase == 'A':
        kw.update(idle_mode=mode, demand_prior=demand)
        if mode == 'drl_idle6':
            kw.update(idle6_agent=agent, on_idle6_transition=cb)
        elif mode == 'drl_idle':
            kw.update(idle_agent=agent)
    else:
        kw.update(route_mode=mode, edge_capacity=1)
        if mode == 'drl_route6':
            kw.update(route6_agent=agent, on_route6_transition=cb)
    return BenchmarkV6(sc['alloc'], g, R, rate, sc['tasks'], seed=sc['seed'], speed=SPEED,
                       pick_time=PICK, speeds=speeds, block_rate=sc.get('block_rate', 0.0),
                       block_min=sc.get('block_min', 30.0), block_max=sc.get('block_max', 120.0),
                       demand_skew=sc.get('skew', 0.0), targets=targets, epsilon=epsilon,
                       explore_seed=explore_seed, **kw)


def idle6_configs(taille):
    """Ecart 3 (PROTOCOLE_V6.md) : modele 'petit' (15 et 40 racks, 3 et 6 robots)
    et modele 'grand' (150 racks, 20 robots) ; 'tous' = plan initial."""
    if taille == 'petit':
        return [c for c in DATASET_CONFIGS if c['robots'] < 10]
    if taille == 'grand':
        return [c for c in DATASET_CONFIGS if c['robots'] >= 10]
    return list(DATASET_CONFIGS)


def val_scenarios(kind, taille='tous'):
    ds = dataset()
    out, i = [], 0
    if kind == 'idle6' and taille == 'grand':
        # 12 fenetres train_val, greedy_pair (vitesses egales) ; graines 100+
        for s in range(12):
            out.append(dict(idle6_configs('grand')[0], phase='A', tasks=150, alloc='greedy_pair',
                            seed=VAL6_SEEDS[100 + s], split='train_val',
                            start=ds.evenly_spaced_start('train_val', 150, s, 12)))
        return out
    if kind == 'idle6':
        # vitesses egales : greedy_time == greedy_pair, donc greedy_pair seul
        # (6 fenetres) ; vitesses variables : les 2 allocations (3 fenetres)
        for cfg in idle6_configs(taille):
            allocs = (('greedy_pair', 'greedy_time') if cfg.get('speeds') else ('greedy_pair',))
            nwin = 6 // len(allocs)
            for alloc in allocs:
                for s in range(nwin):
                    out.append(dict(cfg, phase='A', tasks=150, alloc=alloc, seed=VAL6_SEEDS[i],
                                    split='train_val',
                                    start=ds.evenly_spaced_start('train_val', 150, s, nwin)))
                    i += 1
        return out
    if kind == 'alloc6':
        for cfg in DATASET_CONFIGS:
            for s in range(3):
                out.append(dict(cfg, phase='C', tasks=150, alloc='-', seed=VAL6_SEEDS[200 + i],
                                split='train_val',
                                start=ds.evenly_spaced_start('train_val', 150, s, 3)))
                i += 1
        return out
    for cond in ROUTE6_CONDITIONS:
        for s in range(3):
            sc = dict(phase='B', robots=cond['robots'], dims=cond['dims'], rho=cond['rho'],
                      tasks=150, alloc='greedy_pair', seed=VAL6_SEEDS[i])
            if cond.get('footwear'):
                sc.update(split='train_val',
                          start=ds.evenly_spaced_start('train_val', 150, s, 3))
            out.append(sc)
            i += 1
    return out


def train_scenario(kind, sim_seed, rng, taille='tous'):
    ds = dataset()
    starts = ds.window_starts('train_fit', 100)
    if kind == 'alloc6':
        cfg = rng.choice(DATASET_CONFIGS)
        return dict(cfg, phase='C', tasks=100, alloc='-', seed=sim_seed, split='train_fit',
                    start=rng.choice(starts))
    if kind == 'idle6':
        cfg = rng.choice(idle6_configs(taille))
        return dict(cfg, phase='A', tasks=100, alloc=rng.choice(['greedy_pair', 'greedy_time']),
                    seed=sim_seed, split='train_fit', start=rng.choice(starts))
    R, dims = rng.choice(ROUTE6_TRAIN_FLEETS)
    sc = dict(phase='B', robots=R, dims=dims, rho=rng.choice([0.7, 0.9]), tasks=100,
              alloc='greedy_pair', seed=sim_seed)
    if rng.random() < 0.5:
        sc.update(split='train_fit', start=rng.choice(starts))
    return sc


def drl_mode(kind):
    return {'idle6': 'drl_idle6', 'route6': 'drl_route6', 'alloc6': 'drl_alloc6'}[kind]


def evaluate(kind, agent, scenarios):
    return [make_sim6(sc, drl_mode(kind), agent).run()['temps_traitement_moy_s']
            for sc in scenarios]


def reference(kind, scenarios, out_dir):
    """Heuristiques concurrentes sur la validation (calculees une fois)."""
    path = os.path.join(out_dir, 'val_ref.csv')
    heur = HEURISTICS[kind]
    if os.path.isfile(path):
        with open(path, newline='') as f:
            rows = list(csv.DictReader(f))
        if len(rows) == len(scenarios) and all(h in rows[0] for h in heur):
            return [min(float(r[h]) for h in heur) for r in rows]
    rows = []
    for i, sc in enumerate(scenarios):
        row = {'scenario': i, 'robots': sc['robots'], 'racks': sc['dims'][0] * sc['dims'][1],
               'rho': sc['rho'], 'allocation': sc['alloc'], 'graine': sc['seed'],
               'source': sc.get('split', 'synth'), 'debut': sc.get('start', '')}
        for h in heur:
            row[h] = round(make_sim6(sc, h).run()['temps_traitement_moy_s'], 4)
        rows.append(row)
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return [min(float(r[h]) for h in heur) for r in rows]


# ---------------------------------------------------------------------- #
def _atomic_save(obj, path):
    tmp = path + '.tmp'
    with open(tmp, 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(tmp, path)


def _truncate_csv(path, max_episode):
    """Garde l'en-tete et les lignes d'episode <= max_episode (reprise)."""
    if not os.path.isfile(path):
        return
    with open(path, newline='') as f:
        rows = list(csv.reader(f))
    if not rows:
        return
    head, body = rows[0], rows[1:]
    k = head.index('episode')
    body = [r for r in body if r and int(r[k]) <= max_episode]
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(body)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--kind', choices=['idle6', 'route6', 'alloc6'], required=True)
    p.add_argument('--seed', type=int, required=True)
    p.add_argument('--budget-min', type=float, default=90.0)
    p.add_argument('--val-every-min', type=float, default=10.0)
    p.add_argument('--train-every', type=int, default=1,
                   help='une mise a jour du reseau toutes les N transitions')
    p.add_argument('--threads', type=int, default=2)
    p.add_argument('--taille', choices=['tous', 'petit', 'grand'], default='tous',
                   help='idle6 : modele petit (15/40 racks) ou grand (150 racks), ecart 3')
    p.add_argument('--idle6-sans-tache', choices=['zero', 'ignorer'], default='zero',
                   help='idle6 : decision non suivie d une tache -> recompense 0 ou '
                        'transition ignoree (ecart 4)')
    p.add_argument('--idle6-recompense', choices=['individuelle', 'equipe'],
                   default='individuelle', help='idle6 : recompense (ecart 5)')
    p.add_argument('--out-dir', required=True)
    args = p.parse_args(argv)
    torch.set_num_threads(args.threads)
    os.makedirs(args.out_dir, exist_ok=True)
    kind, seed = args.kind, args.seed
    done_path = os.path.join(args.out_dir, f'fini_seed{seed}.txt')
    if os.path.isfile(done_path):
        print(f'[{kind} graine {seed}] deja fini ({done_path})', flush=True)
        return
    from warehouse_marl.drl.alloc6 import N_ALLOC6_FEATURES
    nf = {'idle6': N_IDLE6_FEATURES, 'route6': N_ROUTE6_FEATURES,
          'alloc6': N_ALLOC6_FEATURES}[kind]
    gamma = {'idle6': 0.9, 'route6': 1.0, 'alloc6': 0.99}[kind]   # alloc6 : ecart 7
    val_sc = val_scenarios(kind, args.taille)
    ref = reference(kind, val_sc, args.out_dir)
    budget = args.budget_min * 60.0
    state_path = os.path.join(args.out_dir, f'etat_seed{seed}.pt')
    tlog_path = os.path.join(args.out_dir, f'train_log_seed{seed}.csv')
    vlog_path = os.path.join(args.out_dir, f'val_log_seed{seed}.csv')

    agent = V4DQN(kind, nf, gamma=gamma, seed=seed)
    agent.meta = {'train_seed': seed, 'version': 'v6',
                  'reward': {'idle6': '-approche / (diametre / vitesse moyenne)',
                             'route6': '-duree / 60 s',
                             'alloc6': '-(taches non finies x duree) / 60 s (ecart 7)'}[kind],
                  'train_every': args.train_every, 'taille': args.taille,
                  'idle6_sans_tache': args.idle6_sans_tache,
                  'idle6_recompense': args.idle6_recompense}
    stream = SeedStream(seed)
    ep, consumed, best, next_val, n_resume = 0, 0.0, (float('inf'), None), 0.0, 0
    if os.path.isfile(state_path):
        with open(state_path, 'rb') as f:
            st = pickle.load(f)
        agent.q.load_state_dict(st['q'])
        agent.target.load_state_dict(st['target'])
        agent.opt.load_state_dict(st['opt'])
        agent.buffer.extend(st['buffer'])
        agent.rng.setstate(st['agent_rng'])
        agent.updates = st['updates']
        torch.set_rng_state(st['torch_rng'])
        np.random.set_state(st['np_rng'])
        random.setstate(st['py_rng'])
        stream = st['stream']
        ep, consumed, best, next_val = st['ep'], st['consumed'], st['best'], st['next_val']
        n_resume = st.get('n_resume', 0) + 1
        _truncate_csv(tlog_path, ep)
        _truncate_csv(vlog_path, ep)
        print(f'[{kind} graine {seed}] REPRISE n {n_resume} a l episode {ep}, '
              f'{consumed / 60:.1f} min deja consommees', flush=True)
    else:
        random.seed(seed)
        np.random.seed(seed)

    t_session = time.time()

    def elapsed():
        return consumed + (time.time() - t_session)

    stats = {'loss': [], 'corr': [], 'n': 0}

    def cb(feat, reward, next_feats, done):
        agent.remember(feat, reward, next_feats, done)
        stats['n'] += 1
        if stats['n'] % args.train_every == 0:
            info = agent.train_step()
            if info:
                stats['loss'].append(info['loss'])
                stats['corr'].append(info['correction'])

    new_t = not os.path.isfile(tlog_path)
    tlog = open(tlog_path, 'a', newline='')
    tw = csv.writer(tlog)
    if new_t:
        tw.writerow(['graine', 'episode', 'temps_min', 'epsilon', 'transitions', 'perte_td_moy',
                     'correction_abs_moy', 'robots', 'racks', 'rho', 'source', 'allocation',
                     'temps_traitement_moy_s'])
    new_v = not os.path.isfile(vlog_path)
    vlog = open(vlog_path, 'a', newline='')
    vw = csv.writer(vlog)
    if new_v:
        vw.writerow(['graine', 'episode', 'temps_min', 'val_temps_traitement_moy_s',
                     'val_ecart_rel_moy', 'reprises'] + [f'sc{i}' for i in range(len(val_sc))])

    def checkpoint():
        nonlocal best
        t0 = elapsed()
        vals = evaluate(kind, agent, val_sc)
        v = statistics.mean(vals)
        rel = statistics.mean((x - y) / y for x, y in zip(vals, ref))
        tmin = round(t0 / 60.0, 2)
        vw.writerow([seed, ep, tmin, round(v, 4), round(rel, 6), n_resume]
                    + [round(x, 4) for x in vals])
        vlog.flush()
        tlog.flush()
        path = os.path.join(args.out_dir, f'ckpt_seed{seed}_t{int(round(tmin))}.pt')
        agent.save(path, val_temps_traitement_moy_s=v, val_ecart_rel_moy=rel, episode=ep,
                   temps_min=tmin)
        if rel < best[0]:
            best = (rel, path)
        st = {'q': agent.q.state_dict(), 'target': agent.target.state_dict(),
              'opt': agent.opt.state_dict(), 'buffer': list(agent.buffer),
              'agent_rng': agent.rng.getstate(), 'updates': agent.updates,
              'torch_rng': torch.get_rng_state(), 'np_rng': np.random.get_state(),
              'py_rng': random.getstate(), 'stream': stream, 'ep': ep,
              'consumed': elapsed(), 'best': best, 'next_val': next_val,
              'n_resume': n_resume}
        _atomic_save(st, state_path)
        print(f'[{kind} graine {seed}] t={tmin:6.1f} min ep={ep:5d} val={v:.3f} s '
              f'ecart rel {100 * rel:+.2f} % (meilleur {100 * best[0]:+.2f} %) '
              f'({elapsed() - t0:.0f} s de validation)', flush=True)

    if ep == 0 and next_val == 0.0:
        next_val = args.val_every_min * 60.0
        checkpoint()
    while elapsed() < budget:
        frac = min(1.0, elapsed() / (0.6 * budget))
        eps = 0.3 - 0.28 * frac
        sim_seed, rng = stream.next()
        sc = train_scenario(kind, sim_seed, rng, args.taille)
        stats.update(loss=[], corr=[], n=0)
        sim = make_sim6(sc, drl_mode(kind), agent, epsilon=eps, cb=cb, explore_seed=sim_seed)
        sim.horizon = min(sim.horizon, sim.arrivals[-1].created + 1800.0)
        if kind == 'idle6':
            sim.idle6_unrewarded = args.idle6_sans_tache
            sim.idle6_reward = args.idle6_recompense
        m = sim.run()
        ep += 1
        tw.writerow([seed, ep, round(elapsed() / 60.0, 2), round(eps, 4), stats['n'],
                     round(statistics.mean(stats['loss']), 6) if stats['loss'] else '',
                     round(statistics.mean(stats['corr']), 6) if stats['corr'] else '',
                     sc['robots'], sc['dims'][0] * sc['dims'][1], sc['rho'],
                     sc.get('split', 'synth'), sc['alloc'],
                     round(m['temps_traitement_moy_s'], 4)])
        if elapsed() >= next_val:
            next_val += args.val_every_min * 60.0
            checkpoint()
    if next_val - args.val_every_min * 60.0 < elapsed() - 120:
        checkpoint()
    tlog.close()
    vlog.close()
    with open(done_path, 'w') as f:
        f.write(f'episodes {ep}\nmeilleur ecart rel {best[0]}\n{best[1]}\n')
    print(f'[{kind} graine {seed}] fin : {ep} episodes, meilleur ecart rel '
          f'{100 * best[0]:+.2f} % ({best[1]})', flush=True)


if __name__ == '__main__':
    main()
