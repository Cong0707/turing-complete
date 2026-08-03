"""Strict physical-BUS synthesis for the current 80/7 S1+S2 joint cut.

The authoritative cut removes ten private ordinary nodes:

    23, 24, 52, 53, 76, 77, 78, 79, 80, 81

and retains the seven already-paid boundary signals:

    4, 5, 22, 25, 51, 45(C1), 56(C3)

Unlike the Boolean-only ordinary search, this worker projects both value and
driven masks from all 131072 rows.  In particular C1 and C3 retain their exact
Z/D states.  It reuses the reviewed resolved-BUS CNF encoder, physical-net
partition constraint, component-liveness constraint, and recursive delay
model.  Any SAT witness is independently replayed on the full masks.

The ``--seed-current`` mode fixes the known ten-ordinary-gate cone and serves
as a positive regression.  The normal mode handles one exact weighted-cost
decomposition per invocation, making solver/case sharding reproducible.

Offline research only: no game launch, formal-save access, graft, or deploy.
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

import pysat
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_DAG = (
    ROOT
    / ".research"
    / "byte_adder_root"
    / "byte-adder-hybrid-phasefold-g80-d7.json"
)
MATERIALIZER = (
    ROOT
    / ".research"
    / "byte_adder_builder_layout_agent"
    / "materialize_factory_dag.py"
)
EXACT_ADAPTER = (
    ROOT
    / ".research"
    / "byte_adder_han_knowles_fused_agent"
    / "search_av97_local_suffix.py"
)

SOURCE_IDS = (4, 5, 22, 25, 51, 45, 56)
SOURCE_LABELS = ("a1", "b1", "G1", "G2", "V2", "C1", "C3")
TARGET_IDS = (77, 81)
TARGET_LABELS = ("S1", "S2")
OUTPUT_DEADLINES = (4, 7)
CUT_NODE_IDS = (23, 24, 52, 53, 76, 77, 78, 79, 80, 81)
FULL_ROWS = 1 << 17
FULL_MASK = (1 << FULL_ROWS) - 1


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def make_problem(states: dict[int, dict[str, int]]):
    source_bits = [int(states[node_id]["bits"]) for node_id in SOURCE_IDS]
    source_drivens = [int(states[node_id]["driven"]) for node_id in SOURCE_IDS]
    target_bits = [int(states[node_id]["bits"]) for node_id in TARGET_IDS]

    for node_id in (*SOURCE_IDS, *TARGET_IDS):
        conflict_count = int(states[node_id]["conflict"]).bit_count()
        if conflict_count:
            raise RuntimeError(f"authoritative node {node_id} has {conflict_count} conflicts")
    for node_id in TARGET_IDS:
        if int(states[node_id]["driven"]) != FULL_MASK:
            raise RuntimeError(f"authoritative target {node_id} is not fully driven")

    classes: dict[tuple[int, ...], tuple[bool, ...]] = {}
    for row in range(FULL_ROWS):
        signature = tuple(
            item
            for bits, driven in zip(source_bits, source_drivens, strict=True)
            for item in ((bits >> row) & 1, (driven >> row) & 1)
        )
        targets = tuple(bool((bits >> row) & 1) for bits in target_bits)
        previous = classes.get(signature)
        if previous is not None and previous != targets:
            raise RuntimeError(
                "joint targets are not determined by the retained value/driven "
                f"signature {signature}: {previous} != {targets}"
            )
        classes[signature] = targets

    signatures = sorted(classes)
    names = list(SOURCE_LABELS)
    values = [[] for _ in names]
    drivens = [[] for _ in names]
    compact_targets = [[] for _ in TARGET_IDS]
    for signature in signatures:
        for index in range(len(names)):
            values[index].append(bool(signature[index * 2]))
            drivens[index].append(bool(signature[index * 2 + 1]))
        target_values = classes[signature]
        for index, value in enumerate(target_values):
            compact_targets[index].append(value)

    target_masks = tuple(
        sum(int(value) << row for row, value in enumerate(values_row))
        for values_row in compact_targets
    )
    arrivals = {
        label: int(states[node_id]["depth"])
        for label, node_id in zip(SOURCE_LABELS, SOURCE_IDS, strict=True)
    }
    source_driven_map = dict(zip(names, drivens, strict=True))
    metadata = {
        "source_ids": list(SOURCE_IDS),
        "source_names": names,
        "source_arrivals": arrivals,
        "source_driven_one_counts": {
            label: int(states[node_id]["driven"]).bit_count()
            for label, node_id in zip(SOURCE_LABELS, SOURCE_IDS, strict=True)
        },
        "source_conflict_one_counts": {
            label: int(states[node_id]["conflict"]).bit_count()
            for label, node_id in zip(SOURCE_LABELS, SOURCE_IDS, strict=True)
        },
        "target_ids": list(TARGET_IDS),
        "target_names": list(TARGET_LABELS),
        "target_one_counts": {
            label: int(states[node_id]["bits"]).bit_count()
            for label, node_id in zip(TARGET_LABELS, TARGET_IDS, strict=True)
        },
        "target_driven_one_counts": {
            label: int(states[node_id]["driven"]).bit_count()
            for label, node_id in zip(TARGET_LABELS, TARGET_IDS, strict=True)
        },
        "compressed_truth_rows": len(signatures),
    }
    return (names, values, target_masks, arrivals), source_driven_map, metadata


def fresh_build(exact: dict[str, Any], args: argparse.Namespace):
    names, rows, targets, arrivals = exact["_strict_joint_truth_template"]
    exact["CURRENT_TRUTH"] = (
        list(names),
        [list(row) for row in rows],
        tuple(targets),
        dict(arrivals),
    )
    return exact["build"](args)


def resolve_bus(
    bus: list[int], values: list[int], drivens: list[int]
) -> tuple[int, int, int]:
    ones = 0
    zeros = 0
    for source in bus:
        ones |= values[source] & drivens[source]
        zeros |= (~values[source] & FULL_MASK) & drivens[source]
    return ones, ones | zeros, ones & zeros


def independent_full_replay(
    witness: dict[str, Any],
    states: dict[int, dict[str, int]],
    gate_library: Any,
) -> dict[str, Any]:
    source_count = len(SOURCE_IDS) + 2
    values = [int(states[node_id]["bits"]) for node_id in SOURCE_IDS]
    values.extend((0, FULL_MASK))
    drivens = [int(states[node_id]["driven"]) for node_id in SOURCE_IDS]
    drivens.extend((FULL_MASK, FULL_MASK))
    arrivals = [int(states[node_id]["depth"]) for node_id in SOURCE_IDS]
    arrivals.extend((0, 0))
    buses: list[list[int]] = []
    used_components: set[int] = set()
    conflict_mask = 0
    actual_gate = 0
    kind_counts = {kind: 0 for kind in gate_library.KINDS}

    for slot, item in enumerate(witness["network"]):
        if int(item["slot"]) != slot or int(item["source"]) != source_count + slot:
            raise RuntimeError("non-canonical decoded component numbering")
        left_bus = [int(source) for source in item["left_bus"]]
        right_bus = [int(source) for source in item["right_bus"]]
        buses.extend((left_bus, right_bus))
        for source in (*left_bus, *right_bus):
            if source >= source_count:
                used_components.add(source - source_count)

        left, _left_driven, left_conflict = resolve_bus(left_bus, values, drivens)
        right, _right_driven, right_conflict = resolve_bus(right_bus, values, drivens)
        conflict_mask |= left_conflict | right_conflict
        kind = str(item["kind"])
        kind_index = gate_library.KINDS.index(kind)
        kind_counts[kind] += 1
        actual_gate += int(gate_library.COST[kind_index])
        if kind == "NOT":
            value, driven = (~left & FULL_MASK), FULL_MASK
        elif kind == "AND":
            value, driven = left & right, FULL_MASK
        elif kind == "OR":
            value, driven = left | right, FULL_MASK
        elif kind == "NAND":
            value, driven = (~(left & right) & FULL_MASK), FULL_MASK
        elif kind == "NOR":
            value, driven = (~(left | right) & FULL_MASK), FULL_MASK
        elif kind == "XOR":
            value, driven = left ^ right, FULL_MASK
        elif kind == "SWITCH":
            value, driven = left & right, left
        else:
            raise RuntimeError(f"unsupported kind {kind}")
        values.append(value)
        drivens.append(driven)
        selected_inputs = [*left_bus, *right_bus]
        if not selected_inputs:
            raise RuntimeError(f"component {slot} has no selected input")
        arrival = max(arrivals[source] for source in selected_inputs) + int(
            gate_library.DELAY[kind_index]
        )
        arrivals.append(arrival)
        if arrival > int(item["depth_upper_bound"]):
            raise RuntimeError("decoded depth upper bound is below actual arrival")

    output_values = []
    output_drivens = []
    output_arrivals = []
    for output_bus_raw in witness["output_buses"]:
        output_bus = [int(source) for source in output_bus_raw]
        buses.append(output_bus)
        for source in output_bus:
            if source >= source_count:
                used_components.add(source - source_count)
        value, driven, conflict = resolve_bus(output_bus, values, drivens)
        conflict_mask |= conflict
        output_values.append(value)
        output_drivens.append(driven)
        output_arrivals.append(max(arrivals[source] for source in output_bus))

    if len(output_values) != len(TARGET_IDS):
        raise RuntimeError("decoded witness has the wrong output count")

    partition_violations = []
    for left_index, left in enumerate(buses):
        left_set = set(left)
        for right_index, right in enumerate(buses[left_index + 1 :], left_index + 1):
            right_set = set(right)
            overlap = left_set & right_set
            if overlap and left_set != right_set:
                partition_violations.append(
                    {
                        "left_bus": left_index,
                        "right_bus": right_index,
                        "overlap": sorted(overlap),
                    }
                )

    mismatch_counts = []
    undriven_counts = []
    for value, driven, target_id in zip(
        output_values, output_drivens, TARGET_IDS, strict=True
    ):
        mismatch_counts.append((value ^ int(states[target_id]["bits"])).bit_count())
        undriven_counts.append(((~driven) & FULL_MASK).bit_count())

    expected_live = set(range(len(witness["network"])))
    dead_components = sorted(expected_live - used_components)
    report = {
        "full_truth_rows": FULL_ROWS,
        "target_ids": list(TARGET_IDS),
        "target_names": list(TARGET_LABELS),
        "mismatch_counts": mismatch_counts,
        "mismatch_count": sum(mismatch_counts),
        "bus_conflict_count": conflict_mask.bit_count(),
        "undriven_output_counts": undriven_counts,
        "undriven_output_count": sum(undriven_counts),
        "physical_net_partition_violation_count": len(partition_violations),
        "physical_net_partition_violations": partition_violations,
        "dead_component_count": len(dead_components),
        "dead_components": dead_components,
        "actual_gate": actual_gate,
        "kind_counts": kind_counts,
        "actual_component_arrivals": arrivals[source_count:],
        "output_arrivals": output_arrivals,
        "output_deadlines": list(OUTPUT_DEADLINES),
    }
    decisive = (
        report["mismatch_count"],
        report["bus_conflict_count"],
        report["undriven_output_count"],
        report["physical_net_partition_violation_count"],
        report["dead_component_count"],
    )
    if any(decisive) or any(
        arrival > deadline
        for arrival, deadline in zip(output_arrivals, OUTPUT_DEADLINES, strict=True)
    ):
        raise RuntimeError(f"independent full replay failed: {report}")
    return report


def force_one_hot(encoder: Any, literals: list[int], selected: int) -> None:
    for index, literal in enumerate(literals):
        encoder.force(literal, index == selected)


def fix_current_witness(
    encoder: Any, state: dict[str, Any], exact: dict[str, Any], args: argparse.Namespace
) -> None:
    if (args.gate_bound, args.components, args.switches, args.xors) != (10, 10, 0, 0):
        raise ValueError("--seed-current requires g10/components10/switches0/xors0")
    source_count = int(state["source_count"])
    if source_count != len(SOURCE_IDS) + 2:
        raise RuntimeError(f"unexpected source count {source_count}")
    node = lambda slot: source_count + slot
    # Input BUS order is canonical for the core's commutative symmetry rule.
    network = (
        ("NOR", (0,), (1,), 1),
        ("NOR", (2,), (node(0),), 2),
        ("AND", (5,), (node(1),), 3),
        ("OR", (2,), (node(2),), 4),
        ("NOR", (5,), (node(1),), 3),
        ("NOR", (node(2),), (node(4),), 4),
        ("OR", (4,), (node(3),), 5),
        ("NAND", (3,), (node(3),), 5),
        ("NAND", (6,), (node(7),), 6),
        ("AND", (node(6),), (node(8),), 7),
    )
    for slot, (kind, left_bus, right_bus, arrival) in enumerate(network):
        force_one_hot(
            encoder, state["kinds"][slot], exact["G"].KINDS.index(kind)
        )
        for source, literal in enumerate(state["left_uses"][slot]):
            encoder.force(literal, source in left_bus)
        for source, literal in enumerate(state["right_uses"][slot]):
            encoder.force(literal, source in right_bus)
        force_one_hot(encoder, state["levels"][slot], arrival - 1)

    output_buses = ((node(5),), (node(9),))
    for uses, selected in zip(state["output_uses"], output_buses, strict=True):
        for source, literal in enumerate(uses):
            encoder.force(literal, source in selected)


def solve_with_timeout(
    encoder: Any, solver_name: str, timeout: float
) -> tuple[bool | None, list[int] | None]:
    with Solver(name=solver_name, bootstrap_with=encoder.cnf) as solver:
        timer = threading.Timer(timeout, solver.interrupt) if timeout > 0 else None
        if timer is not None:
            timer.start()
        try:
            answer = (
                solver.solve_limited(expect_interrupt=True)
                if timer is not None
                else solver.solve()
            )
            model = solver.get_model() if answer is True else None
        finally:
            if timer is not None:
                timer.cancel()
    return answer, model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int, required=True)
    parser.add_argument("--xors", type=int, required=True)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=0.0)
    parser.add_argument("--seed-current", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.timeout < 0:
        parser.error("--timeout must be non-negative")

    materializer = load(MATERIALIZER, "strict_s1s2_materializer")
    adapter = load(EXACT_ADAPTER, "strict_s1s2_exact_adapter")
    dag_payload = json.loads(args.dag.read_text(encoding="utf-8"))
    ordered_nodes = tuple(dag_payload["factory_dag"]["nodes"])
    states = materializer.logical_states(ordered_nodes)
    problem, source_drivens, metadata = make_problem(states)
    exact = adapter.load_core(problem, source_drivens)
    exact["_strict_joint_truth_template"] = (
        tuple(problem[0]),
        tuple(tuple(row) for row in problem[1]),
        tuple(problem[2]),
        dict(problem[3]),
    )

    internal = argparse.Namespace(
        interface="dual",
        gate_bound=args.gate_bound,
        max_delay=max(OUTPUT_DEADLINES),
        components=args.components,
        switches=args.switches,
        xors=args.xors,
        h_arrival=4,
        c5_arrival=4,
        output_deadlines=",".join(str(value) for value in OUTPUT_DEADLINES),
        solver=args.solver,
        timeout=args.timeout,
        output=args.output,
    )
    started = time.perf_counter()
    encoder, state = fresh_build(exact, internal)
    if args.seed_current:
        fix_current_witness(encoder, state, exact, args)
    build_seconds = time.perf_counter() - started
    solve_started = time.perf_counter()
    answer, model = solve_with_timeout(encoder, args.solver, args.timeout)
    solve_seconds = time.perf_counter() - solve_started
    status = "sat" if answer is True else "unsat" if answer is False else "unknown"
    ordinary = args.components - args.switches - args.xors
    result: dict[str, Any] = {
        "schema": "byte-adder-80d7-s1-s2-joint-strict-physical-v1",
        "status": status,
        "source": str(args.dag.resolve()),
        "source_sha256": file_sha256(args.dag),
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "script_sha256_dependencies": {
            "materializer": file_sha256(MATERIALIZER),
            "exact_adapter": file_sha256(EXACT_ADAPTER),
        },
        "cut_node_ids": list(CUT_NODE_IDS),
        "full_truth_rows": FULL_ROWS,
        **metadata,
        "output_deadlines": list(OUTPUT_DEADLINES),
        "gate_bound": args.gate_bound,
        "components": args.components,
        "exact_ordinary": ordinary,
        "exact_switches": args.switches,
        "exact_xors": args.xors,
        "weighted_gate": ordinary + 2 * args.switches + 3 * args.xors,
        "seed_current": args.seed_current,
        "physical_nets": True,
        "all_components_live": True,
        "final_outputs_fully_driven": True,
        "solver": args.solver,
        "timeout_seconds": args.timeout,
        "pysat_version": pysat.__version__,
        "variables": encoder.pool.top,
        "clauses": len(encoder.cnf.clauses),
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "elapsed_seconds": time.perf_counter() - started,
    }
    if model is not None:
        witness = exact["decode"](internal, state, model)
        compressed = exact["verify"](witness, state)
        full = independent_full_replay(witness, states, exact["G"])
        expected_gate = 10 if args.seed_current else args.gate_bound
        if int(witness["actual_gate"]) != expected_gate:
            raise RuntimeError(
                f"decoded gate {witness['actual_gate']} != expected {expected_gate}"
            )
        result["witness"] = witness
        result["compressed_verification"] = compressed
        result["full_verification"] = full

    output_sha = atomic_write(args.output, result)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "status": status,
                "seed_current": args.seed_current,
                "decomposition": [ordinary, args.switches, args.xors],
                "compressed_truth_rows": metadata["compressed_truth_rows"],
                "variables": encoder.pool.top,
                "clauses": len(encoder.cnf.clauses),
                "build_seconds": build_seconds,
                "solve_seconds": solve_seconds,
                "output_sha256": output_sha,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if status != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
