"""PySAT backend for exact active-tradeoff XOR2/Switch-XOR3 covers."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import threading
import time
from typing import Iterable, Sequence

try:
    from pysat.formula import IDPool
    from pysat.solvers import Solver
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).with_name("_vendor")))
    from pysat.formula import IDPool
    from pysat.solvers import Solver

import optimize_pruned38 as model_data


class ClauseSink:
    def __init__(self, solver: Solver) -> None:
        self.solver = solver
        self.count = 0

    def add(self, clause: Iterable[int]) -> None:
        self.solver.add_clause(list(clause))
        self.count += 1


def encode_weighted_atmost(
    sink: ClauseSink,
    pool: IDPool,
    weighted_literals: Sequence[tuple[int, int]],
    bound: int,
) -> None:
    """Forward sequential counter for a small weighted at-most constraint."""
    previous: list[int] | None = None
    for index, (literal, weight) in enumerate(weighted_literals):
        if weight > bound:
            sink.add((-literal,))
            continue
        current = [pool.id(("sum", index, threshold)) for threshold in range(1, bound + 1)]
        for threshold in range(1, weight + 1):
            sink.add((-literal, current[threshold - 1]))
        if previous is not None:
            for threshold in range(1, bound + 1):
                sink.add((-previous[threshold - 1], current[threshold - 1]))
            for threshold in range(1, bound + 1):
                if threshold + weight <= bound:
                    sink.add((-literal, -previous[threshold - 1], current[threshold + weight - 1]))
                else:
                    sink.add((-literal, -previous[threshold - 1]))
        for threshold in range(1, bound):
            sink.add((-current[threshold], current[threshold - 1]))
        previous = current


def solve_with_timeout(solver: Solver, timeout_seconds: float | None) -> bool | None:
    if timeout_seconds is None:
        return solver.solve()
    timer = threading.Timer(timeout_seconds, solver.interrupt)
    timer.start()
    try:
        return solver.solve_limited(expect_interrupt=True)
    finally:
        timer.cancel()
        solver.clear_interrupt()


def solve_candidate(
    candidate: model_data.Candidate,
    *,
    solver_name: str,
    timeout_seconds: float | None,
    target_gate_max: int,
    budget_override: int | None,
    source_log: Path | None,
) -> dict[str, object]:
    h_rows, o_rows, active_hidden = model_data.build_pruned(
        candidate.x_rows, candidate.d_rows
    )
    model_data.verify_sequences(h_rows, o_rows)
    targets = tuple(sorted({row for row in h_rows + o_rows if row.bit_count() >= 2}))
    maximum_weight = max((row.bit_count() for row in targets), default=0)
    state_bits = len(h_rows)
    state_hex_width = (state_bits + 3) // 4
    fixed_gate = 5 * state_bits + 32 + 6
    care_audit = model_data.cross_care_audit(h_rows, o_rows)
    care_audit["total_gate_lower_bound"] = (
        fixed_gate + care_audit["logic_gate_lower_bound"]
    )
    logic_budget = (
        target_gate_max - fixed_gate
        if budget_override is None
        else budget_override
    )
    if logic_budget < 0:
        raise ValueError(
            f"fixed cost {fixed_gate} exceeds target gate limit {target_gate_max}"
        )
    if maximum_weight > 9:
        return {
            "schema": 2,
            "scope": "active-tradeoff exact two-level XOR2/Switch-XOR3 shared cover",
            "status": "UNSUPPORTED",
            "reason": f"target support {maximum_weight} exceeds the library maximum 9",
            "solver": solver_name,
            "logic_budget": logic_budget,
            "fixed_gate": fixed_gate,
            "target_gate_max": target_gate_max,
            "active_original_hidden_rows": list(active_hidden),
            "verified_sequences": {"seeds": 256, "outputs_per_seed": 65},
        }

    target_options = {}
    groups: set[int] = set()
    for target in targets:
        support = tuple(bit for bit in range(len(h_rows)) if (target >> bit) & 1)
        options = model_data.partitions(support)
        target_options[target] = options
        for option in options:
            for block in option:
                if len(block) >= 2:
                    groups.add(model_data.block_mask(block))

    # Every cost is a multiple of three gates, so floor the budget to units.
    unit_bound = logic_budget // 3
    pool = IDPool()
    group_vars = {group: pool.id(("group", group)) for group in sorted(groups)}
    option_vars: dict[tuple[int, int], int] = {}
    weighted: list[tuple[int, int]] = [
        (variable, 1 if group.bit_count() == 2 else 4)
        for group, variable in group_vars.items()
    ]

    started = time.perf_counter()
    with Solver(name=solver_name) as solver:
        sink = ClauseSink(solver)
        for target, options in target_options.items():
            selectors = []
            for index, option in enumerate(options):
                selector = pool.id(("option", target, index))
                option_vars[target, index] = selector
                selectors.append(selector)
                for block in option:
                    if len(block) >= 2:
                        sink.add((-selector, group_vars[model_data.block_mask(block)]))
                final_cost = model_data.option_final_cost(option)
                if final_cost:
                    weighted.append((selector, final_cost // 3))
            sink.add(selectors)

        encode_weighted_atmost(sink, pool, weighted, unit_bound)
        build_seconds = time.perf_counter() - started
        solving_started = time.perf_counter()
        # The bundled CaDiCaL wrapper does not implement interrupt/clear.
        # Its runs are bounded by the outer process timeout used in reproduction.
        sat = (
            solver.solve()
            if solver_name.startswith("cadical")
            else solve_with_timeout(solver, timeout_seconds)
        )
        solve_seconds = time.perf_counter() - solving_started
        stats = solver.accum_stats()

        result: dict[str, object] = {
            "schema": 2,
            "scope": "active-tradeoff exact two-level XOR2/Switch-XOR3 shared cover",
            "status": "SAT" if sat else ("UNSAT" if sat is False else "UNKNOWN"),
            "solver": solver_name,
            "logic_budget": logic_budget,
            "logic_budget_units": unit_bound,
            "fixed_gate": fixed_gate,
            "target_gate_max": target_gate_max,
            "build_seconds": build_seconds,
            "solve_seconds": solve_seconds,
            "variables": pool.top,
            "clauses": sink.count,
            "solver_stats": stats,
            "active_original_hidden_rows": list(active_hidden),
            "original_hidden_rows": len(candidate.d_rows),
            "pruned_identically_zero_hidden_rows": [
                index for index in range(len(candidate.d_rows))
                if index not in active_hidden
            ],
            "cross_care_optimistic_lower_bound": care_audit,
            "candidate": {
                "source_log": str(source_log.resolve()) if source_log else None,
                "source_lines": list(candidate.source_lines),
                "reported_stats": candidate.reported,
                "X_rows_hex": [f"{row:03x}" for row in candidate.x_rows],
                "D_rows_hex": [
                    f"{row:0{(32 + len(candidate.d_rows) + 3) // 4}x}"
                    for row in candidate.d_rows
                ],
            },
            "verified_sequences": {"seeds": 256, "outputs_per_seed": 65},
            "target_summary": {
                "distinct_nontrivial": len(targets),
                "optimistic_logic_lower_bound": 3 * len(targets),
                "optimistic_total_gate_lower_bound": fixed_gate + 3 * len(targets),
                "weight_distribution": {
                    str(weight): sum(row.bit_count() == weight for row in targets)
                    for weight in sorted({row.bit_count() for row in targets})
                },
                "pair_or_triple_group_universe": len(groups),
                "partition_options": sum(len(options) for options in target_options.values()),
            },
            "H_rows_hex": [f"{row:0{state_hex_width}x}" for row in h_rows],
            "O_rows_hex": [f"{row:0{state_hex_width}x}" for row in o_rows],
        }

        if sat:
            positive = {literal for literal in solver.get_model() if literal > 0}
            chosen_options = {}
            required_groups: set[int] = set()
            logic_units = 0
            for target, options in target_options.items():
                chosen = next(
                    index for index in range(len(options))
                    if option_vars[target, index] in positive
                )
                option = options[chosen]
                logic_units += model_data.option_final_cost(option) // 3
                for block in option:
                    if len(block) >= 2:
                        required_groups.add(model_data.block_mask(block))
                chosen_options[f"{target:0{state_hex_width}x}"] = [
                    [*block] for block in option
                ]
            logic_units += sum(1 if group.bit_count() == 2 else 4 for group in required_groups)
            if logic_units > unit_bound:
                raise AssertionError("extracted minimal witness exceeds encoded bound")
            result["solution"] = {
                "logic_gate": 3 * logic_units,
                "total_gate": fixed_gate + 3 * logic_units,
                "delay": 9,
                "cycles": 66,
                "selected_groups": [
                    {
                        "mask_hex": f"{group:0{state_hex_width}x}",
                        "support": [bit for bit in range(state_bits) if (group >> bit) & 1],
                        "kind": "XOR2" if group.bit_count() == 2 else "Switch-XOR3",
                        "gate": 3 if group.bit_count() == 2 else 12,
                    }
                    for group in sorted(required_groups)
                ],
                "target_partitions": chosen_options,
            }

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log", type=Path,
        help="search_active_state_tradeoff log; omit for the historical pruned-38 point",
    )
    parser.add_argument(
        "--candidate", choices=("last", "all"), default="last",
        help="use the last log record or every distinct X/D point",
    )
    parser.add_argument(
        "--budget", type=int,
        help="logic-only override; default is target-gate-max minus the pruned fixed cost",
    )
    parser.add_argument("--target-gate-max", type=int, default=430)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.budget is not None and args.budget < 0:
        raise SystemExit("budget must be nonnegative")
    if args.target_gate_max < 0:
        raise SystemExit("target-gate-max must be nonnegative")

    candidates = (
        model_data.load_log_candidates(args.log, args.candidate)
        if args.log
        else (model_data.default_candidate(),)
    )
    results = [
        solve_candidate(
            candidate,
            solver_name=args.solver,
            timeout_seconds=args.timeout_seconds,
            target_gate_max=args.target_gate_max,
            budget_override=args.budget,
            source_log=args.log,
        )
        for candidate in candidates
    ]
    if len(results) == 1:
        result: dict[str, object] = results[0]
        result["candidate_selection"] = args.candidate
    else:
        result = {
            "schema": 2,
            "scope": "distinct active-tradeoff candidates exact cover batch",
            "selection": args.candidate,
            "source_log": str(args.log.resolve()) if args.log else None,
            "candidate_count": len(results),
            "results": results,
        }

    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("ascii")
    args.output.write_bytes(encoded)
    print(json.dumps({
        "candidate_count": len(results),
        "statuses": [item["status"] for item in results],
        "summaries": [
            {
                "source_lines": item.get("candidate", {}).get("source_lines", []),
                "active_hidden": len(item["active_original_hidden_rows"]),
                "fixed_gate": item["fixed_gate"],
                "logic_budget": item["logic_budget"],
                "targets": item.get("target_summary", {}).get("distinct_nontrivial"),
                "optimistic_total_gate_lower_bound": item.get("target_summary", {}).get(
                    "optimistic_total_gate_lower_bound"
                ),
                "build_seconds": item.get("build_seconds"),
                "solve_seconds": item.get("solve_seconds"),
                "variables": item.get("variables"),
                "clauses": item.get("clauses"),
                "solution": item.get("solution"),
            }
            for item in results
        ],
        "sha256": sha256(encoded).hexdigest(),
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
