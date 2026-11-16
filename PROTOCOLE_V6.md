# Protocole expérimental v6 : faire gagner le DRL, honnêtement

Branche `drl-v6` (issue de `drl-v4`, commit 00b93d2). Rédigé le 16/11/2026, **avant
tout entraînement v6 et avant tout essai sur les graines de test v6**. Ce fichier est
commité avant le premier entraînement. Il n'est plus modifié ensuite, sauf la
section finale « Écarts », datée, qui consigne tout changement et sa raison.

## 0. Point de départ et explorations préalables (déclarées)

Résultats v4 (graines de test 1000 k + 7) :
- `drl_idle` gagne 5 tests sur 14, mais perd à 150 racks / 20 robots (+6,54 s, +10,7 %).
- `drl_route` : 0 victoire sur 24 contre Dijkstra.
- Allocation `drl3` : 0 victoire sur 22 contre `greedy_pair`.

**Constat sur le code v4, avant toute expérience v6 :** l'entraînement v4 de
`drl_idle` voyait déjà la configuration 150 racks / 20 robots (1 épisode sur 4).
La défaite à grande échelle ne vient donc pas seulement de la taille des entrepôts
d'entraînement. Trois causes probables :
- des entrées dépendantes de la taille (distances divisées par 60 s × vitesse,
  comptes bruts de robots, `taille_flotte` = R / 20) ;
- des candidats tous proches du centre de demande, ce qui empêche les 20 robots de
  se répartir ;
- une sélection sur la moyenne **absolue** des scénarios de validation.

**Explorations faites avant ce protocole.** Elles utilisent uniquement des fenêtres
**train_fit** et des graines d'exploration (900 000 000 + i), jamais les graines de
validation ni de test, v4 ou v6. Elles ont servi à concevoir les méthodes, pas à les
régler sur la validation.
- **Phase A.** 8 fenêtres, `greedy_pair`, à 150 racks / 20 robots :
  - `rester_sur_place` : 87,8 s ;
  - `centre_de_demande` : 90,9 s ;
  - `drl_idle` v4 : 95,0 s ;
  - heuristique de **couverture** (définie en 3.1) : **78,4 s**.

  Aux petites tailles, la couverture est proche de `rester_sur_place`, et `drl_idle`
  v4 reste le meilleur.
- **Phase B.** 5 graines par condition, capacité de 1 robot par segment. L'attente
  en file reste faible : de 0,1 à 2,0 s par tâche, pour des temps de traitement de
  20 à 94 s. Les trois Dijkstra sont à moins de 1 s les unes des autres, sauf à
  10 r. / 80 racks, ρ = 0,9 (33,8 contre 35,4 s). **Le gain possible d'un
  routage appris est donc plafonné, en ordre de grandeur, par ce temps d'attente**
  (≤ 2 s par tâche). Une défaite ou une égalité en phase B est un résultat attendu
  et sera rapportée comme telle.

## 1. Hypothèses

- **HA (phase A, attente).** `drl_idle6` réduit le temps de traitement moyen par
  rapport à la **meilleure** des trois heuristiques d'attente (`rester_sur_place`,
  `retour_au_depot`, `centre_de_demande`) dans les conditions des 14 tests v4. En
  particulier, la défaite v4 à 150 racks / 20 robots devient une égalité ou une
  victoire, et les 5 victoires v4 sont conservées.
- **HB (phase B, routage avec congestion).** Avec une capacité de 1 robot par
  segment d'allée, `drl_route6` réduit le temps de traitement moyen par rapport à
  **chacune** des trois Dijkstra, dans au moins une condition chargée.
- **HC (phase C, allocation avec anticipation, si le temps le permet).**
  `drl_alloc6` réduit le temps de traitement moyen par rapport à la meilleure des
  deux allocations `greedy_pair` et `greedy_time`, sur les vagues réelles de test.
- Hypothèse nulle de chaque test : la distribution des différences appariées
  (DRL − concurrent) est symétrique autour de 0. Test **bilatéral**.

## 2. Métriques

Elles sont calculées par essai (une graine = un essai de 150 tâches). Les
définitions sont celles du banc v4.

