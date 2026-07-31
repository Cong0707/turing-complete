from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tc_save_lab.codex_library import CODEX_RECIPES, build_known_codex_library, verify_codex_recipe
from tc_save_lab.codec import decode_v15
from tc_save_lab.custom_design import render_custom_design


class CodexLibraryTests(unittest.TestCase):
    def test_all_recipes_are_connected_and_exhaustively_verified(self):
        reports = {recipe.logical_key: verify_codex_recipe(recipe) for recipe in CODEX_RECIPES}
        self.assertEqual(reports["foundry/codex/half_adder/area"]["vectors"], 4)
        self.assertEqual(reports["foundry/codex/full_adder/area"]["vectors"], 8)
        self.assertEqual(reports["foundry/codex/xor/area"]["vectors"], 4)
        self.assertEqual(reports["foundry/codex/xnor/area"]["vectors"], 4)
        self.assertEqual(
            reports["foundry/codex/half_adder/area"]["connectivity"]["unit_logic_depth"],
            2,
        )
        self.assertEqual(
            reports["foundry/codex/full_adder/area"]["connectivity"]["unit_logic_depth"],
            4,
        )

    def test_builds_modern_custom_candidates_and_registry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = build_known_codex_library(root)
            self.assertEqual(result["component_count"], 4)
            for record in result["components"]:
                circuit = decode_v15(Path(record["candidate"]).read_bytes())
                self.assertNotEqual(circuit.custom_id, 0)
                self.assertEqual(len(circuit.design), 512)
                self.assertTrue(any(circuit.design))
                self.assertEqual(circuit.design, render_custom_design(circuit.components))
                self.assertEqual(circuit.dependencies, ())


if __name__ == "__main__":
    unittest.main()
