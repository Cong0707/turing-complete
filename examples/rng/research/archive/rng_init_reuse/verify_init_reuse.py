"""Verify the RNG tick-zero mode-reuse construction.

The verifier is deliberately independent of save files and the game process.
Every signal is represented twice: its tick-zero linear form over ``seed`` and
its steady-state linear form over encoded state ``q``.

The physical primitive behind a mode-paired leaf is::

    paired(seed_i, q_j) = OR(seed_i, q_j)

At tick zero all Delay Bits contain zero.  On later ticks the controlled Level
Input contributes numeric zero/high impedance, matching the behavior already
validated by the 381/11/66 circuit.  One OR therefore carries ``seed_i`` in
initialization mode and ``q_j`` in steady mode.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations
import random
from typing import Callable, Iterable, Sequence


BITS = 32
MASK = (1 << BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(BITS))

XOR_GATE_COST = 3
XOR_DELAY = 2
OR_GATE_COST = 1
OR_DELAY = 1
DELAY_BIT_GATE_COST = 5
DELAY_BIT_DELAY = 4
CONTROL_GATE_COST = 6  # one Delay Bit plus one NOT


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function: Callable[[int], int]) -> tuple[int, ...]:
    return tuple(
        sum(((function(1 << source) >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    remaining = row
    while remaining:
        low_bit = remaining & -remaining
        result ^= matrix[low_bit.bit_length() - 1]
        remaining ^= low_bit
    return result


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << index for index, row in enumerate(matrix))


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def invert(matrix: Sequence[int]) -> tuple[int, ...]:
    rows = [matrix[index] | ((1 << index) << BITS) for index in range(BITS)]
    for column in range(BITS):
        pivot = next(
            (index for index in range(column, BITS) if (rows[index] >> column) & 1),
            None,
        )
        if pivot is None:
            raise ValueError("matrix is singular")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for index in range(BITS):
            if index != column and ((rows[index] >> column) & 1):
                rows[index] ^= rows[column]
    return tuple((row >> BITS) & MASK for row in rows)


def right_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(lambda value: (value ^ (value >> distance)) & MASK)


A = matrix_from_function(xorshift32)
T = compose(right_shear(17), right_shear(13))
T_INVERSE = invert(T)
C = compose(A, T_INVERSE)
B = compose(T, C)


BC_EXTRA_PAIRS = frozenset(
    int(value, 16)
    for value in (
        "00420000",
        "00840000",
        "01080000",
        "02100000",
        "04200000",
        "08008000",
        "08400000",
        "10010000",
        "10800000",
        "20000001",
        "21000000",
        "40000002",
        "42000000",
        "80000004",
        "84000000",
    )
)


# Tick-zero labels assigned to the 27 physical first-layer nodes of the
# steady B/C network.  They are exactly the first layer of a 34-XOR T network,
# embedded without adding a physical XOR.
FIRST_SEED_LABELS = {
    int(steady, 16): int(seed, 16)
    for steady, seed in (
        ("00000021", "00020000"),
        ("00000042", "00040000"),
        ("00000084", "00080000"),
        ("00000108", "00100000"),
        ("00000210", "00200000"),
        ("00000420", "00400000"),
        ("00000840", "00800000"),
        ("00001080", "01000000"),
        ("00002100", "02000000"),
        ("00004200", "04000000"),
        ("00008008", "00008000"),
        ("00010010", "00010000"),
        ("00420000", "00020001"),
        ("00840000", "00040002"),
        ("01080000", "00080004"),
        ("02100000", "00100008"),
        ("04200000", "00200010"),
        ("08008000", "08000400"),
        ("08400000", "00400020"),
        ("10010000", "10000800"),
        ("10800000", "00800040"),
        ("20000001", "20001000"),
        ("21000000", "01000080"),
        ("40000002", "40002000"),
        ("42000000", "02000100"),
        ("80000004", "80004000"),
        ("84000000", "04000200"),
    )
}


# (seed bit, encoded-state bit).  Each pair is one physical OR gate whose
# output may fan out.  The optional Z3 proof shows that 47 is minimal for this
# fixed 61-XOR DAG and fixed encoding T.
MODE_PAIRS = frozenset(
    {
        (0, 22),
        (1, 23),
        (2, 24),
        (3, 25),
        (4, 26),
        (5, 27),
        (6, 28),
        (7, 29),
        (8, 30),
        (9, 31),
        (10, 27),
        (11, 28),
        (12, 29),
        (13, 30),
        (14, 31),
        (15, 15),
        (16, 16),
        (17, 0),
        (17, 17),
        (18, 1),
        (18, 18),
        (19, 2),
        (19, 19),
        (20, 3),
        (20, 20),
        (21, 4),
        (21, 21),
        (22, 10),
        (22, 22),
        (23, 6),
        (23, 23),
        (24, 12),
        (24, 24),
        (25, 13),
        (25, 25),
        (26, 14),
        (26, 26),
        (27, 10),
        (27, 15),
        (28, 11),
        (28, 16),
        (29, 0),
        (29, 12),
        (30, 1),
        (30, 13),
        (31, 2),
        (31, 14),
    }
)


@dataclass(frozen=True)
class XorGate:
    output: int
    left: int
    right: int
    depth: int


def bits(value: int) -> tuple[int, ...]:
    return tuple(index for index in range(BITS) if (value >> index) & 1)


def pair_partitions(row: int) -> tuple[tuple[int, int], ...]:
    support = bits(row)
    if len(support) == 3:
        return tuple((1 << lone, row ^ (1 << lone)) for lone in support)
    if len(support) == 4:
        a, b, c, d = support
        return (
            ((1 << a) ^ (1 << b), (1 << c) ^ (1 << d)),
            ((1 << a) ^ (1 << c), (1 << b) ^ (1 << d)),
            ((1 << a) ^ (1 << d), (1 << b) ^ (1 << c)),
        )
    raise ValueError(f"row {row:08x} cannot be partitioned as a depth-two output")


def build_steady_network() -> tuple[XorGate, ...]:
    targets = frozenset(B + C)
    direct = frozenset(IDENTITY)
    pair_outputs = frozenset(
        row for row in targets - direct if row.bit_count() == 2
    )
    first_layer = pair_outputs | BC_EXTRA_PAIRS
    if first_layer != frozenset(FIRST_SEED_LABELS):
        raise AssertionError("first-layer certificate does not match the steady DAG")

    gates: list[XorGate] = []
    for pair in sorted(first_layer):
        left_bit, right_bit = bits(pair)
        gates.append(XorGate(pair, 1 << left_bit, 1 << right_bit, 1))

    available = direct | first_layer
    for target in sorted(targets - direct - pair_outputs):
        partition = next(
            (
                candidate
                for candidate in pair_partitions(target)
                if candidate[0] in available and candidate[1] in available
            ),
            None,
        )
        if partition is None:
            raise AssertionError(f"no depth-two partition for {target:08x}")
        gates.append(XorGate(target, partition[0], partition[1], 2))

    if len(gates) != 61 or sum(gate.depth == 1 for gate in gates) != 27:
        raise AssertionError("steady 61-XOR DAG metrics changed")
    return tuple(gates)


GATES = build_steady_network()
GATE_BY_OUTPUT = {gate.output: gate for gate in GATES}
FIRST_LAYER = frozenset(gate.output for gate in GATES if gate.depth == 1)
DIRECT = frozenset(IDENTITY)


def choose_first_leaf_seeds(steady_pair: int, seed_form: int) -> tuple[int | None, int | None]:
    state_left, state_right = bits(steady_pair)
    candidates = (None, *range(BITS))
    for seed_left in candidates:
        for seed_right in candidates:
            form = (0 if seed_left is None else 1 << seed_left) ^ (
                0 if seed_right is None else 1 << seed_right
            )
            if form != seed_form:
                continue
            used = {
                pair
                for pair in ((seed_left, state_left), (seed_right, state_right))
                if pair[0] is not None
            }
            if used <= MODE_PAIRS:
                return seed_left, seed_right
    raise AssertionError(f"no mode-pair realization for first node {steady_pair:08x}")


FIRST_LEAF_SEEDS = {
    node: choose_first_leaf_seeds(node, seed_form)
    for node, seed_form in FIRST_SEED_LABELS.items()
}


def seed_form_of_fanin(node: int, consumer: int, side: int) -> int:
    if node in FIRST_LAYER:
        return FIRST_SEED_LABELS[node]
    if node not in DIRECT:
        raise AssertionError(f"unsupported fanin {node:08x}")

    # Only B's five weight-three outputs require a seed label on a raw input.
    # Their residual mapping is also the direct tick-zero mapping of B[27:32],
    # so no additional OR is needed.  C-only raw inputs remain state-only.
    if consumer not in B:
        return 0
    output_index = B.index(consumer)
    target = T[output_index]
    gate = GATE_BY_OUTPUT[consumer]
    other = gate.right if side == 0 else gate.left
    other_seed = FIRST_SEED_LABELS[other] if other in FIRST_LAYER else 0
    residual = target ^ other_seed
    if residual.bit_count() > 1:
        raise AssertionError(f"raw residual for B[{output_index}] is not one bit")
    return residual


def verify_dual_labels() -> tuple[dict[int, int], frozenset[tuple[int, int]]]:
    seed_labels: dict[int, int] = {}
    used_mode_pairs: set[tuple[int, int]] = set()

    for gate in GATES:
        if gate.depth == 1:
            state_bits = bits(gate.output)
            seed_bits = FIRST_LEAF_SEEDS[gate.output]
            for seed_bit, state_bit in zip(seed_bits, state_bits):
                if seed_bit is not None:
                    used_mode_pairs.add((seed_bit, state_bit))
            left_seed = 0 if seed_bits[0] is None else 1 << seed_bits[0]
            right_seed = 0 if seed_bits[1] is None else 1 << seed_bits[1]
        else:
            left_seed = (
                seed_labels[gate.left]
                if gate.left in seed_labels
                else seed_form_of_fanin(gate.left, gate.output, 0)
            )
            right_seed = (
                seed_labels[gate.right]
                if gate.right in seed_labels
                else seed_form_of_fanin(gate.right, gate.output, 1)
            )
            for node, seed_form in ((gate.left, left_seed), (gate.right, right_seed)):
                if node in DIRECT and seed_form:
                    seed_bit = bits(seed_form)[0]
                    state_bit = bits(node)[0]
                    used_mode_pairs.add((seed_bit, state_bit))

        seed_labels[gate.output] = left_seed ^ right_seed
        if gate.left ^ gate.right != gate.output:
            raise AssertionError(f"steady gate semantics changed for {gate.output:08x}")

    for index, (seed_target, steady_target) in enumerate(zip(T, B)):
        if steady_target in seed_labels:
            actual_seed = seed_labels[steady_target]
        else:
            seed_bit = bits(seed_target)[0]
            state_bit = bits(steady_target)[0]
            used_mode_pairs.add((seed_bit, state_bit))
            actual_seed = seed_target
        if actual_seed != seed_target:
            raise AssertionError(
                f"B[{index}] tick-zero label {actual_seed:08x} != T row {seed_target:08x}"
            )

    for row in C:
        if row not in DIRECT and row not in seed_labels:
            raise AssertionError(f"C output {row:08x} is not produced by the shared DAG")
    if frozenset(used_mode_pairs) != MODE_PAIRS:
        missing = MODE_PAIRS - used_mode_pairs
        extra = used_mode_pairs - MODE_PAIRS
        raise AssertionError(f"mode-pair usage changed; missing={missing}, extra={extra}")
    return seed_labels, frozenset(used_mode_pairs)


def verify_sequences() -> None:
    seeds = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    generator = random.Random(20260801)
    seeds.extend(generator.getrandbits(32) for _ in range(64))

    for seed in seeds:
        natural = seed
        encoded = apply_matrix(T, seed)  # tick zero capture
        if apply_matrix(T_INVERSE, encoded) != seed:
            raise AssertionError("tick-zero encoding does not decode to the seed")
        for _ in range(65):
            natural = xorshift32(natural)
            visible = apply_matrix(C, encoded)
            next_encoded = apply_matrix(B, encoded)
            if visible != natural:
                raise AssertionError(
                    f"visible RNG mismatch for seed {seed:08x}: {visible:08x} != {natural:08x}"
                )
            if next_encoded != apply_matrix(T, natural):
                raise AssertionError("encoded feedback invariant failed")
            encoded = next_encoded


def prove_mode_pair_minimum() -> None:
    try:
        from z3 import AtMost, Bool, If, Implies, Optimize, Or, Sum, Xor, is_true, sat
    except ImportError as error:  # pragma: no cover - optional research dependency
        raise SystemExit(
            "--prove-minimum requires an external `pip install z3-solver`"
        ) from error

    mapping = [[Bool(f"map_{seed}_{state}") for state in range(BITS)] for seed in range(BITS)]
    leaf: dict[tuple[int, int], list[object]] = {}
    optimizer = Optimize()

    for node in sorted(FIRST_LAYER):
        for pin, state_bit in enumerate(bits(node)):
            choices = [Bool(f"leaf_{node:08x}_{pin}_{seed}") for seed in range(BITS)]
            leaf[(node, pin)] = choices
            optimizer.add(AtMost(*choices, 1))
            for seed_bit, choice in enumerate(choices):
                optimizer.add(Implies(choice, mapping[seed_bit][state_bit]))

    raw: dict[tuple[int, int], list[object]] = {}
    for index, steady_target in enumerate(B):
        if steady_target in DIRECT or steady_target in FIRST_LAYER:
            continue
        gate = GATE_BY_OUTPUT[steady_target]
        for side, node in enumerate((gate.left, gate.right)):
            if node not in DIRECT:
                continue
            state_bit = bits(node)[0]
            choices = [Bool(f"raw_{index}_{side}_{seed}") for seed in range(BITS)]
            raw[(index, side)] = choices
            optimizer.add(AtMost(*choices, 1))
            for seed_bit, choice in enumerate(choices):
                optimizer.add(Implies(choice, mapping[seed_bit][state_bit]))

    def coefficient(node: int, seed_bit: int, consumer: int, side: int):
        if node in FIRST_LAYER:
            return Xor(leaf[(node, 0)][seed_bit], leaf[(node, 1)][seed_bit])
        return raw[(consumer, side)][seed_bit]

    for index, (seed_target, steady_target) in enumerate(zip(T, B)):
        if steady_target in DIRECT:
            optimizer.add(mapping[bits(seed_target)[0]][bits(steady_target)[0]])
            continue
        if steady_target in FIRST_LAYER:
            for seed_bit in range(BITS):
                optimizer.add(
                    coefficient(steady_target, seed_bit, index, 0)
                    == bool((seed_target >> seed_bit) & 1)
                )
            continue
        gate = GATE_BY_OUTPUT[steady_target]
        for seed_bit in range(BITS):
            optimizer.add(
                Xor(
                    coefficient(gate.left, seed_bit, index, 0),
                    coefficient(gate.right, seed_bit, index, 1),
                )
                == bool((seed_target >> seed_bit) & 1)
            )

    objective = Sum(
        *(If(variable, 1, 0) for row in mapping for variable in row)
    )
    handle = optimizer.minimize(objective)
    if optimizer.check() != sat:
        raise AssertionError("mode-pair optimization is unexpectedly unsatisfiable")
    optimum = int(str(optimizer.lower(handle)))
    model = optimizer.model()
    selected = {
        (seed, state)
        for seed in range(BITS)
        for state in range(BITS)
        if is_true(model.eval(mapping[seed][state]))
    }
    if optimum != 47 or len(selected) != optimum:
        raise AssertionError(f"expected fixed-DAG optimum 47, got {optimum}")
    print("Z3 proved the fixed 61-XOR DAG needs at least 47 mode-pair OR gates")


def signal_name(value: int) -> str:
    if value.bit_count() == 1:
        return f"q{value.bit_length() - 1}"
    return f"n_{value:08x}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gates", action="store_true", help="print the shared XOR DAG")
    parser.add_argument("--pairs", action="store_true", help="print the 47 OR mode pairs")
    parser.add_argument(
        "--prove-minimum",
        action="store_true",
        help="use optional z3-solver to prove the fixed-DAG OR minimum",
    )
    args = parser.parse_args()

    if compose(C, T) != A or compose(T, C) != B:
        raise AssertionError("encoded matrix identities failed")
    if compose(T, T_INVERSE) != IDENTITY:
        raise AssertionError("T is not invertible")

    seed_labels, used_pairs = verify_dual_labels()
    verify_sequences()

    xor_count = len(GATES)
    or_count = len(used_pairs)
    gate_score = (
        BITS * DELAY_BIT_GATE_COST
        + xor_count * XOR_GATE_COST
        + or_count * OR_GATE_COST
        + CONTROL_GATE_COST
    )
    delay = DELAY_BIT_DELAY + OR_DELAY + 2 * XOR_DELAY
    cycles = 66
    if (xor_count, or_count, gate_score, delay, cycles) != (61, 47, 396, 9, 66):
        raise AssertionError("candidate metrics changed")

    print("matrix identities: C*T=A, T*C=B, T*T^-1=I")
    print("tick-zero feedback labels: T(seed)")
    print("steady feedback/output labels: B(q), C(q)")
    print(f"shared XOR DAG: {xor_count} nodes, depth 2")
    print(f"mode-pair OR bank: {or_count} nodes, delay 1")
    print(f"candidate tuple: {gate_score}/{delay}/{cycles}")
    print(f"energy: {gate_score * delay * cycles}")
    print("verified seeds:", 69)

    if args.prove_minimum:
        prove_mode_pair_minimum()
    if args.pairs:
        for seed_bit, state_bit in sorted(used_pairs):
            print(f"m_s{seed_bit}_q{state_bit} = seed[{seed_bit}] OR q[{state_bit}]")
    if args.gates:
        for gate in GATES:
            print(
                f"d{gate.depth} {signal_name(gate.output)} = "
                f"{signal_name(gate.left)} XOR {signal_name(gate.right)}; "
                f"tick0=0x{seed_labels[gate.output]:08x}"
            )


if __name__ == "__main__":
    main()
