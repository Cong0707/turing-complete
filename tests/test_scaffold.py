from __future__ import annotations

from pathlib import Path
import json
import tempfile
import unittest

from tc_save_lab.scaffold import extract_campaign_scaffolds
from tc_save_lab.storage import DEFAULT_GAME_ROOT


CAMPAIGN_ROOT = DEFAULT_GAME_ROOT / "campaign"


@unittest.skipUnless(CAMPAIGN_ROOT.is_dir(), "local game installation is unavailable")
class ScaffoldExtractionTests(unittest.TestCase):
    def test_extracts_every_main_level_without_copying_campaign_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = extract_campaign_scaffolds(root, CAMPAIGN_ROOT)
            self.assertEqual(result["level_count"], 92)
            self.assertEqual(result["format_versions"], {7: 15, 13: 18, 14: 57, 15: 2})
            self.assertEqual(result["immutable_component_count"], 406)
            files = sorted((root / "examples").glob("*/scaffold/immutable.json"))
            self.assertEqual(len(files), 92)
            not_gate = json.loads(
                (root / "examples" / "not_gate" / "scaffold" / "immutable.json")
                .read_text("utf-8")
            )
            self.assertEqual(not_gate["immutable_component_count"], 2)
            self.assertEqual(
                {component["role"] for component in not_gate["immutable_components"]},
                {"input", "output"},
            )
            self.assertFalse(any(root.rglob("circuit.data")))

    def test_repeated_extraction_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            extract_campaign_scaffolds(root, CAMPAIGN_ROOT)
            before = {
                path.relative_to(root): path.read_bytes()
                for path in root.rglob("*.json")
            }
            extract_campaign_scaffolds(root, CAMPAIGN_ROOT)
            after = {
                path.relative_to(root): path.read_bytes()
                for path in root.rglob("*.json")
            }
            self.assertEqual(after, before)
