"""Tests du DRL v2 (drl/features_v2.py, drl/env_v2.py, drl/pair_dqn.py).

Sans ROS 2. Les tests du reseau sont ignores si PyTorch est absent.
"""

import math
import random
import unittest

import numpy as np

from warehouse_marl.allocation_benchmark import Task
from warehouse_marl.drl.env_v2 import REWARD_NORM_S, AllocationEnvV2, make_benchmark
from warehouse_marl.drl.features_v2 import N_FEATURES, calibrated_bias

try:
    import torch  # noqa: F401
    HAVE_TORCH = True
except ImportError:
    HAVE_TORCH = False


def scenario(robots, dims=(5, 3), tasks=40, seed=3, rho=0.9, block_rate=0.0):
    return dict(dims=dims, robots=robots, rho=rho, block_rate=block_rate, tasks=tasks, seed=seed)


class MinCostScorer:
    """Politique de test sans PyTorch : Q = -cout de chemin."""
    meta = {'reward_norm_s': REWARD_NORM_S, 'speed': 0.5}

    def scores(self, feats):
        return -np.asarray(feats, dtype=np.float32)[:, 0]


def bench_with_open_tasks(robot_nodes, targets, now=50.0):
    """Benchmark a l'arret avec des robots places et des taches en file."""
    b = make_benchmark('drl2_direct', scenario(len(robot_nodes), tasks=1))
    for r, node in zip(b.robots, robot_nodes):
        r.node = node
    b.t = now
    b.open = [Task(f'k{i}', tgt, 1.0 + 0.25 * i, created=10.0 * i)
              for i, tgt in enumerate(targets)]
    b.tasks = list(b.open)
    b.next_arrival = len(b.arrivals)
    return b


class TestObservationShape(unittest.TestCase):
    def test_same_dimension_for_3_4_and_20_robots(self):
        for n, dims in ((3, (5, 3)), (4, (5, 3)), (20, (8, 5))):
            env = AllocationEnvV2(seed=1)
            obs, info = env.reset(scenario=scenario(n, dims=dims, tasks=30))
            self.assertFalse(info['done'])
            self.assertEqual(obs.ndim, 2)
            self.assertEqual(obs.shape[1], N_FEATURES, f'{n} robots')
            self.assertGreater(obs.shape[0], 0)
            for _ in range(10):          # la dimension reste fixe pendant l'episode
                obs, _, done, _ = env.step(0)
                if done:
                    break
                self.assertEqual(obs.shape[1], N_FEATURES)


class TestNoRobotIndex(unittest.TestCase):
    def test_features_do_not_depend_on_robot_index_or_name(self):
        nodes = ['station_A', 'shelf_0_0', 'shelf_4_2', 'charging_dock']
        targets = ['shelf_1_1', 'shelf_3_0', 'shelf_2_2']
        b = bench_with_open_tasks(nodes, targets)
        ref = {(r.node, k.task_id): f for r, k, f in b.candidate_pairs()}

        b2 = bench_with_open_tasks(nodes, targets)
        b2.robots.reverse()                       # autre ordre ...
        for i, r in enumerate(b2.robots):         # ... et autres noms
            r.rid = f'agent_{100 - i}'
        got = {(r.node, k.task_id): f for r, k, f in b2.candidate_pairs()}

        self.assertEqual(set(ref), set(got))
        for key in ref:
            self.assertEqual(ref[key], got[key], key)

    def test_identical_robots_get_identical_features(self):
        b = bench_with_open_tasks(['shelf_0_0', 'shelf_0_0', 'shelf_4_2'], ['shelf_1_1'])
        pairs = b.candidate_pairs()
        same = [f for r, _, f in pairs if r.node == 'shelf_0_0']
        self.assertEqual(len(same), 2)
        self.assertEqual(same[0], same[1])


