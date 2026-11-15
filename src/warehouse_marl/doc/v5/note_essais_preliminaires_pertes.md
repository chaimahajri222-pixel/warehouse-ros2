# Essais préliminaires du test msg_loss (avant la série de `test_ros_pertes.txt`)

Mise au point du harnais, 10 tâches, `msg_loss=0.0`, graine 1 :

| Essai | Résultat |
|---|---|
| 1 | **Échec** : 9 tâches sur 10 attribuées une fois ; 1 tâche jamais attribuée en 120 s ; 0 conflit, 0 exécution multiple. Journaux des nœuds non conservés (le script les supprimait à ce moment-là), cause non identifiée. |
| 2 à 7 | Réussite (10/10 attribuées une seule fois). Journaux conservés pour les essais 3 à 7 (option `KEEP=1`), sans nouvel échec. |

Ce blocage intermittent d'une tâche, sans perte de messages, n'a pas été reproduit
dans les 6 essais suivants ni dans la série de 6 × 30 tâches. On le rapporte quand
même : la propriété « toute tâche finit par être attribuée » n'est pas démontrée,
seulement observée pour 249 tâches sur 250 (série : 180/180 ; essais préliminaires : 69/70).
