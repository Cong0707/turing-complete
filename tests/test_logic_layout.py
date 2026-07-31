from __future__ import annotations

import unittest

from tc_save_lab.logic_layout import layout_logic_network, map_logic_network, verify_logic_layout
from tc_save_lab.logic_network import LogicBuilder, estimate_turing_cost
from tc_save_lab.pins import analyze_connectivity


class LogicLayoutTests(unittest.TestCase):
    def _assert_layout(self, builder: LogicBuilder, vectors: int):
        network = builder.build()
        first = layout_logic_network("foundry/codex/test/layout", network)
        second = layout_logic_network("foundry/codex/test/layout", network)
        self.assertEqual(first, second)
        self.assertEqual(verify_logic_layout(network, first), vectors)
        expected = estimate_turing_cost(network)
        self.assertEqual((first.gate, first.delay), (expected.gates, expected.delay))
        connectivity = analyze_connectivity(first)
        self.assertEqual(connectivity["unconnected_pin_count"], 0)
        self.assertEqual(connectivity["multi_driver_network_count"], 0)
        self.assertEqual(connectivity["width_mismatch_network_count"], 0)
        self.assertEqual(connectivity["cycle_component_count"], 0)
        self.assertEqual(connectivity["unit_logic_depth"], first.delay)
        return network, first

    def test_and_and_nand_phases_are_parallel(self):
        builder = LogicBuilder()
        a = builder.input("A")
        b = builder.input("B")
        conjunction = builder.and_(a, b)
        builder.output("And", conjunction)
        builder.output("Nand", ~conjunction)
        _, circuit = self._assert_layout(builder, 4)
        self.assertEqual((circuit.gate, circuit.delay), (2, 1))

    def test_xor_and_xnor_share_the_first_layer(self):
        builder = LogicBuilder()
        a = builder.input("A")
        b = builder.input("B")
        parity = builder.xor(a, b)
        builder.output("Xor", parity)
        builder.output("Xnor", ~parity)
        network, circuit = self._assert_layout(builder, 4)
        netlist = map_logic_network(network)
        self.assertEqual((netlist.gate_count, netlist.delay), (4, 2))
        self.assertEqual((circuit.gate, circuit.delay), (4, 2))

    def test_input_inversion_and_multi_level_fanout(self):
        builder = LogicBuilder()
        select = builder.input("Select")
        left = builder.input("Left")
        right = builder.input("Right")
        builder.output("Mux", builder.mux(select, left, right))
        self._assert_layout(builder, 8)

    def test_constant_outputs_need_no_scored_gates(self):
        builder = LogicBuilder()
        builder.output("Zero", builder.false)
        builder.output("One", builder.true)
        _, circuit = self._assert_layout(builder, 1)
        self.assertEqual((circuit.gate, circuit.delay), (0, 0))
        self.assertEqual(sorted(component.kind for component in circuit.components), [1, 2, 81, 81])

    def test_spacing_guards_reviewed_geometry(self):
        builder = LogicBuilder()
        value = builder.input("Value")
        builder.output("Out", value)
        network = builder.build()
        with self.assertRaisesRegex(ValueError, "spacing"):
            layout_logic_network("foundry/codex/test/spacing", network, layer_spacing=5)


if __name__ == "__main__":
    unittest.main()
