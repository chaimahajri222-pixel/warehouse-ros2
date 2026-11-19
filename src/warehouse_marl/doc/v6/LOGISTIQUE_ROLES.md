# Missions d'entrepot par roles, sans DRL (19/11/2026)

## Principe

Deux types de missions, chacune en deux etapes (prise, chargement 3 s, depose) :

| Mission | Prise | Depose | Effet sur le stock |
|---|---|---|---|
| stockage | salle de production : `station_A` (-7 ; 4) ou `station_B` (-7 ; -4), zone ouest | rack le moins plein | +1 unite |
| expedition | rack le plus plein | quai de chargement : `delivery_1` (10,5 ; 1,5) ou `delivery_2` (10,5 ; -1,5), zone jaune a l'est | -1 unite |

(coordonnees dans le monde Gazebo)

| Robot | Role | Regle |
|---|---|---|
| robot1 | `stock` | ne fait que du stockage |
| robot2 | `ship` | ne fait que de l'expedition |
| robot3 | `flex` | quand il est libre, prend une mission dans la file la plus chargee (le plus de missions en attente ; a egalite, la plus ancienne) |

Les commandes arrivent par phases de 240 s simulees : a chaque phase, un des
deux flux est 3 fois plus rapide (pic de production, puis pic de commandes
clients). Le robot polyvalent suit ce pic.

## Lancement

```bash
ros2 launch warehouse_marl warehouse_full.launch.py robot_count:=3 \
    headless:=true rviz:=false explore:=false camera_localization:=true \
    map:=$HOME/warehouse_ws/mesures_cameras/carte_sdf.yaml mission_mode:=logistics
```

