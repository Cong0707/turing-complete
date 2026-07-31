from __future__ import annotations

import unittest
from pathlib import Path

from tc_save_lab.codec import decode_v15
from tc_save_lab.model import Circuit, Component, Wire
from tc_save_lab.pins import analyze_connectivity, positioned_pins


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PinLibraryTests(unittest.TestCase):
    def test_rotation_matches_component_coordinate_system(self):
        component = Component(
            kind=3,
            position=(10, 20),
            rotation=1,
            permanent_id=1,
        )
        pins = {pin.name: pin.position for pin in positioned_pins(component)}
        self.assertEqual(pins, {"in": (10, 19), "out": (10, 21)})

    def test_tied_nand_inputs_have_one_source_network_and_depth_one(self):
        circuit = Circuit(
            components=(
                Component(60, (-4, 0), 0, 1, immutable=True),
                Component(6, (0, 0), 0, 2),
                Component(68, (5, 0), 0, 3, immutable=True),
            ),
            wires=(
                Wire(0, "", (-3, 0), ((0, 1), (7, 1))),
                Wire(0, "", (-3, 0), ((0, 1), (1, 1))),
                Wire(0, "", (2, 0), ((0, 2),)),
            ),
        )
        metrics = analyze_connectivity(circuit)
        self.assertEqual(metrics["pin_count"], 5)
        self.assertEqual(metrics["connected_pin_count"], 5)
        self.assertEqual(metrics["logical_network_count"], 2)
        self.assertEqual(metrics["logical_edge_count"], 2)
        self.assertEqual(metrics["unit_logic_depth"], 1)
        self.assertEqual(metrics["cycle_component_count"], 0)

    def test_unknown_component_kind_is_reported_without_guessed_pins(self):
        metrics = analyze_connectivity(
            Circuit(components=(Component(118, (0, 0), 0, 1),))
        )
        self.assertEqual(metrics["supported_component_count"], 0)
        self.assertEqual(metrics["unsupported_component_kind_counts"], {118: 1})

    def test_campaign_word_io_uses_three_cell_port_distance(self):
        input_pin = positioned_pins(Component(61, (-17, 0), 0, 1, word_size=8))[0]
        output_pin = positioned_pins(Component(69, (17, 0), 0, 2, word_size=8))[0]
        self.assertEqual(input_pin.position, (-14, 0))
        self.assertEqual(output_pin.position, (14, 0))

    def test_current_word_logic_uses_wide_body_pin_offsets(self):
        cases = {
            23: {"in0": (-1, -1), "in1": (-1, 1), "out": (2, 0)},
            29: {"in": (-1, 0), "out": (2, 0)},
            34: {"in": (-1, -1), "shift": (-1, 1), "out": (2, 0)},
            42: {"select": (-1, -1), "in0": (-1, 0), "in1": (-1, 1), "out": (2, 0)},
            46: {"out": (3, 0)},
        }
        for kind, expected in cases.items():
            component = Component(kind, (0, 0), 0, kind, word_size=8)
            actual = {pin.name: pin.position for pin in positioned_pins(component)}
            self.assertEqual(actual, expected, kind)

    def test_word_io_baselines_do_not_leave_fixed_ports_unconnected(self):
        levels = ("byte_nand", "byte_not", "byte_mux", "signed_negator", "saving_bytes")
        for level in levels:
            path = PROJECT_ROOT / "examples" / level / "baseline" / "circuit.data"
            circuit = decode_v15(path.read_bytes())
            metrics = analyze_connectivity(circuit)
            fixed_unconnected = [
                pin for pin in metrics["unconnected_pins"]
                if pin["kind"] in {61, 69}
            ]
            self.assertEqual(fixed_unconnected, [], level)
