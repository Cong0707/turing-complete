"""CaDiCaL CNF backend for ``search_phase_friendly.py``.

This encodes the same finite facility-selection model without Z3 pseudo-
Boolean arithmetic.  It exists both for speed and for an independently
checkable clause fingerprint.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def load_base(path: Path):
    spec = importlib.util.spec_from_file_location("rng_deep_phase_base", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def exactly_one(cnf: CNF, literals: list[int]) -> None:
    if not literals:
        cnf.append([])
        return
    cnf.append(literals)
    for left in range(len(literals)):
        for right in range(left + 1, len(literals)):
            cnf.append([-literals[left], -literals[right]])


def at_most_one(cnf: CNF, literals: list[int]) -> None:
    for left in range(len(literals)):
        for right in range(left + 1, len(literals)):
            cnf.append([-literals[left], -literals[right]])


def clause_fingerprint(cnf: CNF) -> str:
    digest = hashlib.sha256()
    for clause in cnf.clauses:
        digest.update(" ".join(str(value) for value in clause).encode("ascii"))
        digest.update(b" 0\n")
    return digest.hexdigest()


def solve(base, *, intermediate_limit: int, solver_name: str) -> dict[str, object]:
    output_options: dict[int, tuple[tuple[int, int], ...]] = {}
    for row in base.A:
        weight = row.bit_count()
        if weight <= 4:
            continue
        output_options[row] = (
            base.heavy_output_options(row)
            if weight == 7
            else base.local_output_options(row)
        )

    depth_two_masks = set(base.LOW_OUTPUTS)
    for options in output_options.values():
        for left, right in options:
            if left.bit_count() in (3, 4):
                depth_two_masks.add(left)
            if right.bit_count() in (3, 4):
                depth_two_masks.add(right)
    depth_two_partitions = {
        mask: base.shallow_partitions(mask) for mask in sorted(depth_two_masks)
    }

    pool = IDPool()
    cnf = CNF()
    pair_used = {pair: pool.id(f"p_{pair:08x}") for pair in sorted(base.PAIRS)}
    residual_used = {
        mask: pool.id(f"r_{mask:08x}")
        for mask in sorted(depth_two_masks)
        if mask not in base.LOW_OUTPUTS
    }
    depth_choices = {
        (mask, index): pool.id(f"d_{mask:08x}_{index}")
        for mask, options in depth_two_partitions.items()
        for index in range(len(options))
    }
    output_choices = {
        (row, index): pool.id(f"o_{row:08x}_{index}")
        for row, options in output_options.items()
        for index in range(len(options))
    }

    pair_consumers: dict[int, list[int]] = defaultdict(list)
    residual_consumers: dict[int, list[int]] = defaultdict(list)

    for mask, options in depth_two_partitions.items():
        choices = [depth_choices[(mask, index)] for index in range(len(options))]
        if mask in base.LOW_OUTPUTS:
            exactly_one(cnf, choices)
        else:
            used = residual_used[mask]
            at_most_one(cnf, choices)
            cnf.append([-used, *choices])
            for choice in choices:
                cnf.append([-choice, used])
        for index, (left, right) in enumerate(options):
            choice = depth_choices[(mask, index)]
            for signal in (left, right):
                if signal in base.PAIRS:
                    cnf.append([-choice, pair_used[signal]])
                    pair_consumers[signal].append(choice)

    for row, options in output_options.items():
        choices = [output_choices[(row, index)] for index in range(len(options))]
        exactly_one(cnf, choices)
        for index, (left, right) in enumerate(options):
            choice = output_choices[(row, index)]
            for signal in (left, right):
                if signal in base.PAIRS:
                    cnf.append([-choice, pair_used[signal]])
                    pair_consumers[signal].append(choice)
                elif signal in residual_used:
                    cnf.append([-choice, residual_used[signal]])
                    residual_consumers[signal].append(choice)

    for pair, used in pair_used.items():
        consumers = pair_consumers.get(pair, [])
        cnf.append([-used, *consumers])
    for mask, used in residual_used.items():
        consumers = residual_consumers.get(mask, [])
        cnf.append([-used, *consumers])

    counted = [*pair_used.values(), *residual_used.values()]
    bound = CardEnc.atmost(
        lits=counted,
        bound=intermediate_limit,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    cnf.extend(bound.clauses)

    fingerprint = clause_fingerprint(cnf)
    started = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        elapsed = time.perf_counter() - started
        model = frozenset(value for value in (solver.get_model() or ()) if value > 0)
        stats = solver.accum_stats()

    result: dict[str, object] = {
        "schema": 1,
        "model": "natural-state phase-friendly depth-three XOR DAG",
        "backend": solver_name,
        "status": "sat" if sat else "unsat",
        "intermediate_limit": intermediate_limit,
        "elapsed_seconds": round(elapsed, 6),
        "variable_count": pool.top,
        "clause_count": len(cnf.clauses),
        "clause_sha256": fingerprint,
        "solver_stats": stats,
        "matrix_sha256": hashlib.sha256(
            b"".join(row.to_bytes(4, "little") for row in base.A)
        ).hexdigest(),
        "candidate_counts": {
            "pairs": len(pair_used),
            "depth_two": len(depth_two_masks),
            "nonlow_outputs": len(output_options),
            "output_options": sum(len(options) for options in output_options.values()),
        },
    }
    if not sat:
        return result

    chosen_pairs = tuple(sorted(pair for pair, var in pair_used.items() if var in model))
    chosen_residuals = tuple(sorted(mask for mask, var in residual_used.items() if var in model))
    decompositions = {}
    for mask, options in depth_two_partitions.items():
        if mask not in base.LOW_OUTPUTS and mask not in chosen_residuals:
            continue
        indexes = [index for index in range(len(options)) if depth_choices[(mask, index)] in model]
        if len(indexes) != 1:
            raise AssertionError(f"depth decomposition is not one-hot: {mask:08x}")
        decompositions[f"{mask:08x}"] = [f"{value:08x}" for value in options[indexes[0]]]
    outputs = {}
    for row, options in output_options.items():
        indexes = [index for index in range(len(options)) if output_choices[(row, index)] in model]
        if len(indexes) != 1:
            raise AssertionError(f"output decomposition is not one-hot: {row:08x}")
        outputs[f"{row:08x}"] = [f"{value:08x}" for value in options[indexes[0]]]

    xor_count = 32 + len(chosen_pairs) + len(chosen_residuals)
    result.update(
        {
            "selected_pair_count": len(chosen_pairs),
            "selected_residual_count": len(chosen_residuals),
            "intermediate_count": len(chosen_pairs) + len(chosen_residuals),
            "xor_count": xor_count,
            "selected_pairs": [f"{value:08x}" for value in chosen_pairs],
            "depth_two_decompositions": decompositions,
            "output_decompositions": outputs,
            "low_outputs": [f"{value:08x}" for value in sorted(base.LOW_OUTPUTS)],
            "heavy_outputs": [f"{value:08x}" for value in sorted(base.HEAVY_OUTPUTS)],
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--intermediate-limit", type=int, default=29)
    parser.add_argument("--solver", default="cadical195")
    args = parser.parse_args()
    base = load_base(Path(__file__).with_name("search_phase_friendly.py"))
    result = solve(
        base,
        intermediate_limit=args.intermediate_limit,
        solver_name=args.solver,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: value
                for key, value in result.items()
                if key
                not in {
                    "selected_pairs",
                    "depth_two_decompositions",
                    "output_decompositions",
                }
            },
            indent=2,
        )
    )
    return 0 if result["status"] == "sat" else 2


if __name__ == "__main__":
    raise SystemExit(main())
