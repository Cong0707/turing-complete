from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


verifier = load_module(
    "interleaved_high29_contract_verifier",
    HERE / "verify_fixed73_high29_physical_witness.py",
)
combiner = load_module(
    "interleaved_high29_contract_combiner",
    ROOT / ".research/byte_adder_paper_synthesis_root/combine_s34_free_tail_high29.py",
)
graft = load_module(
    "interleaved_high29_contract_graft",
    HERE / "graft_fixed73_high29_physical_witness.py",
)


def interleaved_s3_payload() -> dict[str, object]:
    source_index = {
        name: index for index, name in enumerate(verifier.SOURCE_NAMES)
    }
    source_count = len(verifier.SOURCE_NAMES)
    network = [
        {
            "slot": 0,
            "source": source_count,
            "kind": "SWITCH",
            "left_bus": [source_index["Q3"]],
            "right_bus": [source_index["1"]],
            "cost": 2,
            "depth_upper_bound": 2,
        },
        {
            "slot": 1,
            "source": source_count + 1,
            "kind": "SWITCH",
            "left_bus": [source_index["P3"]],
            "right_bus": [source_index["0"]],
            "cost": 2,
            "depth_upper_bound": 3,
        },
        {
            "slot": 2,
            "source": source_count + 2,
            "kind": "SWITCH",
            "left_bus": [source_index["G3"]],
            "right_bus": [source_index["1"]],
            "cost": 2,
            "depth_upper_bound": 2,
        },
        {
            "slot": 3,
            "source": source_count + 3,
            "kind": "XOR",
            "left_bus": [source_count, source_count + 1, source_count + 2],
            "right_bus": [source_index["nC3"]],
            "cost": 3,
            "depth_upper_bound": 5,
        },
    ]
    return {
        "schema": verifier.SCHEMA,
        "status": "sat",
        "domain": verifier.DOMAIN,
        "rows": verifier.DOMAIN_ROWS,
        "output_names": ["S3"],
        "free_sources": list(verifier.SOURCE_NAMES),
        "source_arrivals": verifier.SOURCE_ARRIVALS,
        "physical_nets": True,
        "public_outputs_must_be_driven": True,
        "dependency_sha256": verifier._dependency_hashes(),
        "max_delay": 5,
        "components": 4,
        "exact_switches": 3,
        "exact_xors": 1,
        "ordinary": 0,
        "gate_bound": 9,
        "actual_gate": 9,
        "fixed_kinds": ["SWITCH", "SWITCH", "SWITCH", "XOR"],
        "network": network,
        "output_buses": [[source_count + 3]],
        "verification": {
            "mismatch_count": 0,
            "bus_conflict_count": 0,
            "undriven_output_count": 0,
            "physical_net_partition_violation_count": 0,
            "actual_output_arrivals": [5],
            "actual_max_delay": 5,
            "depth_upper_bound_violation_count": 0,
            "output_deadline_violation_count": 0,
        },
    }


def z_normalized_interleaved_s3_payload() -> dict[str, object]:
    payload = interleaved_s3_payload()
    source_count = len(verifier.SOURCE_NAMES)
    q_driver, _zero_driver, g_driver, xor = payload["network"]
    payload["network"] = [
        q_driver,
        {**g_driver, "slot": 1, "source": source_count + 1},
        {
            **xor,
            "slot": 2,
            "source": source_count + 2,
            "left_bus": [source_count, source_count + 1],
        },
    ]
    payload.update(
        {
            "components": 3,
            "exact_switches": 2,
            "gate_bound": 7,
            "actual_gate": 7,
            "fixed_kinds": ["SWITCH", "SWITCH", "XOR"],
            "output_buses": [[source_count + 2]],
        }
    )
    return payload


