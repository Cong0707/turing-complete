from __future__ import annotations

import unittest

from turingsynth.ir.physical import (
    PhysicalComponent,
    PhysicalDesign,
    PhysicalNet,
    PinRef,
)
from turingsynth.config import ProjectConfig
from turingsynth.layout.layered import (
    _avoid_immutable_obstacles,
    _natural_columns,
    _ranks,
    place,
)


class LayeredLayoutTests(unittest.TestCase):
    def test_fixed_component_leaves_terminal_turn_clearance(self) -> None:
        components = {
            "fixed": PhysicalComponent(
                "fixed",
                69,
                1,
                "output_port",
                0.0,
                0,
                immutable=True,
                position=(0, 0),
            ),
            "gate": PhysicalComponent("gate", 4, 1, "gate", 0.0, 1),
        }

        columns, shifts = _avoid_immutable_obstacles(
            {1: 5},
            {1: ["gate"]},
            {"gate": 0},
            components,
        )

        self.assertEqual(columns[1], 7)
        self.assertEqual(shifts, {1: 2})

    def test_reconvergent_producers_stay_adjacent_to_consumer(self) -> None:
        components = (
            PhysicalComponent("producer-z", 6, 1, "gate", 0.0, 1),
            PhysicalComponent("unrelated", 7, 1, "gate", 0.0, 1),
            PhysicalComponent("producer-a", 9, 1, "gate", 0.0, 1),
            PhysicalComponent("consumer", 4, 1, "gate", 0.0, 2),
        )
        design = PhysicalDesign(
            name="reconvergent",
            components=components,
            nets=(
                PhysicalNet(
                    "left",
                    1,
                    PinRef("producer-z", "out"),
                    (PinRef("consumer", "in0"),),
                ),
                PhysicalNet(
                    "right",
                    1,
                    PinRef("producer-a", "out"),
                    (PinRef("consumer", "in1"),),
                ),
            ),
            gate=4,
            delay=2,
            target_kind="foundry",
        )
        config = ProjectConfig(
            manifest=__file__,
            name="test",
            top="test",
            sources=(),
            target_kind="foundry",
            logical_key="test",
            description="",
            template=None,
            port_bindings={},
            pack_widths=(8, 4, 2),
            horizontal_clearance=5,
            vertical_clearance=3,
        )

        placed, report = place(design, config)
        positions = {
            component.key: component.position for component in placed.components
        }
        ordered = sorted(
            ("producer-z", "producer-a", "unrelated"),
            key=lambda key: positions[key][1],
        )
        pair_indices = sorted(
            (ordered.index("producer-z"), ordered.index("producer-a"))
        )

        self.assertEqual(pair_indices[1] - pair_indices[0], 1)
        pair_midpoint = (
            positions["producer-z"][1] + positions["producer-a"][1]
        ) / 2
        self.assertLessEqual(abs(positions["consumer"][1] - pair_midpoint), 1)
        self.assertGreaterEqual(report["reconvergent_cluster_count"], 1)

    def test_cross_lane_dependency_advances_global_rank(self) -> None:
        design = PhysicalDesign(
            name="global-rank",
            components=(
                PhysicalComponent("a", 2, 1, "gate", 0.0, 0),
                PhysicalComponent("b", 3, 1, "gate", 1.0, 1),
                PhysicalComponent("c", 3, 1, "gate", 1.0, 2),
            ),
            nets=(
                PhysicalNet(
                    "a-b",
                    1,
                    PinRef("a", "out"),
                    (PinRef("b", "in"),),
                ),
                PhysicalNet(
                    "b-c",
                    1,
                    PinRef("b", "out"),
                    (PinRef("c", "in"),),
                ),
            ),
            gate=2,
            delay=2,
            target_kind="foundry",
        )

        self.assertEqual(_ranks(design), {"a": 0, "b": 1, "c": 2})

    def test_driver_breakout_and_tracks_share_one_channel(self) -> None:
        components = {
            "split": PhysicalComponent(
                key="split",
                kind=17,
                word_size=8,
                role="splitter",
                affinity=-1.0,
                logic_depth=0,
            ),
            "gate": PhysicalComponent(
                key="gate",
                kind=4,
                word_size=1,
                role="gate",
                affinity=0.0,
                logic_depth=1,
            ),
        }

        columns = _natural_columns(
            {0: ["split"], 1: ["gate"]},
            components,
            horizontal_clearance=5,
            channel_tracks={0: 8},
            channel_expansion={},
        )

        # Eight staggered splitter leads are the same eight track columns.
        # Adding 9 breakout columns and 8 track columns would create a
        # needlessly wide 22-cell center-to-center gap.
        self.assertEqual(columns[1] - columns[0], 14)


if __name__ == "__main__":
    unittest.main()
