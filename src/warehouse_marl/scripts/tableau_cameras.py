#!/usr/bin/env python3
"""tableau_cameras.py : tableaux Markdown a partir des syntheses de
mesures_cameras.sh (synthese_<mode>.json), presentes comme les tests de
Yumbla et al. (IEEE Access 2025, section IV : A localisation, B navigation
sans collision, C taches).

    python3 tableau_cameras.py DOSSIER [MODE ...]      (defaut : sans cameras)
"""
import json
import os
import sys

LABELS = {'sans': 'AMCL seul', 'cameras': 'AMCL + cameras'}


def fmt(v, nd=2):
    return '-' if v is None else f'{v:.{nd}f}'


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    d = sys.argv[1]
    modes = sys.argv[2:] or ['sans', 'cameras']
    data = {}
    for m in modes:
        p = os.path.join(d, f'synthese_{m}.json')
        if os.path.isfile(p):
            with open(p) as f:
                data[m] = json.load(f)
    if not data:
        print(f'aucune synthese dans {d}')
        return 1
    cols = list(data)
    head = '| | ' + ' | '.join(LABELS.get(m, m) for m in cols) + ' |'
    sep = '|---|' + '---|' * len(cols)
    out = []

    out += ['### A. Localisation : erreur de position estimee / reelle (m)', '', head, sep]
    robots = sorted(next(iter(data.values()))['A_localisation_erreur_m'])
    for key, name in (('moyenne', 'moyenne'), ('mediane', 'mediane'), ('p95', '95e centile'),
                      ('max', 'maximum')):
        out.append(f'| flotte, {name} | ' + ' | '.join(
            fmt((data[m]['A_localisation_erreur_m_flotte'] or {}).get(key)) for m in cols) + ' |')
    for r in robots:
        out.append(f'| {r}, mediane / max | ' + ' | '.join(
            '{} / {}'.format(fmt((data[m]['A_localisation_erreur_m'][r] or {}).get('mediane')),
                             fmt((data[m]['A_localisation_erreur_m'][r] or {}).get('max')))
            for m in cols) + ' |')
    out.append('| lacet, mediane (deg), flotte | ' + ' | '.join(
        fmt(sorted(v['mediane'] for v in data[m]['A_localisation_erreur_lacet_deg'].values()
                   if v)[len(robots) // 2] if any(data[m]['A_localisation_erreur_lacet_deg'].values())
            else None, 1) for m in cols) + ' |')

    out += ['', '### B. Navigation : contacts entre robots (poses Gazebo)', '', head, sep]
    out.append('| contacts (ecart <= 2 cm) | ' + ' | '.join(
        str(data[m]['B_contacts']) for m in cols) + ' |')
    out.append('| quasi-contacts (2-15 cm) | ' + ' | '.join(
        str(data[m]['B_quasi_contacts_moins_15cm']) for m in cols) + ' |')
    pairs = sorted(next(iter(data.values()))['B_ecart_min_m'])
    for k in pairs:
        out.append(f'| ecart minimal {k} (m) | ' + ' | '.join(
            fmt(data[m]['B_ecart_min_m'][k]) for m in cols) + ' |')

    out += ['', '### C. Taches', '', head, sep]
    for key, name in (('C_taches_creees', 'creees'), ('C_taches_reussies', 'reussies'),
                      ('C_taches_echouees', 'echouees'), ('C_taches_annulees', 'annulees'),
                      ('C_taches_non_terminees', 'non terminees a la fin')):
        out.append(f'| {name} | ' + ' | '.join(str(data[m][key]) for m in cols) + ' |')
    out.append('| reussies par robot | ' + ' | '.join(
        ', '.join(f'{r[-1]}:{n}' for r, n in sorted(data[m]['C_reussies_par_robot'].items()))
        for m in cols) + ' |')

    out += ['', '### Corrections envoyees par les cameras', '', head, sep]
    out.append('| nombre | ' + ' | '.join(str(data[m]['corrections_cameras']) for m in cols) + ' |')
    out.append('| par motif | ' + ' | '.join(
        ', '.join(f'{k} {v}' for k, v in sorted(data[m]['corrections_par_motif'].items())) or '-'
        for m in cols) + ' |')
    out.append('| ecart corrige, mediane / max (m) | ' + ' | '.join(
        '{} / {}'.format(fmt((data[m]['ecart_corrige_m'] or {}).get('mediane')),
                         fmt((data[m]['ecart_corrige_m'] or {}).get('max'))) for m in cols) + ' |')
    out.append('| duree mesuree (s, horloge murale) | ' + ' | '.join(
        fmt(data[m]['duree_mesuree_s'], 0) for m in cols) + ' |')
    print('\n'.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
