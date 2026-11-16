#!/usr/bin/env bash
# Experience b de README_SIMULATION.md (3 robots) : idle_mode:=stay puis
# idle_mode:=drl (modele drl_idle v4 installe), mode heuristic, 900 s chacun.
# Attend la fin de la mesure a_3robots. Meme securite thermique (88 C).
#   setsid nohup bash lancer_mesure_idle_3robots.sh > journal_mesure_idle.txt 2>&1 &
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
# attendre la fin de la mesure a (et un PC refroidi sous 60 C)
until grep -q "\] fin" "$WS/mesures/journal_mesure.txt" 2>/dev/null; do sleep 30; done
if grep -q "ARRET THERMIQUE" "$WS/mesures/a_3robots/temperature.log" 2>/dev/null; then
  echo "[$(date '+%F %T')] mesure a arretee pour surchauffe : experience b NON lancee"; exit 1
fi
until [ "$(temp_cpu)" -lt 60 ]; do sleep 30; done
for IDLE in stay drl; do
  OUT=$WS/mesures/b_idle_$IDLE
  mkdir -p "$OUT"
  echo "[$(date '+%F %T')] debut idle_mode:=$IDLE, $(free -m | awk '/Mem/{print $7}') Mo libres, $(temp_cpu) C"
  VENV=$HOME/.venvs/mappo_warehouse ROBOTS=3 MODES=heuristic LAUNCH_ARGS="idle_mode:=$IDLE" \
    setsid bash "$SCRIPTS/mesures_gazebo.sh" 900 "" "$OUT" &
  MPID=$!
  arret=0
  while kill -0 "$MPID" 2>/dev/null; do
    t=$(temp_cpu)
    echo "$(date +%T) temperature ${t} C, $(free -m | awk '/Mem/{print $7}') Mo libres, charge $(cut -d' ' -f1 /proc/loadavg)" >> "$OUT/temperature.log"
    if [ "$t" -ge "$TEMP_MAX" ]; then
      echo "[$(date '+%F %T')] ARRET THERMIQUE : ${t} C >= ${TEMP_MAX} C" | tee -a "$OUT/temperature.log"
      kill -TERM -- -"$MPID" 2>/dev/null
      bash "$KILL_SIM" -y >/dev/null 2>&1
      pkill -TERM -f 'warehouse_marl/lib/warehouse_marl/' 2>/dev/null
      arret=1
      break
    fi
    sleep 30
  done
  wait "$MPID" 2>/dev/null
  echo "[$(date '+%F %T')] fin idle_mode:=$IDLE, $(temp_cpu) C"
  [ "$arret" = 1 ] && exit 1
  until [ "$(temp_cpu)" -lt 60 ]; do sleep 30; done
done
echo "[$(date '+%F %T')] experience b terminee"
