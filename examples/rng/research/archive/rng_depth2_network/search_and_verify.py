"""Verify a depth-two encoded implementation of the RNG linear map.

This is a research-only tool.  It reads and writes no save data, starts no
game process, and uses 32-bit integers as GF(2) row vectors.

The convention is::

    x_next = A x
    q      = T x
    q_next = B q = T A T^-1 q
    x_next = C q = A T^-1 q

Run ``python search_and_verify.py`` for the standard-library certificate.
Install z3-solver separately and add ``--prove-minimum`` to re-prove the
minimum pair-node counts for this fixed encoding.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Iterable, Sequence


BITS = 32
MASK = (1 << BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(BITS))


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


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    """Return the row matrix for ``left(right(x))``."""

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


def left_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(
        lambda value: (value ^ ((value << distance) & MASK)) & MASK
    )


A = matrix_from_function(xorshift32)
R13 = right_shear(13)
R17 = right_shear(17)

# R13 and R17 commute.  The two spellings found by the ordered family search
# below therefore describe one matrix.
T = compose(R17, R13)
T_INVERSE = invert(T)
C = compose(A, T_INVERSE)
B = compose(T, C)


# These pair nodes are a concrete optimum for each fixed row set.  The
# optional Z3 proof reconstructs the optimization problem rather than
# trusting these constants.
T_EXTRA_PAIRS = frozenset(
    int(value, 16)
    for value in (
        "00020001",
        "00040002",
        "00040020",
        "00080040",
        "00088000",
        "00110000",
        "00220000",
        "00400200",
        "00800400",
        "01000800",
        "01100000",
        "02001000",
        "02200000",
        "40002000",
        "80004000",
    )
)

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

TBC_EXTRA_PAIRS = frozenset(
    int(value, 16)
    for value in (
        "00004002",
        "00008004",
        "00020001",
        "00040020",
        "00080040",
        "00100008",
        "00200010",
        "00400200",
        "00420000",
        "00800400",
        "00840000",
        "01000080",
        "01000800",
        "01080000",
        "02100000",
        "02200000",
        "04200000",
        "08004000",
        "08008000",
        "08400000",
        "10010000",
        "10800000",
        "20000001",
        "20001000",
        "21000000",
        "40000002",
        "40002000",
        "42000000",
        "80000004",
        "84000000",
    )
)


@dataclass(frozen=True)
class XorGate:
    output: int
    left: int
    right: int
    depth: int


@dataclass(frozen=True)
class Network:
    gates: tuple[XorGate, ...]
    outputs: tuple[int, ...]

    @property
    def gate_count(self) -> int:
        return len(self.gates)

    @property
    def depth(self) -> int:
        return max((gate.depth for gate in self.gates), default=0)


def input_pair_values() -> frozenset[int]:
    return frozenset((1 << left) ^ (1 << right) for left, right in combinations(range(BITS), 2))


def pair_partitions(row: int) -> tuple[tuple[int, int], ...]:
    bits = tuple(bit for bit in range(BITS) if (row >> bit) & 1)
    if len(bits) == 3:
        result = []
        for lone in bits:
            result.append((1 << lone, row ^ (1 << lone)))
        return tuple(result)
    if len(bits) == 4:
        a, b, c, d = bits
        return (
            ((1 << a) ^ (1 << b), (1 << c) ^ (1 << d)),
            ((1 << a) ^ (1 << c), (1 << b) ^ (1 << d)),
            ((1 << a) ^ (1 << d), (1 << b) ^ (1 << c)),
        )
    raise ValueError(f"row {row:08x} does not need a depth-two partition")


def synthesize(rows: Iterable[int], extra_pairs: frozenset[int]) -> Network:
    outputs = tuple(rows)
    unique = frozenset(outputs)
    direct = frozenset(IDENTITY)
    pair_outputs = frozenset(
        row for row in unique - direct if row.bit_count() == 2
    )
    first_layer = pair_outputs | extra_pairs
    if not first_layer <= input_pair_values():
        raise AssertionError("a declared first-layer node is not an input pair")

    gates: list[XorGate] = []
    for pair in sorted(first_layer):
        bits = tuple(bit for bit in range(BITS) if (pair >> bit) & 1)
        gates.append(XorGate(pair, 1 << bits[0], 1 << bits[1], 1))

    available = direct | first_layer
    for row in sorted(unique - direct - pair_outputs):
        if not 3 <= row.bit_count() <= 4:
            raise AssertionError(
                f"row {row:08x} has support {row.bit_count()}, so depth two is impossible"
            )
        partition = next(
            (
                (left, right)
                for left, right in pair_partitions(row)
                if left in available and right in available
            ),
            None,
        )
        if partition is None:
            raise AssertionError(f"no declared pair nodes cover row {row:08x}")
        gates.append(XorGate(row, partition[0], partition[1], 2))

    seen = set(IDENTITY)
    for gate in gates:
        if gate.left not in seen or gate.right not in seen:
            raise AssertionError(f"gate {gate.output:08x} has a forward reference")
        if gate.left ^ gate.right != gate.output:
            raise AssertionError(f"gate {gate.output:08x} has incorrect semantics")
        seen.add(gate.output)
    if not unique <= seen:
        raise AssertionError("not every requested output was synthesized")
    return Network(tuple(gates), outputs)


def weight_histogram(rows: Iterable[int]) -> dict[int, int]:
    result: dict[int, int] = {}
    for row in rows:
        weight = row.bit_count()
        result[weight] = result.get(weight, 0) + 1
    return dict(sorted(result.items()))


def enumerate_two_shear_family() -> list[tuple[str, str]]:
    shears: dict[str, tuple[int, ...]] = {"I": IDENTITY}
    for distance in range(1, BITS):
        shears[f"R{distance}"] = right_shear(distance)
        shears[f"L{distance}"] = left_shear(distance)

    feasible: list[tuple[str, str]] = []
    for first_name, first in shears.items():
        for second_name, second in shears.items():
            candidate_t = compose(second, first)
            candidate_c = compose(A, invert(candidate_t))
            candidate_b = compose(candidate_t, candidate_c)
            if max(row.bit_count() for row in candidate_b + candidate_c) <= 4:
                feasible.append((first_name, second_name))
    return feasible


def prove_pair_minimum(
    rows: Iterable[int], expected_extra_count: int, label: str
) -> None:
    try:
        from z3 import And, Bool, If, Optimize, Or, Sum, is_true, sat
    except ImportError as error:  # pragma: no cover - optional research dependency
        raise SystemExit(
            "--prove-minimum requires an external `pip install z3-solver`"
        ) from error

    unique = frozenset(rows)
    direct = frozenset(IDENTITY)
    pair_outputs = frozenset(
        row for row in unique - direct if row.bit_count() == 2
    )
    hard = unique - direct - pair_outputs

    raw_options: list[tuple[tuple[int, ...], ...]] = []
    candidates: set[int] = set()
    for row in hard:
        options = []
        for left, right in pair_partitions(row):
            required = tuple(
                value
                for value in (left, right)
                if value.bit_count() == 2 and value not in pair_outputs
            )
            options.append(required)
            candidates.update(required)
        raw_options.append(tuple(options))

    variables = {value: Bool(f"{label}_{value:08x}") for value in candidates}
    optimizer = Optimize()
    for options in raw_options:
        optimizer.add(
            Or(
                *(
                    And(*(variables[value] for value in option))
                    if option
                    else True
                    for option in options
                )
            )
        )
    objective = Sum(*(If(variable, 1, 0) for variable in variables.values()))
    handle = optimizer.minimize(objective)
    if optimizer.check() != sat:
        raise AssertionError(f"{label}: pair-node problem is unexpectedly unsatisfiable")
    model = optimizer.model()
    selected = frozenset(
        value for value, variable in variables.items() if is_true(model.eval(variable))
    )
    optimum = int(str(optimizer.lower(handle)))
    if optimum != expected_extra_count or len(selected) != optimum:
        raise AssertionError(
            f"{label}: expected {expected_extra_count} extra pairs, got {optimum}"
        )
    print(f"{label}: Z3 proved {optimum} extra pair nodes are necessary")


def print_matrix(label: str, matrix: Sequence[int]) -> None:
    print(f"{label} = [")
    for index, row in enumerate(matrix):
        terms = " ^ ".join(f"v{bit}" for bit in range(BITS) if (row >> bit) & 1)
        print(f"  {index:2d}: 0x{row:08x}  {terms}")
    print("]")


def signal_name(value: int) -> str:
    if value.bit_count() == 1:
        return f"v{value.bit_length() - 1}"
    return f"n_{value:08x}"


def print_network(label: str, network: Network) -> None:
    print(f"{label} gates = [")
    for gate in network.gates:
        print(
            f"  d{gate.depth} {signal_name(gate.output)} = "
            f"{signal_name(gate.left)} XOR {signal_name(gate.right)}"
        )
    print("]")
    print(f"{label} outputs = [")
    for index, output in enumerate(network.outputs):
        print(f"  {index:2d}: {signal_name(output)}  (0x{output:08x})")
    print("]")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrices", action="store_true", help="print all T/C/B rows")
    parser.add_argument("--gates", action="store_true", help="print the verified XOR gate lists")
    parser.add_argument(
        "--prove-minimum",
        action="store_true",
        help="use optional z3-solver to prove fixed-encoding pair-node minima",
    )
    args = parser.parse_args()

    if compose(C, T) != A:
        raise AssertionError("C*T != A")
    if compose(T, C) != B:
        raise AssertionError("T*C != B")
    if compose(T, T_INVERSE) != IDENTITY:
        raise AssertionError("T inverse is incorrect")

    natural_heavy = tuple((index, row) for index, row in enumerate(A) if row.bit_count() > 4)
    if len(natural_heavy) != 15 or max(row.bit_count() for row in A) != 7:
        raise AssertionError("natural-state obstruction changed")

    network_t = synthesize(T, T_EXTRA_PAIRS)
    network_bc = synthesize(B + C, BC_EXTRA_PAIRS)
    network_tbc = synthesize(T + B + C, TBC_EXTRA_PAIRS)
    if (network_t.gate_count, network_t.depth) != (34, 2):
        raise AssertionError("unexpected T network metrics")
    if (network_bc.gate_count, network_bc.depth) != (61, 2):
        raise AssertionError("unexpected B/C network metrics")
    if (network_tbc.gate_count, network_tbc.depth) != (95, 2):
        raise AssertionError("unexpected T/B/C union metrics")

    feasible = enumerate_two_shear_family()
    if feasible != [("R13", "R17"), ("R17", "R13")]:
        raise AssertionError(f"two-shear family result changed: {feasible}")

    print("natural A row weights:", weight_histogram(A))
    print("natural depth<=2 obstruction: 15 rows have support > 4")
    print("T row weights:", weight_histogram(T))
    print("C row weights:", weight_histogram(C))
    print("B row weights:", weight_histogram(B))
    print("two-shear feasible ordered spellings:", feasible)
    print(f"T network:   {network_t.gate_count} XOR, depth {network_t.depth}")
    print(f"B/C network: {network_bc.gate_count} XOR, depth {network_bc.depth}")
    print(f"ideal T/B/C union: {network_tbc.gate_count} XOR, depth {network_tbc.depth}")
    print("target gap: 95 - 67 = 28 XOR")
    print("estimated TC gate score with 32 Delay + 32 Switch + control:", 160 + 64 + 3 * 95 + 6)

    if args.prove_minimum:
        prove_pair_minimum(T, 15, "T")
        prove_pair_minimum(B + C, 15, "BC")
        prove_pair_minimum(T + B + C, 30, "TBC")

    if args.matrices:
        print_matrix("T", T)
        print_matrix("C", C)
        print_matrix("B", B)
    if args.gates:
        print_network("T", network_t)
        print_network("B/C", network_bc)
        print_network("T/B/C union", network_tbc)


if __name__ == "__main__":
    main()
