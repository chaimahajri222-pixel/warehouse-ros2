# Diagnostics des modèles `drl_idle6` retenus (petit et grand)

Ces diagnostics portent sur les deux modèles déjà retenus :
- **petit** : graine 0, t = 40 min ;
- **grand** : graine 1, t = 30 min.

Ils utilisent **uniquement les scénarios de validation** v6 :
- petit : 18 scénarios (15 et 40 racks) ;
- grand : 12 scénarios (150 racks / 20 robots).

Il n'y a **ni réentraînement ni graine de test**. Le script est
`src/warehouse_marl/scripts/diagnostics_v6.py` :

```
python diagnostics_v6.py --drl-dir ~/warehouse_ws/drl_v6 --out ~/warehouse_ws/resultats_v6/diagnostics
```

Les modèles sont rejoués sans exploration (ε = 0), chacun avec **sa** règle de
récompense d'entraînement (écarts 4 et 5 de `PROTOCOLE_V6.md`) :
- **petit** : récompense individuelle, −approche / T_ref, avec 0 si aucune
  tâche ne suit la décision ;
- **grand** : récompense d'équipe, −(somme des approches de toutes les tâches
  attribuées dans la fenêtre) / (R × T_ref). La dernière décision de chaque
  robot est tronquée.

T_ref = diamètre / vitesse moyenne. Il vaut 45,4 s ou 70,0 s pour le petit
modèle (15 et 40 racks) et 147,0 s pour le grand (colonne `t_ref_s` de
`decisions_petit.csv` et `decisions_grand.csv`).

**Vérification du rejeu.** Pour les **30 scénarios sur 30**, le temps de
traitement moyen rejoué est identique à celui du journal de validation du point
retenu (`verification_validation.csv`, l.2 à 31, colonne `identique`). Le rejeu
est donc fidèle.

Les sources se lisent ainsi : « fichier l.N » désigne la N-ième ligne du fichier
CSV de ce dossier, la ligne 1 étant l'en-tête.

## 1. Accord avec la couverture seule (`fig_diag_accord_v6.png`)

Pour chaque décision d'attente, on compare le nœud choisi par `drl_idle6` au nœud
que la couverture seule choisirait **dans le même état**. Le second est le
candidat marqué `est_couverture`, c'est-à-dire le choix avec f_θ = 0. Les
trajectoires sont celles du DRL. La matrice 2 × 2 croise « reste sur place / se
déplace » pour la couverture et pour le DRL. La case « les deux se déplacent »
indique en plus combien de déplacements vont vers un **autre** nœud.

| Modèle | Décisions | Couv. reste / DRL reste | Couv. reste / DRL bouge | Couv. bouge / DRL reste | Couv. bouge / DRL bouge (dont autre nœud) | **Décisions modifiées** | Source |
|---|---|---|---|---|---|---|---|
| petit | 737 | 105 | 8 | 246 | 378 (111) | **365 (49,53 %)** | `accord.csv` l.2 |
| grand | 940 | 21 | 3 | 418 | 498 (420) | **841 (89,47 %)** | `accord.csv` l.3 |

**Lecture.**
- **Le DRL s'écarte massivement de la couverture.** Le petit modèle change une
  décision sur deux, le grand près de 9 sur 10.
- **Écart dominant :** la couverture enverrait le robot ailleurs, mais le DRL le
  laisse sur place. C'est le cas de 246 décisions (33,4 %) pour le petit modèle
  et de 418 (44,5 %) pour le grand.
- **Pour le grand modèle,** 420 décisions vont aussi vers un autre nœud que
  celui de la couverture.
- **Effet en test :** à 150 racks, ces changements ne donnent que −0,66 s contre
  la couverture, ce qui n'est pas significatif (`../principal_idle6.csv` l.15).

## 2. Calibration de Q (`fig_diag_calibration_v6.png`)

On trace Q prédit au nœud choisi contre la valeur observée, en nuage de points.
On ajoute, pour chaque décile de Q, la médiane et l'IQR 25-75 % de la valeur
observée (`calibration_bins.csv`). Il y a deux cibles :
- **Coût observé jusqu'à la décision suivante,** c'est-à-dire la récompense d'un
  pas, exactement celle vue à l'entraînement. C'est la cible demandée. Q estime
  pourtant un retour **cumulé et escompté**, et non un seul pas. Il ne doit donc
  pas se trouver sur la diagonale ; on ne la trace pas.
- **Retour escompté observé,** Σ γᵏ r, avec γ = 0,9, le long des décisions
  suivantes du même robot, **tronqué à la fin de l'épisode** comme à
  l'entraînement. C'est la grandeur que Q est censé estimer, d'où la diagonale
  Q = observé.

| Modèle | Cible | Décisions | Sans valeur (tronquées) | Spearman (Q, observé) | Biais moyen (Q − observé) | Q moyen | Observé moyen | Source |
|---|---|---|---|---|---|---|---|---|
| petit | récompense d'un pas | 737 | 0 | 0,1723 | −0,42972 | −0,57119 | −0,14147 | `calibration_resume.csv` l.2 |
| petit | retour escompté | 737 | 0 | 0,2225 | +0,05906 | −0,57119 | −0,63025 | `calibration_resume.csv` l.3 |
| grand | récompense d'un pas | 700 | 240 | 0,6267 | −0,34670 | −0,44548 | −0,09878 | `calibration_resume.csv` l.4 |
| grand | retour escompté | 700 | 240 | 0,5591 | −0,27522 | −0,44548 | −0,17027 | `calibration_resume.csv` l.5 |

Les valeurs sont en unités de récompense. Pour le petit modèle, multiplier par
T_ref donne des secondes d'approche.

