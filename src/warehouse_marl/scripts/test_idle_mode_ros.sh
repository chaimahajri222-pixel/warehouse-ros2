#!/usr/bin/env bash
# Test court de idle_mode sur un domaine ROS isole (sans Gazebo ni Nav2).
# Usage : test_idle_mode_ros.sh <stay|centre|drl> [modele_idle.pt] [cible_t0]
set +u
MODE=${1:-stay}; MODEL=${2:-}; T0=${3:-shelf_4_2}
PY=${PY:-${VENV:-$HOME/warehouse_ws/.venv}/bin/python}   # python avec torch (mode drl)
HERE=$(cd "$(dirname "$0")/.." && pwd)
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-88}
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export PYTHONPATH="$HERE:${PYTHONPATH:-}"
LOG=$(mktemp)
EXTRA=(); [ -n "$MODEL" ] && EXTRA=(-p idle_model:="$MODEL")
"$PY" -m warehouse_marl.mission_executor_node --ros-args \
  -p robot_names:="['robot1']" -p idle_mode:=$MODE "${EXTRA[@]}" \
  -p robot_start_nodes:="['charging_dock']" -p pause_exploration:=false \
  -p block_after_failures:=0 >"$LOG" 2>&1 &
PID=$!
"$PY" "$HERE/scripts/test_idle_mode_ros.py" "$MODE" "$T0"; RC=$?
kill $PID 2>/dev/null; wait $PID 2>/dev/null
echo "--- journal du noeud ($MODE) ---"; grep -v "^$" "$LOG" | tail -14; rm -f "$LOG"
echo "RC=$RC"
exit $RC
