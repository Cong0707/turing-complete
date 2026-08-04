from __future__ import annotations

from dataclasses import replace
import unittest

from turingsynth.audit.relayout import audit_relayout, topology_signature
from turingsynth.formats.model import Circuit, Component
from turingsynth.formats.wire import wire_from_vertices


def _port(kind: int, position: tuple[int, int], permanent_id: int) -> Component:
    return Component(
        kind=kind,
        position=position,
        rotation=0,
        permanent_id=permanent_id,
    )


def _two_channel_circuit(*, crossed: bool = False) -> Circuit:
    components = (
        _port(61, (0, 0), 10),
        _port(61, (0, 8), 11),
        _port(69, (16, 0), 12),
        _port(69, (16, 8), 13),
    )
    if crossed:
        wires = (
            wire_from_vertices(((3, 0), (8, 0), (8, 8), (13, 8))),
            wire_from_vertices(((3, 8), (7, 8), (7, 0), (13, 0))),
        )
    else:
        wires = (
            wire_from_vertices(((3, 0), (13, 0))),
            wire_from_vertices(((3, 8), (13, 8))),
        )
    return Circuit(
        gate=0,
        delay=0,
        description="topology audit fixture",
        components=components,
        wires=wires,
    )


class RelayoutAuditTests(unittest.TestCase):
    def test_position_and_wire_geometry_may_change(self) -> None:
        source = _two_channel_circuit()
        moved_components = (
            source.components[0],
            source.components[1],
            replace(source.components[2], position=(24, 0)),
            replace(source.components[3], position=(24, 8)),
        )
        candidate = replace(
            source,
            components=moved_components,
            wires=(
                wire_from_vertices(((3, 0), (8, 0), (8, 1), (21, 1), (21, 0))),
                wire_from_vertices(((3, 8), (21, 8))),
            ),
        )

        report = audit_relayout(source, candidate)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["logical_network_count"], 2)

    def test_changed_pin_partition_is_rejected(self) -> None:
        source = _two_channel_circuit()
        candidate = _two_channel_circuit(crossed=True)

        self.assertNotEqual(topology_signature(source), topology_signature(candidate))
        with self.assertRaisesRegex(ValueError, "logical pin partition"):
            audit_relayout(source, candidate)

    def test_changed_component_metadata_is_rejected(self) -> None:
        source = _two_channel_circuit()
        candidate = replace(
            source,
            components=(
                replace(source.components[0], user_label="changed"),
                *source.components[1:],
            ),
        )

        with self.assertRaisesRegex(ValueError, "other than position"):
            audit_relayout(source, candidate)

    def test_changed_top_level_metadata_is_rejected(self) -> None:
        source = _two_channel_circuit()
        candidate = replace(source, description="changed")

        with self.assertRaisesRegex(ValueError, "top-level"):
            audit_relayout(source, candidate)


if __name__ == "__main__":
    unittest.main()