class TestReward(unittest.TestCase):
    def _reward_choosing(self, chosen_node, other_node):
        env = AllocationEnvV2(seed=0, center=False)
        env.reset(scenario=scenario(2, tasks=1, rho=0.5))
        b = env.bench
        b.robots[0].node, b.robots[1].node = chosen_node, other_node
        b._invalidate()
        env.pairs = b.candidate_pairs()
        action = next(i for i, (r, _, _) in enumerate(env.pairs) if r is b.robots[0])
        task = env.pairs[action][1]
        _, reward, done, info = env.step(action)
        self.assertTrue(done)
        return reward, info, b.path_cost(chosen_node, task.target), task

    def test_reward_independent_of_whether_chosen_robot_is_cheapest(self):
        env = AllocationEnvV2(seed=0, center=False)
        env.reset(scenario=scenario(2, tasks=1, rho=0.5))
        target = env.pairs[0][1].target
        b = env.bench
        nodes = sorted(b.g.G.nodes, key=lambda n: b.path_cost(n, target))
        mid = nodes[len(nodes) // 2]
        # meme robot choisi (meme position), l'autre robot plus proche ou plus loin
        r_close, i_close, _, _ = self._reward_choosing(mid, nodes[0])
        r_far, i_far, cost, _ = self._reward_choosing(mid, nodes[-1])
        self.assertFalse(i_close['chosen_is_min_cost'])
        self.assertTrue(i_far['chosen_is_min_cost'])
        self.assertAlmostEqual(r_close, r_far, places=9)
        # et la recompense est exactement le temps de service estime, sans bonus
        expected = -(cost / b.speed + b.pick_time) / REWARD_NORM_S
        self.assertAlmostEqual(r_far, expected, places=9)

    def test_choosing_the_cheapest_robot_only_saves_its_travel_time(self):
        env = AllocationEnvV2(seed=0, center=False)
        env.reset(scenario=scenario(2, tasks=1, rho=0.5))
        target = env.pairs[0][1].target
        b = env.bench
        nodes = sorted(b.g.G.nodes, key=lambda n: b.path_cost(n, target))
        near, far = nodes[0], nodes[-1]
        r_near, _, c_near, _ = self._reward_choosing(near, far)
        r_far, _, c_far, _ = self._reward_choosing(far, near)
        saved_travel = (c_far - c_near) / b.speed / REWARD_NORM_S
        self.assertAlmostEqual(r_near - r_far, saved_travel, places=9)

    def test_queue_waiting_time_is_charged(self):
        env = AllocationEnvV2(seed=5, center=False)
        env.reset(scenario=scenario(3, tasks=60, rho=0.9))
        waits = []
        done = False
        while not done:
            _, _, done, info = env.step(0)
            waits.append(info['queue_wait_s'])
        self.assertGreater(sum(waits), 0.0)


class TestDeterminism(unittest.TestCase):
    def _rollout(self, seed):
        env = AllocationEnvV2(seed=seed, n_tasks=40)
        rng = random.Random(123)
        trace = []
        for _ in range(2):
            obs, info = env.reset()
            trace.append(repr(info['scenario']))
            done = info['done']
            while not done:
                a = rng.randrange(len(obs))
                obs, r, done, inf = env.step(a)
                trace.append((round(r, 12), obs.round(9).tobytes()))
            trace.append(inf['metrics']['temps_traitement_moy_s'])
        return trace

    def test_env_is_deterministic_with_fixed_seed(self):
        self.assertEqual(self._rollout(7), self._rollout(7))
        self.assertNotEqual(self._rollout(7), self._rollout(8))

    def test_benchmark_drl2_methods_are_deterministic(self):
        for method in ('drl2_direct', 'drl2_hybrid', 'greedy_pair'):
            a = make_benchmark(method, scenario(4, tasks=40, block_rate=1 / 60),
                               agent2=MinCostScorer()).run()
            b = make_benchmark(method, scenario(4, tasks=40, block_rate=1 / 60),
                               agent2=MinCostScorer()).run()
            self.assertEqual(a, b, method)
            self.assertEqual(a['taches_finies'] + a['taches_echouees'], 40)

    def test_drl2_direct_with_min_cost_scores_equals_greedy_pair(self):
        a = make_benchmark('drl2_direct', scenario(3, tasks=40), agent2=MinCostScorer()).run()
        b = make_benchmark('greedy_pair', scenario(3, tasks=40)).run()
        self.assertEqual(a, b)

    @unittest.skipUnless(HAVE_TORCH, 'PyTorch absent')
    def test_pair_dqn_seeded_initialisation_and_training(self):
        from warehouse_marl.drl.pair_dqn import PairDQN

        def run(seed):
            agent = PairDQN(seed=seed, warmup=8, batch_size=8)
            env = AllocationEnvV2(seed=seed, n_tasks=20)
            obs, _ = env.reset()
            out = [agent.scores(obs).round(6).tolist()]
            done = False
            while not done:
                a = agent.act(obs, epsilon=0.3)
                nxt, r, done, _ = env.step(a)
                agent.remember(obs[a], r, nxt, done)
                st = agent.train_step()
                if st:
                    out.append(round(st['loss'], 6))
                obs = nxt
            return out
        self.assertEqual(run(4), run(4))


class TestCalibratedBias(unittest.TestCase):
    def test_bias_is_zero_mean_and_favours_high_q(self):
        bias = calibrated_bias([1.0, 2.0, 3.0], weight=1.0, scale_m=30.0)
        self.assertAlmostEqual(sum(bias), 0.0)
        self.assertLess(bias[2], bias[0])          # Q eleve -> cout plus faible
        self.assertAlmostEqual(bias[0] - bias[2], 60.0)
        self.assertEqual(calibrated_bias([5.0], 1.0, 30.0), [0.0])
        self.assertTrue(all(math.isclose(b, 0.0) for b in
                            calibrated_bias([1.0, 2.0], weight=0.0, scale_m=30.0)))


if __name__ == '__main__':
    unittest.main()
