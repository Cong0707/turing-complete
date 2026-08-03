"""Strict physical-net replay for relaxed tri-state DAG certificates.

The old superoptimizer represents ``BUS(a, b)`` as a zero-cost functional DAG
node.  A real wire has no output terminal: connecting the same driver terminal
to two buses electrically unions both buses.  This module first collapses all
wire connections with union-find, then replays values, Z masks, conflicts,
combinational dependencies, cost and delay on the resulting physical nets.

This is an offline verifier.  It does not read or write a game save.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
from pathlib import Path
from typing import Iterable


PAID_COST = {
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 3,
    "SWITCH": 2,
}
GATE_DELAY = {
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 2,
    "SWITCH": 1,
}


class UnionFind:
    def __init__(self, items: Iterable[int]) -> None:
        self.parent = {item: item for item in items}
        self.rank = {item: 0 for item in items}

    def find(self, item: int) -> int:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: int, right: int) -> None:
        a, b = self.find(left), self.find(right)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1

    def groups(self) -> dict[int, tuple[int, ...]]:
        groups: dict[int, list[int]] = {}
        for item in self.parent:
            groups.setdefault(self.find(item), []).append(item)
        return {root: tuple(sorted(items)) for root, items in groups.items()}


@dataclass(frozen=True)
class Driver:
    value: int
    driven: int
    depth: int


def _hex(value: int, width: int) -> str:
    return f"{value:0{max(1, (width + 3) // 4)}x}"


def _resolve(drivers: Iterable[Driver], full: int) -> tuple[int, int, int, int]:
    ones = 0
    zeros = 0
    depth = 0
    count = 0
    for driver in drivers:
        ones |= driver.value
        zeros |= driver.driven & (full ^ driver.value)
        depth = max(depth, driver.depth)
        count += 1
    return ones, ones | zeros, ones & zeros, depth if count else 0


def audit_payload(payload: dict[str, object]) -> dict[str, object]:
    network = payload.get("network")
    if not isinstance(network, dict):
        raise ValueError("payload has no serialized network")
    sources = network.get("sources")
    gates = network.get("gates")
    outputs = network.get("outputs")
    if not isinstance(sources, list) or not isinstance(gates, list) or not isinstance(outputs, list):
        raise ValueError("network sources/gates/outputs must be lists")

    source_by_index = {int(source["index"]): source for source in sources}
    gate_by_index = {int(gate["index"]): gate for gate in gates}
    bus_indices = {
        index for index, gate in gate_by_index.items() if str(gate["kind"]).upper() == "BUS"
    }
    terminal_indices = tuple(sorted(set(source_by_index) | (set(gate_by_index) - bus_indices)))
    if not terminal_indices:
        raise ValueError("network has no physical driver terminal")

    verification = payload.get("verification")
    if isinstance(verification, dict) and isinstance(verification.get("all_truth_assignments"), int):
        width = int(verification["all_truth_assignments"])
    else:
        digits = max(len(str(source["driven"])) for source in sources)
        width = 4 * digits
    full = (1 << width) - 1

    leaf_cache: dict[int, frozenset[int]] = {}
    visiting: set[int] = set()

    def leaves(index: int) -> frozenset[int]:
        if index in leaf_cache:
            return leaf_cache[index]
        if index in visiting:
            raise ValueError(f"cyclic BUS expression at {index}")
        if index in terminal_indices:
            result = frozenset((index,))
        elif index in bus_indices:
            visiting.add(index)
            gate = gate_by_index[index]
            result = leaves(int(gate["left"])) | leaves(int(gate["right"]))
            visiting.remove(index)
        else:
            raise ValueError(f"reference to missing node {index}")
        leaf_cache[index] = result
        return result

    uf = UnionFind(terminal_indices)
    intended_nets: list[tuple[str, frozenset[int]]] = []

    def connect(context: str, members: frozenset[int]) -> None:
        if not members:
            raise ValueError(f"empty physical net at {context}")
        first = min(members)
        for member in members:
            uf.union(first, member)
        intended_nets.append((context, members))

    for index in sorted(bus_indices):
        gate = gate_by_index[index]
        connect(f"BUS:{index}", leaves(int(gate["left"])) | leaves(int(gate["right"])))
    for output_index, raw_drivers in enumerate(outputs):
        if not isinstance(raw_drivers, list) or not raw_drivers:
            raise ValueError(f"output {output_index} has no drivers")
        members = frozenset().union(*(leaves(int(index)) for index in raw_drivers))
        connect(f"OUTPUT:{output_index}", members)
    for index, gate in sorted(gate_by_index.items()):
        if index in bus_indices:
            continue
        left = leaves(int(gate["left"]))
        intended_nets.append((f"GATE:{index}:left", left))
        kind = str(gate["kind"]).upper()
        if kind != "NOT":
            intended_nets.append((f"GATE:{index}:right", leaves(int(gate["right"]))))

    alias_divergences = []
    for pos, (left_context, left_members) in enumerate(intended_nets):
        for right_context, right_members in intended_nets[pos + 1 :]:
            overlap = left_members & right_members
            if overlap and left_members != right_members:
                alias_divergences.append(
                    {
                        "left": left_context,
                        "left_drivers": sorted(left_members),
                        "right": right_context,
                        "right_drivers": sorted(right_members),
                        "shared_drivers": sorted(overlap),
                    }
                )

    groups = uf.groups()
    group_for_terminal = {terminal: uf.find(terminal) for terminal in terminal_indices}
    drivers: dict[int, Driver] = {}
    relaxed_mismatches = []
    dependency_errors = []
    conflict_records = []

    for index, source in source_by_index.items():
        value = int(str(source["value"]), 16)
        driven = int(str(source["driven"]), 16)
        if value & ~driven:
            raise ValueError(f"source {index} is one while Z")
        drivers[index] = Driver(value, driven, int(source.get("depth", 0)))

    def resolve_reference(reference: int, consumer: int) -> tuple[int, int, int]:
        members = groups[group_for_terminal[min(leaves(reference))]]
        unavailable = [member for member in members if member not in drivers]
        if unavailable:
            dependency_errors.append(
                {
                    "consumer": consumer,
                    "reference": reference,
                    "future_or_self_drivers": unavailable,
                }
            )
            return 0, 0, 0
        value, driven, conflict, depth = _resolve((drivers[item] for item in members), full)
        if conflict:
            conflict_records.append(
                {
                    "consumer": consumer,
                    "reference": reference,
                    "drivers": list(members),
                    "mask": _hex(conflict, width),
                }
            )
        return value, driven, depth

    for index, gate in sorted(gate_by_index.items()):
        kind = str(gate["kind"]).upper()
        if kind == "BUS":
            continue
        if kind not in PAID_COST:
            raise ValueError(f"unsupported gate kind {kind}")
        lv, _ld, ldepth = resolve_reference(int(gate["left"]), index)
        if kind == "NOT":
            rv, rdepth = lv, ldepth
        else:
            rv, _rd, rdepth = resolve_reference(int(gate["right"]), index)
        maximum = max(ldepth, rdepth)
        if kind == "NOT":
            value, driven, depth = full ^ lv, full, ldepth + 1
        elif kind == "AND":
            value, driven, depth = lv & rv, full, maximum + 1
        elif kind == "OR":
            value, driven, depth = lv | rv, full, maximum + 1
        elif kind == "NAND":
            value, driven, depth = full ^ (lv & rv), full, maximum + 1
        elif kind == "NOR":
            value, driven, depth = full ^ (lv | rv), full, maximum + 1
        elif kind == "XOR":
            value, driven, depth = lv ^ rv, full, maximum + 2
        else:
            # Current runtime: data Z contributes numeric zero; only the
            # enable numeric plane controls output Z.
            value, driven, depth = lv & rv, lv, maximum + 1
        drivers[index] = Driver(value, driven, depth)
        expected = (
            int(str(gate["value"]), 16) if "value" in gate else value,
            int(str(gate["driven"]), 16) if "driven" in gate else driven,
            int(gate.get("depth", depth)),
        )
        if (value, driven, depth) != expected:
            relaxed_mismatches.append(
                {
                    "gate": index,
                    "kind": kind,
                    "relaxed": {
                        "value": _hex(expected[0], width),
                        "driven": _hex(expected[1], width),
                        "depth": expected[2],
                    },
                    "physical": {
                        "value": _hex(value, width),
                        "driven": _hex(driven, width),
                        "depth": depth,
                    },
                }
            )

    physical_nets = []
    for root, members in sorted(groups.items(), key=lambda item: min(item[1])):
        if any(member not in drivers for member in members):
            continue
        value, driven, conflict, depth = _resolve((drivers[item] for item in members), full)
        if conflict:
            conflict_records.append(
                {
                    "consumer": "global",
                    "reference": root,
                    "drivers": list(members),
                    "mask": _hex(conflict, width),
                }
            )
        physical_nets.append(
            {
                "drivers": list(members),
                "value": _hex(value, width),
                "driven": _hex(driven, width),
                "depth": depth,
                "conflict": _hex(conflict, width),
            }
        )

    targets_raw = payload.get("targets", [])
    require_driven = payload.get("require_driven", [True] * len(outputs))
    output_results = []
    output_ok = True
    for output_index, raw_drivers in enumerate(outputs):
        output_leaves = frozenset().union(*(leaves(int(index)) for index in raw_drivers))
        members = groups[group_for_terminal[min(output_leaves)]]
        if any(member not in drivers for member in members):
            value = driven = conflict = depth = 0
        else:
            value, driven, conflict, depth = _resolve((drivers[item] for item in members), full)
        target = int(str(targets_raw[output_index]), 16) if output_index < len(targets_raw) else None
        exact = bool(require_driven[output_index]) if output_index < len(require_driven) else True
        matches = not conflict and (target is None or value == target) and (not exact or driven == full)
        output_ok &= matches
        output_results.append(
            {
                "output": output_index,
                "physical_drivers": list(members),
                "value": _hex(value, width),
                "driven": _hex(driven, width),
                "conflict": _hex(conflict, width),
                "depth": depth,
                "target": _hex(target, width) if target is not None else None,
                "matches": matches,
            }
        )

    unique_conflicts = {
        (str(record["consumer"]), int(record["reference"]), str(record["mask"])):
        record for record in conflict_records
    }
    physical_cost = sum(PAID_COST[str(gate["kind"]).upper()] for gate in gates if str(gate["kind"]).upper() != "BUS")
    valid = not dependency_errors and not unique_conflicts and not relaxed_mismatches and output_ok
    return {
        "schema": 1,
        "model": "net-centric union-find physical replay",
        "valid": valid,
        "width": width,
        "physical_cost": physical_cost,
        "physical_depth": max((result["depth"] for result in output_results), default=0),
        "alias_divergence_count": len(alias_divergences),
        "alias_divergences": alias_divergences,
        "dependency_error_count": len(dependency_errors),
        "dependency_errors": dependency_errors,
        "conflict_count": len(unique_conflicts),
        "conflicts": list(unique_conflicts.values()),
        "relaxed_mismatch_count": len(relaxed_mismatches),
        "relaxed_mismatches": relaxed_mismatches,
        "outputs_match": output_ok,
        "outputs": output_results,
        "physical_nets": physical_nets,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = audit_payload(payload)
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
