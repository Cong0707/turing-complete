from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tc_save_lab.circumference_asic import (
    NODES,
    build_circumference_asic,
    circumference,
    evaluate_network,
    network_metrics,
    verify_circumference_asic,
    write_circumference_asic,
)
from tc_save_lab.codec import decode_v15


class CircumferenceAsicTests(unittest.TestCase):
    def test_level_contract_is_exhaustive(self) -> None:
        for radius in range(1, 42):
            self.assertEqual(circumference(radius), radius * 6)
        for radius in (0, 42, 63):
            with self.assertRaises(ValueError):
                circumference(radius)
        for radius in (-1, 64):
            with self.assertRaises(ValueError):
                evaluate_network(radius)

    def test_reviewed_network_matches_area_delay_frontier(self) -> None:
        metrics = network_metrics()
        self.assertEqual(metrics["gate"], 31)
        self.assertEqual(metrics["delay"], 5)
        self.assertEqual(metrics["energy"], 155)
        self.assertEqual(metrics["physical_gate_component_count"], len(NODES))
        self.assertEqual(
            metrics["output_depths"],
            {"zero": 0, "b0": 0, "y2": 2, "y3": 4, "y4": 5, "y5": 5, "y6": 5, "y7": 4},
        )

    def test_candidate_connectivity_and_header(self) -> None:
        result = verify_circumference_asic()
        self.assertEqual((result["gate"], result["delay"]), (31, 5))
        self.assertEqual(result["tested_vector_count"], 41)
        self.assertEqual(result["connectivity"]["unconnected_pin_count"], 1)
        self.assertEqual(result["connectivity"]["unconnected_pins"][0]["name"], "out7")

    def test_generated_candidate_is_deterministic_v15(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = write_circumference_asic(root)
            path = root / "examples" / "circumference" / "candidate" / "circuit.data"
            payload = path.read_bytes()
            second = write_circumference_asic(root)
            self.assertEqual(first, second)
            self.assertEqual(payload, path.read_bytes())
            self.assertEqual(decode_v15(payload), build_circumference_asic())


if __name__ == "__main__":
    unittest.main()
