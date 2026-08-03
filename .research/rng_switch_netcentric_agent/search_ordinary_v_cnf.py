"""Exact CNF synthesis for the actual V cone without tristate drivers.

When no Switch exists, every useful physical net has exactly one active
driver.  This specialized encoding therefore selects one predecessor per gate
input instead of carrying the much larger arbitrary-BUS/Z model.  All six raw
input complements remain free, so UNSAT is still a valid lower bound for the
real RNG circuit.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import threading
import time
from typing import Iterable

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


KINDS = ("NOT", "AND", "OR", "NAND", "NOR")
NOT, AND, OR, NAND, NOR = range(len(KINDS))
COMMUTATIVE = (AND, OR, NAND, NOR)

# Fifteen ordinary gates implementing five XORs as
# ``NOR(AND(a,b), NOR(a,b))``.  The schedule is the lexicographically sorted
# topological order required by the adjacent-kind symmetry constraint.
KNOWN_XOR_TREE = (
    (AND, 0, 2, 1),
    (AND, 4, 6, 1),
    (AND, 8, 10, 1),
    (NOR, 0, 2, 1),
    (NOR, 14, 17, 2),
    (NOR, 4, 6, 1),
    (NOR, 15, 19, 2),
    (AND, 18, 20, 3),
    (NOR, 18, 20, 3),
    (NOR, 21, 22, 4),
    (NOR, 8, 10, 1),
    (NOR, 16, 24, 2),
    (AND, 18, 25, 3),
    (NOR, 18, 25, 3),
    (NOR, 26, 27, 4),
)


class Encoder:
    def __init__(self) -> None:
        self.pool = IDPool()
        self.cnf = CNF()

    def var(self, name: str) -> int:
        return self.pool.id(name)

    def clause(self, values: Iterable[int | bool]) -> None:
        literals = []
        for value in values:
            if value is True:
                return
            if value is False:
                continue
            literals.append(value)
        self.cnf.append(literals)

    @staticmethod
    def neg(value: int | bool) -> int | bool:
        return not value if type(value) is bool else -value

    def exactly_one(self, values: list[int]) -> None:
        self.cnf.extend(
            CardEnc.equals(
                values,
                bound=1,
                vpool=self.pool,
                encoding=EncType.seqcounter,
            ).clauses
        )


def parity_table(inputs: int, support: tuple[int, ...]) -> int:
    return sum(
        (sum((case >> bit) & 1 for bit in support) & 1) << case
        for case in range(1 << inputs)
    )


def add_conditional_gate(
    enc: Encoder,
    kind: int,
    output: int,
    left: int | bool,
    right: int | bool,
    operation: int,
) -> None:
    if operation == NOT:
        enc.clause((-kind, output, left))
        enc.clause((-kind, -output, -left if isinstance(left, int) else not left))
    elif operation == AND:
        enc.clause((-kind, -output, left))
        enc.clause((-kind, -output, right))
        enc.clause((-kind, output, -left, -right))
    elif operation == OR:
        enc.clause((-kind, output, -left))
        enc.clause((-kind, output, -right))
        enc.clause((-kind, -output, left, right))
    elif operation == NAND:
        enc.clause((-kind, output, left))
        enc.clause((-kind, output, right))
        enc.clause((-kind, -output, -left, -right))
    elif operation == NOR:
        enc.clause((-kind, -output, -left))
        enc.clause((-kind, -output, -right))
        enc.clause((-kind, output, left, right))
    else:  # pragma: no cover
        raise ValueError(operation)


def solve(args: argparse.Namespace) -> dict[str, object]:
    inputs = 6
    assignments = 1 << inputs
    full = (1 << assignments) - 1
    raw = [
        sum(((case >> bit) & 1) << case for case in range(assignments))
        for bit in range(inputs)
    ]
    source_tables = [value for item in raw for value in (item, full ^ item)]
    source_names = [name for bit in range(inputs) for name in (f"x{bit}", f"not_x{bit}")]
    source_tables.extend((0, full))
    source_names.extend(("const0", "const1"))
    source_count = len(source_tables)
    targets = (
        parity_table(inputs, (0, 1, 2, 3)),
        parity_table(inputs, (0, 1, 4, 5)),
    )
    if args.fix_xor_tree and args.slots != len(KNOWN_XOR_TREE):
        raise ValueError("--fix-xor-tree requires exactly 15 slots")

    enc = Encoder()
    values: list[list[int | bool]] = [
        [bool((table >> case) & 1) for case in range(assignments)]
        for table in source_tables
    ]
    kinds: list[list[int]] = []
    levels: list[list[int]] = []
    left_uses: list[list[int]] = []
    right_uses: list[list[int]] = []

    for slot in range(args.slots):
        available = source_count + slot
        slot_kinds = [enc.var(f"kind_{slot}_{kind}") for kind in KINDS]
        enc.exactly_one(slot_kinds)
        slot_levels = [enc.var(f"level_{slot}_{level}") for level in range(1, args.max_delay + 1)]
        enc.exactly_one(slot_levels)
        left = [enc.var(f"left_{slot}_{source}") for source in range(available)]
        right = [enc.var(f"right_{slot}_{source}") for source in range(available)]
        enc.exactly_one(left)
        enc.exactly_one(right)
        # NOT ignores its right input; canonicalize it to source zero.  Other
        # kinds select exactly one right predecessor.
        for source, use in enumerate(right):
            enc.clause((-slot_kinds[NOT], use if source == 0 else -use))
        for left_source in range(available):
            for right_source in range(left_source):
                for operation in COMMUTATIVE:
                    enc.clause((-slot_kinds[operation], -left[left_source], -right[right_source]))
        if args.fix_xor_tree:
            operation, wanted_left, wanted_right, wanted_level = KNOWN_XOR_TREE[slot]
            enc.clause((slot_kinds[operation],))
            enc.clause((left[wanted_left],))
            enc.clause((right[wanted_right],))
            enc.clause((slot_levels[wanted_level - 1],))

        # Chosen level is an upper bound; every selected gate predecessor must
        # lie at least one level earlier.
        for source in range(source_count, available):
            predecessor = source - source_count
            for predecessor_level in range(1, args.max_delay + 1):
                for result_level in range(1, args.max_delay + 1):
                    if result_level <= predecessor_level:
                        enc.clause(
                            (-levels[predecessor][predecessor_level - 1], -left[source], -slot_levels[result_level - 1])
                        )
                        enc.clause(
                            (-levels[predecessor][predecessor_level - 1], -right[source], -slot_levels[result_level - 1])
                        )

        slot_values = []
        for case in range(assignments):
            left_value = enc.var(f"left_value_{slot}_{case}")
            right_value = enc.var(f"right_value_{slot}_{case}")
            for source in range(available):
                source_value = values[source][case]
                enc.clause((-left[source], -left_value, source_value))
                enc.clause((-left[source], left_value, enc.neg(source_value)))
                enc.clause((-right[source], -right_value, source_value))
                enc.clause((-right[source], right_value, enc.neg(source_value)))
            output = enc.var(f"value_{slot}_{case}")
            for operation, literal in enumerate(slot_kinds):
                add_conditional_gate(enc, literal, output, left_value, right_value, operation)
            slot_values.append(output)

        # Adjacent independent gates are sorted by kind.  This is the same
        # complete topological symmetry break used by the physical BUS model.
        if slot:
            dependency = left[source_count + slot - 1]
            dependency_right = right[source_count + slot - 1]
            for previous_kind in range(len(KINDS)):
                for current_kind in range(previous_kind):
                    enc.clause(
                        (
                            dependency,
                            dependency_right,
                            -kinds[slot - 1][previous_kind],
                            -slot_kinds[current_kind],
                        )
                    )

        kinds.append(slot_kinds)
        levels.append(slot_levels)
        left_uses.append(left)
        right_uses.append(right)
        values.append(slot_values)

    output_uses = []
    for output_index, target in enumerate(targets):
        uses = [enc.var(f"output_{output_index}_{source}") for source in range(source_count + args.slots)]
        enc.exactly_one(uses)
        for source, use in enumerate(uses):
            for case in range(assignments):
                wanted = bool((target >> case) & 1)
                value = values[source][case]
                enc.clause((-use, value if wanted else enc.neg(value)))
        output_uses.append(uses)
        if args.fix_xor_tree:
            enc.clause((uses[(23, 28)[output_index]],))

    # Every paid gate is consumed later or selected as an output.
    for slot in range(args.slots):
        source = source_count + slot
        users = [uses[source] for uses in output_uses]
        for later in range(slot + 1, args.slots):
            users.extend((left_uses[later][source], right_uses[later][source]))
        enc.clause(users)

    # Duplicate truth functions are redundant under free fanout.  Excluding
    # them is complete for minimum-size circuits and removes large symmetries.
    for right_source in range(source_count, source_count + args.slots):
        right_values = values[right_source]
        for left_source in range(right_source):
            left_values = values[left_source]
            differences = []
            for case, (left_value, right_value) in enumerate(zip(left_values, right_values, strict=True)):
                if type(left_value) is bool:
                    differences.append(right_value if not left_value else -right_value)
                else:
                    difference = enc.var(f"different_{left_source}_{right_source}_{case}")
                    enc.clause((-difference, left_value, right_value))
                    enc.clause((-difference, -left_value, -right_value))
                    enc.clause((difference, left_value, -right_value))
                    enc.clause((difference, -left_value, right_value))
                    differences.append(difference)
            enc.clause(differences)

    started = time.perf_counter()
    status = "unknown"
    model = None
    reason = None
    with Solver(name=args.solver, bootstrap_with=enc.cnf) as solver:
        timer = threading.Timer(args.timeout, solver.interrupt) if args.timeout > 0 else None
        if timer:
            timer.start()
        try:
            answer = solver.solve_limited(expect_interrupt=True)
        finally:
            if timer:
                timer.cancel()
        if answer is True:
            status = "sat"
            model = solver.get_model()
        elif answer is False:
            status = "unsat"
        else:
            reason = "timeout"

    payload: dict[str, object] = {
        "schema": 1,
        "model": "single-driver ordinary-gate exact CNF with free input complements",
        "status": status,
        "slots": args.slots,
        "max_delay": args.max_delay,
        "inputs": inputs,
        "source_names": source_names,
        "targets_hex": [f"{target:016x}" for target in targets],
        "library": {kind: [1, 1] for kind in KINDS},
        "solver": args.solver,
        "timeout_seconds": args.timeout,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "free_complements": True,
        "physical_reason": "without Switch, every useful net has one active driver",
        "fixed_xor_tree": args.fix_xor_tree,
    }
    if reason:
        payload["reason_unknown"] = reason
    if status == "sat" and model is not None:
        enabled = {literal for literal in model if literal > 0}
        gates = []
        for slot in range(args.slots):
            operation = next(index for index, literal in enumerate(kinds[slot]) if literal in enabled)
            left = next(index for index, literal in enumerate(left_uses[slot]) if literal in enabled)
            right = next(index for index, literal in enumerate(right_uses[slot]) if literal in enabled)
            level = next(index + 1 for index, literal in enumerate(levels[slot]) if literal in enabled)
            gates.append({"slot": slot, "source": source_count + slot, "kind": KINDS[operation], "left": left, "right": right, "level": level})
        payload["gates"] = gates
        payload["outputs"] = [next(index for index, literal in enumerate(uses) if literal in enabled) for uses in output_uses]
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slots", type=int, required=True)
    parser.add_argument("--max-delay", type=int, default=4)
    parser.add_argument("--solver", default="maplecm")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--fix-xor-tree", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = solve(args)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.write_text(encoded, encoding="utf-8")
    print(json.dumps({"status": payload["status"], "seconds": payload["solve_seconds"], "variables": payload["variables"], "clauses": payload["clauses"]}))
    print(f"sha256={sha256(encoded.encode()).hexdigest()}")
    return 2 if payload["status"] == "unknown" else 0


if __name__ == "__main__":
    raise SystemExit(main())
