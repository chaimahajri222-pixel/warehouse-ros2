# warehouse_marl

Package ROS2 (Humble / Jazzy) implementant la couche **coordination
distribuee multi-agents + DRL + RFID/IoT** demandee par le sujet de Master
*"Intelligent Distributed Multi-Agent Coordination for Autonomous Smart
Warehousing in Industry 4.0"* (ARTI, ENIT/INSAT, 2025/2026).

Ce package est concu pour se greffer **par-dessus** le socle de simulation
et de navigation ROS2 [`rosnav`](https://github.com/darshmenon/rosnav)
(Nav2 + SLAM Toolbox + Gazebo Harmonic, monde `warehouse` fourni), qui
gere la couche bas niveau (perception, evitement d'obstacles, deplacement
physique). `warehouse_marl` ajoute la couche haut niveau : graphe
dynamique, RFID, consensus distribue, allocation par DRL.

## Correspondance avec le sujet de Master

| Exigence du sujet | Fichier(s) |
|---|---|
| Entrepot modelise comme un graphe dynamique | `warehouse_marl/warehouse_graph.py` |
| Couche de detection RFID | `warehouse_marl/rfid_model.py`, `rfid_sensor_node.py`, `inventory_node.py` (voir "Couche RFID") |
| Couche de communication IoT | topics ROS 2 (DDS publish/subscribe) en JSON : `/rfid/*`, `/warehouse/*` |
| Decision adaptative | missions de scan RFID declenchees selon l'etat des racks (`inventory_node.py`, `task_generator_node.py`) |
| Protocole de coordination distribue base sur consensus | `warehouse_marl/consensus_node.py` |
| Framework DRL pour l'allocation de taches et le path planning | `warehouse_marl/drl/env.py`, `dqn_agent.py`, `train_drl.py`, `drl_allocator_node.py` |
| Validation par simulation a grande echelle | `launch/warehouse_marl.launch.py` + monde `warehouse` de rosnav |
| Reduction du temps de traitement / taux d'erreur vs heuristique | comparer les modes `heuristique seul` / `hybrid` / `direct` (voir plus bas) |

## Architecture

![Architecture du systeme](doc/architecture.svg)

Vue d'ensemble : simulation Gazebo, pile de navigation par robot, services partages de la flotte, coordination par consensus + couche RFID, et supervision (RViz, tableau de bord web). Version PNG : `doc/architecture.png`.

```
                     ┌────────────────────────┐
                     │   task_generator_node   │  (flux de commandes)
                     └────────────┬────────────┘
                                  │ /warehouse/tasks/new
                                  ▼
   ┌──────────────┐   ┌─────────────────────┐    ┌──────────────────┐
   │ rfid_sensor  │   │ graph_publisher_node │    │ drl_allocator_node│
   │    _node     │──▶│  (graphe dynamique)   │◀──│  (politique DQN)  │
   └──────────────┘   └──────────┬───────────┘    └─────────┬─────────┘
      /rfid/detections           │ /warehouse/graph_state    │ /warehouse/consensus/bid_bias
                                  ▼                            │
                  ┌───────────────────────────┐                │
                  │  consensus_node (x N)      │◀───────────────┘
                  │  un noeud PAR agent robot   │
                  └──────────────┬─────────────┘
                                  │ /warehouse/consensus/bids
                                  │ /warehouse/consensus/assignments
                                  ▼
                  ┌───────────────────────────┐
                  │ mission_executor_node      │
                  │ files + etat des taches   │
                  └──────────────┬────────────┘
                                 │ /robotN/navigate_to_pose
                                 ▼
                                Nav2
```

## Installation

```bash
# Dependances systeme ROS2 (Humble ou Jazzy)
sudo apt install ros-$ROS_DISTRO-rclpy ros-$ROS_DISTRO-std-msgs \
                  ros-$ROS_DISTRO-nav-msgs ros-$ROS_DISTRO-geometry-msgs

# Environnement Python partageant les paquets ROS systeme
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

# Dependances optionnelles pour entrainer/utiliser le DQN
python -m pip install gymnasium torch

# Construction du workspace
cd ~/chaimaws/src/warehouse-ros2
python -m colcon build --symlink-install --packages-select rosnav_bot warehouse_marl
source install/setup.bash
```

## Utilisation

### 1) Entrainer la politique DRL (hors-ligne, pas besoin de ROS2/Gazebo)

```bash
ros2 run warehouse_marl train_drl --episodes 500 --n-agents 4 --out warehouse_dqn.pt
```

Produit `warehouse_dqn.pt` (poids du reseau) et `training_log.csv`
(courbe de convergence reward / cout moyen par episode -> directement
exploitable pour les figures de ton memoire).

### 2) Lancer la simulation (terminal 1, package rosnav)

```bash
ros2 launch rosnav_bot multi_robot.launch.py \
    world:=warehouse robot_count:=4 explore:=true slam_mode:=single \
    merge_scans:=true fleet_mgmt:=false
```

### 3) Lancer la couche de coordination (terminal 2, ce package)

```bash
ros2 launch warehouse_marl warehouse_marl.launch.py \
    robot_names:="['robot1','robot2','robot3','robot4']" \
    drl_mode:=heuristic \
    map_origin_x:=-1.5 map_origin_y:=-1.0
```

Le mode `heuristic` est le point de depart valide : il ne depend pas d'un
modele appris. Les coordonnees `map_origin_x/y` doivent etre celles du spawn
Gazebo de `robot1`; dans le monde `warehouse`, la validation de collision
deplace le spawn demande `(-2.0, -1.0)` vers le point libre
`(-1.5, -1.0)`, d'ou les valeurs ci-dessus. Le generateur attend que des points de picking
soient reellement libres et connus dans `/map_fused` (`/map` sert de repli), puis les missions suspendent
temporairement les objectifs d'exploration pendant qu'elles utilisent Nav2.

Apres une modification/reconstruction de `rosnav_bot`, relancer une fois la
simulation de base afin que le `frontier_coordinator` charge ce mecanisme de
pause.

### 4) Observer le systeme

```bash
ros2 topic echo /warehouse/tasks/new
ros2 topic echo /warehouse/consensus/assignments
ros2 topic echo /warehouse/tasks/status
ros2 topic echo /rfid/detections
ros2 topic echo /rfid/inventory
ros2 topic echo /warehouse/graph_state
```

## Tableau de bord web

Organisation inspiree du dashboard AMR-X (vue "command center", carte
extraite du monde Gazebo comme `extract-sdf-worlds.mjs`), avec un theme
propre : graphite neutre, accent orange securite, racks couleur bois ;
vert = rack scanne recemment, gris = pas scanne recemment, indigo = scan
demande. Il
demarre avec `warehouse_full.launch.py` ; ouvrir **http://localhost:8080**.
Seul : `ros2 run warehouse_marl warehouse_dashboard --ros-args -p use_sim_time:=true`.

Aucune installation supplementaire : le noeud `dashboard_server.py` sert la
page et pousse l'etat au navigateur (Server-Sent Events), sans rosbridge,
Node.js ni base de donnees.

| Vue | Contenu |
|---|---|
| Vue d'ensemble | KPI (robots, missions, lectures RFID, tags lus, racks scannes, missions de scan), carte compacte, lectures RFID par seconde, flotte, activite |
| Carte en direct | monde Gazebo, robots et trajectoires, tags RFID (allumes quand ils sont lus), lectures en cours, racks colores (scanne recemment / pas recemment / scan demande), cibles des missions ; clic sur un rack -> ses tags, derniere lecture et robot, actions |
| Missions & consensus | taches (type, cible, robot gagnant, etat, duree, conflits resolus), fil du consensus |
| Lectures RFID | par rack : tags, tags lus recemment, lectures, dernier scan et robot ; fil des lectures en direct |

Actions de l'operateur (passent par le systeme normal) :
- **Demander un scan RFID** -> `/rfid/scan_requests` -> tache `rfid_scan`
  attribuee par consensus ;
- **Creer un picking** -> `/warehouse/tasks/new` -> consensus.

Les vues sont adressables : `#overview`, `#map`, `#map/shelf_2_0`,
`#reads`, `#missions`. Captures : `doc/dashboard_*.png`.
Arguments du launch : `dashboard:=false`, `dashboard_port:=8080`.

## Protocole de consensus

Chaque robot execute un `consensus_node` ; aucun arbitre central.

1. **Enchere** : a chaque nouvelle tache, chaque agent libre calcule son
   cout (plus court chemin sur le graphe dynamique / priorite, + biais DRL
   eventuel) et le diffuse sur `/warehouse/consensus/bids`. Un agent libre
   n'encherit que sur une tache ouverte a la fois, la plus prioritaire.
2. **Capacite du graphe** : un agent n'encherit pas sur une tache dont le
   rack est deja vise par une autre tache en cours (capacite 1 par rack,
   2 a 4 pour les stations). Tous les agents comptent les memes
   attributions, donc prennent la meme decision ; deux robots ne sont plus
   envoyes au meme rack, ou ils se bloquaient mutuellement.
3. **Cloture** : apres 1,5 s, chaque agent retient localement le cout
   minimal recu (egalite -> robot_id). Si personne n'a encheri (tous les
   robots occupes), la tache reste **ouverte** ; la premiere enchere
   ulterieure relance la fenetre chez tous les agents.
