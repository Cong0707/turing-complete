"""Exact ordinary-gate CNF for reachable RNG mode-macro rows.

At ``slots == gate_bound`` every component must cost one, so XOR and Switch
are impossible.  Every useful ordinary-gate net has one always-driven output;
the physical-net problem then reduces exactly to predecessor selection in an
acyclic DAG.  This specialized projection removes irrelevant net partitions.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import threading
import time

from pysat.solvers import Solver

from search_mode_macro_joint import build_scenarios, load_nodes
from search_ordinary_v_cnf import (
    COMMUTATIVE,
    KINDS,
    NOT,
    Encoder,
    add_conditional_gate,
)


def solve(args: argparse.Namespace) -> dict[str, object]:
    node_map = load_nodes()
    nodes = tuple(int(item, 16) for item in args.nodes.split(","))
    selected = tuple((node, node_map[node]) for node in nodes)
    scenario = build_scenarios(selected)
    width = int(scenario["padded_rows"])
    source_records = list(scenario["sources"])
    target_records = list(scenario["targets"])
    source_tables = [int(source["value"]) for source in source_records]
    source_names = [str(source["name"]) for source in source_records]
    source_count = len(source_tables)

    enc = Encoder()
    values: list[list[int | bool]] = [
        [bool((table >> case) & 1) for case in range(width)]
        for table in source_tables
    ]
    kinds: list[list[int]] = []
    levels: list[list[int]] = []
    left_uses: list[list[int]] = []
    right_uses: list[list[int]] = []

    for slot in range(args.slots):
        available = source_count + slot
        slot_kinds = [enc.var(f"kind_{slot}_{kind}") for kind in KINDS]
        enc.exactly_one(slot_kinds)
        slot_levels = [enc.var(f"level_{slot}_{level}") for level in range(1, args.max_delay + 1)]
        enc.exactly_one(slot_levels)
        left = [enc.var(f"left_{slot}_{source}") for source in range(available)]
        right = [enc.var(f"right_{slot}_{source}") for source in range(available)]
        enc.exactly_one(left)
        enc.exactly_one(right)
        for source, use in enumerate(right):
            enc.clause((-slot_kinds[NOT], use if source == 0 else -use))
        for left_source in range(available):
            for right_source in range(left_source):
                for operation in COMMUTATIVE:
                    enc.clause((-slot_kinds[operation], -left[left_source], -right[right_source]))

        for source in range(source_count, available):
            predecessor = source - source_count
            for predecessor_level in range(1, args.max_delay + 1):
                for result_level in range(1, args.max_delay + 1):
                    if result_level <= predecessor_level:
                        enc.clause(
                            (-levels[predecessor][predecessor_level - 1], -left[source], -slot_levels[result_level - 1])
                        )
                        enc.clause(
                            (-levels[predecessor][predecessor_level - 1], -right[source], -slot_levels[result_level - 1])
                        )

        slot_values = []
        for case in range(width):
            left_value = enc.var(f"left_value_{slot}_{case}")
            right_value = enc.var(f"right_value_{slot}_{case}")
            for source in range(available):
                source_value = values[source][case]
                enc.clause((-left[source], -left_value, source_value))
                enc.clause((-left[source], left_value, enc.neg(source_value)))
                enc.clause((-right[source], -right_value, source_value))
                enc.clause((-right[source], right_value, enc.neg(source_value)))
            output = enc.var(f"value_{slot}_{case}")
            for operation, literal in enumerate(slot_kinds):
                add_conditional_gate(enc, literal, output, left_value, right_value, operation)
            slot_values.append(output)

        if slot:
            dependency_left = left[source_count + slot - 1]
            dependency_right = right[source_count + slot - 1]
            for previous_kind in range(len(KINDS)):
                for current_kind in range(previous_kind):
                    enc.clause(
                        (
                            dependency_left,
                            dependency_right,
                            -kinds[slot - 1][previous_kind],
                            -slot_kinds[current_kind],
                        )
                    )

        kinds.append(slot_kinds)
        levels.append(slot_levels)
        left_uses.append(left)
        right_uses.append(right)
        values.append(slot_values)

    output_uses = []
    for output_index, target_record in enumerate(target_records):
        target = int(target_record["value"])
        uses = [enc.var(f"output_{output_index}_{source}") for source in range(source_count + args.slots)]
        enc.exactly_one(uses)
        for source, use in enumerate(uses):
            for case in range(width):
                wanted = bool((target >> case) & 1)
                value = values[source][case]
                enc.clause((-use, value if wanted else enc.neg(value)))
        output_uses.append(uses)

    for slot in range(args.slots):
        source = source_count + slot
        users = [uses[source] for uses in output_uses]
        for later in range(slot + 1, args.slots):
            users.extend((left_uses[later][source], right_uses[later][source]))
        enc.clause(users)

    # Equal truth functions are redundant under free fanout.
    for right_source in range(source_count, source_count + args.slots):
        right_values = values[right_source]
        for left_source in range(right_source):
            left_values = values[left_source]
            differences = []
            for case, (left_value, right_value) in enumerate(zip(left_values, right_values, strict=True)):
                if type(left_value) is bool:
                    differences.append(right_value if not left_value else -right_value)
                else:
                    difference = enc.var(f"different_{left_source}_{right_source}_{case}")
                    enc.clause((-difference, left_value, right_value))
                    enc.clause((-difference, -left_value, -right_value))
                    enc.clause((difference, left_value, -right_value))
                    enc.clause((difference, -left_value, right_value))
                    differences.append(difference)
            enc.clause(differences)

    started = time.perf_counter()
    status = "unknown"
    model = None
    with Solver(name=args.solver, bootstrap_with=enc.cnf) as solver:
        timer = threading.Timer(args.timeout, solver.interrupt) if args.timeout > 0 else None
        if timer:
            timer.start()
        try:
            answer = solver.solve_limited(expect_interrupt=True)
        finally:
            if timer:
                timer.cancel()
        if answer is True:
            status = "sat"
            model = solver.get_model()
        elif answer is False:
            status = "unsat"

    result: dict[str, object] = {
        "schema": 1,
        "model": "exact single-driver ordinary-gate CNF over reachable load/steady rows",
        "status": status,
        "nodes": [f"{node:08x}" for node in nodes],
        "slots": args.slots,
        "max_delay": args.max_delay,
        "scenario_width": width,
        "source_names": source_names,
        "source_values_hex": [f"{value:0{width // 4}x}" for value in source_tables],
        "targets_hex": [f"{int(target['value']):0{width // 4}x}" for target in target_records],
        "solver": args.solver,
        "timeout_seconds": args.timeout,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "reason_unknown": "timeout" if status == "unknown" else "",
    }
    if status == "sat" and model is not None:
        enabled = {literal for literal in model if literal > 0}
        result["gates"] = [
            {
                "slot": slot,
                "source": source_count + slot,
                "kind": KINDS[next(index for index, literal in enumerate(kinds[slot]) if literal in enabled)],
                "left": next(index for index, literal in enumerate(left_uses[slot]) if literal in enabled),
                "right": next(index for index, literal in enumerate(right_uses[slot]) if literal in enabled),
                "level": next(index + 1 for index, literal in enumerate(levels[slot]) if literal in enabled),
            }
            for slot in range(args.slots)
        ]
        result["outputs"] = [
            next(index for index, literal in enumerate(uses) if literal in enabled)
            for uses in output_uses
        ]
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", required=True)
    parser.add_argument("--slots", type=int, required=True)
    parser.add_argument("--max-delay", type=int, default=3)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = solve(args)
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    args.output.write_text(encoded, encoding="utf-8")
    print(json.dumps({"status": result["status"], "seconds": result["solve_seconds"], "variables": result["variables"], "clauses": result["clauses"]}))
    print(f"sha256={sha256(encoded.encode()).hexdigest()}")
    return 2 if result["status"] == "unknown" else (0 if result["status"] == "sat" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
