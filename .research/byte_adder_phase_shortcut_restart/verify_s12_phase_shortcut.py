"""Replay the S1/S2 D5 phase shortcut over all 131072 Byte Adder inputs."""

from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORE_PATH = ROOT / ".research/byte_adder_interval_dp_agent/interval_dp.py"
BIT0_WITNESS = (
    ROOT
    / ".research/byte_adder_phase_shortcut_forward/fast_negative_bit0_g11_n9_s2_x0.json"
)
EXACT_WITNESS = HERE / "s12_g7_d5_exact.json"
OUTPUT = HERE / "s012_phase_shortcut_d5_fulltruth.json"


def load_core():
    spec = importlib.util.spec_from_file_location("s12_phase_shortcut_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(CORE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = load_core()


def replay_physical_witness(factory, path: Path, sources: dict[str, int]):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "sat":
        raise RuntimeError(f"witness is not SAT: {path}")
    source_nodes = {}
    for index, name in enumerate(payload["free_sources"]):
        if name == "0":
            source_nodes[index] = factory.const0
        elif name == "1":
            source_nodes[index] = factory.const1
        else:
            source_nodes[index] = sources[name]
    switches = {}
    bus_cache = {}

    def resolve(source_ids):
        key = tuple(sorted(source_ids))
        if key in bus_cache:
            return bus_cache[key]
        if len(key) == 1 and key[0] in source_nodes:
            node = source_nodes[key[0]]
        else:
            if not key or any(source not in switches for source in key):
                raise RuntimeError(f"unresolved physical bus: {key}")
            node = factory.bus(switches[source] for source in key)
        bus_cache[key] = node
        return node

    for item in payload["network"]:
        source = int(item["source"])
        left = resolve(item["left_bus"])
        if item["kind"] == "SWITCH":
            switches[source] = (left, resolve(item["right_bus"]))
            continue
        if item["kind"] == "NOT":
            node = factory.gate("NOT", left)
        else:
            node = factory.gate(item["kind"], left, resolve(item["right_bus"]))
        source_nodes[source] = node
    return tuple(resolve(bus) for bus in payload["output_buses"])


def negative_av_combine(factory, low, high):
    low_a, low_v = low
    high_a, high_v = high
    return (
        factory.gate("OR", low_a, high_a),
        factory.bus(((high_a, high_v), (low_v, high_v))),
    )


def negative_av_gray(factory, ncarry, transfer):
    any_kill, valency = transfer
    return factory.bus(((any_kill, valency), (ncarry, valency)))


def build() -> dict[str, object]:
    factory = core.Factory()
    s0, nc1 = replay_physical_witness(
        factory,
        BIT0_WITNESS,
        {
            "a": factory.inputs["a0"],
            "b": factory.inputs["b0"],
            "Cin": factory.inputs["cin"],
        },
    )
    leaves = {}
    for bit in (1, 2):
        a = factory.inputs[f"a{bit}"]
        b = factory.inputs[f"b{bit}"]
        g = factory.gate("AND", a, b)
        q = factory.gate("NOR", a, b)
        p = factory.gate("NOR", g, q)
        n = factory.gate("NAND", a, b)
        leaves[bit] = (g, q, p, n)
    _g1, q1, p1, n1 = leaves[1]
    _g2, q2, p2, n2 = leaves[2]
    av12 = negative_av_combine(factory, (q1, n1), (q2, n2))
    nc3 = negative_av_gray(factory, nc1, av12)

    phase0 = factory.gate("NOR", q1, p2)
    phase1 = factory.gate("AND", p2, nc3)
    phase2 = factory.gate("NAND", nc1, p1)
    phase3 = factory.gate("AND", phase0, phase2)
    phase4 = factory.gate("OR", nc1, p1)
    s1 = factory.gate("NAND", phase2, phase4)
    s2 = factory.gate("OR", phase1, phase3)

    outputs = (s0, s1, s2)
    _packed, semantic = factory.evaluate(outputs)
    metrics = factory.structural_metrics(outputs)
    if semantic["mismatch_union_count"]:
        raise RuntimeError(f"truth mismatch: {semantic}")
    if semantic["conflict_assignment_count"]:
        raise RuntimeError(f"BUS conflict: {semantic}")
    if any(semantic["z_assignment_count_by_output"]):
        raise RuntimeError(f"undriven output: {semantic}")
    if metrics["output_arrivals"] != [4, 4, 5]:
        raise RuntimeError(f"unexpected arrivals: {metrics}")
    exact = json.loads(EXACT_WITNESS.read_text(encoding="utf-8"))
    verification = exact["verification"]
    if any(
        verification[field]
        for field in (
            "mismatch_count",
            "bus_conflict_count",
            "undriven_output_count",
            "physical_net_partition_violation_count",
            "depth_upper_bound_violation_count",
            "output_deadline_violation_count",
        )
    ):
        raise RuntimeError(f"exact witness verification failed: {verification}")
    return {
        "schema": "fast-negative-s12-phase-shortcut-fulltruth-v1",
        "status": "verified",
        "formula_gate_cost": 7,
        "formula": [
            "t0=NOR(Q1,P2)",
            "t1=AND(P2,nC3)",
            "t2=NAND(nC1,P1)",
            "t3=AND(t0,t2)",
            "t4=OR(nC1,P1)",
            "S1=NAND(t2,t4)",
            "S2=OR(t1,t3)",
        ],
        "metrics_for_s0_s1_s2_slice": metrics,
        "semantic": semantic,
        "physical": {
            "exact_witness": EXACT_WITNESS.name,
            "exact_witness_sha256": sha256(EXACT_WITNESS.read_bytes()).hexdigest(),
            "bit0_witness": BIT0_WITNESS.name,
            "bit0_witness_sha256": sha256(BIT0_WITNESS.read_bytes()).hexdigest(),
            "complete_switch_driver_sets_replayed": True,
            "partial_switch_pin_reuse": False,
        },
        "test_domain": {
            "rows": core.ASSIGNMENTS,
            "complete_u8_u8_u1": True,
        },
    }


def main() -> int:
    payload = build()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "sha256": sha256(encoded.encode()).hexdigest(),
                "metrics": payload["metrics_for_s0_s1_s2_slice"],
                "semantic": payload["semantic"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
