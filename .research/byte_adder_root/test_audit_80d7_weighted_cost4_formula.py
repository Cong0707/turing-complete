from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
WORKER = HERE / "audit_80d7_weighted_cost4_formula.py"


def load_worker():
    spec = importlib.util.spec_from_file_location("weighted_formula_worker_test", WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(WORKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


worker = load_worker()


def source(bits: int, rows: int, label: int) -> object:
    mask = (1 << rows) - 1
    return worker.Formula(
        worker.PackedState(bits & mask, mask, 0),
        0,
        ("SOURCE", label),
    )


class WeightedFormulaTests(unittest.TestCase):
    def test_one_driver_bus_preserves_high_impedance(self) -> None:
        mask = 0b1111
        enable = worker.PackedState(0b0011, mask, 0)
        data = worker.PackedState(0b0101, mask, 0)
        result = worker.apply_bus(((enable, data),), mask)
        self.assertEqual(result.bits, 0b0001)
        self.assertEqual(result.driven, 0b0011)
        self.assertEqual(result.conflict, 0)

    def test_two_driver_bus_detects_zero_one_conflict(self) -> None:
        mask = 0b1111
        enable = worker.PackedState(0b0011, mask, 0)
        zero = worker.PackedState(0b0000, mask, 0)
        one = worker.PackedState(0b1111, mask, 0)
        result = worker.apply_bus(((enable, zero), (enable, one)), mask)
        self.assertEqual(result.driven, 0b0011)
        self.assertEqual(result.conflict, 0b0011)

    def test_exact_cost_three_finds_switch_then_not(self) -> None:
        rows = 4
        mask = (1 << rows) - 1
        sources = (source(0b0011, rows, 0), source(0b0101, rows, 1))
        switched = worker.apply_bus(((sources[0].state, sources[1].state),), mask)
        target = worker.apply_not(switched, mask)
        result = worker.enumerate_formula_closure(sources, target, rows, 3)
        self.assertEqual(result["status"], "sat")
        self.assertLessEqual(result["witness"]["arrival"], 2)

    def test_exact_cost_three_finds_xor(self) -> None:
        rows = 4
        mask = (1 << rows) - 1
        sources = (source(0b0011, rows, 0), source(0b0101, rows, 1))
        target = worker.apply_ordinary("XOR", sources[0].state, sources[1].state, mask)
        result = worker.enumerate_formula_closure(sources, target, rows, 3)
        self.assertEqual(result["status"], "sat")
        self.assertLessEqual(result["witness"]["arrival"], 2)

    def test_exact_cost_four_enumerates_two_driver_bus(self) -> None:
        rows = 4
        mask = (1 << rows) - 1
        sources = (
            source(0b0011, rows, 0),
            source(0b1100, rows, 1),
            source(0b0101, rows, 2),
        )
        target = worker.apply_bus(
            ((sources[0].state, sources[2].state), (sources[1].state, sources[2].state)),
            mask,
        )
        result = worker.enumerate_formula_closure(sources, target, rows, 4)
        self.assertGreater(result["levels"][4]["attempts"]["BUS2"], 0)
        self.assertEqual(result["status"], "sat")

    def test_conflicting_public_target_is_rejected(self) -> None:
        rows = 2
        mask = (1 << rows) - 1
        sources = (source(0b01, rows, 0),)
        with self.assertRaises(ValueError):
            worker.enumerate_formula_closure(
                sources,
                worker.PackedState(0, mask, 1),
                rows,
                1,
            )


if __name__ == "__main__":
    unittest.main()
