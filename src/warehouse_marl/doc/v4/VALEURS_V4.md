# VALEURS_V4 : toutes les valeurs, avec leur fichier et leur ligne

Genere par `src/warehouse_marl/scripts/rapport_v4.py` a partir des CSV du dossier. Ligne 1 = en-tete du CSV ; "l.N" = N-ieme ligne du fichier. Protocole : `PROTOCOLE_V4.md` (copie dans ce dossier).

## 1. Selection des modeles (validation uniquement)

### drl_route

| graine | instant (min) | episode | validation (s) | retenu | source |
|---|---|---|---|---|---|
| 0 | 0.0 | 0 | 35.0801 |  | `entrainement_route/selection_route.csv` l.2 |
| 0 | 10.02 | 130 | 36.6643 |  | `entrainement_route/selection_route.csv` l.3 |
| 0 | 20.23 | 253 | 34.4089 |  | `entrainement_route/selection_route.csv` l.4 |
| 0 | 30.04 | 385 | 35.1556 |  | `entrainement_route/selection_route.csv` l.5 |
| 0 | 40.19 | 517 | 35.6779 |  | `entrainement_route/selection_route.csv` l.6 |
| 0 | 50.2 | 657 | 35.1112 |  | `entrainement_route/selection_route.csv` l.7 |
| 0 | 60.0 | 813 | 37.6540 |  | `entrainement_route/selection_route.csv` l.8 |
| 0 | 70.02 | 963 | 34.4578 |  | `entrainement_route/selection_route.csv` l.9 |
| 0 | 80.06 | 1125 | 39.7603 |  | `entrainement_route/selection_route.csv` l.10 |
| 0 | 90.09 | 1304 | 37.6126 |  | `entrainement_route/selection_route.csv` l.11 |
| 0 | 100.06 | 1504 | 34.5285 |  | `entrainement_route/selection_route.csv` l.12 |
| 0 | 110.11 | 1709 | 35.3016 |  | `entrainement_route/selection_route.csv` l.13 |
| 0 | 115.01 | 1784 | 33.9542 |  | `entrainement_route/selection_route.csv` l.14 |
| 1 | 0.0 | 0 | 35.0801 |  | `entrainement_route/selection_route.csv` l.15 |
| 1 | 10.01 | 147 | 37.8889 |  | `entrainement_route/selection_route.csv` l.16 |
| 1 | 20.0 | 290 | 34.6747 |  | `entrainement_route/selection_route.csv` l.17 |
| 1 | 30.07 | 419 | 40.8588 |  | `entrainement_route/selection_route.csv` l.18 |
| 1 | 40.17 | 569 | 35.0039 |  | `entrainement_route/selection_route.csv` l.19 |
| 1 | 50.0 | 725 | 42.0319 |  | `entrainement_route/selection_route.csv` l.20 |
| 1 | 60.02 | 868 | 33.8719 | **oui** | `entrainement_route/selection_route.csv` l.21 |
| 1 | 70.1 | 1002 | 36.6096 |  | `entrainement_route/selection_route.csv` l.22 |
| 1 | 80.2 | 1171 | 35.0043 |  | `entrainement_route/selection_route.csv` l.23 |
| 1 | 90.01 | 1299 | 35.0183 |  | `entrainement_route/selection_route.csv` l.24 |
| 1 | 100.1 | 1502 | 34.2198 |  | `entrainement_route/selection_route.csv` l.25 |
| 1 | 110.03 | 1689 | 34.2439 |  | `entrainement_route/selection_route.csv` l.26 |
| 1 | 115.06 | 1796 | 34.0367 |  | `entrainement_route/selection_route.csv` l.27 |
| 2 | 0.0 | 0 | 35.0801 |  | `entrainement_route/selection_route.csv` l.28 |
| 2 | 10.25 | 118 | 35.4804 |  | `entrainement_route/selection_route.csv` l.29 |
| 2 | 20.27 | 230 | 53.2057 |  | `entrainement_route/selection_route.csv` l.30 |
| 2 | 30.25 | 349 | 34.1149 |  | `entrainement_route/selection_route.csv` l.31 |
| 2 | 40.25 | 462 | 34.3285 |  | `entrainement_route/selection_route.csv` l.32 |
| 2 | 50.01 | 637 | 34.8745 |  | `entrainement_route/selection_route.csv` l.33 |
| 2 | 60.17 | 765 | 34.9764 |  | `entrainement_route/selection_route.csv` l.34 |
| 2 | 70.02 | 915 | 35.0195 |  | `entrainement_route/selection_route.csv` l.35 |
| 2 | 80.05 | 1081 | 37.4790 |  | `entrainement_route/selection_route.csv` l.36 |
| 2 | 90.2 | 1240 | 35.0879 |  | `entrainement_route/selection_route.csv` l.37 |
| 2 | 100.07 | 1426 | 34.7873 |  | `entrainement_route/selection_route.csv` l.38 |
| 2 | 110.01 | 1596 | 34.9509 |  | `entrainement_route/selection_route.csv` l.39 |
| 2 | 115.3 | 1694 | 34.7359 |  | `entrainement_route/selection_route.csv` l.40 |

- Graine 0 : 1784 episodes d'entrainement en 115.01 min (`entrainement_route/train_log_seed0.csv` l.1785).
- Graine 1 : 1796 episodes d'entrainement en 115.06 min (`entrainement_route/train_log_seed1.csv` l.1797).
- Graine 2 : 1694 episodes d'entrainement en 115.3 min (`entrainement_route/train_log_seed2.csv` l.1695).

### drl_idle

| graine | instant (min) | episode | validation (s) | retenu | source |
|---|---|---|---|---|---|
| 0 | 0.0 | 0 | 36.5951 |  | `entrainement_idle/selection_idle.csv` l.2 |
| 0 | 10.01 | 939 | 36.1033 |  | `entrainement_idle/selection_idle.csv` l.3 |
| 0 | 20.01 | 1805 | 35.5231 |  | `entrainement_idle/selection_idle.csv` l.4 |
| 0 | 30.0 | 2792 | 35.6830 |  | `entrainement_idle/selection_idle.csv` l.5 |
| 0 | 40.02 | 3629 | 35.9806 |  | `entrainement_idle/selection_idle.csv` l.6 |
| 0 | 50.0 | 4788 | 35.5055 |  | `entrainement_idle/selection_idle.csv` l.7 |
| 0 | 60.0 | 5650 | 35.5245 |  | `entrainement_idle/selection_idle.csv` l.8 |
| 0 | 70.0 | 6485 | 35.6581 |  | `entrainement_idle/selection_idle.csv` l.9 |
| 0 | 80.01 | 7315 | 35.5592 |  | `entrainement_idle/selection_idle.csv` l.10 |
| 0 | 90.0 | 8329 | 35.8681 |  | `entrainement_idle/selection_idle.csv` l.11 |
| 0 | 100.01 | 9148 | 35.1349 | **oui** | `entrainement_idle/selection_idle.csv` l.12 |
| 0 | 110.0 | 10479 | 35.8709 |  | `entrainement_idle/selection_idle.csv` l.13 |
| 0 | 115.02 | 10942 | 35.7623 |  | `entrainement_idle/selection_idle.csv` l.14 |
| 1 | 0.0 | 0 | 36.5951 |  | `entrainement_idle/selection_idle.csv` l.15 |
| 1 | 10.01 | 1200 | 35.5665 |  | `entrainement_idle/selection_idle.csv` l.16 |
| 1 | 20.0 | 2154 | 35.3985 |  | `entrainement_idle/selection_idle.csv` l.17 |
| 1 | 30.0 | 3177 | 35.8566 |  | `entrainement_idle/selection_idle.csv` l.18 |
| 1 | 40.02 | 4258 | 36.6591 |  | `entrainement_idle/selection_idle.csv` l.19 |
| 1 | 50.0 | 5190 | 35.4087 |  | `entrainement_idle/selection_idle.csv` l.20 |
| 1 | 60.0 | 6179 | 35.3051 |  | `entrainement_idle/selection_idle.csv` l.21 |
| 1 | 70.01 | 7248 | 35.9098 |  | `entrainement_idle/selection_idle.csv` l.22 |
| 1 | 80.01 | 8059 | 36.4047 |  | `entrainement_idle/selection_idle.csv` l.23 |
| 1 | 90.01 | 9007 | 35.7591 |  | `entrainement_idle/selection_idle.csv` l.24 |
| 1 | 100.01 | 9929 | 36.0108 |  | `entrainement_idle/selection_idle.csv` l.25 |
| 1 | 110.0 | 10772 | 36.0344 |  | `entrainement_idle/selection_idle.csv` l.26 |
| 1 | 115.0 | 11196 | 35.5862 |  | `entrainement_idle/selection_idle.csv` l.27 |
| 2 | 0.0 | 0 | 36.5951 |  | `entrainement_idle/selection_idle.csv` l.28 |
| 2 | 10.01 | 883 | 35.8980 |  | `entrainement_idle/selection_idle.csv` l.29 |
| 2 | 20.01 | 1929 | 36.9899 |  | `entrainement_idle/selection_idle.csv` l.30 |
| 2 | 30.01 | 2802 | 36.5498 |  | `entrainement_idle/selection_idle.csv` l.31 |
| 2 | 40.01 | 3842 | 35.7163 |  | `entrainement_idle/selection_idle.csv` l.32 |
| 2 | 50.02 | 4659 | 35.9187 |  | `entrainement_idle/selection_idle.csv` l.33 |
| 2 | 60.0 | 5652 | 35.8335 |  | `entrainement_idle/selection_idle.csv` l.34 |
| 2 | 70.0 | 6653 | 35.4119 |  | `entrainement_idle/selection_idle.csv` l.35 |
| 2 | 80.0 | 8002 | 35.5139 |  | `entrainement_idle/selection_idle.csv` l.36 |
| 2 | 90.0 | 9009 | 36.5683 |  | `entrainement_idle/selection_idle.csv` l.37 |
| 2 | 100.0 | 10255 | 37.1854 |  | `entrainement_idle/selection_idle.csv` l.38 |
| 2 | 110.01 | 11055 | 36.7007 |  | `entrainement_idle/selection_idle.csv` l.39 |
| 2 | 115.01 | 11486 | 36.0448 |  | `entrainement_idle/selection_idle.csv` l.40 |

- Graine 0 : 10942 episodes d'entrainement en 115.02 min (`entrainement_idle/train_log_seed0.csv` l.10943).
- Graine 1 : 11196 episodes d'entrainement en 115.0 min (`entrainement_idle/train_log_seed1.csv` l.11197).
- Graine 2 : 11486 episodes d'entrainement en 115.01 min (`entrainement_idle/train_log_seed2.csv` l.11487).

## 2. Etape 1 : DRL de chemin (famille A, 24 tests, Holm)

