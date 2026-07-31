from __future__ import annotations

import unittest

from tc_save_lab.exact_synthesis import (
    SearchLimitExceeded,
    input_truth_table,
    synthesize_exact,
    truth_table_from_callable,
)


class ExactSynthesisTests(unittest.TestCase):
    def test_truth_table_assignment_order(self):
        self.assertEqual(input_truth_table(2, 0), 0b1010)
        self.assertEqual(input_truth_table(2, 1), 0b1100)
        self.assertEqual(truth_table_from_callable(2, lambda x, y: x ^ y), 0b0110)

    def test_nand_exact_not_and_xor(self):
        not_x = truth_table_from_callable(1, lambda x: 1 ^ x)
        result = synthesize_exact(1, (not_x,), basis="nand", max_gates=1)
        self.assertEqual([(item.gate_count, item.depth) for item in result.frontier], [(1, 1)])

        xor = truth_table_from_callable(2, lambda x, y: x ^ y)
        result = synthesize_exact(2, (xor,), basis="nand", max_gates=4)
        self.assertEqual([(item.gate_count, item.depth) for item in result.frontier], [(4, 3)])
        self.assertEqual([result.frontier[0].evaluate(i)[0] for i in range(4)], [0, 1, 1, 0])

    def test_aig_free_output_inversion(self):
        not_x = truth_table_from_callable(1, lambda x: 1 ^ x)
        result = synthesize_exact(1, (not_x,), basis="aig", max_gates=0)
        self.assertEqual([(item.gate_count, item.depth) for item in result.frontier], [(0, 0)])

    def test_xag_joint_half_adder(self):
        xor = truth_table_from_callable(2, lambda x, y: x ^ y)
        carry = truth_table_from_callable(2, lambda x, y: x & y)
        result = synthesize_exact(2, (xor, carry), basis="xag", max_gates=2)
        self.assertEqual([(item.gate_count, item.depth) for item in result.frontier], [(2, 1)])
        self.assertEqual(
            [result.frontier[0].evaluate(i) for i in range(4)],
            [(0, 0), (1, 0), (1, 0), (0, 1)],
        )

    def test_four_inputs_are_supported(self):
        x3 = input_truth_table(4, 3)
        result = synthesize_exact(4, (x3,), basis="nand", max_gates=0)
        self.assertEqual(result.frontier[0].output_truth_tables(), (x3,))

    def test_state_limit_fails_closed(self):
        xor = truth_table_from_callable(2, lambda x, y: x ^ y)
        with self.assertRaises(SearchLimitExceeded):
            synthesize_exact(2, (xor,), basis="nand", max_gates=4, max_states=1)


if __name__ == "__main__":
    unittest.main()
