from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest

from tc_save_lab.architecture_candidates import build_architecture_candidates
from tc_save_lab.cli import build_parser
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.codex_library import build_known_codex_library
from tc_save_lab.direct_install import (
    ARCHITECTURE_TARGETS,
    NORMAL_TARGETS,
    install_architecture_direct,
    install_reviewed_direct,
    plan_architecture_direct,
    plan_direct_install,
    rewrite_architecture_selection,
    rewrite_architecture_selections,
)
from tc_save_lab.pins import analyze_connectivity
from tc_save_lab.sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    audit_sprite_geometry,
)
from tc_save_lab.storage import direct_replace_circuit


LEVELS = (
    '"before",true,"Default",1&1&1|\n'
    '"mod_4",true,"OVERTURE",\n'
    '"middle",false,"Default",\n'
    '"maze",true,"OVERTURE",\n'
    '"circumference",true,"OVERTURE",\n'
    '"nim",true,"LEG",\n'
    '"capitalize",true,"RV64",\n'
    '"binary_search",true,"OVERTURE",\n'
    '"rng",true,"RV64",\n'
    '"after",true,"Player Design",2&2&2|\n'
).encode() + "".join(
    f'"{level}",true,"Default",\n' for level in NORMAL_TARGETS
).encode()
PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_NORMAL_TARGETS = (
    "bit_adder",
    "byte_constant",
    "byte_divide",
    "byte_equal",
    "byte_nand",
    "byte_not",
    "counting_signals",
    "decoder_3",
    "one_hot_encoding",
    "saving_gracefully",
    "signed_negator",
    "xnor",
    "xor_gate",
)

