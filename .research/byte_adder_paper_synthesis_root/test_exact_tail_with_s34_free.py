from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
SUBJECT = HERE / "exact_tail_with_s34_free.py"


def load_subject():
    spec = importlib.util.spec_from_file_location("test_s34_free_subject", SUBJECT)
    if spec is None or spec.loader is None:
        raise RuntimeError(SUBJECT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


subject = load_subject()


class S34FreeDomainTests(unittest.TestCase):
    def test_full_domain_and_provenance(self):
        domain, provenance = subject.build_domain_with_provenance()
        self.assertEqual(domain.rows, 486)
        self.assertEqual(domain.output_names, ("S5", "S6", "S7", "C8"))
        self.assertEqual(domain.names[-7:], tuple(f"s34_u{i}" for i in range(7)))
        self.assertEqual(
            [domain.arrivals[f"s34_u{i}"] for i in range(7)],
            [3, 4, 4, 3, 4, 4, 5],
        )
        self.assertTrue(provenance["u6_equals_s3"])
        self.assertEqual(
            [node["kind"] for node in provenance["exported_nodes"]],
            ["NOR", "NAND", "AND", "AND", "OR", "OR", "NAND"],
        )
        self.assertTrue(
            all(node["always_driven"] for node in provenance["exported_nodes"])
        )
        self.assertEqual(
            [node["kind"] for node in provenance["excluded_nodes"]],
            ["SWITCH", "SWITCH"],
        )

    def test_exported_u6_equals_original_s3(self):
        domain = subject.build_domain()
        base = subject.physical.domain_s34567c8_leaf()
        u6 = domain.columns[domain.names.index("s34_u6")]
        packed = sum(int(value) << case for case, value in enumerate(u6))
        self.assertEqual(packed, base.targets[base.output_names.index("S3")])

    def test_zero_component_direct_source_positive_regression(self):
        domain = subject.build_domain()
        u6 = domain.columns[domain.names.index("s34_u6")]
        probe = subject.physical.Domain(
            domain.names,
            domain.columns,
            (sum(int(value) << case for case, value in enumerate(u6)),),
            domain.arrivals,
            ("S3_probe",),
        )
        name = "s34_u6_positive_probe"
        subject.physical.DOMAINS[name] = lambda: probe
        args = argparse.Namespace(
            domain=name,
            outputs=None,
            gate_bound=0,
            max_delay=5,
            components=0,
            switches=0,
            xors=0,
            fixed_kinds=None,
            split_slots=0,
            shard_count=1,
            shard_index=0,
            solver="glucose42",
            timeout=0.0,
        )
        payload = subject.physical.solve(args)
        self.assertEqual(payload["status"], "sat")
        self.assertEqual(payload["actual_gate"], 0)
        self.assertEqual(payload["verification"]["mismatch_count"], 0)
        self.assertEqual(payload["verification"]["undriven_output_count"], 0)
        self.assertEqual(payload["verification"]["actual_max_delay"], 5)


if __name__ == "__main__":
    unittest.main()
