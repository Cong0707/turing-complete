"""Build and certify hand-derived physical Sum+U/V two-bit macros."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import exact_adder_block_sat as exact
from exact_sum_transfer_sat import sum_transfer_targets


COST = {name: exact.G.COST[index] for index, name in enumerate(exact.G.KINDS)}


class Builder:
    def __init__(self, bits: int) -> None:
        self.bits = bits
        self.inputs = 2 * bits + 1
        self.source_count = self.inputs + 2
        self.nodes: list[dict[str, object]] = []
        self.depths = [0] * self.source_count

    @property
    def const0(self) -> int:
        return self.inputs

    @property
    def const1(self) -> int:
        return self.inputs + 1

    def gate(self, kind: str, left: int, right: int | None = None) -> int:
        if right is None:
            right_bus: list[int] = []
            input_depth = self.depths[left]
        else:
            right_bus = [right]
            input_depth = max(self.depths[left], self.depths[right])
        delay = exact.G.DELAY[exact.G.KINDS.index(kind)]
        source = self.source_count + len(self.nodes)
        depth = input_depth + delay
        self.nodes.append(
            {
                "slot": len(self.nodes),
                "source": source,
                "kind": kind,
                "left_bus": [left],
                "right_bus": right_bus,
                "cost": COST[kind],
                "depth_upper_bound": depth,
            }
        )
        self.depths.append(depth)
        return source

    def finish(self, name: str, outputs: list[list[int]]) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema": "exact-sum-carry-transfer-switch-dag-v1",
            "status": "sat",
            "family": name,
            "bits": self.bits,
            "inputs": self.inputs,
            "target_truth_tables_hex": [
                f"{target:0{(1 << self.inputs) // 4}x}"
                for target in sum_transfer_targets(self.bits)[1]
            ],
            "allow_z_false": False,
            "allow_z_false_outputs": [False] * self.bits + [True, True],
            "physical_nets": True,
            "actual_gate": sum(int(node["cost"]) for node in self.nodes),
            "network": self.nodes,
            "output_buses": outputs,
            "semantics": {
                "switch": "enable=0 -> Z; enable=1 -> data",
                "ordinary_gate_reads_z_as_zero": True,
                "multi_driver_conflict_forbidden": True,
                "sum_outputs_must_be_driven": True,
                "false_transfer_rails_may_be_z": True,
                "physical_net_partition": "overlap implies identical driver set",
            },
        }
        original_targets = exact.adder_targets
        exact.adder_targets = sum_transfer_targets
        try:
            payload["verification"] = exact.verify_payload(payload)
        finally:
            exact.adder_targets = original_targets
        verification = payload["verification"]
        if any(
            verification[key]
            for key in (
                "mismatch_count",
                "bus_conflict_count",
                "undriven_output_count",
                "physical_net_partition_violation_count",
            )
        ):
            raise RuntimeError(payload)
        payload["actual_delay"] = verification["replayed_max_component_depth"]
        return payload


def build_17_d6() -> dict[str, object]:
    b = Builder(2)
    a0, a1, b0, b1, cin = range(5)
    g0 = b.gate("AND", a0, b0)
    q0 = b.gate("NOR", a0, b0)
    p0 = b.gate("NOR", q0, g0)
    t0 = b.gate("AND", p0, cin)
    n0 = b.gate("NOR", p0, cin)
    s0 = b.gate("NOR", n0, t0)
    c1 = b.gate("OR", g0, t0)
    g1 = b.gate("AND", a1, b1)
    q1 = b.gate("NOR", a1, b1)
    p1 = b.gate("NOR", q1, g1)
    t1 = b.gate("AND", p1, c1)
    n1 = b.gate("NOR", p1, c1)
    s1 = b.gate("NOR", n1, t1)
    p1g0 = b.gate("AND", p1, g0)
    u = b.gate("OR", g1, p1g0)
    p1p0 = b.gate("AND", p1, p0)
    v = b.gate("OR", u, p1p0)
    return b.finish("sum-transfer-2bit-ordinary", [[s0], [s1], [u], [v]])


def build_19_d5() -> dict[str, object]:
    b = Builder(2)
    a0, a1, b0, b1, cin = range(5)
    o0 = b.gate("OR", a0, b0)
    ng0 = b.gate("NAND", a0, b0)
    p0 = b.gate("AND", o0, ng0)
    g0 = b.gate("NOT", ng0)
    h0 = b.gate("AND", o0, cin)
    c1 = b.gate("OR", g0, h0)
    s0 = b.gate("XOR", p0, cin)
    g1 = b.gate("AND", a1, b1)
    q1 = b.gate("NOR", a1, b1)
    p1 = b.gate("NOR", q1, g1)
    t1 = b.gate("AND", p1, c1)
    n1 = b.gate("NOR", p1, c1)
    s1 = b.gate("NOR", n1, t1)
    p1g0 = b.gate("AND", p1, g0)
    u = b.gate("OR", g1, p1g0)
    p1p0 = b.gate("AND", p1, p0)
    v = b.gate("OR", u, p1p0)
    return b.finish("sum-transfer-2bit-fast-low", [[s0], [s1], [u], [v]])


def build_28_d4() -> dict[str, object]:
    b = Builder(2)
    a0, a1, b0, b1, cin = range(5)
    g0 = b.gate("AND", a0, b0)
    v0 = b.gate("OR", a0, b0)
    g1 = b.gate("AND", a1, b1)
    v1 = b.gate("OR", a1, b1)
    p0 = b.gate("XOR", a0, b0)
    p1 = b.gate("XOR", a1, b1)

    ug = b.gate("SWITCH", g1, b.const1)
    ul = b.gate("SWITCH", g0, v1)
    vg = b.gate("SWITCH", g1, b.const1)  # Physical duplicate for V bus.
    vl = b.gate("SWITCH", v0, v1)
    c1g = b.gate("SWITCH", g0, v0)
    c1c = b.gate("SWITCH", cin, v0)
    c1_bus = [c1g, c1c]
    s0 = b.gate("XOR", p0, cin)

    # Materialize the C1 bus once through OR(x,0); ordinary gates read all-Z as 0.
    # This normalization adds one gate and one delay, so instead the final XOR
    # directly resolves the identical physical C1 driver set at its right pin.
    source = b.source_count + len(b.nodes)
    input_depth = max(b.depths[item] for item in c1_bus)
    b.nodes.append(
        {
            "slot": len(b.nodes),
            "source": source,
            "kind": "XOR",
            "left_bus": [p1],
            "right_bus": c1_bus,
            "cost": COST["XOR"],
            "depth_upper_bound": input_depth + 2,
        }
    )
    b.depths.append(input_depth + 2)
    s1 = source
    return b.finish("sum-transfer-2bit-switch-prefix", [[s0], [s1], [ug, ul], [vg, vl]])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    candidates = [build_17_d6(), build_19_d5(), build_28_d4()]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    for payload in candidates:
        name = f"{payload['family']}-g{payload['actual_gate']}-d{payload['actual_delay']}.json"
        encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
        path = args.output_dir / name
        path.write_bytes(encoded)
        summary.append(
            {
                "path": str(path),
                "gate": payload["actual_gate"],
                "delay": payload["actual_delay"],
                "sha256": sha256(encoded).hexdigest(),
                "verification": payload["verification"],
            }
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