EXPECTED_AUDITED_HEADERS = {
    "byte_constant": (
        "8ba8cb2a677372a6ec4eef9c572666b4fbbf357bbf17c2f56cb218a50bda7131",
        0,
        0,
    ),
    "byte_divide": (
        "a2733f8f833ca31e47b635de96bcaefb76fdf796e1ba55cf42d2a1b609c8c3af",
        370,
        32,
    ),
    "byte_nand": (
        "3af017e30a23b7c3ddfee89eb2a5aa23db3f8bbf73388333edbf41bb849b2ffd",
        8,
        1,
    ),
    "byte_not": (
        "f461a23696812a47bf8e9751511ee7ca5483060dc1548227a02d5c552d2171d7",
        8,
        1,
    ),
    "counting_signals": (
        "a8c772330a024989e3db2923a6554f783c09c5ae4b0ce552c6e673cdaf63c681",
        13,
        4,
    ),
    "decoder_3": (
        "27cd1ae3ec2ecc7d8037adc59d1850280917ff2b7a01093c7ed0dbb34f50274c",
        14,
        3,
    ),
    "saving_gracefully": (
        "f0d5632ddc9191b7702d07668aeeb2fdcd7a042a1b9fbf83f923633ee2cc0d26",
        10,
        5,
    ),
    "xnor": (
        "ff0b222aa083a6195754eb6cd7ee4ca7e92222dd22515cfb6cea7423aad28971",
        3,
        2,
    ),
    "xor_gate": (
        "f8624d0e9c2a2afe0c757580b016803b4f0be89f0d0ad864872c2e16560079c7",
        3,
        2,
    ),
}


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
                {
                    "byte_less_s",
                    "byte_less_u",
                    "count_leading_zeroes",
                    "decoder_1",
                    "full_adder",
                    "not_gate",
                }
            )
        )

    def test_audited_normal_target_headers_are_exact(self):
        actual = {
            level: (target.sha256, target.gate, target.delay)
            for level, target in NORMAL_TARGETS.items()
            if level in EXPECTED_AUDITED_HEADERS
        }
        self.assertEqual(actual, EXPECTED_AUDITED_HEADERS)

    @unittest.skipUnless(
        DEFAULT_COMPONENT_SPRITE_ROOT.is_dir(),
        "当前机器未安装 Turing Complete 组件精灵，跳过注册表几何审计",
    )
    def test_normal_registry_candidates_pass_current_sprite_audit(self):
        """直接覆盖名单不得包含穿元件、压引脚或未知精灵的候选。"""

        for level, target in NORMAL_TARGETS.items():
            with self.subTest(level=level):
                circuit = decode_v15((PROJECT_ROOT / target.source).read_bytes())
                audit = audit_sprite_geometry(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
                self.assertEqual(audit.unsupported_component_kinds, ())
                self.assertEqual(audit.component_overlap_cells, ())
                self.assertEqual(audit.wire_collisions, ())
                self.assertEqual(audit.wire_interior_pin_contacts, ())
                connectivity = analyze_connectivity(circuit)
                self.assertEqual(connectivity["unconnected_pin_count"], 0)
                self.assertEqual(connectivity["multi_driver_network_count"], 0)
                self.assertEqual(connectivity["cycle_component_count"], 0)

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
        self.assertEqual(after[6], b'"capitalize",true,"CODEX-CAPITALIZE",\n')
        self.assertEqual(after[7], b'"binary_search",true,"OVERTURE",\n')
        self.assertEqual(after[8], b'"rng",true,"RV64",\n')

    def test_levels_rewrite_rejects_unquoted_duplicate_target(self):
        duplicate = b"maze,true,OVERTURE,\n" + LEVELS
        with self.assertRaisesRegex(ValueError, "maze=2"):
            rewrite_architecture_selections(duplicate)

    def test_single_architecture_plan_writes_only_its_candidate_and_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            save = root / "save"
            source = PROJECT_ROOT / ARCHITECTURE_TARGETS["capitalize"][1]
            candidate = project / ARCHITECTURE_TARGETS["capitalize"][1]
            candidate.parent.mkdir(parents=True)
            candidate.write_bytes(source.read_bytes())
            candidate.with_name("metadata.json").write_bytes(
                source.with_name("metadata.json").read_bytes()
            )
            (save / "schematics" / "architecture").mkdir(parents=True)
            levels_path = save / "levels.txt"
            levels_path.write_bytes(LEVELS)

            plan = plan_architecture_direct(project, save, level="capitalize")
            self.assertEqual(plan.item.name, "capitalize")
            self.assertEqual(
                plan.item.destination,
                save / "schematics" / "architecture" / "CODEX-CAPITALIZE" / "circuit.data",
            )
            self.assertEqual(
                plan.levels_after,
                rewrite_architecture_selection(LEVELS, "capitalize"),
            )
            self.assertIn(b'"capitalize",true,"CODEX-CAPITALIZE",', plan.levels_after)
            self.assertIn(b'"maze",true,"OVERTURE",', plan.levels_after)

            with patch("tc_save_lab.direct_install._assert_game_not_running"):
                result = install_architecture_direct(plan)
            self.assertTrue(result["installed"])
            self.assertFalse(result["created_backup"])
            self.assertEqual(plan.item.destination.read_bytes(), candidate.read_bytes())
            self.assertEqual(levels_path.read_bytes(), plan.levels_after)
            self.assertFalse((save / "schematics" / "foundry").exists())
            self.assertFalse((save / "schematics" / "maze").exists())

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
                    '"byte_equal",true,"Default",',
                    '"byte_equal",true,"人工选择",',
                ),
                encoding="utf-8",
            )
            plan = plan_direct_install(project, save)
            mux = next(
                item
                for item in plan.items
                if item.kind == "normal" and item.name == "byte_equal"
            )
            self.assertEqual(
                mux.destination,
                save / "schematics" / "byte_equal" / "人工选择" / "circuit.data",
            )
            self.assertEqual(dict(plan.normal_selections)["byte_equal"], "人工选择")
            self.assertIn(
                b'"byte_equal",true,"\xe4\xba\xba\xe5\xb7\xa5\xe9\x80\x89\xe6\x8b\xa9",',
                plan.levels_after,
            )

    def test_normal_target_digest_drift_is_rejected_during_planning(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            source = project / NORMAL_TARGETS["bit_adder"].source
            source.write_bytes(source.read_bytes() + b"x")
            with self.assertRaisesRegex(ValueError, "摘要与审查注册不一致"):
                plan_direct_install(project, save)

    def test_normal_target_rejects_a_selected_schematic_path(self):
        with tempfile.TemporaryDirectory() as directory:
            project, save = self._workspace(Path(directory))
            levels_path = save / "levels.txt"
            levels_path.write_text(
                levels_path.read_text("utf-8").replace(
                    '"byte_equal",true,"Default",',
                    '"byte_equal",true,"../其他目录",',
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
                    '"byte_equal",true,"Default",',
                    '"byte_equal",true,"另一个槽位",',
                ),
                encoding="utf-8",
            )
            with patch("tc_save_lab.direct_install._assert_game_not_running"):
                with self.assertRaisesRegex(RuntimeError, "levels.txt changed"):
                    install_reviewed_direct(plan)
            self.assertFalse(
                (save / "schematics" / "byte_equal" / "Default" / "circuit.data").exists()
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

    def test_public_cli_exposes_single_architecture_install(self):
        args = build_parser().parse_args(
            ["install-architecture", "capitalize", "--dry-run"]
        )
        self.assertEqual(args.command, "install-architecture")
        self.assertEqual(args.level, "capitalize")
        self.assertTrue(args.dry_run)

    def test_direct_replace_writes_only_the_final_circuit_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = PROJECT_ROOT / "examples" / "bit_adder" / "candidate" / "circuit.data"
            destination = root / "save" / "schematics" / "bit_adder" / "Default" / "circuit.data"
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

    def test_direct_replace_normalizes_a_valid_noncanonical_v15_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = PROJECT_ROOT / "examples" / "ram_component" / "baseline" / "circuit.data"
            destination = root / "save" / "schematics" / "ram_component" / "Default" / "circuit.data"
            original = source.read_bytes()
            original_circuit = decode_v15(original)
            self.assertNotEqual(original, encode_v15(original_circuit))
            with patch("tc_save_lab.storage.game_is_running", return_value=False):
                result = direct_replace_circuit(source, destination)
            self.assertTrue(result["direct_write"])
            self.assertEqual(destination.read_bytes(), encode_v15(original_circuit))
            self.assertEqual(decode_v15(destination.read_bytes()), original_circuit)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(
                [
                    path
                    for path in root.rglob("*")
                    if path.name.endswith((".bak", ".old", ".new", ".tmp"))
                ],
                [],
            )

    def test_public_cli_exposes_single_level_direct_replace(self):
        args = build_parser().parse_args(["apply-direct", "bit_adder", "--yes"])
        self.assertEqual(args.command, "apply-direct")
        self.assertTrue(args.yes)


if __name__ == "__main__":
    unittest.main()
