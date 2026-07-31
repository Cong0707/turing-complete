from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tc_save_lab.codec import decode_v15
from tc_save_lab.maze_asic import (
    EXPECTED_CYCLES,
    build_maze_asic,
    verify_maze_asic,
    write_maze_asic,
)
from tc_save_lab.model import Component
from tc_save_lab.pins import positioned_pins


class MazeAsicTests(unittest.TestCase):
    def test_current_architecture_ports_and_delay_line_geometry(self):
        cases = {
            13: {"in": (-3, 0), "out": (3, 0)},
            62: {"control": (1, -2), "value": (3, 0)},
            70: {"control": (-1, -2), "value": (-3, 0)},
        }
        for kind, expected in cases.items():
            pins = positioned_pins(Component(kind, (0, 0), 0, kind, word_size=8))
            self.assertEqual({pin.name: pin.position for pin in pins}, expected, kind)

    def test_two_component_state_machine_matches_current_leaderboard(self):
        result = verify_maze_asic()
        self.assertEqual(result["cycles"], list(EXPECTED_CYCLES))
        self.assertEqual(result["leaderboard_tuple"], [6, 5, 373])
        self.assertEqual(result["energy"], 11190)
        self.assertEqual(result["connectivity"]["width_mismatch_network_count"], 1)
        self.assertEqual(build_maze_asic().components[0].word_size, 8)

    def test_generated_candidate_is_deterministic_v15(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = write_maze_asic(root)
            path = root / "examples" / "maze" / "candidate" / "circuit.data"
            payload = path.read_bytes()
            second = write_maze_asic(root)
            self.assertEqual(first, second)
            self.assertEqual(payload, path.read_bytes())
            self.assertEqual(decode_v15(payload), build_maze_asic())
