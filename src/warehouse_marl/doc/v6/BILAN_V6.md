# Bilan v6 : victoires, égalités, défaites et déviations

Branche `drl-v6`. Protocole : `PROTOCOLE_V6.md`, commité avant tout entraînement
(commit 28af50b), avec 7 écarts datés, tous décidés **avant** les essais de test
de la phase concernée. Les graines de test sont nouvelles : 2 000 003 + 1 013 k,
k = 0 … 19. Chaque modèle retenu a été évalué **une seule fois**. Le test est un
Wilcoxon apparié bilatéral, avec une correction de Holm par famille. Une
**victoire** demande p de Holm < 0,05 et un écart moyen < 0. Chaque chiffre
ci-dessous est repris, avec son fichier et sa ligne, dans `VALEURS_V6.md`.

## En bref

| Phase | Tests | Victoires | Égalités | Défaites | (condition, allocation) gagnées |
|---|---|---|---|---|---|
| A, `drl_idle6` (attente) | 28 | 9 | 17 | 2 | **2 / 14** (règle des 2 tests, écart 2) |
| B, `drl_route6` (routage avec congestion) | 12 | 1 | 11 | 0 | **0 / 4** (règle des 3 tests) |
| C, `drl_alloc6` (allocation avec anticipation) | 0 | – | – | – | **apprentissage échoué, non testé** |

## Objectifs de la mission v6 : atteints ou non

| Objectif | Résultat |
|---|---|
| A : la défaite v4 à 150 racks (+10,7 %) devient une égalité ou une victoire | **atteint** : victoire −16,1 % contre les heuristiques v4 ; égalité contre la couverture |
| A : garder les 5 victoires v4 | **atteint** contre les heuristiques v4. Seulement 2 sur 5 si l'on exige aussi de battre la couverture |
| A : ne pas créer de nouvelle défaite | **non atteint** : 2 défaites à Zipf facile, contre `rester_sur_place` |
| B : victoire significative contre les 3 Dijkstra dans une condition chargée | **non atteint** : au mieux B4, victoire contre `dijkstra_statique` seulement |
| C : victoire contre `greedy_pair` / `greedy_time` | **non atteint** : apprentissage échoué, non testé |

## Phase A : point d'attente, 1 680 essais

**Ce qui est atteint.** La défaite v4 à 150 racks / 20 robots disparaît.
- `drl_idle6` fait **56,82 s** contre 67,68 s pour la meilleure des 3 heuristiques
  v4 (`centre_de_demande`), soit **−10,86 s (−16,1 %)**, gagné sur 19 essais sur
  20 (`principal_idle6.csv` l.14 et 16).
- Sur les mêmes graines, l'ancien `drl_idle` v4 fait 75,22 s
  (`secondaire_idle6.csv` l.64).

**Les 5 victoires v4 contre les heuristiques v4 sont conservées :**
- 15 racks, ρ = 0,7, ×2 : −1,67 s ;
- 15 racks, ρ = 0,9, ×2 : −1,61 s ;
- 40 racks, `greedy_pair` : −4,81 s, −9,7 %.

