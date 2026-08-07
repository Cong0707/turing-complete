from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from turingsynth.formats import decode_package, decode_v15, encode_v15
from turingsynth.pipeline import build_project


class HierarchicalPipelineTests(unittest.TestCase):
    def test_component_directories_are_preserved_routed_and_packaged(self) -> None:
        root = Path(__file__).parents[1]
        manifest = root / "examples" / "hierarchical_package" / "project.toml"

        with tempfile.TemporaryDirectory() as temporary:
            compiler_root = Path(temporary)
            report = build_project(compiler_root, manifest)
            build = compiler_root / "build"

            self.assertEqual(report["status"], "pass")
            self.assertEqual([item["name"] for item in report["components"]], ["a", "b"])

            main = decode_v15((build / "05-output" / "circuit.data").read_bytes())
            custom_components = [item for item in main.components if item.kind == 78]
            custom_ids = tuple(item["custom_id"] for item in report["components"])
            self.assertEqual(len(custom_components), 2)
            self.assertEqual(main.dependencies, custom_ids)
            self.assertEqual(
                {item.custom_id for item in custom_components},
                set(custom_ids),
            )

            physical = json.loads(
                (build / "06-audit" / "physical.json").read_text(encoding="utf-8")
            )
            for key in (
                "component_overlap_count",
                "wire_component_collision_count",
                "wire_interior_pin_contact_count",
                "foreign_wire_endpoint_contact_count",
                "non_orthogonal_foreign_contact_count",
                "overlapping_edge_count",
            ):
                self.assertEqual(physical[key], 0, key)

            package = decode_package(
                (build / "05-output" / "circuit-c.pk").read_bytes()
            )
            self.assertEqual(
                tuple(item.path for item in package.dependencies),
                ("codex/a", "codex/b"),
            )
            self.assertEqual(
                tuple(item.name for item in package.main_files),
                ("circuit.data",),
            )
            packaged_main = decode_v15(package.main_files[0].data)
            self.assertEqual(encode_v15(packaged_main), package.main_files[0].data)
            for dependency in package.dependencies:
                self.assertEqual(
                    tuple(item.name for item in dependency.files),
                    ("circuit.data",),
                )
                child = decode_v15(dependency.files[0].data)
                self.assertEqual(encode_v15(child), dependency.files[0].data)


if __name__ == "__main__":
    unittest.main()
