#!/usr/bin/env bash
# entrainer_v6.sh KIND BUDGET_MIN [GRAINES...]
# Entraine les graines L'UNE APRES L'AUTRE (un seul entrainement a la fois,
# PROTOCOLE_V6.md section 5). Si un processus s'arrete anormalement (crash,
# memoire), la meme graine est relancee et REPREND depuis sa derniere
# sauvegarde (etat_seed<k>.pt), au plus 3 fois.
# A lancer detache :  setsid nohup bash entrainer_v6.sh idle6 90 0 1 2 > log 2>&1 &
set -u
KIND=$1
BUDGET=$2
shift 2
SEEDS=${*:-0 1 2}
PY=${PY:-$HOME/.venvs/mappo_warehouse/bin/python}
SRC=${SRC:-$HOME/warehouse_ws/src/warehouse-ros2/src/warehouse_marl}
OUT=${OUT:-$HOME/warehouse_ws/drl_v6/$KIND}
TRAIN_EVERY=${TRAIN_EVERY:-1}
mkdir -p "$OUT"
for s in $SEEDS; do
  for essai in 1 2 3 4; do
    echo "[$(date '+%F %T')] $KIND graine $s, lancement $essai"
    PYTHONPATH="$SRC" "$PY" -u -m warehouse_marl.drl.train_v6 --kind "$KIND" --seed "$s" \
      --budget-min "$BUDGET" --threads 2 --train-every "$TRAIN_EVERY" --taille "${TAILLE:-tous}" \
      --out-dir "$OUT"
    rc=$?
    echo "[$(date '+%F %T')] $KIND graine $s, code de sortie $rc"
    [ -f "$OUT/fini_seed$s.txt" ] && break
    sleep 20
  done
done
echo "[$(date '+%F %T')] $KIND : toutes les graines terminees"
