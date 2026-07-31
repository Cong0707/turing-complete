from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tc_save_lab.codec import decode_v15
from tc_save_lab.nim_asic import (
    build_nim_asic,
    nim_action,
    simulate_nim_strategy,
    verify_nim_asic,
    write_nim_asic,
)


class NimAsicTests(unittest.TestCase):
    def test_reachable_state_boolean_network_matches_reviewed_actions(self):
        expected = {12: 3, 8: 3, 7: 2, 6: 1, 4: 3, 3: 2, 2: 1}
        self.assertEqual({cards: nim_action(cards) for cards in expected}, expected)
        with self.assertRaises(ValueError):
            nim_action(1)

    def test_all_nine_random_paths_win_in_three_outputs(self):
        wins = simulate_nim_strategy()
        self.assertEqual(len(wins), 9)
        self.assertEqual({len(actions) for actions in wins}, {3})
        result = verify_nim_asic()
        self.assertEqual(result["leaderboard_tuple"], [2, 2, 3])
        self.assertEqual(result["energy"], 12)
        self.assertEqual(result["connectivity"]["unit_logic_depth"], 2)

    def test_generated_candidate_is_deterministic_v15(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = write_nim_asic(root)
            path = root / "examples" / "nim" / "candidate" / "circuit.data"
            payload = path.read_bytes()
            second = write_nim_asic(root)
            self.assertEqual(first, second)
            self.assertEqual(payload, path.read_bytes())
            self.assertEqual(decode_v15(payload), build_nim_asic())


if __name__ == "__main__":
    unittest.main()
