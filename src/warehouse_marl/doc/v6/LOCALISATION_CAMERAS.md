# Localisation par cameras et navigation sans collision (v6, 18-19/11/2026)

Objectif : faire collaborer la flotte comme dans Yumbla et al., *An Open-Source
Multi-Robot Framework System for Collaborative Environments Based on ROS2*,
IEEE Access 13 (2025), 16288-16302 : carte connue, AMCL pour chaque robot,
cameras fixes qui corrigent la position des robots, robots qui s'evitent sans
collision. Les resultats sont presentes comme la section IV de l'article
(A localisation, B navigation, C taches).

## 1. Ce qui a ete fait

| Element de l'article | Dans ce projet |
|---|---|
| Carte enregistree + map_server + AMCL par robot | `explore:=false map:=<carte>` ; la carte est generee depuis le monde SDF (origine au depart de robot1, (-1,5 ; -1,0) dans Gazebo) |
| Cameras au plafond + marqueurs ArUco, erreur 0,0244 m / 0,29 deg (Table 1) | `camera_localization_node` : 24 cameras **simulees** (grille de 5 m, champ de 3,6 m de rayon au sol) ; pose reelle Gazebo + bruit gaussien 0,025 m / 0,3 deg |
| Correction de la position (`initialpose`) a l'initialisation et apres chaque tache terminee ou echouee | idem, plus une correction quand l'ecart AMCL / camera depasse 0,30 m ou 10 deg pendant 3 controles (garde-fou) |
| Superviseur central qui connait la position des robots | `fleet_obstacles` place les autres robots a leur position **mesuree par les cameras**, relativement au robot qui recoit le nuage |
| Attribution au robot libre le plus proche | deja present : encheres (`consensus_node`) |

Lancement :

```bash
ros2 launch warehouse_marl warehouse_full.launch.py robot_count:=3 \
    explore:=false camera_localization:=true map:=<carte_sdf.yaml>
```

`mesures_cameras.sh` genere la carte et enchaine les deux modes ;
`tableau_cameras.py` produit les tableaux ci-dessous.

**Limite a ecrire dans le memoire :** les cameras ne produisent pas d'images ;
il n'y a ni rendu ni detection ArUco (trop lourd pour la machine de test). Le
noeud reproduit la *sortie* du module de l'article (pose + bruit, seulement
dans le champ d'une camera), pas sa chaine de traitement d'image.

## 2. Defaut trouve en chemin : les costmaps ne recevaient aucun capteur

Dans `nav2_multirobot_params_jazzy.yaml`, les sources des costmaps etaient
des topics relatifs (`scan`, `fleet_obstacles`, ...). Sous ROS 2 Jazzy, un
topic relatif est resolu dans l'espace de noms du noeud costmap :
`/robotN/local_costmap/scan`, ou personne ne publie. Les costmaps locales et
globales n'ont donc jamais recu ni le laser ni les autres robots (verifie :
costmap locale de robot2 entierement vide alors que robot1 etait a 1,2 m).
Les robots naviguaient avec la seule carte statique ; c'etait la cause des
collisions entre robots. Correction : topics absolus `/ROBOT_NS/...`.

**Consequence :** toutes les mesures Gazebo anterieures au 18/11/2026 (dont
`gazebo_3robots/`) ont ete faites avec des costmaps sans capteur. Elles
restent valables pour comparer les modes entre eux dans ces conditions, mais
pas comme mesure de la navigation.

## 3. Resultats (3 robots, 1 execution de 20 min par mode)

Les deux modes incluent la correction des costmaps. Meme carte, `drl_mode`
heuristic, 120 s de demarrage ignorees, 1081 s mesurees par mode.

### A. Localisation : erreur entre pose estimee et pose reelle (m)

| | AMCL seul | AMCL + cameras |
|---|---|---|
| flotte, moyenne | 0,35 | **0,15** |
| flotte, mediane | 0,13 | **0,10** |
| flotte, 95e centile | 1,68 | **0,48** |
| flotte, maximum | 3,13 | **1,12** |
| robot1, mediane / max | 0,13 / 0,18 | 0,12 / 0,80 |
| robot2, mediane / max | 0,14 / 1,26 | 0,10 / 1,12 |
| robot3, mediane / max | 0,17 / 3,13 | 0,09 / 0,74 |
| lacet, mediane (deg) | 1,4 | 0,9 |

### B. Navigation : contacts entre robots (poses reelles Gazebo)

| | AMCL seul | AMCL + cameras |
|---|---|---|
| contacts (ecart <= 2 cm) | 0 | 0 |
| quasi-contacts (2-15 cm) | 0 | 0 |
| ecart minimal robot1-robot2 (m) | 0,39 | 0,40 |
| ecart minimal robot1-robot3 (m) | 0,75 | 0,20 |
| ecart minimal robot2-robot3 (m) | 0,38 | 0,36 |

Pour comparaison, un essai de 3 min **avant** la correction des costmaps
(cameras actives) avait donne 2 contacts : robot1 a pousse robot2 pendant
environ 45 s dans la zone de depart.

### C. Taches

| | AMCL seul | AMCL + cameras |
|---|---|---|
| reussies | 7 | 9 |
| echouees | 1 | 0 |
| non terminees a la fin | 3 | 3 |
| reussies par robot (1, 2, 3) | 1, 3, 3 | 3, 4, 2 |

### Corrections envoyees par les cameras

49 corrections : 3 a l'initialisation, 10 en fin de tache, 36 sur derive.
Ecart corrige : mediane 0,42 m, maximum 0,95 m.

## 4. Lecture et limites

- La correction des costmaps supprime les contacts entre robots dans les deux
  modes ; les cameras ne sont pas necessaires pour cela.
- Les cameras bornent la derive de localisation : le 95e centile passe de
  1,68 m a 0,48 m, le maximum de 3,13 m a 1,12 m. La mediane change peu :
  AMCL est bon la plupart du temps, les cameras agissent sur les grandes
  derives (36 corrections sur derive).
- L'erreur residuelle (jusqu'a 1,1 m) vient du delai entre deux corrections
  (3 controles a 5 Hz, puis 4 s de pause) sur une machine tres chargee.
- **Une seule execution par mode, et seulement environ 3,5 min de temps
  simule** (la simulation tourne a environ 0,2 fois le temps reel : charge de
  25 a 45 sur 4 coeurs). L'ecart 7 / 9 taches n'est pas significatif ; il
  faut au moins 3 executions par mode, idealement sur une machine plus
  puissante, avant de conclure sur les taches.

Fichiers bruts : `cameras_3robots/` (syntheses JSON, erreurs de localisation
et ecarts entre robots a 5 Hz, statuts des taches, charge machine).
