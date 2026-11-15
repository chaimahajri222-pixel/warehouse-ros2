# Protocole expérimental v4 : DRL de chemin et DRL d'anticipation

Branche `drl-v4` (issue de `drl-v2`, commit a3ec3fa). Rédigé le 15/11/2026, avant
tout entraînement et toute exécution de test. **Ce fichier n'est plus modifié après le
premier essai de test.** Tout écart est consigné à la fin, dans la section
« Écarts », avec sa date et sa raison. Le texte d'origine n'est pas modifié.

## 0. Contexte et constat préalable

- Le cahier des charges demande (1) un DRL pour la planification de chemin et
  (2) une réduction du temps de traitement par rapport aux heuristiques. Le DRL
  d'allocation v3 ne bat la meilleure heuristique dans aucune des 22 conditions.
- Constat sur le code, avant toute expérience : dans `allocation_benchmark.py`,
  `Benchmark.move()` recalcule le plus court chemin à **chaque nœud**. Il utilise
  `WarehouseGraph.shortest_path`, dont le coût d'une arête vaut longueur + 2 × congestion,
  et +inf si l'arête est bloquée. Le comportement actuel du banc est donc déjà une
  **replanification dynamique**. Dans ROS 2, `mission_executor_node` envoie un seul
  `NavigateToPose` vers la cible, sans route sur le graphe. Les deux adversaires sont
  définis ainsi :
  - `dijkstra_statique` : route calculée une fois, au départ de la tâche, sur les
    **longueurs seules** (sans congestion), en excluant les arêtes bloquées à cet
    instant. Le robot la suit. Il replanifie (sur les longueurs) seulement si l'arête
    suivante est bloquée, faute de quoi il ne pourrait pas avancer. C'est un chemin
    statique sur le graphe, comparable à ce que fait ROS aujourd'hui.
  - `dijkstra_dynamique` : replanification à chaque nœud avec les coûts en direct
    (longueur + 2 × congestion, arêtes bloquées exclues). C'est **exactement**
    l'ancien `move()` du banc, donc l'adversaire le plus fort.

## 1. Hypothèses

- **H1 (chemin).** Avec une allocation fixée, `drl_route` réduit le temps de
  traitement moyen par tâche par rapport à la **meilleure** des deux Dijkstra.
  Cette meilleure Dijkstra est choisie sur les essais de test de la même condition
  et de la même allocation, ce qui avantage l'heuristique.
- **H2 (anticipation).** Avec une allocation fixée, `drl_idle` réduit le temps de
  traitement moyen par tâche par rapport à la **meilleure** des trois heuristiques de
  point d'attente, choisie de la même manière sur les essais de test.
- Hypothèse nulle de chaque test : la distribution des différences appariées
  (DRL − adversaire) est symétrique autour de 0. Le test est bilatéral.

## 2. Métriques

Elles sont calculées par essai (une graine = un essai de 150 tâches).

| Métrique | Définition | Rôle |
|---|---|---|
| `temps_traitement_moy_s` | moyenne de (fin − création) sur les tâches **terminées** (définition existante du banc) | **principale** (H1, H2) |
| `temps_trajet_moy_s` | moyenne de (arrivée au rack − début de la tâche) sur les tâches terminées | secondaire |
| `taches_echouees` | tâches abandonnées (90 s sans pouvoir avancer, règle existante) | secondaire, garde-fou |
| `conflits_pour_100_taches` | entrées sur une arête déjà occupée (même sens ou sens inverse), pour 100 tâches terminées | secondaire |
| `attente_noeud_par_tache_s` | temps passé immobile à un nœud (pas de chemin, ou attente choisie), par tâche terminée | secondaire |
| `approche_moy_s` (H2) | moyenne de (arrivée au rack − attribution) | secondaire |
| `ms_par_decision` | temps de calcul moyen d'une décision de route ou d'attente | descriptif |

Comme les tâches échouées ne comptent pas dans la métrique principale, un gain
obtenu avec **plus** d'échecs que l'adversaire est signalé comme tel et n'est pas
présenté comme une amélioration.

## 3. Méthodes

### 3.1 `drl_route` (étape 1)

