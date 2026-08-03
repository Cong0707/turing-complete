#!/usr/bin/env python3
"""Search sample-periodic XORs of two cheap linear-product features."""

from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import struct
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from src.tc_save_lab.rng_encoded_asic import (  # noqa: E402
    B,
    C,
    GATES,
    IDENTITY,
    T,
    apply_matrix,
)
from search_degree4_orbit_collisions import (  # noqa: E402
    CollisionBucket,
    Feature,
    SignatureGroup,
    digest,
    product_anf,
    product_signature,
    signal_signatures,
    signature_groups,
)
from verify_rng_contract import initial_seed, xorshift32  # noqa: E402


def paired_states(period: int) -> tuple[list[int], list[int]]:
    left: list[int] = []
    right: list[int] = []
    for test_id in range(256):
        value = initial_seed(test_id)
        trace = [apply_matrix(T, value)]
        for _ in range(64):
            value = xorshift32(value)
            trace.append(apply_matrix(T, value))
        left.extend(trace[: 65 - period])
        right.extend(trace[period:])
    return left, right


def difference_signature(
    feature: Feature,
    left: list[int],
    right: list[int],
    all_points: int,
) -> int:
    return (
        product_signature(feature, left, all_points)
        ^ product_signature(feature, right, all_points)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", type=int, default=1)
    parser.add_argument("--maximum-degree", type=int, default=4)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "product_pair_period1_certificate.json",
    )
    args = parser.parse_args()
    if not 1 <= args.period <= 42:
        raise SystemExit("period must be in 1..42")
    if not 1 <= args.maximum_degree <= 4:
        raise SystemExit("maximum-degree must be in 1..4")

    started = time.monotonic()
    rows = tuple(sorted(set((*B, *C, *(gate.output for gate in GATES), *IDENTITY))))
    left_states, right_states = paired_states(args.period)
    left = signal_signatures(rows, left_states)
    right = signal_signatures(rows, right_states)
    point_count = len(left_states)
    all_points = (1 << point_count) - 1
    byte_count = (point_count + 7) // 8
    table: dict[bytes, Feature | CollisionBucket] = {}
    feature_count_by_degree: list[int] = []
    exact_difference_duplicate_features = 0
    global_equivalent_duplicate_features = 0
    sample_only_duplicate_features = 0
    nonzero_single_invariant_anf: dict[str, Feature] = {}
    examples: list[dict[str, object]] = []
    digest_collision_count = 0

    for degree in range(1, args.maximum_degree + 1):
        degree_count = 0
        for feature in combinations(range(len(rows)), degree):
            signature = difference_signature(feature, left, right, all_points)
            key = digest(signature, byte_count)
            entry = table.get(key)
            current_anf: frozenset[int] | None = None
            if signature == 0:
                current_anf = product_anf(feature, rows)
                if current_anf:
                    anf_key = sha256(
                        b"".join(struct.pack("<I", term) for term in sorted(current_anf))
                    ).hexdigest()
                    previous = nonzero_single_invariant_anf.get(anf_key)
                    if previous is None or product_anf(previous, rows) != current_anf:
                        nonzero_single_invariant_anf[anf_key] = feature

            if entry is None:
                table[key] = feature
                degree_count += 1
                continue

            groups = list(signature_groups(entry))
            matching_group: SignatureGroup | None = None
            for group in groups:
                if difference_signature(group.representative, left, right, all_points) == signature:
                    matching_group = group
                    break
            if matching_group is None:
                groups.append(SignatureGroup(feature))
                digest_collision_count += 1
            else:
                exact_difference_duplicate_features += 1
                if matching_group.anf_representatives is None:
                    matching_group.anf_representatives = [matching_group.representative]
                if current_anf is None:
                    current_anf = product_anf(feature, rows)
                has_global_equivalent = False
                has_sample_only = False
                for previous in matching_group.anf_representatives:
                    previous_anf = product_anf(previous, rows)
                    global_equivalent = previous_anf == current_anf
                    has_global_equivalent |= global_equivalent
                    has_sample_only |= not global_equivalent
                    if not global_equivalent and len(examples) < 32:
                        examples.append({
                            "left_feature_indices": list(previous),
                            "left_feature_rows_hex": [f"{rows[index]:08x}" for index in previous],
                            "right_feature_indices": list(feature),
                            "right_feature_rows_hex": [f"{rows[index]:08x}" for index in feature],
                            "left_anf_term_count": len(previous_anf),
                            "right_anf_term_count": len(current_anf),
                        })
                global_equivalent_duplicate_features += int(has_global_equivalent)
                sample_only_duplicate_features += int(has_sample_only)
                if not has_global_equivalent:
                    matching_group.anf_representatives.append(feature)
            table[key] = CollisionBucket(groups)
            degree_count += 1
        feature_count_by_degree.append(degree_count)

    state_blob = b"".join(
        struct.pack("<I", value)
        for pair in zip(left_states, right_states)
        for value in pair
    )
    result = {
        "schema": 1,
        "scope": (
            "all products of degree 1..maximum_degree over the listed encoded "
            "linear rows, plus XORs of two distinct product functions"
        ),
        "period": args.period,
        "constraint_point_count": point_count,
        "paired_state_vector_sha256": sha256(state_blob).hexdigest(),
        "linear_signal_count": len(rows),
        "linear_rows_hex": [f"{row:08x}" for row in rows],
        "maximum_degree": args.maximum_degree,
        "feature_count_by_degree": feature_count_by_degree,
        "feature_count": sum(feature_count_by_degree),
        "exact_difference_duplicate_feature_count": exact_difference_duplicate_features,
        "global_equivalent_duplicate_feature_count": global_equivalent_duplicate_features,
        "sample_only_duplicate_feature_count": sample_only_duplicate_features,
        "distinct_nonzero_single_invariant_count": len(nonzero_single_invariant_anf),
        "distinct_nonzero_single_invariant_examples": [
            {
                "indices": list(feature),
                "rows_hex": [f"{rows[index]:08x}" for index in feature],
            }
            for feature in list(nonzero_single_invariant_anf.values())[:32]
        ],
        "sample_only_pair_examples": examples,
        "digest_collision_count": digest_collision_count,
        "elapsed_seconds": time.monotonic() - started,
        "consequence": (
            "no sample-periodic feature representable as one product or XOR of two products"
            if not nonzero_single_invariant_anf and sample_only_duplicate_features == 0
            else "sample-periodic product feature requires orbit and circuit follow-up"
        ),
        "limitations": (
            "does not search XORs of three products, affine factors with a constant, "
            "periods other than the selected value, or combinational cycle updates"
        ),
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "period": result["period"],
        "linear_signal_count": result["linear_signal_count"],
        "feature_count": result["feature_count"],
        "exact_difference_duplicate_feature_count": exact_difference_duplicate_features,
        "sample_only_duplicate_feature_count": sample_only_duplicate_features,
        "distinct_nonzero_single_invariant_count": len(nonzero_single_invariant_anf),
        "elapsed_seconds": result["elapsed_seconds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
