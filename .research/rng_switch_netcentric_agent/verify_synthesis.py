"""Independent concrete replay for net-centric synthesis witnesses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


COST = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 3, "SWITCH": 2}


def resolve(
    members: Iterable[int], drivers: dict[int, tuple[int, int, int]], full: int
) -> tuple[int, int, int, int]:
    ones = zeros = depth = 0
    for terminal in members:
        value, driven, arrival = drivers[terminal]
        ones |= value
        zeros |= driven & (full ^ value)
        depth = max(depth, arrival)
    return ones, ones | zeros, ones & zeros, depth


def verify_result(result: dict[str, object]) -> dict[str, object]:
    if result.get("status") != "sat":
        raise ValueError("result is not SAT")
    network = result["network"]
    input_count = int(result["input_count"])
    assignments = 1 << input_count
    full = (1 << assignments) - 1
    width = max(1, assignments // 4)
    nets = {int(item["net"]): tuple(int(driver) for driver in item["drivers"]) for item in network["nets"]}
    terminal_net: dict[int, int] = {}
    for net, members in nets.items():
        for terminal in members:
            if terminal in terminal_net:
                raise AssertionError(f"terminal {terminal} appears on two nets")
            terminal_net[terminal] = net

    drivers: dict[int, tuple[int, int, int]] = {}
    mismatches = []
    dependency_errors = []
    conflicts = []
    for source in network["sources"]:
        terminal = int(source["terminal"])
        drivers[terminal] = (int(source["value"], 16), int(source["driven"], 16), int(source["depth"]))
        if terminal_net[terminal] != int(source["net"]):
            mismatches.append({"source": terminal, "reason": "net mismatch"})

    def read(net: int, consumer: object) -> tuple[int, int, int]:
        unavailable = [terminal for terminal in nets[net] if terminal not in drivers]
        if unavailable:
            dependency_errors.append({"consumer": consumer, "net": net, "unavailable": unavailable})
            return 0, 0, 0
        value, driven, conflict, depth = resolve(nets[net], drivers, full)
        if conflict:
            conflicts.append({"consumer": consumer, "net": net, "mask": f"{conflict:0{width}x}"})
        return value, driven, depth

    replay_cost = 0
    for gate in network["gates"]:
        terminal = int(gate["terminal"])
        kind = str(gate["kind"])
        left, _left_driven, left_depth = read(int(gate["left_net"]), terminal)
        right, _right_driven, right_depth = read(int(gate["right_net"]), terminal)
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
            raise AssertionError(kind)
        expected = (int(gate["value"], 16), int(gate["driven"], 16), int(gate["depth"]))
        if (value, driven, depth) != expected:
            mismatches.append(
                {
                    "gate": terminal,
                    "expected": [f"{expected[0]:0{width}x}", f"{expected[1]:0{width}x}", expected[2]],
                    "actual": [f"{value:0{width}x}", f"{driven:0{width}x}", depth],
                }
            )
        drivers[terminal] = (value, driven, depth)
        replay_cost += COST[kind]

    for net, members in nets.items():
        if any(terminal not in drivers for terminal in members):
            dependency_errors.append({"consumer": "global", "net": net, "unavailable": list(members)})
            continue
        _value, _driven, conflict, _depth = resolve(members, drivers, full)
        if conflict:
            conflicts.append({"consumer": "global", "net": net, "mask": f"{conflict:0{width}x}"})

    output_results = []
    for output in network["outputs"]:
        net = int(output["net"])
        value, driven, conflict, depth = resolve(nets[net], drivers, full)
        target = int(output["target"], 16)
        matches = not conflict and value == target and (not output["exact_drive"] or driven == full)
        output_results.append(
            {
                "net": net,
                "value": f"{value:0{width}x}",
                "driven": f"{driven:0{width}x}",
                "conflict": f"{conflict:0{width}x}",
                "depth": depth,
                "target": f"{target:0{width}x}",
                "matches": matches,
            }
        )
    unique_conflicts = {
        (str(item["consumer"]), item["net"], item["mask"]): item for item in conflicts
    }
    valid = (
        not mismatches
        and not dependency_errors
        and not unique_conflicts
        and all(output["matches"] for output in output_results)
        and replay_cost == int(network["cost"])
        and max(output["depth"] for output in output_results) == int(network["depth"])
    )
    return {
        "valid": valid,
        "all_truth_assignments": assignments,
        "cost": replay_cost,
        "depth": max(output["depth"] for output in output_results),
        "mismatches": mismatches,
        "dependency_errors": dependency_errors,
        "conflicts": list(unique_conflicts.values()),
        "outputs": output_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    verifications = []
    for index, result in enumerate(payload.get("results", [payload])):
        if result.get("status") == "sat":
            verifications.append({"result_index": index, **verify_result(result)})
    output = {"schema": 1, "input": str(args.input), "verifications": verifications}
    encoded = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if verifications and all(item["valid"] for item in verifications) else 1


if __name__ == "__main__":
    raise SystemExit(main())
