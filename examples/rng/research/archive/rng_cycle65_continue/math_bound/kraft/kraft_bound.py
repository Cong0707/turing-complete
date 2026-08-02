"""Single-target timing bound for the fixed two-shear 65-cycle RNG model.

This is a research-only certificate generator.  It reconstructs the matrices
used by ``rng_constant_seed_math/analyze_constant_seed.py`` and never reads or
writes a game save.

For an XOR2 formula whose q leaves arrive at 4, seed leaves arrive at 0, each
XOR2 adds 2, and the output must arrive by 9, every q occurrence has depth at
most 2 and every seed occurrence has depth at most 4.  Unfolding an arbitrary
fanout/reconvergent DAG into a binary formula gives the necessary Kraft bound

    |Q| / 2**2 + |S| / 2**4 <= 1,

or equivalently ``4*|Q| + |S| <= 16``.
"""

from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Callable, Iterable, Sequence


BITS = 32
MASK = (1 << BITS) - 1
Q_ARRIVAL = 4
SEED_ARRIVAL = 0
XOR2_DELAY = 2
DELAY_LIMIT = 9
Q_DEPTH_LIMIT = (DELAY_LIMIT - Q_ARRIVAL) // XOR2_DELAY
SEED_DEPTH_LIMIT = (DELAY_LIMIT - SEED_ARRIVAL) // XOR2_DELAY
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
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
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
        pivot = next(index for index in range(column, BITS) if rows[index] >> column & 1)
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for index in range(BITS):
            if index != column and rows[index] >> column & 1:
                rows[index] ^= rows[column]
    return tuple((row >> BITS) & MASK for row in rows)


def right_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(lambda value: (value ^ (value >> distance)) & MASK)


def matrix_digest(named_matrices: Iterable[tuple[str, Sequence[int]]]) -> str:
    digest = hashlib.sha256()
    for name, matrix in named_matrices:
        digest.update(name.encode("ascii") + b"\0")
        for row in matrix:
            digest.update(int(row).to_bytes(4, "little"))
    return digest.hexdigest()


@lru_cache(maxsize=None)
def possible_tree_supports(
    q_depth_limit: int, seed_depth_limit: int, depth: int = 0
) -> frozenset[tuple[int, int]]:
    """Return typed leaf counts for full binary trees rooted at ``depth``."""

    result: set[tuple[int, int]] = set()
    if depth <= q_depth_limit:
        result.add((1, 0))
    if depth <= seed_depth_limit:
        result.add((0, 1))
    if depth < max(q_depth_limit, seed_depth_limit):
        children = possible_tree_supports(q_depth_limit, seed_depth_limit, depth + 1)
        for left_q, left_s in children:
            for right_q, right_s in children:
                result.add((left_q + right_q, left_s + right_s))
    return frozenset(result)


def verify_support_envelope() -> dict[str, int]:
    """Exhaustively check that Kraft gives the exact typed-leaf envelope."""

    possible = possible_tree_supports(Q_DEPTH_LIMIT, SEED_DEPTH_LIMIT)
    for q_count in range(0, 5):
        for seed_count in range(0, 17):
            if q_count + seed_count == 0:
                continue
            kraft = 4 * q_count + seed_count <= 16
            if ((q_count, seed_count) in possible) != kraft:
                raise AssertionError((q_count, seed_count, kraft))
    return {str(q_count): 16 - 4 * q_count for q_count in range(5)}


def minimum_formula_delay(q_count: int, seed_count: int) -> int:
    """Return the exact minimum root arrival for a parity with this support."""

    for delay in range(0, 33):
        q_depth = (delay - Q_ARRIVAL) // XOR2_DELAY if delay >= Q_ARRIVAL else -1
        seed_depth = (
            (delay - SEED_ARRIVAL) // XOR2_DELAY if delay >= SEED_ARRIVAL else -1
        )
        if (q_count, seed_count) in possible_tree_supports(q_depth, seed_depth):
            return delay
    raise AssertionError((q_count, seed_count))


def target_record(kind: str, index: int, q_row: int, seed_row: int) -> dict[str, object]:
    q_count = q_row.bit_count()
    seed_count = seed_row.bit_count()
    kraft_numerator = 4 * q_count + seed_count
    timing_feasible = kraft_numerator <= 16
    formula_delay = minimum_formula_delay(q_count, seed_count)
    if timing_feasible != (formula_delay <= DELAY_LIMIT):
        raise AssertionError((kind, index, timing_feasible, formula_delay))
    return {
        "name": f"{kind}[{index}]",
        "q_row_hex": f"0x{q_row:08x}",
        "seed_row_hex": f"0x{seed_row:08x}",
        "q_support": q_count,
        "seed_support": seed_count,
        "total_support": q_count + seed_count,
        "kraft_numerator_over_16": kraft_numerator,
        "timing_feasible": timing_feasible,
        "minimum_formula_delay": formula_delay,
        "cone_xor2_lower_bound": q_count + seed_count - 1,
        "minimum_unshared_tree_xor2": q_count + seed_count - 1 if timing_feasible else None,
    }


def histogram(records: Sequence[dict[str, object]], key: str) -> dict[str, int]:
    return {
        str(value): count
        for value, count in sorted(Counter(int(record[key]) for record in records).items())
    }


