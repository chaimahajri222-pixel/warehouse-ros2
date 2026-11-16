"""Diagnostics des modeles drl_idle6 retenus (petit et grand), sur les scenarios
de VALIDATION uniquement (aucune graine de test, aucun reentrainement).

    python diagnostics_v6.py --drl-dir ~/warehouse_ws/drl_v6 \
        --out ~/warehouse_ws/resultats_v6/diagnostics

Chaque modele est rejoue (epsilon = 0) sur ses scenarios de validation
(train_v6.val_scenarios('idle6', taille)), avec SA regle de recompense
d'entrainement (petit : individuelle, decisions sans tache -> 0 ; grand :
equipe, decisions sans tache tronquees ; ecarts 4 et 5 de PROTOCOLE_V6.md).
Pour chaque decision d'attente on journalise : le noeud choisi par le DRL, le
noeud que la couverture seule choisirait DANS LE MEME ETAT, Q du noeud choisi,
le terme a priori x[0] et la correction f_theta = Q - x[0], et les recompenses
observees (memes valeurs que celles vues a l'entrainement).

Sorties : decisions_<modele>.csv, verification_validation.csv, accord.csv,
calibration_bins.csv, calibration_resume.csv, correction_resume.csv,
fig_diag_accord_v6.png, fig_diag_calibration_v6.png, fig_diag_correction_v6.png,
DIAGNOSTICS.md.
"""
import argparse
import csv
import os
import statistics

import numpy as np

MODELS = (('petit', 'zero', 'individuelle'), ('grand', 'ignorer', 'equipe'))
GAMMA = 0.9
COLORS = {'petit': '#2a78d6', 'grand': '#eb6834'}
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
SEQ = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95']


def collect(drl_dir, taille, sans_tache, recompense):
    import torch
    torch.set_num_threads(1)
    from warehouse_marl.drl.train_v6 import make_sim6, val_scenarios
    from warehouse_marl.drl.v4_dqn import load_v4_model
    path = os.path.join(drl_dir, f'idle6_{taille}', 'selected_idle6.pt')
    agent = load_v4_model(path, 'idle6')
    rows, checks = [], []
    for si, sc in enumerate(val_scenarios('idle6', taille)):
        dec = []                     # decisions de ce scenario
        by_key = {}                  # octets de la caracteristique choisie -> indices

        def cb(feat, reward, next_feats, terminal):
            k = np.asarray(feat, dtype=np.float32).tobytes()
            for i in by_key.get(k, []):
                if dec[i]['recompense'] is None:
                    dec[i]['recompense'] = float(reward)
                    dec[i]['terminale'] = bool(terminal)
                    return
            raise RuntimeError('transition sans decision correspondante')

        sim = make_sim6(sc, 'drl_idle6', agent, cb=cb)
        sim.idle6_unrewarded, sim.idle6_reward = sans_tache, recompense
        orig = sim.idle6_candidates

        def wrapped(r, orig=orig, sim=sim):
            cands, feats = orig(r)
            q = agent.scores(feats)
            j = int(np.argmax(q))
            h = int(np.argmax(feats[:, 15]))          # est_couverture
            dec.append({
                'modele': taille, 'scenario': si, 'robots': sc['robots'],
                'racks': sc['dims'][0] * sc['dims'][1], 'allocation': sc['alloc'],
                'graine_validation': sc['seed'], 'robot': r.rid, 't_s': round(sim.t, 2),
                'noeud_robot': r.node, 'choix_drl': cands[j], 'choix_couverture': cands[h],
                'couverture_reste': cands[h] == r.node, 'drl_reste': cands[j] == r.node,
                'meme_noeud': j == h, 'q_choisi': float(q[j]), 'prior_choisi': float(feats[j, 0]),
                'correction_choisi': float(q[j] - feats[j, 0]),
                'q_couverture': float(q[h]), 'prior_couverture': float(feats[h, 0]),
                't_ref_s': round(sim.reward_scale_s(), 3), 'recompense': None,
                'terminale': None})
            by_key.setdefault(feats[j].astype(np.float32).tobytes(), []).append(len(dec) - 1)
            return cands, feats

        sim.idle6_candidates = wrapped
        m = sim.run()
        checks.append({'modele': taille, 'scenario': si,
                       'temps_traitement_moy_s': round(m['temps_traitement_moy_s'], 4),
                       'decisions': len(dec)})
        # retour escompte observe (meme regle qu'a l'entrainement), par robot
        for rid in sorted({d['robot'] for d in dec}):
            seq = [d for d in dec if d['robot'] == rid]
            g, n_after = None, 0
            for d in reversed(seq):
                if d['recompense'] is None:          # decision tronquee (grand)
                    g, n_after = None, 0
                    d['retour_escompte'] = ''
                    d['decisions_suivantes'] = 0
                    continue
                if d['terminale'] or g is None:
                    g = d['recompense']
                    n_after = 0
                else:
                    g = d['recompense'] + GAMMA * g
                    n_after += 1
                d['retour_escompte'] = g
                d['decisions_suivantes'] = n_after
        rows += dec
    return rows, checks


