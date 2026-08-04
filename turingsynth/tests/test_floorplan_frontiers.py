from __future__ import annotations

import json
import unittest

from turingsynth.floorplan.frontiers import extract_io_frontiers
from turingsynth.ir.physical import PhysicalComponent, PhysicalDesign, PhysicalNet, PinRef


def _component(
    key: str,
    role: str,
    *,
    delay: int = 0,
    cost: int = 0,
) -> PhysicalComponent:
    return PhysicalComponent(
        key=key,
        kind=0,
        word_size=1,
        role=role,
        affinity=0.0,
        logic_depth=0,
        gate_cost=cost,
        gate_delay=delay,
    )


class FloorplanFrontierTests(unittest.TestCase):
    def test_frontiers_cross_only_free_splitters_and_makers(self) -> None:
        design = PhysicalDesign(
            name="frontiers",
            components=(
                _component("input", "input_port"),
                _component("split", "splitter"),
                _component("split-next", "splitter"),
                _component("gate-a", "gate", delay=1, cost=1),
                _component("gate-b", "gate", delay=1, cost=1),
                _component("gate-c", "gate", delay=1, cost=1),
                _component("maker", "maker"),
                _component("output", "output_port"),
                _component("fan-source", "gate"),
                _component("fan-a", "gate"),
                _component("fan-b", "gate"),
                _component("fan-output", "output_port"),
            ),
            nets=(
                PhysicalNet("root", 8, PinRef("input", "out"), (PinRef("split", "in"),)),
                PhysicalNet("lane-0", 1, PinRef("split", "out0"), (PinRef("gate-a", "in"),)),
                PhysicalNet("lane-1", 2, PinRef("split", "out1"), (PinRef("split-next", "in"),)),
                PhysicalNet("leaf-0", 1, PinRef("split-next", "out0"), (PinRef("gate-b", "in"),)),
                PhysicalNet("leaf-1", 1, PinRef("split-next", "out1"), (PinRef("gate-c", "in"),)),
                PhysicalNet("sum-a", 1, PinRef("gate-a", "out"), (PinRef("maker", "in0"),)),
                PhysicalNet("sum-b", 1, PinRef("gate-b", "out"), (PinRef("maker", "in1"),)),
                PhysicalNet("made", 2, PinRef("maker", "out"), (PinRef("output", "in"),)),
                PhysicalNet(
                    "ordinary-high-fanout",
                    1,
                    PinRef("fan-source", "out"),
                    (
                        PinRef("fan-a", "in"),
                        PinRef("fan-b", "in"),
                        PinRef("fan-output", "in"),
                    ),
                ),
            ),
            gate=5,
            delay=1,
            target_kind="level",
        )

        floorplan = extract_io_frontiers(design)

        self.assertEqual(len(floorplan.input_trunks), 1)
        trunk = floorplan.input_trunks[0]
        self.assertEqual(trunk.input_port, "input")
        self.assertEqual(trunk.root_nets, ("root",))
        self.assertEqual(trunk.frontier_nets, ("lane-0", "leaf-0", "leaf-1"))
        self.assertEqual(trunk.splitters, ("split", "split-next"))
        self.assertNotIn("ordinary-high-fanout", trunk.frontier_nets)

        merges = {merge.output_port: merge for merge in floorplan.output_merges}
        self.assertEqual(merges["output"].frontier_nets, ("sum-a", "sum-b"))
        self.assertEqual(merges["output"].makers, ("maker",))
        self.assertEqual(
            merges["fan-output"].frontier_nets,
            ("ordinary-high-fanout",),
        )
        conductors = {conductor.net: conductor for conductor in floorplan.conductors}
        self.assertEqual(len(conductors), len(design.nets))
        ordinary = conductors["ordinary-high-fanout"]
        self.assertEqual(len(ordinary.tips), 1)
        self.assertEqual(len(ordinary.sockets), 3)
        self.assertEqual(ordinary.tips[0].source, PinRef("fan-source", "out"))

        cones = {
            cone.key.removeprefix("cone:output:"): cone
            for cone in floorplan.growth_cones
        }
        self.assertEqual(cones["output"].components, ("gate-a", "gate-b"))
        self.assertEqual(cones["output"].input_trunks, ("input:input",))
        self.assertEqual(cones["fan-output"].components, ("fan-source",))
        self.assertEqual(floorplan.schema, "turingsynth-floorplan-v2")
        json.dumps(floorplan.to_dict())

    def test_nonzero_splitter_is_a_logic_boundary(self) -> None:
        design = PhysicalDesign(
            name="costly-splitter",
            components=(
                _component("input", "input_port"),
                _component("split", "splitter", cost=1),
                _component("gate", "gate", delay=1, cost=1),
                _component("output", "output_port"),
            ),
            nets=(
                PhysicalNet("root", 2, PinRef("input", "out"), (PinRef("split", "in"),)),
                PhysicalNet("child", 1, PinRef("split", "out0"), (PinRef("gate", "in"),)),
                PhysicalNet("result", 1, PinRef("gate", "out"), (PinRef("output", "in"),)),
            ),
            gate=2,
            delay=1,
            target_kind="level",
        )

        floorplan = extract_io_frontiers(design)

        self.assertEqual(floorplan.input_trunks[0].frontier_nets, ("root",))
        self.assertEqual(floorplan.input_trunks[0].splitters, ())


if __name__ == "__main__":
    unittest.main()
