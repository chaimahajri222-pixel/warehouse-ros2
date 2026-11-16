"""Assemble ~/warehouse_ws/resultats_v6 (PROTOCOLE_V6.md, §8) a partir des
fichiers de train_v6, selection_v6 et benchmark_v6, et ecrit VALEURS_V6.md :
chaque valeur citee avec son fichier et sa ligne (ligne 1 = en-tete du CSV).
N'invente rien : tout est relu dans les CSV.

    python rapport_v6.py --drl-dir ~/warehouse_ws/drl_v6 --test-dir ~/warehouse_ws/test_v6 \
        --protocol PROTOCOLE_V6.md --out ~/warehouse_ws/resultats_v6
"""
import argparse
import csv
import glob
import os
import shutil

# (dossier d'entrainement, type de modele, phase) ; ecart 3 : A = petit + grand
TRAININGS = (('idle6_petit', 'idle6', 'A, modele petit (15 et 40 racks)'),
             ('idle6_grand', 'idle6', 'A, modele grand (150 racks)'),
             ('route6', 'route6', 'B'), ('alloc6', 'alloc6', 'C'))


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def ref(fname, i):
    return f'`{fname}` l.{i + 2}'


def copy_all(args, out):
    os.makedirs(out, exist_ok=True)
    for name, kind, _ in TRAININGS:
        d = os.path.join(args.drl_dir, name)
        if not os.path.isdir(d):
            continue
        dst = os.path.join(out, f'entrainement_{name}')
        os.makedirs(dst, exist_ok=True)
        for pat in ('*.csv', '*.png', 'fini_seed*.txt', f'selected_{kind}.pt'):
            for f in glob.glob(os.path.join(d, pat)):
                shutil.copy(f, dst)
        j = os.path.join(args.drl_dir, f'journal_{name}.txt')
        if os.path.isfile(j):
            shutil.copy(j, dst)
    # lancements interrompus (ecarts 3 a 6) : journaux de validation seulement
    for d in sorted(glob.glob(os.path.join(args.drl_dir, '*_interrompu_*'))):
        dst = os.path.join(out, 'lancements_interrompus', os.path.basename(d))
        os.makedirs(dst, exist_ok=True)
        for pat in ('val_log_seed*.csv', 'val_ref.csv', 'journal_*.txt'):
            for f in glob.glob(os.path.join(d, pat)):
                shutil.copy(f, dst)
    for f in glob.glob(os.path.join(args.drl_dir, 'journal_chaine*.txt')):
        shutil.copy(f, out)
    for pat in ('*.csv', '*.png', '*.txt'):
        for f in glob.glob(os.path.join(args.test_dir, pat)):
            shutil.copy(f, out)
    shutil.copy(args.protocol, out)


def section_selection(L, out, name, kind):
    d = os.path.join(out, f'entrainement_{name}')
    path = os.path.join(d, f'selection_{kind}.csv')
    if not os.path.isfile(path):
        L.append(f'*Pas de selection pour {name} (entrainement non fait).*\n')
        return
    rows = read(path)
    fname = f'entrainement_{name}/selection_{kind}.csv'
    L.append('| graine | instant (min) | episode | ecart relatif de validation | '
             'temps de validation (s) | reprises | retenu | source |')
    L.append('|---|---|---|---|---|---|---|---|')
    for i, r in enumerate(rows):
        L.append(f"| {r['graine']} | {r['temps_min']} | {r['episode']} | "
                 f"{100 * float(r['val_ecart_rel_moy']):+.3f} % | "
                 f"{float(r['val_temps_traitement_moy_s']):.3f} | {r['reprises']} | "
                 f"{'**oui**' if r['retenu'] == 'True' else ''} | {ref(fname, i)} |")
    L.append('')
    for s in sorted({r['graine'] for r in rows}):
        tl = os.path.join(d, f'train_log_seed{s}.csv')
        if os.path.isfile(tl):
            t = read(tl)
            L.append(f"- Graine {s} : {len(t)} episodes d'entrainement en {t[-1]['temps_min']} min "
                     f"({ref(f'entrainement_{name}/train_log_seed{s}.csv', len(t) - 1)}).")
    vr = os.path.join(d, 'val_ref.csv')
    if os.path.isfile(vr):
        L.append(f'- Heuristiques concurrentes sur les scenarios de validation : '
                 f'`entrainement_{name}/val_ref.csv` ({len(read(vr))} scenarios).')
    L.append('')


