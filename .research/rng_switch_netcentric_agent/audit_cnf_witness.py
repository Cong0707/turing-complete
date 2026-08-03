"""Physical-net audit for compact bit-blasted joint-parity witnesses.

The source CNF model permits an output terminal to appear in several directed
BUS subsets.  This auditor unions every such connection before replay, making
any hidden bus alias, feedback edge, conflict or output mutation explicit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from netcentric import Driver, UnionFind, _resolve


COST = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 3, "SWITCH": 2}
DELAY = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 2, "SWITCH": 1}


def variable_table(inputs: int, bit: int) -> int:
    return sum(((case >> bit) & 1) << case for case in range(1 << inputs))


def sources_for(payload: dict[str, object]) -> tuple[list[str], list[int]]:
    inputs = int(payload["inputs"])
    assignments = 1 << inputs
    full = (1 << assignments) - 1
    raw = [variable_table(inputs, bit) for bit in range(inputs)]
    mode = str(payload["source_mode"])
    if mode == "pair-dual-tails":
        names = ["x0", "x1"]
        values = [raw[0], raw[1]]
        for bit in range(2, inputs):
            names.extend((f"x{bit}", f"not_x{bit}"))
            values.extend((raw[bit], full ^ raw[bit]))
    elif mode == "all-dual":
        names = []
        values = []
        for bit in range(inputs):
            names.extend((f"x{bit}", f"not_x{bit}"))
            values.extend((raw[bit], full ^ raw[bit]))
    else:
        raise ValueError(mode)
    names.extend(("const0", "const1"))
    values.extend((0, full))
    return names, values


def audit(payload: dict[str, object]) -> dict[str, object]:
    if payload.get("status") != "sat":
        raise ValueError("payload is not SAT")
    network = payload.get("network")
    output_buses = payload.get("output_buses")
    if not isinstance(network, list) or not isinstance(output_buses, list):
        raise ValueError("missing compact network/output_buses")
    inputs = int(payload["inputs"])
    assignments = 1 << inputs
    full = (1 << assignments) - 1
    width = max(1, assignments // 4)
    names, source_values = sources_for(payload)
    source_count = len(source_values)
    terminal_count = source_count + len(network)
    uf = UnionFind(range(terminal_count))
    intended: list[tuple[str, frozenset[int]]] = []

    def connect(context: str, raw_members: object) -> None:
        members = frozenset(int(member) for member in raw_members)
        if not members:
            # NOT right buses are intentionally empty and have no wire.
            intended.append((context, members))
            return
        first = min(members)
        for member in members:
            uf.union(first, member)
        intended.append((context, members))

    for gate in network:
        connect(f"gate:{gate['slot']}:left", gate["left_bus"])
        connect(f"gate:{gate['slot']}:right", gate["right_bus"])
    for output, members in enumerate(output_buses):
        connect(f"output:{output}", members)

    alias_divergences = []
    for pos, (left_context, left) in enumerate(intended):
        if not left:
            continue
        for right_context, right in intended[pos + 1 :]:
            overlap = left & right
            if overlap and left != right:
                alias_divergences.append(
                    {
                        "left": left_context,
                        "left_drivers": sorted(left),
                        "right": right_context,
                        "right_drivers": sorted(right),
                        "shared_drivers": sorted(overlap),
                    }
                )

    groups = uf.groups()
    root = {terminal: uf.find(terminal) for terminal in range(terminal_count)}
    drivers = {
        terminal: Driver(value, full, 0)
        for terminal, value in enumerate(source_values)
    }
    dependency_errors = []
    conflicts = []
    gate_records = []

    def read(raw_members: object, consumer: object) -> tuple[int, int, int, tuple[int, ...]]:
        members0 = tuple(int(member) for member in raw_members)
        if not members0:
            return 0, 0, 0, ()
        members = groups[root[members0[0]]]
        unavailable = [member for member in members if member not in drivers]
        if unavailable:
            dependency_errors.append(
                {"consumer": consumer, "physical_drivers": list(members), "unavailable": unavailable}
            )
            return 0, 0, 0, members
        value, driven, conflict, depth = _resolve((drivers[member] for member in members), full)
        if conflict:
            conflicts.append(
                {"consumer": consumer, "physical_drivers": list(members), "mask": f"{conflict:0{width}x}"}
            )
        return value, driven, depth, members

    actual_cost = 0
    for gate in network:
        terminal = int(gate["source"])
        kind = str(gate["kind"])
        left, _left_driven, left_depth, left_members = read(gate["left_bus"], terminal)
        right, _right_driven, right_depth, right_members = read(gate["right_bus"], terminal)
        maximum = max(left_depth, right_depth)
        if kind == "NOT":
            value, driven, depth = full ^ left, full, left_depth + 1
        elif kind == "AND":
            value, driven, depth = left & right, full, maximum + 1
        elif kind == "OR":
            value, driven, depth = left | right, full, maximum + 1
        elif kind == "NAND":
            value, driven, depth = full ^ (left & right), full, maximum + 1
        elif kind == "NOR":
            value, driven, depth = full ^ (left | right), full, maximum + 1
        elif kind == "XOR":
            value, driven, depth = left ^ right, full, maximum + 2
        elif kind == "SWITCH":
            value, driven, depth = left & right, left, maximum + 1
        else:
            raise ValueError(kind)
        drivers[terminal] = Driver(value, driven, depth)
        actual_cost += COST[kind]
        gate_records.append(
            {
                "terminal": terminal,
                "kind": kind,
                "left_physical_drivers": list(left_members),
                "right_physical_drivers": list(right_members),
                "value": f"{value:0{width}x}",
                "driven": f"{driven:0{width}x}",
                "depth": depth,
            }
        )

    for net, members in groups.items():
        if any(member not in drivers for member in members):
            continue
        _value, _driven, conflict, _depth = _resolve((drivers[member] for member in members), full)
        if conflict:
            conflicts.append(
                {"consumer": "global", "physical_drivers": list(members), "mask": f"{conflict:0{width}x}"}
            )

    targets = [int(value, 16) for value in payload["target_truth_tables_hex"]]
    output_records = []
    for output, (members0, target) in enumerate(zip(output_buses, targets, strict=True)):
        value, driven, depth, members = read(members0, f"output:{output}")
        _value2, _driven2, conflict, _depth2 = _resolve((drivers[member] for member in members), full)
        output_records.append(
            {
                "output": output,
                "physical_drivers": list(members),
                "value": f"{value:0{width}x}",
                "driven": f"{driven:0{width}x}",
                "conflict": f"{conflict:0{width}x}",
                "depth": depth,
                "target": f"{target:0{width}x}",
                "matches": not conflict and value == target,
            }
        )
    unique_conflicts = {
        (str(item["consumer"]), tuple(item["physical_drivers"]), item["mask"]): item
        for item in conflicts
    }
    valid = (
        not alias_divergences
        and not dependency_errors
        and not unique_conflicts
        and actual_cost == int(payload["actual_gate"])
        and all(output["matches"] for output in output_records)
        and max(output["depth"] for output in output_records) <= int(payload["max_delay"])
    )
    return {
        "schema": 1,
        "model": "union-find physical replay of compact CNF witness",
        "valid": valid,
        "source_names": names,
        "all_truth_assignments": assignments,
        "cost": actual_cost,
        "depth": max(output["depth"] for output in output_records),
        "alias_divergence_count": len(alias_divergences),
        "alias_divergences": alias_divergences,
        "dependency_errors": dependency_errors,
        "conflicts": list(unique_conflicts.values()),
        "gates": gate_records,
        "outputs": output_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = audit(payload)
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
