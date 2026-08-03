"""CNF superoptimizer for jointly generated parity outputs.

The first target family is the pair

``(a xor b xor c, a xor b xor d)``.

It models the common fanout pattern in the verified 468/8/67 RNG: one
first-layer parity feeds two second-layer results.  A physical component may
fan out to both output buses, so this closes a gap left by single-output
parity lower bounds.  Switches use the current game's value/Z semantics and
all zero-cost buses must be conflict-free on every assignment.
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


KINDS = ("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH")
NOT, AND, OR, NAND, NOR, XOR, SWITCH = range(len(KINDS))
COST = (1, 1, 1, 1, 1, 3, 2)
DELAY = (1, 1, 1, 1, 1, 2, 1)
COMMUTATIVE = frozenset((AND, OR, NAND, NOR, XOR))
Lit = int | bool


class Encoder:
    def __init__(self) -> None:
        self.pool = IDPool()
        self.cnf = CNF()

    def var(self, name: str) -> int:
        return self.pool.id(name)

    @staticmethod
    def neg(value: Lit) -> Lit:
        return not value if isinstance(value, bool) else -value

    def clause(self, values: Iterable[Lit]) -> None:
        literals: list[int] = []
        for value in values:
            if value is True:
                return
            if value is False:
                continue
            literals.append(value)
        self.cnf.append(literals)

    def force(self, value: Lit, wanted: bool) -> None:
        self.clause((value if wanted else self.neg(value),))

    def exactly_one(self, values: list[int]) -> None:
        self.cnf.extend(
            CardEnc.equals(
                values,
                bound=1,
                vpool=self.pool,
                encoding=EncType.seqcounter,
            ).clauses
        )

    def and_term(self, name: str, values: Iterable[Lit]) -> Lit:
        terms: list[int] = []
        for value in values:
            if value is False:
                return False
            if value is True:
                continue
            terms.append(value)
        terms = list(dict.fromkeys(terms))
        if not terms:
            return True
        if len(terms) == 1:
            return terms[0]
        output = self.var(name)
        for value in terms:
            self.clause((-output, value))
        self.clause((output, *(-value for value in terms)))
        return output

    def equiv_or(self, output: int, values: Iterable[Lit]) -> None:
        terms: list[int] = []
        for value in values:
            if value is True:
                self.force(output, True)
                return
            if value is False:
                continue
            terms.append(value)
        terms = list(dict.fromkeys(terms))
        if not terms:
            self.force(output, False)
            return
        for value in terms:
            self.clause((-value, output))
        self.clause((-output, *terms))

    def bus_case(
        self,
        name: str,
        selected: list[int],
        driver_values: list[Lit],
        driver_drivens: list[Lit],
    ) -> int:
        one_terms: list[Lit] = []
        zero_terms: list[Lit] = []
        for index, (use, value, driven) in enumerate(
            zip(selected, driver_values, driver_drivens, strict=True)
        ):
            one_terms.append(
                self.and_term(f"{name}_one_term_{index}", (use, driven, value))
            )
            zero_terms.append(
                self.and_term(
                    f"{name}_zero_term_{index}",
                    (use, driven, self.neg(value)),
                )
            )
        ones = self.var(f"{name}_ones")
        zeros = self.var(f"{name}_zeros")
        self.equiv_or(ones, one_terms)
        self.equiv_or(zeros, zero_terms)
        self.clause((-ones, -zeros))
        return ones


def _conditional_equiv_not(enc: Encoder, kind: int, out: int, value: Lit) -> None:
    enc.clause((-kind, out, value))
    enc.clause((-kind, -out, enc.neg(value)))


def _conditional_equiv_and(
    enc: Encoder, kind: int, out: int, left: Lit, right: Lit
) -> None:
    enc.clause((-kind, -out, left))
    enc.clause((-kind, -out, right))
    enc.clause((-kind, out, enc.neg(left), enc.neg(right)))


def _conditional_equiv_or(
    enc: Encoder, kind: int, out: int, left: Lit, right: Lit
) -> None:
    enc.clause((-kind, out, enc.neg(left)))
    enc.clause((-kind, out, enc.neg(right)))
    enc.clause((-kind, -out, left, right))


def _conditional_equiv_nand(
    enc: Encoder, kind: int, out: int, left: Lit, right: Lit
) -> None:
    enc.clause((-kind, out, left))
    enc.clause((-kind, out, right))
    enc.clause((-kind, -out, enc.neg(left), enc.neg(right)))


def _conditional_equiv_nor(
    enc: Encoder, kind: int, out: int, left: Lit, right: Lit
) -> None:
    enc.clause((-kind, enc.neg(left), -out))
    enc.clause((-kind, enc.neg(right), -out))
    enc.clause((-kind, left, right, out))


def _conditional_equiv_xor(
    enc: Encoder, kind: int, out: int, left: Lit, right: Lit
) -> None:
    enc.clause((-kind, enc.neg(left), enc.neg(right), -out))
    enc.clause((-kind, left, right, -out))
    enc.clause((-kind, left, enc.neg(right), out))
    enc.clause((-kind, enc.neg(left), right, out))


def _add_commutative_order(
    enc: Encoder, kind: int, left: list[int], right: list[int], name: str
) -> None:
    # Witness the most-significant differing selector: left=0, right=1.
    witnesses = []
    for index in range(len(left)):
        witness = enc.var(f"{name}_less_at_{index}")
        witnesses.append(witness)
        enc.clause((-witness, -left[index]))
        enc.clause((-witness, right[index]))
        for higher in range(index + 1, len(left)):
            enc.clause((-witness, -left[higher], right[higher]))
            enc.clause((-witness, left[higher], -right[higher]))
    enc.clause((-kind, *witnesses))


def _restrict_active_bus_to_switches(
    enc: Encoder,
    selected: list[int],
    source_count: int,
    predecessor_kinds: list[list[int]],
) -> None:
    """Normalize every multi-driver bus to Switch-only drivers.

    A normal output is active on every assignment.  Compatibility therefore
    forces every other selected driver to equal it whenever active, so those
    extra drivers cannot change the resolved signal and can be deleted.  Thus
    any useful bus with two or more drivers consists only of Switch outputs.
    """

    for source, use in enumerate(selected):
        others = selected[:source] + selected[source + 1 :]
        if source < source_count:
            for other in others:
                enc.clause((-use, -other))
            continue
        slot = source - source_count
        for candidate in range(SWITCH):
            for other in others:
                enc.clause((-use, -predecessor_kinds[slot][candidate], -other))


def build(
    inputs: int,
    targets: tuple[int, ...],
    source_mode: str,
    gate_bound: int,
    max_delay: int,
    components: int,
    exact_switches: int | None = None,
    exact_xors: int | None = None,
    exact_output_drivers: int | None = None,
    terminal_switch_drivers: int | None = None,
    fixed_prefix_pair_xors: int | None = None,
) -> tuple[Encoder, dict[str, object]]:
    enc = Encoder()
    assignments = 1 << inputs
    raw_values = [
        [bool((case >> bit) & 1) for case in range(assignments)]
        for bit in range(inputs)
    ]
    if source_mode == "pair-dual-tails":
        if inputs != 4:
            raise ValueError("pair-dual-tails requires four variables")
        source_values = [
            raw_values[0],
            raw_values[1],
            raw_values[2],
            [not value for value in raw_values[2]],
            raw_values[3],
            [not value for value in raw_values[3]],
        ]
    elif source_mode == "all-dual":
        source_values = [
            polarity
            for row in raw_values
            for polarity in (row, [not value for value in row])
        ]
    else:  # pragma: no cover - internal invariant
        raise ValueError(source_mode)
    source_values.extend(
        ([False] * assignments, [True] * assignments)
    )
    source_count = len(source_values)
    values: list[list[Lit]] = list(source_values)
    drivens: list[list[Lit]] = [[True] * assignments for _ in values]

    kinds: list[list[int]] = []
    levels: list[list[int]] = []
    left_uses: list[list[int]] = []
    right_uses: list[list[int]] = []

    for slot in range(components):
        available = source_count + slot
        slot_kinds = [enc.var(f"kind_{slot}_{name}") for name in KINDS]
        enc.exactly_one(slot_kinds)
        slot_levels = [
            enc.var(f"depth_{slot}_{depth}")
            for depth in range(1, max_delay + 1)
        ]
        enc.exactly_one(slot_levels)
        left = [enc.var(f"left_{slot}_{source}") for source in range(available)]
        right = [enc.var(f"right_{slot}_{source}") for source in range(available)]
        enc.clause(left)
        for use in right:
            enc.clause((-slot_kinds[NOT], -use))
        enc.clause((slot_kinds[NOT], *right))
        _restrict_active_bus_to_switches(enc, left, source_count, kinds)
        _restrict_active_bus_to_switches(enc, right, source_count, kinds)
        for candidate in COMMUTATIVE:
            _add_commutative_order(
                enc, slot_kinds[candidate], left, right, f"order_{slot}_{candidate}"
            )

        # A chosen depth is an upper bound on every selected predecessor plus
        # this component's delay.  Overestimation is harmless and preserves
        # completeness while avoiding arithmetic variables.
        for candidate, delay in enumerate(DELAY):
            for result_depth in range(1, delay):
                enc.clause((-slot_kinds[candidate], -slot_levels[result_depth - 1]))
            for source in range(source_count, available):
                predecessor = source - source_count
                for predecessor_depth in range(1, max_delay + 1):
                    for result_depth in range(1, max_delay + 1):
                        if result_depth < predecessor_depth + delay:
                            enc.clause(
                                (
                                    -slot_kinds[candidate],
                                    -levels[predecessor][predecessor_depth - 1],
                                    -left[source],
                                    -slot_levels[result_depth - 1],
                                )
                            )
                            enc.clause(
                                (
                                    -slot_kinds[candidate],
                                    -levels[predecessor][predecessor_depth - 1],
                                    -right[source],
                                    -slot_levels[result_depth - 1],
                                )
                            )

        slot_values: list[Lit] = []
        slot_drivens: list[Lit] = []
        for case in range(assignments):
            driver_values = [row[case] for row in values]
            driver_drivens = [row[case] for row in drivens]
            lv = enc.bus_case(
                f"left_{slot}_case_{case}",
                left,
                driver_values,
                driver_drivens,
            )
            # For NOT, right is empty and therefore resolves numerically to 0.
            rv = enc.bus_case(
                f"right_{slot}_case_{case}",
                right,
                driver_values,
                driver_drivens,
            )
            out = enc.var(f"value_{slot}_{case}")
            driven = enc.var(f"driven_{slot}_{case}")
            _conditional_equiv_not(enc, slot_kinds[NOT], out, lv)
            _conditional_equiv_and(enc, slot_kinds[AND], out, lv, rv)
            _conditional_equiv_or(enc, slot_kinds[OR], out, lv, rv)
            _conditional_equiv_nand(enc, slot_kinds[NAND], out, lv, rv)
            _conditional_equiv_nor(enc, slot_kinds[NOR], out, lv, rv)
            _conditional_equiv_xor(enc, slot_kinds[XOR], out, lv, rv)
            _conditional_equiv_and(enc, slot_kinds[SWITCH], out, lv, rv)
            enc.clause((-slot_kinds[SWITCH], -driven, lv))
            enc.clause((-slot_kinds[SWITCH], driven, -lv))
            for candidate in range(SWITCH):
                enc.clause((-slot_kinds[candidate], driven))
            slot_values.append(out)
            slot_drivens.append(driven)

        kinds.append(slot_kinds)
        levels.append(slot_levels)
        left_uses.append(left)
        right_uses.append(right)
        values.append(slot_values)
        drivens.append(slot_drivens)

    if fixed_prefix_pair_xors is not None:
        if fixed_prefix_pair_xors * 2 > inputs or fixed_prefix_pair_xors > components:
            enc.clause(())
        else:
            for slot in range(fixed_prefix_pair_xors):
                enc.force(kinds[slot][XOR], True)
                for source, use in enumerate(left_uses[slot]):
                    enc.force(use, source == 2 * slot)
                for source, use in enumerate(right_uses[slot]):
                    enc.force(use, source == 2 * slot + 1)

    weighted_literals = []
    for slot_kinds in kinds:
        for candidate, literal in enumerate(slot_kinds):
            # A cardinality network over repeated literals is an exact
            # pseudo-Boolean encoding for these tiny integral costs.  It also
            # avoids the optional pypblib dependency.
            weighted_literals.extend([literal] * COST[candidate])
    enc.cnf.extend(
        CardEnc.atmost(
            lits=weighted_literals,
            bound=gate_bound,
            vpool=enc.pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    if exact_switches is not None:
        enc.cnf.extend(
            CardEnc.equals(
                lits=[slot_kinds[SWITCH] for slot_kinds in kinds],
                bound=exact_switches,
                vpool=enc.pool,
                encoding=EncType.seqcounter,
            ).clauses
        )
    if exact_xors is not None:
        enc.cnf.extend(
            CardEnc.equals(
                lits=[slot_kinds[XOR] for slot_kinds in kinds],
                bound=exact_xors,
                vpool=enc.pool,
                encoding=EncType.seqcounter,
            ).clauses
        )
    if terminal_switch_drivers is not None:
        first_terminal = components - terminal_switch_drivers
        if first_terminal < 0:
            enc.clause(())
        for slot in range(max(0, first_terminal), components):
            enc.force(kinds[slot][SWITCH], True)

    output_uses: list[list[int]] = []
    for output_index, target in enumerate(targets):
        uses = [
            enc.var(f"output_{output_index}_{source}")
            for source in range(source_count + components)
        ]
        enc.clause(uses)
        if exact_output_drivers is not None:
            enc.cnf.extend(
                CardEnc.equals(
                    lits=uses,
                    bound=exact_output_drivers,
                    vpool=enc.pool,
                    encoding=EncType.seqcounter,
                ).clauses
            )
        if terminal_switch_drivers is not None:
            first_terminal_source = (
                source_count + components - terminal_switch_drivers
            )
            for source, use in enumerate(uses):
                if source < first_terminal_source:
                    enc.force(use, False)
        _restrict_active_bus_to_switches(enc, uses, source_count, kinds)
        for case in range(assignments):
            output = enc.bus_case(
                f"output_{output_index}_case_{case}",
                uses,
                [row[case] for row in values],
                [row[case] for row in drivens],
            )
            enc.force(output, bool((target >> case) & 1))
        output_uses.append(uses)

    for slot in range(components):
        source = source_count + slot
        users = [uses[source] for uses in output_uses]
        for later in range(slot + 1, components):
            users.extend((left_uses[later][source], right_uses[later][source]))
        enc.clause(users)

    state = {
        "source_count": source_count,
        "kinds": kinds,
        "levels": levels,
        "left_uses": left_uses,
        "right_uses": right_uses,
        "output_uses": output_uses,
    }
    return enc, state


def solve(args: argparse.Namespace) -> dict[str, object]:
    started = time.perf_counter()
    assignments = 1 << args.inputs
    if args.target_family == "shared-pair":
        if args.inputs != 4:
            raise ValueError("shared-pair requires exactly four inputs")
        source_mode = "pair-dual-tails"
        targets = tuple(
            sum(
                ((((case >> 0) ^ (case >> 1) ^ (case >> tail)) & 1) << case)
                for case in range(assignments)
            )
            for tail in (2, 3)
        )
    elif args.target_family == "dual-shared":
        if args.inputs != 3:
            raise ValueError("dual-shared requires exactly three inputs")
        source_mode = "all-dual"
        targets = tuple(
            sum(
                ((((case >> 0) ^ (case >> tail)) & 1) << case)
                for case in range(assignments)
            )
            for tail in (1, 2)
        )
    else:  # pragma: no cover - argparse constrains this
        raise ValueError(args.target_family)
    enc, state = build(
        args.inputs,
        targets,
        source_mode,
        args.gate_bound,
        args.max_delay,
        args.components,
        args.switches,
        args.xors,
        args.output_drivers,
        args.terminal_switch_drivers,
        args.fixed_prefix_pair_xors,
    )
    timer: threading.Timer | None = None
    model: list[int] | None = None
    status = "unknown"
    reason = None
    with Solver(name=args.solver, bootstrap_with=enc.cnf) as solver:
        if args.conflicts:
            solver.conf_budget(args.conflicts)
        if args.timeout > 0:
            timer = threading.Timer(args.timeout, solver.interrupt)
            timer.start()
        try:
            result = solver.solve_limited(expect_interrupt=True)
        finally:
            if timer is not None:
                timer.cancel()
        if result is True:
            status = "sat"
            model = solver.get_model()
        elif result is False:
            status = "unsat"
        else:
            status = "unknown"
            reason = "timeout-or-conflict-budget"

    payload: dict[str, object] = {
        "schema": 1,
        "model": (
            "joint parity outputs; bit-blasted reviewed gates/Switch; "
            "arbitrary zero-cost compatible Z buses and cross-output fanout"
        ),
        "target_family": args.target_family,
        "source_mode": source_mode,
        "target_truth_tables_hex": [f"{target:0{assignments // 4}x}" for target in targets],
        "status": status,
        "inputs": args.inputs,
        "gate_bound": args.gate_bound,
        "max_delay": args.max_delay,
        "components": args.components,
        "exact_switches": args.switches,
        "exact_xors": args.xors,
        "exact_output_drivers": args.output_drivers,
        "terminal_switch_drivers": args.terminal_switch_drivers,
        "fixed_prefix_pair_xors": args.fixed_prefix_pair_xors,
        "solver": args.solver,
        "timeout_seconds": args.timeout,
        "conflict_budget": args.conflicts,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "library": {
            name: [COST[index], DELAY[index]]
            for index, name in enumerate(KINDS)
        },
        "z_semantics": {
            "switch_value": "enable & data",
            "switch_driven": "enable",
            "ordinary_gate_driven": "all assignments",
            "bus_conflict": "active 0 and active 1 must never overlap",
            "zero_output_may_be_z": True,
        },
    }
    if reason:
        payload["reason_unknown"] = reason
    if status == "sat" and model is not None:
        enabled = {literal for literal in model if literal > 0}
        source_count = int(state["source_count"])
        kinds = state["kinds"]
        levels = state["levels"]
        left_uses = state["left_uses"]
        right_uses = state["right_uses"]
        output_uses = state["output_uses"]
        network = []
        actual_gate = 0
        for slot in range(args.components):
            candidate = next(
                index for index, literal in enumerate(kinds[slot])
                if literal in enabled
            )
            actual_gate += COST[candidate]
            depth = next(
                index + 1 for index, literal in enumerate(levels[slot])
                if literal in enabled
            )
            network.append(
                {
                    "slot": slot,
                    "source": source_count + slot,
                    "kind": KINDS[candidate],
                    "left_bus": [
                        index for index, literal in enumerate(left_uses[slot])
                        if literal in enabled
                    ],
                    "right_bus": [
                        index for index, literal in enumerate(right_uses[slot])
                        if literal in enabled
                    ],
                    "cost": COST[candidate],
                    "depth_upper_bound": depth,
                }
            )
        payload["actual_gate"] = actual_gate
        payload["network"] = network
        payload["output_buses"] = [
            [
                index for index, literal in enumerate(uses)
                if literal in enabled
            ]
            for uses in output_uses
        ]
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=int, choices=(3, 4), default=4)
    parser.add_argument(
        "--target-family",
        choices=("shared-pair", "dual-shared"),
        default="shared-pair",
    )
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int, default=4)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int)
    parser.add_argument("--output-drivers", type=int)
    parser.add_argument("--terminal-switch-drivers", type=int)
    parser.add_argument("--fixed-prefix-pair-xors", type=int)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--conflicts", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = solve(args)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
