"""Remove T matrices already covered by an exact-scope manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest_t(record: dict) -> str:
    payload = "".join(
        f"{int(str(row), 16):08x}" for row in record["T"]
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--known-results", type=Path, nargs="*", default=[])
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    known = set(manifest["scopes"][str(args.scope)]["proof"])
    for result_path in args.known_results:
        with result_path.open(encoding="utf-8-sig") as stream:
            for raw in stream:
                if not raw.strip():
                    continue
                result = json.loads(raw)
                if str(result.get("status", "")).lower() in {"sat", "unsat"}:
                    known.add(str(result["T_sha256"]).lower())
    unique: dict[str, dict] = {}
    input_records = 0
    with args.input.open(encoding="utf-8-sig") as stream:
        for raw in stream:
            if not raw.strip():
                continue
            input_records += 1
            record = json.loads(raw)
            digest = digest_t(record)
            if digest not in known:
                unique.setdefault(digest, record)

    records = sorted(
        unique.items(),
        key=lambda item: (
            int(item[1].get("heavy_or_lower_bound", 1 << 30)),
            int((item[1].get("cover") or {}).get("lower", 1 << 30)),
            int((item[1].get("structural") or {}).get("weight", 1 << 30)),
            item[0],
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        for _digest, record in records:
            stream.write(json.dumps(record, separators=(",", ":")) + "\n")
    print(json.dumps({
        "input_records": input_records,
        "known_T": len(known),
        "uncovered_unique_T": len(records),
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
