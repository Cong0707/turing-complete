"""Exact synthesis of a sparse-2 Ling sum pair with paid GP leaves.

This model differs from ``exact_ling_pair_sat.py`` in one essential way:
the usual local ``g/q/x`` leaf signals are exposed as zero-cost sources.  The
caller therefore measures only the *incremental* cost of Ling sum selection,
without charging the shared per-bit leaf network a second time.

Two interfaces are supported:

``single``
    Only the late pseudocarry ``H`` is available.

``dual``
    Both ``H`` and ``~H`` are available at the same arrival time.  This is the
    interface needed by compound-carry / dual-rail Ling networks.

The resolved-BUS encoding includes the physical net-partition constraint used
throughout the Byte Adder research.  The script is offline only: it does not
read or write the game save and does not launch the game.
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


HERE = Path(__file__).resolve().parent
EXACT_PATH = HERE / "exact_paid_physical_core.py"


def _load_exact():
    spec = importlib.util.spec_from_file_location("free_ling_exact_core", EXACT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(EXACT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


exact = _load_exact()
G = exact.G


def truth_tables(interface: str) -> tuple[list[str], list[list[bool]], tuple[int, ...], dict[str, int]]:
    """Return correlated free-source tables and the two target functions."""

    if interface == "tail7dual":
        assignments = 8
        names = ["a7", "b7", "C7"]
        rows = [
            [bool((case >> bit) & 1) for case in range(assignments)]
            for bit in range(3)
        ]
        a7, b7, c7 = rows

        def pointwise(fn, *args):
            return [bool(fn(*(int(row[i]) for row in args))) for i in range(assignments)]

        c7_bar = [not value for value in c7]
        g7 = pointwise(lambda a, b: a & b, a7, b7)
        q7 = pointwise(lambda a, b: 1 ^ (a | b), a7, b7)
        p7 = pointwise(lambda g, q: 1 ^ (g | q), g7, q7)
        s7 = pointwise(lambda p, c: p ^ c, p7, c7)
        c8 = pointwise(lambda g, p, c: g | (p & c), g7, p7, c7)
        names.extend(("C7_bar", "G7", "Q7", "P7"))
        rows.extend((c7_bar, g7, q7, p7))
        targets = tuple(
            sum(int(value) << case for case, value in enumerate(target))
            for target in (s7, c8)
        )
        arrivals = {
            "a7": 0,
            "b7": 0,
            "C7": 5,
            "C7_bar": 5,
            "G7": 1,
            "Q7": 1,
            "P7": 2,
        }
        return names, rows, targets, arrivals

    if interface == "bit56":
        assignments = 32
        names = ["a5", "b5", "a6", "b6", "C5"]
        rows = [
            [bool((case >> bit) & 1) for case in range(assignments)]
            for bit in range(5)
        ]
        a5, b5, a6, b6, c5 = rows

        def pointwise(fn, *args):
            return [bool(fn(*(int(row[i]) for row in args))) for i in range(assignments)]

        g5 = pointwise(lambda a, b: a & b, a5, b5)
        q5 = pointwise(lambda a, b: 1 ^ (a | b), a5, b5)
        p5 = pointwise(lambda g, q: 1 ^ (g | q), g5, q5)
        g6 = pointwise(lambda a, b: a & b, a6, b6)
        q6 = pointwise(lambda a, b: 1 ^ (a | b), a6, b6)
        p6 = pointwise(lambda g, q: 1 ^ (g | q), g6, q6)
        c6 = pointwise(lambda g, p, c: g | (p & c), g5, p5, c5)
        s5 = pointwise(lambda p, c: p ^ c, p5, c5)
        s6 = pointwise(lambda p, c: p ^ c, p6, c6)
        c7 = pointwise(lambda g, p, c: g | (p & c), g6, p6, c6)
        names.extend(("G5", "Q5", "P5", "G6", "Q6", "P6"))
        rows.extend((g5, q5, p5, g6, q6, p6))
        targets = tuple(
            sum(int(value) << case for case, value in enumerate(target))
            for target in (s5, s6, c7)
        )
        arrivals = {
            "a5": 0,
            "b5": 0,
            "a6": 0,
            "b6": 0,
            "C5": 4,
            "G5": 1,
            "Q5": 1,
            "P5": 2,
            "G6": 1,
            "Q6": 1,
            "P6": 2,
        }
        return names, rows, targets, arrivals

    if interface == "s6":
        assignments = 32
        names = ["a5", "b5", "a6", "b6", "C5"]
        rows = [
            [bool((case >> bit) & 1) for case in range(assignments)]
            for bit in range(5)
        ]
        a5, b5, a6, b6, c5 = rows

        def pointwise(fn, *args):
            return [bool(fn(*(int(row[i]) for row in args))) for i in range(assignments)]

        g5 = pointwise(lambda a, b: a & b, a5, b5)
        q5 = pointwise(lambda a, b: 1 ^ (a | b), a5, b5)
        p5 = pointwise(lambda g, q: 1 ^ (g | q), g5, q5)
        g6 = pointwise(lambda a, b: a & b, a6, b6)
        q6 = pointwise(lambda a, b: 1 ^ (a | b), a6, b6)
        p6 = pointwise(lambda g, q: 1 ^ (g | q), g6, q6)
        both = pointwise(lambda a, b: a & b, p5, p6)
        phase = pointwise(lambda q, t: 1 ^ (q | t), q6, both)
        any_generate = pointwise(lambda a, b: a | b, g5, g6)
        c7 = pointwise(
            lambda t, c, a, d: (t & c) | (a & d),
            both,
            c5,
            any_generate,
            phase,
        )
        c6 = pointwise(lambda g, p, c: g | (p & c), g5, p5, c5)
        s6 = pointwise(lambda p, c: p ^ c, p6, c6)
        names.extend(("G5", "Q5", "P5", "G6", "Q6", "P6", "T", "D", "G", "C7"))
        rows.extend((g5, q5, p5, g6, q6, p6, both, phase, any_generate, c7))
        target = sum(int(value) << case for case, value in enumerate(s6))
        arrivals = {
            "a5": 0,
            "b5": 0,
            "a6": 0,
            "b6": 0,
            "C5": 4,
            "G5": 1,
            "Q5": 1,
            "P5": 2,
            "G6": 1,
            "Q6": 1,
            "P6": 2,
            "T": 3,
            "D": 4,
            "G": 2,
            "C7": 5,
        }
        return names, rows, (target,), arrivals

    if interface == "s4":
        assignments = 32
        names = ["a3", "b3", "a4", "b4", "C3"]
        rows = [
            [bool((case >> bit) & 1) for case in range(assignments)]
            for bit in range(5)
        ]
        a3, b3, a4, b4, c3 = rows

        def pointwise(fn, *args):
            return [bool(fn(*(int(row[i]) for row in args))) for i in range(assignments)]

        g3 = pointwise(lambda a, b: a & b, a3, b3)
        q3 = pointwise(lambda a, b: 1 ^ (a | b), a3, b3)
        p3 = pointwise(lambda g, q: 1 ^ (g | q), g3, q3)
        g4 = pointwise(lambda a, b: a & b, a4, b4)
        q4 = pointwise(lambda a, b: 1 ^ (a | b), a4, b4)
        p4 = pointwise(lambda g, q: 1 ^ (g | q), g4, q4)
        any_generate = pointwise(lambda a, b: a | b, g3, g4)
        no_kill = pointwise(lambda a, b: 1 ^ (a | b), q3, q4)
        v34 = pointwise(lambda g, n: g | n, g4, no_kill)
        c5 = pointwise(lambda a, v, c: v & (a | c), any_generate, v34, c3)
        c4 = pointwise(lambda g, p, c: g | (p & c), g3, p3, c3)
        s4 = pointwise(lambda p, c: p ^ c, p4, c4)
        names.extend(("G3", "Q3", "P3", "G4", "Q4", "P4", "A34", "N34", "V34", "C5"))
        rows.extend((g3, q3, p3, g4, q4, p4, any_generate, no_kill, v34, c5))
        target = sum(int(value) << case for case, value in enumerate(s4))
        arrivals = {
            "a3": 0,
            "b3": 0,
            "a4": 0,
            "b4": 0,
            "C3": 3,
            "G3": 1,
            "Q3": 1,
            "P3": 2,
            "G4": 1,
            "Q4": 1,
            "P4": 2,
            "A34": 2,
            "N34": 2,
            "V34": 3,
            "C5": 4,
        }
        return names, rows, (target,), arrivals

    if interface == "s2":
        assignments = 32
        names = ["a1", "b1", "a2", "b2", "C1"]
        rows = [
            [bool((case >> bit) & 1) for case in range(assignments)]
            for bit in range(5)
        ]
        a1, b1, a2, b2, c1 = rows

        def pointwise(fn, *args):
            return [bool(fn(*(int(row[i]) for row in args))) for i in range(assignments)]

        g1 = pointwise(lambda a, b: a & b, a1, b1)
        q1 = pointwise(lambda a, b: 1 ^ (a | b), a1, b1)
        p1 = pointwise(lambda g, q: 1 ^ (g | q), g1, q1)
        v1 = pointwise(lambda a, b: a | b, a1, b1)
        g2 = pointwise(lambda a, b: a & b, a2, b2)
        q2 = pointwise(lambda a, b: 1 ^ (a | b), a2, b2)
        p2 = pointwise(lambda g, q: 1 ^ (g | q), g2, q2)
        v2 = pointwise(lambda a, b: a | b, a2, b2)
        a12 = pointwise(lambda a, b: a | b, g1, g2)
        v12 = pointwise(lambda gh, vh, vl: vh & (gh | vl), g2, v2, v1)
        c3 = pointwise(lambda a, v, c: v & (a | c), a12, v12, c1)
        c2 = pointwise(lambda g, p, c: g | (p & c), g1, p1, c1)
        s2 = pointwise(lambda p, c: p ^ c, p2, c2)
        names.extend(("G1", "Q1", "P1", "V1", "G2", "Q2", "P2", "V2", "A12", "V12", "C3"))
        rows.extend((g1, q1, p1, v1, g2, q2, p2, v2, a12, v12, c3))
        target = sum(int(value) << case for case, value in enumerate(s2))
        arrivals = {
            "a1": 0,
            "b1": 0,
            "a2": 0,
            "b2": 0,
            "C1": 2,
            "G1": 1,
            "Q1": 1,
            "P1": 2,
            "V1": 1,
            "G2": 1,
            "Q2": 1,
            "P2": 2,
            "V2": 1,
            "A12": 2,
            "V12": 2,
            "C3": 3,
        }
        return names, rows, (target,), arrivals

    # Independent variables: a_even, a_odd, b_even, b_odd, H, q_prev.
    assignments = 64
    names = ["a_even", "a_odd", "b_even", "b_odd", "H", "q_prev"]
    rows = [
        [bool((case >> bit) & 1) for case in range(assignments)]
        for bit in range(6)
    ]
    a0, a1, b0, b1, h, qprev = rows

    def pointwise(fn, *args):
        return [bool(fn(*(int(row[i]) for row in args))) for i in range(assignments)]

    g0 = pointwise(lambda a, b: a & b, a0, b0)
    q0 = pointwise(lambda a, b: 1 ^ (a | b), a0, b0)
    x0 = pointwise(lambda a, b: a ^ b, a0, b0)
    g1 = pointwise(lambda a, b: a & b, a1, b1)
    q1 = pointwise(lambda a, b: 1 ^ (a | b), a1, b1)
    x1 = pointwise(lambda a, b: a ^ b, a1, b1)
    names.extend(("g_even", "q_even", "x_even", "g_odd", "q_odd", "x_odd"))
    rows.extend((g0, q0, x0, g1, q1, x1))
    if interface == "dual":
        names.append("H_bar")
        rows.append([not value for value in h])

    sum_even = 0
    sum_odd = 0
    for case in range(assignments):
        c_even = (not qprev[case]) and h[case]
        se = x0[case] ^ c_even
        c_odd = g0[case] or (x0[case] and c_even)
        so = x1[case] ^ c_odd
        sum_even |= int(se) << case
        sum_odd |= int(so) << case
    arrivals = {name: 0 for name in names}
    for label in ("g_even", "q_even", "g_odd", "q_odd", "q_prev"):
        arrivals[label] = 1
    for label in ("x_even", "x_odd"):
        arrivals[label] = 2
    arrivals["H"] = 4
    if interface == "dual":
        arrivals["H_bar"] = 4
    return names, rows, (sum_even, sum_odd), arrivals


def weighted_bound(enc, kinds: list[list[int]], bound: int) -> None:
    weighted: list[int] = []
    for row in kinds:
        for kind, literal in enumerate(row):
            weighted.extend([literal] * G.COST[kind])
    enc.cnf.extend(
        CardEnc.atmost(
            lits=weighted,
            bound=bound,
            vpool=enc.pool,
            encoding=EncType.seqcounter,
        ).clauses
    )


def build(args: argparse.Namespace):
    names, source_values, targets, named_arrivals = truth_tables(args.interface)
    assignments = len(source_values[0])
    enc = G.Encoder()
    source_values.extend(([False] * assignments, [True] * assignments))
    names.extend(("0", "1"))
    source_count = len(source_values)
    source_arrivals = [named_arrivals.get(name, 0) for name in names]
    if "H" in names:
        source_arrivals[names.index("H")] = args.h_arrival
    if "H_bar" in names:
        source_arrivals[names.index("H_bar")] = args.h_arrival
    if "C5" in names:
        source_arrivals[names.index("C5")] = args.c5_arrival

    values: list[list[object]] = list(source_values)
    drivens: list[list[object]] = [[True] * assignments for _ in values]
    # The current phase-fold C7 is a resolved BUS.  It is active whenever
    # either of its two switch enables (T or A, named ``G`` here) is true;
    # otherwise a Boolean-zero carry is represented by Z.  Keeping this mask
    # exact is essential when a synthesized Switch consumes C7.
    if args.interface == "s6":
        t_values = source_values[names.index("T")]
        a_values = source_values[names.index("G")]
        drivens[names.index("C7")] = [
            bool(t_values[case] or a_values[case]) for case in range(assignments)
        ]
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
                for pred_depth in range(1, args.max_delay + 1):
                    for result_depth in range(1, args.max_delay + 1):
                        if result_depth < pred_depth + delay:
                            enc.clause(
                                (
                                    -slot_kinds[candidate],
                                    -levels[predecessor][pred_depth - 1],
                                    -left[source],
                                    -slot_levels[result_depth - 1],
                                )
                            )
                            enc.clause(
                                (
                                    -slot_kinds[candidate],
                                    -levels[predecessor][pred_depth - 1],
                                    -right[source],
                                    -slot_levels[result_depth - 1],
                                )
                            )
            for source, arrival in enumerate(source_arrivals):
                for result_depth in range(1, args.max_delay + 1):
                    if result_depth < arrival + delay:
                        enc.clause(
                            (-slot_kinds[candidate], -left[source], -slot_levels[result_depth - 1])
                        )
                        enc.clause(
                            (-slot_kinds[candidate], -right[source], -slot_levels[result_depth - 1])
                        )

        slot_values = []
        slot_drivens = []
        for case in range(assignments):
            driver_values = [row[case] for row in values]
            driver_drivens = [row[case] for row in drivens]
            lv = enc.bus_case(f"left_{slot}_{case}", left, driver_values, driver_drivens)
            rv = enc.bus_case(f"right_{slot}_{case}", right, driver_values, driver_drivens)
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

    weighted_bound(enc, kinds, args.gate_bound)
    if args.switches is not None:
        enc.cnf.extend(
            CardEnc.equals(
                lits=[row[G.SWITCH] for row in kinds],
                bound=args.switches,
                vpool=enc.pool,
                encoding=EncType.seqcounter,
            ).clauses
        )
    if args.xors is not None:
        enc.cnf.extend(
            CardEnc.equals(
                lits=[row[G.XOR] for row in kinds],
                bound=args.xors,
                vpool=enc.pool,
                encoding=EncType.seqcounter,
            ).clauses
        )

    output_uses: list[list[int]] = []
    allow_z_false_outputs = tuple(
        args.interface == "bit56" and output == 2 for output in range(len(targets))
    )
    if args.output_deadlines:
        output_deadlines = tuple(int(item) for item in args.output_deadlines.split(","))
        if len(output_deadlines) != len(targets):
            raise ValueError(
                f"expected {len(targets)} output deadlines, got {output_deadlines}"
            )
    else:
        output_deadlines = (
            (args.max_delay, args.max_delay, min(args.max_delay, 5))
            if args.interface == "bit56"
            else tuple(args.max_delay for _ in targets)
        )
    for output, target in enumerate(targets):
        deadline = output_deadlines[output]
        uses = [
            enc.var(f"output_{output}_{source}")
            for source in range(source_count + args.components)
        ]
        enc.clause(uses)
        G._restrict_active_bus_to_switches(enc, uses, source_count, kinds)
        for source, arrival in enumerate(source_arrivals):
            if arrival > deadline:
                enc.clause((-uses[source],))
        for slot, row in enumerate(levels):
            source = source_count + slot
            for depth, literal in enumerate(row, start=1):
                if depth > deadline:
                    enc.clause((-uses[source], -literal))
        for case in range(assignments):
            value, driven = exact.output_bus(
                enc,
                f"output_{output}_{case}",
                uses,
                [row[case] for row in values],
                [row[case] for row in drivens],
            )
            enc.force(value, bool((target >> case) & 1))
            if not allow_z_false_outputs[output] or bool((target >> case) & 1):
                enc.force(driven, True)
        output_uses.append(uses)

    buses = []
    for slot, (left, right) in enumerate(zip(left_uses, right_uses, strict=True)):
        buses.extend(((f"slot{slot}_left", left), (f"slot{slot}_right", right)))
    buses.extend((f"output{index}", uses) for index, uses in enumerate(output_uses))
    exact._enforce_physical_net_partition(enc, buses)

    for slot in range(args.components):
        source = source_count + slot
        users = [uses[source] for uses in output_uses]
        for later in range(slot + 1, args.components):
            users.extend((left_uses[later][source], right_uses[later][source]))
        enc.clause(users)

    return enc, {
        "names": names,
        "source_count": source_count,
        "source_values": source_values,
        "source_drivens": drivens[:source_count],
        "source_arrivals": source_arrivals,
        "targets": targets,
        "kinds": kinds,
        "levels": levels,
        "left_uses": left_uses,
        "right_uses": right_uses,
        "output_uses": output_uses,
        "allow_z_false_outputs": allow_z_false_outputs,
        "output_deadlines": output_deadlines,
    }


def selected(model: list[int]) -> set[int]:
    return {literal for literal in model if literal > 0}


def decode(args: argparse.Namespace, state: dict[str, object], model: list[int]):
    enabled = selected(model)
    source_count = int(state["source_count"])
    network = []
    actual_gate = 0
    for slot in range(args.components):
        kind = next(i for i, literal in enumerate(state["kinds"][slot]) if literal in enabled)
        depth = next(i + 1 for i, literal in enumerate(state["levels"][slot]) if literal in enabled)
        actual_gate += G.COST[kind]
        network.append(
            {
                "slot": slot,
                "source": source_count + slot,
                "kind": G.KINDS[kind],
                "left_bus": [i for i, x in enumerate(state["left_uses"][slot]) if x in enabled],
                "right_bus": [i for i, x in enumerate(state["right_uses"][slot]) if x in enabled],
                "cost": G.COST[kind],
                "depth_upper_bound": depth,
            }
        )
    return {
        "actual_gate": actual_gate,
        "network": network,
        "output_buses": [
            [i for i, x in enumerate(uses) if x in enabled]
            for uses in state["output_uses"]
        ],
    }


def verify(payload: dict[str, object], state: dict[str, object]) -> dict[str, int]:
    mismatch = conflict = undriven = partition = 0
    source_count = int(state["source_count"])
    buses = [item["left_bus"] for item in payload["network"]]
    buses += [item["right_bus"] for item in payload["network"]]
    buses += payload["output_buses"]
    for i, left in enumerate(buses):
        for right in buses[i + 1 :]:
            overlap = set(left) & set(right)
            if overlap and set(left) != set(right):
                # Only component outputs can create a physical tristate net.
                if any(source >= source_count for source in overlap):
                    partition += 1

    assignments = len(state["source_values"][0])
    for case in range(assignments):
        values = [row[case] for row in state["source_values"]]
        drivens = [row[case] for row in state["source_drivens"]]

        def resolve(bus):
            nonlocal conflict
            active = {values[source] for source in bus if drivens[source]}
            if len(active) > 1:
                conflict += 1
                return False, True
            if not active:
                return False, False
            return next(iter(active)), True

        for item in payload["network"]:
            left, _ = resolve(item["left_bus"])
            right, _ = resolve(item["right_bus"])
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
            else:
                raise AssertionError(kind)
            values.append(bool(value))
            drivens.append(bool(driven))
        for output, (bus, target) in enumerate(zip(payload["output_buses"], state["targets"], strict=True)):
            value, driven = resolve(bus)
            expected = bool((target >> case) & 1)
            mismatch += value != expected
            if not state["allow_z_false_outputs"][output] or expected:
                undriven += not driven
    return {
        "mismatch_count": mismatch,
        "bus_conflict_count": conflict,
        "undriven_output_count": undriven,
        "physical_net_partition_violation_count": partition,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--interface",
        choices=("single", "dual", "s2", "s4", "s6", "bit56", "tail7dual"),
        required=True,
    )
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int)
    parser.add_argument("--h-arrival", type=int, default=4)
    parser.add_argument("--c5-arrival", type=int, default=4)
    parser.add_argument(
        "--output-deadlines",
        help="comma-separated per-output deadlines overriding the interface defaults",
    )
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    enc, state = build(args)
    timer = None
    model = None
    status = "unknown"
    with Solver(name=args.solver, bootstrap_with=enc.cnf) as solver:
        if args.timeout:
            timer = threading.Timer(args.timeout, solver.interrupt)
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

    payload: dict[str, object] = {
        "schema": "exact-paid-gp-ling-pair-v1",
        "status": status,
        "interface": args.interface,
        "free_sources": state["names"],
        "source_arrivals": dict(zip(state["names"], state["source_arrivals"], strict=True)),
        "gate_bound": args.gate_bound,
        "max_delay": args.max_delay,
        "components": args.components,
        "exact_switches": args.switches,
        "exact_xors": args.xors,
        "solver": args.solver,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "physical_nets": True,
        "output_deadlines": state.get("output_deadlines"),
    }
    if model is not None:
        payload.update(decode(args, state, model))
        payload["verification"] = verify(payload, state)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(json.dumps({k: v for k, v in payload.items() if k != "network"}, ensure_ascii=False, indent=2))
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 0 if status != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
