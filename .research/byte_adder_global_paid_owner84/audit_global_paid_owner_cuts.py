#!/usr/bin/env python3
"""Audit every paid rail and complete BUS-owner consumer boundary of human85.

This is a deterministic evidence pass, not a circuit search.  It replays the
accepted Factory DAG with the repository's independent physical-state model,
computes fanout/output reachability, and joins the already-recorded bounded
certificates for the only two complete-owner rewrites that reach a one-gate
gap.  It never reads the live save and never launches the game.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = (
    ROOT
    / ".research"
    / "byte_adder_architecture_restart"
    / "byte-adder-human85-s3-positive-phase-full.json"
)
CORE_PATH = (
    ROOT
    / ".research"
    / "byte_adder_conditional_sum_restart"
    / "global_byproduct_core.py"
)
PAID_LEDGER = (
    ROOT
    / ".research"
    / "byte85_paid_phase_ledger"
    / "byte85-paid-phase-ledger.json"
)
C6_AUDIT = (
    ROOT
    / ".research"
    / "byte_adder_c6_joint_owner_recode"
    / "c6-joint-owner-audit.json"
)
GLOBAL_ATLAS = (
    ROOT
    / ".research"
    / "byte_adder_primitive_relation_miner"
    / "human85-global-real-byproduct-atlas-v1.json"
)
NEAR_CUTS = (
    ROOT
    / ".research"
    / "byte_adder_primitive_relation_miner"
    / "human85-near-cut-hyperedges-v1.json"
)
SWITCH_COVERS = (
    ROOT
    / ".research"
    / "byte_adder_primitive_relation_miner"
    / "human85-switch-positive-output-covers-v1.json"
)
LOW_PARTIAL = (
    ROOT
    / ".research"
    / "byte_adder_low_partial_sum"
    / "audit-result-with-sat.json"
)
OUTPUT = HERE / "human85-global-paid-owner-audit-v1.json"

EXPECTED_SOURCE_SHA256 = (
    "b3dbe1d83ed28f32c929f4c840a6fa69a9d747e84895c0df9af794d7f704feee"
)
EXPECTED_STRUCTURAL_SHA256 = (
    "5b3aa51e17c763d85617f28b7db20ac89635157251241498626f2fb148e928ca"
)
OUTPUT_NAMES = ("S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "C8")

ALIASES = {
    18: "B0partial",
    19: "G1",
    20: "V1",
    21: "G0",
    22: "Q0",
    23: "P0",
    24: "Q2",
    25: "G2",
    26: "C2",
    27: "P2",
    28: "R2",
    29: "Q3",
    30: "N23",
    31: "B23",
    32: "G6",
    33: "G7",
    34: "T2",
    35: "Q7",
    36: "C1",
    37: "S1_nand_left",
    38: "S1_nand_right",
    39: "S1_or",
    40: "K67",
    41: "Q6",
    42: "P7",
    43: "S7_reason_left",
    44: "G3",
    45: "S0",
    46: "S1",
    47: "S2",
    48: "P3",
    49: "C4",
    50: "nP6",
    51: "D3",
    52: "Q6P7",
    53: "H7",
    54: "E3",
    55: "O3",
    56: "S3",
    57: "E7",
    58: "G4",
    59: "Q4",
    60: "P4",
    61: "G5",
    62: "Q5",
    63: "P5",
    64: "K34",
    65: "G345",
    66: "V45",
    67: "D45",
    68: "C6",
    69: "T4",
    70: "R4",
    71: "S4",
    72: "D5",
    73: "E5",
    74: "S5",
    75: "A6",
    76: "B6",
    77: "S6",
    78: "Z7",
    79: "C8",
    80: "S7",
}


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def alias(node: dict[str, Any]) -> str:
    node_id = int(node["id"])
    return ALIASES.get(node_id, str(node.get("label") or f"node_{node_id}"))


def build_graph(
    nodes: dict[int, dict[str, Any]],
) -> tuple[dict[int, Counter[int]], dict[int, set[int]]]:
    edge_users: dict[int, Counter[int]] = defaultdict(Counter)
    users: dict[int, set[int]] = defaultdict(set)
    for node_id, node in nodes.items():
        for argument in map(int, node.get("args", ())):
            edge_users[argument][node_id] += 1
            users[argument].add(node_id)
    for node_id in nodes:
        edge_users[node_id]
        users[node_id]
    return edge_users, users


def output_reach(
    nodes: dict[int, dict[str, Any]],
    users: dict[int, set[int]],
    output_by_id: dict[int, str],
) -> dict[int, set[str]]:
    result: dict[int, set[str]] = {}
    for node_id in sorted(nodes, reverse=True):
        reached = {output_by_id[node_id]} if node_id in output_by_id else set()
        for user in users[node_id]:
            reached.update(result[user])
        result[node_id] = reached
    return result


def deadlines(
    nodes: dict[int, dict[str, Any]], output_ids: tuple[int, ...]
) -> dict[int, int | None]:
    infinity = 10**6
    result = {node_id: infinity for node_id in nodes}
    for node_id in output_ids:
        result[node_id] = 6
    for node_id in sorted(nodes, reverse=True):
        if result[node_id] == infinity:
            continue
        step = int(nodes[node_id]["step_delay"])
        for argument in map(int, nodes[node_id].get("args", ())):
            result[argument] = min(result[argument], result[node_id] - step)
    return {
        node_id: None if value == infinity else value
        for node_id, value in result.items()
    }


def direct_roles(
    node_id: int,
    nodes: dict[int, dict[str, Any]],
    users: dict[int, set[int]],
    output_by_id: dict[int, str],
) -> list[dict[str, Any]]:
    roles: list[dict[str, Any]] = []
    for user_id in sorted(users[node_id]):
        user = nodes[user_id]
        if user["op"] == "BUS":
            args = list(map(int, user["args"]))
            pins = [
                "enable" if index % 2 == 0 else "data"
                for index, argument in enumerate(args)
                if argument == node_id
            ]
            if user_id in output_by_id:
                pins.append(f"terminal:{output_by_id[user_id]}")
                kind = "bus_terminal"
            else:
                kind = "bus"
        elif user_id in output_by_id:
            kind = "terminal"
            pins = [output_by_id[user_id]]
        else:
            kind = "ordinary"
            pins = [str(user["op"])]
        roles.append(
            {
                "consumer": user_id,
                "consumer_name": alias(user),
                "kind": kind,
                "pins": pins,
            }
        )
    return roles


def state_signature(state: Any, all_mask: int) -> tuple[int, int, int]:
    return (
        int(state.bits) & all_mask,
        int(state.driven) & all_mask,
        int(state.conflict) & all_mask,
    )


def main() -> int:
    sys.path.insert(0, str(CORE_PATH.parent))
    from global_byproduct_core import (  # type: ignore[import-not-found]
        ALL,
        EXPECTED_OUTPUTS,
        State,
        replay_factory,
    )

    if file_sha(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("authoritative human85 source SHA-256 changed")
    document = load(SOURCE)
    if document["metrics"]["structural_sha256"] != EXPECTED_STRUCTURAL_SHA256:
        raise RuntimeError("authoritative human85 structural SHA-256 changed")

    raw_nodes = list(document["factory_dag"]["nodes"])
    nodes = {int(node["id"]): node for node in raw_nodes}
    output_ids = tuple(map(int, document["factory_dag"]["outputs"]))
    output_by_id = dict(zip(output_ids, OUTPUT_NAMES, strict=True))
    edge_users, users = build_graph(nodes)
    reach = output_reach(nodes, users, output_by_id)
    latest = deadlines(nodes, output_ids)
    states = replay_factory(raw_nodes)

    output_mismatches: dict[str, int] = {}
    output_z: dict[str, int] = {}
    for name, node_id, expected in zip(
        OUTPUT_NAMES, output_ids, EXPECTED_OUTPUTS, strict=True
    ):
        state = states[node_id]
        if not isinstance(state, State):
            raise RuntimeError(f"packed public output {name}")
        observed = int(state.bits) & int(state.driven) & ALL
        output_mismatches[name] = (observed ^ int(expected)).bit_count()
        output_z[name] = ((~int(state.driven)) & ALL).bit_count()

    conflict_union = 0
    for state in states.values():
        conflict_union |= int(state.conflict)

    paid_rails: list[dict[str, Any]] = []
    for node_id in sorted(nodes):
        node = nodes[node_id]
        if int(node["cost"]) == 0:
            continue
        role_rows = direct_roles(node_id, nodes, users, output_by_id)
        paid_rails.append(
            {
                "id": node_id,
                "name": alias(node),
                "op": node["op"],
                "cost": int(node["cost"]),
                "arrival": int(node["arrival"]),
                "latest_arrival_for_D6": latest[node_id],
                "slack": (
                    None
                    if latest[node_id] is None
                    else int(latest[node_id]) - int(node["arrival"])
                ),
                "fanout_edges": sum(edge_users[node_id].values()),
                "unique_consumers": sorted(users[node_id]),
                "direct_roles": role_rows,
                "downstream_outputs": sorted(reach[node_id]),
                "crosses_sum_and_carry": (
                    "C8" in reach[node_id]
                    and any(name.startswith("S") for name in reach[node_id])
                ),
                "directly_feeds_bus": any(
                    str(row["kind"]).startswith("bus") for row in role_rows
                ),
            }
        )

    owner_rows: list[dict[str, Any]] = []
    for node_id in sorted(nodes):
        node = nodes[node_id]
        if node["op"] != "BUS":
            continue
        args = list(map(int, node["args"]))
        drivers: list[dict[str, Any]] = []
        conflict_rows = 0
        for offset in range(0, len(args), 2):
            enable_id, data_id = args[offset : offset + 2]
            enable = states[enable_id]
            data = states[data_id]
            active = int(enable.bits) & ALL
            active_one = active & int(data.bits) & ALL
            active_zero = active & (~int(data.bits) & ALL)
            drivers.append(
                {
                    "enable": enable_id,
                    "enable_name": alias(nodes[enable_id]),
                    "enable_arrival": int(nodes[enable_id]["arrival"]),
                    "data": data_id,
                    "data_name": alias(nodes[data_id]),
                    "data_arrival": int(nodes[data_id]["arrival"]),
                    "active_rows": active.bit_count(),
                    "active_one_rows": active_one.bit_count(),
                    "active_zero_rows": active_zero.bit_count(),
                }
            )
        overlaps: list[dict[str, Any]] = []
        for left in range(len(drivers)):
            for right in range(left + 1, len(drivers)):
                left_enable = states[int(drivers[left]["enable"])]
                right_enable = states[int(drivers[right]["enable"])]
                left_data = states[int(drivers[left]["data"])]
                right_data = states[int(drivers[right]["data"])]
                overlap = int(left_enable.bits) & int(right_enable.bits) & ALL
                disagreement = overlap & (
                    int(left_data.bits) ^ int(right_data.bits)
                )
                conflict_rows |= disagreement
                overlaps.append(
                    {
                        "drivers": [left, right],
                        "active_overlap_rows": overlap.bit_count(),
                        "data_disagreement_rows": disagreement.bit_count(),
                    }
                )
        owner = states[node_id]
        owner_rows.append(
            {
                "id": node_id,
                "name": alias(node),
                "resolved_network": node["resolved_network"],
                "gate": int(node["cost"]),
                "arrival": int(node["arrival"]),
                "fanout_edges": sum(edge_users[node_id].values()),
                "unique_consumers": sorted(users[node_id]),
                "downstream_outputs": sorted(reach[node_id]),
                "drivers": drivers,
                "overlaps": overlaps,
                "z_rows": ((~int(owner.driven)) & ALL).bit_count(),
                "active_zero_rows": (
                    int(owner.driven) & (~int(owner.bits) & ALL)
                ).bit_count(),
                "active_one_rows": (int(owner.driven) & int(owner.bits)).bit_count(),
                "conflict_rows": conflict_rows.bit_count(),
            }
        )

    paid_ids = [row["id"] for row in paid_rails]
    physical_equal: list[list[int]] = []
    normalized_equal: list[list[int]] = []
    normalized_complement: list[list[int]] = []
    for index, left_id in enumerate(paid_ids):
        left = states[left_id]
        left_value = int(left.bits) & int(left.driven) & ALL
        for right_id in paid_ids[index + 1 :]:
            right = states[right_id]
            right_value = int(right.bits) & int(right.driven) & ALL
            if state_signature(left, ALL) == state_signature(right, ALL):
                physical_equal.append([left_id, right_id])
            if left_value == right_value:
                normalized_equal.append([left_id, right_id])
            if left_value == ((~right_value) & ALL):
                normalized_complement.append([left_id, right_id])

    paid_ledger = load(PAID_LEDGER)
    c6_audit = load(C6_AUDIT)
    global_atlas = load(GLOBAL_ATLAS)
    near_cuts = load(NEAR_CUTS)
    switch_covers = load(SWITCH_COVERS)
    low_partial = load(LOW_PARTIAL)

    switch_best = {
        row["output"]: (
            None
            if not row.get("best_candidates")
            else {
                "gate": int(row["best_candidates"][0]["gate"]),
                "delay": int(row["best_candidates"][0]["delay"]),
                "gate_delta": int(row["best_candidates"][0]["gate_delta"]),
            }
        )
        for row in switch_covers["outputs"]
    }

    candidate_boundaries = [
        {
            "priority": 1,
            "name": "U6部分进位与S6/S7/C8完整高尾",
            "current_gate": 15,
            "target_gate": 14,
            "best_closed_gate": int(
                c6_audit["ledger"]["u6_fixed_downstream_lower_bound"][
                    "total_lower_bound"
                ]
            ),
            "arrival": 6,
            "status": "one_gate_gap",
            "decisive_fact": (
                "D45/G345 deletion saves two gates; shared G5 absorption costs "
                "one, and S6 has no <=2-gate D6 closure in the recorded widened basis."
            ),
            "next_architectural_move": (
                "Change the bit6/7 paid-state encoding or final S7/C8 owner so one "
                "new phase replaces A6/Z7 or one M/N/Kprime rail; do not materialize C6."
            ),
        },
        {
            "priority": 2,
            "name": "C2的G1-driver拆分与S1/S2/T2消费者ABI",
            "current_gate": 6,
            "target_gate": 5,
            "best_closed_gate": 6,
            "arrival": 6,
            "status": "one_gate_gap_after_full_consumers",
            "decisive_fact": (
                "B=V1*C1 owner costs four and H12=G1|G2 costs one, but retaining "
                "the S1/S2/T2 ABI requires one more complete-C2 phase; bounded final-Z "
                "covers do not remove that payment."
            ),
            "next_architectural_move": (
                "Cancel the scalar C2 ABI across S1/S2/S3/B23 as one block; isolated "
                "owner compression is already closed at equal cost."
            ),
        },
        {
            "priority": 3,
            "name": "B23/C4与S2/S3联合状态块",
            "current_gate": 18,
            "target_gate": 17,
            "best_closed_gate": 18,
            "arrival": 6,
            "status": "one_gate_gap",
            "decisive_fact": (
                "B23 must remain at D3 for C6; a D4 C4 owner cannot replace that "
                "external consumer.  Existing equal-cost near cuts have no strict union hit."
            ),
            "next_architectural_move": (
                "Expose a new D3 lower-carry descriptor that simultaneously serves C6 "
                "and one S2/S3 phase, rather than replacing only BUS31."
            ),
        },
        {
            "priority": 4,
            "name": "当前S5/S7最终Switch owner直接重画",
            "current_gate": 10,
            "target_gate": 9,
            "best_closed_gate": 10,
            "arrival": 6,
            "status": "closed_for_recorded_paid_endpoints",
            "decisive_fact": (
                "The only zero-delta final positive covers reproduce the current S5 "
                "and S7 owners.  Word Switch cost is lane-linear, so a shared enable "
                "does not itself reduce gates."
            ),
            "next_architectural_move": (
                "Only revisit after an upstream state recode exposes a genuinely shared "
                "data phase; swapping existing enable/data endpoints cannot save a gate."
            ),
        },
    ]

    artifacts = [
        SOURCE,
        CORE_PATH,
        PAID_LEDGER,
        C6_AUDIT,
        GLOBAL_ATLAS,
        NEAR_CUTS,
        SWITCH_COVERS,
        LOW_PARTIAL,
    ]
    payload = {
        "schema": "tc-byte-adder-human85-global-paid-owner-audit-v1",
        "status": "pass",
        "method": (
            "deterministic accepted-DAG replay, complete paid-rail fanout, complete "
            "BUS-driver physical states, and bounded-certificate aggregation; no SAT, "
            "BDD, ABC, random search, game launch, or live-save access"
        ),
        "source": {
            "path": str(SOURCE),
            "sha256": file_sha(SOURCE),
            "structural_sha256": document["metrics"]["structural_sha256"],
        },
        "baseline": {
            **document["metrics"],
            "paid_instance_count": len(paid_rails),
            "paid_gate_sum": sum(int(row["cost"]) for row in paid_rails),
            "output_mismatch_rows": output_mismatches,
            "output_z_rows": output_z,
            "global_conflict_rows": conflict_union.bit_count(),
        },
        "paid_rails": paid_rails,
        "cross_role_paid_rails": [
            row
            for row in paid_rails
            if row["crosses_sum_and_carry"] or row["directly_feeds_bus"]
        ],
        "bus_owners": owner_rows,
        "paid_signature_relations": {
            "physical_equal_pairs": physical_equal,
            "normalized_value_equal_pairs": normalized_equal,
            "normalized_value_complement_pairs": normalized_complement,
            "warning": (
                "Normalized equality discards Z/owner identity and is not by itself a "
                "wireable replacement."
            ),
        },
        "candidate_boundaries": candidate_boundaries,
        "bounded_evidence": {
            "paid_ledger_cut_count": len(paid_ledger["ranked_atomic_cuts"]),
            "c6_two_gate_s6_hit_count": len(c6_audit["two_gate_s6_hits"]),
            "global_real_byproduct_strict_hit_count": len(
                global_atlas["strict_local_improvement_hits"]
            ),
            "near_cut_strict_union_hit_count": len(
                near_cuts["strict_improvement_pairs"]
            ),
            "switch_positive_cover_best": switch_best,
            "low_partial_s1_ordinary": {
                "four_gate": low_partial["ordinary_s1"]["four"]["status"],
                "five_gate": low_partial["ordinary_s1"]["five"]["status"],
                "compressed_truth_rows": low_partial["ordinary_s1"]["four"][
                    "compressed_truth_rows"
                ],
            },
            "claim_boundary": (
                "These are exact only for their recorded paid endpoints and bounded "
                "topologies.  They are not a global 84/6 impossibility proof."
            ),
        },
        "result": {
            "complete_84_6_candidate": False,
            "best_complete_score": [85, 6, 510],
            "highest_priority_unclosed_boundary": candidate_boundaries[0]["name"],
            "formal_save_modified": False,
            "game_started": False,
        },
        "artifact_hashes": [
            {"path": str(path), "sha256": file_sha(path)} for path in artifacts
        ],
        "self_checks": {
            "baseline_is_85_6": (
                int(document["metrics"]["gate"]),
                int(document["metrics"]["delay"]),
            )
            == (85, 6),
            "paid_gate_sum_is_85": sum(
                int(row["cost"]) for row in paid_rails
            )
            == 85,
            "paid_instance_count_is_63": len(paid_rails) == 63,
            "zero_output_mismatch": not any(output_mismatches.values()),
            "zero_global_conflict": conflict_union == 0,
            "all_owner_conflicts_zero": all(
                int(row["conflict_rows"]) == 0 for row in owner_rows
            ),
            "six_complete_bus_owners": len(owner_rows) == 6,
            "c6_bounded_two_gate_s6_is_empty": not c6_audit[
                "two_gate_s6_hits"
            ],
            "recorded_global_strict_hits_empty": not global_atlas[
                "strict_local_improvement_hits"
            ],
            "recorded_near_cut_strict_unions_empty": not near_cuts[
                "strict_improvement_pairs"
            ],
        },
    }
    if not all(payload["self_checks"].values()):
        raise RuntimeError(f"self-check failed: {payload['self_checks']}")

    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.write_text(encoded, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "sha256": sha256(encoded.encode("utf-8")).hexdigest(),
                "paid_instances": len(paid_rails),
                "paid_gate": sum(int(row["cost"]) for row in paid_rails),
                "bus_owners": len(owner_rows),
                "owner_conflicts": sum(
                    int(row["conflict_rows"]) for row in owner_rows
                ),
                "result": payload["result"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
