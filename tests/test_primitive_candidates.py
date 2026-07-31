from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from tc_save_lab.codec import decode_v15
from tc_save_lab.model import Component
from tc_save_lab.pins import positioned_pins
from tc_save_lab.primitive_candidates import (
    PRIMITIVE_LEVELS,
    build_primitive_circuit,
    verify_primitive_candidate,
    write_primitive_candidates,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PrimitiveCandidateTests(unittest.TestCase):
    def test_current_primitive_port_geometry_is_explicit(self):
        cases = {
            14: {
                "save": ((-3, -3), 1),
                "in": ((-3, 0), 1),
                "out": ((3, 0), 1),
            },
            39: {
                "load": ((-1, -1), 1),
                "save": ((-1, 0), 1),
                "in": ((-1, 1), 8),
                "out": ((1, 0), 8),
            },
            49: {
                "in": ((-1, 0), 8),
                "out": ((2, 0), 8),
            },
        }
        for kind, expected in cases.items():
            component = Component(kind, (0, 0), 0, kind, word_size=8)
            actual = {
                pin.name: (pin.position, pin.width)
                for pin in positioned_pins(component)
            }
            self.assertEqual(actual, expected, kind)

    def test_candidates_are_exhaustive_connected_and_physically_safe(self):
        expected_semantics = {
            "byte_adder": {"exhaustive_truth_table_vector_count": 131072},
            "count_leading_zeroes": {"exhaustive_truth_table_vector_count": 256},
            "saving_gracefully": {
                "script_tick_count": 13,
                "exhaustive_state_transition_count": 8,
            },
            "saving_bytes": {"exhaustive_state_transition_count": 131072},
        }
        expected_scores = {
            "byte_adder": [103, 5, 515],
            "count_leading_zeroes": [22, 4, 88],
            "saving_gracefully": [10, 5, 50],
            "saving_bytes": [73, 5, 365],
        }
        for level in PRIMITIVE_LEVELS:
            circuit = build_primitive_circuit(PROJECT_ROOT, level)
            result = verify_primitive_candidate(circuit, level)
            self.assertEqual(result["leaderboard_tuple"], expected_scores[level])
            self.assertEqual(result["semantic"], expected_semantics[level])
            self.assertEqual(result["layout"], {
                "wire_endpoint_non_pin_count": 0,
                "wire_component_contact_count": 0,
                "wire_interior_pin_contact_count": 0,
                "component_body_overlap_count": 0,
            })
            self.assertEqual(result["connectivity"]["unconnected_pin_count"], 0)
            self.assertEqual(result["connectivity"]["multi_driver_network_count"], 0)

    def test_writer_is_deterministic_and_preserves_scaffold_io(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for level in PRIMITIVE_LEVELS:
                source = PROJECT_ROOT / "examples" / level / "scaffold" / "immutable.json"
                destination = root / "examples" / level / "scaffold" / "immutable.json"
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            first = write_primitive_candidates(root)
            payloads = {}
            immutable_counts = {
                "byte_adder": 5,
                "count_leading_zeroes": 2,
                "saving_gracefully": 3,
                "saving_bytes": 3,
            }
            for level in PRIMITIVE_LEVELS:
                path = root / "examples" / level / "candidate" / "circuit.data"
                payloads[level] = path.read_bytes()
                candidate = decode_v15(payloads[level])
                self.assertEqual(candidate, build_primitive_circuit(root, level))
                self.assertTrue(
                    all(
                        component.immutable
                        for component in candidate.components[:immutable_counts[level]]
                    )
                )
                metadata = json.loads(path.with_name("metadata.json").read_text("utf-8"))
                self.assertEqual(metadata["sha256"], sha256(payloads[level]).hexdigest())
                self.assertEqual(metadata["leaderboard_tuple"], first[level]["leaderboard_tuple"])

            second = write_primitive_candidates(root)
            self.assertEqual(first, second)
            for level, payload in payloads.items():
                self.assertEqual(
                    payload,
                    (root / "examples" / level / "candidate" / "circuit.data").read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
