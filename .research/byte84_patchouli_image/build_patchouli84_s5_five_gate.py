"""Rebuild the Patchouli 84/6 Byte Adder from the public circuit image.

The verified human85 DAG is retained everywhere except the S5 cone.  The
public image fixes the replacement topology and its inputs:

    U45 = B23 OR K34
    H5  = NOR(Q4, P5)
    T5  = U45 AND H5
    J5  = NOR(Q5, C6)
    S5  = T5 OR J5

This replaces the six-gate D5/E5/two-Switch owner with five ordinary gates.
The script recomputes the complete 131072-row truth table, BUS conflicts,
arrivals, gate count, and output digest before writing the derived DAG.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ARCH = HERE.parent / "byte_adder_architecture_restart"
SOURCE = ARCH / "byte-adder-human85-s3-positive-phase-full.json"
OUTPUT = HERE / "byte-adder-patchouli84-s5-five-gate-full.json"

sys.path.insert(0, str(ARCH))

from build_human85_s3_positive_phase import (  # noqa: E402
    ALL_ROWS,
    _load_materializer,
    build as build_human85,
)


def _ordinary(
    node: dict[str, Any], op: str, args: list[int], label: str
) -> None:
    node.update(
        {
            "op": op,
            "args": args,
            "cost": 1,
            "step_delay": 1,
            "may_z": False,
            "label": label,
        }
    )
    node.pop("resolved_network", None)
    node.pop("drivers", None)


def _new_node(node_id: int, op: str, args: list[int], label: str) -> dict[str, Any]:
    return {
        "id": node_id,
        "op": op,
        "args": args,
        "cost": 1,
        "step_delay": 1,
        "arrival": 0,
        "may_z": False,
        "label": label,
    }


def build() -> dict[str, Any]:
    materializer = _load_materializer()
    source = build_human85()
    if (source["metrics"]["gate"], source["metrics"]["delay"]) != (85, 6):
        raise RuntimeError("the verified source is no longer 85/6")

    nodes = [dict(node) for node in source["factory_dag"]["nodes"]]
    by_id = {int(node["id"]): node for node in nodes}
    expected = {
        31: ("BUS", [26, 30, 25, 30]),       # B23
        59: ("NOR", [5, 13]),                # Q4
        62: ("NOR", [6, 14]),                # Q5
        63: ("NOR", [61, 62]),               # P5
        64: ("OR", [44, 58]),                # K34
        68: ("BUS", [31, 67, 65, 67]),       # C6
        72: ("NAND", [63, 68]),              # old D5
        73: ("OR", [58, 63]),                # old E5
        74: ("BUS", [73, 72, 69, 72]),       # old S5
    }
    for node_id, wanted in expected.items():
        node = by_id[node_id]
        observed = (str(node["op"]), [int(value) for value in node["args"]])
        if observed != wanted:
            raise RuntimeError(
                f"unexpected source node {node_id}: {observed!r} != {wanted!r}"
            )

    # Screenshot-fixed five-gate S5 cone.
    _ordinary(by_id[72], "OR", [31, 64], "patchouli84.U45")
    _ordinary(by_id[73], "NOR", [59, 63], "patchouli84.H5")
    _ordinary(by_id[74], "AND", [72, 73], "patchouli84.T5")
    nodes.append(_new_node(81, "NOR", [62, 68], "patchouli84.J5"))
    nodes.append(_new_node(82, "OR", [74, 81], "patchouli84.S5"))
    by_id = {int(node["id"]): node for node in nodes}

    outputs = [int(value) for value in source["factory_dag"]["outputs"]]
    if outputs[5] != 74:
        raise RuntimeError(f"unexpected S5 output id: {outputs[5]}")
    outputs[5] = 82

    for node in nodes:
        args = [int(value) for value in node["args"]]
        node["arrival"] = (
            0
            if not args
            else max(int(by_id[value]["arrival"]) for value in args)
            + int(node["step_delay"])
        )

    logical = materializer.logical_states(tuple(nodes))
    observed_outputs = [
        int(logical[node_id]["bits"])
        & int(logical[node_id]["driven"])
        & ALL_ROWS
        for node_id in outputs
    ]
    variables = tuple(materializer._variable(index) for index in range(17))
    carry = variables[16]
    expected_outputs: list[int] = []
    for left, right in zip(variables[:8], variables[8:16], strict=True):
        propagate = left ^ right
        expected_outputs.append(propagate ^ carry)
        carry = (left & right) | (propagate & carry)
    expected_outputs.append(carry)

    mismatch_masks = [
        left ^ right
        for left, right in zip(observed_outputs, expected_outputs, strict=True)
    ]
    mismatch_union = 0
    for mismatch in mismatch_masks:
        mismatch_union |= mismatch
    conflict = 0
    for state in logical.values():
        conflict |= int(state["conflict"])

    gate = sum(int(node["cost"]) for node in nodes)
    output_arrivals = [int(by_id[node_id]["arrival"]) for node_id in outputs]
    delay = max(output_arrivals)
    z_counts = [
        ((~int(logical[node_id]["driven"])) & ALL_ROWS).bit_count()
        for node_id in outputs
    ]
    structural_hash = materializer._structural_sha256(by_id, tuple(outputs))
    factory_dag: dict[str, Any] = {
        "outputs": outputs,
        "nodes": nodes,
        "live_node_count": len(nodes),
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
        "schema": "byte-adder-patchouli84-s5-five-gate-v1",
        "status": "sat",
        "source": {
            "path": str(SOURCE),
            "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "score": source["metrics"],
        },
        "image_evidence": {
            "path": str(
                Path(
                    r"C:\Users\cong\AppData\Local\Temp"
                    r"\codex-clipboard-0f43b28d-452e-431e-93a1-4cdb313c3fca.jpg"
                )
            ),
            "topology": "OR(AND(OR(B23,K34),NOR(Q4,P5)),NOR(Q5,C6))",
        },
        "rewrite": {
            "removed": ["D5=NAND(P5,C6)", "E5=OR(G4,P5)", "S5 two-Switch owner"],
            "replacement": [
                "U45=OR(B23,K34)",
                "H5=NOR(Q4,P5)",
                "T5=AND(U45,H5)",
                "J5=NOR(Q5,C6)",
                "S5=OR(T5,J5)",
            ],
            "old_gate": 6,
            "new_gate": 5,
            "gate_delta": -1,
        },
        "metrics": {
            "gate": gate,
            "delay": delay,
            "energy": gate * delay,
            "output_arrivals": output_arrivals,
            "reachable_nodes": len(nodes),
            "structural_sha256": structural_hash,
        },
        "semantic": {
            "truth_table_rows": 131072,
            "mismatch_count_by_output": [mask.bit_count() for mask in mismatch_masks],
            "mismatch_union_count": mismatch_union.bit_count(),
            "conflict_assignment_count": conflict.bit_count(),
            "z_assignment_count_by_output": z_counts,
            "output_vector_sha256": hashlib.sha256(
                b"".join(
                    value.to_bytes(131072 // 8, "little")
                    for value in observed_outputs
                )
            ).hexdigest(),
            "sequence_domain": None,
        },
        "factory_dag": factory_dag,
    }
    if (gate, delay) != (84, 6):
        raise RuntimeError(f"unexpected score: {gate}/{delay}")
    if output_arrivals != [4, 5, 4, 6, 6, 6, 6, 6, 6]:
        raise RuntimeError(f"unexpected output arrivals: {output_arrivals}")
    if mismatch_union or conflict:
        raise RuntimeError(
            "Patchouli S5 rewrite failed: "
            f"mismatch={mismatch_union.bit_count()} conflict={conflict.bit_count()}"
        )
    if int(logical[82]["driven"]) != ALL_ROWS:
        raise RuntimeError("ordinary-gate S5 must actively drive every row")
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
