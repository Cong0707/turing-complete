"""Select the strongest radius-7 candidates for exact 401/9/67 auditing.

This is an offline research helper.  It reads the line-indexed heavy-OR
frontier and copies matching matrix records from the original BFS JSONL.  It
does not import save-writing code or access the live game save.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--frontier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--xor", type=int, required=True)
    parser.add_argument("--max-heavy-or", type=int, required=True)
    args = parser.parse_args()

    selected: dict[int, dict[str, int]] = {}
    with args.frontier.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            try:
                source_line = int(row["line"])
                xor_count = int(row["xor"])
                heavy_or = int(row["heavy_or_lower_bound"])
                target_or = int(row["target_or"])
            except (TypeError, ValueError):
                continue
            if xor_count == args.xor and heavy_or <= args.max_heavy_or:
                selected[source_line] = {
                    "heavy_or_lower_bound": heavy_or,
                    "target_or": target_or,
                }

    records: list[dict[str, object]] = []
    with args.source.open(encoding="utf-8-sig") as stream:
        for source_line, line in enumerate(stream, 1):
            metadata = selected.get(source_line)
            if metadata is None:
                continue
            record = json.loads(line)
            record["frontier_source_line"] = source_line
            record["heavy_or_lower_bound"] = metadata["heavy_or_lower_bound"]
            record["target_or"] = metadata["target_or"]
            records.append(record)

    records.sort(
        key=lambda record: (
            int(record["heavy_or_lower_bound"]),
            int(record["cover"]["lower"]),
            int(record["structural"]["weight"]),
            int(record["frontier_source_line"]),
        )
    )
    if len(records) != len(selected):
        raise AssertionError(
            f"selected {len(selected)} lines but recovered {len(records)} records"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(json.dumps(record, separators=(",", ":")) + "\n")
    print(
        json.dumps(
            {
                "source": str(args.source),
                "frontier": str(args.frontier),
                "xor": args.xor,
                "max_heavy_or": args.max_heavy_or,
                "record_count": len(records),
                "output": str(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
