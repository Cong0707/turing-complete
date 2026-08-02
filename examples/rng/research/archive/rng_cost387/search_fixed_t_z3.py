"""Bounded joint pair-cover/mode-label search for the fixed two-shear RNG basis.

This research-only script never reads or writes a game save.  It permits every
canonical depth-two pair cover of the fixed B/C row set, then asks whether the
same physical XOR DAG can carry T(seed) on the feedback outputs at tick zero.

The SAT run is deliberately bounded: Z3 receives both a wall-clock timeout and
a memory ceiling.  A satisfying model is emitted as a replayable JSON
certificate; UNSAT only excludes this fixed T and depth-two canonical family.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Iterable, Sequence

from z3 import And, AtMost, Bool, Implies, Or, PbLe, Solver, Xor, is_true, sat, unsat


BITS = 32
IDENTITY = frozenset(1 << bit for bit in range(BITS))


def load_init_module(path: Path):
    spec = importlib.util.spec_from_file_location("rng_init_reuse_source", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_rows(values: Sequence[int | str]) -> tuple[int, ...]:
    return tuple(int(value, 16) if isinstance(value, str) else int(value) for value in values)


def apply_basis_shear(
    T: Sequence[int], B: Sequence[int], C: Sequence[int], dst: int, src: int
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    """Return E*T, E*B*E and C*E for E[dst,src]=1."""
    if not (0 <= dst < BITS and 0 <= src < BITS) or dst == src:
        raise ValueError("neighbor shear requires distinct bit indices in [0,31]")
    next_t, next_b, next_c = list(T), list(B), list(C)
    bit = 1 << dst
    toggle = 1 << src
    next_t[dst] ^= next_t[src]
    for index, row in enumerate(next_b):
        if row & bit:
            next_b[index] ^= toggle
    next_b[dst] ^= next_b[src]
    for index, row in enumerate(next_c):
        if row & bit:
            next_c[index] ^= toggle
    return tuple(next_t), tuple(next_b), tuple(next_c)


def load_matrices(
    source: Path, matrices_json: Path | None, neighbor: tuple[int, int] | None
):
    if matrices_json is None:
        module = load_init_module(source)
        result = tuple(module.T), tuple(module.B), tuple(module.C)
    else:
        document = json.loads(matrices_json.read_text(encoding="utf-8"))
        result = parse_rows(document["T"]), parse_rows(document["B"]), parse_rows(document["C"])
    return apply_basis_shear(*result, *neighbor) if neighbor is not None else result


def support(mask: int) -> tuple[int, ...]:
    return tuple(bit for bit in range(BITS) if mask >> bit & 1)


def pair_options(mask: int) -> tuple[tuple[int, ...], ...]:
    bits = tuple(1 << bit for bit in support(mask))
    if len(bits) == 3:
        return tuple((mask ^ unit,) for unit in bits)
    if len(bits) == 4:
        a, b, c, d = bits
        return (
            tuple(sorted((a | b, c | d))),
            tuple(sorted((a | c, b | d))),
            tuple(sorted((a | d, b | c))),
        )
    raise ValueError(f"row {mask:08x} has unsupported weight {len(bits)}")


def bool_xor(left, right):
    return Xor(left, right)


def conditional_equal(solver: Solver, condition, left, expected: bool) -> None:
    solver.add(Implies(condition, left if expected else ~left))


def solve(
    *,
    source: Path,
    matrices_json: Path | None,
    neighbor: tuple[int, int] | None,
    pair_budget: int,
    mode_budget: int,
    timeout_ms: int,
    memory_mb: int,
) -> tuple[str, dict[str, object] | None, dict[str, int]]:
    T, B, C = load_matrices(source, matrices_json, neighbor)
    if not (len(T) == len(B) == len(C) == BITS):
        raise ValueError("T, B and C must each contain 32 rows")

    targets = frozenset((*B, *C))
    required_pairs = frozenset(row for row in targets if row.bit_count() == 2)
    finals = frozenset(row for row in targets if row.bit_count() in (3, 4))
    options = {row: pair_options(row) for row in finals}
    candidate_pairs = frozenset(
        (*required_pairs, *(pair for row in finals for option in options[row] for pair in option))
    )

    solver = Solver()
    solver.set(timeout=timeout_ms, max_memory=memory_mb)

    selected = {pair: Bool(f"pair_{pair:08x}") for pair in sorted(candidate_pairs)}
    choose = {
        (row, index): Bool(f"choose_{row:08x}_{index}")
        for row in sorted(finals)
        for index in range(len(options[row]))
    }
    for pair in required_pairs:
        solver.add(selected[pair])
    for row in finals:
        row_choices = [choose[row, index] for index in range(len(options[row]))]
        solver.add(Or(*row_choices), AtMost(*row_choices, 1))
        for index, option in enumerate(options[row]):
            for pair in option:
                solver.add(Implies(choose[row, index], selected[pair]))
    solver.add(PbLe([(variable, 1) for variable in selected.values()], pair_budget))

    # mode[s,j] is one physical OR carrying seed[s] at tick zero and q[j]
    # in steady mode.  A selected pair gate has two physical input pins; each
    # pin may carry zero or one seed bit, and its tick-zero label is their XOR.
    mode = {
        (seed, state): Bool(f"mode_s{seed}_q{state}")
        for seed in range(BITS)
        for state in range(BITS)
    }
    mode_users: dict[tuple[int, int], list[object]] = {key: [] for key in mode}
    pin = {
        (pair, side, seed): Bool(f"pin_{pair:08x}_{side}_s{seed}")
        for pair in sorted(candidate_pairs)
        for side in range(2)
        for seed in range(BITS)
    }
    label = {
        (pair, seed): Bool(f"label_{pair:08x}_s{seed}")
        for pair in sorted(candidate_pairs)
        for seed in range(BITS)
    }
    for pair in candidate_pairs:
        states = support(pair)
        if len(states) != 2:
            raise AssertionError(f"candidate {pair:08x} is not a pair")
        for side, state in enumerate(states):
            side_pins = [pin[pair, side, seed] for seed in range(BITS)]
            solver.add(AtMost(*side_pins, 1))
            for seed, variable in enumerate(side_pins):
                solver.add(Implies(variable, selected[pair]))
                solver.add(Implies(variable, mode[seed, state]))
                mode_users[seed, state].append(variable)
        for seed in range(BITS):
            solver.add(
                label[pair, seed]
                == bool_xor(pin[pair, 0, seed], pin[pair, 1, seed])
            )
    solver.add(PbLe([(variable, 1) for variable in mode.values()], mode_budget))

    # Every physical target row has one canonical decomposition.  If it is a
    # B feedback output, its tick-zero label must equal the corresponding T
    # row.  C-only outputs place no tick-zero constraint on the shared node.
    b_index = {row: index for index, row in enumerate(B)}
    for row, index in b_index.items():
        target = T[index]
        if row.bit_count() == 1:
            state = support(row)[0]
            target_bits = support(target)
            if len(target_bits) != 1:
                solver.add(False)
            else:
                solver.add(mode[target_bits[0], state])
                mode_users[target_bits[0], state].append(True)
            continue
        if row.bit_count() == 2:
            for seed in range(BITS):
                solver.add(label[row, seed] == bool(target >> seed & 1))
            continue

        for option_index, option in enumerate(options[row]):
            condition = choose[row, option_index]
            if row.bit_count() == 4:
                left, right = option
                for seed in range(BITS):
                    conditional_equal(
                        solver,
                        condition,
                        bool_xor(label[left, seed], label[right, seed]),
                        bool(target >> seed & 1),
                    )
            else:
                pair = option[0]
                unit = row ^ pair
                state = support(unit)[0]
                residuals = []
                for seed in range(BITS):
                    residual = bool_xor(label[pair, seed], bool(target >> seed & 1))
                    residuals.append(residual)
                    solver.add(Implies(condition, Implies(residual, mode[seed, state])))
                    mode_users[seed, state].append(And(condition, residual))
                solver.add(Implies(condition, AtMost(*residuals, 1)))

    for key, variable in mode.items():
        users = mode_users[key]
        solver.add(variable == Or(*users) if users else ~variable)
    # T is invertible, so every seed coordinate must reach at least one
    # physical leaf.  Stating the implied rank fact directly improves SAT
    # propagation for tight mode budgets.
    for seed in range(BITS):
        solver.add(Or(*(mode[seed, state] for state in range(BITS))))

    check = solver.check()
    stats = {
        "candidate_pairs": len(candidate_pairs),
        "required_pairs": len(required_pairs),
        "finals": len(finals),
        "pair_budget": pair_budget,
        "mode_budget": mode_budget,
    }
    if check == unsat:
        return "unsat", None, stats
    if check != sat:
        return "unknown", {"reason": solver.reason_unknown()}, stats

    model = solver.model()
    chosen_pairs = frozenset(
        pair for pair, variable in selected.items() if is_true(model.eval(variable))
    )
    chosen_modes = frozenset(
        key for key, variable in mode.items() if is_true(model.eval(variable))
    )
    chosen_options = {
        row: next(
            options[row][index]
            for index in range(len(options[row]))
            if is_true(model.eval(choose[row, index]))
        )
        for row in finals
    }
    labels = {
        pair: sum(
            (1 << seed)
            for seed in range(BITS)
            if is_true(model.eval(label[pair, seed]))
        )
        for pair in chosen_pairs
    }
    pins = {
        pair: [
            next(
                (
                    seed
                    for seed in range(BITS)
                    if is_true(model.eval(pin[pair, side, seed]))
                ),
                None,
            )
            for side in range(2)
        ]
        for pair in chosen_pairs
    }
    certificate = {
        "scope": "fixed two-shear T; canonical shared depth-two B/C DAG",
        "T": [f"{row:08x}" for row in T],
        "B": [f"{row:08x}" for row in B],
        "C": [f"{row:08x}" for row in C],
        "selected_pair_gates": [f"{pair:08x}" for pair in sorted(chosen_pairs)],
        "pair_labels": {f"{pair:08x}": f"{labels[pair]:08x}" for pair in sorted(labels)},
        "pair_pin_seed_bits": {f"{pair:08x}": pins[pair] for pair in sorted(pins)},
        "decompositions": {
            f"{row:08x}": [f"{pair:08x}" for pair in chosen_options[row]]
            for row in sorted(chosen_options)
        },
        "mode_pairs": [
            {"seed": seed, "state": state}
            for seed, state in sorted(chosen_modes)
        ],
        "xor_count": len(chosen_pairs) + len(finals),
        "or_count": len(chosen_modes),
        "gate_score": 160 + 3 * (len(chosen_pairs) + len(finals)) + len(chosen_modes) + 6,
        "delay": 9,
        "cycles": 66,
    }
    return "sat", certificate, stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(".research/rng_init_reuse/verify_init_reuse.py"),
    )
    parser.add_argument("--matrices-json", type=Path)
    parser.add_argument("--neighbor", nargs=2, type=int, metavar=("DST", "SRC"))
    parser.add_argument("--pair-budget", type=int, default=27)
    parser.add_argument("--mode-budget", type=int, default=38)
    parser.add_argument("--timeout-ms", type=int, default=60_000)
    parser.add_argument("--memory-mb", type=int, default=512)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    status, certificate, stats = solve(
        source=args.source,
        matrices_json=args.matrices_json,
        neighbor=tuple(args.neighbor) if args.neighbor else None,
        pair_budget=args.pair_budget,
        mode_budget=args.mode_budget,
        timeout_ms=args.timeout_ms,
        memory_mb=args.memory_mb,
    )
    document: dict[str, object] = {"status": status, **stats}
    if certificate is not None:
        document["certificate"] = certificate
    encoded = json.dumps(document, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if status in {"sat", "unsat"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
