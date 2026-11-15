"""Tests du simulateur v4 (PROTOCOLE_V4.md) : equivalences exactes avec le
banc d'origine et avec les heuristiques de depart quand f_theta = 0."""
import pytest

torch = pytest.importorskip('torch')

from warehouse_marl.allocation_benchmark import Benchmark, build_grid_warehouse, mean_service_time
from warehouse_marl.drl.train_v4 import TEST_SEEDS, VAL_SEEDS, train_seed_stream
from warehouse_marl.drl.v4_dqn import V4DQN
from warehouse_marl.drl.v4_sim import BenchmarkV4, N_IDLE_FEATURES, N_ROUTE_FEATURES

KEYS = ('temps_traitement_moy_s', 'taches_echouees', 'distance_par_tache_m', 'duree_simulee_s')
CASES = [((5, 3), 3, 0.0, 'greedy_pair', 7), ((5, 3), 3, 6 / 60, 'greedy_pair', 1007),
         ((5, 3), 3, 6 / 60, 'consensus', 7), ((8, 5), 6, 3 / 60, 'consensus', 2007)]


def _rate(dims, R):
    return 0.7 * R / mean_service_time(build_grid_warehouse(*dims), 0.5, 10.0)


@pytest.mark.parametrize('dims,R,br,alloc,seed', CASES)
def test_dynamic_and_untrained_drl_equal_original(dims, R, br, alloc, seed):
    ref = Benchmark(alloc, build_grid_warehouse(*dims), R, _rate(dims, R), 120, seed=seed,
                    block_rate=br).run()
    agent = V4DQN('route', N_ROUTE_FEATURES, gamma=1.0)
    for mode in ('dijkstra_dynamique', 'drl_route'):
        m = BenchmarkV4(alloc, build_grid_warehouse(*dims), R, _rate(dims, R), 120, seed=seed,
                        block_rate=br, route_mode=mode, route_agent=agent).run()
        for k in KEYS:
            assert m[k] == pytest.approx(ref[k], abs=1e-9), (mode, k)


def test_untrained_idle_equals_demand_center():
    dims, R = (8, 5), 6
    agent = V4DQN('idle', N_IDLE_FEATURES, gamma=0.9)
    out = {}
    for mode in ('centre_de_demande', 'drl_idle'):
        out[mode] = BenchmarkV4('greedy_pair', build_grid_warehouse(*dims), R, _rate(dims, R), 120,
                                seed=7, demand_skew=1.0, idle_mode=mode, idle_agent=agent).run()
    for k in KEYS:
        assert out['drl_idle'][k] == pytest.approx(out['centre_de_demande'][k], abs=1e-9)


def test_seed_sets_disjoint():
    assert not TEST_SEEDS & set(VAL_SEEDS)
    stream = train_seed_stream(0)
    for _ in range(1000):
        s, _ = next(stream)
        assert s not in TEST_SEEDS and s not in VAL_SEEDS


def test_static_route_ignores_congestion_but_avoids_blocks():
    g = build_grid_warehouse(5, 3)
    b = BenchmarkV4('greedy_pair', g, 3, 0.05, 10, seed=7)
    g.set_blocked('shelf_2_0', 'shelf_2_1', True)
    g.set_blocked('shelf_2_1', 'shelf_2_0', True)
    path = b.static_path('shelf_2_0', 'shelf_2_1')
    assert path[0] == 'shelf_2_0' and path[-1] == 'shelf_2_1' and len(path) > 2
