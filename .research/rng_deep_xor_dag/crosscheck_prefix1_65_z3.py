"""Independent Z3 cross-check of the prefix-1 65-cycle OR lower bound."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

import z3


EXPECTED_FIRST_NINE = (5, 5, 4, 4, 4, 6, 6, 5, 6)


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def parity(expressions: list[z3.BoolRef]) -> z3.BoolRef:
    if not expressions:
        return z3.BoolVal(False)
    if len(expressions) == 1:
        return expressions[0]
    result = expressions[0]
    for expression in expressions[1:]:
        result = z3.Xor(result, expression)
    return result


def check_target(masks: tuple[int, ...], target: int, bound: int, timeout_ms: int):
    solver = z3.Solver()
    solver.set(timeout=timeout_ms, random_seed=0x65)
    selected = [z3.Bool(f"s_{index}") for index in range(len(masks))]
    for bit in range(64):
        contributors = [selected[index] for index, mask in enumerate(masks) if mask >> bit & 1]
        solver.add(parity(contributors) == z3.BoolVal(bool(target >> bit & 1)))
    solver.add(z3.Sum([z3.If(value, 1, 0) for value in selected]) <= bound)
    started = time.perf_counter()
    status = solver.check()
    elapsed = time.perf_counter() - started
    chosen = []
    if status == z3.sat:
        model = solver.model()
        chosen = [index for index, value in enumerate(selected) if z3.is_true(model.eval(value, model_completion=True))]
    return str(status), round(elapsed, 6), chosen, solver.reason_unknown() if status == z3.unknown else None


def minimize_target(
    masks: tuple[int, ...], target: int, maximum: int, timeout_ms: int
):
    """Find the exact cardinality minimum with monotone SAT checks."""

    checked = {}

    def check(bound: int):
        if bound not in checked:
            checked[bound] = check_target(masks, target, bound, timeout_ms)
        status = checked[bound][0]
        if status == "unknown":
            raise RuntimeError(
                f"Z3 returned unknown at bound {bound}: {checked[bound][3]}"
            )
        return checked[bound]

    if check(maximum)[0] != "sat":
        raise RuntimeError(f"target is not reachable within --max-bound={maximum}")
    low, high = -1, maximum
    while high - low > 1:
        middle = (low + high) // 2
        if check(middle)[0] == "sat":
            high = middle
        else:
            low = middle
    below, at = check(high - 1), check(high)
    if below[0] != "unsat" or at[0] != "sat":
        raise AssertionError("minimum boundary is not UNSAT/SAT")
    return high, below, at


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout-ms", type=int, default=60_000)
    parser.add_argument("--all-seeds", action="store_true")
    parser.add_argument("--max-bound", type=int, default=16)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    base = load("rng_deep_cross_base", here / "audit_cyclic_retime.py")
    joint = load("rng_deep_cross_joint", here / "audit_cyclic_retime_65.py")
    gates, forms, depths, visible, feedback, T = base.build(1)
    sites = joint.enumerate_sites(base, gates, depths, feedback, visible)
    representatives = {}
    for index, site in enumerate(sites):
        representatives.setdefault(site.influence, index)
    masks = tuple(sorted(representatives))

    identity = tuple(1 << bit for bit in range(32))
    A = identity
    for direction, amount in base.STAGES:
        A = base.stage_rows(A, direction, amount)
    TA = joint.compose(T, A)

    records = []
    minima = []
    seed_count = 32 if args.all_seeds else len(EXPECTED_FIRST_NINE)
    for seed in range(seed_count):
        feedback_column = sum(((row >> seed) & 1) << bit for bit, row in enumerate(TA))
        visible_column = sum(((row >> seed) & 1) << bit for bit, row in enumerate(A))
        target = feedback_column | (visible_column << 32)
        if args.all_seeds:
            expected, below, at = minimize_target(
                masks, target, args.max_bound, args.timeout_ms
            )
        else:
            expected = EXPECTED_FIRST_NINE[seed]
            below = check_target(masks, target, expected - 1, args.timeout_ms)
            at = check_target(masks, target, expected, args.timeout_ms)
        if below[0] != "unsat" or at[0] != "sat" or len(at[2]) > expected:
            raise AssertionError(f"minimum cross-check failed for seed {seed}: {below[0]}/{at[0]}")
        actual = 0
        for index in at[2]:
            actual ^= masks[index]
        if actual != target:
            raise AssertionError("Z3 witness replay failed")
        minima.append(expected)
        records.append(
            {
                "seed": seed,
                "target": f"{target:016x}",
                "minimum": expected,
                "below": {"bound": expected - 1, "status": below[0]},
                "at": {
                    "bound": expected,
                    "status": at[0],
                    "influences": [f"{masks[index]:016x}" for index in at[2]],
                },
            }
        )

    payload = {
        "schema": 1,
        "status": "crosschecked-full" if args.all_seeds else "crosschecked",
        "model": "relaxed legal-site 64-bit influence cover",
        "prefix_stage_count": 1,
        "site_count": len(sites),
        "unique_influence_count": len(masks),
        "seed_columns": list(range(seed_count)),
        "per_seed_minimum": minima,
        "records": records,
    }
    if args.all_seeds:
        total_or = sum(minima)
        logic_cost = 3 * len(gates) + total_or
        gate = 166 + logic_cost
        payload.update(
            {
                "sum_minimum": total_or,
                "xor_count": len(gates),
                "xor_gate_cost": 3,
                "logic_cost": logic_cost,
                "fixed_shell_gate": 166,
                "gate": gate,
                "delay": 10,
                "cycles": 65,
                "energy": gate * 10 * 65,
                "note": (
                    "Different seed bits may reuse one physical site in this relaxed "
                    "model, so the sum is a lower bound for realizable placement."
                ),
            }
        )
    else:
        payload.update(
            {
                "sum_lower_bound": sum(minima),
                "or_budget": 44,
                "conclusion": (
                    "first nine seed columns alone exceed the no-RAM "
                    "393/10/65 OR budget"
                ),
            }
        )
    payload["certificate_sha256"] = hashlib.sha256(
        json.dumps(records, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if key != "records"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