**Lecture.**
- **Petit modèle : calibré en moyenne, mais peu discriminant.**
  - Le biais moyen sur le retour escompté est faible (+0,059).
  - La corrélation de rang est faible (Spearman 0,22).
  - La médiane du retour observé reste entre −0,84 et −0,41 sur tous les déciles
    de Q (`calibration_bins.csv` l.12 à 21), avec un IQR large.
  - Q ordonne donc mal les décisions d'après leur coût réel.
  - 289 récompenses sur 737 valent 0 (`decisions_petit.csv`, colonne
    `recompense`) :
    - 56 viennent de la règle « 0 si aucune tâche ne suit » en fin d'épisode
      (`terminale` = True) ;
    - les 233 autres sont des approches réellement nulles, quand le robot
      attendait déjà au rack de sa tâche suivante.
- **Grand modèle : bien ordonné, mais pessimiste.**
  - Q est mieux ordonné (Spearman 0,56 à 0,63). La médiane du retour observé
    croît avec Q de −0,278 à −0,063, avec une seule baisse, de −0,089 à −0,095,
    entre `calibration_bins.csv` l.39 et l.40 (ensemble : l.32 à 41).
  - Q est **systématiquement plus pessimiste** que le retour observé : biais de
    −0,275.
  - **Cause principale probable :** la troncature. Avec 150 tâches et 20 robots,
    un robot ne prend qu'environ 4 décisions d'attente par épisode (médiane 4,
    maximum 8). Le retour observé s'arrête donc tôt, alors que Q, appris par
    bootstrap, estime un retour sans fin d'épisode.
  - Les 240 décisions « sans valeur » sont les dernières décisions de chaque
    robot (20 robots × 12 scénarios), tronquées par construction (écart 4).
- **Les deux groupes de Q du grand modèle,** visibles sur la figure :
  - le groupe à Q < −0,47 réunit exactement les **240 décisions prises à t = 0**
    par les 20 robots qui partent des stations ou du dépôt (dispersion
    initiale) ;
  - le second groupe réunit les 700 décisions suivantes.

  Filtre appliqué : `q_choisi` < −0,47 dans `decisions_grand.csv`.

## 3. Correction apprise f_θ (`fig_diag_correction_v6.png`)

f_θ = Q − terme a priori de couverture x[0], au nœud choisi. C'est exactement la
sortie du réseau, puisque Q = x[0] + f_θ.

| Modèle | Grandeur | n | Moyenne | Médiane | Écart-type | p05 | p95 | Min | Max | Part > 0 | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| petit | f_θ au nœud choisi | 737 | −0,45507 | −0,46664 | 0,09805 | −0,63799 | −0,29485 | −0,75718 | −0,04050 | 0,00 % | `correction_resume.csv` l.4 |
| grand | f_θ au nœud choisi | 940 | −0,37273 | −0,34562 | 0,06480 | −0,51663 | −0,32031 | −0,52963 | −0,17670 | 0,00 % | `correction_resume.csv` l.5 |
| petit | f_θ(choisi) − f_θ(couverture) | 737 | 0,04940 | 0,00000 | 0,07510 | 0,00000 | 0,23327 | 0,00000 | 0,36376 | 49,53 % | `correction_resume.csv` l.2 |
| grand | f_θ(choisi) − f_θ(couverture) | 940 | 0,01715 | 0,01505 | 0,01707 | 0,00000 | 0,03871 | 0,00000 | 0,13667 | 89,47 % | `correction_resume.csv` l.3 |

**Lecture.**
- **f_θ au nœud choisi est toujours négative** (aucune valeur > 0). Ce n'est pas
  une préférence : c'est surtout un **décalage commun** à tous les candidats. Q
  doit atteindre le niveau d'un retour cumulé, de −0,45 à −0,57 en moyenne,
  alors que le terme a priori n'est qu'une distance normalisée. Celui-ci vaut en
  moyenne 0,116 (petit) et 0,063 (grand) en valeur absolue au nœud choisi
  (`correction_resume.csv` l.4 et 5, colonne `abs_moyen_prior_choisi`). Ce
  décalage ne change pas le nœud choisi.
- **Ce qui fait dévier de la couverture,** c'est l'écart de correction entre le
  nœud choisi et celui de la couverture (deuxième rangée de la figure).
  - Il est nul exactement quand le DRL suit la couverture. Sa part strictement
    positive (49,53 % et 89,47 %) est donc égale à la part de décisions
    modifiées de la section 1.
  - **Petit modèle :** l'écart est tantôt nul, tantôt grand (p95 0,233).
  - **Grand modèle :** l'écart est petit mais presque toujours positif (médiane
    0,015, p95 0,039). Les différences de couverture entre les candidats à
    150 racks sont donc minimes, et une petite correction suffit à changer de
    nœud. C'est cohérent avec les 89 % de décisions modifiées pour un effet de
    test non significatif.

## Fichiers

| Fichier | Contenu |
|---|---|
| `decisions_petit.csv`, `decisions_grand.csv` | une ligne par décision d'attente : scénario, robot, instant, nœuds DRL et couverture, Q, terme a priori, f_θ, récompense, retour escompté |
| `verification_validation.csv` | rejeu contre journal de validation, par scénario |
| `accord.csv` | matrices 2 × 2 et pourcentage de décisions modifiées |
| `calibration_bins.csv`, `calibration_resume.csv` | médiane et IQR par décile de Q ; corrélation, biais |
| `correction_resume.csv` | statistiques de f_θ et de l'écart de correction |
| `fig_diag_accord_v6.png`, `fig_diag_calibration_v6.png`, `fig_diag_correction_v6.png` | les 3 figures |
