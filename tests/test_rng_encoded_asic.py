from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.rng_encoded_asic import (
    A,
    B,
    C,
    EXPECTED_CYCLES,
    EXPECTED_DELAY,
    EXPECTED_GATE,
    GATES,
    IDENTITY,
    MODE_PAIRS,
    T,
    T_INVERSE,
    apply_matrix,
    compose,
    write_rng_encoded_asic,
    xorshift32,
)


class RngEncodedAsicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary_directory = TemporaryDirectory()
        cls.project_root = Path(cls.temporary_directory.name)
        cls.metadata = write_rng_encoded_asic(cls.project_root)
        cls.candidate_path = (
            cls.project_root / "examples" / "rng" / "candidate" / "circuit.data"
        )
        cls.payload = cls.candidate_path.read_bytes()
        cls.circuit = decode_v15(cls.payload)

    @classmethod
    def tearDownClass(cls):
        cls.temporary_directory.cleanup()

    def test_xorshift_reference_vectors(self):
        self.assertEqual(xorshift32(0x00000001), 0x00021001)
        self.assertEqual(xorshift32(0x00000002), 0x00042002)
        self.assertEqual(xorshift32(0x12345678), 0x996CC1E4)
        self.assertEqual(xorshift32(0xFFFFFFFF), 0xF807C000)

    def test_encoded_matrix_certificate(self):
        self.assertEqual(compose(C, T), A)
        self.assertEqual(compose(T, C), B)
        self.assertEqual(compose(T, T_INVERSE), IDENTITY)
        for seed in (0, 1, 0x12345678, 0xFFFFFFFF):
            encoded = apply_matrix(T, seed)
            self.assertEqual(apply_matrix(T_INVERSE, encoded), seed)
            self.assertEqual(apply_matrix(C, encoded), xorshift32(seed))

    def test_fixed_dual_mode_network_metrics(self):
        self.assertEqual(len(GATES), 61)
        self.assertEqual(sum(gate.depth == 1 for gate in GATES), 27)
        self.assertEqual(sum(gate.depth == 2 for gate in GATES), 34)
        self.assertEqual(len(MODE_PAIRS), 47)
        counts = Counter(component.kind for component in self.circuit.components)
        self.assertEqual(counts[7], 47)
        self.assertEqual(counts[10], 61)
        self.assertEqual(counts[13], 33)

    def test_writer_emits_canonical_verified_candidate(self):
        self.assertEqual(encode_v15(self.circuit), self.payload)
        self.assertEqual(sha256(self.payload).hexdigest(), self.metadata["sha256"])
        self.assertEqual(
            (self.circuit.gate, self.circuit.delay),
            (EXPECTED_GATE, EXPECTED_DELAY),
        )
        self.assertEqual(self.metadata["cycles"], EXPECTED_CYCLES)
        self.assertEqual(self.metadata["verified_seed_count"], 69)
        self.assertEqual(self.metadata["leaderboard_tuple"], [396, 9, 66])
        self.assertEqual(self.metadata["declared_energy"], 235224)
        self.assertEqual(self.metadata["layout"]["wire_component_contact_count"], 0)
        self.assertEqual(
            self.metadata["live_sprite_layout"]["internal_wire_collision_count"], 0
        )
        self.assertEqual(
            self.metadata["live_sprite_layout"]["wire_interior_pin_contact_count"], 0
        )
        disk_metadata = json.loads(
            (self.candidate_path.parent / "metadata.json").read_text(encoding="utf-8")
        )
        self.assertEqual(disk_metadata["sha256"], self.metadata["sha256"])
        self.assertEqual(disk_metadata["leaderboard_tuple"], [396, 9, 66])
        self.assertEqual(disk_metadata["live_sprite_layout"], self.metadata["live_sprite_layout"])


if __name__ == "__main__":
    unittest.main()
