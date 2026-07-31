from __future__ import annotations

from contextlib import redirect_stdout
from pathlib import Path
import io
import json
import tempfile
import unittest

from tc_save_lab.foundry import foundry_input, foundry_output
from tc_save_lab.foundry_cli import build_parser, main
from tc_save_lab.model import Circuit, Wire


def _source_json(path: Path) -> None:
    logical_key = "not_gate"
    circuit = Circuit(
        gate=1,
        delay=1,
        clock_speed=100_000,
        components=(
            foundry_input(logical_key, "输入", (-4, 0)),
            foundry_output(logical_key, "输出", (4, 0)),
        ),
        wires=(Wire(0, "", (-1, 0), ((0, 2),)),),
    )
    path.write_text(json.dumps(circuit.to_dict(), ensure_ascii=False), encoding="utf-8")


class FoundryCliTests(unittest.TestCase):
    def test_parser_exposes_build_and_explicit_deploy(self):
        parser = build_parser()
        self.assertEqual(parser.parse_args(["build", "key", "名称", "source.json"]).command, "build")
        self.assertEqual(parser.parse_args(["build-known"]).command, "build-known")
        deploy = parser.parse_args(["deploy", "--dry-run"])
        self.assertEqual(deploy.command, "deploy")
        self.assertTrue(deploy.dry_run)

    def test_build_then_dry_run_never_writes_the_save(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            save = root / "save"
            dependency_root = save / "schematics" / "foundry"
            dependency_root.mkdir(parents=True)
            source = root / "source.json"
            _source_json(source)
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    main(
                        [
                            "build",
                            "not_gate",
                            "非门",
                            str(source),
                            "--project-root",
                            str(project),
                            "--dependency-root",
                            str(dependency_root),
                        ]
                    ),
                    0,
                )
                self.assertEqual(
                    main(
                        [
                            "deploy",
                            "--dry-run",
                            "--project-root",
                            str(project),
                            "--save-root",
                            str(save),
                        ]
                    ),
                    0,
                )
            self.assertIn('"component_count": 1', output.getvalue())
            self.assertFalse((dependency_root / "codex").exists())


if __name__ == "__main__":
    unittest.main()