| Métrique | Rôle |
|---|---|
| `temps_traitement_moy_s` : moyenne de (fin − création) sur les tâches terminées | **principale** (HA, HB, HC) |
| `taches_echouees` | garde-fou : signalé si le DRL en a plus que le concurrent |
| `approche_moy_s` (A), `temps_trajet_moy_s` et `attente_file_par_tache_s` (B), `attente_attribution_moy_s` (C) | secondaires, descriptives |
| `ms_par_decision_*` | descriptif |

## 3. Méthodes

Les trois DRL v6 sont des DQN **résiduels**, comme en v4 : Q = terme a priori +
f_θ(x), avec la dernière couche de f_θ initialisée à zéro. Un modèle non entraîné
reproduit donc **exactement** son heuristique de départ (vérifié par
`test/test_v6.py`). Ils utilisent tous :
- Double DQN, perte de Huber, cible douce (τ = 0,005) ;
- un réseau 64-64, Adam (lr = 3·10⁻⁴), un lot de 64 ;
- une mémoire de rejeu de 100 000 transitions, 1 000 transitions avant la première
  mise à jour, un gradient borné à 5 ;
- un ε-glouton qui passe de 0,3 à 0,02 sur 60 % du budget.

Ces réglages sont ceux de la v4 et ne sont pas réglés davantage.

### 3.1 Phase A : `drl_idle6`

- **Décision.** Elle a lieu, comme en v4, quand un robot devient inoccupé. Le robot
  choisit un point d'attente parmi K = 6 candidats :
  - sa position ;
  - `charging_dock` ;
  - le centre de demande ;
  - le choix de la **couverture** ;
  - puis les meilleurs nœuds dans l'ordre de cov croissant, jusqu'à 6.
- **Couverture.** cov(c) = E_p[ min( d(c, rack), min_o d(o, rack) ) ], où o
  parcourt les points d'attente des **autres** robots inoccupés. L'heuristique
  `couverture` va au nœud de cov minimale, ou reste sur place si sa position fait
  aussi bien. La demande p est la même qu'en v4 :
  - fréquences train_fit pour les vagues ;
  - fréquences observées en ligne, avec un lissage de Laplace, pour Zipf.
- **Terme a priori :** −cov(c) / diamètre (+10⁻³ pour le choix de la couverture).
  Avec f_θ = 0, la politique est donc `couverture`. **`couverture` n'est pas un des
  trois concurrents** ; elle est rapportée à titre descriptif, avec un test
  secondaire DRL contre couverture, pour séparer l'apport de l'apprentissage de
  celui du terme a priori.
- **Entrées indépendantes de la taille (20).** Toutes les distances sont divisées
  par le **diamètre du graphe**. Les entrées sont :
  - E_p[d(c, ·)] et l'écart au centre ;
  - le gain de cov par rapport à rester sur place, et l'écart au meilleur cov ;
  - la distance du robot au candidat ;
  - les inoccupés au candidat (/ R) ;
  - la distance au plus proche autre inoccupé ;
  - la **demande locale en fraction** (masse de p dans un rayon de 0,15 ×
    diamètre) et son rapport à l'uniforme ;
  - les inoccupés et les robots occupés dont la cible est dans ce rayon (/ R) ;
  - 4 indicateurs : position, dépôt, centre, couverture ;
  - la part de robots libres ;
  - les tâches ouvertes / R ;
  - la vitesse relative ;
  - le **ratio robots / racks** (× 5).
