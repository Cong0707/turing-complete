from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tc_save_lab.analysis import analyze_circuit, wire_points
from tc_save_lab.model import Circuit, Wire


class AnalysisTests(unittest.TestCase):
    def test_expands_diagonal_path_and_counts_bends(self):
        wire = Wire(0, "", (0, 0), ((0, 2), (2, 2), (4, 1)))
        self.assertEqual(
            wire_points(wire),
            ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2)),
        )
        metrics = analyze_circuit(Circuit(wires=(wire,)))
        self.assertEqual(metrics["wire"]["total_length"], 5)
        self.assertEqual(metrics["wire"]["bend_count"], 2)
        self.assertEqual(metrics["wire"]["bounding_box"], {
            "min_x": 0, "min_y": 0, "max_x": 2, "max_y": 2,
            "width": 3, "height": 3,
        })

    def test_wire_overlap_forms_one_network(self):
        circuit = Circuit(
            wires=(
                Wire(0, "", (0, 0), ((0, 3),)),
                Wire(0, "", (1, 0), ((2, 2),)),
                Wire(0, "", (8, 8), ((0, 1),)),
            )
        )
        metrics = analyze_circuit(circuit)
        self.assertEqual(metrics["wire"]["network_count"], 2)
        self.assertGreater(metrics["wire"]["shared_point_count"], 0)

    def test_teleport_is_reported_separately(self):
        circuit = Circuit(wires=(Wire(0, "", (0, 0), (), (5, 7)),))
        metrics = analyze_circuit(circuit, format_version=7)
        self.assertEqual(metrics["wire"]["teleport_wire_count"], 1)
        self.assertEqual(metrics["wire"]["total_length"], 0)
