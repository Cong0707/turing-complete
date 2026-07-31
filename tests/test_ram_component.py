from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.ram_component import (
    AND_KIND,
    DECODER_KIND,
    EXPECTED_DELAY,
    EXPECTED_GATE,
    REGISTER_KIND,
    build_ram_component_candidate,
    verify_ram_component_candidate,
    write_ram_component_candidate,
)
from tc_save_lab.sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RamComponentCandidateTests(unittest.TestCase):
    def test_candidate_uses_only_preexisting_base_components(self) -> None:
        candidate = build_ram_component_candidate(PROJECT_ROOT)
        kinds = [component.kind for component in candidate.components]
        self.assertNotIn(118, kinds)
        self.assertEqual(kinds.count(REGISTER_KIND), 4)
        self.assertEqual(kinds.count(DECODER_KIND), 1)
        self.assertEqual(kinds.count(AND_KIND), 8)
        self.assertEqual((candidate.gate, candidate.delay), (EXPECTED_GATE, EXPECTED_DELAY))

    def test_candidate_preserves_game_read_before_write_timing(self) -> None:
        candidate = build_ram_component_candidate(PROJECT_ROOT)
        result = verify_ram_component_candidate(candidate)
        self.assertEqual(result["state_transition_vector_count"], 1_048_576)
        self.assertEqual(result["leaderboard_tuple"], [368, 5, 1840])
        self.assertEqual(result["component_kind_counts"], {
            "4": 8,
            "39": 4,
            "44": 1,
            "60": 2,
            "61": 1,
            "63": 1,
            "69": 1,
        })
        self.assertEqual(result["connectivity"]["width_mismatch_network_count"], 0)
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
    def test_candidate_has_no_component_or_nonendpoint_pin_crossing(self) -> None:
        result = verify_ram_component_candidate(build_ram_component_candidate(PROJECT_ROOT))
        geometry = result["geometry"]
        self.assertIsNotNone(geometry)
        assert geometry is not None
        self.assertEqual(geometry["unexpected_wire_collision_count"], 0)
        self.assertEqual(geometry["wire_interior_pin_contact_count"], 0)
        self.assertEqual(geometry["port_lead_collision_count"], 34)
        self.assertEqual(result["board"], {
            "limit": 16,
            "min_x": -16,
            "max_x": 16,
            "min_y": -14,
            "max_y": 15,
        })

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
            self.assertIn("368 gate / 5 delay", metadata["metric_status"])
            self.assertEqual(write_ram_component_candidate(root), first)
            self.assertEqual(path.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
