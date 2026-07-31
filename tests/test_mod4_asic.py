from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tc_save_lab.codec import decode_v15
from tc_save_lab.mod4_asic import (
    build_mod_4_asic,
    evaluate_mod_4,
    verify_mod_4_asic,
    write_mod_4_asic,
)


class Mod4AsicTests(unittest.TestCase):
    def test_two_bit_input_truncation_is_modulo_four(self):
        for value in range(256):
            self.assertEqual(evaluate_mod_4(value), value % 4)
        with self.assertRaises(ValueError):
            evaluate_mod_4(256)

    def test_direct_architecture_reaches_the_metric_lower_bound(self):
        result = verify_mod_4_asic()
        self.assertEqual(result["leaderboard_tuple"], [0, 0, 1])
        self.assertEqual(result["energy"], 0)
        self.assertEqual(result["connectivity"]["connected_pin_count"], 5)
        self.assertEqual(result["connectivity"]["unit_logic_depth"], 0)

    def test_generated_candidate_is_deterministic_v15(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = write_mod_4_asic(root)
            path = root / "examples" / "mod_4" / "candidate" / "circuit.data"
            payload = path.read_bytes()
            second = write_mod_4_asic(root)
            self.assertEqual(first, second)
            self.assertEqual(payload, path.read_bytes())
            self.assertEqual(decode_v15(payload), build_mod_4_asic())


if __name__ == "__main__":
    unittest.main()
