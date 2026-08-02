"""Allow low-weight prefix-1 targets to move from XOR depth two to three.

This extends ``search_prefix1_layered_cnf.py``.  A weight-three/four B/C
target may either be its own layer-two form or a layer-three XOR of two other
depth-two-or-shallower forms.  The extension captures sharing that the simpler
normal form intentionally omitted while retaining an exact finite CNF.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def clause_fingerprint(cnf: CNF) -> str:
    digest = hashlib.sha256()
    for clause in cnf.clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    return digest.hexdigest()


def build_problem(layered, base, extra_limit: int):
    original = base.build(1)
    original_forms, visible, feedback, T = original[1], original[3], original[4], original[5]
    visible_forms = tuple(original_forms[signal] for signal in visible)
    feedback_forms = tuple(original_forms[signal] for signal in feedback)
    target_forms = frozenset((*visible_forms, *feedback_forms))
    nonunit_targets = frozenset(
        form for form in target_forms if form.bit_count() > 1
    )
    pair_targets = frozenset(form for form in nonunit_targets if form.bit_count() == 2)
    low_targets = frozenset(
        form for form in nonunit_targets if form.bit_count() in (3, 4)
    )
    final_targets = frozenset(form for form in nonunit_targets if form.bit_count() >= 3)
    final_options = {
        form: layered.final_partitions(form) for form in sorted(final_targets)
    }
    residuals = {
        operand
        for options in final_options.values()
        for option in options
        for operand in option
        if operand.bit_count() in (3, 4)
    }
    depth_forms = frozenset((*low_targets, *residuals))
    depth_options = {
        form: layered.shallow_partitions(form) for form in sorted(depth_forms)
    }

    pool = IDPool()
    cnf = CNF()
    pair_used = {form: pool.id(f"p_{form:08x}") for form in layered.PAIRS}
    depth_used = {form: pool.id(f"r_{form:08x}") for form in sorted(depth_forms)}
    depth_choice = {
        (form, index): pool.id(f"d_{form:08x}_{index}")
        for form, options in depth_options.items()
        for index in range(len(options))
    }
    shallow_target = {
        form: pool.id(f"s_{form:08x}") for form in sorted(low_targets)
    }
    final_choice = {
        (form, index): pool.id(f"o_{form:08x}_{index}")
        for form, options in final_options.items()
        for index in range(len(options))
    }

    for form in pair_targets:
        cnf.append([pair_used[form]])
    for form, options in depth_options.items():
        used = depth_used[form]
        choices = [depth_choice[(form, index)] for index in range(len(options))]
        cnf.append([-used, *choices])
        for index, option in enumerate(options):
            choice = depth_choice[(form, index)]
            cnf.append([-choice, used])
            for operand in option:
                if operand.bit_count() == 2:
                    cnf.append([-choice, pair_used[operand]])
        if form in low_targets:
            # If this target exists at depth two, that same gate is its output;
            # a separate depth-three duplicate can only waste a gate.
            cnf.append([-used, shallow_target[form]])
            cnf.append([-shallow_target[form], used])

    for form, options in final_options.items():
        choices = [final_choice[(form, index)] for index in range(len(options))]
        if form in low_targets:
            cnf.append([shallow_target[form], *choices])
        else:
            cnf.append(choices)
        for index, option in enumerate(options):
            choice = final_choice[(form, index)]
            for operand in option:
                if operand.bit_count() == 2:
                    cnf.append([-choice, pair_used[operand]])
                elif operand.bit_count() in (3, 4):
                    cnf.append([-choice, depth_used[operand]])

    extra_vars = [
        *(variable for form, variable in pair_used.items() if form not in pair_targets),
        *(variable for form, variable in depth_used.items() if form not in low_targets),
    ]
    cnf.extend(
        CardEnc.atmost(
            lits=extra_vars,
            bound=extra_limit,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    return {
        "cnf": cnf,
        "pool": pool,
        "T": T,
        "visible_forms": visible_forms,
        "feedback_forms": feedback_forms,
        "nonunit_targets": nonunit_targets,
        "pair_targets": pair_targets,
        "low_targets": low_targets,
        "final_targets": final_targets,
        "pair_used": pair_used,
        "depth_used": depth_used,
        "depth_options": depth_options,
        "depth_choice": depth_choice,
        "shallow_target": shallow_target,
        "final_options": final_options,
        "final_choice": final_choice,
    }


def choose_true(model: frozenset[int], variables) -> list[int]:
    return [index for index, variable in variables if variable in model]


def extract(layered, base, problem, model: frozenset[int]):
    chosen_pairs = frozenset(
        form for form, variable in problem["pair_used"].items() if variable in model
    )
    chosen_depth = frozenset(
        form for form, variable in problem["depth_used"].items() if variable in model
    )
    depth_decompositions = {}
    for form in chosen_depth:
        indexes = choose_true(
            model,
            (
                (index, problem["depth_choice"][(form, index)])
                for index in range(len(problem["depth_options"][form]))
            ),
        )
        if not indexes:
            raise AssertionError("selected depth form has no decomposition")
        depth_decompositions[form] = problem["depth_options"][form][indexes[0]]

    deep_targets = {
        form
        for form in problem["final_targets"]
        if form not in problem["low_targets"]
        or problem["shallow_target"][form] not in model
    }
    final_decompositions = {}
    for form in deep_targets:
        indexes = choose_true(
            model,
            (
                (index, problem["final_choice"][(form, index)])
                for index in range(len(problem["final_options"][form]))
            ),
        )
        if not indexes:
            raise AssertionError("deep target has no decomposition")
        final_decompositions[form] = problem["final_options"][form][indexes[0]]

    forms = {signal: 1 << signal for signal in range(layered.BITS)}
    depths = {signal: 0 for signal in range(layered.BITS)}
    signal_for_form = {form: signal for signal, form in forms.items()}
    gates = []
    next_signal = layered.BITS

    def add(form: int, operands: tuple[int, int], layer: int):
        nonlocal next_signal
        if form in signal_for_form:
            return
        left, right = (signal_for_form[operand] for operand in operands)
        output = next_signal
        next_signal += 1
        gates.append(base.Gate(output, left, right, layer))
        forms[output] = forms[left] ^ forms[right]
        depths[output] = max(depths[left], depths[right]) + 1
        if forms[output] != form:
            raise AssertionError("gate form replay failed")
        signal_for_form[form] = output

    for form in sorted(chosen_pairs):
        support = tuple(bit for bit in range(layered.BITS) if form >> bit & 1)
        add(form, (1 << support[0], 1 << support[1]), 0)
    for form in sorted(chosen_depth):
        add(form, depth_decompositions[form], 1)
    for form in sorted(deep_targets):
        add(form, final_decompositions[form], 2)

    visible = tuple(signal_for_form[form] for form in problem["visible_forms"])
    feedback = tuple(signal_for_form[form] for form in problem["feedback_forms"])
    return (
        tuple(gates),
        forms,
        depths,
        visible,
        feedback,
        depth_decompositions,
        final_decompositions,
    )


def solve(layered, base, *, extra_limit: int, solver_name: str, phase_max: int):
    problem = build_problem(layered, base, extra_limit)
    started = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=problem["cnf"].clauses) as solver:
        sat = solver.solve()
        model = frozenset(value for value in (solver.get_model() or ()) if value > 0)
        stats = solver.accum_stats()
    elapsed = time.perf_counter() - started
    result = {
        "schema": 1,
        "model": "prefix1 general layered depth-three B/C XOR DAG",
        "status": "sat" if sat else "unsat",
        "solver": solver_name,
        "extra_limit": extra_limit,
        "base_nonunit_target_count": len(problem["nonunit_targets"]),
        "xor_limit": len(problem["nonunit_targets"]) + extra_limit,
        "xor_gate_cost": layered.XOR_GATE_COST,
        "xor_delay": layered.XOR_DELAY,
        "variable_count": problem["pool"].top,
        "clause_count": len(problem["cnf"].clauses),
        "clause_sha256": clause_fingerprint(problem["cnf"]),
        "elapsed_seconds": round(elapsed, 6),
        "solver_stats": stats,
        "candidate_counts": {
            "pairs": len(problem["pair_used"]),
            "depth_two_forms": len(problem["depth_used"]),
            "depth_two_choices": len(problem["depth_choice"]),
            "final_targets": len(problem["final_targets"]),
            "final_choices": len(problem["final_choice"]),
        },
    }
    if not sat:
        return result

    dag = extract(layered, base, problem, model)
    gates, forms, depths, visible, feedback, depth_decompositions, final_decompositions = dag
    phase = layered.audit_phase(
        base, gates, forms, depths, feedback, problem["T"], phase_max
    )
    or_count = phase.get("or_count")
    gate = None
    if or_count is not None:
        gate = (
            layered.FIXED_SHELL_GATE
            + layered.XOR_GATE_COST * len(gates)
            + or_count
        )
    result.update(
        {
            "xor_count": len(gates),
            "max_xor_depth": max(depths[signal] for signal in (*visible, *feedback)),
            "gate": gate,
            "delay": 10,
            "cycles": 66,
            "energy": None if gate is None else gate * 10 * 66,
            "beats_431_9_66": gate is not None and gate * 10 < 431 * 9,
            "depth_two_decompositions": {
                f"{form:08x}": [f"{value:08x}" for value in option]
                for form, option in depth_decompositions.items()
            },
            "final_decompositions": {
                f"{form:08x}": [f"{value:08x}" for value in option]
                for form, option in final_decompositions.items()
            },
            "gate_dag": [asdict(gate_item) for gate_item in gates],
            "phase_audit": phase,
        }
    )
    if len(gates) > result["xor_limit"]:
        raise AssertionError("extracted circuit exceeds XOR limit")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--extra-limit", type=int, default=9)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--phase-max-sites", type=int, default=6)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    layered = load("rng_prefix1_general_layered", here / "search_prefix1_layered_cnf.py")
    base = load("rng_prefix1_general_base", here / "audit_cyclic_retime.py")
    result = solve(
        layered,
        base,
        extra_limit=args.extra_limit,
        solver_name=args.solver,
        phase_max=args.phase_max_sites,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: value
                for key, value in result.items()
                if key not in {"depth_two_decompositions", "final_decompositions", "gate_dag", "phase_audit"}
            },
            indent=2,
        )
    )
    return 0 if result["status"] == "sat" else 2


if __name__ == "__main__":
    raise SystemExit(main())
