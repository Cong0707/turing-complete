from __future__ import annotations

from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tc_save_lab.codec import decode_v15
from tc_save_lab.rng_natural_ram_asic import (
    EXPECTED_CYCLES,
    EXPECTED_DELAY,
    EXPECTED_GATE,
    build_rng_natural_ram_asic,
    verify_rng_natural_ram_asic,
    write_rng_natural_ram_asic,
)


class RngNaturalRamAsicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.circuit = build_rng_natural_ram_asic()
        cls.verification = verify_rng_natural_ram_asic()

    def test_matches_validated_topology_and_score(self):
        self.assertEqual(
            (self.circuit.gate, self.circuit.delay, EXPECTED_CYCLES),
            (245, 7, 66),
        )
        self.assertEqual((EXPECTED_GATE, EXPECTED_DELAY), (245, 7))
        self.assertEqual(len(self.circuit.components), 122)
        self.assertEqual(len(self.circuit.wires), 278)
        self.assertEqual(
            Counter(component.kind for component in self.circuit.components),
            Counter(
                {
                    2: 1,
                    3: 1,
                    7: 32,
                    13: 1,
                    16: 8,
                    17: 8,
                    23: 61,
                    46: 1,
                    54: 1,
                    56: 1,
                    62: 1,
                    70: 1,
                    97: 2,
                    99: 2,
                    118: 1,
                }
            ),
        )

    def test_full_runtime_and_geometry_verification(self):
        self.assertEqual(self.verification["leaderboard_tuple"], [245, 7, 66])
        self.assertEqual(self.verification["energy"], 113_190)
        self.assertEqual(self.verification["runtime_test_seed_count"], 256)
        self.assertEqual(self.verification["runtime_tick_count"], 16_896)
        self.assertEqual(
            self.verification["layout"]["internal_wire_component_contact_count"],
            0,
        )
        self.assertEqual(
            self.verification["live_sprite_layout"]["internal_wire_collision_count"],
            0,
        )

    def test_writer_uses_a_temporary_project(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = write_rng_natural_ram_asic(root)
            payload = (
                root / "examples" / "rng" / "candidate" / "circuit.data"
            ).read_bytes()
            decoded = decode_v15(payload)
            self.assertEqual((decoded.gate, decoded.delay), (245, 7))
            self.assertEqual(metadata["game_validation"]["observed_tuple"], [245, 7, 66])


if __name__ == "__main__":
    unittest.main()
