#!/usr/bin/env python3
"""RETRACTED: run Espresso only on a non-authoritative local sample care set.

The server regenerates random 32-bit seeds.  See ``RETRACTED.md`` before using
any output from this script.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent / "pyproject.toml").exists())
DEFAULT_ESPRESSO = (
    ROOT
    / ".research"
    / "rng_42state_direct"
    / "sample_nonlinear"
    / "agent_care"
    / "espresso-src"
    / "bin"
    / "espresso.exe"
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def probe(executable: Path, pla: Path, timeout_seconds: int) -> dict[str, object]:
    command = [str(executable), "-efast", "-s", "-x", str(pla)]
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        output = completed.stdout
        status = "completed" if completed.returncode == 0 else "failed"
        returncode: int | None = completed.returncode
    except subprocess.TimeoutExpired as error:
        partial = error.stdout or ""
        output = partial.decode("utf-8", errors="replace") if isinstance(partial, bytes) else partial
        status = "timeout"
        returncode = None

    match = re.search(
        r"ESPRESSO\s+Time was ([0-9.]+) sec, cost is "
        r"c=(\d+)\((\d+)\) in=(\d+) out=(\d+) tot=(\d+)",
        output,
    )
    parsed = None
    if match:
        parsed = {
            "seconds": float(match.group(1)),
            "cubes": int(match.group(2)),
            "sparse_cubes": int(match.group(3)),
            "input_literals": int(match.group(4)),
            "output_literals": int(match.group(5)),
            "total_cost": int(match.group(6)),
        }
    return {
        "pla": str(pla.relative_to(ROOT)),
        "pla_sha256": digest(pla),
        "timeout_seconds": timeout_seconds,
        "status": status,
        "returncode": returncode,
        "heuristic_cost": parsed,
        "decisive_output_lines": [
            line
            for line in output.splitlines()
            if "PLA is " in line or "ESPRESSO" in line or "cost is" in line
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--espresso", type=Path, default=DEFAULT_ESPRESSO)
    parser.add_argument("--output", type=Path, default=HERE / "espresso_audit.json")
    parser.add_argument("--quick-timeout", type=int, default=15)
    args = parser.parse_args()

    if not args.espresso.is_file():
        raise FileNotFoundError(args.espresso)
    experiments = [
        probe(args.espresso, HERE / "counter_output_v0_care.pla", args.quick_timeout),
        probe(args.espresso, HERE / "deleted_state_q17_care.pla", args.quick_timeout),
        probe(args.espresso, HERE / "counter_output_care.pla", args.quick_timeout),
    ]
    result = {
        "schema": 1,
        "tool": {
            "path": str(args.espresso),
            "sha256": digest(args.espresso),
            "command": "espresso -efast -s -x <pla>",
        },
        "experiments": experiments,
        "interpretation": (
            "A completed Espresso result is a heuristic SOP upper bound, not a lower "
            "bound. A timeout is only a bounded tool result. Neither may be reported "
            "as UNSAT."
        ),
    }
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
