"""Reproduce the lower bound for the fixed 468/8/67 Switch compressor.

The proof is deliberately scoped to the reviewed fixed two-layer 61-XOR DAG
and its explicit dual-rail/two-Switch implementation family.  It is not a
global lower bound for arbitrary tristate circuits or state encodings.
"""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab import rng_encoded_asic as base  # noqa: E402


HERE = Path(__file__).resolve().parent
PAIR_COVER_PROOF = ROOT / ".research/rng_cost387/agent_paircover/result.json"
PHASE_PROOF = ROOT / ".research/rng_switch_algebra/phase_one_gate_exhaustive.json"
OUTPUT = HERE / "restricted-lower-bound.json"


def _binary(op: str, left: int, right: int, mask: int) -> int:
    if op == "and":
        return left & right
    if op == "nand":
        return mask ^ (left & right)
    if op == "or":
        return left | right
    if op == "nor":
        return mask ^ (left | right)
    raise ValueError(op)


def minimum_dual_rail_cost() -> dict[str, object]:
    """Exhaust weighted Boolean DAGs producing XOR and XNOR by depth two."""

    # Truth-table bit order is 00, 01, 10, 11.
    mask = 0b1111
    a = 0b1100
    b = 0b1010
    xor = a ^ b
    xnor = mask ^ xor

    # A state maps every available truth table to its minimum arrival depth.
    # Ordinary gates cost 1/delay 1.  Native XOR costs 3/delay 2.
    states: dict[tuple[tuple[int, int], ...], tuple[int, tuple[str, ...]]] = {
        tuple(sorted(((a, 0), (b, 0)))): (0, ())
    }
    witness = None
    for budget in range(5):
        frontier = [
            (signature, trace)
            for signature, (cost, trace) in states.items()
            if cost == budget
        ]
        for signature, trace in frontier:
            depths = dict(signature)
            if xor in depths and xnor in depths:
                witness = (budget, trace)
                break
            signals = tuple(depths)
            candidates: list[tuple[int, int, str, int]] = []
            for source in signals:
                candidates.append(
                    (mask ^ source, depths[source] + 1, f"NOT({source:04b})", 1)
                )
            for left in signals:
                for right in signals:
                    for operation in ("and", "nand", "or", "nor"):
                        candidates.append(
                            (
                                _binary(operation, left, right, mask),
                                max(depths[left], depths[right]) + 1,
                                f"{operation.upper()}({left:04b},{right:04b})",
                                1,
                            )
                        )
                    candidates.append(
                        (
                            left ^ right,
                            max(depths[left], depths[right]) + 2,
                            f"XOR({left:04b},{right:04b})",
                            3,
                        )
                    )
            for table, depth, text, cost in candidates:
                if depth > 2 or budget + cost > 4:
                    continue
                updated = dict(depths)
                if table in updated and updated[table] <= depth:
                    continue
                updated[table] = depth
                new_signature = tuple(sorted(updated.items()))
                previous = states.get(new_signature)
                new_value = (budget + cost, (*trace, text))
                if previous is None or new_value < previous:
                    states[new_signature] = new_value
        if witness is not None:
            break

    if witness is None:
        raise AssertionError("dual-rail synthesis did not find the known cost-four cell")
    cost, trace = witness
    if cost != 4:
        raise AssertionError(f"dual-rail minimum changed: {cost}")
    return {
        "minimum_gate_cost": cost,
        "maximum_delay": 2,
        "witness": list(trace),
        "target_tables": {"xor": f"{xor:04b}", "xnor": f"{xnor:04b}"},
    }


def minimum_switches_for_xor() -> dict[str, object]:
    """Enumerate Switch buses over pre-existing positive/negative rails."""

    # Truth-table bit order is x,y = 00, 01, 10, 11.
    mask = 0b1111
    signals = {
        "x": 0b1100,
        "not_x": 0b0011,
        "y": 0b1010,
        "not_y": 0b0101,
        "zero": 0,
        "one": mask,
    }
    target = signals["x"] ^ signals["y"]
    drivers = []
    for enable_name, enable in signals.items():
        for data_name, data in signals.items():
            if enable & (data ^ target):
                continue
            drivers.append(
                {
                    "enable": enable_name,
                    "data": data_name,
                    "covered": enable & target,
                }
            )

    one_switch = [driver for driver in drivers if driver["covered"] == target]
    if one_switch:
        raise AssertionError("one Switch unexpectedly realizes XOR")
    witnesses = []
    for left_index, left in enumerate(drivers):
        for right in drivers[left_index + 1 :]:
            if left["covered"] | right["covered"] == target:
                witnesses.append((left, right))
    if not witnesses:
        raise AssertionError("two-Switch XOR witness disappeared")
    witness = min(
        witnesses,
        key=lambda pair: tuple(
            (driver["enable"], driver["data"]) for driver in pair
        ),
    )
    return {
        "minimum_switch_count": 2,
        "minimum_gate_cost": 4,
        "z_is_numeric_zero": True,
        "witness": list(witness),
    }


