"""Build the 84/7 Byte Adder by replacing bit 0 with a 10-gate joint macro."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_PATH = (
    ROOT
    / ".research"
    / "byte_adder_prefix_frontier_agent"
    / "build_hybrid_phasefold_85_d7.py"
)
MACRO_CERT = HERE / "full1z-s4-c2-g10-n8.json"
OUTPUT_PATH = HERE / "byte-adder-hybrid-phasefold-g84-d7.json"


def load_base():
    spec = importlib.util.spec_from_file_location("byte_adder_hybrid84_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_base()
core = base.core
support = base.support


def bit0_joint_10(factory):
    """Physical 10-gate S0/C1 macro, independently exact-synthesized.

    Carry false may be Z; every ordinary consumer reads Z as logic zero.
    The two Switch drivers belong to one complete resolved BUS.
    """

    a = factory.inputs["a0"]
    b = factory.inputs["b0"]
    cin = factory.inputs["cin"]
    v = factory.gate("OR", b, cin)
    g = factory.gate("AND", b, cin)
    carry = factory.bus(((a, v), (g, g)))
    zero_case = factory.gate("NOR", a, v)
    not_all_three = factory.gate("NAND", a, g)
    exactly_two = factory.gate("AND", carry, not_all_three)
    sum0 = factory.gate("NOR", zero_case, exactly_two)
    return sum0, carry


def build() -> dict[str, object]:
    factory = core.Factory()
    gp_leaves = core.gp_leaves(factory)
    s0, c1 = bit0_joint_10(factory)
    v1, v2 = (support.v_leaf(factory, bit) for bit in (1, 2))

    c2 = core.gray_gp(factory, c1, gp_leaves[1], "ordinary")
    av12 = support.av_combine_switch(
        factory,
        (gp_leaves[1].g, v1),
        (gp_leaves[2].g, v2),
    )
    c3 = support.av_gray_switch(factory, c1, av12)
    c4 = core.gray_gp(factory, c3, gp_leaves[3], "ordinary")
    av34 = base.q_phase_av2(factory, 3, gp_leaves)
    c5 = support.av_gray_switch(factory, c3, av34)
    c6 = core.gray_gp(factory, c5, gp_leaves[5], "switch")
    gp56 = core.combine_gp(factory, gp_leaves[5], gp_leaves[6], "ordinary")
    c7 = core.gray_gp(factory, c5, gp56, "switch")
    c8 = core.gray_gp(factory, c7, gp_leaves[7], "ordinary")

    carries = (None, c1, c2, c3, c4, c5, c6, c7, c8)
    sums = [s0]
    sums.extend(
        core.sum_from_gp(factory, gp_leaves[bit].p, carries[bit])[0]
        for bit in range(1, 8)
    )
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
    buses = [node for node in live if factory.nodes[node].op == "BUS"]
    macro = json.loads(MACRO_CERT.read_text(encoding="utf-8"))
    return {
        "schema": "byte-adder-hybrid-q-phase-bit0-joint-dag-v1",
        "status": "sat",
        "family": "85/7 Q-phase schedule plus exact 10-gate S0/C1 macro",
        "source": str(BASE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "bit0_joint_macro": {
            "certificate": str(MACRO_CERT.relative_to(ROOT)).replace("\\", "/"),
            "certificate_sha256": hashlib.sha256(MACRO_CERT.read_bytes()).hexdigest(),
            "gate": 10,
            "sum_arrival": factory.nodes[s0].arrival,
            "carry_arrival": factory.nodes[c1].arrival,
            "allowed_z_zero": macro["verification"]["allowed_z_zero_count"],
            "formula": [
                "v=b0 OR cin",
                "g=b0 AND cin",
                "C1=BUS(Switch(a0,v), Switch(g,g))",
                "z=NOR(a0,v)",
                "n=NAND(a0,g)",
                "t=C1 AND n",
                "S0=NOR(z,t)",
            ],
        },
        "metrics": metrics,
        "semantic": semantic,
        "physical": {
            "bus_nodes": len(buses),
            "bus_node_ids": buses,
            "partial_driver_reuse_possible": False,
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
    OUTPUT_PATH.write_text(encoded, encoding="utf-8")
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
