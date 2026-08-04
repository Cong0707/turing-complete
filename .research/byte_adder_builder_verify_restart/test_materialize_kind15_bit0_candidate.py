from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "materialize_kind15_bit0_candidate.py"
SPEC = importlib.util.spec_from_file_location("materialize_kind15_bit0_candidate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Kind15Bit0CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.original = json.loads(MODULE.AUTHORITATIVE_DAG.read_text(encoding="utf-8"))

    def test_exact_transformation_is_77_9_not_77_7(self) -> None:
        transformed = MODULE.transform_authoritative(self.original)
        self.assertEqual(transformed["metrics"]["gate"], 77)
        self.assertEqual(transformed["metrics"]["delay"], 9)
        self.assertEqual(transformed["metrics"]["energy"], 693)
        self.assertEqual(
            transformed["metrics"]["output_arrivals"],
            [4, 6, 9, 7, 9, 8, 9, 9, 9],
        )
        self.assertEqual(transformed["timing_delta"]["before"]["C1"], 2)
        self.assertEqual(transformed["timing_delta"]["after"]["C1"], 4)
        self.assertEqual(transformed["semantic"]["mismatch_union_count"], 0)

    def test_transformation_removes_only_private_bit0_nodes(self) -> None:
        transformed = MODULE.transform_authoritative(self.original)
        ids = {int(node["id"]) for node in transformed["factory_dag"]["nodes"]}
        self.assertTrue(MODULE.REMOVED_BIT0_NODES.isdisjoint(ids))
        self.assertIn(MODULE.BIT0_CARRY_NODE, ids)
        self.assertIn(MODULE.BIT0_SUM_NODE, ids)
        self.assertEqual(transformed["factory_dag"]["live_node_count"], 77)

    def test_physical_builder_has_one_explicit_7_4_kind15(self) -> None:
        transformed = MODULE.transform_authoritative(self.original)
        by_id = {int(node["id"]): node for node in transformed["factory_dag"]["nodes"]}
        candidate, _connections, _mapping = MODULE.build_physical(transformed, by_id)
        full_adders = [component for component in candidate.components if component.kind == 15]
        self.assertEqual(len(full_adders), 1)
        self.assertEqual((full_adders[0].cost_gate, full_adders[0].cost_delay), (7, 4))
        self.assertEqual((candidate.gate, candidate.delay, candidate.energy), (77, 9, 693))

    def test_kind15_pin_body_mask_is_anchored_to_v15_baseline(self) -> None:
        contract = MODULE.review_kind15_geometry_contract()
        self.assertEqual(contract["baseline_full_adder_count"], 8)
        self.assertTrue(contract["all_five_pin_offsets_have_wire_endpoints_on_every_instance"])
        self.assertEqual(contract["reviewed_output_lead_offsets"], [[2, 0], [2, 1]])


if __name__ == "__main__":
    unittest.main()
