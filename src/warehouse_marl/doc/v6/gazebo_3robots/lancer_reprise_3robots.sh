#!/usr/bin/env bash
# Reprise des mesures Gazebo a 3 robots, STRICTEMENT l'une apres l'autre :
#   1) hybrid (la 1re execution hybrid etait faussee : processus Nav2 de
#      l'execution heuristic encore actifs, carte jamais recue) ;
#   2) idle_mode:=stay (mode heuristic) ;  3) idle_mode:=drl (mode heuristic).
# Avant chaque mesure : >= 3000 Mo libres et < 60 C. Securite : arret a 88 C.
#   setsid nohup bash lancer_reprise_3robots.sh > journal_reprise.txt 2>&1 &
set +u
WS=$HOME/warehouse_ws
TEMP_MAX=${TEMP_MAX:-88}
SCRIPTS=$WS/src/warehouse-ros2/src/warehouse_marl/scripts
KILL_SIM=$WS/src/warehouse-ros2/src/rosnav/src/rosnav_bot/scripts/kill_rosnav_sim.sh
temp_cpu() {
  local t=0 v
  for z in /sys/class/thermal/thermal_zone*; do
    case $(cat "$z/type") in x86_pkg_temp|acpitz|B0D4)
      v=$(( $(cat "$z/temp") / 1000 )); [ "$v" -gt "$t" ] && t=$v ;;
    esac
  done
  echo "$t"
}
libre() { free -m | awk '/Mem/{print $7}'; }

mesure() {   # mesure <dossier> <MODES> <LAUNCH_ARGS>
  local OUT=$1 MODES=$2 ARGS=$3 attente=0
  mkdir -p "$OUT"
  until [ "$(temp_cpu)" -lt 60 ] && [ "$(libre)" -ge 3000 ]; do
    sleep 30; attente=$((attente + 30))
    if [ "$attente" -ge 900 ]; then
      echo "[$(date '+%F %T')] $OUT NON LANCE : $(libre) Mo libres, $(temp_cpu) C apres 15 min d'attente"
      return 1
    fi
  done
  echo "[$(date '+%F %T')] debut $OUT (modes=$MODES args=$ARGS), $(libre) Mo libres, $(temp_cpu) C"
  VENV=$HOME/.venvs/mappo_warehouse ROBOTS=3 MODES="$MODES" LAUNCH_ARGS="$ARGS" \
    setsid bash "$SCRIPTS/mesures_gazebo.sh" 900 "" "$OUT" &
  local MPID=$!
  while kill -0 "$MPID" 2>/dev/null; do
    local t; t=$(temp_cpu)
    echo "$(date +%T) temperature ${t} C, $(libre) Mo libres, charge $(cut -d' ' -f1 /proc/loadavg)" >> "$OUT/temperature.log"
    if [ "$t" -ge "$TEMP_MAX" ]; then
      echo "[$(date '+%F %T')] ARRET THERMIQUE : ${t} C >= ${TEMP_MAX} C" | tee -a "$OUT/temperature.log"
      kill -TERM -- -"$MPID" 2>/dev/null
      ROS_DOMAIN_ID=83 bash "$KILL_SIM" -y >/dev/null 2>&1
      return 2
    fi
    sleep 30
  done
  wait "$MPID" 2>/dev/null
  echo "[$(date '+%F %T')] fin $OUT, $(libre) Mo libres, $(temp_cpu) C"
}

mesure "$WS/mesures/a_3robots_hybrid_reprise" "hybrid" "" ; [ $? = 2 ] && exit 2
mesure "$WS/mesures/b_idle_stay" "heuristic" "idle_mode:=stay" ; [ $? = 2 ] && exit 2
mesure "$WS/mesures/b_idle_drl" "heuristic" "idle_mode:=drl" ; [ $? = 2 ] && exit 2
echo "[$(date '+%F %T')] reprise terminee"
