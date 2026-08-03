"""Independent replay and accounting for a bit-3:4 exact-search witness."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


KINDS = ("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH")
COST = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 3, "SWITCH": 2}
DELAY = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 2, "SWITCH": 1}
TARGET_NAMES = ("S3", "S4", "C5")
PROFILES = {
    "d7_80": {
        "output_deadlines": (5, 7, 4),
        "max_delay": 7,
        "current_complete_gate": 80,
        "current_complete_delay": 7,
        "fixed_shell_with_paid_leaves": 66,
        "target_complete_gate": 73,
    },
    "d6_95": {
        "output_deadlines": (5, 6, 4),
        "max_delay": 6,
        "current_complete_gate": 95,
        "current_complete_delay": 6,
        "fixed_shell_with_paid_leaves": 81,
        "target_complete_gate": 85,
    },
}


def problem():
    names = ["a3", "b3", "a4", "b4", "C3"]
    rows = [[] for _ in names]
    drivens = [[] for _ in names]
    states = []
    for raw in range(16):
        bits = [bool((raw >> bit) & 1) for bit in range(4)]
        for state in ("Z0", "D0", "D1"):
            values = (*bits, state == "D1")
            for index, value in enumerate(values):
                rows[index].append(bool(value))
                drivens[index].append(index != 4 or state != "Z0")
            states.append(state)

    def pw(function, *inputs):
        return [
            bool(function(*(int(row[index]) for row in inputs)))
            for index in range(len(inputs[0]))
        ]

    a3, b3, a4, b4, c3 = rows
    g3 = pw(lambda a, b: a & b, a3, b3)
    q3 = pw(lambda a, b: 1 ^ (a | b), a3, b3)
    p3 = pw(lambda g, q: 1 ^ (g | q), g3, q3)
    g4 = pw(lambda a, b: a & b, a4, b4)
    q4 = pw(lambda a, b: 1 ^ (a | b), a4, b4)
    p4 = pw(lambda g, q: 1 ^ (g | q), g4, q4)
    c4 = pw(lambda g, p, c: g | (p & c), g3, p3, c3)
    targets = (
        pw(lambda p, c: p ^ c, p3, c3),
        pw(lambda p, c: p ^ c, p4, c4),
        pw(lambda g, p, c: g | (p & c), g4, p4, c4),
    )
    names.extend(("G3", "Q3", "P3", "G4", "Q4", "P4", "0", "1"))
    rows.extend((g3, q3, p3, g4, q4, p4, [False] * 48, [True] * 48))
    drivens.extend([[True] * 48 for _ in range(8)])
    arrivals = [0, 0, 0, 0, 3, 1, 1, 2, 1, 1, 2, 0, 0]
    return names, rows, drivens, arrivals, targets, states


def resolve(bus, values, drivens):
    active = {values[source] for source in bus if drivens[source]}
    return (
        (False, False, False)
        if not active
        else (next(iter(active)), True, False)
        if len(active) == 1
        else (False, True, True)
    )


def replay(payload: dict[str, object]) -> dict[str, object]:
    # Certificates produced before profiles were added are the calibrated
    # D7/80 interface and remain independently replayable.
    profile_name = str(payload.get("profile", "d7_80"))
    if profile_name not in PROFILES:
        raise ValueError(f"unknown profile {profile_name!r}")
    profile = PROFILES[profile_name]
    deadlines = tuple(int(value) for value in profile["output_deadlines"])
    names, source_rows, source_drivens, source_arrivals, targets, states = problem()
    network = payload.get("network")
    output_buses = payload.get("output_buses")
    if not isinstance(network, list) or not isinstance(output_buses, list):
        raise ValueError("certificate has no decoded network/output buses")
    if len(output_buses) != 3:
        raise ValueError("expected three output buses")

    source_count = len(names)
    values_by_case = []
    driven_by_case = []
    arrivals = list(source_arrivals)
    gate = 0
    kind_counts = {kind: 0 for kind in KINDS}
    topology_errors = []
    declared_depth_errors = []
    for case in range(48):
        values_by_case.append([row[case] for row in source_rows])
        driven_by_case.append([row[case] for row in source_drivens])

    buses = []
    internal_bus_conflict_count = 0
    for expected_slot, item in enumerate(network):
        kind = str(item["kind"])
        if kind not in KINDS:
            raise ValueError(f"unknown kind {kind}")
        if int(item["slot"]) != expected_slot or int(item["source"]) != source_count + expected_slot:
            topology_errors.append({"slot": expected_slot, "item": item})
        left = tuple(int(value) for value in item["left_bus"])
        right = tuple(int(value) for value in item["right_bus"])
        available = source_count + expected_slot
        if any(source < 0 or source >= available for source in (*left, *right)):
            topology_errors.append({"slot": expected_slot, "reason": "forward/out-of-range source"})
        if not left or (kind != "NOT" and not right) or (kind == "NOT" and right):
            topology_errors.append({"slot": expected_slot, "reason": "invalid arity"})
        buses.extend((frozenset(left), frozenset(right)))
        actual_depth = max((arrivals[source] for source in (*left, *right)), default=0) + DELAY[kind]
        arrivals.append(actual_depth)
        if int(item["depth_upper_bound"]) < actual_depth:
            declared_depth_errors.append(
                {"slot": expected_slot, "actual": actual_depth, "declared": item["depth_upper_bound"]}
            )
        gate += COST[kind]
        kind_counts[kind] += 1

        for case in range(48):
            values = values_by_case[case]
            drivens = driven_by_case[case]
            lv, _ld, left_conflict = resolve(left, values, drivens)
            rv, _rd, right_conflict = resolve(right, values, drivens)
            internal_bus_conflict_count += int(left_conflict) + int(right_conflict)
            if left_conflict or right_conflict:
                # Preserve a sentinel; conflict count is accumulated below.
                value, driven = False, True
            elif kind == "NOT":
                value, driven = not lv, True
            elif kind == "AND":
                value, driven = lv and rv, True
            elif kind == "OR":
                value, driven = lv or rv, True
            elif kind == "NAND":
                value, driven = not (lv and rv), True
            elif kind == "NOR":
                value, driven = not (lv or rv), True
            elif kind == "XOR":
                value, driven = lv ^ rv, True
            elif kind == "SWITCH":
                value, driven = lv and rv, lv
            else:
                raise AssertionError(kind)
            values.append(bool(value))
            drivens.append(bool(driven))

    forced_slot_kind_errors = []
    forced_slot_kinds = payload.get("forced_slot_kinds", {})
    if not isinstance(forced_slot_kinds, dict):
        forced_slot_kind_errors.append(
            {
                "field": "forced_slot_kinds",
                "expected": "object",
                "actual": forced_slot_kinds,
            }
        )
    else:
        for raw_slot, expected_kind in forced_slot_kinds.items():
            try:
                slot = int(raw_slot)
            except (TypeError, ValueError):
                forced_slot_kind_errors.append(
                    {"slot": raw_slot, "reason": "slot is not an integer"}
                )
                continue
            if not 0 <= slot < len(network):
                forced_slot_kind_errors.append(
                    {"slot": slot, "reason": "slot is outside the network"}
                )
                continue
            actual_kind = str(network[slot]["kind"])
            if actual_kind != expected_kind:
                forced_slot_kind_errors.append(
                    {
                        "slot": slot,
                        "expected_kind": expected_kind,
                        "actual_kind": actual_kind,
                    }
                )

    output_sets = [frozenset(int(value) for value in bus) for bus in output_buses]
    buses.extend(output_sets)
    partition_violations = []
    for left_index, left in enumerate(buses):
        for right_index, right in enumerate(buses[left_index + 1 :], start=left_index + 1):
            shared = left & right
            if shared and left != right:
                partition_violations.append(
                    {"left_bus": left_index, "right_bus": right_index, "shared": sorted(shared)}
                )

    mismatch_by_output = [0, 0, 0]
    conflict_by_output = [0, 0, 0]
    z_by_output = [0, 0, 0]
    illegal_z_by_output = [0, 0, 0]
    deadline_errors = []
    for output, bus in enumerate(output_sets):
        arrival = max((arrivals[source] for source in bus), default=0)
        if arrival > deadlines[output]:
            deadline_errors.append(
                {
                    "output": TARGET_NAMES[output],
                    "arrival": arrival,
                    "deadline": deadlines[output],
                }
            )
        for case in range(48):
            value, driven, conflict = resolve(
                bus, values_by_case[case], driven_by_case[case]
            )
            expected = targets[output][case]
            mismatch_by_output[output] += value != expected
            conflict_by_output[output] += conflict
            z_by_output[output] += not driven
            if output < 2 and not driven:
                illegal_z_by_output[output] += 1
            if output == 2 and expected and not driven:
                illegal_z_by_output[output] += 1

    accounting = payload.get("accounting")
    accounting_errors = []
    declared_deadlines = tuple(int(value) for value in payload.get("output_deadlines", ()))
    if declared_deadlines != deadlines:
        accounting_errors.append(
            {
                "field": "output_deadlines",
                "expected": list(deadlines),
                "actual": list(declared_deadlines),
            }
        )
    expected_scalars = {
        "max_delay": profile["max_delay"],
        "components": len(network),
        "actual_gate": gate,
    }
    for field, expected in expected_scalars.items():
        actual = payload.get(field)
        if actual != expected:
            accounting_errors.append(
                {"field": field, "expected": expected, "actual": actual}
            )
    gate_bound = payload.get("gate_bound")
    if not isinstance(gate_bound, int) or gate > gate_bound:
        accounting_errors.append(
            {"field": "gate_bound", "expected": f">= {gate}", "actual": gate_bound}
        )
    actual_switches = kind_counts["SWITCH"]
    actual_xors = kind_counts["XOR"]
    for field, actual_count in (
        ("exact_switches", actual_switches),
        ("exact_xors", actual_xors),
    ):
        declared = payload.get(field)
        if declared is not None and declared != actual_count:
            accounting_errors.append(
                {"field": field, "expected": actual_count, "actual": declared}
            )
    if not isinstance(accounting, dict):
        accounting_errors.append(
            {"field": "accounting", "expected": "object", "actual": accounting}
        )
        accounting = {}
    projected_gate = int(profile["fixed_shell_with_paid_leaves"]) + gate
    expected_accounting = {
        "current_complete_gate": profile["current_complete_gate"],
        "current_complete_delay": profile["current_complete_delay"],
        "current_residual_gate": 14,
        "current_residual_components": 12,
        "fixed_shell_with_paid_leaves": profile["fixed_shell_with_paid_leaves"],
        "projected_complete_gate_actual": projected_gate,
        "projected_complete_gate_at_bound": (
            int(profile["fixed_shell_with_paid_leaves"]) + int(gate_bound)
            if isinstance(gate_bound, int)
            else None
        ),
        "projected_complete_delay": profile["current_complete_delay"],
        "target_complete_gate": profile["target_complete_gate"],
    }
    # Older D7 certificates predate the last three explicit fields.  Missing
    # legacy fields are accepted only for that backward-compatible schema;
    # present fields must always agree with the independently known ledger.
    legacy_d7 = "profile" not in payload and profile_name == "d7_80"
    optional_legacy = {
        "target_complete_gate",
    }
    for field, expected in expected_accounting.items():
        if legacy_d7 and field in optional_legacy and field not in accounting:
            continue
        actual = accounting.get(field)
        if actual != expected:
            accounting_errors.append(
                {"field": f"accounting.{field}", "expected": expected, "actual": actual}
            )

    ok = not (
        topology_errors
        or declared_depth_errors
        or partition_violations
        or any(mismatch_by_output)
        or any(conflict_by_output)
        or any(illegal_z_by_output)
        or internal_bus_conflict_count
        or deadline_errors
        or accounting_errors
        or forced_slot_kind_errors
    )
    return {
        "ok": ok,
        "profile": profile_name,
        "rows": 48,
        "boundary_state_counts": {state: states.count(state) for state in sorted(set(states))},
        "actual_gate": gate,
        "kind_counts": {key: value for key, value in kind_counts.items() if value},
        "projected_complete_gate": projected_gate,
        "projected_complete_delay": profile["current_complete_delay"],
        "target_complete_gate": profile["target_complete_gate"],
        "gate_gap_to_target": projected_gate - int(profile["target_complete_gate"]),
        "output_deadlines": list(deadlines),
        "output_arrivals": [
            max((arrivals[source] for source in bus), default=0) for bus in output_sets
        ],
        "mismatch_count_by_output": dict(zip(TARGET_NAMES, mismatch_by_output, strict=True)),
        "conflict_count_by_output": dict(zip(TARGET_NAMES, conflict_by_output, strict=True)),
        "z_count_by_output": dict(zip(TARGET_NAMES, z_by_output, strict=True)),
        "illegal_z_count_by_output": dict(zip(TARGET_NAMES, illegal_z_by_output, strict=True)),
        "internal_bus_conflict_count": internal_bus_conflict_count,
        "topology_errors": topology_errors,
        "declared_depth_errors": declared_depth_errors,
        "physical_net_partition_violations": partition_violations,
        "deadline_errors": deadline_errors,
        "accounting_errors": accounting_errors,
        "forced_slot_kind_errors": forced_slot_kind_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = args.certificate.read_bytes()
    payload = json.loads(raw)
    report = {
        "schema": "tc-byte-adder-bit34-independent-replay-v1",
        "certificate": str(args.certificate.resolve()),
        "certificate_sha256": sha256(raw).hexdigest(),
        "certificate_status": payload.get("status"),
        "verification": replay(payload),
    }
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["verification"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
