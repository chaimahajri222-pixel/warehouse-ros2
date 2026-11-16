# Conformité au cahier des charges (v6)

Sujet : *Intelligent Distributed Multi-Agent Coordination for Autonomous Smart
Warehousing in Industry 4.0*. État au 17/11/2026, branche `drl-v6`.

Ce fichier met à jour `doc/v5/CONFORMITE_CAHIER.md`. Il ajoute :
- les résultats v6 du banc (`VALEURS_V6.md`, `BILAN_V6.md`) ;
- les **premières mesures dans Gazebo**, sur ce PC, avec 3 robots (dossier
  `gazebo_3robots/`).

**Statuts.** ✅ atteint ; 🟡 partiel ; ❌ non atteint. Un statut est « atteint »
seulement s'il est mesuré et, pour un gain, significatif. Les chiffres du banc
viennent de tests de Wilcoxon appariés, avec 20 graines de test et une correction
de Holm.

## 1. Résultats attendus du sujet

| Résultat attendu | Statut | Preuve | Ce qu'on peut affirmer |
|---|---|---|---|
| **Protocole de coordination distribué pour des agents robotiques hétérogènes** | ✅ (hétérogénéité 🟡) | `consensus_node.py` (un agent par robot) ; banc `banc/*_statistiques.csv` ; v5 `test_ros_pertes.txt`, `test_ros_blocage.txt` ; **Gazebo : `gazebo_3robots/`** | Le protocole fonctionne sans arbitre central : enchères, fenêtre de 1,5 s, conflits résolus. Il résiste à 50 % de pertes d'enchères (attribution unique vérifiée dans ROS). Il tourne de bout en bout dans Gazebo avec 3 robots. Il est **plus lent** qu'un dispatcher central dans le banc (+19 % contre FIFO), ce qui est le prix de la décentralisation. Les vitesses hétérogènes ne sont testées que dans le banc ; dans Gazebo, les robots sont identiques. |
| **Framework DRL pour l'allocation de tâches et la planification de chemin** | ✅ implémenté, 🟡 en efficacité | Allocation : v1 à v3, `drl_allocator_node.py`, v6 `alloc6.py`. Chemin : v4 `drl_route`, v6 `drl_route6` (congestion), `route_mode:=drl` dans ROS. Anticipation : `drl_idle` v4 et `drl_idle6` v6. | Les trois DRL sont implémentés et entraînés. Le DRL d'allocation et celui de chemin sont intégrés dans ROS 2. Ce sont des DQN « résiduels » : non entraînés, ils reproduisent exactement l'heuristique, ce qui est vérifié par des tests unitaires. L'efficacité est traitée dans la ligne suivante. |
| **Réduction du temps de traitement par rapport aux heuristiques** | 🟡 partiel | `principal_idle6.csv`, `principal_route6.csv`, `BILAN_V6.md` ; Gazebo `gazebo_3robots/synthese_gazebo_3robots.csv` | Les résultats sont détaillés en section 2. **Oui** pour l'anticipation : `drl_idle6` gagne 7 tests sur 14 contre les heuristiques classiques, dont −16,1 % à 20 robots / 150 racks. **Non** pour l'allocation (v4 : 0 sur 22 ; v6 : apprentissage échoué). **Non** pour le chemin (v4 : 0 sur 24 ; v6 : 1 sur 12, aucune condition gagnée). Dans Gazebo, pas de différence mesurable (une seule exécution par mode). |
| **Réduction des taux d'erreur par rapport aux heuristiques** | ✅ inventaire, ❌ tâches | `rfid/rfid_offline_experiment.csv` l.61 ; `derives/comparaison_cahier.csv` l.398 à 401 ; `principal_*6.csv` (colonnes d'échecs) | Erreur d'inventaire : **79,8 % avec le WMS seul, 4,0 % avec le RFID adaptatif (−95 %)**, sur 10 graines sur 10, p = 0,002. Tâches échouées : pas de baisse due au DRL (A : jamais plus d'échecs que l'heuristique ; B : 0 échec partout). |
| **Validation par simulation à grande échelle** | 🟡 partiel | Banc : jusqu'à **20 robots et 150 racks**, données réelles Footwear, 1 680 + 320 essais v6. Gazebo : `gazebo_3robots/` | La grande échelle est validée dans le **banc** (simulation à événements discrets du graphe), pas dans Gazebo. Gazebo n'a été mesuré qu'avec **3 robots** et une exécution par mode : le PC (8 Go, 4 cœurs) sature. Le guide et le script sont prêts pour un PC plus puissant (`README_SIMULATION.md`). |

