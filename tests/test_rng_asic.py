from __future__ import annotations

import json
from pathlib import Path
import unittest

from tc_save_lab.codec import decode_v15
from tc_save_lab.rng_asic import (
    EXPECTED_CYCLES,
    EXPECTED_DELAY,
    EXPECTED_GATE,
    build_rng_asic,
    verify_rng_asic,
    write_rng_asic,
    xorshift32,
)
from tc_save_lab.simulate import simulate_clocked_ticks


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RngAsicTests(unittest.TestCase):
    def test_xorshift_reference_vectors(self):
        self.assertEqual(xorshift32(0x00000001), 0x00021001)
        self.assertEqual(xorshift32(0x00000002), 0x00042002)
        self.assertEqual(xorshift32(0x12345678), 0x996CC1E4)
        self.assertEqual(xorshift32(0xFFFFFFFF), 0xF807C000)

    def test_candidate_emits_65_values_after_one_load_tick(self):
        circuit = build_rng_asic()
        trace = simulate_clocked_ticks(
            circuit,
            inputs={"Seed": 0x12345678},
            tick_count=EXPECTED_CYCLES,
        )
        self.assertEqual(trace[0].outputs, {})
        expected = 0x12345678
        for result in trace[1:]:
            expected = xorshift32(expected)
            self.assertEqual(result.outputs, {"RNG output": expected})

    def test_verified_candidate_writes_canonical_metadata(self):
        metadata = write_rng_asic(PROJECT_ROOT)
        path = PROJECT_ROOT / "examples" / "rng" / "candidate" / "circuit.data"
        decoded = decode_v15(path.read_bytes())
        self.assertEqual((decoded.gate, decoded.delay), (EXPECTED_GATE, EXPECTED_DELAY))
        self.assertEqual(metadata["cycles"], EXPECTED_CYCLES)
        self.assertEqual(metadata["layout"]["wire_component_contact_count"], 0)
        disk_metadata = json.loads((path.parent / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(disk_metadata["sha256"], metadata["sha256"])

    def test_full_offline_verification(self):
        result = verify_rng_asic(build_rng_asic())
        self.assertEqual(result["first_seed_prefix"], ["00021001", "21211091", "12828955"])
        self.assertEqual(result["connectivity"]["cycle_component_count"], 0)


if __name__ == "__main__":
    unittest.main()