4. **Resolution des conflits** : une enchere arrivee trop tard peut amener
   deux agents a se croire gagnants. Chaque revendication
   (`/warehouse/consensus/assignments`) porte son cout ; tous les agents et
   le `mission_executor_node` appliquent la meme regle (cout minimal, puis
   robot_id) et les perdants se retirent. L'executeur attend 0,5 s
   (`claim_window_sec`) apres la premiere revendication avant de lancer la
   mission.

## Couche RFID

- Chaque article des racks porte un tag RFID.
- Chaque robot embarque un lecteur RFID (`rfid_sensor_node`) qui lit les
  tags proches quand il passe le long des racks.
- Le noeud `inventory_node` combine toutes les lectures pour connaitre le
  stock de chaque rack.
- **Missions de scan RFID** : un rack a verifier devient une tache
  `rfid_scan`, attribuee par consensus comme les autres ; le robot gagnant
  longe le rack et lit ses tags. Les scans sont demandes automatiquement
  ou par l'operateur depuis le tableau de bord.

### Topics

| Topic | Contenu |
|---|---|
| `/rfid/detections` | lecture d'un tag de localisation (robot, noeud) |
| `/rfid/scans` | un cycle de lecture d'un robot : position + tags lus |
| `/rfid/inventory` | stock de chaque rack, dernier scan |
| `/rfid/scan_requests` | rack a scanner |

