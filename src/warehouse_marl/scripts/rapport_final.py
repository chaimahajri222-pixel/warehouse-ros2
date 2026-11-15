#!/usr/bin/env python3
"""
rapport_final.py
----------------
Rassemble les valeurs du memoire a partir des fichiers de resultats MESURES,
sans rien recalculer d'autre que des moyennes / tests sur ces fichiers.

    python3 rapport_final.py RACINE

RACINE contient (chemins relatifs, ceux du zip resultats_finaux) :
  banc/<exp>_statistiques.csv, banc/<exp>_essais.csv   (exp = load, scale,
      blocking, network, structured, dataset) : banc apres correction ;
  banc_avant_correction/allocation_benchmark_statistiques.csv : banc avant ;
  rfid/rfid_offline_experiment.csv, rfid/rfid_offline_experiment_graines.csv ;
  entrainement_synthetique/indicators_v3.csv,
  entrainement_donnees_reelles/indicators_v3.csv ;
  gazebo/synthese_taches.csv, gazebo/rfid_<mode>.csv (optionnels).

Ecrit dans RACINE :
  derives/valeurs_derivees.csv      valeurs agregees + lignes sources ;
  derives/drl_vs_meilleure.csv      DRL v3 (direct, hybride) vs meilleure heuristique ;
  derives/comparaison_cahier.csv    criteres du sujet (temps, erreurs) ;
  derives/avant_apres_equite.csv    blocking / network avant et apres correction ;
  VALEURS_MEMOIRE.md                chaque valeur avec sa source (fichier + ligne).
Toute valeur citee renvoie a une ligne d'un CSV (ligne 1 = en-tete).
"""

from __future__ import annotations

import csv
import math
import os
import statistics
import sys
from typing import Dict, List, Optional

from warehouse_marl.allocation_benchmark import bootstrap_ci, wilcoxon_p

EXPS = ('load', 'scale', 'blocking', 'network', 'structured', 'dataset')
REFS = ('fifo', 'greedy_pair', 'greedy_time')
SYSTEMS = ('consensus', 'drl3_hybrid', 'drl2_hybrid')


def read(path: str) -> List[Dict]:
    """Lignes d'un CSV, chacune avec '_ligne' (numero de ligne, en-tete = 1)."""
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f))
    for i, r in enumerate(rows):
        r['_ligne'] = i + 2
    return rows


