from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
SUBJECT = HERE / "combine_tail729_high30_physical_witness.py"


def load_subject():
    spec = importlib.util.spec_from_file_location("test_tail729_high30_combiner", SUBJECT)
    if spec is None or spec.loader is None:
        raise RuntimeError(SUBJECT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


subject = load_subject()


class Tail729High30CombinerTests(unittest.TestCase):
    def test_prefix_restores_family_and_paid_phases(self):
        prefix = subject.build_prefix("primary")
        network = prefix["network"]
        self.assertEqual(len(network), 11)
        self.assertEqual(sum(item["cost"] for item in network), 13)
        self.assertEqual([item["slot"] for item in network], list(range(11)))
        self.assertEqual(
            [item["source"] for item in network],
            list(range(len(subject.NEGATIVE_SOURCES), len(subject.NEGATIVE_SOURCES) + 11)),
        )
        self.assertEqual(prefix["output_buses"], [[32], [33, 35]])
        self.assertEqual(
            prefix["paid_sources"],
            {
                "s34_family1_u0": 27,
                "s34_family1_u1": 28,
                "s34_family1_u2": 29,
                "s34_family1_u3": 30,
                "s34_family1_u4": 31,
                "s34_family1_u7": 34,
                "phase_nor_q6_p7": 36,
                "phase_nor_n4_p5": 37,
            },
        )

    def test_projected_source_mapping_is_exact(self):
        domain, _provenance = subject.tail_worker.build_domain_with_provenance("primary")
        prefix = subject.build_prefix("primary")
        mapped = {name: index for index, name in enumerate(subject.NEGATIVE_SOURCES)}
        mapped.update(prefix["paid_sources"])
        self.assertEqual(tuple(domain.names), tuple(mapped))
        self.assertEqual(len(mapped), 35)
        self.assertEqual(
            (
                subject.production.FIXED_TOTAL_GATE + subject.HIGH_GATE,
                subject.MAX_DELAY,
                (subject.production.FIXED_TOTAL_GATE + subject.HIGH_GATE)
                * subject.MAX_DELAY,
            ),
            (103, 5, 515),
        )

    def test_729_verifier_compatibility_uses_high30_abi(self):
        fixture = (
            subject.ROOT
            / ".research/byte_adder_av_reduced_forward/"
            "negative_high_d5_s34_only_physical729_regression.json"
        )
        review = subject.verify_negative_witness(fixture, fixture=True)
        self.assertEqual(review["status"], "verified")
        self.assertEqual(review["physical_quotient_replay"]["rows"], 729)
        self.assertEqual(review["physical_quotient_replay"]["mismatch_union_count"], 0)
        self.assertEqual(review["full_replay"]["rows"], 131072)
        self.assertEqual(review["full_replay"]["mismatch_union_count"], 0)

    def test_non_sat_tail_is_rejected(self):
        witness = (
            subject.ROOT
            / ".research/byte_adder_phase_shortcut_restart/local-runs/"
            "s34_family1_two_phase_tail729_r1/primary_all_switch.json"
        )
        with self.assertRaisesRegex(RuntimeError, "tail metadata mismatch at status"):
            subject.validate_tail(witness, profile="primary")


if __name__ == "__main__":
    unittest.main()
