#!/usr/bin/env bash
# mesures_gazebo.sh : mesures du systeme complet (Gazebo headless + Nav2 + MARL)
# en deux modes successifs : drl_mode heuristic, puis hybrid (modele DRL v3).
#
#   bash mesures_gazebo.sh [DUREE_S=900] [MODELE_V3] [DOSSIER_SORTIE]
#
# Variables : ROS_DOMAIN_ID (defaut 83, domaine dedie), WS (~/warehouse_ws),
#             ROBOTS (3), MIN_FREE_MB (3000 : pas de lancement en dessous).
# Sorties (DOSSIER_SORTIE, defaut ~/warehouse_ws/mesures_gazebo) :
#   taches_<mode>.csv (task_metrics_logger), rfid_<mode>.csv
#   (rfid_metrics_logger), launch_<mode>.log, ressources_<mode>.log
#   (memoire libre et charge toutes les 30 s), synthese_taches.csv.
set -u
set -m                                   # jobs en arriere-plan : SIGINT transmis
DUREE=${1:-900}
MODELE=${2:-$HOME/warehouse_ws/drl_v3_footwear/drl3_best.pt}
OUT=${3:-$HOME/warehouse_ws/mesures_gazebo}
WS=${WS:-$HOME/warehouse_ws}
ROBOTS=${ROBOTS:-3}
MIN_FREE_MB=${MIN_FREE_MB:-3000}
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-83}
KILL_SIM=$WS/src/warehouse-ros2/src/rosnav/src/rosnav_bot/scripts/kill_rosnav_sim.sh
source /opt/ros/jazzy/setup.bash
source "$WS/install/setup.bash" 2>/dev/null
mkdir -p "$OUT"

nettoyage() {   # uniquement les processus de CE domaine
  bash "$KILL_SIM" -y >/dev/null 2>&1 || true
  for pid in $(pgrep -f 'warehouse_marl/lib/warehouse_marl/'); do
    dom=$(tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | sed -n 's/^ROS_DOMAIN_ID=//p')
    [ "$dom" = "$ROS_DOMAIN_ID" ] && kill -TERM "$pid" 2>/dev/null
  done
  sleep 3
}

run_mode() {
  local mode=$1; shift
  local libre
  libre=$(free -m | awk '/Mem/{print $7}')
  if [ "$libre" -lt "$MIN_FREE_MB" ]; then
    echo "[$mode] NON LANCE : ${libre} Mo libres < ${MIN_FREE_MB} Mo." | tee "$OUT/ressources_$mode.log"
    return 1
  fi
  nettoyage
  echo "[$mode] demarrage $(date +%T), ${libre} Mo libres, domaine $ROS_DOMAIN_ID"
  ros2 launch warehouse_marl warehouse_full.launch.py robot_count:="$ROBOTS" headless:=true \
      rviz:=false dashboard:=false drl_mode:="$mode" "$@" > "$OUT/launch_$mode.log" 2>&1 &
  local lpid=$!
  ros2 run warehouse_marl task_metrics_logger --ros-args -p output:="$OUT/taches_$mode.csv" \
      -p mode_label:="$mode" > "$OUT/logger_$mode.log" 2>&1 &
  local tpid=$!
  ros2 run warehouse_marl rfid_metrics_logger --ros-args -p output:="$OUT/rfid_$mode.csv" \
      > "$OUT/rfid_logger_$mode.log" 2>&1 &
  local rpid=$!
  local fin=$((SECONDS + DUREE))
  while [ $SECONDS -lt $fin ]; do
    echo "$(date +%T) $(free -m | awk '/Mem/{print $7}') Mo libres, charge $(cut -d' ' -f1 /proc/loadavg)" >> "$OUT/ressources_$mode.log"
    if ! kill -0 "$lpid" 2>/dev/null; then
      echo "$(date +%T) ARRET PREMATURE du launch" >> "$OUT/ressources_$mode.log"; break
    fi
    sleep 30
  done
  kill -INT "$tpid" "$rpid" 2>/dev/null
  kill -INT "$lpid" 2>/dev/null; sleep 20; kill -TERM "$lpid" 2>/dev/null
  nettoyage
  echo "[$mode] fin $(date +%T)"
}

run_mode heuristic
run_mode hybrid obs_version:=v3 model_path:="$MODELE"
FICHIERS=$(ls "$OUT"/taches_*.csv 2>/dev/null)
if [ -n "$FICHIERS" ]; then
  ros2 run warehouse_marl summarize_task_metrics $FICHIERS --out "$OUT/synthese_taches.csv"
else
  echo "Aucun CSV de taches : rien a synthetiser."
fi
