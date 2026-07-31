from __future__ import annotations

import random
import unittest

from tc_save_lab.logic_network import (
    ABSTRACT_XAG_COST,
    CostModel,
    CostPoint,
    LogicBuilder,
    LogicNetworkError,
    NandOp,
    estimate_cost,
    estimate_turing_cost,
    lower_to_nand,
    merge_networks,
    pareto_front,
    rewrite_network,
)


def _all_assignments(*names: str):
    for assignment in range(1 << len(names)):
        yield {
            name: (assignment >> index) & 1
            for index, name in enumerate(names)
        }


class LogicBuilderTests(unittest.TestCase):
    def test_structural_hashing_constants_and_complements(self):
        builder = LogicBuilder()
        a = builder.input("a")
        b = builder.input("b")

        self.assertEqual(builder.and_(a, b), builder.and_(b, a))
        self.assertEqual(builder.and_(a, builder.true), a)
        self.assertEqual(builder.and_(a, ~a), builder.false)
        self.assertEqual(builder.xor(a, a), builder.false)
        self.assertEqual(builder.xor(a, ~a), builder.true)
        self.assertEqual(builder.xor(~a, b), ~builder.xor(a, b))

    def test_absorption_and_complemented_absorption(self):
        builder = LogicBuilder()
        a = builder.input("a")
        b = builder.input("b")
        ab = builder.and_(a, b)

        self.assertEqual(builder.and_(a, ab), ab)
        self.assertEqual(builder.and_(a, ~ab), builder.and_(a, ~b))

    def test_xag_weighted_absorption_and_common_factor_rules(self):
        builder = LogicBuilder()
        a = builder.input("a")
        b = builder.input("b")
        c = builder.input("c")

        expected = builder.and_(a, ~b)
        self.assertEqual(builder.xor(a, builder.and_(a, b)), expected)
        self.assertEqual(builder.and_(a, builder.xor(a, b)), expected)
        self.assertEqual(
            builder.xor(builder.and_(a, b), builder.and_(a, c)),
            builder.and_(a, builder.xor(b, c)),
        )

    def test_multi_output_truth_tables_use_one_shared_graph(self):
        builder = LogicBuilder()
        a = builder.input("a")
        b = builder.input("b")
        shared = builder.and_(a, b)
        builder.output("and", shared)
        builder.output("nand", ~shared)
        network = builder.build()

        self.assertEqual(network.truth_tables(), {"and": 0b1000, "nand": 0b0111})
        self.assertEqual(len(network.reachable_nodes()), 3)


class RewriteTests(unittest.TestCase):
    def test_balances_associative_and_tree_without_changing_function(self):
        builder = LogicBuilder()
        inputs = [builder.input(name) for name in ("a", "b", "c", "d")]
        chain = builder.and_many(inputs, balanced=False)
        builder.output("y", chain)
        original = builder.build()

        balanced = rewrite_network(original, balance_associative=True)
        self.assertEqual(original.truth_tables(), balanced.truth_tables())
        self.assertEqual(estimate_cost(original, ABSTRACT_XAG_COST).delay, 3)
        self.assertEqual(estimate_cost(balanced, ABSTRACT_XAG_COST).delay, 2)

    def test_aig_lowering_removes_xor_nodes_and_is_exhaustively_equivalent(self):
        builder = LogicBuilder()
        a = builder.input("a")
        b = builder.input("b")
        c = builder.input("c")
        builder.output("sum", builder.xor_many((a, b, c)))
        xag = builder.build()

        aig = rewrite_network(xag, basis="aig")
        self.assertTrue(aig.is_aig)
        self.assertEqual(xag.truth_tables(), aig.truth_tables())

    def test_merge_unifies_inputs_and_cross_output_subexpressions(self):
        left_builder = LogicBuilder()
        left_a = left_builder.input("a")
        left_b = left_builder.input("b")
        left_builder.output("y", left_builder.and_(left_a, left_b))

        right_builder = LogicBuilder()
        right_a = right_builder.input("a")
        right_b = right_builder.input("b")
        right_c = right_builder.input("c")
        right_builder.output(
            "y",
            right_builder.xor(right_builder.and_(right_a, right_b), right_c),
        )

        merged = merge_networks({"f": left_builder.build(), "g": right_builder.build()})
        self.assertEqual(merged.input_names, ("a", "b", "c"))
        operator_nodes = [node for node in merged.nodes if node.op.value in {"and", "xor"}]
        self.assertEqual(len(operator_nodes), 2)
        for inputs in _all_assignments("a", "b", "c"):
            outputs = merged.evaluate(inputs)
            shared = inputs["a"] & inputs["b"]
            self.assertEqual(outputs, {"f.y": shared, "g.y": shared ^ inputs["c"]})

    def test_deterministic_random_networks_survive_all_basis_rewrites(self):
        rng = random.Random(20260801)
        for _ in range(50):
            builder = LogicBuilder()
            signals = [builder.input(name) for name in ("a", "b", "c", "d")]
            operations = (builder.and_, builder.nand, builder.or_, builder.xor, builder.xnor)
            for _ in range(12):
                result = rng.choice(operations)(rng.choice(signals), rng.choice(signals))
                signals.append(~result if rng.randrange(4) == 0 else result)
            for index, signal in enumerate(rng.sample(signals, 3)):
                builder.output(f"y{index}", signal)
            source = builder.build()
            expected = source.truth_tables()
            self.assertEqual(rewrite_network(source, basis="xag").truth_tables(), expected)
            self.assertEqual(rewrite_network(source, basis="aig").truth_tables(), expected)
            self.assertEqual(lower_to_nand(source).truth_tables(), expected)


