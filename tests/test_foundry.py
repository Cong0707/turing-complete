from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import json
import subprocess
import tempfile
import unittest

import tc_save_lab.foundry as foundry_module
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.foundry import (
    FoundryError,
    build_codex_candidate,
    create_custom_circuit,
    custom_instance,
    deploy_codex_foundry,
    foundry_input,
    foundry_output,
    ordered_custom_dependencies,
    plan_codex_deployment,
    stable_custom_id,
)
from tc_save_lab.model import Circuit, Wire
from tc_save_lab.pins import positioned_pins


def _source(logical_key: str, *, gate: int = 0, word_size: int = 1) -> Circuit:
    input_component = foundry_input(
        logical_key,
        "输入",
        (-4, 0),
        word_size=word_size,
    )
    output_component = foundry_output(
        logical_key,
        "输出",
        (4, 0),
        word_size=word_size,
    )
    return Circuit(
        gate=gate,
        delay=gate,
        clock_speed=100_000,
        components=(input_component, output_component),
        wires=(Wire(0, "", (-1, 0), ((0, 2),)),),
    )


class FoundryIdentityTests(unittest.TestCase):
    def test_stable_custom_id_vectors(self):
        self.assertEqual(stable_custom_id("not_gate"), 8458610656123358129)
        self.assertEqual(
            stable_custom_id("foundry/codex/byte_adder/low-delay"),
            4657811890726674128,
        )
        self.assertEqual(stable_custom_id("not_gate", nonce=1), 7866151722793110784)
        self.assertEqual(
            stable_custom_id("not_gate", namespace="Cafe\u0301"),
            stable_custom_id("not_gate", namespace="Caf\u00e9"),
        )

    def test_dependencies_preserve_first_occurrence_order(self):
        components = (
            custom_instance("parent", "first", 5, (0, 0)),
            custom_instance("parent", "second", 2, (2, 0)),
            custom_instance("parent", "third", 5, (4, 0)),
        )
        self.assertEqual(ordered_custom_dependencies(components), (5, 2))

    def test_modern_ports_have_three_cell_pins_and_canonical_settings(self):
        source = _source("ports", word_size=64)
        input_component, output_component = source.components
        self.assertEqual(input_component.settings, (2,))
        self.assertEqual(output_component.settings, (0,))
        self.assertEqual(positioned_pins(input_component)[0].position, (-1, 0))
        self.assertEqual(positioned_pins(output_component)[0].position, (1, 0))
        self.assertEqual(positioned_pins(input_component)[0].width, 64)


