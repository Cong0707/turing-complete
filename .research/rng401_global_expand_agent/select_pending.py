"""Select only unresolved or never-solved transition matrices for exact SAT."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest_t(record: dict) -> str:
    rows = record["T"]
    payload = "".join(f"{int(str(row), 16):08x}" for row in rows).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--frontiers", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    definitive: set[str] = set()
    seen_results: set[str] = set()
    # Reconstruct status sets from the compact duplicate/unresolved sections
    # plus the result files themselves.  Reading the files avoids depending on
    # incidental summary details and keeps this selector replayable.
    result_root = Path(audit["source"])
    for file_name in audit["result_files"]:
        with (result_root / file_name).open(encoding="utf-8-sig") as stream:
            for raw in stream:
                if not raw.strip():
                    continue
                record = json.loads(raw)
                digest = str(record["T_sha256"]).lower()
                seen_results.add(digest)
                if str(record.get("status", "")).lower() in {"sat", "unsat"}:
                    definitive.add(digest)

    chosen: dict[str, dict] = {}
    provenance: dict[str, dict] = {}
    for frontier in args.frontiers:
        with frontier.open(encoding="utf-8-sig") as stream:
            for line_number, raw in enumerate(stream, 1):
                if not raw.strip():
                    continue
                record = json.loads(raw)
                digest = digest_t(record)
                if digest in definitive or digest in chosen:
                    continue
                copied = dict(record)
                copied["pending_origin"] = (
                    "retry_unknown" if digest in seen_results else "never_solved"
                )
                copied["pending_source_file"] = str(frontier.resolve())
                copied["pending_source_line"] = line_number
                chosen[digest] = copied
                provenance[digest] = {
                    "origin": copied["pending_origin"],
                    "source_file": str(frontier.resolve()),
                    "source_line": line_number,
                    "frontier_source_line": record.get("frontier_source_line"),
                    "heavy_or_lower_bound": record.get("heavy_or_lower_bound"),
                    "target_or": record.get("target_or"),
                    "cover_lower": (record.get("cover") or {}).get("lower"),
                    "structural_weight": (record.get("structural") or {}).get("weight"),
                }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        for digest, record in chosen.items():
            stream.write(json.dumps(record, separators=(",", ":")) + "\n")
    manifest = {
        "definitive_T_before": len(definitive),
        "seen_result_T_before": len(seen_results),
        "pending_count": len(chosen),
        "origins": {
            origin: sum(item["origin"] == origin for item in provenance.values())
            for origin in ("retry_unknown", "never_solved")
        },
        "pending": provenance,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: manifest[key] for key in (
        "definitive_T_before", "seen_result_T_before", "pending_count", "origins"
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
