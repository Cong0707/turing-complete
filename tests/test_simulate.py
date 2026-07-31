from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from tc_save_lab.builder import build_recipe
from tc_save_lab.codec import decode_v15
from tc_save_lab.model import Component
from tc_save_lab.simulate import SimulationError, simulate_combinational


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CombinationalSimulationTests(unittest.TestCase):
    def test_generated_recipes_match_their_complete_truth_tables(self):
        expectations = {
            "or_gate_3": [0, 1, 1, 1, 1, 1, 1, 1],
            "and_gate_3": [0, 0, 0, 0, 0, 0, 0, 1],
            "xnor": [1, 0, 0, 1],
            "bit_inverter": [0, 1, 1, 0],
            "decoder_1": [1, 2],
        }
        for level, expected in expectations.items():
            build_recipe(PROJECT_ROOT, level)
            circuit = decode_v15(
                (PROJECT_ROOT / "examples" / level / "candidate" / "circuit.data").read_bytes()
            )
            actual = [
                simulate_combinational(circuit, {"Input": value})["Output"]
                for value in range(len(expected))
            ]
            self.assertEqual(actual, expected)

    def test_unknown_component_semantics_are_rejected(self):
        path = PROJECT_ROOT / "examples" / "xnor" / "candidate" / "circuit.data"
        circuit = decode_v15(path.read_bytes())
        component = replace(circuit.components[2], kind=78)
        broken = replace(circuit, components=circuit.components[:2] + (component,) + circuit.components[3:])
        with self.assertRaises(SimulationError):
            simulate_combinational(broken, {"Input": 0})


if __name__ == "__main__":
    unittest.main()
