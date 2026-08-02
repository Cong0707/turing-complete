"""Verify proxy-v2-alt RNG candidates without launching the game."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re


VISIBLE = 32
LOG_PATTERN = re.compile(
    r"^(?P<prefix>.*?)\bX=(?P<x>[0-9a-fA-F]+(?:,[0-9a-fA-F]+)*)"
    r"\s+D=(?P<d>[0-9a-fA-F]+(?:,[0-9a-fA-F]+)*)\s*$"
)
STAT_PATTERN = re.compile(r"\b([a-zA-Z0-9_]+)=(-?\d+)")


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & 0xFFFFFFFF
    value ^= value >> 5
    return value & 0xFFFFFFFF


def transition_rows() -> tuple[int, ...]:
    return tuple(
        sum(((xorshift32(1 << source) >> target) & 1) << source for source in range(VISIBLE))
        for target in range(VISIBLE)
    )


def apply_row(row: int, matrix: tuple[int, ...]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def apply_matrix(matrix: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << index for index, row in enumerate(matrix))


def parse_last(path: Path) -> dict[str, object]:
    matches: list[tuple[int, re.Match[str]]] = []
    for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        match = LOG_PATTERN.match(line.strip())
        if match:
            matches.append((line_number, match))
    if not matches:
        raise ValueError(f"no candidate in {path}")
    line_number, match = matches[-1]
    return {
        "source_log": str(path.resolve()),
        "source_line": line_number,
        "source_sha256": sha256(path.read_bytes()).hexdigest(),
        "reported": {key: int(value) for key, value in STAT_PATTERN.findall(match.group("prefix"))},
        "X": tuple(int(value, 16) for value in match.group("x").split(",")),
        "D": tuple(int(value, 16) for value in match.group("d").split(",")),
    }


def build_full(x_rows: tuple[int, ...], d_rows: tuple[int, ...]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if len(x_rows) != VISIBLE or not d_rows:
        raise ValueError("invalid X/D dimensions")
    a_rows = transition_rows()
    output = tuple((1 << index) | (x_rows[index] << VISIBLE) for index in range(VISIBLE))
    top = tuple(
        apply_row(a_rows[index], output) ^ apply_row(x_rows[index], d_rows)
        for index in range(VISIBLE)
    )
    return top + d_rows, output


def active_hidden_rows(full_h: tuple[int, ...], hidden: int) -> tuple[int, ...]:
    symbolic = tuple(1 << index for index in range(VISIBLE)) + (0,) * hidden
    active: set[int] = set()
    for _ in range(len(full_h)):
        active.update(index for index in range(hidden) if symbolic[VISIBLE + index])
        symbolic = tuple(apply_row(row, symbolic) for row in full_h)
    return tuple(sorted(active))


def project_active(
    full_h: tuple[int, ...],
    full_o: tuple[int, ...],
    active: tuple[int, ...],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    kept = tuple(range(VISIBLE)) + tuple(VISIBLE + index for index in active)

    def project(row: int) -> int:
        return sum(((row >> old) & 1) << new for new, old in enumerate(kept))

    return tuple(project(full_h[index]) for index in kept), tuple(project(row) for row in full_o)


def verify_candidate(parsed: dict[str, object]) -> dict[str, object]:
    x_rows = parsed["X"]
    d_rows = parsed["D"]
    assert isinstance(x_rows, tuple) and isinstance(d_rows, tuple)
    full_h, full_o = build_full(x_rows, d_rows)
    a_rows = transition_rows()

    # This identity proves the recurrence for every state, not only the samples.
    for index in range(VISIBLE):
        if apply_row(full_o[index], full_h) != apply_row(a_rows[index], full_o):
            raise AssertionError(f"lifting identity failed at output row {index}")

    active = active_hidden_rows(full_h, len(d_rows))
    h_rows, o_rows = project_active(full_h, full_o, active)
    for seed in range(256):
        state = apply_matrix(h_rows, seed)
        natural = seed
        for cycle in range(65):
            natural = xorshift32(natural)
            actual = apply_matrix(o_rows, state)
            if actual != natural:
                raise AssertionError(
                    f"sequence mismatch seed={seed} cycle={cycle}: {actual:08x}!={natural:08x}"
                )
            state = apply_matrix(h_rows, state)

    targets = tuple(sorted({row for row in h_rows + o_rows if row.bit_count() >= 2}))
    occurrence_weights = Counter(row.bit_count() for row in h_rows + o_rows)
    distinct_weights = Counter(row.bit_count() for row in targets)
    state_width = len(h_rows)
    hex_width = (state_width + 3) // 4
    reported = parsed["reported"]
    assert isinstance(reported, dict)
    if reported.get("active_hidden") != len(active):
        raise AssertionError(
            f"reported active_hidden={reported.get('active_hidden')} but exact reachability gives {len(active)}"
        )
    return {
        "source_log": parsed["source_log"],
        "source_line": parsed["source_line"],
        "source_sha256": parsed["source_sha256"],
        "reported_proxy": reported,
        "X_rows_hex": [f"{row:03x}" for row in x_rows],
        "D_rows_hex": [f"{row:011x}" for row in d_rows],
        "exact_active_original_hidden_rows": list(active),
        "pruned_state_bits": state_width,
        "fixed_gate": 5 * state_width + 32 + 6,
        "target_summary": {
            "raw_H_O_rows": len(h_rows) + len(o_rows),
            "distinct_nontrivial": len(targets),
            "maximum_weight": max((row.bit_count() for row in targets), default=0),
            "occurrence_weight_distribution": {
                str(weight): count for weight, count in sorted(occurrence_weights.items())
            },
            "distinct_weight_distribution": {
                str(weight): count for weight, count in sorted(distinct_weights.items())
            },
        },
        "H_rows_hex": [f"{row:0{hex_width}x}" for row in h_rows],
        "O_rows_hex": [f"{row:0{hex_width}x}" for row in o_rows],
        "verification": {
            "strict_zero_hidden_initial_state": "PASS",
            "lifting_identity_OH_equals_AO": "PASS (all 32 rows)",
            "sample_sequences": "PASS",
            "seeds": 256,
            "outputs_per_seed": 65,
            "total_outputs_checked": 256 * 65,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    candidates = []
    seen: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    for path in args.log:
        parsed = parse_last(path)
        key = parsed["X"], parsed["D"]
        assert isinstance(key[0], tuple) and isinstance(key[1], tuple)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(verify_candidate(parsed))
    candidates.sort(key=lambda item: item["reported_proxy"]["greedy_total_gate"])
    result = {
        "schema": 1,
        "scope": "proxy-v2-alt active-hidden candidates",
        "candidate_count": len(candidates),
        "best_greedy_total_gate": candidates[0]["reported_proxy"]["greedy_total_gate"],
        "candidates": candidates,
    }
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("ascii")
    args.output.write_bytes(encoded)
    print(json.dumps({
        "candidate_count": len(candidates),
        "best_greedy_total_gate": result["best_greedy_total_gate"],
        "sha256": sha256(encoded).hexdigest(),
    }, indent=2))


if __name__ == "__main__":
    main()
