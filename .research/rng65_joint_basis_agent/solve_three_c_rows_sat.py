#!/usr/bin/env python3
"""Exact support-9 completion around a persistent-seed RNG basis.

Only the output rows of C that violate the requested support bound are free.
Instead of encoding an unconstrained inverse P, use the equivalent identities

    C * B = A * C
    C * D = A * (A + I)

The right-hand side of the second identity is invertible for the xorshift32
transition, so every satisfying C is invertible and describes exactly

    B = C^-1 * A * C
    D = C^-1 * A * (A + I)
    T = C^-1 * A.

This reduces the three-row neighbourhood from roughly 168k variables to a
small exact SAT instance.  SAT is only a support-feasibility result; it is not
a physical XOR/Switch implementation and must be followed by timed synthesis.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import time
from typing import Iterable, Sequence

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


BITS = 32
MASK32 = (1 << BITS) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK32
    value ^= value >> 5
    return value & MASK32


def transition_rows() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << source) for source in range(BITS))
    return tuple(
        sum(((columns[source] >> target) & 1) << source for source in range(BITS))
        for target in range(BITS)
    )


def identity_rows() -> tuple[int, ...]:
    return tuple(1 << bit for bit in range(BITS))


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(
        ((row & value).bit_count() & 1) << bit
        for bit, row in enumerate(matrix)
    )


def inverse(matrix: Sequence[int]) -> tuple[int, ...]:
    work = list(matrix)
    result = list(identity_rows())
    for column in range(BITS):
        pivot = next(
            (row for row in range(column, BITS) if work[row] >> column & 1),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        result[column], result[pivot] = result[pivot], result[column]
        for row in range(BITS):
            if row != column and work[row] >> column & 1:
                work[row] ^= work[column]
                result[row] ^= result[column]
    if tuple(work) != identity_rows():
        raise AssertionError("inverse reduction failed")
    return tuple(result)


def matrix_hex(matrix: Sequence[int]) -> list[str]:
    return [f"{row:08x}" for row in matrix]


def load_center(path: Path) -> dict[str, object]:
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    if not records:
        raise ValueError("center JSONL is empty")

    def key(record: dict[str, object]) -> tuple[int, ...]:
        score = record.get("score")
        if not isinstance(score, dict):
            return (10**9,) * 5
        return tuple(
            int(score.get(name, 10**9))
            for name in ("over", "excess", "max", "standalone", "weight")
        )

    center = min(records, key=key)
    for name in ("B", "C", "D"):
        rows = center.get(name)
        if not isinstance(rows, list) or len(rows) != BITS:
            raise ValueError(f"center record has no 32-row {name}")
    return center


def parse_rows(record: dict[str, object], name: str) -> tuple[int, ...]:
    value = record[name]
    if not isinstance(value, list):
        raise TypeError(name)
    return tuple(int(str(row), 16) for row in value)


def rss_mb() -> float | None:
    try:
        import psutil

        return psutil.Process().memory_info().rss / (1024 * 1024)
    except ImportError:
        return None


class ThreeRowModel:
    def __init__(
        self,
        solver: Solver,
        center_c: Sequence[int],
        support: int,
        free_rows: Sequence[int],
    ) -> None:
        self.solver = solver
        self.center_c = tuple(center_c)
        self.support = support
        self.free_rows = tuple(sorted(set(free_rows)))
        self.free_set = frozenset(self.free_rows)
        self.next_variable = 1
        self.clause_count = 0
        self.kind_counts: Counter[str] = Counter()

        self.a = transition_rows()
        identity = identity_rows()
        self.a_plus_i = tuple(row ^ unit for row, unit in zip(self.a, identity))
        self.k = compose(self.a, self.a_plus_i)
        # C*D=K implies C is invertible only when K is invertible.
        inverse(self.k)

        self.c: list[list[int | None]] = []
        for row in range(BITS):
            self.c.append(
                [self.fresh("C") for _ in range(BITS)]
                if row in self.free_set
                else [None] * BITS
            )
        self.b = self.matrix("B")
        self.d = self.matrix("D")

        self.encode_cb_equals_ac()
        self.encode_cd_equals_k()
        self.encode_support()

    def fresh(self, kind: str) -> int:
        variable = self.next_variable
        self.next_variable += 1
        self.kind_counts[kind] += 1
        return variable

    def matrix(self, kind: str) -> list[list[int]]:
        return [[self.fresh(kind) for _ in range(BITS)] for _ in range(BITS)]

    def add(self, clause: Iterable[int]) -> None:
        self.solver.add_clause(list(clause))
        self.clause_count += 1

    def c_entry(self, row: int, column: int) -> bool | int:
        if row in self.free_set:
            variable = self.c[row][column]
            if variable is None:
                raise AssertionError("free C entry has no variable")
            return variable
        return bool(self.center_c[row] >> column & 1)

    def and2(self, left: int, right: int) -> int:
        output = self.fresh("AND")
        self.add((-left, -right, output))
        self.add((left, -output))
        self.add((right, -output))
        return output

    def xor2(self, left: int, right: int) -> int:
        output = self.fresh("XOR_AUX")
        self.add((left, right, -output))
        self.add((-left, -right, -output))
        self.add((left, -right, output))
        self.add((-left, right, output))
        return output

    def parity(self, terms: Iterable[int], value: bool) -> None:
        # Identical variables cancel in GF(2).  Cancelling here materially
        # reduces clauses in fixed-row equations.
        parity_terms: set[int] = set()
        for term in terms:
            if term in parity_terms:
                parity_terms.remove(term)
            else:
                parity_terms.add(term)
        ordered = sorted(parity_terms)
        if not ordered:
            if value:
                self.add(())
            return
        current = ordered[0]
        for term in ordered[1:]:
            current = self.xor2(current, term)
        self.add((current if value else -current,))

    def c_times_variable_matrix_terms(
        self,
        c_row: int,
        matrix: Sequence[Sequence[int]],
        column: int,
    ) -> list[int]:
        terms: list[int] = []
        for inner in range(BITS):
            entry = self.c_entry(c_row, inner)
            if entry is False:
                continue
            if entry is True:
                terms.append(matrix[inner][column])
            else:
                terms.append(self.and2(entry, matrix[inner][column]))
        return terms

    def a_times_c_terms(self, row: int, column: int) -> tuple[list[int], bool]:
        terms: list[int] = []
        constant = False
        sources = self.a[row]
        while sources:
            low = sources & -sources
            source = low.bit_length() - 1
            entry = self.c_entry(source, column)
            if entry is True:
                constant = not constant
            elif entry is not False:
                terms.append(entry)
            sources ^= low
        return terms, constant

    def encode_cb_equals_ac(self) -> None:
        for row in range(BITS):
            for column in range(BITS):
                terms = self.c_times_variable_matrix_terms(row, self.b, column)
                right_terms, right_constant = self.a_times_c_terms(row, column)
                self.parity((*terms, *right_terms), right_constant)

    def encode_cd_equals_k(self) -> None:
        for row in range(BITS):
            for column in range(BITS):
                terms = self.c_times_variable_matrix_terms(row, self.d, column)
                self.parity(terms, bool(self.k[row] >> column & 1))

    def atmost(self, literals: Sequence[int], bound: int) -> None:
        if bound < 0:
            self.add(())
            return
        if bound >= len(literals):
            return
        encoding = CardEnc.atmost(
            lits=list(literals),
            bound=bound,
            top_id=self.next_variable - 1,
            encoding=EncType.seqcounter,
        )
        for clause in encoding.clauses:
            self.add(clause)
        if encoding.nv >= self.next_variable:
            added = encoding.nv - self.next_variable + 1
            self.kind_counts["CARD_AUX"] += added
            self.next_variable = encoding.nv + 1

    def encode_support(self) -> None:
        for row in range(BITS):
            budget = self.support - self.a[row].bit_count()
            if row in self.free_set:
                variables = [item for item in self.c[row] if item is not None]
                self.atmost(variables, budget)
            elif self.center_c[row].bit_count() > budget:
                self.add(())
        for row in range(BITS):
            self.atmost([*self.b[row], *self.d[row]], self.support)

    def phases(
        self,
        center_b: Sequence[int],
        center_d: Sequence[int],
    ) -> list[int]:
        result: list[int] = []
        for row in self.free_rows:
            for column, variable in enumerate(self.c[row]):
                if variable is None:
                    raise AssertionError("free phase variable missing")
                result.append(
                    variable if self.center_c[row] >> column & 1 else -variable
                )
        for values, variables in ((center_b, self.b), (center_d, self.d)):
            result.extend(
                variable if values[row] >> column & 1 else -variable
                for row in range(BITS)
                for column, variable in enumerate(variables[row])
            )
        return result

    @staticmethod
    def rows_from_model(
        positive: frozenset[int],
        variables: Sequence[Sequence[int]],
    ) -> tuple[int, ...]:
        return tuple(
            sum((variable in positive) << column for column, variable in enumerate(row))
            for row in variables
        )

    def extract(self, model: Sequence[int]) -> dict[str, object]:
        positive = frozenset(literal for literal in model if literal > 0)
        c = list(self.center_c)
        for row in self.free_rows:
            variables = self.c[row]
            c[row] = sum(
                (variable in positive) << column
                for column, variable in enumerate(variables)
                if variable is not None
            )
        c_rows = tuple(c)
        b_rows = self.rows_from_model(positive, self.b)
        d_rows = self.rows_from_model(positive, self.d)
        p_rows = inverse(c_rows)
        t_rows = compose(p_rows, self.a)

        if compose(c_rows, b_rows) != compose(self.a, c_rows):
            raise AssertionError("extracted C*B != A*C")
        if compose(c_rows, d_rows) != self.k:
            raise AssertionError("extracted C*D != A*(A+I)")
        if b_rows != compose(compose(t_rows, self.a), inverse(t_rows)):
            raise AssertionError("extracted B != T*A*T^-1")
        if d_rows != compose(t_rows, self.a_plus_i):
            raise AssertionError("extracted D != T*(A+I)")
        if c_rows != compose(self.a, inverse(t_rows)):
            raise AssertionError("extracted C != A*T^-1")

        feedback_weights = tuple(
            left.bit_count() + right.bit_count()
            for left, right in zip(b_rows, d_rows, strict=True)
        )
        output_weights = tuple(
            left.bit_count() + right.bit_count()
            for left, right in zip(c_rows, self.a, strict=True)
        )
        if max((*feedback_weights, *output_weights)) > self.support:
            raise AssertionError("extracted solution violates support bound")

        replayed = 0
        seeds = (0, *identity_rows(), MASK32, 0x12345678, 0xDEADBEEF)
        for seed in seeds:
            state = 0
            expected = seed
            for _tick in range(65):
                # Output is sampled before the state update.  Tick zero emits
                # A*seed; q_k=T*(A^k+I)*seed then telescopes exactly.
                output = apply_matrix(c_rows, state) ^ apply_matrix(self.a, seed)
                expected = xorshift32(expected)
                if output != expected:
                    raise AssertionError("65-cycle protocol replay failed")
                state = apply_matrix(b_rows, state) ^ apply_matrix(d_rows, seed)
                replayed += 1

        return {
            "T": matrix_hex(t_rows),
            "B": matrix_hex(b_rows),
            "C": matrix_hex(c_rows),
            "D": matrix_hex(d_rows),
            "P": matrix_hex(p_rows),
            "feedback_weights": list(feedback_weights),
            "output_weights": list(output_weights),
            "maximum_support": max((*feedback_weights, *output_weights)),
            "matrix_identities_verified": True,
            "protocol": {
                "sample_order": "output then state update",
                "seed_count": len(seeds),
                "cycles_per_seed": 65,
                "outputs_replayed": replayed,
            },
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--center", type=Path, required=True)
    parser.add_argument("--support", type=int, default=9)
    parser.add_argument(
        "--free-rows",
        type=lambda value: tuple(int(item) for item in value.split(",") if item),
        help="defaults to the center C rows that violate the output bound",
    )
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--conflicts", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    center = load_center(args.center)
    center_c = parse_rows(center, "C")
    center_b = parse_rows(center, "B")
    center_d = parse_rows(center, "D")
    a = transition_rows()
    free_rows = args.free_rows
    if free_rows is None:
        free_rows = tuple(
            row
            for row in range(BITS)
            if center_c[row].bit_count() + a[row].bit_count() > args.support
        )
    if not free_rows:
        parser.error("the selected center has no violating output rows")
    if any(row < 0 or row >= BITS for row in free_rows):
        parser.error("--free-rows entries must be in 0..31")

    started = time.monotonic()
    with Solver(name=args.solver) as solver:
        model = ThreeRowModel(solver, center_c, args.support, free_rows)
        built = time.monotonic()
        phase_hint_applied = False
        try:
            solver.set_phases(model.phases(center_b, center_d))
            phase_hint_applied = True
        except NotImplementedError:
            pass
        if args.conflicts:
            solver.conf_budget(args.conflicts)
            answer = solver.solve_limited(expect_interrupt=True)
        else:
            answer = solver.solve()
        solved = time.monotonic()

        payload: dict[str, object] = {
            "schema": 1,
            "model": "persistent seed exact support completion with fixed C rows",
            "equations": ["C*B=A*C", "C*D=A*(A+I)"],
            "support_limit": args.support,
            "status": (
                "sat" if answer is True else "unsat" if answer is False else "unknown"
            ),
            "solver": args.solver,
            "conflict_budget": args.conflicts or None,
            "variables": model.next_variable - 1,
            "variable_kinds": dict(sorted(model.kind_counts.items())),
            "clauses": model.clause_count,
            "build_seconds": built - started,
            "solve_seconds": solved - built,
            "rss_mb": rss_mb(),
            "center": {
                "path": str(args.center),
                "source_score": center.get("score"),
                "free_rows": list(free_rows),
                "fixed_rows": [row for row in range(BITS) if row not in free_rows],
                "phase_hint_applied": phase_hint_applied,
            },
            "transition_sha256": sha256(
                b"".join(row.to_bytes(4, "little") for row in a)
            ).hexdigest(),
            "scope": (
                "SAT/UNSAT is exact only in the stated fixed-C-row neighbourhood. "
                "SAT still requires arrival-aware physical synthesis."
            ),
        }
        if answer is True:
            payload["solution"] = model.extract(solver.get_model())

    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))
    return 0 if answer is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
