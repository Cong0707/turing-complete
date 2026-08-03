"""Build the 86/7 hybrid GP/A/V Byte Adder with a 17-gate joint block."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORE_PATH = ROOT / ".research/byte_adder_interval_dp_agent/interval_dp.py"
MACRO_CERTIFICATE = (
    ROOT / ".research/byte_adder_switch_z_agent/sumav2_freegp_physical_total17_g11_d5_n7.json"
)
OUTPUT_PATH = HERE / "byte-adder-hybrid-gp-av-g86-d7.json"


def load_core():
    spec = importlib.util.spec_from_file_location("byte_adder_hybrid86_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = load_core()


def v_leaf(factory, bit: int) -> int:
    return factory.gate(
        "OR", factory.inputs[f"a{bit}"], factory.inputs[f"b{bit}"]
    )


def av_combine_switch(factory, low: tuple[int, int], high: tuple[int, int]):
    low_a, low_v = low
    high_a, high_v = high
    any_generate = factory.gate("OR", high_a, low_a)
    v = factory.bus(((high_a, high_v), (low_v, high_v)))
    return any_generate, v


def av_gray_switch(factory, carry: int, transfer: tuple[int, int]) -> int:
    any_generate, v = transfer
    return factory.bus(((any_generate, v), (carry, v)))


def sum_av_17(factory, lo: int, cin: int, gp_leaves):
    """Certified formula from sumav2_freegp_physical_total17_g11_d5_n7."""

    low = gp_leaves[lo]
    high = gp_leaves[lo + 1]
    a0 = factory.inputs[f"a{lo}"]
    b0 = factory.inputs[f"b{lo}"]
    a1 = factory.inputs[f"a{lo + 1}"]
    b1 = factory.inputs[f"b{lo + 1}"]
    # Re-materializing q is canonical and shares the already-paid GP leaf node.
    q0 = factory.gate("NOR", a0, b0)
    q1 = factory.gate("NOR", a1, b1)
    n0 = factory.gate("NOR", cin, low.g)
    c1 = factory.gate("NOR", q0, n0)
    s1 = factory.gate("XOR", high.p, c1)
    s0 = factory.gate("XOR", cin, low.p)
    any_generate = factory.gate("OR", low.g, high.g)
    no_kill = factory.gate("NOR", q0, q1)
    v = factory.gate("OR", high.g, no_kill)
    return s0, s1, any_generate, v


def serialize_live_dag(factory, outputs: tuple[int, ...]) -> dict[str, object]:
    live = sorted(factory.reachable(outputs))
    rows = []
    for index in live:
        node = factory.nodes[index]
        item: dict[str, object] = {
            "id": index,
            "op": node.op,
            "args": list(node.args),
            "cost": node.cost,
            "step_delay": node.step_delay,
            "arrival": node.arrival,
            "may_z": node.may_z,
            "label": node.label,
        }
        if node.op == "BUS":
            item["resolved_network"] = f"bus_node_{index}"
            item["drivers"] = [
                {
                    "enable": node.args[offset],
                    "data": node.args[offset + 1],
                    "owner": f"bus_node_{index}",
                }
                for offset in range(0, len(node.args), 2)
            ]
        rows.append(item)
    payload: dict[str, object] = {
        "outputs": list(outputs),
        "nodes": rows,
        "live_node_count": len(live),
    }
    payload["sha256"] = hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def build() -> dict[str, object]:
    factory = core.Factory()
    gp_leaves = core.gp_leaves(factory)
    v0, v1, v2 = (v_leaf(factory, bit) for bit in range(3))
    c0 = factory.inputs["cin"]

    c1 = av_gray_switch(factory, c0, (gp_leaves[0].g, v0))
    c2 = core.gray_gp(factory, c1, gp_leaves[1], "ordinary")
    av12 = av_combine_switch(
        factory,
        (gp_leaves[1].g, v1),
        (gp_leaves[2].g, v2),
    )
    c3 = av_gray_switch(factory, c1, av12)

    s3, s4, a34, v34 = sum_av_17(factory, 3, c3, gp_leaves)
    c5 = av_gray_switch(factory, c3, (a34, v34))
    c6 = core.gray_gp(factory, c5, gp_leaves[5], "switch")
    gp56 = core.combine_gp(factory, gp_leaves[5], gp_leaves[6], "ordinary")
    c7 = core.gray_gp(factory, c5, gp56, "switch")
    c8 = core.gray_gp(factory, c7, gp_leaves[7], "ordinary")

    carries = (c0, c1, c2, c3, None, c5, c6, c7, c8)
    sums = []
    for bit in range(8):
        if bit == 3:
            sums.append(s3)
        elif bit == 4:
            sums.append(s4)
        else:
            carry = carries[bit]
            if carry is None:
                raise RuntimeError(f"missing C{bit}")
            sums.append(core.sum_from_gp(factory, gp_leaves[bit].p, carry)[0])
    outputs = tuple([*sums, c8])
    metrics = factory.structural_metrics(outputs)
    _packed, semantic = factory.evaluate(outputs)
    if metrics["gate"] != 86 or metrics["delay"] != 7:
        raise RuntimeError(f"unexpected metrics: {metrics}")
    if semantic["mismatch_union_count"]:
        raise RuntimeError(f"truth mismatch: {semantic}")
    if semantic["conflict_assignment_count"]:
        raise RuntimeError(f"BUS conflict: {semantic}")
    if any(semantic["z_assignment_count_by_output"]):
        raise RuntimeError(f"undriven output: {semantic}")

    live = factory.reachable(outputs)
    bus_nodes = [index for index in live if factory.nodes[index].op == "BUS"]
    certificate_bytes = MACRO_CERTIFICATE.read_bytes()
    return {
        "schema": "byte-adder-hybrid-gp-av-sum-macro-dag-v1",
        "status": "sat",
        "family": "hybrid GP/A/V schedule with 17-gate Sum+A/V macro at bits 3:4",
        "source_schedule": {
            "baseline": ".research/byte_adder_depth4_global_agent/hybrid_gp_av_d7_g87.json",
            "carry_edges": [
                "C1<-C0:av/switch[0:0]",
                "C2<-C1:gp/ordinary[1:1]",
                "C3<-C1:av/switch[1:2]",
                "S3,S4,A34,V34<-17/5 joint macro(C3)",
                "C5<-C3:av/switch[A34,V34]",
                "C6<-C5:gp/switch[5:5]",
                "C7<-C5:gp/switch[5:6]",
                "C8<-C7:gp/ordinary[7:7]",
            ],
        },
        "joint_macro": {
            "certificate": str(MACRO_CERTIFICATE.relative_to(ROOT)).replace("\\", "/"),
            "certificate_sha256": hashlib.sha256(certificate_bytes).hexdigest(),
            "gate_including_gp_leaves": 17,
            "cin_arrival": factory.nodes[c3].arrival,
            "output_arrivals": [
                factory.nodes[s3].arrival,
                factory.nodes[s4].arrival,
                factory.nodes[a34].arrival,
                factory.nodes[v34].arrival,
            ],
            "interface_output_order": ["S0", "S1", "A", "V"],
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
        "factory_dag": serialize_live_dag(factory, outputs),
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
