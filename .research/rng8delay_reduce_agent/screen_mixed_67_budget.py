"""Decision-only screen for a <=279-gate 67-cycle RNG data plane.

This wraps the independently checked mixed native/Switch encoding and turns
its weighted objective into one hard pseudo-Boolean bound.  It never builds a
save, starts the game, or reads the live save.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def weighted_terms(encoding) -> tuple[list[int], list[int]]:
    terms: dict[int, int] = {}
    for category in encoding.cost_terms.values():
        for variable, weight in category:
            terms[variable] = terms.get(variable, 0) + weight
    return list(terms), [terms[variable] for variable in terms]


def solve_record(exact, dual, init, record: dict[str, object], budget: int, solver: str):
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver

    T = exact.matrix(record, "T")
    B = exact.matrix(record, "B")
    C = exact.matrix(record, "C")
    encoding = exact.build_encoding(dual, init, T, B, C)
    literals, weights = weighted_terms(encoding)
    # The bundled environment does not require pypblib.  Expand each weighted
    # objective literal into equivalent unit-cost copies, then use PySAT's
    # built-in sequential counter over those copies.
    copies: list[int] = []
    equivalences: list[list[int]] = []
    for variable, weight in zip(literals, weights, strict=True):
        for ordinal in range(weight):
            copy = encoding.pool.id(("cost_copy", variable, ordinal))
            copies.append(copy)
            equivalences.append([-copy, variable])
            equivalences.append([-variable, copy])
    bound = CardEnc.atmost(
        lits=copies,
        bound=budget,
        vpool=encoding.pool,
        encoding=EncType.seqcounter,
    )
    started = time.perf_counter()
    with exact.MemoryMonitor() as monitor:
        with Solver(name=solver, bootstrap_with=encoding.wcnf.hard) as sat:
            sat.append_formula(equivalences)
            sat.append_formula(bound.clauses)
            feasible = sat.solve()
            model = sat.get_model() if feasible else None
    elapsed = time.perf_counter() - started
    result: dict[str, object] = {
        "status": "sat" if feasible else "unsat",
        "budget": budget,
        "variable_count": encoding.pool.top,
        "hard_clause_count": (
            len(encoding.wcnf.hard) + len(equivalences) + len(bound.clauses)
        ),
        "weight_copy_count": len(copies),
        "equivalence_clause_count": len(equivalences),
        "pb_clause_count": len(bound.clauses),
        "elapsed_seconds": round(elapsed, 6),
        "peak_working_set_mb": round(monitor.peak / (1024 * 1024), 3),
    }
    if model is not None:
        positive = {literal for literal in model if literal > 0}
        logic = sum(
            weight for variable, weight in zip(literals, weights, strict=True)
            if variable in positive
        )
        result["logic_cost"] = logic
        result["certificate"] = exact.decode_and_verify(
            init, T, B, C, encoding, model, logic
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--budget", type=int, default=279)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int)
    parser.add_argument("--stop-on-sat", action="store_true")
    args = parser.parse_args()

    source = args.source if args.source.is_absolute() else ROOT / args.source
    output = args.output if args.output.is_absolute() else ROOT / args.output
    exact = load_module("rng_exact_mixed_67", HERE / "exact_mixed_67.py")
    dual = exact.load_module(
        "rng_67_decision_dual",
        ROOT / "examples/rng/research/archive/rng_cost387/search_basis_dualmode.py",
    )
    init = exact.load_module(
        "rng_67_decision_init",
        ROOT / "examples/rng/research/archive/rng_init_reuse/verify_init_reuse.py",
    )

    all_records = [
        json.loads(line)
        for line in source.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    last = len(all_records) if args.last is None else min(args.last, len(all_records))
    selected = all_records[args.first - 1:last]
    results = []
    started = time.perf_counter()
    for offset, record in enumerate(selected, args.first):
        result = solve_record(exact, dual, init, record, args.budget, args.solver)
        result["source_line"] = offset
        result["source_hash"] = record.get("hash")
        result["lower"] = record.get("lower")
        results.append(result)
        print(
            f"line={offset} status={result['status']} "
            f"seconds={result['elapsed_seconds']} rss={result['peak_working_set_mb']}MB",
            flush=True,
        )
        if args.stop_on_sat and result["status"] == "sat":
            break

    document = {
        "schema": 1,
        "model": "67-cycle depth-two mixed native/Switch decision screen",
        "source": str(source),
        "source_sha256": sha256(source.read_bytes()).hexdigest(),
        "range": [args.first, args.first + len(results) - 1],
        "candidate_count": len(results),
        "budget": args.budget,
        "target": [172 + args.budget, 8, 67],
        "terminal_split_enabled": False,
        "solver": args.solver,
        "status": "sat" if any(r["status"] == "sat" for r in results) else "unsat",
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "results": results,
    }
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in document.items() if key != "results"}, indent=2))
    return 0 if document["status"] == "sat" else 1


if __name__ == "__main__":
    raise SystemExit(main())
