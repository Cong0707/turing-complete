"""Build the 85/6 Byte Adder by jointly recoding bits 4 and 5.

This is a fixed architecture rewrite over the reviewed human 86/6 DAG.  It
does not search for Boolean formulas.  The old N/V/not-P state for bits 4:5,
the C6 owner, and the S4/S5 closures are replaced atomically by a G/Q/P state
and a shared ``T4 = P4 & C4`` phase:

    C5 = G4 | T4
    S4 = P4 XOR C4
    C6 = G5 | P5*C5
    S5 = NAND(P5,C6) & (G4 | P5 | T4)

The last equation is emitted as a two-driver common-data BUS.  It changes the
joint region from 24 to 23 gates while preserving the six-delay boundary.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "byte-adder-human86-s7-owner-merge-full.json"
OUTPUT = HERE / "byte-adder-human85-s45-c6-recode-full.json"

sys.path.insert(0, str(HERE))

from build_human86_s7_merge_factory import (  # noqa: E402
    ALL_ROWS,
    _load_materializer,
    build as build_human86,
)


def build() -> dict[str, Any]:
    materializer = _load_materializer()
    source = build_human86()
    if (source["metrics"]["gate"], source["metrics"]["delay"]) != (86, 6):
        raise RuntimeError("the human86 source no longer has the expected score")

    nodes = [dict(node) for node in source["factory_dag"]["nodes"]]
    by_id = {int(node["id"]): node for node in nodes}
    if source["metrics"]["structural_sha256"] != (
        "4058b453d2f50f4495392f2bc725d310fb710a234731950c24e9bc637e12ff85"
    ):
        raise RuntimeError("the reviewed human86 DAG structure changed")

    # Fixed boundary assertions.  These make an accidental patch against a
    # different numbering or architecture fail before any candidate is made.
    expected = {
        31: ("BUS", [26, 30, 25, 30]),  # R23 = V3*C3 reason rail
        44: ("OR", [34, 33]),           # G6|G7, consumed by the old tail
        48: ("AND", [12, 4]),           # G3
        57: ("OR", [48, 31]),           # C4
        58: ("OR", [45, 33]),           # not P6
        64: ("OR", [63, 39]),           # C8 phase
        80: ("OR", [47, 63]),           # merged S7 enable
    }
    for node_id, (op, args) in expected.items():
        node = by_id[node_id]
        if node["op"] != op or [int(value) for value in node["args"]] != args:
            raise RuntimeError(f"unexpected boundary node {node_id}: {node}")

    next_id = max(by_id) + 1

    def add(
        op: str,
        args: list[int],
        *,
        cost: int = 1,
        step_delay: int = 1,
        may_z: bool = False,
        label: str,
    ) -> int:
        nonlocal next_id
        node_id = next_id
        next_id += 1
        arrival = (
            0
            if not args
            else max(int(by_id[arg]["arrival"]) for arg in args) + step_delay
        )
        node: dict[str, Any] = {
            "id": node_id,
            "op": op,
            "args": args,
            "cost": cost,
            "step_delay": step_delay,
            "arrival": arrival,
            "may_z": may_z,
            "label": label,
        }
        if op == "BUS":
            owner = f"bus_{node_id}"
            node["resolved_network"] = owner
            node["drivers"] = [
                {"enable": args[index], "data": args[index + 1], "owner": owner}
                for index in range(0, len(args), 2)
            ]
        nodes.append(node)
        by_id[node_id] = node
        return node_id

    # Inputs in the normalized human86 DAG are a0..a7=1..8,
    # b0..b7=9..16, cin=17.
    g4 = add("AND", [5, 13], label="human85.G4")
    q4 = add("NOR", [5, 13], label="human85.Q4")
    p4 = add("NOR", [g4, q4], label="human85.P4")
    g5 = add("AND", [6, 14], label="human85.G5")
    q5 = add("NOR", [6, 14], label="human85.Q5")
    p5 = add("NOR", [g5, q5], label="human85.P5")

    h1 = add("OR", [g4, g5], label="human85.G45")
    h = add("OR", [h1, 48], label="human85.G345")
    v45 = add("NOR", [q4, q5], label="human85.V45")
    d45 = add("OR", [g5, v45], label="human85.C6_data")
    c6 = add(
        "BUS",
        [31, d45, h, d45],
        cost=4,
        may_z=True,
        label="human85.C6",
    )

    t4 = add("AND", [p4, 57], label="human85.T4")
    r4 = add("NOR", [p4, 57], label="human85.R4")
    s4 = add("NOR", [t4, r4], label="human85.S4")

    d5 = add("NAND", [p5, c6], label="human85.D5")
    e5 = add("OR", [g4, p5], label="human85.E5")
    s5 = add(
        "BUS",
        [e5, d5, t4, d5],
        cost=4,
        may_z=True,
        label="human85.S5",
    )

    # Rebuild the unchanged high tail after the new C6 node so the Factory DAG
    # remains topologically ordered.  The old nodes 71..81 become unreachable.
    s6_or = add("OR", [c6, 58], label="human85.S6_or")
    s6_nand = add("NAND", [58, c6], label="human85.S6_nand")
    s6 = add("NAND", [s6_or, s6_nand], label="human85.S6")
    c8_zero_reason = add("NOR", [c6, 44], label="human85.C8_zero_reason")
    c8 = add("NOR", [c8_zero_reason, 64], label="human85.C8")
    s7 = add(
        "BUS",
        [80, s6_or, c8_zero_reason, 46],
        cost=4,
        may_z=True,
        label="human85.S7",
    )

    outputs = [52, 53, 54, 77, s4, s5, s6, s7, c8]

    # Prune the removed region and densely renumber the live topological DAG.
    live: set[int] = set()
    stack = list(outputs)
    while stack:
        node_id = stack.pop()
        if node_id in live:
            continue
        live.add(node_id)
        stack.extend(int(value) for value in by_id[node_id]["args"])
    retained = [node for node in nodes if int(node["id"]) in live]
    remap = {int(node["id"]): index + 1 for index, node in enumerate(retained)}
    normalized: list[dict[str, Any]] = []
    for node in retained:
        copied = dict(node)
        copied["id"] = remap[int(node["id"])]
        copied["args"] = [remap[int(value)] for value in node["args"]]
        if copied["op"] == "BUS":
            owner = f"bus_{copied['id']}"
            copied["resolved_network"] = owner
            copied["drivers"] = [
                {
                    "enable": copied["args"][index],
                    "data": copied["args"][index + 1],
                    "owner": owner,
                }
                for index in range(0, len(copied["args"]), 2)
            ]
        normalized.append(copied)
    outputs = [remap[node_id] for node_id in outputs]
    by_id = {int(node["id"]): node for node in normalized}

    logical = materializer.logical_states(tuple(normalized))
    observed = [
        int(logical[node_id]["bits"]) & int(logical[node_id]["driven"]) & ALL_ROWS
        for node_id in outputs
    ]
    variables = tuple(materializer._variable(index) for index in range(17))
    carry = variables[16]
    expected_sum: list[int] = []
    for left, right in zip(variables[:8], variables[8:16], strict=True):
        propagate = left ^ right
        expected_sum.append(propagate ^ carry)
        carry = (left & right) | (propagate & carry)
    expected_outputs = [*expected_sum, carry]
    mismatch_masks = [
        left ^ right for left, right in zip(observed, expected_outputs, strict=True)
    ]
    mismatch_union = 0
    for mask in mismatch_masks:
        mismatch_union |= mask
    conflict = 0
    for state in logical.values():
        conflict |= int(state["conflict"])

    output_arrivals = [int(by_id[node_id]["arrival"]) for node_id in outputs]
    gate = sum(int(node["cost"]) for node in normalized)
    delay = max(output_arrivals)
    structural_hash = materializer._structural_sha256(by_id, tuple(outputs))
    z_counts = [
        ((~int(logical[node_id]["driven"])) & ALL_ROWS).bit_count()
        for node_id in outputs
    ]

    factory_dag: dict[str, Any] = {
        "outputs": outputs,
        "nodes": normalized,
        "live_node_count": len(normalized),
    }
    factory_dag["sha256"] = hashlib.sha256(
        json.dumps(
            factory_dag,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()

    payload = {
        "schema": "byte-adder-human85-s45-c6-recode-v1",
        "status": "sat",
        "source": {
            "path": str(SOURCE),
            "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        },
        "rewrite": {
            "removed_region_gate": 24,
            "replacement_region_gate": 23,
            "shared_phase": "T4=P4&C4 feeds both S4 and S5",
            "description": "joint G/Q/P recode of bits4:5, C6, S4 and S5",
        },
        "metrics": {
            "gate": gate,
            "delay": delay,
            "energy": gate * delay,
            "output_arrivals": output_arrivals,
            "reachable_nodes": len(normalized),
            "structural_sha256": structural_hash,
        },
        "semantic": {
            "truth_table_rows": 131072,
            "mismatch_count_by_output": [mask.bit_count() for mask in mismatch_masks],
            "mismatch_union_count": mismatch_union.bit_count(),
            "conflict_assignment_count": conflict.bit_count(),
            "z_assignment_count_by_output": z_counts,
            "output_vector_sha256": hashlib.sha256(
                b"".join(value.to_bytes(131072 // 8, "little") for value in observed)
            ).hexdigest(),
            "sequence_domain": None,
        },
        "factory_dag": factory_dag,
    }
    if (gate, delay) != (85, 6):
        raise RuntimeError(f"unexpected score: {gate}/{delay}")
    if mismatch_union or conflict:
        raise RuntimeError(
            "human85 verification failed: "
            f"mismatch={mismatch_union.bit_count()} conflict={conflict.bit_count()}"
        )
    return payload


def main() -> int:
    payload = build()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.write_text(encoded, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "sha256": hashlib.sha256(encoded.encode()).hexdigest(),
                "metrics": payload["metrics"],
                "semantic": payload["semantic"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