| experience | condition | allocation | DRL (s) [IC95] | meilleure heuristique (s) [IC95] | ecart (s) [IC95] | gagnes | echecs DRL/heur. | p Wilcoxon | p Holm | conclusion | source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| blocages | 0 blocage/min | greedy_pair | 26.083 [25.596 ; 26.603] | dijkstra_dynamique 26.033 [25.552 ; 26.503] | 0.051 [-0.037 ; 0.137] | 6/20 | 0/0 | 0.2759 | 1 | pas de difference significative | `principal_route.csv` l.2 |
| blocages | 0 blocage/min | consensus | 33.856 [31.72 ; 36.217] | dijkstra_dynamique 34.107 [31.943 ; 36.384] | -0.251 [-0.819 ; 0.11] | 8/20 | 0/0 | 0.7628 | 1 | pas de difference significative | `principal_route.csv` l.3 |
| blocages | 1 blocage/min | greedy_pair | 26.962 [26.239 ; 27.892] | dijkstra_dynamique 26.982 [26.286 ; 27.965] | -0.02 [-0.222 ; 0.197] | 13/20 | 0/0 | 0.498 | 1 | pas de difference significative | `principal_route.csv` l.4 |
| blocages | 1 blocage/min | consensus | 35.667 [33.335 ; 38.089] | dijkstra_dynamique 35.916 [33.542 ; 38.367] | -0.249 [-0.816 ; 0.251] | 8/20 | 0/0 | 0.9563 | 1 | pas de difference significative | `principal_route.csv` l.5 |
| blocages | 3 blocage/min | greedy_pair | 32.866 [30.985 ; 34.833] | dijkstra_dynamique 31.643 [29.94 ; 33.407] | 1.223 [0.379 ; 2.078] | 6/20 | 4/0 | 0.01923 | 0.4424 | pas de difference significative | `principal_route.csv` l.6 |
| blocages | 3 blocage/min | consensus | 47.05 [43.038 ; 51.385] | dijkstra_dynamique 46.731 [42.612 ; 51.272] | 0.319 [-2.758 ; 3.282] | 8/20 | 5/2 | 0.4524 | 1 | pas de difference significative | `principal_route.csv` l.7 |
| blocages | 6 blocage/min | greedy_pair | 52.898 [50.56 ; 55.3] | dijkstra_dynamique 51.793 [49.353 ; 54.354] | 1.106 [-1.351 ; 3.759] | 8/20 | 78/43 | 0.498 | 1 | pas de difference significative | `principal_route.csv` l.8 |
| blocages | 6 blocage/min | consensus | 90.562 [78.777 ; 103.066] | dijkstra_dynamique 73.748 [65.171 ; 83.763] | 16.814 [3.909 ; 29.801] | 4/20 | 51/27 | 0.004221 | 0.1013 | pas de difference significative | `principal_route.csv` l.9 |
| taille | 3 robots, 15 racks | greedy_pair | 26.962 [26.239 ; 27.892] | dijkstra_dynamique 26.982 [26.286 ; 27.965] | -0.02 [-0.222 ; 0.197] | 13/20 | 0/0 | 0.498 | 1 | pas de difference significative | `principal_route.csv` l.10 |
| taille | 3 robots, 15 racks | consensus | 35.667 [33.335 ; 38.089] | dijkstra_dynamique 35.916 [33.542 ; 38.367] | -0.249 [-0.816 ; 0.251] | 8/20 | 0/0 | 0.9563 | 1 | pas de difference significative | `principal_route.csv` l.11 |
| taille | 6 robots, 40 racks | greedy_pair | 29.024 [28.187 ; 29.899] | dijkstra_dynamique 28.985 [28.123 ; 29.897] | 0.039 [-0.087 ; 0.158] | 7/20 | 0/0 | 0.605 | 1 | pas de difference significative | `principal_route.csv` l.12 |
| taille | 6 robots, 40 racks | consensus | 31.836 [30.315 ; 33.471] | dijkstra_statique 31.896 [30.349 ; 33.513] | -0.06 [-0.628 ; 0.539] | 9/20 | 0/0 | 0.9679 | 1 | pas de difference significative | `principal_route.csv` l.13 |
| taille | 10 robots, 80 racks | greedy_pair | 30.339 [29.485 ; 31.191] | dijkstra_statique 30.469 [29.639 ; 31.3] | -0.13 [-0.564 ; 0.2] | 12/20 | 0/0 | 0.3271 | 1 | pas de difference significative | `principal_route.csv` l.14 |
| taille | 10 robots, 80 racks | consensus | 33.028 [31.728 ; 34.501] | dijkstra_statique 33.015 [31.735 ; 34.424] | 0.013 [-0.216 ; 0.264] | 11/20 | 0/0 | 0.8092 | 1 | pas de difference significative | `principal_route.csv` l.15 |
| taille | 20 robots, 150 racks | greedy_pair | 35.43 [34.424 ; 36.568] | dijkstra_dynamique 35.39 [34.282 ; 36.604] | 0.041 [-0.227 ; 0.305] | 12/20 | 0/0 | 0.8695 | 1 | pas de difference significative | `principal_route.csv` l.16 |
| taille | 20 robots, 150 racks | consensus | 37.547 [36.394 ; 38.8] | dijkstra_dynamique 37.698 [36.393 ; 39.317] | -0.15 [-0.623 ; 0.235] | 11/20 | 0/0 | 0.7112 | 1 | pas de difference significative | `principal_route.csv` l.17 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | 30.568 [27.097 ; 35.881] | dijkstra_dynamique 30.569 [27.084 ; 35.878] | -0.001 [-0.022 ; 0.024] | 4/20 | 0/0 | 0.4982 | 1 | pas de difference significative | `principal_route.csv` l.18 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | 41.426 [34.69 ; 50.562] | dijkstra_dynamique 41.433 [34.692 ; 50.578] | -0.007 [-0.04 ; 0.024] | 4/20 | 0/0 | 0.5992 | 1 | pas de difference significative | `principal_route.csv` l.19 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | 45.092 [36.695 ; 56.834] | dijkstra_statique 45.027 [36.582 ; 56.689] | 0.065 [-0.027 ; 0.21] | 2/20 | 0/0 | 0.3105 | 1 | pas de difference significative | `principal_route.csv` l.20 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | 62.605 [49.695 ; 79.697] | dijkstra_dynamique 62.513 [49.577 ; 79.643] | 0.092 [0.018 ; 0.182] | 1/20 | 0/0 | 0.04252 | 0.9355 | pas de difference significative | `principal_route.csv` l.21 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | 53.336 [41.637 ; 68.515] | dijkstra_dynamique 52.764 [41.103 ; 68.064] | 0.572 [0.05 ; 1.273] | 3/20 | 0/0 | 0.1141 | 1 | pas de difference significative | `principal_route.csv` l.22 |
| dataset | 40 racks, 6 r., vit. var. | consensus | 64.445 [49.677 ; 83.315] | dijkstra_dynamique 64.831 [50.228 ; 83.778] | -0.386 [-0.942 ; 0.048] | 8/20 | 0/0 | 0.5701 | 1 | pas de difference significative | `principal_route.csv` l.23 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | 61.354 [48.451 ; 79.026] | dijkstra_dynamique 61.371 [48.391 ; 79.107] | -0.017 [-0.263 ; 0.32] | 13/20 | 0/0 | 0.2668 | 1 | pas de difference significative | `principal_route.csv` l.24 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | 70.698 [55.683 ; 91.844] | dijkstra_dynamique 71.033 [55.826 ; 92.093] | -0.334 [-0.71 ; 0.0] | 11/20 | 0/0 | 0.1446 | 1 | pas de difference significative | `principal_route.csv` l.25 |

Decompte (meme fichier) : pas de difference significative : 24/24

## 3. Etape 2 : DRL d anticipation (famille B, 14 tests, Holm)

| experience | condition | allocation | DRL (s) [IC95] | meilleure heuristique (s) [IC95] | ecart (s) [IC95] | gagnes | echecs DRL/heur. | p Wilcoxon | p Holm | conclusion | source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | 27.852 [24.864 ; 32.385] | centre_de_demande 30.11 [26.966 ; 34.993] | -2.258 [-2.851 ; -1.698] | 20/20 | 0/0 | 2e-06 | 2.7e-05 | DRL meilleur (significatif) | `principal_idle.csv` l.2 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | 27.852 [24.864 ; 32.385] | centre_de_demande 30.11 [26.966 ; 34.993] | -2.258 [-2.851 ; -1.698] | 20/20 | 0/0 | 2e-06 | 2.7e-05 | DRL meilleur (significatif) | `principal_idle.csv` l.3 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | 41.969 [34.051 ; 53.088] | centre_de_demande 42.969 [34.895 ; 54.166] | -1.0 [-1.552 ; -0.504] | 15/20 | 0/0 | 0.001209 | 0.01088 | DRL meilleur (significatif) | `principal_idle.csv` l.4 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | 41.969 [34.051 ; 53.088] | centre_de_demande 42.969 [34.895 ; 54.166] | -1.0 [-1.552 ; -0.504] | 15/20 | 0/0 | 0.001209 | 0.01088 | DRL meilleur (significatif) | `principal_idle.csv` l.5 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | 47.148 [37.749 ; 59.147] | centre_de_demande 51.885 [42.388 ; 64.095] | -4.738 [-5.601 ; -3.915] | 20/20 | 0/0 | 2e-06 | 2.7e-05 | DRL meilleur (significatif) | `principal_idle.csv` l.6 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | 48.48 [39.078 ; 60.145] | centre_de_demande 49.997 [40.526 ; 62.13] | -1.517 [-3.049 ; 0.354] | 16/20 | 0/0 | 0.01718 | 0.1203 | pas de difference significative | `principal_idle.csv` l.7 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | 67.91 [54.58 ; 86.121] | rester_sur_place 61.371 [48.391 ; 79.107] | 6.538 [4.922 ; 8.197] | 1/20 | 0/0 | 6e-06 | 6.3e-05 | heuristique meilleure (significatif) | `principal_idle.csv` l.8 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | 67.91 [54.58 ; 86.121] | rester_sur_place 61.371 [48.391 ; 79.107] | 6.538 [4.922 ; 8.197] | 1/20 | 0/0 | 6e-06 | 6.3e-05 | heuristique meilleure (significatif) | `principal_idle.csv` l.9 |
| zipf | facile (s=0.5) | greedy_pair | 27.36 [26.417 ; 28.389] | rester_sur_place 27.47 [26.584 ; 28.361] | -0.11 [-0.919 ; 0.721] | 12/20 | 0/0 | 0.7841 | 1 | pas de difference significative | `principal_idle.csv` l.10 |
| zipf | facile (s=0.5) | greedy_time | 27.059 [26.148 ; 27.951] | rester_sur_place 27.109 [26.342 ; 27.891] | -0.05 [-0.82 ; 0.652] | 9/20 | 0/0 | 1 | 1 | pas de difference significative | `principal_idle.csv` l.11 |
| zipf | moyen (s=1.0) | greedy_pair | 29.088 [28.091 ; 30.278] | rester_sur_place 27.873 [26.89 ; 28.86] | 1.215 [0.345 ; 2.078] | 7/20 | 0/0 | 0.02664 | 0.1599 | pas de difference significative | `principal_idle.csv` l.12 |
| zipf | moyen (s=1.0) | greedy_time | 28.496 [27.321 ; 29.785] | rester_sur_place 28.165 [27.251 ; 29.269] | 0.33 [-0.461 ; 1.117] | 8/20 | 0/1 | 0.4091 | 1 | pas de difference significative | `principal_idle.csv` l.13 |
| zipf | difficile (s=1.5) | greedy_pair | 29.96 [28.901 ; 31.079] | rester_sur_place 28.712 [27.056 ; 30.472] | 1.248 [-0.325 ; 2.911] | 5/20 | 1/1 | 0.1231 | 0.6155 | pas de difference significative | `principal_idle.csv` l.14 |
| zipf | difficile (s=1.5) | greedy_time | 28.563 [27.501 ; 29.64] | rester_sur_place 27.613 [26.224 ; 29.054] | 0.95 [-0.315 ; 2.142] | 7/20 | 1/1 | 0.1536 | 0.6155 | pas de difference significative | `principal_idle.csv` l.15 |

