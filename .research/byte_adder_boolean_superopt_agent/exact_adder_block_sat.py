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


def adder_targets(bits: int, dual_cout: bool = False) -> tuple[int, tuple[int, ...]]:
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
    if dual_cout:
        targets.append(((1 << assignments) - 1) ^ targets[-1])
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


def _enforce_physical_net_partition(
    enc,
    buses: list[tuple[str, list[int]]],
) -> None:
    """Require abstract resolved buses to form physical wire-net partitions.

    A component output pin may fan out to several sinks, so identical driver
    sets are allowed.  Two different physical nets cannot partially share a
    driver pin: if any source occurs in both buses, all their selected sources
    must be identical.  Without this rule, one Switch output can incorrectly
    be reused as an isolating driver in two independently resolved buses.
    """

    for left_index, (left_name, left) in enumerate(buses):
        for right_name, right in buses[left_index + 1 :]:
            common = min(len(left), len(right))
            overlap_terms = [
                enc.and_term(
                    f"physical_overlap_{left_name}_{right_name}_{source}",
                    (left[source], right[source]),
                )
                for source in range(common)
            ]
            overlap = enc.var(f"physical_overlap_{left_name}_{right_name}")
            enc.equiv_or(overlap, overlap_terms)
            union = max(len(left), len(right))
            for source in range(union):
                left_use = left[source] if source < len(left) else None
                right_use = right[source] if source < len(right) else None
                if left_use is None:
                    enc.clause((-overlap, -right_use))
                elif right_use is None:
                    enc.clause((-overlap, -left_use))
                else:
                    enc.clause((-overlap, -left_use, right_use))
                    enc.clause((-overlap, left_use, -right_use))


