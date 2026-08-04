#!/usr/bin/env python3
"""Run the reviewed tail729 worker while fingerprinting its exact CNF stream."""

from __future__ import annotations

import argparse
from array import array
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import struct
import sys
from typing import Any, Iterable

from pysat.solvers import Solver as PySATSolver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER_PATH = (
    ROOT
    / ".research/byte_adder_phase_shortcut_restart/"
    "exact_tail729_with_s34_family1_two_phase_free.py"
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


worker = _load_module("tail729_high30_formula_base", WORKER_PATH)
LAST_FINGERPRINT: dict[str, Any] | None = None


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def fingerprint_cnf(formula: Any) -> dict[str, Any]:
    clauses: Iterable[Iterable[int]] = getattr(formula, "clauses", formula)
    clause_list = clauses if isinstance(clauses, list) else list(clauses)
    nv = int(getattr(formula, "nv", 0))
    atmosts = getattr(formula, "atmosts", ())
    if atmosts:
        raise RuntimeError("native cardinality constraints are outside CNF fingerprint v1")
    fingerprint = sha256(b"tail729-high30-cnf-literal-stream-v1\0")
    fingerprint.update(struct.pack("<QQ", nv, len(clause_list)))
    literal_count = 0
    max_variable = 0
    for clause_raw in clause_list:
        clause = [int(literal) for literal in clause_raw]
        fingerprint.update(struct.pack("<I", len(clause)))
        literals = array("i", clause)
        if literals.itemsize != 4:
            raise RuntimeError("platform C int is not 32 bits")
        if sys.byteorder != "little":
            literals.byteswap()
        fingerprint.update(literals.tobytes())
        literal_count += len(clause)
        if clause:
            max_variable = max(max_variable, *(abs(literal) for literal in clause))
    if nv:
        if max_variable > nv:
            raise RuntimeError("CNF literal exceeds declared variable count")
    else:
        nv = max_variable
    return {
        "schema": "tail729-high30-cnf-fingerprint-v1",
        "sha256": fingerprint.hexdigest(),
        "variables": nv,
        "clauses": len(clause_list),
        "literals": literal_count,
        "clause_order_preserved": True,
        "literal_order_preserved": True,
        "encoding": "header-u64le; clause-length-u32le; literals-i32le",
    }


class FingerprintingSolver:
    def __init__(
        self,
        *,
        name: str,
        bootstrap_with: Any,
        formula_only: bool,
        **kwargs: Any,
    ) -> None:
        global LAST_FINGERPRINT
        LAST_FINGERPRINT = fingerprint_cnf(bootstrap_with)
        self.inner = None if formula_only else PySATSolver(
            name=name, bootstrap_with=bootstrap_with, **kwargs
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if self.inner is not None:
            self.inner.delete()
        return False

    def solve(self, *args: Any, **kwargs: Any):
        return None if self.inner is None else self.inner.solve(*args, **kwargs)

    def solve_limited(self, *args: Any, **kwargs: Any):
        return None if self.inner is None else self.inner.solve_limited(*args, **kwargs)

    def get_model(self):
        return None if self.inner is None else self.inner.get_model()

    def interrupt(self) -> None:
        if self.inner is not None:
            self.inner.interrupt()


def solve(args: argparse.Namespace) -> dict[str, Any]:
    global LAST_FINGERPRINT
    LAST_FINGERPRINT = None
    original_solver = worker.base.Solver

    def factory(*, name: str, bootstrap_with: Any, **kwargs: Any):
        return FingerprintingSolver(
            name=name,
            bootstrap_with=bootstrap_with,
            formula_only=args.formula_only,
            **kwargs,
        )

    worker.base.Solver = factory
    try:
        payload = worker.solve(args)
    finally:
        worker.base.Solver = original_solver
    if LAST_FINGERPRINT is None:
        raise RuntimeError("tail worker did not instantiate the fingerprinting solver")
    payload["formula_fingerprint"] = LAST_FINGERPRINT
    payload["formula_worker"] = {
        "path": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
        "sha256": digest(Path(__file__)),
        "base_worker": str(WORKER_PATH.relative_to(ROOT)).replace("\\", "/"),
        "base_worker_sha256": digest(WORKER_PATH),
        "formula_only": args.formula_only,
    }
    return payload


def parser() -> argparse.ArgumentParser:
    result = worker._parser()
    result.add_argument("--formula-only", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.self_check:
        raise ValueError("use the reviewed base worker for --self-check")
    for name in ("gate_bound", "components", "switches"):
        if getattr(args, name) is None:
            raise ValueError(f"--{name.replace('_', '-')} is required")
    if args.output is None:
        raise ValueError("--output is required")
    if args.max_delay != worker.MAX_DELAY or args.xors != 0:
        raise ValueError("formula worker requires D5 and zero XORs")
    expected_gate = args.components + args.switches + 2 * args.xors
    if args.gate_bound != expected_gate:
        raise ValueError("inconsistent component/Switch/gate decomposition")
    args.outputs = ",".join(worker.TAIL_OUTPUTS)
    payload = solve(args)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    summary = {key: value for key, value in payload.items() if key != "network"}
    summary["output"] = str(args.output.resolve())
    summary["sha256"] = sha256(encoded).hexdigest()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.formula_only:
        return 0
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
