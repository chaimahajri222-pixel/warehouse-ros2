# VALEURS_V6 : toutes les valeurs, avec leur fichier et leur ligne

Genere par `src/warehouse_marl/scripts/rapport_v6.py` a partir des CSV du dossier. Ligne 1 = en-tete du CSV ; "l.N" = N-ieme ligne du fichier. Protocole : `PROTOCOLE_V6.md` (copie dans ce dossier). Graines de test v6 : 2 000 003 + 1 013 k, k = 0..19. Victoire = p de Holm < 0,05 et ecart moyen < 0.

## 1. Selection des modeles (validation uniquement)

### Phase A, modele petit (15 et 40 racks) : drl_idle6

| graine | instant (min) | episode | ecart relatif de validation | temps de validation (s) | reprises | retenu | source |
|---|---|---|---|---|---|---|---|
| 0 | 0.0 | 0 | +1.490 % | 42.759 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.2 |
| 0 | 10.0 | 1930 | +2.895 % | 43.441 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.3 |
| 0 | 20.0 | 3760 | +0.068 % | 42.063 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.4 |
| 0 | 30.0 | 5632 | -0.776 % | 41.778 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.5 |
| 0 | 40.0 | 7514 | -0.847 % | 41.818 | 0 | **oui** | `entrainement_idle6_petit/selection_idle6.csv` l.6 |
| 1 | 0.0 | 0 | +1.490 % | 42.759 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.7 |
| 1 | 10.0 | 2009 | -0.234 % | 41.897 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.8 |
| 1 | 20.0 | 3935 | +0.570 % | 42.355 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.9 |
| 1 | 30.0 | 5854 | +0.213 % | 42.017 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.10 |
| 1 | 40.0 | 7728 | -0.047 % | 41.812 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.11 |
| 2 | 0.0 | 0 | +1.490 % | 42.759 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.12 |
| 2 | 10.0 | 2009 | +0.328 % | 41.893 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.13 |
| 2 | 20.0 | 3907 | +0.817 % | 42.333 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.14 |
| 2 | 30.0 | 5788 | -0.399 % | 41.750 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.15 |
| 2 | 40.0 | 7651 | +2.050 % | 42.978 | 0 |  | `entrainement_idle6_petit/selection_idle6.csv` l.16 |

- Graine 0 : 7514 episodes d'entrainement en 40.0 min (`entrainement_idle6_petit/train_log_seed0.csv` l.7515).
- Graine 1 : 7728 episodes d'entrainement en 40.0 min (`entrainement_idle6_petit/train_log_seed1.csv` l.7729).
- Graine 2 : 7651 episodes d'entrainement en 40.0 min (`entrainement_idle6_petit/train_log_seed2.csv` l.7652).
- Heuristiques concurrentes sur les scenarios de validation : `entrainement_idle6_petit/val_ref.csv` (18 scenarios).

### Phase A, modele grand (150 racks) : drl_idle6

| graine | instant (min) | episode | ecart relatif de validation | temps de validation (s) | reprises | retenu | source |
|---|---|---|---|---|---|---|---|
| 0 | 0.0 | 0 | +0.000 % | 54.963 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.2 |
| 0 | 10.01 | 629 | +2.797 % | 56.395 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.3 |
| 0 | 20.01 | 1242 | +1.976 % | 55.991 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.4 |
| 0 | 30.01 | 1856 | -0.125 % | 55.013 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.5 |
| 0 | 40.01 | 2464 | -0.469 % | 54.997 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.6 |
| 0 | 50.01 | 3058 | -0.219 % | 55.535 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.7 |
| 0 | 60.01 | 3585 | +0.009 % | 54.663 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.8 |
| 1 | 0.0 | 0 | +0.000 % | 54.963 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.9 |
| 1 | 10.02 | 529 | +1.143 % | 55.721 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.10 |
| 1 | 20.01 | 1056 | +0.626 % | 55.412 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.11 |
| 1 | 30.0 | 1657 | -1.503 % | 54.413 | 0 | **oui** | `entrainement_idle6_grand/selection_idle6.csv` l.12 |
| 1 | 40.0 | 2252 | -0.720 % | 54.822 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.13 |
| 1 | 50.01 | 2857 | -1.136 % | 54.507 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.14 |
| 1 | 60.01 | 3469 | -0.673 % | 54.718 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.15 |
| 2 | 0.0 | 0 | +0.000 % | 54.963 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.16 |
| 2 | 10.01 | 634 | +0.368 % | 55.377 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.17 |
| 2 | 20.01 | 1265 | +1.892 % | 55.768 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.18 |
| 2 | 30.01 | 1891 | +4.050 % | 56.590 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.19 |
| 2 | 40.0 | 2486 | -0.575 % | 54.453 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.20 |
| 2 | 50.01 | 3068 | -0.552 % | 54.719 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.21 |
| 2 | 60.01 | 3680 | +0.962 % | 55.521 | 0 |  | `entrainement_idle6_grand/selection_idle6.csv` l.22 |

- Graine 0 : 3585 episodes d'entrainement en 60.01 min (`entrainement_idle6_grand/train_log_seed0.csv` l.3586).
- Graine 1 : 3469 episodes d'entrainement en 60.01 min (`entrainement_idle6_grand/train_log_seed1.csv` l.3470).
- Graine 2 : 3680 episodes d'entrainement en 60.01 min (`entrainement_idle6_grand/train_log_seed2.csv` l.3681).
- Heuristiques concurrentes sur les scenarios de validation : `entrainement_idle6_grand/val_ref.csv` (12 scenarios).

### Phase B : drl_route6

| graine | instant (min) | episode | ecart relatif de validation | temps de validation (s) | reprises | retenu | source |
|---|---|---|---|---|---|---|---|
| 0 | 0.0 | 0 | +0.602 % | 45.511 | 0 |  | `entrainement_route6/selection_route6.csv` l.2 |
| 0 | 10.02 | 55 | +1.927 % | 45.900 | 0 |  | `entrainement_route6/selection_route6.csv` l.3 |
| 0 | 20.07 | 143 | +2.822 % | 46.296 | 0 |  | `entrainement_route6/selection_route6.csv` l.4 |
| 0 | 30.13 | 235 | +1.276 % | 45.737 | 0 |  | `entrainement_route6/selection_route6.csv` l.5 |
| 0 | 40.06 | 329 | +0.806 % | 45.578 | 0 |  | `entrainement_route6/selection_route6.csv` l.6 |
| 0 | 50.16 | 432 | +0.970 % | 45.637 | 0 |  | `entrainement_route6/selection_route6.csv` l.7 |
| 0 | 60.02 | 549 | +1.005 % | 45.647 | 0 |  | `entrainement_route6/selection_route6.csv` l.8 |
| 1 | 0.0 | 0 | +0.602 % | 45.511 | 0 |  | `entrainement_route6/selection_route6.csv` l.9 |
| 1 | 10.01 | 54 | +2.641 % | 46.258 | 0 |  | `entrainement_route6/selection_route6.csv` l.10 |
| 1 | 20.0 | 140 | +2.447 % | 46.166 | 0 |  | `entrainement_route6/selection_route6.csv` l.11 |
| 1 | 30.28 | 232 | +0.846 % | 45.579 | 0 |  | `entrainement_route6/selection_route6.csv` l.12 |
| 1 | 40.06 | 333 | +0.405 % | 45.423 | 0 |  | `entrainement_route6/selection_route6.csv` l.13 |
| 1 | 50.08 | 420 | +0.502 % | 45.480 | 0 |  | `entrainement_route6/selection_route6.csv` l.14 |
| 1 | 60.02 | 517 | +0.744 % | 45.553 | 0 |  | `entrainement_route6/selection_route6.csv` l.15 |
| 2 | 0.0 | 0 | +0.602 % | 45.511 | 0 |  | `entrainement_route6/selection_route6.csv` l.16 |
| 2 | 10.1 | 72 | +1.505 % | 45.845 | 0 |  | `entrainement_route6/selection_route6.csv` l.17 |
| 2 | 20.17 | 150 | +2.581 % | 46.198 | 0 |  | `entrainement_route6/selection_route6.csv` l.18 |
| 2 | 30.01 | 237 | -0.000 % | 45.265 | 0 | **oui** | `entrainement_route6/selection_route6.csv` l.19 |
| 2 | 40.2 | 346 | +1.104 % | 45.706 | 0 |  | `entrainement_route6/selection_route6.csv` l.20 |
| 2 | 50.19 | 461 | +6.585 % | 47.700 | 0 |  | `entrainement_route6/selection_route6.csv` l.21 |
| 2 | 60.1 | 556 | +1.668 % | 45.920 | 0 |  | `entrainement_route6/selection_route6.csv` l.22 |

- Graine 0 : 549 episodes d'entrainement en 60.02 min (`entrainement_route6/train_log_seed0.csv` l.550).
- Graine 1 : 517 episodes d'entrainement en 60.02 min (`entrainement_route6/train_log_seed1.csv` l.518).
- Graine 2 : 556 episodes d'entrainement en 60.1 min (`entrainement_route6/train_log_seed2.csv` l.557).
- Heuristiques concurrentes sur les scenarios de validation : `entrainement_route6/val_ref.csv` (12 scenarios).

### Phase C : drl_alloc6

*Pas de selection pour alloc6 : entrainement arrete, aucun modele retenu (ecart 8 de PROTOCOLE_V6.md).*

Lancements interrompus (ecarts 3 a 6 de `PROTOCOLE_V6.md`, ni selection ni test) : journaux de validation dans `lancements_interrompus/`.

## 2. Phase A : drl_idle6 contre la meilleure des 3 heuristiques d attente v4 et contre la couverture (famille A, 28 tests, Holm ; ecart 2)

