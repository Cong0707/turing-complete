"""Exact synthesis of small carry/transfer blocks under the TC Switch model.

The fixed 48-gate Byte Adder shell already pays for per-bit G/Q/P and Sum
phase gates.  ``--free-gp`` therefore exposes those reviewed signals at their
real arrivals (G,Q at 1; P at 2) without charging them again.  Every synthesized
component is additional carry-network cost.
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

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / ".research/byte_adder_boolean_superopt_agent/exact_adder_block_sat.py"


def load_base():
    spec = importlib.util.spec_from_file_location("tc_exact_adder_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_base()
G = B.G


def problem(bits: int, mode: str, free_gp: bool):
    inputs = 2 * bits + 1
    assignments = 1 << inputs
    mask = (1 << bits) - 1
    source_values = [
        [bool((case >> index) & 1) for case in range(assignments)]
        for index in range(inputs)
    ]
    source_arrivals = [0] * inputs
    source_names = [
        *[f"a{bit}" for bit in range(bits)],
        *[f"b{bit}" for bit in range(bits)],
        "cin",
    ]
    if free_gp:
        for bit in range(bits):
            a = source_values[bit]
            b = source_values[bits + bit]
            source_values.extend(
                (
                    [x and y for x, y in zip(a, b, strict=True)],
                    [not (x or y) for x, y in zip(a, b, strict=True)],
                    [x != y for x, y in zip(a, b, strict=True)],
                )
            )
            source_arrivals.extend((1, 1, 2))
            source_names.extend((f"g{bit}", f"q{bit}", f"p{bit}"))
    source_values.extend(([False] * assignments, [True] * assignments))
    source_arrivals.extend((0, 0))
    source_names.extend(("0", "1"))

    targets: list[int] = []
    target_names: list[str] = []
    for output in (
        ("carry",)
        if mode == "carry"
        else ("u", "v")
        if mode == "transfer"
        else ("u", "v", "nu", "nv")
    ):
        packed = 0
        for case in range(assignments):
            a = case & mask
            b = (case >> bits) & mask
            cin = (case >> (2 * bits)) & 1
            if output == "carry":
                value = (a + b + cin) >> bits
            elif output == "u":
                value = (a + b) >> bits
            elif output == "v":
                value = (a + b + 1) >> bits
            elif output == "nu":
                value = 1 ^ ((a + b) >> bits)
            else:
                value = 1 ^ ((a + b + 1) >> bits)
            packed |= (value & 1) << case
        targets.append(packed)
        target_names.append(output)
    return (
        inputs,
        assignments,
        source_values,
        source_arrivals,
        source_names,
        tuple(targets),
        tuple(target_names),
    )


def build(args: argparse.Namespace):
    (
        inputs,
        assignments,
        source_values,
        source_arrivals,
        source_names,
        targets,
        target_names,
    ) = problem(args.bits, args.mode, args.free_gp)
    enc = G.Encoder()
    source_count = len(source_values)
    values = list(source_values)
    drivens = [[True] * assignments for _ in values]
    kinds: list[list[int]] = []
    levels: list[list[int]] = []
    left_uses: list[list[int]] = []
    right_uses: list[list[int]] = []

    for slot in range(args.components):
        available = source_count + slot
        slot_kinds = [enc.var(f"kind_{slot}_{name}") for name in G.KINDS]
        enc.exactly_one(slot_kinds)
        slot_levels = [
            enc.var(f"depth_{slot}_{depth}")
            for depth in range(1, args.max_delay + 1)
        ]
        enc.exactly_one(slot_levels)
        left = [enc.var(f"left_{slot}_{source}") for source in range(available)]
        right = [enc.var(f"right_{slot}_{source}") for source in range(available)]
        enc.clause(left)
        for use in right:
            enc.clause((-slot_kinds[G.NOT], -use))
        enc.clause((slot_kinds[G.NOT], *right))
        G._restrict_active_bus_to_switches(enc, left, source_count, kinds)
        G._restrict_active_bus_to_switches(enc, right, source_count, kinds)
        for candidate in G.COMMUTATIVE:
            G._add_commutative_order(
                enc, slot_kinds[candidate], left, right, f"order_{slot}_{candidate}"
            )

        for candidate, delay in enumerate(G.DELAY):
            for result_depth in range(1, delay):
                enc.clause((-slot_kinds[candidate], -slot_levels[result_depth - 1]))
            for source, arrival in enumerate(source_arrivals):
                for result_depth in range(1, args.max_delay + 1):
                    if result_depth < arrival + delay:
                        enc.clause(
                            (-slot_kinds[candidate], -left[source], -slot_levels[result_depth - 1])
                        )
                        enc.clause(
                            (-slot_kinds[candidate], -right[source], -slot_levels[result_depth - 1])
                        )
            for source in range(source_count, available):
                predecessor = source - source_count
                for predecessor_depth in range(1, args.max_delay + 1):
                    for result_depth in range(1, args.max_delay + 1):
                        if result_depth < predecessor_depth + delay:
                            for uses in (left, right):
                                enc.clause(
                                    (
                                        -slot_kinds[candidate],
                                        -levels[predecessor][predecessor_depth - 1],
                                        -uses[source],
                                        -slot_levels[result_depth - 1],
                                    )
                                )

        slot_values = []
        slot_drivens = []
        for case in range(assignments):
            driver_values = [row[case] for row in values]
            driver_drivens = [row[case] for row in drivens]
            lv = enc.bus_case(f"left_{slot}_case_{case}", left, driver_values, driver_drivens)
            rv = enc.bus_case(f"right_{slot}_case_{case}", right, driver_values, driver_drivens)
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

    weighted = []
    for row in kinds:
        for candidate, literal in enumerate(row):
            weighted.extend([literal] * G.COST[candidate])
    enc.cnf.extend(
        CardEnc.atmost(
            lits=weighted,
            bound=args.gate_bound,
            vpool=enc.pool,
            encoding=EncType.seqcounter,
        ).clauses
    )

    output_uses = []
    for output_index, target in enumerate(targets):
        uses = [
            enc.var(f"output_{output_index}_{source}")
            for source in range(source_count + args.components)
        ]
        enc.clause(uses)
        G._restrict_active_bus_to_switches(enc, uses, source_count, kinds)
        for case in range(assignments):
            value, driven = B.output_bus(
                enc,
                f"output_{output_index}_case_{case}",
                uses,
                [row[case] for row in values],
                [row[case] for row in drivens],
            )
            enc.force(value, bool((target >> case) & 1))
            enc.force(driven, True)
        output_uses.append(uses)

    if not args.abstract_buses:
        resolved_buses: list[tuple[str, list[int]]] = []
        for slot, (left, right) in enumerate(zip(left_uses, right_uses, strict=True)):
            resolved_buses.append((f"slot{slot}_left", left))
            resolved_buses.append((f"slot{slot}_right", right))
        resolved_buses.extend(
            (f"output{output}", uses)
            for output, uses in enumerate(output_uses)
        )
        B._enforce_physical_net_partition(enc, resolved_buses)

    for slot in range(args.components):
        source = source_count + slot
        users = [uses[source] for uses in output_uses]
        for later in range(slot + 1, args.components):
            users.extend((left_uses[later][source], right_uses[later][source]))
        enc.clause(users)

    return enc, {
        "inputs": inputs,
        "assignments": assignments,
        "source_count": source_count,
        "source_values": source_values,
        "source_arrivals": source_arrivals,
        "source_names": source_names,
        "targets": targets,
        "target_names": target_names,
        "kinds": kinds,
        "levels": levels,
        "left_uses": left_uses,
        "right_uses": right_uses,
        "output_uses": output_uses,
        "physical_nets": not args.abstract_buses,
    }


def decode(args, state, model):
    enabled = {literal for literal in model if literal > 0}
    source_count = state["source_count"]
    network = []
    actual_gate = 0
    for slot in range(args.components):
        candidate = next(i for i, literal in enumerate(state["kinds"][slot]) if literal in enabled)
        actual_gate += G.COST[candidate]
        depth = next(i + 1 for i, literal in enumerate(state["levels"][slot]) if literal in enabled)
        network.append(
            {
                "slot": slot,
                "source": source_count + slot,
                "kind": G.KINDS[candidate],
                "left_bus": [i for i, literal in enumerate(state["left_uses"][slot]) if literal in enabled],
                "right_bus": [i for i, literal in enumerate(state["right_uses"][slot]) if literal in enabled],
                "cost": G.COST[candidate],
                "depth_upper_bound": depth,
            }
        )
    return {
        "actual_gate": actual_gate,
        "network": network,
        "output_buses": [
            [i for i, literal in enumerate(uses) if literal in enabled]
            for uses in state["output_uses"]
        ],
    }


def verify(payload, state):
    mismatch = conflict = undriven = 0
    max_depth = 0
    for case in range(state["assignments"]):
        values = [bool(row[case]) for row in state["source_values"]]
        drivens = [True] * state["source_count"]
        depths = list(state["source_arrivals"])

        def resolve(bus):
            nonlocal conflict
            active = {values[source] for source in bus if drivens[source]}
            if len(active) > 1:
                conflict += 1
                return False, True
            return (next(iter(active)), True) if active else (False, False)

        for item in payload["network"]:
            left, _ = resolve(item["left_bus"])
            right, _ = resolve(item["right_bus"])
            kind = item["kind"]
            if kind == "NOT": value, driven = not left, True
            elif kind == "AND": value, driven = left and right, True
            elif kind == "OR": value, driven = left or right, True
            elif kind == "NAND": value, driven = not (left and right), True
            elif kind == "NOR": value, driven = not (left or right), True
            elif kind == "XOR": value, driven = left != right, True
            elif kind == "SWITCH": value, driven = left and right, left
            else: raise AssertionError(kind)
            values.append(bool(value)); drivens.append(bool(driven))
            depth = max((depths[source] for source in item["left_bus"] + item["right_bus"]), default=0) + G.DELAY[G.KINDS.index(kind)]
            depths.append(depth); max_depth = max(max_depth, depth)
        for output, bus in enumerate(payload["output_buses"]):
            value, driven = resolve(bus)
            wanted = bool((state["targets"][output] >> case) & 1)
            if not driven: undriven += 1
            if not driven or value != wanted: mismatch += 1
    resolved_buses: list[tuple[str, frozenset[int]]] = []
    for index, item in enumerate(payload["network"]):
        resolved_buses.append((f"slot{index}_left", frozenset(item["left_bus"])))
        resolved_buses.append((f"slot{index}_right", frozenset(item["right_bus"])))
    resolved_buses.extend(
        (f"output{index}", frozenset(bus))
        for index, bus in enumerate(payload["output_buses"])
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
        "assignments": state["assignments"],
        "output_checks": state["assignments"] * len(state["targets"]),
        "mismatch_count": mismatch,
        "bus_conflict_count": conflict,
        "undriven_output_count": undriven,
        "physical_net_partition_violation_count": len(physical_violations),
        "physical_net_partition_violations": physical_violations,
        "replayed_max_component_depth": max_depth,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, choices=(1, 2, 3, 4), required=True)
    parser.add_argument("--mode", choices=("carry", "transfer", "dual-transfer"), required=True)
    parser.add_argument("--free-gp", action="store_true")
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--abstract-buses", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    enc, state = build(args)
    model = None
    status = "unknown"
    with Solver(name=args.solver, bootstrap_with=enc.cnf) as solver:
        timer = threading.Timer(args.timeout, solver.interrupt) if args.timeout > 0 else None
        if timer is not None: timer.start()
        try: result = solver.solve_limited(expect_interrupt=True)
        finally:
            if timer is not None: timer.cancel()
        if result is True:
            status = "sat"; model = solver.get_model()
        elif result is False: status = "unsat"
    payload = {
        "schema": "exact-carry-block-switch-cnf-v1",
        "status": status,
        "bits": args.bits,
        "mode": args.mode,
        "free_gp": args.free_gp,
        "source_names": state["source_names"],
        "source_arrivals": state["source_arrivals"],
        "target_names": state["target_names"],
        "gate_bound": args.gate_bound,
        "max_delay": args.max_delay,
        "components": args.components,
        "physical_nets": not args.abstract_buses,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
    }
    if model is not None:
        payload.update(decode(args, state, model))
        payload["verification"] = verify(payload, state)
        if any(
            payload["verification"][key]
            for key in (
                "mismatch_count",
                "bus_conflict_count",
                "undriven_output_count",
                "physical_net_partition_violation_count",
            )
        ):
            raise RuntimeError("decoded carry witness failed replay")
    elif status == "unknown": payload["reason_unknown"] = "timeout"
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 0 if status != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
