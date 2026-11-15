# Bilan v5

Trois ajouts dans ROS 2, testés sur des domaines ROS isolés, **sans Gazebo** : les
robots sont simulés par des TF statiques et de faux serveurs Nav2. Ces tests
vérifient le fonctionnement ; ils ne mesurent **pas** les performances.

1. **`idle_mode:=stay|centre|drl`** (`mission_executor_node`, commit 11ce9a3).
   Quand un robot devient inoccupé, il choisit son point d'attente avec le modèle
   `drl_idle` retenu (graine 0, t = 100 min), puis s'y rend par `NavigateToPose`.
   Ce trajet est annulé dès qu'une mission arrive pour ce robot.
   - La décision est identique à celle du banc v4 dans tous les états testés
     (`test/test_idle_planner.py`).
   - Le test fonctionnel réussit dans les 4 cas (`test_ros_idle_mode.txt`).
   - Dans le scénario de base, `drl` laisse le robot sur place (il est déjà dans
     la zone de demande). Le trajet et son annulation ne sont donc exercés avec
     `drl` que dans la variante où le robot part du dépôt.
   - Limites : la demande est estimée en ligne dans ROS (pas d'historique
     train_fit) ; après un trajet interrompu, la position du robot sur le graphe
     reste le dernier nœud atteint.
2. **`msg_loss`** (`consensus_node`, commit 55aecbd).
   - À 0 % comme à 50 % de pertes d'enchères (3 graines × 30 tâches), toutes les
     tâches ont été attribuées une seule fois et aucune n'a été exécutée deux fois
     (`pertes_essais.csv`).
   - À 50 %, 60 à 68 enchères ont été perdues par essai, ce qui a produit
     2 conflits, tous résolus par le retrait du robot perdant.
   - Un essai préliminaire sans perte a laissé une tâche non attribuée ; il n'a
     pas été reproduit et sa cause n'est pas identifiée
     (`note_essais_preliminaires_pertes.md`).
3. **Blocage d'allée en direct** (commit 288ea95), 3 répétitions sur 3 réussies
   (`test_ros_blocage.txt`) :
   - un blocage publié sur `/warehouse/blocked_edges` apparaît dans
     `/warehouse/graph_state` ;
   - l'enchère de robot1 passe de 7,0 à 13,1 (détour) ;
   - robot1 isolé n'enchérit plus, et robot2 gagne ;
   - après déblocage, l'enchère revient à 7,0.

**Ce qui reste partiel :**
- aucun de ces trois tests n'a été fait dans Gazebo ;
- le retard de messages n'est pas injecté dans ROS ;
- les pertes ne touchent que les enchères ;
- le gain de `drl_idle` n'a été mesuré que dans le banc (v4), pas dans ROS.
