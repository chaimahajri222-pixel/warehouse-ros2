"""Resume du test msg_loss (test_consensus_ros.sh pertes) : lit le journal
test_ros_pertes.txt et ecrit pertes_essais.csv (une ligne par essai, avec les
compteurs des journaux des noeuds) et pertes_taches.csv (une ligne par tache).

    python resume_pertes_v5.py ~/warehouse_ws/resultats_v5/test_ros_pertes.txt
"""
import csv
import json
import os
import re
import sys


def main():
    path = os.path.expanduser(sys.argv[1])
    out_dir = os.path.dirname(path)
    runs, tasks = [], []
    cur = None
    for line in open(path):
        if line.startswith('## '):
            cur = {'section': line[3:].strip(), 'pertes_simulees': 0, 'retraits_sur_conflit': 0}
            runs.append(cur)
        elif line.startswith('{') and cur is not None:
            d = json.loads(line)
            cur.update(d['resume'])
            for p in d['par_tache']:
                tasks.append({'essai': d['resume']['essai'], **p})
        elif cur is not None and re.match(r'robot\d : pertes simulees', line):
            m = re.search(r'pertes simulees (\d+), retraits sur conflit (\d+)', line)
            cur['pertes_simulees'] += int(m.group(1))
            cur['retraits_sur_conflit'] += int(m.group(2))
            c = re.search(r'\((\d+)/(\d+)\)', line)
            if c:   # compteur imprime seulement avec une perte (valeur au dernier rejet)
                cur['encheres_recues_au_dernier_rejet'] = (
                    cur.get('encheres_recues_au_dernier_rejet', 0) + int(c.group(2)))
        elif cur is not None and line.startswith('RC='):
            cur['rc'] = int(line.strip()[3:])
    cols = ['section', 'taches', 'attribuees', 'attribuees_une_seule_fois',
            'mises_en_file_multiples', 'executions_multiples', 'reussies_une_fois',
            'non_attribuees', 'conflits', 'retraits_sur_conflit',
            'executant_different_du_meilleur', 'encheres_publiees', 'encheres_recues_au_dernier_rejet',
            'pertes_simulees', 'delai_attribution_moy_s', 'toutes_terminees', 'reussi', 'rc']
    with open(os.path.join(out_dir, 'pertes_essais.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(runs)
    if tasks:
        with open(os.path.join(out_dir, 'pertes_taches.csv'), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(tasks[0]))
            w.writeheader()
            w.writerows(tasks)
    for r in runs:
        print({k: r.get(k) for k in cols})


if __name__ == '__main__':
    main()