Demander un scan depuis un terminal :

```bash
ros2 topic pub --once -w 1 /rfid/scan_requests std_msgs/msg/String \
  '{data: "{\"shelf\": \"shelf_2_1\", \"source\": \"dashboard\"}"}'
```

## Modes d'allocation comparables (pour ton evaluation experimentale)

- **Heuristique pure** (`drl_mode:=heuristic`, recommande pour valider la
  simulation) : consensus par plus court chemin + priorite, sans modele.
- **DRL direct** : `drl_mode:=direct` -> allocation centralisee par
  argmax des Q-values (necessite un `model_path` valide).
- **Hybride** : `drl_mode:=hybrid` -> le DRL oriente les encheres, la
  decision finale reste distribuee. Sans modele valide, aucun poids aleatoire
  n'est utilise et le consensus reste heuristique.

Le topic `/warehouse/tasks/status` publie `queued`, `navigating`, `retrying`,
et un etat terminal (`succeeded`, `failed`, `rejected`, `canceled`) avec
`elapsed_sec`. Il permet de mesurer le temps physique creation -> fin, plus
pertinent que le seul temps d'allocation.

## DRL v2 : evaluation

### Pourquoi une v2

Le DQN v1 (`drl/env.py`) ne pouvait pas battre l'heuristique : il recevait
+1 quand il choisissait le robot de cout minimal (il apprenait a COPIER
l'heuristique), son observation contenait l'index du robot, la charge des
robots baissait au hasard (aucun temps de traitement mesurable), l'entree
du reseau valait `n_robots*3+1` (un modele par taille de flotte) et le
biais hybride ajoutait `-Q` a des metres sans calibration.

### Ce que fait la v2

| Element | Fichier |
|---|---|
| Caracteristiques par couple (robot libre, tache), sans index de robot | `drl/features_v2.py` |
| Environnement construit sur la simulation du banc d'essai | `drl/env_v2.py` |
| Reseau partage Q(couple) a une sortie, Double DQN | `drl/pair_dqn.py` |
| Entrainement multi-graines, validation, figures, indicateurs | `drl/train_drl_v2.py` (`train_drl_v2`) |
| Methodes `drl2_direct`, `drl2_hybrid` et temoin `greedy_pair` | `allocation_benchmark.py` (`--model2`) |
| Deploiement ROS (`obs_version:=v2`, `bias_weight`) | `drl_allocator_node.py`, fichiers launch |

- **Decision** : quand des robots sont libres et que des taches attendent,
  l'agent note chaque couple (robot libre, tache parmi les K=5 plus
  anciennes dont la cible a de la place) et choisit le couple de Q maximale.
  Il choisit donc aussi QUELLE tache servir, pas seulement quel robot.
