"""Low-memory depth-two XOR2/XOR3 synthesis for the natural RNG map.

The model is deliberately narrower than the existing cancellation-capable
``search_depth2_mixed.py`` model.  Every output is represented by a disjoint
partition of its support into two or three source forms.  First-layer forms
have weight two (XOR2) or three (the reviewed 12/2 XOR3).  This restriction
keeps the instance small enough to audit and makes every SAT model directly
convertible into a gate list.

Research only: this script does not read or write the game save.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
import argparse
import json
from pathlib import Path
from typing import Iterable


BITS = 32
MASK = (1 << BITS) - 1
XOR2_COST = 3
XOR3_COST = 12


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


def bit_masks(value: int) -> tuple[int, ...]:
    return tuple(1 << bit for bit in range(BITS) if value & (1 << bit))


def set_partitions(items: tuple[int, ...], block_count: int) -> Iterable[tuple[int, ...]]:
    """Yield canonical set partitions as sorted tuples of block masks."""

    blocks: list[list[int]] = []

    def visit(index: int) -> Iterable[tuple[int, ...]]:
        if index == len(items):
            if len(blocks) == block_count and all(1 <= len(block) <= 3 for block in blocks):
                yield tuple(sorted(sum(block) for block in blocks))
            return

        item = items[index]
        for block in blocks:
            if len(block) >= 3:
                continue
            block.append(item)
            yield from visit(index + 1)
            block.pop()
        if len(blocks) < block_count:
            blocks.append([item])
            yield from visit(index + 1)
            blocks.pop()

    yield from visit(0)


def output_options(row: int) -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Return ``(final arity, required first-layer forms)`` choices."""

    weight = row.bit_count()
    if weight == 1:
        return ((0, ()),)

    result: set[tuple[int, tuple[int, ...]]] = set()
    if weight in {2, 3}:
        result.add((0, (row,)))
    for arity in (2, 3):
        for blocks in set_partitions(bit_masks(row), arity):
            if any(block.bit_count() > 3 for block in blocks):
                continue
            required = tuple(sorted(block for block in blocks if block.bit_count() > 1))
            result.add((arity, required))
    return tuple(sorted(result, key=lambda item: (item[0], len(item[1]), item[1])))


def gate_cost(arity: int) -> int:
    if arity == 2:
        return XOR2_COST
    if arity == 3:
        return XOR3_COST
    if arity == 0:
        return 0
    raise ValueError(f"unsupported XOR arity {arity}")


