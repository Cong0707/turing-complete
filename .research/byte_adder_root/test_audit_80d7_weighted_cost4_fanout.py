from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
AUDITOR = HERE / "audit_80d7_weighted_cost4_fanout.py"


def load_auditor():
    spec = importlib.util.spec_from_file_location("weighted_fanout_auditor_test", AUDITOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(AUDITOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


audit = load_auditor()


class WeightedFanoutAuditTests(unittest.TestCase):
    def test_resolved_bus_preserves_z_and_detects_conflict(self) -> None:
        old_mask = audit.MASK
        try:
            audit.MASK = 0b1111
            values = [0b0101, 0b0000]
            drivens = [0b0011, 0b0110]
            bits, driven, conflict = audit.resolve_packed([0, 1], values, drivens)
            self.assertEqual(bits, 0b0001)
            self.assertEqual(driven, 0b0111)
            self.assertEqual(conflict, 0)
            values[1] = 0b0010
            _, _, conflict = audit.resolve_packed([0, 1], values, drivens)
            self.assertEqual(conflict, 0b0010)
        finally:
            audit.MASK = old_mask

    def test_physical_partition_requires_equal_overlapping_driver_sets(self) -> None:
        self.assertEqual(audit.physical_partition_violations([[1, 2], [1, 2], [3]]), 0)
        self.assertEqual(audit.physical_partition_violations([[1, 2], [2, 3]]), 1)

    def test_expected_matrix_has_eight_negative_and_four_positive_records(self) -> None:
        matrix = audit.expected_files()
        self.assertEqual(len(matrix), 12)
        self.assertEqual(sum(variant != "positive" for _, variant, _ in matrix.values()), 8)
        self.assertEqual(sum(variant == "positive" for _, variant, _ in matrix.values()), 4)


if __name__ == "__main__":
    unittest.main()