- **Récompense :** −(temps d'approche de la tâche suivante du robot) /
  (diamètre / vitesse moyenne), ce qui la rend indépendante de la taille ; γ = 0,9.
- **Entraînement (curriculum mélangé).** À chaque épisode, une des 4 configurations
  dataset est tirée au hasard :
  - 15 racks / 3 robots à ρ = 0,7 ;
  - 15 racks / 3 robots à ρ = 0,9 ;
  - 40 racks / 6 robots à vitesses variables ;
  - 150 racks / 20 robots à ρ = 0,7.

  L'allocation (`greedy_pair` ou `greedy_time`) est aussi tirée au hasard. Chaque
  épisode prend une fenêtre de 100 tâches de **train_fit**. Zipf n'est pas vue
  (test de généralisation, comme en v4).

### 3.2 Phase B : banc de routage avec congestion, `drl_route6`

- **Banc.** Un segment d'allée (une arête, les deux sens confondus) accueille
  **au plus 1 robot**. Un robot qui veut entrer dans un segment occupé attend au
  nœud, dans une **file FIFO** propre au segment. Les nœuds n'ont pas de capacité,
  donc il n'y a pas d'interblocage. L'attente en file ne compte pas pour l'échec à
  90 s, qui ne concerne que l'absence de chemin. Les robots inoccupés qui se
  déplacent respectent aussi la capacité. Il n'y a pas de blocage d'arête.
- **Concurrents :**
  - `dijkstra_statique` : route sur les longueurs, calculée au départ et suivie
    (définition v4) ;
  - `dijkstra_dynamique` : replanification à chaque nœud, coût longueur +
    2 × congestion (définition v4) ;
  - `dijkstra_congestion` : replanification à **chaque pas de temps** passé à un
    nœud. Le coût d'une arête vaut longueur + v × (temps restant de l'occupant) +
    longueur × (robots en file devant soi), soit l'**occupation actuelle**.
- **`drl_route6`.** Q(u→v) = −(c(u,v) + d_cong(v, but)) / (60 s × v) + f_θ.
  Avec f_θ = 0, c'est exactement `dijkstra_congestion`. Une action « attendre »
  est aussi possible, comme en v4. Les 22 entrées comprennent :
  - l'**occupation du segment** (occupé, temps restant, sens) et la file devant
    soi ;
  - l'**occupation et les files des 3 segments suivants** du chemin prévu ;
  - les **réservations des autres robots**, c'est-à-dire leurs 4 prochains segments
    prévus, avec leurs heures d'arrivée estimées. On compte celles qui recouvrent
    notre propre fenêtre de passage, sur le segment (au total et en sens inverse)
    et sur les 3 segments suivants ;
  - les distances au but (congestion, longueurs) ;
  - les robots au voisin et en route vers lui ;
  - le demi-tour, l'attente, le choix de l'heuristique ;
  - la densité de robots, l'attente en file cumulée, la vitesse.

  La récompense vaut −durée de l'étape / 60, avec γ = 1 (comme en v4). Un garde-fou
  bascule sur `dijkstra_congestion` au-delà de 3|V| déplacements ou de 20|V|
  décisions pour une tâche ; le nombre de replis est rapporté.
- **Entraînement.**
  - Flottes : 10 r. / 80 racks, 20 r. / 80 racks ou 20 r. / 150 racks.
  - Charge : ρ ∈ {0,7 ; 0,9}.
  - Tâches : uniformes, ou fenêtres train_fit (une chance sur deux).
  - Allocation `greedy_pair`, 100 tâches par épisode.

### 3.3 Phase C : `drl_alloc6` (seulement si A et B sont finies)

- **Décision.** Les candidats sont les couples (robot libre, tâche parmi les 5 plus
  anciennes), comme `greedy_pair`, plus **une action « attendre un pas » par robot
  libre** : le robot n'est pas attribué pendant 1 s et garde sa place pour une
  tâche attendue.
- **Terme a priori :** −coût / diamètre pour un couple. Pour l'attente :
  −(meilleur coût du robot + 0,05 × diamètre) / diamètre. Avec f_θ = 0, c'est donc
  exactement `greedy_pair`.
- **Entrées.** Celles du v3 (`features_v3`), plus une **prévision de la demande
  par zone**. La zone est le rayon de 0,15 × diamètre autour d'un nœud. La
  prévision vient des fréquences de la partie **entraînement** du découpage
  chronologique 70/30 (train_fit), avec :
  - la masse prévue près du robot et près de la cible ;
  - le temps prévu avant la prochaine arrivée dans la zone du robot ;
  - un indicateur d'attente.
