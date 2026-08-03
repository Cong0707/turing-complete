#!/usr/bin/env python3
"""Prove a depth-8 XOR2 lower bound from the q-weight-three targets.

The model deliberately gives every seed-only linear form away for free.  It
counts only gates whose q projection is nonzero, so its optimum is a lower
bound for every ordinary XOR2 circuit, including circuits with cancellation.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import time
from typing import Sequence

from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2
from pysat.formula import IDPool, WCNF
from pysat.solvers import Solver


BITS = 32
MASK32 = (1 << BITS) - 1
TARGET_GATE_BASELINE = 61
XOR2_GATE_COST = 3
LOGIC_BUDGET = 292


class ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("PageFaultCount", ctypes.c_ulong),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def working_set_bytes() -> int:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ProcessMemoryCounters),
        ctypes.c_ulong,
    ]
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    process = kernel32.GetCurrentProcess()
    if not psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return int(counters.WorkingSetSize)


def load_targets(path: Path) -> tuple[tuple[int, ...], tuple[int, ...]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    raw_targets = document.get("targets")
    metrics = document.get("metrics")
    if not isinstance(raw_targets, list) or len(raw_targets) != 64:
        raise ValueError("certificate must contain 64 targets")
    if not isinstance(metrics, list) or len(metrics) != 64:
        raise ValueError("certificate must contain 64 metrics")
    targets = tuple(int(str(value), 16) for value in raw_targets)
    selected = tuple(
        index
        for index, metric in enumerate(metrics)
        if isinstance(metric, dict) and not bool(metric.get("over_delay8_xor"))
    )
    if selected != tuple(index for index in range(64) if index not in (13, 16, 27)):
        raise AssertionError("the expected three oversized rows changed")
    if len({targets[index] for index in selected}) != TARGET_GATE_BASELINE:
        raise AssertionError("the 61 safe targets must be distinct")
    return targets, selected


def bits(mask: int) -> tuple[int, ...]:
    return tuple(bit for bit in range(BITS) if mask >> bit & 1)


def build_model(
    targets: Sequence[int], selected: Sequence[int]
) -> tuple[
    IDPool,
    tuple[tuple[int, ...], ...],
    tuple[int, ...],
    tuple[dict[str, object], ...],
    frozenset[tuple[int, int]],
    dict[int, tuple[str, int, int]],
]:
    q1 = tuple(
        index for index in selected if (targets[index] & MASK32).bit_count() == 1
    )
    q3 = tuple(
        index for index in selected if (targets[index] & MASK32).bit_count() == 3
    )
    if len(q1) != 11 or len(q3) != 26:
        raise AssertionError("safe-row q-weight distribution changed")

    base_units = frozenset(
        (
            (targets[index] & MASK32).bit_length() - 1,
            targets[index] >> BITS,
        )
        for index in q1
    )
    pool = IDPool()
    hard: list[tuple[int, ...]] = []
    cost_nodes: dict[int, tuple[str, int, int]] = {}
    records: list[dict[str, object]] = []

    def node(kind: str, q_value: int, seed_value: int = 0) -> int:
        key = ("node", kind, q_value, seed_value)
        variable = pool.id(key)
        if kind == "unit":
            bit = q_value.bit_length() - 1
            is_base = (bit, seed_value) in base_units
        else:
            is_base = False
        if not is_base:
            cost_nodes[variable] = (kind, q_value, seed_value)
        return variable

    for target_index in q3:
        target = targets[target_index]
        q_value = target & MASK32
        seed_value = target >> BITS
        option_variables = []
        options = []
        for remaining_bit in bits(q_value):
            pair_value = q_value ^ (1 << remaining_bit)
            unit_value = 1 << remaining_bit
            pair_variable = node("pair", pair_value)
            unit_variable = node("unit", unit_value, seed_value)
            option_variable = pool.id(("option", target_index, remaining_bit))
            option_variables.append(option_variable)
            hard.append((-option_variable, pair_variable))
            if (remaining_bit, seed_value) not in base_units:
                hard.append((-option_variable, unit_variable))
            options.append(
                {
                    "remaining_q_bit": remaining_bit,
                    "pair_q": f"{pair_value:08x}",
                    "unit_q": f"{unit_value:08x}",
                    "unit_seed": f"{seed_value:08x}",
                    "unit_reuses_q1_target": (
                        remaining_bit,
                        seed_value,
                    )
                    in base_units,
                    "option_variable": option_variable,
                }
            )
        hard.append(tuple(option_variables))
        records.append(
            {
                "target_index": target_index,
                "target": f"{target:016x}",
                "q": f"{q_value:08x}",
                "seed": f"{seed_value:08x}",
                "options": options,
            }
        )

    return (
        pool,
        tuple(hard),
        tuple(sorted(cost_nodes)),
        tuple(records),
        base_units,
        cost_nodes,
    )


def solve_optimum(
    pool: IDPool,
    hard: Sequence[Sequence[int]],
    cost_variables: Sequence[int],
    solver_name: str,
) -> tuple[int, frozenset[int], float]:
    formula = WCNF()
    for clause in hard:
        formula.append(list(clause))
    for variable in cost_variables:
        formula.append([-variable], weight=1)
    started = time.perf_counter()
    with RC2(formula, solver=solver_name, adapt=True, exhaust=True, incr=True) as rc2:
        model = rc2.compute()
        optimum = int(rc2.cost)
    elapsed = time.perf_counter() - started
    if model is None:
        raise AssertionError("the relaxed q3 model must be satisfiable")
    positive = frozenset(literal for literal in model if literal > 0)
    replay_cost = sum(variable in positive for variable in cost_variables)
    if replay_cost != optimum:
        raise AssertionError("RC2 objective replay failed")
    return optimum, positive, elapsed


def solve_boundary(
    pool_top: int,
    hard: Sequence[Sequence[int]],
    cost_variables: Sequence[int],
    bound: int,
    solver_name: str,
) -> tuple[bool, float, int, int]:
    cardinality = CardEnc.atmost(
        lits=list(cost_variables),
        bound=bound,
        top_id=pool_top,
        encoding=EncType.seqcounter,
    )
    clauses = [list(clause) for clause in hard]
    clauses.extend(cardinality.clauses)
    started = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        satisfiable = bool(solver.solve())
    return (
        satisfiable,
        time.perf_counter() - started,
        cardinality.nv,
        len(clauses),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--solvers", nargs="+", default=("g4", "m22"))
    args = parser.parse_args()

    initial_working_set = working_set_bytes()
    targets, selected_indices = load_targets(args.certificate)
    pool, hard, cost_variables, records, base_units, cost_nodes = build_model(
        targets, selected_indices
    )
    optimum, positive, rc2_seconds = solve_optimum(
        pool, hard, cost_variables, args.solvers[0]
    )
    if optimum != 41:
        raise AssertionError(f"expected q3 extra optimum 41, got {optimum}")

    boundaries = []
    for solver_name in args.solvers:
        for bound in (optimum - 1, optimum):
            satisfiable, elapsed, variables, clauses = solve_boundary(
                pool.top, hard, cost_variables, bound, solver_name
            )
            expected = bound == optimum
            if satisfiable != expected:
                raise AssertionError(
                    f"{solver_name} boundary {bound} returned {satisfiable}"
                )
            boundaries.append(
                {
                    "solver": solver_name,
                    "bound": bound,
                    "status": "SAT" if satisfiable else "UNSAT",
                    "seconds": elapsed,
                    "variables": variables,
                    "clauses": clauses,
                }
            )

    selected_nodes = [
        {
            "kind": cost_nodes[variable][0],
            "q": f"{cost_nodes[variable][1]:08x}",
            "seed": f"{cost_nodes[variable][2]:08x}",
            "variable": variable,
        }
        for variable in cost_variables
        if variable in positive
    ]
    for record in records:
        chosen = [
            option
            for option in record["options"]
            if option["option_variable"] in positive
        ]
        if not chosen:
            raise AssertionError("RC2 witness leaves a q3 target uncovered")
        record["chosen_option"] = chosen[0]

    q_xor2_lower_bound = TARGET_GATE_BASELINE + optimum
    logic_lower_bound = q_xor2_lower_bound * XOR2_GATE_COST
    payload = {
        "schema": 1,
        "status": "verified-lower-bound-restricted-to-ordinary-xor2",
        "scope": (
            "61 safe targets of the over=3 persistent-seed center; all "
            "seed-only linear computation is free; q cancellation and sharing "
            "are allowed; nonlinear gates and resolved Switch buses are excluded"
        ),
        "certificate": str(args.certificate),
        "certificate_sha256": hashlib.sha256(args.certificate.read_bytes()).hexdigest(),
        "excluded_target_indices": sorted(set(range(64)) - set(selected_indices)),
        "safe_target_count": len(selected_indices),
        "q1_target_count": len(base_units),
        "q3_target_count": len(records),
        "reason": {
            "state_input_arrival": 4,
            "xor2_delay": 2,
            "deadline": 8,
            "q3_final_operands": "one disjoint q-pair plus one q-unit",
            "q_pair_seed_label": 0,
            "q_unit_seed_label": "the complete target seed label",
            "seed_only_gate_cost": 0,
        },
        "model": {
            "hard_clauses": len(hard),
            "id_pool_variables_before_cardinality": pool.top,
            "cost_node_variables": len(cost_variables),
            "base_q1_units_available_without_extra_cost": [
                {"q_bit": bit, "seed": f"{seed:08x}"}
                for bit, seed in sorted(base_units)
            ],
        },
        "q3_extra_gate_optimum": optimum,
        "target_gate_baseline": TARGET_GATE_BASELINE,
        "q_involving_xor2_lower_bound": q_xor2_lower_bound,
        "logic_gate_lower_bound": logic_lower_bound,
        "logic_budget": LOGIC_BUDGET,
        "exceeds_logic_budget": logic_lower_bound > LOGIC_BUDGET,
        "rc2": {
            "solver": args.solvers[0],
            "seconds": rc2_seconds,
        },
        "boundary_checks": boundaries,
        "selected_cost_nodes": selected_nodes,
        "targets": records,
        "working_set": {
            "initial_bytes": initial_working_set,
            "final_bytes": working_set_bytes(),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "q3_extra_gate_optimum": optimum,
                "q_involving_xor2_lower_bound": q_xor2_lower_bound,
                "logic_gate_lower_bound": logic_lower_bound,
                "logic_budget": LOGIC_BUDGET,
                "boundary_checks": boundaries,
                "working_set": payload["working_set"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
