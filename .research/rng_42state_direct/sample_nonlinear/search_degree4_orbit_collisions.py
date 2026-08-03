#!/usr/bin/env python3
"""Search cheap degree-four stored features on the fixed RNG trajectories.

For every square-free product of up to four distinct linear signals used by
the checked encoded RNG DAG, compare its evaluation vector on q_t with the
successor evaluation on q_(t+1)=B*q_t.  A match means that a nonlinear stored
feature can be updated by a wire (or by one NOT for a complemented match) on
all 256 live tests and 64 feedback transitions.

Only 128-bit digests are retained for the large signature table.  Every hit
is rechecked with the full 16,384-bit Python integer before it is reported.
The script is read-only with respect to the game and player save.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import blake2b, sha256
from itertools import combinations
import json
from pathlib import Path
import struct
import sys
import time
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / ".research" / "rng_test_specialization"))

from src.tc_save_lab.rng_encoded_asic import (  # noqa: E402
    B,
    C,
    GATES,
    IDENTITY,
    T,
    apply_matrix,
    apply_row,
)
from verify_rng_contract import initial_seed, xorshift32  # noqa: E402


Feature = tuple[int, ...]


@dataclass(slots=True)
class SignatureGroup:
    """One exact care signature and one representative per distinct ANF."""

    representative: Feature
    anf_representatives: list[Feature] | None = None


@dataclass(slots=True)
class CollisionBucket:
    """Groups that share a 128-bit digest but not necessarily a signature."""

    groups: list[SignatureGroup]


def feedback_states(rounds: int) -> list[int]:
    states: list[int] = []
    for test_id in range(256):
        natural = initial_seed(test_id)
        for _ in range(rounds):
            states.append(apply_matrix(T, natural))
            natural = xorshift32(natural)
    if len(states) != 256 * rounds or len(set(states)) != len(states):
        raise AssertionError("feedback care state count changed")
    return states


def signal_signatures(rows: Sequence[int], states: Sequence[int]) -> list[int]:
    signatures = [0] * len(rows)
    for point, state in enumerate(states):
        for index, row in enumerate(rows):
            if (row & state).bit_count() & 1:
                signatures[index] |= 1 << point
    return signatures


def product_signature(indices: Iterable[int], signatures: Sequence[int], all_points: int) -> int:
    result = all_points
    for index in indices:
        result &= signatures[index]
    return result


def signature_groups(
    entry: Feature | CollisionBucket,
) -> Iterable[SignatureGroup]:
    if isinstance(entry, tuple):
        yield SignatureGroup(entry)
    else:
        yield from entry.groups


def digest(value: int, byte_count: int) -> bytes:
    return blake2b(value.to_bytes(byte_count, "little"), digest_size=16).digest()


def product_anf(indices: Iterable[int], rows: Sequence[int]) -> frozenset[int]:
    """Return the exact Boolean-ring ANF as a set of square-free monomials."""

    polynomial = {0}
    for index in indices:
        row = rows[index]
        factors = [1 << bit for bit in range(32) if row >> bit & 1]
        product: set[int] = set()
        for monomial in polynomial:
            for factor in factors:
                term = monomial | factor
                if term in product:
                    product.remove(term)
                else:
                    product.add(term)
        polynomial = product
    return frozenset(polynomial)


def anf_digest(polynomial: frozenset[int]) -> str:
    packed = b"".join(struct.pack("<I", monomial) for monomial in sorted(polynomial))
    return sha256(packed).hexdigest()


def feature_record(
    successor_feature: tuple[int, ...],
    current_feature: tuple[int, ...],
    rows: Sequence[int],
    *,
    complemented: bool = False,
) -> dict[str, object]:
    return {
        "successor_feature_indices": list(successor_feature),
        "successor_feature_rows_hex": [f"{rows[index]:08x}" for index in successor_feature],
        "current_feature_indices": list(current_feature),
        "current_feature_rows_hex": [f"{rows[index]:08x}" for index in current_feature],
        "complemented": complemented,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=64)
    parser.add_argument("--maximum-degree", type=int, default=4)
    parser.add_argument(
        "--include-all-state-bits",
        action="store_true",
        help="extend the 66 checked DAG rows with every raw encoded-state bit",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "degree4_orbit_collision_certificate.json",
    )
    args = parser.parse_args()
    if args.rounds <= 0 or not 1 <= args.maximum_degree <= 4:
        raise SystemExit("rounds must be positive and maximum-degree must be in 1..4")

    started = time.monotonic()
    row_set = set((*B, *C, *(gate.output for gate in GATES)))
    if args.include_all_state_bits:
        row_set.update(IDENTITY)
    rows = tuple(sorted(row_set))
    states = feedback_states(args.rounds)
    successor_states = [apply_matrix(B, state) for state in states]
    expected_successors: list[int] = []
    for test_id in range(256):
        natural = initial_seed(test_id)
        for _ in range(args.rounds):
            natural = xorshift32(natural)
            expected_successors.append(apply_matrix(T, natural))
    if successor_states != expected_successors:
        raise AssertionError("B successor identity changed")

    current = signal_signatures(rows, states)
    transformed_rows = tuple(apply_row(row, B) for row in rows)
    successor = signal_signatures(transformed_rows, states)
    if successor != signal_signatures(rows, successor_states):
        raise AssertionError("row-transform and state-transform successors differ")

    point_count = len(states)
    byte_count = (point_count + 7) // 8
    all_points = (1 << point_count) - 1
    table: dict[bytes, Feature | CollisionBucket] = {}
    current_duplicate_monomials = 0
    current_global_duplicates = 0
    current_sample_only_duplicates = 0
    current_duplicate_examples: list[dict[str, object]] = []
    monomial_count_by_degree: list[int] = []
    for degree in range(1, args.maximum_degree + 1):
        count = 0
        for indices in combinations(range(len(rows)), degree):
            signature = product_signature(indices, current, all_points)
            key = digest(signature, byte_count)
            has_duplicate = False
            has_global_duplicate = False
            has_sample_only_duplicate = False
            entry = table.get(key)
            if entry is None:
                table[key] = indices
            else:
                groups = list(signature_groups(entry))
                matching_group: SignatureGroup | None = None
                for group in groups:
                    if product_signature(group.representative, current, all_points) == signature:
                        matching_group = group
                        break
                if matching_group is None:
                    groups.append(SignatureGroup(indices))
                else:
                    has_duplicate = True
                    if matching_group.anf_representatives is None:
                        matching_group.anf_representatives = [matching_group.representative]
                    current_anf = product_anf(indices, rows)
                    for other in matching_group.anf_representatives:
                        global_equal = product_anf(other, rows) == current_anf
                        has_global_duplicate |= global_equal
                        has_sample_only_duplicate |= not global_equal
                        if len(current_duplicate_examples) < 32:
                            current_duplicate_examples.append({
                                "left_indices": list(other),
                                "right_indices": list(indices),
                                "left_rows_hex": [f"{rows[index]:08x}" for index in other],
                                "right_rows_hex": [f"{rows[index]:08x}" for index in indices],
                                "global_boolean_identity": global_equal,
                            })
                    if not has_global_duplicate:
                        matching_group.anf_representatives.append(indices)
                table[key] = CollisionBucket(groups)
            current_duplicate_monomials += int(has_duplicate)
            current_global_duplicates += int(has_global_duplicate)
            current_sample_only_duplicates += int(has_sample_only_duplicate)
            count += 1
        monomial_count_by_degree.append(count)

    wire_any = 0
    wire_global = 0
    wire_sample_only = 0
    wire_nonzero_global = 0
    wire_nonzero_sample_only = 0
    not_any = 0
    not_global = 0
    not_sample_only = 0
    wire_examples: list[dict[str, object]] = []
    not_examples: list[dict[str, object]] = []
    global_wire_edges: dict[str, str] = {}
    global_wire_representatives: dict[str, dict[str, object]] = {}
    successor_count = 0
    for degree in range(1, args.maximum_degree + 1):
        for indices in combinations(range(len(rows)), degree):
            signature = product_signature(indices, successor, all_points)
            successor_count += 1
            successor_anf: frozenset[int] | None = None
            for complement in (False, True):
                wanted = all_points ^ signature if complement else signature
                any_match = False
                global_match = False
                sample_only_match = False
                nonzero_global_match = False
                nonzero_sample_only_match = False
                entry = table.get(digest(wanted, byte_count))
                if entry is not None:
                    for group in signature_groups(entry):
                        if product_signature(group.representative, current, all_points) != wanted:
                            continue
                        candidates = group.anf_representatives or [group.representative]
                        any_match = True
                        if successor_anf is None:
                            successor_anf = product_anf(indices, transformed_rows)
                        for other in candidates:
                            current_anf = product_anf(other, rows)
                            if complement:
                                current_anf = (
                                    frozenset((*current_anf, 0))
                                    if 0 not in current_anf
                                    else frozenset(set(current_anf) - {0})
                                )
                            global_equal = successor_anf == current_anf
                            global_match |= global_equal
                            sample_only_match |= not global_equal
                            nonzero_global_match |= global_equal and bool(successor_anf)
                            nonzero_sample_only_match |= (not global_equal) and bool(signature)
                            if not complement and global_equal and successor_anf:
                                source_anf = product_anf(indices, rows)
                                source_key = anf_digest(source_anf)
                                target_key = anf_digest(successor_anf)
                                previous_target = global_wire_edges.setdefault(source_key, target_key)
                                if previous_target != target_key:
                                    raise AssertionError("one Boolean feature has two B successors")
                                global_wire_representatives.setdefault(source_key, {
                                    "indices": list(indices),
                                    "rows_hex": [f"{rows[index]:08x}" for index in indices],
                                    "anf_term_count": len(source_anf),
                                })
                                global_wire_representatives.setdefault(target_key, {
                                    "indices": list(other),
                                    "rows_hex": [f"{rows[index]:08x}" for index in other],
                                    "anf_term_count": len(successor_anf),
                                })
                            examples = not_examples if complement else wire_examples
                            if len(examples) < 32:
                                record = feature_record(indices, other, rows, complemented=complement)
                                record["global_boolean_identity"] = global_equal
                                examples.append(record)
                        break
                if complement:
                    not_any += int(any_match)
                    not_global += int(global_match)
                    not_sample_only += int(sample_only_match)
                else:
                    wire_any += int(any_match)
                    wire_global += int(global_match)
                    wire_sample_only += int(sample_only_match)
                    wire_nonzero_global += int(nonzero_global_match)
                    wire_nonzero_sample_only += int(nonzero_sample_only_match)

    # A wire-only bank of Delay Bits requires a directed cycle: every stored
    # feature's B-successor must be supplied by another stored feature.  Paths
    # that leave this finite feature family still require combinational logic.
    cycles: list[list[str]] = []
    visited: set[str] = set()
    for start in global_wire_edges:
        if start in visited:
            continue
        order: list[str] = []
        positions: dict[str, int] = {}
        node = start
        while node in global_wire_edges and node not in visited and node not in positions:
            positions[node] = len(order)
            order.append(node)
            node = global_wire_edges[node]
        if node in positions:
            cycles.append(order[positions[node] :])
        visited.update(order)
    cycle_records = [
        [
            {
                "anf_sha256": key,
                **global_wire_representatives[key],
            }
            for key in cycle
        ]
        for cycle in cycles[:32]
    ]

    state_blob = b"".join(struct.pack("<I", state) for state in states)
    result = {
        "schema": 1,
        "model": "products of up to four checked encoded-DAG linear signals",
        "feedback_rounds_per_seed": args.rounds,
        "care_point_count": point_count,
        "care_point_unique_count": len(set(states)),
        "care_state_vector_sha256": sha256(state_blob).hexdigest(),
        "linear_signal_count": len(rows),
        "includes_all_raw_state_bits": args.include_all_state_bits,
        "linear_rows_hex": [f"{row:08x}" for row in rows],
        "maximum_degree": args.maximum_degree,
        "monomial_count_by_degree": monomial_count_by_degree,
        "current_monomial_count": sum(monomial_count_by_degree),
        "successor_monomial_count": successor_count,
        "current_duplicate_monomial_count": current_duplicate_monomials,
        "current_global_duplicate_monomial_count": current_global_duplicates,
        "current_sample_only_duplicate_monomial_count": current_sample_only_duplicates,
        "wire_successor_feature_with_match_count": wire_any,
        "wire_successor_feature_with_global_match_count": wire_global,
        "wire_successor_feature_with_sample_only_match_count": wire_sample_only,
        "wire_nonzero_feature_with_global_match_count": wire_nonzero_global,
        "wire_nonzero_feature_with_sample_only_match_count": wire_nonzero_sample_only,
        "global_nonzero_wire_feature_node_count": len(global_wire_representatives),
        "global_nonzero_wire_edge_count": len(global_wire_edges),
        "global_nonzero_wire_cycle_count": len(cycles),
        "global_nonzero_wire_cycle_lengths": [len(cycle) for cycle in cycles],
        "global_nonzero_wire_cycle_examples": cycle_records,
        "not_successor_feature_with_match_count": not_any,
        "not_successor_feature_with_global_match_count": not_global,
        "not_successor_feature_with_sample_only_match_count": not_sample_only,
        "current_duplicate_examples": current_duplicate_examples,
        "wire_successor_examples": wire_examples,
        "not_successor_examples": not_examples,
        "elapsed_seconds": time.monotonic() - started,
        "scope": (
            "complete for square-free products of degree 1..maximum_degree over "
            "the listed linear rows; not a search over arbitrary affine forms or "
            "multi-gate successor networks"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "linear_signal_count": result["linear_signal_count"],
        "current_monomial_count": result["current_monomial_count"],
        "current_duplicate_monomial_count": result["current_duplicate_monomial_count"],
        "current_sample_only_duplicate_monomial_count": result["current_sample_only_duplicate_monomial_count"],
        "wire_successor_feature_with_match_count": result["wire_successor_feature_with_match_count"],
        "wire_successor_feature_with_sample_only_match_count": result["wire_successor_feature_with_sample_only_match_count"],
        "wire_nonzero_feature_with_global_match_count": result["wire_nonzero_feature_with_global_match_count"],
        "global_nonzero_wire_cycle_count": result["global_nonzero_wire_cycle_count"],
        "not_successor_feature_with_match_count": result["not_successor_feature_with_match_count"],
        "elapsed_seconds": result["elapsed_seconds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
