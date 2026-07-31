from __future__ import annotations

from collections import Counter
from pathlib import Path
import tempfile
import unittest

from tc_save_lab.binary_search_asic import (
    EXPECTED_DELAY,
    EXPECTED_GATE,
    EXPECTED_TERMINALS,
    GATE_DEFINITIONS,
    INITIAL_STATE,
    build_binary_search_asic,
    enumerate_search_paths,
    evaluate_synthesized_next_state,
    next_state,
    verify_binary_search_asic,
    write_binary_search_asic,
)
from tc_save_lab.codec import decode_v15


class BinarySearchAsicTests(unittest.TestCase):
    def test_feedback_order_regression_and_balanced_guesses(self):
        self.assertEqual(INITIAL_STATE, 127)
        self.assertEqual(next_state(0, 0), 1)
        self.assertEqual(next_state(127, 1), 63)
        self.assertEqual(next_state(127, 0), 191)
        self.assertEqual(next_state(63, 1), 31)
        self.assertEqual(next_state(63, 0), 95)
        self.assertEqual(next_state(253, 1), 252)

    def test_exhaustive_feedback_tree_covers_all_codes(self):
        paths = enumerate_search_paths()
        self.assertEqual(len(paths), 128)
        self.assertEqual(tuple(sorted(path.terminal for path in paths)), EXPECTED_TERMINALS)
        self.assertEqual({path.cycles for path in paths}, {8, 9})
        for path in paths:
            self.assertEqual(path.guesses[-1], path.terminal)
            self.assertEqual(path.cycles, len(path.feedback) + 1)

    def test_synthesized_network_matches_full_input_domain(self):
        transitions = {
            (state, over)
            for path in enumerate_search_paths()
            for state, over in zip(path.guesses, path.feedback)
        }
        self.assertGreater(len(transitions), 250)
        for state in range(256):
            for over in (0, 1):
                self.assertEqual(
                    evaluate_synthesized_next_state(state, over),
                    next_state(state, over),
                    (state, over),
                )

    def test_candidate_is_an_honest_offline_asic_without_old_dependencies(self):
        candidate = build_binary_search_asic()
        result = verify_binary_search_asic(candidate)
        self.assertEqual(result["leaderboard_tuple"], [77, 8, 9])
        self.assertEqual(result["energy"], 5544)
        self.assertEqual(result["public_leaderboard_reference"], [92, 6, 9, 4968])
        self.assertEqual(result["terminal_count"], 128)
        self.assertEqual(result["full_domain_vector_count"], 512)
        self.assertEqual(candidate.dependencies, ())
        self.assertNotIn(78, {component.kind for component in candidate.components})
        self.assertEqual(candidate.gate, EXPECTED_GATE)
        self.assertEqual(candidate.delay, EXPECTED_DELAY)

        expected_logic = Counter(gate.kind for gate in GATE_DEFINITIONS)
        actual = Counter(component.kind for component in candidate.components)
        self.assertEqual(
            {kind: actual[kind] for kind in expected_logic},
            dict(expected_logic),
        )
        self.assertEqual(actual[13], 8)
        self.assertEqual(len(candidate.components), 50)
        self.assertEqual(len(candidate.wires), 92)
        self.assertEqual(result["connectivity"]["unit_logic_depth"], 8)
        delays = [component for component in candidate.components if component.kind == 13]
        self.assertEqual(
            {component.position[1]: component.init_data for component in delays},
            {-35: 1, -25: 1, -15: 1, -5: 1, 5: 1, 15: 1, 25: 1, 35: 0},
        )

    def test_generated_candidate_is_deterministic_v15(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = write_binary_search_asic(root)
            path = root / "examples" / "binary_search" / "candidate" / "circuit.data"
            payload = path.read_bytes()
            second = write_binary_search_asic(root)
            self.assertEqual(first, second)
            self.assertEqual(payload, path.read_bytes())
            self.assertEqual(decode_v15(payload), build_binary_search_asic())


if __name__ == "__main__":
    unittest.main()