- **Récompense.** −(temps de service mesuré de la tâche attribuée + attente
  cumulée des tâches en file jusqu'à la décision suivante) / 60, comme en v3.
- Les détails d'implémentation qui ne sont pas écrits ici seront consignés dans
  « Écarts » **avant** l'entraînement C.

## 4. Graines et séparation

| Usage | Graines de simulation | Tâches (Footwear) |
|---|---|---|
| Entraînement | tirées dans [10⁷ ; 10⁹), **refusées** (assertion) si elles tombent dans un ensemble de validation ou de test v4 ou v6 | fenêtres **train_fit** |
| Validation v6 (sélection) | 3 000 017 + 1 019 × i | **train_val** (fenêtres régulières) |
| **Test v6** | **2 000 003 + 1 013 × k, k = 0 … 19** : 20 graines **nouvelles**, jamais utilisées (ni en v4 ni dans les explorations) | **test** : **milieu** du k-ième de 20 intervalles réguliers, soit des fenêtres différentes de celles de la v4 |

- Le découpage chronologique de Footwear est celui de `dataset_footwear.py` :
  70 % train (dont 85 % train_fit et 15 % train_val), 30 % test.
- Toutes les méthodes d'une même condition voient, pour une graine donnée, les
  mêmes arrivées, les mêmes cibles et les mêmes blocages. Les essais sont donc
  **appariés**.

**Validation.**
- **A :** les 4 configurations dataset, 24 scénarios :
  - 6 fenêtres avec `greedy_pair` pour les configurations à vitesse égale (où
    `greedy_time` donne les mêmes essais) ;
  - 3 fenêtres × 2 allocations pour la configuration à vitesses variables.
- **B :** les 4 conditions de test (§6.2) × 3 graines de validation, soit
  12 scénarios.
- **C :** les 4 configurations dataset × 3 fenêtres train_val.

## 5. Budget, entraînement et sélection

- **Au plus 3 graines d'entraînement (0, 1, 2) par expérience**, au plus 2 h par
  graine. Budgets retenus :
  - phase A : 90 min par graine ;
  - phase B : 90 min par graine ;
  - phase C : 60 min par graine.
- **Un seul entraînement à la fois** : les graines tournent l'une après l'autre,
  dans un processus détaché (`setsid nohup`), avec `torch.set_num_threads(2)`.
- **Sauvegarde complète toutes les 10 minutes**, en même temps que la validation.
  Elle contient :
  - les réseaux et l'état d'Adam ;
  - la mémoire de rejeu ;
  - les générateurs aléatoires ;
  - l'épisode et le temps consommé.

  Une relance de la même commande **reprend** là où la sauvegarde s'est arrêtée.
  Le temps perdu entre la sauvegarde et le crash n'est pas compté dans le budget.
  Toute reprise est consignée dans « Écarts ».
- **Validation à l'instant 0** (f_θ = 0, l'heuristique de départ) puis toutes les
  10 minutes.
- **Critère de sélection, sur la validation uniquement.** On retient le point de
  contrôle (graine, instant) qui minimise l'**écart relatif moyen**. Pour chaque
  scénario de validation, l'écart relatif vaut (temps DRL − temps de la meilleure
  des heuristiques concurrentes sur ce scénario) / ce temps ; on en fait la moyenne
  sur les scénarios.
  - Ce critère remplace la moyenne absolue de la v4, pour que les grands entrepôts
    ne dominent pas le choix.
  - En cas d'égalité, on prend l'instant le plus précoce, puis la graine la plus
    petite.
  - L'instant 0 fait partie des candidats. S'il est retenu, le DRL testé est
    l'heuristique de départ, et on le rapporte tel quel.
- Seul le modèle retenu est évalué sur le test, **une seule fois**.

## 6. Expériences de test (graines de test v6)

### 6.1 Phase A

Les 14 tests de la v4 : 7 conditions × 2 allocations (`greedy_pair`,
`greedy_time`), avec routage `dijkstra_dynamique` et sans capacité de segment.
- **dataset**, vagues de test : 15 racks / 3 r. à ρ = 0,7 ; 15 / 3 à ρ = 0,9 ;
  40 / 6 à vitesses variables ; 150 / 20 à ρ = 0,7.
- **zipf** : les 3 niveaux `structured` (facile, moyen, difficile).

