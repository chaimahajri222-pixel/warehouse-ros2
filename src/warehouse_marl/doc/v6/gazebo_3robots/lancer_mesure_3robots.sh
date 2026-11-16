#!/usr/bin/env bash
# Mesure Gazebo a 3 robots (README_SIMULATION.md, experience a, 3 robots
# seulement) sur ce PC, avec une securite thermique : si le processeur depasse
# TEMP_MAX (88 C), toute la simulation est arretee.
#   setsid nohup bash lancer_mesure_3robots.sh > journal_mesure.txt 2>&1 &
set +u
WS=$HOME/warehouse_ws
OUT=$WS/mesures/a_3robots
TEMP_MAX=${TEMP_MAX:-88}
SCRIPTS=$WS/src/warehouse-ros2/src/warehouse_marl/scripts
KILL_SIM=$WS/src/warehouse-ros2/src/rosnav/src/rosnav_bot/scripts/kill_rosnav_sim.sh
mkdir -p "$OUT"
temp_cpu() {   # temperature max des zones x86_pkg_temp / processeur, en C
  local t=0 v
  for z in /sys/class/thermal/thermal_zone*; do
    case $(cat "$z/type") in x86_pkg_temp|acpitz|B0D4)
      v=$(( $(cat "$z/temp") / 1000 )); [ "$v" -gt "$t" ] && t=$v ;;
    esac
  done
  echo "$t"
}
echo "[$(date '+%F %T')] debut, $(free -m | awk '/Mem/{print $7}') Mo libres, $(temp_cpu) C"
VENV=$HOME/.venvs/mappo_warehouse ROBOTS=3 setsid bash "$SCRIPTS/mesures_gazebo.sh" 900 "" "$OUT" &
MPID=$!
while kill -0 "$MPID" 2>/dev/null; do
  t=$(temp_cpu)
  echo "$(date +%T) temperature ${t} C, $(free -m | awk '/Mem/{print $7}') Mo libres, charge $(cut -d' ' -f1 /proc/loadavg)" >> "$OUT/temperature.log"
  if [ "$t" -ge "$TEMP_MAX" ]; then
    echo "[$(date '+%F %T')] ARRET THERMIQUE : ${t} C >= ${TEMP_MAX} C" | tee -a "$OUT/temperature.log"
    kill -TERM -- -"$MPID" 2>/dev/null
    bash "$KILL_SIM" -y >/dev/null 2>&1
    pkill -TERM -f 'warehouse_marl/lib/warehouse_marl/' 2>/dev/null
    break
  fi
  sleep 30
done
wait "$MPID" 2>/dev/null
echo "[$(date '+%F %T')] fin, $(temp_cpu) C"
