"""Stream-select low-conflict x59/x60 bases for physical Switch auditing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def rows(record: dict[str, object], name: str) -> tuple[int, ...]:
    return tuple(int(str(value), 16) for value in record[name])


def conflicts(t_rows: tuple[int, ...], b_rows: tuple[int, ...]) -> tuple[int, int]:
    direct = 0
    pair_exact = 0
    seen: dict[int, int] = {}
    for target, steady in zip(t_rows, b_rows):
        if steady.bit_count() == 1:
            direct += target.bit_count() != 1
        elif steady.bit_count() == 2:
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
    parser.add_argument("--xor", type=int, required=True)
    parser.add_argument("--max-direct", type=int, required=True)
    parser.add_argument("--max-pair", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    selected: list[tuple[tuple[int, int, int, str], str]] = []
    total_xor = 0
    with args.source.open("r", encoding="utf-8-sig") as source:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line)
            if int(record["cover"]["greedy_xor"]) != args.xor:
                continue
            total_xor += 1
            direct, pair_exact = conflicts(rows(record, "T"), rows(record, "B"))
            if direct > args.max_direct or pair_exact > args.max_pair:
                continue
            key = (
                direct,
                pair_exact,
                int(record["structural"]["weight"]),
                str(record["hash"]),
            )
            selected.append((key, line))
    selected.sort(key=lambda item: item[0])
    if args.limit is not None:
        selected = selected[: args.limit]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(line for _, line in selected), encoding="utf-8")
    print(json.dumps({
        "xor": args.xor,
        "total_xor_records": total_xor,
        "selected_records": len(selected),
        "max_direct": args.max_direct,
        "max_pair": args.max_pair,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