def solve(
    *,
    timeout_ms: int,
    exact_xor2: int | None,
    exact_xor3: int | None,
    max_cost: int | None,
) -> dict[str, object]:
    try:
        from z3 import Bool, Implies, Or, PbEq, PbLe, Tactic, sat, unsat
    except ImportError as error:  # pragma: no cover - environment dependent
        raise SystemExit("requires z3-solver") from error

    rows = target_rows()
    options = tuple(output_options(row) for row in rows)
    forms = tuple(sorted({form for choices in options for _, needed in choices for form in needed}))
    form_var = {form: Bool(f"f_{form:08x}") for form in forms}
    choice_var = {
        (output, option): Bool(f"y{output:02d}_o{option:04d}")
        for output, choices in enumerate(options)
        for option in range(len(choices))
    }

    solver = Tactic("sat").solver()
    solver.set(timeout=timeout_ms)
    for output, choices in enumerate(options):
        solver.add(PbEq([(choice_var[(output, option)], 1) for option in range(len(choices))], 1))

    users: dict[int, list[object]] = defaultdict(list)
    for output, choices in enumerate(options):
        for option, (_arity, needed) in enumerate(choices):
            selected = choice_var[(output, option)]
            for form in needed:
                solver.add(Implies(selected, form_var[form]))
                users[form].append(selected)
    for form in forms:
        solver.add(form_var[form] == Or(*users[form]))

    xor2_literals = [form_var[form] for form in forms if form.bit_count() == 2]
    xor3_literals = [form_var[form] for form in forms if form.bit_count() == 3]
    xor2_literals.extend(
        choice_var[(output, option)]
        for output, choices in enumerate(options)
        for option, (arity, _needed) in enumerate(choices) if arity == 2
    )
    xor3_literals.extend(
        choice_var[(output, option)]
        for output, choices in enumerate(options)
        for option, (arity, _needed) in enumerate(choices) if arity == 3
    )

    if exact_xor2 is not None:
        solver.add(PbEq([(literal, 1) for literal in xor2_literals], exact_xor2))
    if exact_xor3 is not None:
        solver.add(PbEq([(literal, 1) for literal in xor3_literals], exact_xor3))
    if max_cost is not None:
        solver.add(
            PbLe(
                [(literal, XOR2_COST) for literal in xor2_literals]
                + [(literal, XOR3_COST) for literal in xor3_literals],
                max_cost,
            )
        )

    result = solver.check()
    payload: dict[str, object] = {
        "model": "depth-two, cancellation-free support partitions",
        "status": str(result),
        "timeout_ms": timeout_ms,
        "constraints": {
            "exact_xor2": exact_xor2,
            "exact_xor3": exact_xor3,
            "max_cost": max_cost,
        },
        "target_weight_counts": dict(sorted(Counter(row.bit_count() for row in rows).items())),
        "first_form_universe": len(forms),
        "option_count": sum(map(len, options)),
    }
    if result == unsat:
        return payload
    if result != sat:
        payload["reason_unknown"] = solver.reason_unknown()
        return payload

    model = solver.model()
    selected_forms = tuple(form for form in forms if bool(model.eval(form_var[form], model_completion=True)))
    selected_options: list[dict[str, object]] = []
    for output, choices in enumerate(options):
        chosen = next(
            option
            for option in range(len(choices))
            if bool(model.eval(choice_var[(output, option)], model_completion=True))
        )
        arity, needed = choices[chosen]
        selected_options.append(
            {
                "output": output,
                "target": f"{rows[output]:08x}",
                "final_arity": arity,
                "sources": [f"{source:08x}" for source in _sources_for_choice(rows[output], arity, needed)],
                "required_first_forms": [f"{form:08x}" for form in needed],
            }
        )

    counts = Counter(form.bit_count() for form in selected_forms)
    counts.update(entry["final_arity"] for entry in selected_options if entry["final_arity"])
    if exact_xor2 is not None and counts[2] != exact_xor2:
        raise AssertionError("extracted XOR2 count differs from SMT model")
    if exact_xor3 is not None and counts[3] != exact_xor3:
        raise AssertionError("extracted XOR3 count differs from SMT model")
    for entry in selected_options:
        value = 0
        for source in entry["sources"]:
            value ^= int(source, 16)
        if value != int(entry["target"], 16):
            raise AssertionError(f"bad output certificate for y{entry['output']}")

    payload.update(
        {
            "xor2_count": counts[2],
            "xor3_count": counts[3],
            "logic_gate_cost": XOR2_COST * counts[2] + XOR3_COST * counts[3],
            "selected_first_forms": [f"{form:08x}" for form in selected_forms],
            "outputs": selected_options,
        }
    )
    return payload


def _sources_for_choice(row: int, arity: int, needed: tuple[int, ...]) -> tuple[int, ...]:
    if arity == 0:
        return (row,)
    needed_set = set(needed)
    for blocks in set_partitions(bit_masks(row), arity):
        if tuple(sorted(block for block in blocks if block.bit_count() > 1)) == needed:
            return blocks
    raise AssertionError("selected requirement has no matching partition")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    parser.add_argument("--exact-xor2", type=int)
    parser.add_argument("--exact-xor3", type=int)
    parser.add_argument("--max-cost", type=int)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = solve(
        timeout_ms=args.timeout_ms,
        exact_xor2=args.exact_xor2,
        exact_xor3=args.exact_xor3,
        max_cost=args.max_cost,
    )
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
