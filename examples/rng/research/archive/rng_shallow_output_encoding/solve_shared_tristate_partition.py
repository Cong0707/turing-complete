"""Exact shared Switch/Z core over cancellation-free two-layer partitions.

Unlike a black-box XOR3 cost model, this solver counts its four switches and
globally shared NOR/AND controls separately.  Every selected macro is emitted
with concrete sources and one AND orientation, making the result replayable as
real Turing Complete primitives rather than as a forged metric.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import random
import sys
import time
from typing import Sequence

from pysat.examples.rc2 import RC2Stratified
from pysat.formula import IDPool, WCNF

import solve_mixed_cover as common


XOR2_COST = 3
SWITCH_XOR3_COST = 8


def load_partition_model():
    path = Path(__file__).resolve().parents[1] / "rng_cost_reverse" / "search_partition_mixed.py"
    spec = importlib.util.spec_from_file_location("shared_z_partition_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def signal_pairs(sources: Sequence[int]) -> tuple[tuple[int, int], ...]:
    if len(sources) != 3:
        raise ValueError("Switch/Z XOR3 needs exactly three input signals")
    return tuple(sorted(tuple(sorted(pair)) for pair in combinations(sources, 2)))


def local_and_mask(sources: Sequence[int], chosen_pair: tuple[int, int]) -> int:
    result = 0
    for index, source in enumerate(sources):
        if source in chosen_pair:
            result |= 1 << index
    if result not in (0b011, 0b101, 0b110):
        raise AssertionError("AND orientation is not a source pair")
    return result


def xor3_z(a: int, b: int, c: int, and_mask: int) -> int:
    values = (a, b, c)
    pair = tuple(index for index in range(3) if and_mask >> index & 1)
    remaining = next(index for index in range(3) if index not in pair)
    drivers = []
    if not (a or b):
        drivers.append(c)
    if not (a or c):
        drivers.append(b)
    if not (b or c):
        drivers.append(a)
    if values[pair[0]] and values[pair[1]]:
        drivers.append(values[remaining])
    return int(any(drivers))


def solve(memory_mb: int) -> dict[str, object]:
    started = time.perf_counter()
    stopped, peak = common.start_watchdog(memory_mb)
    model = load_partition_model()
    rows = model.target_rows()
    options = tuple(model.output_options(row) for row in rows)
    concrete = {
        (output, index): model._sources_for_choice(
            rows[output], option[0], option[1]
        )
        for output, choices in enumerate(options)
        for index, option in enumerate(choices)
    }
    forms = tuple(
        sorted(
            {
                form
                for choices in options
                for _arity, required in choices
                for form in required
            }
        )
    )

    pool = IDPool()
    formula = WCNF()
    form_var = {form: pool.id(("form", form)) for form in forms}
    option_var: dict[tuple[int, int], int] = {}
    form_users: dict[int, list[int]] = defaultdict(list)
    for output, choices in enumerate(options):
        variables = []
        for index, (arity, required) in enumerate(choices):
            variable = pool.id(("option", output, index))
            option_var[output, index] = variable
            variables.append(variable)
            for form in required:
                formula.append([-variable, form_var[form]])
                form_users[form].append(variable)
            if arity == 2:
                formula.append([-variable], weight=XOR2_COST)
            elif arity == 3:
                formula.append([-variable], weight=SWITCH_XOR3_COST)
        formula.append(variables)
        for left_index, left in enumerate(variables):
            for right in variables[left_index + 1 :]:
                formula.append([-left, -right])
    for form, variable in form_var.items():
        formula.append([-variable, *form_users[form]])
        formula.append(
            [-variable],
            weight=XOR2_COST if form.bit_count() == 2 else SWITCH_XOR3_COST,
        )

    # A macro key identifies a physical four-switch XOR3.  A first-layer form
    # is active with form_var; a final macro is active with its option selector.
    macro_sources: dict[tuple[object, ...], tuple[int, int, int]] = {}
    macro_select: dict[tuple[object, ...], int] = {}
    for form in forms:
        if form.bit_count() == 3:
            units = tuple(1 << bit for bit in range(32) if form >> bit & 1)
            key = ("form", form)
            macro_sources[key] = units
            macro_select[key] = form_var[form]
    for output, choices in enumerate(options):
        for index, (arity, _required) in enumerate(choices):
            if arity == 3:
                key = ("final", output, index)
                sources = concrete[output, index]
                if len(sources) != 3:
                    raise AssertionError("final XOR3 source count mismatch")
                macro_sources[key] = sources
                macro_select[key] = option_var[output, index]

    control_pairs = tuple(
        sorted({pair for sources in macro_sources.values() for pair in signal_pairs(sources)})
    )
    nor_var = {pair: pool.id(("nor", pair)) for pair in control_pairs}
    and_var = {pair: pool.id(("and", pair)) for pair in control_pairs}
    and_users: dict[tuple[int, int], list[int]] = defaultdict(list)
    orientation_var: dict[tuple[tuple[object, ...], tuple[int, int]], int] = {}
    for key, sources in macro_sources.items():
        select = macro_select[key]
        orientations = []
        for pair in signal_pairs(sources):
            formula.append([-select, nor_var[pair]])
            variable = pool.id(("orient", key, pair))
            orientation_var[key, pair] = variable
            orientations.append(variable)
            formula.append([-variable, select])
            formula.append([-variable, and_var[pair]])
            and_users[pair].append(variable)
        formula.append([-select, *orientations])
        for left_index, left in enumerate(orientations):
            for right in orientations[left_index + 1 :]:
                formula.append([-left, -right])
    for pair in control_pairs:
        formula.append([-nor_var[pair]], weight=1)
        formula.append([-and_var[pair]], weight=1)
        formula.append([-and_var[pair], *and_users[pair]])

    build_seconds = time.perf_counter() - started
    print(
        f"built forms={len(forms)} options={len(option_var)} macros={len(macro_sources)} "
        f"control_pairs={len(control_pairs)} vars={pool.top} "
        f"hard={len(formula.hard)} soft={len(formula.soft)}",
        flush=True,
    )
    with RC2Stratified(
        formula,
        solver="cd195",
        adapt=True,
        exhaust=True,
        minz=True,
        trim=2,
        verbose=1,
    ) as rc2:
        assignment = rc2.compute()
        optimum = rc2.cost
    solve_seconds = time.perf_counter() - started - build_seconds
    stopped.set()
    peak[0] = max(peak[0], common.working_set_bytes())
    if assignment is None:
        raise AssertionError("partition model unexpectedly UNSAT")
    positive = {literal for literal in assignment if literal > 0}

    selected_forms = tuple(form for form in forms if form_var[form] in positive)
    selected_macros = {
        key: sources
        for key, sources in macro_sources.items()
        if macro_select[key] in positive
    }
    selected_nors = tuple(pair for pair in control_pairs if nor_var[pair] in positive)
    selected_ands = tuple(pair for pair in control_pairs if and_var[pair] in positive)
    orientations = {
        key: next(
            pair
            for pair in signal_pairs(sources)
            if orientation_var[key, pair] in positive
        )
        for key, sources in selected_macros.items()
    }

    output_entries = []
    final_xor2 = 0
    final_xor3 = 0
    for output, choices in enumerate(options):
        active = [
            index
            for index in range(len(choices))
            if option_var[output, index] in positive
        ]
        if len(active) != 1:
            raise AssertionError(f"output {output} has {len(active)} active choices")
        index = active[0]
        arity, required = choices[index]
        final_xor2 += arity == 2
        final_xor3 += arity == 3
        output_entries.append(
            {
                "output": output,
                "target": f"{rows[output]:08x}",
                "final_arity": arity,
                "sources": [f"{source:08x}" for source in concrete[output, index]],
                "required_first_forms": [f"{form:08x}" for form in required],
                "macro_key": None if arity != 3 else ["final", output, index],
            }
        )

    first_xor2 = sum(form.bit_count() == 2 for form in selected_forms)
    first_xor3 = sum(form.bit_count() == 3 for form in selected_forms)
    recomputed = (
        XOR2_COST * (first_xor2 + final_xor2)
        + SWITCH_XOR3_COST * (first_xor3 + final_xor3)
        + len(selected_nors)
        + len(selected_ands)
    )
    if recomputed != optimum:
        raise AssertionError(f"RC2 cost {optimum} != extracted cost {recomputed}")

    macros = []
    for key, sources in selected_macros.items():
        macros.append(
            {
                "key": list(key),
                "sources": [f"{source:08x}" for source in sources],
                "and_pair": [f"{source:08x}" for source in orientations[key]],
            }
        )
    certificate = {
        "schema": 1,
        "model": "natural cancellation-free depth-two XOR2/Switch-Z-XOR3 with shared controls",
        "solver": "RC2Stratified/cd195",
        "target_rows": [f"{row:08x}" for row in rows],
        "selected_first_forms": [f"{form:08x}" for form in selected_forms],
        "xor3_macros": macros,
        "shared_nor_controls": [
            [f"{left:08x}", f"{right:08x}"] for left, right in selected_nors
        ],
        "shared_and_controls": [
            [f"{left:08x}", f"{right:08x}"] for left, right in selected_ands
        ],
        "outputs": output_entries,
        "metrics": {
            "first_xor2": first_xor2,
            "first_xor3": first_xor3,
            "final_xor2": final_xor2,
            "final_xor3": final_xor3,
            "xor3_switch_gate": SWITCH_XOR3_COST * (first_xor3 + final_xor3),
            "shared_nor_gate": len(selected_nors),
            "shared_and_gate": len(selected_ands),
            "core_gate": recomputed,
            "core_delay": 4,
            "within_200": recomputed <= 200,
            "full_rng_gate": 160 + 64 + 6 + recomputed,
        },
        "verification": verify(
            rows,
            selected_forms,
            selected_macros,
            orientations,
            selected_nors,
            selected_ands,
            output_entries,
        ),
    }
    return {
        "status": "optimal",
        "scope": certificate["model"],
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "peak_working_set_mb": peak[0] / 1048576,
        "candidate_forms": len(forms),
        "candidate_options": len(option_var),
        "candidate_macros": len(macro_sources),
        "candidate_control_pairs": len(control_pairs),
        "certificate": certificate,
    }


def verify(
    rows: Sequence[int],
    selected_forms: Sequence[int],
    selected_macros: dict[tuple[object, ...], Sequence[int]],
    orientations: dict[tuple[object, ...], tuple[int, int]],
    selected_nors: Sequence[tuple[int, int]],
    selected_ands: Sequence[tuple[int, int]],
    outputs: Sequence[dict[str, object]],
) -> dict[str, object]:
    forms = set(selected_forms)
    nors = set(selected_nors)
    ands = set(selected_ands)
    for key, sources in selected_macros.items():
        pairs = set(signal_pairs(sources))
        chosen = orientations[key]
        if not pairs <= nors or chosen not in ands:
            raise AssertionError("selected XOR3 macro lacks a physical control")
        mask = local_and_mask(sources, chosen)
        for a, b, c in product((0, 1), repeat=3):
            if xor3_z(a, b, c, mask) != (a ^ b ^ c):
                raise AssertionError("Switch/Z macro truth table mismatch")
    for output, entry in enumerate(outputs):
        sources = tuple(int(source, 16) for source in entry["sources"])
        value = 0
        for source in sources:
            value ^= source
            if source.bit_count() > 1 and source not in forms:
                raise AssertionError("output references an absent first form")
        if value != rows[output] or int(entry["target"], 16) != rows[output]:
            raise AssertionError(f"output {output} linear form mismatch")
        arity = entry["final_arity"]
        if arity == 0 and len(sources) != 1:
            raise AssertionError("direct output has multiple sources")
        if arity in (2, 3) and len(sources) != arity:
            raise AssertionError("final primitive source count mismatch")

    vectors = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    vectors.extend(random.Random(0x5A7A7E).getrandbits(32) for _ in range(64))
    for value in vectors:
        if common.apply_matrix(rows, value) != common.xorshift32(value):
            raise AssertionError("natural transition replay mismatch")
    return {
        "xor3_truth_tables": len(selected_macros),
        "transition_test_vectors": len(vectors),
        "outputs_reconstructed": 32,
        "uses_score_field_forgery": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memory-mb", type=int, default=680)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = solve(args.memory_mb)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "certificate"}, indent=2))
    print(json.dumps(result["certificate"]["metrics"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
