"""Tests du DRL v3 : caracteristiques relatives, scenarios structures,
apprentissage residuel. Sans ROS 2 ; tests PyTorch ignores si absent."""

import math
import unittest

from warehouse_marl.allocation_benchmark import Task, build_grid_warehouse
from warehouse_marl.drl.env_v2 import make_benchmark
from warehouse_marl.drl.features_v3 import N_FEATURES_V3, graph_diameter

try:
    import torch  # noqa: F401
    HAVE_TORCH = True
except ImportError:
    HAVE_TORCH = False


def scenario(robots, dims=(5, 3), tasks=40, seed=3, rho=0.9, block_rate=0.0, **extra):
    return dict(dims=dims, robots=robots, rho=rho, block_rate=block_rate, tasks=tasks,
                seed=seed, **extra)


def bench_with_open_tasks(robot_nodes, targets, speeds=None, now=50.0):
    b = make_benchmark('greedy_pair', scenario(len(robot_nodes), tasks=1))
    for i, (r, node) in enumerate(zip(b.robots, robot_nodes)):
        r.node = node
        if speeds:
            r.speed = speeds[i]
    b.t = now
    b.open = [Task(f'k{i}', tgt, 1.0 + 0.25 * i, created=10.0 * i)
              for i, tgt in enumerate(targets)]
    for k in b.open:
        k.due = k.created + 60.0 / k.priority
    b.tasks = list(b.open)
    b.next_arrival = len(b.arrivals)
    return b


class TestFeaturesV3(unittest.TestCase):
    NODES = ['station_A', 'shelf_0_0', 'shelf_4_2', 'charging_dock']
    TARGETS = ['shelf_1_1', 'shelf_3_0', 'shelf_2_2']

    def test_diameter(self):
        g = build_grid_warehouse(5, 3)
        d = graph_diameter(g)
        self.assertTrue(math.isfinite(d))
        for a in g.G.nodes:
            for b in g.G.nodes:
                self.assertLessEqual(g.shortest_path(a, b)[1], d + 1e-9)
        self.assertGreater(graph_diameter(build_grid_warehouse(15, 10)), d)

    def test_same_dimension_for_3_4_and_20_robots(self):
        for n, dims in ((3, (5, 3)), (4, (5, 3)), (20, (8, 5))):
            b = make_benchmark('greedy_pair', scenario(n, dims=dims, tasks=30))
            b.begin_tick()
            while not b.candidate_pairs_v3():
                b.end_tick()
                b.begin_tick()
            for _, _, f in b.candidate_pairs_v3():
                self.assertEqual(len(f), N_FEATURES_V3)

    def test_features_do_not_depend_on_robot_index_or_name(self):
        b = bench_with_open_tasks(self.NODES, self.TARGETS, speeds=[0.3, 0.5, 0.7, 0.5])
        ref = {(r.node, r.speed, k.task_id): f for r, k, f in b.candidate_pairs_v3()}
        b2 = bench_with_open_tasks(self.NODES, self.TARGETS, speeds=[0.3, 0.5, 0.7, 0.5])
        b2.robots.reverse()
        for i, r in enumerate(b2.robots):
            r.rid = f'agent_{100 - i}'
        got = {(r.node, r.speed, k.task_id): f for r, k, f in b2.candidate_pairs_v3()}
        self.assertEqual(ref, got)

    def test_relative_features(self):
        b = bench_with_open_tasks(self.NODES, self.TARGETS)
        pairs = b.candidate_pairs_v3()
        feats = [f for _, _, f in pairs]
        for f in feats:
            self.assertGreaterEqual(f[4], 0.0)
            self.assertLessEqual(f[4], 1.0)
            self.assertGreaterEqual(f[5], 0.0)
            self.assertLessEqual(f[0], 1.0 + 1e-9)       # pas de congestion ici
        cheapest = min(feats, key=lambda f: f[0])
        self.assertEqual(cheapest[5], 0.0)
        self.assertEqual(cheapest[4], 0.0)
        # tache la plus ancienne = rang d'age 0
        oldest = [f for (_, k, f) in pairs if k.task_id == 'k0']
        self.assertTrue(all(f[9] == 0.0 for f in oldest))

    def test_cost_feature_orders_pairs_like_greedy_pair(self):
        b = bench_with_open_tasks(self.NODES, self.TARGETS)
        v2 = [(-f[0]) for _, _, f in b.candidate_pairs()]
        v3 = [(-f[0]) for _, _, f in b.candidate_pairs_v3()]
        best2 = max(range(len(v2)), key=lambda j: v2[j])
        best3 = max(range(len(v3)), key=lambda j: v3[j])
        self.assertEqual(best2, best3)


class TestStructuredScenarios(unittest.TestCase):
    def test_defaults_keep_original_draws(self):
        a = make_benchmark('fifo', scenario(3, tasks=30))
        b = make_benchmark('fifo', scenario(3, tasks=30, skew=0.0))
        self.assertEqual([(k.target, k.created) for k in a.arrivals],
                         [(k.target, k.created) for k in b.arrivals])

    def test_heterogeneous_speeds_and_lateness_metric(self):
        b = make_benchmark('greedy_time', scenario(6, dims=(8, 5), tasks=60, skew=1.5,
                                                   speeds=(0.3, 0.5, 0.7)))
        self.assertEqual([r.speed for r in b.robots], [0.3, 0.5, 0.7, 0.3, 0.5, 0.7])
        res = b.run()
        self.assertGreaterEqual(res['taches_en_retard_pct'], 0.0)
        self.assertLessEqual(res['taches_en_retard_pct'], 100.0)

    def test_zipf_demand_concentrates_targets(self):
        b = make_benchmark('fifo', scenario(3, dims=(8, 5), tasks=400, skew=1.5))
        counts = {}
        for k in b.arrivals:
            counts[k.target] = counts.get(k.target, 0) + 1
        top = max(counts.values())
        self.assertGreater(top / len(b.arrivals), 0.15)    # uniforme : 1/40 = 2.5 %


if __name__ == '__main__':
    unittest.main()
