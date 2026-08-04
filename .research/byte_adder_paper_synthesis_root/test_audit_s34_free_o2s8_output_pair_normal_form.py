from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
SUBJECT = HERE / "audit_s34_free_o2s8_output_pair_normal_form.py"


def load_subject():
    spec = importlib.util.spec_from_file_location("test_o2s8_normal_form", SUBJECT)
    if spec is None or spec.loader is None:
        raise RuntimeError(SUBJECT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


subject = load_subject()


class PairSwitchOracleTests(unittest.TestCase):
    def test_oracle_matches_bruteforce_on_small_problem(self):
        mask = 0b1111
        base = (0, mask, 0b0011, 0b0101)
        targets = (0b0000, 0b0110, 0b1001, 0b1111)
        candidates = (0b0001, 0b0010, 0b0110, 0b1001, 0b1100)
        for target in targets:
            oracle = subject.PairSwitchOracle(base, target, mask)
            for first in candidates:
                for second in candidates:
                    self.assertEqual(
                        oracle.accepts(first, second),
                        subject.brute_pair_switch_repr(
                            base, first, second, target, mask
                        ),
                    )

    def test_full_audit_counts(self):
        payload = subject.audit()
        self.assertEqual(payload["status"], "unsat_within_normal_form")
        self.assertFalse(payload["global_o2s8_lower_bound_proved"])
        self.assertEqual(payload["domain"]["rows"], 486)
        self.assertEqual(payload["domain"]["base_source_count"], 35)
        self.assertEqual(
            payload["independent"]["unique_one_gate_functions_d4"], 1118
        )
        self.assertEqual(payload["independent"]["unordered_function_pairs"], 625521)
        self.assertEqual(
            payload["independent"]["representable_pair_count_by_target"],
            {name: 0 for name in subject.TARGETS},
        )
        self.assertEqual(
            payload["dependent_chain"]["unique_first_gate_functions_d3"], 752
        )
        self.assertEqual(payload["dependent_chain"]["topological_function_pairs"], 67847)
        self.assertEqual(
            payload["dependent_chain"]["representable_pair_count_by_target"],
            {name: 0 for name in subject.TARGETS},
        )


if __name__ == "__main__":
    unittest.main()
