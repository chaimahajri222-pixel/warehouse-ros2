# Lancer la simulation de l'entrepôt (branche `drl-v4`)

Ce guide explique comment installer le projet, lancer la simulation Gazebo et
faire trois expériences, puis renvoyer les résultats. Il ne suppose aucune
connaissance du projet. Copie les commandes telles quelles, dans l'ordre.

**Ce qu'il faut :**
- Ubuntu 24.04 avec ROS 2 Jazzy (`ros-jazzy-desktop`) et Gazebo Harmonic ;
- 16 Go de RAM conseillés pour 6 robots. Sur un PC de 8 Go, Gazebo + Nav2 + 3
  robots remplit déjà presque toute la mémoire.

**Le projet en deux phrases :** des robots (robot1, robot2, …) se partagent des
tâches de préparation de commandes dans un entrepôt simulé. Ils se répartissent
les tâches par enchères (« consensus »), éventuellement aidés par un réseau de
neurones (DRL).

---

## 1. Installation (une seule fois)

### 1.1 Paquets système

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-ros-gz ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox ros-jazzy-xacro ros-jazzy-joint-state-publisher \
  ros-jazzy-robot-localization ros-jazzy-laser-filters \
  ros-jazzy-pointcloud-to-laserscan ros-jazzy-tf2-geometry-msgs \
  ros-jazzy-teleop-twist-keyboard ros-jazzy-opennav-docking \
  ros-jazzy-vision-msgs ros-jazzy-sensor-msgs-py ros-jazzy-cv-bridge \
  ros-jazzy-turtlebot3-description ros-jazzy-turtlebot3-gazebo \
  ros-jazzy-cartographer-ros ros-jazzy-rtabmap-slam \
  ros-jazzy-rmf-fleet-adapter-python \
  python3-colcon-common-extensions python3-rosdep python3-venv python3-pip \
  python3-numpy python3-scipy python3-matplotlib python3-networkx \
  python3-yaml python3-pytest zip
```

C'est la liste des paquets installés sur le PC où la simulation a été mise au
point. Certains ne servent pas au monde « entrepôt », mais le package
`rosnav_bot` les déclare.

### 1.2 Récupérer le code

```bash
mkdir -p ~/warehouse_ws/src
cd ~/warehouse_ws/src
git clone -b drl-v6 https://github.com/chaimahajri222-pixel/warehouse-ros2.git
```

Le dossier doit s'appeler exactement `~/warehouse_ws/src/warehouse-ros2` : les
commandes de ce guide utilisent ce chemin.

### 1.3 Environnement Python avec torch

Les modes DRL ont besoin de PyTorch. On l'installe dans un environnement
virtuel `~/warehouse_ws/.venv`, qui voit aussi les paquets du système
(`--system-site-packages`) :

```bash
python3 -m venv --system-site-packages ~/warehouse_ws/.venv
~/warehouse_ws/.venv/bin/pip install --upgrade pip
~/warehouse_ws/.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
```

La version CPU de torch suffit : les modèles sont minuscules (25 Ko). Si tu
préfères la version GPU, remplace la dernière ligne par
`~/warehouse_ws/.venv/bin/pip install torch`.

### 1.4 Compiler

```bash
cd ~/warehouse_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --base-paths src
```

Résultat attendu : `Summary: 6 packages finished`. L'option `--base-paths src`
empêche colcon de fouiller dans `.venv`.

### 1.5 Préparer chaque terminal

**Dans CHAQUE nouveau terminal**, avant toute commande `ros2` :

```bash
source ~/warehouse_ws/src/warehouse-ros2/src/warehouse_marl/scripts/env_simulation.sh
```

Ce script charge ROS 2, le projet compilé (`install/setup.bash`) et torch.
Pour ne plus y penser, ajoute cette ligne à la fin de `~/.bashrc`.

### 1.6 Vérifier l'installation (30 s, sans Gazebo)

```bash
ros2 pkg prefix warehouse_marl          # doit afficher .../install/warehouse_marl
python3 -c "import torch; print(torch.__version__)"
bash ~/warehouse_ws/src/warehouse-ros2/src/warehouse_marl/scripts/test_idle_mode_ros.sh drl \
  $(ros2 pkg prefix warehouse_marl)/share/warehouse_marl/models/selected_idle.pt
