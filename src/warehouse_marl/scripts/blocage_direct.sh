#!/usr/bin/env bash
# blocage_direct.sh : bloque une allee (arete du graphe) PENDANT une simulation
# deja lancee, enregistre ce qui se passe, puis debloque.
#
#   bash blocage_direct.sh [U=shelf_2_0] [V=shelf_2_1] [DUREE_S=120] [SORTIE]
#
# A lancer dans un 2e terminal, avec le MEME ROS_DOMAIN_ID que la simulation,
# apres "source .../env_simulation.sh". Sortie (defaut
# ~/warehouse_ws/mesures_blocage_<date>) :
#   avant.txt / pendant.txt / apres.txt : etat des aretes U-V (graph_state)
#   encheres.log, assignations.log, statuts.log, routes.log : messages
#   enregistres pendant toute la duree (avant, pendant, apres le blocage)
#   journal.txt : heures du blocage et du deblocage.
set +u
U=${1:-shelf_2_0}; V=${2:-shelf_2_1}; DUREE=${3:-120}
OUT=${4:-$HOME/warehouse_ws/mesures_blocage_$(date +%Y%m%d_%H%M%S)}
mkdir -p "$OUT"
if ! ros2 topic list 2>/dev/null | grep -q '^/warehouse/graph_state$'; then
  echo "Aucune simulation visible (/warehouse/graph_state absent) sur ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-0}."
  echo "Lancer d'abord la simulation, et sourcer env_simulation.sh dans ce terminal."
  exit 1
fi
PIDS=()
for t in bids:encheres assignments:assignations; do
  ros2 topic echo --full-length /warehouse/consensus/${t%%:*} std_msgs/msg/String > "$OUT/${t##*:}.log" 2>&1 &
  PIDS+=($!)
done
ros2 topic echo --full-length /warehouse/tasks/status std_msgs/msg/String > "$OUT/statuts.log" 2>&1 & PIDS+=($!)
ros2 topic echo --full-length /warehouse/routes std_msgs/msg/String > "$OUT/routes.log" 2>&1 & PIDS+=($!)

etat() {   # etat de l'arete U-V dans /warehouse/graph_state ; $1 = true|false :
           # attend (20 s au plus) que l'arete soit dans cet etat ; vide = 1er message
  timeout 20 ros2 topic echo --full-length /warehouse/graph_state std_msgs/msg/String 2>/dev/null \
    | python3 -c "
import sys, json, yaml
want = '$1'
doc, last = [], None
for line in sys.stdin:
    if line.strip() != '---':
        doc.append(line); continue
    try:
        d = json.loads(yaml.safe_load(''.join(doc))['data'])
    except Exception:
        doc = []; continue
    doc = []
    e = [x for x in d['edges'] if {x['u'], x['v']} == {'$U', '$V'}]
    if not e:
        print('arete $U-$V introuvable dans le graphe'); sys.exit(0)
    last = e[0]
    if not want or str(last['blocked']).lower() == want:
        print(json.dumps(last)); sys.exit(0)
print(json.dumps(last) + '  (ETAT ATTENDU blocked=' + want + ' NON OBSERVE en 20 s)')"
}
publier() {   # $1 = true|false
  local extra=''
  [ "$1" = true ] && extra=", \"duration_s\": $((DUREE + 60))"
  ros2 topic pub --once /warehouse/blocked_edges std_msgs/msg/String \
    "{data: '{\"u\": \"$U\", \"v\": \"$V\", \"blocked\": $1$extra, \"source\": \"blocage_direct.sh\", \"reason\": \"essai\"}'}" >/dev/null
}
log() { echo "$(date +%T) $*" | tee -a "$OUT/journal.txt"; }

log "enregistrement 30 s avant le blocage"; sleep 30
etat > "$OUT/avant.txt"; log "etat avant : $(cat "$OUT/avant.txt")"
etat true > "$OUT/pendant.txt" & EP=$!
sleep 2
log "BLOCAGE $U <-> $V pendant $DUREE s"
publier true
wait $EP; log "etat pendant : $(cat "$OUT/pendant.txt")"
sleep "$DUREE"
etat false > "$OUT/apres.txt" & EP=$!
sleep 2
log "DEBLOCAGE $U <-> $V"
publier false
wait $EP; log "etat apres : $(cat "$OUT/apres.txt")"
sleep 30
kill -INT "${PIDS[@]}" 2>/dev/null
for _ in 1 2 3 4 5 6 7 8 9 10; do
  kill -0 "${PIDS[@]}" 2>/dev/null || break; sleep 0.5
done
kill -9 "${PIDS[@]}" 2>/dev/null; wait "${PIDS[@]}" 2>/dev/null
log "termine : $OUT"
