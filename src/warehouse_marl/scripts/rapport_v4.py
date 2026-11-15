"""Assemble ~/warehouse_ws/resultats_v4 (PROTOCOLE_V4.md, §9) a partir des
fichiers produits par train_v4, selection_v4 et benchmark_v4, et ecrit
VALEURS_V4.md : chaque valeur citee avec son fichier et sa ligne (ligne 1 =
en-tete du CSV). N'invente rien : tout est relu dans les CSV.

    python rapport_v4.py --drl-dir ~/warehouse_ws/drl_v4 --test-dir ~/warehouse_ws/test_v4 \
        --out ~/warehouse_ws/resultats_v4
"""
import argparse
import csv
import glob
import os
import shutil


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def ref(fname, i):
    return f'`{fname}` l.{i + 2}'


def copy_all(args, out):
    os.makedirs(out, exist_ok=True)
    sub = {'entrainement_route': os.path.join(args.drl_dir, 'route'),
           'entrainement_idle': os.path.join(args.drl_dir, 'idle')}
    for name, d in sub.items():
        if not os.path.isdir(d):
            continue
        dst = os.path.join(out, name)
        os.makedirs(dst, exist_ok=True)
        for pat in ('*.csv', '*.png', 'stdout_seed*.txt', 'selected_*.pt'):
            for f in glob.glob(os.path.join(d, pat)):
                shutil.copy(f, dst)
    for pat in ('*.csv', '*.png', '*.txt'):
        for f in glob.glob(os.path.join(args.test_dir, pat)):
            shutil.copy(f, out)
    shutil.copy(args.protocol, out)


def section_selection(lines, out, kind):
    d = os.path.join(out, f'entrainement_{kind}')
    path = os.path.join(d, f'selection_{kind}.csv')
    if not os.path.isfile(path):
        lines.append(f'*Pas de selection pour {kind} (fichier absent).*\n')
        return
    rows = read(path)
    fname = f'entrainement_{kind}/selection_{kind}.csv'
    lines.append(f'| graine | instant (min) | episode | validation (s) | retenu | source |')
    lines.append('|---|---|---|---|---|---|')
    for i, r in enumerate(rows):
        lines.append(f"| {r['graine']} | {r['temps_min']} | {r['episode']} | "
                     f"{float(r['val_temps_traitement_moy_s']):.4f} | "
                     f"{'**oui**' if r['retenu'] == 'True' else ''} | {ref(fname, i)} |")
    lines.append('')
    for s in sorted({r['graine'] for r in rows}):
        tl = os.path.join(d, f'train_log_seed{s}.csv')
        if os.path.isfile(tl):
            t = read(tl)
            lines.append(f"- Graine {s} : {len(t)} episodes d'entrainement en "
                         f"{t[-1]['temps_min']} min ({ref(f'entrainement_{kind}/train_log_seed{s}.csv', len(t) - 1)}).")
    lines.append('')


def section_principal(lines, out, step):
    path = os.path.join(out, f'principal_{step}.csv')
    if not os.path.isfile(path):
        lines.append(f'*Pas de resultats de test pour {step}.*\n')
        return []
    rows = read(path)
    fname = f'principal_{step}.csv'
    lines.append('| experience | condition | allocation | DRL (s) [IC95] | meilleure heuristique (s) [IC95] '
                 '| ecart (s) [IC95] | gagnes | echecs DRL/heur. | p Wilcoxon | p Holm | conclusion | source |')
    lines.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for i, r in enumerate(rows):
        lines.append(
            f"| {r['experience']} | {r['condition']} | {r['allocation']} | "
            f"{r['drl_moyenne_s']} [{r['drl_ic95_bas']} ; {r['drl_ic95_haut']}] | "
            f"{r['meilleure_heuristique']} {r['heur_moyenne_s']} [{r['heur_ic95_bas']} ; {r['heur_ic95_haut']}] | "
            f"{r['ecart_moyen_s']} [{r['ecart_ic95_bas']} ; {r['ecart_ic95_haut']}] | {r['drl_gagne']} | "
            f"{r['echecs_drl']}/{r['echecs_heur']} | {float(r['p_wilcoxon']):.4g} | {float(r['p_holm']):.4g} | "
            f"{r['conclusion']} | {ref(fname, i)} |")
    lines.append('')
    counts = {}
    for r in rows:
        counts[r['conclusion']] = counts.get(r['conclusion'], 0) + 1
    lines.append('Decompte (meme fichier) : ' + ' ; '.join(
        f'{k} : {v}/{len(rows)}' for k, v in sorted(counts.items())) + '\n')
    return rows