| experience | condition | allocation | DRL (s) [IC95] | concurrent (s) [IC95] | ecart (s) [IC95] | gain | gagnes | echecs DRL/conc. | p Wilcoxon | p Holm | verdict | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | 27.274 [25.098 ; 29.547] | centre_de_demande 28.939 [26.583 ; 31.414] | -1.666 [-2.53 ; -0.906] | 5.76 % | 17/20 | 0/0 | 0.000322 | 0.008059 | **victoire** | `principal_idle6.csv` l.2 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | 27.274 [25.098 ; 29.547] | couverture 28.458 [26.286 ; 30.764] | -1.184 [-1.814 ; -0.587] | 4.16 % | 16/20 | 0/0 | 0.001017 | 0.02033 | **victoire** | `principal_idle6.csv` l.3 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | 27.274 [25.098 ; 29.547] | centre_de_demande 28.939 [26.583 ; 31.414] | -1.666 [-2.53 ; -0.906] | 5.76 % | 17/20 | 0/0 | 0.000322 | 0.008059 | **victoire** | `principal_idle6.csv` l.4 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | 27.274 [25.098 ; 29.547] | couverture 28.458 [26.286 ; 30.764] | -1.184 [-1.814 ; -0.587] | 4.16 % | 16/20 | 0/0 | 0.001017 | 0.02033 | **victoire** | `principal_idle6.csv` l.5 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | 37.485 [32.832 ; 42.957] | centre_de_demande 39.094 [34.407 ; 45.016] | -1.61 [-2.513 ; -0.803] | 4.12 % | 15/20 | 0/0 | 0.000708 | 0.01628 | **victoire** | `principal_idle6.csv` l.6 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | 37.485 [32.832 ; 42.957] | couverture 38.996 [34.215 ; 44.732] | -1.512 [-2.725 ; -0.473] | 3.88 % | 15/20 | 0/0 | 0.00639 | 0.09584 | **egalite** | `principal_idle6.csv` l.7 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | 37.485 [32.832 ; 42.957] | centre_de_demande 39.094 [34.407 ; 45.016] | -1.61 [-2.513 ; -0.803] | 4.12 % | 15/20 | 0/0 | 0.000708 | 0.01628 | **victoire** | `principal_idle6.csv` l.8 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | 37.485 [32.832 ; 42.957] | couverture 38.996 [34.215 ; 44.732] | -1.512 [-2.725 ; -0.473] | 3.88 % | 15/20 | 0/0 | 0.00639 | 0.09584 | **egalite** | `principal_idle6.csv` l.9 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | 45.052 [38.636 ; 53.168] | rester_sur_place 49.864 [43.131 ; 58.086] | -4.812 [-6.21 ; -3.404] | 9.65 % | 18/20 | 0/0 | 2.7e-05 | 0.000694 | **victoire** | `principal_idle6.csv` l.10 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | 45.052 [38.636 ; 53.168] | couverture 45.92 [38.616 ; 55.749] | -0.869 [-2.989 ; 0.81] | 1.89 % | 13/20 | 0/0 | 0.498 | 1 | **egalite** | `principal_idle6.csv` l.11 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | 44.433 [37.72 ; 52.708] | centre_de_demande 46.94 [40.612 ; 54.608] | -2.506 [-3.835 ; -1.21] | 5.34 % | 14/20 | 0/0 | 0.004221 | 0.07176 | **egalite** | `principal_idle6.csv` l.12 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | 44.433 [37.72 ; 52.708] | couverture 45.057 [38.607 ; 52.831] | -0.624 [-1.912 ; 0.695] | 1.39 % | 10/20 | 0/0 | 0.33 | 1 | **egalite** | `principal_idle6.csv` l.13 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | 56.819 [41.635 ; 81.21] | centre_de_demande 67.678 [53.214 ; 90.917] | -10.86 [-12.378 ; -9.008] | 16.05 % | 19/20 | 0/0 | 4e-06 | 0.000107 | **victoire** | `principal_idle6.csv` l.14 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | 56.819 [41.635 ; 81.21] | couverture 57.475 [41.792 ; 82.399] | -0.656 [-1.89 ; 0.513] | 1.14 % | 13/20 | 0/0 | 0.3683 | 1 | **egalite** | `principal_idle6.csv` l.15 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | 56.819 [41.635 ; 81.21] | centre_de_demande 67.678 [53.214 ; 90.917] | -10.86 [-12.378 ; -9.008] | 16.05 % | 19/20 | 0/0 | 4e-06 | 0.000107 | **victoire** | `principal_idle6.csv` l.16 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | 56.819 [41.635 ; 81.21] | couverture 57.475 [41.792 ; 82.399] | -0.656 [-1.89 ; 0.513] | 1.14 % | 13/20 | 0/0 | 0.3683 | 1 | **egalite** | `principal_idle6.csv` l.17 |
| zipf | facile (s=0.5) | greedy_pair | 29.23 [28.047 ; 30.403] | rester_sur_place 26.899 [26.147 ; 27.701] | 2.331 [1.204 ; 3.443] | -8.67 % | 5/20 | 0/0 | 0.00169 | 0.03042 | **defaite** | `principal_idle6.csv` l.18 |
| zipf | facile (s=0.5) | greedy_pair | 29.23 [28.047 ; 30.403] | couverture 27.731 [27.098 ; 28.387] | 1.498 [0.516 ; 2.48] | -5.4 % | 7/20 | 0/0 | 0.03277 | 0.426 | **egalite** | `principal_idle6.csv` l.19 |
| zipf | facile (s=0.5) | greedy_time | 28.684 [27.782 ; 29.557] | rester_sur_place 26.827 [26.065 ; 27.616] | 1.856 [0.952 ; 2.797] | -6.92 % | 5/20 | 0/0 | 0.000851 | 0.01786 | **defaite** | `principal_idle6.csv` l.20 |
| zipf | facile (s=0.5) | greedy_time | 28.684 [27.782 ; 29.557] | couverture 27.658 [26.818 ; 28.467] | 1.026 [0.176 ; 1.872] | -3.71 % | 4/20 | 0/0 | 0.00486 | 0.07776 | **egalite** | `principal_idle6.csv` l.21 |
| zipf | moyen (s=1.0) | greedy_pair | 29.355 [28.333 ; 30.392] | rester_sur_place 28.798 [27.649 ; 29.998] | 0.556 [-0.468 ; 1.579] | -1.93 % | 8/20 | 0/0 | 0.3683 | 1 | **egalite** | `principal_idle6.csv` l.22 |
| zipf | moyen (s=1.0) | greedy_pair | 29.355 [28.333 ; 30.392] | couverture 29.092 [28.055 ; 30.061] | 0.263 [-0.856 ; 1.208] | -0.9 % | 10/20 | 0/0 | 0.7285 | 1 | **egalite** | `principal_idle6.csv` l.23 |
| zipf | moyen (s=1.0) | greedy_time | 29.165 [27.925 ; 30.363] | rester_sur_place 28.424 [27.143 ; 29.701] | 0.74 [-0.307 ; 1.785] | -2.6 % | 8/20 | 0/0 | 0.2611 | 1 | **egalite** | `principal_idle6.csv` l.24 |
| zipf | moyen (s=1.0) | greedy_time | 29.165 [27.925 ; 30.363] | couverture 29.168 [28.013 ; 30.275] | -0.004 [-0.907 ; 0.963] | 0.01 % | 12/20 | 0/0 | 0.6477 | 1 | **egalite** | `principal_idle6.csv` l.25 |
| zipf | difficile (s=1.5) | greedy_pair | 29.379 [27.997 ; 30.824] | rester_sur_place 29.527 [28.067 ; 30.998] | -0.148 [-1.637 ; 1.323] | 0.5 % | 9/20 | 0/0 | 0.9273 | 1 | **egalite** | `principal_idle6.csv` l.26 |
| zipf | difficile (s=1.5) | greedy_pair | 29.379 [27.997 ; 30.824] | couverture 29.479 [28.39 ; 30.575] | -0.099 [-1.393 ; 1.26] | 0.34 % | 11/20 | 0/2 | 0.7012 | 1 | **egalite** | `principal_idle6.csv` l.27 |
| zipf | difficile (s=1.5) | greedy_time | 27.472 [25.581 ; 29.436] | rester_sur_place 28.14 [26.665 ; 29.774] | -0.668 [-2.014 ; 0.851] | 2.37 % | 13/20 | 2/2 | 0.2774 | 1 | **egalite** | `principal_idle6.csv` l.28 |
| zipf | difficile (s=1.5) | greedy_time | 27.472 [25.581 ; 29.436] | couverture 28.639 [27.399 ; 30.028] | -1.167 [-2.434 ; 0.125] | 4.08 % | 14/20 | 2/2 | 0.08969 | 1 | **egalite** | `principal_idle6.csv` l.29 |

Decompte (meme fichier) : defaite : 2/28 ; egalite : 17/28 ; victoire : 9/28

Par (condition, allocation), gagnee seulement si les 2 tests (meilleure des 3 heuristiques v4 ET couverture, ecart 2) sont des victoires :

