from __future__ import annotations

from collections import Counter
from pathlib import Path
import importlib.util
import random
import sys
import unittest


MODEL_PATH = Path(__file__).parents[1] / "examples" / "sort" / "asic_model.py"
SPEC = importlib.util.spec_from_file_location("sort_asic_model", MODEL_PATH)
assert SPEC is not None and SPEC.loader is not None
sort_asic_model = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = sort_asic_model
SPEC.loader.exec_module(sort_asic_model)


class SortAsicTests(unittest.TestCase):
    def assert_sorted_by_asic(self, values: list[int]) -> None:
        outputs, trace = sort_asic_model.sort_stream(values)
        self.assertEqual(outputs, tuple(sorted(values)))
        self.assertEqual(len(trace), 32)
        self.assertEqual([cycle.phase for cycle in trace[:16]], ["load"] * 16)
        self.assertEqual([cycle.phase for cycle in trace[16:]], ["flush"] * 16)
        self.assertEqual(Counter(outputs), Counter(values))
        for cycle in trace:
            self.assertEqual(
                cycle.registers,
                tuple(sorted(cycle.registers, reverse=True)),
            )

    def test_fixed_boundaries_and_duplicates(self) -> None:
        cases = [
            [0] * 16,
            [255] * 16,
            list(range(16)),
            list(range(15, -1, -1)),
            [0, 255] * 8,
            [7, 7, 3, 3, 255, 0, 7, 3, 128, 128, 1, 1, 254, 2, 2, 2],
        ]
        for values in cases:
            with self.subTest(values=values):
                self.assert_sorted_by_asic(values)

    def test_deterministic_random_vectors(self) -> None:
        generator = random.Random(0xC0D3)
        for _ in range(4096):
            self.assert_sorted_by_asic(
                [generator.randrange(256) for _ in range(16)]
            )

    def test_rejects_invalid_input(self) -> None:
        with self.assertRaises(ValueError):
            sort_asic_model.sort_stream([0] * 15)
        with self.assertRaises(ValueError):
            sort_asic_model.sort_stream([0] * 15 + [256])
        with self.assertRaises(ValueError):
            sort_asic_model.insertion_cycle((0,) * 15, 0)


if __name__ == "__main__":
    unittest.main()