- **Caracteristiques (11)** : cout du chemin dynamique / 20, cible
  accessible, congestion sur le chemin, age de la tache, priorite, part de
  robots libres, file par robot, cout du robot libre concurrent le plus
  proche, avantage sur ce concurrent, cout de la meilleure autre tache pour
  ce robot, charge du robot. Meme dimension pour 3, 4 ou 20 robots.
- **Recompense** : `-(attente cumulee des taches en file jusqu'a la decision
  suivante + duree estimee de la tache choisie) / 60 s`, centree par une
  moyenne glissante. Sa somme sur un episode est (au signe pres) la somme des
  temps de traitement. Aucun bonus pour le robot le moins couteux (teste).
- **Episodes** : rho dans {0.5, 0.7, 0.9}, 3 a 6 robots, entrepot 5x3 ou
  8x5, 0, 1 ou 3 blocages d'aretes par minute, 80 taches.
- **Temoin `greedy_pair`** : meme espace de decision que le DRL v2, sans
  apprentissage (couple de cout de chemin minimal). Il separe ce qu'apporte
  l'apprentissage de ce qu'apporte le fait de choisir la tache.
- **Biais hybride calibre** :
  `bias = -bias_weight * (Q - moyenne des Q des robots libres) * echelle`,
  echelle = 60 s x vitesse du modele (30 m par unite de Q a 0,5 m/s),
  modifiable par le parametre `bias_scale_m`.

### Commandes

```bash
# Entrainement (3 graines, ~4 min sur un Intel i3-7020U)
ros2 run warehouse_marl train_drl_v2 --episodes 300 --seeds 3 --out-dir drl_v2

# Banc d'essai complet avec le meilleur modele
ros2 run warehouse_marl allocation_benchmark --exp all --seeds 10 \
    --model2 drl_v2/drl2_best.pt

# Deploiement ROS (le modele v2 sert pour toute taille de flotte)
ros2 launch warehouse_marl warehouse_full.launch.py drl_mode:=hybrid \
    obs_version:=v2 model_path:=$PWD/drl_v2/drl2_best.pt bias_weight:=1.0
```

`train_drl_v2` ecrit `drl2_seed<k>.pt`, `drl2_best.pt`,
`training_log_v2.csv` (recompense, perte TD, Q moyenne, norme du gradient,
epsilon, temps de traitement par episode), `validation_v2.csv`,
`indicators_v2.csv` et `training_curves_v2.png`. Options utiles :
`--no-double`, `--patience`, `--val-every`, `--gamma`, `--lr`.

### Resultats (2026-11-15, 3 graines x 300 episodes, banc 10 graines x 150 taches)

Entrainement : 4 min 15 s pour les 3 graines (arret anticipe a 140, 240 et
280 episodes). Validation (12 scenarios fixes) : DRL v2 29,15 s +/- 0,21
entre graines, FIFO 35,90 s, consensus 42,82 s, `greedy_pair` 29,05 s. Le
meilleur modele (graine 0) a ete retenu a l'episode 20 (epsilon 0,88) ; la
courbe de validation reste plate ensuite. Q n'est stable en fin
d'entrainement que pour 1 graine sur 3 (derive due au centrage glissant).