**Contre la couverture** (concurrent ajouté par l'écart 2) :
- **une seule victoire** : à 15 racks, ρ = 0,7, −1,18 s, sur les 2 allocations
  (l.3 et 5). Ce sont les **2 (condition, allocation) gagnées** au sens strict ;
- partout ailleurs, c'est une égalité. L'essentiel du gain à 40 et 150 racks
  vient donc du **terme a priori de couverture**, pas de l'apprentissage. À
  150 racks, par exemple, il ne reste que −0,66 s contre la couverture, non
  significatif.

**Défaites :** Zipf facile (s = 0,5), contre `rester_sur_place`, +2,33 s et
+1,86 s, sur les 2 allocations (l.18 et 20). La v4 y faisait égalité. Le modèle
petit, entraîné sur la demande Footwear, généralise mal à une demande presque
uniforme. Zipf moyen et Zipf difficile donnent des égalités.

**Échecs :** le DRL n'a jamais plus de tâches échouées que son concurrent. À Zipf
difficile avec `greedy_time`, il en a 2, contre 2.

## Phase B : routage avec capacité de 1 robot par segment, 320 essais

- **Aucune condition n'est gagnée contre les trois Dijkstra.**
- La seule victoire est en **B4** (20 r., 150 racks, vagues réelles) contre
  `dijkstra_statique` : −0,67 s, 17 essais gagnés sur 20, p de Holm 0,010
  (`principal_route6.csv` l.11).
- Dans la même condition, le DRL est plus rapide que `dijkstra_dynamique`
  (−0,29 s, 16/20) et que `dijkstra_congestion` (−0,27 s, 16/20), mais ce n'est
  pas significatif après Holm (0,12 et 0,063).
- Les 11 autres tests sont des égalités (−0,57 à +0,02 s), sans aucun échec.

Cela correspond au plafond annoncé dans le protocole (§0) : l'attente en file
ne dépasse pas 2 s par tâche. Le modèle retenu (graine 2, t = 30 min) est
à −0,000 % en validation, donc au niveau de la meilleure Dijkstra.

## Phase C : allocation avec anticipation

**Apprentissage échoué, non testé** (écart 8). Aucun essai de test C n'a été
lancé, et la famille C n'est pas calculée.

- **Validations de la graine 0,** après la correction de la récompense (écart 7),
  en écart relatif à la meilleure de `greedy_pair` et `greedy_time`
  (`VALEURS_V6.md` §4, `lancements_interrompus/alloc6_interrompu_2104/val_log_seed0.csv`
  l.2 à 6) :

  | Instant | Écart relatif |
  |---|---|
  | t = 0 (`greedy_pair` seul) | +0,11 % |
  | t = 10 min | +167,8 % |
  | t = 20 min | +289,5 % |
  | t = 30 min | +182,6 % |
  | t = 40 min | +219,7 % |

  L'entraînement a été arrêté à 21 h 04, à la demande de l'utilisatrice, vers
  t ≈ 42 min sur 45. Les graines 1 et 2 n'ont pas été lancées.
- **Diagnostic,** sur une graine d'exploration, 60 tâches train_fit : la
  politique choisit « attendre un pas » **361 fois** pour 60 attributions. Elle
  fait 48,7 s de temps de traitement moyen, contre 21,9 s pour `greedy_pair` :
  - attente avant attribution : 28,9 s contre 7,9 s ;
  - approche : 9,7 s contre 4,0 s.
- **Cause.** Une attente mène à un état presque identique et ne coûte qu'un pas
  très court. Sa valeur Q vaut donc presque celle de la meilleure attribution, et
  la moindre erreur d'approximation du DQN la fait choisir. Il faudrait une autre
  formulation (semi-MDP, coût minimal de l'attente ou valeur d'avantage), qui
  n'est pas faite en v6.
- **Conséquence.** Le constat v4 pour l'allocation apprise (0 victoire sur 22
  contre `greedy_pair`) n'est pas amélioré.

## Déviations du protocole (détail dans `PROTOCOLE_V6.md`, section « Écarts »)

1. Précisions d'implémentation de la phase C, données avant tout entraînement.
2. **La couverture devient un concurrent de A** (demande de l'utilisatrice), ce
   qui porte la famille A à 28 tests. La référence de validation passe à 4
   heuristiques.
3. **Arrêt de l'entraînement A.** Il se dégradait à 20 robots en validation
   (+13 %). On le remplace par deux modèles, **petit** (15 et 40 racks) et
   **grand** (150 racks), et on revoit les budgets : 40 et 60 min pour A, 60 min
   pour B, 45 min pour C.
4. **A grand :** les décisions d'attente sans tâche recevaient une récompense
   nulle « gratuite ». Elles sont désormais tronquées. Le modèle petit, déjà
   sélectionné, n'a pas été réentraîné : c'est une limite.
5. **A grand :** passage à une **récompense d'équipe** (choix de l'utilisatrice).
   La récompense individuelle poussait à faire moins de tâches.
6. **B :** deux échappatoires de la récompense de `drl_route6`, reprises de la
   v4, sont fermées. Un échec ne coûtait rien de plus, et un repli sur Dijkstra
   rendait gratuit le reste du trajet.
7. **C :** la récompense devient « au fil de l'eau », avec γ = 0,99 et au plus 10
   attentes consécutives. Avant, l'attente était toujours « moins chère ».
8. **C : arrêt de l'entraînement et pas de test** (demande de l'utilisatrice).
   Résultat rapporté : apprentissage échoué, non testé.

**Lancements interrompus,** jamais utilisés pour la sélection ni pour le test
(journaux dans `lancements_interrompus/`) :
- A, modèle unique : 09 h 51 ;
- A grand : 12 h 05 et 13 h 24 ;
- B : 16 h 50 ;
- C : 20 h 22 (après l'écart 6) et 21 h 04 (après l'écart 7, écart 8).

Une coupure de courant vers 14 h 40 a fait passer le portable sur batterie, sans
interrompre l'entraînement. Le secteur est revenu à 14 h 53.

## Limites

- Les modèles petit et grand de `drl_idle6` n'ont pas la même règle de
  récompense (écarts 4 et 5).
- Dans 3 des 4 conditions dataset, `greedy_time` et `greedy_pair` donnent les
  mêmes essais. Les 14 (condition, allocation) de A ne recouvrent donc que 11
  comparaisons distinctes (comme en v4).
- La validation est bruitée (environ 1 % d'un point à l'autre). Le gain de
  validation du modèle retenu est donc probablement optimiste.
- Tout est mesuré dans le banc hors ligne. Rien n'est mesuré dans Gazebo ni dans
  ROS 2.
