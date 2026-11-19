#!/usr/bin/env bash
# mesures_cameras.sh : effet du module de localisation par cameras
# (camera_localization_node, d'apres Yumbla et al., IEEE Access 2025).
# Deux executions successives, meme carte connue (explore:=false) :
#   sans    : AMCL seul (comme avant) ;
#   cameras : camera_localization:=true (correction AMCL + poses externes
#             pour fleet_obstacles).
#
#   bash mesures_cameras.sh [DUREE_S=900] [DOSSIER_SORTIE]
#
# Variables : ROS_DOMAIN_ID (84), ROBOTS (3), MIN_FREE_MB (3000),
#             MODES ("sans cameras"), WARMUP (120 s ignorees au debut),
#             LAUNCH_ARGS (arguments ajoutes aux deux lancements),
#             DASHBOARD (true : tableau de bord sur http://localhost:8080
#             pendant les mesures ; false par defaut, plus leger).
# Le script affiche son avancement chaque minute (taches, contacts).
# Sorties : synthese_<mode>.json, loc_/gaps_/contacts_<mode>.csv
#           (localization_metrics), taches_<mode>.csv, launch_<mode>.log,
#           ressources_<mode>.log, carte_sdf.yaml/.pgm.
set +u
set -m
DUREE=${1:-900}
OUT=${2:-$HOME/warehouse_ws/mesures_cameras}
WS=${WS:-$HOME/warehouse_ws}
ROBOTS=${ROBOTS:-3}
MIN_FREE_MB=${MIN_FREE_MB:-3000}
WARMUP=${WARMUP:-120}
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-84}
MODES=${MODES:-sans cameras}
DASHBOARD=${DASHBOARD:-false}
read -r -a EXTRA <<< "${LAUNCH_ARGS:-}"
HERE=$(cd "$(dirname "$0")" && pwd)
KILL_SIM=$HERE/../../rosnav/src/rosnav_bot/scripts/kill_rosnav_sim.sh
source "$HERE/env_simulation.sh"
mkdir -p "$OUT"

# Carte exacte du monde, origine au depart de robot1 (-1.5, -1.0) : la meme
# pour les deux modes (sinon une carte SLAM sauvegardee serait reprise).
SHARE=$(ros2 pkg prefix rosnav_bot)/share/rosnav_bot
CARTE=$(/usr/bin/python3 -c "
import sys; sys.path.insert(0, '$(ros2 pkg prefix rosnav_bot)/lib/rosnav_bot')
import world_to_map
print(world_to_map.build('$SHARE/worlds/warehouse.world', '$OUT/carte_sdf', (-1.5, -1.0)))")
echo "robots=$ROBOTS duree=${DUREE}s par mode, modes=[$MODES], sortie=$OUT"
echo "Duree totale prevue : environ $(( ( $(wc -w <<< "$MODES") * (DUREE + 60) ) / 60 )) min. Avancement affiche chaque minute."

pids_du_domaine() {
  local pid dom
  for pid in $(pgrep -f '/opt/ros/|warehouse_ws/install|gz sim|ruby .*gz'); do
    [ "$pid" = "$$" ] && continue
    [ "$pid" = "$PPID" ] && continue
    dom=$(tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | sed -n 's/^ROS_DOMAIN_ID=//p')
    [ "$dom" = "$ROS_DOMAIN_ID" ] && echo "$pid"
  done
}

nettoyage() {
  bash "$KILL_SIM" -y >/dev/null 2>&1 || true
  local p
  p=$(pids_du_domaine); [ -n "$p" ] && kill -TERM $p 2>/dev/null
  sleep 8
  p=$(pids_du_domaine); [ -n "$p" ] && kill -KILL $p 2>/dev/null
  sleep 2
  fastdds shm clean >/dev/null 2>&1 || true
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
      rviz:=false dashboard:="$DASHBOARD" explore:=false map:="$CARTE" "${EXTRA[@]}" "$@" \
      > "$OUT/launch_$mode.log" 2>&1 &
  local lpid=$!
  ros2 run warehouse_marl task_metrics_logger --ros-args -p use_sim_time:=true \
      -p output:="$OUT/taches_$mode.csv" -p mode_label:="$mode" > "$OUT/logger_$mode.log" 2>&1 &
  local tpid=$!
  ros2 run warehouse_marl localization_metrics --ros-args -p use_sim_time:=true \
      -p output_dir:="$OUT" -p label:="$mode" -p duration:="$DUREE" -p warmup:="$WARMUP" \
      -p "robot_names:=[$(seq -s, -f 'robot%g' 1 "$ROBOTS")]" > "$OUT/metrics_$mode.log" 2>&1 &
  local mpid=$!
  [ "$DASHBOARD" = true ] && echo "[$mode] tableau de bord : http://localhost:8080 (dans ~1 min)"
  local debut=$SECONDS fin=$((SECONDS + DUREE)) n=0 ok ko ct
  while [ $SECONDS -lt $fin ]; do
    echo "$(date +%T) $(free -m | awk '/Mem/{print $7}') Mo libres, charge $(cut -d' ' -f1 /proc/loadavg)" >> "$OUT/ressources_$mode.log"
    if ! kill -0 "$lpid" 2>/dev/null; then
      echo "$(date +%T) ARRET PREMATURE du launch" | tee -a "$OUT/ressources_$mode.log"; break
    fi
    if [ $((n % 2)) -eq 0 ]; then
      ok=$(grep -c ',succeeded,' "$OUT/taches_$mode.csv" 2>/dev/null); ok=${ok:-0}
      ko=$(grep -c ',failed,' "$OUT/taches_$mode.csv" 2>/dev/null); ko=${ko:-0}
      ct=$(grep -c ',contact,' "$OUT/contacts_$mode.csv" 2>/dev/null); ct=${ct:-0}
      echo "[$mode] $(( (SECONDS - debut) / 60 ))/$(( DUREE / 60 )) min : taches reussies $ok, echouees $ko, contacts $ct, charge $(cut -d' ' -f1 /proc/loadavg)"
    fi
    n=$((n + 1))
    sleep 30
  done
  kill -INT "$mpid" 2>/dev/null; sleep 3
  kill -INT "$tpid" 2>/dev/null
  kill -INT "$lpid" 2>/dev/null; sleep 20; kill -TERM "$lpid" 2>/dev/null
  nettoyage
  echo "[$mode] fin $(date +%T)"
}
trap 'echo; echo "Interrompu : arret de la simulation..."; nettoyage; exit 130' INT

for m in $MODES; do
  case $m in
    sans)    run_mode sans camera_localization:=false ;;
    cameras) run_mode cameras camera_localization:=true ;;
    *) echo "Mode inconnu : $m (sans ou cameras)" ;;
  esac
done
