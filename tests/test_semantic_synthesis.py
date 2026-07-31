from __future__ import annotations

import unittest

from tc_save_lab.semantic_synthesis import make_truth_tables, synthesize_pareto


class SemanticSynthesisTests(unittest.TestCase):
    def test_truth_table_packing_uses_input_zero_as_low_assignment_bit(self):
        xor, carry = make_truth_tables(2, lambda bits: (bits[0] ^ bits[1], bits[0] & bits[1]))
        self.assertEqual(xor, 0b0110)
        self.assertEqual(carry, 0b1000)

    def test_aig_inversion_is_a_free_edge(self):
        (not_a,) = make_truth_tables(1, lambda bits: 1 - bits[0])
        report = synthesize_pareto(1, (not_a,), library="aig", max_gates=0, state_limit=None)

        self.assertTrue(report.exhaustive)
        self.assertEqual([(item.gate_count, item.depth) for item in report.candidates], [(0, 0)])
        self.assertEqual(report.candidates[0].network.truth_tables(), (not_a,))

    def test_nand_inversion_requires_one_gate(self):
        (not_a,) = make_truth_tables(1, lambda bits: 1 - bits[0])
        report = synthesize_pareto(1, (not_a,), library="nand", max_gates=1, state_limit=None)

        self.assertTrue(report.exhaustive)
        self.assertEqual([(item.gate_count, item.depth) for item in report.candidates], [(1, 1)])
        self.assertEqual(report.candidates[0].network.truth_tables(), (not_a,))

    def test_aig_shares_and_node_with_half_adder_outputs(self):
        targets = make_truth_tables(2, lambda bits: (bits[0] ^ bits[1], bits[0] & bits[1]))
        report = synthesize_pareto(2, targets, library="aig", max_gates=3, state_limit=None)

        self.assertTrue(report.exhaustive)
        self.assertEqual([(item.gate_count, item.depth) for item in report.candidates], [(3, 2)])
        self.assertEqual(report.candidates[0].network.truth_tables(), targets)

    def test_nand_half_adder_uses_five_shared_gates(self):
        targets = make_truth_tables(2, lambda bits: (bits[0] ^ bits[1], bits[0] & bits[1]))
        report = synthesize_pareto(2, targets, library="nand", max_gates=5, state_limit=None)

        self.assertTrue(report.exhaustive)
        self.assertEqual([(item.gate_count, item.depth) for item in report.candidates], [(5, 3)])
        self.assertEqual(report.candidates[0].network.truth_tables(), targets)

    def test_state_limit_marks_result_as_heuristic(self):
        (xor,) = make_truth_tables(2, lambda bits: bits[0] ^ bits[1])
        report = synthesize_pareto(2, (xor,), library="nand", max_gates=4, state_limit=1)

        self.assertFalse(report.exhaustive)
        self.assertTrue(report.truncated_layers)

    def test_later_truncation_does_not_invalidate_an_earlier_proof(self):
        (and_gate,) = make_truth_tables(2, lambda bits: bits[0] & bits[1])
        report = synthesize_pareto(2, (and_gate,), library="aig", max_gates=2, state_limit=5)

        self.assertFalse(report.exhaustive)
        self.assertEqual(report.exhaustive_through, 1)
        self.assertEqual([(item.gate_count, item.depth) for item in report.candidates], [(1, 1)])
        self.assertTrue(report.candidates[0].exhaustive)

    def test_input_and_target_validation(self):
        with self.assertRaisesRegex(ValueError, "one to four"):
            synthesize_pareto(5, (0,), max_gates=1)
        with self.assertRaisesRegex(ValueError, "fit mask"):
            synthesize_pareto(1, (4,), max_gates=1)


if __name__ == "__main__":
    unittest.main()
