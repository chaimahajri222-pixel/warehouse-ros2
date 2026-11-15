# env_simulation.sh : environnement d'un terminal pour la simulation.
# A SOURCER (pas executer) dans chaque nouveau terminal :
#
#   source ~/warehouse_ws/src/warehouse-ros2/src/warehouse_marl/scripts/env_simulation.sh
#
# 1. ROS 2 Jazzy ; 2. le workspace compile (install/setup.bash) ;
# 3. les paquets Python de l'environnement virtuel (torch...) ajoutes au
#    PYTHONPATH : les noeuds ROS sont lances par /usr/bin/python3, qui ne voit
#    pas torch sans cela (modes hybrid, idle_mode:=drl, route_mode:=drl).
# Variables : WS (defaut ~/warehouse_ws), VENV (defaut $WS/.venv).

WS=${WS:-$HOME/warehouse_ws}
VENV=${VENV:-$WS/.venv}
source /opt/ros/jazzy/setup.bash
if [ -f "$WS/install/setup.bash" ]; then
  source "$WS/install/setup.bash"
else
  echo "[env_simulation] $WS/install/setup.bash absent : lancer d'abord colcon build (voir README_SIMULATION.md)."
fi
_site=$(ls -d "$VENV"/lib/python3*/site-packages 2>/dev/null | head -1)
if [ -n "$_site" ]; then
  case ":${PYTHONPATH:-}:" in
    *":$_site:"*) ;;
    *) export PYTHONPATH="$_site${PYTHONPATH:+:$PYTHONPATH}" ;;
  esac
else
  echo "[env_simulation] environnement Python $VENV absent : les modes DRL ne marcheront pas."
fi
unset _site
if ! /usr/bin/python3 -c 'import torch' 2>/dev/null; then
  echo "[env_simulation] torch introuvable pour /usr/bin/python3 : modes DRL indisponibles (voir README_SIMULATION.md, installation)."
fi
