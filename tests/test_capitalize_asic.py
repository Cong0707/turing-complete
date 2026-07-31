from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tc_save_lab.analysis import wire_points
from tc_save_lab.capitalize_asic import (
    EXPECTED_CYCLES,
    EXPECTED_DELAY,
    EXPECTED_GATE,
    PUBLIC_REFERENCE,
    TEST_TEXTS,
    build_capitalize_asic,
    expected_character,
    verify_capitalize_asic,
    write_capitalize_asic,
)
from tc_save_lab.codec import decode_v15
from tc_save_lab.pins import positioned_pins
from tc_save_lab.simulate import simulate_clocked_tick


class CapitalizeAsicTests(unittest.TestCase):
    def test_bit_six_is_the_exact_letter_predicate_for_all_level_inputs(self):
        alphabet = "abcdefghijklmnopqrstuvwxyz "
        self.assertEqual({(ord(value) >> 6) & 1 for value in alphabet[:-1]}, {1})
        self.assertEqual((ord(" ") >> 6) & 1, 0)
        for text in TEST_TEXTS:
            self.assertTrue(set(text) <= set(alphabet))

    def test_event_protocol_matches_all_three_live_script_texts(self):
        circuit = build_capitalize_asic()
        for text in TEST_TEXTS:
            memory = None
            received = []
            for index, character in enumerate(text):
                result = simulate_clocked_tick(
                    circuit,
                    inputs={"Character": ord(character)},
                    memory=memory,
                )
                received.append(result.outputs["Capitalized"])
                self.assertEqual(received[-1], expected_character(text, index))
                memory = result.memory
            self.assertEqual(bytes(received).decode("ascii"), "".join(chr(expected_character(text, i)) for i in range(len(text))))

    def test_candidate_reaches_the_public_metric_with_one_real_delay(self):
        candidate = build_capitalize_asic()
        result = verify_capitalize_asic(candidate)
        self.assertEqual((candidate.gate, candidate.delay), (EXPECTED_GATE, EXPECTED_DELAY))
        self.assertEqual(result["leaderboard_tuple"], list(PUBLIC_REFERENCE))
        self.assertEqual(result["cycles"], list(EXPECTED_CYCLES))
        self.assertEqual(result["component_kind_counts"], {"2": 2, "13": 1, "16": 1, "17": 1, "62": 1, "70": 1})
        self.assertEqual(result["connectivity"]["unconnected_pin_count"], 1)
        self.assertEqual(result["connectivity"]["unconnected_pins"][0]["name"], "out5")
        self.assertEqual(result["layout"]["wire_body_collision_count"], 0)
        self.assertEqual(result["layout"]["wire_interior_pin_contact_count"], 0)

        splitter = next(component for component in candidate.components if component.kind == 17)
        delay = next(component for component in candidate.components if component.kind == 13)
        maker = next(component for component in candidate.components if component.kind == 16)
        splitter_bit_6 = next(pin.position for pin in positioned_pins(splitter) if pin.name == "out6")
        delay_input = next(pin.position for pin in positioned_pins(delay) if pin.name == "in")
        delay_output = next(pin.position for pin in positioned_pins(delay) if pin.name == "out")
        maker_bit_5 = next(pin.position for pin in positioned_pins(maker) if pin.name == "in5")
        endpoints = [frozenset((wire.start, wire_points(wire)[-1])) for wire in candidate.wires]
        self.assertIn(frozenset((splitter_bit_6, delay_input)), endpoints)
        self.assertIn(frozenset((delay_output, maker_bit_5)), endpoints)

    def test_generated_candidate_is_deterministic_v15(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = write_capitalize_asic(root)
            path = root / "examples" / "capitalize" / "candidate" / "circuit.data"
            payload = path.read_bytes()
            second = write_capitalize_asic(root)
            self.assertEqual(first, second)
            self.assertEqual(payload, path.read_bytes())
            self.assertEqual(decode_v15(payload), build_capitalize_asic())
            on_disk = json.loads((path.parent / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(on_disk["sha256"], first["sha256"])


if __name__ == "__main__":
    unittest.main()
