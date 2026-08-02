"""Run one bounded canonical pair/mode SAT check on an audited candidate."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def parse_rows(values) -> tuple[int, ...]:
    return tuple(int(value, 16) if isinstance(value, str) else int(value) for value in values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--xor", type=int, required=True)
    parser.add_argument("--mode", type=int, required=True)
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--memory-mb", type=int, default=512)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    sat_module = load_module(
        "rng_or_budget_sat", root / ".research/rng_cost387/search_fixed_t_z3.py"
    )
    document = json.loads(args.source.read_text(encoding="utf-8"))
    candidate = document.get("best_candidate", document)
    T, B, C = (parse_rows(candidate[key]) for key in ("T", "B", "C"))
    finals = frozenset(row for row in (*B, *C) if row.bit_count() in (3, 4))
    pair_budget = args.xor - len(finals)
    if pair_budget < 0:
        raise ValueError("XOR budget is below the mandatory final-gate count")

    def fixed_matrices(_source, _matrices_json, _neighbor):
        return T, B, C

    sat_module.load_matrices = fixed_matrices
    status, certificate, stats = sat_module.solve(
        source=Path("unused"),
        matrices_json=Path("in-memory"),
        neighbor=None,
        pair_budget=pair_budget,
        mode_budget=args.mode,
        timeout_ms=args.timeout_ms,
        memory_mb=args.memory_mb,
    )
    result = {
        "status": status,
        "source": str(args.source),
        "requested_xor": args.xor,
        "requested_mode": args.mode,
        "final_count": len(finals),
        **stats,
    }
    if certificate is not None:
        result["certificate"] = certificate
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if status in {"sat", "unsat"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
