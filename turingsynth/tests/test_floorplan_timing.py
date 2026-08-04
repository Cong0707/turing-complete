from __future__ import annotations

import json
import unittest

from turingsynth.floorplan.timing import analyze_timing
from turingsynth.ir.physical import PhysicalComponent, PhysicalDesign, PhysicalNet, PinRef


def _component(key: str, role: str, delay: int = 0) -> PhysicalComponent:
    return PhysicalComponent(
        key=key,
        kind=0,
        word_size=1,
        role=role,
        affinity=0.0,
        logic_depth=0,
        gate_cost=delay,
        gate_delay=delay,
    )


class FloorplanTimingTests(unittest.TestCase):
    def test_arrival_required_slack_and_critical_input(self) -> None:
        design = PhysicalDesign(
            name="timing",
            components=(
                _component("input", "input_port"),
                _component("first", "gate", 1),
                _component("last", "gate", 2),
                _component("side", "gate", 1),
                _component("output", "output_port"),
                _component("side-output", "output_port"),
            ),
            nets=(
                PhysicalNet("input-first", 1, PinRef("input", "out"), (PinRef("first", "in"),)),
                PhysicalNet(
                    "first-last",
                    1,
                    PinRef("first", "out"),
                    (PinRef("last", "in"),),
                ),
                PhysicalNet("last-output", 1, PinRef("last", "out"), (PinRef("output", "in"),)),
                PhysicalNet("input-side", 1, PinRef("input", "out"), (PinRef("side", "in"),)),
                PhysicalNet("side-output", 1, PinRef("side", "out"), (PinRef("side-output", "in"),)),
            ),
            gate=4,
            delay=3,
            target_kind="level",
        )

        frame = analyze_timing(design)
        facts = frame.fact_by_component()

        self.assertEqual(frame.actual_delay, 3)
        self.assertEqual(facts["first"].arrival, 1)
        self.assertEqual(facts["first"].required, 1)
        self.assertEqual(facts["first"].slack, 0)
        self.assertEqual(facts["last"].arrival, 3)
        self.assertEqual(facts["last"].critical_input_net, "first-last")
        self.assertEqual(facts["last"].critical_input, PinRef("last", "in"))
        self.assertEqual(facts["last"].critical_source, PinRef("first", "out"))
        self.assertEqual(facts["side"].slack, 2)
        self.assertEqual(frame.critical_outputs, ("output",))
        json.dumps(frame.to_dict())

    def test_combinational_cycle_is_rejected(self) -> None:
        design = PhysicalDesign(
            name="cycle",
            components=(
                _component("left", "gate", 1),
                _component("right", "gate", 1),
            ),
            nets=(
                PhysicalNet("left-right", 1, PinRef("left", "out"), (PinRef("right", "in"),)),
                PhysicalNet("right-left", 1, PinRef("right", "out"), (PinRef("left", "in"),)),
            ),
            gate=2,
            delay=2,
            target_kind="level",
        )

        with self.assertRaisesRegex(ValueError, "cycle"):
            analyze_timing(design)


if __name__ == "__main__":
    unittest.main()
