"""Exact bounded-neighborhood repair allowing zero hidden transition rows.

The global model is nonlinear over GF(2), but a Hamming ball around a concrete
frontier is small enough for Z3 to decide with little memory.  A SAT result is
fully verified here; an UNSAT result applies only to the requested Hamming
ball, not to all 42-state circuits.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import time

from z3 import And, Bool, BoolRef, If, Not, Or, PbEq, PbGe, PbLe, Solver, SolverFor, Xor, is_true


VISIBLE = 32
MASK32 = (1 << VISIBLE) - 1

DEFAULT_X = (
    0x010, 0x122, 0x040, 0x004, 0x008, 0x090, 0x020, 0x040,
    0x108, 0x200, 0x080, 0x044, 0x101, 0x100, 0x200, 0x004,
    0x008, 0x011, 0x022, 0x040, 0x004, 0x008, 0x210, 0x020,
    0x040, 0x100, 0x200, 0x280, 0x000, 0x000, 0x100, 0x200,
)
DEFAULT_D = (
    0x20040020001, 0x10400004002, 0x00800110008, 0x00100220010,
    0x08200040020, 0x04400080040, 0x00401100080, 0x0A000800400,
    0x20004002000, 0x08008404000,
)


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK32
    value ^= value >> 5
    return value & MASK32


def transition_rows() -> tuple[int, ...]:
    return tuple(
        sum(((xorshift32(1 << source) >> target) & 1) << source for source in range(VISIBLE))
        for target in range(VISIBLE)
    )


A_ROWS = transition_rows()


def xor_all(terms: list[BoolRef], constant: bool = False) -> BoolRef:
    if not terms:
        return Bool("__true") if constant else Bool("__false")
    result = terms[0]
    for term in terms[1:]:
        result = Xor(result, term)
    return Not(result) if constant else result


def xor_value(values: tuple[int, ...], mask: int) -> int:
    result = 0
    while mask:
        low = mask & -mask
        result ^= values[low.bit_length() - 1]
        mask ^= low
    return result


def output_rows(x_rows: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((1 << row) | (x_rows[row] << VISIBLE) for row in range(VISIBLE))


def top_rows(x_rows: tuple[int, ...], d_rows: tuple[int, ...]) -> tuple[int, ...]:
    outputs = output_rows(x_rows)
    return tuple(
        xor_value(outputs, A_ROWS[row]) ^ xor_value(d_rows, x_rows[row])
        for row in range(VISIBLE)
    )


def apply_matrix(rows: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << index for index, row in enumerate(rows))


def parse_candidate(line: str | None, hidden: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if not line:
        if hidden != 10:
            raise ValueError("the built-in frontier has hidden=10")
        return DEFAULT_X, DEFAULT_D
    match = re.search(r"\bX=([0-9a-f,]+) D=([0-9a-f,]+)\s*$", line.strip())
    if not match:
        raise ValueError("candidate must end in 'X=<hex,...> D=<hex,...>'")
    x_rows = tuple(int(value, 16) for value in match.group(1).split(","))
    d_rows = tuple(int(value, 16) for value in match.group(2).split(","))
    if len(x_rows) != VISIBLE or len(d_rows) != hidden:
        raise ValueError("candidate dimensions do not match")
    return x_rows, d_rows


@dataclass
class ModelData:
    x: list[list[BoolRef]]
    d: list[list[BoolRef]]
    top: list[list[BoolRef]]
    hamming: list[BoolRef]


def build_model(
    solver: Solver,
    hidden: int,
    start_x: tuple[int, ...],
    start_d: tuple[int, ...],
) -> ModelData:
    bits = VISIBLE + hidden
    false_const = Bool("__false")
    true_const = Bool("__true")
    solver.add(Not(false_const), true_const)

    x = [[Bool(f"x_{row}_{aux}") for aux in range(hidden)] for row in range(VISIBLE)]
    d = [[Bool(f"d_{aux}_{column}") for column in range(bits)] for aux in range(hidden)]
    for row in range(VISIBLE):
        solver.add(PbLe([(value, 1) for value in x[row]], 3))
    for aux in range(hidden):
        solver.add(PbLe([(value, 1) for value in d[aux]], 4))

    top: list[list[BoolRef]] = []
    for row in range(VISIBLE):
        top_row = []
        for column in range(bits):
            terms: list[BoolRef] = []
            constant = column < VISIBLE and bool((A_ROWS[row] >> column) & 1)
            if column >= VISIBLE:
                aux_column = column - VISIBLE
                terms.extend(
                    x[source][aux_column]
                    for source in range(VISIBLE)
                    if (A_ROWS[row] >> source) & 1
                )
            terms.extend(And(x[row][aux], d[aux][column]) for aux in range(hidden))
            top_row.append(xor_all(terms, constant))
        top.append(top_row)
        solver.add(PbLe([(value, 1) for value in top_row], 4))

    hamming = []
    for row in range(VISIBLE):
        for aux in range(hidden):
            hamming.append(x[row][aux] if not ((start_x[row] >> aux) & 1) else Not(x[row][aux]))
    for aux in range(hidden):
        for column in range(bits):
            hamming.append(d[aux][column] if not ((start_d[aux] >> column) & 1) else Not(d[aux][column]))
    return ModelData(x=x, d=d, top=top, hamming=hamming)


def extract_rows(model: object, variables: list[list[BoolRef]]) -> tuple[int, ...]:
    return tuple(
        sum(is_true(model.eval(value, model_completion=True)) << column for column, value in enumerate(row))
        for row in variables
    )


def pair_partitions(row: int) -> tuple[tuple[int, ...], ...]:
    support = tuple(index for index in range(row.bit_length()) if (row >> index) & 1)
    if len(support) == 3:
        return tuple(
            (sum(1 << support[index] for index in range(3) if index != lone),)
            for lone in range(3)
        )
    if len(support) == 4:
        return tuple(
            (
                (1 << support[0]) | (1 << support[mate]),
                row ^ ((1 << support[0]) | (1 << support[mate])),
            )
            for mate in range(1, 4)
        )
    raise ValueError(f"row weight is not 3 or 4: {row:x}")


def exact_pair_cover(target_rows: tuple[int, ...], timeout_ms: int) -> dict[str, object]:
    targets = tuple(sorted({row for row in target_rows if row.bit_count() >= 2}))
    paid_pairs = {row for row in targets if row.bit_count() == 2}
    requirements = [pair_partitions(row) for row in targets if row.bit_count() >= 3]
    candidate_pairs = sorted(
        {
            pair
            for options in requirements
            for option in options
            for pair in option
            if pair not in paid_pairs
        }
    )
    variables = {pair: Bool(f"pair_{pair:x}") for pair in candidate_pairs}
    solver = Solver()
    solver.set(timeout=timeout_ms)
    for options in requirements:
        solver.add(
            Or(
                *(
                    And(*(True if pair in paid_pairs else variables[pair] for pair in option))
                    for option in options
                )
            )
        )
    upper = len(candidate_pairs)
    best_selected: list[int] | None = None
    for bound in range(upper + 1):
        solver.push()
        solver.add(PbLe([(variable, 1) for variable in variables.values()], bound))
        status = solver.check()
        if str(status) == "sat":
            model = solver.model()
            best_selected = [pair for pair, variable in variables.items() if is_true(model.eval(variable))]
            solver.pop()
            break
        solver.pop()
        if str(status) == "unknown":
            return {
                "status": "unknown",
                "reason": solver.reason_unknown(),
                "distinct_nontrivial_targets": len(targets),
            }
    if best_selected is None:
        raise AssertionError("finite pair-cover unexpectedly UNSAT")
    return {
        "status": "optimal",
        "distinct_nontrivial_targets": len(targets),
        "additional_pairs": len(best_selected),
        "xor_count": len(targets) + len(best_selected),
        "selected_pairs_hex": [f"{pair:011x}" for pair in best_selected],
    }


def verify_candidate(x_rows: tuple[int, ...], d_rows: tuple[int, ...], pair_timeout_ms: int) -> dict[str, object]:
    hidden = len(d_rows)
    bits = VISIBLE + hidden
    outputs = output_rows(x_rows)
    top = top_rows(x_rows, d_rows)
    h_rows = top + d_rows
    if max(row.bit_count() for row in outputs + h_rows) > 4:
        raise AssertionError("SAT extraction violates depth-two support")

    # O*H = A*O is the exact semiconjugacy used by the search model.
    for state_bit in range(bits):
        state = 1 << state_bit
        left = apply_matrix(outputs, apply_matrix(h_rows, state))
        right = xorshift32(apply_matrix(outputs, state))
        if left != right:
            raise AssertionError(f"semiconjugacy failed at state bit {state_bit}")

    for seed in range(256):
        state = apply_matrix(h_rows, seed)
        natural = seed
        for _ in range(65):
            natural = xorshift32(natural)
            if apply_matrix(outputs, state) != natural:
                raise AssertionError(f"sequence mismatch for seed {seed}")
            state = apply_matrix(h_rows, state)

    cover = exact_pair_cover(outputs + h_rows, pair_timeout_ms)
    result: dict[str, object] = {
        "verified_sequences": {"seeds": 256, "outputs_per_seed": 65},
        "semiconjugacy_basis_states": bits,
        "max_target_weight": max(row.bit_count() for row in outputs + h_rows),
        "X_rows_hex": [f"{row:03x}" for row in x_rows],
        "D_rows_hex": [f"{row:011x}" for row in d_rows],
        "H_rows_hex": [f"{row:011x}" for row in h_rows],
        "O_rows_hex": [f"{row:011x}" for row in outputs],
        "pair_cover": cover,
    }
    if cover.get("status") == "optimal":
        xor_count = int(cover["xor_count"])
        gate = bits * 5 + 32 + 6 + 3 * xor_count
        result["score"] = {
            "gate": gate,
            "delay": 9,
            "cycles": 66,
            "energy": gate * 9 * 66,
            "beats_256014": gate * 9 * 66 < 256014,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hidden", type=int, default=10)
    parser.add_argument("--candidate-line")
    parser.add_argument("--bounds", default="2,4,6,8,10,12,16,20")
    parser.add_argument("--timeout-ms", type=int, default=15000)
    parser.add_argument("--pair-timeout-ms", type=int, default=30000)
    parser.add_argument("--exact-distance", action="store_true")
    parser.add_argument("--solver", choices=("default", "qffd"), default="default")
    parser.add_argument(
        "--free-x",
        help="comma-separated X row indices; all other X rows are fixed",
    )
    parser.add_argument(
        "--free-d",
        help="comma-separated D row indices; all other D rows are fixed",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    start_x, start_d = parse_candidate(args.candidate_line, args.hidden)
    solver = SolverFor("QF_FD") if args.solver == "qffd" else Solver()
    solver.set(timeout=args.timeout_ms)
    data = build_model(solver, args.hidden, start_x, start_d)
    if args.free_x is not None:
        free_x = {int(value) for value in args.free_x.split(",") if value}
        for row in range(VISIBLE):
            if row in free_x:
                continue
            for aux, variable in enumerate(data.x[row]):
                solver.add(variable == bool((start_x[row] >> aux) & 1))
    if args.free_d is not None:
        free_d = {int(value) for value in args.free_d.split(",") if value}
        for aux in range(args.hidden):
            if aux in free_d:
                continue
            for column, variable in enumerate(data.d[aux]):
                solver.add(variable == bool((start_d[aux] >> column) & 1))
    attempts = []
    solution = None
    for bound in (int(value) for value in args.bounds.split(",")):
        solver.push()
        distance_constraint = (
            PbEq([(literal, 1) for literal in data.hamming], bound)
            if args.exact_distance
            else PbLe([(literal, 1) for literal in data.hamming], bound)
        )
        solver.add(distance_constraint)
        started = time.monotonic()
        status = solver.check()
        elapsed = time.monotonic() - started
        attempt = {"hamming_bound": bound, "status": str(status), "seconds": elapsed}
        if str(status) == "unknown":
            attempt["reason"] = solver.reason_unknown()
        attempts.append(attempt)
        if str(status) == "sat":
            model = solver.model()
            x_rows = extract_rows(model, data.x)
            d_rows = extract_rows(model, data.d)
            solution = verify_candidate(x_rows, d_rows, args.pair_timeout_ms)
            solution["hamming_distance"] = sum(
                (left ^ right).bit_count()
                for left, right in zip(start_x + start_d, x_rows + d_rows)
            )
            solver.pop()
            break
        solver.pop()

    result = {
        "scope": (
            "exact support<=4 repair inside bounded Hamming balls; "
            "zero hidden D rows are allowed"
        ),
        "hidden": args.hidden,
        "zero_d_rows_allowed": True,
        "center": {
            "X_rows_hex": [f"{row:03x}" for row in start_x],
            "D_rows_hex": [f"{row:011x}" for row in start_d],
        },
        "timeout_ms_per_bound": args.timeout_ms,
        "attempts": attempts,
        "solution": solution,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
