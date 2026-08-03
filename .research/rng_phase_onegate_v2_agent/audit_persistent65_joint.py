#!/usr/bin/env python3
"""Audit invariant and arrival lower bounds for the 65-cycle RNG map.

This script is deliberately independent from save generation.  It checks the
full linear map [B|D; C|A], the strict leaderboard budgets, and the XOR2
mixed-arrival Kraft obstruction for a corpus of candidate state bases.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable, Iterator, Sequence


BITS = 32
MASK = (1 << BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(BITS))
STATE_GATE = 5
STATE_DELAY = 4
XOR_GATE = 3
XOR_DELAY = 2
CYCLES = 65
VERIFIED_REFERENCE = (402, 9, 67)
RESEARCH_REFERENCE = (401, 9, 67)


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


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def inverse(matrix: Sequence[int]) -> tuple[int, ...]:
    work = list(matrix)
    result = list(IDENTITY)
    for column in range(BITS):
        pivot = next(
            (row for row in range(column, BITS) if work[row] >> column & 1),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        result[column], result[pivot] = result[pivot], result[column]
        for row in range(BITS):
            if row != column and work[row] >> column & 1:
                work[row] ^= work[column]
                result[row] ^= result[column]
    return tuple(result)


def rank(rows: Iterable[int], width: int) -> int:
    basis = [0] * width
    result = 0
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if basis[pivot]:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                result += 1
                break
    return result


def matrices(t: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    a = transition()
    ti = inverse(t)
    a_plus_i = tuple(row ^ unit for row, unit in zip(a, IDENTITY, strict=True))
    b = compose(compose(t, a), ti)
    d = compose(t, a_plus_i)
    c = compose(a, ti)
    return b, d, c, a


def targets(t: Sequence[int]) -> tuple[int, ...]:
    b, d, c, a = matrices(t)
    return tuple(
        [b[row] | (d[row] << BITS) for row in range(BITS)]
        + [c[row] | (a[row] << BITS) for row in range(BITS)]
    )


def parse_matrix(value: object) -> tuple[int, ...] | None:
    if not isinstance(value, list) or len(value) != BITS:
        return None
    try:
        return tuple(int(str(item), 16) for item in value)
    except (ValueError, TypeError):
        return None


def candidate_t(record: dict[str, object], a: Sequence[int]) -> tuple[int, ...] | None:
    direct = parse_matrix(record.get("T"))
    if direct is not None:
        try:
            inverse(direct)
        except ValueError:
            return None
        return direct

    c = parse_matrix(record.get("C"))
    b = parse_matrix(record.get("B"))
    d = parse_matrix(record.get("D"))
    if c is None or b is None or d is None:
        return None
    try:
        c_inverse = inverse(c)
    except ValueError:
        return None
    a_plus_i = tuple(row ^ unit for row, unit in zip(a, IDENTITY, strict=True))

    # True 65-cycle records store C=A*T^-1.
    t65 = compose(c_inverse, a)
    t65_inverse = inverse(t65)
    if (
        compose(compose(t65, a), t65_inverse) == b
        and compose(t65, a_plus_i) == d
    ):
        return t65

    # A 66-cycle record stores C=T^-1.  Its T is still a valid state basis to
    # rescore under the true 65-cycle equations.
    t66 = c_inverse
    if (
        compose(compose(t66, a), c) == b
        and compose(t66, a_plus_i) == d
    ):
        return t66
    return None


def nested(value: object) -> Iterator[dict[str, object]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nested(child)
    elif isinstance(value, list):
        for child in value:
            yield from nested(child)


def records(path: Path) -> Iterator[dict[str, object]]:
    if path.suffix.lower() == ".jsonl":
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                try:
                    yield from nested(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return
    try:
        yield from nested(json.loads(path.read_text(encoding="utf-8-sig")))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return


def strict_logic_budget(reference: tuple[int, int, int], delay: int) -> int:
    reference_energy = reference[0] * reference[1] * reference[2]
    total_gate = (reference_energy - 1) // (delay * CYCLES)
    return total_gate - BITS * STATE_GATE


def audit_t(t: Sequence[int]) -> dict[str, object]:
    b, d, c, a = matrices(t)
    rows = targets(t)
    feedback = [
        4 * left.bit_count() + right.bit_count()
        for left, right in zip(b, d, strict=True)
    ]
    visible = [
        4 * left.bit_count() + right.bit_count()
        for left, right in zip(c, a, strict=True)
    ]
    metrics = feedback + visible
    q_weights = [row.bit_count() for row in (*b, *c)]
    seed_weights = [row.bit_count() for row in (*d, *a)]
    return {
        "rank": rank(rows, 2 * BITS),
        "distinct_targets": len(set(rows)),
        "input_aliases": sum(row.bit_count() == 1 for row in rows),
        "nonzero_q_halves": sum(weight > 0 for weight in q_weights),
        "nonzero_seed_halves": sum(weight > 0 for weight in seed_weights),
        "mandatory_target_nodes": sum(row.bit_count() > 1 for row in rows),
        "mixed_over": sum(metric > 16 for metric in metrics),
        "mixed_excess": sum(max(0, metric - 16) for metric in metrics),
        "mixed_max": max(metrics),
        "q_weight_histogram": dict(sorted(Counter(q_weights).items())),
        "seed_weight_histogram": dict(sorted(Counter(seed_weights).items())),
        "target_sha256": sha256(
            b"".join(row.to_bytes(8, "little") for row in rows)
        ).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="*")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    a = transition()
    a_plus_i = tuple(row ^ unit for row, unit in zip(a, IDENTITY, strict=True))
    seen: set[tuple[int, ...]] = set()
    frontier: list[dict[str, object]] = []
    objects = matrices_seen = 0
    for path in args.inputs:
        for index, record in enumerate(records(path)):
            objects += 1
            t = candidate_t(record, a)
            if t is None:
                continue
            matrices_seen += 1
            if t in seen:
                continue
            seen.add(t)
            result = audit_t(t)
            result.update({"source": str(path), "record_index": index})
            frontier.append(result)

    frontier.sort(
        key=lambda item: (
            item["mixed_over"], item["mixed_excess"], item["mixed_max"]
        )
    )
    identity_t = IDENTITY
    identity_audit = audit_t(identity_t)
    document = {
        "schema": 1,
        "model": "65-cycle persistent-seed full joint XOR2 arrival audit",
        "equations": {
            "B": "T*A*T^-1",
            "D": "T*(A+I)",
            "C65": "A*T^-1",
            "targets": "[B|D; C65|A]",
        },
        "arrival": {
            "q": STATE_DELAY,
            "seed": 0,
            "xor": XOR_DELAY,
            "deadline": 8,
            "necessary_per_row": "4*wt(q)+wt(seed)<=16",
            "note": "A pure XOR2 network has only even delay, so delay 9 gives the same XOR depth as delay 8.",
        },
        "budgets": {
            "fixed_state_gate": BITS * STATE_GATE,
            "beat_verified_402_9_67": {
                "delay_9_logic": strict_logic_budget(VERIFIED_REFERENCE, 9),
                "delay_8_logic": strict_logic_budget(VERIFIED_REFERENCE, 8),
            },
            "beat_research_401_9_67": {
                "delay_9_logic": strict_logic_budget(RESEARCH_REFERENCE, 9),
                "delay_8_logic": strict_logic_budget(RESEARCH_REFERENCE, 8),
            },
            "ordinary_xor_gate": XOR_GATE,
        },
        "global_invariants": {
            "rank_A": rank(a, BITS),
            "rank_A_plus_I": rank(a_plus_i, BITS),
            "factorization": (
                "M(T)=diag(T,A)*[[A,A+I],[I,I]]*diag(T^-1,I)"
            ),
            "joint_rank_for_every_invertible_T": 2 * BITS,
            "all_B_D_C_A_rows_nonzero": True,
            "minimum_distinct_target_nodes": 2 * BITS,
        },
        "identity_basis_audit": identity_audit,
        "corpus": {
            "paths": [str(path) for path in args.inputs],
            "objects": objects,
            "matrix_objects": matrices_seen,
            "unique_T": len(seen),
            "kraft_feasible": sum(item["mixed_over"] == 0 for item in frontier),
            "best": frontier[:32],
        },
        "scope": (
            "The rank-64/64-node statement is global. The corpus result is exhaustive only for the listed T values. "
            "Kraft feasibility is necessary for arbitrary XOR2 DAGs but is not a gate-count sufficiency proof. "
            "Switch/Z and nonlinear reachable-state specializations are outside this certificate."
        ),
    }
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "budgets": document["budgets"],
        "global_invariants": document["global_invariants"],
        "corpus_unique_T": len(seen),
        "corpus_kraft_feasible": document["corpus"]["kraft_feasible"],
        "corpus_best": frontier[:1],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
