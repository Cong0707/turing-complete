from __future__ import annotations

from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest

from tc_save_lab.architecture_candidates import build_architecture_candidates
from tc_save_lab.cli import build_parser
from tc_save_lab.codec import decode_v15
from tc_save_lab.codex_library import build_known_codex_library
from tc_save_lab.direct_install import (
    install_reviewed_direct,
    plan_direct_install,
    rewrite_architecture_selections,
)


LEVELS = (
    '"before",true,"Default",1&1&1|\n'
    '"mod_4",true,"OVERTURE",\n'
    '"middle",false,"Default",\n'
    '"maze",true,"OVERTURE",\n'
    '"after",true,"Player Design",2&2&2|\n'
).encode()


class DirectInstallTests(unittest.TestCase):
    def _workspace(self, root: Path) -> tuple[Path, Path]:
        project = root / "project"
        save = root / "save"
        (save / "schematics" / "foundry").mkdir(parents=True)
        (save / "schematics" / "architecture").mkdir(parents=True)
        (save / "levels.txt").write_bytes(LEVELS)
        build_known_codex_library(project)
        build_architecture_candidates(project)
        return project, save

    def test_levels_rewrite_changes_only_two_lines(self):
        rewritten = rewrite_architecture_selections(LEVELS)
        before = LEVELS.splitlines(keepends=True)
        after = rewritten.splitlines(keepends=True)
        self.assertEqual(before[0], after[0])
        self.assertEqual(before[2], after[2])
        self.assertEqual(before[4], after[4])
        self.assertEqual(after[1], b'"mod_4",true,"CODEX-MOD-4",\n')
        self.assertEqual(after[3], b'"maze",true,"CODEX-MAZE",\n')

    def test_levels_rewrite_rejects_unquoted_duplicate_target(self):
        duplicate = b"maze,true,OVERTURE,\n" + LEVELS
        with self.assertRaisesRegex(ValueError, "maze=2"):
            rewrite_architecture_selections(duplicate)

    def test_plan_is_read_only_and_install_writes_only_final_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            plan = plan_direct_install(project, save)
            self.assertEqual(len(plan.items), 6)
            self.assertFalse((save / "schematics" / "foundry" / "codex").exists())
            with patch("tc_save_lab.direct_install._assert_game_not_running"):
                result = install_reviewed_direct(plan)
            self.assertTrue(result["installed"])
            self.assertFalse(result["created_backup"])
            for item in plan.items:
                circuit = decode_v15(item.destination.read_bytes())
                self.assertEqual(circuit.custom_id, item.custom_id)
            self.assertEqual((save / "levels.txt").read_bytes(), plan.levels_after)
            forbidden = [
                path
                for path in save.rglob("*")
                if path.name.endswith((".bak", ".old", ".new", ".tmp"))
                or path.name.startswith(".codex.tc-save-lab.")
            ]
            self.assertEqual(forbidden, [])
            second_plan = plan_direct_install(project, save)
            with patch("tc_save_lab.direct_install._assert_game_not_running"):
                second = install_reviewed_direct(second_plan)
            self.assertTrue(second["installed"])

    def test_source_change_after_plan_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            plan = plan_direct_install(project, save)
            plan.items[-1].source.write_bytes(plan.items[-1].source.read_bytes() + b"x")
            with patch("tc_save_lab.direct_install._assert_game_not_running"):
                with self.assertRaisesRegex(RuntimeError, "changed after planning"):
                    install_reviewed_direct(plan)
            self.assertFalse((save / "schematics" / "foundry" / "codex").exists())

    def test_architecture_destination_change_after_plan_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            plan = plan_direct_install(project, save)
            destination = plan.items[-1].destination
            destination.parent.mkdir(parents=True)
            destination.write_bytes(b"user change")
            with patch("tc_save_lab.direct_install._assert_game_not_running"):
                with self.assertRaisesRegex(RuntimeError, "destination changed"):
                    install_reviewed_direct(plan)
            self.assertEqual(destination.read_bytes(), b"user change")

    def test_directory_created_after_plan_is_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            plan = plan_direct_install(project, save)
            levels_before = (save / "levels.txt").read_bytes()
            destination = plan.items[-1].destination
            destination.mkdir(parents=True)
            with patch("tc_save_lab.direct_install._assert_game_not_running"):
                with self.assertRaisesRegex(RuntimeError, "destination changed"):
                    install_reviewed_direct(plan)
            for item in plan.items[:-1]:
                self.assertFalse(item.destination.exists())
            self.assertEqual((save / "levels.txt").read_bytes(), levels_before)

    def test_public_cli_exposes_direct_install(self):
        args = build_parser().parse_args(["install-reviewed", "--dry-run"])
        self.assertEqual(args.command, "install-reviewed")
        self.assertTrue(args.dry_run)


if __name__ == "__main__":
    unittest.main()