Decompte (meme fichier) : DRL meilleur (significatif) : 5/14 ; heuristique meilleure (significatif) : 2/14 ; pas de difference significative : 7/14

## 4. Metriques secondaires (moyenne et IC 95 %, toutes methodes)

Tests DRL contre chaque adversaire et par metrique (Holm par famille) : `secondaire_route.csv`, `secondaire_idle.csv`.

### Etape 1

| experience | condition | allocation | methode | metrique | moyenne [IC95] | source |
|---|---|---|---|---|---|---|
| blocages | 0 blocage/min | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 11.1312 [10.7669 ; 11.4769] | `descriptif_route.csv` l.3 |
| blocages | 0 blocage/min | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.4 |
| blocages | 0 blocage/min | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 3.1667 [2.4667 ; 3.8667] | `descriptif_route.csv` l.5 |
| blocages | 0 blocage/min | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.6 |
| blocages | 0 blocage/min | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0255 [0.0208 ; 0.0319] | `descriptif_route.csv` l.8 |
| blocages | 0 blocage/min | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.10 |
| blocages | 0 blocage/min | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 11.105 [10.7381 ; 11.4562] | `descriptif_route.csv` l.13 |
| blocages | 0 blocage/min | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.14 |
| blocages | 0 blocage/min | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 2.7 [2.1 ; 3.3333] | `descriptif_route.csv` l.15 |
| blocages | 0 blocage/min | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.16 |
| blocages | 0 blocage/min | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.066 [0.0566 ; 0.0764] | `descriptif_route.csv` l.18 |
| blocages | 0 blocage/min | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.20 |
| blocages | 0 blocage/min | greedy_pair | drl_route | temps_trajet_moy_s | 11.1218 [10.7529 ; 11.4646] | `descriptif_route.csv` l.23 |
| blocages | 0 blocage/min | greedy_pair | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.24 |
| blocages | 0 blocage/min | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 2.1667 [1.6333 ; 2.7333] | `descriptif_route.csv` l.25 |
| blocages | 0 blocage/min | greedy_pair | drl_route | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.26 |
| blocages | 0 blocage/min | greedy_pair | drl_route | ms_par_decision_route | 0.7047 [0.6489 ; 0.7814] | `descriptif_route.csv` l.28 |
| blocages | 0 blocage/min | greedy_pair | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.30 |
| blocages | 0 blocage/min | consensus | dijkstra_statique | temps_trajet_moy_s | 12.3548 [12.0368 ; 12.6822] | `descriptif_route.csv` l.33 |
| blocages | 0 blocage/min | consensus | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.34 |
| blocages | 0 blocage/min | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 4.1333 [3.3667 ; 4.9] | `descriptif_route.csv` l.35 |
| blocages | 0 blocage/min | consensus | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.36 |
| blocages | 0 blocage/min | consensus | dijkstra_statique | ms_par_decision_route | 0.0214 [0.0185 ; 0.0255] | `descriptif_route.csv` l.38 |
| blocages | 0 blocage/min | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.40 |
| blocages | 0 blocage/min | consensus | dijkstra_dynamique | temps_trajet_moy_s | 12.3428 [12.004 ; 12.683] | `descriptif_route.csv` l.43 |
| blocages | 0 blocage/min | consensus | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.44 |
| blocages | 0 blocage/min | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 3.4333 [2.8 ; 4.0667] | `descriptif_route.csv` l.45 |
| blocages | 0 blocage/min | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.46 |
| blocages | 0 blocage/min | consensus | dijkstra_dynamique | ms_par_decision_route | 0.0543 [0.0492 ; 0.0603] | `descriptif_route.csv` l.48 |
| blocages | 0 blocage/min | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.50 |
| blocages | 0 blocage/min | consensus | drl_route | temps_trajet_moy_s | 12.2596 [11.9263 ; 12.5874] | `descriptif_route.csv` l.53 |
| blocages | 0 blocage/min | consensus | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.54 |
| blocages | 0 blocage/min | consensus | drl_route | conflits_aretes_pour_100_taches | 3.1 [2.4 ; 3.9] | `descriptif_route.csv` l.55 |
| blocages | 0 blocage/min | consensus | drl_route | attente_noeud_par_tache_s | 0.0003 [0.0 ; 0.001] | `descriptif_route.csv` l.56 |
| blocages | 0 blocage/min | consensus | drl_route | ms_par_decision_route | 0.6719 [0.6364 ; 0.7117] | `descriptif_route.csv` l.58 |
| blocages | 0 blocage/min | consensus | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.60 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 11.6082 [11.1588 ; 12.0421] | `descriptif_route.csv` l.63 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.64 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 4.1667 [3.4 ; 4.9] | `descriptif_route.csv` l.65 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 0.0223 [0.0 ; 0.0567] | `descriptif_route.csv` l.66 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0216 [0.0175 ; 0.0274] | `descriptif_route.csv` l.68 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.70 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 11.5655 [11.1126 ; 12.0092] | `descriptif_route.csv` l.73 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.74 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 3.7 [3.0667 ; 4.3] | `descriptif_route.csv` l.75 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0158 [0.0 ; 0.0458] | `descriptif_route.csv` l.76 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.0541 [0.0486 ; 0.0606] | `descriptif_route.csv` l.78 |
| blocages | 1 blocage/min | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.80 |
| blocages | 1 blocage/min | greedy_pair | drl_route | temps_trajet_moy_s | 11.5347 [11.1337 ; 11.9465] | `descriptif_route.csv` l.83 |
| blocages | 1 blocage/min | greedy_pair | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.84 |
| blocages | 1 blocage/min | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 2.6 [2.1 ; 3.0667] | `descriptif_route.csv` l.85 |
| blocages | 1 blocage/min | greedy_pair | drl_route | attente_noeud_par_tache_s | 0.0784 [0.0294 ; 0.1362] | `descriptif_route.csv` l.86 |
| blocages | 1 blocage/min | greedy_pair | drl_route | ms_par_decision_route | 0.6211 [0.5935 ; 0.6563] | `descriptif_route.csv` l.88 |
| blocages | 1 blocage/min | greedy_pair | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.90 |
| blocages | 1 blocage/min | consensus | dijkstra_statique | temps_trajet_moy_s | 13.0887 [12.6636 ; 13.5447] | `descriptif_route.csv` l.93 |
| blocages | 1 blocage/min | consensus | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.94 |
| blocages | 1 blocage/min | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 5.8667 [4.8667 ; 6.7667] | `descriptif_route.csv` l.95 |
| blocages | 1 blocage/min | consensus | dijkstra_statique | attente_noeud_par_tache_s | 0.0049 [0.0 ; 0.0147] | `descriptif_route.csv` l.96 |
| blocages | 1 blocage/min | consensus | dijkstra_statique | ms_par_decision_route | 0.016 [0.0154 ; 0.0166] | `descriptif_route.csv` l.98 |
| blocages | 1 blocage/min | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.100 |
| blocages | 1 blocage/min | consensus | dijkstra_dynamique | temps_trajet_moy_s | 13.0976 [12.6898 ; 13.5427] | `descriptif_route.csv` l.103 |
| blocages | 1 blocage/min | consensus | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.104 |
| blocages | 1 blocage/min | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 5.4 [4.4667 ; 6.2667] | `descriptif_route.csv` l.105 |
| blocages | 1 blocage/min | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0049 [0.0 ; 0.0147] | `descriptif_route.csv` l.106 |
| blocages | 1 blocage/min | consensus | dijkstra_dynamique | ms_par_decision_route | 0.0436 [0.0421 ; 0.0452] | `descriptif_route.csv` l.108 |
| blocages | 1 blocage/min | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.110 |
| blocages | 1 blocage/min | consensus | drl_route | temps_trajet_moy_s | 12.9736 [12.5693 ; 13.4299] | `descriptif_route.csv` l.113 |
| blocages | 1 blocage/min | consensus | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.114 |
| blocages | 1 blocage/min | consensus | drl_route | conflits_aretes_pour_100_taches | 4.2 [3.2667 ; 5.2] | `descriptif_route.csv` l.115 |
| blocages | 1 blocage/min | consensus | drl_route | attente_noeud_par_tache_s | 0.1017 [0.0523 ; 0.1638] | `descriptif_route.csv` l.116 |
| blocages | 1 blocage/min | consensus | drl_route | ms_par_decision_route | 0.552 [0.5348 ; 0.5709] | `descriptif_route.csv` l.118 |
| blocages | 1 blocage/min | consensus | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.120 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 13.9117 [13.2062 ; 14.6433] | `descriptif_route.csv` l.123 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.124 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 6.4667 [5.1 ; 7.9] | `descriptif_route.csv` l.125 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 0.6222 [0.4103 ; 0.8642] | `descriptif_route.csv` l.126 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0211 [0.0192 ; 0.0229] | `descriptif_route.csv` l.128 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.130 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 13.7199 [13.0162 ; 14.4816] | `descriptif_route.csv` l.133 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.134 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 5.5333 [4.5 ; 6.6667] | `descriptif_route.csv` l.135 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 0.7043 [0.4883 ; 0.934] | `descriptif_route.csv` l.136 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.0484 [0.0443 ; 0.0524] | `descriptif_route.csv` l.138 |
| blocages | 3 blocage/min | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.140 |
| blocages | 3 blocage/min | greedy_pair | drl_route | temps_trajet_moy_s | 14.3134 [13.5454 ; 15.0859] | `descriptif_route.csv` l.143 |
| blocages | 3 blocage/min | greedy_pair | drl_route | taches_echouees | 0.2 [0.05 ; 0.4] | `descriptif_route.csv` l.144 |
| blocages | 3 blocage/min | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 4.0049 [3.2398 ; 4.7725] | `descriptif_route.csv` l.145 |
| blocages | 3 blocage/min | greedy_pair | drl_route | attente_noeud_par_tache_s | 1.7683 [1.3127 ; 2.268] | `descriptif_route.csv` l.146 |
| blocages | 3 blocage/min | greedy_pair | drl_route | ms_par_decision_route | 0.5188 [0.5034 ; 0.5358] | `descriptif_route.csv` l.148 |
| blocages | 3 blocage/min | greedy_pair | drl_route | replis_dijkstra | 3.4 [0.3 ; 8.85] | `descriptif_route.csv` l.150 |
| blocages | 3 blocage/min | consensus | dijkstra_statique | temps_trajet_moy_s | 16.0091 [15.3561 ; 16.6468] | `descriptif_route.csv` l.153 |
| blocages | 3 blocage/min | consensus | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.154 |
| blocages | 3 blocage/min | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 9.7333 [8.3667 ; 11.1] | `descriptif_route.csv` l.155 |
| blocages | 3 blocage/min | consensus | dijkstra_statique | attente_noeud_par_tache_s | 0.3153 [0.2012 ; 0.4453] | `descriptif_route.csv` l.156 |
| blocages | 3 blocage/min | consensus | dijkstra_statique | ms_par_decision_route | 0.0209 [0.0182 ; 0.0239] | `descriptif_route.csv` l.158 |
| blocages | 3 blocage/min | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.160 |
| blocages | 3 blocage/min | consensus | dijkstra_dynamique | temps_trajet_moy_s | 15.7143 [15.0298 ; 16.3596] | `descriptif_route.csv` l.163 |
| blocages | 3 blocage/min | consensus | dijkstra_dynamique | taches_echouees | 0.1 [0.0 ; 0.25] | `descriptif_route.csv` l.164 |
| blocages | 3 blocage/min | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 8.1732 [6.9065 ; 9.377] | `descriptif_route.csv` l.165 |
| blocages | 3 blocage/min | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 0.3984 [0.2331 ; 0.5947] | `descriptif_route.csv` l.166 |
| blocages | 3 blocage/min | consensus | dijkstra_dynamique | ms_par_decision_route | 0.0639 [0.0543 ; 0.0745] | `descriptif_route.csv` l.168 |
| blocages | 3 blocage/min | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.170 |
| blocages | 3 blocage/min | consensus | drl_route | temps_trajet_moy_s | 15.8531 [15.087 ; 16.5723] | `descriptif_route.csv` l.173 |
| blocages | 3 blocage/min | consensus | drl_route | taches_echouees | 0.25 [0.05 ; 0.45] | `descriptif_route.csv` l.174 |
| blocages | 3 blocage/min | consensus | drl_route | conflits_aretes_pour_100_taches | 5.8103 [4.6049 ; 7.14] | `descriptif_route.csv` l.175 |
| blocages | 3 blocage/min | consensus | drl_route | attente_noeud_par_tache_s | 1.5138 [1.1942 ; 1.8267] | `descriptif_route.csv` l.176 |
| blocages | 3 blocage/min | consensus | drl_route | ms_par_decision_route | 0.5537 [0.5334 ; 0.5754] | `descriptif_route.csv` l.178 |
| blocages | 3 blocage/min | consensus | drl_route | replis_dijkstra | 6.1 [0.45 ; 16.5] | `descriptif_route.csv` l.180 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 19.3593 [18.4422 ; 20.3169] | `descriptif_route.csv` l.183 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_statique | taches_echouees | 2.15 [1.7 ; 2.65] | `descriptif_route.csv` l.184 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 10.8212 [9.292 ; 12.4562] | `descriptif_route.csv` l.185 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 5.7867 [5.0778 ; 6.4219] | `descriptif_route.csv` l.186 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0178 [0.0163 ; 0.0194] | `descriptif_route.csv` l.188 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.190 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 19.1132 [18.4063 ; 19.8255] | `descriptif_route.csv` l.193 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_dynamique | taches_echouees | 2.15 [1.7 ; 2.7] | `descriptif_route.csv` l.194 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 8.9923 [7.9429 ; 10.0416] | `descriptif_route.csv` l.195 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 6.1432 [5.461 ; 6.8188] | `descriptif_route.csv` l.196 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.0367 [0.033 ; 0.0406] | `descriptif_route.csv` l.198 |
| blocages | 6 blocage/min | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.200 |
| blocages | 6 blocage/min | greedy_pair | drl_route | temps_trajet_moy_s | 18.9352 [18.2861 ; 19.5709] | `descriptif_route.csv` l.203 |
| blocages | 6 blocage/min | greedy_pair | drl_route | taches_echouees | 3.9 [3.0 ; 4.9] | `descriptif_route.csv` l.204 |
| blocages | 6 blocage/min | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 4.3688 [3.5867 ; 5.1579] | `descriptif_route.csv` l.205 |
| blocages | 6 blocage/min | greedy_pair | drl_route | attente_noeud_par_tache_s | 8.9388 [8.1134 ; 9.8821] | `descriptif_route.csv` l.206 |
| blocages | 6 blocage/min | greedy_pair | drl_route | ms_par_decision_route | 0.4283 [0.4029 ; 0.4525] | `descriptif_route.csv` l.208 |
| blocages | 6 blocage/min | greedy_pair | drl_route | replis_dijkstra | 33.25 [7.85 ; 68.2] | `descriptif_route.csv` l.210 |
| blocages | 6 blocage/min | consensus | dijkstra_statique | temps_trajet_moy_s | 19.1291 [18.0733 ; 20.1918] | `descriptif_route.csv` l.213 |
| blocages | 6 blocage/min | consensus | dijkstra_statique | taches_echouees | 1.1 [0.75 ; 1.5] | `descriptif_route.csv` l.214 |
| blocages | 6 blocage/min | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 14.484 [12.6643 ; 16.5786] | `descriptif_route.csv` l.215 |
| blocages | 6 blocage/min | consensus | dijkstra_statique | attente_noeud_par_tache_s | 2.7387 [2.3253 ; 3.1781] | `descriptif_route.csv` l.216 |
| blocages | 6 blocage/min | consensus | dijkstra_statique | ms_par_decision_route | 0.0128 [0.0109 ; 0.0149] | `descriptif_route.csv` l.218 |
| blocages | 6 blocage/min | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.220 |
| blocages | 6 blocage/min | consensus | dijkstra_dynamique | temps_trajet_moy_s | 18.5391 [17.7612 ; 19.3745] | `descriptif_route.csv` l.223 |
| blocages | 6 blocage/min | consensus | dijkstra_dynamique | taches_echouees | 1.35 [0.95 ; 1.8] | `descriptif_route.csv` l.224 |
| blocages | 6 blocage/min | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 11.374 [10.0993 ; 12.6668] | `descriptif_route.csv` l.225 |
| blocages | 6 blocage/min | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 3.3241 [2.9456 ; 3.7645] | `descriptif_route.csv` l.226 |
| blocages | 6 blocage/min | consensus | dijkstra_dynamique | ms_par_decision_route | 0.0341 [0.0296 ; 0.0385] | `descriptif_route.csv` l.228 |
| blocages | 6 blocage/min | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.230 |
| blocages | 6 blocage/min | consensus | drl_route | temps_trajet_moy_s | 20.2483 [19.2695 ; 21.3517] | `descriptif_route.csv` l.233 |
| blocages | 6 blocage/min | consensus | drl_route | taches_echouees | 2.55 [1.95 ; 3.2] | `descriptif_route.csv` l.234 |
| blocages | 6 blocage/min | consensus | drl_route | conflits_aretes_pour_100_taches | 5.8716 [5.0641 ; 6.7561] | `descriptif_route.csv` l.235 |
| blocages | 6 blocage/min | consensus | drl_route | attente_noeud_par_tache_s | 7.3666 [6.5152 ; 8.2146] | `descriptif_route.csv` l.236 |
| blocages | 6 blocage/min | consensus | drl_route | ms_par_decision_route | 0.3681 [0.3356 ; 0.4013] | `descriptif_route.csv` l.238 |
| blocages | 6 blocage/min | consensus | drl_route | replis_dijkstra | 53.15 [18.4 ; 93.4] | `descriptif_route.csv` l.240 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 11.6082 [11.1588 ; 12.0421] | `descriptif_route.csv` l.243 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.244 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 4.1667 [3.4 ; 4.9] | `descriptif_route.csv` l.245 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 0.0223 [0.0 ; 0.0567] | `descriptif_route.csv` l.246 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0116 [0.0103 ; 0.0129] | `descriptif_route.csv` l.248 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.250 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 11.5655 [11.1126 ; 12.0092] | `descriptif_route.csv` l.253 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.254 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 3.7 [3.0667 ; 4.3] | `descriptif_route.csv` l.255 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0158 [0.0 ; 0.0458] | `descriptif_route.csv` l.256 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.031 [0.0271 ; 0.0351] | `descriptif_route.csv` l.258 |
| taille | 3 robots, 15 racks | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.260 |
| taille | 3 robots, 15 racks | greedy_pair | drl_route | temps_trajet_moy_s | 11.5347 [11.1337 ; 11.9465] | `descriptif_route.csv` l.263 |
| taille | 3 robots, 15 racks | greedy_pair | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.264 |
| taille | 3 robots, 15 racks | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 2.6 [2.1 ; 3.0667] | `descriptif_route.csv` l.265 |
| taille | 3 robots, 15 racks | greedy_pair | drl_route | attente_noeud_par_tache_s | 0.0784 [0.0294 ; 0.1362] | `descriptif_route.csv` l.266 |
| taille | 3 robots, 15 racks | greedy_pair | drl_route | ms_par_decision_route | 0.3674 [0.3344 ; 0.4017] | `descriptif_route.csv` l.268 |
| taille | 3 robots, 15 racks | greedy_pair | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.270 |
| taille | 3 robots, 15 racks | consensus | dijkstra_statique | temps_trajet_moy_s | 13.0887 [12.6636 ; 13.5447] | `descriptif_route.csv` l.273 |
| taille | 3 robots, 15 racks | consensus | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.274 |
| taille | 3 robots, 15 racks | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 5.8667 [4.8667 ; 6.7667] | `descriptif_route.csv` l.275 |
| taille | 3 robots, 15 racks | consensus | dijkstra_statique | attente_noeud_par_tache_s | 0.0049 [0.0 ; 0.0147] | `descriptif_route.csv` l.276 |
| taille | 3 robots, 15 racks | consensus | dijkstra_statique | ms_par_decision_route | 0.0124 [0.011 ; 0.0137] | `descriptif_route.csv` l.278 |
| taille | 3 robots, 15 racks | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.280 |
| taille | 3 robots, 15 racks | consensus | dijkstra_dynamique | temps_trajet_moy_s | 13.0976 [12.6898 ; 13.5427] | `descriptif_route.csv` l.283 |
| taille | 3 robots, 15 racks | consensus | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.284 |
| taille | 3 robots, 15 racks | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 5.4 [4.4667 ; 6.2667] | `descriptif_route.csv` l.285 |
| taille | 3 robots, 15 racks | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0049 [0.0 ; 0.0147] | `descriptif_route.csv` l.286 |
| taille | 3 robots, 15 racks | consensus | dijkstra_dynamique | ms_par_decision_route | 0.0348 [0.0308 ; 0.0386] | `descriptif_route.csv` l.288 |
| taille | 3 robots, 15 racks | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.290 |
| taille | 3 robots, 15 racks | consensus | drl_route | temps_trajet_moy_s | 12.9736 [12.5693 ; 13.4299] | `descriptif_route.csv` l.293 |
| taille | 3 robots, 15 racks | consensus | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.294 |
| taille | 3 robots, 15 racks | consensus | drl_route | conflits_aretes_pour_100_taches | 4.2 [3.2667 ; 5.2] | `descriptif_route.csv` l.295 |
| taille | 3 robots, 15 racks | consensus | drl_route | attente_noeud_par_tache_s | 0.1017 [0.0523 ; 0.1638] | `descriptif_route.csv` l.296 |
| taille | 3 robots, 15 racks | consensus | drl_route | ms_par_decision_route | 0.4868 [0.4462 ; 0.5289] | `descriptif_route.csv` l.298 |
| taille | 3 robots, 15 racks | consensus | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.300 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 16.9561 [16.3043 ; 17.6621] | `descriptif_route.csv` l.303 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.304 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 4.0333 [3.2333 ; 4.9] | `descriptif_route.csv` l.305 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 0.0095 [0.0 ; 0.0285] | `descriptif_route.csv` l.306 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0181 [0.0162 ; 0.0201] | `descriptif_route.csv` l.308 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.310 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 16.908 [16.2816 ; 17.5858] | `descriptif_route.csv` l.313 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.314 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 3.4 [2.7667 ; 4.0667] | `descriptif_route.csv` l.315 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0178 [0.0 ; 0.0535] | `descriptif_route.csv` l.316 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.0662 [0.0576 ; 0.0767] | `descriptif_route.csv` l.318 |
| taille | 6 robots, 40 racks | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.320 |
| taille | 6 robots, 40 racks | greedy_pair | drl_route | temps_trajet_moy_s | 16.9059 [16.3207 ; 17.5127] | `descriptif_route.csv` l.323 |
| taille | 6 robots, 40 racks | greedy_pair | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.324 |
| taille | 6 robots, 40 racks | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 3.6 [2.8667 ; 4.4] | `descriptif_route.csv` l.325 |
| taille | 6 robots, 40 racks | greedy_pair | drl_route | attente_noeud_par_tache_s | 0.0238 [0.001 ; 0.0655] | `descriptif_route.csv` l.326 |
| taille | 6 robots, 40 racks | greedy_pair | drl_route | ms_par_decision_route | 0.6832 [0.6261 ; 0.747] | `descriptif_route.csv` l.328 |
| taille | 6 robots, 40 racks | greedy_pair | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.330 |
| taille | 6 robots, 40 racks | consensus | dijkstra_statique | temps_trajet_moy_s | 17.2205 [16.344 ; 18.0941] | `descriptif_route.csv` l.333 |
| taille | 6 robots, 40 racks | consensus | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.334 |
| taille | 6 robots, 40 racks | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 4.9 [3.7 ; 6.1667] | `descriptif_route.csv` l.335 |
| taille | 6 robots, 40 racks | consensus | dijkstra_statique | attente_noeud_par_tache_s | 0.009 [0.0 ; 0.027] | `descriptif_route.csv` l.336 |
| taille | 6 robots, 40 racks | consensus | dijkstra_statique | ms_par_decision_route | 0.0218 [0.0183 ; 0.0263] | `descriptif_route.csv` l.338 |
| taille | 6 robots, 40 racks | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.340 |
| taille | 6 robots, 40 racks | consensus | dijkstra_dynamique | temps_trajet_moy_s | 17.3652 [16.3892 ; 18.338] | `descriptif_route.csv` l.343 |
| taille | 6 robots, 40 racks | consensus | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.344 |
| taille | 6 robots, 40 racks | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 4.3667 [3.3667 ; 5.4] | `descriptif_route.csv` l.345 |
| taille | 6 robots, 40 racks | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0173 [0.0 ; 0.052] | `descriptif_route.csv` l.346 |
| taille | 6 robots, 40 racks | consensus | dijkstra_dynamique | ms_par_decision_route | 0.0757 [0.0668 ; 0.0858] | `descriptif_route.csv` l.348 |
| taille | 6 robots, 40 racks | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.350 |
| taille | 6 robots, 40 racks | consensus | drl_route | temps_trajet_moy_s | 17.1898 [16.3487 ; 18.0227] | `descriptif_route.csv` l.353 |
| taille | 6 robots, 40 racks | consensus | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.354 |
| taille | 6 robots, 40 racks | consensus | drl_route | conflits_aretes_pour_100_taches | 4.0667 [3.1667 ; 5.0333] | `descriptif_route.csv` l.355 |
| taille | 6 robots, 40 racks | consensus | drl_route | attente_noeud_par_tache_s | 0.0257 [0.0027 ; 0.0647] | `descriptif_route.csv` l.356 |
| taille | 6 robots, 40 racks | consensus | drl_route | ms_par_decision_route | 0.5959 [0.5611 ; 0.6292] | `descriptif_route.csv` l.358 |
| taille | 6 robots, 40 racks | consensus | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.360 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 19.1691 [18.4132 ; 19.9448] | `descriptif_route.csv` l.363 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.364 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 5.6667 [4.7 ; 6.6667] | `descriptif_route.csv` l.365 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 0.0123 [0.0 ; 0.0367] | `descriptif_route.csv` l.366 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0247 [0.0206 ; 0.0318] | `descriptif_route.csv` l.368 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.370 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 19.3014 [18.5128 ; 20.103] | `descriptif_route.csv` l.373 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.374 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 4.9667 [4.0 ; 6.0667] | `descriptif_route.csv` l.375 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0171 [0.0 ; 0.0513] | `descriptif_route.csv` l.376 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.099 [0.0876 ; 0.1107] | `descriptif_route.csv` l.378 |
| taille | 10 robots, 80 racks | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.380 |
| taille | 10 robots, 80 racks | greedy_pair | drl_route | temps_trajet_moy_s | 19.0757 [18.3087 ; 19.8378] | `descriptif_route.csv` l.383 |
| taille | 10 robots, 80 racks | greedy_pair | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.384 |
| taille | 10 robots, 80 racks | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 4.5333 [3.6667 ; 5.5] | `descriptif_route.csv` l.385 |
| taille | 10 robots, 80 racks | greedy_pair | drl_route | attente_noeud_par_tache_s | 0.0213 [0.0003 ; 0.06] | `descriptif_route.csv` l.386 |
| taille | 10 robots, 80 racks | greedy_pair | drl_route | ms_par_decision_route | 0.7185 [0.6564 ; 0.7845] | `descriptif_route.csv` l.388 |
| taille | 10 robots, 80 racks | greedy_pair | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.390 |
| taille | 10 robots, 80 racks | consensus | dijkstra_statique | temps_trajet_moy_s | 19.4483 [18.4318 ; 20.509] | `descriptif_route.csv` l.393 |
| taille | 10 robots, 80 racks | consensus | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.394 |
| taille | 10 robots, 80 racks | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 6.2333 [4.9 ; 7.6333] | `descriptif_route.csv` l.395 |
| taille | 10 robots, 80 racks | consensus | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.396 |
| taille | 10 robots, 80 racks | consensus | dijkstra_statique | ms_par_decision_route | 0.0219 [0.0197 ; 0.0245] | `descriptif_route.csv` l.398 |
| taille | 10 robots, 80 racks | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.400 |
| taille | 10 robots, 80 racks | consensus | dijkstra_dynamique | temps_trajet_moy_s | 19.5016 [18.4614 ; 20.5379] | `descriptif_route.csv` l.403 |
| taille | 10 robots, 80 racks | consensus | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.404 |
| taille | 10 robots, 80 racks | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 5.3333 [4.0 ; 6.7667] | `descriptif_route.csv` l.405 |
| taille | 10 robots, 80 racks | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.406 |
| taille | 10 robots, 80 racks | consensus | dijkstra_dynamique | ms_par_decision_route | 0.094 [0.0851 ; 0.1027] | `descriptif_route.csv` l.408 |
| taille | 10 robots, 80 racks | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.410 |
| taille | 10 robots, 80 racks | consensus | drl_route | temps_trajet_moy_s | 19.4868 [18.4701 ; 20.5267] | `descriptif_route.csv` l.413 |
| taille | 10 robots, 80 racks | consensus | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.414 |
| taille | 10 robots, 80 racks | consensus | drl_route | conflits_aretes_pour_100_taches | 4.4 [3.3667 ; 5.5] | `descriptif_route.csv` l.415 |
| taille | 10 robots, 80 racks | consensus | drl_route | attente_noeud_par_tache_s | 0.0114 [0.0027 ; 0.0227] | `descriptif_route.csv` l.416 |
| taille | 10 robots, 80 racks | consensus | drl_route | ms_par_decision_route | 0.801 [0.7497 ; 0.8502] | `descriptif_route.csv` l.418 |
| taille | 10 robots, 80 racks | consensus | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.420 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 24.0954 [23.1727 ; 25.1402] | `descriptif_route.csv` l.423 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.424 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 17.0 [14.0333 ; 20.2333] | `descriptif_route.csv` l.425 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.426 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0244 [0.0218 ; 0.0271] | `descriptif_route.csv` l.428 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.430 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 23.8343 [22.9521 ; 24.7913] | `descriptif_route.csv` l.433 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.434 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 12.7667 [10.9667 ; 14.6333] | `descriptif_route.csv` l.435 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.436 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.2347 [0.2089 ; 0.2611] | `descriptif_route.csv` l.438 |
| taille | 20 robots, 150 racks | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.440 |
| taille | 20 robots, 150 racks | greedy_pair | drl_route | temps_trajet_moy_s | 23.8663 [23.0605 ; 24.7551] | `descriptif_route.csv` l.443 |
| taille | 20 robots, 150 racks | greedy_pair | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.444 |
| taille | 20 robots, 150 racks | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 12.0333 [10.1 ; 14.1] | `descriptif_route.csv` l.445 |
| taille | 20 robots, 150 racks | greedy_pair | drl_route | attente_noeud_par_tache_s | 0.0227 [0.0093 ; 0.0387] | `descriptif_route.csv` l.446 |
| taille | 20 robots, 150 racks | greedy_pair | drl_route | ms_par_decision_route | 1.4279 [1.2906 ; 1.5845] | `descriptif_route.csv` l.448 |
| taille | 20 robots, 150 racks | greedy_pair | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.450 |
| taille | 20 robots, 150 racks | consensus | dijkstra_statique | temps_trajet_moy_s | 24.2172 [23.1343 ; 25.3875] | `descriptif_route.csv` l.453 |
| taille | 20 robots, 150 racks | consensus | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.454 |
| taille | 20 robots, 150 racks | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 18.4667 [15.4 ; 21.8] | `descriptif_route.csv` l.455 |
| taille | 20 robots, 150 racks | consensus | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.456 |
| taille | 20 robots, 150 racks | consensus | dijkstra_statique | ms_par_decision_route | 0.0344 [0.0315 ; 0.0373] | `descriptif_route.csv` l.458 |
| taille | 20 robots, 150 racks | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.460 |
| taille | 20 robots, 150 racks | consensus | dijkstra_dynamique | temps_trajet_moy_s | 23.8634 [22.8372 ; 25.0888] | `descriptif_route.csv` l.463 |
| taille | 20 robots, 150 racks | consensus | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.464 |
| taille | 20 robots, 150 racks | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 13.7333 [11.4333 ; 16.2333] | `descriptif_route.csv` l.465 |
| taille | 20 robots, 150 racks | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.466 |
| taille | 20 robots, 150 racks | consensus | dijkstra_dynamique | ms_par_decision_route | 0.2051 [0.178 ; 0.2358] | `descriptif_route.csv` l.468 |
| taille | 20 robots, 150 racks | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.470 |
| taille | 20 robots, 150 racks | consensus | drl_route | temps_trajet_moy_s | 23.7086 [22.8081 ; 24.6294] | `descriptif_route.csv` l.473 |
| taille | 20 robots, 150 racks | consensus | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.474 |
| taille | 20 robots, 150 racks | consensus | drl_route | conflits_aretes_pour_100_taches | 12.5 [10.5 ; 14.6] | `descriptif_route.csv` l.475 |
| taille | 20 robots, 150 racks | consensus | drl_route | attente_noeud_par_tache_s | 0.0193 [0.0073 ; 0.034] | `descriptif_route.csv` l.476 |
| taille | 20 robots, 150 racks | consensus | drl_route | ms_par_decision_route | 1.8488 [1.6279 ; 2.0789] | `descriptif_route.csv` l.478 |
| taille | 20 robots, 150 racks | consensus | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.480 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 2.7158 [2.3077 ; 3.1125] | `descriptif_route.csv` l.483 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.484 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 0.5333 [0.2333 ; 0.9] | `descriptif_route.csv` l.485 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.486 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0122 [0.0113 ; 0.0133] | `descriptif_route.csv` l.488 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.490 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 2.7135 [2.3058 ; 3.1108] | `descriptif_route.csv` l.493 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.494 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 0.4667 [0.2 ; 0.8] | `descriptif_route.csv` l.495 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.496 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.0321 [0.0291 ; 0.035] | `descriptif_route.csv` l.498 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.500 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_route | temps_trajet_moy_s | 2.7099 [2.2998 ; 3.1061] | `descriptif_route.csv` l.503 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.504 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 0.3 [0.1 ; 0.5333] | `descriptif_route.csv` l.505 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_route | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.506 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_route | ms_par_decision_route | 0.4957 [0.4352 ; 0.5712] | `descriptif_route.csv` l.508 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.510 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_statique | temps_trajet_moy_s | 2.7635 [2.3283 ; 3.1674] | `descriptif_route.csv` l.513 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.514 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 0.7 [0.4 ; 1.0333] | `descriptif_route.csv` l.515 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.516 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_statique | ms_par_decision_route | 0.0268 [0.0157 ; 0.0468] | `descriptif_route.csv` l.518 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.520 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_dynamique | temps_trajet_moy_s | 2.7611 [2.3258 ; 3.1646] | `descriptif_route.csv` l.523 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.524 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 0.6333 [0.3333 ; 1.0] | `descriptif_route.csv` l.525 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.526 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_dynamique | ms_par_decision_route | 0.0385 [0.0356 ; 0.0413] | `descriptif_route.csv` l.528 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.530 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | drl_route | temps_trajet_moy_s | 2.7582 [2.3254 ; 3.1605] | `descriptif_route.csv` l.533 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.534 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | drl_route | conflits_aretes_pour_100_taches | 0.6 [0.3 ; 0.9667] | `descriptif_route.csv` l.535 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | drl_route | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.536 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | drl_route | ms_par_decision_route | 0.6256 [0.5399 ; 0.7417] | `descriptif_route.csv` l.538 |
| dataset | 15 racks, 3 r., rho=0.7 | consensus | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.540 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 2.7662 [2.329 ; 3.1659] | `descriptif_route.csv` l.543 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.544 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 0.6333 [0.3 ; 1.0333] | `descriptif_route.csv` l.545 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.546 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0158 [0.0142 ; 0.0175] | `descriptif_route.csv` l.548 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.550 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 2.7712 [2.3298 ; 3.1803] | `descriptif_route.csv` l.553 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.554 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 0.4667 [0.2 ; 0.8667] | `descriptif_route.csv` l.555 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.556 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.0392 [0.0363 ; 0.042] | `descriptif_route.csv` l.558 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.560 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_route | temps_trajet_moy_s | 2.7788 [2.3348 ; 3.1888] | `descriptif_route.csv` l.563 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.564 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 0.5333 [0.2667 ; 0.8667] | `descriptif_route.csv` l.565 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_route | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.566 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_route | ms_par_decision_route | 0.466 [0.4343 ; 0.4968] | `descriptif_route.csv` l.568 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.570 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_statique | temps_trajet_moy_s | 2.8795 [2.4183 ; 3.3179] | `descriptif_route.csv` l.573 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.574 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 0.9 [0.5333 ; 1.3] | `descriptif_route.csv` l.575 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.576 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_statique | ms_par_decision_route | 0.0224 [0.0147 ; 0.037] | `descriptif_route.csv` l.578 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.580 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_dynamique | temps_trajet_moy_s | 2.8742 [2.4137 ; 3.3126] | `descriptif_route.csv` l.583 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.584 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 0.7333 [0.4 ; 1.1333] | `descriptif_route.csv` l.585 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.586 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_dynamique | ms_par_decision_route | 0.0331 [0.0284 ; 0.0384] | `descriptif_route.csv` l.588 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.590 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | drl_route | temps_trajet_moy_s | 2.8805 [2.4184 ; 3.3183] | `descriptif_route.csv` l.593 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.594 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | drl_route | conflits_aretes_pour_100_taches | 0.9 [0.5667 ; 1.2333] | `descriptif_route.csv` l.595 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | drl_route | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.596 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | drl_route | ms_par_decision_route | 0.396 [0.3644 ; 0.4264] | `descriptif_route.csv` l.598 |
| dataset | 15 racks, 3 r., rho=0.9 | consensus | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.600 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 5.5092 [4.7628 ; 6.2507] | `descriptif_route.csv` l.603 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.604 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 3.2667 [2.2667 ; 4.4] | `descriptif_route.csv` l.605 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.606 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0179 [0.0159 ; 0.0196] | `descriptif_route.csv` l.608 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.610 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 5.4706 [4.7373 ; 6.2095] | `descriptif_route.csv` l.613 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.614 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 2.2333 [1.5667 ; 3.0667] | `descriptif_route.csv` l.615 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.616 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.064 [0.0551 ; 0.0734] | `descriptif_route.csv` l.618 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.620 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_route | temps_trajet_moy_s | 5.4688 [4.7288 ; 6.2122] | `descriptif_route.csv` l.623 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.624 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 1.8333 [1.2667 ; 2.5] | `descriptif_route.csv` l.625 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_route | attente_noeud_par_tache_s | 0.0087 [0.0 ; 0.0223] | `descriptif_route.csv` l.626 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_route | ms_par_decision_route | 0.6389 [0.6012 ; 0.6758] | `descriptif_route.csv` l.628 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.630 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_statique | temps_trajet_moy_s | 5.6798 [4.8626 ; 6.5167] | `descriptif_route.csv` l.633 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.634 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 3.3333 [2.4 ; 4.3] | `descriptif_route.csv` l.635 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.636 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_statique | ms_par_decision_route | 0.0215 [0.0195 ; 0.0239] | `descriptif_route.csv` l.638 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.640 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_dynamique | temps_trajet_moy_s | 5.6288 [4.8232 ; 6.4625] | `descriptif_route.csv` l.643 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.644 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 2.2667 [1.6667 ; 2.9] | `descriptif_route.csv` l.645 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.646 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_dynamique | ms_par_decision_route | 0.0793 [0.0689 ; 0.0907] | `descriptif_route.csv` l.648 |
| dataset | 40 racks, 6 r., vit. var. | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.650 |
| dataset | 40 racks, 6 r., vit. var. | consensus | drl_route | temps_trajet_moy_s | 5.6138 [4.8395 ; 6.3833] | `descriptif_route.csv` l.653 |
| dataset | 40 racks, 6 r., vit. var. | consensus | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.654 |
| dataset | 40 racks, 6 r., vit. var. | consensus | drl_route | conflits_aretes_pour_100_taches | 1.9667 [1.4333 ; 2.5667] | `descriptif_route.csv` l.655 |
| dataset | 40 racks, 6 r., vit. var. | consensus | drl_route | attente_noeud_par_tache_s | 0.012 [0.003 ; 0.024] | `descriptif_route.csv` l.656 |
| dataset | 40 racks, 6 r., vit. var. | consensus | drl_route | ms_par_decision_route | 0.7199 [0.6532 ; 0.7994] | `descriptif_route.csv` l.658 |
| dataset | 40 racks, 6 r., vit. var. | consensus | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.660 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_statique | temps_trajet_moy_s | 10.1881 [9.0588 ; 11.3933] | `descriptif_route.csv` l.663 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.664 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_statique | conflits_aretes_pour_100_taches | 15.2 [11.8333 ; 18.6333] | `descriptif_route.csv` l.665 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.666 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_statique | ms_par_decision_route | 0.0313 [0.028 ; 0.0351] | `descriptif_route.csv` l.668 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.670 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_dynamique | temps_trajet_moy_s | 9.96 [8.8545 ; 11.1222] | `descriptif_route.csv` l.673 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.674 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_dynamique | conflits_aretes_pour_100_taches | 10.0 [7.9667 ; 11.9667] | `descriptif_route.csv` l.675 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.676 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_dynamique | ms_par_decision_route | 0.2019 [0.1678 ; 0.2386] | `descriptif_route.csv` l.678 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.680 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_route | temps_trajet_moy_s | 9.9077 [8.8021 ; 11.0559] | `descriptif_route.csv` l.683 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.684 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_route | conflits_aretes_pour_100_taches | 7.8333 [5.9667 ; 9.7333] | `descriptif_route.csv` l.685 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_route | attente_noeud_par_tache_s | 0.0157 [0.006 ; 0.0263] | `descriptif_route.csv` l.686 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_route | ms_par_decision_route | 1.1425 [1.0349 ; 1.2461] | `descriptif_route.csv` l.688 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.690 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_statique | temps_trajet_moy_s | 10.1158 [9.0019 ; 11.3198] | `descriptif_route.csv` l.693 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_statique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.694 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_statique | conflits_aretes_pour_100_taches | 15.0333 [11.6333 ; 18.6] | `descriptif_route.csv` l.695 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_statique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.696 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_statique | ms_par_decision_route | 0.0248 [0.0219 ; 0.0278] | `descriptif_route.csv` l.698 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_statique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.700 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_dynamique | temps_trajet_moy_s | 9.9142 [8.8406 ; 11.0644] | `descriptif_route.csv` l.703 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_dynamique | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.704 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_dynamique | conflits_aretes_pour_100_taches | 9.7 [7.6 ; 11.8333] | `descriptif_route.csv` l.705 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_dynamique | attente_noeud_par_tache_s | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.706 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_dynamique | ms_par_decision_route | 0.2025 [0.1741 ; 0.2317] | `descriptif_route.csv` l.708 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | dijkstra_dynamique | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.710 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | drl_route | temps_trajet_moy_s | 9.8361 [8.754 ; 11.0037] | `descriptif_route.csv` l.713 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | drl_route | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.714 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | drl_route | conflits_aretes_pour_100_taches | 7.7667 [5.9 ; 9.6333] | `descriptif_route.csv` l.715 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | drl_route | attente_noeud_par_tache_s | 0.0207 [0.0077 ; 0.037] | `descriptif_route.csv` l.716 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | drl_route | ms_par_decision_route | 1.1528 [1.0421 ; 1.2766] | `descriptif_route.csv` l.718 |
| dataset | 150 racks, 20 r., rho=0.7 | consensus | drl_route | replis_dijkstra | 0.0 [0.0 ; 0.0] | `descriptif_route.csv` l.720 |

