"""Build the 85/7 hybrid adder using a two-bit Q-phase A/V transfer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
SUPPORT_PATH = HERE / "build_hybrid_gp_av_86_d7.py"
OUTPUT_PATH = HERE / "byte-adder-hybrid-phasefold-g85-d7.json"


def load_support():
    spec = importlib.util.spec_from_file_location("byte_adder_hybrid85_support", SUPPORT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SUPPORT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


support = load_support()
core = support.core


def q_phase_av2(factory, lo: int, gp_leaves):
    low = gp_leaves[lo]
    high = gp_leaves[lo + 1]
    a0 = factory.inputs[f"a{lo}"]
    b0 = factory.inputs[f"b{lo}"]
    a1 = factory.inputs[f"a{lo + 1}"]
    b1 = factory.inputs[f"b{lo + 1}"]
    q0 = factory.gate("NOR", a0, b0)
    q1 = factory.gate("NOR", a1, b1)
    any_generate = factory.gate("OR", low.g, high.g)
    no_kill = factory.gate("NOR", q0, q1)
    v = factory.gate("OR", high.g, no_kill)
    return any_generate, v


def build() -> dict[str, object]:
    factory = core.Factory()
    gp_leaves = core.gp_leaves(factory)
    v0, v1, v2 = (support.v_leaf(factory, bit) for bit in range(3))
    c0 = factory.inputs["cin"]

    c1 = support.av_gray_switch(factory, c0, (gp_leaves[0].g, v0))
    c2 = core.gray_gp(factory, c1, gp_leaves[1], "ordinary")
    av12 = support.av_combine_switch(
        factory,
        (gp_leaves[1].g, v1),
        (gp_leaves[2].g, v2),
    )
    c3 = support.av_gray_switch(factory, c1, av12)
    c4 = core.gray_gp(factory, c3, gp_leaves[3], "ordinary")
    av34 = q_phase_av2(factory, 3, gp_leaves)
    c5 = support.av_gray_switch(factory, c3, av34)
    c6 = core.gray_gp(factory, c5, gp_leaves[5], "switch")
    gp56 = core.combine_gp(factory, gp_leaves[5], gp_leaves[6], "ordinary")
    c7 = core.gray_gp(factory, c5, gp56, "switch")
    c8 = core.gray_gp(factory, c7, gp_leaves[7], "ordinary")
    carries = (c0, c1, c2, c3, c4, c5, c6, c7, c8)
    sums = [
        core.sum_from_gp(factory, gp_leaves[bit].p, carries[bit])[0]
        for bit in range(8)
    ]
    outputs = tuple([*sums, c8])
    metrics = factory.structural_metrics(outputs)
    _packed, semantic = factory.evaluate(outputs)
    if metrics["gate"] != 85 or metrics["delay"] != 7:
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
        "schema": "byte-adder-hybrid-q-phase-av-dag-v1",
        "status": "sat",
        "family": "hybrid GP/A/V schedule with Q-phase A/V transfer at bits 3:4",
        "source_schedule": {
            "baseline": ".research/byte_adder_depth4_global_agent/hybrid_gp_av_d7_g87.json",
            "carry_edges": [
                "C1<-C0:av/switch[0:0]",
                "C2<-C1:gp/ordinary[1:1]",
                "C3<-C1:av/switch[1:2]",
                "C4<-C3:gp/ordinary[3:3]",
                "C5<-C3:av/switch[q-phase 3:4]",
                "C6<-C5:gp/switch[5:5]",
                "C7<-C5:gp/switch[5:6]",
                "C8<-C7:gp/ordinary[7:7]",
            ],
        },
        "q_phase_transfer": {
            "formula": ["A=g3 OR g4", "V=g4 OR NOR(q3,q4)"],
            "gate": 3,
            "output_arrivals": [
                factory.nodes[av34[0]].arrival,
                factory.nodes[av34[1]].arrival,
            ],
            "replaced_gp_interval_gate": 5,
        },
        "metrics": metrics,
        "semantic": semantic,
        "physical": {
            "bus_nodes": len(bus_nodes),
            "bus_node_ids": bus_nodes,
            "partial_driver_reuse_possible": False,
            "reason": "each BUS node serializes a complete independently owned driver set",
        },
        "test_domain": {
            "variables": core.VARIABLES,
            "rows": core.ASSIGNMENTS,
            "complete_u8_u8_u1": True,
        },
        "factory_dag": support.serialize_live_dag(factory, outputs),
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
