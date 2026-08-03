"""Cross-check exact-result coverage of a mixed candidate JSONL by T."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def digest_rows(rows: list[str]) -> str:
    payload = "".join(f"{int(str(row), 16):08x}" for row in rows).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8-sig") as stream:
        for line_number, raw in enumerate(stream, 1):
            if raw.strip():
                yield line_number, json.loads(raw)


def source_xor(record: dict) -> int | None:
    value = record.get("xor")
    if value is None:
        value = (record.get("cover") or {}).get("greedy_xor")
    return None if value is None else int(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--xor", type=int, required=True)
    parser.add_argument("--results", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pending-output", type=Path)
    args = parser.parse_args()

    candidates: dict[str, dict] = {}
    candidate_duplicates = 0
    for line_number, record in iter_jsonl(args.candidates):
        if source_xor(record) != args.xor:
            continue
        digest = digest_rows(record["T"])
        if digest in candidates:
            candidate_duplicates += 1
            continue
        candidates[digest] = {
            "source_line": line_number,
            "record": record,
        }

    observations: dict[str, list[dict]] = defaultdict(list)
    for path in args.results:
        for line_number, record in iter_jsonl(path):
            digest = str(record.get("T_sha256", "")).lower()
            if not digest:
                continue
            observations[digest].append({
                "file": path.name,
                "line": line_number,
                "record": record.get("record"),
                "source_line": record.get("source_line"),
                "status": str(record.get("status", "missing")).lower(),
                "logic_cost": record.get("logic_cost"),
            })

    statuses = Counter()
    pending = []
    covered = {}
    for digest, candidate in candidates.items():
        found = observations.get(digest, [])
        status_set = sorted({item["status"] for item in found})
        definitive = bool({"sat", "unsat"} & set(status_set))
        key = "+".join(status_set) if status_set else "never_solved"
        statuses[key] += 1
        item = {
            "T_sha256": digest,
            "source_line": candidate["source_line"],
            "frontier_source_line": candidate["record"].get("frontier_source_line"),
            "cover_lower": (candidate["record"].get("cover") or {}).get("lower"),
            "structural_weight": (candidate["record"].get("structural") or {}).get("weight"),
            "observations": found,
        }
        if definitive:
            covered[digest] = item
        else:
            pending.append(item)

    result = {
        "candidate_source": str(args.candidates),
        "xor": args.xor,
        "candidate_unique_T": len(candidates),
        "candidate_duplicate_records": candidate_duplicates,
        "result_files": [str(path) for path in args.results],
        "status_sets": dict(sorted(statuses.items())),
        "definitive_covered_T": len(covered),
        "pending_T": len(pending),
        "pending": pending,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.pending_output is not None:
        pending_digests = {item["T_sha256"] for item in pending}
        args.pending_output.parent.mkdir(parents=True, exist_ok=True)
        with args.pending_output.open("w", encoding="utf-8", newline="\n") as stream:
            for _line_number, record in iter_jsonl(args.candidates):
                if source_xor(record) != args.xor:
                    continue
                if digest_rows(record["T"]) in pending_digests:
                    stream.write(json.dumps(record, separators=(",", ":")) + "\n")
    print(json.dumps({key: result[key] for key in (
        "xor", "candidate_unique_T", "candidate_duplicate_records",
        "status_sets", "definitive_covered_T", "pending_T"
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
