"""
benchmark_v6.py
---------------
Essais de TEST du protocole v6 (PROTOCOLE_V6.md, sections 6 et 7).

    python -m warehouse_marl.benchmark_v6 --step idle6  --model selected_idle6.pt --out-dir DIR
    python -m warehouse_marl.benchmark_v6 --step route6 --model selected_route6.pt --out-dir DIR
    python -m warehouse_marl.benchmark_v6 --step alloc6 --model selected_alloc6.pt --out-dir DIR
    python -m warehouse_marl.benchmark_v6 --step idle6 --out-dir DIR --stats-only

Graines de test v6 : 2 000 003 + 1 013 k, k = 0..19 ; vagues de TEST de Footwear
(milieu du k-ieme de 20 intervalles). Sorties : essais_<step>.csv,
principal_<step>.csv (famille principale, Wilcoxon + Holm), secondaire_<step>.csv,
descriptif_<step>.csv, fig_<step>_<experience>_v6.png, fig_<step>_ecarts_v6.png.
"""

from __future__ import annotations

import argparse
import math
import multiprocessing as mp
import os
import statistics
import time

from warehouse_marl.allocation_benchmark import STRUCTURED_LEVELS, bootstrap_ci, wilcoxon_p
from warehouse_marl.benchmark_v4 import DATASET, _nanmean, holm, read_csv, write_csv
from warehouse_marl.drl.train_v6 import N_TEST6, ROUTE6_CONDITIONS, TEST6_SEEDS

N_TASKS = 150
PRIMARY = 'temps_traitement_moy_s'
V4_IDLE_MODEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             'models', 'selected_idle.pt')

ZIPF = [dict(label=f"{lv['label']} (s={lv['skew']})", robots=6, dims=(8, 5), rho=lv['rho'],
             skew=lv['skew'], speeds=lv['speeds'], block_rate=lv['block_rate'],
             block_min=60.0, block_max=300.0) for lv in STRUCTURED_LEVELS]

STEPS = {
    'idle6': dict(
        phase='A', drl='drl_idle6',
        competitors=('rester_sur_place', 'retour_au_depot', 'centre_de_demande'),
        descriptive=('couverture', 'drl_idle'), compare='best',
        allocations=('greedy_pair', 'greedy_time'),
        experiments=[('dataset', DATASET), ('zipf', ZIPF)],
        secondary=('approche_moy_s', 'taches_echouees', 'attente_attribution_moy_s')),
    'route6': dict(
        phase='B', drl='drl_route6',
        competitors=('dijkstra_statique', 'dijkstra_dynamique', 'dijkstra_congestion'),
        descriptive=(), compare='each', allocations=('greedy_pair',),
        experiments=[('congestion', ROUTE6_CONDITIONS)],
        secondary=('temps_trajet_moy_s', 'attente_file_par_tache_s', 'taches_echouees',
                   'distance_par_tache_m')),
    'alloc6': dict(
        phase='C', drl='drl_alloc6', competitors=('greedy_pair', 'greedy_time'),
        descriptive=(), compare='best', allocations=('-',),
        experiments=[('dataset', DATASET)],
        secondary=('attente_attribution_moy_s', 'approche_moy_s', 'taches_echouees')),
}

_AGENTS = {}


def _init_worker(step, model_path):
    import torch
    torch.set_num_threads(1)
    from warehouse_marl.drl.v4_dqn import load_v4_model
    if model_path:
        kind = {'idle6': 'idle6', 'route6': 'route6', 'alloc6': 'alloc6'}[step]
        _AGENTS['drl'] = load_v4_model(model_path, kind)
    if step == 'idle6' and os.path.isfile(V4_IDLE_MODEL):
        _AGENTS['drl_idle'] = load_v4_model(V4_IDLE_MODEL, 'idle')


def scenario(step, cfg, alloc, k):
    from warehouse_marl.drl.train_v4 import dataset
    from warehouse_marl.drl.train_v6 import test_window_start
    sc = dict(phase=STEPS[step]['phase'], robots=cfg['robots'], dims=cfg['dims'],
              rho=cfg['rho'], tasks=N_TASKS, alloc=alloc, seed=TEST6_SEEDS[k],
              speeds=cfg.get('speeds'), block_rate=cfg.get('block_rate', 0.0),
              block_min=cfg.get('block_min', 30.0), block_max=cfg.get('block_max', 120.0),
              skew=cfg.get('skew', 0.0))
    if cfg.get('footwear'):
        sc.update(split='test', start=test_window_start(dataset(), k, N_TASKS))
    return sc


