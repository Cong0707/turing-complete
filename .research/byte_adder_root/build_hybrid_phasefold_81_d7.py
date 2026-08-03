"""Build an 81/7 Byte Adder by sharing the S5 phase term with S6.

The baseline is the independently replayed 84/7 hybrid DAG.  Bits 5:6 used
23 gates there (including their six G/Q/P leaves).  This builder replaces that
region with a 20-gate joint block:

    C5@4 -> S5@6, S6@7, C7@5

No native adder component is used.  False C7 may be represented by Z inside
the DAG; all nine primary outputs are explicitly checked to be driven.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASELINE_BUILDER = (
    ROOT
    / ".research/byte_adder_prefix_frontier_agent/build_hybrid_phasefold_84_d7.py"
)
OUTPUT_PATH = HERE / "byte-adder-hybrid-phasefold-g81-d7.json"


def load_baseline():
    spec = importlib.util.spec_from_file_location(
        "byte_adder_hybrid82_support", BASELINE_BUILDER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BASELINE_BUILDER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


baseline = load_baseline()
support = baseline.support
base = baseline.base
core = baseline.core


def bit56_joint(factory, c5: int, gp_leaves):
    """Return S5, S6 and C7 for the late-Cin two-bit region."""

    low = gp_leaves[5]
    high = gp_leaves[6]
    q5 = factory.gate("NOR", factory.inputs["a5"], factory.inputs["b5"])
    q6 = factory.gate("NOR", factory.inputs["a6"], factory.inputs["b6"])

    # S5 = P5 xor C5.  Use the exact three-gate phase form so the P5&C5
    # product is available to the adjacent S6 reconstruction at no extra cost.
    s5, t5 = core.sum_from_gp(factory, low.p, c5)

    # Direct two-bit carry at absolute arrival 5.  The two switch enables are
    # conflict-safe; when the Boolean carry is false the resolved BUS may be Z.
    both_propagate = factory.gate("AND", low.p, high.p)
    phase_data = factory.gate("NOR", q6, both_propagate)
    any_generate = factory.gate("OR", low.g, high.g)
    c7 = factory.bus(((both_propagate, c5), (any_generate, phase_data)))

    # Four-gate reconstruction found by exact local truth-table enumeration:
    # S6 = NAND(C7,P6) AND (T5 OR G5 OR P6).
    left = factory.gate("NAND", c7, high.p)
    right0 = factory.gate("OR", low.g, high.p)
    right1 = factory.gate("OR", t5, right0)
    s6 = factory.gate("AND", left, right1)
    return s5, s6, c7


def build() -> dict[str, object]:
    factory = core.Factory()
    gp_leaves = core.gp_leaves(factory)
    c0 = factory.inputs["cin"]
    s0, c1 = baseline.bit0_sum_carry_10(factory, c0)

    v1, v2 = (base.v_leaf(factory, bit) for bit in (1, 2))
    c2 = core.gray_gp(factory, c1, gp_leaves[1], "ordinary")
    av12 = base.av_combine_switch(
        factory,
        (gp_leaves[1].g, v1),
        (gp_leaves[2].g, v2),
    )
    c3 = base.av_gray_switch(factory, c1, av12)
    c4 = core.gray_gp(factory, c3, gp_leaves[3], "ordinary")
    av34 = support.q_phase_av2(factory, 3, gp_leaves)
    c5 = base.av_gray_switch(factory, c3, av34)

    s5, s6, c7 = bit56_joint(factory, c5, gp_leaves)
    c8 = core.gray_gp(factory, c7, gp_leaves[7], "ordinary")
    carries = (c0, c1, c2, c3, c4, c5, None, c7, c8)
    sums = [s0]
    for bit in range(1, 5):
        sums.append(core.sum_from_gp(factory, gp_leaves[bit].p, carries[bit])[0])
    sums.extend((s5, s6))
    sums.append(core.sum_from_gp(factory, gp_leaves[7].p, c7)[0])
    outputs = tuple([*sums, c8])

    metrics = factory.structural_metrics(outputs)
    _packed, semantic = factory.evaluate(outputs)
    if metrics["gate"] != 81 or metrics["delay"] != 7:
        raise RuntimeError(f"unexpected metrics: {metrics}")
    if semantic["mismatch_union_count"]:
        raise RuntimeError(f"truth mismatch: {semantic}")
    if semantic["conflict_assignment_count"]:
        raise RuntimeError(f"BUS conflict: {semantic}")
    if any(semantic["z_assignment_count_by_output"]):
        raise RuntimeError(f"undriven output: {semantic}")

    live = factory.reachable(outputs)
    bus_nodes = [index for index in live if factory.nodes[index].op == "BUS"]
    return {
        "schema": "byte-adder-hybrid-q-phase-s5s6-fold-dag-v1",
        "status": "sat",
        "family": "84/7 hybrid with exact late-Cin S5/S6/C7 phase fold",
        "source_schedule": {
            "baseline": str(
                BASELINE_BUILDER.relative_to(ROOT)
            ).replace("\\", "/"),
            "replacement": "bits5:6 23 gates -> 20 gates",
            "interface": "C5@4 -> S5@6,S6@7,C7@5",
        },
        "bit56_joint_macro": {
            "gate_including_gp_leaves": 20,
            "replaced_gate_including_gp_leaves": 23,
            "saved_gate": 3,
            "output_arrivals": [
                factory.nodes[s5].arrival,
                factory.nodes[s6].arrival,
                factory.nodes[c7].arrival,
            ],
            "formula": [
                "T5=AND(P5,C5)",
                "S5=NOR(NOR(P5,C5),T5)",
                "T=AND(P5,P6)",
                "D=NOR(Q6,T)",
                "A=OR(G5,G6)",
                "C7=BUS(SW(T,C5),SW(A,D))",
                "S6=AND(NAND(C7,P6),OR(T5,OR(G5,P6)))",
            ],
        },
        "metrics": metrics,
        "semantic": semantic,
        "physical": {
            "bus_nodes": len(bus_nodes),
            "bus_node_ids": bus_nodes,
            "partial_driver_reuse_possible": False,
            "reason": "each BUS node owns its complete driver set",
        },
        "test_domain": {
            "variables": core.VARIABLES,
            "rows": core.ASSIGNMENTS,
            "complete_u8_u8_u1": True,
        },
        "factory_dag": base.serialize_live_dag(factory, outputs),
    }


def main() -> int:
    payload = build()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT_PATH.write_bytes(encoded.encode("utf-8"))
    print(
        json.dumps(
            {
                "output": str(OUTPUT_PATH),
                "metrics": payload["metrics"],
                "semantic": payload["semantic"],
                "sha256": hashlib.sha256(encoded.encode()).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
