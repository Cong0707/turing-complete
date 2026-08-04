"""Independently replay the 17/2 FullAdder physical SAT witness."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
WITNESS = HERE / "truth_tuple_cases" / "fa_d2_g17_p11_n2_s6_x0.json"
OUTPUT = HERE / "full_adder_d2_g17_independent_audit.json"
EXPECTED_WITNESS_SHA256 = "c9cfc91124202330d00175289022177ebde56280897034c020823d707ed4698d"
FULL = 0xFF
COST = {
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 3,
    "SWITCH": 2,
    "NORMALIZE": 0,
}
DELAY = {
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 2,
    "SWITCH": 1,
    "NORMALIZE": 0,
}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def resolve_bus(bus: list[int], states: list[tuple[int, int]]) -> tuple[int, int, int]:
    ones = 0
    zeros = 0
    for source in bus:
        value, driven = states[source]
        ones |= value & driven
        zeros |= (~value & FULL) & driven
    conflict = ones & zeros
    return ones, ones | zeros, conflict


def ordinary(kind: str, left: int, right: int) -> int:
    if kind == "NOT":
        return ~left & FULL
    if kind == "AND":
        return left & right
    if kind == "OR":
        return left | right
    if kind == "NAND":
        return ~(left & right) & FULL
    if kind == "NOR":
        return ~(left | right) & FULL
    if kind == "XOR":
        return left ^ right
    raise RuntimeError(f"unsupported ordinary kind {kind}")


def main() -> None:
    require(digest(WITNESS) == EXPECTED_WITNESS_SHA256, "witness SHA drift")
    payload = json.loads(WITNESS.read_text(encoding="utf-8"))
    expected_fields = {
        "schema": "tc-arbitrary-truth-tuple-exact-physical-v1",
        "status": "sat",
        "input_count": 3,
        "target_truth_tables_hex": ["96", "e8"],
        "output_max_delays": [2, 2],
        "gate_bound": 17,
        "max_delay": 2,
        "components": 13,
        "exact_normalizers": 2,
        "exact_switches": 6,
        "exact_xors": 0,
        "allow_z_false": False,
        "physical_nets": True,
        "actual_gate": 17,
    }
    for key, value in expected_fields.items():
        require(payload.get(key) == value, f"{key} drift")

    states: list[tuple[int, int]] = [
        (0xAA, FULL),
        (0xCC, FULL),
        (0xF0, FULL),
        (0x00, FULL),
        (0xFF, FULL),
    ]
    arrivals = [0] * len(states)
    buses: list[tuple[str, tuple[int, ...]]] = []
    node_rows = []
    weighted_cost = 0
    normalizer_count = 0
    switch_count = 0
    xor_count = 0
    for slot, item in enumerate(payload["network"]):
        require(item["slot"] == slot, f"slot ordering drift at {slot}")
        require(item["source"] == len(states), f"source ordering drift at {slot}")
        kind = str(item["kind"])
        left_bus = [int(source) for source in item["left_bus"]]
        right_bus = [int(source) for source in item["right_bus"]]
        require(left_bus and max(left_bus) < len(states), f"bad left predecessor at {slot}")
        require(not right_bus or max(right_bus) < len(states), f"bad right predecessor at {slot}")
        buses.append((f"slot:{slot}:left", tuple(sorted(left_bus))))
        if right_bus:
            buses.append((f"slot:{slot}:right", tuple(sorted(right_bus))))
        left_value, left_driven, left_conflict = resolve_bus(left_bus, states)
        require(left_conflict == 0, f"left BUS conflict at slot {slot}")
        if right_bus:
            right_value, right_driven, right_conflict = resolve_bus(right_bus, states)
            require(right_conflict == 0, f"right BUS conflict at slot {slot}")
        else:
            right_value, right_driven = 0, 0

        if kind == "SWITCH":
            value = left_value & right_value
            driven = left_value
            switch_count += 1
        elif kind == "NORMALIZE":
            require(
                all(payload["network"][source - 5]["kind"] == "SWITCH" for source in left_bus),
                f"normalizer form violation at slot {slot}",
            )
            value = left_value
            driven = FULL
            normalizer_count += 1
        else:
            value = ordinary(kind, left_value, right_value)
            driven = FULL
            if kind == "XOR":
                xor_count += 1
        predecessor_arrival = max((arrivals[source] for source in left_bus + right_bus), default=0)
        arrival = predecessor_arrival + DELAY[kind]
        require(arrival <= int(item["depth_upper_bound"]), f"CNF arrival drift at slot {slot}")
        require(item["cost"] == COST[kind] and item["delay"] == DELAY[kind], f"library drift at {slot}")
        states.append((value, driven))
        arrivals.append(arrival)
        weighted_cost += COST[kind]
        node_rows.append(
            {
                "slot": slot,
                "source": item["source"],
                "kind": kind,
                "value_hex": f"{value:02x}",
                "driven_hex": f"{driven:02x}",
                "arrival": arrival,
            }
        )

    output_values = []
    output_arrivals = []
    for index, bus in enumerate(payload["output_buses"]):
        bus = [int(source) for source in bus]
        buses.append((f"output:{index}", tuple(sorted(bus))))
        value, driven, conflict = resolve_bus(bus, states)
        require(conflict == 0, f"output {index} conflict")
        require(driven == FULL, f"output {index} is not fully driven")
        output_values.append(value)
        output_arrivals.append(max(arrivals[source] for source in bus))

    require(output_values == [0x96, 0xE8], "truth tuple mismatch")
    require(output_arrivals == [2, 2], "output arrival mismatch")
    require(weighted_cost == 17, "weighted cost mismatch")
    require((normalizer_count, switch_count, xor_count) == (2, 6, 0), "kind counts drift")

    unique_sets = sorted({drivers for _label, drivers in buses})
    source_owners: dict[int, set[tuple[int, ...]]] = {}
    for _label, drivers in buses:
        for source in drivers:
            source_owners.setdefault(source, set()).add(drivers)
    partition_violations = {
        source: sorted(map(list, owners))
        for source, owners in source_owners.items()
        if len(owners) > 1
    }
    require(not partition_violations, "physical driver-set partition violation")

    live_sources = set(source for bus in payload["output_buses"] for source in bus)
    pending = list(live_sources)
    while pending:
        source = pending.pop()
        if source < 5:
            continue
        item = payload["network"][source - 5]
        for predecessor in item["left_bus"] + item["right_bus"]:
            if predecessor not in live_sources:
                live_sources.add(predecessor)
                pending.append(predecessor)
    dead_slots = [slot for slot in range(len(payload["network"])) if slot + 5 not in live_sources]
    require(not dead_slots, "dead paid/normalizer components present")

    owners = payload["physical_owners"]
    manifest_sets = {
        tuple(owner["drivers"]): owner["owner"] for owner in owners["owners"]
    }
    require(set(manifest_sets) == set(unique_sets), "owner driver sets drift")
    for reference in owners["references"]:
        drivers = tuple(reference["drivers"])
        require(manifest_sets[drivers] == reference["owner"], "owner reference drift")

    audit = {
        "schema": "full-adder-d2-g17-independent-physical-audit-v1",
        "status": "verified",
        "scope": "offline decoded-witness replay; no SAT/CNF helper imported",
        "witness": {"path": str(WITNESS), "sha256": digest(WITNESS)},
        "score": {"gate": weighted_cost, "delay": max(output_arrivals)},
        "target_truth_tables_hex": [f"{value:02x}" for value in output_values],
        "output_arrivals": output_arrivals,
        "kind_counts": {
            "ordinary": len(payload["network"]) - normalizer_count - switch_count,
            "switch": switch_count,
            "normalizer": normalizer_count,
            "xor": xor_count,
        },
        "verification": {
            "assignments": 8,
            "output_checks": 16,
            "mismatch_count": 0,
            "conflict_count": 0,
            "undriven_output_count": 0,
            "physical_net_partition_violation_count": 0,
            "dead_component_count": 0,
            "normalizer_normal_form_violation_count": 0,
        },
        "physical_owners": {
            "driver_set_count": len(unique_sets),
            "sum_partial_driver_owner": owners["components"][-1]["normalizes_bus_owner"],
            "carry_output_owner": owners["output_owners"][1],
            "sum_output_owner": owners["output_owners"][0],
            "maker_splitter_owners": [
                component["maker_splitter_physical_owner"]
                for component in owners["components"]
                if component["kind"] == "NORMALIZE"
            ],
        },
        "nodes": node_rows,
        "auditor": {
            "path": str(Path(__file__).resolve()),
            "sha256": digest(Path(__file__).resolve()),
        },
    }
    encoded = (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    OUTPUT.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": audit["status"],
                "output": str(OUTPUT),
                "sha256": sha256(encoded).hexdigest(),
                "score": audit["score"],
                "verification": audit["verification"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