Méthodes :
- les 3 concurrents : `rester_sur_place`, `retour_au_depot`, `centre_de_demande` ;
- `drl_idle6` ;
- à titre descriptif : `couverture` (f_θ = 0) et `drl_idle` v4 (modèle
  `models/selected_idle.pt`).

Cela fait 7 × 2 × 6 × 20 = **1 680 essais**.

### 6.2 Phase B

Allocation `greedy_pair`, capacité de 1 robot par segment, sans blocage. Méthodes :
`dijkstra_statique`, `dijkstra_dynamique`, `dijkstra_congestion`, `drl_route6`.

| Condition | Robots / racks | ρ | Tâches |
|---|---|---|---|
| B1 | 10 / 80 | 0,9 | uniformes |
| B2 | 20 / 80 | 0,9 | uniformes |
| B3 | 20 / 150 | 0,9 | uniformes |
| B4 | 20 / 150 | 0,7 | vagues de test Footwear |

Cela fait 4 × 4 × 20 = **320 essais**.

### 6.3 Phase C (si exécutée)

Les 4 conditions dataset (vagues de test), sans capacité de segment. Méthodes :
`greedy_pair`, `greedy_time`, `drl_alloc6`. Cela fait 4 × 3 × 20 = **240 essais**.

## 7. Analyse statistique et critère de victoire

- **Test :** Wilcoxon des rangs signés, apparié, bilatéral
  (`scipy.stats.wilcoxon`, options par défaut), sur les 20 essais appariés.
- **Correction de Holm**, α = 0,05, dans chaque famille principale :
  - **Famille A** (14 tests) : `drl_idle6` contre la meilleure des 3 heuristiques
    de la même (condition, allocation). La meilleure est choisie sur la moyenne de
    test, comme en v4, ce qui avantage l'heuristique.
  - **Famille B** (12 tests) : `drl_route6` contre **chacun** des 3 concurrents,
    dans chacune des 4 conditions.
  - **Famille C** (4 tests) : `drl_alloc6` contre la meilleure de `greedy_pair` et
    `greedy_time`.
- **Victoire** (définie avant tout essai) : p ajustée par Holm < 0,05 **et** écart
  moyen (DRL − concurrent) < 0.
  - Si p ajustée < 0,05 avec un écart > 0, c'est une **défaite**.
  - Sinon, c'est une **égalité** (pas de différence significative).
  - Une victoire obtenue avec plus de tâches échouées que le concurrent est
    signalée « victoire avec réserve ».
  - Pour la phase B, une condition est gagnée seulement si les 3 tests de la
    condition sont des victoires.
- **Rapportés pour chaque test :**
  - les moyennes, l'IC à 95 % bootstrap (2 000 tirages, graine 0) de chaque
    méthode et de l'écart apparié ;
  - le nombre d'essais gagnés ;
  - p brute et p de Holm.
- **Familles secondaires** (descriptives, Holm dans chaque famille) :
  - A : DRL contre chaque concurrent, contre `couverture` et contre `drl_idle` v4 ;
  - B et C : métriques secondaires.
- Dans 3 des 4 conditions dataset, les vitesses sont égales. `greedy_time` et
  `greedy_pair` y donnent donc les mêmes essais, et les 14 tests A ne recouvrent
  que 11 comparaisons distinctes (comme en v4). On les garde à 14 pour rester
  comparable à la v4 ; la correction de Holm sur 14 tests est prudente.
- **Tout est rapporté**, y compris les défaites et les égalités. Les graines de
  test, les concurrents et les métriques ne sont **pas** modifiés après avoir vu
  les résultats.

## 8. Livrables

- `~/warehouse_ws/resultats_v6/` contient :
  - `VALEURS_V6.md` : tous les chiffres, avec leur fichier et leur ligne ;
  - `BILAN_V6.md` : victoires, égalités, défaites et déviations du protocole ;
  - les figures `fig_*_ecarts_v6.png`, au même style que la v4 ;
  - les CSV bruts et les courbes d'entraînement ;
  - une copie de ce protocole.
- `~/warehouse_ws/resultats_v6.zip`.
- Un commit sur la branche `drl-v6`, sans pousser.

## Écarts

(aucun à la date de rédaction)