def run_one(job):
    from warehouse_marl.drl.train_v6 import make_sim6
    step, exp, cfg, alloc, method, k = job
    spec = STEPS[step]
    sc = scenario(step, cfg, alloc, k)
    agent = None
    if method == spec['drl']:
        agent = _AGENTS['drl']
    elif method == 'drl_idle':
        agent = _AGENTS.get('drl_idle')
    t0 = time.perf_counter()
    if step == 'alloc6':
        from warehouse_marl.drl.alloc6 import make_alloc_sim
        sim = make_alloc_sim(sc, method, agent)
    else:
        sim = make_sim6(sc, method, agent)
    m = sim.run()
    m.update(etape=step, experience=exp, condition=cfg['label'], allocation=alloc,
             methode=method, graine=k, graine_simulation=TEST6_SEEDS[k], robots=cfg['robots'],
             racks=cfg['dims'][0] * cfg['dims'][1], rho=cfg['rho'],
             blocages_par_min=round(cfg.get('block_rate', 0.0) * 60, 3),
             taches='footwear (test)' if cfg.get('footwear') else
             ('zipf' if cfg.get('skew') else 'synthetiques uniformes'),
             capacite_segment=1 if step == 'route6' else 0,
             duree_calcul_s=round(time.perf_counter() - t0, 3))
    return m


# ---------------------------------------------------------------------- #
def _groups(rows):
    out = {}
    for r in rows:
        out.setdefault((r['experience'], r['condition'], r['allocation']), {}) \
           .setdefault(r['methode'], {})[r['graine']] = r
    return out


def _compare(by_m, drl, adv, metric=PRIMARY):
    seeds = sorted(set(by_m[drl]) & set(by_m[adv]))
    a = [float(by_m[drl][s][metric]) for s in seeds]
    b = [float(by_m[adv][s][metric]) for s in seeds]
    return seeds, a, b


def _row(step, exp, cond, alloc, by_m, drl, adv, kind):
    seeds, a, b = _compare(by_m, drl, adv)
    diffs = [x - y for x, y in zip(a, b)]
    (alo, ahi), (blo, bhi), (dlo, dhi) = bootstrap_ci(a), bootstrap_ci(b), bootstrap_ci(diffs)
    fa = sum(float(by_m[drl][s]['taches_echouees']) for s in seeds)
    fb = sum(float(by_m[adv][s]['taches_echouees']) for s in seeds)
    return {
        'etape': step, 'experience': exp, 'condition': cond, 'allocation': alloc,
        'methode_drl': drl, 'concurrent': adv, 'type_comparaison': kind, 'n_essais': len(seeds),
        'drl_moyenne_s': round(statistics.mean(a), 3), 'drl_ic95_bas': round(alo, 3),
        'drl_ic95_haut': round(ahi, 3),
        'conc_moyenne_s': round(statistics.mean(b), 3), 'conc_ic95_bas': round(blo, 3),
        'conc_ic95_haut': round(bhi, 3),
        'ecart_moyen_s': round(statistics.mean(diffs), 3),
        'ecart_ic95_bas': round(dlo, 3), 'ecart_ic95_haut': round(dhi, 3),
        'gain_pct': round(100 * (statistics.mean(b) - statistics.mean(a)) / statistics.mean(b), 2),
        'drl_gagne': f'{sum(x < y for x, y in zip(a, b))}/{len(seeds)}',
        'egalites': sum(abs(x - y) < 1e-9 for x, y in zip(a, b)),
        'echecs_drl': int(fa), 'echecs_conc': int(fb),
        'p_wilcoxon': wilcoxon_p(a, b),
    }


def _decide(rows):
    adj = holm([r['p_wilcoxon'] for r in rows])
    for r, pa in zip(rows, adj):
        r['p_holm'] = round(pa, 6)
        r['p_wilcoxon'] = round(r['p_wilcoxon'], 6)
        if pa < 0.05 and r['ecart_moyen_s'] < 0:
            r['verdict'] = ('victoire avec reserve (plus d echecs)'
                            if r['echecs_drl'] > r['echecs_conc'] else 'victoire')
        elif pa < 0.05:
            r['verdict'] = 'defaite'
        else:
            r['verdict'] = 'egalite'
    return rows


