"""
benchmark_v4.py
---------------
Essais de TEST du protocole v4 (PROTOCOLE_V4.md, sections 6 et 7).

    python -m warehouse_marl.benchmark_v4 --step route --model best.pt --out-dir DIR
    python -m warehouse_marl.benchmark_v4 --step idle  --model best.pt --out-dir DIR
    python -m warehouse_marl.benchmark_v4 --step stats --out-dir DIR   # statistiques seules

Graines de test : 1000 k + 7, k = 0..19 ; vagues de TEST de Footwear (k-ieme de
20 fenetres regulierement reparties). Sorties : essais_<step>.csv,
principal_<step>.csv (DRL contre la meilleure heuristique, Wilcoxon + Holm),
secondaire_<step>.csv, figures fig_<step>_<experience>.png.
"""

from __future__ import annotations

import argparse
import csv
import math
import multiprocessing as mp
import os
import statistics
import time

from warehouse_marl.allocation_benchmark import (
    STRUCTURED_LEVELS, bootstrap_ci, build_grid_warehouse, mean_service_time, wilcoxon_p)

N_TEST = 20
TEST_SEED = [1000 * k + 7 for k in range(N_TEST)]
N_TASKS = 150
SPEED, PICK = 0.5, 10.0
PRIMARY = 'temps_traitement_moy_s'
SECONDARY = ('temps_trajet_moy_s', 'taches_echouees', 'conflits_aretes_pour_100_taches',
             'attente_noeud_par_tache_s', 'approche_moy_s')

DATASET = [
    dict(label='15 racks, 3 r., rho=0.7', robots=3, dims=(5, 3), rho=0.7, footwear=True),
    dict(label='15 racks, 3 r., rho=0.9', robots=3, dims=(5, 3), rho=0.9, footwear=True),
    dict(label='40 racks, 6 r., vit. var.', robots=6, dims=(8, 5), rho=0.9,
         speeds=(0.3, 0.5, 0.7), footwear=True),
    dict(label='150 racks, 20 r., rho=0.7', robots=20, dims=(15, 10), rho=0.7, footwear=True),
]
STEPS = {
    'route': dict(
        methods=('dijkstra_statique', 'dijkstra_dynamique', 'drl_route'),
        drl='drl_route', allocations=('greedy_pair', 'consensus'),
        experiments=[
            ('blocages', [dict(label=f'{x} blocage/min', robots=3, dims=(5, 3), rho=0.7,
                               block_rate=x / 60.0) for x in (0, 1, 3, 6)]),
            ('taille', [dict(label=f'{R} robots, {d[0] * d[1]} racks', robots=R, dims=d,
                             rho=0.7, block_rate=1 / 60.0)
                        for R, d in ((3, (5, 3)), (6, (8, 5)), (10, (10, 8)), (20, (15, 10)))]),
            ('dataset', DATASET)]),
    'idle': dict(
        methods=('rester_sur_place', 'retour_au_depot', 'centre_de_demande', 'drl_idle'),
        drl='drl_idle', allocations=('greedy_pair', 'greedy_time'),
        experiments=[
            ('dataset', DATASET),
            ('zipf', [dict(label=f"{lv['label']} (s={lv['skew']})", robots=6, dims=(8, 5),
                           rho=lv['rho'], skew=lv['skew'], speeds=lv['speeds'],
                           block_rate=lv['block_rate'], block_min=60.0, block_max=300.0)
                      for lv in STRUCTURED_LEVELS])]),
}

_AGENT = None


def _init_worker(model_path, kind):
    global _AGENT
    import torch
    torch.set_num_threads(1)
    if model_path:
        from warehouse_marl.drl.v4_dqn import load_v4_model
        _AGENT = load_v4_model(model_path, kind)