def build_certificate() -> dict[str, object]:
    a = matrix_from_function(xorshift32)
    # This is the exact fixed construction named two-shear-R13-R17 by the
    # canonical analysis script.  The two right shears commute.
    t = compose(right_shear(17), right_shear(13))
    t_inverse = invert(t)
    b = compose(t, compose(a, t_inverse))
    c = compose(a, t_inverse)
    d = compose(t, add(a, IDENTITY))

    if compose(t, t_inverse) != IDENTITY:
        raise AssertionError("T inverse mismatch")
    if compose(c, t) != a or compose(t, c) != b:
        raise AssertionError("two-shear identities changed")
    if d != compose(t, add(a, IDENTITY)):
        raise AssertionError("D identity changed")

    records = [
        target_record("feedback", index, q_row, seed_row)
        for index, (q_row, seed_row) in enumerate(zip(b, d))
    ] + [
        target_record("output", index, q_row, seed_row)
        for index, (q_row, seed_row) in enumerate(zip(c, a))
    ]

    feedback_bad = [
        int(record["name"].split("[")[1][:-1])
        for record in records[:BITS]
        if not record["timing_feasible"]
    ]
    output_bad = [
        int(record["name"].split("[")[1][:-1])
        for record in records[BITS:]
        if not record["timing_feasible"]
    ]
    if feedback_bad != list(range(19)):
        raise AssertionError(feedback_bad)
    if output_bad != list(range(10)) + [12, 13, 14]:
        raise AssertionError(output_bad)

    # Protocol check on all basis seeds plus several edge cases.
    for seed in (0, MASK, 0x12345678) + tuple(1 << bit for bit in range(BITS)):
        q = 0
        natural = seed
        for _ in range(65):
            visible = apply_matrix(c, q) ^ apply_matrix(a, seed)
            next_q = apply_matrix(b, q) ^ apply_matrix(d, seed)
            natural = xorshift32(natural)
            if visible != natural:
                raise AssertionError((seed, "visible"))
            if next_q != apply_matrix(t, natural ^ seed):
                raise AssertionError((seed, "state"))
            q = next_q

    feasible = [record for record in records if record["timing_feasible"]]
    infeasible = [record for record in records if not record["timing_feasible"]]
    return {
        "scope": "fixed two-shear T, constant-seed, 65-cycle direct-output, XOR2 only",
        "canonical_definition": ".research/rng_constant_seed_math/analyze_constant_seed.py",
        "model": {
            "feedback": "q_next = B*q xor D*seed",
            "output": "y = C*q xor A*seed",
            "T": "R17_right o R13_right",
            "B": "T*A*T^-1",
            "C": "A*T^-1",
            "D": "T*(A+I)",
        },
        "timing": {
            "q_leaf_arrival": Q_ARRIVAL,
            "seed_leaf_arrival": SEED_ARRIVAL,
            "xor2_delay": XOR2_DELAY,
            "delay_limit": DELAY_LIMIT,
            "q_path_xor2_limit": Q_DEPTH_LIMIT,
            "seed_path_xor2_limit": SEED_DEPTH_LIMIT,
        },
        "proof": {
            "kraft_necessary": "q_support/4 + seed_support/16 <= 1",
            "integer_form": "4*q_support + seed_support <= 16",
            "support_envelope_max_seed_by_q": verify_support_envelope(),
            "cone_gate_lower_bound": "q_support + seed_support - 1",
            "minimum_delay_method": "exact typed full-binary-tree enumeration",
            "dag_note": "unfolding fanout/reconvergence only duplicates leaves; each supported variable still has at least one occurrence",
        },
        "matrix_sha256_le_u32": matrix_digest(
            (("A", a), ("T", t), ("T_inverse", t_inverse), ("B", b), ("C", c), ("D", d))
        ),
        "summary": {
            "target_count": len(records),
            "timing_feasible_count": len(feasible),
            "timing_infeasible_count": len(infeasible),
            "feedback_infeasible_indices": feedback_bad,
            "output_infeasible_indices": output_bad,
            "feedback_pair_histogram": {
                f"q{q}_s{s}": count
                for (q, s), count in sorted(
                    Counter(
                        (int(record["q_support"]), int(record["seed_support"]))
                        for record in records[:BITS]
                    ).items()
                )
            },
            "output_pair_histogram": {
                f"q{q}_s{s}": count
                for (q, s), count in sorted(
                    Counter(
                        (int(record["q_support"]), int(record["seed_support"]))
                        for record in records[BITS:]
                    ).items()
                )
            },
            "kraft_numerator_histogram": histogram(records, "kraft_numerator_over_16"),
            "individual_cone_xor2_lower_bound_histogram": histogram(
                records, "cone_xor2_lower_bound"
            ),
            "minimum_formula_delay_histogram": histogram(records, "minimum_formula_delay"),
        },
        "conclusion": (
            "UNSAT at delay <= 9 regardless of the XOR2 gate budget: "
            "32 required targets violate the single-target Kraft bound"
        ),
        "targets": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    certificate = build_certificate()
    rendered = json.dumps(certificate, indent=2) + "\n"
    if args.json:
        args.json.write_text(rendered, encoding="ascii")
    print(rendered, end="")


if __name__ == "__main__":
    main()
