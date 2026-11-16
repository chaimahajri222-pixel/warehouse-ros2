"""Selection du modele v6 sur la VALIDATION uniquement (PROTOCOLE_V6.md, §5)
et courbes d'entrainement.

    python selection_v6.py --kind idle6 --dir ~/warehouse_ws/drl_v6/idle6

Ecrit dans --dir : selection_<kind>.csv (tous les points de controle, critere,
choix), selected_<kind>.pt (copie du point retenu), courbes_<kind>.png.
Regle : plus faible ecart relatif moyen a la meilleure heuristique concurrente
de chaque scenario de validation ; egalite -> instant le plus precoce, puis
graine la plus petite. L'instant 0 (f_theta = 0) fait partie des candidats.
"""
import argparse
import csv
import glob
import os
import shutil
import statistics

START = {'idle6': 'couverture (f = 0)', 'route6': 'dijkstra_congestion (f = 0)',
         'alloc6': 'greedy_pair (f = 0)'}


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


COMPETITORS = {'idle6': ('rester_sur_place', 'retour_au_depot', 'centre_de_demande',
                         'couverture'),
               'route6': ('dijkstra_statique', 'dijkstra_dynamique', 'dijkstra_congestion'),
               'alloc6': ('greedy_pair', 'greedy_time')}


def criterion(r, ref_rows, kind):
    """Ecart relatif moyen recalcule depuis les colonnes sc<i> du journal de
    validation et val_ref.csv (concurrents de COMPETITORS, couverture comprise
    pour idle6 : ecart 2 de PROTOCOLE_V6.md)."""
    gaps = []
    for i, x in enumerate(ref_rows):
        best = min(float(x[h]) for h in COMPETITORS[kind])
        gaps.append((float(r[f'sc{i}']) - best) / best)
    return statistics.mean(gaps)


def select(kind, d):
    rows = []
    ref_rows = read(os.path.join(d, 'val_ref.csv'))
    for path in sorted(glob.glob(os.path.join(d, 'val_log_seed*.csv'))):
        for line, r in enumerate(read(path), start=2):
            seed = int(r['graine'])
            tmin = float(r['temps_min'])
            ckpt = os.path.join(d, f'ckpt_seed{seed}_t{int(round(tmin))}.pt')
            rows.append({'kind': kind, 'graine': seed, 'episode': int(r['episode']),
                         'temps_min': tmin,
                         'val_ecart_rel_moy': criterion(r, ref_rows, kind),
                         'val_temps_traitement_moy_s': float(r['val_temps_traitement_moy_s']),
                         'reprises': r.get('reprises', '0'),
                         'fichier_val': os.path.basename(path), 'ligne_val': line,
                         'point_de_controle': os.path.basename(ckpt),
                         'existe': os.path.isfile(ckpt)})
    cand = [r for r in rows if r['existe']]
    best = min(cand, key=lambda r: (r['val_ecart_rel_moy'], r['temps_min'], r['graine']))
    for r in rows:
        r['retenu'] = r is best
    out = os.path.join(d, f'selection_{kind}.csv')
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    shutil.copy(os.path.join(d, best['point_de_controle']), os.path.join(d, f'selected_{kind}.pt'))
    t0 = [r for r in rows if r['temps_min'] == 0.0]
    print(f'{kind}: retenu {best["point_de_controle"]} (graine {best["graine"]}, '
          f't = {best["temps_min"]} min, episode {best["episode"]}), ecart relatif de '
          f'validation {100 * best["val_ecart_rel_moy"]:+.3f} % ; instant 0 '
          f'({START[kind]}) : {100 * t0[0]["val_ecart_rel_moy"]:+.3f} %')
    return rows, best


def curves(kind, d, rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    seeds = sorted({r['graine'] for r in rows})
    cols = ['#4c72b0', '#dd8452', '#55a868']
    fig, axs = plt.subplots(1, 4, figsize=(19, 4.2))
    base = [r['val_ecart_rel_moy'] for r in rows if r['temps_min'] == 0.0][0]
    for s, c in zip(seeds, cols):
        v = sorted((r['temps_min'], 100 * r['val_ecart_rel_moy']) for r in rows
                   if r['graine'] == s)
        axs[0].plot([x for x, _ in v], [y for _, y in v], 'o-', color=c, label=f'graine {s}')
        tl = read(os.path.join(d, f'train_log_seed{s}.csv'))
        t = [float(r['temps_min']) for r in tl]

        def roll(key, w=50):
            xs = [float(r[key]) if r[key] not in ('', 'nan') else float('nan') for r in tl]
            out = []
            for i in range(len(xs)):
                win = [x for x in xs[max(0, i - w + 1):i + 1] if x == x]
                out.append(statistics.mean(win) if win else float('nan'))
            return out
        axs[1].plot(t, roll('temps_traitement_moy_s'), color=c, lw=1)
        axs[2].plot(t, roll('perte_td_moy'), color=c, lw=1)
        axs[3].plot(t, roll('correction_abs_moy'), color=c, lw=1)
    axs[0].axhline(100 * base, color='k', ls='--', lw=1, label=f'instant 0 = {START[kind]}')
    axs[0].axhline(0, color='#c44e52', ls=':', lw=1, label='meilleure heuristique concurrente')
    axs[0].set_title('Validation : ecart relatif moyen (%)\na la meilleure heuristique concurrente')
    axs[0].legend(fontsize=8)
    axs[1].set_title('Episodes d entrainement (exploration) :\ntemps de traitement, moyenne glissante 50')
    axs[2].set_title('Perte TD (Huber), moyenne glissante 50')
    axs[2].set_yscale('log')
    axs[3].set_title('|correction f_theta| moyenne (unites de Q)')
    for ax in axs:
        ax.set_xlabel('temps d entrainement (min)')
        ax.grid(alpha=0.3)
    fig.suptitle(f'Entrainement drl_{kind} (v6) : {len(seeds)} graine(s), une a la fois (CPU, 2 fils)')
    fig.tight_layout()
    path = os.path.join(d, f'courbes_{kind}.png')
    fig.savefig(path, dpi=130)
    print('Figure :', path)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--kind', required=True)
    p.add_argument('--dir', required=True)
    a = p.parse_args()
    rows, _ = select(a.kind, os.path.expanduser(a.dir))
    curves(a.kind, os.path.expanduser(a.dir), rows)
