"""Graphe dynamique en ligne : logique de /warehouse/blocked_edges (sans ROS)."""

import json
import math
import unittest

from warehouse_marl.dynamic_blocking import (
    EdgeBlockManager, FailureTracker, access_edge, block_message, parse_block_message)
from warehouse_marl.warehouse_graph import build_demo_warehouse


def msg(u, v, blocked=True, duration=60.0):
    return parse_block_message(json.dumps({'u': u, 'v': v, 'blocked': blocked,
                                           'duration_s': duration}))


class TestParse(unittest.TestCase):
    def test_valid_and_invalid_messages(self):
        m = msg('shelf_0_0', 'shelf_0_1')
        self.assertEqual((m['u'], m['v'], m['blocked'], m['duration_s']),
                         ('shelf_0_0', 'shelf_0_1', True, 60.0))
        for bad in ('pas du json', '{"u": "a"}', '{"u": "a", "v": "b", "blocked": "oui"}',
                    '{"u": "a", "v": "b", "duration_s": -5}', '[1, 2]'):
            with self.assertRaises(ValueError):
                parse_block_message(bad)
        self.assertEqual(parse_block_message(block_message('a', 'b', 60, 's', 'r'))['u'], 'a')


class TestEdgeBlockManager(unittest.TestCase):
    def setUp(self):
        self.g = build_demo_warehouse()
        self.m = EdgeBlockManager(self.g)

    def test_block_both_directions_then_expire(self):
        self.assertTrue(self.m.apply(msg('shelf_0_0', 'shelf_0_1', duration=60), now=10.0))
        self.assertTrue(math.isinf(self.g.edge_cost('shelf_0_0', 'shelf_0_1')))
        self.assertTrue(math.isinf(self.g.edge_cost('shelf_0_1', 'shelf_0_0')))
        path, _ = self.g.shortest_path('shelf_0_0', 'shelf_0_1')
        self.assertNotIn(('shelf_0_0', 'shelf_0_1'), list(zip(path, path[1:])))
        self.assertEqual(self.m.expire(69.9), [])
        self.assertEqual(self.m.expire(70.0), [('shelf_0_0', 'shelf_0_1')])
        self.assertFalse(math.isinf(self.g.edge_cost('shelf_0_0', 'shelf_0_1')))

    def test_unblock_message_and_indefinite_block(self):
        self.m.apply(msg('shelf_1_1', 'shelf_2_1', duration=0), now=0.0)
        self.assertEqual(self.m.expire(1e9), [])               # sans echeance
        self.assertTrue(self.m.apply(msg('shelf_2_1', 'shelf_1_1', blocked=False), now=5.0))
        self.assertFalse(math.isinf(self.g.edge_cost('shelf_1_1', 'shelf_2_1')))
        self.assertFalse(self.m.apply(msg('shelf_2_1', 'shelf_1_1', blocked=False), now=6.0))

    def test_unknown_edge_is_ignored_and_reblock_extends(self):
        self.assertFalse(self.m.apply(msg('shelf_0_0', 'shelf_4_2'), now=0.0))
        self.m.apply(msg('shelf_0_0', 'shelf_0_1', duration=60), now=0.0)
        self.assertFalse(self.m.apply(msg('shelf_0_1', 'shelf_0_0', duration=60), now=30.0))
        self.assertEqual(self.m.expire(60.0), [])                # prolonge jusqu'a 90 s
        self.assertEqual(len(self.m.expire(90.0)), 1)


class TestFailureTracker(unittest.TestCase):
    def test_threshold_window_and_reset(self):
        t = FailureTracker(threshold=2, window_s=100)
        self.assertFalse(t.record_failure('shelf_2_1', 0.0))
        self.assertTrue(t.record_failure('shelf_2_1', 50.0))
        self.assertFalse(t.record_failure('shelf_2_1', 60.0))    # compteur remis a zero
        self.assertFalse(t.record_failure('shelf_0_0', 0.0))
        self.assertFalse(t.record_failure('shelf_0_0', 150.0))   # hors fenetre
        t.record_success('shelf_0_0')
        self.assertFalse(t.record_failure('shelf_0_0', 160.0))


class TestAccessEdge(unittest.TestCase):
    def test_access_edge_is_last_edge_of_path_from_entry(self):
        g = build_demo_warehouse()
        for target in ('shelf_0_0', 'shelf_4_2', 'station_A'):
            u, v = access_edge(g, target)
            self.assertEqual(v, target)
            self.assertTrue(g.G.has_edge(u, v))
            path, _ = g.shortest_path('charging_dock', target)
            self.assertEqual((u, v), (path[-2], path[-1]))
        self.assertIsNone(access_edge(g, 'inconnu'))
        u, v = access_edge(g, 'charging_dock')       # cible = entree : voisin le plus proche
        self.assertEqual(v, 'charging_dock')

    def test_blocking_access_edge_reroutes(self):
        g = build_demo_warehouse()
        m = EdgeBlockManager(g)
        u, v = access_edge(g, 'shelf_0_0')
        before = g.shortest_path('charging_dock', 'shelf_0_0')[1]
        m.apply(msg(u, v), now=0.0)
        after_path, after = g.shortest_path('charging_dock', 'shelf_0_0')
        self.assertGreater(after, before)
        self.assertNotIn((u, v), list(zip(after_path, after_path[1:])))


if __name__ == '__main__':
    unittest.main()
