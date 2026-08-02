"""Stream-verify a fast BFS JSONL and retain only label-structural survivors.

The verifier keeps compact 128-byte T encodings and 64-bit hashes for
deduplication.  It never imports save-writing code and never materializes the
JSONL as Python objects.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys
import time


BITS = 32
MASK64 = (1 << 64) - 1
LOG_PATTERN = re.compile(
    r"^depth=(\d+) new=(\d+) total=(\d+) low_xor=(\d+) emitted=(\d+)$"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rows(record: dict[str, object], key: str) -> tuple[int, ...]:
    values = record.get(key)
    if not isinstance(values, list) or len(values) != BITS:
        raise ValueError(f"{key} must contain 32 rows")
    result = tuple(int(str(value), 16) for value in values)
    if any(not 0 <= value <= 0xFFFFFFFF for value in result):
        raise ValueError(f"{key} row outside U32")
    return result


def mix64(value: int) -> int:
    value ^= value >> 30
    value = (value * 0xBF58476D1CE4E5B9) & MASK64
    value ^= value >> 27
    value = (value * 0x94D049BB133111EB) & MASK64
    return (value ^ (value >> 31)) & MASK64


def state_hash(matrix: tuple[int, ...]) -> int:
    value = 0x9E3779B97F4A7C15
    for row in matrix:
        value = mix64(value ^ row)
    return value


def structural_failure(T: tuple[int, ...], B: tuple[int, ...]) -> str | None:
    exact: dict[int, int] = {}
    for target, steady in zip(T, B):
        weight = steady.bit_count()
        if weight == 1:
            if target.bit_count() != 1:
                return "direct_target_not_unit"
        elif weight == 2:
            if target.bit_count() > 2:
                return "pair_exact_target_invalid"
            previous = exact.setdefault(steady, target)
            if previous != target:
                return "pair_exact_label_conflict"
    return None


def parse_log(path: Path) -> list[dict[str, int]]:
    markers: list[dict[str, int]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        match = LOG_PATTERN.fullmatch(raw)
        if match is None:
            raise ValueError(f"{path}:{line_number}: malformed completion marker")
        depth, new, total, low_xor, emitted = map(int, match.groups())
        markers.append(
            {
                "depth": depth,
                "new": new,
                "total": total,
                "low_xor": low_xor,
                "emitted": emitted,
            }
        )
    if [item["depth"] for item in markers] != list(range(1, 7)):
        raise ValueError("completion log does not contain exactly depths 1..6")
    previous_total = 1
    previous_emitted = 1
    for marker in markers:
        if marker["total"] != previous_total + marker["new"]:
            raise ValueError(f"depth {marker['depth']} total/new mismatch")
        if marker["emitted"] != previous_emitted + marker["low_xor"]:
            raise ValueError(f"depth {marker['depth']} emitted/low_xor mismatch")
        previous_total = marker["total"]
        previous_emitted = marker["emitted"]
    return markers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--survivors", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    init = load_module(
        "rng_or_verify_init", root / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    cover_module = load_module(
        "rng_or_verify_cover", root / ".research/rng_joint_search_resume/search.py"
    )

    markers = parse_log(args.log)
    with args.input.open("rb") as stream:
        stream.seek(-1, 2)
        terminal_lf = stream.read(1) == b"\n"
    if not terminal_lf:
        raise ValueError("JSONL does not end with LF")

    started = time.perf_counter()
    with args.input.open("rb") as source_bytes:
        source_sha256 = hashlib.file_digest(source_bytes, "sha256").hexdigest()
    depth_counts: Counter[int] = Counter()
    xor_counts: Counter[int] = Counter()
    depth_xor_counts: Counter[tuple[int, int]] = Counter()
    rejection_counts: Counter[str] = Counter()
    survivor_counts: Counter[int] = Counter()
    seen_hashes: set[int] = set()
    seen_matrices: set[bytes] = set()
    identity_failures = 0
    metric_failures = 0
    hash_failures = 0
    duplicate_hashes = 0
    duplicate_matrices = 0
    hash_collisions = 0
    line_count = 0
    previous_depth = -1

    temporary = args.survivors.with_suffix(args.survivors.suffix + ".tmp")
    temporary.parent.mkdir(parents=True, exist_ok=True)
    with args.input.open(encoding="utf-8-sig") as source, temporary.open(
        "w", encoding="utf-8", newline="\n"
    ) as survivors:
        for line_count, line in enumerate(source, 1):
            record = json.loads(line)
            depth = int(record["step"])
            if not 0 <= depth <= 6 or depth < previous_depth:
                raise ValueError(f"line {line_count}: invalid/nonmonotonic depth {depth}")
            previous_depth = depth
            T, B, C = (rows(record, key) for key in ("T", "B", "C"))

            packed = struct.pack("<32I", *T)
            claimed_hash = int(str(record["hash"]), 16)
            computed_hash = state_hash(T)
            if computed_hash != claimed_hash:
                hash_failures += 1
            if claimed_hash in seen_hashes:
                duplicate_hashes += 1
                if packed not in seen_matrices:
                    hash_collisions += 1
            if packed in seen_matrices:
                duplicate_matrices += 1
            seen_hashes.add(claimed_hash)
            seen_matrices.add(packed)

            if (
                init.compose(C, T) != init.A
                or init.compose(T, C) != B
                or max(row.bit_count() for row in (*T, *B, *C)) > 4
                or any(row == 0 for row in (*T, *B, *C))
            ):
                identity_failures += 1

            cover = cover_module.depth_two_cost((*B, *C))
            reported = record["cover"]
            required_pairs = len({row for row in (*B, *C) if row.bit_count() == 2})
            finals = len({row for row in (*B, *C) if row.bit_count() in (3, 4)})
            if (
                cover.greedy_upper_bound != int(reported["greedy_xor"])
                or cover.lower_bound != int(reported["lower"])
                or required_pairs != int(reported["required_pairs"])
                or finals != int(reported["finals"])
            ):
                metric_failures += 1

            xor_count = int(reported["greedy_xor"])
            depth_counts[depth] += 1
            xor_counts[xor_count] += 1
            depth_xor_counts[(depth, xor_count)] += 1
            if 61 <= xor_count <= 63:
                failure = structural_failure(T, B)
                if failure is None:
                    survivor_counts[xor_count] += 1
                    survivors.write(line if line.endswith("\n") else line + "\n")
                else:
                    rejection_counts[failure] += 1

            if not line_count % 5000:
                print(f"verified records={line_count}", flush=True)

    temporary.replace(args.survivors)
    with args.survivors.open("rb") as survivor_bytes:
        survivor_sha256 = hashlib.file_digest(survivor_bytes, "sha256").hexdigest()

    for marker in markers:
        depth = marker["depth"]
        if depth_counts[depth] != marker["low_xor"]:
            raise ValueError(f"depth {depth} JSON/log count mismatch")
        if sum(depth_counts[index] for index in range(depth + 1)) != marker["emitted"]:
            raise ValueError(f"depth {depth} cumulative emitted mismatch")
    if depth_counts[0] != 1 or line_count != markers[-1]["emitted"]:
        raise ValueError("origin/final record count mismatch")

    status = "verified" if not any(
        (
            identity_failures,
            metric_failures,
            hash_failures,
            duplicate_hashes,
            duplicate_matrices,
            hash_collisions,
        )
    ) else "failed"
    document = {
        "status": status,
        "input": str(args.input),
        "input_size_bytes": args.input.stat().st_size,
        "input_sha256": source_sha256,
        "terminal_lf": terminal_lf,
        "completion_markers": markers,
        "record_count": line_count,
        "unique_claimed_hash_count": len(seen_hashes),
        "unique_full_T_count": len(seen_matrices),
        "depth_counts": {str(key): value for key, value in sorted(depth_counts.items())},
        "greedy_xor_counts": {str(key): value for key, value in sorted(xor_counts.items())},
        "depth_greedy_xor_counts": {
            f"{depth}:{xor_count}": count
            for (depth, xor_count), count in sorted(depth_xor_counts.items())
        },
        "identity_or_structural_failure_count": identity_failures,
        "cover_metric_failure_count": metric_failures,
        "hash_failure_count": hash_failures,
        "duplicate_claimed_hash_count": duplicate_hashes,
        "duplicate_full_T_count": duplicate_matrices,
        "hash_collision_count": hash_collisions,
        "x61_x63_structural_rejection_counts": dict(sorted(rejection_counts.items())),
        "x61_x63_survivor_counts": {
            str(key): value for key, value in sorted(survivor_counts.items())
        },
        "survivor_path": str(args.survivors),
        "survivor_size_bytes": args.survivors.stat().st_size,
        "survivor_sha256": survivor_sha256,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(document, indent=2))
    return 0 if status == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