def section_descriptif(lines, out, step, metrics):
    path = os.path.join(out, f'descriptif_{step}.csv')
    if not os.path.isfile(path):
        return
    rows = read(path)
    fname = f'descriptif_{step}.csv'
    lines.append('| experience | condition | allocation | methode | metrique | moyenne [IC95] | source |')
    lines.append('|---|---|---|---|---|---|---|')
    for i, r in enumerate(rows):
        if r['metrique'] in metrics:
            lines.append(f"| {r['experience']} | {r['condition']} | {r['allocation']} | {r['methode']} | "
                         f"{r['metrique']} | {r['moyenne']} [{r['ic95_bas']} ; {r['ic95_haut']}] | "
                         f"{ref(fname, i)} |")
    lines.append('')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--drl-dir', required=True)
    p.add_argument('--test-dir', required=True)
    p.add_argument('--protocol', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--ros-log', default='')
    args = p.parse_args()
    for k in ('drl_dir', 'test_dir', 'protocol', 'out', 'ros_log'):
        setattr(args, k, os.path.expanduser(getattr(args, k)))
    out = args.out
    copy_all(args, out)
    if args.ros_log and os.path.isfile(args.ros_log):
        shutil.copy(args.ros_log, os.path.join(out, 'test_ros_route_mode.txt'))
    L = ['# VALEURS_V4 : toutes les valeurs, avec leur fichier et leur ligne', '',
         'Genere par `src/warehouse_marl/scripts/rapport_v4.py` a partir des CSV du dossier. '
         'Ligne 1 = en-tete du CSV ; "l.N" = N-ieme ligne du fichier. '
         'Protocole : `PROTOCOLE_V4.md` (copie dans ce dossier).', '']
    L += ['## 1. Selection des modeles (validation uniquement)', '', '### drl_route', '']
    section_selection(L, out, 'route')
    L += ['### drl_idle', '']
    section_selection(L, out, 'idle')
    L += ['## 2. Etape 1 : DRL de chemin (famille A, 24 tests, Holm)', '']
    section_principal(L, out, 'route')
    L += ['## 3. Etape 2 : DRL d anticipation (famille B, 14 tests, Holm)', '']
    section_principal(L, out, 'idle')
    L += ['## 4. Metriques secondaires (moyenne et IC 95 %, toutes methodes)', '',
          'Tests DRL contre chaque adversaire et par metrique (Holm par famille) : '
          '`secondaire_route.csv`, `secondaire_idle.csv`.', '', '### Etape 1', '']
    section_descriptif(L, out, 'route', ('temps_trajet_moy_s', 'taches_echouees',
                                         'conflits_aretes_pour_100_taches',
                                         'attente_noeud_par_tache_s', 'ms_par_decision_route',
                                         'replis_dijkstra'))
    L += ['### Etape 2', '']
    section_descriptif(L, out, 'idle', ('approche_moy_s', 'taches_echouees',
                                        'ms_par_decision_attente'))
    with open(os.path.join(out, 'VALEURS_V4.md'), 'w') as f:
        f.write('\n'.join(L) + '\n')
    print(os.path.join(out, 'VALEURS_V4.md'))


if __name__ == '__main__':
    main()
