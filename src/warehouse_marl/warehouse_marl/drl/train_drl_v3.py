"""
train_drl_v3.py
---------------
Entrainement du DRL v3 (Q residuel sur greedy_pair, drl/residual_dqn.py) sur
drl/env_v3.py : recompense sur le temps de service mesure, reference de
centrage figee, entrepots de 15 a 150 racks et 3 a 20 robots, robots
heterogenes, demande de Zipf, blocages longs.

    ros2 run warehouse_marl train_drl_v3 --episodes 1000 --seeds 5 --workers 3 --out-dir drl_v3
    python3 -m warehouse_marl.drl.train_drl_v3 --episodes 30 --seeds 2 --val-every 10  # essai

La validation (scenarios FIXES) a lieu a l'episode 0 (correction nulle =
greedy_pair) puis tous les --val-every episodes ; le meilleur modele de
chaque graine est conserve, episode 0 compris.

Sorties (--out-dir) : drl3_seed<k>.pt, drl3_best.pt, training_log_v3.csv,
validation_v3.csv, indicators_v3.csv, training_curves_v3.png.
"""

from __future__ import annotations

import argparse
import csv
import math
import multiprocessing as mp
import os
import random
import shutil
import statistics
import time
import warnings
from typing import Dict, List

import numpy as np

from warehouse_marl.drl.env_v2 import make_benchmark
from warehouse_marl.drl.env_v3 import AllocationEnvV3, greedy_reward_center

REFERENCES = ('fifo', 'consensus', 'greedy_pair', 'greedy_time')

# Scenarios FIXES de validation (graines distinctes de l'entrainement).
VAL_CONFIGS = [
    dict(dims=(5, 3), robots=3, rho=0.9),
    dict(dims=(8, 5), robots=6, rho=0.75, skew=1.0, speeds=(0.3, 0.5, 0.7),
         block_rate=1 / 60, block_min=60.0, block_max=300.0),
    dict(dims=(8, 5), robots=6, rho=0.9, skew=1.5, speeds=(0.25, 0.5, 0.75),
         block_rate=2 / 60, block_min=60.0, block_max=300.0),
    dict(dims=(8, 5), robots=6, rho=0.9, skew=1.5, speeds=(0.25, 0.5, 0.75)),
    dict(dims=(10, 8), robots=10, rho=0.7, skew=0.8, speeds=(0.4, 0.5, 0.6)),
    dict(dims=(15, 10), robots=20, rho=0.7, speeds=(0.3, 0.5, 0.7), block_rate=1 / 60),
]


def val_scenarios(n_tasks: int, n_seeds: int = 2) -> List[Dict]:
    return [dict({'block_rate': 0.0}, **cfg, tasks=n_tasks, seed=700_003 + 7919 * i + 104_729 * s)
            for i, cfg in enumerate(VAL_CONFIGS) for s in range(n_seeds)]


def evaluate(method: str, scenarios, agent=None) -> List[float]:
    return [make_benchmark(method, sc, agent3=agent).run()['temps_traitement_moy_s']
            for sc in scenarios]


def parse_args(argv=None):
    p = argparse.ArgumentParser(description='Entrainement DQN v3 (Q residuel sur greedy_pair)')
    p.add_argument('--episodes', type=int, default=1000)
    p.add_argument('--seeds', type=int, default=5)
    p.add_argument('--seed-base', type=int, default=0)
    p.add_argument('--workers', type=int, default=1, help='graines entrainees en parallele')
    p.add_argument('--tasks', type=int, default=80, help='taches par episode')
    p.add_argument('--val-every', type=int, default=50)
    p.add_argument('--val-tasks', type=int, default=100)
    p.add_argument('--patience', type=int, default=0,
                   help='validations sans amelioration avant arret (0 = jamais)')
    p.add_argument('--center-episodes', type=int, default=40,
                   help='episodes greedy_pair pour la reference de centrage figee')
    p.add_argument('--gamma', type=float, default=0.95)
    p.add_argument('--lr', type=float, default=3e-4)
    p.add_argument('--hidden', type=int, default=64)
    p.add_argument('--beta', type=float, default=1.0, help='poids du terme -cout/diametre')
    p.add_argument('--tau', type=float, default=0.005, help='mise a jour douce du reseau cible')
    p.add_argument('--batch-size', type=int, default=64)
    p.add_argument('--buffer', type=int, default=100_000)
    p.add_argument('--warmup', type=int, default=1000)
    p.add_argument('--eps-start', type=float, default=0.5)
    p.add_argument('--eps-end', type=float, default=0.05)
    p.add_argument('--eps-decay-frac', type=float, default=0.6)
    p.add_argument('--failure-penalty', type=float, default=120.0)
    p.add_argument('--late-penalty', type=float, default=0.0,
                   help='penalite (s) par tache finie apres son delai (0 = temps seul)')
    p.add_argument('--double', dest='double', action='store_true', default=True)
    p.add_argument('--no-double', dest='double', action='store_false')
    p.add_argument('--out-dir', default='drl_v3')
    return p.parse_args(argv)


