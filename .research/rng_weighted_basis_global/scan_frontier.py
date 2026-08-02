"""Stream a basis JSONL and classify necessary tick-zero phase conflicts."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path


def rows(record: dict[str, object], name: str) -> tuple[int, ...]:
    return tuple(int(str(value), 16) for value in record[name])


def early_conflicts(t_rows: tuple[int, ...], b_rows: tuple[int, ...]) -> tuple[int, int]:
    direct = 0
    pair_exact = 0
    seen: dict[int, int] = {}
    for target, steady in zip(t_rows, b_rows):
        weight = steady.bit_count()
        if weight == 1:
            direct += target.bit_count() != 1
        elif weight == 2:
            if target.bit_count() > 2:
                pair_exact += 1
            elif steady in seen and seen[steady] != target:
                pair_exact += 1
            else:
                seen[steady] = target
    return direct, pair_exact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--clean-jsonl", type=Path, required=True)
    parser.add_argument("--min-xor", type=int, default=56)
    parser.add_argument("--max-xor", type=int, default=63)
    args = parser.parse_args()

    counts: Counter[int] = Counter()
    minima: dict[int, tuple[int, int]] = {}
    histograms: dict[int, Counter[str]] = defaultdict(Counter)
    clean_count: Counter[int] = Counter()
    total = 0
    with (
        args.source.open("r", encoding="utf-8-sig") as source,
        args.clean_jsonl.open("w", encoding="utf-8", newline="\n") as clean,
    ):
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            total += 1
            record = json.loads(line)
            xor_count = int(record["cover"]["greedy_xor"])
            if not args.min_xor <= xor_count <= args.max_xor:
                continue
            direct, pair_exact = early_conflicts(rows(record, "T"), rows(record, "B"))
            counts[xor_count] += 1
            histograms[xor_count][f"{direct}/{pair_exact}"] += 1
            metric = (direct, pair_exact)
            if xor_count not in minima or metric < minima[xor_count]:
                minima[xor_count] = metric
            if metric == (0, 0):
                clean_count[xor_count] += 1
                record["source_line"] = line_number
                record["early_phase"] = {"direct": 0, "pair_exact": 0}
                clean.write(json.dumps(record, separators=(",", ":")) + "\n")

    document = {
        "source": str(args.source),
        "total_records": total,
        "selected_by_xor": {str(key): counts[key] for key in sorted(counts)},
        "minimum_conflicts_by_xor": {
            str(key): {"direct": minima[key][0], "pair_exact": minima[key][1]}
            for key in sorted(minima)
        },
        "early_clean_by_xor": {
            str(key): clean_count[key] for key in sorted(clean_count)
        },
        "conflict_histogram_by_xor": {
            str(key): dict(sorted(histograms[key].items())) for key in sorted(histograms)
        },
    }
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in document.items() if "histogram" not in key}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
