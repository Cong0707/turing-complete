from __future__ import annotations

import unittest

from tc_save_lab.codex_library import CODEX_RECIPES
from tc_save_lab.custom_design import (
    DESIGN_BYTES,
    CustomDesignError,
    design_position,
    pack_design,
    render_custom_design,
    unpack_design,
)
from tc_save_lab.model import Component


class CustomDesignTests(unittest.TestCase):
    def test_position_matches_current_game_integer_mapping(self):
        self.assertEqual(design_position((-18, -8)), (13, 14))
        self.assertEqual(design_position((-9, -2)), (14, 15))
        self.assertEqual(design_position((18, 6)), (18, 16))

    def test_pack_round_trip_uses_x_major_pairs(self):
        grid = [[0] * 32 for _ in range(32)]
        grid[0][0] = 1
        grid[0][1] = 2
        grid[13][14] = 3
        design = pack_design(grid)
        self.assertEqual(len(design), DESIGN_BYTES)
        self.assertEqual(design[0], 0x12)
        self.assertEqual(design[13 * 16 + 7], 0x30)
        self.assertEqual(unpack_design(design), tuple(tuple(column) for column in grid))

    def test_full_adder_has_all_ports_and_gates_in_preview(self):
        recipe = next(
            value
            for value in CODEX_RECIPES
            if value.logical_key == "foundry/codex/full_adder/area"
        )
        grid = unpack_design(render_custom_design(recipe.circuit.components))
        expected = {
            (13, 14): 1,
            (13, 15): 1,
            (13, 16): 1,
            (14, 14): 3,
            (14, 15): 3,
            (15, 15): 3,
            (16, 15): 3,
            (16, 16): 3,
            (17, 15): 3,
            (17, 16): 3,
            (18, 15): 2,
            (18, 16): 2,
        }
        actual = {
            (x, y): grid[x][y]
            for x in range(32)
            for y in range(32)
            if grid[x][y]
        }
        self.assertEqual(actual, expected)

    def test_generic_component_does_not_hide_a_foundry_port(self):
        design = render_custom_design(
            (
                Component(79, (0, 0), 0, 1),
                Component(4, (0, 0), 0, 2),
            )
        )
        x, y = design_position((0, 0))
        self.assertEqual(unpack_design(design)[x][y], 1)

    def test_rejects_bad_grid_shape_and_values(self):
        with self.assertRaises(CustomDesignError):
            pack_design([[0]])
        grid = [[0] * 32 for _ in range(32)]
        grid[0][0] = 16
        with self.assertRaises(CustomDesignError):
            pack_design(grid)


if __name__ == "__main__":
    unittest.main()