Temps de traitement moyen (s), banc d'essai, `drl2_direct` contre les
references (gain, robots gagnants sur 10 graines, Wilcoxon apparie) :

| Condition | drl2_direct | vs FIFO | vs consensus | vs greedy_pair |
|---|---|---|---|---|
| rho=0.5, 3 robots | 23.2 | +1.2 % (6/10, p=0.37) | +11.2 % (10/10, p=0.002) | -0.2 % (p=0.50) |
| rho=0.7, 3 robots | 26.7 | +9.7 % (10/10, p=0.002) | +24.2 % (10/10, p=0.002) | +0.1 % (p=1.0) |
| rho=0.9, 3 robots | 30.3 | +34.6 % (10/10, p=0.002) | +46.4 % (10/10, p=0.002) | -0.9 % (p=0.38) |
| 6 robots, 40 racks | 29.5 | +0.5 % (5/10, p=0.77) | +8.6 % (9/10, p=0.004) | -1.6 % (p=0.19) |
| 10 robots, 80 racks | 32.3 | -4.5 % (3/10, p=0.11) | +3.0 % (7/10, p=0.32) | -6.7 % (p=0.014) |
| 20 robots, 150 racks | 36.7 | -4.1 % (1/10, p=0.006) | +1.2 % (8/10, p=0.23) | -4.0 % (p=0.004) |
| 3 blocages/min | 31.9 | +21.1 % (10/10, p=0.002) | +32.4 % (10/10, p=0.002) | -0.5 % (p=0.56) |
| 6 blocages/min | 58.4 | +52.2 % (10/10, p=0.002) | +26.4 % (9/10, p=0.004) | -5.7 % (p=0.11) |
| perte 50 % | 26.7 | +9.7 % (10/10, p=0.002) | +24.7 % (10/10, p=0.002) | +0.1 % (p=1.0) |

`drl2_hybrid` reste au niveau du consensus ou un peu en dessous (-0.3 % a
-4.7 % ; significatif a rho=0.5, 1 blocage/min, 10 et 20 robots).

**Lecture honnete.** Le DRL v2 direct bat FIFO et le consensus dans
l'entrepot de demonstration, mais tout ce gain vient de l'espace de
decision (choisir aussi la tache) : `greedy_pair`, sans apprentissage, fait
aussi bien partout et mieux a grande echelle. L'apprentissage n'apporte
pas de gain mesurable :
1. la regle gloutonne est deja presque optimale pour cette recompense, et le
   reseau apprend surtout a classer les couples par cout ;
2. hors distribution (80 et 150 racks, 10 et 20 robots, alors que
   l'entrainement va jusqu'a 40 racks et 6 robots), les couts /20 sortent de
   la plage vue et le modele perd 4 a 7 % ;
3. en mode hybride, le biais ne change que le robot gagnant d'une tache
   choisie par priorite ; la perte du consensus (ordre par priorite, latence
   des encheres) n'est pas corrigee.

Pistes : apprendre un residu par rapport a `greedy_pair` (Q = -cout + correction),
figer la reference de centrage (ou passer en recompense moyenne / semi-MDP
avec gamma^dt), utiliser le temps de service realise, ajouter des
caracteristiques relatives (rang du cout, ecart au cout minimal, rang d'age)
et normaliser les couts par le diametre de l'entrepot, inclure 80-150 racks
et 10-20 robots a l'entrainement, entrainer 1000+ episodes avec 5 graines,
et en hybride laisser le DRL orienter le CHOIX DE LA TACHE de chaque robot.

## Limites connues / pistes d'extension pour le memoire

- L'environnement DRL (`drl/env.py`) est un environnement **de haut
  niveau** (allocation), pas un controleur bas niveau : le DRL ne pilote
  pas directement les roues (delegue a Nav2/MPPI de rosnav). C'est un
  choix pedagogique raisonnable a justifier/discuter dans ton memoire.
- Le lecteur RFID est simule de maniere logicielle (pas de plugin
  Gazebo).
- Les missions de scan ne prelevent pas d'articles (pas de manipulateur).
- Le DQN peut etre remplace par un algorithme multi-agent plus avance
  (QMIX, MADDPG, PPO multi-agent) pour aller plus loin dans la partie
  recherche du memoire.