def _gains(v, refs):
    return {f'gain_vs_{m}_pct': 100 * statistics.mean((r - x) / r for x, r in zip(v, refs[m]))
            for m in REFERENCES}


def train_seed(job) -> Dict:
    k, args, val_sc, refs, center = job
    import torch
    torch.set_num_threads(1)
    from warehouse_marl.drl.residual_dqn import ResidualDQN

    seed = args.seed_base + k
    random.seed(seed)
    np.random.seed(seed)
    env = AllocationEnvV3(seed=20_000 + seed, n_tasks=args.tasks, reward_center=center,
                          failure_penalty_s=args.failure_penalty,
                          late_penalty_s=args.late_penalty)
    agent = ResidualDQN(hidden=args.hidden, lr=args.lr, gamma=args.gamma, double=args.double,
                        buffer_size=args.buffer, batch_size=args.batch_size, warmup=args.warmup,
                        seed=seed, beta=args.beta, tau=args.tau)
    agent.meta = {'reward_norm_s': 60.0, 'reward_center': center, 'train_seed': seed,
                  'failure_penalty_s': args.failure_penalty, 'late_penalty_s': args.late_penalty}
    path = os.path.join(args.out_dir, f'drl3_seed{seed}.pt')
    log, vals, t0 = [], [], time.time()

    def validate(ep):
        agent.q.eval()
        v = evaluate('drl3_direct', val_sc, agent)
        agent.q.train()
        row = {'graine': seed, 'episode': ep, 'val_drl3_s': statistics.mean(v)}
        row.update({f'val_{m}_s': statistics.mean(refs[m]) for m in REFERENCES})
        row.update(_gains(v, refs))
        vals.append(row)
        return row

    best = validate(0)
    agent.save(path, val_temps_traitement_s=best['val_drl3_s'], val_episode=0)
    best_ep, since = 0, 0
    print(f'  [graine {seed}] ep    0  val={best["val_drl3_s"]:6.2f} s  '
          f'vs greedy_pair {best["gain_vs_greedy_pair_pct"]:+.2f} %', flush=True)
    decay = max(1, int(args.eps_decay_frac * args.episodes))
    for ep in range(1, args.episodes + 1):
        eps = max(args.eps_end, args.eps_start - (args.eps_start - args.eps_end) * (ep - 1) / decay)
        obs, info = env.reset()
        done = info['done']
        rewards, raws, losses, qs, grads, corrs, metrics = [], [], [], [], [], [], {}
        while not done:
            a = agent.act(obs, eps)
            obs, done, inf = env.step(a)
            for feat, r, nxt, term, raw in inf['transitions']:
                agent.remember(feat, r, nxt, term)
                rewards.append(r)
                raws.append(raw)
                st = agent.train_step()
                if st:
                    losses.append(st['loss'])
                    qs.append(st['q'])
                    grads.append(st['grad'])
                    corrs.append(st['correction'])
            metrics = inf.get('metrics', metrics)
        sc = env.scenario

        def mean(xs):
            return statistics.mean(xs) if xs else math.nan
        row = {'graine': seed, 'episode': ep, 'epsilon': round(eps, 4),
               'robots': sc['robots'], 'racks': sc['dims'][0] * sc['dims'][1], 'rho': sc['rho'],
               'vitesses': '/'.join(map(str, sc['speeds'])) if sc['speeds'] else 'uniforme',
               'skew': sc['skew'], 'blocages_min': round(60 * sc['block_rate'], 2),
               'decisions': len(rewards), 'recompense_moy': mean(rewards),
               'recompense_brute_moy': mean(raws), 'perte_td': mean(losses), 'q_moy': mean(qs),
               'norme_gradient': mean(grads), 'correction_abs_moy': mean(corrs),
               'temps_traitement_s': metrics.get('temps_traitement_moy_s', math.nan),
               'retard_pct': metrics.get('taches_en_retard_pct', math.nan)}
        log.append(row)
        if ep % args.val_every == 0 or ep == args.episodes:
            v = validate(ep)
            mark = ''
            if v['val_drl3_s'] < best['val_drl3_s']:
                best, best_ep, since = v, ep, 0
                agent.save(path, val_temps_traitement_s=v['val_drl3_s'], val_episode=ep)
                mark = ' *meilleur*'
            else:
                since += 1
            print(f'  [graine {seed}] ep {ep:4d}  eps={eps:.2f}  perte={row["perte_td"]:.4f}  '
                  f'Q={row["q_moy"]:+.3f}  |corr|={row["correction_abs_moy"]:.3f}  '
                  f'val={v["val_drl3_s"]:6.2f} s  vs greedy_pair '
                  f'{v["gain_vs_greedy_pair_pct"]:+.2f} %  vs greedy_time '
                  f'{v["gain_vs_greedy_time_pct"]:+.2f} %  ({time.time() - t0:.0f} s){mark}',
                  flush=True)
            if args.patience and since >= args.patience:
                print(f'  [graine {seed}] arret anticipe a l episode {ep}')
                break
    return {'seed': seed, 'log': log, 'vals': vals, 'best': best, 'best_ep': best_ep,
            'path': path, 'seconds': time.time() - t0}


