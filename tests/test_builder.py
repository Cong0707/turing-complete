from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest

from tc_save_lab.builder import RECIPES, build_recipe, wire_from_vertices
from tc_save_lab.codec import decode_v15
from tc_save_lab.pins import analyze_connectivity


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class BuilderTests(unittest.TestCase):
    def test_rejects_non_octilinear_route(self):
        with self.assertRaises(ValueError):
            wire_from_vertices(((0, 0), (2, 1)))

    def test_reviewed_recipes_are_deterministic_and_fully_connected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for level, recipe in RECIPES.items():
                source = PROJECT_ROOT / "examples" / level
                target = root / "examples" / level
                shutil.copytree(source / "baseline", target / "baseline")
                shutil.copytree(source / "scaffold", target / "scaffold")
                first = build_recipe(root, level)
                first_payload = (target / "candidate" / "circuit.data").read_bytes()
                second = build_recipe(root, level)
                second_payload = (target / "candidate" / "circuit.data").read_bytes()
                self.assertEqual(first, second)
                self.assertEqual(first_payload, second_payload)
                candidate = decode_v15(first_payload)
                self.assertEqual(candidate.gate, recipe.declared_gate)
                self.assertEqual(candidate.delay, recipe.declared_delay)
                connectivity = analyze_connectivity(candidate)
                self.assertEqual(connectivity["unconnected_pin_count"], 0)
                self.assertEqual(connectivity["cycle_component_count"], 0)
