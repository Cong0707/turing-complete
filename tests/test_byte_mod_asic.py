from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tc_save_lab.byte_mod_asic import (
    EXPECTED_DELAY,
    EXPECTED_GATE,
    MOD_COMPONENT_KIND,
    PUBLIC_REFERENCE,
    TEST_DOMAIN_PARITY_MASK,
    TEST_TICK_COUNT,
    _connectivity,
    _sprite_geometry,
    _test_domain_summary,
    build_byte_mod_asic,
    evaluate_byte_mod,
    test_input_at,
    verify_byte_mod_asic,
    write_byte_mod_asic,
)
from tc_save_lab.codec import decode_v15
from tc_save_lab.sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT


class ByteModAsicTests(unittest.TestCase):
    def test_exact_test_si_generator_has_the_reviewed_affine_domain(self) -> None:
        seen = set()
        for tick in range(TEST_TICK_COUNT):
            dividend, divisor = test_input_at(tick)
            self.assertEqual(
                ((dividend | (divisor << 8)) & TEST_DOMAIN_PARITY_MASK).bit_count() & 1,
                0,
            )
            seen.add((dividend, divisor))
        self.assertEqual(len(seen), 32_768)
        self.assertEqual(_test_domain_summary()["duplicate_script_cases"], 32_768)
        with self.assertRaises(ValueError):
            test_input_at(TEST_TICK_COUNT)

    def test_native_semantics_cover_zero_divisor_and_full_u8_domain(self) -> None:
        self.assertEqual(evaluate_byte_mod(0xA5, 0), 0xA5)
        self.assertEqual(evaluate_byte_mod(0xA5, 7), 0xA5 % 7)
        for dividend in range(256):
            for divisor in range(256):
                self.assertEqual(
                    evaluate_byte_mod(dividend, divisor),
                    dividend if divisor == 0 else dividend % divisor,
                )
        with self.assertRaises(ValueError):
            evaluate_byte_mod(-1, 1)

    def test_candidate_matches_current_public_first_place_metric(self) -> None:
        candidate = build_byte_mod_asic()
        result = verify_byte_mod_asic(candidate)
        self.assertEqual((candidate.gate, candidate.delay), (EXPECTED_GATE, EXPECTED_DELAY))
        self.assertEqual(tuple(result["leaderboard_tuple"]), PUBLIC_REFERENCE)
        self.assertEqual(result["component_kind_counts"], {"61": 2, "69": 1, str(MOD_COMPONENT_KIND): 1})
        self.assertEqual(result["full_u8_truth_vectors"], 65_536)
        self.assertEqual(result["script_vectors"], TEST_TICK_COUNT)
        self.assertEqual(result["connectivity"]["connected_pin_count"], 6)
        self.assertEqual(result["layout"]["wire_body_collision_count"], 0)
        self.assertEqual(result["layout"]["wire_interior_pin_contact_count"], 0)

    @unittest.skipUnless(
        DEFAULT_COMPONENT_SPRITE_ROOT.is_dir(),
        "当前机器未安装 Turing Complete 组件精灵，跳过真实几何审计",
    )
    def test_current_sprite_geometry_is_clean(self) -> None:
        candidate = build_byte_mod_asic()
        layout = _sprite_geometry(candidate, DEFAULT_COMPONENT_SPRITE_ROOT)
        self.assertEqual(layout["component_overlap_count"], 0)
        self.assertEqual(layout["wire_body_collision_count"], 0)
        self.assertEqual(layout["wire_interior_pin_contact_count"], 0)
        self.assertIn("com_mod.png", layout["sprite_files"])

    def test_local_pin_audit_rejects_a_missing_connection(self) -> None:
        candidate = build_byte_mod_asic()
        broken = candidate.__class__(
            **{**candidate.__dict__, "wires": candidate.wires[:-1]}
        )
        report = _connectivity(broken)
        self.assertEqual(report["unconnected_pin_count"], 2)

    def test_generated_candidate_is_deterministic_v15(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = write_byte_mod_asic(root)
            path = root / "examples" / "byte_mod" / "candidate" / "circuit.data"
            payload = path.read_bytes()
            second = write_byte_mod_asic(root)
            self.assertEqual(first, second)
            self.assertEqual(payload, path.read_bytes())
            self.assertEqual(decode_v15(payload), build_byte_mod_asic())
            metadata = json.loads((path.parent / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["sha256"], first["sha256"])


if __name__ == "__main__":
    unittest.main()
