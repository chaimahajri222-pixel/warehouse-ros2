### A. Localisation : erreur de position estimee / reelle (m)

| | AMCL seul | AMCL + cameras |
|---|---|---|
| flotte, moyenne | 0.35 | 0.15 |
| flotte, mediane | 0.13 | 0.10 |
| flotte, 95e centile | 1.68 | 0.48 |
| flotte, maximum | 3.13 | 1.12 |
| robot1, mediane / max | 0.13 / 0.18 | 0.12 / 0.80 |
| robot2, mediane / max | 0.14 / 1.26 | 0.10 / 1.12 |
| robot3, mediane / max | 0.17 / 3.13 | 0.09 / 0.74 |
| lacet, mediane (deg), flotte | 1.4 | 0.9 |

### B. Navigation : contacts entre robots (poses Gazebo)

| | AMCL seul | AMCL + cameras |
|---|---|---|
| contacts (ecart <= 2 cm) | 0 | 0 |
| quasi-contacts (2-15 cm) | 0 | 0 |
| ecart minimal robot1-robot2 (m) | 0.39 | 0.40 |
| ecart minimal robot1-robot3 (m) | 0.75 | 0.20 |
| ecart minimal robot2-robot3 (m) | 0.38 | 0.36 |

### C. Taches

| | AMCL seul | AMCL + cameras |
|---|---|---|
| creees | 13 | 15 |
| reussies | 7 | 9 |
| echouees | 1 | 0 |
| annulees | 0 | 0 |
| non terminees a la fin | 3 | 3 |
| reussies par robot | 1:1, 2:3, 3:3 | 1:3, 2:4, 3:2 |

### Corrections envoyees par les cameras

| | AMCL seul | AMCL + cameras |
|---|---|---|
| nombre | 0 | 49 |
| par motif | - | derive 36, fin 10, initialisation 3 |
| ecart corrige, mediane / max (m) | - / - | 0.42 / 0.95 |
| duree mesuree (s, horloge murale) | 1081 | 1081 |
