# Modèles retenus

Ces trois fichiers sont installés dans `share/warehouse_marl/models/` par
`colcon build`. Les launch files les utilisent par défaut.

| Fichier | Rôle | Paramètre de lancement | Provenance |
|---|---|---|---|
| `drl3_best.pt` | DRL v3 d'allocation (biais résiduel sur le consensus) | `drl_mode:=hybrid` (`obs_version:=v3`, par défaut) | `train_drl_v3 --tasks-from footwear`, graine 0, meilleur point de validation |
| `selected_route.pt` | `drl_route`, choix du chemin sur le graphe | `route_mode:=drl` | protocole v4, étape 1 : graine 1, t = 60 min, sélection sur la validation |
| `selected_idle.pt` | `drl_idle`, point d'attente d'un robot inoccupé | `idle_mode:=drl` | protocole v4, étape 2 : graine 0, t = 100 min, sélection sur la validation |

Empreintes SHA-256 :

```
48162c14529ab1885ae8b0b48b493d4f391113def94e52f8ee1a704f7ee36e81  drl3_best.pt
0ed55d1100ccd556abaf6080202bed4b8b5c177f48156c29a541eeb212f749bc  selected_route.pt
02712261399a14fd795b223e8e80a6ff80beb74d1040e4539d26ac67ce70dade  selected_idle.pt
```

`selected_route.pt` et `selected_idle.pt` sont identiques aux copies de
`doc/v4/entrainement_route/` et `doc/v4/entrainement_idle/`.
