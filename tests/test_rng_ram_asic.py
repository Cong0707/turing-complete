from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.rng_ram_asic import (
    EXPECTED_CYCLES,
    EXPECTED_DELAY,
    EXPECTED_ENERGY,
    EXPECTED_GATE,
    RAM_BUFFER_SIZE,
    RAM_SETTINGS,
    write_rng_ram_asic,
)


class RngRamAsicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary_directory = TemporaryDirectory()
        cls.project_root = Path(cls.temporary_directory.name)
        cls.metadata = write_rng_ram_asic(cls.project_root)
        cls.candidate_path = (
            cls.project_root / "examples" / "rng" / "candidate" / "circuit.data"
        )
        cls.payload = cls.candidate_path.read_bytes()
        cls.circuit = decode_v15(cls.payload)

    @classmethod
    def tearDownClass(cls):
        cls.temporary_directory.cleanup()

    def test_hidden_ram_state_register(self):
        rams = [component for component in self.circuit.components if component.kind == 118]
        self.assertEqual(len(rams), 1)
        ram = rams[0]
        self.assertEqual(ram.word_size, 8)
        self.assertEqual(ram.buffer_size, RAM_BUFFER_SIZE)
        self.assertEqual(ram.settings, RAM_SETTINGS)
        self.assertEqual(ram.init_data, 0)

        counts = Counter(component.kind for component in self.circuit.components)
        self.assertEqual(counts[13], 1)
        self.assertEqual(counts[54], 1)
        self.assertEqual(counts[56], 1)
        self.assertEqual(counts[118], 1)
        self.assertEqual(counts[16], 8)
        self.assertEqual(counts[17], 8)
        self.assertEqual(counts[97], 2)
        self.assertEqual(counts[99], 2)

    def test_writer_emits_verified_candidate(self):
        self.assertEqual(encode_v15(self.circuit), self.payload)
        self.assertEqual(sha256(self.payload).hexdigest(), self.metadata["sha256"])
        self.assertEqual(
            (self.circuit.gate, self.circuit.delay),
            (EXPECTED_GATE, EXPECTED_DELAY),
        )
        self.assertEqual(EXPECTED_CYCLES, 66)
        self.assertEqual(EXPECTED_ENERGY, 171_600)
        self.assertEqual(self.metadata["leaderboard_tuple"], [260, 10, 66])
        self.assertEqual(self.metadata["declared_energy"], 171_600)
        self.assertEqual(self.metadata["ram_load_gate_cost"], RAM_BUFFER_SIZE)
        self.assertEqual(self.metadata["ram_store_gate_cost"], RAM_BUFFER_SIZE)
        self.assertEqual(self.metadata["component_count"], 137)
        self.assertEqual(self.metadata["wire_count"], 308)
        self.assertEqual(self.metadata["runtime_test_seed_count"], 256)
        self.assertEqual(self.metadata["runtime_tick_count"], 16_896)

    def test_connectivity_and_sprite_geometry_are_clean(self):
        connectivity = self.metadata["connectivity"]
        for field in (
            "unconnected_pin_count",
            "multi_driver_network_count",
            "undriven_network_count",
            "sinkless_network_count",
            "width_mismatch_network_count",
            "cycle_component_count",
        ):
            self.assertEqual(connectivity[field], 0)
        self.assertFalse(connectivity["unsupported_component_kind_counts"])
        for field in (
            "wire_component_contact_count",
            "wire_interior_pin_contact_count",
            "component_footprint_overlap_count",
        ):
            self.assertEqual(self.metadata["layout"][field], 0)
        self.assertGreater(
            self.metadata["layout"]["intentional_ram_group_overlap_pair_count"],
            0,
        )
        self.assertEqual(
            self.metadata["live_sprite_layout"]["internal_wire_collision_count"],
            0,
        )
        self.assertEqual(
            self.metadata["live_sprite_layout"]["wire_interior_pin_contact_count"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
