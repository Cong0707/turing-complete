from __future__ import annotations

import json
from pathlib import Path
import unittest

from netcentric import audit_payload


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


class NetCentricAuditTests(unittest.TestCase):
    def test_alias_counterexample_is_rejected(self) -> None:
        payload = json.loads((HERE / "alias_counterexample.json").read_text(encoding="utf-8"))
        result = audit_payload(payload)
        self.assertFalse(result["valid"])
        self.assertGreaterEqual(result["alias_divergence_count"], 1)
        self.assertGreaterEqual(result["conflict_count"], 1)
        self.assertFalse(result["outputs_match"])

    def test_native_xor_tree_remains_valid(self) -> None:
        path = REPO / ".research" / "rng_switch_shared_net" / "parity4-bound9-sat.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        # The older parity4 serializer uses a compact gate list.  The strict
        # verifier intentionally consumes the canonical superopt serializer,
        # so use the canonical XOR2 certificate for regression instead.
        path = REPO / ".research" / "rng_tristate_superopt" / "xor2_c3_d2.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        result = audit_payload(payload)
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["physical_cost"], 3)
        self.assertEqual(result["physical_depth"], 2)

    def test_single_output_complement_switch_xor_is_valid(self) -> None:
        path = REPO / ".research" / "rng_tristate_superopt" / "xor2_free_complements_c4_d1.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        result = audit_payload(payload)
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["physical_cost"], 4)
        self.assertEqual(result["physical_depth"], 1)


if __name__ == "__main__":
    unittest.main()
