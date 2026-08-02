#!/usr/bin/env python3
"""Screen promising low-rank extensions for the persistent-seed RNG model.

The source checkpoint ranks already-proved-UNSAT row sets by solve time.  This
script adds one or more free C rows to those boundary sets, deduplicates the
resulting supersets, and checks the correct persistent model with
``D = T * (A + I)`` and the mixed-arrival Kraft limit of 16.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import itertools
import json
from pathlib import Path
import time
import types


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOLVER_PATH = ROOT / ".research" / "rng_weighted_basis_global" / "solve_persistent_rank3.py"
SOLVER_SOURCE = SOLVER_PATH.read_text(encoding="ascii")
OLD_RANK_GUARD = "if not 1 <= len(free_rows) <= 5:"
if SOLVER_SOURCE.count(OLD_RANK_GUARD) != 1:
    raise RuntimeError("upstream rank guard changed; refusing an unchecked extension")
SOLVER_SOURCE = SOLVER_SOURCE.replace(
    OLD_RANK_GUARD,
    "if not 1 <= len(free_rows) <= 8:",
)
SOLVER = types.ModuleType("persistent_rank_solver_extended")
SOLVER.__file__ = str(SOLVER_PATH)
exec(compile(SOLVER_SOURCE, str(SOLVER_PATH), "exec"), SOLVER.__dict__)


def candidate_rows(
    checkpoint: dict[str, object],
    *,
    parent_limit: int,
    target_rank: int,
) -> list[tuple[int, ...]]:
    slowest = checkpoint.get("slowest")
    if not isinstance(slowest, list) or not slowest:
        records = checkpoint.get("records")
        if not isinstance(records, list) or not records:
            raise ValueError("source checkpoint has no ranked records")
        slowest = sorted(
            records,
            key=lambda record: float(record["solve_seconds"]),
            reverse=True,
        )
    parents: list[tuple[int, ...]] = []
    for record in slowest[:parent_limit]:
        if not isinstance(record, dict) or not isinstance(record.get("rows"), list):
            raise ValueError("malformed slowest record")
        rows = tuple(sorted(int(row) for row in record["rows"]))
        if len(rows) >= target_rank:
            raise ValueError("target rank must exceed every parent rank")
        parents.append(rows)

    candidates: set[tuple[int, ...]] = set()
    for parent in parents:
        remaining = tuple(row for row in range(32) if row not in parent)
        for added in itertools.combinations(remaining, target_rank - len(parent)):
            candidates.add(tuple(sorted((*parent, *added))))
    return sorted(candidates)


def checkpoint_payload(
    *,
    center: Path,
    source_checkpoint: Path,
    parent_limit: int,
    target_rank: int,
    scheduled: int,
    records: list[dict[str, object]],
    winner: dict[str, object] | None,
    started: float,
) -> dict[str, object]:
    return {
        "schema": 1,
        "model": "persistent-seed mixed-Kraft prioritized rank extension",
        "protocol": {
            "next": "B*q + D*seed",
            "output": "C*q + A*seed",
            "D": "T*(A+I)",
        },
        "center": str(center),
        "center_sha256": sha256(center.read_bytes()).hexdigest(),
        "source_checkpoint": str(source_checkpoint),
        "source_checkpoint_sha256": sha256(source_checkpoint.read_bytes()).hexdigest(),
        "support_limit": 16,
        "metric": "mixed-kraft: 4*state_weight + seed_weight",
        "parent_limit": parent_limit,
        "target_rank": target_rank,
        "scheduled": scheduled,
        "processed": len(records),
        "status_counts": dict(sorted(Counter(record["status"] for record in records).items())),
        "slowest": sorted(
            records,
            key=lambda record: float(record["solve_seconds"]),
            reverse=True,
        )[:64],
        "records": records,
        "winner": winner,
        "elapsed_seconds": time.monotonic() - started,
        "complete": winner is not None or len(records) == scheduled,
        "scope_limit": (
            "UNSAT covers only target-rank supersets of the selected slow parent sets; "
            "a SAT support result still needs a shared physical DAG certificate."
        ),
    }


def write_payload(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--center", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--parent-limit", type=int, default=32)
    parser.add_argument("--target-rank", type=int, default=3)
    parser.add_argument("--timeout-seconds", type=int, default=2)
    parser.add_argument("--memory-mb", type=int, default=300)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.checkpoint.read_text(encoding="ascii"))
    candidates = candidate_rows(
        source,
        parent_limit=args.parent_limit,
        target_rank=args.target_rank,
    )
    started = time.monotonic()
    records: list[dict[str, object]] = []
    winner: dict[str, object] | None = None
    for index, rows in enumerate(candidates):
        result = SOLVER.solve(
            args.center,
            rows,
            16,
            args.timeout_seconds,
            args.memory_mb,
            None,
            "qfbv",
            "mixed-kraft",
        )
        record = {
            "index": index,
            "rows": list(rows),
            "status": result["status"],
            "solve_seconds": result["solve_seconds"],
        }
        records.append(record)
        if result["status"] == "sat":
            winner = {"record": record, "solution": result["solution"]}
        if winner is not None or len(records) % 25 == 0:
            write_payload(
                args.output,
                checkpoint_payload(
                    center=args.center,
                    source_checkpoint=args.checkpoint,
                    parent_limit=args.parent_limit,
                    target_rank=args.target_rank,
                    scheduled=len(candidates),
                    records=records,
                    winner=winner,
                    started=started,
                ),
            )
        if winner is not None:
            return 0

    write_payload(
        args.output,
        checkpoint_payload(
            center=args.center,
            source_checkpoint=args.checkpoint,
            parent_limit=args.parent_limit,
            target_rank=args.target_rank,
            scheduled=len(candidates),
            records=records,
            winner=None,
            started=started,
        ),
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
