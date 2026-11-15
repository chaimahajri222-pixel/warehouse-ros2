#!/usr/bin/env bash
# Test court de route_mode sur un domaine ROS isole (protocole v4, etape 3).
# Usage : test_route_mode_ros.sh <dijkstra|drl> [modele.pt] [rack_cible]
set +u
MODE=${1:-dijkstra}; MODEL=${2:-}; TARGET=${3:-shelf_4_2}
PY=${PY:-${VENV:-$HOME/warehouse_ws/.venv}/bin/python}   # python avec torch (mode drl)
HERE=$(cd "$(dirname "$0")/.." && pwd)
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-87}
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export PYTHONPATH="$HERE:${PYTHONPATH:-}"
LOG=$(mktemp)
EXTRA=(); [ -n "$MODEL" ] && EXTRA=(-p route_model:="$MODEL")
"$PY" -m warehouse_marl.mission_executor_node --ros-args \
  -p robot_names:="['robot1']" -p route_mode:=$MODE "${EXTRA[@]}" \
  -p robot_start_nodes:="['charging_dock']" -p pause_exploration:=false >"$LOG" 2>&1 &
PID=$!
"$PY" "$HERE/scripts/test_route_mode_ros.py" "$TARGET"; RC=$?
kill $PID 2>/dev/null; wait $PID 2>/dev/null
echo "--- journal du noeud ($MODE) ---"; grep -v "^$" "$LOG" | tail -8; rm -f "$LOG"
exit $RC
