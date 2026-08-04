"""Independently replay a SAT physical_exact S5/S6/S7/C8 witness.

This verifier does not rebuild the CNF and does not trust the worker's
``verification`` object.  It replays all 486 rows, Switch Z/driven behavior,
BUS conflicts, public-output driven state, physical-net partitioning,
component liveness, exact primitive cost, and D5 timing from the decoded
network alone.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHYSICAL_EXACT = (
    ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
)
KINDS = ("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH")
COST = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 3, "SWITCH": 2}
DELAY = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 2, "SWITCH": 1}
ALLOWED_OUTPUT_NAMES = ("S3", "S4", "S5", "S6", "S7", "C8")


def load_physical_exact():
    spec = importlib.util.spec_from_file_location(
        "han_witness_replay_physical_exact", PHYSICAL_EXACT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(PHYSICAL_EXACT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


physical_exact = load_physical_exact()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    evidence_path = args.evidence.resolve()
    output_path = args.output or evidence_path.with_name(
        evidence_path.stem + "_independent_replay.json"
    )
    raw = evidence_path.read_bytes()
    payload = json.loads(raw)
    if payload.get("status") != "sat":
        raise ValueError("evidence is not SAT")

    domain = physical_exact.domain_s34567c8_leaf()
    output_names = tuple(payload.get("output_names") or ())
    if not output_names or any(name not in ALLOWED_OUTPUT_NAMES for name in output_names):
        raise ValueError(f"invalid output subset: {output_names!r}")
    target_indices = tuple(domain.output_names.index(name) for name in output_names)
    targets = tuple(domain.targets[index] for index in target_indices)
    expected_sources = [*domain.names, "0", "1"]
    network = list(payload.get("network") or [])
    output_buses = list(payload.get("output_buses") or [])
    source_count = len(expected_sources)
    rows = domain.rows
    errors: list[dict[str, object]] = []

    def error(reason: str, **details: object) -> None:
        errors.append({"reason": reason, **details})

    if payload.get("domain") != "s34567c8_leaf":
        error("domain", actual=payload.get("domain"))
    if payload.get("rows") != rows:
        error("rows", expected=rows, actual=payload.get("rows"))
    if len(set(output_names)) != len(output_names):
        error("duplicate_outputs", actual=list(output_names))
    if payload.get("free_sources") != expected_sources:
        error("free_sources", actual=payload.get("free_sources"))
    if len(network) != payload.get("components"):
        error(
            "network_length",
            expected=payload.get("components"),
            actual=len(network),
        )
    if len(output_buses) != len(output_names):
        error("output_bus_count", actual=len(output_buses))

    values = [list(column) for column in domain.columns]
    values.extend(([False] * rows, [True] * rows))
    drivens = [[True] * rows for _ in values]
    arrivals = [domain.arrivals[name] for name in domain.names]
    arrivals.extend((0, 0))
    all_buses: list[tuple[str, frozenset[int]]] = []
    conflict_count = 0
    malformed_bus_count = 0

    def validate_bus(name: str, bus: object, available: int) -> list[int]:
        nonlocal malformed_bus_count
        if not isinstance(bus, list) or any(not isinstance(item, int) for item in bus):
            malformed_bus_count += 1
            error("malformed_bus", bus=name, value=bus)
            return []
        if len(set(bus)) != len(bus):
            malformed_bus_count += 1
            error("duplicate_bus_source", bus=name, value=bus)
        if any(source < 0 or source >= available for source in bus):
            malformed_bus_count += 1
            error("out_of_range_bus_source", bus=name, available=available, value=bus)
        valid = [source for source in bus if 0 <= source < available]
        if len(valid) > 1:
            for source in valid:
                if source < source_count:
                    error("multi_driver_bus_contains_paid_source", bus=name, source=source)
                else:
                    predecessor = source - source_count
                    if predecessor >= len(network) or network[predecessor].get("kind") != "SWITCH":
                        error(
                            "multi_driver_bus_contains_non_switch",
                            bus=name,
                            source=source,
                        )
        all_buses.append((name, frozenset(valid)))
        return valid

    def resolve(bus: list[int], row: int, name: str) -> tuple[bool, bool]:
        nonlocal conflict_count
        active = {values[source][row] for source in bus if drivens[source][row]}
        if len(active) > 1:
            conflict_count += 1
            error("bus_conflict", bus=name, row=row)
            return False, True
        if not active:
            return False, False
        return bool(next(iter(active))), True

    actual_gate = 0
    switch_count = 0
    xor_count = 0
    depth_upper_bound_violation_count = 0
    for slot, item in enumerate(network):
        available = source_count + slot
        if item.get("slot") != slot:
            error("slot_index", slot=slot, actual=item.get("slot"))
        if item.get("source") != available:
            error("source_index", slot=slot, expected=available, actual=item.get("source"))
        kind = item.get("kind")
        if kind not in KINDS:
            error("kind", slot=slot, actual=kind)
            kind = "NOT"
        expected_cost = COST[kind]
        if item.get("cost") != expected_cost:
            error("item_cost", slot=slot, expected=expected_cost, actual=item.get("cost"))
        actual_gate += expected_cost
        switch_count += int(kind == "SWITCH")
        xor_count += int(kind == "XOR")

        left = validate_bus(f"slot{slot}_left", item.get("left_bus"), available)
        right = validate_bus(f"slot{slot}_right", item.get("right_bus"), available)
        if not left:
            error("empty_left_bus", slot=slot)
        if kind == "NOT" and right:
            error("not_has_right_bus", slot=slot, right=right)
        if kind != "NOT" and not right:
            error("binary_kind_empty_right_bus", slot=slot, kind=kind)

        out_values: list[bool] = []
        out_drivens: list[bool] = []
        for row in range(rows):
            left_value, _left_driven = resolve(left, row, f"slot{slot}_left")
            right_value, _right_driven = resolve(right, row, f"slot{slot}_right")
            if kind == "NOT":
                value, driven = not left_value, True
            elif kind == "AND":
                value, driven = left_value and right_value, True
            elif kind == "OR":
                value, driven = left_value or right_value, True
            elif kind == "NAND":
                value, driven = not (left_value and right_value), True
            elif kind == "NOR":
                value, driven = not (left_value or right_value), True
            elif kind == "XOR":
                value, driven = left_value ^ right_value, True
            elif kind == "SWITCH":
                value, driven = left_value and right_value, left_value
            else:  # pragma: no cover
                raise AssertionError(kind)
            out_values.append(bool(value))
            out_drivens.append(bool(driven))
        values.append(out_values)
        drivens.append(out_drivens)

        input_arrival = max((arrivals[source] for source in [*left, *right]), default=0)
        actual_arrival = input_arrival + DELAY[kind]
        arrivals.append(actual_arrival)
        upper = item.get("depth_upper_bound")
        if not isinstance(upper, int) or actual_arrival > upper:
            depth_upper_bound_violation_count += 1
            error(
                "depth_upper_bound",
                slot=slot,
                actual=actual_arrival,
                upper=upper,
            )

    output_arrivals: list[int] = []
    mismatch_count = 0
    undriven_output_count = 0
    checked_output_buses: list[list[int]] = []
    for output, target in enumerate(targets):
        bus = validate_bus(
            f"output{output}",
            output_buses[output] if output < len(output_buses) else [],
            source_count + len(network),
        )
        checked_output_buses.append(bus)
        if not bus:
            error("empty_output_bus", output=output)
        output_arrivals.append(max((arrivals[source] for source in bus), default=0))
        for row in range(rows):
            value, driven = resolve(bus, row, f"output{output}")
            wanted = bool((target >> row) & 1)
            if not driven:
                undriven_output_count += 1
            if not driven or value != wanted:
                mismatch_count += 1

    physical_violations: list[dict[str, object]] = []
    for left_index, (left_name, left_bus) in enumerate(all_buses):
        for right_name, right_bus in all_buses[left_index + 1 :]:
            shared = left_bus & right_bus
            if shared and left_bus != right_bus:
                physical_violations.append(
                    {
                        "left": left_name,
                        "right": right_name,
                        "shared_sources": sorted(shared),
                        "left_only": sorted(left_bus - right_bus),
                        "right_only": sorted(right_bus - left_bus),
                    }
                )

    dead_components: list[int] = []
    for slot in range(len(network)):
        source = source_count + slot
        used = any(
            source in (item.get("left_bus") or [])
            or source in (item.get("right_bus") or [])
            for item in network[slot + 1 :]
        ) or any(source in bus for bus in checked_output_buses)
        if not used:
            dead_components.append(slot)

    fixed = payload.get("fixed_kinds")
    fixed_mismatches: list[dict[str, object]] = []
    if fixed is not None:
        for slot, (expected, item) in enumerate(zip(fixed, network, strict=True)):
            if expected != "*" and item.get("kind") != expected:
                fixed_mismatches.append(
                    {"slot": slot, "expected": expected, "actual": item.get("kind")}
                )

    verification = payload.get("verification") or {}
    recomputed = {
        "rows": rows,
        "output_checks": rows * len(targets),
        "mismatch_count": mismatch_count,
        "bus_conflict_count": conflict_count,
        "undriven_output_count": undriven_output_count,
        "physical_net_partition_violation_count": len(physical_violations),
        "dead_component_count": len(dead_components),
        "depth_upper_bound_violation_count": depth_upper_bound_violation_count,
        "output_deadline_violation_count": sum(
            arrival > payload.get("max_delay", 5) for arrival in output_arrivals
        ),
        "actual_output_arrivals": output_arrivals,
        "actual_max_delay": max(output_arrivals, default=0),
        "actual_gate": actual_gate,
        "switch_count": switch_count,
        "xor_count": xor_count,
        "malformed_bus_count": malformed_bus_count,
    }
    zero_required = (
        "mismatch_count",
        "bus_conflict_count",
        "undriven_output_count",
        "physical_net_partition_violation_count",
        "dead_component_count",
        "depth_upper_bound_violation_count",
        "output_deadline_violation_count",
        "malformed_bus_count",
    )
    for key in zero_required:
        if recomputed[key]:
            error("nonzero_recomputed_count", field=key, value=recomputed[key])
    if actual_gate != payload.get("actual_gate"):
        error("actual_gate", recomputed=actual_gate, worker=payload.get("actual_gate"))
    if actual_gate > payload.get("gate_bound", 0):
        error("gate_bound", actual=actual_gate, bound=payload.get("gate_bound"))
    if switch_count != payload.get("exact_switches"):
        error("switch_count", actual=switch_count, expected=payload.get("exact_switches"))
    if xor_count != payload.get("exact_xors"):
        error("xor_count", actual=xor_count, expected=payload.get("exact_xors"))
    if fixed_mismatches:
        error("fixed_kind_mismatch", mismatches=fixed_mismatches)
    if verification:
        for key in zero_required:
            if key in verification and verification[key] != recomputed[key]:
                error(
                    "worker_verification_disagrees",
                    field=key,
                    worker=verification[key],
                    recomputed=recomputed[key],
                )
        for key in ("actual_output_arrivals", "actual_max_delay"):
            if key in verification and verification[key] != recomputed[key]:
                error(
                    "worker_verification_disagrees",
                    field=key,
                    worker=verification[key],
                    recomputed=recomputed[key],
                )

    result = {
        "schema": "s567c8-physical-witness-independent-replay-v1",
        "status": "verified" if not errors else "failed",
        "evidence": relative(evidence_path),
        "evidence_sha256": sha256(raw).hexdigest(),
        "physical_exact": relative(PHYSICAL_EXACT),
        "physical_exact_sha256": sha256(PHYSICAL_EXACT.read_bytes()).hexdigest(),
        "recomputed": recomputed,
        "physical_net_partition_violations": physical_violations,
        "dead_components": dead_components,
        "fixed_kind_mismatches": fixed_mismatches,
        "errors": errors,
    }
    encoded = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": result["status"],
                "errors": len(errors),
                "recomputed": recomputed,
                "output": str(output_path.resolve()),
                "sha256": sha256(encoded).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
