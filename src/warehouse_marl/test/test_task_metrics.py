"""Synthese des statuts de taches (task_metrics), sans ROS."""

import json
import math
import unittest

from warehouse_marl.task_metrics import parse_status, summarize


def row(mode, tid, state, elapsed=None, robot='robot1'):
    d = {'task_id': tid, 'robot_id': robot, 'state': state, 'stamp': 1.0}
    if elapsed is not None:
        d['elapsed_sec'] = elapsed
    return parse_status(json.dumps(d), mode, 0.0)


class TestTaskMetrics(unittest.TestCase):
    def test_parse(self):
        r = row('heuristic', 'T1', 'succeeded', 12.5)
        self.assertEqual((r['task_id'], r['state'], r['elapsed_sec']), ('T1', 'succeeded', 12.5))
        self.assertIsNone(parse_status('pas du json', 'm', 0.0))
        self.assertIsNone(parse_status('{"state": "queued"}', 'm', 0.0))

    def test_summary_counts_final_states_per_mode(self):
        rows = [row('h', 'T1', 'queued'), row('h', 'T1', 'navigating'),
                row('h', 'T1', 'succeeded', 10.0),
                row('h', 'T2', 'retrying'), row('h', 'T2', 'failed', 40.0),
                row('h', 'T3', 'succeeded', 20.0), row('h', 'T4', 'navigating'),
                row('y', 'T1', 'succeeded', 30.0)]
        table = {r['mode']: r for r in summarize(rows)}
        h = table['h']
        self.assertEqual((h['taches_vues'], h['terminees'], h['echouees'],
                          h['en_cours_a_la_fin']), (4, 2, 1, 1))
        self.assertEqual(h['temps_moyen_s'], 15.0)
        self.assertEqual(h['temps_median_s'], 15.0)
        self.assertLessEqual(h['ic95_bas_s'], 15.0)
        self.assertGreaterEqual(h['ic95_haut_s'], 15.0)
        y = table['y']
        self.assertEqual(y['terminees'], 1)
        self.assertTrue(math.isnan(y['ic95_bas_s']))          # une seule valeur


if __name__ == '__main__':
    unittest.main()