- **Décision :** à chaque nœud où le robot a au moins deux arêtes sortantes, il
  choisit l'arête suivante parmi tous ses voisins. Choisir une arête bloquée signifie
  attendre 1 s au nœud, puis décider de nouveau. Les deux Dijkstra n'attendent que
  s'il n'existe aucun chemin.
- **Q résiduel :**
  Q(e = u→v) = −(c(u,v) + d(v, but)) / D + f_θ(x_e).
  - c(u,v) est le coût en direct de l'arête (longueur + 2 × congestion). Une arête
    bloquée prend la valeur longueur + P, avec P = 2 × diamètre du graphe.
  - d(v, but) est la distance de Dijkstra en direct du voisin au but, plafonnée à P
    si le but est inaccessible.
  - D = 60 s × vitesse du robot. Pour tout D > 0, l'argmax ne change pas, donc avec
    f_θ = 0 la politique est **exactement** `dijkstra_dynamique` (mêmes coûts ;
    égalités départagées par le nom du voisin). Ce choix de D met le terme a priori
    à l'échelle du retour (−temps / 60) en écoulement libre.
  - La dernière couche de f_θ est initialisée à zéro.
- **Caractéristiques x_e (normalisées) :**
  - longueur de l'arête ;
  - robots présents sur l'arête (même sens et sens inverse) ;
  - robots en route, c'est-à-dire ceux dont le prochain nœud est v ou dont la route
    prévue passe par l'arête ;
  - drapeau de blocage ;
  - temps de blocage déjà écoulé ;
  - distance au but depuis le voisin, en direct et sur les longueurs ;
  - charge de la file à destination : autres robots dont la tâche ou la file vise
    le même rack, divisée par la capacité du rack ;
  - vitesse du robot ;
  - indicateur de demi-tour ;
  - terme a priori.
