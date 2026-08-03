"""Exact bounded synthesis of small multi-output adder blocks.

The encoding uses the reviewed Turing Complete primitive costs and three-state
Switch semantics.  It deliberately requires every primary output to be driven
on every assignment; a high-impedance output is not accepted as numeric zero.

This research-only script imports the already audited generic CNF helpers from
``.research/rng_468_joint_macro/joint_parity_cnf.py``.  It never reads or writes
the game save.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import threading
import time
from typing import Iterable

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[2]
GENERIC_PATH = ROOT / ".research/rng_468_joint_macro/joint_parity_cnf.py"


def load_generic():
    spec = importlib.util.spec_from_file_location("tc_joint_switch_cnf", GENERIC_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generic encoder: {GENERIC_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


G = load_generic()


def adder_targets(bits: int) -> tuple[int, tuple[int, ...]]:
    """Return input count and packed Sum/Cout truth tables.

    Input order is ``a[0..bits-1], b[0..bits-1], cin``.  Outputs are
    ``sum[0..bits-1], cout``.
    """

    inputs = 2 * bits + 1
    assignments = 1 << inputs
    targets = [0] * (bits + 1)
    word_mask = (1 << bits) - 1
    for case in range(assignments):
        a = case & word_mask
        b = (case >> bits) & word_mask
        cin = (case >> (2 * bits)) & 1
        total = a + b + cin
        for output in range(bits + 1):
            targets[output] |= ((total >> output) & 1) << case
    return inputs, tuple(targets)


def output_bus(
    enc,
    name: str,
    selected: list[int],
    driver_values: list[object],
    driver_drivens: list[object],
) -> tuple[int, int]:
    """Resolve a conflict-free bus and expose both value and driven state."""

    one_terms = []
    zero_terms = []
    for index, (use, value, driven) in enumerate(
        zip(selected, driver_values, driver_drivens, strict=True)
    ):
        one_terms.append(
            enc.and_term(f"{name}_one_term_{index}", (use, driven, value))
        )
        zero_terms.append(
            enc.and_term(
                f"{name}_zero_term_{index}",
                (use, driven, enc.neg(value)),
            )
        )
    ones = enc.var(f"{name}_ones")
    zeros = enc.var(f"{name}_zeros")
    enc.equiv_or(ones, one_terms)
    enc.equiv_or(zeros, zero_terms)
    enc.clause((-ones, -zeros))
    driven = enc.var(f"{name}_driven")
    enc.equiv_or(driven, (ones, zeros))
    return ones, driven


def _at_most_weighted(enc, kinds: list[list[int]], gate_bound: int) -> None:
    weighted = []
    for slot_kinds in kinds:
        for candidate, literal in enumerate(slot_kinds):
            weighted.extend([literal] * G.COST[candidate])
    enc.cnf.extend(
        CardEnc.atmost(
            lits=weighted,
            bound=gate_bound,
            vpool=enc.pool,
            encoding=EncType.seqcounter,
        ).clauses
    )


def build(
    bits: int,
    gate_bound: int,
    max_delay: int,
    components: int,
    *,
    exact_switches: int | None = None,
    exact_xors: int | None = None,
    single_driver: bool = False,
) -> tuple[object, dict[str, object]]:
    inputs, targets = adder_targets(bits)
    assignments = 1 << inputs
    enc = G.Encoder()

    # Raw primary inputs and free constants only.  Complements are not free.
    source_values: list[list[object]] = [
        [bool((case >> bit) & 1) for case in range(assignments)]
        for bit in range(inputs)
    ]
    source_values.extend(([False] * assignments, [True] * assignments))
    source_count = len(source_values)
    values: list[list[object]] = list(source_values)
    drivens: list[list[object]] = [[True] * assignments for _ in values]

    kinds: list[list[int]] = []
    levels: list[list[int]] = []
    left_uses: list[list[int]] = []
    right_uses: list[list[int]] = []

    for slot in range(components):
        available = source_count + slot
        slot_kinds = [enc.var(f"kind_{slot}_{name}") for name in G.KINDS]
        enc.exactly_one(slot_kinds)
        slot_levels = [
            enc.var(f"depth_{slot}_{depth}") for depth in range(1, max_delay + 1)
        ]
        enc.exactly_one(slot_levels)
        left = [enc.var(f"left_{slot}_{source}") for source in range(available)]
        right = [enc.var(f"right_{slot}_{source}") for source in range(available)]
        if single_driver:
            enc.exactly_one(left)
            enc.cnf.extend(
                CardEnc.atmost(
                    lits=right,
                    bound=1,
                    vpool=enc.pool,
                    encoding=EncType.seqcounter,
                ).clauses
            )
        else:
            enc.clause(left)
        for use in right:
            enc.clause((-slot_kinds[G.NOT], -use))
        enc.clause((slot_kinds[G.NOT], *right))
        G._restrict_active_bus_to_switches(enc, left, source_count, kinds)
        G._restrict_active_bus_to_switches(enc, right, source_count, kinds)
        for candidate in G.COMMUTATIVE:
            G._add_commutative_order(
                enc,
                slot_kinds[candidate],
                left,
                right,
                f"order_{slot}_{candidate}",
            )

        for candidate, delay in enumerate(G.DELAY):
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

        slot_values = []
        slot_drivens = []
        for case in range(assignments):
            driver_values = [row[case] for row in values]
            driver_drivens = [row[case] for row in drivens]
            lv = enc.bus_case(
                f"left_{slot}_case_{case}", left, driver_values, driver_drivens
            )
            rv = enc.bus_case(
                f"right_{slot}_case_{case}", right, driver_values, driver_drivens
            )
            out = enc.var(f"value_{slot}_{case}")
            driven = enc.var(f"driven_{slot}_{case}")
            G._conditional_equiv_not(enc, slot_kinds[G.NOT], out, lv)
            G._conditional_equiv_and(enc, slot_kinds[G.AND], out, lv, rv)
            G._conditional_equiv_or(enc, slot_kinds[G.OR], out, lv, rv)
            G._conditional_equiv_nand(enc, slot_kinds[G.NAND], out, lv, rv)
            G._conditional_equiv_nor(enc, slot_kinds[G.NOR], out, lv, rv)
            G._conditional_equiv_xor(enc, slot_kinds[G.XOR], out, lv, rv)
            G._conditional_equiv_and(enc, slot_kinds[G.SWITCH], out, lv, rv)
            enc.clause((-slot_kinds[G.SWITCH], -driven, lv))
            enc.clause((-slot_kinds[G.SWITCH], driven, -lv))
            for candidate in range(G.SWITCH):
                enc.clause((-slot_kinds[candidate], driven))
            slot_values.append(out)
            slot_drivens.append(driven)

        kinds.append(slot_kinds)
        levels.append(slot_levels)
        left_uses.append(left)
        right_uses.append(right)
        values.append(slot_values)
        drivens.append(slot_drivens)

    _at_most_weighted(enc, kinds, gate_bound)
    if exact_switches is not None:
        enc.cnf.extend(
            CardEnc.equals(
                lits=[row[G.SWITCH] for row in kinds],
                bound=exact_switches,
                vpool=enc.pool,
                encoding=EncType.seqcounter,
            ).clauses
        )
    if exact_xors is not None:
        enc.cnf.extend(
            CardEnc.equals(
                lits=[row[G.XOR] for row in kinds],
                bound=exact_xors,
                vpool=enc.pool,
                encoding=EncType.seqcounter,
            ).clauses
        )

    output_uses: list[list[int]] = []
    for output_index, target in enumerate(targets):
        uses = [
            enc.var(f"output_{output_index}_{source}")
            for source in range(source_count + components)
        ]
        if single_driver:
            enc.exactly_one(uses)
        else:
            enc.clause(uses)
        G._restrict_active_bus_to_switches(enc, uses, source_count, kinds)
        for case in range(assignments):
            value, driven = output_bus(
                enc,
                f"output_{output_index}_case_{case}",
                uses,
                [row[case] for row in values],
                [row[case] for row in drivens],
            )
            enc.force(value, bool((target >> case) & 1))
            enc.force(driven, True)
        output_uses.append(uses)

    # Every component must affect a later component or a primary output.
    for slot in range(components):
        source = source_count + slot
        users = [uses[source] for uses in output_uses]
        for later in range(slot + 1, components):
            users.extend((left_uses[later][source], right_uses[later][source]))
        enc.clause(users)

    return enc, {
        "inputs": inputs,
        "targets": targets,
        "source_count": source_count,
        "kinds": kinds,
        "levels": levels,
        "left_uses": left_uses,
        "right_uses": right_uses,
        "output_uses": output_uses,
        "single_driver": single_driver,
    }


def _selected(model: list[int]) -> set[int]:
    return {literal for literal in model if literal > 0}


def decode(args: argparse.Namespace, state: dict[str, object], model: list[int]) -> dict[str, object]:
    enabled = _selected(model)
    source_count = int(state["source_count"])
    kinds = state["kinds"]
    levels = state["levels"]
    left_uses = state["left_uses"]
    right_uses = state["right_uses"]
    output_uses = state["output_uses"]
    network = []
    actual_gate = 0
    for slot in range(args.components):
        candidate = next(i for i, literal in enumerate(kinds[slot]) if literal in enabled)
        actual_gate += G.COST[candidate]
        depth = next(i + 1 for i, literal in enumerate(levels[slot]) if literal in enabled)
        network.append(
            {
                "slot": slot,
                "source": source_count + slot,
                "kind": G.KINDS[candidate],
                "left_bus": [i for i, literal in enumerate(left_uses[slot]) if literal in enabled],
                "right_bus": [i for i, literal in enumerate(right_uses[slot]) if literal in enabled],
                "cost": G.COST[candidate],
                "depth_upper_bound": depth,
            }
        )
    return {
        "actual_gate": actual_gate,
        "network": network,
        "output_buses": [
            [i for i, literal in enumerate(uses) if literal in enabled]
            for uses in output_uses
        ],
    }


def verify_payload(payload: dict[str, object]) -> dict[str, object]:
    """Independently replay a decoded SAT witness with value/Z semantics."""

    bits = int(payload["bits"])
    inputs, targets = adder_targets(bits)
    assignments = 1 << inputs
    source_count = inputs + 2
    network = payload["network"]
    output_buses = payload["output_buses"]
    max_seen_depth = 0
    mismatch_count = 0
    conflict_count = 0
    undriven_count = 0

    for case in range(assignments):
        values = [bool((case >> bit) & 1) for bit in range(inputs)] + [False, True]
        drivens = [True] * source_count
        depths = [0] * source_count

        def resolve(bus: list[int]) -> tuple[bool, bool]:
            nonlocal conflict_count
            active = {values[source] for source in bus if drivens[source]}
            if len(active) > 1:
                conflict_count += 1
                return False, True
            if not active:
                return False, False
            return next(iter(active)), True

        for item in network:
            left, _left_driven = resolve(item["left_bus"])
            right, _right_driven = resolve(item["right_bus"])
            kind = item["kind"]
            if kind == "NOT":
                value, driven = not left, True
            elif kind == "AND":
                value, driven = left and right, True
            elif kind == "OR":
                value, driven = left or right, True
            elif kind == "NAND":
                value, driven = not (left and right), True
            elif kind == "NOR":
                value, driven = not (left or right), True
            elif kind == "XOR":
                value, driven = left ^ right, True
            elif kind == "SWITCH":
                value, driven = left and right, left
            else:  # pragma: no cover
                raise AssertionError(kind)
            values.append(bool(value))
            drivens.append(bool(driven))
            input_depth = max(
                (depths[source] for source in item["left_bus"] + item["right_bus"]),
                default=0,
            )
            depth = input_depth + G.DELAY[G.KINDS.index(kind)]
            depths.append(depth)
            max_seen_depth = max(max_seen_depth, depth)

        for output, bus in enumerate(output_buses):
            value, driven = resolve(bus)
            if not driven:
                undriven_count += 1
            wanted = bool((targets[output] >> case) & 1)
            if not driven or value != wanted:
                mismatch_count += 1

    return {
        "assignments": assignments,
        "output_checks": assignments * (bits + 1),
        "mismatch_count": mismatch_count,
        "bus_conflict_count": conflict_count,
        "undriven_output_count": undriven_count,
        "replayed_max_component_depth": max_seen_depth,
    }


def solve(args: argparse.Namespace) -> dict[str, object]:
    started = time.perf_counter()
    enc, state = build(
        args.bits,
        args.gate_bound,
        args.max_delay,
        args.components,
        exact_switches=args.switches,
        exact_xors=args.xors,
        single_driver=args.single_driver,
    )
    timer = None
    model = None
    status = "unknown"
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

    inputs, targets = adder_targets(args.bits)
    payload: dict[str, object] = {
        "schema": "exact-adder-block-switch-cnf-v1",
        "status": status,
        "bits": args.bits,
        "inputs": inputs,
        "target_truth_tables_hex": [
            f"{target:0{(1 << inputs) // 4}x}" for target in targets
        ],
        "gate_bound": args.gate_bound,
        "max_delay": args.max_delay,
        "components": args.components,
        "exact_switches": args.switches,
        "exact_xors": args.xors,
        "single_driver": args.single_driver,
        "solver": args.solver,
        "timeout_seconds": args.timeout,
        "conflict_budget": args.conflicts,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "library": {
            name: {"gate": G.COST[i], "delay": G.DELAY[i]}
            for i, name in enumerate(G.KINDS)
        },
        "semantics": {
            "switch": "enable=0 -> Z; enable=1 -> data",
            "ordinary_gate_reads_z_as_zero": True,
            "multi_driver_conflict_forbidden": True,
            "primary_outputs_must_be_driven": True,
            "free_sources": "raw inputs plus constants 0 and 1; no free complements",
        },
    }
    if model is not None:
        payload.update(decode(args, state, model))
        payload["verification"] = verify_payload(payload)
        if any(
            payload["verification"][key]
            for key in ("mismatch_count", "bus_conflict_count", "undriven_output_count")
        ):
            raise RuntimeError("decoded witness failed independent replay")
    elif status == "unknown":
        payload["reason_unknown"] = "timeout-or-conflict-budget"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, choices=(1, 2, 3, 4), required=True)
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int)
    parser.add_argument("--single-driver", action="store_true")
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
