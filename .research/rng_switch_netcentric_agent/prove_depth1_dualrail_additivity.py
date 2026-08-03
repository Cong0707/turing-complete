"""Exact depth-one dual-rail XOR cover and multi-output additivity proof."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Driver:
    kind: str
    left: str
    right: str
    value: int
    driven: int
    cost: int


def variable_table(inputs: int, bit: int) -> int:
    return sum(((case >> bit) & 1) << case for case in range(1 << inputs))


def minimum_cover(inputs: int, left_bit: int, right_bit: int) -> dict[str, object]:
    assignments = 1 << inputs
    full = (1 << assignments) - 1
    raw = [variable_table(inputs, bit) for bit in range(inputs)]
    signals = {
        **{f"x{bit}": value for bit, value in enumerate(raw)},
        **{f"not_x{bit}": full ^ value for bit, value in enumerate(raw)},
    }
    target = raw[left_bit] ^ raw[right_bit]
    drivers: list[Driver] = []
    names = sorted(signals)
    for left in names:
        a = signals[left]
        drivers.append(Driver("NOT", left, left, full ^ a, full, 1))
        for right in names:
            b = signals[right]
            if left <= right:
                drivers.extend(
                    (
                        Driver("AND", left, right, a & b, full, 1),
                        Driver("OR", left, right, a | b, full, 1),
                        Driver("NAND", left, right, full ^ (a & b), full, 1),
                        Driver("NOR", left, right, full ^ (a | b), full, 1),
                    )
                )
            # XOR is excluded: its reviewed delay is two, outside this proof.
            drivers.append(Driver("SWITCH", left, right, a & b, a, 2))

    # A driver on a target output net must agree with the target whenever it
    # is active.  Deduplicate equivalent terminals at minimum cost.
    compatible: dict[tuple[int, int], Driver] = {}
    for driver in drivers:
        if driver.driven & (driver.value ^ target):
            continue
        key = (driver.value, driver.driven)
        previous = compatible.get(key)
        if previous is None or (driver.cost, driver.kind, driver.left, driver.right) < (
            previous.cost,
            previous.kind,
            previous.left,
            previous.right,
        ):
            compatible[key] = driver
    candidates = tuple(compatible.values())

    optimum = None
    witness: tuple[Driver, ...] | None = None
    for count in range(1, len(candidates) + 1):
        for selected in combinations(candidates, count):
            cost = sum(driver.cost for driver in selected)
            if optimum is not None and cost >= optimum:
                continue
            ones = zeros = 0
            for driver in selected:
                ones |= driver.value
                zeros |= driver.driven & (full ^ driver.value)
            if ones & zeros or ones != target:
                continue
            optimum = cost
            witness = selected
        if optimum is not None and count * 1 >= optimum:
            break
    if optimum is None or witness is None:
        raise AssertionError("dual-rail XOR unexpectedly uncovered")
    return {
        "target": f"x{left_bit} XOR x{right_bit}",
        "target_table": f"{target:0{assignments // 4}x}",
        "compatible_distinct_driver_functions": len(candidates),
        "minimum_gate": optimum,
        "minimum_terminal_count": len(witness),
        "witness": [
            {
                "kind": driver.kind,
                "enable_or_left": driver.left,
                "data_or_right": driver.right,
                "value": f"{driver.value:0{assignments // 4}x}",
                "driven": f"{driver.driven:0{assignments // 4}x}",
                "cost": driver.cost,
            }
            for driver in witness
        ],
    }


def main() -> None:
    pair_results = [minimum_cover(3, left, right) for left, right in ((0, 1), (0, 2), (1, 2))]
    if any(result["minimum_gate"] != 4 or result["minimum_terminal_count"] != 2 for result in pair_results):
        raise AssertionError("depth-one XOR lower bound changed")
    payload = {
        "schema": 1,
        "scope": "depth-one final layer with free positive/negative operand rails",
        "output_zero_may_be_z": True,
        "library": {
            "NOT/AND/OR/NAND/NOR": [1, 1],
            "SWITCH": [2, 1],
            "XOR": [3, 2],
        },
        "pair_isomorphism_checks": pair_results,
        "additivity_argument": [
            "At delay one, a paid gate output cannot feed another paid gate.",
            "Every paid output terminal therefore belongs directly to at most one physical output net.",
            "Different XOR truth tables cannot be the same physical net.",
            "Shared input fanout is free, but paid output terminals cannot be copied across isolated nets.",
            "Therefore the four-gate single-output minima add over distinct outputs.",
        ],
        "actual_468_final_layer": {
            "distinct_xor_outputs": 34,
            "minimum_gate": 34 * 4,
            "implemented_gate": 136,
            "reduction_possible_inside_fixed_depth1_dualrail_layer": False,
        },
    }
    path = HERE / "depth1-dualrail-additivity.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["actual_468_final_layer"], ensure_ascii=False))


if __name__ == "__main__":
    main()