def run_one(job):
    from warehouse_marl.drl.v4_sim import BenchmarkV4
    step, exp, cfg, alloc, method, k = job
    dims, R = cfg['dims'], cfg['robots']
    speeds = cfg.get('speeds')
    mean_speed = statistics.mean(speeds) if speeds else SPEED
    g = build_grid_warehouse(*dims)
    targets, demand = None, None
    if cfg.get('footwear'):
        from warehouse_marl.dataset_footwear import load_dataset
        ds = load_dataset()
        service = ds.service_time(g, mean_speed, PICK)
        targets = ds.targets(g, 'test', ds.evenly_spaced_start('test', N_TASKS, k, N_TEST),
                             N_TASKS)
        if step == 'idle':
            from warehouse_marl.drl.train_v4 import train_fit_demand
            demand = train_fit_demand(g)
    else:
        service = mean_service_time(g, mean_speed, PICK)
    rate = cfg['rho'] * R / service
    kw = {}
    if step == 'route':
        kw.update(route_mode=method, route_agent=_AGENT if method == 'drl_route' else None)
    else:
        kw.update(idle_mode=method, idle_agent=_AGENT if method == 'drl_idle' else None,
                  demand_prior=demand)
    b = BenchmarkV4(alloc, g, R, rate, N_TASKS, seed=TEST_SEED[k], speed=SPEED, pick_time=PICK,
                    speeds=speeds, block_rate=cfg.get('block_rate', 0.0),
                    block_min=cfg.get('block_min', 30.0), block_max=cfg.get('block_max', 120.0),
                    demand_skew=cfg.get('skew', 0.0), targets=targets, **kw)
    t0 = time.perf_counter()
    m = b.run()
    m.update(etape=step, experience=exp, condition=cfg['label'], allocation=alloc,
             methode=method, graine=k, graine_simulation=TEST_SEED[k], robots=R,
             racks=dims[0] * dims[1], rho=cfg['rho'],
             blocages_par_min=round(cfg.get('block_rate', 0.0) * 60, 3),
             taches='footwear (test)' if cfg.get('footwear') else
             ('zipf' if cfg.get('skew') else 'synthetiques uniformes'),
             duree_calcul_s=round(time.perf_counter() - t0, 3))
    return m


def write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def read_csv(path):
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            try:
                r[k] = float(v)
            except (TypeError, ValueError):
                pass
        r['graine'] = int(r['graine'])
    return rows


def holm(pvals):
    """p ajustees de Holm (meme ordre que l'entree ; NaN -> 1)."""
    p = [1.0 if (x is None or math.isnan(x)) else x for x in pvals]
    m = len(p)
    order = sorted(range(m), key=lambda i: p[i])
    adj, running = [0.0] * m, 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[i]))
        adj[i] = running
    return adj


def _groups(rows):
    out = {}
    for r in rows:
        out.setdefault((r['experience'], r['condition'], r['allocation']), {}) \
           .setdefault(r['methode'], {})[r['graine']] = r
    return out


def _vals(by_seed, metric, seeds):
    return [float(by_seed[s][metric]) for s in seeds]


def _nanmean(xs):
    xs = [x for x in xs if not math.isnan(x)]
    return statistics.mean(xs) if xs else math.nan


