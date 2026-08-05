"""Reconstruct and audit Patchouli's 84/6 Byte Adder S5 closure.

This is a fixed screenshot-derived rewrite over the authoritative verified
85/6 Factory DAG.  It does not search a general gate space.  The only changed
region is the old six-gate S5 owner:

    D5 = NAND(P5, C6)
    E5 = OR(G4, P5)
    S5 = BUS(SW(E5, D5), SW(T4, D5))

It is replaced by the five ordinary gates visible in the public 84/6 image:

    U45 = OR(B23, K34)
    H5  = NOR(Q4, P5)
    T5  = AND(U45, H5)
    J5  = NOR(Q5, C6)
    S5  = OR(T5, J5)
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = (
    ROOT
    / ".research/byte_adder_architecture_restart/"
    "byte-adder-human85-s3-positive-phase-full.json"
)
MATERIALIZER = (
    ROOT
    / ".research/byte_adder_builder_layout_agent/"
    "materialize_factory_dag.py"
)
OUTPUT = HERE / "patchouli-s5-84-audit-v1.json"

SOURCE_SHA256 = "b3dbe1d83ed28f32c929f4c840a6fa69a9d747e84895c0df9af794d7f704feee"
SOURCE_STRUCTURAL_SHA256 = (
    "5b3aa51e17c763d85617f28b7db20ac89635157251241498626f2fb148e928ca"
)


def _load_materializer() -> Any:
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("patchouli84_materializer", MATERIALIZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Factory DAG materializer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()


def _expected_outputs(materializer: Any) -> list[int]:
    variables = tuple(materializer._variable(index) for index in range(17))
    carry = variables[16]
    outputs: list[int] = []
    for left, right in zip(variables[:8], variables[8:16], strict=True):
        propagate = left ^ right
        outputs.append(propagate ^ carry)
        carry = (left & right) | (propagate & carry)
    outputs.append(carry)
    return outputs


def build() -> dict[str, Any]:
    source_bytes = SOURCE.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != SOURCE_SHA256:
        raise RuntimeError("authoritative 85/6 source file changed")
    source = json.loads(source_bytes)
    if source["metrics"]["structural_sha256"] != SOURCE_STRUCTURAL_SHA256:
        raise RuntimeError("authoritative 85/6 Factory DAG changed")

    source_nodes = [dict(node) for node in source["factory_dag"]["nodes"]]
    source_by_id = {int(node["id"]): node for node in source_nodes}
    expected_boundary = {
        31: ("BUS", [26, 30, 25, 30]),       # B23
        44: ("AND", [12, 4]),                # G3
        58: ("AND", [5, 13]),                # G4
        59: ("NOR", [5, 13]),                # Q4
        61: ("AND", [6, 14]),                # G5
        62: ("NOR", [6, 14]),                # Q5
        63: ("NOR", [61, 62]),               # P5
        64: ("OR", [44, 58]),                # K34
        65: ("OR", [64, 61]),                # G345
        66: ("NOR", [59, 62]),               # V45
        67: ("OR", [61, 66]),                # D45
        68: ("BUS", [31, 67, 65, 67]),       # C6
        69: ("AND", [60, 49]),               # T4
        70: ("NOR", [60, 49]),               # R4
        71: ("NOR", [69, 70]),               # S4
        72: ("NAND", [63, 68]),              # old D5
        73: ("OR", [58, 63]),                # old E5
        74: ("BUS", [73, 72, 69, 72]),       # old S5
    }
    for node_id, expected in expected_boundary.items():
        node = source_by_id[node_id]
        observed = (str(node["op"]), [int(value) for value in node["args"]])
        if observed != expected:
            raise RuntimeError(f"unexpected boundary node {node_id}: {observed!r}")

    # Retain the authoritative DAG except for the old S5 three-node owner.
    nodes = [node for node in source_nodes if int(node["id"]) not in {72, 73, 74}]
    by_id = {int(node["id"]): node for node in nodes}
    next_id = max(by_id) + 1

    def add(op: str, args: list[int], label: str) -> int:
        nonlocal next_id
        node_id = next_id
        next_id += 1
        arrival = max(int(by_id[arg]["arrival"]) for arg in args) + 1
        node = {
            "id": node_id,
            "op": op,
            "args": args,
            "cost": 1,
            "step_delay": 1,
            "arrival": arrival,
            "may_z": False,
            "label": label,
        }
        nodes.append(node)
        by_id[node_id] = node
        return node_id

    u45 = add("OR", [31, 64], "patchouli84.U45")
    h5 = add("NOR", [59, 63], "patchouli84.H5")
    t5 = add("AND", [u45, h5], "patchouli84.T5")
    j5 = add("NOR", [62, 68], "patchouli84.J5")
    s5 = add("OR", [t5, j5], "patchouli84.S5")

    outputs = [int(value) for value in source["factory_dag"]["outputs"]]
    outputs[5] = s5

    materializer = _load_materializer()
    logical = materializer.logical_states(tuple(nodes))
    all_rows = int(materializer.ALL)
    observed_outputs = [
        int(logical[node_id]["bits"])
        & int(logical[node_id]["driven"])
        & all_rows
        for node_id in outputs
    ]
    expected_outputs = _expected_outputs(materializer)
    mismatch_masks = [
        observed ^ expected
        for observed, expected in zip(
            observed_outputs, expected_outputs, strict=True
        )
    ]
    mismatch_union = 0
    conflict_union = 0
    for mismatch in mismatch_masks:
        mismatch_union |= mismatch
    for state in logical.values():
        conflict_union |= int(state["conflict"])

    gate = sum(int(node["cost"]) for node in nodes)
    output_arrivals = [int(by_id[node_id]["arrival"]) for node_id in outputs]
    delay = max(output_arrivals)
    z_counts = [
        ((~int(logical[node_id]["driven"])) & all_rows).bit_count()
        for node_id in outputs
    ]
    c6_state = logical[68]
    c6_bits = int(c6_state["bits"])
    c6_driven = int(c6_state["driven"])

    factory_dag: dict[str, Any] = {
        "outputs": outputs,
        "nodes": nodes,
        "live_node_count": len(nodes),
    }
    factory_dag["sha256"] = _canonical_sha256(factory_dag)
    structural_sha256 = materializer._structural_sha256(by_id, tuple(outputs))

    result = {
        "schema": "patchouli-byte-adder-s5-84-audit-v1",
        "status": "pass",
        "source": {
            "path": str(SOURCE),
            "sha256": SOURCE_SHA256,
            "structural_sha256": SOURCE_STRUCTURAL_SHA256,
        },
        "screenshot_reconstruction": {
            "unchanged": [
                "bits0:3 = 42 gate",
                "bits6:7 + C8 = 20 gate",
                "K34/G345/V45/D45/C6",
                "S4",
            ],
            "removed": [
                "D5=NAND(P5,C6)",
                "E5=OR(G4,P5)",
                "S5=BUS(SW(E5,D5),SW(T4,D5))",
            ],
            "replacement": [
                "U45=OR(B23,K34)",
                "H5=NOR(Q4,P5)",
                "T5=AND(U45,H5)",
                "J5=NOR(Q5,C6)",
                "S5=OR(T5,J5)",
            ],
            "identity": [
                "U45*H5 = C5*NOT(P5)",
                "NOR(Q5,C6) = P5*NOT(C5)",
                "S5 = P5 XOR C5",
            ],
        },
        "ledger": {
            "bits0_3": 42,
            "bits4_5_and_c6": 22,
            "bits6_7_and_c8": 20,
            "total_gate": gate,
            "delay": delay,
            "energy": gate * delay,
        },
        "arrival": {
            "U45": by_id[u45]["arrival"],
            "H5": by_id[h5]["arrival"],
            "T5": by_id[t5]["arrival"],
            "J5": by_id[j5]["arrival"],
            "S5": by_id[s5]["arrival"],
            "outputs": output_arrivals,
        },
        "semantic": {
            "truth_table_rows": 131072,
            "mismatch_count_by_output": [
                value.bit_count() for value in mismatch_masks
            ],
            "mismatch_union_count": mismatch_union.bit_count(),
            "conflict_assignment_count": conflict_union.bit_count(),
            "z_assignment_count_by_output": z_counts,
            "output_vector_sha256": hashlib.sha256(
                b"".join(
                    value.to_bytes(131072 // 8, "little")
                    for value in observed_outputs
                )
            ).hexdigest(),
        },
        "c6_three_state": {
            "active_one": (c6_bits & c6_driven & all_rows).bit_count(),
            "active_zero": ((~c6_bits) & c6_driven & all_rows).bit_count(),
            "z": ((~c6_driven) & all_rows).bit_count(),
            "conflict": int(c6_state["conflict"]).bit_count(),
            "J5_reads_z_as_zero": True,
        },
        "factory_dag": factory_dag,
        "metrics": {
            "gate": gate,
            "delay": delay,
            "energy": gate * delay,
            "reachable_nodes": len(nodes),
            "structural_sha256": structural_sha256,
        },
    }
    if (gate, delay) != (84, 6):
        raise RuntimeError(f"unexpected score: {gate}/{delay}")
    if mismatch_union or conflict_union:
        raise RuntimeError(
            "Patchouli 84/6 replay failed: "
            f"mismatch={mismatch_union.bit_count()} "
            f"conflict={conflict_union.bit_count()}"
        )
    if [by_id[value]["arrival"] for value in (u45, h5, t5, j5, s5)] != [
        4,
        3,
        5,
        5,
        6,
    ]:
        raise RuntimeError("screenshot S5 arrival contract changed")
    return result


def main() -> int:
    result = build()
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(encoded, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "sha256": hashlib.sha256(encoded.encode()).hexdigest(),
                "metrics": result["metrics"],
                "semantic": result["semantic"],
                "c6_three_state": result["c6_three_state"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
