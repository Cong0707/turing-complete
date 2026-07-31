from __future__ import annotations

from pathlib import Path
import os
import tempfile
import unittest

from tc_save_lab.campaign import campaign_levels, initialize_examples
from tc_save_lab.codec import decode_v15
from tc_save_lab.storage import DEFAULT_GAME_ROOT, DEFAULT_SAVE_ROOT, inventory


class CurrentInstallationTests(unittest.TestCase):
    @unittest.skipUnless(DEFAULT_GAME_ROOT.is_dir(), "local game installation is unavailable")
    def test_main_map_has_exactly_92_campaign_levels(self):
        levels = campaign_levels(DEFAULT_GAME_ROOT / "campaign")
        self.assertEqual(len(levels), 92)
        self.assertEqual(len(levels), len(set(levels)))
        self.assertEqual(levels[:3], ["introduction", "nand_gate", "not_gate"])
        self.assertEqual(levels[-1], "tower")
        self.assertIn("tower", levels)
        self.assertNotIn("overture_6_budget", levels)

    @unittest.skipUnless(
        DEFAULT_GAME_ROOT.is_dir() and DEFAULT_SAVE_ROOT.is_dir(),
        "local game installation or save is unavailable",
    )
    def test_example_generation_handles_shared_architectures(self):
        with tempfile.TemporaryDirectory() as directory:
            result = initialize_examples(
                Path(directory), DEFAULT_GAME_ROOT / "campaign", DEFAULT_SAVE_ROOT
            )
            self.assertEqual(result["level_count"], 92)
            schemes = {item["scheme"] for item in result["architectures"]}
            self.assertTrue({"LEG", "OVERTURE", "RV64"}.issubset(schemes))
            for scheme in schemes:
                self.assertTrue(
                    (
                        Path(directory)
                        / "examples"
                        / "_architectures"
                        / scheme
                        / "baseline"
                        / "circuit.data"
                    ).is_file()
                )

    @unittest.skipUnless(DEFAULT_SAVE_ROOT.is_dir(), "current save root is unavailable")
    def test_every_active_circuit_is_v15_decodable(self):
        records = inventory(DEFAULT_SAVE_ROOT)
        self.assertGreater(len(records), 0)
        invalid = [record for record in records if not record["valid_v15"]]
        self.assertEqual(invalid, [])

    @unittest.skipUnless(DEFAULT_SAVE_ROOT.is_dir(), "current save root is unavailable")
    def test_no_write_is_performed_when_inspecting_save(self):
        path = DEFAULT_SAVE_ROOT / "schematics" / "not_gate" / "Default" / "circuit.data"
        if not path.is_file():
            self.skipTest("not_gate Default circuit is unavailable")
        before = path.read_bytes()
        decode_v15(before)
        inventory(DEFAULT_SAVE_ROOT)
        self.assertEqual(path.read_bytes(), before)