def principal(rows, step):
    spec = STEPS[step]
    drl, comp = spec['drl'], spec['competitors']
    out = []
    for (exp, cond, alloc), by_m in _groups(rows).items():
        if drl not in by_m:
            continue
        means = {m: _nanmean([float(r[PRIMARY]) for r in by_m[m].values()]) for m in comp}
        if spec['compare'] == 'best':
            best = min(means, key=lambda m: means[m])
            row = _row(step, exp, cond, alloc, by_m, drl, best, 'meilleur concurrent')
            row.update({f'moyenne_{m}': round(means[m], 3) for m in comp})
            out.append(row)
        else:
            for m in comp:
                out.append(_row(step, exp, cond, alloc, by_m, drl, m, 'chaque concurrent'))
    return _decide(out)


def secondaire(rows, step):
    spec = STEPS[step]
    drl = spec['drl']
    out = []
    # famille 1 : contre chaque concurrent ; familles 2.. : contre chaque methode descriptive
    families = [('contre chaque concurrent', spec['competitors'])] + \
        [(f'contre {d}', (d,)) for d in spec['descriptive']]
    for name, advs in families:
        fam = []
        for (exp, cond, alloc), by_m in _groups(rows).items():
            for adv in advs:
                if drl in by_m and adv in by_m:
                    r = _row(step, exp, cond, alloc, by_m, drl, adv, name)
                    r['famille'] = f'{PRIMARY} {name}'
                    fam.append(r)
        out += _decide(fam)
    for metric in spec['secondary']:
        fam = []
        for (exp, cond, alloc), by_m in _groups(rows).items():
            if drl not in by_m:
                continue
            for adv in spec['competitors']:
                seeds, a, b = _compare(by_m, drl, adv, metric)
                if not a or any(math.isnan(x) for x in a + b):
                    continue
                fam.append({'etape': step, 'famille': f'{metric} contre chaque concurrent',
                            'metrique': metric, 'experience': exp, 'condition': cond,
                            'allocation': alloc, 'concurrent': adv,
                            'drl_moyenne': round(statistics.mean(a), 4),
                            'conc_moyenne': round(statistics.mean(b), 4),
                            'ecart_moyen': round(statistics.mean(a) - statistics.mean(b), 4),
                            'p_wilcoxon': wilcoxon_p(a, b)})
        for r, pa in zip(fam, holm([r['p_wilcoxon'] for r in fam])):
            r['p_wilcoxon'] = round(r['p_wilcoxon'], 6)
            r['p_holm_famille'] = round(pa, 6)
        out += fam
    return out


def descriptive(rows, step):
    spec = STEPS[step]
    metrics = (PRIMARY,) + spec['secondary'] + ('ms_par_decision_route',
                                                'ms_par_decision_attente', 'replis_route6',
                                                'attentes_choisies')
    out = []
    for (exp, cond, alloc), by_m in _groups(rows).items():
        for m, by_s in by_m.items():
            for metric in metrics:
                xs = [float(r[metric]) for r in by_s.values()
                      if metric in r and r[metric] != '']
                xs = [x for x in xs if not math.isnan(x)]
                if not xs:
                    continue
                lo, hi = bootstrap_ci(xs)
                out.append({'etape': step, 'experience': exp, 'condition': cond,
                            'allocation': alloc, 'methode': m, 'metrique': metric,
                            'n': len(xs), 'moyenne': round(statistics.mean(xs), 4),
                            'ic95_bas': round(lo, 4), 'ic95_haut': round(hi, 4)})
    return out


# ---------------------------------------------------------------------- #
PALETTE = ('#8c8c8c', '#937860', '#4c72b0', '#55a868', '#dd8452', '#c44e52')