def fnum(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return math.nan


def fmt(x, nd=2, pct=False) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return 'n/d'
    s = f'{x:+.{nd}f}' if pct else f'{x:.{nd}f}'
    return s.replace('.', ',') + (' %' if pct else '')


class Report:
    def __init__(self, root: str):
        self.root = root
        self.derived: List[Dict] = []
        self.md: List[str] = []

    def p(self, rel: str) -> str:
        return os.path.join(self.root, rel)

    def exists(self, rel: str) -> bool:
        return os.path.isfile(self.p(rel))

    # -- derivees ---------------------------------------------------------
    def add(self, ident: str, desc: str, valeur, fichier: str, lignes, calcul: str) -> str:
        """Enregistre une valeur derivee ; renvoie sa reference de source."""
        lignes = sorted(set(lignes))
        self.derived.append({'id': ident, 'description': desc, 'valeur': valeur,
                             'fichier_source': fichier,
                             'lignes_source': ' '.join(map(str, lignes)), 'calcul': calcul})
        return f'derives/valeurs_derivees.csv, ligne {len(self.derived) + 1}'

    def stat_row(self, exp: str, cond: str, meth: str) -> Optional[Dict]:
        rel = f'banc/{exp}_statistiques.csv'
        if not self.exists(rel):
            return None
        for r in read(self.p(rel)):
            if r['experience'] == exp and r['condition'] == cond and r['methode'] == meth:
                r['_fichier'] = rel
                return r
        return None

    def essais(self, exp: str) -> List[Dict]:
        rel = f'banc/{exp}_essais.csv'
        return read(self.p(rel)) if self.exists(rel) else []

    def per_seed(self, rows, cond, meth, metric):
        sub = [r for r in rows if r['condition'] == cond and r['methode'] == meth]
        return {int(r['graine']): (fnum(r[metric]), r['_ligne']) for r in sub}

    def paired(self, exp, cond, a_meth, b_meth, metric, ident, desc):
        """Moyennes, IC 95 %, ecart %, gagnes, Wilcoxon de a contre b (par graine)."""
        rows = self.essais(exp)
        a, b = self.per_seed(rows, cond, a_meth, metric), self.per_seed(rows, cond, b_meth, metric)
        seeds = sorted(set(a) & set(b))
        if not seeds:
            return None
        xa, xb = [a[s][0] for s in seeds], [b[s][0] for s in seeds]
        lines = [a[s][1] for s in seeds] + [b[s][1] for s in seeds]
        ma, mb = statistics.mean(xa), statistics.mean(xb)
        res = {'a_moy': ma, 'a_ic': bootstrap_ci(xa), 'b_moy': mb, 'b_ic': bootstrap_ci(xb),
               'ecart_pct': 100 * (ma - mb) / mb if mb else math.nan,
               'a_gagne': f'{sum(x < y for x, y in zip(xa, xb))}/{len(seeds)}',
               'p': wilcoxon_p(xa, xb), 'n': len(seeds)}
        res['src'] = self.add(
            ident, desc,
            f"{a_meth} {ma:.3f} [{res['a_ic'][0]:.3f} ; {res['a_ic'][1]:.3f}] vs {b_meth} {mb:.3f} "
            f"[{res['b_ic'][0]:.3f} ; {res['b_ic'][1]:.3f}] ; ecart {res['ecart_pct']:+.2f} % ; "
            f"{a_meth} plus bas {res['a_gagne']} ; p={res['p']:.4f}",
            f'banc/{exp}_essais.csv', lines,
            f'{metric} par graine ({len(seeds)} graines), moyenne, IC 95 % bootstrap, '
            f'ecart = (a - b) / b, Wilcoxon apparie')
        return res

    # -- sections ---------------------------------------------------------
    def section(self, title):
        self.md += ['', f'## {title}', '']

    def cite_stat(self, r, col):
        return f"{r['_fichier']}, ligne {r['_ligne']} (colonne {col})"

    def run(self):
        os.makedirs(self.p('derives'), exist_ok=True)
        self.md += ['# Valeurs du memoire (mesurees)', '',
                    'Chaque valeur renvoie a un fichier de ce dossier et a une ligne '
                    '(ligne 1 = en-tete). Convention : pour un temps, un ecart negatif = plus '
                    'rapide que la reference ; dans les fichiers *_statistiques.csv, '
                    '`gain_vs_X_pct` = (X - methode) / X, donc positif = plus rapide que X. '
                    'Banc : 10 graines x 150 taches, apres correction des generateurs '
                    'aleatoires (blocages identiques pour toutes les methodes).']
        self.a_to_f()
        self.g()
        self.h()
        self.i()
        self.j()
        self.comparaison()
        self.avant_apres()
        self.write()

    def a_to_f(self):
        self.section('a) Consensus contre FIFO, conditions nominales (rho = 0,7, 3 robots)')
        r = self.stat_row('load', 'rho=0.7', 'consensus')
        if r:
            g = fnum(r['gain_vs_fifo_pct'])
            self.md.append(
                f"- Temps de traitement : consensus {fmt(fnum(r['moyenne']))} s "
                f"[{fmt(fnum(r['ic95_bas']))} ; {fmt(fnum(r['ic95_haut']))}], soit "
                f"{fmt(-g, 1, True)} par rapport a FIFO ; consensus plus rapide dans "
                f"{r['gagne_vs_fifo']} scenarios ; p = {r['p_wilcoxon_vs_fifo']} "
                f"({self.cite_stat(r, 'gain_vs_fifo_pct, gagne_vs_fifo, p_wilcoxon_vs_fifo')}).")
            f = self.stat_row('load', 'rho=0.7', 'fifo')
            if f:
                self.md.append(f"- FIFO : {fmt(fnum(f['moyenne']))} s "
                               f"({self.cite_stat(f, 'moyenne')}).")

        self.section('b) Consensus contre FIFO avec 6 blocages/min')
        r = self.stat_row('blocking', '6 blocage/min', 'consensus')
        if r:
            g = fnum(r['gain_vs_fifo_pct'])
            self.md.append(
                f"- Temps de traitement : consensus {fmt(fnum(r['moyenne']))} s, soit "
                f"{fmt(-g, 1, True)} par rapport a FIFO ; plus rapide dans "
                f"{r['gagne_vs_fifo']} ; p = {r['p_wilcoxon_vs_fifo']} "
                f"({self.cite_stat(r, 'gain_vs_fifo_pct')}).")
        rows = self.essais('blocking')
        for m in ('fifo', 'consensus', 'greedy_pair', 'greedy_time', 'drl3_hybrid', 'drl3_direct'):
            d = self.per_seed(rows, '6 blocage/min', m, 'taches_echouees')
            if not d:
                continue
            tot = sum(v for v, _ in d.values())
            src = self.add(f'b_echecs_{m}', f'taches echouees, 6 blocages/min, {m}',
                           f'{tot:.0f} au total, {tot / len(d):.2f} par essai',
                           'banc/blocking_essais.csv', [ln for _, ln in d.values()],
                           f'somme de taches_echouees sur {len(d)} graines (150 taches chacune)')
            self.md.append(f'- Echecs {m} : {tot:.0f} taches sur {len(d)} essais '
                           f'({tot / len(d):.2f} par essai) ({src}).')

        self.section('c) Messages par tache : consensus contre FIFO')
        for exp, cond, lab in (('load', 'rho=0.7', 'nominal (rho 0,7, 3 robots, 15 racks)'),
                               ('scale', '20 robots, 150 racks', '20 robots, 150 racks')):
            res = self.paired(exp, cond, 'consensus', 'fifo', 'messages_par_tache',
                              f'c_messages_{exp}', f'messages par tache, {lab}')
            if res:
                self.md.append(f"- {lab} : consensus {fmt(res['a_moy'])} contre FIFO "
                               f"{fmt(res['b_moy'])} messages par tache, ecart "
                               f"{fmt(res['ecart_pct'], 1, True)} ({res['src']}).")

        self.section('d) Consensus contre FIFO, 20 robots et 150 racks')
        r = self.stat_row('scale', '20 robots, 150 racks', 'consensus')
        if r:
            g = fnum(r['gain_vs_fifo_pct'])
            self.md.append(
                f"- Consensus {fmt(fnum(r['moyenne']))} s, soit {fmt(-g, 1, True)} par rapport "
                f"a FIFO ; plus rapide dans {r['gagne_vs_fifo']} ; p = "
                f"{r['p_wilcoxon_vs_fifo']} ({self.cite_stat(r, 'gain_vs_fifo_pct')}).")

        self.section('e) Pertes de messages : 50 % contre 0 % (consensus)')
        rows = self.essais('network')
        for cond in ('perte 0 %', 'perte 50 %'):
            d = self.per_seed(rows, cond, 'consensus', 'conflits_pour_100_taches')
            if d:
                m = statistics.mean(v for v, _ in d.values())
                src = self.add(f'e_conflits_{cond}', f'conflits pour 100 taches, consensus, {cond}',
                               f'{m:.3f}', 'banc/network_essais.csv',
                               [ln for _, ln in d.values()],
                               f'moyenne de conflits_pour_100_taches sur {len(d)} graines')
                self.md.append(f'- Conflits pour 100 taches, {cond} : {fmt(m)} ({src}).')
        a = self.per_seed(rows, 'perte 50 %', 'consensus', 'temps_traitement_moy_s')
        b = self.per_seed(rows, 'perte 0 %', 'consensus', 'temps_traitement_moy_s')
        seeds = sorted(set(a) & set(b))
        if seeds:
            xa, xb = [a[s][0] for s in seeds], [b[s][0] for s in seeds]
            ma, mb = statistics.mean(xa), statistics.mean(xb)
            pv = wilcoxon_p(xa, xb)
            src = self.add('e_variation_temps', 'temps de traitement consensus, perte 50 % vs 0 %',
                           f'{ma:.3f} vs {mb:.3f} s ; variation {100 * (ma - mb) / mb:+.2f} % ; '
                           f'p={pv:.4f}', 'banc/network_essais.csv',
                           [a[s][1] for s in seeds] + [b[s][1] for s in seeds],
                           'temps_traitement_moy_s par graine, Wilcoxon apparie (meme graine)')
            self.md.append(f'- Temps de traitement du consensus : {fmt(ma)} s a 50 % de perte '
                           f'contre {fmt(mb)} s sans perte, variation '
                           f'{fmt(100 * (ma - mb) / mb, 2, True)}, p = {pv:.4f} ({src}).')

        self.section('f) greedy_pair et greedy_time contre FIFO a forte charge (rho = 0,9)')
        for m in ('greedy_pair', 'greedy_time'):
            r = self.stat_row('load', 'rho=0.9', m)
            if r:
                g = fnum(r['gain_vs_fifo_pct'])
                self.md.append(
                    f"- {m} : {fmt(fnum(r['moyenne']))} s, soit {fmt(-g, 1, True)} par rapport "
                    f"a FIFO ; plus rapide dans {r['gagne_vs_fifo']} ; p = "
                    f"{r['p_wilcoxon_vs_fifo']} ({self.cite_stat(r, 'gain_vs_fifo_pct')}).")

    def g(self):
        from warehouse_marl.allocation_benchmark import vs_best_heuristic
        self.section('g) DRL v3 contre la meilleure heuristique (par condition)')
        self.md.append('Meilleure heuristique = plus faible moyenne parmi fifo, consensus, '
                       'greedy_pair, greedy_time, choisie sur les memes essais (ce qui avantage '
                       "l'heuristique). Ecart = (DRL - heuristique) / heuristique.")
        out = []
        for exp in EXPS:
            rel = f'banc/{exp}_essais.csv'
            if not self.exists(rel):
                continue
            rows = read(self.p(rel))
            for r in rows:
                r['temps_traitement_moy_s'] = fnum(r['temps_traitement_moy_s'])
                r['graine'] = int(r['graine'])
            for meth in ('drl3_direct', 'drl3_hybrid'):
                for v in vs_best_heuristic(rows, meth, experience=exp):
                    v['experience'], v['source'] = exp, rel
                    v['lignes_source'] = ' '.join(str(r['_ligne']) for r in rows
                                                 if r['condition'] == v['condition']
                                                 and r['methode'] in (meth, v['meilleure_heuristique']))
                    out.append(v)
        path = self.p('derives/drl_vs_meilleure.csv')
        if out:
            keys = ['experience', 'condition', 'methode', 'meilleure_heuristique', 'drl3_moyenne',
                    'drl3_ic95_bas', 'drl3_ic95_haut', 'heur_moyenne', 'heur_ic95_bas',
                    'heur_ic95_haut', 'gain_pct', 'ecart_ic95_bas', 'ecart_ic95_haut', 'gagne',
                    'p_wilcoxon', 'source', 'lignes_source']
            with open(path, 'w', newline='') as f:
                w = csv.DictWriter(f, fieldnames=keys)
                w.writeheader()
                w.writerows(out)
        for meth in ('drl3_direct', 'drl3_hybrid'):
            self.md += ['', f'### {meth}', '',
                        '| Experience | Condition | Meilleure heuristique | DRL (s) [IC 95 %] | '
                        'Heuristique (s) | Ecart | DRL plus rapide | p | Source |',
                        '|---|---|---|---|---|---|---|---|---|']
            for i, v in enumerate(out):
                if v['methode'] != meth:
                    continue
                self.md.append(
                    f"| {v['experience']} | {v['condition']} | {v['meilleure_heuristique']} | "
                    f"{fmt(v['drl3_moyenne'])} [{fmt(v['drl3_ic95_bas'])} ; "
                    f"{fmt(v['drl3_ic95_haut'])}] | {fmt(v['heur_moyenne'])} | "
                    f"{fmt(-v['gain_pct'], 2, True)} | {v['gagne']} | {v['p_wilcoxon']} | "
                    f"derives/drl_vs_meilleure.csv, ligne {i + 2} |")
            sub = [v for v in out if v['methode'] == meth]
            sig_better = [v for v in sub if v['gain_pct'] > 0 and v['p_wilcoxon'] < 0.05]
            sig_worse = [v for v in sub if v['gain_pct'] < 0 and v['p_wilcoxon'] < 0.05]
            self.md.append(f'\n{meth} : {len(sub)} conditions, significativement meilleur '
                           f'(p < 0,05) dans {len(sig_better)}, significativement moins bon dans '
                           f'{len(sig_worse)} (sans correction pour comparaisons multiples).')

    def h(self):
        self.section("h) Taux d'erreur d'inventaire RFID (60 min, 10 graines)")
        rel, relg = 'rfid/rfid_offline_experiment.csv', 'rfid/rfid_offline_experiment_graines.csv'
        if not self.exists(relg):
            self.md.append('- Non mesure (fichier absent).')
            return
        main = read(self.p(rel)) if self.exists(rel) else []
        last = main[-1] if main else None
        rows = read(self.p(relg))
        for s in ('wms_only', 'rfid_random', 'rfid_adaptive'):
            sub = [r for r in rows if r['strategie'] == s]
            fin = statistics.mean(fnum(r['erreur_fin']) for r in sub)
            half = statistics.mean(fnum(r['erreur_moy_2e_moitie']) for r in sub)
            src = self.add(f'h_{s}', f"taux d'erreur RFID {s}",
                           f'fin {fin:.4f} ; 2e moitie {half:.4f}', relg, [r['_ligne'] for r in sub],
                           f'moyenne sur {len(sub)} graines de erreur_fin et erreur_moy_2e_moitie')
            fin_main = (f", ligne {last['_ligne']} de {rel} (minute {last['minute']}) : "
                        f"{fnum(last[s]) * 100:.1f} %") if last else ''
            self.md.append(f'- {s} : fin {fin * 100:.1f} %, moyenne de la 2e moitie '
                           f'{half * 100:.1f} % ({src}{fin_main}).')

    def i(self):
        self.section('i) Simulation Gazebo (systeme complet)')
        rel = 'gazebo/synthese_taches.csv'
        if not self.exists(rel):
            self.md.append('- Non mesure (voir CONFORMITE_CAHIER.md et le rapport de session).')
            return
        for r in read(self.p(rel)):
            reads = 'n/d'
            rr = f"gazebo/rfid_{r['mode']}.csv"
            if self.exists(rr):
                rf = read(self.p(rr))
                if rf:
                    reads = f"{rf[-1]['reads']} ({rr}, ligne {rf[-1]['_ligne']}, colonne reads)"
            self.md.append(
                f"- {r['mode']} : {r['terminees']} taches terminees, {r['echouees']} echouees, "
                f"{r['en_cours_a_la_fin']} en cours a la fin, temps moyen "
                f"{r['temps_moyen_s']} s [{r['ic95_bas_s']} ; {r['ic95_haut_s']}] "
                f"({rel}, ligne {r['_ligne']}) ; lectures RFID cumulees : {reads}.")

    def j(self):
        self.section("j) Indicateurs d'entrainement DRL v3")
        for rel, lab in (('entrainement_synthetique/indicators_v3.csv', 'synthetique'),
                         ('entrainement_donnees_reelles/indicators_v3.csv', 'donnees reelles')):
            if not self.exists(rel):
                self.md.append(f'- {lab} : fichier absent.')
                continue
            self.md += ['', f'### Entrainement {lab}', '',
                        '| Graine | Meilleur episode | Validation (s) | Episode 0 (s) | '
                        'vs greedy_pair | Validation finale (s) | Q stable | Source |',
                        '|---|---|---|---|---|---|---|---|']
            for r in read(self.p(rel)):
                if r['graine'] == 'toutes':
                    self.md.append(f"\nToutes graines : Q stable pour toutes = "
                                   f"{r.get('q_stable_toutes_graines', 'n/d')} ({rel}, "
                                   f"ligne {r['_ligne']}).")
                    continue
                self.md.append(
                    f"| {r['graine']} | {r['episode_meilleur']} | {r['meilleure_val_s']} | "
                    f"{r['val_episode0_s']} | {r['gain_val_vs_greedy_pair_pct']} % | "
                    f"{r['val_finale_s']} | {r['q_stable']} (derive {r['q_derive_20pct']}) | "
                    f"{rel}, ligne {r['_ligne']} |")

    def comparaison(self):
        """Etape 8a : criteres du sujet, systeme propose contre heuristiques."""
        out = []
        for exp in EXPS:
            rel = f'banc/{exp}_statistiques.csv'
            if not self.exists(rel):
                continue
            for r in read(self.p(rel)):
                if r['methode'] not in SYSTEMS:
                    continue
                for ref in REFS:
                    if f'gain_vs_{ref}_pct' not in r or r[f'gain_vs_{ref}_pct'] == '':
                        continue
                    out.append({'critere': 'temps de traitement (s)', 'experience': exp,
                                'condition': r['condition'], 'systeme': r['methode'],
                                'reference': ref, 'moyenne': r['moyenne'],
                                'ic95': f"[{r['ic95_bas']} ; {r['ic95_haut']}]",
                                'gain_pct': r[f'gain_vs_{ref}_pct'],
                                'systeme_meilleur': r[f'gagne_vs_{ref}'],
                                'p_wilcoxon': r[f'p_wilcoxon_vs_{ref}'],
                                'source': f"{rel}, ligne {r['_ligne']}"})
        # taux de taches echouees par methode
        for exp in EXPS:
            rows = self.essais(exp)
            for cond in dict.fromkeys(r['condition'] for r in rows):
                for sysm in SYSTEMS:
                    a = self.per_seed(rows, cond, sysm, 'taches_echouees')
                    if not a:
                        continue
                    for ref in REFS:
                        b = self.per_seed(rows, cond, ref, 'taches_echouees')
                        seeds = sorted(set(a) & set(b))
                        if not seeds:
                            continue
                        xa, xb = [a[s][0] for s in seeds], [b[s][0] for s in seeds]
                        lo, hi = bootstrap_ci(xa)
                        mb = statistics.mean(xb)
                        out.append({
                            'critere': 'taches echouees par essai (sur 150)', 'experience': exp,
                            'condition': cond, 'systeme': sysm, 'reference': ref,
                            'moyenne': round(statistics.mean(xa), 3), 'ic95': f'[{lo:.2f} ; {hi:.2f}]',
                            'gain_pct': round(100 * (mb - statistics.mean(xa)) / mb, 1) if mb else 'n/d',
                            'systeme_meilleur': f'{sum(x < y for x, y in zip(xa, xb))}/{len(seeds)}',
                            'p_wilcoxon': round(wilcoxon_p(xa, xb), 4),
                            'source': f"banc/{exp}_essais.csv, lignes "
                                      + ' '.join(str(v[1]) for s in seeds for v in (a[s], b[s]))})
        # taux d'erreur d'inventaire : RFID adaptatif contre WMS seul
        relg = 'rfid/rfid_offline_experiment_graines.csv'
        if self.exists(relg):
            rows = read(self.p(relg))
            for col, lab in (('erreur_fin', 'fin (60 min)'), ('erreur_moy_2e_moitie', '2e moitie')):
                for ref in ('wms_only', 'rfid_random'):
                    a = {int(r['graine']): (fnum(r[col]), r['_ligne']) for r in rows
                         if r['strategie'] == 'rfid_adaptive'}
                    b = {int(r['graine']): (fnum(r[col]), r['_ligne']) for r in rows
                         if r['strategie'] == ref}
                    seeds = sorted(set(a) & set(b))
                    xa, xb = [a[s][0] for s in seeds], [b[s][0] for s in seeds]
                    lo, hi = bootstrap_ci(xa)
                    mb = statistics.mean(xb)
                    out.append({'critere': f"taux d'erreur d'inventaire, {lab}",
                                'experience': 'rfid_offline_experiment', 'condition': '60 min',
                                'systeme': 'rfid_adaptive', 'reference': ref,
                                'moyenne': round(statistics.mean(xa), 4),
                                'ic95': f'[{lo:.4f} ; {hi:.4f}]',
                                'gain_pct': round(100 * (mb - statistics.mean(xa)) / mb, 1),
                                'systeme_meilleur': f'{sum(x < y for x, y in zip(xa, xb))}/{len(seeds)}',
                                'p_wilcoxon': round(wilcoxon_p(xa, xb), 4),
                                'source': f"{relg}, lignes "
                                          + ' '.join(str(v[1]) for s in seeds for v in (a[s], b[s]))})
        with open(self.p('derives/comparaison_cahier.csv'), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(out[0]))
            w.writeheader()
            w.writerows(out)
        self.section('Comparaison selon le cahier des charges (etape 8a)')
        self.md.append('Fichier complet : derives/comparaison_cahier.csv (une ligne par '
                       'experience x condition x systeme x reference, avec la source). '
                       'gain_pct > 0 = le systeme fait mieux que la reference.')
        tt = [r for r in out if r['critere'].startswith('temps') and r['systeme'] == 'drl3_hybrid']
        if tt:
            sig_b = sum(1 for r in tt if fnum(r['gain_pct']) > 0 and fnum(r['p_wilcoxon']) < 0.05)
            sig_w = sum(1 for r in tt if fnum(r['gain_pct']) < 0 and fnum(r['p_wilcoxon']) < 0.05)
            self.md.append(f'- Temps de traitement, drl3_hybrid (consensus + biais DRL v3) contre '
                           f'fifo / greedy_pair / greedy_time : {len(tt)} comparaisons, '
                           f'significativement meilleur dans {sig_b}, significativement moins bon '
                           f'dans {sig_w}.')
        er = [r for r in out if r['critere'].startswith("taux d'erreur")]
        for r in er:
            self.md.append(f"- {r['critere']} : rfid_adaptive {r['moyenne']} {r['ic95']} contre "
                           f"{r['reference']} : gain {r['gain_pct']} %, meilleur dans "
                           f"{r['systeme_meilleur']}, p = {r['p_wilcoxon']} "
                           f"(derives/comparaison_cahier.csv, ligne {out.index(r) + 2}).")

    def avant_apres(self):
        rel_av = 'banc_avant_correction/allocation_benchmark_statistiques.csv'
        if not self.exists(rel_av):
            return
        av = read(self.p(rel_av))
        out = []
        for exp in ('blocking', 'network'):
            ap = read(self.p(f'banc/{exp}_statistiques.csv'))
            for r in ap:
                old = next((o for o in av if o['experience'] == exp
                            and o['condition'] == r['condition'] and o['methode'] == r['methode']),
                           None)
                if old is None:
                    continue
                out.append({'experience': exp, 'condition': r['condition'],
                            'methode': r['methode'],
                            'avant_moyenne': old['moyenne'], 'apres_moyenne': r['moyenne'],
                            'avant_gain_vs_fifo_pct': old.get('gain_vs_fifo_pct', ''),
                            'apres_gain_vs_fifo_pct': r.get('gain_vs_fifo_pct', ''),
                            'avant_p_vs_fifo': old.get('p_wilcoxon_vs_fifo', ''),
                            'apres_p_vs_fifo': r.get('p_wilcoxon_vs_fifo', ''),
                            'source_avant': f"{rel_av}, ligne {old['_ligne']}",
                            'source_apres': f"banc/{exp}_statistiques.csv, ligne {r['_ligne']}"})
        with open(self.p('derives/avant_apres_equite.csv'), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(out[0]))
            w.writeheader()
            w.writerows(out)
        self.section('Equite du banc : blocking et network avant / apres correction')
        self.md += ['| Experience | Condition | Methode | Avant (s) | Apres (s) | '
                    'Gain vs FIFO avant | apres | p vs FIFO avant | apres |',
                    '|---|---|---|---|---|---|---|---|---|']
        for r in out:
            if r['methode'] in ('fifo', 'consensus', 'greedy_pair', 'greedy_time'):
                self.md.append(
                    f"| {r['experience']} | {r['condition']} | {r['methode']} | "
                    f"{r['avant_moyenne']} | {r['apres_moyenne']} | {r['avant_gain_vs_fifo_pct']} | "
                    f"{r['apres_gain_vs_fifo_pct']} | {r['avant_p_vs_fifo']} | "
                    f"{r['apres_p_vs_fifo']} |")
        self.md.append('\nSource : derives/avant_apres_equite.csv (avec les lignes d origine).')

    def write(self):
        with open(self.p('derives/valeurs_derivees.csv'), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['id', 'description', 'valeur', 'fichier_source',
                                              'lignes_source', 'calcul'])
            w.writeheader()
            w.writerows(self.derived)
        with open(self.p('VALEURS_MEMOIRE.md'), 'w') as f:
            f.write('\n'.join(self.md) + '\n')
        print(f"Ecrit : {self.p('VALEURS_MEMOIRE.md')} et {self.p('derives')}/")


if __name__ == '__main__':
    Report(sys.argv[1] if len(sys.argv) > 1 else '.').run()
