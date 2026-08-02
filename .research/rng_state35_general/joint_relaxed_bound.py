"""Low-memory lazy feasibility audit for the 35-state RNG mixed XOR network.

For every output the legal implementations form a monotone DNF over paid
first-level forms and paid final-node types.  Materialising one selector per
DNF term needs hundreds of thousands of variables and too much solver memory.
This script instead solves a weak weighted MaxSAT master and separates an uncovered
output with a valid hitting-set clause.  If the weak master becomes UNSAT, the
full physical circuit is necessarily UNSAT too.

All NOR/AND controls of Switch-XOR3 nodes are free in this relaxation.  Thus an
UNSAT result at core bound 217 proves physical total gate >= 431.  No game,
save, RAM component, or network service is accessed.
"""

from __future__ import annotations

import argparse
from array import array
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import threading
import time

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF

import joint_shared_controls as shared


@dataclass(slots=True)
class OptionFamily:
    target: int
    flat: array
    offsets: array
    raw_option_count: int
    option_sha256: str

    @property
    def option_count(self) -> int:
        return len(self.offsets) - 1


class VariablePool:
    def __init__(self) -> None:
        self.top = 0

    def new(self) -> int:
        self.top += 1
        return self.top


class FormulaFingerprint:
    """Stable fingerprint for native cardinalities and lazily added clauses."""

    def __init__(self) -> None:
        self.digest = sha256()
        self.clauses = 0
        self.literal_occurrences = 0
        self.atmosts = 0

    def clause(self, literals: list[int]) -> None:
        self.digest.update(b"c ")
        self.digest.update(" ".join(map(str, literals)).encode("ascii"))
        self.digest.update(b" 0\n")
        self.clauses += 1
        self.literal_occurrences += len(literals)

    def atmost(self, literals: list[int], bound: int) -> None:
        self.digest.update(f"a {bound} ".encode("ascii"))
        self.digest.update(" ".join(map(str, literals)).encode("ascii"))
        self.digest.update(b" 0\n")
        self.atmosts += 1
        self.literal_occurrences += len(literals)

    def soft(self, literal: int, weight: int) -> None:
        self.digest.update(f"s {weight} {literal} 0\n".encode("ascii"))
        self.literal_occurrences += 1

    def hexdigest(self) -> str:
        return self.digest.hexdigest()


def options_for(target: int, state_bits: int) -> tuple[tuple[shared.Option, ...], int]:
    raw = shared.enumerate_options(target, state_bits)
    reduced = shared.relaxed_reduce_options(raw)
    if not reduced:
        raise AssertionError(f"target {target:x} has no relaxed option")
    return reduced, len(raw)