- dataset | 15 racks, 3 r., rho=0.7 | greedy_pair : **gagnee** (contre centre_de_demande : victoire `principal_idle6.csv` l.2, contre couverture : victoire `principal_idle6.csv` l.3)
- dataset | 15 racks, 3 r., rho=0.7 | greedy_time : **gagnee** (contre centre_de_demande : victoire `principal_idle6.csv` l.4, contre couverture : victoire `principal_idle6.csv` l.5)
- dataset | 15 racks, 3 r., rho=0.9 | greedy_pair : non gagnee (contre centre_de_demande : victoire `principal_idle6.csv` l.6, contre couverture : egalite `principal_idle6.csv` l.7)
- dataset | 15 racks, 3 r., rho=0.9 | greedy_time : non gagnee (contre centre_de_demande : victoire `principal_idle6.csv` l.8, contre couverture : egalite `principal_idle6.csv` l.9)
- dataset | 40 racks, 6 r., vit. var. | greedy_pair : non gagnee (contre rester_sur_place : victoire `principal_idle6.csv` l.10, contre couverture : egalite `principal_idle6.csv` l.11)
- dataset | 40 racks, 6 r., vit. var. | greedy_time : non gagnee (contre centre_de_demande : egalite `principal_idle6.csv` l.12, contre couverture : egalite `principal_idle6.csv` l.13)
- dataset | 150 racks, 20 r., rho=0.7 | greedy_pair : non gagnee (contre centre_de_demande : victoire `principal_idle6.csv` l.14, contre couverture : egalite `principal_idle6.csv` l.15)
- dataset | 150 racks, 20 r., rho=0.7 | greedy_time : non gagnee (contre centre_de_demande : victoire `principal_idle6.csv` l.16, contre couverture : egalite `principal_idle6.csv` l.17)
- zipf | facile (s=0.5) | greedy_pair : non gagnee (contre rester_sur_place : defaite `principal_idle6.csv` l.18, contre couverture : egalite `principal_idle6.csv` l.19)
- zipf | facile (s=0.5) | greedy_time : non gagnee (contre rester_sur_place : defaite `principal_idle6.csv` l.20, contre couverture : egalite `principal_idle6.csv` l.21)
- zipf | moyen (s=1.0) | greedy_pair : non gagnee (contre rester_sur_place : egalite `principal_idle6.csv` l.22, contre couverture : egalite `principal_idle6.csv` l.23)
- zipf | moyen (s=1.0) | greedy_time : non gagnee (contre rester_sur_place : egalite `principal_idle6.csv` l.24, contre couverture : egalite `principal_idle6.csv` l.25)
- zipf | difficile (s=1.5) | greedy_pair : non gagnee (contre rester_sur_place : egalite `principal_idle6.csv` l.26, contre couverture : egalite `principal_idle6.csv` l.27)
- zipf | difficile (s=1.5) | greedy_time : non gagnee (contre rester_sur_place : egalite `principal_idle6.csv` l.28, contre couverture : egalite `principal_idle6.csv` l.29)

Total : 2/14 (condition, allocation) gagnees.

**Famille secondaire : temps_traitement_moy_s contre drl_idle** (Holm dans la famille, descriptif)

| experience | condition | allocation | concurrent | DRL (s) | concurrent (s) | ecart (s) [IC95] | gagnes | p Holm | verdict | source |
|---|---|---|---|---|---|---|---|---|---|---|
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_idle | 27.274 | 26.825 | 0.449 [0.05 ; 0.97] | 6/20 | 0.5735 | egalite | `secondaire_idle6.csv` l.58 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | drl_idle | 27.274 | 26.825 | 0.449 [0.05 ; 0.97] | 6/20 | 0.5735 | egalite | `secondaire_idle6.csv` l.59 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_idle | 37.485 | 36.962 | 0.523 [0.117 ; 1.001] | 8/20 | 0.5735 | egalite | `secondaire_idle6.csv` l.60 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | drl_idle | 37.485 | 36.962 | 0.523 [0.117 ; 1.001] | 8/20 | 0.5735 | egalite | `secondaire_idle6.csv` l.61 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_idle | 45.052 | 45.135 | -0.083 [-1.486 ; 1.437] | 13/20 | 1 | egalite | `secondaire_idle6.csv` l.62 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | drl_idle | 44.433 | 44.72 | -0.287 [-1.515 ; 1.008] | 12/20 | 1 | egalite | `secondaire_idle6.csv` l.63 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_idle | 56.819 | 75.218 | -18.399 [-22.351 ; -15.547] | 20/20 | 2.7e-05 | victoire | `secondaire_idle6.csv` l.64 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | drl_idle | 56.819 | 75.218 | -18.399 [-22.351 ; -15.547] | 20/20 | 2.7e-05 | victoire | `secondaire_idle6.csv` l.65 |
| zipf | facile (s=0.5) | greedy_pair | drl_idle | 29.23 | 27.24 | 1.99 [0.898 ; 3.081] | 4/20 | 0.05832 | egalite | `secondaire_idle6.csv` l.66 |
| zipf | facile (s=0.5) | greedy_time | drl_idle | 28.684 | 27.382 | 1.301 [0.363 ; 2.257] | 7/20 | 0.1718 | egalite | `secondaire_idle6.csv` l.67 |
| zipf | moyen (s=1.0) | greedy_pair | drl_idle | 29.355 | 30.667 | -1.313 [-2.444 ; -0.201] | 15/20 | 0.5735 | egalite | `secondaire_idle6.csv` l.68 |
| zipf | moyen (s=1.0) | greedy_time | drl_idle | 29.165 | 29.558 | -0.393 [-1.273 ; 0.526] | 12/20 | 1 | egalite | `secondaire_idle6.csv` l.69 |
| zipf | difficile (s=1.5) | greedy_pair | drl_idle | 29.379 | 30.207 | -0.827 [-2.677 ; 0.855] | 11/20 | 1 | egalite | `secondaire_idle6.csv` l.70 |
| zipf | difficile (s=1.5) | greedy_time | drl_idle | 27.472 | 30.154 | -2.682 [-4.37 ; -1.029] | 15/20 | 0.09139 | egalite | `secondaire_idle6.csv` l.71 |

**Famille secondaire : temps_traitement_moy_s contre chaque concurrent** (Holm dans la famille, descriptif)