### Etape 2

| experience | condition | allocation | methode | metrique | moyenne [IC95] | source |
|---|---|---|---|---|---|---|
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.4 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | rester_sur_place | approche_moy_s | 2.7135 [2.3058 ; 3.1108] | `descriptif_idle.csv` l.7 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.9 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.14 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | retour_au_depot | approche_moy_s | 4.456 [3.805 ; 5.0856] | `descriptif_idle.csv` l.17 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0025 [0.0015 ; 0.0046] | `descriptif_idle.csv` l.19 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.24 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | centre_de_demande | approche_moy_s | 2.8416 [2.3885 ; 3.2678] | `descriptif_idle.csv` l.27 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0822 [0.0721 ; 0.0938] | `descriptif_idle.csv` l.29 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.34 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_idle | approche_moy_s | 2.2262 [1.8691 ; 2.5743] | `descriptif_idle.csv` l.37 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_pair | drl_idle | ms_par_decision_attente | 0.8514 [0.7776 ; 0.9357] | `descriptif_idle.csv` l.39 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.44 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | rester_sur_place | approche_moy_s | 2.7135 [2.3058 ; 3.1108] | `descriptif_idle.csv` l.47 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.49 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.54 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | retour_au_depot | approche_moy_s | 4.456 [3.805 ; 5.0856] | `descriptif_idle.csv` l.57 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0014 [0.0014 ; 0.0015] | `descriptif_idle.csv` l.59 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.64 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | centre_de_demande | approche_moy_s | 2.8416 [2.3885 ; 3.2678] | `descriptif_idle.csv` l.67 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | centre_de_demande | ms_par_decision_attente | 0.0991 [0.0785 ; 0.1233] | `descriptif_idle.csv` l.69 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.74 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | drl_idle | approche_moy_s | 2.2262 [1.8691 ; 2.5743] | `descriptif_idle.csv` l.77 |
| dataset | 15 racks, 3 r., rho=0.7 | greedy_time | drl_idle | ms_par_decision_attente | 0.9638 [0.8398 ; 1.1198] | `descriptif_idle.csv` l.79 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.84 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | rester_sur_place | approche_moy_s | 2.7712 [2.3298 ; 3.1803] | `descriptif_idle.csv` l.87 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.89 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.94 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | retour_au_depot | approche_moy_s | 3.7511 [3.1738 ; 4.2848] | `descriptif_idle.csv` l.97 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0054 [0.0014 ; 0.0119] | `descriptif_idle.csv` l.99 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.104 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | centre_de_demande | approche_moy_s | 2.7662 [2.3247 ; 3.1808] | `descriptif_idle.csv` l.107 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0692 [0.0648 ; 0.0745] | `descriptif_idle.csv` l.109 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.114 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_idle | approche_moy_s | 2.4 [1.9992 ; 2.7797] | `descriptif_idle.csv` l.117 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_pair | drl_idle | ms_par_decision_attente | 0.8177 [0.7363 ; 0.9055] | `descriptif_idle.csv` l.119 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.124 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | rester_sur_place | approche_moy_s | 2.7712 [2.3298 ; 3.1803] | `descriptif_idle.csv` l.127 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.129 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.134 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | retour_au_depot | approche_moy_s | 3.7511 [3.1738 ; 4.2848] | `descriptif_idle.csv` l.137 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0014 [0.0013 ; 0.0014] | `descriptif_idle.csv` l.139 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.144 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | centre_de_demande | approche_moy_s | 2.7662 [2.3247 ; 3.1808] | `descriptif_idle.csv` l.147 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | centre_de_demande | ms_par_decision_attente | 0.0775 [0.0694 ; 0.0873] | `descriptif_idle.csv` l.149 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.154 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | drl_idle | approche_moy_s | 2.4 [1.9992 ; 2.7797] | `descriptif_idle.csv` l.157 |
| dataset | 15 racks, 3 r., rho=0.9 | greedy_time | drl_idle | ms_par_decision_attente | 0.7414 [0.6742 ; 0.8198] | `descriptif_idle.csv` l.159 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.164 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | rester_sur_place | approche_moy_s | 5.4706 [4.7373 ; 6.2095] | `descriptif_idle.csv` l.167 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.169 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.174 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | retour_au_depot | approche_moy_s | 7.9366 [6.8971 ; 8.9503] | `descriptif_idle.csv` l.177 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0013 [0.0013 ; 0.0014] | `descriptif_idle.csv` l.179 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.184 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | centre_de_demande | approche_moy_s | 5.7595 [5.0013 ; 6.5287] | `descriptif_idle.csv` l.187 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0774 [0.0639 ; 0.0955] | `descriptif_idle.csv` l.189 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.194 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_idle | approche_moy_s | 4.5486 [3.8001 ; 5.2511] | `descriptif_idle.csv` l.197 |
| dataset | 40 racks, 6 r., vit. var. | greedy_pair | drl_idle | ms_par_decision_attente | 0.6626 [0.6361 ; 0.6956] | `descriptif_idle.csv` l.199 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.204 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | rester_sur_place | approche_moy_s | 5.3755 [4.6531 ; 6.0991] | `descriptif_idle.csv` l.207 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.209 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.214 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | retour_au_depot | approche_moy_s | 7.3532 [6.3283 ; 8.3502] | `descriptif_idle.csv` l.217 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0012 [0.0011 ; 0.0012] | `descriptif_idle.csv` l.219 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.224 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | centre_de_demande | approche_moy_s | 5.1587 [4.4065 ; 5.8766] | `descriptif_idle.csv` l.227 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | centre_de_demande | ms_par_decision_attente | 0.0572 [0.0545 ; 0.0601] | `descriptif_idle.csv` l.229 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.234 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | drl_idle | approche_moy_s | 4.7386 [3.9958 ; 5.4879] | `descriptif_idle.csv` l.237 |
| dataset | 40 racks, 6 r., vit. var. | greedy_time | drl_idle | ms_par_decision_attente | 0.6275 [0.6129 ; 0.6481] | `descriptif_idle.csv` l.239 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.244 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | rester_sur_place | approche_moy_s | 9.96 [8.8545 ; 11.1222] | `descriptif_idle.csv` l.247 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.249 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.254 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | retour_au_depot | approche_moy_s | 13.2719 [11.7026 ; 14.8647] | `descriptif_idle.csv` l.257 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0011 [0.0011 ; 0.0012] | `descriptif_idle.csv` l.259 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.264 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | centre_de_demande | approche_moy_s | 10.4596 [9.0898 ; 11.7949] | `descriptif_idle.csv` l.267 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.1041 [0.1018 ; 0.1072] | `descriptif_idle.csv` l.269 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.274 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_idle | approche_moy_s | 12.223 [10.7748 ; 13.7255] | `descriptif_idle.csv` l.277 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_pair | drl_idle | ms_par_decision_attente | 0.7643 [0.7531 ; 0.7785] | `descriptif_idle.csv` l.279 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.284 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | rester_sur_place | approche_moy_s | 9.96 [8.8545 ; 11.1222] | `descriptif_idle.csv` l.287 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.289 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.294 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | retour_au_depot | approche_moy_s | 13.2719 [11.7026 ; 14.8647] | `descriptif_idle.csv` l.297 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0011 [0.0011 ; 0.0012] | `descriptif_idle.csv` l.299 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.304 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | centre_de_demande | approche_moy_s | 10.4596 [9.0898 ; 11.7949] | `descriptif_idle.csv` l.307 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | centre_de_demande | ms_par_decision_attente | 0.1081 [0.1034 ; 0.1142] | `descriptif_idle.csv` l.309 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.314 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | drl_idle | approche_moy_s | 12.223 [10.7748 ; 13.7255] | `descriptif_idle.csv` l.317 |
| dataset | 150 racks, 20 r., rho=0.7 | greedy_time | drl_idle | ms_par_decision_attente | 0.7609 [0.7482 ; 0.7757] | `descriptif_idle.csv` l.319 |
| zipf | facile (s=0.5) | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.324 |
| zipf | facile (s=0.5) | greedy_pair | rester_sur_place | approche_moy_s | 15.4834 [14.8239 ; 16.1612] | `descriptif_idle.csv` l.327 |
| zipf | facile (s=0.5) | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.329 |
| zipf | facile (s=0.5) | greedy_pair | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.334 |
| zipf | facile (s=0.5) | greedy_pair | retour_au_depot | approche_moy_s | 24.1115 [23.5671 ; 24.6129] | `descriptif_idle.csv` l.337 |
| zipf | facile (s=0.5) | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.001 [0.001 ; 0.0012] | `descriptif_idle.csv` l.339 |
| zipf | facile (s=0.5) | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.344 |
| zipf | facile (s=0.5) | greedy_pair | centre_de_demande | approche_moy_s | 20.0263 [19.4421 ; 20.6324] | `descriptif_idle.csv` l.347 |
| zipf | facile (s=0.5) | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0506 [0.0499 ; 0.0515] | `descriptif_idle.csv` l.349 |
| zipf | facile (s=0.5) | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.354 |
| zipf | facile (s=0.5) | greedy_pair | drl_idle | approche_moy_s | 15.6653 [14.9456 ; 16.4152] | `descriptif_idle.csv` l.357 |
| zipf | facile (s=0.5) | greedy_pair | drl_idle | ms_par_decision_attente | 0.6006 [0.5914 ; 0.6105] | `descriptif_idle.csv` l.359 |
| zipf | facile (s=0.5) | greedy_time | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.364 |
| zipf | facile (s=0.5) | greedy_time | rester_sur_place | approche_moy_s | 15.3072 [14.724 ; 15.9117] | `descriptif_idle.csv` l.367 |
| zipf | facile (s=0.5) | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.369 |
| zipf | facile (s=0.5) | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.374 |
| zipf | facile (s=0.5) | greedy_time | retour_au_depot | approche_moy_s | 23.3245 [22.9228 ; 23.7418] | `descriptif_idle.csv` l.377 |
| zipf | facile (s=0.5) | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0011 [0.001 ; 0.0012] | `descriptif_idle.csv` l.379 |
| zipf | facile (s=0.5) | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.384 |
| zipf | facile (s=0.5) | greedy_time | centre_de_demande | approche_moy_s | 19.1371 [18.5486 ; 19.7501] | `descriptif_idle.csv` l.387 |
| zipf | facile (s=0.5) | greedy_time | centre_de_demande | ms_par_decision_attente | 0.052 [0.0503 ; 0.0546] | `descriptif_idle.csv` l.389 |
| zipf | facile (s=0.5) | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.394 |
| zipf | facile (s=0.5) | greedy_time | drl_idle | approche_moy_s | 15.4704 [14.6702 ; 16.2297] | `descriptif_idle.csv` l.397 |
| zipf | facile (s=0.5) | greedy_time | drl_idle | ms_par_decision_attente | 0.5929 [0.5867 ; 0.5992] | `descriptif_idle.csv` l.399 |
| zipf | moyen (s=1.0) | greedy_pair | rester_sur_place | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.404 |
| zipf | moyen (s=1.0) | greedy_pair | rester_sur_place | approche_moy_s | 13.8079 [13.052 ; 14.6528] | `descriptif_idle.csv` l.407 |
| zipf | moyen (s=1.0) | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.409 |
| zipf | moyen (s=1.0) | greedy_pair | retour_au_depot | taches_echouees | 0.05 [0.0 ; 0.15] | `descriptif_idle.csv` l.414 |
| zipf | moyen (s=1.0) | greedy_pair | retour_au_depot | approche_moy_s | 21.0134 [20.4319 ; 21.6232] | `descriptif_idle.csv` l.417 |
| zipf | moyen (s=1.0) | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.001 [0.001 ; 0.001] | `descriptif_idle.csv` l.419 |
| zipf | moyen (s=1.0) | greedy_pair | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.424 |
| zipf | moyen (s=1.0) | greedy_pair | centre_de_demande | approche_moy_s | 17.4529 [16.7519 ; 18.1834] | `descriptif_idle.csv` l.427 |
| zipf | moyen (s=1.0) | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.0516 [0.0505 ; 0.0527] | `descriptif_idle.csv` l.429 |
| zipf | moyen (s=1.0) | greedy_pair | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.434 |
| zipf | moyen (s=1.0) | greedy_pair | drl_idle | approche_moy_s | 14.7822 [13.994 ; 15.6963] | `descriptif_idle.csv` l.437 |
| zipf | moyen (s=1.0) | greedy_pair | drl_idle | ms_par_decision_attente | 0.5928 [0.5853 ; 0.6012] | `descriptif_idle.csv` l.439 |
| zipf | moyen (s=1.0) | greedy_time | rester_sur_place | taches_echouees | 0.05 [0.0 ; 0.15] | `descriptif_idle.csv` l.444 |
| zipf | moyen (s=1.0) | greedy_time | rester_sur_place | approche_moy_s | 14.0228 [13.2903 ; 14.9272] | `descriptif_idle.csv` l.447 |
| zipf | moyen (s=1.0) | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.449 |
| zipf | moyen (s=1.0) | greedy_time | retour_au_depot | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.454 |
| zipf | moyen (s=1.0) | greedy_time | retour_au_depot | approche_moy_s | 19.7096 [19.1089 ; 20.2775] | `descriptif_idle.csv` l.457 |
| zipf | moyen (s=1.0) | greedy_time | retour_au_depot | ms_par_decision_attente | 0.001 [0.001 ; 0.0011] | `descriptif_idle.csv` l.459 |
| zipf | moyen (s=1.0) | greedy_time | centre_de_demande | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.464 |
| zipf | moyen (s=1.0) | greedy_time | centre_de_demande | approche_moy_s | 16.2213 [15.5069 ; 16.9671] | `descriptif_idle.csv` l.467 |
| zipf | moyen (s=1.0) | greedy_time | centre_de_demande | ms_par_decision_attente | 0.0536 [0.051 ; 0.0575] | `descriptif_idle.csv` l.469 |
| zipf | moyen (s=1.0) | greedy_time | drl_idle | taches_echouees | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.474 |
| zipf | moyen (s=1.0) | greedy_time | drl_idle | approche_moy_s | 14.397 [13.5883 ; 15.2828] | `descriptif_idle.csv` l.477 |
| zipf | moyen (s=1.0) | greedy_time | drl_idle | ms_par_decision_attente | 0.5985 [0.592 ; 0.6061] | `descriptif_idle.csv` l.479 |
| zipf | difficile (s=1.5) | greedy_pair | rester_sur_place | taches_echouees | 0.05 [0.0 ; 0.15] | `descriptif_idle.csv` l.484 |
| zipf | difficile (s=1.5) | greedy_pair | rester_sur_place | approche_moy_s | 8.8909 [8.1285 ; 9.7867] | `descriptif_idle.csv` l.487 |
| zipf | difficile (s=1.5) | greedy_pair | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.489 |
| zipf | difficile (s=1.5) | greedy_pair | retour_au_depot | taches_echouees | 0.05 [0.0 ; 0.15] | `descriptif_idle.csv` l.494 |
| zipf | difficile (s=1.5) | greedy_pair | retour_au_depot | approche_moy_s | 14.1801 [13.4851 ; 14.8443] | `descriptif_idle.csv` l.497 |
| zipf | difficile (s=1.5) | greedy_pair | retour_au_depot | ms_par_decision_attente | 0.0011 [0.0011 ; 0.0011] | `descriptif_idle.csv` l.499 |
| zipf | difficile (s=1.5) | greedy_pair | centre_de_demande | taches_echouees | 0.05 [0.0 ; 0.15] | `descriptif_idle.csv` l.504 |
| zipf | difficile (s=1.5) | greedy_pair | centre_de_demande | approche_moy_s | 11.9019 [11.0939 ; 12.7897] | `descriptif_idle.csv` l.507 |
| zipf | difficile (s=1.5) | greedy_pair | centre_de_demande | ms_par_decision_attente | 0.057 [0.0556 ; 0.0584] | `descriptif_idle.csv` l.509 |
| zipf | difficile (s=1.5) | greedy_pair | drl_idle | taches_echouees | 0.05 [0.0 ; 0.15] | `descriptif_idle.csv` l.514 |
| zipf | difficile (s=1.5) | greedy_pair | drl_idle | approche_moy_s | 10.0991 [9.51 ; 10.7644] | `descriptif_idle.csv` l.517 |
| zipf | difficile (s=1.5) | greedy_pair | drl_idle | ms_par_decision_attente | 0.6124 [0.6003 ; 0.6258] | `descriptif_idle.csv` l.519 |
| zipf | difficile (s=1.5) | greedy_time | rester_sur_place | taches_echouees | 0.05 [0.0 ; 0.15] | `descriptif_idle.csv` l.524 |
| zipf | difficile (s=1.5) | greedy_time | rester_sur_place | approche_moy_s | 8.3792 [7.6864 ; 9.1871] | `descriptif_idle.csv` l.527 |
| zipf | difficile (s=1.5) | greedy_time | rester_sur_place | ms_par_decision_attente | 0.0 [0.0 ; 0.0] | `descriptif_idle.csv` l.529 |
| zipf | difficile (s=1.5) | greedy_time | retour_au_depot | taches_echouees | 0.05 [0.0 ; 0.15] | `descriptif_idle.csv` l.534 |
| zipf | difficile (s=1.5) | greedy_time | retour_au_depot | approche_moy_s | 13.0164 [12.38 ; 13.6307] | `descriptif_idle.csv` l.537 |
| zipf | difficile (s=1.5) | greedy_time | retour_au_depot | ms_par_decision_attente | 0.0011 [0.0011 ; 0.0011] | `descriptif_idle.csv` l.539 |
| zipf | difficile (s=1.5) | greedy_time | centre_de_demande | taches_echouees | 0.05 [0.0 ; 0.15] | `descriptif_idle.csv` l.544 |
| zipf | difficile (s=1.5) | greedy_time | centre_de_demande | approche_moy_s | 10.6381 [9.8279 ; 11.54] | `descriptif_idle.csv` l.547 |
| zipf | difficile (s=1.5) | greedy_time | centre_de_demande | ms_par_decision_attente | 0.0567 [0.0553 ; 0.0582] | `descriptif_idle.csv` l.549 |
| zipf | difficile (s=1.5) | greedy_time | drl_idle | taches_echouees | 0.05 [0.0 ; 0.15] | `descriptif_idle.csv` l.554 |
| zipf | difficile (s=1.5) | greedy_time | drl_idle | approche_moy_s | 9.3177 [8.4992 ; 10.2588] | `descriptif_idle.csv` l.557 |
| zipf | difficile (s=1.5) | greedy_time | drl_idle | ms_par_decision_attente | 0.5504 [0.5083 ; 0.5875] | `descriptif_idle.csv` l.559 |