class InterleavedHigh29ContractTests(unittest.TestCase):
    def test_combiner_remaps_interleaved_tail_bus_after_s34(self):
        payload = interleaved_s3_payload()
        free_map = {
            name: index for index, name in enumerate(verifier.SOURCE_NAMES)
        }
        network, output_buses, _local_map, next_source = combiner.remap_network(
            payload,
            free_map,
            next_source=38,
            standard_source_count=len(verifier.SOURCE_NAMES),
        )

        self.assertEqual([item["slot"] for item in network], [9, 10, 11, 12])
        self.assertEqual([item["source"] for item in network], [38, 39, 40, 41])
        self.assertEqual(network[3]["left_bus"], [38, 39, 40])
        self.assertEqual(network[3]["right_bus"], [0])
        self.assertEqual(output_buses, [[41]])
        self.assertEqual(next_source, 42)

    def test_combiner_accepts_ordinary_after_resolved_bus(self):
        payload = interleaved_s3_payload()
        network = payload["network"]
        output_buses = payload["output_buses"]
        domain = combiner.physical.domain_s34567c8_leaf()
        source_arrivals = [
            domain.arrivals.get(name, 0) for name in verifier.SOURCE_NAMES
        ]
        structure = combiner._audit_structure(
            network,
            output_buses,
            source_count=len(verifier.SOURCE_NAMES),
            source_arrivals=source_arrivals,
        )
        semantic = combiner._audit_semantics(
            domain, network, output_buses, ("S3",)
        )

        self.assertEqual(structure["errors"], [])
        self.assertEqual(structure["gate"], 9)
        self.assertEqual(structure["actual_output_arrivals"], [5])
        self.assertEqual(structure["physical_net_partition_violation_count"], 0)
        self.assertEqual(structure["dead_component_output_count"], 0)
        self.assertEqual(semantic["mismatch_count"], 0)
        self.assertEqual(semantic["bus_conflict_count"], 0)
        self.assertEqual(semantic["undriven_output_count"], 0)

    def test_independent_verifier_replays_486_and_131072_rows(self):
        payload = interleaved_s3_payload()
        with tempfile.TemporaryDirectory(prefix="interleaved_contract_", dir=HERE) as tmp:
            witness = Path(tmp) / "fixture.json"
            witness.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            report = verifier.verify_witness(witness, fixture=True)

        for replay, rows in (
            (report["reduced_replay"], 486),
            (report["full_replay"], 1 << 17),
        ):
            self.assertEqual(replay["rows"], rows)
            self.assertEqual(replay["mismatch_union_count"], 0)
            self.assertEqual(replay["bus_conflict_count"], 0)
            self.assertEqual(replay["z_assignment_count_by_output"], [0])
            self.assertEqual(replay["output_arrivals"], [5])

    def test_factory_graft_preserves_resolved_bus_node(self):
        payload = interleaved_s3_payload()
        shell = graft._build_fixed_shell()
        first_new_node = len(shell.factory.nodes)
        outputs, _nodes, switches = graft.materialize_exact_network(
            shell.factory, payload, shell.named
        )

        output = shell.factory.nodes[outputs[0]]
        new_nodes = shell.factory.nodes[first_new_node:]
        self.assertEqual([node.op for node in new_nodes], ["BUS", "XOR"])
        self.assertEqual(sum(node.cost for node in new_nodes), 9)
        self.assertEqual(len(switches), 3)
        self.assertEqual(output.op, "XOR")
        self.assertEqual(output.arrival, 5)

        exact_bus_id = first_new_node
        exact_bus = shell.factory.nodes[exact_bus_id]
        self.assertEqual(exact_bus.op, "BUS")
        self.assertEqual(exact_bus.cost, 6)
        self.assertEqual(exact_bus.arrival, 3)
        self.assertEqual(len(exact_bus.args), 6)
        self.assertIn(exact_bus_id, output.args)
        self.assertIn(shell.named["nC3"], output.args)
        self.assertEqual(shell.factory.nodes[shell.named["nC3"]].op, "BUS")

    def test_factory_graft_keeps_z_normalizing_ordinary_gate(self):
        for kind, right_source, gate_cost, arrival in (
            ("AND", 2, 1, 2),
            ("OR", 1, 1, 2),
            ("XOR", 1, 3, 3),
        ):
            with self.subTest(kind=kind):
                factory = graft.core.Factory()
                payload = {
                    "free_sources": ["en", "0", "1"],
                    "network": [
                        {
                            "slot": 0,
                            "source": 3,
                            "kind": "SWITCH",
                            "left_bus": [0],
                            "right_bus": [2],
                            "cost": 2,
                            "depth_upper_bound": 1,
                        },
                        {
                            "slot": 1,
                            "source": 4,
                            "kind": kind,
                            "left_bus": [3],
                            "right_bus": [right_source],
                            "cost": gate_cost,
                            "depth_upper_bound": arrival,
                        },
                    ],
                    "output_buses": [[4]],
                }
                first_new_node = len(factory.nodes)
                outputs, nodes, switches = graft.materialize_exact_network(
                    factory,
                    payload,
                    {
                        "en": factory.inputs["a0"],
                        "0": factory.const0,
                        "1": factory.const1,
                    },
                )

                new_nodes = factory.nodes[first_new_node:]
                output = factory.nodes[outputs[0]]
                self.assertEqual([node.op for node in new_nodes], ["BUS", kind])
                self.assertEqual(sum(node.cost for node in new_nodes), 2 + gate_cost)
                self.assertEqual(len(switches), 1)
                self.assertEqual(nodes[4], outputs[0])
                self.assertEqual(output.op, kind)
                self.assertEqual(output.arrival, arrival)
                self.assertFalse(output.may_z)

    def test_factory_graft_keeps_double_not_over_z_bus(self):
        factory = graft.core.Factory()
        payload = {
            "free_sources": ["en", "0", "1"],
            "network": [
                {
                    "slot": 0,
                    "source": 3,
                    "kind": "SWITCH",
                    "left_bus": [0],
                    "right_bus": [2],
                    "cost": 2,
                    "depth_upper_bound": 1,
                },
                {
                    "slot": 1,
                    "source": 4,
                    "kind": "NOT",
                    "left_bus": [3],
                    "right_bus": [],
                    "cost": 1,
                    "depth_upper_bound": 2,
                },
                {
                    "slot": 2,
                    "source": 5,
                    "kind": "NOT",
                    "left_bus": [4],
                    "right_bus": [],
                    "cost": 1,
                    "depth_upper_bound": 3,
                },
            ],
            "output_buses": [[5]],
        }
        first_new_node = len(factory.nodes)
        outputs, nodes, switches = graft.materialize_exact_network(
            factory,
            payload,
            {"en": factory.inputs["a0"], "0": factory.const0, "1": factory.const1},
        )

        new_nodes = factory.nodes[first_new_node:]
        output = factory.nodes[outputs[0]]
        self.assertEqual([node.op for node in new_nodes], ["BUS", "NOT", "NOT"])
        self.assertEqual(sum(node.cost for node in new_nodes), 4)
        self.assertEqual(len(switches), 1)
        self.assertEqual(nodes[5], outputs[0])
        self.assertEqual(output.op, "NOT")
        self.assertEqual(output.args, (nodes[4],))
        self.assertEqual(output.arrival, 3)
        self.assertFalse(output.may_z)

    def test_factory_graft_keeps_always_enabled_switch_over_z_bus(self):
        factory = graft.core.Factory()
        payload = {
            "free_sources": ["en", "0", "1"],
            "network": [
                {
                    "slot": 0,
                    "source": 3,
                    "kind": "SWITCH",
                    "left_bus": [0],
                    "right_bus": [2],
                    "cost": 2,
                    "depth_upper_bound": 1,
                },
                {
                    "slot": 1,
                    "source": 4,
                    "kind": "SWITCH",
                    "left_bus": [2],
                    "right_bus": [3],
                    "cost": 2,
                    "depth_upper_bound": 2,
                },
            ],
            "output_buses": [[4]],
        }
        first_new_node = len(factory.nodes)
        outputs, _nodes, switches = graft.materialize_exact_network(
            factory,
            payload,
            {"en": factory.inputs["a0"], "0": factory.const0, "1": factory.const1},
        )

        new_nodes = factory.nodes[first_new_node:]
        output = factory.nodes[outputs[0]]
        self.assertEqual([node.op for node in new_nodes], ["BUS", "BUS"])
        self.assertEqual(sum(node.cost for node in new_nodes), 4)
        self.assertEqual(len(switches), 2)
        self.assertNotEqual(outputs[0], first_new_node)
        self.assertEqual(output.op, "BUS")
        self.assertEqual(output.arrival, 2)
        self.assertEqual(output.args, (factory.const1, first_new_node))

    def test_valid_z_normalizing_interleaved_s3_full_replay_and_factory(self):
        payload = z_normalized_interleaved_s3_payload()
        domain = combiner.physical.domain_s34567c8_leaf()
        columns = dict(zip(domain.names, domain.columns, strict=True))
        undriven_rows = sum(
            not (q3 or g3)
            for q3, g3 in zip(columns["Q3"], columns["G3"], strict=True)
        )
        self.assertEqual(undriven_rows, 162)

        with tempfile.TemporaryDirectory(prefix="interleaved_z_", dir=HERE) as tmp:
            witness = Path(tmp) / "fixture.json"
            witness.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            report = verifier.verify_witness(witness, fixture=True)
        for replay in (report["reduced_replay"], report["full_replay"]):
            self.assertEqual(replay["mismatch_union_count"], 0)
            self.assertEqual(replay["bus_conflict_count"], 0)
            self.assertEqual(replay["z_assignment_count_by_output"], [0])

        shell = graft._build_fixed_shell()
        first_new_node = len(shell.factory.nodes)
        outputs, _nodes, switches = graft.materialize_exact_network(
            shell.factory, payload, shell.named
        )
        new_nodes = shell.factory.nodes[first_new_node:]
        self.assertEqual([node.op for node in new_nodes], ["BUS", "XOR"])
        self.assertEqual(sum(node.cost for node in new_nodes), 7)
        self.assertEqual(len(switches), 2)
        self.assertTrue(new_nodes[0].may_z)
        self.assertFalse(shell.factory.nodes[outputs[0]].may_z)
        self.assertEqual(shell.factory.nodes[outputs[0]].arrival, 5)


if __name__ == "__main__":
    unittest.main()
