#!/usr/bin/env python3
"""Exact cancellation-free lower bound for the 65-cycle visible RNG outputs."""

from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from typing import Sequence

from pysat.examples.rc2 import RC2
from pysat.formula import IDPool, WCNF


BITS = 32
MASK = (1 << BITS) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def transition() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << bit) for bit in range(BITS))
    return tuple(
        sum(((columns[source] >> target) & 1) << source for source in range(BITS))
        for target in range(BITS)
    )


def candidate_forms(targets: Sequence[int]) -> tuple[int, ...]:
    forms: set[int] = set()
    for target in targets:
        bits = [bit for bit in range(BITS) if target >> bit & 1]
        for size in range(1, len(bits) + 1):
            for selected in combinations(bits, size):
                forms.add(sum(1 << bit for bit in selected))
    return tuple(sorted(forms))


def bipartitions(form: int) -> tuple[tuple[int, int], ...]:
    bits = [bit for bit in range(BITS) if form >> bit & 1]
    first, rest = bits[0], bits[1:]
    result = []
    for selector in range(1 << len(rest)):
        left = 1 << first
        for index, bit in enumerate(rest):
            if selector >> index & 1:
                left |= 1 << bit
        if left != form:
            result.append((left, form ^ left))
    return tuple(result)


def encode(targets: Sequence[int]):
    forms = candidate_forms(targets)
    gates = tuple(form for form in forms if form.bit_count() >= 2)
    pool = IDPool()
    formula = WCNF()
    selected = {form: pool.id(("selected", form)) for form in gates}
    choices: dict[int, list[tuple[int, int, int]]] = {}

    for form in gates:
        options = []
        option_literals = []
        for left, right in bipartitions(form):
            choice = pool.id(("split", form, left))
            options.append((choice, left, right))
            option_literals.append(choice)
            formula.append([-choice, selected[form]])
            if left.bit_count() >= 2:
                formula.append([-choice, selected[left]])
            if right.bit_count() >= 2:
                formula.append([-choice, selected[right]])
        formula.append([-selected[form], *option_literals])
        formula.append([-selected[form]], weight=1)
        choices[form] = options
    for target in targets:
        formula.append([selected[target]])
    return forms, gates, pool, formula, selected, choices


def verify_solution(
    targets: Sequence[int],
    chosen: set[int],
    splits: dict[int, tuple[int, int]],
) -> None:
    if not set(targets) <= chosen:
        raise AssertionError("an A target is missing")
    available = {1 << bit for bit in range(BITS)}
    for form in sorted(chosen, key=lambda value: (value.bit_count(), value)):
        left, right = splits[form]
        if left & right or left ^ right != form:
            raise AssertionError("split is not a disjoint union")
        if left not in available or right not in available:
            raise AssertionError("split references an unavailable child")
        available.add(form)
    if not set(targets) <= available:
        raise AssertionError("reconstructed circuit misses an A target")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    targets = transition()
    forms, gates, pool, formula, selected, choices = encode(targets)
    with RC2(formula, solver="g4", adapt=True, exhaust=True, verbose=0) as optimizer:
        model = optimizer.compute()
        optimum = optimizer.cost
    if model is None:
        raise AssertionError("RC2 unexpectedly returned no optimum")
    model_set = {literal for literal in model if literal > 0}
    chosen = {form for form in gates if selected[form] in model_set}
    splits = {}
    for form in chosen:
        valid = [
            (left, right)
            for choice, left, right in choices[form]
            if choice in model_set and (
                left.bit_count() == 1 or left in chosen
            ) and (
                right.bit_count() == 1 or right in chosen
            )
        ]
        if not valid:
            # RC2 may leave an equivalent choice literal false even though the
            # selected child forms already provide a legal decomposition.
            valid = [
                (left, right)
                for _choice, left, right in choices[form]
                if (left.bit_count() == 1 or left in chosen)
                and (right.bit_count() == 1 or right in chosen)
            ]
        if not valid:
            raise AssertionError("selected signal has no selected decomposition")
        splits[form] = min(valid)
    verify_solution(targets, chosen, splits)
    if optimum != len(chosen) or optimum != 61:
        raise AssertionError(f"unexpected cancellation-free optimum {optimum}")

    seed_merge = optimum
    q_injection = BITS
    xor_nodes = seed_merge + q_injection
    logic_gate = xor_nodes * 3
    total_gate = BITS * 5 + logic_gate
    payload = {
        "schema": 1,
        "status": "proved-cancellation-free-lower-bound",
        "model": "65-cycle visible outputs [C65|A], arbitrary invertible C65",
        "seed_projection": {
            "candidate_forms": len(forms),
            "non_singleton_forms": len(gates),
            "decomposition_choices": sum(len(value) for value in choices.values()),
            "variables": pool.top,
            "hard_clauses": len(formula.hard),
            "soft_clauses": len(formula.soft),
            "solver": "RC2 + Glucose 4",
            "optimum_seed_merge_nodes": seed_merge,
            "argument": (
                "Every useful cancellation-free intermediate is a nonempty subset of at least one A row. "
                "The weighted AND/OR DAG selects every required A row and one disjoint bipartition for "
                "each selected non-singleton form, so its optimum is exactly L_cf(A)."
            ),
        },
        "q_injection": {
            "minimum_nodes": q_injection,
            "argument": (
                "Project every signal to its q half. Each q dimension must first cross from a seed-empty "
                "signal into a seed-nonempty signal at an injection gate. All C65 rows lie in the span of "
                "these crossing forms; rank(C65)=32 therefore requires at least 32 injection gates."
            ),
            "disjoint_from_seed_merge": (
                "A seed merge has two seed-nonempty children; an injection has exactly one."
            ),
        },
        "lower_bound": {
            "xor_nodes": xor_nodes,
            "logic_gate": logic_gate,
            "state_gate": BITS * 5,
            "total_gate": total_gate,
            "delay_9_cycles_65_energy_floor": total_gate * 9 * 65,
            "excludes_total_414_delay_9_cycles_65": total_gate > 414,
            "excludes_total_466_delay_8_cycles_65": total_gate > 466,
        },
        "transition_sha256": sha256(
            b"".join(row.to_bytes(4, "little") for row in targets)
        ).hexdigest(),
        "chosen_seed_forms": [f"{form:08x}" for form in sorted(chosen)],
        "chosen_decompositions": [
            {
                "form": f"{form:08x}",
                "left": f"{splits[form][0]:08x}",
                "right": f"{splits[form][1]:08x}",
            }
            for form in sorted(chosen)
        ],
        "scope": (
            "The 93-node result is global for cancellation-free XOR2 DAGs and already follows from the "
            "32 visible outputs. It does not cover XOR cancellation, nonlinear Switch/Z sharing, or a "
            "reachable-sample-specialized Boolean network."
        ),
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "status": payload["status"],
        "L_cf_A": seed_merge,
        "q_injection": q_injection,
        "xor_nodes": xor_nodes,
        "total_gate": total_gate,
        "excludes_414_9_65": payload["lower_bound"]["excludes_total_414_delay_9_cycles_65"],
        "excludes_466_8_65": payload["lower_bound"]["excludes_total_466_delay_8_cycles_65"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