def option_digest(options: tuple[shared.Option, ...]) -> str:
    digest = sha256()
    for option in options:
        digest.update(option.kind.encode("ascii"))
        digest.update(b":")
        digest.update(",".join(f"{value:x}" for value in option.required_forms).encode("ascii"))
        digest.update(b":")
        digest.update(",".join(f"{value:x}" for value in option.sources).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def variable_map_digest(
    form_var: dict[int, int],
    type_var: dict[tuple[int, str], int],
    var_cost: dict[int, int],
) -> str:
    digest = sha256()
    for form, variable in sorted(form_var.items(), key=lambda item: item[1]):
        digest.update(f"f {variable} {var_cost[variable]} {form:x}\n".encode("ascii"))
    for (output, kind), variable in sorted(type_var.items(), key=lambda item: item[1]):
        digest.update(f"t {variable} {var_cost[variable]} {output} {kind}\n".encode("ascii"))
    return digest.hexdigest()


def build_families(
    targets: tuple[int, ...],
    state_bits: int,
    *,
    memory_mb: int,
) -> tuple[
    list[OptionFamily],
    dict[int, int],
    dict[tuple[int, str], int],
    dict[int, int],
    int,
    int,
    int,
]:
    pool = VariablePool()
    form_var: dict[int, int] = {}
    type_var: dict[tuple[int, str], int] = {}
    var_cost: dict[int, int] = {}
    families = []
    raw_total = 0
    reduced_total = 0
    compact_literals = 0
    limit = memory_mb * 1048576

    def form_variable(form: int) -> int:
        variable = form_var.get(form)
        if variable is None:
            variable = pool.new()
            form_var[form] = variable
            var_cost[variable] = (
                shared.PAIR_GATE if form.bit_count() == 2 else shared.SWITCH_XOR3_BASE_GATE
            )
        return variable

    for output, target in enumerate(targets):
        options, raw_count = options_for(target, state_bits)
        raw_total += raw_count
        reduced_total += len(options)
        flat = array("I")
        offsets = array("I", [0])
        for option in options:
            requirements = [form_variable(form) for form in option.required_forms]
            if option.final_base_gate:
                type_key = (output, option.kind)
                variable = type_var.get(type_key)
                if variable is None:
                    variable = pool.new()
                    type_var[type_key] = variable
                    var_cost[variable] = option.final_base_gate
                requirements.append(variable)
            requirements = sorted(set(requirements))
            if not requirements:
                raise AssertionError("zero-cost option invalidates the lower-bound model")
            flat.extend(requirements)
            offsets.append(len(flat))
        compact_literals += len(flat)
        families.append(
            OptionFamily(
                target=target,
                flat=flat,
                offsets=offsets,
                raw_option_count=raw_count,
                option_sha256=option_digest(options),
            )
        )
        current = shared.current_rss_bytes()
        print(
            f"target={output + 1:02d}/{len(targets)} row={target:09x} "
            f"weight={target.bit_count()} raw={raw_count} reduced={len(options)} "
            f"compact_lits={len(flat)} vars={pool.top} rss_mib={current / 1048576:.1f}",
            flush=True,
        )
        if current > limit:
            raise MemoryError(f"build RSS {current / 1048576:.1f} MiB exceeds limit")
        del options
        shared.switch_source_triples.cache_clear()
    return (
        families,
        form_var,
        type_var,
        var_cost,
        pool.top,
        raw_total,
        reduced_total,
        compact_literals,
    )


def satisfied_option(family: OptionFamily, truth: bytearray) -> int | None:
    flat, offsets = family.flat, family.offsets
    for option_index in range(family.option_count):
        if all(truth[flat[position]] for position in range(offsets[option_index], offsets[option_index + 1])):
            return option_index
    return None


def option_is_hit(family: OptionFamily, option_index: int, hitting: set[int]) -> bool:
    start, end = family.offsets[option_index], family.offsets[option_index + 1]
    return any(family.flat[position] in hitting for position in range(start, end))


def separating_clause(family: OptionFamily, truth: bytearray, variable_count: int) -> list[int]:
    """Return a false-variable hitting set for all DNF terms of one output."""

    flat, offsets = family.flat, family.offsets
    remaining = list(range(family.option_count))
    chosen: list[int] = []
    counts = array("I", [0]) * (variable_count + 1)
    while remaining:
        touched: list[int] = []
        for option_index in remaining:
            has_false = False
            for position in range(offsets[option_index], offsets[option_index + 1]):
                variable = flat[position]
                if truth[variable]:
                    continue
                has_false = True
                if counts[variable] == 0:
                    touched.append(variable)
                counts[variable] += 1
            if not has_false:
                raise AssertionError("separator called for a covered family")
        best = max(touched, key=lambda variable: (counts[variable], -variable))
        chosen.append(best)
        remaining = [
            option_index
            for option_index in remaining
            if best not in flat[offsets[option_index] : offsets[option_index + 1]]
        ]
        for variable in touched:
            counts[variable] = 0

    # Greedy set cover is not necessarily inclusion-minimal.  Removing
    # redundant literals makes the learned consequence strictly stronger.
    hitting = set(chosen)
    for variable in reversed(chosen):
        trial = hitting - {variable}
        if all(option_is_hit(family, index, trial) for index in range(family.option_count)):
            hitting = trial
    clause = sorted(hitting)
    if not clause or any(truth[variable] for variable in clause):
        raise AssertionError("invalid separating clause")
    if not all(option_is_hit(family, index, hitting) for index in range(family.option_count)):
        raise AssertionError("separating clause does not hit every option")
    return clause


def replay_selection(
    families: list[OptionFamily],
    selected_indices: list[int],
    state_bits: int,
) -> tuple[shared.Option, ...]:
    selection = []
    for family, selected_index in zip(families, selected_indices):
        options, raw_count = options_for(family.target, state_bits)
        if raw_count != family.raw_option_count:
            raise AssertionError("raw option count changed during replay")
        if len(options) != family.option_count or option_digest(options) != family.option_sha256:
            raise AssertionError("option stream changed during replay")
        selection.append(options[selected_index])
        del options
        shared.switch_source_triples.cache_clear()
    return tuple(selection)


def solve_lazy(
    targets: tuple[int, ...],
    state_bits: int,
    *,
    bound: int,
    timeout_seconds: float,
    memory_mb: int,
) -> tuple[dict[str, object], tuple[shared.Option, ...] | None, shared.Score | None]:
    build_started = time.perf_counter()
    (
        families,
        form_var,
        type_var,
        var_cost,
        variable_count,
        raw_total,
        reduced_total,
        compact_literals,
    ) = build_families(targets, state_bits, memory_mb=memory_mb)
    build_seconds = time.perf_counter() - build_started
    cost_literals = [
        variable
        for variable, weight in sorted(var_cost.items())
        for _ in range(weight)
    ]
    fingerprint = FormulaFingerprint()
    for variable, weight in sorted(var_cost.items()):
        fingerprint.soft(-variable, weight)
    peak = [shared.current_rss_bytes()]
    interrupted = threading.Event()
    memory_interrupted = threading.Event()
    limit = memory_mb * 1048576
    deadline = time.monotonic() + timeout_seconds
    iterations = 0
    cuts = 0
    max_cut_width = 0
    selected_indices: list[int] | None = None
    final_truth: bytearray | None = None
    status = "UNKNOWN"
    solve_started = time.perf_counter()
    cut_records: list[tuple[int, list[int]]] = []
    stats = {"restarts": 0, "conflicts": 0, "decisions": 0, "propagations": 0}
    unknown_reason = None
    last_master_optimum: int | None = None
    while not interrupted.is_set():
        if time.monotonic() >= deadline:
            interrupted.set()
            unknown_reason = "global timeout before master rebuild"
            break
        formula = WCNF()
        for _, clause in cut_records:
            formula.append(clause)
        for variable, weight in sorted(var_cost.items()):
            formula.append([-variable], weight=weight)

        local_stop = threading.Event()
        model = None
        optimum = None
        with RC2(formula, solver="g4", adapt=True, exhaust=True, incr=False) as rc2:
            def watch() -> None:
                while not local_stop.wait(0.10):
                    current = shared.current_rss_bytes()
                    peak[0] = max(peak[0], current)
                    if current > limit:
                        memory_interrupted.set()
                        interrupted.set()
                        rc2.oracle.interrupt()
                        return
                    if time.monotonic() >= deadline:
                        interrupted.set()
                        rc2.oracle.interrupt()
                        return

            watcher = threading.Thread(target=watch, daemon=True)
            watcher.start()
            try:
                model = rc2.compute()
                if model is not None and not interrupted.is_set():
                    optimum = int(rc2.cost)
                for key, value in rc2.oracle.accum_stats().items():
                    stats[key] = stats.get(key, 0) + int(value)
            finally:
                local_stop.set()
                watcher.join(timeout=1)
                peak[0] = max(peak[0], shared.current_rss_bytes())
        del formula

        if interrupted.is_set():
            unknown_reason = "memory limit" if memory_interrupted.is_set() else "global timeout"
            status = "UNKNOWN"
            break
        iterations += 1
        if model is None or optimum is None:
            status = "UNSAT"
            last_master_optimum = None
            break
        last_master_optimum = optimum
        if optimum > bound:
            status = "UNSAT"
            break

        truth = bytearray(variable_count + 1)
        for literal in model:
            if 0 < literal <= variable_count:
                truth[literal] = 1
        del model
        assignment_cost = sum(weight for variable, weight in var_cost.items() if truth[variable])
        if assignment_cost != optimum:
            raise AssertionError(f"RC2 model cost {assignment_cost} != optimum {optimum}")
        current_indices = []
        uncovered = []
        for family_index, family in enumerate(families):
            option_index = satisfied_option(family, truth)
            current_indices.append(-1 if option_index is None else option_index)
            if option_index is None:
                uncovered.append(family_index)
        if not uncovered:
            status = "SAT"
            selected_indices = current_indices
            final_truth = truth
            break
        for family_index in uncovered:
            clause = separating_clause(families[family_index], truth, variable_count)
            cut_records.append((family_index, clause))
            fingerprint.clause(clause)
            cuts += 1
            max_cut_width = max(max_cut_width, len(clause))
        current = shared.current_rss_bytes()
        peak[0] = max(peak[0], current)
        print(
            f"iteration={iterations} master_optimum={optimum} "
            f"covered={len(families) - len(uncovered)}/{len(families)} "
            f"new_cuts={len(uncovered)} total_cuts={cuts} "
            f"max_cut={max_cut_width} rss_mib={current / 1048576:.1f}",
            flush=True,
        )

    solve_seconds = time.perf_counter() - solve_started
    selection = None
    physical_score = None
    assignment_cost = None
    relaxed_score = None
    if selected_indices is not None and final_truth is not None:
        selection = replay_selection(families, selected_indices, state_bits)
        assignment_cost = sum(weight for variable, weight in var_cost.items() if final_truth[variable])
        relaxed_score = shared.score_selection(selection, include_controls=False)
        physical_score = shared.score_selection(selection, include_controls=True)
        if relaxed_score.core_gate > assignment_cost or assignment_cost > bound:
            raise AssertionError("SAT replay exceeds master assignment cost")

    proven_core_lower = (
        last_master_optimum
        if status == "UNSAT" and last_master_optimum is not None
        else bound + 1 if status == "UNSAT" else None
    )
    metadata: dict[str, object] = {
        "status": status,
        "bound": bound,
        "strict_conclusion": (
            f"relaxed_core>={proven_core_lower}; physical_total>={shared.SHELL_GATE + proven_core_lower}"
            if proven_core_lower is not None
            else None
        ),
        "proven_core_lower_bound": proven_core_lower,
        "formula": {
            "variables": variable_count,
            "lazy_clauses": fingerprint.clauses,
            "native_atmost": fingerprint.atmosts,
            "weighted_soft_clauses": len(var_cost),
            "literal_occurrences": fingerprint.literal_occurrences,
            "weighted_cost_literals": len(cost_literals),
            "sha256": fingerprint.hexdigest(),
            "raw_options": raw_total,
            "reduced_options": reduced_total,
            "compact_option_literals": compact_literals,
            "first_forms": len(form_var),
            "final_types": len(type_var),
            "iterations": iterations,
            "max_cut_width": max_cut_width,
            "last_master_optimum": last_master_optimum,
            "variable_map_sha256": variable_map_digest(form_var, type_var, var_cost),
        },
        "cut_certificate": [
            {
                "target_index": family_index,
                "target": f"{families[family_index].target:09x}",
                "clause": clause,
            }
            for family_index, clause in cut_records
        ],
        "limits": {
            "timeout_seconds": timeout_seconds,
            "memory_mb": memory_mb,
            "interrupted": interrupted.is_set(),
            "memory_interrupted": memory_interrupted.is_set(),
        },
        "runtime": {
            "build_seconds": build_seconds,
            "solve_seconds": solve_seconds,
            "peak_working_set_mb": peak[0] / 1048576,
            "solver_stats": stats,
            "unknown_reason": unknown_reason,
        },
        "sat_assignment_cost": assignment_cost,
        "sat_relaxed_score": shared.score_json(relaxed_score, state_bits) if relaxed_score else None,
        "sat_physical_replay_score": shared.score_json(physical_score, state_bits) if physical_score else None,
    }
    return metadata, selection, physical_score


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--hidden", type=int, default=3)
    parser.add_argument("--bound", type=int, default=shared.CORE_BUDGET)
    parser.add_argument("--timeout-seconds", type=float, default=1800.0)
    parser.add_argument("--memory-mb", type=int, default=680)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 64 <= args.memory_mb <= 700:
        parser.error("--memory-mb must be in [64,700]")
    if args.bound < 0:
        parser.error("--bound must be non-negative")

    h_rows, o_rows = shared.load_candidate(args.candidate, args.hidden)
    targets = tuple(sorted({row for row in (*h_rows, *o_rows) if row.bit_count() >= 2}))
    state_bits = shared.VISIBLE + args.hidden
    metadata, selection, physical_score = solve_lazy(
        targets,
        state_bits,
        bound=args.bound,
        timeout_seconds=args.timeout_seconds,
        memory_mb=args.memory_mb,
    )
    payload: dict[str, object] = {
        "schema": 2,
        "source": str(args.candidate.resolve()),
        "source_sha256": sha256(args.candidate.read_bytes()).hexdigest(),
        "model": "lazy RC2 weighted MaxSAT; complete cancellation-aware depth-two XOR2/Switch-XOR3; all controls free",
        "proof_scope": "strict physical lower bound because NOR/AND control gates are free",
        "state_bits": state_bits,
        "target_count": len(targets),
        "target_weight_histogram": {
            str(weight): sum(target.bit_count() == weight for target in targets)
            for weight in sorted({target.bit_count() for target in targets})
        },
        "cost_contract": {
            "shell_gate": shared.SHELL_GATE,
            "physical_total_target": 430,
            "core_bound": args.bound,
            "scalar_and_u1_word_xor": [shared.PAIR_GATE, 2],
            "u2_u3_u4_u8_word_xor_gate": [6, 9, 12, 24],
            "word_xor_delay": 2,
            "scalar_switch_xor3_base_gate": shared.SWITCH_XOR3_BASE_GATE,
            "NOR_AND_controls": "free relaxation",
            "ram": False,
        },
        "solve": metadata,
    }
    if selection is not None and physical_score is not None:
        payload["certificate"] = {
            "selection": [
                shared.option_json(target, option, state_bits)
                for target, option in zip(targets, selection)
            ],
            "physical_score": shared.score_json(physical_score, state_bits),
            "physical_total_gate": shared.SHELL_GATE + physical_score.core_gate,
            "switch_truth_tables": shared.switch_truth_tables(physical_score, state_bits),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": metadata["status"],
                "strict_conclusion": metadata["strict_conclusion"],
                "peak_working_set_mb": metadata["runtime"]["peak_working_set_mb"],
                "output": str(args.output),
                "output_sha256": sha256(encoded).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )
    return {"SAT": 0, "UNSAT": 20, "UNKNOWN": 30}[str(metadata["status"])]


if __name__ == "__main__":
    raise SystemExit(main())
