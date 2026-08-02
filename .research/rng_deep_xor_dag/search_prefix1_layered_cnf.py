"""Search alternative depth-three XOR DAGs for the prefix-1 RNG encoding.

The model fixes the prefix-1 state encoding and the B/C output matrices, but
does not fix the original three-stage gate graph.  It uses a finite layered
normal form:

* layer 1 contains two-input XORs of primary state bits;
* layer 2 contains weight-three/four forms built from layer-0/1 signals;
* every heavier B/C target is one final XOR of two signals of depth <= 2.

All 51 distinct non-unit B/C targets already cost one XOR each.  The SAT bound
counts only additional layer-1/layer-2 forms.  XOR cost is always 3 gates and
2 delay per bit; there is no word-width discount.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import asdict
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


BITS = 32
XOR_GATE_COST = 3
XOR_DELAY = 2
FIXED_SHELL_GATE = 166


def load_base(path: Path):
    spec = importlib.util.spec_from_file_location("rng_prefix1_layered_base", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def masks_of_weight(weight: int) -> tuple[int, ...]:
    return tuple(
        sum(1 << bit for bit in support)
        for support in combinations(range(BITS), weight)
    )


UNITS = masks_of_weight(1)
PAIRS = masks_of_weight(2)
SHALLOW = frozenset((*UNITS, *PAIRS))
UP_TO_FOUR = tuple(
    mask for weight in range(1, 5) for mask in masks_of_weight(weight)
)
UP_TO_FOUR_SET = frozenset(UP_TO_FOUR)


def shallow_partitions(mask: int) -> tuple[tuple[int, int], ...]:
    result = []
    for left in SHALLOW:
        right = mask ^ left
        if left < right and right in SHALLOW:
            result.append((left, right))
    return tuple(sorted(result))


def final_partitions(mask: int) -> tuple[tuple[int, int], ...]:
    result = []
    for left in UP_TO_FOUR:
        right = mask ^ left
        if left < right and right in UP_TO_FOUR_SET:
            result.append((left, right))
    return tuple(result)


def exactly_one(cnf: CNF, literals: list[int]) -> None:
    cnf.append(literals)
    for left, right in combinations(literals, 2):
        cnf.append([-left, -right])


def at_most_one(cnf: CNF, literals: list[int]) -> None:
    for left, right in combinations(literals, 2):
        cnf.append([-left, -right])


def clause_fingerprint(cnf: CNF) -> str:
    digest = hashlib.sha256()
    for clause in cnf.clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    return digest.hexdigest()


def build_problem(base, extra_limit: int):
    original_gates, original_forms, _, visible, feedback, T = base.build(1)
    target_forms = frozenset(
        original_forms[signal] for signal in (*visible, *feedback)
    )
    nonunit_targets = frozenset(
        form for form in target_forms if form.bit_count() > 1
    )
    pair_targets = frozenset(form for form in nonunit_targets if form.bit_count() == 2)
    depth_two_targets = frozenset(
        form for form in nonunit_targets if form.bit_count() in (3, 4)
    )
    heavy_targets = frozenset(form for form in nonunit_targets if form.bit_count() > 4)

    final_options = {form: final_partitions(form) for form in sorted(heavy_targets)}
    if any(not options for options in final_options.values()):
        raise AssertionError("a heavy target has no depth-three decomposition")
    residuals = {
        operand
        for options in final_options.values()
        for option in options
        for operand in option
        if operand.bit_count() in (3, 4)
    }
    depth_two_forms = frozenset((*depth_two_targets, *residuals))
    depth_options = {
        form: shallow_partitions(form) for form in sorted(depth_two_forms)
    }
    if any(not options for options in depth_options.values()):
        raise AssertionError("a depth-two form has no shallow decomposition")

    pool = IDPool()
    cnf = CNF()
    pair_used = {form: pool.id(f"p_{form:08x}") for form in PAIRS}
    depth_used = {
        form: pool.id(f"r_{form:08x}") for form in sorted(depth_two_forms)
    }
    depth_choice = {
        (form, index): pool.id(f"d_{form:08x}_{index}")
        for form, options in depth_options.items()
        for index in range(len(options))
    }
    final_choice = {
        (form, index): pool.id(f"o_{form:08x}_{index}")
        for form, options in final_options.items()
        for index in range(len(options))
    }

    pair_consumers: dict[int, list[int]] = defaultdict(list)
    depth_consumers: dict[int, list[int]] = defaultdict(list)

    for form in pair_targets:
        cnf.append([pair_used[form]])
    for form, options in depth_options.items():
        choices = [depth_choice[(form, index)] for index in range(len(options))]
        used = depth_used[form]
        if form in depth_two_targets:
            cnf.append([used])
            exactly_one(cnf, choices)
        else:
            at_most_one(cnf, choices)
            cnf.append([-used, *choices])
            for choice in choices:
                cnf.append([-choice, used])
        for index, option in enumerate(options):
            choice = depth_choice[(form, index)]
            for operand in option:
                if operand.bit_count() == 2:
                    cnf.append([-choice, pair_used[operand]])
                    pair_consumers[operand].append(choice)

    for form, options in final_options.items():
        choices = [final_choice[(form, index)] for index in range(len(options))]
        exactly_one(cnf, choices)
        for index, option in enumerate(options):
            choice = final_choice[(form, index)]
            for operand in option:
                if operand.bit_count() == 2:
                    cnf.append([-choice, pair_used[operand]])
                    pair_consumers[operand].append(choice)
                elif operand.bit_count() in (3, 4):
                    cnf.append([-choice, depth_used[operand]])
                    depth_consumers[operand].append(choice)

    for form, used in pair_used.items():
        if form not in pair_targets:
            cnf.append([-used, *pair_consumers.get(form, [])])
    for form, used in depth_used.items():
        if form not in depth_two_targets:
            cnf.append([-used, *depth_consumers.get(form, [])])

    extra_pair_vars = [
        variable for form, variable in pair_used.items() if form not in pair_targets
    ]
    extra_depth_vars = [
        variable
        for form, variable in depth_used.items()
        if form not in depth_two_targets
    ]
    extra_vars = [*extra_pair_vars, *extra_depth_vars]
    bound = CardEnc.atmost(
        lits=extra_vars,
        bound=extra_limit,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    cnf.extend(bound.clauses)
    return {
        "cnf": cnf,
        "pool": pool,
        "T": T,
        "visible": visible,
        "feedback": feedback,
        "target_forms": target_forms,
        "nonunit_targets": nonunit_targets,
        "pair_targets": pair_targets,
        "depth_two_targets": depth_two_targets,
        "heavy_targets": heavy_targets,
        "pair_used": pair_used,
        "depth_used": depth_used,
        "depth_options": depth_options,
        "depth_choice": depth_choice,
        "final_options": final_options,
        "final_choice": final_choice,
        "original_gate_count": len(original_gates),
        "extra_vars": extra_vars,
    }


def selected(model: frozenset[int], variable: int) -> bool:
    return variable in model


def extract_dag(base, problem, model: frozenset[int]):
    chosen_pairs = frozenset(
        form
        for form, variable in problem["pair_used"].items()
        if selected(model, variable)
    )
    chosen_depth = frozenset(
        form
        for form, variable in problem["depth_used"].items()
        if selected(model, variable)
    )
    chosen_depth_options = {}
    for form in sorted(chosen_depth):
        indexes = [
            index
            for index in range(len(problem["depth_options"][form]))
            if selected(model, problem["depth_choice"][(form, index)])
        ]
        if len(indexes) != 1:
            raise AssertionError(f"depth-two form {form:08x} lacks one choice")
        chosen_depth_options[form] = problem["depth_options"][form][indexes[0]]
    chosen_final_options = {}
    for form in sorted(problem["heavy_targets"]):
        indexes = [
            index
            for index in range(len(problem["final_options"][form]))
            if selected(model, problem["final_choice"][(form, index)])
        ]
        if len(indexes) != 1:
            raise AssertionError(f"heavy target {form:08x} lacks one choice")
        chosen_final_options[form] = problem["final_options"][form][indexes[0]]

    forms = {signal: 1 << signal for signal in range(BITS)}
    depths = {signal: 0 for signal in range(BITS)}
    signal_for_form = {form: signal for signal, form in forms.items()}
    gates = []
    next_signal = BITS

    def add(form: int, operands: tuple[int, int], layer: int):
        nonlocal next_signal
        if form in signal_for_form:
            return
        left, right = (signal_for_form[operand] for operand in operands)
        if forms[left] ^ forms[right] != form:
            raise AssertionError("gate form replay failed")
        output = next_signal
        next_signal += 1
        gates.append(base.Gate(output, left, right, layer))
        forms[output] = form
        depths[output] = max(depths[left], depths[right]) + 1
        signal_for_form[form] = output

    for form in sorted(chosen_pairs):
        bits = tuple(bit for bit in range(BITS) if form >> bit & 1)
        add(form, (1 << bits[0], 1 << bits[1]), 0)
    for form in sorted(chosen_depth):
        add(form, chosen_depth_options[form], 1)
    for form in sorted(problem["heavy_targets"]):
        add(form, chosen_final_options[form], 2)

    visible = tuple(signal_for_form[form] for form in problem["target_visible_forms"])
    feedback = tuple(signal_for_form[form] for form in problem["target_feedback_forms"])
    if max(depths[signal] for signal in (*visible, *feedback)) > 3:
        raise AssertionError("DAG exceeds XOR depth three")
    return tuple(gates), forms, depths, visible, feedback, chosen_depth_options, chosen_final_options


def audit_phase(base, gates, forms, depths, feedback, T, maximum: int):
    sites = base.enumerate_sites(gates, depths, feedback)
    assignments = []
    total_or = 0
    for seed in range(BITS):
        target = sum(((row >> seed) & 1) << output for output, row in enumerate(T))
        found = base.shortest_representation(target, sites, maximum)
        if found is None:
            return {
                "status": "unreachable-within-bound",
                "failed_seed": seed,
                "maximum_sites_per_seed": maximum,
            }
        count, indexes = found
        total_or += count
        assignments.append(
            {
                "seed": seed,
                "target": f"{target:08x}",
                "or_count": count,
                "site_influences": [f"{sites[index].influence:08x}" for index in indexes],
            }
        )
    return {
        "status": "relaxed-exact-within-bound",
        "or_count": total_or,
        "site_count": len(sites),
        "unique_influence_count": len({site.influence for site in sites}),
        "maximum_sites_per_seed": maximum,
        "assignments": assignments,
        "certificate_sha256": hashlib.sha256(
            json.dumps(assignments, sort_keys=True, separators=(",", ":")).encode("ascii")
        ).hexdigest(),
    }


def solve(base, *, extra_limit: int, solver_name: str, phase_maximum: int):
    problem = build_problem(base, extra_limit)
    original_gates, original_forms, _, original_visible, original_feedback, _ = base.build(1)
    problem["target_visible_forms"] = tuple(original_forms[s] for s in original_visible)
    problem["target_feedback_forms"] = tuple(original_forms[s] for s in original_feedback)
    cnf = problem["cnf"]
    started = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        elapsed = time.perf_counter() - started
        model = frozenset(value for value in (solver.get_model() or ()) if value > 0)
        stats = solver.accum_stats()

    result = {
        "schema": 1,
        "model": "prefix1 layered depth-three B/C XOR DAG",
        "status": "sat" if sat else "unsat",
        "solver": solver_name,
        "extra_limit": extra_limit,
        "base_nonunit_target_count": len(problem["nonunit_targets"]),
        "xor_limit": len(problem["nonunit_targets"]) + extra_limit,
        "xor_gate_cost": XOR_GATE_COST,
        "xor_delay": XOR_DELAY,
        "variable_count": problem["pool"].top,
        "clause_count": len(cnf.clauses),
        "clause_sha256": clause_fingerprint(cnf),
        "elapsed_seconds": round(elapsed, 6),
        "solver_stats": stats,
        "candidate_counts": {
            "pairs": len(problem["pair_used"]),
            "depth_two_forms": len(problem["depth_used"]),
            "depth_two_choices": len(problem["depth_choice"]),
            "heavy_targets": len(problem["heavy_targets"]),
            "final_choices": len(problem["final_choice"]),
        },
    }
    if not sat:
        return result

    dag = extract_dag(base, problem, model)
    gates, forms, depths, visible, feedback, depth_options, final_options = dag
    xor_count = len(gates)
    phase = audit_phase(
        base, gates, forms, depths, feedback, problem["T"], phase_maximum
    )
    or_count = phase.get("or_count")
    gate = None if or_count is None else FIXED_SHELL_GATE + XOR_GATE_COST * xor_count + or_count
    result.update(
        {
            "xor_count": xor_count,
            "selected_extra_count": xor_count - len(problem["nonunit_targets"]),
            "max_xor_depth": max(depths[signal] for signal in (*visible, *feedback)),
            "gate": gate,
            "delay": 10,
            "cycles": 66,
            "energy": None if gate is None else gate * 10 * 66,
            "beats_431_9_66": gate is not None and gate * 10 < 431 * 9,
            "depth_two_decompositions": {
                f"{form:08x}": [f"{value:08x}" for value in option]
                for form, option in depth_options.items()
            },
            "final_decompositions": {
                f"{form:08x}": [f"{value:08x}" for value in option]
                for form, option in final_options.items()
            },
            "visible_forms": [f"{forms[signal]:08x}" for signal in visible],
            "feedback_forms": [f"{forms[signal]:08x}" for signal in feedback],
            "gate_dag": [asdict(gate_item) for gate_item in gates],
            "phase_audit": phase,
        }
    )
    if xor_count > result["xor_limit"]:
        raise AssertionError("extracted DAG exceeds SAT XOR bound")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--extra-limit", type=int, default=9)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--phase-max-sites", type=int, default=6)
    args = parser.parse_args()
    if args.extra_limit < 0:
        parser.error("--extra-limit must be nonnegative")
    base = load_base(Path(__file__).with_name("audit_cyclic_retime.py"))
    result = solve(
        base,
        extra_limit=args.extra_limit,
        solver_name=args.solver,
        phase_maximum=args.phase_max_sites,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: value
                for key, value in result.items()
                if key
                not in {
                    "depth_two_decompositions",
                    "final_decompositions",
                    "visible_forms",
                    "feedback_forms",
                    "gate_dag",
                    "phase_audit",
                }
            },
            indent=2,
        )
    )
    return 0 if result["status"] == "sat" else 2


if __name__ == "__main__":
    raise SystemExit(main())
