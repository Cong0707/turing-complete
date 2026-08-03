"""Build an 80/7 Byte Adder with a carry-aware bit-2 sum cell.

This is a forward Jackson/Ling-style phase fusion over the existing 81/7
hybrid.  Bit 2 already exposes the reduced state ``(G2, V2)`` for the fast
``C3`` A/V carry path, and both adjacent carries ``C2`` and ``C3`` are live.
Therefore ``P2`` does not need to be materialized solely for ``S2``:

    S2 = (V2 OR C2) AND NAND(C3, NAND(G2, C2))

The identity is exact on the three valid one-bit carry states:

* kill:      ``(G,V)=(0,0)`` -> ``S=C``;
* propagate: ``(G,V)=(0,1)`` -> ``S=~C``;
* generate:  ``(G,V)=(1,1)`` -> ``S=C``.

Compared with ``Q2 + P2 + three-gate XOR phase`` this consumes four ordinary
gates instead of five.  The slower ``S2@7`` remains inside the global D7
budget.  No native adder or mux component is used.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASELINE_BUILDER = HERE / "build_hybrid_phasefold_81_d7.py"
OUTPUT_PATH = HERE / "byte-adder-hybrid-phasefold-g80-d7.json"


def load_baseline():
    spec = importlib.util.spec_from_file_location(
        "byte_adder_hybrid80_support", BASELINE_BUILDER
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


def sum_from_gv_adjacent_carries(
    factory, generate: int, valency: int, carry_in: int, carry_out: int
) -> int:
    """Four-gate Sum from the reduced G/V state and adjacent carries."""

    active = factory.gate("OR", valency, carry_in)
    not_all_generate = factory.gate("NAND", generate, carry_in)
    selected_phase = factory.gate("NAND", carry_out, not_all_generate)
    return factory.gate("AND", active, selected_phase)


def build() -> dict[str, object]:
    factory = core.Factory()
    gp_leaves = core.gp_leaves(factory)
    c0 = factory.inputs["cin"]
    s0, c1 = baseline.baseline.bit0_sum_carry_10(factory, c0)

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

    s5, s6, c7 = baseline.bit56_joint(factory, c5, gp_leaves)
    c8 = core.gray_gp(factory, c7, gp_leaves[7], "ordinary")

    s1 = core.sum_from_gp(factory, gp_leaves[1].p, c1)[0]
    s2 = sum_from_gv_adjacent_carries(
        factory, gp_leaves[2].g, v2, c2, c3
    )
    s3 = core.sum_from_gp(factory, gp_leaves[3].p, c3)[0]
    s4 = core.sum_from_gp(factory, gp_leaves[4].p, c4)[0]
    s7 = core.sum_from_gp(factory, gp_leaves[7].p, c7)[0]
    outputs = (s0, s1, s2, s3, s4, s5, s6, s7, c8)

    metrics = factory.structural_metrics(outputs)
    _packed, semantic = factory.evaluate(outputs)
    if metrics["gate"] != 80 or metrics["delay"] != 7:
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
        "schema": "byte-adder-hybrid-gv-adjacent-carry-sum-dag-v1",
        "status": "sat",
        "family": "81/7 hybrid plus Jackson/Ling G/V adjacent-carry Sum fusion",
        "source_schedule": {
            "baseline": str(BASELINE_BUILDER.relative_to(ROOT)).replace("\\", "/"),
            "replacement": "bit2 Q/P/S phase 5 gates -> G/V/C2/C3 fused Sum 4 gates",
            "identity": "S2=(V2 OR C2) AND NAND(C3,NAND(G2,C2))",
        },
        "bit2_fused_sum": {
            "incremental_gate": 4,
            "replaced_incremental_gate": 5,
            "saved_gate": 1,
            "arrival": factory.nodes[s2].arrival,
            "inputs": {
                "G2": factory.nodes[gp_leaves[2].g].arrival,
                "V2": factory.nodes[v2].arrival,
                "C2": factory.nodes[c2].arrival,
                "C3": factory.nodes[c3].arrival,
            },
        },
        "metrics": metrics,
        "semantic": semantic,
        "physical": {
            "bus_nodes": len(bus_nodes),
            "bus_node_ids": bus_nodes,
            "partial_driver_reuse_possible": False,
            "reason": "each BUS node owns its complete independent driver set",
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
