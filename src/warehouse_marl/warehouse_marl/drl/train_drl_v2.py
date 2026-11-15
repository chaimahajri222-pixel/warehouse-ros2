"""
train_drl_v2.py
---------------
Entrainement hors-ligne du DRL v2 (Q par couple robot/tache) sur
drl/env_v2.py, avec plusieurs graines independantes, validation reguliere
contre FIFO et le consensus heuristique, et conservation du meilleur modele.

    ros2 run warehouse_marl train_drl_v2 --episodes 300 --seeds 3 --out-dir drl_v2
    python3 -m warehouse_marl.drl.train_drl_v2 --episodes 40 --seeds 2   # essai rapide

Sorties (dans --out-dir) :
  drl2_seed<k>.pt          meilleur modele de chaque graine (validation)
  drl2_best.pt             meilleur modele toutes graines confondues
  training_log_v2.csv      une ligne par episode et par graine : recompense
                           moyenne (centree et brute), perte TD, Q moyenne,
                           norme du gradient, epsilon, temps de traitement
  validation_v2.csv        une ligne par validation : temps de traitement
                           moyen du DRL, de FIFO, du consensus et du temoin
                           greedy_pair (meme espace de decision, sans
                           apprentissage : couple de cout minimal)
  indicators_v2.csv        tableau d'indicateurs (aussi affiche)
  training_curves_v2.png   moyenne +/- ecart-type sur les graines
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import random
import statistics
import time
import warnings
from typing import Dict, List

import numpy as np

from warehouse_marl.drl.env_v2 import AllocationEnvV2, REWARD_NORM_S, make_benchmark

# Scenarios FIXES de validation (jamais tires pendant l'entrainement : graines
# distinctes) ; 2 graines par configuration.
VAL_CONFIGS = [
    dict(dims=(5, 3), robots=3, rho=0.5, block_rate=0.0),
    dict(dims=(5, 3), robots=3, rho=0.7, block_rate=0.0),
    dict(dims=(5, 3), robots=3, rho=0.9, block_rate=0.0),
    dict(dims=(5, 3), robots=4, rho=0.9, block_rate=3 / 60),
    dict(dims=(8, 5), robots=6, rho=0.7, block_rate=1 / 60),
    dict(dims=(8, 5), robots=5, rho=0.9, block_rate=0.0),
]


def val_scenarios(n_tasks: int, n_seeds: int = 2) -> List[Dict]:
    return [dict(cfg, tasks=n_tasks, seed=900_001 + 7919 * i + 104_729 * s)
            for i, cfg in enumerate(VAL_CONFIGS) for s in range(n_seeds)]


def evaluate(method: str, scenarios, agent=None) -> List[float]:
    out = []
    for sc in scenarios:
        res = make_benchmark(method, sc, agent2=agent).run()
        out.append(res['temps_traitement_moy_s'])
    return out


def parse_args(argv=None):
    p = argparse.ArgumentParser(description='Entrainement DQN v2 (Q par couple robot/tache)')
    p.add_argument('--episodes', type=int, default=300)
    p.add_argument('--seeds', type=int, default=3, help='graines d entrainement independantes')
    p.add_argument('--seed-base', type=int, default=0)
    p.add_argument('--tasks', type=int, default=80, help='taches par episode')
    p.add_argument('--val-every', type=int, default=20)
    p.add_argument('--val-tasks', type=int, default=100)
    p.add_argument('--patience', type=int, default=6,
                   help='validations sans amelioration avant arret (0 = jamais)')
    p.add_argument('--gamma', type=float, default=0.95)
    p.add_argument('--lr', type=float, default=5e-4)
    p.add_argument('--hidden', type=int, default=64)
    p.add_argument('--batch-size', type=int, default=64)
    p.add_argument('--buffer', type=int, default=50_000)
    p.add_argument('--warmup', type=int, default=500)
    p.add_argument('--target-every', type=int, default=250,
                   help='pas entre copies du reseau cible')
    p.add_argument('--eps-start', type=float, default=1.0)
    p.add_argument('--eps-end', type=float, default=0.05)
    p.add_argument('--eps-decay-frac', type=float, default=0.5,
                   help='fraction des episodes pour la decroissance lineaire d epsilon')
    p.add_argument('--double', dest='double', action='store_true', default=True)
    p.add_argument('--no-double', dest='double', action='store_false')
    p.add_argument('--out-dir', default='drl_v2')
    p.add_argument('--threads', type=int, default=1, help='threads PyTorch (1 = plus rapide ici)')
    return p.parse_args(argv)


def train_seed(k: int, args, val_sc, refs, out_dir) -> Dict:
    import torch
    from warehouse_marl.drl.pair_dqn import PairDQN

    seed = args.seed_base + k
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    env = AllocationEnvV2(seed=10_000 + seed, n_tasks=args.tasks)
    agent = PairDQN(hidden=args.hidden, lr=args.lr, gamma=args.gamma, double=args.double,
                    buffer_size=args.buffer, batch_size=args.batch_size,
                    target_every=args.target_every, warmup=args.warmup, seed=seed)
    agent.meta = {'reward_norm_s': REWARD_NORM_S, 'speed': env.speed,
                  'pick_time': env.pick_time, 'k_candidates': 5, 'train_seed': seed}
    decay_eps = max(1, int(args.eps_decay_frac * args.episodes))
    best, best_ep, since_best = math.inf, 0, 0
    log, vals = [], []
    best_path = os.path.join(out_dir, f'drl2_seed{seed}.pt')
    t0 = time.time()
    for ep in range(1, args.episodes + 1):
        frac = (ep - 1) / decay_eps
        eps = max(args.eps_end, args.eps_start - (args.eps_start - args.eps_end) * frac)
        obs, info = env.reset()
        done = info['done']
        rewards, raws, losses, qs, grads = [], [], [], [], []
        metrics = {}
        while not done:
            a = agent.act(obs, eps)
            nxt, r, done, inf = env.step(a)
            agent.remember(obs[a], r, nxt, done)
            st = agent.train_step()
            if st:
                losses.append(st['loss'])
                qs.append(st['q'])
                grads.append(st['grad'])
            rewards.append(r)
            raws.append(inf['raw_reward'])
            obs = nxt
            metrics = inf.get('metrics', metrics)
        sc = env.scenario
        row = {'graine': seed, 'episode': ep, 'epsilon': round(eps, 4),
               'robots': sc['robots'], 'racks': sc['dims'][0] * sc['dims'][1], 'rho': sc['rho'],
               'blocages_min': round(60 * sc['block_rate'], 2), 'decisions': len(rewards),
               'recompense_moy': statistics.mean(rewards) if rewards else math.nan,
               'recompense_brute_moy': statistics.mean(raws) if raws else math.nan,
               'perte_td': statistics.mean(losses) if losses else math.nan,
               'q_moy': statistics.mean(qs) if qs else math.nan,
               'norme_gradient': statistics.mean(grads) if grads else math.nan,
               'temps_traitement_s': metrics.get('temps_traitement_moy_s', math.nan),
               'val_temps_traitement_s': math.nan}
        if ep % args.val_every == 0 or ep == args.episodes:
            agent.q.eval()
            v = evaluate('drl2_direct', val_sc, agent)
            agent.q.train()
            vm = statistics.mean(v)
            row['val_temps_traitement_s'] = vm
            gain_f = 100 * statistics.mean((f - x) / f for x, f in zip(v, refs['fifo']))
            gain_c = 100 * statistics.mean((c - x) / c for x, c in zip(v, refs['consensus']))
            gain_g = 100 * statistics.mean((g - x) / g for x, g in zip(v, refs['greedy_pair']))
            vals.append({'graine': seed, 'episode': ep, 'val_drl2_s': vm,
                         'val_fifo_s': statistics.mean(refs['fifo']),
                         'val_consensus_s': statistics.mean(refs['consensus']),
                         'val_greedy_pair_s': statistics.mean(refs['greedy_pair']),
                         'gain_vs_fifo_pct': gain_f, 'gain_vs_consensus_pct': gain_c,
                         'gain_vs_greedy_pair_pct': gain_g})
            mark = ''
            if vm < best:
                best, best_ep, since_best = vm, ep, 0
                agent.save(best_path, val_temps_traitement_s=vm, val_episode=ep,
                           val_gain_vs_fifo_pct=gain_f, val_gain_vs_consensus_pct=gain_c,
                           val_gain_vs_greedy_pair_pct=gain_g)
                mark = ' *meilleur*'
            else:
                since_best += 1
            print(f'  [graine {seed}] ep {ep:4d}  eps={eps:.2f}  perte={row["perte_td"]:.4f}  '
                  f'Q={row["q_moy"]:+.3f}  val={vm:6.2f} s  vs FIFO {gain_f:+.1f} %  '
                  f'vs consensus {gain_c:+.1f} %  vs greedy_pair {gain_g:+.1f} %  '
                  f'({time.time() - t0:.0f} s){mark}', flush=True)
        log.append(row)
        if args.patience and since_best >= args.patience:
            print(f'  [graine {seed}] arret anticipe a l episode {ep} '
                  f'(meilleur a l episode {best_ep})')
            break
    return {'seed': seed, 'log': log, 'vals': vals, 'best': best, 'best_ep': best_ep,
            'path': best_path, 'seconds': time.time() - t0}


# ---------------------------------------------------------------------- #
def _window(xs, frac, last):
    xs = [x for x in xs if not math.isnan(x)]
    if not xs:
        return math.nan
    n = max(1, int(len(xs) * frac))
    return statistics.mean(xs[-n:] if last else xs[:n])


def indicators(results, refs) -> List[Dict]:
    rows = []
    fifo, cons = statistics.mean(refs['fifo']), statistics.mean(refs['consensus'])
    for res in results:
        vals = [v['val_drl2_s'] for v in res['vals']]
        eps = [v['episode'] for v in res['vals']]
        final = vals[-1] if vals else math.nan
        conv = math.nan
        for i in range(len(vals)):
            if all(abs(x - final) <= 0.05 * final for x in vals[i:]):
                conv = eps[i]
                break
        best_val = next((v for v in res['vals'] if v['episode'] == res['best_ep']), {})
        losses = [r['perte_td'] for r in res['log']]
        qs = [r['q_moy'] for r in res['log'] if not math.isnan(r['q_moy'])]
        q_range = (max(qs) - min(qs)) if qs else math.nan
        n20 = max(2, len(qs) // 5)
        q_tail = qs[-n20:]
        q_drift = (max(q_tail) - min(q_tail)) if q_tail else math.nan
        rows.append({
            'graine': res['seed'],
            'meilleure_val_s': round(res['best'], 2),
            'episode_meilleur': res['best_ep'],
            'gain_val_vs_fifo_pct': round(best_val.get('gain_vs_fifo_pct', math.nan), 2),
            'gain_val_vs_consensus_pct': round(best_val.get('gain_vs_consensus_pct', math.nan), 2),
            'gain_val_vs_greedy_pair_pct': round(
                best_val.get('gain_vs_greedy_pair_pct', math.nan), 2),
            'episode_convergence_5pct': conv,
            'perte_debut': round(_window(losses, 0.1, False), 4),
            'perte_fin': round(_window(losses, 0.1, True), 4),
            'q_fin_moy': round(statistics.mean(q_tail), 3) if q_tail else math.nan,
            'q_variation_20pct_fin': round(q_drift, 3),
            'q_stable': bool(q_tail) and q_drift <= 0.1 * max(q_range, 1e-9) + 0.05,
            'duree_s': round(res['seconds'], 1),
        })
    bests = [r['meilleure_val_s'] for r in rows]
    rows.append({
        'graine': 'toutes',
        'meilleure_val_s': round(statistics.mean(bests), 2),
        'ecart_type_graines_s': round(statistics.pstdev(bests), 2) if len(bests) > 1 else 0.0,
        'gain_val_vs_fifo_pct': round(statistics.mean(r['gain_val_vs_fifo_pct'] for r in rows), 2),
        'gain_val_vs_consensus_pct': round(
            statistics.mean(r['gain_val_vs_consensus_pct'] for r in rows), 2),
        'gain_val_vs_greedy_pair_pct': round(
            statistics.mean(r['gain_val_vs_greedy_pair_pct'] for r in rows), 2),
        'val_fifo_s': round(fifo, 2), 'val_consensus_s': round(cons, 2),
        'val_greedy_pair_s': round(statistics.mean(refs['greedy_pair']), 2),
    })
    return rows


def write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def plot(results, refs, path, smooth=10):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib absent : pas de figure.')
        return
    n_ep = max(len(r['log']) for r in results)

    def stack(key):
        arr = np.full((len(results), n_ep), np.nan)
        for i, r in enumerate(results):
            xs = np.array([row[key] for row in r['log']], dtype=float)
            if smooth > 1:   # moyenne glissante en ignorant les NaN
                out = np.full_like(xs, np.nan)
                for j in range(len(xs)):
                    w = xs[max(0, j - smooth + 1):j + 1]
                    w = w[~np.isnan(w)]
                    out[j] = w.mean() if len(w) else np.nan
                xs = out
            arr[i, :len(xs)] = xs
        return arr

    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    ep = np.arange(1, n_ep + 1)
    for ax, (key, title) in zip(axs.ravel()[:3], [
            ('recompense_brute_moy', 'Recompense moyenne par decision (brute)'),
            ('perte_td', 'Perte TD (Huber)'), ('q_moy', 'Valeur Q moyenne (lot)')]):
        a = stack(key)
        with warnings.catch_warnings(), np.errstate(all='ignore'):
            # episodes sans pas d'apprentissage (avant warmup) : colonnes vides
            warnings.simplefilter('ignore', RuntimeWarning)
            m, s = np.nanmean(a, axis=0), np.nanstd(a, axis=0)
        ax.plot(ep, m, color='C0')
        ax.fill_between(ep, m - s, m + s, color='C0', alpha=0.25)
        ax.set_title(f'{title}, moy. glissante {smooth} ep.', fontsize=10)
        ax.set_xlabel('episode')
        ax.grid(alpha=0.3)
    ax = axs[1, 1]
    eps = sorted({v['episode'] for r in results for v in r['vals']})
    m, s = [], []
    for e in eps:
        xs = [v['val_drl2_s'] for r in results for v in r['vals'] if v['episode'] == e]
        m.append(np.mean(xs))
        s.append(np.std(xs))
    m, s = np.array(m), np.array(s)
    ax.plot(eps, m, 'o-', color='C0', label=f'DRL v2 ({len(results)} graines)')
    ax.fill_between(eps, m - s, m + s, color='C0', alpha=0.25)
    ax.axhline(np.mean(refs['fifo']), color='C1', ls='--', label='FIFO + plus proche')
    ax.axhline(np.mean(refs['consensus']), color='C2', ls='--', label='Consensus heuristique')
    ax.axhline(np.mean(refs['greedy_pair']), color='C3', ls=':',
               label='greedy_pair (couple de cout min., sans apprentissage)')
    ax.set_title('Validation : temps de traitement moyen (s), scenarios fixes', fontsize=10)
    ax.set_xlabel('episode')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f'Figure : {path}')


def main(argv=None):
    args = parse_args(argv)
    import torch
    torch.set_num_threads(max(1, args.threads))
    os.makedirs(args.out_dir, exist_ok=True)
    val_sc = val_scenarios(args.val_tasks)
    print(f'Validation : {len(val_sc)} scenarios fixes ; '
          'references FIFO, consensus, greedy_pair ...')
    refs = {m: evaluate(m, val_sc) for m in ('fifo', 'consensus', 'greedy_pair')}
    print(f'  FIFO {statistics.mean(refs["fifo"]):.2f} s, '
          f'consensus {statistics.mean(refs["consensus"]):.2f} s, '
          f'greedy_pair {statistics.mean(refs["greedy_pair"]):.2f} s')
    t0 = time.time()
    results = []
    for k in range(args.seeds):
        print(f'Graine {args.seed_base + k} ({args.episodes} episodes max, '
              f'{"Double " if args.double else ""}DQN)')
        results.append(train_seed(k, args, val_sc, refs, args.out_dir))

    write_csv(os.path.join(args.out_dir, 'training_log_v2.csv'),
              [row for r in results for row in r['log']])
    write_csv(os.path.join(args.out_dir, 'validation_v2.csv'),
              [row for r in results for row in r['vals']])
    table = indicators(results, refs)
    write_csv(os.path.join(args.out_dir, 'indicators_v2.csv'), table)
    best = min(results, key=lambda r: r['best'])
    best_path = os.path.join(args.out_dir, 'drl2_best.pt')
    import shutil
    shutil.copyfile(best['path'], best_path)
    plot(results, refs, os.path.join(args.out_dir, 'training_curves_v2.png'))

    print('\nIndicateurs (validation = temps de traitement moyen, plus bas = meilleur) :')
    for r in table:
        print('  ' + ', '.join(f'{k}={v}' for k, v in r.items()))
    print(f'\nMeilleur modele : {os.path.abspath(best_path)} (graine {best["seed"]}, '
          f'validation {best["best"]:.2f} s)')
    print(f'Duree totale : {time.time() - t0:.0f} s')


if __name__ == '__main__':
    main()
