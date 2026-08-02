"""Extract the lexicographically best sparse-init RNG state from JSONL shards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def key(record: dict[str, object]) -> tuple[int, ...]:
    score = record["score"]
    assert isinstance(score, dict)
    return (
        int(score["excess"]),
        int(score["heavy"]),
        int(score["maximum"]),
        int(score["xor_total"]),
        int(score["weight"]),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    records: list[dict[str, object]] = []
    for path in args.inputs:
        with path.open(encoding="utf-8") as stream:
            records.extend(json.loads(line) for line in stream if line.strip())
    best = min(records, key=key)
    args.output.write_text(json.dumps(best, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"key": key(best), "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