```

La dernière commande doit finir par `RC=0`.

---

## 2. Lancement de base (3 robots, avec l'interface graphique)

```bash
ros2 launch warehouse_marl warehouse_full.launch.py robot_count:=3
```

- Gazebo et RViz s'ouvrent, puis les robots explorent l'entrepôt.
- La couche « coordination » (tâches, enchères) démarre automatiquement après
  environ 50 s.
- **Tableau de bord :** ouvre http://localhost:8080 dans un navigateur. Il
  affiche la carte, les robots, les tâches et le RFID.

**Arrêter :** fais `Ctrl+C` dans le terminal, puis nettoie les processus de
Gazebo qui restent parfois :

```bash
bash ~/warehouse_ws/src/warehouse-ros2/src/rosnav/src/rosnav_bot/scripts/kill_rosnav_sim.sh -y
```

Paramètres utiles (à ajouter à la commande `ros2 launch`) :

| Paramètre | Valeurs | Effet |
|---|---|---|
| `robot_count:=N` | 1, 2, 3, … | nombre de robots |
| `drl_mode:=` | `heuristic` (défaut), `hybrid` | répartition par enchères seules, ou enchères + DRL |
| `idle_mode:=` | `stay` (défaut), `centre`, `drl` | où va un robot qui n'a plus de tâche |
| `route_mode:=` | `direct` (défaut), `dijkstra`, `drl` | chemin : Nav2 seul, ou route sur le graphe de l'entrepôt |
| `headless:=true` | | Gazebo sans fenêtre (plus léger) |
| `rviz:=false` | | sans RViz |

Les modèles DRL sont livrés avec le code (`src/warehouse_marl/models/`) et
utilisés par défaut : il n'y a aucun chemin de fichier à donner.

---

## 3. Les expériences

Les commandes partent de `~/warehouse_ws`, dans un terminal préparé (§ 1.5).
Tous les résultats vont dans `~/warehouse_ws/mesures/`.

Avant chaque expérience :
- ferme les programmes lourds (navigateur, etc.) ;
- vérifie qu'aucune autre simulation ne tourne.

### a) Mesures avec 3 puis 6 robots, modes `heuristic` et `hybrid`

Le script `mesures_gazebo.sh` lance Gazebo sans fenêtre, fait tourner chaque
mode 15 minutes (900 s), enregistre les tâches, puis arrête tout proprement.
Chaque commande dure environ 35 minutes (2 modes).

```bash
cd ~/warehouse_ws
ROBOTS=3 bash src/warehouse-ros2/src/warehouse_marl/scripts/mesures_gazebo.sh 900 "" ~/warehouse_ws/mesures/a_3robots
ROBOTS=6 MIN_FREE_MB=6000 bash src/warehouse-ros2/src/warehouse_marl/scripts/mesures_gazebo.sh 900 "" ~/warehouse_ws/mesures/a_6robots
```

- Le `""` veut dire « modèle DRL par défaut ».
- `MIN_FREE_MB` : le script refuse de démarrer s'il reste moins de mémoire libre
  que cette valeur. Il écrit alors `NON LANCE` dans `ressources_<mode>.log`.

### b) Robot inoccupé : `idle_mode:=stay` puis `idle_mode:=drl` (3 robots)

Même script, en mode `heuristic` seulement, avec un paramètre en plus. Chaque
commande dure environ 17 minutes.

```bash
cd ~/warehouse_ws
ROBOTS=3 MODES=heuristic LAUNCH_ARGS="idle_mode:=stay" \
  bash src/warehouse-ros2/src/warehouse_marl/scripts/mesures_gazebo.sh 900 "" ~/warehouse_ws/mesures/b_idle_stay
ROBOTS=3 MODES=heuristic LAUNCH_ARGS="idle_mode:=drl" \
  bash src/warehouse-ros2/src/warehouse_marl/scripts/mesures_gazebo.sh 900 "" ~/warehouse_ws/mesures/b_idle_drl
```

Avec `idle_mode:=drl`, le journal `launch_heuristic.log` doit contenir
`Politique drl_idle chargee` et des lignes `inoccupe en ... : attente drl -> ...`.

### c) Blocage d'une allée en direct

Il faut deux terminaux, préparés tous les deux (§ 1.5), avec le **même**
numéro de domaine ROS.

Terminal 1, la simulation avec fenêtres (pour filmer, § 5) :

```bash
export ROS_DOMAIN_ID=84
ros2 launch warehouse_marl warehouse_full.launch.py robot_count:=3 route_mode:=dijkstra
```

Attends que des tâches apparaissent dans le tableau de bord (2 à 3 minutes).
Ensuite, dans le terminal 2, bloque l'allée entre `shelf_2_0` et `shelf_2_1`
pendant 120 s :

```bash
export ROS_DOMAIN_ID=84
bash ~/warehouse_ws/src/warehouse-ros2/src/warehouse_marl/scripts/blocage_direct.sh \
  shelf_2_0 shelf_2_1 120 ~/warehouse_ws/mesures/c_blocage