def build(
    bits: int,
    gate_bound: int,
    max_delay: int,
    components: int,
    *,
    exact_switches: int | None = None,
    exact_xors: int | None = None,
    single_driver: bool = False,
    cin_arrival: int = 0,
    output_deadlines: tuple[int, ...] | None = None,
    dual_cin: bool = False,
    dual_cout: bool = False,
    allow_z_false: bool = False,
    allow_z_false_outputs: tuple[bool, ...] | None = None,
    physical_nets: bool = True,
) -> tuple[object, dict[str, object]]:
    inputs, targets = adder_targets(bits, dual_cout)
    assignments = 1 << inputs
    enc = G.Encoder()

    # Raw primary inputs and free constants only.  Complements are not free.
    source_values: list[list[object]] = [
        [bool((case >> bit) & 1) for case in range(assignments)]
        for bit in range(inputs)
    ]
    if dual_cin:
        source_values.append(
            [not bool((case >> (2 * bits)) & 1) for case in range(assignments)]
        )
    source_values.extend(([False] * assignments, [True] * assignments))
    source_count = len(source_values)
    source_arrivals = [0] * source_count
    source_arrivals[2 * bits] = cin_arrival
    if dual_cin:
        source_arrivals[inputs] = cin_arrival
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
            for source, source_arrival in enumerate(source_arrivals):
                for result_depth in range(1, max_delay + 1):
                    if result_depth < source_arrival + delay:
                        enc.clause(
                            (
                                -slot_kinds[candidate],
                                -left[source],
                                -slot_levels[result_depth - 1],
                            )
                        )
                        enc.clause(
                            (
                                -slot_kinds[candidate],
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
    if allow_z_false_outputs is None:
        allow_z_false_outputs = tuple([allow_z_false] * len(targets))
    if len(allow_z_false_outputs) != len(targets):
        raise ValueError("allow_z_false_outputs must match target count")
    for output_index, target in enumerate(targets):
        deadline = (
            output_deadlines[output_index]
            if output_deadlines is not None
            else max_delay
        )
        uses = [
            enc.var(f"output_{output_index}_{source}")
            for source in range(source_count + components)
        ]
        if single_driver:
            enc.exactly_one(uses)
        else:
            enc.clause(uses)
        G._restrict_active_bus_to_switches(enc, uses, source_count, kinds)
        for source, source_arrival in enumerate(source_arrivals):
            if source_arrival > deadline:
                enc.clause((-uses[source],))
        for slot, slot_levels in enumerate(levels):
            source = source_count + slot
            for depth, level_literal in enumerate(slot_levels, start=1):
                if depth > deadline:
                    enc.clause((-uses[source], -level_literal))
        for case in range(assignments):
            value, driven = output_bus(
                enc,
                f"output_{output_index}_case_{case}",
                uses,
                [row[case] for row in values],
                [row[case] for row in drivens],
            )
            enc.force(value, bool((target >> case) & 1))
            if not allow_z_false_outputs[output_index] or ((target >> case) & 1):
                enc.force(driven, True)
        output_uses.append(uses)

    if physical_nets:
        resolved_buses: list[tuple[str, list[int]]] = []
        for slot, (left, right) in enumerate(zip(left_uses, right_uses, strict=True)):
            resolved_buses.append((f"slot{slot}_left", left))
            resolved_buses.append((f"slot{slot}_right", right))
        resolved_buses.extend(
            (f"output{output}", uses)
            for output, uses in enumerate(output_uses)
        )
        _enforce_physical_net_partition(enc, resolved_buses)

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
        "source_arrivals": source_arrivals,
        "output_deadlines": output_deadlines,
        "dual_cin": dual_cin,
        "dual_cout": dual_cout,
        "allow_z_false": allow_z_false,
        "allow_z_false_outputs": allow_z_false_outputs,
        "physical_nets": physical_nets,
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
    dual_cin = bool(payload.get("dual_cin", False))
    dual_cout = bool(payload.get("dual_cout", False))
    inputs, targets = adder_targets(bits, dual_cout)
    assignments = 1 << inputs
    source_count = inputs + 2 + int(dual_cin)
    network = payload["network"]
    output_buses = payload["output_buses"]
    max_seen_depth = 0
    mismatch_count = 0
    conflict_count = 0
    undriven_count = 0
    allowed_z_zero_count = 0
    allow_z_false = bool(payload.get("allow_z_false", False))
    allow_z_false_outputs = payload.get("allow_z_false_outputs")
    if allow_z_false_outputs is None:
        allow_z_false_outputs = [allow_z_false] * len(targets)

    for case in range(assignments):
        values = [bool((case >> bit) & 1) for bit in range(inputs)]
        if dual_cin:
            values.append(not values[2 * bits])
        values.extend([False, True])
        drivens = [True] * source_count
        depths = [0] * source_count
        depths[2 * bits] = int(payload.get("cin_arrival", 0))
        if dual_cin:
            depths[inputs] = int(payload.get("cin_arrival", 0))

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
            wanted = bool((targets[output] >> case) & 1)
            output_allows_z = bool(allow_z_false_outputs[output])
            if not driven and (wanted or not output_allows_z):
                undriven_count += 1
            elif not driven:
                allowed_z_zero_count += 1
            if (not driven and (wanted or not output_allows_z)) or value != wanted:
                mismatch_count += 1

    resolved_buses: list[tuple[str, frozenset[int]]] = []
    for index, item in enumerate(network):
        resolved_buses.append((f"slot{index}_left", frozenset(item["left_bus"])))
        resolved_buses.append((f"slot{index}_right", frozenset(item["right_bus"])))
    resolved_buses.extend(
        (f"output{index}", frozenset(bus))
        for index, bus in enumerate(output_buses)
    )
    physical_violations = []
    for left_index, (left_name, left_bus) in enumerate(resolved_buses):
        for right_name, right_bus in resolved_buses[left_index + 1 :]:
            shared = left_bus & right_bus
            if shared and left_bus != right_bus:
                physical_violations.append(
                    {
                        "left": left_name,
                        "right": right_name,
                        "shared_sources": sorted(shared),
                        "left_only": sorted(left_bus - right_bus),
                        "right_only": sorted(right_bus - left_bus),
                    }
                )

    return {
        "assignments": assignments,
        "output_checks": assignments * len(targets),
        "mismatch_count": mismatch_count,
        "bus_conflict_count": conflict_count,
        "undriven_output_count": undriven_count,
        "allowed_z_zero_count": allowed_z_zero_count,
        "physical_net_partition_violation_count": len(physical_violations),
        "physical_net_partition_violations": physical_violations,
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
        cin_arrival=args.cin_arrival,
        output_deadlines=(
            tuple(
                [args.sum_deadline] * args.bits
                + [args.carry_deadline]
                + ([args.carry_bar_deadline] if args.dual_cout else [])
            )
            if args.sum_deadline is not None and args.carry_deadline is not None
            else None
        ),
        dual_cin=args.dual_cin,
        dual_cout=args.dual_cout,
        allow_z_false=args.allow_z_false,
        allow_z_false_outputs=getattr(args, "allow_z_false_outputs", None),
        physical_nets=not getattr(args, "abstract_buses", False),
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

    inputs, targets = adder_targets(args.bits, args.dual_cout)
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
        "cin_arrival": args.cin_arrival,
        "sum_deadline": args.sum_deadline,
        "carry_deadline": args.carry_deadline,
        "carry_bar_deadline": args.carry_bar_deadline,
        "dual_cin": args.dual_cin,
        "dual_cout": args.dual_cout,
        "allow_z_false": args.allow_z_false,
        "allow_z_false_outputs": getattr(args, "allow_z_false_outputs", None),
        "physical_nets": not getattr(args, "abstract_buses", False),
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
            "primary_outputs_must_be_driven": not args.allow_z_false,
            "internal_transfer_outputs_may_use_z_for_zero": args.allow_z_false,
            "free_sources": "raw inputs plus constants 0 and 1; no free complements",
        },
    }
    if model is not None:
        payload.update(decode(args, state, model))
        payload["verification"] = verify_payload(payload)
        if any(
            payload["verification"][key]
            for key in (
                "mismatch_count",
                "bus_conflict_count",
                "undriven_output_count",
                "physical_net_partition_violation_count",
            )
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
    parser.add_argument("--cin-arrival", type=int, default=0)
    parser.add_argument("--sum-deadline", type=int)
    parser.add_argument("--carry-deadline", type=int)
    parser.add_argument("--carry-bar-deadline", type=int)
    parser.add_argument("--dual-cin", action="store_true")
    parser.add_argument("--dual-cout", action="store_true")
    parser.add_argument("--allow-z-false", action="store_true")
    parser.add_argument("--abstract-buses", action="store_true")
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--conflicts", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if (args.sum_deadline is None) != (args.carry_deadline is None):
        parser.error("--sum-deadline and --carry-deadline must be used together")
    if args.dual_cout != (args.carry_bar_deadline is not None):
        parser.error("--dual-cout and --carry-bar-deadline must be used together")
    deadlines = [
        value
        for value in (args.sum_deadline, args.carry_deadline, args.carry_bar_deadline)
        if value is not None
    ]
    if deadlines and max(deadlines) > args.max_delay:
        parser.error("output deadlines must not exceed --max-delay")
    payload = solve(args)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
