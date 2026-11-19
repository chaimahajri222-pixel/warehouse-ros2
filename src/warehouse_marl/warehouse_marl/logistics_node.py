"""
logistics_node.py
-----------------
Flux d'entrepot par roles, sans DRL (mission_mode:=logistics).

Deux types de missions, chacune en deux etapes (prise puis depose) :
  stockage   : salle de production (station_A / station_B, zone ouest)
               -> rack (on remplit l'etagere) ;
  expedition : rack -> quai de chargement (delivery_1 / delivery_2, zone est).

Roles (parametre ``roles``, dans l'ordre de ``robot_names``) :
  stock : ne fait que du stockage (robot1 par defaut) ;
  ship  : ne fait que de l'expedition (robot2) ;
  flex  : polyvalent (robot3) ; quand il est libre, il prend une mission dans
          la file la plus chargee (le plus de missions en attente ; a egalite,
          la plus ancienne). Il aide donc la ou la charge est la plus forte.

Le noeud tient un stock par rack (unites sur l'etagere) et suit chaque
colis : stockage = colis pris en production (sortie de production), puis
pose sur le rack a l'arrivee (+1 au rack) ; expedition = colis retire du rack
au chargement (-1 au rack), puis livre au quai a l'arrivee. Un colis
d'expedition dont la mission echoue apres chargement est remis sur son rack. Le rack est choisi au moment de l'attribution : le moins plein (stockage)
ou le plus plein (expedition), dans une allee ou aucun autre robot n'a de
mission. Deux robots ne peuvent pas se croiser dans une allee (marges de
securite des costmaps) : sans cette regle, ils s'y bloquaient.

Charge variable : les commandes arrivent par phases de ``phase_sec``
secondes ; a chaque phase, l'un des deux flux est ``burst_factor`` fois plus
rapide (pic de production, puis pic de commandes clients), pour montrer le
robot polyvalent changer de mission selon la charge.

Le noeud remplace task_generator + consensus/DRL : il publie chaque mission
sur /warehouse/tasks/new (avec ``pickup_node``) au moment ou il l'attribue,
puis l'attribution sur /warehouse/tasks/direct_assignment (mission_executor).
Etat pour le tableau de bord : /warehouse/logistics/state (JSON, 1 Hz).
"""

import json
import random
import uuid
from collections import deque

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from warehouse_marl.warehouse_graph import build_demo_warehouse

FINAL = ('succeeded', 'failed', 'rejected', 'canceled')
TYPES = ('stockage', 'expedition')
ROLE_TYPES = {'stock': ('stockage',), 'ship': ('expedition',), 'flex': TYPES}


