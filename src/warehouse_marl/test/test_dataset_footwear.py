"""Tests du jeu de donnees reel (dataset_footwear.py).

Ignores si les CSV ne sont pas presents (WAREHOUSE_FOOTWEAR_DIR ou
~/warehouse_ws/data/footwear)."""

import os
import unittest

from warehouse_marl.allocation_benchmark import build_grid_warehouse
from warehouse_marl.dataset_footwear import (
    FootwearDataset, default_data_dir, load_dataset, project_locations, read_picking_waves,
    read_storage_locations)

HAVE_DATA = os.path.isfile(os.path.join(default_data_dir(), 'Picking_Wave.csv'))


@unittest.skipUnless(HAVE_DATA, 'jeu de donnees footwear absent')
class TestReading(unittest.TestCase):
    def test_storage_locations(self):
        locs = read_storage_locations()
        self.assertEqual(len(locs), 2292)
        a = locs['A-14-11']
        self.assertEqual((a.x, a.y, a.z), (368.0, 0.0, 1.0))

    def test_picking_waves_file_order(self):
        lines = read_picking_waves()
        self.assertEqual(len(lines), 215192)
        self.assertEqual(len({p.wave for p in lines}), 9707)
        first = lines[0]
        self.assertEqual((first.wave, first.reference, first.location, first.operator),
                         (43175, '8N10W9', 'H-06-13', 'Operator_1'))
        self.assertTrue(all(p.quantity >= 1 for p in lines))


@unittest.skipUnless(HAVE_DATA, 'jeu de donnees footwear absent')
class TestSplit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds = load_dataset()

    def test_no_test_wave_in_training(self):
        ds = self.ds
        train, test = set(ds.waves_of('train')), set(ds.waves_of('test'))
        self.assertTrue(train and test)
        self.assertFalse(train & test)
        self.assertLess(max(train), min(test))              # separation temporelle
        fit, val = set(ds.waves_of('train_fit')), set(ds.waves_of('train_val'))
        self.assertFalse(fit & val)
        self.assertEqual(fit | val, train)
        self.assertLess(max(fit), min(val))
        for split in ('train_fit', 'train_val'):
            for s in ds.window_starts(split, 80)[::500]:
                self.assertFalse({p.wave for p in ds.window(split, s, 80)} & test)

    def test_chronological_order_and_split_sizes(self):
        ds = self.ds
        self.assertEqual(ds.waves, sorted(ds.waves))
        self.assertEqual(round(0.7 * len(ds.waves)),
                         len([w for w in ds.waves if ds.wave_split[w] == 'train']))
        n = sum(len(ds.lines[s]) for s in ('train', 'test'))
        self.assertEqual(n + sum(ds.excluded.values()), ds.n_raw_lines)
        for split in ('train', 'test'):
            keys = [(p.wave, p.row) for p in ds.lines[split]]
            self.assertEqual(keys, sorted(keys))

    def test_windows_start_on_wave_boundaries(self):
        ds = self.ds
        lines = ds.lines['test']
        for s in ds.window_starts('test', 150)[:50]:
            self.assertTrue(s == 0 or lines[s].wave != lines[s - 1].wave)

    def test_determinism(self):
        other = FootwearDataset()
        for split in ('train_fit', 'test'):
            self.assertEqual(self.ds.lines[split], other.lines[split])
        g = build_grid_warehouse(5, 3)
        s = self.ds.evenly_spaced_start('test', 150, 3, 10)
        self.assertEqual(self.ds.targets(g, 'test', s, 150), other.targets(g, 'test', s, 150))


@unittest.skipUnless(HAVE_DATA, 'jeu de donnees footwear absent')
class TestProjection(unittest.TestCase):
    def test_projection_preserves_coordinate_order(self):
        locs = read_storage_locations()
        for dims in ((5, 3), (8, 5), (15, 10)):
            graph = build_grid_warehouse(*dims)
            proj = project_locations(locs, *dims)
            self.assertTrue(set(proj.values()) <= set(graph.G.nodes))
            items = sorted(locs.values(), key=lambda p: p.x)
            cols = [int(proj[p.code].split('_')[2]) for p in items]
            self.assertEqual(cols, sorted(cols))
            items = sorted(locs.values(), key=lambda p: p.y)
            rows = [int(proj[p.code].split('_')[1]) for p in items]
            self.assertEqual(rows, sorted(rows, reverse=True))   # rangee 0 = plus grand y
            gy = [graph.G.nodes[proj[p.code]]['y'] for p in items]
            self.assertEqual(gy, sorted(gy))                   # meme ordre en y dans le graphe

    def test_extreme_locations_hit_grid_corners(self):
        locs = read_storage_locations()
        proj = project_locations(locs, 5, 3)
        xmin = min(locs.values(), key=lambda p: p.x)
        xmax = max(locs.values(), key=lambda p: p.x)
        self.assertTrue(proj[xmin.code].endswith('_0'))
        self.assertTrue(proj[xmax.code].endswith('_2'))


@unittest.skipUnless(HAVE_DATA, 'jeu de donnees footwear absent')
class TestBenchmarkTasks(unittest.TestCase):
    def test_benchmark_uses_test_waves_in_order(self):
        from warehouse_marl.drl.env_v2 import make_benchmark
        ds = load_dataset()
        test_waves = set(ds.waves_of('test'))
        for k in range(10):
            start = ds.evenly_spaced_start('test', 150, k, 10)
            window = ds.window('test', start, 150)
            self.assertTrue({p.wave for p in window} <= test_waves)
            sc = dict(dims=(5, 3), robots=3, rho=0.7, tasks=150, seed=k,
                      footwear={'split': 'test', 'start': start})
            b = make_benchmark('fifo', sc)
            proj = ds.projection(b.g)
            self.assertEqual([t.target for t in b.arrivals], [proj[p.location] for p in window])
            self.assertTrue(all(t.priority == 1.0 for t in b.arrivals))

    def test_footwear_runs_are_deterministic(self):
        from warehouse_marl.drl.env_v2 import make_benchmark
        ds = load_dataset()
        sc = dict(dims=(8, 5), robots=6, rho=0.9, tasks=80, seed=5,
                  footwear={'split': 'test', 'start': ds.evenly_spaced_start('test', 80, 2, 10)})
        self.assertEqual(make_benchmark('greedy_pair', sc).run(),
                         make_benchmark('greedy_pair', sc).run())

    def test_same_load_uses_empirical_service_time(self):
        ds = load_dataset()
        g = build_grid_warehouse(5, 3)
        from warehouse_marl.allocation_benchmark import mean_service_time
        self.assertLess(ds.service_time(g, 0.5, 10.0), mean_service_time(g, 0.5, 10.0))
        self.assertEqual(ds.service_time(g, 0.5, 10.0), ds.service_time(g, 0.5, 10.0))


if __name__ == '__main__':
    unittest.main()
