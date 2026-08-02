"""Exact disjoint-partition search for a depth-two xorshift32 core.

This is a deliberately bounded research model.  Every first-level form is an
XOR2 or the reviewed 12/2 XOR3, and every final gate is XOR2 or XOR3.  The
inputs of a final gate must partition the target support, so this model does
not include cancellation through bits outside the target row.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import product
import json
import math
from pathlib import Path
import random


BITS = 32
MASK = (1 << BITS) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def target_rows() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << source) for source in range(BITS))
    return tuple(
        sum(((columns[source] >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


@dataclass(frozen=True)
class Option:
    final_arity: int
    blocks: tuple[int, ...]

    @property
    def required_forms(self) -> tuple[int, ...]:
        return tuple(block for block in self.blocks if block.bit_count() >= 2)

    @property
    def final_units(self) -> int:
        if self.final_arity == 0:
            return 0
        return 1 if self.final_arity == 2 else 4


def partitions(row: int, count: int) -> tuple[tuple[int, ...], ...]:
    bits = tuple(bit for bit in range(BITS) if (row >> bit) & 1)
    values: set[tuple[int, ...]] = set()
    for owners in product(range(count), repeat=len(bits)):
        if set(owners) != set(range(count)):
            continue
        blocks = [0] * count
        for bit, owner in zip(bits, owners):
            blocks[owner] |= 1 << bit
        if max(block.bit_count() for block in blocks) > 3:
            continue
        values.add(tuple(sorted(blocks)))
    return tuple(sorted(values))


def options_for(row: int) -> tuple[Option, ...]:
    result: list[Option] = []
    if row.bit_count() in {2, 3}:
        result.append(Option(0, (row,)))
    for arity in (2, 3):
        result.extend(Option(arity, blocks) for blocks in partitions(row, arity))
    return tuple(result)


def form_units(form: int) -> int:
    weight = form.bit_count()
    if weight == 2:
        return 1
    if weight == 3:
        return 4
    raise ValueError(f"unsupported first-level form weight {weight}")


def certificate_for(
    rows: tuple[int, ...],
    selected_options: list[Option],
    budget_gate: int,
) -> dict[str, object]:
    used_forms = frozenset(
        form for option in selected_options for form in option.required_forms
    )
    primary_units = sum(form_units(form) for form in used_forms)
    final_units = sum(option.final_units for option in selected_options)
    return {
        "model": "natural-state disjoint depth-two XOR2/XOR3",
        "budget_gate": budget_gate,
        "actual_gate": 3 * (primary_units + final_units),
        "primary_gate": 3 * primary_units,
        "final_gate": 3 * final_units,
        "maximum_delay": 4,
        "forms": [f"{form:08x}" for form in sorted(used_forms)],
        "outputs": [
            {
                "row": index,
                "target": f"{rows[index]:08x}",
                "final_arity": option.final_arity,
                "blocks": [f"{block:08x}" for block in option.blocks],
            }
            for index, option in enumerate(selected_options)
        ],
    }


def heuristic(
    budget_gate: int,
    restarts: int,
    moves: int,
    seed: int,
    output: Path | None,
) -> int:
    rows = target_rows()
    options = tuple(options_for(row) for row in rows)
    generator = random.Random(seed)

    def standalone(option: Option) -> int:
        return option.final_units + sum(
            form_units(form) for form in option.required_forms
        )

    best_score = 1 << 30
    best_selection: list[Option] | None = None
    for restart in range(restarts):
        if restart == 0:
            selection = [min(row_options, key=standalone) for row_options in options]
        else:
            selection = [
                generator.choice(
                    sorted(row_options, key=standalone)[: min(12, len(row_options))]
                )
                for row_options in options
            ]
        counts: dict[int, int] = {}
        for option in selection:
            for form in option.required_forms:
                counts[form] = counts.get(form, 0) + 1
        score = sum(option.final_units for option in selection) + sum(
            form_units(form) for form in counts
        )
        if score < best_score:
            best_score = score
            best_selection = list(selection)
            print(
                f"best_units={best_score} best_gate={best_score * 3} "
                f"restart={restart} move=initial",
                flush=True,
            )

        for move in range(moves):
            temperature = max(0.15, 4.0 * (1.0 - move / moves))
            row = generator.randrange(BITS)
            old = selection[row]
            candidate = generator.choice(options[row])
            if candidate == old:
                continue
            delta = candidate.final_units - old.final_units
            old_forms = frozenset(old.required_forms)
            candidate_forms = frozenset(candidate.required_forms)
            for form in old_forms | candidate_forms:
                before = counts.get(form, 0)
                after = before - int(form in old_forms) + int(form in candidate_forms)
                if before and not after:
                    delta -= form_units(form)
                elif not before and after:
                    delta += form_units(form)
            if delta > 0 and generator.random() >= math.exp(-delta / temperature):
                continue
            for form in old.required_forms:
                counts[form] -= 1
                if counts[form] == 0:
                    del counts[form]
            for form in candidate.required_forms:
                counts[form] = counts.get(form, 0) + 1
            selection[row] = candidate
            score += delta
            if score < best_score:
                best_score = score
                best_selection = list(selection)
                print(
                    f"best_units={best_score} best_gate={best_score * 3} "
                    f"restart={restart} move={move}",
                    flush=True,
                )
                if best_score * 3 <= budget_gate:
                    break
        if best_score * 3 <= budget_gate:
            break

    assert best_selection is not None
    certificate = certificate_for(rows, best_selection, budget_gate)
    certificate["search"] = {
        "kind": "simulated annealing upper bound",
        "seed": seed,
        "restarts": restart + 1,
        "moves_per_restart": moves,
    }
    print(json.dumps(certificate, indent=2), flush=True)
    if output is not None:
        output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    return 0 if best_score * 3 <= budget_gate else 1


def solve(budget_gate: int, timeout_ms: int, output: Path | None) -> int:
    try:
        import z3
    except ImportError as error:
        raise SystemExit("requires z3-solver") from error

    if budget_gate % 3:
        raise SystemExit("the XOR2/XOR3-only budget must be divisible by 3")
    budget_units = budget_gate // 3
    rows = target_rows()
    options = tuple(options_for(row) for row in rows)
    forms = tuple(
        sorted(
            {
                form
                for row_options in options
                for option in row_options
                for form in option.required_forms
            }
        )
    )
    form_vars = {form: z3.Bool(f"p_{form:08x}") for form in forms}
    option_vars = tuple(
        tuple(z3.Bool(f"y{row_index:02d}_o{index}") for index in range(len(row_options)))
        for row_index, row_options in enumerate(options)
    )

    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    for row_vars in option_vars:
        solver.add(z3.PbEq([(variable, 1) for variable in row_vars], 1))
    for row_options, row_vars in zip(options, option_vars):
        for option, variable in zip(row_options, row_vars):
            for form in option.required_forms:
                solver.add(z3.Implies(variable, form_vars[form]))

    weighted = [
        *((variable, form_units(form)) for form, variable in form_vars.items()),
        *(
            (variable, option.final_units)
            for row_options, row_vars in zip(options, option_vars)
            for option, variable in zip(row_options, row_vars)
        ),
    ]
    solver.add(z3.PbLe(weighted, budget_units))
    print(
        json.dumps(
            {
                "budget_gate": budget_gate,
                "budget_units": budget_units,
                "primary_form_count": len(forms),
                "option_count": sum(map(len, options)),
                "options_by_row": [len(value) for value in options],
            },
            indent=2,
        ),
        flush=True,
    )
    result = solver.check()
    print(f"result={result}", flush=True)
    if result == z3.unknown:
        print(f"reason_unknown={solver.reason_unknown()}", flush=True)
        return 2
    if result == z3.unsat:
        return 1

    model = solver.model()
    selected_options: list[Option] = []
    for row_options, row_vars in zip(options, option_vars):
        selected_options.append(
            next(
                option
                for option, variable in zip(row_options, row_vars)
                if z3.is_true(model.eval(variable))
            )
        )
    certificate = certificate_for(rows, selected_options, budget_gate)
    print(json.dumps(certificate, indent=2), flush=True)
    if output is not None:
        output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget-gate", type=int, default=201)
    parser.add_argument("--timeout-ms", type=int, default=180_000)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--heuristic", action="store_true")
    parser.add_argument("--restarts", type=int, default=64)
    parser.add_argument("--moves", type=int, default=100_000)
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x5EED)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.heuristic:
        raise SystemExit(
            heuristic(
                arguments.budget_gate,
                arguments.restarts,
                arguments.moves,
                arguments.seed,
                arguments.output,
            )
        )
    raise SystemExit(solve(arguments.budget_gate, arguments.timeout_ms, arguments.output))
