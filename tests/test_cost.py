from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tc_save_lab.codec import encode_v15
from tc_save_lab.cost import analyze_custom_costs
from tc_save_lab.model import Circuit, Component


DESIGN = bytes(512)


def write_custom(
    root: Path,
    name: str,
    custom_id: int,
    gate: int,
    delay: int,
    children: tuple[int, ...] = (),
) -> None:
    components = tuple(
        Component(
            78,
            (index * 3, 0),
            0,
            custom_id * 100 + index + 1,
            custom_id=child_id,
        )
        for index, child_id in enumerate(children)
    )
    circuit = Circuit(
        custom_id=custom_id,
        gate=gate,
        delay=delay,
        dependencies=tuple(sorted(set(children))),
        design=DESIGN,
        components=components,
    )
    path = root / name / "circuit.data"
    path.parent.mkdir(parents=True)
    path.write_bytes(encode_v15(circuit))


class CostModelTests(unittest.TestCase):
    def test_recursive_gate_expansion_matches_nested_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_custom(root, "leaf", 1, 10, 2)
            write_custom(root, "pair", 2, 25, 4, (1, 1))
            write_custom(root, "top", 3, 30, 7, (2,))

            report = analyze_custom_costs(root)

            self.assertTrue(report["healthy"])
            records = {item["custom_id"]: item for item in report["circuits"]}
            self.assertEqual(records[1]["local_gate_excluding_children"], 10)
            self.assertEqual(records[2]["local_gate_excluding_children"], 5)
            self.assertEqual(records[3]["local_gate_excluding_children"], 5)
            self.assertEqual(records[3]["recursive_gate"], 30)

    def test_missing_dependency_is_explicit_and_not_resolved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_custom(root, "broken", 1, 10, 2, (999,))

            report = analyze_custom_costs(root)

            self.assertFalse(report["healthy"])
            self.assertEqual(report["missing_dependency_ids"], [999])
            self.assertIsNone(report["circuits"][0]["recursive_gate"])

    def test_cycles_and_duplicate_ids_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_custom(root, "a", 1, 10, 2, (2,))
            write_custom(root, "b", 2, 10, 2, (1,))
            write_custom(root, "a-copy", 1, 10, 2, (2,))

            report = analyze_custom_costs(root)

            self.assertFalse(report["healthy"])
            self.assertIn("1", report["duplicate_custom_ids"])
            self.assertTrue(report["cycle_ids"])


if __name__ == "__main__":
    unittest.main()