class LogisticsNode(Node):

    def __init__(self):
        super().__init__('logistics_node')
        self.declare_parameter('robot_names', ['robot1', 'robot2', 'robot3'])
        self.declare_parameter('roles', ['stock', 'ship', 'flex'])
        self.declare_parameter('map_origin_x', -1.5)
        self.declare_parameter('map_origin_y', -1.0)
        self.declare_parameter('production_nodes', ['station_A', 'station_B'])
        self.declare_parameter('delivery_nodes', ['delivery_1', 'delivery_2'])
        # Une commande de chaque type toutes les <period> s simulees en
        # moyenne (Poisson) ; le flux en pic est burst_factor fois plus rapide.
        self.declare_parameter('stock_period_sec', 40.0)
        self.declare_parameter('ship_period_sec', 40.0)
        self.declare_parameter('phase_sec', 240.0)
        self.declare_parameter('burst_factor', 3.0)
        self.declare_parameter('max_waiting', 6)          # par file
        self.declare_parameter('rack_capacity', 10)
        self.declare_parameter('initial_stock_min', 2)
        self.declare_parameter('initial_stock_max', 8)
        self.declare_parameter('start_delay_sec', 20.0)
        # Mission refusee (Nav2 du robot pas encore actif) : remise en tete de
        # file, et le robot n'est plus sollicite pendant reject_pause_sec.
        self.declare_parameter('reject_pause_sec', 10.0)
        self.declare_parameter('max_rejects', 5)
        self.declare_parameter('seed', 42)

        gp = self.get_parameter
        self.robots = list(gp('robot_names').value)
        roles = list(gp('roles').value)
        self.roles = {r: (roles[i] if i < len(roles) else 'flex')
                      for i, r in enumerate(self.robots)}
        for r, role in self.roles.items():
            if role not in ROLE_TYPES:
                raise ValueError(f'role inconnu pour {r} : {role} (stock, ship, flex)')
        self.graph = build_demo_warehouse(float(gp('map_origin_x').value),
                                          float(gp('map_origin_y').value), True)
        self.production = list(gp('production_nodes').value)
        self.delivery = list(gp('delivery_nodes').value)
        self.shelves = sorted(n for n, d in self.graph.G.nodes(data=True)
                              if d.get('node_type') == 'shelf')
        self.period = {'stockage': float(gp('stock_period_sec').value),
                       'expedition': float(gp('ship_period_sec').value)}
        self.phase_sec = float(gp('phase_sec').value)
        self.burst = float(gp('burst_factor').value)
        self.max_waiting = int(gp('max_waiting').value)
        self.capacity = int(gp('rack_capacity').value)
        self.rng = random.Random(int(gp('seed').value))
        lo, hi = int(gp('initial_stock_min').value), int(gp('initial_stock_max').value)
        self.stock = {s: self.rng.randint(lo, hi) for s in self.shelves}
        self.start_delay = float(gp('start_delay_sec').value)
        self.reject_pause = float(gp('reject_pause_sec').value)
        self.max_rejects = int(gp('max_rejects').value)
        self.paused_until = {r: 0.0 for r in self.robots}
        # Deux echecs de suite : le robot (Nav2 en difficulte) est mis en pause.
        self.fail_streak = {r: 0 for r in self.robots}
        self.fail_pause = 60.0

        self.queues = {t: deque() for t in TYPES}
        self.busy = {r: None for r in self.robots}      # robot -> mission en cours
        self.active = {}                                # task_id -> mission
        self.next_at = {}
        self.t0 = None
        self.done = {r: {t: 0 for t in TYPES} for r in self.robots}
        self.failed = {t: 0 for t in TYPES}
        self.created = {t: 0 for t in TYPES}
        self.flex_choices = {t: 0 for t in TYPES}
        self.last_event = ''
        # Compteurs de colis (tableau de bord) et derniers mouvements.
        self.totals = {'produits': 0, 'entres_stock': 0, 'sortis_stock': 0, 'livres': 0}
        self.moves = deque(maxlen=40)
        self._move_id = 0
        self.place_count = {p: 0 for p in self.production + self.delivery}

        self.task_pub = self.create_publisher(String, '/warehouse/tasks/new', 10)
        self.assign_pub = self.create_publisher(String, '/warehouse/tasks/direct_assignment', 10)
        self.state_pub = self.create_publisher(String, '/warehouse/logistics/state', 10)
        self.create_subscription(String, '/warehouse/tasks/status', self._on_status, 50)
        self.create_timer(0.5, self._tick)
        self.create_timer(1.0, self._publish_state)
        self.get_logger().info(
            'Logistique par roles : ' + ', '.join(f'{r}={self.roles[r]}' for r in self.robots)
            + f' ; production {self.production}, delivery {self.delivery}.')

    # ------------------------------------------------------------ temps / charge
    def _now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def _peak(self, now):
        """Flux en pic pendant la phase courante (alternance)."""
        if self.phase_sec <= 0:
            return None
        return TYPES[int((now - self.t0) // self.phase_sec) % 2]

    def _draw_next(self, kind, now):
        period = self.period[kind]
        if self._peak(now) == kind:
            period /= self.burst
        self.next_at[kind] = now + self.rng.expovariate(1.0 / period)

    # ------------------------------------------------------------ commandes
    @staticmethod
    def _aisle(shelf):
        """Allee de service d'un rack : rangees 0, 1, 2 ; 3 et 4 partagent la leur."""
        return min(int(shelf.split('_')[1]), 3)

    def _pick_rack(self, kind):
        """Rack pour une mission, dans une allee libre si possible."""
        busy_racks = {m['rack'] for m in self.active.values()}
        busy_aisles = {self._aisle(r) for r in busy_racks}
        if kind == 'stockage':
            ok = [s for s in self.shelves if self.stock[s] < self.capacity and s not in busy_racks]
            key = lambda s: (self._aisle(s) in busy_aisles, self.stock[s], self.rng.random())
        else:
            ok = [s for s in self.shelves if self.stock[s] > 0 and s not in busy_racks]
            key = lambda s: (self._aisle(s) in busy_aisles, -self.stock[s], self.rng.random())
        return min(ok, key=key, default=None)

    def _create(self, kind, now):
        mission = {'task_id': f'{kind[:4]}_{uuid.uuid4().hex[:6]}', 'kind': kind,
                   'created_at': now}
        self.queues[kind].append(mission)
        self.created[kind] += 1
        self.get_logger().info(
            f'Commande {mission["task_id"]} ({kind}) ; file {kind} = {len(self.queues[kind])}.')

    # ------------------------------------------------------------ attribution
    def _choose_queue(self, robot):
        allowed = ROLE_TYPES[self.roles[robot]]
        candidates = [t for t in allowed if self.queues[t]]
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]
        # Polyvalent : la file la plus longue ; a egalite la plus ancienne.
        return max(candidates, key=lambda t: (len(self.queues[t]),
                                              -self.queues[t][0]['created_at']))

    def _endpoint(self, points):
        """Point de production / delivery le moins utilise par les missions en cours."""
        use = {p: 0 for p in points}
        for m in self.active.values():
            for key in ('pickup', 'drop'):
                if m.get(key) in use:
                    use[m[key]] += 1
        return min(points, key=lambda p: (use[p], points.index(p)))

    def _assign(self, robot, kind):
        rack = self._pick_rack(kind)
        if rack is None:
            return False                      # aucun rack possible pour l'instant
        m = self.queues[kind].popleft()
        m['rack'] = rack
        if kind == 'stockage':
            m['pickup'], m['drop'] = self._endpoint(self.production), m['rack']
        else:
            m['pickup'], m['drop'] = m['rack'], self._endpoint(self.delivery)
        m['robot'] = robot
        self.busy[robot] = m
        self.active[m['task_id']] = m
        if self.roles[robot] == 'flex':
            self.flex_choices[kind] += 1
            other = TYPES[1 - TYPES.index(kind)]
            self.last_event = (f'{robot} (polyvalent) -> {kind} : file {kind} '
                               f'{len(self.queues[kind]) + 1} / {other} {len(self.queues[other])}')
            self.get_logger().info(self.last_event)
        task = {'task_id': m['task_id'], 'task_type': kind, 'pickup_node': m['pickup'],
                'target_node': m['drop'], 'priority': 1.0, 'created_at': m['created_at']}
        self.task_pub.publish(String(data=json.dumps(task)))
        self.assign_pub.publish(String(data=json.dumps(
            {'task_id': m['task_id'], 'robot_id': robot, 'target_node': m['drop'], 'cost': 0.0})))
        self.get_logger().info(
            f'{robot} ({self.roles[robot]}) : {m["task_id"]} {kind} '
            f'{m["pickup"]} -> {m["drop"]} (stock du rack {self.stock[rack]}, '
            f'allee {self._aisle(rack)}).')
        return True

    def _move(self, robot, kind, place, delta, text):
        """Mouvement de colis pour le tableau de bord (delta : effet sur ``place``)."""
        self._move_id += 1
        if place in self.place_count:
            self.place_count[place] += 1
        self.moves.append({'id': self._move_id, 'time': round(self._now(), 1), 'robot': robot,
                           'kind': kind, 'place': place, 'delta': delta,
                           'stock': self.stock.get(place), 'text': text})

    def _on_status(self, msg):
        try:
            d = json.loads(msg.data)
        except ValueError:
            return
        m = self.active.get(d.get('task_id'))
        if m is None:
            return
        if d.get('state') == 'picked_up' and not m.get('loaded'):
            m['loaded'] = True
            if m['kind'] == 'stockage':
                self.totals['produits'] += 1
                self._move(m['robot'], 'stockage', m['pickup'], -1,
                           f'{m["robot"]} prend un colis en production ({m["pickup"]})')
            else:
                self.stock[m['rack']] = max(0, self.stock[m['rack']] - 1)
                self.totals['sortis_stock'] += 1
                self._move(m['robot'], 'expedition', m['rack'], -1,
                           f'{m["robot"]} retire un colis du rack {m["rack"]} '
                           f'(stock {self.stock[m["rack"]]})')
            return
        if d.get('state') not in FINAL:
            return
        del self.active[m['task_id']]
        if self.busy.get(m['robot']) is m:
            self.busy[m['robot']] = None
        kind = m['kind']
        if d['state'] == 'rejected' and m.get('rejects', 0) < self.max_rejects:
            m['rejects'] = m.get('rejects', 0) + 1
            self.paused_until[m['robot']] = self._now() + self.reject_pause
            m['task_id'] = f'{kind[:4]}_{uuid.uuid4().hex[:6]}'   # nouvel identifiant
            for key in ('pickup', 'drop', 'robot', 'rack'):
                m.pop(key, None)
            self.queues[kind].appendleft(m)
            self.get_logger().warn(
                f'Mission refusee par {d.get("robot_id")} (Nav2 pas pret ?) : remise en '
                f'tete de file {kind} ({m["rejects"]}/{self.max_rejects}).')
            return
        if d['state'] == 'succeeded':
            if kind == 'stockage':
                self.stock[m['rack']] = min(self.capacity, self.stock[m['rack']] + 1)
                self.totals['entres_stock'] += 1
                self._move(m['robot'], kind, m['rack'], +1,
                           f'{m["robot"]} pose un colis sur le rack {m["rack"]} '
                           f'(stock {self.stock[m["rack"]]})')
            else:
                if not m.get('loaded'):           # chargement non signale : on le compte ici
                    self.stock[m['rack']] = max(0, self.stock[m['rack']] - 1)
                    self.totals['sortis_stock'] += 1
                self.totals['livres'] += 1
                self._move(m['robot'], kind, m['drop'], +1,
                           f'{m["robot"]} livre un colis au quai ({m["drop"]})')
            self.done[m['robot']][kind] += 1
            self.fail_streak[m['robot']] = 0
            self.get_logger().info(
                f'{m["robot"]} a fini {m["task_id"]} ({kind}) : rack {m["rack"]} '
                f'stock {self.stock[m["rack"]]}.')
        else:
            self.failed[kind] += 1
            self.fail_streak[m['robot']] += 1
            if self.fail_streak[m['robot']] >= 2:
                self.paused_until[m['robot']] = self._now() + self.fail_pause
                self.get_logger().warn(
                    f'{m["robot"]} : {self.fail_streak[m["robot"]]} echecs de suite, '
                    f'pause de {self.fail_pause:.0f} s avant une nouvelle mission.')
            if kind == 'expedition' and m.get('loaded'):
                self.stock[m['rack']] = min(self.capacity, self.stock[m['rack']] + 1)
                self.totals['sortis_stock'] -= 1
                self._move(m['robot'], kind, m['rack'], +1,
                           f'{m["robot"]} : mission echouee, colis remis sur {m["rack"]}')
            self.get_logger().warn(f'{m["task_id"]} ({kind}) : {d["state"]}.')

    def _tick(self):
        now = self._now()
        if now <= 0.0:
            return                                      # pas encore d'horloge simulee
        if self.t0 is None:
            self.t0 = now + self.start_delay
            for kind in TYPES:
                self._draw_next(kind, self.t0)
        if now < self.t0:
            return
        for kind in TYPES:
            while now >= self.next_at[kind]:
                if len(self.queues[kind]) < self.max_waiting:
                    self._create(kind, now)
                self._draw_next(kind, self.next_at[kind])
        for robot in self.robots:
            if self.busy[robot] is None and now >= self.paused_until[robot]:
                kind = self._choose_queue(robot)
                if kind is not None:
                    self._assign(robot, kind)

    def _publish_state(self):
        now = self._now()
        state = {
            'time': round(now, 1),
            'peak': self._peak(now) if self.t0 and now >= self.t0 else None,
            'roles': self.roles,
            'queues': {t: len(q) for t, q in self.queues.items()},
            'busy': {r: (None if m is None else {'task_id': m['task_id'], 'kind': m['kind'],
                                                  'pickup': m['pickup'], 'drop': m['drop'],
                                                  'loaded': bool(m.get('loaded'))})
                     for r, m in self.busy.items()},
            'done': self.done,
            'failed': self.failed,
            'created': self.created,
            'flex_choices': self.flex_choices,
            'stock': self.stock,
            'capacity': self.capacity,
            'totals': {**self.totals,
                       'en_transit': sum(1 for m in self.busy.values() if m and m.get('loaded')),
                       'stock_total': sum(self.stock.values())},
            'moves': list(self.moves),
            'place_count': self.place_count,
            'last_event': self.last_event,
        }
        self.state_pub.publish(String(data=json.dumps(state)))


def main(args=None):
    rclpy.init(args=args)
    node = LogisticsNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
