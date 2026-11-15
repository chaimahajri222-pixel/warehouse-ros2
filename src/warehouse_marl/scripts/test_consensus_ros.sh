#!/usr/bin/env bash
# Tests courts du consensus sur un domaine ROS isole, sans Gazebo ni Nav2.
#   test_consensus_ros.sh pertes <msg_loss> <graine> [n_taches=30] [periode_s=1.5]
#   test_consensus_ros.sh blocage
# Sortie : JSON du harnais, puis les compteurs extraits des journaux des noeuds.
set +u
MODE=${1:-pertes}
PY=${PY:-${VENV:-$HOME/warehouse_ws/.venv}/bin/python}   # python avec torch (mode drl)
HERE=$(cd "$(dirname "$0")/.." && pwd)
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-89}
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export PYTHONPATH="$HERE:${PYTHONPATH:-}"
TMP=$(mktemp -d)
PIDS=()
if [ "$MODE" = pertes ]; then
  LOSS=${2:-0.0}; SEED=${3:-1}; N=${4:-30}; PERIOD=${5:-1.5}
  for r in robot1 robot2 robot3; do
    "$PY" -m warehouse_marl.consensus_node --ros-args -r __node:=consensus_$r \
      -p robot_id:=$r -p msg_loss:=$LOSS -p msg_loss_seed:=$SEED >"$TMP/$r.log" 2>&1 &
    PIDS+=($!)
  done
  "$PY" -m warehouse_marl.mission_executor_node --ros-args \
    -p robot_names:="['robot1','robot2','robot3']" -p pause_exploration:=false \
    -p block_after_failures:=0 >"$TMP/executor.log" 2>&1 &
  PIDS+=($!)
  "$PY" "$HERE/scripts/test_consensus_ros.py" pertes "$N" "$PERIOD" "$SEED" \
    "msg_loss=$LOSS graine=$SEED"; RC=$?
else
  "$PY" -m warehouse_marl.graph_publisher_node --ros-args \
    -p robot_names:="['robot1','robot2']" >"$TMP/graph.log" 2>&1 &
  PIDS+=($!)
  for r in robot1 robot2; do
    "$PY" -m warehouse_marl.consensus_node --ros-args -r __node:=consensus_$r \
      -p robot_id:=$r >"$TMP/$r.log" 2>&1 &
    PIDS+=($!)
  done
  "$PY" "$HERE/scripts/test_consensus_ros.py" blocage; RC=$?
fi
kill "${PIDS[@]}" 2>/dev/null; wait "${PIDS[@]}" 2>/dev/null
for f in "$TMP"/robot*.log; do
  r=$(basename "$f" .log)
  echo "$r : pertes simulees $(grep -c 'perte simulee' "$f"), retraits sur conflit $(grep -c 'conflit sur' "$f"), victoires $(grep -c 'GAGNE' "$f"), dernier compteur : $(grep -o '([0-9]*/[0-9]*)' "$f" | tail -1)"
done
[ -f "$TMP/executor.log" ] && echo "executeur : $(grep -c 'revendications, retenu' "$TMP/executor.log") taches avec plusieurs revendications"
[ -f "$TMP/graph.log" ] && grep -E 'Arete' "$TMP/graph.log" | sed 's/^/graph_publisher : /'
grep -h -E 'Traceback|Error' "$TMP"/*.log | head -5
[ -n "$KEEP" ] && echo "journaux : $TMP" || rm -rf "$TMP"
echo "RC=$RC"
exit $RC
