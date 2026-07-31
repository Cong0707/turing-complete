from __future__ import annotations

import unittest

from tc_save_lab.xag import (
    XagCostModel,
    XagLiteral,
    XagNetwork,
    XagNode,
    XagSynthesisLimitError,
    canonical_truth_table,
    enumerate_xags,
    input_truth_table,
    truth_table_from_callable,
)


class XagTruthTableTests(unittest.TestCase):
    def test_input_order_uses_input_zero_as_assignment_lsb(self):
        self.assertEqual(input_truth_table(2, 0), 0b1010)
        self.assertEqual(input_truth_table(2, 1), 0b1100)

    def test_callable_and_complement_normalization(self):
        xor = truth_table_from_callable(2, lambda a, b: a ^ b)
        self.assertEqual(xor, 0b0110)
        self.assertEqual(canonical_truth_table(xor, 2), (0b0110, False))
        self.assertEqual(canonical_truth_table(xor ^ 0b1111, 2), (0b0110, True))


class XagNetworkTests(unittest.TestCase):
    def test_network_evaluation_and_weighted_metrics(self):
        network = XagNetwork(
            input_count=2,
            nodes=(
                XagNode("xor", XagLiteral(1), XagLiteral(2)),
                XagNode("and", XagLiteral(1), XagLiteral(3)),
            ),
            output=XagLiteral(4),
        )
        expected = truth_table_from_callable(2, lambda a, b: a and (a ^ b))
        self.assertEqual(network.truth_table(), expected)
        metrics = network.metrics(XagCostModel.turing_complete_primitives())
        self.assertEqual((metrics.gate_count, metrics.and_count, metrics.xor_count), (2, 1, 1))
        self.assertEqual((metrics.gate_cost, metrics.delay, metrics.energy), (4, 3, 12))

    def test_forward_reference_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "earlier sources"):
            XagNetwork(
                2,
                (XagNode("and", XagLiteral(4), XagLiteral(1)),),
                XagLiteral(3),
            )


class ExactXagSynthesisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = enumerate_xags(2, 2, max_candidates=20_000)

    def test_complemented_edges_make_not_and_or_zero_or_one_gate(self):
        a = input_truth_table(2, 0)
        not_a = a ^ 0b1111
        conjunction = truth_table_from_callable(2, lambda x, y: x and y)
        disjunction = truth_table_from_callable(2, lambda x, y: x or y)

        self.assertEqual(len(self.database.minimum(not_a).nodes), 0)
        self.assertEqual(len(self.database.minimum(conjunction).nodes), 1)
        self.assertEqual(len(self.database.minimum(disjunction).nodes), 1)
        self.assertEqual(self.database.minimum(disjunction).truth_table(), disjunction)

    def test_xor_has_one_gate_and_all_two_input_classes_are_reached(self):
        xor = truth_table_from_callable(2, lambda a, b: a ^ b)
        network = self.database.minimum(xor)
        self.assertIsNotNone(network)
        self.assertEqual(len(network.nodes), 1)
        self.assertEqual(network.truth_table(), xor)
        # 16 functions collapse to eight classes under free output inversion.
        self.assertEqual(self.database.truth_class_count, 8)

    def test_bounded_pareto_is_nondominated_and_functionally_exact(self):
        function = truth_table_from_callable(2, lambda a, b: a and not b)
        front = self.database.pareto(function, XagCostModel.turing_complete_primitives())
        points = [
            (network.metrics(XagCostModel.turing_complete_primitives()).gate_cost,
             network.metrics(XagCostModel.turing_complete_primitives()).delay)
            for network in front
        ]
        self.assertTrue(front)
        self.assertEqual(len(points), len(set(points)))
        self.assertTrue(all(network.truth_table() == function for network in front))
        for index, point in enumerate(points):
            self.assertFalse(any(
                other[0] <= point[0] and other[1] <= point[1]
                for other_index, other in enumerate(points)
                if other_index != index
            ))

    def test_four_input_simple_function_is_supported(self):
        database = enumerate_xags(4, 1, max_candidates=50_000)
        function = truth_table_from_callable(4, lambda a, b, c, d: a ^ d)
        network = database.minimum(function)
        self.assertIsNotNone(network)
        self.assertEqual(len(network.nodes), 1)
        self.assertEqual(network.truth_table(), function)

    def test_candidate_limit_fails_closed(self):
        with self.assertRaises(XagSynthesisLimitError):
            enumerate_xags(3, 2, max_candidates=4)


if __name__ == "__main__":
    unittest.main()
