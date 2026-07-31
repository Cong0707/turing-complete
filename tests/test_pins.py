from __future__ import annotations

import unittest

from tc_save_lab.model import Circuit, Component, Wire
from tc_save_lab.pins import analyze_connectivity, positioned_pins


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