def figures(rows, step, out_dir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'axes.grid': True, 'grid.alpha': 0.3, 'axes.spines.top': False,
                         'axes.spines.right': False})
    spec = STEPS[step]
    methods = list(spec['competitors']) + list(spec['descriptive']) + [spec['drl']]
    methods = [m for m in methods if any(r['methode'] == m for r in rows)]
    colors = dict(zip(methods, PALETTE[-len(methods):] if len(methods) < 6 else PALETTE))
    colors[spec['drl']] = '#c44e52'
    metrics = [(PRIMARY, 'Temps de traitement moyen (s)')] + \
        [(m, m) for m in spec['secondary']]
    paths = []
    for exp, _ in spec['experiments']:
        sub = [r for r in rows if r['experience'] == exp]
        conds = list(dict.fromkeys(r['condition'] for r in sub))
        allocs = spec['allocations']
        fig, axs = plt.subplots(len(allocs), len(metrics),
                                figsize=(4.4 * len(metrics), 3.8 * len(allocs)), squeeze=False)
        for i, alloc in enumerate(allocs):
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
        fig.suptitle(f'v6, etape {step}, experience {exp} : moyenne et IC 95 % bootstrap '
                     f'({N_TEST6} graines de test v6)', fontsize=11)
        fig.tight_layout()
        path = os.path.join(out_dir, f'fig_{step}_{exp}_v6.png')
        fig.savefig(path, dpi=130)
        plt.close(fig)
        paths.append(path)
    return paths


def figure_ecarts(prin, step, out_dir):
    """Meme style que fig_<step>_ecarts.png de la v4 : ecart apparie DRL -
    concurrent (s), IC 95 % bootstrap ; vert = victoire, rouge = defaite,
    gris = egalite (Holm, alpha = 0,05) ; etoile = significatif."""
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
                        f"(vs {r['concurrent']})" for r in reversed(prin)], fontsize=7)
    ax.set_xlabel('Ecart de temps de traitement moyen, DRL - concurrent (s)\n'
                  '< 0 : DRL plus rapide ; gris : non significatif (Holm, alpha = 0,05)')
    ax.set_title(f'v6, etape {step} : ecart apparie et IC 95 % bootstrap '
                 f'({N_TEST6} graines de test v6)', fontsize=10)
    fig.tight_layout()
    path = os.path.join(out_dir, f'fig_{step}_ecarts_v6.png')
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def main(argv=None):
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    p = argparse.ArgumentParser()
    p.add_argument('--step', choices=list(STEPS), required=True)
    p.add_argument('--model', default='')
    p.add_argument('--out-dir', required=True)
    p.add_argument('--workers', type=int, default=2)
    p.add_argument('--stats-only', action='store_true')
    args = p.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    step = args.step
    spec = STEPS[step]
    path = os.path.join(args.out_dir, f'essais_{step}.csv')
    if not args.stats_only:
        methods = list(spec['competitors']) + list(spec['descriptive']) + [spec['drl']]
        jobs = [(step, exp, cfg, alloc, m, k) for exp, cfgs in spec['experiments']
                for cfg in cfgs for alloc in spec['allocations'] for m in methods
                for k in range(N_TEST6)]
        print(f'{len(jobs)} essais de test ({step}), modele {args.model}', flush=True)
        t0 = time.time()
        if args.workers > 1:
            with mp.get_context('fork').Pool(args.workers, _init_worker,
                                             (step, args.model)) as pool:
                rows = pool.map(run_one, jobs, chunksize=2)
        else:
            _init_worker(step, args.model)
            rows = [run_one(j) for j in jobs]
        for r in rows:
            r['modele'] = (os.path.basename(args.model) if r['methode'] == spec['drl'] else
                           ('selected_idle.pt (v4)' if r['methode'] == 'drl_idle' else ''))
        write_csv(path, rows)
        print(f'{path} ({time.time() - t0:.0f} s)', flush=True)
    rows = read_csv(path)
    prin = principal(rows, step)
    write_csv(os.path.join(args.out_dir, f'principal_{step}.csv'), prin)
    write_csv(os.path.join(args.out_dir, f'secondaire_{step}.csv'), secondaire(rows, step))
    write_csv(os.path.join(args.out_dir, f'descriptif_{step}.csv'), descriptive(rows, step))
    for r in prin:
        print(f"{r['experience']:10s} {r['condition']:36s} {r['allocation']:12s} "
              f"DRL {r['drl_moyenne_s']:7.2f} vs {r['concurrent']:20s} "
              f"{r['conc_moyenne_s']:7.2f}  ecart {r['ecart_moyen_s']:+7.3f} "
              f"[{r['ecart_ic95_bas']:+.3f};{r['ecart_ic95_haut']:+.3f}]  {r['drl_gagne']:>5s}  "
              f"p={r['p_wilcoxon']:.4g} holm={r['p_holm']:.4g}  {r['verdict']}")
    for f in figures(rows, step, args.out_dir) + [figure_ecarts(prin, step, args.out_dir)]:
        print('Figure :', f)


if __name__ == '__main__':
    main()