def write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def style(ax):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--drl-dir', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    drl_dir, out = os.path.expanduser(a.drl_dir), os.path.expanduser(a.out)
    os.makedirs(out, exist_ok=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 9, 'text.color': INK, 'axes.labelcolor': INK,
                         'axes.titlecolor': INK, 'figure.facecolor': '#fcfcfb',
                         'axes.facecolor': '#fcfcfb'})

    data, all_checks = {}, []
    for taille, sans_tache, recompense in MODELS:
        rows, checks = collect(drl_dir, taille, sans_tache, recompense)
        data[taille] = rows
        all_checks += checks
        write_csv(os.path.join(out, f'decisions_{taille}.csv'), rows)
    # verification : memes temps de traitement que la validation du point retenu
    for taille, _, _ in MODELS:
        sel = [r for r in csv.DictReader(open(os.path.join(
            drl_dir, f'idle6_{taille}', 'selection_idle6.csv'))) if r['retenu'] == 'True'][0]
        vl = list(csv.DictReader(open(os.path.join(drl_dir, f'idle6_{taille}',
                                                   sel['fichier_val']))))
        vrow = vl[int(sel['ligne_val']) - 2]
        for c in all_checks:
            if c['modele'] == taille:
                c['validation_journal_s'] = float(vrow[f"sc{c['scenario']}"])
                c['identique'] = abs(c['validation_journal_s'] - c['temps_traitement_moy_s']) < 1e-3
    write_csv(os.path.join(out, 'verification_validation.csv'), all_checks)

    # ---- 1. accord ------------------------------------------------------------
    acc = []
    for taille, _, _ in MODELS:
        rows = data[taille]
        n = len(rows)
        cell = {(cr, dr): sum(1 for r in rows if r['couverture_reste'] == cr
                              and r['drl_reste'] == dr) for cr in (True, False) for dr in (True, False)}
        both_move_diff = sum(1 for r in rows if not r['couverture_reste'] and not r['drl_reste']
                             and not r['meme_noeud'])
        modif = sum(1 for r in rows if not r['meme_noeud'])
        acc.append({'modele': taille, 'decisions': n,
                    'couv_reste_drl_reste': cell[(True, True)],
                    'couv_reste_drl_bouge': cell[(True, False)],
                    'couv_bouge_drl_reste': cell[(False, True)],
                    'couv_bouge_drl_bouge': cell[(False, False)],
                    'dont_bouge_bouge_noeud_different': both_move_diff,
                    'decisions_modifiees': modif,
                    'pct_decisions_modifiees': round(100 * modif / n, 2)})
    write_csv(os.path.join(out, 'accord.csv'), acc)
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.2))
    for ax, r in zip(axs, acc):
        m = np.array([[r['couv_reste_drl_reste'], r['couv_reste_drl_bouge']],
                      [r['couv_bouge_drl_reste'], r['couv_bouge_drl_bouge']]])
        vmax = max(1, m.max())
        cmap = matplotlib.colors.ListedColormap(SEQ)
        ax.imshow(m, cmap=cmap, vmin=0, vmax=vmax)
        for (i, k), v in np.ndenumerate(m):
            pct = 100 * v / r['decisions']
            txt = f'{v}\n({pct:.1f} %)'
            if (i, k) == (1, 1):
                txt += f"\ndont {r['dont_bouge_bouge_noeud_different']} vers\nun autre noeud"
            ax.text(k, i, txt, ha='center', va='center', fontsize=9,
                    color='white' if v > 0.55 * vmax else INK)
        ax.set_xticks([0, 1], ['DRL : reste', 'DRL : se deplace'])
        ax.set_yticks([0, 1], ['couverture :\nreste', 'couverture :\nse deplace'])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0, colors=INK2)
        ax.set_title(f"Modele {r['modele']} : {r['decisions']} decisions\n"
                     f"{r['pct_decisions_modifiees']} % de noeuds differents de la couverture",
                     fontsize=10)
    fig.suptitle('drl_idle6 contre la couverture seule, dans le meme etat (scenarios de validation)',
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(out, 'fig_diag_accord_v6.png'), dpi=140)
    plt.close(fig)

    # ---- 2. calibration -----------------------------------------------------------
    bins_out, resume = [], []
    fig, axs = plt.subplots(2, 2, figsize=(10.5, 8.2))
    for ri, (taille, _, _) in enumerate(MODELS):
        rows = data[taille]
        for ci, (key, lab) in enumerate((
                ('recompense', 'cout observe jusqu a la decision suivante\n(recompense d un pas)'),
                ('retour_escompte', 'retour escompte observe (gamma = 0,9),\ntronque a la fin de l episode'))):
            pts = [(r['q_choisi'], float(r[key])) for r in rows
                   if r[key] not in ('', None)]
            ax = axs[ri][ci]
            style(ax)
            x = np.array([q for q, _ in pts])
            y = np.array([v for _, v in pts])
            ax.scatter(x, y, s=9, color=COLORS[taille], alpha=0.25, lw=0)
            edges = np.unique(np.quantile(x, np.linspace(0, 1, 11)))
            mids, med, lo, hi = [], [], [], []
            for b in range(len(edges) - 1):
                sel = (x >= edges[b]) & ((x < edges[b + 1]) if b < len(edges) - 2 else (x <= edges[b + 1]))
                if sel.sum() < 5:
                    continue
                mids.append(float(np.median(x[sel])))
                med.append(float(np.median(y[sel])))
                lo.append(float(np.quantile(y[sel], 0.25)))
                hi.append(float(np.quantile(y[sel], 0.75)))
                bins_out.append({'modele': taille, 'cible': key, 'classe': b,
                                 'q_min': round(float(edges[b]), 5),
                                 'q_max': round(float(edges[b + 1]), 5), 'n': int(sel.sum()),
                                 'q_mediane': round(mids[-1], 5), 'observe_mediane': round(med[-1], 5),
                                 'observe_q25': round(lo[-1], 5), 'observe_q75': round(hi[-1], 5)})
            ax.fill_between(mids, lo, hi, color=INK2, alpha=0.18, lw=0, label='IQR 25-75 %')
            ax.plot(mids, med, color=INK, lw=2, marker='o', ms=4, label='mediane par classe de Q')
            if key == 'retour_escompte':
                lims = [min(x.min(), y.min()), max(x.max(), y.max())]
                ax.plot(lims, lims, color=INK2, lw=1, ls='--', label='Q = observe')
            from scipy.stats import spearmanr
            rho = float(spearmanr(x, y).correlation)
            bias = float(np.mean(x - y))
            resume.append({'modele': taille, 'cible': key, 'n': len(x),
                           'decisions_sans_valeur': len(rows) - len(x),
                           'spearman_q_observe': round(rho, 4),
                           'biais_moyen_q_moins_observe': round(bias, 5),
                           'q_moyen': round(float(x.mean()), 5),
                           'observe_moyen': round(float(y.mean()), 5)})
            ax.set_xlabel('Q predit au noeud choisi (unites de recompense)')
            ax.set_ylabel(lab, fontsize=8)
            ax.set_title(f'Modele {taille} : {len(x)} decisions, Spearman {rho:.2f}', fontsize=10)
            ax.legend(fontsize=7, frameon=False, loc='upper left')
    fig.suptitle('Calibration de Q (drl_idle6, scenarios de validation) : nuage, mediane et IQR '
                 'par decile de Q', fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(out, 'fig_diag_calibration_v6.png'), dpi=140)
    plt.close(fig)
    write_csv(os.path.join(out, 'calibration_bins.csv'), bins_out)
    write_csv(os.path.join(out, 'calibration_resume.csv'), resume)

    # ---- 3. correction f_theta ------------------------------------------------
    corr = []
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.2))
    for ax, (taille, _, _) in zip(axes[1], MODELS):
        # ecart de correction : ce qui fait devier de la couverture (le niveau
        # absolu de f_theta est un decalage commun a tous les candidats)
        d = np.array([r['correction_choisi'] - (r['q_couverture'] - r['prior_couverture'])
                      for r in data[taille]])
        style(ax)
        ax.hist(d, bins=40, color=COLORS[taille], edgecolor='#fcfcfb', linewidth=0.6)
        ax.axvline(0, color=INK2, lw=1, ls='--')
        ax.set_xlabel('f_theta(noeud choisi) - f_theta(noeud de la couverture)')
        ax.set_ylabel('decisions')
        ax.set_title(f'Modele {taille} : ecart de correction\n(0 = meme noeud que la couverture)',
                     fontsize=9)
        corr.append({'modele': taille, 'grandeur': 'ecart_correction_choisi_moins_couverture',
                     'n': len(d), 'moyenne': round(float(d.mean()), 5),
                     'mediane': round(float(np.median(d)), 5), 'ecart_type': round(float(d.std()), 5),
                     'p05': round(float(np.quantile(d, 0.05)), 5),
                     'p95': round(float(np.quantile(d, 0.95)), 5),
                     'min': round(float(d.min()), 5), 'max': round(float(d.max()), 5),
                     'part_positive_pct': round(100 * float((d > 1e-6).mean()), 2),
                     'abs_moyen_prior_choisi': ''})
    for ax, (taille, _, _) in zip(axes[0], MODELS):
        f = np.array([r['correction_choisi'] for r in data[taille]])
        style(ax)
        ax.hist(f, bins=40, color=COLORS[taille], edgecolor='#fcfcfb', linewidth=0.6)
        ax.axvline(0, color=INK2, lw=1, ls='--')
        ax.axvline(float(np.median(f)), color=INK, lw=1.5)
        ax.text(float(np.median(f)), ax.get_ylim()[1] * 0.95, f'  mediane {np.median(f):.3f}',
                fontsize=8, color=INK, va='top')
        ax.set_xlabel('f_theta = Q - terme de couverture, au noeud choisi')
        ax.set_ylabel('decisions')
        ax.set_title(f'Modele {taille} ({len(f)} decisions)', fontsize=10)
        corr.append({'modele': taille, 'grandeur': 'correction_au_noeud_choisi',
                     'n': len(f), 'moyenne': round(float(f.mean()), 5),
                     'mediane': round(float(np.median(f)), 5),
                     'ecart_type': round(float(f.std()), 5),
                     'p05': round(float(np.quantile(f, 0.05)), 5),
                     'p95': round(float(np.quantile(f, 0.95)), 5),
                     'min': round(float(f.min()), 5), 'max': round(float(f.max()), 5),
                     'part_positive_pct': round(100 * float((f > 0).mean()), 2),
                     'abs_moyen_prior_choisi': round(float(np.mean([abs(r['prior_choisi'])
                                                                    for r in data[taille]])), 5)})
    fig.suptitle('Correction apprise f_theta au noeud choisi (drl_idle6, scenarios de validation)',
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(out, 'fig_diag_correction_v6.png'), dpi=140)
    plt.close(fig)
    write_csv(os.path.join(out, 'correction_resume.csv'), corr)
    print('ok', out)


if __name__ == '__main__':
    main()
