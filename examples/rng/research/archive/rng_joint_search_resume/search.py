"""Low-memory GF(2) search for a depth-two xorshift32 state encoding.

This file is deliberately isolated under ``.research``.  It never imports the
save writer and cannot touch the live game save.  A matrix is represented by
32 Python integers; bit j in row i means that output i depends on input j.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import random
import time
from typing import Iterable, Sequence


N = 32
MASK = (1 << N) - 1
IDENTITY = tuple(1 << i for i in range(N))

# Parent search frontier.  Each pair is row[dst] ^= row[src], starting at I.
SEED_ROW_OPERATIONS = (
    (6, 19), (31, 14), (19, 2), (30, 13), (1, 18),
    (4, 21), (0, 17), (5, 18), (9, 22), (8, 21),
    (3, 20), (7, 20), (5, 22), (6, 23), (7, 24),
    (4, 17), (3, 16), (3, 29), (10, 23), (17, 22),
    (22, 27), (11, 24), (18, 23), (23, 28), (21, 26),
)

# Deterministic 0x258000 anneal frontier.  Unlike the 25-operation seed, all
# rows of T, B and C have weight <= 4.  Its target-count lower bound is 68 and
# its current greedy realization costs 105 XOR, so it is a research frontier,
# not a deployable <=67 result.
FEASIBLE_FRONTIER_T = tuple(
    int(item, 16)
    for item in """
        40022001 00040002 20010000 00110008 00220010 00440020 00880040 03100080
        00000100 40000000 10008000 01080000 01000000 00420000 00840000 08800400
        11000800 08400200 00004000 00088004 00400000 00200000 00100000 10800000
        20000000 02000000 04000000 08000000 10000000 20001000 44002000 80044002
    """.split()
)


def xorshift32(value: int) -> int:
    value &= MASK
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def apply_matrix(rows: Sequence[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << i for i, row in enumerate(rows))


def matrix_from_function(function) -> tuple[int, ...]:
    rows = [0] * N
    for source in range(N):
        output = function(1 << source)
        for target in range(N):
            if output >> target & 1:
                rows[target] |= 1 << source
    return tuple(rows)


A = matrix_from_function(xorshift32)


def matrix_multiply(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    result = []
    for row in left:
        value = 0
        remaining = row
        while remaining:
            bit = remaining & -remaining
            value ^= right[bit.bit_length() - 1]
            remaining ^= bit
        result.append(value)
    return tuple(result)


def matrix_inverse(rows: Sequence[int]) -> tuple[int, ...]:
    work = list(rows)
    result = list(IDENTITY)
    for column in range(N):
        try:
            pivot = next(i for i in range(column, N) if work[i] >> column & 1)
        except StopIteration as exc:
            raise ValueError("matrix is singular") from exc
        work[column], work[pivot] = work[pivot], work[column]
        result[column], result[pivot] = result[pivot], result[column]
        for row in range(N):
            if row != column and work[row] >> column & 1:
                work[row] ^= work[column]
                result[row] ^= result[column]
    return tuple(result)


def matrices_for_basis(basis: Sequence[int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return B=T*A*T^-1 and C=A*T^-1 for q=T*x."""

    inverse = matrix_inverse(basis)
    transition = matrix_multiply(matrix_multiply(basis, A), inverse)
    output = matrix_multiply(A, inverse)
    return transition, output


def seed_basis(reverse: bool = False) -> tuple[int, ...]:
    rows = list(IDENTITY)
    for first, second in SEED_ROW_OPERATIONS:
        dst, src = (second, first) if reverse else (first, second)
        rows[dst] ^= rows[src]
    return tuple(rows)


def mutate(
    basis: list[int], transition: list[int], output: list[int], dst: int, src: int
) -> None:
    """Apply E on the left of T, updating B'=E*B*E and C'=C*E."""

    bit = 1 << dst
    toggle = 1 << src
    basis[dst] ^= basis[src]
    for index, row in enumerate(transition):
        if row & bit:
            transition[index] ^= toggle
    transition[dst] ^= transition[src]
    for index, row in enumerate(output):
        if row & bit:
            output[index] ^= toggle


@lru_cache(maxsize=131_072)
def _pairs(mask: int) -> tuple[int, ...]:
    bits = [1 << i for i in range(N) if mask >> i & 1]
    return tuple(bits[i] | bits[j] for i in range(len(bits)) for j in range(i + 1, len(bits)))


@lru_cache(maxsize=131_072)
def _options(mask: int) -> tuple[frozenset[int], ...]:
    weight = mask.bit_count()
    if weight == 3:
        return tuple(frozenset((pair,)) for pair in _pairs(mask))
    if weight == 4:
        partitions = {
            tuple(sorted((pair, mask ^ pair)))
            for pair in _pairs(mask)
            if (mask ^ pair).bit_count() == 2
        }
        return tuple(frozenset(item) for item in sorted(partitions))
    return ()