- **Récompense :** −(durée de l'étape) / 60. L'étape va de la décision à la décision
  suivante du même robot (traversée de l'arête ou attente de 1 s). La transition est
  terminale à l'arrivée au rack.
- **Apprentissage :** Double DQN, perte de Huber, cible douce (τ = 0,005),
  γ = 0,99. Réseau 64-64, Adam (lr = 3·10⁻⁴), lot de 64, mémoire de 100 000
  transitions, 1 000 transitions avant la première mise à jour, gradient borné à 5.
  ε-glouton, ε passe de 0,3 à 0,02 en décroissance linéaire sur 60 % du budget de
  temps. La politique (ε excepté) est partagée par tous les robots.
- **Garde-fou anti-boucle :** au-delà de 3 × |V| décisions pour une même tâche, le
  robot suit `dijkstra_dynamique`. Le nombre de déclenchements est rapporté.
- **Allocation pendant l'entraînement :** `greedy_pair`.
- **Scénarios d'entraînement :** tirés au hasard à chaque épisode.
  - Flotte et entrepôt : 3 robots / 15 racks, 6 / 40, 10 / 80 ou 20 / 150.
  - Blocages : 0, 1, 3 ou 6 par minute.
  - Charge : ρ ∈ {0,7 ; 0,9}.
  - Tâches synthétiques uniformes, ou fenêtres aléatoires des vagues **train_fit**.
  - 100 tâches par épisode.

### 3.2 `drl_idle` (étape 2)

- **Décision :** quand un robot devient inoccupé (ni tâche ni file), il choisit un
  point d'attente parmi K = 6 nœuds candidats :
  - sa position actuelle ;
  - `charging_dock` ;
  - le centre de demande ;
  - les 3 nœuds suivants dans l'ordre de la distance espérée à la demande, en
    excluant les candidats déjà retenus.

  Le robot s'y rend (routage `dijkstra_dynamique`) et reste attribuable pendant le
  trajet.
- **Estimation de la demande p(rack) :**
  - conditions dataset : fréquences des racks dans **train_fit**, projetées sur le
    graphe ;
  - condition Zipf : fréquences **observées depuis le début de l'essai** (tâches déjà
    arrivées), avec un lissage de Laplace (+1). Aucune information future n'est
    utilisée.
- **Q résiduel :** Q(c) = −E_p[d(c, rack)] / D + f_θ(x_c), avec la dernière couche de
  f_θ à zéro. Le terme a priori est maximal au centre de demande, donc avec
  f_θ = 0 la politique est **exactement** `centre_de_demande`.
- **Caractéristiques x_c :**
  - E_p[d(c, ·)] ;
  - distance du robot à c ;
  - autres robots inoccupés présents en c ou en route vers c ;
  - distance de c au robot inoccupé le plus proche ;
  - masse de demande dans un rayon de 1 arête ;
  - indicateurs (position actuelle, dépôt, centre) ;
  - robots libres / flotte ;
  - longueur de la file ;
  - vitesse ;
  - terme a priori.
- **Récompense :** −(temps d'approche de la prochaine tâche attribuée au robot) / 60.
  Le temps d'approche va de l'attribution à l'arrivée au rack. La transition se
  termine à la décision d'attente suivante du même robot ; elle est terminale si
  l'essai finit avant. γ = 0,9. Le reste est identique à 3.1, avec ε de 0,3 à 0,02.
- **Allocation pendant l'entraînement :** `greedy_pair` ou `greedy_time`, tirée au
  hasard à chaque épisode.
- **Données d'entraînement :** fenêtres aléatoires des vagues **train_fit**, avec
  les configurations des 4 conditions dataset. La condition Zipf n'est **pas** vue
  à l'entraînement ; c'est un test de généralisation.

### 3.3 Adversaires

- **Chemin :** `dijkstra_statique` et `dijkstra_dynamique` (§0).
- **Anticipation :**
  - `rester_sur_place` : le comportement actuel du banc ;
  - `retour_au_depot` : `charging_dock` ;
  - `centre_de_demande` : le nœud qui minimise E_p[d(n, rack)] (1-médiane pondérée
    par la demande ; même estimation p que `drl_idle`).
- L'heuristique de référence de chaque test est la meilleure de ces adversaires
  (§1).

## 4. Données, graines et séparation

| Usage | Graines de simulation | Tâches |
|---|---|---|
| Entraînement | tirées dans [10 000 000 ; 10⁹), **refusées** si elles tombent dans un ensemble de validation ou de test (assertion dans le code) | synthétiques, ou vagues **train_fit** |
| Validation (sélection) | 500 000 + 1 009 × i, i = 0, 1, … | synthétiques, ou vagues **train_val** (fenêtres régulièrement réparties) |
| Test | 1 000 × k + 7, k = 0 … 19 (**20 essais par condition**, convention du banc) | synthétiques, ou vagues **test** (k-ième de 20 fenêtres régulièrement réparties) |

Les trois ensembles de graines sont disjoints (vérifié par assertion). Le découpage
chronologique de Footwear est celui de `dataset_footwear.py` :
- 70 % des vagues pour train et 30 % pour test ;
- à l'intérieur de train, 85 % pour train_fit et 15 % pour train_val.

Toutes les méthodes d'une même condition voient, pour une graine donnée, les mêmes
arrivées, les mêmes cibles et les mêmes blocages, car ceux-ci sont tirés par des
générateurs séparés. Les essais sont donc **appariés**.

**Validation de `drl_route` :** 12 scénarios fixes, évalués avec `greedy_pair` et
ε = 0 :
- 3 robots / 15 racks avec 1, 3 et 6 blocages par minute ;
- 6 robots / 40 racks avec 3 blocages par minute ;
- 10 robots / 80 racks avec 1 blocage par minute ;
- train_val, 3 robots, ρ = 0,9 ;
- 2 graines chacun.

**Validation de `drl_idle` :** les 4 configurations dataset × 2 allocations ×
2 fenêtres de train_val, soit 16 scénarios.

## 5. Budget et sélection des modèles

- Pour chaque modèle (`drl_route`, `drl_idle`) : **3 graines d'entraînement** (0, 1, 2).
  Chaque graine dispose d'au plus **2 h de temps réel**, et les graines tournent en
  parallèle. Calcul sur CPU uniquement, avec `torch.set_num_threads(1)` pour chaque
  processus.
- Validation toutes les 10 minutes environ, plus une validation à l'instant 0
  (f_θ = 0, donc l'heuristique de départ).
- Le **modèle retenu** est le point de contrôle (graine, instant) de plus faible
  temps de traitement moyen en **validation**. L'instant 0 fait partie des candidats.
  Aucune donnée de test n'intervient dans ce choix ni dans le réglage des
  hyperparamètres, fixés ci-dessus avant tout essai.
- Si le point retenu est l'instant 0, le modèle testé est l'heuristique elle-même.
  On le rapporte tel quel.
- Seul le modèle retenu est évalué sur le test, une seule fois.

## 6. Expériences de test

**Étape 1 (chemin) :** méthodes `dijkstra_statique`, `dijkstra_dynamique` et
`drl_route`, avec deux allocations, `greedy_pair` puis `consensus`.

| Expérience | Conditions | Réglages |
|---|---|---|
| blocages | 0, 1, 3, 6 blocages par minute | 3 robots, 15 racks, ρ = 0,7, tâches synthétiques uniformes |
| taille | 3 / 15, 6 / 40, 10 / 80, 20 / 150 (robots / racks) | ρ = 0,7, **1 blocage par minute** (choisi pour que le routage ait un effet ; le cas sans blocage est couvert par « blocages = 0 ») |
| dataset | les 4 conditions « dataset » du banc (vagues de **test**, sans blocage) | 15 racks avec 3 robots à ρ = 0,7 et ρ = 0,9 ; 40 racks avec 6 robots à vitesses variables ; 150 racks avec 20 robots à ρ = 0,7 |

Cela fait 12 conditions × 2 allocations × 3 méthodes × 20 graines, soit
**1 440 essais**.

**Étape 2 (anticipation) :** méthodes `rester_sur_place`, `retour_au_depot`,
`centre_de_demande` et `drl_idle`, avec deux allocations, `greedy_pair` et
`greedy_time`. Le routage est `dijkstra_dynamique`.

| Expérience | Conditions |
|---|---|
| dataset | les 4 conditions dataset (vagues de test) |
| zipf | les 3 niveaux du scénario `structured` (facile, moyen, difficile ; demande de Zipf avec un exposant de 0,5, 1,0 et 1,5) |

Cela fait 7 conditions × 2 allocations × 4 méthodes × 20 graines, soit
**1 120 essais**.

## 7. Analyse statistique

- Pour chaque (condition, allocation) :
  - moyenne et IC à 95 % bootstrap (2 000 rééchantillonnages, graine 0) par méthode ;
  - IC à 95 % bootstrap de l'écart apparié ;
  - nombre d'essais gagnés.
- **Test principal :** test des rangs signés de Wilcoxon apparié et bilatéral
  (`scipy.stats.wilcoxon`, options par défaut). Il compare le DRL à la meilleure
  heuristique, choisie sur les essais de test de cette (condition, allocation).
  - Famille A (H1) : 12 × 2 = **24 tests**.
  - Famille B (H2) : 7 × 2 = **14 tests**.
  - **Correction de Holm** dans chaque famille, avec **α = 0,05**.
- **Règle de décision :** le DRL « réduit le temps de traitement » dans une
  (condition, allocation) si les trois conditions suivantes sont réunies :
  - la valeur p ajustée par Holm est inférieure à 0,05 ;
  - l'écart moyen est négatif ;
  - le DRL n'a pas plus de tâches échouées au total que l'heuristique comparée.

  Si p ajustée < 0,05 avec un écart positif, l'heuristique est significativement
  meilleure, et on le rapporte comme tel.
- **Tests secondaires :**
  - DRL contre chaque adversaire pris séparément ;
  - métriques secondaires.

  Leurs valeurs p sont rapportées avec la correction de Holm dans leur propre
  famille, une famille par métrique et par étape. Ils sont descriptifs et ne servent
  pas à conclure sur H1 ou H2.
- **Tous les résultats sont rapportés**, y compris les résultats négatifs et nuls.
  Aucune valeur n'est rapportée sans le fichier CSV et la ligne dont elle provient.

## 8. Étape 3 : intégration ROS 2 (si le temps le permet)

- Ajouter le paramètre `route_mode:=dijkstra|drl` à `mission_executor_node`. Avec
  `drl`, la route du graphe (politique `drl_route`) est convertie en points de
  passage Nav2 et envoyée par `FollowWaypoints`.
- Test fonctionnel court sur un domaine ROS isolé (`ROS_DOMAIN_ID` dédié,
  `ROS_LOCALHOST_ONLY=1`) : démarrage du nœud, conversion d'une route en points de
  passage, envoi du but.
- Ce test ne mesure **pas** les performances.

## 9. Livrables

Le dossier `~/warehouse_ws/resultats_v4`, compressé en `resultats_v4.zip`, contient :
- `VALEURS_V4.md` : chaque valeur avec son fichier et sa ligne ;
- les CSV des essais et des statistiques ;
- les figures (moyenne et IC à 95 %) ;
- les courbes d'entraînement ;
- `CONFORMITE_CAHIER.md` mis à jour ;
- un bilan en 5 phrases.

## Écarts

Tous les écarts ci-dessous ont été décidés le 15/11/2026, **avant tout entraînement
complet et avant tout essai de test**. Ils viennent des équivalences et d'un essai
d'entraînement de 4 minutes, rejeté ensuite.

1. **Attente et départage des égalités (§3.1).** L'action « attendre » (un candidat
   de plus, en plus des arêtes ; choisir une arête bloquée revient aussi à attendre)
   dure 1 s. Elle s'interrompt dès que l'ensemble des arêtes bloquées change.
   Le terme a priori de l'attente vaut −(d(u, but) + 0,01 m) / D. Un bonus de 10⁻³
   (en unités de Q) est ajouté à l'action que choisirait `dijkstra_dynamique` (le
   voisin suivant, ou l'attente s'il n'y a pas de chemin). Le départage par le nom
   du voisin n'est donc pas utilisé.
   *Raison :* sans cela, f_θ = 0 ne reproduisait pas exactement `dijkstra_dynamique`
   dans les égalités de la grille et quand il n'existe aucun chemin libre.
   L'équivalence exacte est vérifiée par `test/test_v4.py`, pour `drl_route` comme
   pour `drl_idle`.
2. **γ = 1 pour `drl_route` (au lieu de 0,99).** *Raison :* avec un escompte par
   décision, 60 s d'attente découpées en décisions courtes coûtaient presque rien
   (0,99^n). L'épisode d'une route est fini : il se termine à l'arrivée, à l'échec
   après 90 s d'attente, ou au repli après 3|V| déplacements. Le retour non escompté
   est donc défini, et il correspond à l'objectif (le temps total).
3. **Compression du terme a priori.** Le coût de l'arête plus la distance au but,
   avec P = 1000 m pour une arête bloquée, passe par la fonction strictement
   croissante g(x) = x si x ≤ 3 × diamètre, et 3 × diamètre + 0,001 (x − 3 × diamètre)
   sinon. Les caractéristiques de distance sont compressées de la même façon.
   *Raison :* dans l'essai de 4 minutes, des valeurs a priori de −33 faisaient
   diverger la correction. Comme g est strictement croissante, l'argmax ne change
   pas et l'équivalence du point 1 tient toujours.
4. **Durée maximale d'un épisode d'entraînement :** 1 800 s simulées après la
   dernière arrivée (au lieu de 3 600 s). Cela évite qu'un épisode dégradé par
   l'exploration consomme le budget. Ne s'applique ni à la validation ni au test.
5. **Budget :** 115 min d'entraînement par graine, plus la dernière validation,
   pour rester sous 2 h par graine.

### Incident consigné après le début des entraînements

6. **Interruption de l'entraînement de `drl_idle` (15/11/2026, 17 h 14).** Le
   premier lancement des 3 graines (16 h 30) s'est arrêté après environ 43,7 min
   sur 115 : la mémoire de la machine (RAM et swap) était saturée, le noyau a tué
   le processus de l'éditeur, et les 3 entraînements, lancés depuis cette session,
   se sont arrêtés avec lui (journal du noyau, « Out of memory: Killed process »).
   Le script ne sait pas reprendre un entraînement (le tampon de rejeu et l'état
   de l'optimiseur ne sont pas sauvegardés).
   *Décision :* les 3 graines sont relancées **depuis le début**, avec les mêmes
   réglages (115 min, en parallèle, `torch.set_num_threads(1)`), à 17 h 26, après
   avoir vérifié qu'au moins 2,5 Go de mémoire étaient disponibles, et en processus
   détachés (`setsid nohup`). Les fichiers du premier lancement sont conservés dans
   `~/warehouse_ws/drl_v4/idle_interrompu_1714/`. Ils ne servent **ni** à la
   sélection du modèle **ni** au test. Aucune donnée de test n'a été utilisée avant
   ou pendant cet incident ; aucun réglage n'a été modifié.
