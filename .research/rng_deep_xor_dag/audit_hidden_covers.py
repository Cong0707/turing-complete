"""Find exact depth-two XOR covers hidden behind a greedy score.

The input JSONL files contain 32-bit GF(2) state encodings whose B/C rows
have weight at most four.  Every distinct weight-three/four target needs one
final scalar XOR.  Weight-two targets and pair intermediates are shared.

This tool solves the pair-intermediate cover exactly with a small branch and
bound search.  It is deliberately streaming and never imports save-writing
code.  XOR cost follows the current game rule exactly: each scalar/U1 XOR is
3 gates / 2 delay; a width-w XOR is 3*w gates / 2 delay.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import time
from typing import Iterable, Iterator, Sequence


BITS = 32
XOR_GATE_PER_BIT = 3
XOR_DELAY = 2


def pair_options(row: int) -> tuple[frozenset[int], ...]:
    units = tuple(1 << bit for bit in range(BITS) if (row >> bit) & 1)
    if len(units) == 3:
        return tuple(frozenset((row ^ unit,)) for unit in units)
    if len(units) == 4:
        a, b, c, d = units
        return (
            frozenset((a | b, c | d)),
            frozenset((a | c, b | d)),
            frozenset((a | d, b | c)),
        )
    raise ValueError(f"unsupported target weight {len(units)}: {row:08x}")


@dataclass(frozen=True)
class ExactCover:
    xor_count: int
    final_count: int
    pair_count: int
    required_pair_count: int
    selected_pairs: tuple[int, ...]
    visited_states: int


class PairCoverSolver:
    def __init__(self, rows: Sequence[int]) -> None:
        targets = frozenset(rows)
        if 0 in targets or any(row.bit_count() > 4 for row in targets):
            raise ValueError("all distinct targets must have weight 1..4")
        self.required = frozenset(row for row in targets if row.bit_count() == 2)
        self.finals = tuple(sorted(row for row in targets if row.bit_count() >= 3))
        self.options = {
            row: tuple(sorted((option | self.required for option in pair_options(row)),
                              key=lambda item: (len(item), tuple(sorted(item)))))
            for row in self.finals
        }
        self.visited = 0
        self.dead: set[tuple[int, frozenset[int]]] = set()

    def _uncovered(self, selected: frozenset[int]) -> list[tuple[int, tuple[frozenset[int], ...]]]:
        result = []
        for row, options in self.options.items():
            if any(option <= selected for option in options):
                continue
            additions = tuple(
                sorted(
                    {option - selected for option in options},
                    key=lambda item: (len(item), tuple(sorted(item))),
                )
            )
            result.append((row, additions))
        return result

    @staticmethod
    def _packing_lower_bound(
        uncovered: Sequence[tuple[int, tuple[frozenset[int], ...]]]
    ) -> int:
        """Cheap admissible bound from targets with disjoint option universes."""

        claimed: set[int] = set()
        lower = 0
        ordered = sorted(
            uncovered,
            key=lambda item: (
                len(set().union(*item[1])),
                len(item[1]),
                min(len(option) for option in item[1]),
            ),
        )
        for _row, options in ordered:
            universe = set().union(*options)
            if universe.isdisjoint(claimed):
                claimed.update(universe)
                lower += min(len(option) for option in options)
        return lower

    def _search(self, selected: frozenset[int], budget: int) -> frozenset[int] | None:
        self.visited += 1
        if len(selected) > budget:
            return None
        key = (budget, selected)
        if key in self.dead:
            return None
        uncovered = self._uncovered(selected)
        if not uncovered:
            return selected
        if len(selected) + self._packing_lower_bound(uncovered) > budget:
            self.dead.add(key)
            return None

        # Fail first: fewest distinct branches, then the largest minimum add.
        _row, choices = min(
            uncovered,
            key=lambda item: (
                len(item[1]),
                -min(len(option) for option in item[1]),
                len(set().union(*item[1])),
                item[0],
            ),
        )
        # Prefer a branch that immediately covers the most remaining targets.
        ranked = sorted(
            choices,
            key=lambda addition: (
                -sum(
                    any(option <= (selected | addition) for option in options)
                    for _target, options in uncovered
                ),
                len(addition),
                tuple(sorted(addition)),
            ),
        )
        for addition in ranked:
            witness = self._search(selected | addition, budget)
            if witness is not None:
                return witness
        self.dead.add(key)
        return None

    def solve(self, upper_bound: int | None = None) -> ExactCover:
        greedy = self._search(self.required, upper_bound or 10_000)
        if greedy is None:
            raise RuntimeError("unbounded pair-cover search unexpectedly failed")
        best = greedy
        # Tighten one pair at a time.  The previous witness is a valid upper bound.
        for budget in range(len(best) - 1, len(self.required) - 1, -1):
            self.dead.clear()
            witness = self._search(self.required, budget)
            if witness is None:
                break
            best = witness
        return ExactCover(
            xor_count=len(best) + len(self.finals),
            final_count=len(self.finals),
            pair_count=len(best),
            required_pair_count=len(self.required),
            selected_pairs=tuple(sorted(best)),
            visited_states=self.visited,
        )


def verify_cover(rows: Sequence[int], result: ExactCover) -> None:
    """Replay a certificate without relying on the branch-and-bound state."""

    targets = frozenset(rows)
    required = frozenset(row for row in targets if row.bit_count() == 2)
    finals = frozenset(row for row in targets if row.bit_count() >= 3)
    selected = frozenset(result.selected_pairs)
    if not required <= selected:
        raise AssertionError("exact cover omitted a required weight-two target")
    if len(selected) != result.pair_count or len(finals) != result.final_count:
        raise AssertionError("exact cover count certificate changed")
    if result.xor_count != len(selected) + len(finals):
        raise AssertionError("exact XOR count certificate changed")
    for row in finals:
        if not any(option <= selected for option in pair_options(row)):
            raise AssertionError(f"target {row:08x} is not covered")


def records(paths: Iterable[Path]) -> Iterator[tuple[Path, int, dict[str, object]]]:
    for path in paths:
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, 1):
                if line.strip():
                    yield path, line_number, json.loads(line)


def digest_t(record: dict[str, object]) -> str:
    rows = record.get("T")
    if not isinstance(rows, list) or len(rows) != BITS:
        raise ValueError("record T must contain 32 rows")
    payload = b"".join(int(str(row), 16).to_bytes(4, "little") for row in rows)
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--emit-at-most", type=int, default=56)
    parser.add_argument(
        "--exclude-inputs",
        nargs="*",
        type=Path,
        default=(),
        help="JSONL records whose T matrices must not be emitted or rescored",
    )
    args = parser.parse_args()

    started = time.perf_counter()
    excluded = {
        digest_t(record)
        for _path, _line, record in records(args.exclude_inputs)
    }
    seen: set[str] = set(excluded)
    histogram: dict[int, int] = {}
    input_count = duplicate_count = emitted_count = visited_states = 0
    scored_count = 0
    best: dict[str, object] | None = None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as sink:
        for path, line_number, record in records(args.inputs):
            input_count += 1
            digest = digest_t(record)
            if digest in seen:
                duplicate_count += 1
                continue
            seen.add(digest)
            rows = tuple(
                int(str(value), 16)
                for name in ("B", "C")
                for value in record[name]  # type: ignore[index]
            )
            result = PairCoverSolver(rows).solve()
            scored_count += 1
            verify_cover(rows, result)
            histogram[result.xor_count] = histogram.get(result.xor_count, 0) + 1
            visited_states += result.visited_states
            item = dict(record)
            item.update(
                {
                    "source": str(path),
                    "source_line": line_number,
                    "exact_xor": result.xor_count,
                    "exact_xor_gate": XOR_GATE_PER_BIT * result.xor_count,
                    "exact_xor_delay_per_layer": XOR_DELAY,
                    "exact_pairs": [f"{pair:08x}" for pair in result.selected_pairs],
                    "exact_pair_count": result.pair_count,
                    "exact_final_count": result.final_count,
                    "exact_required_pair_count": result.required_pair_count,
                    "cover_visited_states": result.visited_states,
                    "t_sha256": digest,
                }
            )
            if best is None or (result.xor_count, digest) < (
                int(best["exact_xor"]), str(best["t_sha256"])
            ):
                best = item
            if result.xor_count <= args.emit_at_most:
                sink.write(json.dumps(item, separators=(",", ":")) + "\n")
                sink.flush()
                emitted_count += 1
                print(
                    f"hit exact_xor={result.xor_count} "
                    f"{path.name}:{line_number} sha={digest[:12]}",
                    flush=True,
                )

    summary = {
        "schema": 1,
        "model": "exact scalar depth-two XOR pair cover",
        "cost_model": {
            "ordinary_xor": [3, 2],
            "u1_xor": [3, 2],
            "width_w_xor": ["3*w", 2],
        },
        "inputs": [str(path) for path in args.inputs],
        "exclude_inputs": [str(path) for path in args.exclude_inputs],
        "excluded_t_count": len(excluded),
        "input_count": input_count,
        "scored_t_count": scored_count,
        "seen_t_count_including_excluded": len(seen),
        "duplicate_count": duplicate_count,
        "emitted_at_most": args.emit_at_most,
        "emitted_count": emitted_count,
        "xor_histogram": dict(sorted(histogram.items())),
        "cover_visited_states": visited_states,
        "elapsed_seconds": time.perf_counter() - started,
        "best": best,
    }
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "best"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