@dataclass(frozen=True)
class DepthTwoCost:
    feasible: bool
    lower_bound: int
    greedy_upper_bound: int | None
    distinct_targets: int
    distinct_non_unit_targets: int
    required_pair_outputs: int
    final_outputs: int
    selected_pair_gates: tuple[int, ...]


def depth_two_cost(rows: Iterable[int]) -> DepthTwoCost:
    """Construct a deterministic shared XOR2 plan and a strict lower bound.

    A weight-3 output needs one selected pair and a final XOR.  A weight-4
    output needs one of its three two-pair partitions and a final XOR.  The
    greedy result is an upper bound; the number of distinct non-unit targets is
    an unconditional lower bound for this particular target set.
    """

    targets = frozenset(rows)
    non_unit = frozenset(mask for mask in targets if mask & (mask - 1))
    if 0 in targets or any(mask.bit_count() > 4 for mask in targets):
        return DepthTwoCost(
            False, len(non_unit), None, len(targets), len(non_unit), 0, 0, ()
        )

    required = {mask for mask in targets if mask.bit_count() == 2}
    finals = {mask for mask in targets if mask.bit_count() >= 3}
    selected = set(required)

    def satisfied(mask: int, pairs: set[int]) -> bool:
        return any(option <= pairs for option in _options(mask))

    while True:
        unmet = [mask for mask in finals if not satisfied(mask, selected)]
        if not unmet:
            break
        actions = {
            option - selected
            for mask in unmet
            for option in _options(mask)
            if option - selected
        }
        if not actions:
            raise AssertionError("a <=4-input row has no depth-two decomposition")

        def action_key(action: frozenset[int]):
            gain = sum(satisfied(mask, selected | set(action)) for mask in unmet)
            return (
                gain / len(action),
                gain,
                -len(action),
                tuple(-item for item in sorted(action)),
            )

        selected.update(max(actions, key=action_key))

    # Deterministic deletion pass removes greedily redundant intermediates.
    changed = True
    while changed:
        changed = False
        for pair in sorted(selected - required, reverse=True):
            candidate = selected - {pair}
            if all(satisfied(mask, candidate) for mask in finals):
                selected = candidate
                changed = True

    gate_count = len(selected) + len(finals)
    return DepthTwoCost(
        True,
        len(non_unit),
        gate_count,
        len(targets),
        len(non_unit),
        len(required),
        len(finals),
        tuple(sorted(selected)),
    )


@dataclass(frozen=True, order=True)
class StateScore:
    max_feedback_output_weight: int
    bad_feedback_output_rows: int
    max_initialization_weight: int
    bad_initialization_rows: int
    strict_total_lower_bound: int
    feedback_output_lower_bound: int
    total_row_weight: int


def state_score(
    basis: Sequence[int], transition: Sequence[int], output: Sequence[int]
) -> StateScore:
    feedback_weights = [row.bit_count() for row in (*transition, *output)]
    initialization_weights = [row.bit_count() for row in basis]
    init_targets = {row for row in basis if row & (row - 1)}
    joint_targets = {row for row in (*transition, *output) if row & (row - 1)}
    return StateScore(
        max(feedback_weights),
        sum(weight > 4 for weight in feedback_weights),
        max(initialization_weights),
        sum(weight > 4 for weight in initialization_weights),
        len(init_targets) + len(joint_targets),
        len(joint_targets),
        sum(feedback_weights) + sum(initialization_weights),
    )


def full_cost(
    basis: Sequence[int], transition: Sequence[int], output: Sequence[int]
) -> dict[str, object]:
    initialization = depth_two_cost(basis)
    feedback_output = depth_two_cost((*transition, *output))
    total = None
    if initialization.greedy_upper_bound is not None and feedback_output.greedy_upper_bound is not None:
        total = initialization.greedy_upper_bound + feedback_output.greedy_upper_bound
    return {
        "score": state_score(basis, transition, output).__dict__,
        "initialization": initialization.__dict__,
        "feedback_output": feedback_output.__dict__,
        "greedy_total_xor": total,
    }


def _energy(basis: Sequence[int], transition: Sequence[int], output: Sequence[int]) -> int:
    rows = (*basis, *transition, *output)
    weights = [row.bit_count() for row in rows]
    bad = sum(weight > 4 for weight in weights)
    excess = sum(max(0, weight - 4) ** 2 for weight in weights)
    maximum = max(weights)
    score = state_score(basis, transition, output)
    return (
        30_000 * bad
        + 10_000 * excess
        + 40_000 * max(0, maximum - 5) ** 2
        + 400 * score.strict_total_lower_bound
        + score.total_row_weight
    )