def principal(rows, step):
    spec = STEPS[step]
    drl = spec['drl']
    heur = [m for m in spec['methods'] if m != drl]
    out = []
    for (exp, cond, alloc), by_m in _groups(rows).items():
        if drl not in by_m:
            continue
        means = {m: _nanmean([float(r[PRIMARY]) for r in by_m[m].values()]) for m in heur}
        best = min(means, key=lambda m: means[m])
        seeds = sorted(set(by_m[drl]) & set(by_m[best]))
        a, b = _vals(by_m[drl], PRIMARY, seeds), _vals(by_m[best], PRIMARY, seeds)
        diffs = [x - y for x, y in zip(a, b)]
        (alo, ahi), (blo, bhi), (dlo, dhi) = bootstrap_ci(a), bootstrap_ci(b), bootstrap_ci(diffs)
        fa = sum(float(by_m[drl][s]['taches_echouees']) for s in seeds)
        fb = sum(float(by_m[best][s]['taches_echouees']) for s in seeds)
        out.append({
            'etape': step, 'experience': exp, 'condition': cond, 'allocation': alloc,
            'methode_drl': drl, 'meilleure_heuristique': best, 'n_essais': len(seeds),
            'drl_moyenne_s': round(statistics.mean(a), 3), 'drl_ic95_bas': round(alo, 3),
            'drl_ic95_haut': round(ahi, 3),
            'heur_moyenne_s': round(statistics.mean(b), 3), 'heur_ic95_bas': round(blo, 3),
            'heur_ic95_haut': round(bhi, 3),
            'ecart_moyen_s': round(statistics.mean(diffs), 3),
            'ecart_ic95_bas': round(dlo, 3), 'ecart_ic95_haut': round(dhi, 3),
            'gain_pct': round(100 * (statistics.mean(b) - statistics.mean(a)) / statistics.mean(b), 2),
            'drl_gagne': f'{sum(x < y for x, y in zip(a, b))}/{len(seeds)}',
            'egalites': sum(abs(x - y) < 1e-9 for x, y in zip(a, b)),
            'echecs_drl': int(fa), 'echecs_heur': int(fb),
            'p_wilcoxon': wilcoxon_p(a, b),
            **{f'moyenne_{m}': round(means[m], 3) for m in heur},
        })
    adj = holm([r['p_wilcoxon'] for r in out])
    for r, pa in zip(out, adj):
        r['p_holm'] = pa
        sig = pa < 0.05
        if sig and r['ecart_moyen_s'] < 0 and r['echecs_drl'] <= r['echecs_heur']:
            r['conclusion'] = 'DRL meilleur (significatif)'
        elif sig and r['ecart_moyen_s'] < 0:
            r['conclusion'] = 'DRL plus rapide mais plus d echecs (non retenu)'
        elif sig:
            r['conclusion'] = 'heuristique meilleure (significatif)'
        else:
            r['conclusion'] = 'pas de difference significative'
        r['p_wilcoxon'] = round(r['p_wilcoxon'], 6)
        r['p_holm'] = round(pa, 6)
    return out


def secondaire(rows, step):
    spec = STEPS[step]
    drl = spec['drl']
    heur = [m for m in spec['methods'] if m != drl]
    out = []
    metrics = (PRIMARY,) + SECONDARY
    for metric in metrics:
        fam = []
        for (exp, cond, alloc), by_m in _groups(rows).items():
            if drl not in by_m:
                continue
            for h in heur:
                seeds = sorted(set(by_m[drl]) & set(by_m[h]))
                a, b = _vals(by_m[drl], metric, seeds), _vals(by_m[h], metric, seeds)
                if any(math.isnan(x) for x in a + b):
                    continue
                fam.append({'etape': step, 'metrique': metric, 'experience': exp,
                            'condition': cond, 'allocation': alloc, 'adversaire': h,
                            'drl_moyenne': round(statistics.mean(a), 4),
                            'adv_moyenne': round(statistics.mean(b), 4),
                            'ecart_moyen': round(statistics.mean(a) - statistics.mean(b), 4),
                            'p_wilcoxon': wilcoxon_p(a, b)})
        for r, pa in zip(fam, holm([r['p_wilcoxon'] for r in fam])):
            r['p_wilcoxon'] = round(r['p_wilcoxon'], 6)
            r['p_holm_famille'] = round(pa, 6)
        out += fam
    return out


def descriptive(rows, step):
    """Moyenne et IC 95 % de chaque methode, metrique, condition, allocation."""
    out = []
    metrics = (PRIMARY,) + SECONDARY + ('ms_par_decision_route', 'ms_par_decision_attente',
                                        'replis_dijkstra', 'attentes_choisies')
    for (exp, cond, alloc), by_m in _groups(rows).items():
        for m, by_s in by_m.items():
            for metric in metrics:
                xs = [float(r[metric]) for r in by_s.values() if metric in r]
                xs = [x for x in xs if not math.isnan(x)]
                if not xs:
                    continue
                lo, hi = bootstrap_ci(xs)
                out.append({'etape': step, 'experience': exp, 'condition': cond,
                            'allocation': alloc, 'methode': m, 'metrique': metric,
                            'n': len(xs), 'moyenne': round(statistics.mean(xs), 4),
                            'ic95_bas': round(lo, 4), 'ic95_haut': round(hi, 4)})
    return out