class CostTests(unittest.TestCase):
    def test_complemented_edges_are_never_implicitly_free(self):
        builder = LogicBuilder()
        a = builder.input("a")
        b = builder.input("b")
        nand = builder.nand(a, b)
        builder.output("nand", nand)
        network = builder.build()

        self.assertEqual(estimate_cost(network, ABSTRACT_XAG_COST), CostPoint(1, 1))
        self.assertEqual(estimate_cost(network), CostPoint(2, 2))

    def test_shared_inverse_is_counted_once(self):
        builder = LogicBuilder()
        a = builder.input("a")
        b = builder.input("b")
        c = builder.input("c")
        inverted = ~builder.and_(a, b)
        builder.output("x", inverted)
        builder.output("y", builder.and_(inverted, c))
        network = builder.build()

        cost = estimate_cost(network, CostModel())
        self.assertEqual(cost.gates, 3)
        self.assertEqual(cost.delay, 3)

    def test_turing_mapping_absorbs_native_nand_and_prices_xor(self):
        nand_builder = LogicBuilder()
        a = nand_builder.input("a")
        b = nand_builder.input("b")
        nand_builder.output("y", nand_builder.nand(a, b))
        self.assertEqual(estimate_turing_cost(nand_builder.build()), CostPoint(1, 1))

        xor_builder = LogicBuilder()
        a = xor_builder.input("a")
        b = xor_builder.input("b")
        value = xor_builder.xor(a, b)
        xor_builder.output("xor", value)
        xor_builder.output("xnor", ~value)
        self.assertEqual(estimate_turing_cost(xor_builder.build()), CostPoint(4, 2))

    def test_turing_mapping_charges_both_required_and_phases(self):
        builder = LogicBuilder()
        a = builder.input("a")
        b = builder.input("b")
        value = builder.and_(a, b)
        builder.output("and", value)
        builder.output("nand", ~value)
        self.assertEqual(estimate_turing_cost(builder.build()), CostPoint(2, 1))

    def test_pareto_front_removes_dominated_and_duplicate_points(self):
        front = pareto_front((
            CostPoint(7, 4, "low-gate"),
            CostPoint(14, 3, "low-delay"),
            CostPoint(8, 5, "dominated"),
            CostPoint(7, 4, "same-point-later"),
        ))
        self.assertEqual({(point.gates, point.delay) for point in front}, {(7, 4), (14, 3)})
        self.assertEqual(next(point.label for point in front if point.gates == 7), "low-gate")


class NandLoweringTests(unittest.TestCase):
    def test_lowering_uses_only_nand_and_preserves_multiple_outputs(self):
        builder = LogicBuilder()
        a = builder.input("a")
        b = builder.input("b")
        conjunction = builder.and_(a, b)
        builder.output("and", conjunction)
        builder.output("nand", ~conjunction)
        builder.output("xor", builder.xor(a, b))
        source = builder.build()

        nand = lower_to_nand(source)
        self.assertTrue(all(node.op in {NandOp.INPUT, NandOp.NAND} for node in nand.nodes))
        self.assertEqual(nand.gate_count, 5)
        self.assertEqual(nand.delay, 3)
        for inputs in _all_assignments("a", "b"):
            self.assertEqual(nand.evaluate(inputs), source.evaluate(inputs))

    def test_constant_output_is_synthesized_from_an_input(self):
        builder = LogicBuilder()
        builder.input("seed")
        builder.output("zero", builder.false)
        builder.output("one", builder.true)
        nand = lower_to_nand(builder.build())

        self.assertEqual(nand.evaluate({"seed": 0}), {"zero": 0, "one": 1})
        self.assertEqual(nand.evaluate({"seed": 1}), {"zero": 0, "one": 1})

    def test_constant_only_network_fails_closed(self):
        builder = LogicBuilder()
        builder.output("one", builder.true)
        with self.assertRaisesRegex(LogicNetworkError, "needs an input"):
            lower_to_nand(builder.build())


if __name__ == "__main__":
    unittest.main()
