"""Build the 84/7 hybrid adder with Q-phase transfer and bit0 S/C1 macro."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
SUPPORT_PATH = HERE / "build_hybrid_phasefold_85_d7.py"
ROOT = HERE.parents[1]
BIT0_CERTIFICATE = ROOT / ".research/byte_adder_root/full1z-s4-c2-g10-n8.json"
OUTPUT_PATH = HERE / "byte-adder-hybrid-phasefold-g84-d7.json"


def load_support():
    spec = importlib.util.spec_from_file_location("byte_adder_hybrid84_support", SUPPORT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SUPPORT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


support = load_support()
base = support.support
core = support.core


def bit0_sum_carry_10(factory, cin: int) -> tuple[int, int]:
    a = factory.inputs["a0"]
    b = factory.inputs["b0"]
    v = factory.gate("OR", b, cin)
    g = factory.gate("AND", b, cin)
    c1 = factory.bus(((a, v), (g, g)))
    z = factory.gate("NOR", a, v)
    n = factory.gate("NAND", a, g)
    t = factory.gate("AND", c1, n)
    s0 = factory.gate("NOR", z, t)
    return s0, c1


def build() -> dict[str, object]:
    factory = core.Factory()
    gp_leaves = core.gp_leaves(factory)
    c0 = factory.inputs["cin"]
    s0, c1 = bit0_sum_carry_10(factory, c0)

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
    c6 = core.gray_gp(factory, c5, gp_leaves[5], "switch")
    gp56 = core.combine_gp(factory, gp_leaves[5], gp_leaves[6], "ordinary")
    c7 = core.gray_gp(factory, c5, gp56, "switch")
    c8 = core.gray_gp(factory, c7, gp_leaves[7], "ordinary")
    carries = (c0, c1, c2, c3, c4, c5, c6, c7, c8)
    sums = [s0] + [
        core.sum_from_gp(factory, gp_leaves[bit].p, carries[bit])[0]
        for bit in range(1, 8)
    ]
    outputs = tuple([*sums, c8])
    metrics = factory.structural_metrics(outputs)
    _packed, semantic = factory.evaluate(outputs)
    if metrics["gate"] != 84 or metrics["delay"] != 7:
        raise RuntimeError(f"unexpected metrics: {metrics}")
    if semantic["mismatch_union_count"]:
        raise RuntimeError(f"truth mismatch: {semantic}")
    if semantic["conflict_assignment_count"]:
        raise RuntimeError(f"BUS conflict: {semantic}")
    if any(semantic["z_assignment_count_by_output"]):
        raise RuntimeError(f"undriven output: {semantic}")

    live = factory.reachable(outputs)
    bus_nodes = [index for index in live if factory.nodes[index].op == "BUS"]
    cert_bytes = BIT0_CERTIFICATE.read_bytes()
    return {
        "schema": "byte-adder-hybrid-q-phase-bit0-macro-dag-v1",
        "status": "sat",
        "family": "hybrid GP/A/V Q-phase schedule plus 10-gate bit0 S/C1 macro",
        "source_schedule": {
            "baseline": ".research/byte_adder_prefix_frontier_agent/byte-adder-hybrid-phasefold-g85-d7.json",
            "carry_edges": [
                "S0,C1<-10-gate joint bit0 macro",
                "C2<-C1:gp/ordinary[1:1]",
                "C3<-C1:av/switch[1:2]",
                "C4<-C3:gp/ordinary[3:3]",
                "C5<-C3:av/switch[q-phase 3:4]",
                "C6<-C5:gp/switch[5:5]",
                "C7<-C5:gp/switch[5:6]",
                "C8<-C7:gp/ordinary[7:7]",
            ],
        },
        "bit0_joint_macro": {
            "certificate": str(BIT0_CERTIFICATE.relative_to(ROOT)).replace("\\", "/"),
            "certificate_sha256": hashlib.sha256(cert_bytes).hexdigest(),
            "gate": 10,
            "output_arrivals": [
                factory.nodes[s0].arrival,
                factory.nodes[c1].arrival,
            ],
            "interface_output_order": ["S0", "C1"],
        },
        "q_phase_transfer": {
            "formula": ["A=g3 OR g4", "V=g4 OR NOR(q3,q4)"],
            "gate": 3,
            "output_arrivals": [
                factory.nodes[av34[0]].arrival,
                factory.nodes[av34[1]].arrival,
            ],
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
