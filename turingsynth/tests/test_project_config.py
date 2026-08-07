from __future__ import annotations

from pathlib import Path
import unittest

from turingsynth.config import load_project


class ProjectConfigTests(unittest.TestCase):
    def test_files_directories_globs_and_component_metadata_are_resolved(self) -> None:
        root = Path(__file__).parents[1]
        config = load_project(root / "examples" / "hierarchical_package" / "project.toml")

        self.assertEqual(config.top, "circuit_c")
        self.assertEqual(tuple(path.name for path in config.sources), ("circuit_c.sv",))
        self.assertEqual(len(config.components), 2)
        self.assertEqual(config.components[0].sources[0].name, "component_a.sv")
        self.assertEqual(config.components[1].sources[0].name, "component_b.v")
        self.assertEqual(config.components[0].display_path, "codex/a")
        self.assertEqual(config.package.filename, "circuit-c.pk")
        self.assertTrue(config.package.enabled)
        self.assertIn("TURINGSYNTH_HIERARCHICAL_EXAMPLE=1", config.defines)
        self.assertEqual(dict(config.parameters), {"WIDTH": "8"})


if __name__ == "__main__":
    unittest.main()
