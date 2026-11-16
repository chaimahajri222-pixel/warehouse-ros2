"""Tests du simulateur v6 (PROTOCOLE_V6.md) : equivalences exactes avec la v4
sans capacite, avec les heuristiques de depart quand f_theta = 0, capacite de
1 robot par segment, graines disjointes, reprise des journaux."""
import csv

import pytest

torch = pytest.importorskip('torch')

from warehouse_marl.allocation_benchmark import build_grid_warehouse, mean_service_time
from warehouse_marl.drl.train_v6 import (FORBIDDEN, TEST6_SEEDS, VAL6_SEEDS, SeedStream,
                                         _truncate_csv)
from warehouse_marl.drl.v4_dqn import V4DQN
from warehouse_marl.drl.v4_sim import BenchmarkV4
from warehouse_marl.drl.v6_sim import N_IDLE6_FEATURES, N_ROUTE6_FEATURES, BenchmarkV6, seg_key

KEYS = ('temps_traitement_moy_s', 'taches_echouees', 'distance_par_tache_m', 'duree_simulee_s')


def _rate(dims, R, rho=0.7):
    return rho * R / mean_service_time(build_grid_warehouse(*dims), 0.5, 10.0)


@pytest.mark.parametrize('route,idle', [('dijkstra_dynamique', 'rester_sur_place'),
                                        ('dijkstra_statique', 'centre_de_demande'),
                                        ('dijkstra_dynamique', 'retour_au_depot')])
def test_v6_without_capacity_equals_v4(route, idle):
    dims, R = (8, 5), 6
    kw = dict(block_rate=3 / 60, route_mode=route, idle_mode=idle, demand_skew=1.0)
    a = BenchmarkV4('greedy_pair', build_grid_warehouse(*dims), R, _rate(dims, R), 120, seed=7,
                    **kw).run()
    b = BenchmarkV6('greedy_pair', build_grid_warehouse(*dims), R, _rate(dims, R), 120, seed=7,
                    **kw).run()
    for k in KEYS:
        assert a[k] == pytest.approx(b[k], abs=1e-9), k


@pytest.mark.parametrize('dims,R', [((5, 3), 3), ((15, 10), 20)])
def test_untrained_idle6_equals_coverage(dims, R):
    agent = V4DQN('idle6', N_IDLE6_FEATURES, gamma=0.9)
    out = {}
    for mode in ('couverture', 'drl_idle6'):
        out[mode] = BenchmarkV6('greedy_pair', build_grid_warehouse(*dims), R, _rate(dims, R),
                                120, seed=11, demand_skew=1.0, idle_mode=mode,
                                idle6_agent=agent).run()
    for k in KEYS:
        assert out['drl_idle6'][k] == pytest.approx(out['couverture'][k], abs=1e-9), k


@pytest.mark.parametrize('dims,R', [((10, 8), 10), ((10, 8), 20)])
def test_untrained_route6_equals_congestion_dijkstra(dims, R):
    agent = V4DQN('route6', N_ROUTE6_FEATURES, gamma=1.0)
    out = {}
    for mode in ('dijkstra_congestion', 'drl_route6'):
        out[mode] = BenchmarkV6('greedy_pair', build_grid_warehouse(*dims), R,
                                _rate(dims, R, 0.9), 120, seed=13, route_mode=mode,
                                edge_capacity=1, route6_agent=agent).run()
    for k in KEYS:
        assert out['drl_route6'][k] == pytest.approx(out['dijkstra_congestion'][k], abs=1e-9), k


@pytest.mark.parametrize('mode', ['dijkstra_statique', 'dijkstra_dynamique',
                                  'dijkstra_congestion'])
def test_capacity_one_robot_per_segment(mode):
    dims, R = (8, 5), 20
    b = BenchmarkV6('greedy_pair', build_grid_warehouse(*dims), R, _rate(dims, R, 0.9), 80,
                    seed=17, route_mode=mode, edge_capacity=1)
    seen_queue = False
    while b.t < b.horizon:
        b.begin_tick()
        b.allocate()
        fin = b.end_tick()
        segs = [seg_key(*r.edge) for r in b.robots if r.edge is not None]
        assert len(segs) == len(set(segs))
        seen_queue = seen_queue or b.queue_wait_total > 0
        if fin:
            break
    m = b.metrics()
    assert m['taches_finies'] + m['taches_echouees'] == 80
    assert seen_queue


@pytest.mark.parametrize('cfg_i', [0, 2, 3])
def test_untrained_alloc6_equals_greedy_pair(cfg_i):
    from warehouse_marl.drl.alloc6 import N_ALLOC6_FEATURES
    from warehouse_marl.drl.train_v4 import DATASET_CONFIGS, dataset
    from warehouse_marl.drl.train_v6 import make_sim6
    agent = V4DQN('alloc6', N_ALLOC6_FEATURES, gamma=0.95)
    st = dataset().window_starts('train_fit', 100)
    sc = dict(DATASET_CONFIGS[cfg_i], phase='C', tasks=100, alloc='-', seed=123_456_789,
              split='train_fit', start=st[5])
    a = make_sim6(sc, 'greedy_pair').run()
    b = make_sim6(sc, 'drl_alloc6', agent).run()
    for k in KEYS:
        assert a[k] == pytest.approx(b[k], abs=1e-9), k
    assert b['attentes_allocation'] == 0


def test_alloc6_rewards_sum_to_total_time():
    """Somme des recompenses = -(somme des temps de traitement) / 60 quand
    toutes les taches finissent (pas d'exploration)."""
    from warehouse_marl.drl.alloc6 import N_ALLOC6_FEATURES
    from warehouse_marl.drl.train_v4 import DATASET_CONFIGS, dataset
    from warehouse_marl.drl.train_v6 import make_sim6
    agent = V4DQN('alloc6', N_ALLOC6_FEATURES, gamma=0.95)
    st = dataset().window_starts('train_fit', 60)
    sc = dict(DATASET_CONFIGS[0], phase='C', tasks=60, alloc='-', seed=223_456_789,
              split='train_fit', start=st[9])
    rewards = []
    sim = make_sim6(sc, 'drl_alloc6', agent, cb=lambda f, r, n, d: rewards.append(r))
    m = sim.run()
    assert m['taches_echouees'] == 0 and m['taches_non_finies'] == 0
    total = sum(k.done - k.created for k in sim.tasks)
    assert sum(rewards) == pytest.approx(-total / 60.0, rel=0.02)


def test_seed_sets_disjoint():
    assert not set(TEST6_SEEDS) & set(VAL6_SEEDS)
    st = SeedStream(0)
    for _ in range(2000):
        s, _ = st.next()
        assert s not in FORBIDDEN


def test_truncate_csv(tmp_path):
    p = tmp_path / 'log.csv'
    with open(p, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['graine', 'episode', 'x'])
        for e in range(10):
            w.writerow([0, e, e * 2])
    _truncate_csv(str(p), 4)
    with open(p, newline='') as f:
        rows = list(csv.reader(f))
    assert [int(r[1]) for r in rows[1:]] == [0, 1, 2, 3, 4]
