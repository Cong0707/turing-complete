from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from turingsynth.formats.model import Circuit, Component
from turingsynth.formats.v15 import encode_v15
from turingsynth.formats.wire import wire_from_vertices
from turingsynth.ir.physical import PinRef
from turingsynth.importers.v15 import (
    _maker_affinity,
    _splitter_affinity,
    _splitter_output_affinity,
    import_v15,
)


def _driver_only_splitter_rail() -> Circuit:
    return Circuit(
        components=(
            Component(
                kind=61,
                position=(0, 0),
                rotation=0,
                permanent_id=1,
                word_size=2,
            ),
            Component(kind=109, position=(8, 0), rotation=0, permanent_id=2),
            Component(kind=69, position=(16, -1), rotation=0, permanent_id=3),
        ),
        wires=(
            wire_from_vertices(((3, 0), (7, 0))),
            wire_from_vertices(((9, -1), (13, -1))),
            wire_from_vertices(((9, 0), (9, 6))),
        ),
    )


class V15ImporterAffinityTests(unittest.TestCase):
    def test_scalar_splitter_precedes_first_bit_lane(self) -> None:
        self.assertEqual(_splitter_output_affinity(17, "out0"), 0.0)
        self.assertEqual(_splitter_output_affinity(17, "out7"), 7.0)
        self.assertEqual(_splitter_affinity(17), -1.0)

    def test_scalar_maker_follows_last_bit_lane(self) -> None:
        self.assertEqual(_maker_affinity(16, tuple(float(i) for i in range(8))), 8.0)

    def test_chunk_splitter_uses_chunk_centers(self) -> None:
        self.assertEqual(_splitter_output_affinity(99, "out0"), 3.5)
        self.assertEqual(_splitter_output_affinity(99, "out3"), 27.5)
        self.assertEqual(_splitter_affinity(99), -4.5)


class V15ImporterDriverOnlyRailTests(unittest.TestCase):
    def test_driver_only_rail_is_preserved_outside_logical_nets(self) -> None:
        circuit = _driver_only_splitter_rail()
        with tempfile.TemporaryDirectory() as raw_directory:
            path = Path(raw_directory) / "driver-only-rail.data"
            path.write_bytes(encode_v15(circuit))

            imported = import_v15(path)

        self.assertEqual(imported.logical_network_count, 3)
        self.assertEqual(len(imported.design.nets), 2)
        self.assertEqual(len(imported.driver_only_rails), 1)
        rail = imported.driver_only_rails[0]
        self.assertEqual(rail.sources, (PinRef("import:1:2", "out1"),))
        self.assertEqual(rail.wire_indices, (2,))
        self.assertEqual(rail.wires, (circuit.wires[2],))


if __name__ == "__main__":
    unittest.main()
