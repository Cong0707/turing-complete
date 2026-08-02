"""Exact natural xorshift32 core with cross-XOR3 Switch/Z control sharing.

The public 12/2 XOR3 is not treated as an indivisible 12-gate component.  For
``xor3(a,b,c)`` its physical implementation is:

* four Bit Switches: 8 gates;
* NOR(a,b), NOR(a,c), NOR(b,c): one gate each;
* one of AND(a,b), AND(a,c), AND(b,c): one gate.

NOR and AND controls with identical raw input pairs may fan out to several
XOR3 output buses.  RC2 minimizes that real shared structure together with
ordinary 3/2 XOR2 gates.  Only a direct first layer plus an optional final
XOR2 is allowed, so every combinational path is at most four delay.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import importlib.util
import json
from itertools import combinations, product
from pathlib import Path
import sys
import time
from typing import Sequence

from pysat.examples.rc2 import RC2Stratified
from pysat.formula import IDPool, WCNF

import solve_mixed_cover as watchdog


BITS = 32
XOR2_COST = 3
XOR3_SWITCH_COST = 8
CONTROL_COST = 1


def load_linear_model():
    path = Path(__file__).resolve().parents[1] / "rng_xor3_retime" / "depth2_mixed" / "search_depth2_mixed.py"
    spec = importlib.util.spec_from_file_location("shared_z_linear_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def bit_pair_masks(triple: int) -> tuple[int, ...]:
    units = tuple(1 << bit for bit in range(BITS) if triple >> bit & 1)
    if len(units) != 3:
        raise ValueError(f"{triple:08x} is not a raw three-input form")
    return tuple(sorted(left | right for left, right in combinations(units, 2)))


def build_options(model):
    sources, primary_cost = model.forms()
    rows = model.target_rows()
    records: list[list[tuple[int, tuple[int, ...]]]] = []
    for row in rows:
        raw = model.enumerate_options(row, sources, primary_cost)
        direct = model.minimal_requirements(raw, 0)
        xor2 = model.minimal_requirements(raw, 3)
        choices = [(0, required) for required in direct]
        choices.extend((3, required) for required in xor2)
        if not choices:
            raise AssertionError(f"target {row:08x} has no direct/XOR2 shallow option")
        records.append(choices)
    return rows, sources, primary_cost, records


def concrete_sources(
    target: int,
    final_cost: int,
    required: tuple[int, ...],
    sources: Sequence[int],
    primary_cost: dict[int, int],
) -> tuple[int, ...]:
    if final_cost == 0:
        if required != (target,):
            raise AssertionError("direct output requirement mismatch")
        return (target,)
    if final_cost != XOR2_COST:
        raise AssertionError("only final XOR2 is modeled")
    source_set = set(sources)
    for left in sources:
        right = target ^ left
        if left >= right or right not in source_set:
            continue
        actual = tuple(
            sorted(value for value in (left, right) if value in primary_cost)
        )
        if actual == required:
            return left, right
    raise AssertionError("selected requirement has no concrete XOR2 source pair")


def xor3_switch_z(a: int, b: int, c: int, and_pair: int) -> int:
    """Truth model of the four mutually-exclusive public XOR3 drivers."""

    values = {0: a, 1: b, 2: c}
    pairs = {(0, 1): a & b, (0, 2): a & c, (1, 2): b & c}
    pair_index = {
        0b011: (0, 1),
        0b101: (0, 2),
        0b110: (1, 2),
    }[and_pair]
    remaining = next(index for index in range(3) if index not in pair_index)
    drivers = []
    if not (a or b):
        drivers.append(c)
    if not (a or c):
        drivers.append(b)
    if not (b or c):
        drivers.append(a)
    if pairs[pair_index]:
        drivers.append(values[remaining])
    active_ones = [value for value in drivers if value]
    return 1 if active_ones else 0


def solve(memory_mb: int) -> dict[str, object]:
    started = time.perf_counter()
    stopped, peak = watchdog.start_watchdog(memory_mb)
    linear = load_linear_model()
    rows, sources, primary_cost, records = build_options(linear)
    used_forms = tuple(
        sorted(
            {
                form
                for choices in records
                for _final_cost, required in choices
                for form in required
            }
        )
    )
    pair_forms = tuple(form for form in used_forms if form.bit_count() == 2)
    triple_forms = tuple(form for form in used_forms if form.bit_count() == 3)

    pool = IDPool()
    formula = WCNF()
    form_var = {form: pool.id(("form", form)) for form in used_forms}
    option_var: dict[tuple[int, int], int] = {}
    form_users: dict[int, list[int]] = defaultdict(list)
    for output, choices in enumerate(records):
        variables = []
        for option_index, (final_cost, required) in enumerate(choices):
            variable = pool.id(("option", output, option_index))
            option_var[output, option_index] = variable
            variables.append(variable)
            for form in required:
                formula.append([-variable, form_var[form]])
                form_users[form].append(variable)
            if final_cost:
                formula.append([-variable], weight=final_cost)
        formula.append(variables)
        for left_index, left in enumerate(variables):
            for right in variables[left_index + 1 :]:
                formula.append([-left, -right])
    for form in used_forms:
        formula.append([-form_var[form], *form_users[form]])

    for form in pair_forms:
        formula.append([-form_var[form]], weight=XOR2_COST)
    for form in triple_forms:
        formula.append([-form_var[form]], weight=XOR3_SWITCH_COST)

    control_pairs = tuple(
        sorted({pair for triple in triple_forms for pair in bit_pair_masks(triple)})
    )
    nor_var = {pair: pool.id(("nor", pair)) for pair in control_pairs}
    and_var = {pair: pool.id(("and", pair)) for pair in control_pairs}
    and_users: dict[int, list[int]] = defaultdict(list)
    and_choice: dict[tuple[int, int], int] = {}
    for triple in triple_forms:
        choices = []
        for pair in bit_pair_masks(triple):
            formula.append([-form_var[triple], nor_var[pair]])
            variable = pool.id(("and_choice", triple, pair))
            and_choice[triple, pair] = variable
            choices.append(variable)
            formula.append([-variable, form_var[triple]])
            formula.append([-variable, and_var[pair]])
            and_users[pair].append(variable)
        formula.append([-form_var[triple], *choices])
        for left_index, left in enumerate(choices):
            for right in choices[left_index + 1 :]:
                formula.append([-left, -right])
    for pair in control_pairs:
        formula.append([-nor_var[pair]], weight=CONTROL_COST)
        formula.append([-and_var[pair]], weight=CONTROL_COST)
        if and_users[pair]:
            formula.append([-and_var[pair], *and_users[pair]])
        else:
            formula.append([-and_var[pair]])

    build_seconds = time.perf_counter() - started
    print(
        f"built forms={len(used_forms)} triples={len(triple_forms)} "
        f"controls={len(control_pairs)} options={len(option_var)} vars={pool.top} "
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
    peak[0] = max(peak[0], watchdog.working_set_bytes())
    if assignment is None:
        raise AssertionError("hard shared-tristate model unexpectedly UNSAT")
    positive = {literal for literal in assignment if literal > 0}

    selected_forms = tuple(form for form in used_forms if form_var[form] in positive)
    selected_nors = tuple(pair for pair in control_pairs if nor_var[pair] in positive)
    selected_ands = tuple(pair for pair in control_pairs if and_var[pair] in positive)
    orientations = {
        triple: next(
            pair
            for pair in bit_pair_masks(triple)
            if and_choice[triple, pair] in positive
        )
        for triple in selected_forms
        if triple.bit_count() == 3
    }
    outputs = []
    final_xor2 = 0
    for output, choices in enumerate(records):
        active = [
            index
            for index in range(len(choices))
            if option_var[output, index] in positive
        ]
        if len(active) != 1:
            raise AssertionError(f"output {output} has {len(active)} options")
        final_cost, required = choices[active[0]]
        concrete = concrete_sources(
            rows[output], final_cost, required, sources, primary_cost
        )
        if final_cost:
            final_xor2 += 1
        outputs.append(
            {
                "output": output,
                "target": f"{rows[output]:08x}",
                "final": "direct" if final_cost == 0 else "xor2",
                "sources": [f"{source:08x}" for source in concrete],
                "required_first_forms": [f"{form:08x}" for form in required],
            }
        )

    selected_pair_forms = sum(form.bit_count() == 2 for form in selected_forms)
    selected_triple_forms = sum(form.bit_count() == 3 for form in selected_forms)
    recomputed = (
        XOR2_COST * (selected_pair_forms + final_xor2)
        + XOR3_SWITCH_COST * selected_triple_forms
        + len(selected_nors)
        + len(selected_ands)
    )
    if recomputed != optimum:
        raise AssertionError(f"RC2 cost {optimum} != extracted {recomputed}")

    certificate = {
        "schema": 1,
        "model": "natural depth-two XOR2 plus cross-macro shared Switch/Z XOR3 controls",
        "solver": "RC2Stratified/cd195",
        "target_rows": [f"{row:08x}" for row in rows],
        "selected_first_forms": [f"{form:08x}" for form in selected_forms],
        "xor3_and_orientation": {
            f"{triple:08x}": f"{pair:08x}" for triple, pair in sorted(orientations.items())
        },
        "shared_nor_controls": [f"{pair:08x}" for pair in selected_nors],
        "shared_and_controls": [f"{pair:08x}" for pair in selected_ands],
        "outputs": outputs,
        "metrics": {
            "first_xor2": selected_pair_forms,
            "first_xor3": selected_triple_forms,
            "final_xor2": final_xor2,
            "xor3_switch_gate": XOR3_SWITCH_COST * selected_triple_forms,
            "shared_nor_gate": len(selected_nors),
            "shared_and_gate": len(selected_ands),
            "core_gate": recomputed,
            "core_delay": 4,
            "within_200": recomputed <= 200,
            "full_rng_gate": 160 + 64 + 6 + recomputed,
        },
        "timing": {
            "first_layer": 2,
            "final_xor2": 2,
            "maximum_combination": 4,
        },
        "verification": verify(
            rows,
            selected_forms,
            orientations,
            selected_nors,
            selected_ands,
            outputs,
        ),
    }
    return {
        "status": "optimal",
        "scope": certificate["model"],
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "peak_working_set_mb": peak[0] / 1048576,
        "candidate_form_count": len(used_forms),
        "candidate_option_count": len(option_var),
        "certificate": certificate,
    }


def verify(
    rows: Sequence[int],
    selected_forms: Sequence[int],
    orientations: dict[int, int],
    selected_nors: Sequence[int],
    selected_ands: Sequence[int],
    outputs: Sequence[dict[str, object]],
) -> dict[str, object]:
    selected = set(selected_forms)
    nors = set(selected_nors)
    ands = set(selected_ands)
    for triple, orientation in orientations.items():
        pairs = set(bit_pair_masks(triple))
        if triple not in selected or orientation not in pairs:
            raise AssertionError("invalid XOR3 AND orientation")
        if not pairs <= nors or orientation not in ands:
            raise AssertionError("XOR3 physical controls are absent")
        local_orientation = 0
        units = tuple(1 << bit for bit in range(BITS) if triple >> bit & 1)
        for index, unit in enumerate(units):
            if orientation & unit:
                local_orientation |= 1 << index
        for a, b, c in product((0, 1), repeat=3):
            if xor3_switch_z(a, b, c, local_orientation) != (a ^ b ^ c):
                raise AssertionError("Switch/Z XOR3 truth table mismatch")

    if len(outputs) != BITS:
        raise AssertionError("output count mismatch")
    for output, entry in enumerate(outputs):
        sources = tuple(int(source, 16) for source in entry["sources"])
        actual = 0
        for source in sources:
            actual ^= source
            if source.bit_count() > 1 and source not in selected:
                raise AssertionError("output uses absent first-layer form")
        if actual != rows[output] or int(entry["target"], 16) != rows[output]:
            raise AssertionError(f"output {output} linear form mismatch")
        if (entry["final"] == "direct") != (len(sources) == 1):
            raise AssertionError("output final gate mismatch")

    test_values = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    test_values.extend(__import__("random").Random(0x5A7A7E).getrandbits(BITS) for _ in range(64))
    for value in test_values:
        if watchdog.apply_matrix(rows, value) != watchdog.xorshift32(value):
            raise AssertionError("natural transition replay mismatch")
    return {
        "xor3_truth_tables": len(orientations),
        "transition_test_vectors": len(test_values),
        "outputs_reconstructed": BITS,
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
