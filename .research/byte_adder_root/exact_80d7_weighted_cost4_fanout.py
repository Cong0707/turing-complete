"""Exact mixed-DAG closure for the remaining local 80/7 replacement gap.

For S2 and S4 the ordinary-only four-component DAG is already independently
UNSAT, while formula closure covers all two-component cost-four mixtures.  The
only remaining cost-four local topology is therefore three components with
exactly one Switch and two ordinary gates.  This worker encodes arbitrary
internal fanout, resolved buses, source Z masks, component liveness, timing,
and physical net partitioning.

The CLI is deliberately parameterized so that five-ordinary positive controls
can exercise the same encoder.  It is offline and never touches the game save.
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
from typing import Any

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_DAG = HERE / "byte-adder-hybrid-phasefold-g80-d7.json"
UPSTREAM = ROOT / ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py"
MATERIALIZER = ROOT / ".research/byte_adder_builder_layout_agent/materialize_factory_dag.py"
FULL_ROWS = 1 << 17

TARGETS = {
    "s2": {
        "target": 81,
        "sources": (4, 5, 6, 7, 22, 23, 24, 25, 45, 50, 51, 52, 54, 55, 56, 76, 77),
    },
    "s4": {
        "target": 86,
        "sources": (8, 9, 10, 11, 28, 29, 30, 31, 32, 56, 57, 59, 60, 61, 62, 82, 83),
    },
}


def load_upstream():
    spec = importlib.util.spec_from_file_location("weighted_cost4_fanout_upstream", UPSTREAM)
    if spec is None or spec.loader is None:
        raise RuntimeError(UPSTREAM)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


upstream = load_upstream()
G = upstream.G
exact = upstream.exact


def load_dag(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location(
        "weighted_cost4_fanout_materializer", MATERIALIZER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(MATERIALIZER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    states = module.logical_states(tuple(payload["factory_dag"]["nodes"]))
    return payload, states


def dependency_sha256() -> dict[str, str]:
    paths = (
        UPSTREAM,
        upstream.EXACT_PATH,
        upstream.exact.GENERIC_PATH,
        MATERIALIZER,
    )
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path.read_bytes()).hexdigest()
        for path in paths
    }


def cnf_sha256(clauses: list[list[int]]) -> str:
    digest = sha256()
    for clause in clauses:
        digest.update((" ".join(str(literal) for literal in clause) + " 0\n").encode("ascii"))
    return digest.hexdigest()


def project_domain(
    target: int,
    source_ids: tuple[int, ...],
    states: dict[int, dict[str, int]],
    include_constants: bool,
) -> dict[str, Any]:
    classes: dict[tuple[int, ...], tuple[int, int, int]] = {}
    for row in range(FULL_ROWS):
        signature: list[int] = []
        for node_id in source_ids:
            state = states[node_id]
            if int(state["conflict"]):
                raise RuntimeError(f"source node {node_id} has a conflict assignment")
            signature.extend(
                (
                    (int(state["bits"]) >> row) & 1,
                    (int(state["driven"]) >> row) & 1,
                )
            )
        target_state = states[target]
        target_value = (
            (int(target_state["bits"]) >> row) & 1,
            (int(target_state["driven"]) >> row) & 1,
            (int(target_state["conflict"]) >> row) & 1,
        )
        key = tuple(signature)
        previous = classes.get(key)
        if previous is not None and previous != target_value:
            raise RuntimeError(f"target {target} is not determined by source signature")
        classes[key] = target_value

    signatures = tuple(sorted(classes))
    assignments = len(signatures)
    names = [f"n{node_id}" for node_id in source_ids]
    source_values = [
        [bool(signature[2 * index]) for signature in signatures]
        for index in range(len(source_ids))
    ]
    source_drivens = [
        [bool(signature[2 * index + 1]) for signature in signatures]
        for index in range(len(source_ids))
    ]
    source_arrivals = [int(states[node_id]["depth"]) for node_id in source_ids]
    full_source_bits = [int(states[node_id]["bits"]) for node_id in source_ids]
    full_source_drivens = [int(states[node_id]["driven"]) for node_id in source_ids]
    if include_constants:
        names.extend(("0", "1"))
        source_values.extend(([False] * assignments, [True] * assignments))
        source_drivens.extend(([True] * assignments, [True] * assignments))
        source_arrivals.extend((0, 0))
        full_mask = (1 << FULL_ROWS) - 1
        full_source_bits.extend((0, full_mask))
        full_source_drivens.extend((full_mask, full_mask))

    target_rows = tuple(classes[signature] for signature in signatures)
    if any(driven != 1 or conflict != 0 for _, driven, conflict in target_rows):
        raise RuntimeError("public target is not fully driven and conflict-free")
    target_bits = sum(value << row for row, (value, _, _) in enumerate(target_rows))
    return {
        "names": names,
        "source_values": source_values,
        "source_drivens": source_drivens,
        "source_arrivals": source_arrivals,
        "targets": (target_bits,),
        "compact_rows": assignments,
        "full_source_bits": full_source_bits,
        "full_source_drivens": full_source_drivens,
        "full_target_bits": int(states[target]["bits"]),
    }


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


def exact_kind_count(enc, kinds: list[list[int]], kind: int, count: int) -> None:
    enc.cnf.extend(
        CardEnc.equals(
            lits=[row[kind] for row in kinds],
            bound=count,
            vpool=enc.pool,
            encoding=EncType.seqcounter,
        ).clauses
    )


def build(args: argparse.Namespace, domain: dict[str, Any]):
    source_values = list(domain["source_values"])
    source_drivens = list(domain["source_drivens"])
    source_arrivals = list(domain["source_arrivals"])
    targets = tuple(domain["targets"])
    assignments = len(source_values[0])
    source_count = len(source_values)
    enc = G.Encoder()
    values: list[list[object]] = list(source_values)
    drivens: list[list[object]] = list(source_drivens)
    kinds: list[list[int]] = []
    levels: list[list[int]] = []
    left_uses: list[list[int]] = []
    right_uses: list[list[int]] = []

    for slot in range(args.components):
        available = source_count + slot
        slot_kinds = [enc.var(f"kind_{slot}_{name}") for name in G.KINDS]
        enc.exactly_one(slot_kinds)
        slot_levels = [
            enc.var(f"depth_{slot}_{depth}") for depth in range(1, args.max_delay + 1)
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
    exact_kind_count(enc, kinds, G.SWITCH, args.switches)
    exact_kind_count(enc, kinds, G.XOR, args.xors)

    output_uses: list[list[int]] = []
    for output, target in enumerate(targets):
        uses = [
            enc.var(f"output_{output}_{source}")
            for source in range(source_count + args.components)
        ]
        enc.clause(uses)
        G._restrict_active_bus_to_switches(enc, uses, source_count, kinds)
        for source, arrival in enumerate(source_arrivals):
            if arrival > args.max_delay:
                enc.clause((-uses[source],))
        for slot, row in enumerate(levels):
            source = source_count + slot
            for depth, literal in enumerate(row, start=1):
                if depth > args.max_delay:
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
        "names": domain["names"],
        "source_count": source_count,
        "source_values": source_values,
        "source_drivens": source_drivens,
        "source_arrivals": source_arrivals,
        "targets": targets,
        "kinds": kinds,
        "levels": levels,
        "left_uses": left_uses,
        "right_uses": right_uses,
        "output_uses": output_uses,
        "allow_z_false_outputs": (False,),
        "output_deadlines": (args.max_delay,),
    }


def resolve_packed(
    bus: list[int], values: list[int], drivens: list[int], mask: int
) -> tuple[int, int, int]:
    ones = 0
    zeros = 0
    for source in bus:
        ones |= values[source] & drivens[source]
        zeros |= (~values[source] & mask) & drivens[source]
    return ones & mask, (ones | zeros) & mask, (ones & zeros) & mask


def full_replay(payload: dict[str, Any], domain: dict[str, Any]) -> dict[str, Any]:
    mask = (1 << FULL_ROWS) - 1
    values = list(domain["full_source_bits"])
    drivens = list(domain["full_source_drivens"])
    arrivals = list(domain["source_arrivals"])
    conflict = 0
    actual_cost = 0
    delay_by_kind = dict(zip(G.KINDS, G.DELAY, strict=True))
    cost_by_kind = dict(zip(G.KINDS, G.COST, strict=True))
    for item in payload["network"]:
        left, _, left_conflict = resolve_packed(item["left_bus"], values, drivens, mask)
        right, _, right_conflict = resolve_packed(item["right_bus"], values, drivens, mask)
        conflict |= left_conflict | right_conflict
        kind = item["kind"]
        if kind == "NOT":
            value, driven = ~left & mask, mask
        elif kind == "AND":
            value, driven = left & right, mask
        elif kind == "OR":
            value, driven = left | right, mask
        elif kind == "NAND":
            value, driven = ~(left & right) & mask, mask
        elif kind == "NOR":
            value, driven = ~(left | right) & mask, mask
        elif kind == "XOR":
            value, driven = left ^ right, mask
        elif kind == "SWITCH":
            value, driven = left & right, left
        else:
            raise AssertionError(kind)
        selected_arrivals = [
            arrivals[source]
            for source in set(item["left_bus"]) | set(item["right_bus"])
        ]
        arrival = max(selected_arrivals, default=0) + delay_by_kind[kind]
        if arrival > int(item["depth_upper_bound"]):
            raise RuntimeError("decoded depth upper bound is below actual arrival")
        values.append(value & mask)
        drivens.append(driven & mask)
        arrivals.append(arrival)
        actual_cost += cost_by_kind[kind]

    output, output_driven, output_conflict = resolve_packed(
        payload["output_buses"][0], values, drivens, mask
    )
    conflict |= output_conflict
    output_arrival = max(arrivals[source] for source in payload["output_buses"][0])
    mismatch = (output ^ int(domain["full_target_bits"])).bit_count()
    undriven = (mask ^ output_driven).bit_count()
    return {
        "truth_rows": FULL_ROWS,
        "mismatch_count": mismatch,
        "conflict_assignment_count": conflict.bit_count(),
        "undriven_output_count": undriven,
        "actual_gate": actual_cost,
        "actual_output_arrival": output_arrival,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    parser.add_argument("--target", choices=tuple(TARGETS), required=True)
    parser.add_argument("--gate-bound", type=int, default=4)
    parser.add_argument("--max-delay", type=int, default=7)
    parser.add_argument("--components", type=int, default=3)
    parser.add_argument("--switches", type=int, default=1)
    parser.add_argument("--xors", type=int, default=0)
    parser.add_argument("--include-constants", action="store_true")
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    dag, states = load_dag(args.dag)
    target_spec = TARGETS[args.target]
    domain = project_domain(
        int(target_spec["target"]),
        tuple(target_spec["sources"]),
        states,
        args.include_constants,
    )
    started = time.perf_counter()
    enc, state = build(args, domain)
    model = None
    status = "unknown"
    timer = None
    with Solver(name=args.solver, bootstrap_with=enc.cnf.clauses) as solver:
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

    payload: dict[str, Any] = {
        "schema": "byte-adder-80d7-weighted-cost4-fanout-exact-v1",
        "status": status,
        "source_dag": str(args.dag.resolve()),
        "source_dag_sha256": sha256(args.dag.read_bytes()).hexdigest(),
        "dependency_sha256": dependency_sha256(),
        "target": args.target,
        "target_node": int(target_spec["target"]),
        "source_ids": list(target_spec["sources"]),
        "compact_truth_rows": int(domain["compact_rows"]),
        "include_constants": args.include_constants,
        "gate_bound": args.gate_bound,
        "max_delay": args.max_delay,
        "components": args.components,
        "exact_switches": args.switches,
        "exact_xors": args.xors,
        "solver": args.solver,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "cnf_sha256": cnf_sha256(enc.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "physical_nets": True,
    }
    if model is not None:
        payload.update(upstream.decode(args, state, model))
        payload["compact_verification"] = upstream.verify(payload, state)
        payload["full_verification"] = full_replay(payload, domain)
        if any(payload["compact_verification"].values()):
            raise RuntimeError("compact witness verification failed")
        full = payload["full_verification"]
        if any(
            full[key]
            for key in (
                "mismatch_count",
                "conflict_assignment_count",
                "undriven_output_count",
            )
        ):
            raise RuntimeError("full witness verification failed")
        if full["actual_gate"] > args.gate_bound or full["actual_output_arrival"] > args.max_delay:
            raise RuntimeError("full witness violates cost or delay")

    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {key: value for key, value in payload.items() if key != "network"},
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 0 if status != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
