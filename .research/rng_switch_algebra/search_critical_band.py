"""Exact shared-control search for the depth-three xorshift32 band.

The canonical xorshift circuit has 61 XOR2 gates.  Outputs y0..y11 and
y27..y31 already have depth at most four, while y12..y26 cross all three
canonical shift stages.  This model keeps the 34 XOR2 gates needed by the
already-fast outputs and resynthesizes only that critical band.

Every newly selected first/final node is either XOR2 (3 gates / 2 delay) or
the reviewed four-Switch XOR3 data plane (8 gates).  XOR3 controls are the
three pair NOR functions and one selectable pair AND function.  Equal control
truth tables are shared globally.  A selected XOR2 is implemented by the
reviewed three-gate multi-output cell, so its exact-input AND and NOR nodes may
serve an XOR3 control at no extra gate cost.  The same is true for the 34
fixed XOR2 gates.

This deliberately cancellation-free model is small enough for exact RC2 and
never accesses the game or save directory.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import sys

from pysat.examples.rc2 import RC2
from pysat.formula import IDPool, WCNF


ROOT = Path(__file__).resolve().parents[2]
SHARED_DIR = ROOT / ".research" / "rng_switch_cover_next"
sys.path.insert(0, str(SHARED_DIR))

import search_shared_controls as shared  # noqa: E402


CRITICAL_OUTPUTS = tuple(range(12, 27))
FIXED_FIRST_FORMS = frozenset((1 << bit) ^ (1 << (bit + 13)) for bit in range(17))


@dataclass(frozen=True, slots=True)
class Triple:
    active: int
    sources: tuple[int, int, int]
    tag: tuple[object, ...]


def fixed_xor_pairs() -> tuple[tuple[int, int], ...]:
    """Return the 34 exact input pairs of the retained canonical gates."""

    pairs: list[tuple[int, int]] = []
    # First stage: a_i = x_i XOR x_(i+13), i=0..16.
    pairs.extend((1 << bit, 1 << (bit + 13)) for bit in range(17))
    # Fast low band: y_i = a_i XOR a_(i+5), i=0..11.
    pairs.extend(
        (FIXED_FIRST_MASK(bit), FIXED_FIRST_MASK(bit + 5))
        for bit in range(12)
    )
    # Fast high band: y_i = a_(i-17) XOR x_i, i=27..31.
    pairs.extend((FIXED_FIRST_MASK(bit - 17), 1 << bit) for bit in range(27, 32))
    assert len(pairs) == 34
    return tuple(tuple(sorted(pair)) for pair in pairs)


def FIXED_FIRST_MASK(bit: int) -> int:
    return (1 << bit) ^ (1 << (bit + 13))


def solve(solver_name: str) -> dict[str, object]:
    rows = shared.target_rows()
    choices = tuple(shared.output_options(rows[output]) for output in CRITICAL_OUTPUTS)
    forms = tuple(
        sorted(
            {
                form
                for output_choices in choices
                for option in output_choices
                for form in option.required_forms
            }
        )
    )

    pool = IDPool()
    formula = WCNF()
    option_var = {
        (local_output, option_index): pool.id(("option", local_output, option_index))
        for local_output, output_choices in enumerate(choices)
        for option_index in range(len(output_choices))
    }
    form_var = {form: pool.id(("form", form)) for form in forms}

    form_users: dict[int, list[int]] = defaultdict(list)
    for local_output, output_choices in enumerate(choices):
        variables = [
            option_var[(local_output, option_index)]
            for option_index in range(len(output_choices))
        ]
        formula.append(variables)
        for left_index, left in enumerate(variables):
            for right in variables[left_index + 1 :]:
                formula.append([-left, -right])
        for option_index, option in enumerate(output_choices):
            active = option_var[(local_output, option_index)]
            for form in option.required_forms:
                formula.append([-active, form_var[form]])
                form_users[form].append(active)
            if option.final_arity == 2:
                formula.append([-active], weight=3)
            elif option.final_arity == 3:
                formula.append([-active], weight=8)

    for form in forms:
        active = form_var[form]
        formula.append([-active, *form_users[form]])
        if form not in FIXED_FIRST_FORMS:
            formula.append([-active], weight=3 if form.bit_count() == 2 else 8)

    triples: list[Triple] = []
    for form in forms:
        if form.bit_count() == 3:
            triples.append(
                Triple(
                    active=form_var[form],
                    sources=tuple(shared.bit_masks(form)),
                    tag=("form", form),
                )
            )
    for local_output, output_choices in enumerate(choices):
        for option_index, option in enumerate(output_choices):
            if option.final_arity == 3:
                triples.append(
                    Triple(
                        active=option_var[(local_output, option_index)],
                        sources=option.sources,
                        tag=("output", CRITICAL_OUTPUTS[local_output], option_index),
                    )
                )

    control_var: dict[tuple[int, ...], int] = {}
    control_providers: dict[tuple[int, ...], set[int]] = defaultdict(set)

    def control(kind: str, left: int, right: int) -> int:
        key = shared.control_key(kind, left, right)
        return control_var.setdefault(key, pool.id(("control", key)))

    orientation_var: dict[tuple[tuple[object, ...], int], int] = {}
    for triple in triples:
        orientations = []
        for pair_index, (left, right) in enumerate(
            __import__("itertools").combinations(triple.sources, 2)
        ):
            formula.append([-triple.active, control("NOR", left, right)])
            orientation = pool.id(("orientation", triple.tag, pair_index))
            orientation_var[(triple.tag, pair_index)] = orientation
            orientations.append(orientation)
            formula.append([-orientation, triple.active])
            formula.append([-orientation, control("AND", left, right)])
        formula.append([-triple.active, *orientations])
        for left_index, left in enumerate(orientations):
            for right in orientations[left_index + 1 :]:
                formula.append([-left, -right])

    # Every retained XOR2 exposes exact-input AND and NOR controls for free.
    fixed_control_keys: set[tuple[int, ...]] = set()
    for left, right in fixed_xor_pairs():
        fixed_control_keys.add(shared.control_key("AND", left, right))
        fixed_control_keys.add(shared.control_key("NOR", left, right))

    # Every selected first/final XOR2 can expose the same two controls.
    for form in forms:
        if form.bit_count() != 2:
            continue
        left, right = shared.bit_masks(form)
        provider = form_var[form]
        control_providers[shared.control_key("AND", left, right)].add(provider)
        control_providers[shared.control_key("NOR", left, right)].add(provider)
    for local_output, output_choices in enumerate(choices):
        for option_index, option in enumerate(output_choices):
            if option.final_arity != 2:
                continue
            left, right = option.sources
            provider = option_var[(local_output, option_index)]
            control_providers[shared.control_key("AND", left, right)].add(provider)
            control_providers[shared.control_key("NOR", left, right)].add(provider)

    pay_var: dict[tuple[int, ...], int] = {}
    for key, required in control_var.items():
        if key in fixed_control_keys:
            continue
        providers = sorted(control_providers.get(key, ()))
        if not providers:
            pay_var[key] = required
            formula.append([-required], weight=1)
            continue
        pay = pool.id(("pay", key))
        pay_var[key] = pay
        # pay <=> required AND NOT(any active exact-input XOR2 provider).
        formula.append([-pay, required])
        formula.append([-pay, *(-provider for provider in providers)])
        for provider in providers:
            formula.append([-required, provider, pay])
        formula.append([-pay], weight=1)

    with RC2(
        formula,
        solver=solver_name,
        adapt=True,
        exhaust=True,
        incr=True,
        verbose=0,
    ) as optimizer:
        model = optimizer.compute()
        optimum_increment = optimizer.cost
    if model is None:
        raise RuntimeError("RC2 unexpectedly returned no model")
    positive = {literal for literal in model if literal > 0}

    selected_options = []
    selected_forms = tuple(form for form in forms if form_var[form] in positive)
    for local_output, output_choices in enumerate(choices):
        option_index = next(
            index
            for index in range(len(output_choices))
            if option_var[(local_output, index)] in positive
        )
        option = output_choices[option_index]
        rebuilt = 0
        for source in option.sources:
            rebuilt ^= source
        output = CRITICAL_OUTPUTS[local_output]
        assert rebuilt == rows[output]
        selected_options.append(
            {
                "output": output,
                "target": f"{rows[output]:08x}",
                "option_index": option_index,
                "final_arity": option.final_arity,
                "sources": [f"{source:08x}" for source in option.sources],
            }
        )

    selected_triples = [triple for triple in triples if triple.active in positive]
    triple_records = []
    for triple in selected_triples:
        pair_records = []
        for pair_index, (left, right) in enumerate(
            __import__("itertools").combinations(triple.sources, 2)
        ):
            pair_records.append(
                {
                    "left": f"{left:08x}",
                    "right": f"{right:08x}",
                    "special_and": orientation_var[(triple.tag, pair_index)] in positive,
                }
            )
        assert sum(record["special_and"] for record in pair_records) == 1
        triple_records.append(
            {
                "tag": list(triple.tag),
                "sources": [f"{source:08x}" for source in triple.sources],
                "pairs": pair_records,
            }
        )

    pair_forms = sum(form.bit_count() == 2 for form in selected_forms if form not in FIXED_FIRST_FORMS)
    triple_forms = sum(form.bit_count() == 3 for form in selected_forms)
    final_pair = sum(record["final_arity"] == 2 for record in selected_options)
    final_triple = sum(record["final_arity"] == 3 for record in selected_options)
    paid_controls = tuple(key for key, variable in pay_var.items() if variable in positive)
    rebuilt_increment = (
        3 * pair_forms
        + 8 * triple_forms
        + 3 * final_pair
        + 8 * final_triple
        + len(paid_controls)
    )
    assert rebuilt_increment == optimum_increment
    fixed_gate = 34 * 3
    return {
        "schema": 1,
        "status": "optimal",
        "model": "critical y12..y26 cancellation-free XOR2/shared-control Switch-XOR3",
        "solver": solver_name,
        "critical_outputs": list(CRITICAL_OUTPUTS),
        "fixed": {
            "xor2_count": 34,
            "gate": fixed_gate,
            "first_forms": [f"{form:08x}" for form in sorted(FIXED_FIRST_FORMS)],
        },
        "increment_gate_optimum": optimum_increment,
        "core_gate": fixed_gate + optimum_increment,
        "total_gate_with_198_shell": 198 + fixed_gate + optimum_increment,
        "delay": 4,
        "counts": {
            "new_first_xor2": pair_forms,
            "new_first_switch_xor3": triple_forms,
            "final_xor2": final_pair,
            "final_switch_xor3": final_triple,
            "bit_switch": 4 * (triple_forms + final_triple),
            "paid_shared_control": len(paid_controls),
        },
        "selected_first_forms": [f"{form:08x}" for form in selected_forms],
        "outputs": selected_options,
        "triple_gates": triple_records,
        "paid_controls_anf": [shared.polynomial_text(key) for key in paid_controls],
        "formula": {
            "variables": pool.top,
            "hard_clauses": len(formula.hard),
            "soft_clauses": len(formula.soft),
            "candidate_options": sum(len(value) for value in choices),
            "candidate_forms": len(forms),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", default="g4")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("critical_band_optimum.json"),
    )
    args = parser.parse_args()
    payload = solve(args.solver)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                key: payload[key]
                for key in (
                    "status",
                    "increment_gate_optimum",
                    "core_gate",
                    "total_gate_with_198_shell",
                    "counts",
                    "formula",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
