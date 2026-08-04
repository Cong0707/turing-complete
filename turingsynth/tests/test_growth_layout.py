from __future__ import annotations

import unittest

from turingsynth.config import ProjectConfig
from turingsynth.ir.physical import (
    PhysicalComponent,
    PhysicalDesign,
    PhysicalNet,
    PinRef,
)
from turingsynth.layout.growth import place_growth


def _config() -> ProjectConfig:
    return ProjectConfig(
        manifest=__file__,
        name="growth-test",
        top="growth_test",
        sources=(),
        target_kind="level",
        logical_key="growth-test",
        description="",
        template=None,
        port_bindings={},
        pack_widths=(8, 4, 2),
        horizontal_clearance=5,
        vertical_clearance=3,
    )


class GrowthLayoutTests(unittest.TestCase):
    def test_input_bus_is_established_before_logic_growth(self) -> None:
        design = PhysicalDesign(
            name="bus-growth",
            components=(
                PhysicalComponent(
                    "input",
                    61,
                    8,
                    "input_port",
                    3.5,
                    0,
                    immutable=True,
                    position=(-20, 0),
                ),
                PhysicalComponent("split", 17, 1, "splitter", -1.0, 0),
                PhysicalComponent("gate-a", 4, 1, "gate", 0.0, 1, 1, 1),
                PhysicalComponent("gate-b", 7, 1, "gate", 1.0, 1, 1, 1),
            ),
            nets=(
                PhysicalNet(
                    "bus",
                    8,
                    PinRef("input", "value"),
                    (PinRef("split", "in"),),
                ),
                PhysicalNet(
                    "lane0",
                    1,
                    PinRef("split", "out0"),
                    (PinRef("gate-a", "in0"),),
                ),
                PhysicalNet(
                    "lane1",
                    1,
                    PinRef("split", "out1"),
                    (PinRef("gate-b", "in0"),),
                ),
            ),
            gate=2,
            delay=1,
            target_kind="level",
        )

        placed, report = place_growth(design, _config())
        components = placed.component_by_key()

        self.assertEqual(
            components["input"].position[0],
            components["split"].position[0],
        )
        self.assertLess(
            components["input"].position[1],
            components["split"].position[1],
        )
        self.assertEqual(components["input"].rotation, 1)
        self.assertEqual(components["split"].rotation, 1)
        lane_starts = {
            lane["source_y"]
            for trunk in report["bus_trunks"]
            for lane in trunk["lanes"]
        }
        rail_xs = [
            lane["rail_x"]
            for trunk in report["bus_trunks"]
            for lane in trunk["lanes"]
        ]
        self.assertEqual(len(lane_starts), 1)
        self.assertTrue(
            all(
                components[key].position[0] > max(rail_xs)
                for key in ("gate-a", "gate-b")
            )
        )
        self.assertTrue(report["relocated_top_level_ports"])
        self.assertEqual(report["input_frontier_networks"], ["lane0", "lane1"])
        self.assertEqual(report["ordinary_global_trunk_count"], 0)

    def test_high_fanout_gate_does_not_become_an_input_trunk(self) -> None:
        sinks = tuple(
            PhysicalComponent(f"sink-{index}", 4, 1, "gate", index, 2, 1, 1)
            for index in range(4)
        )
        design = PhysicalDesign(
            name="local-fanout",
            components=(
                PhysicalComponent(
                    "input",
                    61,
                    1,
                    "input_port",
                    0.0,
                    0,
                    immutable=True,
                    position=(-20, 0),
                ),
                PhysicalComponent("producer", 7, 1, "gate", 0.0, 1, 1, 1),
                *sinks,
            ),
            nets=(
                PhysicalNet(
                    "source",
                    1,
                    PinRef("input", "value"),
                    (PinRef("producer", "in0"),),
                ),
                PhysicalNet(
                    "fanout",
                    1,
                    PinRef("producer", "out"),
                    tuple(PinRef(component.key, "in0") for component in sinks),
                ),
            ),
            gate=5,
            delay=2,
            target_kind="level",
        )

        _placed, report = place_growth(design, _config())

        self.assertEqual(report["input_frontier_networks"], ["source"])
        self.assertEqual(report["ordinary_global_trunk_count"], 0)


if __name__ == "__main__":
    unittest.main()
