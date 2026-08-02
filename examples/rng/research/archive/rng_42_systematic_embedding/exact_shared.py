"""Exact depth-two XOR cover for one 42-state systematic embedding."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from z3 import And, Bool, If, Optimize, Or, Sum, sat


N = 32
K = 10
MASK = (1 << N) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def transition_rows() -> tuple[int, ...]:
    return tuple(
        sum(((xorshift32(1 << source) >> target) & 1) << source for source in range(N))
        for target in range(N)
    )


def apply_row(row: int, matrix: tuple[int, ...]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def pair_partitions(form: int) -> tuple[tuple[int, ...], ...]:
    support = tuple(index for index in range(N + K) if (form >> index) & 1)
    if len(support) == 1:
        return ((),)
    if len(support) == 2:
        return ((form,),)
    if len(support) == 3:
        return tuple(
            (sum(1 << bit for index, bit in enumerate(support) if index != skip),)
            for skip in range(3)
        )
    if len(support) == 4:
        return tuple(
            (
                (1 << support[0]) | (1 << support[mate]),
                form ^ ((1 << support[0]) | (1 << support[mate])),
            )
            for mate in range(1, 4)
        )
    raise ValueError(f"unsupported form weight {len(support)}")


def target_options(rows: tuple[int, ...]) -> dict[int, tuple[tuple[int, ...], ...]]:
    matrix = transition_rows()
    targets = tuple(sorted(set((*matrix, *(apply_row(row, matrix) for row in rows)))))
    combinations = [0] * (1 << K)
    for mask in range(1, 1 << K):
        low = mask & -mask
        combinations[mask] = combinations[mask ^ low] ^ rows[low.bit_length() - 1]

    result: dict[int, tuple[tuple[int, ...], ...]] = {}
    for target in targets:
        options: set[tuple[int, ...]] = set()
        for aux_mask, combination in enumerate(combinations):
            raw = target ^ combination
            form = raw | (aux_mask << N)
            if not 1 <= form.bit_count() <= 4:
                continue
            for pairs in pair_partitions(form):
                options.add(tuple(sorted({form, *pairs})))
        if not options:
            raise RuntimeError(f"target {target:08x} has no depth-two representation")
        result[target] = tuple(sorted(options, key=lambda option: (len(option), option)))
    return result


def solve(rows: tuple[int, ...]) -> dict[str, object]:
    options = target_options(rows)
    gates = tuple(sorted({gate for target in options.values() for option in target for gate in option}))
    selected = {gate: Bool(f"g_{gate:011x}") for gate in gates}
    optimizer = Optimize()
    for target_options_value in options.values():
        optimizer.add(Or(*(And(*(selected[gate] for gate in option)) for option in target_options_value)))
    objective = optimizer.minimize(Sum(*(If(selected[gate], 1, 0) for gate in gates)))
    if optimizer.check() != sat:
        raise RuntimeError("unexpected UNSAT exact cover")
    model = optimizer.model()
    optimum = objective.value().as_long()
    selected_gates = frozenset(gate for gate in gates if model.eval(selected[gate], model_completion=True))

    choices: dict[str, list[str]] = {}
    for target, target_options_value in options.items():
        viable = [option for option in target_options_value if set(option) <= selected_gates]
        if not viable:
            raise AssertionError(f"model does not cover target {target:08x}")
        choice = min(viable, key=lambda option: (len(option), option))
        choices[f"{target:08x}"] = [f"{gate:011x}" for gate in choice]

    pair_gates = tuple(gate for gate in selected_gates if gate.bit_count() == 2)
    return {
        "status": "sat",
        "R": [f"{row:08x}" for row in rows],
        "target_count": len(options),
        "option_count": sum(len(value) for value in options.values()),
        "gate_universe_count": len(gates),
        "xor_optimum": optimum,
        "selected_pair_count": len(pair_gates),
        "selected_gates": [f"{gate:011x}" for gate in sorted(selected_gates)],
        "choices": choices,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rows",
        default=(
            "00080004,0c400200,21201190,908c4042,00108000,"
            "02200100,0c620210,08040020,80044002,40022001"
        ),
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = tuple(int(value, 16) for value in args.rows.split(","))
    if len(rows) != K:
        raise ValueError(f"expected {K} R rows, got {len(rows)}")
    report = solve(rows)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
