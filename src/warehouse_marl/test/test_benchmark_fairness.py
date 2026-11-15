"""Equite du banc : toutes les methodes voient les memes blocages et les
memes arrivees pour une graine donnee (generateurs separes)."""

import unittest

from warehouse_marl.drl.env_v2 import make_benchmark

METHODS = ('fifo', 'greedy_pair', 'greedy_time', 'consensus', 'random')


def run(method, seed, loss=0.0, block_rate=6 / 60):
    b = make_benchmark(method, dict(dims=(5, 3), robots=3, rho=0.7, block_rate=block_rate,
                                    tasks=120, seed=seed, loss=loss))
    b.run()
    return b


class TestFairness(unittest.TestCase):
    def test_all_methods_see_the_same_blockages(self):
        for seed in (7, 1007):
            for loss in (0.0, 0.3):
                runs = {m: run(m, seed, loss) for m in METHODS}
                horizon = min(b.t for b in runs.values())
                ref = [x for x in runs['fifo'].block_log if x[0] < horizon]
                self.assertGreater(len(ref), 10)
                for m, b in runs.items():
                    got = [x for x in b.block_log if x[0] < horizon]
                    self.assertEqual(got, ref, f'{m}, graine {seed}, perte {loss}')

    def test_all_methods_see_the_same_arrivals(self):
        runs = {m: run(m, 3, 0.3) for m in METHODS}
        ref = [(k.task_id, k.target, k.priority, k.created) for k in runs['fifo'].arrivals]
        for m, b in runs.items():
            self.assertEqual([(k.task_id, k.target, k.priority, k.created) for k in b.arrivals],
                             ref, m)

    def test_message_loss_does_not_change_the_world(self):
        a, b = run('consensus', 11, 0.0), run('consensus', 11, 0.5)
        horizon = min(a.t, b.t)
        self.assertEqual([x for x in a.block_log if x[0] < horizon],
                         [x for x in b.block_log if x[0] < horizon])


if __name__ == '__main__':
    unittest.main()
