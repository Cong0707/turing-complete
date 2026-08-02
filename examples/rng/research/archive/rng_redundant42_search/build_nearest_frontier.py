"""Build and verify the closest invalid rank-32 lifting from a search log."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import re


BITS = 32
AUX = 10
MASK = (1 << BITS) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def transition_rows() -> tuple[int, ...]:
    return tuple(
        sum(((xorshift32(1 << source) >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


def apply_row(row: int, matrix: tuple[int, ...]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def apply_matrix(matrix: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << index for index, row in enumerate(matrix))


def parse_best(path: Path) -> tuple[tuple[int, int, int], tuple[int, ...], tuple[int, ...]]:
    pattern = re.compile(
        r"best excess=(\d+) max_weight=(\d+) total_weight=(\d+) "
        r"R=([0-9a-f,]+) V=([0-9a-f,]+)$"
    )
    candidates = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.fullmatch(line)
        if not match:
            continue
        score = tuple(int(match.group(index)) for index in range(1, 4))
        redundant = tuple(int(value, 16) for value in match.group(4).split(","))
        decoder_labels = tuple(int(value, 16) for value in match.group(5).split(","))
        if len(redundant) != AUX or len(decoder_labels) != BITS:
            raise ValueError(f"invalid local-search line: {line}")
        candidates.append((score, redundant, decoder_labels))
    if not candidates:
        raise ValueError(f"no local-search candidates in {path}")
    return min(candidates, key=lambda candidate: candidate[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    reported_score, redundant, x_rows = parse_best(args.log)
    a_rows = transition_rows()
    e_rows = tuple(
        a_rows[index] ^ apply_row(x_rows[index], redundant)
        for index in range(BITS)
    ) + redundant
    o_rows = tuple((1 << index) | (x_rows[index] << BITS) for index in range(BITS))
    h_rows = tuple(
        row | (apply_row(row, x_rows) << BITS)
        for row in e_rows
    )

    if tuple(row & MASK for row in h_rows) != e_rows:
        raise AssertionError("H*S != E")
    if compose(o_rows, e_rows) != a_rows:
        raise AssertionError("O*E != A")
    if compose(h_rows, e_rows) != compose(e_rows, a_rows):
        raise AssertionError("H*E != E*A")

    seeds = [0, 1, 2, 0x12345678, MASK]
    generator = random.Random(20260801)
    seeds.extend(generator.getrandbits(BITS) for _ in range(64))
    for seed in seeds:
        natural = seed
        state = apply_matrix(e_rows, seed)
        for _ in range(65):
            natural = xorshift32(natural)
            if apply_matrix(o_rows, state) != natural:
                raise AssertionError("visible sequence mismatch")
            state = apply_matrix(h_rows, state)

    h_weights = tuple(row.bit_count() for row in h_rows)
    o_weights = tuple(row.bit_count() for row in o_rows)
    excess = sum(max(0, weight - 4) for weight in h_weights + o_weights)
    score = (excess, max(h_weights + o_weights), sum(h_weights + o_weights))
    if score != reported_score:
        raise AssertionError(f"search score changed: {score} != {reported_score}")

    result = {
        "status": "invalid-frontier",
        "reason": "at least one target row has support greater than four",
        "verified_sequences": {"seeds": len(seeds), "outputs_per_seed": 65},
        "score": {
            "support_excess_over_4": score[0],
            "maximum_row_weight": score[1],
            "total_H_O_row_weight": score[2],
        },
        "bad_H_rows": [
            {"index": index, "weight": weight, "row_hex_42bit": f"{h_rows[index]:011x}"}
            for index, weight in enumerate(h_weights)
            if weight > 4
        ],
        "redundant_rows_hex": [f"{row:08x}" for row in redundant],
        "X_rows_hex": [f"{row:03x}" for row in x_rows],
        "E_rows_hex": [f"{row:08x}" for row in e_rows],
        "H_rows_hex_42bit": [f"{row:011x}" for row in h_rows],
        "O_rows_hex_42bit": [f"{row:011x}" for row in o_rows],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["score"], indent=2))
    print(f"bad H rows: {len(result['bad_H_rows'])}")


if __name__ == "__main__":
    main()