```

Le script se déroule ainsi (environ 4 minutes) :
1. il enregistre 30 s avant le blocage ;
2. il bloque l'allée ;
3. il vérifie que le graphe en tient compte ;
4. il attend 120 s ;
5. il débloque l'allée et vérifie le déblocage ;
6. il enregistre encore 30 s.

Dans `journal.txt`, la ligne « etat pendant » doit contenir `"blocked": true`
et la ligne « etat apres » `"blocked": false`. Pendant le blocage, les routes
(`routes.log`) ne doivent plus passer par cette allée.

`route_mode:=dijkstra` fait suivre aux robots une route calculée sur le graphe,
qui évite les allées bloquées. En mode `direct` (par défaut), Nav2 choisit seul
son chemin : le blocage ne change alors que les enchères. Ce mode `dijkstra`
dans Gazebo n'a **pas** encore été essayé. Si les robots restent bloqués, refais
l'expérience sans `route_mode:=dijkstra` et note-le.

---

## 4. Résultats : où ils sont, quoi m'envoyer

| Dossier | Contenu |
|---|---|
| `~/warehouse_ws/mesures/a_3robots`, `a_6robots` | `taches_<mode>.csv` (une ligne par tâche), `synthese_taches.csv` (résumé), `rfid_<mode>.csv`, `ressources_<mode>.log` (mémoire et charge toutes les 30 s), `launch_<mode>.log` (journal complet) |
| `~/warehouse_ws/mesures/b_idle_stay`, `b_idle_drl` | mêmes fichiers, mode `heuristic` |
| `~/warehouse_ws/mesures/c_blocage` | `journal.txt`, `avant.txt`, `pendant.txt`, `apres.txt`, `encheres.log`, `assignations.log`, `statuts.log`, `routes.log` |

À la fin, ajoute la description du PC et fais **un seul zip** :

```bash
cd ~/warehouse_ws
{ lscpu | head -20; free -h; nvidia-smi 2>/dev/null | head -15; \
  git -C src/warehouse-ros2 log --oneline -1; } > mesures/pc.txt
zip -r resultats_simulation_$(date +%Y%m%d).zip mesures
```

Envoie-moi `~/warehouse_ws/resultats_simulation_<date>.zip`. Les vidéos sont trop
grosses pour le zip : envoie-les à part (Drive, WeTransfer…).

Si une expérience a échoué, envoie quand même son dossier. Le journal
`launch_*.log` permet de comprendre ce qui s'est passé.

---

## 5. Filmer l'écran

- Appuie sur **Ctrl+Shift+Alt+R** pour démarrer : un point rouge apparaît en
  haut à droite.
- Appuie de nouveau sur **Ctrl+Shift+Alt+R** pour arrêter.
- La vidéo est enregistrée dans `~/Vidéos/Screencasts/` (ou `~/Videos/Screencasts/`).
- Si l'enregistrement s'arrête tout seul après 30 s, lance une fois :
  `gsettings set org.gnome.settings-daemon.plugins.media-keys max-screencast-length 0`.

Les expériences a) et b) tournent sans fenêtre (`headless`). Filme plutôt le
lancement de base (§ 2) ou l'expérience c), avec Gazebo et le tableau de bord
visibles côte à côte.

---

## 6. Problèmes connus et solutions

| Symptôme | Cause | Solution |
|---|---|---|
| `Package 'warehouse_marl' not found` | le terminal n'est pas préparé, ou la compilation a échoué | `source ~/warehouse_ws/src/warehouse-ros2/src/warehouse_marl/scripts/env_simulation.sh` ; sinon recompiler (§ 1.4) et lire l'erreur |
| `mesures_gazebo.sh: ... unbound variable` | ancienne version du script avec `set -u` (les scripts `setup.bash` de ROS lisent des variables non définies) | dans cette branche, la ligne est `set +u` ; si tu vois `set -u`, remplace-la par `set +u` |
| `ModuleNotFoundError: No module named 'torch'`, ou `repli sur drl_mode heuristic` dans le journal | les nœuds ROS ne voient pas torch | refaire le § 1.3 et sourcer `env_simulation.sh` (il affiche un avertissement si torch manque) |
| PC qui rame, processus tués, `NON LANCE` dans `ressources_*.log` | mémoire insuffisante (6 robots = beaucoup de RAM) | fermer le navigateur ; vérifier avec `free -m` ; voir si le noyau a tué un processus : `journalctl -k \| grep -i "out of memory"` ; réduire le nombre de robots et me le signaler |
| Gazebo ou des nœuds restent après `Ctrl+C` | l'arrêt ne se propage pas toujours à Gazebo | `bash ~/warehouse_ws/src/warehouse-ros2/src/rosnav/src/rosnav_bot/scripts/kill_rosnav_sim.sh -y` |
| Deux simulations se mélangent (robots fantômes, tâches en double) | même `ROS_DOMAIN_ID` | une seule simulation à la fois, ou un `ROS_DOMAIN_ID` différent par terminal |
| `colcon build` : `can't find .../warehouse_description/worlds` | dossier vide absent | `mkdir -p ~/warehouse_ws/src/warehouse-ros2/src/warehouse_description/{worlds,urdf}` puis recompiler |
| Simulation très lente avec 6 robots | Gazebo tourne moins vite que le temps réel | normal : les 900 s sont des secondes réelles ; noter le « RTF » affiché par Gazebo |
