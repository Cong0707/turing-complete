#!/usr/bin/env python3
"""Audit the joint-singular rank-2/rank-3 RNG search certificate."""

from __future__ import annotations

import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path
import random


BITS = 32
MASK32 = (1 << BITS) - 1
SPARSE_ROWS = 32 + 496 + 4960
EXPECTED_SUMMARY = {
    "status": "unsat-in-subspace",
    "max_hamming": 12,
    "destination_pairs": 343,
    "checked": 10_326_758_967,
    "within_radius": 10_326_758_967,
    "invertible": 542_967_173,
    "repaired_original": 0,
    "pair_with_possible_third": 859_128,
    "pair_destination_options": 875_394,
    "pair_beam": 61_078,
    "rank3_checked": 90_568_464,
    "rank3_invertible": 33_644_182,
    "rank3_repaired": 0,
    "rank3_empty_intersection": 44_581,
    "best": [3, 20, 34],
}


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK32
    value ^= value >> 5
    return value & MASK32


def transition() -> tuple[int, ...]:
    rows = [0] * BITS
    for source in range(BITS):
        column = xorshift32(1 << source)
        for target in range(BITS):
            rows[target] |= ((column >> target) & 1) << source
    return tuple(rows)


def apply_row(row: int, matrix: tuple[int, ...]) -> int:
    result = 0
    while row:
        bit = (row & -row).bit_length() - 1
        result ^= matrix[bit]
        row &= row - 1
    return result


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def inverse(rows: tuple[int, ...]) -> tuple[int, ...]:
    matrix = list(rows)
    result = [1 << bit for bit in range(BITS)]
    for column in range(BITS):
        pivot = next(
            (row for row in range(column, BITS) if matrix[row] >> column & 1),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        result[column], result[pivot] = result[pivot], result[column]
        for row in range(BITS):
            if row != column and matrix[row] >> column & 1:
                matrix[row] ^= matrix[column]
                result[row] ^= result[column]
    return tuple(result)


def load_records(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def matrix_rows(record: dict[str, object], name: str) -> tuple[int, ...]:
    values = record[name]
    if not isinstance(values, list):
        raise TypeError(f"{name} is not a list")
    return tuple(int(str(value), 16) for value in values)


def digest(path: Path, root: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": len(data),
        "sha256": sha256(data).hexdigest(),
    }


def score(b_rows: tuple[int, ...], t_rows: tuple[int, ...]) -> dict[str, object]:
    metrics = [
        4 * left.bit_count() + right.bit_count()
        for left, right in zip(b_rows, t_rows)
    ]
    return {
        "over": sum(metric > 16 for metric in metrics),
        "excess": sum(max(0, metric - 16) for metric in metrics),
        "maximum": max(metrics),
        "combined_weight": sum(row.bit_count() for row in (*b_rows, *t_rows)),
        "metrics": metrics,
    }


def sparse_rows() -> tuple[int, ...]:
    rows: list[int] = []
    for weight in range(1, 4):
        for bits in itertools.combinations(range(BITS), weight):
            rows.append(sum(1 << bit for bit in bits))
    assert len(rows) == SPARSE_ROWS
    return tuple(rows)


def cross_check_updates(
    c_rows: tuple[int, ...],
    p_rows: tuple[int, ...],
    a_rows: tuple[int, ...],
    a_plus_i: tuple[int, ...],
    coordinate_pairs: list[tuple[int, int]],
) -> dict[str, object]:
    rng = random.Random(0x66A123)
    values = sparse_rows()
    verified = 0
    attempts = 0
    categories = {"regular_regular": 0, "singular_singular": 0, "mixed": 0}
    rank3_verified = 0
    while verified < 4096:
        attempts += 1
        first, second = rng.choice(coordinate_pairs)
        first_value = rng.choice(values)
        second_value = rng.choice(values)
        if first_value == c_rows[first] or second_value == c_rows[second]:
            continue
        first_delta = first_value ^ c_rows[first]
        second_delta = second_value ^ c_rows[second]
        first_alpha = apply_row(first_delta, p_rows)
        second_alpha = apply_row(second_delta, p_rows)
        m00 = 1 ^ (first_alpha >> first & 1)
        m01 = first_alpha >> second & 1
        m10 = second_alpha >> first & 1
        m11 = 1 ^ (second_alpha >> second & 1)
        determinant = (m00 & m11) ^ (m01 & m10)
        if not determinant:
            continue

        first_regular = bool(m00)
        second_regular = bool(m11)
        category = (
            "regular_regular" if first_regular and second_regular
            else "singular_singular" if not first_regular and not second_regular
            else "mixed"
        )
        categories[category] += 1
        pair_c = list(c_rows)
        pair_c[first] = first_value
        pair_c[second] = second_value
        direct_pair_p = inverse(tuple(pair_c))
        incremental_pair_p = []
        for p_row in p_rows:
            x0 = p_row >> first & 1
            x1 = p_row >> second & 1
            y0 = (x0 & m11) ^ (x1 & m10)
            y1 = (x0 & m01) ^ (x1 & m00)
            incremental_pair_p.append(
                p_row ^ (first_alpha if y0 else 0) ^ (second_alpha if y1 else 0)
            )
        assert tuple(incremental_pair_p) == direct_pair_p
        pair_t = compose(direct_pair_p, a_plus_i)
        pair_b = compose(compose(direct_pair_p, a_rows), tuple(pair_c))
        assert compose(tuple(pair_c), direct_pair_p) == tuple(1 << bit for bit in range(BITS))
        assert len(pair_t) == len(pair_b) == BITS

        third = rng.choice([bit for bit in range(BITS) if bit not in (first, second)])
        while True:
            third_value = rng.choice(values)
            third_delta = third_value ^ pair_c[third]
            if not third_delta:
                continue
            third_alpha = apply_row(third_delta, direct_pair_p)
            if not (third_alpha >> third & 1):
                break
        triple_c = list(pair_c)
        triple_c[third] = third_value
        direct_triple_p = inverse(tuple(triple_c))
        incremental_triple_p = tuple(
            p_row ^ (third_alpha if p_row >> third & 1 else 0)
            for p_row in direct_pair_p
        )
        assert incremental_triple_p == direct_triple_p
        assert compose(direct_triple_p, a_plus_i) == compose(
            incremental_triple_p, a_plus_i
        )
        assert compose(compose(direct_triple_p, a_rows), tuple(triple_c)) == compose(
            compose(incremental_triple_p, a_rows), tuple(triple_c)
        )
        rank3_verified += 1
        verified += 1
    return {
        "seed": "0x66a123",
        "attempts": attempts,
        "joint_invertible_rank2_verified": verified,
        "rank2_categories": categories,
        "legal_sequential_rank3_verified": rank3_verified,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("joint-rank23-certificate.json"),
    )
    parser.add_argument("--peak-working-set-bytes", type=int, default=7_794_688)
    parser.add_argument("--elapsed-seconds", type=float, default=70.66)
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    root = here.parents[1]
    center_path = here / "sparse-c66-run-c6602.jsonl"
    second_center_path = (
        root / ".research" / "rng65_joint_basis_agent"
        / "phase8-legal-transvection-beam.jsonl"
    )
    result_path = here / "joint-rank3-main-allcoords-b256.jsonl"
    monitored_path = here / "joint-rank3-main-allcoords-b256-monitored.jsonl"
    second_result_path = here / "joint-rank3-second-beam2048.jsonl"
    source_path = here / "search_joint_singular_c66.cpp"
    sparse_continuation_source_path = here / "search_sparse_c66.cpp"
    transvection_continuation_source_path = (
        root / ".research" / "rng65_joint_basis_agent"
        / "search_legal_transvections.cpp"
    )
    audit_path = Path(__file__).resolve()

    center = load_records(center_path)[-1]
    c_rows = matrix_rows(center, "C")
    a_rows = transition()
    identity = tuple(1 << bit for bit in range(BITS))
    a_plus_i = tuple(left ^ right for left, right in zip(a_rows, identity))
    p_rows = inverse(c_rows)
    pa_rows = compose(p_rows, a_rows)
    b_rows = compose(pa_rows, c_rows)
    t_rows = compose(p_rows, a_plus_i)
    assert compose(p_rows, c_rows) == identity
    assert compose(c_rows, p_rows) == identity

    base_score = score(b_rows, t_rows)
    bad_rows = [
        row for row, metric in enumerate(base_score["metrics"])
        if int(metric) > 16
    ]
    assert bad_rows == [13, 16, 27]
    assert [base_score["metrics"][row] for row in bad_rows] == [17, 34, 17]
    assert {key: base_score[key] for key in ("over", "excess", "maximum")}
    assert (base_score["over"], base_score["excess"], base_score["maximum"]) == (
        3,
        20,
        34,
    )
    assert base_score["combined_weight"] == 181
    assert sum(row.bit_count() for row in c_rows) == 68

    sensitivities = [p_rows[row] | pa_rows[row] for row in bad_rows]
    completable_pair_values: list[tuple[int, int]] = []
    for first, second in itertools.combinations(range(BITS), 2):
        completion = MASK32
        for sensitive in sensitivities:
            if not (sensitive >> first & 1 or sensitive >> second & 1):
                completion &= sensitive
        completion &= ~((1 << first) | (1 << second)) & MASK32
        if completion:
            completable_pair_values.append((first, second))
    completable_pairs = len(completable_pair_values)
    coordinate_triples = sum(
        all(any(sensitive >> bit & 1 for bit in triple)
            for sensitive in sensitivities)
        for triple in itertools.combinations(range(BITS), 3)
    )
    assert completable_pairs == 343
    assert coordinate_triples == 672
    assert completable_pairs * (SPARSE_ROWS - 1) ** 2 == 10_326_758_967
    formula_cross_check = cross_check_updates(
        c_rows,
        p_rows,
        a_rows,
        a_plus_i,
        completable_pair_values,
    )

    result_records = load_records(result_path)
    monitored_records = load_records(monitored_path)
    assert not any(record.get("status") == "sat" for record in result_records)
    assert result_records[-1] == EXPECTED_SUMMARY
    assert monitored_records[-1] == EXPECTED_SUMMARY

    second_center = load_records(second_center_path)[-1]
    second_c = matrix_rows(second_center, "C")
    second_p = inverse(second_c)
    second_b = compose(compose(second_p, a_rows), second_c)
    second_t = compose(second_p, a_plus_i)
    second_score = score(second_b, second_t)
    second_bad = [
        row for row, metric in enumerate(second_score["metrics"])
        if int(metric) > 16
    ]
    assert second_bad == [12, 16, 18]
    assert (second_score["over"], second_score["excess"], second_score["maximum"]) == (
        3,
        20,
        34,
    )

    artifacts = [
        center_path,
        second_center_path,
        source_path,
        sparse_continuation_source_path,
        transvection_continuation_source_path,
        audit_path,
        result_path,
        monitored_path,
        second_result_path,
    ]
    certificate = {
        "schema": 1,
        "date": "2026-08-03",
        "model": "persistent-seed 66-cycle / 8-delay joint sparse-row search",
        "base": {
            "score": [3, 20, 34],
            "combined_weight": 181,
            "c_weight": 68,
            "bad_rows": bad_rows,
            "bad_metrics": [17, 34, 17],
            "sensitive_supports": [
                [bit for bit in range(BITS) if mask >> bit & 1]
                for mask in sensitivities
            ],
        },
        "coordinate_scope": {
            "completable_rank2_coordinate_pairs": completable_pairs,
            "rank3_hitting_coordinate_triples": coordinate_triples,
            "sparse_nonzero_rows": SPARSE_ROWS,
            "replacement_values_per_changed_row": SPARSE_ROWS - 1,
        },
        "observed_summary": EXPECTED_SUMMARY,
        "formula_cross_check": formula_cross_check,
        "beam": {
            "per_pair_and_third_destination": 256,
            "per_pair_and_original_bad_mask": 64,
            "ordering": ["over", "excess", "maximum", "combined_weight"],
        },
        "monitored_replay": {
            "elapsed_seconds": args.elapsed_seconds,
            "peak_working_set_bytes": args.peak_working_set_bytes,
            "peak_working_set_mib": round(args.peak_working_set_bytes / 2**20, 3),
            "poll_interval_ms": 100,
            "exit_code": 2,
            "exit_code_meaning": "search completed without a hit",
        },
        "second_center_cross_check": {
            "score": [3, 20, 34],
            "bad_rows": second_bad,
            "scope": "24 hit-all pairs with a 2048-value rank3 bridge beam",
        },
        "artifacts": [digest(path, root) for path in artifacts],
        "fixed_input_provenance": {
            "status": "fixed-inputs-preserved",
            "inputs": [
                str(center_path.relative_to(root)).replace("\\", "/"),
                str(second_center_path.relative_to(root)).replace("\\", "/"),
            ],
            "limitation": (
                "The exact source revisions and invocation parameters that "
                "created these two JSONL inputs are unavailable, so they "
                "cannot be claimed as byte-for-byte regenerated."
            ),
            "continuation_sources": [
                str(sparse_continuation_source_path.relative_to(root)).replace(
                    "\\", "/"
                ),
                str(transvection_continuation_source_path.relative_to(root)).replace(
                    "\\", "/"
                ),
            ],
            "continuation_sources_scope": (
                "These current sources can validate or continue from the fixed "
                "inputs; they are not evidence of exact input regeneration."
            ),
        },
        "replay": {
            "compile": (
                "g++ -std=c++20 -O3 -march=native -DNDEBUG "
                ".research/rng_alt_protocol_v2_agent/search_joint_singular_c66.cpp "
                "-o .research/rng_alt_protocol_v2_agent/search_joint_singular_c66.exe"
            ),
            "search": (
                ".research/rng_alt_protocol_v2_agent/search_joint_singular_c66.exe "
                ".research/rng_alt_protocol_v2_agent/sparse-c66-run-c6602.jsonl "
                ".research/rng_alt_protocol_v2_agent/joint-rank3-main-allcoords-b256.jsonl "
                "12 256"
            ),
            "audit": (
                ".venv/Scripts/python.exe "
                ".research/rng_alt_protocol_v2_agent/audit_joint_rank23_certificate.py"
            ),
            "input_mode": (
                "Replay starts from the two committed fixed-input JSONL files; "
                "it does not regenerate those centers."
            ),
        },
        "scope_limit": [
            "The rank-2 coordinate/value scan is exhaustive only for pairs that can be completed into a three-coordinate hitting set.",
            "The rank-3 value scan keeps finite beams; it is not a global rank-3 UNSAT proof.",
            "A full-rank three-row replacement with no invertible two-row intermediate is outside this sequential bridge search.",
            "The mixed-Kraft row bound is a timing necessity, not a shared physical XOR/Switch DAG certificate.",
            "The two center JSONL files are fixed inputs: their original exact generator revisions and invocation parameters are unavailable, and the current continuation sources do not reproduce them byte-for-byte.",
        ],
    }
    args.output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "status": "verified",
        "output": str(args.output),
        "checked": EXPECTED_SUMMARY["checked"],
        "rank3_checked": EXPECTED_SUMMARY["rank3_checked"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