def figures(rows, step, out_dir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'axes.grid': True, 'grid.alpha': 0.3, 'axes.spines.top': False,
                         'axes.spines.right': False})
    spec = STEPS[step]
    methods = spec['methods']
    colors = dict(zip(methods, ('#8c8c8c', '#4c72b0', '#dd8452', '#c44e52')))
    if step == 'idle':
        colors = dict(zip(methods, ('#8c8c8c', '#937860', '#4c72b0', '#c44e52')))
    metrics = [(PRIMARY, 'Temps de traitement moyen (s)'),
               ('temps_trajet_moy_s', 'Temps de trajet moyen (s)'),
               ('taches_echouees', 'Taches echouees (par essai)'),
               ('conflits_aretes_pour_100_taches', 'Conflits d aretes / 100 taches'),
               ('attente_noeud_par_tache_s', 'Attente aux noeuds (s / tache)')]
    if step == 'idle':
        metrics[3] = ('approche_moy_s', 'Approche moyenne (s)')
    paths = []
    for exp, _ in spec['experiments']:
        sub = [r for r in rows if r['experience'] == exp]
        conds = list(dict.fromkeys(r['condition'] for r in sub))
        fig, axs = plt.subplots(len(spec['allocations']), len(metrics),
                                figsize=(4.2 * len(metrics), 3.6 * len(spec['allocations'])),
                                squeeze=False)
        for i, alloc in enumerate(spec['allocations']):
            for j, (metric, lab) in enumerate(metrics):
                ax = axs[i][j]
                w = 0.8 / len(methods)
                for mi, m in enumerate(methods):
                    ys, lo, hi = [], [], []
                    for c in conds:
                        xs = [float(r[metric]) for r in sub if r['condition'] == c
                              and r['allocation'] == alloc and r['methode'] == m]
                        xs = [x for x in xs if not math.isnan(x)]
                        if xs:
                            mu = statistics.mean(xs)
                            a, b = bootstrap_ci(xs)
                            ys.append(mu); lo.append(mu - a); hi.append(b - mu)
                        else:
                            ys.append(math.nan); lo.append(0); hi.append(0)
                    xpos = [k + (mi - (len(methods) - 1) / 2) * w for k in range(len(conds))]
                    ax.bar(xpos, ys, w, yerr=[lo, hi], capsize=2, color=colors[m], label=m)
                ax.set_xticks(range(len(conds)))
                ax.set_xticklabels(conds, fontsize=7, rotation=20, ha='right')
                ax.set_title(f'{lab}\nallocation {alloc}', fontsize=9)
        axs[0][0].legend(fontsize=7)
        fig.suptitle(f'Etape {step}, experience {exp} : moyenne et IC 95 % bootstrap '
                     f'({N_TEST} graines de test)', fontsize=11)
        fig.tight_layout()
        path = os.path.join(out_dir, f'fig_{step}_{exp}.png')
        fig.savefig(path, dpi=130)
        plt.close(fig)
        paths.append(path)
    return paths