Tableau de bord (http://localhost:8080), en mode logistique :

- **Score** (en haut de la vue d'ensemble) : colis sortis de production,
  entres en stock (+), sortis du stock (-), livres au quai, en transit (portes
  par les robots), stock total.
- **Plan** : jauge et nombre d'unites sur chaque rack (rouge < 25 %, vert
  > 75 %) ; « +1 » / « -1 » animes la ou un colis est pose ou retire ;
  compteurs « N sortis » a PROD-A / PROD-B et « N livres » a QUAI-1 / QUAI-2 ;
  un **carton colore sur le robot** quand il porte un colis (vert = stockage,
  jaune = expedition) et « 📦 » a cote de son nom.
- **Etape de chaque mission** : « 1/2 va chercher -> PROD-A » puis
  « 📦 2/2 livre -> E3-0 ».
- **Carte « Logistique par roles »** : files d'attente et pic de charge, role
  et mission de chaque robot, grille du stock des 15 racks (la case clignote
  quand le stock change), derniers mouvements de colis.
- Les positions affichees sont celles vues par les cameras quand
  `camera_localization:=true`.

Suivi des colis (`logistics_node`) : un colis de stockage sort de la
production au chargement et entre sur le rack a l'arrivee ; un colis
d'expedition quitte le rack au chargement et est livre au quai a l'arrivee ;
si une expedition echoue apres le chargement, le colis est remis sur son rack.

## Code

- `warehouse_marl/logistics_node.py` : commandes, stock par rack, files,
  attribution par role. Remplace `task_generator` + encheres + DRL.
- `mission_executor_node.py` : missions en plusieurs etapes (`pickup_node`),
  etat `picked_up`, parametres `with_delivery`, `handling_time_sec`.
- `warehouse_graph.py` : `build_demo_warehouse(..., with_delivery=True)`
  ajoute `delivery_1/2` (desactive par defaut : les modeles DRL ont ete
  entraines sur le graphe sans ces points).
- Options de lancement : `mission_mode:=auction|logistics`,
  `roles:=stock,ship,flex`.

## Problemes trouves et corriges (19/11/2026)

| Probleme observe | Cause | Correction |
|---|---|---|
| robot1 n'atteint pas son rack | les 3 robots envoyes dans la meme allee (rangee 0) : deux robots ne se croisent pas dans une allee (marges de securite) | le rack est choisi a l'attribution, dans une allee ou aucun autre robot n'a de mission |
| robot1 et robot3 bloques des minutes devant le mur de separation | un seul passage (4 m) entre production et racks ; face-a-face | « feu » : une seule etape a la fois peut traverser le mur (`crossing_mutex`) ; l'autre robot attend a sa place |
| simulation tres lente, controleur a 10-12 Hz au lieu de 20 | MPPI : 2000 trajectoires x 56 pas, 20 fois/s, 3 robots sur 4 coeurs | 10 Hz, 1000 trajectoires, 28 pas de 0,1 s (meme horizon 2,8 s) : ~8 fois moins de calcul |
| robot qui patine sur place pendant 10 min (odometrie qui avance, robot non) | non reproduit avec un robot seul ; lie a la saturation de la machine | detection de blocage par les cameras : pas 0,3 m en 60 s -> etape annulee, nouvel essai, puis abandon (`stuck_timeout_sec`) |
| robot3 attend longtemps au feu (robot1 garde le passage jusqu'a la fin de son etape) | passage libere seulement a la fin de l'etape | passage libere des que le robot a franchi le mur de 1,5 m (position cameras) |
| robot1 semble bloque sur le tableau de bord dans la zone ouest | le tableau affichait la pose AMCL, qui derive dans cette zone degagee | le tableau affiche la pose vue par les cameras quand elle existe |
| mission perdue au demarrage | Nav2 du robot pas encore actif : objectif refuse | mission remise en tete de file (5 fois au plus), pause de 10 s pour ce robot |

## Essais (3 robots, cameras, 25 min chacun)

| Essai | Corrections actives | Missions terminees (robot1 / robot2 / robot3) | Echecs | Contacts |
|---|---|---|---|---|
| 1 (15 min) | aucune | 1 (0 / 0 / 1) | 0 | 0 |
| 2 | allees libres, MPPI allege | 10 (2 / 7 / 1) | 0 | 0 |
| 3 | + feu de circulation | 9 (1 / 7 / 1) | 0 | 0 |
| 4 | + detection de blocage | 4 (1 / 2 / 1) | 0 | 0 |
| 5 (15 min) | + suivi des colis (tableau de bord) | 6 (1 / 4 / 1) | 0 | 0 |
| 6 (20 min) | + sol sans rebord | 1 (0 / 1 / 0) : controleur de R1 jamais active (demarrage Nav2 sature) | 6 | 0 |
| 7 (25 min) | + reservation du passage au dernier moment, demarrage echelonne 25 s, pause apres 2 echecs | **12 (3 / 6 / 3)** | 0 | 0 |

Lecture :

- Le flux complet fonctionne : production -> rack et rack -> quai, avec
  chargement, sans collision (ecart minimal entre robots 0,20 a 0,46 m) ;
  erreur de localisation mediane 0,05 a 0,10 m grace aux cameras.
- Le robot polyvalent prend la file la plus chargee (stockage pendant les pics
  de production).
- Le debit reste faible et variable : la simulation tourne a environ 0,2 fois
  le temps reel avec 3 robots (charge 35 a 55 sur 4 coeurs), et les missions
  de stockage traversent tout l'entrepot (ouest -> est). L'essai 4 a en plus
  un trou de 14 min dans les mesures (machine probablement en veille) : il n'a
  dure en realite qu'environ 18 min. Avec un seul robot, la simulation tourne
  presque en temps reel (production atteinte en 25 s).
- Il faut plusieurs essais par configuration, sur une machine plus puissante,
  pour comparer des debits.

## A traiter ensuite

- Objets importes de Gazebo Fuel absents de la carte : une personne debout a
  1 m de `station_A` et une autre a 1 m de `station_B`, une valise entre
  `delivery_1` et `delivery_2`. Les robots ne les voient qu'au laser.

Essai 7 : erreur de localisation mediane 0,08 m, 95e centile 0,20 m, ecart minimal entre robots 0,18 m.

Fichiers : `logistique_3robots_essai2/`, `_essai3/`, `_essai4/`, `_essai7/` (syntheses,
statuts des taches, journal logistique, charge machine).
