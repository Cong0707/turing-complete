"""Independently replay the frozen g16 S7/C8 witness as a positive control.

The target four-output search fixes exactly
``NOT,NOR,OR,OR,SWITCH,SWITCH,SWITCH,SWITCH,SWITCH,SWITCH``.  The frozen
two-output witness already inhabits that precise 16-gate, D5 topology.  This
script reconstructs all 486 correlated rows and independently checks Boolean
semantics, high-Z BUS resolution, physical-net partitioning, liveness, cost,
and timing.  It calibrates the topology only; it is not an S5/S6 witness.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_WITNESS = HERE / "tail_s7c8_g16_fixed_kinds_d5.json"
WORKER = HERE / "physical_exact.py"
EXPECTED_SOURCE_SHA256 = (
    "bad7c9b909be8faf572c1577632b4f1f39143a92c2763ff7fee96ab2b911db29"
)
KINDS = ("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH")
COST = dict(zip(KINDS, (1, 1, 1, 1, 1, 3, 2), strict=True))
DELAY = dict(zip(KINDS, (1, 1, 1, 1, 1, 2, 1), strict=True))
COMMUTATIVE = {"AND", "OR", "NAND", "NOR", "XOR"}
FIXED_KINDS = ("NOT", "NOR", "OR", "OR", *("SWITCH" for _ in range(6)))


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _local_state(state: int) -> tuple[bool, bool, bool, bool]:
    if state not in range(3):
        raise ValueError(state)
    return state == 2, state == 0, state == 1, state != 2


def _prefix_values(
    local: dict[int, tuple[bool, bool, bool, bool]], nc3: bool
) -> dict[str, bool]:
    _g3, q3, p3, n3 = local[3]
    _g4, q4, p4, n4 = local[4]
    _g5, q5, p5, n5 = local[5]
    _g6, q6, p6, n6 = local[6]
    a34 = q3 or q4
    v34 = n4 and (q4 or n3)
    a56 = q5 or q6
    v56 = n6 and (q6 or n5)
    a36 = a34 or a56
    v36 = v56 and (a56 or v34)
    nc4 = q3 or (p3 and nc3)
    nc5 = q4 or (p4 and nc4)
    nc6 = q5 or (p5 and nc5)
    nc7 = q6 or (p6 and nc6)
    return {
        "A34n": a34,
        "V34n": v34,
        "A56n": a56,
        "V56n": v56,
        "A36n": a36,
        "V36n": v36,
        "nC4": nc4,
        "nC5": nc5,
        "nC6": nc6,
        "nC7": nc7,
    }


def regression_rows(
    free_sources: tuple[str, ...],
) -> Iterable[tuple[list[bool], tuple[bool, bool]]]:
    for nc3 in (False, True):
        for states in itertools.product(range(3), repeat=5):
            local = {
                bit: _local_state(state)
                for bit, state in zip(range(3, 8), states, strict=True)
            }
            prefix = _prefix_values(local, nc3)
            row: dict[str, bool] = {"nC3": nc3, "0": False, "1": True}
            for bit in range(3, 7):
                g, q, p, n = local[bit]
                row.update(
                    {f"G{bit}": g, f"Q{bit}": q, f"P{bit}": p, f"N{bit}": n}
                )
            g7, q7, p7, _n7 = local[7]
            row.update({"G7": g7, "Q7": q7, "P7": p7})
            row.update(
                {name: value for name, value in prefix.items() if name in free_sources}
            )
            nc7 = prefix["nC7"]
            nc8 = q7 or (p7 and nc7)
            yield [row[name] for name in free_sources], (p7 == nc7, not nc8)


def build_regression(source: dict[str, object]) -> dict[str, object]:
    return {
        "domain": "s34567c8_leaf",
        "rows": 486,
        "output_names": ["S7", "C8"],
        "target_search_outputs": ["S5", "S6", "S7", "C8"],
        "gate_bound": 16,
        "max_delay": 5,
        "components": 10,
        "ordinary": 4,
        "exact_switches": 6,
        "exact_xors": 0,
        "fixed_kinds": list(FIXED_KINDS),
        "free_sources": list(source["free_sources"]),
        "source_arrivals": dict(source["source_arrivals"]),
        "network": [dict(item) for item in source["network"]],
        "output_buses": [list(bus) for bus in source["output_buses"]],
        "physical_nets": True,
        "public_outputs_must_be_driven": True,
    }


def _resolve(
    values: list[bool], drivens: list[bool], bus: list[int]
) -> tuple[bool, bool, int]:
    active = {values[source] for source in bus if drivens[source]}
    if len(active) > 1:
        return False, True, 1
    if not active:
        return False, False, 0
    return next(iter(active)), True, 0


def verify(payload: dict[str, object]) -> dict[str, object]:
    free_sources = tuple(payload["free_sources"])
    source_count = len(free_sources)
    network = payload["network"]
    output_buses = payload["output_buses"]
    buses = [item["left_bus"] for item in network]
    buses += [item["right_bus"] for item in network]
    buses += output_buses

    topology_violations = 0
    canonical_order_violations = 0
    active_bus_non_switch_driver_violations = 0
    for slot, item in enumerate(network):
        topology_violations += item["slot"] != slot
        topology_violations += item["source"] != source_count + slot
        topology_violations += item["kind"] != FIXED_KINDS[slot]
        topology_violations += any(
            source >= source_count + slot
            for source in item["left_bus"] + item["right_bus"]
        )
        topology_violations += item["kind"] == "NOT" and bool(item["right_bus"])
        if item["kind"] in COMMUTATIVE:
            left_mask = sum(1 << source for source in item["left_bus"])
            right_mask = sum(1 << source for source in item["right_bus"])
            canonical_order_violations += left_mask >= right_mask
    for bus in buses:
        if len(bus) <= 1:
            continue
        for source in bus:
            if source < source_count:
                active_bus_non_switch_driver_violations += 1
            elif network[source - source_count]["kind"] != "SWITCH":
                active_bus_non_switch_driver_violations += 1

    physical_partition_violations = 0
    for index, left in enumerate(buses):
        for right in buses[index + 1 :]:
            overlap = set(left) & set(right)
            if (
                overlap
                and set(left) != set(right)
                and any(source >= source_count for source in overlap)
            ):
                physical_partition_violations += 1

    users = {source_count + slot: 0 for slot in range(len(network))}
    for item in network:
        for source in item["left_bus"] + item["right_bus"]:
            if source in users:
                users[source] += 1
    for bus in output_buses:
        for source in bus:
            if source in users:
                users[source] += 1
    dead_component_count = sum(count == 0 for count in users.values())

    arrivals = [int(payload["source_arrivals"][name]) for name in free_sources]
    depth_upper_bound_violations = 0
    actual_gate = 0
    for item in network:
        input_arrival = max(
            (arrivals[source] for source in item["left_bus"] + item["right_bus"]),
            default=0,
        )
        actual = input_arrival + DELAY[item["kind"]]
        arrivals.append(actual)
        actual_gate += COST[item["kind"]]
        depth_upper_bound_violations += actual > int(item["depth_upper_bound"])
    output_arrivals = [
        max((arrivals[source] for source in bus), default=0) for bus in output_buses
    ]
    output_deadline_violations = sum(
        arrival > int(payload["max_delay"]) for arrival in output_arrivals
    )

    mismatch_count = 0
    bus_conflict_count = 0
    undriven_output_count = 0
    rows = 0
    for source_values, targets in regression_rows(free_sources):
        rows += 1
        values = list(source_values)
        drivens = [True] * source_count
        for item in network:
            left, _left_driven, left_conflict = _resolve(
                values, drivens, item["left_bus"]
            )
            right, _right_driven, right_conflict = _resolve(
                values, drivens, item["right_bus"]
            )
            bus_conflict_count += left_conflict + right_conflict
            kind = item["kind"]
            if kind == "NOT":
                value, driven = not left, True
            elif kind == "AND":
                value, driven = left and right, True
            elif kind == "OR":
                value, driven = left or right, True
            elif kind == "NAND":
                value, driven = not (left and right), True
            elif kind == "NOR":
                value, driven = not (left or right), True
            elif kind == "XOR":
                value, driven = left ^ right, True
            elif kind == "SWITCH":
                value, driven = left and right, left
            else:  # pragma: no cover
                raise AssertionError(kind)
            values.append(bool(value))
            drivens.append(bool(driven))
        for bus, expected in zip(output_buses, targets, strict=True):
            value, driven, conflict = _resolve(values, drivens, bus)
            bus_conflict_count += conflict
            mismatch_count += value != expected
            undriven_output_count += not driven

    checks = {
        "rows": rows,
        "actual_gate": actual_gate,
        "actual_output_arrivals": output_arrivals,
        "actual_max_delay": max(output_arrivals),
        "mismatch_count": mismatch_count,
        "bus_conflict_count": bus_conflict_count,
        "undriven_output_count": undriven_output_count,
        "physical_net_partition_violation_count": physical_partition_violations,
        "active_bus_non_switch_driver_violation_count": (
            active_bus_non_switch_driver_violations
        ),
        "topology_violation_count": topology_violations,
        "commutative_order_violation_count": canonical_order_violations,
        "dead_component_count": dead_component_count,
        "depth_upper_bound_violation_count": depth_upper_bound_violations,
        "output_deadline_violation_count": output_deadline_violations,
    }
    zero_fields = [key for key in checks if key.endswith("count")]
    checks["verified"] = (
        rows == 486
        and actual_gate == 16
        and max(output_arrivals) <= 5
        and all(checks[key] == 0 for key in zero_fields)
    )
    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if digest(SOURCE_WITNESS) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("frozen S7/C8 source witness hash changed")
    source = json.loads(SOURCE_WITNESS.read_text(encoding="utf-8"))
    if (
        source.get("status") != "sat"
        or tuple(source.get("fixed_kinds", ())) != FIXED_KINDS
        or source.get("verification", {}).get("mismatch_count") != 0
        or source.get("verification", {}).get("bus_conflict_count") != 0
        or source.get("verification", {}).get("undriven_output_count") != 0
    ):
        raise RuntimeError("frozen S7/C8 source witness failed provenance checks")
    regression = build_regression(source)
    verification = verify(regression)
    if not verification["verified"]:
        raise RuntimeError(f"positive regression failed: {verification}")
    payload = {
        "schema": "s567c8-g16-o4-s6-all-switch-tail-positive-regression-v1",
        "status": "verified-positive-regression",
        "purpose": (
            "Two-output S7/C8 calibration of the exact g16 topology; not a "
            "four-output competitive witness"
        ),
        "source_witness": str(SOURCE_WITNESS.relative_to(ROOT)).replace("\\", "/"),
        "source_witness_sha256": digest(SOURCE_WITNESS),
        "worker": str(WORKER.relative_to(ROOT)).replace("\\", "/"),
        "worker_sha256": digest(WORKER),
        "competitive_candidate": False,
        "regression": regression,
        "verification": verification,
        "scope_note": (
            "This proves the fixed topology, exact cost, D5 timing, Z/BUS "
            "resolution, physical partition, and liveness on S7/C8 only."
        ),
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(args.output) if args.output else None,
                "output_sha256": (
                    digest(args.output)
                    if args.output is not None
                    else sha256(encoded.encode()).hexdigest()
                ),
                "verification": verification,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