## 2. Réduction du temps de traitement : détail v6 (banc, graines de test nouvelles)

| DRL | Tâche | Contre | Résultat (Holm, α = 0,05) | Source |
|---|---|---|---|---|
| `drl_idle6` | point d'attente des robots inoccupés | meilleure des 3 heuristiques classiques | **7 victoires**, 5 égalités, **2 défaites** sur 14 | `principal_idle6.csv` |
| `drl_idle6` | | couverture (sa propre heuristique de départ) | 2 victoires, 12 égalités, 0 défaite | `principal_idle6.csv` |
| `drl_idle6` | | règle stricte (battre les deux) | **2 sur 14** (15 racks, ρ = 0,7) | `VALEURS_V6.md` §2 |
| `drl_route6` | routage avec capacité de 1 robot par allée | chacune des 3 Dijkstra | 1 victoire, 11 égalités ; 0 condition sur 4 gagnée | `principal_route6.csv` |
| `drl_alloc6` | allocation avec action « attendre » | `greedy_pair`, `greedy_time` | apprentissage échoué, non testé | `PROTOCOLE_V6.md` écart 8 |

Points marquants :
- **150 racks / 20 robots :** 56,82 s contre 67,68 s, soit **−10,86 s (−16,1 %)**,
  sur 19 essais sur 20. Le DRL v4 perdait ici (+10,7 %).
- **Défaites :** Zipf facile, +2,3 s et +1,9 s.
- **Origine du gain à grande échelle :** il vient surtout de l'heuristique de
  **couverture** conçue en v6, et non de l'apprentissage. Contre elle, l'écart
  n'est que de −0,66 s, non significatif.

## 3. Mesures dans Gazebo (3 robots, ce PC, 16/11/2026)

Les tâches sont générées en continu pendant 900 s par mode, avec Nav2 et
`ros_gz_bridge`, sans interface graphique. Le temps est mesuré de la création de
la tâche à sa fin (`elapsed_sec`), avec la même définition que dans le banc.
L'IC à 95 % est un bootstrap sur les tâches réussies.

| Exécution | État | Tâches émises | Vues | Réussies | Échouées | En cours à la fin | Temps moyen [IC 95 %] | Médiane | Mémoire libre min. | Charge max. | T max. | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| heuristic (consensus seul) | valide | 28 | 24 | 19 | 3 | 2 | 14.26 s [8.58 ; 20.69] | 12.19 s | 1270 Mo | 109.42 | 74 °C | `gazebo_3robots/synthese_gazebo_3robots.csv` l.2 |
| hybrid, 1re execution | INVALIDE : processus Nav2 restants, carte jamais recue | 0 | 0 | 0 | 0 | 0 | – | – | 635 Mo | 147.23 | 74 °C | `gazebo_3robots/synthese_gazebo_3robots.csv` l.3 |
| hybrid (consensus + DRL v3), reprise | valide | 27 | 25 | 16 | 6 | 3 | 12.98 s [7.04 ; 20.79] | 9.23 s | 1130 Mo | 111.14 | 72 °C | `gazebo_3robots/synthese_gazebo_3robots.csv` l.4 |
| idle_mode:=stay | valide (robot2 : 5 abandons Nav2) | 16 | 13 | 3 | 7 | 3 | 16.91 s [14.5 ; 19.65] | 16.59 s | 1401 Mo | 117.27 | 72 °C | `gazebo_3robots/synthese_gazebo_3robots.csv` l.5 |
| idle_mode:=drl (modele v4) | valide mais 8 taches emises, 2 executees (carte incomplete) | 8 | 2 | 1 | 1 | 0 | 10.96 s (1 tâche) | 10.96 s | 1244 Mo | 103.78 | 70 °C | `gazebo_3robots/synthese_gazebo_3robots.csv` l.6 |

