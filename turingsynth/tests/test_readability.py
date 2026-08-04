from __future__ import annotations

from dataclasses import replace
import unittest

from turingsynth.audit.readability import audit_layout_readability
from turingsynth.ir.physical import (
    PhysicalComponent,
    PhysicalDesign,
    PhysicalNet,
    PinRef,
)


def _component(
    key: str,
    kind: int,
    position: tuple[int, int],
    logic_depth: int,
) -> PhysicalComponent:
    return PhysicalComponent(
        key=key,
        kind=kind,
        word_size=1,
        role="gate",
        affinity=0.0,
        logic_depth=logic_depth,
        gate_cost=1,
        gate_delay=1,
        position=position,
    )


def _fixture(noise_y: int) -> tuple[PhysicalDesign, dict[str, int]]:
    components = (
        _component("producer-a", 6, (0, -4), 1),
        _component("producer-b", 9, (0, 4), 1),
        _component("noise", 7, (0, noise_y), 1),
        _component("consumer", 4, (8, 0), 2),
    )
    nets = (
        PhysicalNet(
            name="left",
            width=1,
            source=PinRef("producer-a", "out"),
            sinks=(PinRef("consumer", "in0"),),
        ),
        PhysicalNet(
            name="right",
            width=1,
            source=PinRef("producer-b", "out"),
            sinks=(PinRef("consumer", "in1"),),
        ),
    )
    design = PhysicalDesign(
        name="motif",
        components=components,
        nets=nets,
        gate=4,
        delay=2,
        target_kind="custom",
    )
    return design, {
        "producer-a": 1,
        "producer-b": 1,
        "noise": 1,
        "consumer": 2,
    }


class ReadabilityAuditTests(unittest.TestCase):
    def test_compact_reconvergent_pair_is_triangle_ready(self) -> None:
        design, ranks = _fixture(noise_y=12)

        report = audit_layout_readability(design, ranks)

        self.assertEqual(report["reconvergent_pair_count"], 1)
        self.assertEqual(report["triangle_ready_count"], 1)
        self.assertEqual(report["interleaved_pair_count"], 0)

    def test_unrelated_gate_between_producers_is_reported(self) -> None:
        design, ranks = _fixture(noise_y=0)

        report = audit_layout_readability(design, ranks)

        self.assertEqual(report["triangle_ready_count"], 0)
        self.assertEqual(report["interleaved_pair_count"], 1)
        self.assertEqual(report["total_intervening_components"], 1)

    def test_off_center_consumer_is_reported(self) -> None:
        design, ranks = _fixture(noise_y=12)
        components = tuple(
            replace(component, position=(8, 5))
            if component.key == "consumer"
            else component
            for component in design.components
        )

        report = audit_layout_readability(
            replace(design, components=components),
            ranks,
        )

        self.assertEqual(report["centered_consumer_count"], 0)
        self.assertEqual(report["total_consumer_center_error"], 5)


if __name__ == "__main__":
    unittest.main()
