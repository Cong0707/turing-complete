from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import shutil
import tempfile
import unittest

from tc_save_lab.architecture_candidates import build_architecture_candidates
from tc_save_lab.cli import build_parser
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.codex_library import build_known_codex_library
from tc_save_lab.direct_install import (
    ARCHITECTURE_TARGETS,
    NORMAL_TARGETS,
    install_reviewed_direct,
    plan_direct_install,
    rewrite_architecture_selections,
)
from tc_save_lab.storage import direct_replace_circuit


LEVELS = (
    '"before",true,"Default",1&1&1|\n'
    '"mod_4",true,"OVERTURE",\n'
    '"middle",false,"Default",\n'
    '"maze",true,"OVERTURE",\n'
    '"circumference",true,"OVERTURE",\n'
    '"nim",true,"LEG",\n'
    '"binary_search",true,"OVERTURE",\n'
    '"rng",true,"RV64",\n'
    '"after",true,"Player Design",2&2&2|\n'
).encode() + "".join(
    f'"{level}",true,"Default",\n' for level in NORMAL_TARGETS
).encode()
PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_NORMAL_TARGETS = (
    "and_gate_3",
    "bit_adder",
    "bit_inverter",
    "byte_adder",
    "byte_asr",
    "byte_equal",
    "byte_lsr",
    "byte_mux",
    "byte_xor",
    "count_leading_zeroes",
    "counting_signals",
    "decoder_2",
    "decoder_3",
    "one_hot_encoding",
    "or_gate_3",
    "saving_bytes",
    "saving_gracefully",
    "signed_negator",
    "xnor",
    "xor_gate",
)


