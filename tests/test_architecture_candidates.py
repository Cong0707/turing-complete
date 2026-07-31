from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tc_save_lab.architecture_candidates import (
    ARCHITECTURE_CANDIDATES,
    build_architecture_candidates,
)
from tc_save_lab.cli import build_parser


class ArchitectureCandidateTests(unittest.TestCase):
    def test_registry_builds_every_reviewed_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = build_architecture_candidates(root)
            self.assertEqual(result["candidate_count"], len(ARCHITECTURE_CANDIDATES))
            self.assertEqual(
                [record["level"] for record in result["candidates"]],
                list(ARCHITECTURE_CANDIDATES),
            )
            for level in ARCHITECTURE_CANDIDATES:
                self.assertTrue(
                    (root / "examples" / level / "candidate" / "circuit.data").is_file()
                )

    def test_registry_rejects_unknown_levels_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "unknown"):
                build_architecture_candidates(root, levels=("unknown",))
            self.assertFalse((root / "examples").exists())

    def test_public_cli_exposes_architecture_builder(self):
        args = build_parser().parse_args(
            ["build-architecture-candidates", "maze", "mod_4"]
        )
        self.assertEqual(args.command, "build-architecture-candidates")
        self.assertEqual(args.levels, ["maze", "mod_4"])


if __name__ == "__main__":
    unittest.main()
