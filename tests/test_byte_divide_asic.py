from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tc_save_lab.byte_divide_asic import (
    DIVIDER_KIND,
    EXPECTED_DELAY,
    EXPECTED_GATE,
    PUBLIC_REFERENCE,
    TEST_TICK_COUNT,
    _test_domain_summary,
    build_byte_divide_circuit,
    evaluate_byte_divide,
    test_input_at,
    verify_byte_divide_asic,
    write_byte_divide_asic,
)
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.pins import pin_specs_for
from tc_save_lab.sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ByteDivideAsicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.circuit = build_byte_divide_circuit(PROJECT_ROOT)

    def test_runtime_schema_is_three_port_quotient_only(self) -> None:
        specs = pin_specs_for(self.circuit.components[-1])
        self.assertIsNotNone(specs)
        self.assertEqual(
            tuple((spec.name, spec.offset) for spec in specs),
            (("in0", (-1, -1)), ("in1", (-1, 1)), ("out", (2, 0))),
        )

    def test_candidate_matches_public_frontier(self) -> None:
        result = verify_byte_divide_asic(self.circuit)
        self.assertEqual((self.circuit.gate, self.circuit.delay), (EXPECTED_GATE, EXPECTED_DELAY))
        self.assertEqual(tuple(result["leaderboard_tuple"]), PUBLIC_REFERENCE)
        self.assertEqual(result["component_kind_counts"], {"61": 2, "69": 1, str(DIVIDER_KIND): 1})
        self.assertEqual(result["full_u8_truth_vectors"], 65536)
        self.assertEqual(result["script_vectors"], TEST_TICK_COUNT)
        self.assertEqual(result["connectivity"]["connected_pin_count"], 6)
        self.assertEqual(result["layout"]["wire_collisions"], [])
        self.assertEqual(result["layout"]["wire_interior_pin_contacts"], [])

    def test_divide_semantics_cover_zero_divisor_and_full_u8_domain(self) -> None:
        self.assertEqual(evaluate_byte_divide(0xA5, 0), 0)
        self.assertEqual(evaluate_byte_divide(0xA5, 7), 0xA5 // 7)
        for dividend in range(256):
            for divisor in range(256):
                expected = 0 if divisor == 0 else dividend // divisor
                self.assertEqual(evaluate_byte_divide(dividend, divisor), expected)
        with self.assertRaises(ValueError):
            evaluate_byte_divide(-1, 1)

    def test_test_si_domain_is_replayed_exactly(self) -> None:
        seen = {test_input_at(tick) for tick in range(TEST_TICK_COUNT)}
        self.assertEqual(len(seen), 32768)
        self.assertEqual(_test_domain_summary()["duplicate_script_cases"], 32768)
        with self.assertRaises(ValueError):
            test_input_at(TEST_TICK_COUNT)

    def test_v15_round_trip_is_lossless(self) -> None:
        payload = encode_v15(self.circuit)
        self.assertEqual(payload[0], 15)
        self.assertEqual(decode_v15(payload), self.circuit)

    @unittest.skipUnless(
        DEFAULT_COMPONENT_SPRITE_ROOT.is_dir(),
        "当前机器未安装 Turing Complete 组件精灵，跳过真实几何审计",
    )
    def test_current_sprite_geometry_is_clean(self) -> None:
        result = verify_byte_divide_asic(self.circuit)
        self.assertEqual(result["layout"]["component_overlap_cells"], [])
        self.assertIn("com_div.png", result["layout"]["sprite_files"])

    def test_generated_artifacts_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Reuse the repository scaffold for the isolated writer test.
            target = root / "examples" / "byte_divide" / "scaffold"
            target.mkdir(parents=True)
            source = PROJECT_ROOT / "examples" / "byte_divide" / "scaffold" / "immutable.json"
            (target / "immutable.json").write_bytes(source.read_bytes())
            first = write_byte_divide_asic(root)
            path = root / "examples" / "byte_divide" / "candidate" / "circuit.data"
            payload = path.read_bytes()
            second = write_byte_divide_asic(root)
            self.assertEqual(first, second)
            self.assertEqual(payload, path.read_bytes())
            self.assertEqual(decode_v15(payload), build_byte_divide_circuit(root))
            metadata = json.loads((path.parent / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["sha256"], first["sha256"])


if __name__ == "__main__":
    unittest.main()