# ---------------------------------------------------------------------- #
def smooth(xs, w=20):
    xs = np.asarray(xs, dtype=float)
    out = np.full_like(xs, np.nan)
    for j in range(len(xs)):
        win = xs[max(0, j - w + 1):j + 1]
        win = win[~np.isnan(win)]
        out[j] = win.mean() if len(win) else np.nan
    return out


def q_stability(qs):
    """Critere fixe AVANT les resultats : Q lissee sur 20 episodes ;
    stable si |moyenne des 20 % derniers episodes - moyenne des 20 %
    precedents| <= 0.05 + 10 % de l'amplitude de Q lissee sur tout
    l'entrainement."""
    q = smooth(qs)
    q = q[~np.isnan(q)]
    if len(q) < 10:
        return math.nan, math.nan, False
    n = max(2, len(q) // 5)
    drift = abs(q[-n:].mean() - q[-2 * n:-n].mean())
    amp = q.max() - q.min()
    return float(drift), float(amp), bool(drift <= 0.05 + 0.1 * amp)


def indicators(results, refs) -> List[Dict]:
    rows = []
    for res in results:
        vals = [v['val_drl3_s'] for v in res['vals']]
        eps = [v['episode'] for v in res['vals']]
        final = vals[-1]
        conv = next((eps[i] for i in range(len(vals))
                     if all(abs(x - final) <= 0.05 * final for x in vals[i:])), math.nan)
        losses = [r['perte_td'] for r in res['log'] if not math.isnan(r['perte_td'])]
        n10 = max(1, len(losses) // 10)
        drift, amp, stable = q_stability([r['q_moy'] for r in res['log']])
        b = res['best']
        rows.append({
            'graine': res['seed'],
            'val_episode0_s': round(res['vals'][0]['val_drl3_s'], 3),
            'meilleure_val_s': round(b['val_drl3_s'], 3), 'episode_meilleur': res['best_ep'],
            'val_finale_s': round(final, 3),
            **{f'gain_val_vs_{m}_pct': round(b[f'gain_vs_{m}_pct'], 2) for m in REFERENCES},
            'gain_final_vs_greedy_pair_pct': round(res['vals'][-1]['gain_vs_greedy_pair_pct'], 2),
            'episode_convergence_5pct': conv,
            'perte_debut': round(statistics.mean(losses[:n10]), 4) if losses else math.nan,
            'perte_fin': round(statistics.mean(losses[-n10:]), 4) if losses else math.nan,
            'q_derive_20pct': round(drift, 4), 'q_amplitude': round(amp, 4), 'q_stable': stable,
            'duree_s': round(res['seconds'], 1),
        })
    bests = [r['meilleure_val_s'] for r in rows]
    rows.append({
        'graine': 'toutes', 'meilleure_val_s': round(statistics.mean(bests), 3),
        'ecart_type_graines_s': round(statistics.pstdev(bests), 3),
        **{f'gain_val_vs_{m}_pct': round(statistics.mean(r[f'gain_val_vs_{m}_pct'] for r in rows), 2)
           for m in REFERENCES},
        'gain_final_vs_greedy_pair_pct': round(
            statistics.mean(r['gain_final_vs_greedy_pair_pct'] for r in rows), 2),
        'q_stable_toutes_graines': all(r['q_stable'] for r in rows),
        **{f'val_{m}_s': round(statistics.mean(refs[m]), 3) for m in REFERENCES},
    })
    return rows


def write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def plot(results, refs, path):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib absent : pas de figure.')
        return
    n_ep = max(len(r['log']) for r in results)
    fig, axs = plt.subplots(2, 2, figsize=(13, 8.5))
    ep = np.arange(1, n_ep + 1)
    for ax, (key, title) in zip(axs.ravel()[:3], [
            ('perte_td', 'Perte TD (Huber)'), ('q_moy', 'Valeur Q moyenne (lot)'),
            ('correction_abs_moy', '|correction| moyenne (ecart a greedy_pair)')]):
        arr = np.full((len(results), n_ep), np.nan)
        for i, r in enumerate(results):
            xs = smooth([row[key] for row in r['log']])
            arr[i, :len(xs)] = xs
        with warnings.catch_warnings(), np.errstate(all='ignore'):
            warnings.simplefilter('ignore', RuntimeWarning)
            m, s = np.nanmean(arr, axis=0), np.nanstd(arr, axis=0)
        ax.plot(ep, m, color='C0')
        ax.fill_between(ep, m - s, m + s, color='C0', alpha=0.25)
        ax.set_title(f'{title}, moy. glissante 20 ep., {len(results)} graines', fontsize=10)
        ax.set_xlabel('episode')
        ax.grid(alpha=0.3)
    ax = axs[1, 1]
    eps = sorted({v['episode'] for r in results for v in r['vals']})
    m = np.array([np.mean([v['val_drl3_s'] for r in results for v in r['vals']
                           if v['episode'] == e]) for e in eps])
    s = np.array([np.std([v['val_drl3_s'] for r in results for v in r['vals']
                          if v['episode'] == e]) for e in eps])
    ax.plot(eps, m, 'o-', color='C0', ms=3, label='DRL v3 (moy. +/- e.-t.)')
    ax.fill_between(eps, m - s, m + s, color='C0', alpha=0.25)
    for ref, col, ls, lab in (('fifo', 'C1', '--', 'FIFO'), ('consensus', 'C2', '--', 'Consensus'),
                              ('greedy_pair', 'C3', ':', 'greedy_pair'),
                              ('greedy_time', 'C4', ':', 'greedy_time')):
        ax.axhline(np.mean(refs[ref]), color=col, ls=ls, label=lab)
    ax.set_title('Validation (episode 0 = greedy_pair) : temps de traitement moyen (s)',
                 fontsize=10)
    ax.set_xlabel('episode')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f'Figure : {path}')


def main(argv=None):
    args = parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    t0 = time.time()
    val_sc = val_scenarios(args.val_tasks)
    print(f'Validation : {len(val_sc)} scenarios fixes ; references {", ".join(REFERENCES)} ...')
    refs = {m: evaluate(m, val_sc) for m in REFERENCES}
    print('  ' + ', '.join(f'{m} {statistics.mean(refs[m]):.2f} s' for m in REFERENCES))
    center = greedy_reward_center(seed=999, episodes=args.center_episodes, n_tasks=args.tasks)
    print(f'Reference de centrage figee (greedy_pair, {args.center_episodes} episodes) : '
          f'{center:.4f}')
    jobs = [(k, args, val_sc, refs, center) for k in range(args.seeds)]
    if args.workers > 1:
        with mp.get_context('fork').Pool(min(args.workers, args.seeds)) as pool:
            results = pool.map(train_seed, jobs)
    else:
        results = [train_seed(j) for j in jobs]

    write_csv(os.path.join(args.out_dir, 'training_log_v3.csv'),
              [row for r in results for row in r['log']])
    write_csv(os.path.join(args.out_dir, 'validation_v3.csv'),
              [row for r in results for row in r['vals']])
    table = indicators(results, refs)
    write_csv(os.path.join(args.out_dir, 'indicators_v3.csv'), table)
    best = min(results, key=lambda r: r['best']['val_drl3_s'])
    shutil.copyfile(best['path'], os.path.join(args.out_dir, 'drl3_best.pt'))
    plot(results, refs, os.path.join(args.out_dir, 'training_curves_v3.png'))
    print('\nIndicateurs (validation = temps de traitement moyen, plus bas = meilleur) :')
    for r in table:
        print('  ' + ', '.join(f'{k}={v}' for k, v in r.items()))
    print(f'\nMeilleur modele : {os.path.abspath(os.path.join(args.out_dir, "drl3_best.pt"))} '
          f'(graine {best["seed"]}, episode {best["best_ep"]}, '
          f'validation {best["best"]["val_drl3_s"]:.3f} s)')
    print(f'Duree totale : {time.time() - t0:.0f} s')


if __name__ == '__main__':
    main()
