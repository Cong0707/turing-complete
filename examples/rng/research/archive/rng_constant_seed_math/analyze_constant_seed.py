"""Analyze the RNG construction that keeps the test seed available every tick.

This is a research-only module.  It does not import the save writer, touch the
live schematic, or start the game.

For a natural state ``x`` and the constant architecture input ``s``, use

    q = T (x xor s)

so the all-zero Delay Bit initialization is already the correct encoded state.
The combinational maps are

    q_next = B q xor D s
    output = C q xor A s

where ``B=T A T^-1``, ``C=A T^-1`` and ``D=T(A+I)``.  At tick zero q=0,
therefore the first visible result is A*s and no load/ready tick is needed.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import random
from typing import Callable, Iterable, Sequence


BITS = 32
INPUT_BITS = 64
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
        low = remaining & -remaining
        result ^= matrix[low.bit_length() - 1]
        remaining ^= low
    return result


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(matrix))


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def add(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(a ^ b for a, b in zip(left, right))


def invert(matrix: Sequence[int]) -> tuple[int, ...]:
    rows = [matrix[index] | ((1 << index) << BITS) for index in range(BITS)]
    for column in range(BITS):
        pivot = next(
            (index for index in range(column, BITS) if rows[index] >> column & 1),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for index in range(BITS):
            if index != column and rows[index] >> column & 1:
                rows[index] ^= rows[column]
    return tuple((row >> BITS) & MASK for row in rows)


def right_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(lambda value: (value ^ (value >> distance)) & MASK)


def left_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(lambda value: (value ^ (value << distance)) & MASK)


A = matrix_from_function(xorshift32)


@dataclass(frozen=True)
class Construction:
    name: str
    t: tuple[int, ...]
    t_inverse: tuple[int, ...]
    b: tuple[int, ...]
    c: tuple[int, ...]
    d: tuple[int, ...]
    feedback: tuple[int, ...]
    output: tuple[int, ...]

    @property
    def targets(self) -> tuple[int, ...]:
        return self.feedback + self.output


def construction(name: str, t: Sequence[int]) -> Construction:
    t = tuple(t)
    t_inverse = invert(t)
    b = compose(t, compose(A, t_inverse))
    c = compose(A, t_inverse)
    d = compose(t, add(A, IDENTITY))
    feedback = tuple(q | (s << BITS) for q, s in zip(b, d))
    output = tuple(q | (s << BITS) for q, s in zip(c, A))
    result = Construction(name, t, t_inverse, b, c, d, feedback, output)
    verify_identities(result)
    return result


def verify_identities(item: Construction) -> None:
    if compose(item.c, item.t) != A:
        raise AssertionError("C*T != A")
    if compose(item.t, item.c) != item.b:
        raise AssertionError("T*C != B")
    if compose(item.t, item.t_inverse) != IDENTITY:
        raise AssertionError("T*T^-1 != I")
    if item.d != compose(item.t, add(A, IDENTITY)):
        raise AssertionError("D != T*(A+I)")


def verify_protocol(item: Construction, seeds: Iterable[int]) -> None:
    for seed in seeds:
        q = 0
        natural = seed
        for _tick in range(65):
            combined = q | (seed << BITS)
            visible = apply_matrix(item.output, combined)
            next_q = apply_matrix(item.feedback, combined)
            natural = xorshift32(natural)
            if visible != natural:
                raise AssertionError(
                    f"{item.name}: output mismatch for seed {seed:08x}"
                )
            expected_q = apply_matrix(item.t, natural ^ seed)
            if next_q != expected_q:
                raise AssertionError(
                    f"{item.name}: state mismatch for seed {seed:08x}"
                )
            q = next_q


def histogram(values: Iterable[int]) -> dict[int, int]:
    return dict(sorted(Counter(values).items()))


def stats(item: Construction) -> dict[str, object]:
    targets = item.targets
    unique = frozenset(targets)
    nonunit = frozenset(row for row in unique if row.bit_count() > 1)
    return {
        "name": item.name,
        "T_weight_histogram": histogram(row.bit_count() for row in item.t),
        "B_weight_histogram": histogram(row.bit_count() for row in item.b),
        "C_weight_histogram": histogram(row.bit_count() for row in item.c),
        "D_weight_histogram": histogram(row.bit_count() for row in item.d),
        "feedback_weight_histogram": histogram(row.bit_count() for row in item.feedback),
        "output_weight_histogram": histogram(row.bit_count() for row in item.output),
        "distinct_targets": len(unique),
        "distinct_nonunit_targets": len(nonunit),
        "target_gate_lower_bound": len(nonunit),
        "maximum_target_weight": max(row.bit_count() for row in targets),
        "depth2_raw_inputs_possible": max(row.bit_count() for row in targets) <= 4,
    }


def named_constructions() -> tuple[Construction, ...]:
    two_shear = compose(right_shear(17), right_shear(13))
    return (
        construction("identity", IDENTITY),
        construction("two-shear-R13-R17", two_shear),
    )


def current_decode_targets(item: Construction) -> tuple[int, ...]:
    """Return feedback plus the current-state decoder used after a hidden tick.

    The decoder is ``x=T^-1*q xor s``.  Its tick-zero value is deliberately
    hidden by one initialized Delay Bit; ticks 1..65 expose A*s..A^65*s.
    """

    decoder = tuple(row | (1 << (BITS + bit)) for bit, row in enumerate(item.t_inverse))
    return item.feedback + decoder


def verilog_expression(row: int) -> str:
    terms = []
    for bit in range(INPUT_BITS):
        if row >> bit & 1:
            terms.append(f"q[{bit}]" if bit < BITS else f"s[{bit - BITS}]")
    return " ^ ".join(terms) if terms else "1'b0"


def write_verilog(path: Path, item: Construction, target_mode: str) -> None:
    if target_mode == "direct-next":
        targets = item.targets
    elif target_mode == "current-decode":
        targets = current_decode_targets(item)
    else:
        raise ValueError(f"unknown target mode {target_mode!r}")
    lines = [
        f"module constant_seed_{item.name.replace('-', '_')}(q, s, y);",
        "  input [31:0] q;",
        "  input [31:0] s;",
        "  output [63:0] y;",
    ]
    lines.extend(
        f"  assign y[{index}] = {verilog_expression(row)};"
        for index, row in enumerate(targets)
    )
    lines.append("endmodule")
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    parser.add_argument("--verilog", type=Path)
    parser.add_argument(
        "--construction",
        choices=("identity", "two-shear-R13-R17"),
        default="identity",
    )
    parser.add_argument(
        "--target-mode",
        choices=("direct-next", "current-decode"),
        default="current-decode",
    )
    args = parser.parse_args()

    generator = random.Random(20260801)
    seeds = (0, 1, 2, 0x12345678, 0xFFFFFFFF) + tuple(
        generator.getrandbits(BITS) for _ in range(64)
    )
    documents = []
    for item in named_constructions():
        verify_protocol(item, seeds)
        document = stats(item)
        documents.append(document)
        print(json.dumps(document, indent=2))
    if args.json:
        args.json.write_text(json.dumps(documents, indent=2) + "\n", encoding="utf-8")
    if args.verilog:
        selected = next(item for item in named_constructions() if item.name == args.construction)
        write_verilog(args.verilog, selected, args.target_mode)


if __name__ == "__main__":
    main()