def section_principal(L, out, step):
    path = os.path.join(out, f'principal_{step}.csv')
    if not os.path.isfile(path):
        L.append(f'*Pas de resultats de test pour {step}.*\n')
        return []
    rows = read(path)
    fname = f'principal_{step}.csv'
    L.append('| experience | condition | allocation | DRL (s) [IC95] | concurrent (s) [IC95] '
             '| ecart (s) [IC95] | gain | gagnes | echecs DRL/conc. | p Wilcoxon | p Holm | '
             'verdict | source |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for i, r in enumerate(rows):
        L.append(
            f"| {r['experience']} | {r['condition']} | {r['allocation']} | "
            f"{r['drl_moyenne_s']} [{r['drl_ic95_bas']} ; {r['drl_ic95_haut']}] | "
            f"{r['concurrent']} {r['conc_moyenne_s']} [{r['conc_ic95_bas']} ; {r['conc_ic95_haut']}] | "
            f"{r['ecart_moyen_s']} [{r['ecart_ic95_bas']} ; {r['ecart_ic95_haut']}] | "
            f"{r['gain_pct']} % | {r['drl_gagne']} | {r['echecs_drl']}/{r['echecs_conc']} | "
            f"{float(r['p_wilcoxon']):.4g} | {float(r['p_holm']):.4g} | **{r['verdict']}** | "
            f"{ref(fname, i)} |")
    L.append('')
    counts = {}
    for r in rows:
        counts[r['verdict']] = counts.get(r['verdict'], 0) + 1
    L.append('Decompte (meme fichier) : ' + ' ; '.join(
        f'{k} : {v}/{len(rows)}' for k, v in sorted(counts.items())) + '\n')
    if step in ('route6', 'idle6'):
        what = ('les 3 tests (une Dijkstra chacun)' if step == 'route6' else
                'les 2 tests (meilleure des 3 heuristiques v4 ET couverture, ecart 2)')
        L.append(f'Par (condition, allocation), gagnee seulement si {what} sont des victoires :\n')
        keys = list(dict.fromkeys((r['experience'], r['condition'], r['allocation'])
                                  for r in rows))
        n_ok = 0
        for key in keys:
            sub = [(i, r) for i, r in enumerate(rows)
                   if (r['experience'], r['condition'], r['allocation']) == key]
            ok = all(r['verdict'].startswith('victoire') for _, r in sub)
            n_ok += ok
            L.append(f"- {' | '.join(key)} : {'**gagnee**' if ok else 'non gagnee'} ("
                     + ', '.join(f"contre {r['concurrent']} : {r['verdict']} {ref(fname, i)}"
                                 for i, r in sub) + ')')
        L.append(f'\nTotal : {n_ok}/{len(keys)} (condition, allocation) gagnees.\n')
    return rows


def section_secondaire(L, out, step, families):
    path = os.path.join(out, f'secondaire_{step}.csv')
    if not os.path.isfile(path):
        return
    rows = read(path)
    fname = f'secondaire_{step}.csv'
    for fam in families:
        sub = [(i, r) for i, r in enumerate(rows) if r.get('famille') == fam]
        if not sub:
            continue
        L.append(f'**Famille secondaire : {fam}** (Holm dans la famille, descriptif)\n')
        L.append('| experience | condition | allocation | concurrent | DRL (s) | concurrent (s) | '
                 'ecart (s) [IC95] | gagnes | p Holm | verdict | source |')
        L.append('|---|---|---|---|---|---|---|---|---|---|---|')
        for i, r in sub:
            L.append(f"| {r['experience']} | {r['condition']} | {r['allocation']} | "
                     f"{r['concurrent']} | {r['drl_moyenne_s']} | {r['conc_moyenne_s']} | "
                     f"{r['ecart_moyen_s']} [{r['ecart_ic95_bas']} ; {r['ecart_ic95_haut']}] | "
                     f"{r['drl_gagne']} | {float(r['p_holm']):.4g} | {r['verdict']} | "
                     f"{ref(fname, i)} |")
        L.append('')


def section_descriptif(L, out, step, metrics):
    path = os.path.join(out, f'descriptif_{step}.csv')
    if not os.path.isfile(path):
        return
    rows = read(path)
    fname = f'descriptif_{step}.csv'
    L.append('| experience | condition | allocation | methode | metrique | moyenne [IC95] | source |')
    L.append('|---|---|---|---|---|---|---|')
    for i, r in enumerate(rows):
        if r['metrique'] in metrics:
            L.append(f"| {r['experience']} | {r['condition']} | {r['allocation']} | {r['methode']} | "
                     f"{r['metrique']} | {r['moyenne']} [{r['ic95_bas']} ; {r['ic95_haut']}] | "
                     f"{ref(fname, i)} |")
    L.append('')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--drl-dir', required=True)
    p.add_argument('--test-dir', required=True)
    p.add_argument('--protocol', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()
    for k in ('drl_dir', 'test_dir', 'protocol', 'out'):
        setattr(args, k, os.path.expanduser(getattr(args, k)))
    out = args.out
    copy_all(args, out)
    L = ['# VALEURS_V6 : toutes les valeurs, avec leur fichier et leur ligne', '',
         'Genere par `src/warehouse_marl/scripts/rapport_v6.py` a partir des CSV du dossier. '
         'Ligne 1 = en-tete du CSV ; "l.N" = N-ieme ligne du fichier. '
         'Protocole : `PROTOCOLE_V6.md` (copie dans ce dossier). Graines de test v6 : '
         '2 000 003 + 1 013 k, k = 0..19. Victoire = p de Holm < 0,05 et ecart moyen < 0.', '']
    L += ['## 1. Selection des modeles (validation uniquement)', '']
    for name, kind, label in TRAININGS:
        L += [f'### Phase {label} : drl_{kind}', '']
        section_selection(L, out, name, kind)
    L += ['Lancements interrompus (ecarts 3 a 6 de `PROTOCOLE_V6.md`, ni selection ni test) : '
          'journaux de validation dans `lancements_interrompus/`.', '']
    L += ['## 2. Phase A : drl_idle6 contre la meilleure des 3 heuristiques d attente v4 '
          'et contre la couverture (famille A, 28 tests, Holm ; ecart 2)', '']
    section_principal(L, out, 'idle6')
    section_secondaire(L, out, 'idle6', (
        'temps_traitement_moy_s contre drl_idle',
        'temps_traitement_moy_s contre chaque concurrent'))
    L += ['## 3. Phase B : drl_route6 contre chacune des 3 Dijkstra, capacite 1 robot par '
          'segment (famille B, 12 tests, Holm)', '']
    section_principal(L, out, 'route6')
    L += ['## 4. Phase C : drl_alloc6 contre la meilleure de greedy_pair et greedy_time '
          '(famille C, 4 tests, Holm)', '']
    section_principal(L, out, 'alloc6')
    L += ['## 5. Metriques secondaires (moyenne et IC 95 %, toutes methodes)', '',
          'Tests DRL contre chaque concurrent et par metrique (Holm par famille) : '
          '`secondaire_<etape>.csv`.', '', '### Phase A', '']
    section_descriptif(L, out, 'idle6', ('approche_moy_s', 'taches_echouees',
                                         'ms_par_decision_attente'))
    L += ['### Phase B', '']
    section_descriptif(L, out, 'route6', ('attente_file_par_tache_s', 'temps_trajet_moy_s',
                                          'taches_echouees', 'distance_par_tache_m',
                                          'ms_par_decision_route', 'replis_route6'))
    L += ['### Phase C', '']
    section_descriptif(L, out, 'alloc6', ('attente_attribution_moy_s', 'approche_moy_s',
                                          'taches_echouees', 'attentes_allocation'))
    with open(os.path.join(out, 'VALEURS_V6.md'), 'w') as f:
        f.write('\n'.join(L) + '\n')
    print(os.path.join(out, 'VALEURS_V6.md'))


if __name__ == '__main__':
    main()