| experience | condition | allocation | concurrent | DRL (s) | concurrent (s) | ecart (s) [IC95] | gagnes | p Holm | verdict | source |
|---|---|---|---|---|---|---|---|---|---|---|
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | rester_sur_place | 27.274 | 28.999 | -1.726 [-2.396 ; -1.064] | 18/20 | 0.006504 | victoire | `secondaire_idle6.csv` l.2 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | retour_au_depot | 27.274 | 35.735 | -8.461 [-9.099 ; -7.818] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.3 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | centre_de_demande | 27.274 | 28.939 | -1.666 [-2.53 ; -0.906] | 17/20 | 0.009026 | victoire | `secondaire_idle6.csv` l.4 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | couverture | 27.274 | 28.458 | -1.184 [-1.814 ; -0.587] | 16/20 | 0.02135 | victoire | `secondaire_idle6.csv` l.5 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | rester_sur_place | 27.274 | 28.999 | -1.726 [-2.396 ; -1.064] | 18/20 | 0.006504 | victoire | `secondaire_idle6.csv` l.6 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | retour_au_depot | 27.274 | 35.735 | -8.461 [-9.099 ; -7.818] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.7 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | centre_de_demande | 27.274 | 28.939 | -1.666 [-2.53 ; -0.906] | 17/20 | 0.009026 | victoire | `secondaire_idle6.csv` l.8 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | couverture | 27.274 | 28.458 | -1.184 [-1.814 ; -0.587] | 16/20 | 0.02135 | victoire | `secondaire_idle6.csv` l.9 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | rester_sur_place | 37.485 | 40.41 | -2.925 [-3.827 ; -2.091] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.10 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | retour_au_depot | 37.485 | 45.961 | -8.476 [-9.442 ; -7.529] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.11 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | centre_de_demande | 37.485 | 39.094 | -1.61 [-2.513 ; -0.803] | 15/20 | 0.01698 | victoire | `secondaire_idle6.csv` l.12 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | couverture | 37.485 | 38.996 | -1.512 [-2.725 ; -0.473] | 15/20 | 0.09584 | egalite | `secondaire_idle6.csv` l.13 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | rester_sur_place | 37.485 | 40.41 | -2.925 [-3.827 ; -2.091] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.14 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | retour_au_depot | 37.485 | 45.961 | -8.476 [-9.442 ; -7.529] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.15 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | centre_de_demande | 37.485 | 39.094 | -1.61 [-2.513 ; -0.803] | 15/20 | 0.01698 | victoire | `secondaire_idle6.csv` l.16 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | couverture | 37.485 | 38.996 | -1.512 [-2.725 ; -0.473] | 15/20 | 0.09584 | egalite | `secondaire_idle6.csv` l.17 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | rester_sur_place | 45.052 | 49.864 | -4.812 [-6.21 ; -3.404] | 18/20 | 0.000908 | victoire | `secondaire_idle6.csv` l.18 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | retour_au_depot | 45.052 | 58.164 | -13.112 [-15.151 ; -11.407] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.19 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | centre_de_demande | 45.052 | 50.195 | -5.143 [-6.639 ; -3.843] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.20 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | couverture | 45.052 | 45.92 | -0.869 [-2.989 ; 0.81] | 13/20 | 1 | egalite | `secondaire_idle6.csv` l.21 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | rester_sur_place | 44.433 | 48.654 | -4.221 [-5.589 ; -2.847] | 18/20 | 0.00116 | victoire | `secondaire_idle6.csv` l.22 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | retour_au_depot | 44.433 | 56.59 | -12.157 [-14.542 ; -10.077] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.23 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | centre_de_demande | 44.433 | 46.94 | -2.506 [-3.835 ; -1.21] | 14/20 | 0.07176 | egalite | `secondaire_idle6.csv` l.24 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | couverture | 44.433 | 45.057 | -0.624 [-1.912 ; 0.695] | 10/20 | 1 | egalite | `secondaire_idle6.csv` l.25 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | rester_sur_place | 56.819 | 69.23 | -12.411 [-17.183 ; -9.064] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.26 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | retour_au_depot | 56.819 | 77.353 | -20.534 [-22.898 ; -18.647] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.27 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | centre_de_demande | 56.819 | 67.678 | -10.86 [-12.378 ; -9.008] | 19/20 | 0.000137 | victoire | `secondaire_idle6.csv` l.28 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | couverture | 56.819 | 57.475 | -0.656 [-1.89 ; 0.513] | 13/20 | 1 | egalite | `secondaire_idle6.csv` l.29 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | rester_sur_place | 56.819 | 69.23 | -12.411 [-17.183 ; -9.064] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.30 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | retour_au_depot | 56.819 | 77.353 | -20.534 [-22.898 ; -18.647] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.31 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | centre_de_demande | 56.819 | 67.678 | -10.86 [-12.378 ; -9.008] | 19/20 | 0.000137 | victoire | `secondaire_idle6.csv` l.32 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | couverture | 56.819 | 57.475 | -0.656 [-1.89 ; 0.513] | 13/20 | 1 | egalite | `secondaire_idle6.csv` l.33 |
| zipf | facile (s=0.5) | greedy_pair | rester_sur_place | 29.23 | 26.899 | 2.331 [1.204 ; 3.443] | 5/20 | 0.03042 | defaite | `secondaire_idle6.csv` l.34 |
| zipf | facile (s=0.5) | greedy_pair | retour_au_depot | 29.23 | 37.27 | -8.04 [-8.852 ; -7.277] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.35 |
| zipf | facile (s=0.5) | greedy_pair | centre_de_demande | 29.23 | 32.056 | -2.826 [-3.649 ; -1.993] | 18/20 | 0.000908 | victoire | `secondaire_idle6.csv` l.36 |
| zipf | facile (s=0.5) | greedy_pair | couverture | 29.23 | 27.731 | 1.498 [0.516 ; 2.48] | 7/20 | 0.426 | egalite | `secondaire_idle6.csv` l.37 |
| zipf | facile (s=0.5) | greedy_time | rester_sur_place | 28.684 | 26.827 | 1.856 [0.952 ; 2.797] | 5/20 | 0.01871 | defaite | `secondaire_idle6.csv` l.38 |
| zipf | facile (s=0.5) | greedy_time | retour_au_depot | 28.684 | 36.203 | -7.519 [-8.068 ; -6.978] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.39 |
| zipf | facile (s=0.5) | greedy_time | centre_de_demande | 28.684 | 30.777 | -2.093 [-2.833 ; -1.241] | 18/20 | 0.01026 | victoire | `secondaire_idle6.csv` l.40 |
| zipf | facile (s=0.5) | greedy_time | couverture | 28.684 | 27.658 | 1.026 [0.176 ; 1.872] | 4/20 | 0.07776 | egalite | `secondaire_idle6.csv` l.41 |
| zipf | moyen (s=1.0) | greedy_pair | rester_sur_place | 29.355 | 28.798 | 0.556 [-0.468 ; 1.579] | 8/20 | 1 | egalite | `secondaire_idle6.csv` l.42 |
| zipf | moyen (s=1.0) | greedy_pair | retour_au_depot | 29.355 | 37.972 | -8.617 [-9.592 ; -7.626] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.43 |
| zipf | moyen (s=1.0) | greedy_pair | centre_de_demande | 29.355 | 33.503 | -4.148 [-5.094 ; -3.284] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.44 |
| zipf | moyen (s=1.0) | greedy_pair | couverture | 29.355 | 29.092 | 0.263 [-0.856 ; 1.208] | 10/20 | 1 | egalite | `secondaire_idle6.csv` l.45 |
| zipf | moyen (s=1.0) | greedy_time | rester_sur_place | 29.165 | 28.424 | 0.74 [-0.307 ; 1.785] | 8/20 | 1 | egalite | `secondaire_idle6.csv` l.46 |
| zipf | moyen (s=1.0) | greedy_time | retour_au_depot | 29.165 | 35.838 | -6.674 [-7.689 ; -5.61] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.47 |
| zipf | moyen (s=1.0) | greedy_time | centre_de_demande | 29.165 | 31.724 | -2.559 [-3.708 ; -1.365] | 16/20 | 0.02135 | victoire | `secondaire_idle6.csv` l.48 |
| zipf | moyen (s=1.0) | greedy_time | couverture | 29.165 | 29.168 | -0.004 [-0.907 ; 0.963] | 12/20 | 1 | egalite | `secondaire_idle6.csv` l.49 |
| zipf | difficile (s=1.5) | greedy_pair | rester_sur_place | 29.379 | 29.527 | -0.148 [-1.637 ; 1.323] | 9/20 | 1 | egalite | `secondaire_idle6.csv` l.50 |
| zipf | difficile (s=1.5) | greedy_pair | retour_au_depot | 29.379 | 38.594 | -9.214 [-10.836 ; -7.557] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.51 |
| zipf | difficile (s=1.5) | greedy_pair | centre_de_demande | 29.379 | 34.388 | -5.009 [-7.176 ; -2.87] | 17/20 | 0.01206 | victoire | `secondaire_idle6.csv` l.52 |
| zipf | difficile (s=1.5) | greedy_pair | couverture | 29.379 | 29.479 | -0.099 [-1.393 ; 1.26] | 11/20 | 1 | egalite | `secondaire_idle6.csv` l.53 |
| zipf | difficile (s=1.5) | greedy_time | rester_sur_place | 27.472 | 28.14 | -0.668 [-2.014 ; 0.851] | 13/20 | 1 | egalite | `secondaire_idle6.csv` l.54 |
| zipf | difficile (s=1.5) | greedy_time | retour_au_depot | 27.472 | 36.232 | -8.76 [-10.658 ; -6.921] | 20/20 | 0.000107 | victoire | `secondaire_idle6.csv` l.55 |
| zipf | difficile (s=1.5) | greedy_time | centre_de_demande | 27.472 | 30.833 | -3.361 [-4.655 ; -2.012] | 16/20 | 0.007578 | victoire | `secondaire_idle6.csv` l.56 |
| zipf | difficile (s=1.5) | greedy_time | couverture | 27.472 | 28.639 | -1.167 [-2.434 ; 0.125] | 14/20 | 1 | egalite | `secondaire_idle6.csv` l.57 |

## 3. Phase B : drl_route6 contre chacune des 3 Dijkstra, capacite 1 robot par segment (famille B, 12 tests, Holm)

| experience | condition | allocation | DRL (s) [IC95] | concurrent (s) [IC95] | ecart (s) [IC95] | gain | gagnes | echecs DRL/conc. | p Wilcoxon | p Holm | verdict | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | 34.36 [32.945 ; 35.835] | dijkstra_statique 34.612 [33.271 ; 35.904] | -0.252 [-1.102 ; 0.69] | 0.73 % | 14/20 | 0/0 | 0.2122 | 1 | **egalite** | `principal_route6.csv` l.2 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | 34.36 [32.945 ; 35.835] | dijkstra_dynamique 34.78 [33.326 ; 36.374] | -0.421 [-1.082 ; 0.378] | 1.21 % | 13/20 | 0/0 | 0.04863 | 0.389 | **egalite** | `principal_route6.csv` l.3 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | 34.36 [32.945 ; 35.835] | dijkstra_congestion 34.503 [32.872 ; 36.331] | -0.143 [-0.839 ; 0.649] | 0.42 % | 13/20 | 0/0 | 0.3683 | 1 | **egalite** | `principal_route6.csv` l.4 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | 33.592 [32.599 ; 34.624] | dijkstra_statique 34.157 [33.122 ; 35.244] | -0.565 [-1.003 ; -0.178] | 1.65 % | 14/20 | 0/0 | 0.03277 | 0.2949 | **egalite** | `principal_route6.csv` l.5 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | 33.592 [32.599 ; 34.624] | dijkstra_dynamique 33.84 [32.814 ; 34.912] | -0.249 [-0.534 ; 0.013] | 0.73 % | 13/20 | 0/0 | 0.1054 | 0.7378 | **egalite** | `principal_route6.csv` l.6 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | 33.592 [32.599 ; 34.624] | dijkstra_congestion 33.568 [32.51 ; 34.657] | 0.024 [-0.406 ; 0.412] | -0.07 % | 8/20 | 0/0 | 0.6477 | 1 | **egalite** | `principal_route6.csv` l.7 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | 40.74 [39.146 ; 42.247] | dijkstra_statique 40.935 [39.157 ; 42.702] | -0.195 [-0.909 ; 0.535] | 0.48 % | 11/20 | 0/0 | 0.6477 | 1 | **egalite** | `principal_route6.csv` l.8 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | 40.74 [39.146 ; 42.247] | dijkstra_dynamique 41.248 [39.389 ; 43.072] | -0.508 [-1.518 ; 0.45] | 1.23 % | 14/20 | 0/0 | 0.2024 | 1 | **egalite** | `principal_route6.csv` l.9 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | 40.74 [39.146 ; 42.247] | dijkstra_congestion 41.247 [39.436 ; 43.068] | -0.507 [-1.325 ; 0.337] | 1.23 % | 12/20 | 0/0 | 0.3488 | 1 | **egalite** | `principal_route6.csv` l.10 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | 69.026 [51.246 ; 97.59] | dijkstra_statique 69.691 [51.963 ; 98.305] | -0.665 [-1.188 ; -0.253] | 0.95 % | 17/20 | 0/0 | 0.000837 | 0.01005 | **victoire** | `principal_route6.csv` l.11 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | 69.026 [51.246 ; 97.59] | dijkstra_dynamique 69.316 [51.509 ; 97.902] | -0.291 [-0.651 ; -0.034] | 0.42 % | 16/20 | 0/0 | 0.01226 | 0.1226 | **egalite** | `principal_route6.csv` l.12 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | 69.026 [51.246 ; 97.59] | dijkstra_congestion 69.296 [51.489 ; 97.911] | -0.27 [-0.632 ; -0.001] | 0.39 % | 16/20 | 0/0 | 0.005684 | 0.06253 | **egalite** | `principal_route6.csv` l.13 |

Decompte (meme fichier) : egalite : 11/12 ; victoire : 1/12

Par (condition, allocation), gagnee seulement si les 3 tests (une Dijkstra chacun) sont des victoires :

- congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair : non gagnee (contre dijkstra_statique : egalite `principal_route6.csv` l.2, contre dijkstra_dynamique : egalite `principal_route6.csv` l.3, contre dijkstra_congestion : egalite `principal_route6.csv` l.4)
- congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair : non gagnee (contre dijkstra_statique : egalite `principal_route6.csv` l.5, contre dijkstra_dynamique : egalite `principal_route6.csv` l.6, contre dijkstra_congestion : egalite `principal_route6.csv` l.7)
- congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair : non gagnee (contre dijkstra_statique : egalite `principal_route6.csv` l.8, contre dijkstra_dynamique : egalite `principal_route6.csv` l.9, contre dijkstra_congestion : egalite `principal_route6.csv` l.10)
- congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair : non gagnee (contre dijkstra_statique : victoire `principal_route6.csv` l.11, contre dijkstra_dynamique : egalite `principal_route6.csv` l.12, contre dijkstra_congestion : egalite `principal_route6.csv` l.13)

Total : 0/4 (condition, allocation) gagnees.

## 4. Phase C : drl_alloc6 contre la meilleure de greedy_pair et greedy_time (famille C, 4 tests, Holm)

*Pas de resultats de test pour alloc6.*

**Phase C : apprentissage echoue, non testee** (ecart 8). Validations du lancement arrete (ecart relatif a la meilleure de greedy_pair et greedy_time) :

| graine | instant (min) | episode | temps de validation (s) | ecart relatif | source |
|---|---|---|---|---|---|
| 0 | 0.0 | 0 | 55.1314 | +0.11 % | `lancements_interrompus/alloc6_interrompu_2104/val_log_seed0.csv` l.2 |
| 0 | 10.07 | 135 | 161.479 | +167.76 % | `lancements_interrompus/alloc6_interrompu_2104/val_log_seed0.csv` l.3 |
| 0 | 20.06 | 271 | 214.6426 | +289.46 % | `lancements_interrompus/alloc6_interrompu_2104/val_log_seed0.csv` l.4 |
| 0 | 30.11 | 387 | 165.0547 | +182.60 % | `lancements_interrompus/alloc6_interrompu_2104/val_log_seed0.csv` l.5 |
| 0 | 40.11 | 476 | 184.9193 | +219.69 % | `lancements_interrompus/alloc6_interrompu_2104/val_log_seed0.csv` l.6 |

## 5. Metriques secondaires (moyenne et IC 95 %, toutes methodes)

Tests DRL contre chaque concurrent et par metrique (Holm par famille) : `secondaire_<etape>.csv`.

### Phase A

