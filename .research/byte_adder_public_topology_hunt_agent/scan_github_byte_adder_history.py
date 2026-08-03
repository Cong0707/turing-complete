"""Scan public GitHub Byte Adder file history without invoking Git.

Commit-list responses are retained verbatim.  Historical circuit payloads are
hashed and inspected in memory; only exact target-score hits are saved as
artifacts.  This keeps source provenance reproducible without cloning repos or
mixing unlicensed material into candidate circuits.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from tc_save_lab.snappy import decompress_raw


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_OUTPUT_ROOT = HERE / "github-history"
DEFAULT_REPORT = HERE / "github-byte-adder-history-scan.json"
USER_AGENT = "byte-adder-public-history-audit/1.0"
MAX_RESPONSE = 8 * 1024 * 1024
TARGET_SCORES = {(103, 5), (91, 6), (88, 6), (79, 7), (74, 8), (154, 4)}


SOURCES = (
    {
        "repository": "Fatalist0001/Turing-complete-full-workflow-save",
        "license": "NOASSERTION",
        "paths": ("schematics/byte_adder/Default/circuit.data",),
    },
    {
        "repository": "chastitywhiterose/Turing-Complete",
        "license": "GPL-3.0",
        "paths": ("savedata/Turing Complete/schematics/byte_adder/Default/circuit.data",),
    },
    {
        "repository": "MizuchiKun/TuringComplete",
        "license": "NOASSERTION",
        "paths": (
            "byte_adder/Default/circuit.data",
            "byte_adder/FasterTBD/circuit.data",
            "byte_adder/old_Default/circuit.data",
        ),
    },
    {
        "repository": "CoccaGuo/Turing-Complete-Saves",
        "license": "NOASSERTION",
        "paths": ("extracted/Turing Complete/schematics/byte_adder/Default/circuit.data",),
    },
    {
        "repository": "GeniusRyder/My-Turing-Complete-Save",
        "license": "NOASSERTION",
        "paths": ("Turing Complete/schematics/byte_adder/Default/circuit.data",),
    },
    {
        "repository": "magnitood/Turing-Complete",
        "license": "NOASSERTION",
        "paths": ("schematics/byte_adder/Default/circuit.data",),
    },
    {
        "repository": "zoickx/turing-complete",
        "license": "CC0-1.0",
        "paths": (
            "schematics/byte_adder/Default/circuit.data",
            "schematics/byte_adder/Low-Delay/circuit.data",
            "schematics/byte_adder/Low-Delay-parallel/circuit.data",
        ),
    },
    {
        "repository": "yuioto/Turing-Complete-saves",
        "license": "NOASSERTION",
        "paths": (
            "schematics/byte_adder/Default/circuit.data",
            "schematics/byte_adder/try2/circuit.data",
        ),
    },
)


def fetch(url: str, accept: str) -> tuple[int, bytes]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    with urlopen(request, timeout=25.0) as response:
        payload = response.read(MAX_RESPONSE + 1)
        if len(payload) > MAX_RESPONSE:
            raise ValueError(f"response exceeds {MAX_RESPONSE} bytes")
        return response.status, payload


def circuit_header(payload: bytes) -> tuple[int, int, int]:
    if not payload:
        raise ValueError("empty circuit payload")
    raw = decompress_raw(payload[1:])
    if len(raw) < 28:
        raise ValueError("decompressed circuit is too short")
    gate = struct.unpack_from("<q", raw, 12)[0]
    delay = struct.unpack_from("<q", raw, 20)[0]
    return payload[0], gate, delay


def safe_slug(value: str) -> str:
    return "".join(character if character.isalnum() or character in "._-" else "_" for character in value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--repository",
        action="append",
        help="limit the scan to one repository; repeat for multiple repositories",
    )
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    calls: list[dict[str, object]] = []
    records: list[dict[str, object]] = []
    seen_payloads: set[tuple[str, str]] = set()

    for source in SOURCES:
        repository = str(source["repository"])
        if args.repository and repository not in set(args.repository):
            continue
        for source_path in source["paths"]:
            api_url = (
                f"https://api.github.com/repos/{repository}/commits"
                f"?per_page=100&path={quote(str(source_path), safe='')}"
            )
            call: dict[str, object] = {
                "repository": repository,
                "path": source_path,
                "url": api_url,
            }
            try:
                status, body = fetch(api_url, "application/vnd.github+json")
                response_path = args.output_root / f"{safe_slug(repository)}--{sha256(str(source_path).encode()).hexdigest()[:12]}.json"
                response_path.write_bytes(body)
                commits = json.loads(body.decode("utf-8"))
                call.update(
                    {
                        "status": status,
                        "response_path": response_path.resolve().relative_to(ROOT).as_posix(),
                        "response_bytes": len(body),
                        "response_sha256": sha256(body).hexdigest(),
                        "commit_count": len(commits),
                    }
                )
                for commit in commits:
                    commit_sha = str(commit["sha"])
                    raw_url = (
                        f"https://raw.githubusercontent.com/{repository}/{commit_sha}/"
                        f"{quote(str(source_path), safe='/')}"
                    )
                    try:
                        raw_status, payload = fetch(raw_url, "application/octet-stream")
                        digest = sha256(payload).hexdigest()
                        duplicate = (repository, digest) in seen_payloads
                        seen_payloads.add((repository, digest))
                        version, gate, delay = circuit_header(payload)
                        record: dict[str, object] = {
                            "repository": repository,
                            "license": source["license"],
                            "path": source_path,
                            "commit_sha": commit_sha,
                            "commit_url": commit.get("html_url"),
                            "commit_date": commit.get("commit", {}).get("committer", {}).get("date"),
                            "raw_url": raw_url,
                            "raw_status": raw_status,
                            "bytes": len(payload),
                            "sha256": digest,
                            "duplicate_payload_in_repository": duplicate,
                            "format_version": version,
                            "declared_gate": gate,
                            "declared_delay": delay,
                            "declared_energy": gate * delay,
                            "target_score_match": (gate, delay) in TARGET_SCORES,
                        }
                        if record["target_score_match"]:
                            hit_path = (
                                args.output_root
                                / "hits"
                                / safe_slug(repository)
                                / commit_sha
                                / safe_slug(str(source_path))
                            )
                            hit_path.parent.mkdir(parents=True, exist_ok=True)
                            hit_path.write_bytes(payload)
                            record["artifact_path"] = hit_path.resolve().relative_to(ROOT).as_posix()
                        records.append(record)
                    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
                        records.append(
                            {
                                "repository": repository,
                                "license": source["license"],
                                "path": source_path,
                                "commit_sha": commit_sha,
                                "raw_url": raw_url,
                                "error": f"{type(exc).__name__}: {exc}",
                            }
                        )
                    time.sleep(0.05)
            except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
                call["error"] = f"{type(exc).__name__}: {exc}"
            calls.append(call)
            time.sleep(0.1)

    result = {
        "schema": "turing-complete-public-github-byte-adder-history-v1",
        "scope": "public GitHub commit lists and raw historical Byte Adder files; no git invocation",
        "target_scores": [list(score) for score in sorted(TARGET_SCORES)],
        "calls": calls,
        "record_count": len(records),
        "unique_payload_count": len(seen_payloads),
        "target_hits": [record for record in records if record.get("target_score_match")],
        "records": records,
    }
    encoded = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    args.report.write_bytes(encoded)
    print(
        json.dumps(
            {
                "report": args.report.resolve().relative_to(ROOT).as_posix(),
                "bytes": len(encoded),
                "sha256": sha256(encoded).hexdigest(),
                "api_calls": len(calls),
                "records": len(records),
                "unique_payloads": len(seen_payloads),
                "target_hits": len(result["target_hits"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
