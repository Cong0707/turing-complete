"""Build a structurally new 85/6 Byte Adder over the verified human85 DAG.

The rewrite is deliberately fixed and reviewable:

* S3 consumes the already-paid C4 positive phase instead of materializing nC3.
* The C6 generate tree is reassociated as (G3 | G4) | G5.

No circuit search is performed here.  The complete 131072-row domain,
arrival, BUS conflict state and output vector are recomputed before writing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "byte-adder-human85-s45-c6-recode-full.json"
OUTPUT = HERE / "byte-adder-human85-s3-positive-phase-full.json"

sys.path.insert(0, str(HERE))

from build_human85_s45_c6_recode import (  # noqa: E402
    ALL_ROWS,
    _load_materializer,
    build as build_human85,
)


def build() -> dict[str, Any]:
    materializer = _load_materializer()
    source = build_human85()
    if (source["metrics"]["gate"], source["metrics"]["delay"]) != (85, 6):
        raise RuntimeError("the verified human85 source is no longer 85/6")

    nodes = [dict(node) for node in source["factory_dag"]["nodes"]]
    by_id = {int(node["id"]): node for node in nodes}

    expected = {
        25: ("AND", [11, 3]),       # G2
        34: ("AND", [26, 27]),      # T2 = C2 & P2
        44: ("AND", [12, 4]),       # G3
        48: ("NOR", [29, 44]),      # P3
        49: ("OR", [44, 31]),       # C4
        51: ("NOR", [34, 25]),      # old nC3
        54: ("NAND", [48, 51]),     # old S3 phase
        55: ("OR", [51, 48]),       # old S3 phase
        56: ("NAND", [55, 54]),     # old S3
        58: ("AND", [5, 13]),       # G4
        61: ("AND", [6, 14]),       # G5
        64: ("OR", [58, 61]),       # old G4 | G5
        65: ("OR", [64, 44]),       # old G3 | G4 | G5
    }
    for node_id, (op, args) in expected.items():
        node = by_id[node_id]
        observed = (str(node["op"]), [int(value) for value in node["args"]])
        if observed != (op, args):
            raise RuntimeError(f"unexpected human85 node {node_id}: {observed!r}")

    def rewrite(node_id: int, op: str, args: list[int], label: str) -> None:
        node = by_id[node_id]
        node["op"] = op
        node["args"] = args
        node["cost"] = 1
        node["step_delay"] = 1
        node["may_z"] = False
        node["label"] = label
        node.pop("resolved_network", None)
        node.pop("drivers", None)

    # P3 XOR C3, with C3 = G2 | T2 and C4 = G3 | P3*C3:
    #   D3 = NAND(P3,C4) = NAND(P3,C3)
    #   O3 = P3 | G2 | T2 = P3 | C3
    #   S3 = D3 & O3
    rewrite(51, "NAND", [48, 49], "human85.alt.D3")
    rewrite(54, "OR", [25, 48], "human85.alt.E3")
    rewrite(55, "OR", [54, 34], "human85.alt.O3")
    rewrite(56, "AND", [51, 55], "human85.alt.S3")

    # Preserve H = G3 | G4 | G5 but expose K34 = G3 | G4 as the paid rail.
    rewrite(64, "OR", [44, 58], "human85.alt.K34")
    rewrite(65, "OR", [64, 61], "human85.alt.G345")

    # Recompute every arrival in topological order, including unchanged users.
    for node in nodes:
        args = [int(value) for value in node["args"]]
        node["arrival"] = (
            0
            if not args
            else max(int(by_id[value]["arrival"]) for value in args)
            + int(node["step_delay"])
        )

    outputs = [int(value) for value in source["factory_dag"]["outputs"]]
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
    for mask in mismatch_masks:
        mismatch_union |= mask
    conflict = 0
    for state in logical.values():
        conflict |= int(state["conflict"])

    output_arrivals = [int(by_id[node_id]["arrival"]) for node_id in outputs]
    gate = sum(int(node["cost"]) for node in nodes)
    delay = max(output_arrivals)
    structural_hash = materializer._structural_sha256(by_id, tuple(outputs))
    z_counts = [
        ((~int(logical[node_id]["driven"])) & ALL_ROWS).bit_count()
        for node_id in outputs
    ]

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
        "schema": "byte-adder-human85-s3-positive-phase-v1",
        "status": "sat",
        "source": {
            "path": str(SOURCE),
            "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        },
        "rewrite": {
            "removed": ["nC3", "old S3 NAND/OR/NAND phase", "G4|G5 root"],
            "replacement": [
                "D3=NAND(P3,C4)",
                "E3=G2|P3",
                "O3=E3|T2",
                "S3=D3&O3",
                "K34=G3|G4",
                "G345=K34|G5",
            ],
            "gate_delta": 0,
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
                b"".join(value.to_bytes(131072 // 8, "little") for value in observed_outputs)
            ).hexdigest(),
            "sequence_domain": None,
        },
        "factory_dag": factory_dag,
    }
    if (gate, delay) != (85, 6):
        raise RuntimeError(f"unexpected score: {gate}/{delay}")
    if mismatch_union or conflict:
        raise RuntimeError(
            "positive-phase rewrite failed: "
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