| experience | condition | allocation | methode | metrique | moyenne [IC95] | source |
|---|---|---|---|---|---|---|
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | rester_sur_place | approche_moy_s | 2.8032 [2.4269 ; 3.1775] | `descriptif_idle6.csv` l.3 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.4 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.7 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | retour_au_depot | approche_moy_s | 4.7574 [4.1825 ; 5.2878] | `descriptif_idle6.csv` l.11 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.12 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0014 [0.0013 ; 0.0016] | `descriptif_idle6.csv` l.15 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | centre_de_demande | approche_moy_s | 3.0995 [2.7783 ; 3.4178] | `descriptif_idle6.csv` l.19 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.20 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0337 [0.0324 ; 0.0354] | `descriptif_idle6.csv` l.23 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | couverture | approche_moy_s | 2.743 [2.4493 ; 3.0297] | `descriptif_idle6.csv` l.27 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.28 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | couverture | ms_par_decision_attente | 0.0677 [0.0659 ; 0.07] | `descriptif_idle6.csv` l.31 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_idle | approche_moy_s | 2.3547 [2.0212 ; 2.6833] | `descriptif_idle6.csv` l.35 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.36 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_idle | ms_par_decision_attente | 0.3874 [0.3759 ; 0.4027] | `descriptif_idle6.csv` l.39 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_idle6 | approche_moy_s | 2.4027 [2.0872 ; 2.7155] | `descriptif_idle6.csv` l.43 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.44 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_idle6 | ms_par_decision_attente | 0.5237 [0.5181 ; 0.5292] | `descriptif_idle6.csv` l.47 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | rester_sur_place | approche_moy_s | 2.8032 [2.4269 ; 3.1775] | `descriptif_idle6.csv` l.51 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.52 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.55 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | retour_au_depot | approche_moy_s | 4.7574 [4.1825 ; 5.2878] | `descriptif_idle6.csv` l.59 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.60 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0013 [0.0013 ; 0.0014] | `descriptif_idle6.csv` l.63 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | centre_de_demande | approche_moy_s | 3.0995 [2.7783 ; 3.4178] | `descriptif_idle6.csv` l.67 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.68 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | centre_de_demande | ms_par_decision_attente | 0.033 [0.0318 ; 0.0344] | `descriptif_idle6.csv` l.71 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | couverture | approche_moy_s | 2.743 [2.4493 ; 3.0297] | `descriptif_idle6.csv` l.75 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.76 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | couverture | ms_par_decision_attente | 0.0662 [0.065 ; 0.0677] | `descriptif_idle6.csv` l.79 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | drl_idle | approche_moy_s | 2.3547 [2.0212 ; 2.6833] | `descriptif_idle6.csv` l.83 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.84 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | drl_idle | ms_par_decision_attente | 0.3837 [0.3771 ; 0.3905] | `descriptif_idle6.csv` l.87 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | drl_idle6 | approche_moy_s | 2.4027 [2.0872 ; 2.7155] | `descriptif_idle6.csv` l.91 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.92 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | drl_idle6 | ms_par_decision_attente | 0.5272 [0.5203 ; 0.5359] | `descriptif_idle6.csv` l.95 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | rester_sur_place | approche_moy_s | 2.9144 [2.5082 ; 3.3248] | `descriptif_idle6.csv` l.99 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.100 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.103 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | retour_au_depot | approche_moy_s | 4.0141 [3.4108 ; 4.5332] | `descriptif_idle6.csv` l.107 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.108 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0014 [0.0013 ; 0.0014] | `descriptif_idle6.csv` l.111 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | centre_de_demande | approche_moy_s | 2.7845 [2.3763 ; 3.1712] | `descriptif_idle6.csv` l.115 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.116 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0356 [0.0342 ; 0.0371] | `descriptif_idle6.csv` l.119 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | couverture | approche_moy_s | 2.6665 [2.2659 ; 3.0388] | `descriptif_idle6.csv` l.123 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.124 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | couverture | ms_par_decision_attente | 0.0691 [0.067 ; 0.0716] | `descriptif_idle6.csv` l.127 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_idle | approche_moy_s | 2.4217 [2.0257 ; 2.8089] | `descriptif_idle6.csv` l.131 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.132 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_idle | ms_par_decision_attente | 0.4049 [0.3893 ; 0.424] | `descriptif_idle6.csv` l.135 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_idle6 | approche_moy_s | 2.4889 [2.104 ; 2.8734] | `descriptif_idle6.csv` l.139 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.140 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_idle6 | ms_par_decision_attente | 0.5458 [0.5349 ; 0.5614] | `descriptif_idle6.csv` l.143 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | rester_sur_place | approche_moy_s | 2.9144 [2.5082 ; 3.3248] | `descriptif_idle6.csv` l.147 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.148 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.151 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | retour_au_depot | approche_moy_s | 4.0141 [3.4108 ; 4.5332] | `descriptif_idle6.csv` l.155 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.156 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0015 [0.0014 ; 0.0015] | `descriptif_idle6.csv` l.159 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | centre_de_demande | approche_moy_s | 2.7845 [2.3763 ; 3.1712] | `descriptif_idle6.csv` l.163 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.164 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | centre_de_demande | ms_par_decision_attente | 0.0399 [0.0363 ; 0.0443] | `descriptif_idle6.csv` l.167 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | couverture | approche_moy_s | 2.6665 [2.2659 ; 3.0388] | `descriptif_idle6.csv` l.171 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.172 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | couverture | ms_par_decision_attente | 0.0739 [0.0709 ; 0.0772] | `descriptif_idle6.csv` l.175 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | drl_idle | approche_moy_s | 2.4217 [2.0257 ; 2.8089] | `descriptif_idle6.csv` l.179 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.180 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | drl_idle | ms_par_decision_attente | 0.4019 [0.3921 ; 0.4124] | `descriptif_idle6.csv` l.183 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | drl_idle6 | approche_moy_s | 2.4889 [2.104 ; 2.8734] | `descriptif_idle6.csv` l.187 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.188 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | drl_idle6 | ms_par_decision_attente | 0.5949 [0.565 ; 0.6324] | `descriptif_idle6.csv` l.191 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | rester_sur_place | approche_moy_s | 5.746 [4.9855 ; 6.5251] | `descriptif_idle6.csv` l.195 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.196 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.199 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | retour_au_depot | approche_moy_s | 8.2438 [7.3392 ; 9.0938] | `descriptif_idle6.csv` l.203 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.204 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0016 [0.0015 ; 0.0017] | `descriptif_idle6.csv` l.207 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | centre_de_demande | approche_moy_s | 5.97 [5.2038 ; 6.7655] | `descriptif_idle6.csv` l.211 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.212 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0401 [0.0379 ; 0.0424] | `descriptif_idle6.csv` l.215 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | couverture | approche_moy_s | 4.6796 [3.9737 ; 5.462] | `descriptif_idle6.csv` l.219 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.220 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | couverture | ms_par_decision_attente | 0.0993 [0.0962 ; 0.1024] | `descriptif_idle6.csv` l.223 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_idle | approche_moy_s | 4.7525 [3.9245 ; 5.6148] | `descriptif_idle6.csv` l.227 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.228 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_idle | ms_par_decision_attente | 0.5114 [0.4919 ; 0.534] | `descriptif_idle6.csv` l.231 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_idle6 | approche_moy_s | 4.7135 [3.9605 ; 5.5165] | `descriptif_idle6.csv` l.235 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.236 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_idle6 | ms_par_decision_attente | 0.7171 [0.702 ; 0.7308] | `descriptif_idle6.csv` l.239 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | rester_sur_place | approche_moy_s | 5.534 [4.7531 ; 6.4119] | `descriptif_idle6.csv` l.243 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.244 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.247 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | retour_au_depot | approche_moy_s | 7.6765 [6.7745 ; 8.5116] | `descriptif_idle6.csv` l.251 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.252 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0022 [0.002 ; 0.0024] | `descriptif_idle6.csv` l.255 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | centre_de_demande | approche_moy_s | 5.2536 [4.5038 ; 6.0577] | `descriptif_idle6.csv` l.259 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.260 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | centre_de_demande | ms_par_decision_attente | 0.0533 [0.0517 ; 0.0552] | `descriptif_idle6.csv` l.263 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | couverture | approche_moy_s | 4.5197 [3.7758 ; 5.3643] | `descriptif_idle6.csv` l.267 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.268 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | couverture | ms_par_decision_attente | 0.1207 [0.1129 ; 0.1286] | `descriptif_idle6.csv` l.271 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | drl_idle | approche_moy_s | 4.5423 [3.7287 ; 5.4123] | `descriptif_idle6.csv` l.275 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.276 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | drl_idle | ms_par_decision_attente | 0.5369 [0.4946 ; 0.5831] | `descriptif_idle6.csv` l.279 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | drl_idle6 | approche_moy_s | 4.4948 [3.6836 ; 5.4232] | `descriptif_idle6.csv` l.283 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.284 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | drl_idle6 | ms_par_decision_attente | 0.6511 [0.6334 ; 0.671] | `descriptif_idle6.csv` l.287 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | rester_sur_place | approche_moy_s | 9.9249 [8.8035 ; 10.9751] | `descriptif_idle6.csv` l.291 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.292 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.295 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | retour_au_depot | approche_moy_s | 13.902 [12.1941 ; 15.5107] | `descriptif_idle6.csv` l.299 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.300 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0016 [0.0015 ; 0.0017] | `descriptif_idle6.csv` l.303 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | centre_de_demande | approche_moy_s | 10.6873 [9.2516 ; 12.0841] | `descriptif_idle6.csv` l.307 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.308 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0928 [0.0903 ; 0.0953] | `descriptif_idle6.csv` l.311 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | couverture | approche_moy_s | 6.1296 [5.142 ; 7.2509] | `descriptif_idle6.csv` l.315 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.316 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | couverture | ms_par_decision_attente | 0.2149 [0.2048 ; 0.2255] | `descriptif_idle6.csv` l.319 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_idle | approche_moy_s | 12.3703 [10.8782 ; 13.8961] | `descriptif_idle6.csv` l.323 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.324 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_idle | ms_par_decision_attente | 0.5509 [0.5414 ; 0.5611] | `descriptif_idle6.csv` l.327 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_idle6 | approche_moy_s | 6.2367 [5.2743 ; 7.3528] | `descriptif_idle6.csv` l.331 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.332 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_idle6 | ms_par_decision_attente | 0.8675 [0.854 ; 0.8822] | `descriptif_idle6.csv` l.335 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | rester_sur_place | approche_moy_s | 9.9249 [8.8035 ; 10.9751] | `descriptif_idle6.csv` l.339 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.340 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.343 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | retour_au_depot | approche_moy_s | 13.902 [12.1941 ; 15.5107] | `descriptif_idle6.csv` l.347 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.348 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0016 [0.0016 ; 0.0017] | `descriptif_idle6.csv` l.351 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | centre_de_demande | approche_moy_s | 10.6873 [9.2516 ; 12.0841] | `descriptif_idle6.csv` l.355 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.356 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | centre_de_demande | ms_par_decision_attente | 0.0919 [0.0882 ; 0.0977] | `descriptif_idle6.csv` l.359 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | couverture | approche_moy_s | 6.1296 [5.142 ; 7.2509] | `descriptif_idle6.csv` l.363 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.364 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | couverture | ms_par_decision_attente | 0.1831 [0.18 ; 0.1857] | `descriptif_idle6.csv` l.367 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | drl_idle | approche_moy_s | 12.3703 [10.8782 ; 13.8961] | `descriptif_idle6.csv` l.371 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.372 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | drl_idle | ms_par_decision_attente | 0.5483 [0.5375 ; 0.5601] | `descriptif_idle6.csv` l.375 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | drl_idle6 | approche_moy_s | 6.2367 [5.2743 ; 7.3528] | `descriptif_idle6.csv` l.379 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.380 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | drl_idle6 | ms_par_decision_attente | 0.8584 [0.8472 ; 0.8705] | `descriptif_idle6.csv` l.383 |
| zipf | facile (s=0.5) | greedy_pair | rester_sur_place | approche_moy_s | 15.1408 [14.5315 ; 15.8082] | `descriptif_idle6.csv` l.387 |
| zipf | facile (s=0.5) | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.388 |
| zipf | facile (s=0.5) | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.391 |
| zipf | facile (s=0.5) | greedy_pair | retour_au_depot | approche_moy_s | 23.8893 [23.3654 ; 24.4166] | `descriptif_idle6.csv` l.395 |
| zipf | facile (s=0.5) | greedy_pair | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.396 |
| zipf | facile (s=0.5) | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0016 [0.0015 ; 0.0017] | `descriptif_idle6.csv` l.399 |
| zipf | facile (s=0.5) | greedy_pair | centre_de_demande | approche_moy_s | 19.8149 [19.2855 ; 20.2744] | `descriptif_idle6.csv` l.403 |
| zipf | facile (s=0.5) | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.404 |
| zipf | facile (s=0.5) | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0713 [0.0704 ; 0.072] | `descriptif_idle6.csv` l.407 |
| zipf | facile (s=0.5) | greedy_pair | couverture | approche_moy_s | 16.0452 [15.4403 ; 16.6338] | `descriptif_idle6.csv` l.411 |
| zipf | facile (s=0.5) | greedy_pair | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.412 |
| zipf | facile (s=0.5) | greedy_pair | couverture | ms_par_decision_attente | 0.1227 [0.1133 ; 0.1312] | `descriptif_idle6.csv` l.415 |
| zipf | facile (s=0.5) | greedy_pair | drl_idle | approche_moy_s | 15.4909 [14.8489 ; 16.099] | `descriptif_idle6.csv` l.419 |
| zipf | facile (s=0.5) | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.420 |
| zipf | facile (s=0.5) | greedy_pair | drl_idle | ms_par_decision_attente | 0.4271 [0.424 ; 0.4307] | `descriptif_idle6.csv` l.423 |
| zipf | facile (s=0.5) | greedy_pair | drl_idle6 | approche_moy_s | 17.2507 [16.2162 ; 18.1875] | `descriptif_idle6.csv` l.427 |
| zipf | facile (s=0.5) | greedy_pair | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.428 |
| zipf | facile (s=0.5) | greedy_pair | drl_idle6 | ms_par_decision_attente | 0.604 [0.5976 ; 0.613] | `descriptif_idle6.csv` l.431 |
| zipf | facile (s=0.5) | greedy_time | rester_sur_place | approche_moy_s | 15.0996 [14.5283 ; 15.7003] | `descriptif_idle6.csv` l.435 |
| zipf | facile (s=0.5) | greedy_time | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.436 |
| zipf | facile (s=0.5) | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.439 |
| zipf | facile (s=0.5) | greedy_time | retour_au_depot | approche_moy_s | 23.1087 [22.5505 ; 23.6687] | `descriptif_idle6.csv` l.443 |
| zipf | facile (s=0.5) | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.444 |
| zipf | facile (s=0.5) | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0014 [0.0014 ; 0.0015] | `descriptif_idle6.csv` l.447 |
| zipf | facile (s=0.5) | greedy_time | centre_de_demande | approche_moy_s | 18.7819 [18.2302 ; 19.2967] | `descriptif_idle6.csv` l.451 |
| zipf | facile (s=0.5) | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.452 |
| zipf | facile (s=0.5) | greedy_time | centre_de_demande | ms_par_decision_attente | 0.0455 [0.045 ; 0.046] | `descriptif_idle6.csv` l.455 |
| zipf | facile (s=0.5) | greedy_time | couverture | approche_moy_s | 15.8167 [15.0837 ; 16.5144] | `descriptif_idle6.csv` l.459 |
| zipf | facile (s=0.5) | greedy_time | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.460 |
| zipf | facile (s=0.5) | greedy_time | couverture | ms_par_decision_attente | 0.0974 [0.0923 ; 0.1043] | `descriptif_idle6.csv` l.463 |
| zipf | facile (s=0.5) | greedy_time | drl_idle | approche_moy_s | 15.5928 [14.8575 ; 16.4144] | `descriptif_idle6.csv` l.467 |
| zipf | facile (s=0.5) | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.468 |
| zipf | facile (s=0.5) | greedy_time | drl_idle | ms_par_decision_attente | 0.6303 [0.6155 ; 0.6534] | `descriptif_idle6.csv` l.471 |
| zipf | facile (s=0.5) | greedy_time | drl_idle6 | approche_moy_s | 16.7982 [16.0027 ; 17.5407] | `descriptif_idle6.csv` l.475 |
| zipf | facile (s=0.5) | greedy_time | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.476 |
| zipf | facile (s=0.5) | greedy_time | drl_idle6 | ms_par_decision_attente | 0.7596 [0.6876 ; 0.8208] | `descriptif_idle6.csv` l.479 |
| zipf | moyen (s=1.0) | greedy_pair | rester_sur_place | approche_moy_s | 14.0162 [13.277 ; 14.8298] | `descriptif_idle6.csv` l.483 |
| zipf | moyen (s=1.0) | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.484 |
| zipf | moyen (s=1.0) | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.487 |
| zipf | moyen (s=1.0) | greedy_pair | retour_au_depot | approche_moy_s | 20.5203 [20.1831 ; 20.8202] | `descriptif_idle6.csv` l.491 |
| zipf | moyen (s=1.0) | greedy_pair | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.492 |
| zipf | moyen (s=1.0) | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0019 [0.0018 ; 0.002] | `descriptif_idle6.csv` l.495 |
| zipf | moyen (s=1.0) | greedy_pair | centre_de_demande | approche_moy_s | 17.2928 [16.7055 ; 17.857] | `descriptif_idle6.csv` l.499 |
| zipf | moyen (s=1.0) | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.500 |
| zipf | moyen (s=1.0) | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0562 [0.0554 ; 0.0571] | `descriptif_idle6.csv` l.503 |
| zipf | moyen (s=1.0) | greedy_pair | couverture | approche_moy_s | 14.6527 [14.0127 ; 15.2513] | `descriptif_idle6.csv` l.507 |
| zipf | moyen (s=1.0) | greedy_pair | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.508 |
| zipf | moyen (s=1.0) | greedy_pair | couverture | ms_par_decision_attente | 0.1084 [0.1072 ; 0.1095] | `descriptif_idle6.csv` l.511 |
| zipf | moyen (s=1.0) | greedy_pair | drl_idle | approche_moy_s | 15.0567 [14.4441 ; 15.6647] | `descriptif_idle6.csv` l.515 |
| zipf | moyen (s=1.0) | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.516 |
| zipf | moyen (s=1.0) | greedy_pair | drl_idle | ms_par_decision_attente | 0.4945 [0.4918 ; 0.4972] | `descriptif_idle6.csv` l.519 |
| zipf | moyen (s=1.0) | greedy_pair | drl_idle6 | approche_moy_s | 14.6909 [14.0812 ; 15.2995] | `descriptif_idle6.csv` l.523 |
| zipf | moyen (s=1.0) | greedy_pair | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.524 |
| zipf | moyen (s=1.0) | greedy_pair | drl_idle6 | ms_par_decision_attente | 0.6985 [0.6943 ; 0.7042] | `descriptif_idle6.csv` l.527 |
| zipf | moyen (s=1.0) | greedy_time | rester_sur_place | approche_moy_s | 13.587 [12.8547 ; 14.2956] | `descriptif_idle6.csv` l.531 |
| zipf | moyen (s=1.0) | greedy_time | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.532 |
| zipf | moyen (s=1.0) | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.535 |
| zipf | moyen (s=1.0) | greedy_time | retour_au_depot | approche_moy_s | 19.3743 [19.0018 ; 19.7563] | `descriptif_idle6.csv` l.539 |
| zipf | moyen (s=1.0) | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.540 |
| zipf | moyen (s=1.0) | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0017 [0.0016 ; 0.0018] | `descriptif_idle6.csv` l.543 |
| zipf | moyen (s=1.0) | greedy_time | centre_de_demande | approche_moy_s | 16.0652 [15.3289 ; 16.8195] | `descriptif_idle6.csv` l.547 |
| zipf | moyen (s=1.0) | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.548 |
| zipf | moyen (s=1.0) | greedy_time | centre_de_demande | ms_par_decision_attente | 0.0562 [0.0553 ; 0.0572] | `descriptif_idle6.csv` l.551 |
| zipf | moyen (s=1.0) | greedy_time | couverture | approche_moy_s | 14.4287 [13.7246 ; 15.1449] | `descriptif_idle6.csv` l.555 |
| zipf | moyen (s=1.0) | greedy_time | couverture | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.556 |
| zipf | moyen (s=1.0) | greedy_time | couverture | ms_par_decision_attente | 0.1085 [0.1077 ; 0.1093] | `descriptif_idle6.csv` l.559 |
| zipf | moyen (s=1.0) | greedy_time | drl_idle | approche_moy_s | 14.5534 [13.9803 ; 15.0968] | `descriptif_idle6.csv` l.563 |
| zipf | moyen (s=1.0) | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.564 |
| zipf | moyen (s=1.0) | greedy_time | drl_idle | ms_par_decision_attente | 0.4921 [0.4901 ; 0.4941] | `descriptif_idle6.csv` l.567 |
| zipf | moyen (s=1.0) | greedy_time | drl_idle6 | approche_moy_s | 14.5913 [13.8003 ; 15.3835] | `descriptif_idle6.csv` l.571 |
| zipf | moyen (s=1.0) | greedy_time | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.572 |
| zipf | moyen (s=1.0) | greedy_time | drl_idle6 | ms_par_decision_attente | 0.6983 [0.6903 ; 0.7085] | `descriptif_idle6.csv` l.575 |
| zipf | difficile (s=1.5) | greedy_pair | rester_sur_place | approche_moy_s | 9.2587 [8.636 ; 9.8598] | `descriptif_idle6.csv` l.579 |
| zipf | difficile (s=1.5) | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.580 |
| zipf | difficile (s=1.5) | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.583 |
| zipf | difficile (s=1.5) | greedy_pair | retour_au_depot | approche_moy_s | 14.6935 [14.2463 ; 15.1199] | `descriptif_idle6.csv` l.587 |
| zipf | difficile (s=1.5) | greedy_pair | retour_au_depot | taches_echouees | 0.1 [0.0 ; 0.3] | `descriptif_idle6.csv` l.588 |
| zipf | difficile (s=1.5) | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0023 [0.0021 ; 0.0024] | `descriptif_idle6.csv` l.591 |
| zipf | difficile (s=1.5) | greedy_pair | centre_de_demande | approche_moy_s | 12.1204 [11.6595 ; 12.5744] | `descriptif_idle6.csv` l.595 |
| zipf | difficile (s=1.5) | greedy_pair | centre_de_demande | taches_echouees | 0.1 [0.0 ; 0.3] | `descriptif_idle6.csv` l.596 |
| zipf | difficile (s=1.5) | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0615 [0.0605 ; 0.0626] | `descriptif_idle6.csv` l.599 |
| zipf | difficile (s=1.5) | greedy_pair | couverture | approche_moy_s | 9.8931 [9.3791 ; 10.3945] | `descriptif_idle6.csv` l.603 |
| zipf | difficile (s=1.5) | greedy_pair | couverture | taches_echouees | 0.1 [0.0 ; 0.3] | `descriptif_idle6.csv` l.604 |
| zipf | difficile (s=1.5) | greedy_pair | couverture | ms_par_decision_attente | 0.1135 [0.112 ; 0.115] | `descriptif_idle6.csv` l.607 |
| zipf | difficile (s=1.5) | greedy_pair | drl_idle | approche_moy_s | 10.4287 [9.9228 ; 10.9512] | `descriptif_idle6.csv` l.611 |
| zipf | difficile (s=1.5) | greedy_pair | drl_idle | taches_echouees | 0.1 [0.0 ; 0.3] | `descriptif_idle6.csv` l.612 |
| zipf | difficile (s=1.5) | greedy_pair | drl_idle | ms_par_decision_attente | 0.4077 [0.4031 ; 0.4125] | `descriptif_idle6.csv` l.615 |
| zipf | difficile (s=1.5) | greedy_pair | drl_idle6 | approche_moy_s | 9.7561 [9.2509 ; 10.3333] | `descriptif_idle6.csv` l.619 |
| zipf | difficile (s=1.5) | greedy_pair | drl_idle6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.620 |
| zipf | difficile (s=1.5) | greedy_pair | drl_idle6 | ms_par_decision_attente | 0.5753 [0.5691 ; 0.5816] | `descriptif_idle6.csv` l.623 |
| zipf | difficile (s=1.5) | greedy_time | rester_sur_place | approche_moy_s | 8.5453 [8.0016 ; 9.0576] | `descriptif_idle6.csv` l.627 |
| zipf | difficile (s=1.5) | greedy_time | rester_sur_place | taches_echouees | 0.1 [0.0 ; 0.3] | `descriptif_idle6.csv` l.628 |
| zipf | difficile (s=1.5) | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle6.csv` l.631 |
| zipf | difficile (s=1.5) | greedy_time | retour_au_depot | approche_moy_s | 13.3549 [12.8183 ; 13.878] | `descriptif_idle6.csv` l.635 |
| zipf | difficile (s=1.5) | greedy_time | retour_au_depot | taches_echouees | 0.1 [0.0 ; 0.3] | `descriptif_idle6.csv` l.636 |
| zipf | difficile (s=1.5) | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0014 [0.0013 ; 0.0014] | `descriptif_idle6.csv` l.639 |
| zipf | difficile (s=1.5) | greedy_time | centre_de_demande | approche_moy_s | 10.6681 [10.0666 ; 11.2439] | `descriptif_idle6.csv` l.643 |
| zipf | difficile (s=1.5) | greedy_time | centre_de_demande | taches_echouees | 0.1 [0.0 ; 0.3] | `descriptif_idle6.csv` l.644 |
| zipf | difficile (s=1.5) | greedy_time | centre_de_demande | ms_par_decision_attente | 0.0454 [0.044 ; 0.047] | `descriptif_idle6.csv` l.647 |
| zipf | difficile (s=1.5) | greedy_time | couverture | approche_moy_s | 9.4455 [8.8126 ; 10.0964] | `descriptif_idle6.csv` l.651 |
| zipf | difficile (s=1.5) | greedy_time | couverture | taches_echouees | 0.1 [0.0 ; 0.3] | `descriptif_idle6.csv` l.652 |
| zipf | difficile (s=1.5) | greedy_time | couverture | ms_par_decision_attente | 0.0905 [0.0892 ; 0.0919] | `descriptif_idle6.csv` l.655 |
| zipf | difficile (s=1.5) | greedy_time | drl_idle | approche_moy_s | 9.94 [9.2922 ; 10.5947] | `descriptif_idle6.csv` l.659 |
| zipf | difficile (s=1.5) | greedy_time | drl_idle | taches_echouees | 0.1 [0.0 ; 0.3] | `descriptif_idle6.csv` l.660 |
| zipf | difficile (s=1.5) | greedy_time | drl_idle | ms_par_decision_attente | 0.4133 [0.4085 ; 0.4182] | `descriptif_idle6.csv` l.663 |
| zipf | difficile (s=1.5) | greedy_time | drl_idle6 | approche_moy_s | 8.6863 [7.8756 ; 9.495] | `descriptif_idle6.csv` l.667 |
| zipf | difficile (s=1.5) | greedy_time | drl_idle6 | taches_echouees | 0.1 [0.0 ; 0.3] | `descriptif_idle6.csv` l.668 |
| zipf | difficile (s=1.5) | greedy_time | drl_idle6 | ms_par_decision_attente | 0.581 [0.5763 ; 0.5854] | `descriptif_idle6.csv` l.671 |

### Phase B

| experience | condition | allocation | methode | metrique | moyenne [IC95] | source |
|---|---|---|---|---|---|---|
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 21.7383 [20.7936 ; 22.6609] | `descriptif_route6.csv` l.3 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | attente_file_par_tache_s | 0.3991 [0.3144 ; 0.4933] | `descriptif_route6.csv` l.4 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.5 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | distance_par_tache_m | 10.2645 [9.8285 ; 10.6969] | `descriptif_route6.csv` l.6 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0329 [0.0299 ; 0.0359] | `descriptif_route6.csv` l.7 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.9 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 21.8943 [20.9664 ; 22.8143] | `descriptif_route6.csv` l.12 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | attente_file_par_tache_s | 0.359 [0.2827 ; 0.4447] | `descriptif_route6.csv` l.13 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.14 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | distance_par_tache_m | 10.3589 [9.9315 ; 10.7772] | `descriptif_route6.csv` l.15 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.102 [0.0898 ; 0.1158] | `descriptif_route6.csv` l.16 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.18 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | temps_trajet_moy_s | 21.6924 [20.6388 ; 22.722] | `descriptif_route6.csv` l.21 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | attente_file_par_tache_s | 0.3028 [0.246 ; 0.37] | `descriptif_route6.csv` l.22 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.23 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | distance_par_tache_m | 10.2884 [9.7892 ; 10.7784] | `descriptif_route6.csv` l.24 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | ms_par_decision_route | 0.8654 [0.8459 ; 0.8815] | `descriptif_route6.csv` l.25 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.27 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | temps_trajet_moy_s | 21.5946 [20.5999 ; 22.5818] | `descriptif_route6.csv` l.30 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | attente_file_par_tache_s | 0.2497 [0.2067 ; 0.2999] | `descriptif_route6.csv` l.31 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.32 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | distance_par_tache_m | 10.252 [9.7869 ; 10.7237] | `descriptif_route6.csv` l.33 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | ms_par_decision_route | 1.0116 [0.9781 ; 1.0548] | `descriptif_route6.csv` l.34 |
| congestion | B1 10 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.36 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 19.6578 [19.1238 ; 20.1714] | `descriptif_route6.csv` l.39 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | attente_file_par_tache_s | 2.0973 [1.802 ; 2.3949] | `descriptif_route6.csv` l.40 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.41 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | distance_par_tache_m | 8.4383 [8.1801 ; 8.6984] | `descriptif_route6.csv` l.42 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0611 [0.0578 ; 0.0653] | `descriptif_route6.csv` l.43 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_statique | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.45 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 19.3882 [18.9187 ; 19.8262] | `descriptif_route6.csv` l.48 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | attente_file_par_tache_s | 1.9783 [1.6794 ; 2.2577] | `descriptif_route6.csv` l.49 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.50 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | distance_par_tache_m | 8.3657 [8.1579 ; 8.5598] | `descriptif_route6.csv` l.51 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.1474 [0.1331 ; 0.1617] | `descriptif_route6.csv` l.52 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.54 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | temps_trajet_moy_s | 19.1114 [18.6155 ; 19.5822] | `descriptif_route6.csv` l.57 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | attente_file_par_tache_s | 1.9201 [1.6303 ; 2.1959] | `descriptif_route6.csv` l.58 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.59 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | distance_par_tache_m | 8.2601 [8.058 ; 8.4623] | `descriptif_route6.csv` l.60 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | ms_par_decision_route | 0.633 [0.583 ; 0.6937] | `descriptif_route6.csv` l.61 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | dijkstra_congestion | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.63 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | temps_trajet_moy_s | 19.1653 [18.7052 ; 19.6328] | `descriptif_route6.csv` l.66 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | attente_file_par_tache_s | 1.6885 [1.4477 ; 1.9123] | `descriptif_route6.csv` l.67 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.68 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | distance_par_tache_m | 8.293 [8.0988 ; 8.4843] | `descriptif_route6.csv` l.69 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | ms_par_decision_route | 0.9659 [0.9428 ; 1.0047] | `descriptif_route6.csv` l.70 |
| congestion | B2 20 r., 80 racks, rho=0.9 | greedy_pair | drl_route6 | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.72 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 27.3258 [26.1929 ; 28.3879] | `descriptif_route6.csv` l.75 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_statique | attente_file_par_tache_s | 1.9444 [1.6357 ; 2.2207] | `descriptif_route6.csv` l.76 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.77 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_statique | distance_par_tache_m | 12.2072 [11.728 ; 12.6568] | `descriptif_route6.csv` l.78 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.1312 [0.1115 ; 0.1517] | `descriptif_route6.csv` l.79 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_statique | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.81 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 27.8015 [26.4515 ; 29.0842] | `descriptif_route6.csv` l.84 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | attente_file_par_tache_s | 1.8814 [1.5987 ; 2.1586] | `descriptif_route6.csv` l.85 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.86 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | distance_par_tache_m | 12.4667 [11.8793 ; 13.0492] | `descriptif_route6.csv` l.87 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.234 [0.2092 ; 0.2647] | `descriptif_route6.csv` l.88 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_dynamique | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.90 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_congestion | temps_trajet_moy_s | 27.7057 [26.4487 ; 28.8998] | `descriptif_route6.csv` l.93 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_congestion | attente_file_par_tache_s | 1.8173 [1.5321 ; 2.0913] | `descriptif_route6.csv` l.94 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_congestion | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.95 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_congestion | distance_par_tache_m | 12.4515 [11.9193 ; 12.9578] | `descriptif_route6.csv` l.96 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_congestion | ms_par_decision_route | 1.2824 [1.2031 ; 1.3735] | `descriptif_route6.csv` l.97 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | dijkstra_congestion | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.99 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | drl_route6 | temps_trajet_moy_s | 27.2881 [26.1953 ; 28.3164] | `descriptif_route6.csv` l.102 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | drl_route6 | attente_file_par_tache_s | 1.5526 [1.3115 ; 1.7672] | `descriptif_route6.csv` l.103 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | drl_route6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.104 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | drl_route6 | distance_par_tache_m | 12.252 [11.7725 ; 12.7082] | `descriptif_route6.csv` l.105 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | drl_route6 | ms_par_decision_route | 1.4721 [1.4202 ; 1.5346] | `descriptif_route6.csv` l.106 |
| congestion | B3 20 r., 150 racks, rho=0.9 | greedy_pair | drl_route6 | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.108 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 10.0789 [8.9117 ; 11.2191] | `descriptif_route6.csv` l.111 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_statique | attente_file_par_tache_s | 0.404 [0.2632 ; 0.567] | `descriptif_route6.csv` l.112 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.113 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_statique | distance_par_tache_m | 4.6491 [4.1422 ; 5.138] | `descriptif_route6.csv` l.114 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0693 [0.0538 ; 0.0886] | `descriptif_route6.csv` l.115 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_statique | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.117 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 10.0389 [8.841 ; 11.2211] | `descriptif_route6.csv` l.120 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_dynamique | attente_file_par_tache_s | 0.3253 [0.2018 ; 0.4617] | `descriptif_route6.csv` l.121 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.122 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_dynamique | distance_par_tache_m | 4.6677 [4.1404 ; 5.1985] | `descriptif_route6.csv` l.123 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.1793 [0.1591 ; 0.2] | `descriptif_route6.csv` l.124 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_dynamique | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.126 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_congestion | temps_trajet_moy_s | 10.0097 [8.8392 ; 11.1469] | `descriptif_route6.csv` l.129 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_congestion | attente_file_par_tache_s | 0.3203 [0.1956 ; 0.4575] | `descriptif_route6.csv` l.130 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_congestion | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.131 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_congestion | distance_par_tache_m | 4.6559 [4.1378 ; 5.1674] | `descriptif_route6.csv` l.132 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_congestion | ms_par_decision_route | 1.2736 [1.2669 ; 1.2809] | `descriptif_route6.csv` l.133 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | dijkstra_congestion | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.135 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | drl_route6 | temps_trajet_moy_s | 9.9543 [8.7794 ; 11.1045] | `descriptif_route6.csv` l.138 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | drl_route6 | attente_file_par_tache_s | 0.2801 [0.1651 ; 0.4102] | `descriptif_route6.csv` l.139 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | drl_route6 | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.140 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | drl_route6 | distance_par_tache_m | 4.6402 [4.1267 ; 5.154] | `descriptif_route6.csv` l.141 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | drl_route6 | ms_par_decision_route | 1.768 [1.6997 ; 1.8566] | `descriptif_route6.csv` l.142 |
| congestion | B4 20 r., 150 racks, rho=0.7, vagues | greedy_pair | drl_route6 | replis_route6 | 0.0 [0.0 ; 0.0] | `descriptif_route6.csv` l.144 |

### Phase C

