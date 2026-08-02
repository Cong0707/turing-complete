"""General finite-horizon linear decoder search around the best 42-state H.

Unlike ``search_general_lift.cpp``, this checker does not assume ``O=[I|X]``
or the global semiconjugacy ``O*H=A*O``.  For each sparse transition matrix H
it computes the 65 reachable state trajectories from the seed injection and
then solves every output row exactly by a <=4-state meet-in-the-middle lookup.
"""

from __future__ import annotations

import argparse
from itertools import product
import json
from pathlib import Path


VISIBLE = 32
STATES = 42
CYCLES = 65
MASK32 = (1 << VISIBLE) - 1

H_FRONTIER = (
    0x12000002001, 0x00204002000, 0x00401008004, 0x10400300100,
    0x00800600200, 0x03000000000, 0x02001000800, 0x04103001000,
    0x00100020110, 0x01000000200, 0x00410008000, 0x00020000888,
    0x00006001000, 0x00080044002, 0x00400488004, 0x00410008000,
    0x01820010000, 0x02100402000, 0x00080840000, 0x00400088004,
    0x00002200100, 0x20004400200, 0x08000804400, 0x00011800800,
    0x00122001000, 0x00042200100, 0x01084000200, 0x20000404000,
    0x00411000800, 0x00122001000, 0x00040000000, 0x20080400000,
    0x20040020001, 0x10400004002, 0x00800110008, 0x00100220010,
    0x08200040020, 0x04400080040, 0x00401100080, 0x0A000800400,
    0x20004002000, 0x08008404000,
)
BAD_ROWS = (3, 7, 14)


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK32
    value ^= value >> 5
    return value & MASK32


def transition_rows() -> tuple[int, ...]:
    return tuple(
        sum(((xorshift32(1 << source) >> target) & 1) << source for source in range(VISIBLE))
        for target in range(VISIBLE)
    )


A_ROWS = transition_rows()


def apply_row(row: int, matrix: tuple[int, ...]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def state_signatures(h_rows: tuple[int, ...]) -> tuple[int, ...]:
    current = tuple(row & MASK32 for row in h_rows)  # H*S, the first state.
    signatures = [0] * STATES
    for cycle in range(CYCLES):
        for state, row in enumerate(current):
            signatures[state] |= row << (VISIBLE * cycle)
        current = tuple(apply_row(row, current) for row in h_rows)
    return tuple(signatures)


def desired_signatures() -> tuple[int, ...]:
    current = A_ROWS
    signatures = [0] * VISIBLE
    for cycle in range(CYCLES):
        for output, row in enumerate(current):
            signatures[output] |= row << (VISIBLE * cycle)
        current = compose(A_ROWS, current)
    return tuple(signatures)


DESIRED = desired_signatures()


def subset2_dictionary(signatures: tuple[int, ...]) -> tuple[tuple[tuple[int, int], ...], dict[int, int]]:
    entries = [(0, 0)]
    entries.extend((signature, 1 << index) for index, signature in enumerate(signatures))
    for left in range(STATES):
        for right in range(left + 1, STATES):
            entries.append((signatures[left] ^ signatures[right], (1 << left) | (1 << right)))
    best: dict[int, int] = {}
    for signature, mask in entries:
        old = best.get(signature)
        if old is None or mask.bit_count() < old.bit_count():
            best[signature] = mask
    return tuple(entries), best


def decode_outputs(h_rows: tuple[int, ...]) -> tuple[tuple[int | None, ...], dict[str, int]]:
    signatures = state_signatures(h_rows)
    entries, dictionary = subset2_dictionary(signatures)
    outputs: list[int | None] = []
    lookups = 0
    for target in DESIRED:
        found = None
        for partial_signature, partial_mask in entries:
            lookups += 1
            mate = dictionary.get(target ^ partial_signature)
            if mate is None:
                continue
            candidate = partial_mask ^ mate
            if candidate.bit_count() <= 4:
                if found is None or candidate.bit_count() < found.bit_count():
                    found = candidate
        outputs.append(found)
    return tuple(outputs), {"pair_entries": len(entries), "lookups": lookups}


def apply_matrix(rows: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << index for index, row in enumerate(rows))


def verify_sequences(h_rows: tuple[int, ...], o_rows: tuple[int, ...]) -> None:
    for seed in range(256):
        state = apply_matrix(h_rows, seed)
        natural = seed
        for _ in range(CYCLES):
            natural = xorshift32(natural)
            if apply_matrix(o_rows, state) != natural:
                raise AssertionError(f"sequence mismatch at seed {seed}")
            state = apply_matrix(h_rows, state)


def dropped_variants(row: int) -> tuple[int, ...]:
    if row.bit_count() != 5:
        raise ValueError("drop neighborhood requires a weight-five row")
    return tuple(
        row ^ (1 << bit) for bit in range(STATES) if (row >> bit) & 1
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    baseline_outputs, baseline_work = decode_outputs(H_FRONTIER)
    if any(row is None for row in baseline_outputs):
        raise AssertionError("known semiconjugate frontier must decode all outputs")
    verify_sequences(H_FRONTIER, tuple(int(row) for row in baseline_outputs))

    variants = [dropped_variants(H_FRONTIER[index]) for index in BAD_ROWS]
    records = []
    best = None
    full_solution = None
    for choices in product(*variants):
        h_rows = list(H_FRONTIER)
        for index, row in zip(BAD_ROWS, choices):
            h_rows[index] = row
        h_tuple = tuple(h_rows)
        decoded, work = decode_outputs(h_tuple)
        matched = sum(row is not None for row in decoded)
        support = sum(int(row).bit_count() for row in decoded if row is not None)
        record = {
            "replacement_rows_hex": [f"{row:011x}" for row in choices],
            "matched_output_rows": matched,
            "matched_output_support": support,
            "unmatched_output_rows": [index for index, row in enumerate(decoded) if row is None],
        }
        records.append(record)
        key = (-matched, support, tuple(choices))
        if best is None or key < best[0]:
            best = (key, record)
        if matched == VISIBLE:
            o_rows = tuple(int(row) for row in decoded)
            verify_sequences(h_tuple, o_rows)
            full_solution = {
                "H_rows_hex": [f"{row:011x}" for row in h_tuple],
                "O_rows_hex": [f"{row:011x}" for row in o_rows],
                "verified_sequences": {"seeds": 256, "outputs_per_seed": CYCLES},
            }
            break

    assert best is not None
    result = {
        "scope": (
            "all 5^3 drop-one repairs of the three weight-five H rows; O is an arbitrary "
            "32x42 matrix with row support <=4 and is solved exactly over all 65 cycles"
        ),
        "model_restrictions_removed": ["O=[I|X]", "O*H=A*O"],
        "baseline": {
            "decoded_output_rows": sum(row is not None for row in baseline_outputs),
            "verified_sequences": {"seeds": 256, "outputs_per_seed": CYCLES},
            **baseline_work,
        },
        "searched_H_matrices": len(records),
        "best": best[1],
        "full_solution": full_solution,
        "records": records,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("scope", "searched_H_matrices", "best", "full_solution")}, indent=2))


if __name__ == "__main__":
    main()
