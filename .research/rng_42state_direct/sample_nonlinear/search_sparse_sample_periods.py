#!/usr/bin/env python3
"""Search one- and two-monomial periodic features on official RNG traces.

For each period L, compare f(A^L x) with f(x) on every trajectory position
where a length-L wire cycle can be composed from the 64 feedback transitions.
The search is read-only with respect to the game and player save.
"""

from __future__ import annotations

import argparse
from hashlib import blake2b, sha256
from itertools import combinations
import json
from pathlib import Path
import struct
import time


HERE = Path(__file__).resolve().parent
from verify_low_degree_rank import initial_seed, xorshift32  # noqa: E402


def trajectories() -> list[list[int]]:
    result: list[list[int]] = []
    for test_id in range(256):
        value = initial_seed(test_id)
        trace = [value]
        for _ in range(64):
            value = xorshift32(value)
            trace.append(value)
        result.append(trace)
    return result


def variable_signatures(states: list[int]) -> list[int]:
    signatures = [0] * 32
    for point, state in enumerate(states):
        value = state
        while value:
            low = value & -value
            signatures[low.bit_length() - 1] |= 1 << point
            value ^= low
    return signatures


def monomial_signature(mask: int, variables: list[int], all_points: int) -> int:
    result = all_points
    while mask:
        low = mask & -mask
        result &= variables[low.bit_length() - 1]
        mask ^= low
    return result


def monomial_masks(maximum_degree: int) -> list[int]:
    result: list[int] = []
    for degree in range(1, maximum_degree + 1):
        result.extend(
            sum(1 << index for index in indices)
            for indices in combinations(range(32), degree)
        )
    return result


def evaluation_rank(
    variables: list[int], point_count: int, maximum_degree: int
) -> tuple[int, int]:
    all_points = (1 << point_count) - 1
    basis: dict[int, int] = {}
    column_count = 0
    for degree in range(maximum_degree + 1):
        masks = [0] if degree == 0 else (
            sum(1 << index for index in indices)
            for indices in combinations(range(32), degree)
        )
        for mask in masks:
            vector = monomial_signature(mask, variables, all_points)
            column_count += 1
            while vector:
                pivot = vector.bit_length() - 1
                previous = basis.get(pivot)
                if previous is None:
                    basis[pivot] = vector
                    break
                vector ^= previous
    return column_count, len(basis)


def difference_signature(
    mask: int,
    left_variables: list[int],
    right_variables: list[int],
    all_points: int,
) -> int:
    return (
        monomial_signature(mask, left_variables, all_points)
        ^ monomial_signature(mask, right_variables, all_points)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--maximum-degree", type=int, default=4)
    parser.add_argument("--maximum-period", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "sparse_sample_period_certificate.json",
    )
    args = parser.parse_args()
    if not 1 <= args.maximum_degree <= 4:
        raise SystemExit("maximum-degree must be in 1..4")
    if not 1 <= args.maximum_period <= 64:
        raise SystemExit("maximum-period must be in 1..64")

    started = time.monotonic()
    traces = trajectories()
    flat_trace = [state for trace in traces for state in trace]
    trace_blob = b"".join(struct.pack("<I", state) for state in flat_trace)
    masks = monomial_masks(args.maximum_degree)
    records: list[dict[str, object]] = []
    total_single = 0
    total_pair = 0

    for period in range(1, args.maximum_period + 1):
        left_states = [
            trace[tick]
            for trace in traces
            for tick in range(65 - period)
        ]
        right_states = [
            trace[tick + period]
            for trace in traces
            for tick in range(65 - period)
        ]
        left_variables = variable_signatures(left_states)
        right_variables = variable_signatures(right_states)
        point_count = len(left_states)
        all_points = (1 << point_count) - 1
        byte_count = (point_count + 7) // 8
        degree3_column_count, degree3_rank = evaluation_rank(
            left_variables, point_count, 3
        )
        table: dict[bytes, int | list[int]] = {}
        single_invariants: list[int] = []
        pair_invariant_count = 0
        pair_invariant_examples: list[tuple[int, int]] = []
        digest_collision_count = 0

        for mask in masks:
            signature = difference_signature(
                mask, left_variables, right_variables, all_points
            )
            if signature == 0:
                single_invariants.append(mask)
            key = blake2b(
                signature.to_bytes(byte_count, "little"), digest_size=16
            ).digest()
            entry = table.get(key)
            if entry is None:
                table[key] = mask
                continue
            previous_masks = [entry] if isinstance(entry, int) else entry
            for previous in previous_masks:
                previous_signature = difference_signature(
                    previous, left_variables, right_variables, all_points
                )
                if previous_signature == signature:
                    pair_invariant_count += 1
                    if len(pair_invariant_examples) < 32:
                        pair_invariant_examples.append((previous, mask))
                else:
                    digest_collision_count += 1
            if isinstance(entry, int):
                table[key] = [entry, mask]
            else:
                entry.append(mask)

        total_single += len(single_invariants)
        total_pair += pair_invariant_count
        records.append({
            "period": period,
            "constraint_point_count": point_count,
            "start_state_degree3_column_count": degree3_column_count,
            "start_state_degree3_evaluation_rank": degree3_rank,
            "single_monomial_invariant_count": len(single_invariants),
            "two_monomial_invariant_count": pair_invariant_count,
            "digest_collision_count": digest_collision_count,
            "single_monomial_examples_hex": [
                f"{mask:08x}" for mask in single_invariants[:32]
            ],
            "two_monomial_examples_hex": [
                [f"{left:08x}", f"{right:08x}"]
                for left, right in pair_invariant_examples
            ],
        })

    result = {
        "schema": 1,
        "scope": (
            "all nonconstant natural-state ANF monomials through maximum_degree "
            "and XORs of two distinct such monomials"
        ),
        "trace_definition": "256 official seeds, natural states A^0(s)..A^64(s)",
        "trace_state_count": len(flat_trace),
        "trace_state_unique_count": len(set(flat_trace)),
        "trace_vector_sha256": sha256(trace_blob).hexdigest(),
        "maximum_degree": args.maximum_degree,
        "monomial_count": len(masks),
        "maximum_period": args.maximum_period,
        "period_records": records,
        "total_single_monomial_period_hits": total_single,
        "total_two_monomial_period_hits": total_pair,
        "all_start_sets_degree3_evaluation_injective": all(
            record["start_state_degree3_evaluation_rank"]
            == record["start_state_degree3_column_count"]
            for record in records
        ),
        "elapsed_seconds": time.monotonic() - started,
        "consequence": (
            "no nonconstant sample-periodic feature of degree <=3, and no "
            "degree-4 sample-periodic feature with ANF support <=2"
            if total_single == 0
            and total_pair == 0
            and all(
                record["start_state_degree3_evaluation_rank"]
                == record["start_state_degree3_column_count"]
                for record in records
            )
            else "low-support sample-periodic features require follow-up orbit construction"
        ),
        "limitations": (
            "does not search ANF support >=3, products of arbitrary affine forms as "
            "atomic gates, or cycles containing combinational updates"
        ),
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "monomial_count": result["monomial_count"],
        "period_count": len(records),
        "total_single_monomial_period_hits": total_single,
        "total_two_monomial_period_hits": total_pair,
        "all_start_sets_degree3_evaluation_injective": result[
            "all_start_sets_degree3_evaluation_injective"
        ],
        "elapsed_seconds": result["elapsed_seconds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
