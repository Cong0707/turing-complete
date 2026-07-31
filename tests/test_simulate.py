from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from tc_save_lab.builder import build_recipe
from tc_save_lab.codec import decode_v15
from tc_save_lab.model import Component
from tc_save_lab.simulate import SimulationError, simulate_combinational, verify_truth_table


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

    def test_multi_input_truth_table_returns_exact_vector_count(self):
        build_recipe(PROJECT_ROOT, "decoder_3")
        path = PROJECT_ROOT / "examples" / "decoder_3" / "candidate" / "circuit.data"
        circuit = decode_v15(path.read_bytes())

        tested = verify_truth_table(
            circuit,
            inputs={"Input": 3, "Disable": 1},
            output_label="Output",
            expected=lambda values: 0 if values["Disable"] else 1 << values["Input"],
        )

        self.assertEqual(tested, 16)

    def test_multi_output_truth_table_checks_every_named_output(self):
        build_recipe(PROJECT_ROOT, "full_adder")
        path = PROJECT_ROOT / "examples" / "full_adder" / "candidate" / "circuit.data"
        circuit = decode_v15(path.read_bytes())

        tested = verify_truth_table(
            circuit,
            inputs={"Input 0": 1, "Input 1": 1, "Input 2": 1},
            output_label=("Sum", "Carry"),
            expected=lambda values: {
                "Sum": sum(values.values()) & 1,
                "Carry": (sum(values.values()) >> 1) & 1,
            },
        )

        self.assertEqual(tested, 8)

    def test_truth_table_rejects_incomplete_input_width(self):
        build_recipe(PROJECT_ROOT, "byte_mux")
        path = PROJECT_ROOT / "examples" / "byte_mux" / "candidate" / "circuit.data"
        circuit = decode_v15(path.read_bytes())
        with self.assertRaisesRegex(SimulationError, "input schema mismatch"):
            verify_truth_table(
                circuit,
                inputs={"Select": 1, "A": 2, "B": 8},
                output_label="Output",
                expected=lambda values: 0,
            )


if __name__ == "__main__":
    unittest.main()