class DirectInstallTests(unittest.TestCase):
    def _workspace(self, root: Path) -> tuple[Path, Path]:
        project = root / "project"
        save = root / "save"
        (save / "schematics" / "foundry").mkdir(parents=True)
        (save / "schematics" / "architecture").mkdir(parents=True)
        for level, target in NORMAL_TARGETS.items():
            source = PROJECT_ROOT / target.source
            destination = project / target.source
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())
            (save / "schematics" / level).mkdir(parents=True)
        (save / "levels.txt").write_bytes(LEVELS)
        build_known_codex_library(project)
        build_architecture_candidates(project)
        return project, save

    def test_normal_registry_contains_only_deployed_reviewed_candidates(self):
        self.assertEqual(tuple(NORMAL_TARGETS), EXPECTED_NORMAL_TARGETS)
        self.assertTrue(
            set(NORMAL_TARGETS).isdisjoint(
                {"byte_less_s", "byte_less_u", "full_adder", "ram_component"}
            )
        )

    def test_levels_rewrite_changes_only_reviewed_lines(self):
        rewritten = rewrite_architecture_selections(LEVELS)
        before = LEVELS.splitlines(keepends=True)
        after = rewritten.splitlines(keepends=True)
        self.assertEqual(before[0], after[0])
        self.assertEqual(before[2], after[2])
        self.assertEqual(before[8], after[8])
        self.assertEqual(after[1], b'"mod_4",true,"CODEX-MOD-4",\n')
        self.assertEqual(after[3], b'"maze",true,"CODEX-MAZE",\n')
        self.assertEqual(after[4], b'"circumference",true,"CODEX-CIRCUMFERENCE",\n')
        self.assertEqual(after[5], b'"nim",true,"CODEX-NIM",\n')
        self.assertEqual(after[6], b'"binary_search",true,"OVERTURE",\n')
        self.assertEqual(after[7], b'"rng",true,"RV64",\n')

    def test_levels_rewrite_rejects_unquoted_duplicate_target(self):
        duplicate = b"maze,true,OVERTURE,\n" + LEVELS
        with self.assertRaisesRegex(ValueError, "maze=2"):
            rewrite_architecture_selections(duplicate)

    def test_plan_is_read_only_and_install_writes_only_final_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            plan = plan_direct_install(project, save)
            self.assertEqual(
                len(plan.items),
                len(plan.foundry_plan.items)
                + len(NORMAL_TARGETS)
                + len(ARCHITECTURE_TARGETS),
            )
            normal_items = [item for item in plan.items if item.kind == "normal"]
            self.assertEqual(tuple(item.name for item in normal_items), EXPECTED_NORMAL_TARGETS)
            self.assertEqual(
                dict(plan.normal_selections),
                {level: "Default" for level in EXPECTED_NORMAL_TARGETS},
            )
            for item in normal_items:
                self.assertEqual(
                    item.destination,
                    save / "schematics" / item.name / "Default" / "circuit.data",
                )
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

    def test_normal_target_uses_currently_selected_schematic_without_rewriting_it(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            levels_path = save / "levels.txt"
            levels_path.write_text(
                levels_path.read_text("utf-8").replace(
                    '"byte_mux",true,"Default",',
                    '"byte_mux",true,"人工选择",',
                ),
                encoding="utf-8",
            )
            plan = plan_direct_install(project, save)
            mux = next(
                item
                for item in plan.items
                if item.kind == "normal" and item.name == "byte_mux"
            )
            self.assertEqual(
                mux.destination,
                save / "schematics" / "byte_mux" / "人工选择" / "circuit.data",
            )
            self.assertEqual(dict(plan.normal_selections)["byte_mux"], "人工选择")
            self.assertIn(
                b'"byte_mux",true,"\xe4\xba\xba\xe5\xb7\xa5\xe9\x80\x89\xe6\x8b\xa9",',
                plan.levels_after,
            )

    def test_missing_normal_level_directory_is_created_only_by_direct_install(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            level = "count_leading_zeroes"
            level_root = save / "schematics" / level
            shutil.rmtree(level_root)
            plan = plan_direct_install(project, save)
            item = next(
                item
                for item in plan.items
                if item.kind == "normal" and item.name == level
            )
            self.assertEqual(item.destination_before_kind, "absent")
            self.assertFalse(level_root.exists())
            with patch("tc_save_lab.direct_install._assert_game_not_running"):
                install_reviewed_direct(plan)
            self.assertEqual(item.destination.read_bytes(), item.payload)
            self.assertEqual(item.destination.parent, level_root / "Default")

    def test_normal_target_digest_drift_is_rejected_during_planning(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            source = project / NORMAL_TARGETS["and_gate_3"].source
            source.write_bytes(source.read_bytes() + b"x")
            with self.assertRaisesRegex(ValueError, "摘要与审查注册不一致"):
                plan_direct_install(project, save)

    def test_normal_target_rejects_a_selected_schematic_path(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            levels_path = save / "levels.txt"
            levels_path.write_text(
                levels_path.read_text("utf-8").replace(
                    '"byte_mux",true,"Default",',
                    '"byte_mux",true,"../其他目录",',
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "不是单一存档槽名"):
                plan_direct_install(project, save)

    def test_normal_selection_change_after_plan_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            plan = plan_direct_install(project, save)
            levels_path = save / "levels.txt"
            levels_path.write_text(
                levels_path.read_text("utf-8").replace(
                    '"byte_mux",true,"Default",',
                    '"byte_mux",true,"另一个槽位",',
                ),
                encoding="utf-8",
            )
            with patch("tc_save_lab.direct_install._assert_game_not_running"):
                with self.assertRaisesRegex(RuntimeError, "levels.txt changed"):
                    install_reviewed_direct(plan)
            self.assertFalse(
                (save / "schematics" / "byte_mux" / "Default" / "circuit.data").exists()
            )

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

    def test_existing_architecture_identity_is_preserved_without_rewrite(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            first = plan_direct_install(project, save)
            with patch("tc_save_lab.direct_install._assert_game_not_running"):
                install_reviewed_direct(first)
            destination = next(
                item.destination for item in first.items if item.name == "maze"
            )
            circuit = decode_v15(destination.read_bytes())
            identified = replace(circuit, custom_id=123456789, design=bytes(512))
            destination.write_bytes(encode_v15(identified))
            before = destination.read_bytes()
            second = plan_direct_install(project, save)
            maze = next(item for item in second.items if item.name == "maze")
            self.assertFalse(maze.to_dict()["will_write"])
            with patch("tc_save_lab.direct_install._assert_game_not_running"):
                install_reviewed_direct(second)
            self.assertEqual(destination.read_bytes(), before)

    def test_public_cli_exposes_direct_install(self):
        args = build_parser().parse_args(["install-reviewed", "--dry-run"])
        self.assertEqual(args.command, "install-reviewed")
        self.assertTrue(args.dry_run)

    def test_direct_replace_writes_only_the_final_circuit_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = PROJECT_ROOT / "examples" / "and_gate_3" / "candidate" / "circuit.data"
            destination = root / "save" / "schematics" / "and_gate_3" / "Default" / "circuit.data"
            with patch("tc_save_lab.storage.game_is_running", return_value=False):
                result = direct_replace_circuit(source, destination)
            self.assertTrue(result["direct_write"])
            self.assertFalse(result["created_backup"])
            self.assertEqual(destination.read_bytes(), source.read_bytes())
            forbidden = [
                path
                for path in root.rglob("*")
                if path.name.endswith((".bak", ".old", ".new", ".tmp"))
            ]
            self.assertEqual(forbidden, [])

    def test_public_cli_exposes_single_level_direct_replace(self):
        args = build_parser().parse_args(["apply-direct", "and_gate_3", "--yes"])
        self.assertEqual(args.command, "apply-direct")
        self.assertTrue(args.yes)


if __name__ == "__main__":
    unittest.main()