class FoundryBuilderTests(unittest.TestCase):
    def test_first_registration_persists_the_lowest_collision_free_nonce(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            external = root / "external"
            occupied = create_custom_circuit("not_gate", _source("not_gate"))
            occupied_path = external / "occupied" / "circuit.data"
            occupied_path.parent.mkdir(parents=True)
            occupied_path.write_bytes(encode_v15(occupied))
            result = build_codex_candidate(
                root,
                "not_gate",
                "非门",
                _source("not_gate"),
                dependency_roots=(external,),
            )
            self.assertEqual(result["nonce"], 1)
            self.assertEqual(result["custom_id"], stable_custom_id("not_gate", nonce=1))

    def test_build_is_deterministic_and_keeps_identity_across_internal_updates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = build_codex_candidate(root, "not_gate", "非门", _source("not_gate"))
            first_payload = Path(first["candidate"]).read_bytes()
            second = build_codex_candidate(
                root,
                "not_gate",
                "非门",
                _source("not_gate"),
            )
            self.assertEqual(first, second)
            self.assertEqual(first_payload, Path(second["candidate"]).read_bytes())
            updated = build_codex_candidate(
                root,
                "not_gate",
                "非门",
                _source("not_gate", gate=3),
            )
            self.assertEqual(updated["custom_id"], first["custom_id"])
            circuit = decode_v15(Path(updated["candidate"]).read_bytes())
            self.assertEqual(circuit.gate, 3)
            self.assertEqual(len(circuit.design), 512)
            registry = json.loads(
                (root / "examples" / "foundry" / "codex" / "custom-ids.json").read_text("utf-8")
            )
            self.assertEqual(registry["entries"]["foundry/codex/not_gate"]["nonce"], 0)

    def test_registered_interface_change_requires_explicit_override(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_codex_candidate(root, "word", "字元件", _source("word"))
            with self.assertRaisesRegex(FoundryError, "interface changed"):
                build_codex_candidate(
                    root,
                    "word",
                    "字元件",
                    _source("word", word_size=8),
                )
            changed = build_codex_candidate(
                root,
                "word",
                "字元件",
                _source("word", word_size=8),
                allow_interface_change=True,
            )
            self.assertEqual(changed["interface_signature"][0]["word_size"], 8)

    def test_existing_registry_identity_collision_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            external = root / "external"
            result = build_codex_candidate(root, "collision", "碰撞", _source("collision"))
            collision_path = external / "other" / "circuit.data"
            collision_path.parent.mkdir(parents=True)
            collision_path.write_bytes(Path(result["candidate"]).read_bytes())
            with self.assertRaisesRegex(FoundryError, "custom_id .* collision"):
                build_codex_candidate(
                    root,
                    "collision",
                    "碰撞",
                    _source("collision", gate=1),
                    dependency_roots=(external,),
                )


class FoundryDeploymentTests(unittest.TestCase):
    def test_process_check_fails_closed_and_detects_the_game(self):
        failed = subprocess.CompletedProcess(["tasklist"], 1, "", "denied")
        with patch.object(foundry_module.os, "name", "nt"), patch.object(
            foundry_module.subprocess,
            "run",
            return_value=failed,
        ):
            with self.assertRaisesRegex(RuntimeError, "tasklist failed"):
                foundry_module._assert_game_not_running()
        running = subprocess.CompletedProcess(
            ["tasklist"],
            0,
            '"Turing Complete.exe","123","Console","1","1,024 K"\n',
            "",
        )
        with patch.object(foundry_module.os, "name", "nt"), patch.object(
            foundry_module.subprocess,
            "run",
            return_value=running,
        ):
            with self.assertRaisesRegex(RuntimeError, "is running"):
                foundry_module._assert_game_not_running()

    def test_explicit_deployment_preserves_unmanaged_codex_and_leaves_no_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            save = root / "save"
            foundry = save / "schematics" / "foundry"
            foundry.mkdir(parents=True)
            build_codex_candidate(project, "not_gate", "非门", _source("not_gate"))

            manual = create_custom_circuit("manual", _source("manual"))
            manual_path = foundry / "codex" / "手工元件" / "circuit.data"
            manual_path.parent.mkdir(parents=True)
            manual_path.write_bytes(encode_v15(manual))

            plan = plan_codex_deployment(project, save)
            self.assertEqual(len(plan.items), 1)
            with patch("tc_save_lab.foundry._assert_game_not_running") as stopped:
                result = deploy_codex_foundry(plan)
            self.assertEqual(stopped.call_count, 2)
            self.assertTrue(result["deployed"])
            self.assertFalse(result["persistent_backup"])
            self.assertEqual(decode_v15(manual_path.read_bytes()), manual)
            installed = foundry / "codex" / "非门" / "circuit.data"
            self.assertEqual(decode_v15(installed.read_bytes()).custom_id, stable_custom_id("not_gate"))
            leftovers = [path.name for path in foundry.iterdir() if path.name.startswith(".codex.tc-save-lab.")]
            self.assertEqual(leftovers, [])

    def test_plan_rejects_replacing_a_different_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            save = root / "save"
            foundry = save / "schematics" / "foundry"
            destination = foundry / "codex" / "非门" / "circuit.data"
            destination.parent.mkdir(parents=True)
            build_codex_candidate(project, "not_gate", "非门", _source("not_gate"))
            destination.write_bytes(encode_v15(create_custom_circuit("other", _source("other"))))
            with self.assertRaisesRegex(FoundryError, "different Custom identity"):
                plan_codex_deployment(project, save)

    def test_deployment_rejects_state_change_after_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            save = root / "save"
            foundry = save / "schematics" / "foundry"
            foundry.mkdir(parents=True)
            result = build_codex_candidate(project, "not_gate", "非门", _source("not_gate"))
            plan = plan_codex_deployment(project, save)
            candidate_path = Path(result["candidate"])
            candidate = decode_v15(candidate_path.read_bytes())
            candidate_path.write_bytes(encode_v15(replace(candidate, gate=1)))
            with patch("tc_save_lab.foundry._assert_game_not_running"):
                with self.assertRaisesRegex(FoundryError, "changed after planning"):
                    deploy_codex_foundry(plan)

    def test_plan_refuses_leftovers_from_an_interrupted_transaction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            save = root / "save"
            foundry = save / "schematics" / "foundry"
            foundry.mkdir(parents=True)
            build_codex_candidate(project, "not_gate", "非门", _source("not_gate"))
            (foundry / ".codex.tc-save-lab.old.interrupted").mkdir()
            with self.assertRaisesRegex(FoundryError, "interrupted Codex transaction"):
                plan_codex_deployment(project, save)


if __name__ == "__main__":
    unittest.main()
