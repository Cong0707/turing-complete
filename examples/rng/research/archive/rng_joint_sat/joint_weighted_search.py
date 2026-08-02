"""Exact weighted SAT search over a finite xorshift32 basis neighborhood.

For every enumerated basis ``T`` this script jointly chooses the canonical
depth-two XOR pair cover for ``B = T*A*T^-1`` and ``C = A*T^-1``, all tick-zero
labels, and the distinct ``(seed, state)`` OR leaves.  Unlike the older fixed-T
solver, the only cost constraint is the real weighted objective::

    3 * XOR + OR <= logic_budget

The outer basis domain is finite and explicit.  An UNSAT result therefore
only excludes that enumerated row-shear neighborhood, not every invertible
32-by-32 matrix.  This research script never imports save-writing code.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import gc
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Iterable, Sequence

from z3 import And, AtMost, Bool, Implies, Not, Or, PbLe, Solver, Xor, is_true, sat, unsat


BITS = 32
BASE_GATE_COST = 166
DEFAULT_LOGIC_BUDGET = 221


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def support(mask: int) -> tuple[int, ...]:
    return tuple(bit for bit in range(BITS) if mask >> bit & 1)


def pair_options(mask: int) -> tuple[tuple[int, ...], ...]:
    units = tuple(1 << bit for bit in support(mask))
    if len(units) == 3:
        return tuple((mask ^ unit,) for unit in units)
    if len(units) == 4:
        a, b, c, d = units
        return (
            tuple(sorted((a | b, c | d))),
            tuple(sorted((a | c, b | d))),
            tuple(sorted((a | d, b | c))),
        )
    raise ValueError(f"row {mask:08x} has unsupported weight {len(units)}")


@dataclass(frozen=True)
class BasisCandidate:
    T: tuple[int, ...]
    B: tuple[int, ...]
    C: tuple[int, ...]
    operations: tuple[tuple[int, int], ...]


def enumerate_bases(init_module, search_module, radius: int) -> list[BasisCandidate]:
    """Enumerate the exact feasible row-shear ball used by prior searches."""

    start = BasisCandidate(
        tuple(init_module.T), tuple(init_module.B), tuple(init_module.C), ()
    )
    seen: dict[tuple[int, ...], BasisCandidate] = {start.T: start}
    frontier = [start]
    for _depth in range(radius):
        following: list[BasisCandidate] = []
        for candidate in frontier:
            for dst in range(BITS):
                for src in range(BITS):
                    if dst == src:
                        continue
                    T, B, C = map(list, (candidate.T, candidate.B, candidate.C))
                    search_module.mutate(T, B, C, dst, src)
                    if any(row == 0 or row.bit_count() > 4 for row in (*T, *B, *C)):
                        continue
                    key = tuple(T)
                    if key in seen:
                        continue
                    item = BasisCandidate(
                        key,
                        tuple(B),
                        tuple(C),
                        candidate.operations + ((dst, src),),
                    )
                    seen[key] = item
                    following.append(item)
        frontier = following
    return list(seen.values())


def _matrix_hex(rows: Sequence[int]) -> list[str]:
    return [f"{row:08x}" for row in rows]


def _weighted_lower_bound(B: Sequence[int], C: Sequence[int]) -> int:
    # Every distinct non-unit target needs one XOR and invertible T makes all
    # 32 seed coordinates appear in at least one paid mode mapping.
    non_units = {row for row in (*B, *C) if row.bit_count() >= 2}
    return 3 * len(non_units) + BITS


def build_solver(
    candidate: BasisCandidate,
    *,
    logic_budget: int,
    timeout_ms: int,
    memory_mb: int,
    fixed_pairs: frozenset[int] | None = None,
):
    T, B, C = candidate.T, candidate.B, candidate.C
    targets = frozenset((*B, *C))
    if 0 in targets or any(row.bit_count() > 4 for row in targets):
        raise ValueError("all B/C rows must have weight in [1,4]")

    required_pairs = frozenset(row for row in targets if row.bit_count() == 2)
    finals = frozenset(row for row in targets if row.bit_count() in (3, 4))
    options = {row: pair_options(row) for row in finals}
    if fixed_pairs is None:
        candidate_pairs = frozenset(
            (*required_pairs, *(pair for row in finals for option in options[row] for pair in option))
        )
    else:
        if not required_pairs <= fixed_pairs:
            raise ValueError("fixed pair set omits a pair-valued target")
        options = {
            row: tuple(option for option in row_options if set(option) <= fixed_pairs)
            for row, row_options in options.items()
        }
        if any(not row_options for row_options in options.values()):
            raise ValueError("fixed pair set does not cover every final target")
        candidate_pairs = fixed_pairs

    solver = Solver()
    solver.set(timeout=timeout_ms, max_memory=memory_mb)

    selected = {pair: Bool(f"pair_{pair:08x}") for pair in sorted(candidate_pairs)}
    choose = {
        (row, index): Bool(f"choose_{row:08x}_{index}")
        for row in sorted(finals)
        for index in range(len(options[row]))
    }
    pair_users: dict[int, list[object]] = {pair: [] for pair in candidate_pairs}
    for row in finals:
        row_choices = [choose[row, index] for index in range(len(options[row]))]
        solver.add(Or(*row_choices), AtMost(*row_choices, 1))
        for index, option in enumerate(options[row]):
            for pair in option:
                solver.add(Implies(choose[row, index], selected[pair]))
                pair_users[pair].append(choose[row, index])
    for pair in candidate_pairs:
        if pair in required_pairs:
            solver.add(selected[pair])
        else:
            # Any feasible solution can delete an unused first-layer gate.
            solver.add(selected[pair] == Or(*pair_users[pair]))

    mode = {
        (seed, state): Bool(f"mode_s{seed}_q{state}")
        for seed in range(BITS)
        for state in range(BITS)
    }
    mode_users: dict[tuple[int, int], list[object]] = {key: [] for key in mode}
    pin = {
        (pair, side, seed): Bool(f"pin_{pair:08x}_{side}_s{seed}")
        for pair in sorted(candidate_pairs)
        for side in range(2)
        for seed in range(BITS)
    }
    label = {
        (pair, seed): Bool(f"label_{pair:08x}_s{seed}")
        for pair in sorted(candidate_pairs)
        for seed in range(BITS)
    }
    for pair in candidate_pairs:
        states = support(pair)
        if len(states) != 2:
            raise AssertionError("candidate pair is not weight two")
        for side, state in enumerate(states):
            side_pins = [pin[pair, side, seed] for seed in range(BITS)]
            solver.add(AtMost(*side_pins, 1))
            for seed, variable in enumerate(side_pins):
                solver.add(Implies(variable, selected[pair]))
                solver.add(Implies(variable, mode[seed, state]))
                mode_users[seed, state].append(variable)
        for seed in range(BITS):
            solver.add(label[pair, seed] == Xor(pin[pair, 0, seed], pin[pair, 1, seed]))

    # B is invertible, hence its rows are unique and each has one tick-zero T
    # label.  C-only targets have no tick-zero requirement because output is
    # disabled during seed loading.
    b_index = {row: index for index, row in enumerate(B)}
    if len(b_index) != BITS:
        raise AssertionError("B must have 32 unique rows")
    for row, index in b_index.items():
        target = T[index]
        weight = row.bit_count()
        if weight == 1:
            target_bits = support(target)
            if len(target_bits) != 1:
                solver.add(False)
            else:
                key = (target_bits[0], support(row)[0])
                solver.add(mode[key])
                mode_users[key].append(True)
        elif weight == 2:
            for seed in range(BITS):
                solver.add(label[row, seed] == bool(target >> seed & 1))
        elif weight == 3:
            for option_index, option in enumerate(options[row]):
                condition = choose[row, option_index]
                pair = option[0]
                state = support(row ^ pair)[0]
                residuals = []
                for seed in range(BITS):
                    residual = Xor(label[pair, seed], bool(target >> seed & 1))
                    residuals.append(residual)
                    user = And(condition, residual)
                    solver.add(Implies(user, mode[seed, state]))
                    mode_users[seed, state].append(user)
                solver.add(Implies(condition, AtMost(*residuals, 1)))
        elif weight == 4:
            for option_index, (left, right) in enumerate(options[row]):
                condition = choose[row, option_index]
                for seed in range(BITS):
                    expected = bool(target >> seed & 1)
                    value = Xor(label[left, seed], label[right, seed])
                    solver.add(Implies(condition, value if expected else Not(value)))
        else:
            solver.add(False)

    for key, variable in mode.items():
        users = mode_users[key]
        solver.add(variable == Or(*users) if users else Not(variable))
    for seed in range(BITS):
        solver.add(Or(*(mode[seed, state] for state in range(BITS))))

    # XOR = selected first-layer pairs + one final gate per distinct weight-3/4
    # target.  This single PB inequality is the real score objective.
    fixed_final_cost = 3 * len(finals)
    residual_budget = logic_budget - fixed_final_cost
    if residual_budget < 0:
        solver.add(False)
    else:
        weighted = [(variable, 3) for variable in selected.values()]
        weighted.extend((variable, 1) for variable in mode.values())
        solver.add(PbLe(weighted, residual_budget))

    metadata = {
        "targets": len(targets),
        "required_pairs": len(required_pairs),
        "finals": len(finals),
        "candidate_pairs": len(candidate_pairs),
        "weighted_lower_bound": _weighted_lower_bound(B, C),
    }
    variables = {"selected": selected, "choose": choose, "mode": mode, "pin": pin, "label": label}
    constants = {"options": options, "finals": finals}
    return solver, variables, constants, metadata


def extract_certificate(candidate, model, variables, constants, logic_budget: int) -> dict[str, object]:
    selected_vars = variables["selected"]
    choose = variables["choose"]
    mode_vars = variables["mode"]
    pin = variables["pin"]
    label = variables["label"]
    options = constants["options"]
    finals = constants["finals"]

    selected = frozenset(pair for pair, var in selected_vars.items() if is_true(model.eval(var)))
    modes = frozenset(key for key, var in mode_vars.items() if is_true(model.eval(var)))
    decompositions = {
        row: next(
            option
            for index, option in enumerate(options[row])
            if is_true(model.eval(choose[row, index]))
        )
        for row in finals
    }
    labels = {
        pair: sum(1 << seed for seed in range(BITS) if is_true(model.eval(label[pair, seed])))
        for pair in selected
    }
    pins = {
        pair: [
            next(
                (seed for seed in range(BITS) if is_true(model.eval(pin[pair, side, seed]))),
                None,
            )
            for side in range(2)
        ]
        for pair in selected
    }
    xor_count = len(selected) + len(finals)
    or_count = len(modes)
    return {
        "T": _matrix_hex(candidate.T),
        "B": _matrix_hex(candidate.B),
        "C": _matrix_hex(candidate.C),
        "basis_row_shears": [list(item) for item in candidate.operations],
        "selected_pair_gates": [f"{pair:08x}" for pair in sorted(selected)],
        "decompositions": {
            f"{row:08x}": [f"{pair:08x}" for pair in option]
            for row, option in sorted(decompositions.items())
        },
        "pair_labels": {f"{pair:08x}": f"{labels[pair]:08x}" for pair in sorted(labels)},
        "pair_pin_seed_bits": {f"{pair:08x}": pins[pair] for pair in sorted(pins)},
        "mode_pairs": [{"seed": seed, "state": state} for seed, state in sorted(modes)],
        "metrics": {
            "xor": xor_count,
            "or": or_count,
            "logic_cost": 3 * xor_count + or_count,
            "logic_budget": logic_budget,
            "gate": BASE_GATE_COST + 3 * xor_count + or_count,
            "delay": 9,
            "cycles": 66,
        },
    }


def constrain_known_root_dag(solver, variables, constants, init_module) -> None:
    """Pin the full-width smoke run to the independently verified 61-XOR DAG."""

    selected = variables["selected"]
    choose = variables["choose"]
    options = constants["options"]
    known_pairs = frozenset(init_module.FIRST_LAYER)
    if not known_pairs <= frozenset(selected):
        raise AssertionError("known first layer is outside the SAT pair universe")
    for pair, variable in selected.items():
        solver.add(variable if pair in known_pairs else Not(variable))
    gate_by_output = init_module.GATE_BY_OUTPUT
    for row, row_options in options.items():
        gate = gate_by_output[row]
        known = tuple(sorted(fanin for fanin in (gate.left, gate.right) if fanin.bit_count() == 2))
        option_index = row_options.index(known)
        for index in range(len(row_options)):
            variable = choose[row, index]
            solver.add(variable if index == option_index else Not(variable))


def verify_certificate(init_module, certificate: dict[str, object]) -> None:
    parse = lambda rows: tuple(int(row, 16) for row in rows)
    T, B, C = map(parse, (certificate["T"], certificate["B"], certificate["C"]))
    if init_module.compose(C, T) != init_module.A or init_module.compose(T, C) != B:
        raise AssertionError("matrix identities failed")

    selected = frozenset(int(row, 16) for row in certificate["selected_pair_gates"])
    decompositions = {
        int(row, 16): tuple(int(pair, 16) for pair in option)
        for row, option in certificate["decompositions"].items()
    }
    labels = {int(row, 16): int(value, 16) for row, value in certificate["pair_labels"].items()}
    pins = {int(row, 16): tuple(value) for row, value in certificate["pair_pin_seed_bits"].items()}
    modes = frozenset((item["seed"], item["state"]) for item in certificate["mode_pairs"])

    for pair in selected:
        states = support(pair)
        actual = 0
        for seed, state in zip(pins[pair], states):
            if seed is not None:
                actual ^= 1 << seed
                if (seed, state) not in modes:
                    raise AssertionError("pair pin uses an absent mode mapping")
        if actual != labels[pair]:
            raise AssertionError("pair tick-zero label mismatch")

    targets = frozenset((*B, *C))
    for row in targets:
        if row.bit_count() == 2 and row not in selected:
            raise AssertionError("required pair target is absent")
        if row.bit_count() >= 3:
            option = decompositions[row]
            if not set(option) <= selected:
                raise AssertionError("final target references an absent pair")
            if option not in pair_options(row):
                raise AssertionError("invalid steady decomposition")

    for target, steady in zip(T, B):
        weight = steady.bit_count()
        if weight == 1:
            if target.bit_count() != 1:
                raise AssertionError("direct B target has non-unit seed label")
            actual = target
            required = (support(target)[0], support(steady)[0])
            if required not in modes:
                raise AssertionError("direct B mode mapping is absent")
        elif weight == 2:
            actual = labels[steady]
        elif weight == 3:
            pair = decompositions[steady][0]
            residual = target ^ labels[pair]
            if residual.bit_count() > 1:
                raise AssertionError("weight-three raw residual is not a unit")
            if residual and (support(residual)[0], support(steady ^ pair)[0]) not in modes:
                raise AssertionError("weight-three raw mode mapping is absent")
            actual = labels[pair] ^ residual
        else:
            left, right = decompositions[steady]
            actual = labels[left] ^ labels[right]
        if actual != target:
            raise AssertionError("B tick-zero label mismatch")

    metrics = certificate["metrics"]
    if metrics["logic_cost"] != 3 * metrics["xor"] + metrics["or"]:
        raise AssertionError("weighted cost accounting mismatch")
    for seed in (0, 1, 2, 0x12345678, 0xFFFFFFFF, 0x80000000):
        natural = seed
        encoded = init_module.apply_matrix(T, seed)
        for _ in range(65):
            natural = init_module.xorshift32(natural)
            if init_module.apply_matrix(C, encoded) != natural:
                raise AssertionError("visible RNG sequence mismatch")
            encoded = init_module.apply_matrix(B, encoded)


def search(args) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    init_module = load_module("joint_weighted_init", root / ".research/rng_init_reuse/verify_init_reuse.py")
    search_module = load_module("joint_weighted_basis", root / ".research/rng_joint_search_resume/search.py")
    candidates = enumerate_bases(init_module, search_module, args.radius)
    candidates.sort(
        key=lambda item: (
            _weighted_lower_bound(item.B, item.C),
            len(item.operations),
            item.operations,
        )
    )
    total_candidates = len(candidates)
    if args.max_candidates is not None:
        candidates = candidates[: args.max_candidates]

    started = time.perf_counter()
    records: list[dict[str, object]] = []
    best_certificate = None
    unknown = 0
    skipped_by_bound = 0
    complete = len(candidates) == total_candidates

    for ordinal, candidate in enumerate(candidates):
        if args.max_total_seconds and time.perf_counter() - started >= args.max_total_seconds:
            complete = False
            break
        lower = _weighted_lower_bound(candidate.B, candidate.C)
        if lower > args.logic_budget:
            skipped_by_bound += 1
            records.append({"operations": [list(x) for x in candidate.operations], "status": "bound_unsat", "lower": lower})
            continue

        solver, variables, constants, metadata = build_solver(
            candidate,
            logic_budget=args.logic_budget,
            timeout_ms=args.timeout_ms,
            memory_mb=args.memory_mb,
            fixed_pairs=(frozenset(init_module.FIRST_LAYER) if args.fix_known_dag else None),
        )
        if args.fix_known_dag:
            if candidate.operations:
                raise AssertionError("known DAG can only be applied to the root basis")
            constrain_known_root_dag(solver, variables, constants, init_module)
        checked_at = time.perf_counter()
        result = solver.check()
        elapsed = time.perf_counter() - checked_at
        record: dict[str, object] = {
            "ordinal": ordinal,
            "operations": [list(x) for x in candidate.operations],
            "elapsed_seconds": round(elapsed, 6),
            **metadata,
        }
        if result == sat:
            certificate = extract_certificate(candidate, solver.model(), variables, constants, args.logic_budget)
            verify_certificate(init_module, certificate)
            record["status"] = "sat"
            record["metrics"] = certificate["metrics"]
            if best_certificate is None or certificate["metrics"]["logic_cost"] < best_certificate["metrics"]["logic_cost"]:
                best_certificate = certificate
            records.append(record)
            if args.stop_on_sat:
                complete = False
                break
        elif result == unsat:
            record["status"] = "unsat"
            records.append(record)
        else:
            record["status"] = "unknown"
            record["reason"] = solver.reason_unknown()
            records.append(record)
            unknown += 1
        del solver, variables, constants
        gc.collect()

    if best_certificate is not None:
        status = "sat"
    elif complete and unknown == 0:
        status = "unsat_in_enumerated_family"
    else:
        status = "unknown"
    return {
        "status": status,
        "scope": (
            "fixed verified root DAG"
            if args.fix_known_dag
            else f"all feasible row-shear bases within radius {args.radius} of fixed two-shear T"
        ),
        "logic_budget": args.logic_budget,
        "gate_budget": BASE_GATE_COST + args.logic_budget,
        "basis_count_in_scope": total_candidates,
        "basis_count_attempted": len(records),
        "complete": complete,
        "unknown_count": unknown,
        "skipped_by_lower_bound": skipped_by_bound,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "memory_limit_mb_per_solver": args.memory_mb,
        "records": records,
        **({"certificate": best_certificate} if best_certificate is not None else {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius", type=int, default=0)
    parser.add_argument("--logic-budget", type=int, default=DEFAULT_LOGIC_BUDGET)
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    parser.add_argument("--memory-mb", type=int, default=512)
    parser.add_argument("--max-total-seconds", type=float, default=0)
    parser.add_argument("--max-candidates", type=int)
    parser.add_argument("--stop-on-sat", action="store_true")
    parser.add_argument("--fix-known-dag", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.radius < 0 or args.radius > 6:
        parser.error("radius must be in [0,6]")
    if args.fix_known_dag and args.radius != 0:
        parser.error("--fix-known-dag requires --radius 0")
    if not 64 <= args.memory_mb < 2048:
        parser.error("memory-mb must be in [64,2047]")

    document = search(args)
    payload = json.dumps(document, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if document["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
