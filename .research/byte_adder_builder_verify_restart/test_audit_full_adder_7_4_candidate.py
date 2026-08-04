from __future__ import annotations

from dataclasses import replace
import importlib.util
from pathlib import Path
import sys
import unittest

from tc_save_lab.codec import encode_v15
from tc_save_lab.model import Circuit


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
MODULE_PATH = HERE / "audit_full_adder_7_4_candidate.py"
FIXTURE_PATH = (
    PROJECT_ROOT
    / ".research"
    / "byte_adder_hybrid_native_agent"
    / "full_adder_macro"
    / "current_full_adder_7_4.json"
)

SPEC = importlib.util.spec_from_file_location("audit_full_adder_7_4_candidate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class FullAdderSevenFourAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import json

        cls.circuit = Circuit.from_dict(json.loads(FIXTURE_PATH.read_text(encoding="utf-8")))
        cls.payload = encode_v15(cls.circuit)

    def test_reviewed_primitive_fixture_passes_full_chain(self) -> None:
        circuit, report = AUDIT.verify_candidate(FIXTURE_PATH, self.payload)
        self.assertEqual(circuit, self.circuit)
        self.assertEqual(report["status"], "verified")
        self.assertEqual(report["score"]["declared"], [7, 4, 28])
        self.assertEqual(report["score"]["replayed"], [7, 4, 28])
        self.assertEqual(report["truth_protocol"]["vectors"], 8)
        self.assertEqual(report["truth_protocol"]["mismatch_count"], 0)
        self.assertEqual(report["structure"]["native_com_full_adder_count"], 0)
        self.assertEqual(report["timing_and_ownership"]["dead_primitive_count"], 0)
        self.assertEqual(report["geometry"]["unsupported_component_kinds"], ())
        self.assertEqual(report["geometry"]["component_overlap_cells"], ())
        self.assertEqual(report["geometry"]["wire_collisions"], ())
        self.assertEqual(report["geometry"]["wire_interior_pin_contacts"], ())

    def test_header_only_score_claim_is_rejected(self) -> None:
        bad = replace(self.circuit, gate=6)
        with self.assertRaisesRegex(AUDIT.AuditError, "declared score"):
            AUDIT.verify_candidate(FIXTURE_PATH, encode_v15(bad))

    def test_recursive_native_full_adder_is_rejected(self) -> None:
        components = list(self.circuit.components)
        primitive_index = next(
            index for index, component in enumerate(components) if component.kind == 4
        )
        components[primitive_index] = replace(components[primitive_index], kind=15)
        bad = replace(self.circuit, components=tuple(components))
        with self.assertRaisesRegex(AUDIT.AuditError, "unexpected component kinds"):
            AUDIT.verify_candidate(FIXTURE_PATH, encode_v15(bad))


if __name__ == "__main__":
    unittest.main()
