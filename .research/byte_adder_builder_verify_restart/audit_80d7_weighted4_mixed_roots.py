"""Exact mixed-primitive cost-4 audit for the 80/7 S2 and S4 roots.

The authoritative DAG has two private five-gate cones ending at node 81
(``S2``) and node 86 (``S4``).  The root audit already closed every live
four-ordinary-gate DAG over the reviewed retained source pools.  This script
covers the remaining exact weighted-cost-four decompositions:

* two ordinary components plus one Switch (``o2+s1``);
* two Switches (``s2``);
* one ordinary component plus one XOR (``o1+x1``).

It reuses the reviewed physical BUS encoder.  Retained source value *and*
driven masks are projected from all 131072 rows, so the existing BUS sources
45/55/56/62 retain their exact Z/D behaviour.  Synthesized Switch outputs may
remain Z internally, identical complete physical BUS driver sets may be
reused, partial overlaps are forbidden, and the final Sum output must always
be driven.  Any SAT witness is independently replayed over the uncompressed
131072-row masks before it is reported.

Offline research only: no game launch, formal-save access, or deployment.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any

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

TARGET_POOLS = {
    81: (4, 5, 6, 7, 22, 23, 24, 25, 45, 50, 51, 52, 54, 55, 56, 76, 77),
    86: (8, 9, 10, 11, 28, 29, 30, 31, 32, 56, 57, 59, 60, 61, 62, 82, 83),
}
TARGET_LABELS = {81: "S2", 86: "S4"}
DEADLINE = 7
FULL_ROWS = 1 << 17
FULL_MASK = (1 << FULL_ROWS) - 1
MIXED_DECOMPOSITIONS = (
    {"name": "o2_s1", "components": 3, "switches": 1, "xors": 0},
    {"name": "s2", "components": 2, "switches": 2, "xors": 0},
    {"name": "o1_x1", "components": 2, "switches": 0, "xors": 1},
)


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


def make_problem(
    source_ids: tuple[int, ...],
    target_id: int,
    states: dict[int, dict[str, int]],
) -> tuple[
    tuple[list[str], list[list[bool]], tuple[int, ...], dict[str, int]],
    dict[str, list[bool]],
    dict[str, Any],
]:
    """Compress exact value/driven signatures without weakening the target."""

    source_bits = [int(states[node_id]["bits"]) for node_id in source_ids]
    source_drivens = [int(states[node_id]["driven"]) for node_id in source_ids]
    target_bits = int(states[target_id]["bits"])
    classes: dict[tuple[int, ...], bool] = {}
    for row in range(FULL_ROWS):
        signature: list[int] = []
        for bits, driven in zip(source_bits, source_drivens, strict=True):
            signature.extend(((bits >> row) & 1, (driven >> row) & 1))
        key = tuple(signature)
        target = bool((target_bits >> row) & 1)
        previous = classes.get(key)
        if previous is not None and previous != target:
            raise RuntimeError(
                f"target {target_id} is not determined by retained value/driven "
                f"signature {key}"
            )
        classes[key] = target

    signatures = sorted(classes)
    names = [f"n{node_id}" for node_id in source_ids]
    values = [[] for _ in names]
    drivens = [[] for _ in names]
    target_row: list[bool] = []
    for signature in signatures:
        for index in range(len(names)):
            values[index].append(bool(signature[index * 2]))
            drivens[index].append(bool(signature[index * 2 + 1]))
        target_row.append(classes[signature])
    target_mask = sum(int(value) << row for row, value in enumerate(target_row))
    arrivals = {
        name: int(states[node_id]["depth"])
        for name, node_id in zip(names, source_ids, strict=True)
    }
    source_driven_map = dict(zip(names, drivens, strict=True))
    metadata = {
        "target": target_id,
        "target_label": TARGET_LABELS[target_id],
        "source_ids": list(source_ids),
        "source_names": names,
        "source_arrivals": arrivals,
        "source_driven_one_counts": {
            name: int(states[node_id]["driven"]).bit_count()
            for name, node_id in zip(names, source_ids, strict=True)
        },
        "source_conflict_one_counts": {
            name: int(states[node_id]["conflict"]).bit_count()
            for name, node_id in zip(names, source_ids, strict=True)
        },
        "compressed_truth_rows": len(signatures),
        "target_one_count": target_bits.bit_count(),
    }
    return (names, values, (target_mask,), arrivals), source_driven_map, metadata


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
    source_ids: tuple[int, ...],
    target_id: int,
    states: dict[int, dict[str, int]],
    gate_library: Any,
) -> dict[str, Any]:
    # The reviewed core appends free constant 0/1 sources after the explicit
    # retained pool.  Mirror those exact indices in the independent replay.
    source_count = len(source_ids) + 2
    values = [int(states[node_id]["bits"]) for node_id in source_ids]
    values.extend((0, FULL_MASK))
    drivens = [int(states[node_id]["driven"]) for node_id in source_ids]
    drivens.extend((FULL_MASK, FULL_MASK))
    arrivals = [int(states[node_id]["depth"]) for node_id in source_ids]
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
        input_arrival = max(
            max(arrivals[source] for source in left_bus),
            max(arrivals[source] for source in right_bus),
        )
        arrival = input_arrival + int(gate_library.DELAY[kind_index])
        arrivals.append(arrival)
        if arrival > int(item["depth_upper_bound"]):
            raise RuntimeError("decoded depth upper bound is below actual arrival")

    output_bus = [int(source) for source in witness["output_buses"][0]]
    buses.append(output_bus)
    for source in output_bus:
        if source >= source_count:
            used_components.add(source - source_count)
    output, output_driven, output_conflict = resolve_bus(output_bus, values, drivens)
    conflict_mask |= output_conflict

    partition_violations = []
    for left_index, left in enumerate(buses):
        for right_index, right in enumerate(buses[left_index + 1 :], left_index + 1):
            if set(left) & set(right) and set(left) != set(right):
                partition_violations.append(
                    {"left_bus": left_index, "right_bus": right_index}
                )

    expected = int(states[target_id]["bits"])
    mismatch_mask = output ^ expected
    undriven_mask = (~output_driven) & FULL_MASK
    expected_live = set(range(len(witness["network"])))
    dead_components = sorted(expected_live - used_components)
    output_arrival = max(arrivals[source] for source in output_bus)
    report = {
        "full_truth_rows": FULL_ROWS,
        "mismatch_count": mismatch_mask.bit_count(),
        "bus_conflict_count": conflict_mask.bit_count(),
        "undriven_output_count": undriven_mask.bit_count(),
        "physical_net_partition_violation_count": len(partition_violations),
        "physical_net_partition_violations": partition_violations,
        "dead_component_count": len(dead_components),
        "dead_components": dead_components,
        "actual_gate": actual_gate,
        "kind_counts": kind_counts,
        "actual_component_arrivals": arrivals[source_count:],
        "output_arrival": output_arrival,
        "deadline": DEADLINE,
    }
    decisive = (
        report["mismatch_count"],
        report["bus_conflict_count"],
        report["undriven_output_count"],
        report["physical_net_partition_violation_count"],
        report["dead_component_count"],
    )
    if any(decisive) or output_arrival > DEADLINE:
        raise RuntimeError(f"independent full replay failed: {report}")
    return report


def fresh_exact_build(exact: dict[str, Any], args: argparse.Namespace):
    """Build from a pristine truth-table copy.

    The reused generic core appends its free ``0/1`` sources in place.  Reset
    ``CURRENT_TRUTH`` before every build so positive regression and both SAT
    solvers receive byte-for-byte equivalent source domains rather than an
    increasing number of redundant constant aliases.
    """

    names, rows, targets, arrivals = exact["_weighted4_truth_template"]
    exact["CURRENT_TRUTH"] = (
        list(names),
        [list(row) for row in rows],
        tuple(targets),
        dict(arrivals),
    )
    return exact["build"](args)


def solve_case(
    exact: dict[str, Any],
    states: dict[int, dict[str, int]],
    source_ids: tuple[int, ...],
    target_id: int,
    decomposition: dict[str, Any],
    solver_name: str,
) -> dict[str, Any]:
    args = argparse.Namespace(
        interface="s6",
        gate_bound=4,
        max_delay=DEADLINE,
        components=int(decomposition["components"]),
        switches=int(decomposition["switches"]),
        xors=int(decomposition["xors"]),
        h_arrival=4,
        c5_arrival=4,
        output_deadlines=str(DEADLINE),
        solver=solver_name,
        timeout=0,
        output=HERE / "unused.json",
    )
    started = time.perf_counter()
    encoder, state = fresh_exact_build(exact, args)
    with Solver(name=solver_name, bootstrap_with=encoder.cnf) as solver:
        answer = solver.solve()
        model = solver.get_model() if answer is True else None
    result: dict[str, Any] = {
        **decomposition,
        "ordinary": int(decomposition["components"])
        - int(decomposition["switches"])
        - int(decomposition["xors"]),
        "weighted_gate": 4,
        "solver": solver_name,
        "status": "sat" if answer is True else "unsat",
        "variables": encoder.pool.top,
        "clauses": len(encoder.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
    }
    if model is not None:
        witness = exact["decode"](args, state, model)
        compressed = exact["verify"](witness, state)
        full = independent_full_replay(
            witness, source_ids, target_id, states, exact["G"]
        )
        if int(witness["actual_gate"]) != 4 or int(full["actual_gate"]) != 4:
            raise RuntimeError("decoded mixed witness does not have weighted cost four")
        result["witness"] = witness
        result["compressed_verification"] = compressed
        result["full_verification"] = full
    return result


def positive_regression(
    exact: dict[str, Any],
    states: dict[int, dict[str, int]],
    source_ids: tuple[int, ...],
    target_id: int,
    solver_name: str,
) -> dict[str, Any]:
    args = argparse.Namespace(
        interface="s6",
        gate_bound=5,
        max_delay=DEADLINE,
        components=5,
        switches=0,
        xors=0,
        h_arrival=4,
        c5_arrival=4,
        output_deadlines=str(DEADLINE),
        solver=solver_name,
        timeout=0,
        output=HERE / "unused.json",
    )
    started = time.perf_counter()
    encoder, state = fresh_exact_build(exact, args)
    with Solver(name=solver_name, bootstrap_with=encoder.cnf) as solver:
        answer = solver.solve()
        model = solver.get_model() if answer is True else None
    if model is None:
        raise RuntimeError(f"target {target_id} mixed-core five-gate regression failed")
    witness = exact["decode"](args, state, model)
    compressed = exact["verify"](witness, state)
    full = independent_full_replay(witness, source_ids, target_id, states, exact["G"])
    if int(witness["actual_gate"]) != 5 or int(full["actual_gate"]) != 5:
        raise RuntimeError("positive regression has the wrong weighted cost")
    return {
        "status": "sat",
        "solver": solver_name,
        "components": 5,
        "exact_switches": 0,
        "exact_xors": 0,
        "variables": encoder.pool.top,
        "clauses": len(encoder.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "witness": witness,
        "compressed_verification": compressed,
        "full_verification": full,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    parser.add_argument(
        "--solvers", default="cadical195,glucose42", help="comma-separated solvers"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "weighted4_mixed_roots_80d7.json",
    )
    args_cli = parser.parse_args()

    solvers = tuple(item.strip() for item in args_cli.solvers.split(",") if item.strip())
    if not solvers:
        parser.error("at least one solver is required")
    materializer = load(MATERIALIZER, "weighted4_root_materializer")
    adapter = load(EXACT_ADAPTER, "weighted4_root_exact_adapter")
    dag_payload = json.loads(args_cli.dag.read_text(encoding="utf-8"))
    ordered_nodes = tuple(dag_payload["factory_dag"]["nodes"])
    states = materializer.logical_states(ordered_nodes)
    started = time.perf_counter()
    targets = []
    any_sat = False

    for target_id, source_ids in TARGET_POOLS.items():
        problem, source_drivens, metadata = make_problem(source_ids, target_id, states)
        exact = adapter.load_core(problem, source_drivens)
        exact["_weighted4_truth_template"] = (
            tuple(problem[0]),
            tuple(tuple(row) for row in problem[1]),
            tuple(problem[2]),
            dict(problem[3]),
        )
        regression = positive_regression(
            exact, states, source_ids, target_id, solvers[0]
        )
        runs = []
        for decomposition in MIXED_DECOMPOSITIONS:
            per_solver = []
            for solver_name in solvers:
                run = solve_case(
                    exact,
                    states,
                    source_ids,
                    target_id,
                    decomposition,
                    solver_name,
                )
                per_solver.append(run)
                any_sat |= run["status"] == "sat"
            statuses = {run["status"] for run in per_solver}
            if len(statuses) != 1:
                raise RuntimeError(
                    f"solver disagreement for target {target_id} {decomposition['name']}: "
                    f"{statuses}"
                )
            runs.append(
                {
                    "decomposition": decomposition,
                    "status": per_solver[0]["status"],
                    "solver_runs": per_solver,
                }
            )
        targets.append(
            {
                **metadata,
                "deadline": DEADLINE,
                "private_gate_cost": 5,
                "replacement_weighted_gate": 4,
                "five_gate_positive_regression": regression,
                "mixed_cost4_runs": runs,
                "status": "sat"
                if any(item["status"] == "sat" for item in runs)
                else "unsat",
            }
        )

    result = {
        "schema": "byte-adder-80d7-weighted4-mixed-root-audit-v1",
        "source": str(args_cli.dag.resolve()),
        "source_sha256": file_sha256(args_cli.dag),
        "reviewed_all_ordinary_audit": str(
            (ROOT / ".research/byte_adder_root/four-gate-dag-sat-80d7.json").resolve()
        ),
        "script_sha256_dependencies": {
            "materializer": file_sha256(MATERIALIZER),
            "exact_adapter": file_sha256(EXACT_ADAPTER),
        },
        "full_truth_rows": FULL_ROWS,
        "solvers": list(solvers),
        "library_costs": {
            "ordinary": 1,
            "switch": 2,
            "xor": 3,
        },
        "covered_remaining_exact_cost4_decompositions": [
            dict(item) for item in MIXED_DECOMPOSITIONS
        ],
        "all_ordinary_cost4": "covered separately by byte_adder_root dual-solver audit",
        "targets": targets,
        "status": "sat" if any_sat else "all-mixed-cost4-unsat",
        "scope": (
            "all live mixed-primitive weighted-cost4 DAGs over each explicit retained "
            "source pool, exact source value/driven masks, physical BUS partition, "
            "and final driven Sum at delay<=7"
        ),
        "limitations": [
            "fixed retained source pools only",
            "does not co-synthesize upstream retained nodes",
            "not a global 79/7 lower bound",
        ],
        "elapsed_seconds": time.perf_counter() - started,
    }
    encoded = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode()
    args_cli.output.parent.mkdir(parents=True, exist_ok=True)
    args_cli.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "output": str(args_cli.output.resolve()),
                "status": result["status"],
                "targets": [
                    {
                        "target": item["target"],
                        "label": item["target_label"],
                        "status": item["status"],
                        "compressed_truth_rows": item["compressed_truth_rows"],
                    }
                    for item in targets
                ],
                "elapsed_seconds": result["elapsed_seconds"],
                "sha256": sha256(encoded).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
