from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from tc_save_lab.builder import build_recipe, wire_from_vertices
from tc_save_lab.capitalize_asic import build_capitalize_asic
from tc_save_lab.codec import decode_v15
from tc_save_lab.model import Circuit, Component, Wire
from tc_save_lab.rng_asic import build_rng_asic
from tc_save_lab.simulate import (
    SimulationError,
    simulate_clocked_tick,
    simulate_clocked_ticks,
    simulate_clocked_trace,
    simulate_combinational,
    verify_truth_table,
)


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

    def test_zero_input_truth_table_runs_one_vector(self):
        result = build_recipe(PROJECT_ROOT, "byte_constant")
        self.assertEqual(result["exhaustive_test_vectors"], 1)

        path = PROJECT_ROOT / "examples" / "byte_constant" / "candidate" / "circuit.data"
        circuit = decode_v15(path.read_bytes())
        self.assertEqual(simulate_combinational(circuit, {}), {"Output": 164})

    def test_current_clz_component_matches_every_unsigned_byte(self):
        circuit = Circuit(
            components=(
                Component(61, (-8, 0), 0, 1, user_label="Input", word_size=8),
                Component(49, (0, 0), 0, 2, word_size=8),
                Component(69, (6, 0), 0, 3, user_label="Output", word_size=8),
            ),
            wires=(
                Wire(0, "", (-5, 0), ((0, 4),)),
                Wire(0, "", (2, 0), ((0, 1),)),
            ),
        )
        for value in range(256):
            expected = 8 if value == 0 else 8 - value.bit_length()
            self.assertEqual(
                simulate_combinational(circuit, {"Input": value}),
                {"Output": expected},
                value,
            )

    def test_bit_switch_tristate_bus_matches_runtime_semantics(self):
        circuit = Circuit(
            components=(
                Component(60, (-10, 0), 0, 1, user_label="A"),
                Component(60, (-10, 4), 0, 2, user_label="Enable A"),
                Component(60, (-10, 8), 0, 3, user_label="B"),
                Component(60, (-10, 12), 0, 4, user_label="Enable B"),
                Component(12, (-5, 0), 0, 5),
                Component(12, (-5, 8), 0, 6),
                Component(68, (5, 4), 0, 7, user_label="Output"),
            ),
            wires=(
                wire_from_vertices(((-9, 0), (-6, 0))),
                wire_from_vertices(((-9, 4), (-5, 4), (-5, 1))),
                wire_from_vertices(((-9, 8), (-6, 8))),
                wire_from_vertices(((-9, 12), (-5, 12), (-5, 9))),
                wire_from_vertices(((-3, 0), (0, 0), (0, 4))),
                wire_from_vertices(((-3, 8), (0, 8), (0, 4))),
                wire_from_vertices(((0, 4), (4, 4))),
            ),
        )

        def evaluate(a: int, enable_a: int, b: int, enable_b: int) -> int:
            return simulate_combinational(
                circuit,
                {"A": a, "Enable A": enable_a, "B": b, "Enable B": enable_b},
            )["Output"]

        self.assertEqual(evaluate(1, 1, 0, 0), 1)
        self.assertEqual(evaluate(0, 0, 1, 1), 1)
        self.assertEqual(evaluate(1, 0, 1, 0), 0)
        self.assertEqual(evaluate(1, 1, 1, 1), 1)
        with self.assertRaisesRegex(SimulationError, "conflicting drivers"):
            evaluate(0, 1, 1, 1)

    def test_official_bit_switch_level_computes_xor(self):
        path = PROJECT_ROOT / "examples" / "bit_switch" / "baseline" / "circuit.data"
        circuit = decode_v15(path.read_bytes())
        self.assertEqual(
            [simulate_combinational(circuit, {"Input": value})["Output"] for value in range(4)],
            [0, 1, 1, 0],
        )

    def test_clocked_trace_reuses_one_compiled_network_for_changing_inputs(self):
        circuit = build_rng_asic()
        inputs = (
            {"Seed": 0x12345678},
            {"Seed": 0x00000000},
            {"Seed": 0xFFFFFFFF},
        )
        self.assertEqual(
            simulate_clocked_trace(circuit, inputs=inputs),
            simulate_clocked_ticks(circuit, inputs=inputs[0], tick_count=len(inputs)),
        )

    def test_clocked_simulation_allows_an_unused_fanout_output(self):
        # Capitalize intentionally does not consume Splitter8 output 5: the
        # Maker receives its replacement bit from a delay line.  Game saves
        # allow that unused source pin, and simulation must mirror it.
        result = simulate_clocked_tick(
            build_capitalize_asic(),
            inputs={"Character": ord("a")},
        )
        self.assertEqual(result.outputs, {"Capitalized": ord("A")})


if __name__ == "__main__":
    unittest.main()
