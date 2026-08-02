"""Enumerate every fixed-cost pair cover and feedback decomposition variant."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import reduce
from itertools import product
import json
from operator import mul
from pathlib import Path
from typing import Sequence


def bits(value: int) -> tuple[int, ...]:
    return tuple(index for index in range(32) if value >> index & 1)


def pair_partitions(row: int) -> tuple[tuple[int, ...], ...]:
    support = tuple(1 << bit for bit in bits(row))
    if len(support) == 3:
        return tuple((row ^ unit,) for unit in support)
    if len(support) == 4:
        a, b, c, d = support
        return (
            tuple(sorted((a | b, c | d))),
            tuple(sorted((a | c, b | d))),
            tuple(sorted((a | d, b | c))),
        )
    raise ValueError(f"row {row:08x} has weight {len(support)}")


@dataclass
class CoverEnumerator:
    options: dict[int, tuple[frozenset[int], ...]]
    budget: int
    state_limit: int
    solution_limit: int
    visited: set[frozenset[int]]
    solutions: set[frozenset[int]]
    truncated: bool = False

    def run(self) -> None:
        self._visit(frozenset())

    def _visit(self, selected: frozenset[int]) -> None:
        if self.truncated or selected in self.visited:
            return
        if len(self.visited) >= self.state_limit or len(self.solutions) >= self.solution_limit:
            self.truncated = True
            return
        self.visited.add(selected)
        uncovered = [
            options
            for options in self.options.values()
            if not any(option <= selected for option in options)
        ]
        if not uncovered:
            self.solutions.add(selected)
            return
        if len(selected) >= self.budget:
            return
        row_options = min(
            uncovered,
            key=lambda options: (
                len({option - selected for option in options}),
                -min(len(option - selected) for option in options),
            ),
        )
        additions = sorted(
            {option - selected for option in row_options},
            key=lambda option: (len(option), tuple(sorted(option))),
        )
        for addition in additions:
            extended = selected | addition
            if len(extended) <= self.budget:
                self._visit(extended)


def enumerate_pair_covers(
    rows: Sequence[int],
    pair_budget: int,
    *,
    state_limit: int,
    solution_limit: int,
) -> tuple[tuple[frozenset[int], ...], int, bool]:
    targets = frozenset(rows)
    required = frozenset(row for row in targets if row.bit_count() == 2)
    finals = frozenset(row for row in targets if row.bit_count() in (3, 4))
    extra_budget = pair_budget - len(required)
    if extra_budget < 0:
        return (), 0, False
    options = {
        row: tuple(frozenset(option) - required for option in pair_partitions(row))
        for row in finals
    }
    enumerator = CoverEnumerator(
        options,
        extra_budget,
        state_limit,
        solution_limit,
        set(),
        set(),
    )
    enumerator.run()
    covers = tuple(
        sorted(
            (required | extras for extras in enumerator.solutions),
            key=lambda cover: (len(cover), tuple(sorted(cover))),
        )
    )
    return covers, len(enumerator.visited), enumerator.truncated


def matrix(record: dict[str, object], name: str) -> tuple[int, ...]:
    return tuple(int(str(value), 16) for value in record[name])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--max-xor", type=int, required=True)
    parser.add_argument("--state-limit", type=int, default=1_000_000)
    parser.add_argument("--solution-limit", type=int, default=50_000)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    records = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    emitted = 0
    covers_total = 0
    variants_total = 0
    cover_states = 0
    truncated_records = 0
    maximum_variants = 0
    by_xor: dict[int, int] = {}
    seen: set[tuple[tuple[int, ...], tuple[int, ...], tuple[tuple[int, tuple[int, ...]], ...]]] = set()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as output:
        for record_index, record in enumerate(records):
            T = matrix(record, "T")
            B = matrix(record, "B")
            C = matrix(record, "C")
            finals = frozenset(row for row in (*B, *C) if row.bit_count() in (3, 4))
            pair_budget = args.max_xor - len(finals)
            covers, visited, truncated = enumerate_pair_covers(
                (*B, *C),
                pair_budget,
                state_limit=args.state_limit,
                solution_limit=args.solution_limit,
            )
            cover_states += visited
            truncated_records += int(truncated)
            covers_total += len(covers)

            for cover_index, pairs in enumerate(covers):
                xor_count = len(pairs) + len(finals)
                if xor_count > args.max_xor:
                    continue
                options = {
                    row: tuple(
                        option
                        for option in pair_partitions(row)
                        if set(option) <= pairs
                    )
                    for row in finals
                }
                if any(not choices for choices in options.values()):
                    raise AssertionError("enumerated cover does not cover every final")
                active_b = tuple(
                    row
                    for row in dict.fromkeys(B)
                    if row in options and len(options[row]) > 1
                )
                variant_count = reduce(
                    mul, (len(options[row]) for row in active_b), 1
                )
                maximum_variants = max(maximum_variants, variant_count)
                variants_total += variant_count
                for indexes in product(*(range(len(options[row])) for row in active_b)):
                    decompositions = {row: choices[0] for row, choices in options.items()}
                    for row, index in zip(active_b, indexes):
                        decompositions[row] = options[row][index]
                    key = (
                        T,
                        tuple(sorted(pairs)),
                        tuple(sorted((row, decompositions[row]) for row in active_b)),
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    derived = {
                        "source_record_index": record_index,
                        "source_cover_index": cover_index,
                        "xor_count": xor_count,
                        "T": [f"{row:08x}" for row in T],
                        "B": [f"{row:08x}" for row in B],
                        "C": [f"{row:08x}" for row in C],
                        "selected_pair_gates": [f"{pair:08x}" for pair in sorted(pairs)],
                        "decompositions": {
                            f"{row:08x}": [f"{node:08x}" for node in decompositions[row]]
                            for row in sorted(decompositions)
                        },
                    }
                    output.write(json.dumps(derived, separators=(",", ":")) + "\n")
                    emitted += 1
                    by_xor[xor_count] = by_xor.get(xor_count, 0) + 1
            if not (record_index + 1) % 50:
                print(
                    f"records={record_index + 1}/{len(records)} covers={covers_total} emitted={emitted}",
                    flush=True,
                )

    summary = {
        "schema": 1,
        "input": str(args.input),
        "input_records": len(records),
        "max_xor": args.max_xor,
        "pair_cover_count": covers_total,
        "decomposition_variant_count": variants_total,
        "emitted_unique_variant_count": emitted,
        "emitted_by_xor": {str(key): by_xor[key] for key in sorted(by_xor)},
        "cover_search_states": cover_states,
        "truncated_record_count": truncated_records,
        "maximum_feedback_decomposition_variants": maximum_variants,
        "limits": {
            "state_limit": args.state_limit,
            "solution_limit": args.solution_limit,
        },
    }
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if not truncated_records else 2


if __name__ == "__main__":
    raise SystemExit(main())
