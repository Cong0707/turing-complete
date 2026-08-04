from __future__ import annotations

import importlib.util
import itertools
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
SUBJECT = HERE / "run_s34_free_tail_o2s8_positions.py"


def load_subject():
    spec = importlib.util.spec_from_file_location("test_s34_free_o2s8_positions", SUBJECT)
    if spec is None or spec.loader is None:
        raise RuntimeError(SUBJECT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


subject = load_subject()


class PositionSweepTests(unittest.TestCase):
    def test_complete_unique_position_cover(self):
        rows = subject.placements()
        expected = set(itertools.combinations(range(subject.COMPONENTS), 2))
        self.assertEqual(len(rows), 45)
        self.assertEqual(len(set(rows)), 45)
        self.assertEqual(set(rows), expected)

    def test_each_wildcard_pair_is_forced_ordinary_by_exact_quota(self):
        for pair in subject.placements():
            kinds = subject.fixed_kinds(pair)
            self.assertEqual(len(kinds), 10)
            self.assertEqual(kinds.count("*"), 2)
            self.assertEqual(kinds.count("SWITCH"), 8)
            self.assertEqual(tuple(index for index, kind in enumerate(kinds) if kind == "*"), pair)

    def test_priority_starts_with_strict_interleaves(self):
        rows = subject.placements()
        classes = [subject.placement_class(*pair) for pair in rows]
        self.assertEqual(classes[0], "strict_switch_ordinary_switch")
        rank = {
            "strict_switch_ordinary_switch": 0,
            "switch_ordinary_terminal_ordinary": 1,
            "early_ordinary_interleaved": 2,
            "ordinary_edge_normal_form": 3,
        }
        self.assertEqual([rank[name] for name in classes], sorted(rank[name] for name in classes))


if __name__ == "__main__":
    unittest.main()