def figure_ecarts(prin, step, out_dir):
    """Ecart apparie DRL - meilleure heuristique (s), IC 95 % bootstrap,
    une ligne par (condition, allocation) ; etoile = significatif apres Holm."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    n = len(prin)
    fig, ax = plt.subplots(figsize=(8.5, 0.32 * n + 1.6))
    for i, r in enumerate(prin):
        y = n - 1 - i
        col = '#2a9d55' if r['ecart_moyen_s'] < 0 else '#c44e52'
        if r['p_holm'] >= 0.05:
            col = '#7f7f7f'
        ax.errorbar(r['ecart_moyen_s'], y,
                    xerr=[[r['ecart_moyen_s'] - r['ecart_ic95_bas']],
                          [r['ecart_ic95_haut'] - r['ecart_moyen_s']]],
                    fmt='o', color=col, capsize=3)
        if r['p_holm'] < 0.05:
            ax.annotate('*', (r['ecart_ic95_haut'], y), xytext=(4, -4),
                        textcoords='offset points', fontsize=12, color=col)
    ax.axvline(0, color='k', lw=0.8)
    ax.set_yticks(range(n))
    ax.set_yticklabels([f"{r['experience']} | {r['condition']} | {r['allocation']} "
                        f"(vs {r['meilleure_heuristique']})" for r in reversed(prin)], fontsize=7)
    ax.set_xlabel('Ecart de temps de traitement moyen, DRL - meilleure heuristique (s)\n'
                  '< 0 : DRL plus rapide ; gris : non significatif (Holm, alpha = 0,05)')
    ax.set_title(f'Etape {step} : ecart apparie et IC 95 % bootstrap ({N_TEST} graines)',
                 fontsize=10)
    fig.tight_layout()
    path = os.path.join(out_dir, f'fig_{step}_ecarts.png')
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def main(argv=None):
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    p = argparse.ArgumentParser()
    p.add_argument('--step', choices=['route', 'idle'], required=True)
    p.add_argument('--model', default='')
    p.add_argument('--out-dir', required=True)
    p.add_argument('--workers', type=int, default=1)
    p.add_argument('--stats-only', action='store_true')
    args = p.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    step = args.step
    spec = STEPS[step]
    path = os.path.join(args.out_dir, f'essais_{step}.csv')
    if not args.stats_only:
        jobs = [(step, exp, cfg, alloc, m, k) for exp, cfgs in spec['experiments']
                for cfg in cfgs for alloc in spec['allocations'] for m in spec['methods']
                for k in range(N_TEST)]
        print(f'{len(jobs)} essais de test ({step}), modele {args.model}', flush=True)
        t0 = time.time()
        kind = 'route' if step == 'route' else 'idle'
        if args.workers > 1:
            with mp.get_context('fork').Pool(args.workers, _init_worker,
                                             (args.model, kind)) as pool:
                rows = pool.map(run_one, jobs, chunksize=4)
        else:
            _init_worker(args.model, kind)
            rows = [run_one(j) for j in jobs]
        for r in rows:
            r['modele'] = os.path.basename(args.model) if r['methode'].startswith('drl') else ''
        write_csv(path, rows)
        print(f'{path} ({time.time() - t0:.0f} s)', flush=True)
    rows = read_csv(path)
    prin = principal(rows, step)
    write_csv(os.path.join(args.out_dir, f'principal_{step}.csv'), prin)
    write_csv(os.path.join(args.out_dir, f'secondaire_{step}.csv'), secondaire(rows, step))
    write_csv(os.path.join(args.out_dir, f'descriptif_{step}.csv'), descriptive(rows, step))
    for r in prin:
        print(f"{r['experience']:9s} {r['condition']:28s} {r['allocation']:12s} "
              f"DRL {r['drl_moyenne_s']:7.2f} vs {r['meilleure_heuristique']:18s} "
              f"{r['heur_moyenne_s']:7.2f}  ecart {r['ecart_moyen_s']:+7.3f} "
              f"[{r['ecart_ic95_bas']:+.3f};{r['ecart_ic95_haut']:+.3f}]  {r['drl_gagne']:>5s}  "
              f"p={r['p_wilcoxon']:.4g} holm={r['p_holm']:.4g}  {r['conclusion']}")
    for f in figures(rows, step, args.out_dir) + [figure_ecarts(prin, step, args.out_dir)]:
        print('Figure :', f)


if __name__ == '__main__':
    main()
