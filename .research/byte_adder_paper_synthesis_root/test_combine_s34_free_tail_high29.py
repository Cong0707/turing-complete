from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
SUBJECT = HERE / "combine_s34_free_tail_high29.py"


def load_subject():
    spec = importlib.util.spec_from_file_location("test_s34_free_combiner", SUBJECT)
    if spec is None or spec.loader is None:
        raise RuntimeError(SUBJECT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


subject = load_subject()


class S34FreeCombinerTests(unittest.TestCase):
    def setUp(self):
        self.s34 = subject.load_witness(
            subject.S34_DEFAULT, outputs=("S3", "S4"), gate=11
        )

    def test_global_source_mapping(self):
        domain, names, network, outputs, exported, next_source = (
            subject.build_s34_context(self.s34)
        )
        self.assertEqual(domain.rows, 486)
        self.assertEqual(len(names), 29)
        self.assertEqual(len(network), 9)
        self.assertEqual(next_source, 38)
        self.assertEqual(exported, {f"s34_u{i}": 29 + i for i in range(7)})
        tail_map = subject.build_tail_free_map(names, exported)
        self.assertEqual(tail_map["0"], 27)
        self.assertEqual(tail_map["1"], 28)
        self.assertEqual(tail_map["s34_u6"], 35)
        self.assertEqual(len(outputs), 2)

    def test_restored_s34_network_is_exact(self):
        domain, names, network, outputs, _exported, _next_source = (
            subject.build_s34_context(self.s34)
        )
        arrivals = [domain.arrivals.get(name, 0) for name in names]
        structure = subject._audit_structure(
            network,
            outputs,
            source_count=len(names),
            source_arrivals=arrivals,
        )
        semantics = subject._audit_semantics(
            domain, network, outputs, ("S3", "S4")
        )
        self.assertEqual(structure["gate"], 11)
        self.assertEqual(structure["actual_output_arrivals"], [5, 5])
        self.assertEqual(structure["physical_net_partition_violation_count"], 0)
        self.assertEqual(structure["dead_component_output_count"], 0)
        self.assertEqual(structure["errors"], [])
        self.assertEqual(semantics["mismatch_count"], 0)
        self.assertEqual(semantics["bus_conflict_count"], 0)
        self.assertEqual(semantics["undriven_output_count"], 0)

    def test_not_with_nonempty_right_bus_is_rejected(self):
        domain = subject.physical.domain_s34567c8_leaf()
        names = (*domain.names, "0", "1")
        arrivals = [domain.arrivals.get(name, 0) for name in names]
        source_count = len(names)
        structure = subject._audit_structure(
            [
                {
                    "slot": 0,
                    "source": source_count,
                    "kind": "NOT",
                    "left_bus": [0],
                    "right_bus": [1],
                    "cost": 1,
                    "depth_upper_bound": 4,
                }
            ],
            [[source_count]],
            source_count=source_count,
            source_arrivals=arrivals,
        )
        self.assertIn("NOT has a nonempty right bus at 0", structure["errors"])


if __name__ == "__main__":
    unittest.main()