def anneal(
    *, seed: int, cycles: int, steps_per_cycle: int, start: str = "seed"
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...], StateScore]:
    """Run deterministic constant-memory annealing from the 25-operation seed."""

    basis0 = FEASIBLE_FRONTIER_T if start == "frontier" else seed_basis()
    transition0, output0 = matrices_for_basis(basis0)
    best = (basis0, transition0, output0, state_score(basis0, transition0, output0))

    for cycle in range(cycles):
        rng = random.Random(seed + cycle)
        if cycle % 3:
            basis, transition, output = map(list, best[:3])
        else:
            basis, transition, output = map(list, (basis0, transition0, output0))
        for _ in range(3 + cycle % 6):
            dst = rng.randrange(N)
            src = rng.randrange(N - 1)
            src += src >= dst
            mutate(basis, transition, output, dst, src)
        energy = _energy(basis, transition, output)

        for step in range(steps_per_cycle):
            dst = rng.randrange(N)
            src = rng.randrange(N - 1)
            src += src >= dst
            mutate(basis, transition, output, dst, src)
            candidate_energy = _energy(basis, transition, output)
            delta = candidate_energy - energy
            temperature = 35_000 * (0.001 ** (step / steps_per_cycle)) + 3
            if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                energy = candidate_energy
            else:
                mutate(basis, transition, output, dst, src)

            if not step & 127:
                candidate_score = state_score(basis, transition, output)
                if candidate_score < best[3]:
                    best = (
                        tuple(basis), tuple(transition), tuple(output), candidate_score
                    )
    return best


def matrix_hex(rows: Sequence[int]) -> list[str]:
    return [f"{row:08x}" for row in rows]


def certificate_digest(*matrices: Sequence[int]) -> str:
    payload = b"".join(row.to_bytes(4, "little") for matrix in matrices for row in matrix)
    return hashlib.sha256(payload).hexdigest()


def verify_sequence(
    basis: Sequence[int], transition: Sequence[int], output: Sequence[int]
) -> None:
    inverse = matrix_inverse(basis)
    assert matrix_multiply(basis, inverse) == IDENTITY
    assert matrix_multiply(matrix_multiply(basis, A), inverse) == tuple(transition)
    assert matrix_multiply(A, inverse) == tuple(output)
    for seed in (0, 1, 0x12345678, 0xFFFFFFFF, 0x80000000):
        expected = seed
        encoded = apply_matrix(basis, seed)
        for _ in range(65):
            expected = xorshift32(expected)
            assert apply_matrix(output, encoded) == expected
            encoded = apply_matrix(transition, encoded)


def result_document(
    basis: Sequence[int], transition: Sequence[int], output: Sequence[int], **extra
) -> dict[str, object]:
    verify_sequence(basis, transition, output)
    result = {
        "convention": "q=T*x; B=T*A*T^-1; C=A*T^-1; row[dst]^=row[src]",
        "xorshift": "x^=x>>13; x^=x<<17; x^=x>>5 (all U32)",
        "sha256": certificate_digest(basis, transition, output),
        "T": matrix_hex(basis),
        "B": matrix_hex(transition),
        "C": matrix_hex(output),
        "cost": full_cost(basis, transition, output),
    }
    result.update(extra)
    return result


def self_test() -> None:
    assert xorshift32(1) == 0x00021001
    assert xorshift32(0x12345678) == 0x996CC1E4
    basis = seed_basis()
    transition, output = matrices_for_basis(basis)
    verify_sequence(basis, transition, output)
    score = state_score(basis, transition, output)
    assert score == StateScore(5, 1, 4, 0, 68, 49, 278), score
    reverse = seed_basis(reverse=True)
    reverse_transition, reverse_output = matrices_for_basis(reverse)
    assert state_score(reverse, reverse_transition, reverse_output).bad_feedback_output_rows == 27
    init_cost = depth_two_cost(basis)
    assert init_cost.feasible and init_cost.greedy_upper_bound == 25


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x258000)
    parser.add_argument("--cycles", type=int, default=8)
    parser.add_argument("--steps", type=int, default=120_000)
    parser.add_argument("--start", choices=("seed", "frontier"), default="seed")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("self-test: ok")

    basis = seed_basis()
    transition, output = matrices_for_basis(basis)
    source = "25-operation seed"
    elapsed = 0.0
    if args.search:
        started = time.perf_counter()
        basis, transition, output, _ = anneal(
            seed=args.seed,
            cycles=args.cycles,
            steps_per_cycle=args.steps,
            start=args.start,
        )
        elapsed = time.perf_counter() - started
        source = "deterministic anneal"

    document = result_document(
        basis,
        transition,
        output,
        source=source,
        start=args.start,
        deterministic_seed=args.seed,
        cycles=args.cycles if args.search else 0,
        steps_per_cycle=args.steps if args.search else 0,
        elapsed_seconds=round(elapsed, 6),
        memory_model="three 32-row integer matrices; constant-memory annealing",
    )
    encoded = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
