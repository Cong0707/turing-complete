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


def _driver_only_splitter_rail() -> Circuit:
    return Circuit(
        components=(
            Component(
                kind=61,
                position=(0, 0),
                rotation=0,
                permanent_id=20,
                word_size=2,
            ),
            Component(kind=109, position=(8, 0), rotation=0, permanent_id=21),
            Component(kind=69, position=(16, -1), rotation=0, permanent_id=22),
        ),
        wires=(
            wire_from_vertices(((3, 0), (7, 0))),
            wire_from_vertices(((9, -1), (13, -1))),
            wire_from_vertices(((9, 0), (9, 6))),
        ),
    )


class RelayoutAuditTests(unittest.TestCase):
    def test_endpoint_to_interior_contact_does_not_join_networks(self) -> None:
        circuit = Circuit(
            components=(
                _port(61, (0, 0), 30),
                _port(69, (16, 0), 31),
                Component(kind=61, position=(8, 3), rotation=3, permanent_id=32),
                Component(kind=69, position=(8, 8), rotation=1, permanent_id=33),
            ),
            wires=(
                wire_from_vertices(((3, 0), (13, 0))),
                wire_from_vertices(((8, 0), (8, 5))),
            ),
        )

        signature = topology_signature(circuit)

        self.assertEqual(sum(signature.values()), 2)
        self.assertEqual(sorted(map(len, signature.elements())), [2, 2])

    def test_driver_only_rail_is_counted_and_must_be_preserved(self) -> None:
        source = _driver_only_splitter_rail()

        report = audit_relayout(source, source)

        self.assertEqual(report["logical_network_count"], 3)
        without_rail = replace(source, wires=source.wires[:2])
        with self.assertRaisesRegex(ValueError, "unconnected pin"):
            audit_relayout(source, without_rail)

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

        with self.assertRaisesRegex(ValueError, "other than position/rotation"):
            audit_relayout(source, candidate)

    def test_changed_top_level_metadata_is_rejected(self) -> None:
        source = _two_channel_circuit()
        candidate = replace(source, description="changed")

        with self.assertRaisesRegex(ValueError, "top-level"):
            audit_relayout(source, candidate)


if __name__ == "__main__":
    unittest.main()
