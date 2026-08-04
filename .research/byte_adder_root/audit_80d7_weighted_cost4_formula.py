"""Enumerate low-cost mixed formula replacements in the audited 80/7 adder.

The existing local-root audit closes ordinary-only replacements.  This worker
adds the component mixtures that matter at the next exact cost:

* ordinary gates: cost 1, delay 1;
* one physical Switch driver / one-driver BUS: cost 2, delay 1;
* XOR and XNOR: cost 3, delay 2;
* one resolved BUS with two Switch drivers: cost 4, delay 1.

The search is a complete formula-tree closure over each explicitly reviewed
source pool.  It preserves packed ``bits`` and ``driven`` state.  Conflicting
states are discarded because every supported operation propagates an input
conflict monotonically; such a state can never become a legal public output.
For equal semantics at equal exact cost, only the earliest witness is kept,
which is complete for a fixed output deadline.

This is an offline audit.  It does not read or write the formal game save.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import gc
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_DAG = HERE / "byte-adder-hybrid-phasefold-g80-d7.json"
DEFAULT_OUTPUT = HERE / "weighted-cost4-formula-resub-80d7.json"
MATERIALIZER = (
    ROOT / ".research" / "byte_adder_builder_layout_agent" / "materialize_factory_dag.py"
)

DELAY_LIMIT = 7
FULL_ROWS = 1 << 17

TARGETS = {
    # S0 and S6 own four private gates; search exact-cost-three replacements.
    49: {
        "name": "S0",
        "private_cost": 4,
        "replacement_cost": 3,
        "sources": (2, 3, 18, 43, 44, 45),
    },
    73: {
        "name": "S6",
        "private_cost": 4,
        "replacement_cost": 3,
        "sources": (12, 13, 14, 15, 34, 35, 36, 37, 38, 39, 62, 63, 64, 65, 66, 67, 68, 69),
    },
    # S2 and S4 own five private gates; search exact-cost-four replacements.
    81: {
        "name": "S2",
        "private_cost": 5,
        "replacement_cost": 4,
        "sources": (4, 5, 6, 7, 22, 23, 24, 25, 45, 50, 51, 52, 54, 55, 56, 76, 77),
    },
    86: {
        "name": "S4",
        "private_cost": 5,
        "replacement_cost": 4,
        "sources": (8, 9, 10, 11, 28, 29, 30, 31, 32, 56, 57, 59, 60, 61, 62, 82, 83),
    },
}

COMMUTATIVE_ORDINARY = ("AND", "NAND", "OR", "NOR")
COMMUTATIVE_XOR = ("XOR", "XNOR")


@dataclass(frozen=True, slots=True)
class PackedState:
    bits: int
    driven: int
    conflict: int


@dataclass(frozen=True, slots=True)
class Formula:
    state: PackedState
    arrival: int
    expression: tuple[Any, ...]


def load_materializer():
    spec = importlib.util.spec_from_file_location(
        "byte_adder_weighted_formula_materializer", MATERIALIZER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(MATERIALIZER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def apply_ordinary(op: str, left: PackedState, right: PackedState, mask: int) -> PackedState:
    if op == "AND":
        bits = left.bits & right.bits
    elif op == "NAND":
        bits = ~(left.bits & right.bits) & mask
    elif op == "OR":
        bits = left.bits | right.bits
    elif op == "NOR":
        bits = ~(left.bits | right.bits) & mask
    elif op == "XOR":
        bits = left.bits ^ right.bits
    elif op == "XNOR":
        bits = ~(left.bits ^ right.bits) & mask
    else:
        raise ValueError(op)
    return PackedState(bits & mask, mask, left.conflict | right.conflict)


def apply_not(value: PackedState, mask: int) -> PackedState:
    return PackedState(~value.bits & mask, mask, value.conflict)


def apply_bus(drivers: Iterable[tuple[PackedState, PackedState]], mask: int) -> PackedState:
    ones = 0
    zeros = 0
    driven = 0
    conflict = 0
    for enable, data in drivers:
        active = enable.bits
        ones |= active & data.bits
        zeros |= active & (~data.bits & mask)
        driven |= active
        conflict |= enable.conflict | data.conflict
    conflict |= ones & zeros
    return PackedState(ones & mask, driven & mask, conflict & mask)


def project_domain(
    source_ids: tuple[int, ...],
    target: int,
    states: dict[int, dict[str, int]],
) -> tuple[tuple[Formula, ...], PackedState, int]:
    """Compress all rows by exact source bits/driven/conflict signatures."""

    classes: dict[tuple[int, ...], tuple[int, int, int]] = {}
    for row in range(FULL_ROWS):
        signature: list[int] = []
        for node_id in source_ids:
            state = states[node_id]
            signature.extend(
                (
                    (int(state["bits"]) >> row) & 1,
                    (int(state["driven"]) >> row) & 1,
                    (int(state["conflict"]) >> row) & 1,
                )
            )
        target_state = states[target]
        target_value = (
            (int(target_state["bits"]) >> row) & 1,
            (int(target_state["driven"]) >> row) & 1,
            (int(target_state["conflict"]) >> row) & 1,
        )
        key = tuple(signature)
        previous = classes.get(key)
        if previous is not None and previous != target_value:
            raise RuntimeError(
                f"target {target} is not determined by reviewed source pool: {key}"
            )
        classes[key] = target_value

    signatures = tuple(sorted(classes))
    compact_sources: list[Formula] = []
    for source_index, node_id in enumerate(source_ids):
        offset = source_index * 3
        compact = PackedState(
            bits=sum(signature[offset] << row for row, signature in enumerate(signatures)),
            driven=sum(
                signature[offset + 1] << row for row, signature in enumerate(signatures)
            ),
            conflict=sum(
                signature[offset + 2] << row for row, signature in enumerate(signatures)
            ),
        )
        compact_sources.append(
            Formula(compact, int(states[node_id]["depth"]), ("SOURCE", node_id))
        )

    target_rows = tuple(classes[signature] for signature in signatures)
    compact_target = PackedState(
        bits=sum(value[0] << row for row, value in enumerate(target_rows)),
        driven=sum(value[1] << row for row, value in enumerate(target_rows)),
        conflict=sum(value[2] << row for row, value in enumerate(target_rows)),
    )
    return tuple(compact_sources), compact_target, len(signatures)


def unordered_pairs(
    left: tuple[Formula, ...],
    right: tuple[Formula, ...],
    same_level: bool,
):
    for left_index, left_formula in enumerate(left):
        start = left_index if same_level else 0
        for right_formula in right[start:]:
            yield left_formula, right_formula


def enumerate_formula_closure(
    sources: tuple[Formula, ...],
    target: PackedState,
    compact_rows: int,
    exact_cost: int,
) -> dict[str, Any]:
    mask = (1 << compact_rows) - 1
    if target.driven != mask or target.conflict:
        raise ValueError("the audited public target must be fully driven and conflict-free")
    level_zero: dict[tuple[int, int], Formula] = {}
    for source in sources:
        if source.state.conflict:
            raise RuntimeError("reviewed source pool contains a conflicting source")
        key = (source.state.bits, source.state.driven)
        previous = level_zero.get(key)
        if previous is None or source.arrival < previous.arrival:
            level_zero[key] = source

    levels: list[dict[tuple[int, int], Formula]] = [level_zero]
    level_summaries: list[dict[str, Any]] = [
        {
            "cost": 0,
            "deadline_feasible_states": len(level_zero),
            "fully_driven_states": sum(state[1] == mask for state in level_zero),
            "attempts": {"SOURCE": len(sources)},
            "conflict_pruned": 0,
            "late_pruned": 0,
        }
    ]

    hit: Formula | None = None
    for cost in range(1, exact_cost + 1):
        current: dict[tuple[int, int], Formula] = {}
        attempts: dict[str, int] = {}
        conflict_pruned = 0
        late_pruned = 0

        def remember(op: str, candidate: Formula) -> None:
            nonlocal conflict_pruned, late_pruned
            attempts[op] = attempts.get(op, 0) + 1
            if candidate.state.conflict:
                conflict_pruned += 1
                return
            if candidate.arrival > DELAY_LIMIT:
                late_pruned += 1
                return
            key = (candidate.state.bits, candidate.state.driven)
            previous = current.get(key)
            if previous is None or candidate.arrival < previous.arrival:
                current[key] = candidate

        # One cost-one ordinary gate.
        for child in levels[cost - 1].values():
            remember(
                "NOT",
                Formula(
                    apply_not(child.state, mask),
                    child.arrival + 1,
                    ("NOT", child.expression),
                ),
            )
        for left_cost in range(cost):
            right_cost = cost - 1 - left_cost
            if left_cost > right_cost:
                continue
            left_level = tuple(levels[left_cost].values())
            right_level = tuple(levels[right_cost].values())
            for left, right in unordered_pairs(
                left_level, right_level, left_cost == right_cost
            ):
                arrival = max(left.arrival, right.arrival) + 1
                for op in COMMUTATIVE_ORDINARY:
                    remember(
                        op,
                        Formula(
                            apply_ordinary(op, left.state, right.state, mask),
                            arrival,
                            (op, left.expression, right.expression),
                        ),
                    )

        # One cost-two Switch driver, represented by its complete one-driver BUS.
        if cost >= 2:
            for enable_cost in range(cost - 1):
                data_cost = cost - 2 - enable_cost
                for enable in levels[enable_cost].values():
                    for data in levels[data_cost].values():
                        remember(
                            "BUS1",
                            Formula(
                                apply_bus(((enable.state, data.state),), mask),
                                max(enable.arrival, data.arrival) + 1,
                                ("BUS1", enable.expression, data.expression),
                            ),
                        )

        # XOR/XNOR are each one cost-three, delay-two component.
        if cost >= 3:
            for left_cost in range(cost - 2):
                right_cost = cost - 3 - left_cost
                if left_cost > right_cost:
                    continue
                left_level = tuple(levels[left_cost].values())
                right_level = tuple(levels[right_cost].values())
                for left, right in unordered_pairs(
                    left_level, right_level, left_cost == right_cost
                ):
                    arrival = max(left.arrival, right.arrival) + 2
                    for op in COMMUTATIVE_XOR:
                        remember(
                            op,
                            Formula(
                                apply_ordinary(op, left.state, right.state, mask),
                                arrival,
                                (op, left.expression, right.expression),
                            ),
                        )

        # At total cost four a resolved network may own two raw Switch drivers.
        if cost == 4:
            raw = tuple(levels[0].values())
            driver_pairs = tuple((enable, data) for enable in raw for data in raw)
            for left_index, (enable0, data0) in enumerate(driver_pairs):
                for enable1, data1 in driver_pairs[left_index:]:
                    remember(
                        "BUS2",
                        Formula(
                            apply_bus(
                                (
                                    (enable0.state, data0.state),
                                    (enable1.state, data1.state),
                                ),
                                mask,
                            ),
                            max(
                                enable0.arrival,
                                data0.arrival,
                                enable1.arrival,
                                data1.arrival,
                            )
                            + 1,
                            (
                                "BUS2",
                                enable0.expression,
                                data0.expression,
                                enable1.expression,
                                data1.expression,
                            ),
                        ),
                    )

        levels.append(current)
        level_summaries.append(
            {
                "cost": cost,
                "deadline_feasible_states": len(current),
                "fully_driven_states": sum(state[1] == mask for state in current),
                "attempts": attempts,
                "conflict_pruned": conflict_pruned,
                "late_pruned": late_pruned,
            }
        )
        hit = current.get((target.bits, target.driven))

    return {
        "levels": level_summaries,
        "status": "sat" if hit is not None else "unsat",
        "witness": None
        if hit is None
        else {
            "arrival": hit.arrival,
            "expression": hit.expression,
        },
    }


def replay_expression(
    expression: tuple[Any, ...] | list[Any],
    states: dict[int, dict[str, int]],
    mask: int,
) -> tuple[PackedState, int, int]:
    op = str(expression[0])
    if op == "SOURCE":
        node_id = int(expression[1])
        source = states[node_id]
        return (
            PackedState(
                int(source["bits"]),
                int(source["driven"]),
                int(source["conflict"]),
            ),
            int(source["depth"]),
            0,
        )
    children = [replay_expression(child, states, mask) for child in expression[1:]]
    if op == "NOT":
        state, arrival, cost = children[0]
        return apply_not(state, mask), arrival + 1, cost + 1
    if op in COMMUTATIVE_ORDINARY:
        left, right = children
        return (
            apply_ordinary(op, left[0], right[0], mask),
            max(left[1], right[1]) + 1,
            left[2] + right[2] + 1,
        )
    if op in COMMUTATIVE_XOR:
        left, right = children
        return (
            apply_ordinary(op, left[0], right[0], mask),
            max(left[1], right[1]) + 2,
            left[2] + right[2] + 3,
        )
    if op == "BUS1":
        enable, data = children
        return (
            apply_bus(((enable[0], data[0]),), mask),
            max(enable[1], data[1]) + 1,
            enable[2] + data[2] + 2,
        )
    if op == "BUS2":
        enable0, data0, enable1, data1 = children
        return (
            apply_bus(((enable0[0], data0[0]), (enable1[0], data1[0])), mask),
            max(enable0[1], data0[1], enable1[1], data1[1]) + 1,
            enable0[2] + data0[2] + enable1[2] + data1[2] + 4,
        )
    raise ValueError(op)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--target", action="append", type=int, choices=tuple(TARGETS))
    args = parser.parse_args()

    materializer = load_materializer()
    payload = json.loads(args.dag.read_text(encoding="utf-8"))
    ordered_nodes = tuple(payload["factory_dag"]["nodes"])
    states = materializer.logical_states(ordered_nodes)
    selected_targets = tuple(args.target or TARGETS)
    output_nodes = tuple(int(value) for value in payload["factory_dag"]["outputs"])
    full_mask = (1 << FULL_ROWS) - 1

    results = []
    for target in selected_targets:
        spec = TARGETS[target]
        source_ids = tuple(int(value) for value in spec["sources"])
        compact_sources, compact_target, compact_rows = project_domain(
            source_ids, target, states
        )
        started = time.perf_counter()
        closure = enumerate_formula_closure(
            compact_sources,
            compact_target,
            compact_rows,
            int(spec["replacement_cost"]),
        )
        elapsed = time.perf_counter() - started
        result: dict[str, Any] = {
            "target": target,
            "output": spec["name"],
            "source_ids": list(source_ids),
            "private_cost": int(spec["private_cost"]),
            "replacement_cost": int(spec["replacement_cost"]),
            "compact_truth_rows": compact_rows,
            "delay_limit": DELAY_LIMIT,
            "search_seconds": elapsed,
            **closure,
        }
        witness = closure["witness"]
        if witness is not None:
            replayed, arrival, cost = replay_expression(
                witness["expression"], states, full_mask
            )
            target_state = states[target]
            if replayed.bits != int(target_state["bits"]):
                raise RuntimeError(f"target {target} witness fails full truth replay")
            if replayed.driven != full_mask or replayed.conflict:
                raise RuntimeError(f"target {target} witness is not a legal driven output")
            if cost != int(spec["replacement_cost"]) or arrival > DELAY_LIMIT:
                raise RuntimeError(f"target {target} witness violates cost/deadline")
            other_arrivals = [
                int(states[node_id]["depth"])
                for node_id in output_nodes
                if node_id != target
            ]
            result["full_replay"] = {
                "truth_rows": FULL_ROWS,
                "bits_match": True,
                "driven_all": True,
                "conflict_assignments": 0,
                "cost": cost,
                "arrival": arrival,
                "projected_gate": int(payload["metrics"]["gate"])
                - int(spec["private_cost"])
                + cost,
                "projected_delay": max((*other_arrivals, arrival)),
            }
        results.append(result)
        del compact_sources
        gc.collect()

    final = {
        "schema": "byte-adder-80d7-weighted-cost4-formula-closure-v1",
        "source": str(args.dag.resolve()),
        "baseline": payload["metrics"],
        "component_costs": {
            "ordinary": {"gate": 1, "delay": 1},
            "switch_driver": {"gate": 2, "delay": 1},
            "xor_xnor": {"gate": 3, "delay": 2},
        },
        "full_truth_rows": FULL_ROWS,
        "targets": results,
        "status": "sat" if any(item["status"] == "sat" for item in results) else "unsat",
        "scope": (
            "complete exact-cost mixed formula-tree closure over each explicit reviewed "
            "local source pool, with packed bits/driven/conflict and deadline<=7"
        ),
        "limitations": [
            "not an arbitrary internal-fanout DAG closure",
            "does not change any retained source or cross output boundaries",
            "not a global 79/7 lower bound",
        ],
    }
    canonical = json.loads(json.dumps(final, ensure_ascii=False))
    canonical["source"] = Path(str(canonical["source"])).name
    for item in canonical["targets"]:
        item.pop("search_seconds", None)
    final["deterministic_payload_sha256"] = hashlib.sha256(
        json.dumps(
            canonical,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        (json.dumps(final, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "status": final["status"],
                "targets": [
                    {
                        "target": item["target"],
                        "output": item["output"],
                        "status": item["status"],
                        "search_seconds": item["search_seconds"],
                        "final_states": item["levels"][-1]["deadline_feasible_states"],
                        "witness": item["witness"],
                    }
                    for item in results
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
