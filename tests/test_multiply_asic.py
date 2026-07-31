from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import unittest

from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.multiply_asic import (
    DECLARED_DELAY,
    DECLARED_GATE,
    MULTIPLIER_KIND,
    audit_connectivity,
    audit_geometry,
    build_multiply_circuit,
    candidate_metadata,
    simulate_multiply,
    verify_multiply_truth_table,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class MultiplyAsicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.circuit = build_multiply_circuit(PROJECT_ROOT)

    def test_current_native_multiplier_shape_and_frontier_header(self) -> None:
        self.assertEqual(self.circuit.gate, DECLARED_GATE)
        self.assertEqual(self.circuit.delay, DECLARED_DELAY)
        self.assertEqual(self.circuit.energy, 2530)
        multiplier = [component for component in self.circuit.components if component.kind == MULTIPLIER_KIND]
        self.assertEqual(len(multiplier), 1)
        self.assertEqual(multiplier[0].word_size, 8)
        self.assertEqual(len(self.circuit.components), 4)
        self.assertEqual(len(self.circuit.wires), 3)

    def test_v15_round_trip_is_lossless(self) -> None:
        payload = encode_v15(self.circuit)
        self.assertEqual(payload[0], 15)
        self.assertEqual(decode_v15(payload), self.circuit)

    def test_endpoint_connectivity_is_complete(self) -> None:
        audit = audit_connectivity(self.circuit)
        self.assertEqual(audit.unconnected_inputs, ())
        self.assertEqual(audit.multi_driver_network_count, 0)
        self.assertEqual(audit.undriven_network_count, 0)
        self.assertEqual(audit.sinkless_network_count, 0)
        self.assertEqual(audit.width_mismatch_network_count, 0)
        self.assertEqual(audit.endpoint_non_pin_count, 0)

    def test_current_sprite_alpha_geometry_is_clean(self) -> None:
        audit = audit_geometry(self.circuit)
        self.assertEqual(audit.sprite_files, (
            "com_level_input_word.png",
            "com_level_output_word.png",
            "com_mul.png",
        ))
        self.assertEqual(audit.component_overlap_cells, ())
        self.assertEqual(audit.wire_component_collisions, ())
        self.assertEqual(audit.wire_interior_pin_contacts, ())
        self.assertEqual(audit.endpoint_non_pin_count, 0)

    def test_all_u8_input_pairs(self) -> None:
        self.assertEqual(verify_multiply_truth_table(self.circuit), 65536)

    def test_selected_boundary_vectors_use_lower_byte_only(self) -> None:
        vectors = {
            (0x00, 0xFF): 0x00,
            (0x01, 0xFF): 0xFF,
            (0x10, 0x10): 0x00,
            (0x7F, 0x7F): 0x01,
            (0xFF, 0xFF): 0x01,
        }
        for (a, b), expected in vectors.items():
            with self.subTest(a=a, b=b):
                self.assertEqual(simulate_multiply(self.circuit, a, b), expected)

    def test_generated_candidate_artifacts_are_current(self) -> None:
        path = PROJECT_ROOT / "examples" / "multiply" / "candidate" / "circuit.data"
        metadata_path = path.with_name("metadata.json")
        payload = path.read_bytes()
        self.assertEqual(decode_v15(payload), self.circuit)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata, candidate_metadata(self.circuit))
        self.assertEqual(metadata["sha256"], sha256(payload).hexdigest())


if __name__ == "__main__":
    unittest.main()