**Lecture.**
- La **même configuration** (`heuristic` avec `idle_mode:=stay`) donne 19 tâches réussies sur 24 dans une exécution, et 3 sur 13 dans une autre (robot2 : 5 abandons de Nav2).
- Le nombre de tâches émises varie de 8 à 28 selon l'avancement de la carte (exploration SLAM).
- Sur ce PC, la variabilité due à la machine dépasse donc tout effet de la méthode. **Aucune comparaison entre modes n'est interprétable.**
- Ce que ces mesures montrent, c'est que **le système complet fonctionne de bout en bout dans Gazebo** dans tous les modes : génération des tâches, enchères de consensus, biais DRL (`hybrid`), politique `drl_idle` chargée et utilisée, navigation Nav2, lectures RFID.

**Limites, à lire avant tout chiffre :**
- Il n'y a **qu'une exécution par mode**, et les tâches d'une même exécution ne
  sont pas indépendantes. Aucun test statistique n'est valide : ces chiffres
  **décrivent** le fonctionnement, ils ne prouvent pas un gain.
- Le PC est surchargé : charge jusqu'à 147 pour 4 cœurs, et jusqu'à 0,6 Go
  seulement de mémoire libre (`ressources_*.log`). La température est restée
  ≤ 74 °C, sans arrêt thermique (`temperature.log`). Nav2 abandonne certains buts (`nav_status` 6), d'où des échecs
  qui tiennent probablement à la machine plus qu'à la méthode.
- **Une première exécution `hybrid` est invalide.** Des processus Nav2 de
  l'exécution précédente tournaient encore, et la carte n'a jamais été reçue
  (0 tâche). Elle est conservée dans `a_3robots/launch_hybrid_FAUSSE_*.log` et
  refaite sur un PC propre. Le script de nettoyage a été corrigé
  (`mesures_gazebo.sh`).
- `idle_mode:=drl` utilise dans ROS le modèle **v4** (`selected_idle.pt`). Les
  modèles v6 ne sont pas encore intégrés à ROS.

## 4. Autres exigences de la description du sujet

| Exigence | Statut | Commentaire |
|---|---|---|
| Entrepôt modélisé en **graphe dynamique** | ✅ | Congestion et blocages en direct dans ROS (le blocage se propage aux enchères, testé 3 fois sur 3) et dans le banc. La chaîne « échecs Nav2 → blocage » n'est pas exercée dans Gazebo. |
| **Architecture multi-agents hybride** | ✅ | Agents décentralisés (consensus) et biais DRL central optionnel (`drl_mode:=hybrid`). |
| **Couche RFID** | ✅ | Lecteur UHF probabiliste (logiciel, pas de plugin radio Gazebo), inventaire bayésien. |
| **Couche de communication IoT** | 🟡 | ROS 2 / DDS en publish/subscribe et JSON. Pertes de messages injectées (enchères dans ROS, tous les messages dans le banc). Pas de retard injecté dans ROS, ni de protocole IoT matériel (MQTT…). |
| **Décision adaptative sous incertitude** | ✅ | Scans RFID déclenchés par l'incertitude : meilleurs que les lectures opportunistes (10 graines sur 10, p = 0,002). Replanification en cas de blocage. |
| **Gestion d'inventaire en temps réel** | ✅ | Inventaire mis à jour en continu par les lectures de tous les robots (`inventory_node`), visible sur le tableau de bord. |

## 5. Synthèse honnête

- **Ce qui est solide :**
  - un cadre complet et fonctionnel, du graphe dynamique au tableau de bord, qui
    tourne dans ROS 2 et dans Gazebo ;
  - un protocole de consensus robuste aux pertes ;
  - une **réduction de 95 % de l'erreur d'inventaire** grâce au RFID adaptatif ;
  - un **gain significatif de temps à grande échelle** pour l'anticipation
    (−16 % à 20 robots / 150 racks) ;
  - une méthodologie rigoureuse : protocole écrit et commité avant les
    entraînements, graines de test jamais vues, Wilcoxon et Holm, déviations
    datées.
- **Ce qui est partiel :**
  - le DRL ne bat pas les heuristiques pour l'allocation ni pour le chemin. Les
    causes sont identifiées : Dijkstra est déjà presque optimal sans forte
    congestion, et les récompenses avaient des biais, documentés et corrigés en
    v6 ;
  - le gain d'anticipation vient surtout de l'heuristique de couverture ;
  - Gazebo n'a été mesuré qu'à 3 robots, avec une exécution par mode.
- **Ce qui reste à faire :** des mesures Gazebo répétées, à 6 robots ou plus, sur
  une machine plus puissante (guide prêt), et l'intégration de `drl_idle6` dans
  ROS.
