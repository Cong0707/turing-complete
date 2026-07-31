from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.model import Component
from tc_save_lab.pins import positioned_pins
from tc_save_lab.ram_component import (
    EXPECTED_DELAY,
    EXPECTED_GATE,
    build_ram_component_candidate,
    verify_ram_component_candidate,
    write_ram_component_candidate,
)
from tc_save_lab.sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, audit_sprite_geometry


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RamComponentCandidateTests(unittest.TestCase):
    def test_current_ram_port_geometry_is_explicit(self) -> None:
        ram = Component(118, (0, 0), 0, 1, word_size=8, buffer_size=4)
        actual = {
            pin.name: (pin.position, pin.width, pin.direction)
            for pin in positioned_pins(ram)
        }
        self.assertEqual(
            actual,
            {
                "load": ((-15, -15), 1, "input"),
                "save": ((-15, -14), 1, "input"),
                "address": ((-15, -13), 8, "input"),
                "in": ((-15, -12), 8, "input"),
                "out": ((16, -15), 8, "output_tristate"),
            },
        )

    def test_candidate_preserves_game_ram_timing(self) -> None:
        candidate = build_ram_component_candidate(PROJECT_ROOT)
        result = verify_ram_component_candidate(candidate)
        self.assertEqual((candidate.gate, candidate.delay), (EXPECTED_GATE, EXPECTED_DELAY))
        self.assertEqual(result["leaderboard_tuple"], [368, 5, 1840])
        self.assertEqual(result["state_transition_vector_count"], 1_048_576)
        self.assertEqual(result["connectivity"]["width_mismatch_network_count"], 1)
        self.assertEqual(result["script_prefix"], [
            {"address": 0, "value": 0x11, "output": 0x11},
            {"address": 1, "value": 0x22, "output": 0x22},
            {"address": 2, "value": 0x33, "output": 0x33},
            {"address": 3, "value": 0x44, "output": 0x44},
        ])

    @unittest.skipUnless(
        DEFAULT_COMPONENT_SPRITE_ROOT.is_dir(),
        "当前机器未安装 Turing Complete 组件精灵，跳过真实几何审计",
    )
    def test_candidate_passes_current_sprite_geometry_audit(self) -> None:
        candidate = build_ram_component_candidate(PROJECT_ROOT)
        audit = audit_sprite_geometry(candidate, DEFAULT_COMPONENT_SPRITE_ROOT)
        self.assertEqual(audit.unsupported_component_kinds, ())
        self.assertEqual(audit.component_overlap_cells, ())
        self.assertEqual(
            {
                (item.wire_index, item.component_index, item.point)
                for item in audit.wire_collisions
            },
            {
                (2, 1, (-13, -4)),
                (3, 1, (-13, -2)),
            },
        )
        self.assertEqual(audit.wire_interior_pin_contacts, ())

    def test_writer_is_deterministic_and_v15_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = PROJECT_ROOT / "examples" / "ram_component" / "scaffold"
            target = root / "examples" / "ram_component" / "scaffold"
            shutil.copytree(source, target)
            first = write_ram_component_candidate(root)
            path = root / "examples" / "ram_component" / "candidate" / "circuit.data"
            payload = path.read_bytes()
            circuit = decode_v15(payload)
            self.assertEqual(circuit, build_ram_component_candidate(root))
            self.assertEqual(decode_v15(encode_v15(circuit)), circuit)
            metadata = json.loads(path.with_name("metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["sha256"], first["sha256"])
            self.assertEqual(write_ram_component_candidate(root), first)
            self.assertEqual(path.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
