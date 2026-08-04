"""Independently verify a fixed73/high-residual physical SAT witness.

The verifier intentionally does not import ``physical_exact.py`` or its SAT
backend.  It reconstructs the correlated 486-row high-window domain and the
complete 2^17 Byte Adder input domain, then replays every ordinary gate,
Switch driver, resolved BUS, conflict mask, Z mask, and recursive arrival.

Production mode accepts only the complete S3..S7/C8 witness used by the
conditional 102/5 or 103/5 construction.  ``--fixture`` is explicit and
accepts an ordered output subset on the same paid-source boundary; fixture
results are never labelled as competitive candidates.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import itertools
import json
from pathlib import Path
import re
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER = ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
DEPENDENCIES = (
    ROOT / ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py",
    ROOT / ".research/byte_adder_boolean_superopt_agent/exact_adder_block_sat.py",
    ROOT / ".research/rng_468_joint_macro/joint_parity_cnf.py",
)

SCHEMA = "exact-fast-negative-physical-shard-v2"
DOMAIN = "s34567c8_leaf"
DOMAIN_ROWS = 2 * 3**5
FULL_ROWS = 1 << 17
OUTPUT_NAMES = ("S3", "S4", "S5", "S6", "S7", "C8")
FIXED_LOW_PREFIX_GATE = 35
FIXED_HIGH_PAID_STATE_GATE = 38
FIXED_TOTAL_GATE = FIXED_LOW_PREFIX_GATE + FIXED_HIGH_PAID_STATE_GATE
STRICT_RESIDUAL_GATE_LIMIT = 29
MAX_RESIDUAL_GATE_LIMIT = 30
MAX_COMPLETE_GATE = FIXED_TOTAL_GATE + MAX_RESIDUAL_GATE_LIMIT
MAX_COMPLETE_DELAY = 5
MAX_COMPLETE_ENERGY = MAX_COMPLETE_GATE * MAX_COMPLETE_DELAY
SUPPORTED_RESIDUAL_GATE_LIMITS = (
    STRICT_RESIDUAL_GATE_LIMIT,
    MAX_RESIDUAL_GATE_LIMIT,
)
SOURCE_NAMES = (
    "nC3",
    "G3", "Q3", "P3", "N3",
    "G4", "Q4", "P4", "N4",
    "G5", "Q5", "P5", "N5",
    "G6", "Q6", "P6", "N6",
    "G7", "Q7", "P7",
    "A34n", "V34n",
    "A56n", "V56n",
    "A36n", "V36n",
    "nC7",
    "0", "1",
)
SOURCE_ARRIVALS = {
    "nC3": 3,
    "G3": 1, "Q3": 1, "P3": 2, "N3": 1,
    "G4": 1, "Q4": 1, "P4": 2, "N4": 1,
    "G5": 1, "Q5": 1, "P5": 2, "N5": 1,
    "G6": 1, "Q6": 1, "P6": 2, "N6": 1,
    "G7": 1, "Q7": 1, "P7": 2,
    "A34n": 2, "V34n": 2,
    "A56n": 2, "V56n": 2,
    "A36n": 3, "V36n": 3,
    "nC7": 4,
    "0": 0, "1": 0,
}
EXACT_COST = {
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 3,
    "SWITCH": 2,
}
EXACT_DELAY = {
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 2,
    "SWITCH": 1,
}


def complete_score_within_contract(metrics: dict[str, Any]) -> bool:
    """Return whether independently recomputed metrics meet the D5 frontier."""

    values = (metrics.get("gate"), metrics.get("delay"), metrics.get("energy"))
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        return False
    gate, delay, energy = values
    return (
        0 <= gate <= MAX_COMPLETE_GATE
        and 0 <= delay <= MAX_COMPLETE_DELAY
        and energy == gate * delay
        and energy <= MAX_COMPLETE_ENERGY
    )
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True, slots=True)
class Signal:
    value: int
    driven: int
    conflict: int
    arrival: int


def _require_int(value: object, label: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise RuntimeError(f"{label} must be an integer >= {minimum}: {value!r}")
    return value


def _portable(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def _assert_output_path(path: Path) -> Path:
    resolved = path.resolve()
    if resolved != HERE and HERE not in resolved.parents:
        raise RuntimeError(f"derived output must stay below {HERE}: {resolved}")
    return resolved


def _dependency_hashes() -> dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in DEPENDENCIES
    }


def _bus(
    raw: object,
    *,
    label: str,
    available: int,
    source_count: int,
    switch_sources: set[int],
    allow_empty: bool = False,
) -> tuple[int, ...]:
    if not isinstance(raw, list):
        raise RuntimeError(f"{label} must be a list")
    result = tuple(_require_int(item, f"{label} source") for item in raw)
    if not result and not allow_empty:
        raise RuntimeError(f"{label} must not be empty")
    if result != tuple(sorted(set(result))):
        raise RuntimeError(f"{label} must be sorted and unique: {result!r}")
    if any(item >= available for item in result):
        raise RuntimeError(f"{label} contains a forward or unknown source: {result!r}")
    if len(result) > 1 and any(
        item < source_count or item not in switch_sources for item in result
    ):
        raise RuntimeError(f"{label} is not a Switch-only resolved BUS: {result!r}")
    return result


def _validate_structure(
    payload: dict[str, Any],
    *,
    fixture: bool,
    max_residual_gate: int,
) -> dict[str, Any]:
    if max_residual_gate not in SUPPORTED_RESIDUAL_GATE_LIMITS:
        raise ValueError(
            f"max_residual_gate must be one of {SUPPORTED_RESIDUAL_GATE_LIMITS!r}"
        )
    if payload.get("schema") != SCHEMA:
        raise RuntimeError(f"unsupported witness schema: {payload.get('schema')!r}")
    if payload.get("status") != "sat":
        raise RuntimeError(f"witness is not SAT: {payload.get('status')!r}")
    if payload.get("domain") != DOMAIN:
        raise RuntimeError(f"witness domain must be {DOMAIN!r}")
    if _require_int(payload.get("rows"), "rows") != DOMAIN_ROWS:
        raise RuntimeError(f"witness rows must be {DOMAIN_ROWS}")

    raw_output_names = payload.get("output_names")
    if not isinstance(raw_output_names, list):
        raise RuntimeError("output_names must be a list")
    output_names = tuple(str(name) for name in raw_output_names)
    if fixture:
        if not output_names:
            raise RuntimeError("fixture output_names must not be empty")
        expected_subset = tuple(name for name in OUTPUT_NAMES if name in output_names)
        if output_names != expected_subset or len(set(output_names)) != len(output_names):
            raise RuntimeError(
                f"fixture outputs must be an ordered subset of {OUTPUT_NAMES!r}: "
                f"{output_names!r}"
            )
    elif output_names != OUTPUT_NAMES:
        raise RuntimeError(
            f"production witness must expose {OUTPUT_NAMES!r}, got {output_names!r}"
        )

    if tuple(payload.get("free_sources", ())) != SOURCE_NAMES:
        raise RuntimeError("paid free-source order changed")
    if payload.get("source_arrivals") != SOURCE_ARRIVALS:
        raise RuntimeError("paid source-arrival contract changed")
    if payload.get("physical_nets") is not True:
        raise RuntimeError("physical_nets must be true")
    if payload.get("public_outputs_must_be_driven") is not True:
        raise RuntimeError("public_outputs_must_be_driven must be true")

    dependency_hashes = payload.get("dependency_sha256")
    current_dependency_hashes = _dependency_hashes()
    if dependency_hashes != current_dependency_hashes:
        raise RuntimeError(
            "SAT dependency hashes differ from the locally reviewed worker dependencies"
        )
    if not all(HEX64.fullmatch(value) for value in current_dependency_hashes.values()):
        raise AssertionError("invalid local SHA-256")

    max_delay = _require_int(payload.get("max_delay"), "max_delay")
    if max_delay != 5:
        raise RuntimeError(f"high-window deadline must be 5, got {max_delay}")
    components = _require_int(payload.get("components"), "components")
    switches_claimed = _require_int(payload.get("exact_switches"), "exact_switches")
    xors_claimed = _require_int(payload.get("exact_xors"), "exact_xors")
    ordinary_claimed = _require_int(payload.get("ordinary"), "ordinary")
    gate_bound = _require_int(payload.get("gate_bound"), "gate_bound")
    actual_gate_claimed = _require_int(payload.get("actual_gate"), "actual_gate")
    if gate_bound > max_residual_gate:
        raise RuntimeError(
            f"high residual exceeds the {max_residual_gate}-gate budget: {gate_bound}"
        )
    if components + switches_claimed + 2 * xors_claimed != gate_bound:
        raise RuntimeError("component/Switch/XOR gate-bound decomposition changed")
    if components - switches_claimed - xors_claimed != ordinary_claimed:
        raise RuntimeError("ordinary component decomposition changed")

    network_raw = payload.get("network")
    if not isinstance(network_raw, list) or len(network_raw) != components:
        raise RuntimeError("network length differs from components")
    output_buses_raw = payload.get("output_buses")
    if not isinstance(output_buses_raw, list) or len(output_buses_raw) != len(output_names):
        raise RuntimeError("output_buses length differs from output_names")

    source_count = len(SOURCE_NAMES)
    arrivals = [SOURCE_ARRIVALS[name] for name in SOURCE_NAMES]
    switch_sources: set[int] = set()
    all_buses: list[tuple[str, tuple[int, ...]]] = []
    network: list[dict[str, Any]] = []
    gate = switches = xors = 0
    depth_violations = 0

    fixed_kinds_raw = payload.get("fixed_kinds")
    if fixed_kinds_raw is not None:
        if not isinstance(fixed_kinds_raw, list) or len(fixed_kinds_raw) != components:
            raise RuntimeError("fixed_kinds must be null or a component-length list")
        if any(kind not in {*EXACT_COST, "*"} for kind in fixed_kinds_raw):
            raise RuntimeError("fixed_kinds contains an unsupported kind")

    for slot, raw_item in enumerate(network_raw):
        if not isinstance(raw_item, dict):
            raise RuntimeError(f"slot {slot} is not an object")
        if _require_int(raw_item.get("slot"), f"slot {slot}.slot") != slot:
            raise RuntimeError("network slots are not consecutive")
        source = _require_int(raw_item.get("source"), f"slot {slot}.source")
        if source != source_count + slot:
            raise RuntimeError(
                f"slot {slot} source must be {source_count + slot}, got {source}"
            )
        kind = raw_item.get("kind")
        if kind not in EXACT_COST:
            raise RuntimeError(f"slot {slot} has unsupported kind {kind!r}")
        if fixed_kinds_raw is not None and fixed_kinds_raw[slot] not in {"*", kind}:
            raise RuntimeError(f"slot {slot} violates fixed_kinds")
        cost = _require_int(raw_item.get("cost"), f"slot {slot}.cost")
        if cost != EXACT_COST[kind]:
            raise RuntimeError(f"slot {slot} cost annotation changed")

        available = source_count + slot
        left = _bus(
            raw_item.get("left_bus"),
            label=f"slot {slot}.left_bus",
            available=available,
            source_count=source_count,
            switch_sources=switch_sources,
        )
        right = _bus(
            raw_item.get("right_bus"),
            label=f"slot {slot}.right_bus",
            available=available,
            source_count=source_count,
            switch_sources=switch_sources,
            allow_empty=kind == "NOT",
        )
        if kind == "NOT" and right:
            raise RuntimeError(f"slot {slot} NOT has a right BUS")
        if kind != "NOT" and not right:
            raise RuntimeError(f"slot {slot} {kind} has an empty right BUS")
        all_buses.append((f"slot{slot}.left", left))
        if right:
            all_buses.append((f"slot{slot}.right", right))

        actual_arrival = max(arrivals[item] for item in (*left, *right)) + EXACT_DELAY[kind]
        claimed_arrival = _require_int(
            raw_item.get("depth_upper_bound"), f"slot {slot}.depth_upper_bound"
        )
        if actual_arrival > claimed_arrival or claimed_arrival > max_delay:
            depth_violations += 1
            raise RuntimeError(
                f"slot {slot} recursive arrival invalid: actual={actual_arrival}, "
                f"claim={claimed_arrival}, deadline={max_delay}"
            )
        arrivals.append(actual_arrival)
        gate += cost
        switches += kind == "SWITCH"
        xors += kind == "XOR"
        if kind == "SWITCH":
            switch_sources.add(source)
        network.append(
            {
                "slot": slot,
                "source": source,
                "kind": kind,
                "left_bus": list(left),
                "right_bus": list(right),
                "cost": cost,
                "depth_upper_bound": claimed_arrival,
            }
        )

    output_buses: list[list[int]] = []
    for index, raw_bus in enumerate(output_buses_raw):
        bus = _bus(
            raw_bus,
            label=f"output {index}",
            available=len(arrivals),
            source_count=source_count,
            switch_sources=switch_sources,
        )
        all_buses.append((f"output{index}", bus))
        output_buses.append(list(bus))

    partition_violations = []
    for index, (left_name, left) in enumerate(all_buses):
        left_set = set(left)
        for right_name, right in all_buses[index + 1 :]:
            if left_set.intersection(right) and left != right:
                partition_violations.append(
                    {
                        "left": left_name,
                        "right": right_name,
                        "left_bus": list(left),
                        "right_bus": list(right),
                    }
                )
    if partition_violations:
        raise RuntimeError(
            f"physical-net partition violation: {partition_violations[:2]!r}"
        )

    unused_sources = [
        source
        for source in range(source_count, source_count + components)
        if not any(source in bus for _label, bus in all_buses)
    ]
    if unused_sources:
        raise RuntimeError(f"dead exact component outputs: {unused_sources!r}")
    if gate != gate_bound or gate != actual_gate_claimed:
        raise RuntimeError(
            f"recomputed gate cost {gate} differs from bound/actual "
            f"{gate_bound}/{actual_gate_claimed}"
        )
    if switches != switches_claimed or xors != xors_claimed:
        raise RuntimeError(
            f"recomputed Switch/XOR counts {switches}/{xors} differ from "
            f"{switches_claimed}/{xors_claimed}"
        )
    output_arrivals = [max(arrivals[source] for source in bus) for bus in output_buses]
    if any(arrival > max_delay for arrival in output_arrivals):
        raise RuntimeError(f"output deadline failure: {output_arrivals!r}")

    return {
        "output_names": list(output_names),
        "source_count": source_count,
        "component_count": components,
        "ordinary": ordinary_claimed,
        "switches": switches,
        "xors": xors,
        "gate": gate,
        "max_delay": max_delay,
        "node_arrivals": arrivals[source_count:],
        "output_arrivals": output_arrivals,
        "network": network,
        "output_buses": output_buses,
        "physical_net_partition_violation_count": 0,
        "depth_upper_bound_violation_count": depth_violations,
        "dead_component_output_count": 0,
        "dependency_sha256": current_dependency_hashes,
    }


def _resolve(signals: Iterable[Signal], all_mask: int) -> Signal:
    signals = tuple(signals)
    if not signals:
        return Signal(0, 0, 0, 0)
    ones = zeros = driven = conflict = 0
    arrival = 0
    for signal in signals:
        ones |= signal.driven & signal.value
        zeros |= signal.driven & (~signal.value & all_mask)
        driven |= signal.driven
        conflict |= signal.conflict
        arrival = max(arrival, signal.arrival)
    conflict |= ones & zeros
    return Signal(
        ones & all_mask,
        driven & all_mask,
        conflict & all_mask,
        arrival,
    )


def _replay(
    network: list[dict[str, Any]],
    output_buses: list[list[int]],
    sources: tuple[Signal, ...],
    all_mask: int,
) -> tuple[tuple[Signal, ...], int]:
    signals = list(sources)
    bus_conflict = 0
    for item in network:
        left = _resolve((signals[index] for index in item["left_bus"]), all_mask)
        right = _resolve((signals[index] for index in item["right_bus"]), all_mask)
        bus_conflict |= left.conflict | right.conflict
        kind = item["kind"]
        if kind == "NOT":
            value = ~left.value
        elif kind == "AND":
            value = left.value & right.value
        elif kind == "OR":
            value = left.value | right.value
        elif kind == "NAND":
            value = ~(left.value & right.value)
        elif kind == "NOR":
            value = ~(left.value | right.value)
        elif kind == "XOR":
            value = left.value ^ right.value
        elif kind == "SWITCH":
            value = left.value & right.value
        else:  # pragma: no cover - validated before replay
            raise AssertionError(kind)
        driven = left.value if kind == "SWITCH" else all_mask
        signals.append(
            Signal(
                value & all_mask,
                driven & all_mask,
                (left.conflict | right.conflict) & all_mask,
                max(left.arrival, right.arrival) + EXACT_DELAY[kind],
            )
        )
    outputs = tuple(
        _resolve((signals[source] for source in bus), all_mask)
        for bus in output_buses
    )
    for output in outputs:
        bus_conflict |= output.conflict
    return outputs, bus_conflict & all_mask


def _local_state(state: int) -> tuple[bool, bool, bool, bool]:
    if state not in range(3):
        raise ValueError(state)
    q = state == 0
    p = state == 1
    g = state == 2
    return g, q, p, not g


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


def _pack(values: Iterable[bool]) -> int:
    return sum(int(value) << case for case, value in enumerate(values))


def _reduced_domain() -> tuple[dict[str, int], dict[str, int], int]:
    rows: list[dict[str, bool]] = []
    targets: dict[str, list[bool]] = {name: [] for name in OUTPUT_NAMES}
    for nc3 in (False, True):
        for states in itertools.product(range(3), repeat=5):
            local = {
                bit: _local_state(state)
                for bit, state in zip(range(3, 8), states, strict=True)
            }
            prefix = _prefix_values(local, nc3)
            row: dict[str, bool] = {"nC3": nc3}
            for bit in range(3, 7):
                g, q, p, n = local[bit]
                row.update(
                    {f"G{bit}": g, f"Q{bit}": q, f"P{bit}": p, f"N{bit}": n}
                )
            g7, q7, p7, _n7 = local[7]
            row.update({"G7": g7, "Q7": q7, "P7": p7})
            row.update({name: prefix[name] for name in SOURCE_NAMES if name in prefix})
            row.update({"0": False, "1": True})
            rows.append(row)
            carries = {3: nc3, 4: prefix["nC4"], 5: prefix["nC5"],
                       6: prefix["nC6"], 7: prefix["nC7"]}
            for bit in range(3, 8):
                targets[f"S{bit}"].append(local[bit][2] == carries[bit])
            nc8 = q7 or (p7 and prefix["nC7"])
            targets["C8"].append(not nc8)
    if len(rows) != DOMAIN_ROWS:
        raise AssertionError("reduced-domain row count changed")
    source_masks = {
        name: _pack(row[name] for row in rows)
        for name in SOURCE_NAMES
    }
    target_masks = {name: _pack(values) for name, values in targets.items()}
    return source_masks, target_masks, (1 << DOMAIN_ROWS) - 1


def _variable(index: int) -> int:
    if index < 3:
        byte = (0xAA, 0xCC, 0xF0)[index]
        return int.from_bytes(bytes([byte]) * (FULL_ROWS // 8), "little")
    block = 1 << (index - 3)
    data = (bytes(block) + bytes([0xFF]) * block) * (FULL_ROWS // (16 * block))
    return int.from_bytes(data, "little")


def _full_domain() -> tuple[
    dict[str, int], dict[str, int], dict[str, int], int, int
]:
    all_mask = (1 << FULL_ROWS) - 1
    a = [_variable(bit) for bit in range(8)]
    b = [_variable(8 + bit) for bit in range(8)]
    carry = _variable(16)
    sums: list[int] = []
    g: list[int] = []
    q: list[int] = []
    p: list[int] = []
    n: list[int] = []
    carry_by_bit = {0: carry}
    for bit in range(8):
        gi = a[bit] & b[bit]
        pi = a[bit] ^ b[bit]
        qi = ~(a[bit] | b[bit]) & all_mask
        ni = ~gi & all_mask
        g.append(gi)
        q.append(qi)
        p.append(pi)
        n.append(ni)
        sums.append(pi ^ carry)
        carry = gi | (pi & carry)
        carry_by_bit[bit + 1] = carry

    nc1 = ~carry_by_bit[1] & all_mask
    nc3 = ~carry_by_bit[3] & all_mask
    a12 = q[1] | q[2]
    v12 = n[2] & (q[2] | n[1])
    v12_driven = q[2] | n[1]
    nc3_driven = a12 | nc1
    a34 = q[3] | q[4]
    v34 = n[4] & (q[4] | n[3])
    a56 = q[5] | q[6]
    v56 = n[6] & (q[6] | n[5])
    a36 = a34 | a56
    v36 = v56 & (a56 | v34)
    nc7 = v36 & (a36 | nc3)
    v34_driven = q[4] | n[3]
    v56_driven = q[6] | n[5]
    v36_driven = a56 | v34
    nc7_driven = a36 | nc3
    boundary_mismatch = (nc7 ^ (~carry_by_bit[7] & all_mask)).bit_count()

    values = {
        "nC3": nc3,
        **{
            name: value
            for bit in range(3, 7)
            for name, value in (
                (f"G{bit}", g[bit]),
                (f"Q{bit}", q[bit]),
                (f"P{bit}", p[bit]),
                (f"N{bit}", n[bit]),
            )
        },
        "G7": g[7], "Q7": q[7], "P7": p[7],
        "A34n": a34, "V34n": v34,
        "A56n": a56, "V56n": v56,
        "A36n": a36, "V36n": v36,
        "nC7": nc7,
        "0": 0, "1": all_mask,
    }
    targets = {
        **{f"S{bit}": sums[bit] for bit in range(3, 8)},
        "C8": carry_by_bit[8],
    }
    driven = {
        name: all_mask for name in SOURCE_NAMES
    }
    driven.update(
        {
            "nC3": nc3_driven,
            "V34n": v34_driven,
            "V56n": v56_driven,
            "V36n": v36_driven,
            "nC7": nc7_driven,
        }
    )
    # The formulas above are the actual fixed-shell Switch enable unions.
    # ``v12_driven`` is retained in the assertion to guard the nc3 derivation.
    if (v12 & ~v12_driven & all_mask) or (nc3 & ~nc3_driven & all_mask):
        raise AssertionError("fixed-shell BUS value is asserted outside its driver mask")
    return values, driven, targets, all_mask, boundary_mismatch


def _signals(
    values: dict[str, int],
    all_mask: int,
    driven: dict[str, int] | None = None,
) -> tuple[Signal, ...]:
    driven = driven or {name: all_mask for name in SOURCE_NAMES}
    return tuple(
        Signal(
            values[name] & all_mask,
            driven[name] & all_mask,
            0,
            SOURCE_ARRIVALS[name],
        )
        for name in SOURCE_NAMES
    )


def _replay_report(
    *,
    label: str,
    rows: int,
    values: dict[str, int],
    targets: dict[str, int],
    all_mask: int,
    structure: dict[str, Any],
    driven: dict[str, int] | None = None,
) -> dict[str, Any]:
    outputs, conflict = _replay(
        structure["network"],
        structure["output_buses"],
        _signals(values, all_mask, driven),
        all_mask,
    )
    output_names = structure["output_names"]
    mismatches = [
        (signal.value ^ targets[name]).bit_count()
        for name, signal in zip(output_names, outputs, strict=True)
    ]
    mismatch_union = 0
    for name, signal in zip(output_names, outputs, strict=True):
        mismatch_union |= signal.value ^ targets[name]
    z_counts = [((~signal.driven) & all_mask).bit_count() for signal in outputs]
    output_arrivals = [signal.arrival for signal in outputs]
    digest = b"".join(
        signal.value.to_bytes((rows + 7) // 8, "little") for signal in outputs
    )
    result = {
        "label": label,
        "rows": rows,
        "output_names": list(output_names),
        "mismatch_count_by_output": mismatches,
        "mismatch_union_count": mismatch_union.bit_count(),
        "bus_conflict_count": conflict.bit_count(),
        "z_assignment_count_by_output": z_counts,
        "output_arrivals": output_arrivals,
        "output_vector_sha256": sha256(digest).hexdigest(),
        "paid_source_z_assignment_count": {
            name: ((~mask) & all_mask).bit_count()
            for name, mask in sorted((driven or {}).items())
            if mask != all_mask
        },
    }
    if any(mismatches) or mismatch_union or conflict or any(z_counts):
        raise RuntimeError(f"{label} semantic replay failed: {result!r}")
    if output_arrivals != structure["output_arrivals"]:
        raise RuntimeError(f"{label} replay arrival differs from structural recursion")
    return result


def _verify_metadata(payload: dict[str, Any], structure: dict[str, Any]) -> None:
    verification = payload.get("verification")
    if not isinstance(verification, dict):
        raise RuntimeError("verification metadata is missing")
    expected = {
        "mismatch_count": 0,
        "bus_conflict_count": 0,
        "undriven_output_count": 0,
        "physical_net_partition_violation_count": 0,
        "actual_output_arrivals": structure["output_arrivals"],
        "actual_max_delay": max(structure["output_arrivals"], default=0),
        "depth_upper_bound_violation_count": 0,
        "output_deadline_violation_count": 0,
    }
    for key, value in expected.items():
        if verification.get(key) != value:
            raise RuntimeError(
                f"untrusted verification metadata differs at {key}: "
                f"{verification.get(key)!r} != {value!r}"
            )


def verify_witness(
    witness_path: Path,
    *,
    fixture: bool = False,
    max_residual_gate: int = MAX_RESIDUAL_GATE_LIMIT,
) -> dict[str, Any]:
    witness_path = witness_path.resolve()
    witness_bytes = witness_path.read_bytes()
    payload = json.loads(witness_bytes.decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("witness root must be an object")
    structure = _validate_structure(
        payload,
        fixture=fixture,
        max_residual_gate=max_residual_gate,
    )

    reduced_values, reduced_targets, reduced_all = _reduced_domain()
    reduced = _replay_report(
        label="correlated-high-domain",
        rows=DOMAIN_ROWS,
        values=reduced_values,
        targets=reduced_targets,
        all_mask=reduced_all,
        structure=structure,
    )
    full_values, full_driven, full_targets, full_all, boundary_mismatch = _full_domain()
    if boundary_mismatch:
        raise RuntimeError(f"fixed shell nC7 identity failed on {boundary_mismatch} rows")
    full = _replay_report(
        label="complete-u8-u8-u1-domain",
        rows=FULL_ROWS,
        values=full_values,
        targets=full_targets,
        all_mask=full_all,
        structure=structure,
        driven=full_driven,
    )
    _verify_metadata(payload, structure)

    report = {
        "schema": "fixed73-high-residual-independent-physical-witness-verification-v2",
        "status": "verified",
        "mode": "fixture" if fixture else "production",
        "competitive_contract": not fixture,
        "witness": {
            "path": _portable(witness_path),
            "sha256": sha256(witness_bytes).hexdigest(),
            "schema": payload["schema"],
            "domain": payload["domain"],
            "output_names": structure["output_names"],
        },
        "fixed_interface": {
            "fixed_low_prefix_gate": FIXED_LOW_PREFIX_GATE,
            "fixed_high_paid_state_gate": FIXED_HIGH_PAID_STATE_GATE,
            "fixed_total_gate": FIXED_TOTAL_GATE,
            "residual_gate_budget": max_residual_gate,
            "complete_gate_budget": FIXED_TOTAL_GATE + max_residual_gate,
            "complete_delay_target": MAX_COMPLETE_DELAY,
            "complete_energy_budget": (
                (FIXED_TOTAL_GATE + max_residual_gate) * MAX_COMPLETE_DELAY
            ),
            "source_names": list(SOURCE_NAMES),
            "source_arrivals": SOURCE_ARRIVALS,
            "nC7_full_domain_mismatch_count": boundary_mismatch,
        },
        "structure": {
            key: value
            for key, value in structure.items()
            if key not in {"network", "output_buses"}
        },
        "network_sha256": sha256(
            json.dumps(
                {
                    "network": structure["network"],
                    "output_buses": structure["output_buses"],
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
        "reduced_replay": reduced,
        "full_replay": full,
        "metadata_recomputed_equal": True,
        "worker": {
            "path": _portable(WORKER),
            "sha256": sha256(WORKER.read_bytes()).hexdigest(),
            "imported_for_verification": False,
            "dependency_sha256": structure["dependency_sha256"],
        },
    }
    return json.loads(json.dumps(report, ensure_ascii=False))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path = _assert_output_path(path)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    if path.read_bytes() != encoded:
        raise RuntimeError("written verification report changed")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Independently replay a fixed73/high-residual physical SAT witness."
    )
    parser.add_argument("witness", type=Path)
    parser.add_argument(
        "--fixture",
        action="store_true",
        help="accept an ordered output subset on the same high paid-source domain",
    )
    parser.add_argument(
        "--max-residual-gate",
        type=int,
        choices=SUPPORTED_RESIDUAL_GATE_LIMITS,
        default=MAX_RESIDUAL_GATE_LIMIT,
        help="accept residual witnesses up to 29 (strict) or 30 (103/5 tie)",
    )
    parser.add_argument("--output", type=Path, help="derived JSON below this research directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = verify_witness(
        args.witness,
        fixture=args.fixture,
        max_residual_gate=args.max_residual_gate,
    )
    if args.output is not None:
        _write_json(args.output, report)
    summary = {
        "status": report["status"],
        "mode": report["mode"],
        "witness": report["witness"],
        "gate": report["structure"]["gate"],
        "output_arrivals": report["structure"]["output_arrivals"],
        "reduced_rows": report["reduced_replay"]["rows"],
        "full_rows": report["full_replay"]["rows"],
        "output": str(args.output.resolve()) if args.output is not None else None,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