def fixed_topology() -> dict[str, object]:
    first = tuple(gate for gate in base.GATES if gate.depth == 1)
    second = tuple(gate for gate in base.GATES if gate.depth == 2)
    consumers: dict[int, list[str]] = defaultdict(list)
    direct_nodes = set()
    for gate in second:
        for node in (gate.left, gate.right):
            if node in base.FIRST_LAYER:
                consumers[node].append(f"{gate.output:08x}")
            else:
                direct_nodes.add(node)
    unused_first = sorted(node for node in base.FIRST_LAYER if not consumers[node])
    if unused_first:
        raise AssertionError(f"first-layer nodes without final consumers: {unused_first}")
    if (len(first), len(second), len(base.GATES)) != (27, 34, 61):
        raise AssertionError("fixed XOR topology metrics changed")
    if len(direct_nodes) != 5:
        raise AssertionError(f"direct second-layer state bits changed: {len(direct_nodes)}")
    return {
        "xor_gate_count": len(base.GATES),
        "first_layer_count": len(first),
        "second_layer_count": len(second),
        "all_first_layer_nodes_feed_second_layer": True,
        "first_layer_fanout": {
            f"{node:08x}": outputs for node, outputs in sorted(consumers.items())
        },
        "distinct_direct_second_layer_state_bits": [
            next(iter(base.bits(node))) for node in sorted(direct_nodes)
        ],
    }


def imported_proofs() -> dict[str, object]:
    pair_cover = json.loads(PAIR_COVER_PROOF.read_text(encoding="utf-8"))
    phase = json.loads(PHASE_PROOF.read_text(encoding="utf-8"))
    cover = pair_cover["cover_enumeration"]
    tick = pair_cover["tick_zero_optimization"]
    if not cover["canonicalization_complete_for_all_61_xor_networks"]:
        raise AssertionError("pair-cover proof is not marked complete")
    if tick["exact_minimum_or"] != 47:
        raise AssertionError("fixed mode-OR minimum changed")
    if phase["solution_count_at_logic_cost_le_1"] != 0:
        raise AssertionError("phase shell unexpectedly has a <=1-gate solution")
    return {
        "pair_cover": {
            "minimum_pair_set_count": cover["minimum_pair_set_count"],
            "canonicalization_complete": True,
            "exact_mode_or_minimum": tick["exact_minimum_or"],
        },
        "phase": {
            "checked_wirings": phase["checked_wirings"],
            "logic_cost_le_1_solution_count": phase[
                "solution_count_at_logic_cost_le_1"
            ],
            "minimum_fixed_shell_gate": 12,
        },
    }


def main() -> None:
    topology = fixed_topology()
    dual = minimum_dual_rail_cost()
    switch = minimum_switches_for_xor()
    imported = imported_proofs()

    categories = {
        "32 state Delay Bit": 32 * 5,
        "67-cycle zero-init phase shell": imported["phase"][
            "minimum_fixed_shell_gate"
        ],
        "47 fixed mode OR": imported["pair_cover"]["exact_mode_or_minimum"],
        "27 dual XOR/XNOR cells": topology["first_layer_count"]
        * dual["minimum_gate_cost"],
        "34 two-Switch XOR buses": topology["second_layer_count"]
        * switch["minimum_gate_cost"],
        "5 shared direct-leaf complements": len(
            topology["distinct_direct_second_layer_state_bits"]
        ),
    }
    total = sum(categories.values())
    if total != 468:
        raise AssertionError(f"restricted lower bound changed: {total}")
    result = {
        "schema": 1,
        "scope": (
            "fixed two-shear 61-XOR DAG; explicit depth-two dual rails; "
            "one-layer Bit Switch XOR buses; zero-init 67-cycle controller"
        ),
        "not_a_global_bound": True,
        "topology": topology,
        "dual_rail_synthesis": dual,
        "switch_bus_synthesis": switch,
        "imported_complete_proofs": imported,
        "category_lower_bounds": categories,
        "gate_lower_bound": total,
        "delay": 8,
        "cycles": 67,
        "energy": total * 8 * 67,
        "conclusion": (
            "The existing 468/8/67 candidate is gate-optimal inside this "
            "restricted compressor family. A <=452 candidate must change the "
            "DAG, state encoding, timing protocol, or Switch macro family."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
