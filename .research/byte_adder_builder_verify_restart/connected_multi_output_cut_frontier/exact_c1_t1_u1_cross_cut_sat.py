"""Exact physical-BUS synthesis for the cross-boundary C1/T1/U1 cut.

Authoritative cut::

    removed paid nodes: 45(C1 BUS), 52(T1), 76(U1)
    current weighted cost: 6
    improving target cost: 5
    fixed shell: 74
    projected complete result at SAT: 79/7/553

The graph-minimal source frontier is ``a0/P1/V0/G0``.  The default expanded
profile additionally exposes the already-paid raw/leaves
``b0/cin/a1/b1/G1/Q1`` so an exact witness may bypass a retained leaf.  The
expanded complete U8/U8/U1 trace compresses to exactly 32 source-state rows.

Output policy is strict and asymmetric:

* C1@2 may be high impedance only when its Boolean target is zero;
* T1@3 and U1@6 must be driven on every row.

The CNF uses the reviewed resolved-BUS semantics, active-bus Switch normal
form, physical-net partition, component liveness, weighted primitive costs,
and recursive timing.  Every SAT model is independently replayed on all
131072 assignments before it is written.

``--seed-current`` fixes the known two-Switch C1 plus AND/NOR phase pair and
is the required positive regression.  This script is research-only: it never
starts the game and never reads or writes the formal save or shared candidate.
"""

from __future__ import annotations

import argparse
from collections import Counter
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
ROOT = HERE.parents[2]
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
EXACT_CORE = (
    ROOT
    / ".research"
    / "byte_adder_ling_theory_agent"
    / "exact_free_ling_pair_sat.py"
)

SOURCE_PROFILES: dict[str, tuple[tuple[int, ...], tuple[str, ...]]] = {
    "minimal": (
        (2, 24, 43, 44),
        ("a0", "P1", "V0", "G0"),
    ),
    "expanded": (
        (2, 3, 18, 43, 44, 4, 5, 22, 23, 24),
        ("a0", "b0", "cin", "V0", "G0", "a1", "b1", "G1", "Q1", "P1"),
    ),
}
TARGET_IDS = (45, 52, 76)
TARGET_LABELS = ("C1", "T1", "U1")
OUTPUT_DEADLINES = (2, 3, 6)
ALLOW_Z_FALSE_OUTPUTS = (True, False, False)
CUT_NODE_IDS = (45, 52, 76)
FULL_ROWS = 1 << 17
FULL_BYTES = FULL_ROWS // 8
FULL_MASK = (1 << FULL_ROWS) - 1
KIND_COST = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 3, "SWITCH": 2}
KIND_DELAY = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 2, "SWITCH": 1}


def load_module(path: Path, name: str):
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
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def make_problem(
    states: dict[int, dict[str, int]],
    source_profile: str,
):
    source_ids, source_labels = SOURCE_PROFILES[source_profile]
    source_bits = [int(states[node_id]["bits"]) for node_id in source_ids]
    source_drivens = [int(states[node_id]["driven"]) for node_id in source_ids]
    target_bits = [int(states[node_id]["bits"]) for node_id in TARGET_IDS]

    for node_id in (*source_ids, *TARGET_IDS):
        conflicts = int(states[node_id]["conflict"]).bit_count()
        if conflicts:
            raise RuntimeError(f"authoritative node {node_id} has {conflicts} conflicts")
    for output, node_id in enumerate(TARGET_IDS):
        if not ALLOW_Z_FALSE_OUTPUTS[output] and int(states[node_id]["driven"]) != FULL_MASK:
            raise RuntimeError(f"strict target {node_id} is not fully driven")
        illegal_target_z = (
            (~int(states[node_id]["driven"]) & int(states[node_id]["bits"]) & FULL_MASK)
        ).bit_count()
        if illegal_target_z:
            raise RuntimeError(f"target {node_id} is Z on {illegal_target_z} true rows")

    classes: dict[tuple[int, ...], tuple[bool, ...]] = {}
    for row in range(FULL_ROWS):
        signature = tuple(
            item
            for bits, driven in zip(source_bits, source_drivens, strict=True)
            for item in ((bits >> row) & 1, (driven >> row) & 1)
        )
        target = tuple(bool((bits >> row) & 1) for bits in target_bits)
        previous = classes.get(signature)
        if previous is not None and previous != target:
            raise RuntimeError(
                f"targets are not functions of source signature {signature}: "
                f"{previous} != {target}"
            )
        classes[signature] = target

    signatures = sorted(classes)
    values = [[] for _ in source_ids]
    drivens = [[] for _ in source_ids]
    compact_targets = [[] for _ in TARGET_IDS]
    for signature in signatures:
        for index in range(len(source_ids)):
            values[index].append(bool(signature[index * 2]))
            drivens[index].append(bool(signature[index * 2 + 1]))
        for index, target in enumerate(classes[signature]):
            compact_targets[index].append(bool(target))
    target_masks = tuple(
        sum(int(value) << row for row, value in enumerate(target))
        for target in compact_targets
    )
    arrivals = {
        label: int(states[node_id]["depth"])
        for label, node_id in zip(source_labels, source_ids, strict=True)
    }
    source_driven_map = dict(zip(source_labels, drivens, strict=True))
    metadata = {
        "source_profile": source_profile,
        "source_ids": list(source_ids),
        "source_names": list(source_labels),
        "source_arrivals": arrivals,
        "source_driven_one_counts": {
            label: int(states[node_id]["driven"]).bit_count()
            for label, node_id in zip(source_labels, source_ids, strict=True)
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
    expected_rows = 12 if source_profile == "minimal" else 32
    if len(signatures) != expected_rows:
        raise RuntimeError(
            f"{source_profile} compressed row count changed: {len(signatures)} != {expected_rows}"
        )
    return (
        (list(source_labels), values, target_masks, arrivals),
        source_driven_map,
        metadata,
    )


def load_exact_core(problem: tuple[Any, ...], source_drivens: dict[str, list[bool]]):
    """Load the reviewed core with exact truth/source/output-policy adapters."""

    text = EXACT_CORE.read_text(encoding="utf-8")
    begin = text.index("def truth_tables(")
    end = text.index("def weighted_bound", begin)
    text = text[:begin] + "def truth_tables(_interface):\n    return CURRENT_TRUTH\n\n\n" + text[end:]

    old_source_policy = '''    # The current phase-fold C7 is a resolved BUS.  It is active whenever
    # either of its two switch enables (T or A, named ``G`` here) is true;
    # otherwise a Boolean-zero carry is represented by Z.  Keeping this mask
    # exact is essential when a synthesized Switch consumes C7.
    if args.interface == "s6":
        t_values = source_values[names.index("T")]
        a_values = source_values[names.index("G")]
        drivens[names.index("C7")] = [
            bool(t_values[case] or a_values[case]) for case in range(assignments)
        ]'''
    new_source_policy = '''    for source_name, source_driven in CURRENT_SOURCE_DRIVENS.items():
        drivens[names.index(source_name)] = list(source_driven)'''
    if old_source_policy not in text:
        raise RuntimeError("source-driven patch anchor changed")
    text = text.replace(old_source_policy, new_source_policy)

    old_output_policy = '''    allow_z_false_outputs = tuple(
        args.interface == "bit56" and output == 2 for output in range(len(targets))
    )'''
    new_output_policy = '''    allow_z_false_outputs = tuple(CURRENT_ALLOW_Z_FALSE_OUTPUTS)
    if len(allow_z_false_outputs) != len(targets):
        raise ValueError("output Z policy length differs from target count")'''
    if old_output_policy not in text:
        raise RuntimeError("output Z-policy patch anchor changed")
    text = text.replace(old_output_policy, new_output_policy)

    namespace = {
        "__name__": "c1_t1_u1_exact_core",
        "__file__": str(EXACT_CORE),
        "__package__": None,
        "CURRENT_TRUTH": problem,
        "CURRENT_SOURCE_DRIVENS": source_drivens,
        "CURRENT_ALLOW_Z_FALSE_OUTPUTS": ALLOW_Z_FALSE_OUTPUTS,
    }
    exec(compile(text, str(EXACT_CORE), "exec"), namespace)
    return namespace


def fresh_build(exact: dict[str, Any], args: argparse.Namespace):
    names, rows, targets, arrivals = exact["_truth_template"]
    exact["CURRENT_TRUTH"] = (
        list(names),
        [list(row) for row in rows],
        tuple(targets),
        dict(arrivals),
    )
    return exact["build"](args)


def resolve_bus(
    bus: list[int],
    values: list[int],
    drivens: list[int],
) -> tuple[int, int, int]:
    ones = 0
    zeros = 0
    for source in bus:
        ones |= values[source] & drivens[source]
        zeros |= (~values[source] & FULL_MASK) & drivens[source]
    return ones & FULL_MASK, (ones | zeros) & FULL_MASK, (ones & zeros) & FULL_MASK


def independent_full_replay(
    witness: dict[str, Any],
    states: dict[int, dict[str, int]],
    source_profile: str,
    expected_components: int,
    expected_switches: int,
    expected_xors: int,
    expected_gate: int,
) -> dict[str, Any]:
    source_ids, source_labels = SOURCE_PROFILES[source_profile]
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
    kind_counts: Counter[str] = Counter()
    actual_gate = 0
    active_bus_violations = []

    network = witness.get("network")
    if not isinstance(network, list) or len(network) != expected_components:
        raise RuntimeError("decoded network component count changed")
    for slot, item in enumerate(network):
        source = source_count + slot
        if int(item["slot"]) != slot or int(item["source"]) != source:
            raise RuntimeError("non-canonical component numbering")
        kind = str(item["kind"])
        if kind not in KIND_COST:
            raise RuntimeError(f"unsupported kind {kind}")
        left_bus = [int(value) for value in item["left_bus"]]
        right_bus = [int(value) for value in item["right_bus"]]
        if not left_bus:
            raise RuntimeError(f"slot {slot} has an empty left bus")
        if kind == "NOT" and right_bus:
            raise RuntimeError(f"NOT slot {slot} has a right input")
        if kind != "NOT" and not right_bus:
            raise RuntimeError(f"binary slot {slot} has an empty right bus")
        for bus_name, bus in (("left", left_bus), ("right", right_bus)):
            if len(bus) != len(set(bus)):
                raise RuntimeError(f"slot {slot} {bus_name} bus contains duplicates")
            for predecessor in bus:
                if predecessor < 0 or predecessor >= source:
                    raise RuntimeError(f"slot {slot} has illegal predecessor {predecessor}")
            if len(bus) > 1:
                illegal = []
                for predecessor in bus:
                    if predecessor < source_count:
                        illegal.append(predecessor)
                    else:
                        predecessor_kind = str(network[predecessor - source_count]["kind"])
                        if predecessor_kind != "SWITCH":
                            illegal.append(predecessor)
                if illegal:
                    active_bus_violations.append(
                        {"slot": slot, "side": bus_name, "illegal_sources": illegal}
                    )
        buses.extend((left_bus, right_bus))
        for predecessor in (*left_bus, *right_bus):
            if predecessor >= source_count:
                used_components.add(predecessor - source_count)

        left, _left_driven, left_conflict = resolve_bus(left_bus, values, drivens)
        right, _right_driven, right_conflict = resolve_bus(right_bus, values, drivens)
        conflict_mask |= left_conflict | right_conflict
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
        else:
            value, driven = left & right, left
        values.append(value & FULL_MASK)
        drivens.append(driven & FULL_MASK)
        arrival = max(arrivals[predecessor] for predecessor in (*left_bus, *right_bus)) + KIND_DELAY[kind]
        arrivals.append(arrival)
        if arrival > int(item["depth_upper_bound"]):
            raise RuntimeError(
                f"slot {slot} actual arrival {arrival} exceeds decoded bound {item['depth_upper_bound']}"
            )
        kind_counts[kind] += 1
        actual_gate += KIND_COST[kind]

    output_buses_raw = witness.get("output_buses")
    if not isinstance(output_buses_raw, list) or len(output_buses_raw) != len(TARGET_IDS):
        raise RuntimeError("decoded output count changed")
    output_values = []
    output_drivens = []
    output_arrivals = []
    for output, output_bus_raw in enumerate(output_buses_raw):
        output_bus = [int(value) for value in output_bus_raw]
        if not output_bus or len(output_bus) != len(set(output_bus)):
            raise RuntimeError(f"output {output} has an empty or duplicate driver set")
        for source in output_bus:
            if source < 0 or source >= source_count + expected_components:
                raise RuntimeError(f"output {output} has illegal source {source}")
            if source >= source_count:
                used_components.add(source - source_count)
        if len(output_bus) > 1:
            illegal = []
            for source in output_bus:
                if source < source_count or str(network[source - source_count]["kind"]) != "SWITCH":
                    illegal.append(source)
            if illegal:
                active_bus_violations.append(
                    {"output": output, "illegal_sources": illegal}
                )
        buses.append(output_bus)
        value, driven, conflict = resolve_bus(output_bus, values, drivens)
        conflict_mask |= conflict
        output_values.append(value)
        output_drivens.append(driven)
        output_arrivals.append(max(arrivals[source] for source in output_bus))

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
    illegal_z_counts = []
    actual_z_counts = []
    driven_mismatch_counts = []
    for output, (value, driven, target_id) in enumerate(
        zip(output_values, output_drivens, TARGET_IDS, strict=True)
    ):
        expected_value = int(states[target_id]["bits"])
        expected_driven = int(states[target_id]["driven"])
        mismatch_counts.append((value ^ expected_value).bit_count())
        actual_z_counts.append(((~driven) & FULL_MASK).bit_count())
        driven_mismatch_counts.append((driven ^ expected_driven).bit_count())
        illegal_mask = (~driven) & FULL_MASK
        if ALLOW_Z_FALSE_OUTPUTS[output]:
            illegal_mask &= expected_value
        illegal_z_counts.append(illegal_mask.bit_count())

    dead_components = sorted(set(range(expected_components)) - used_components)
    report = {
        "full_truth_rows": FULL_ROWS,
        "source_profile": source_profile,
        "source_ids": list(source_ids),
        "source_names": list(source_labels),
        "target_ids": list(TARGET_IDS),
        "target_names": list(TARGET_LABELS),
        "mismatch_counts": mismatch_counts,
        "mismatch_count": sum(mismatch_counts),
        "bus_conflict_count": conflict_mask.bit_count(),
        "actual_z_output_counts": actual_z_counts,
        "illegal_z_output_counts": illegal_z_counts,
        "illegal_z_output_count": sum(illegal_z_counts),
        "authoritative_driven_mismatch_counts": driven_mismatch_counts,
        "physical_net_partition_violation_count": len(partition_violations),
        "physical_net_partition_violations": partition_violations,
        "active_bus_normal_form_violation_count": len(active_bus_violations),
        "active_bus_normal_form_violations": active_bus_violations,
        "dead_component_count": len(dead_components),
        "dead_components": dead_components,
        "actual_component_count": len(network),
        "actual_gate": actual_gate,
        "kind_counts": dict(sorted(kind_counts.items())),
        "actual_switches": kind_counts["SWITCH"],
        "actual_xors": kind_counts["XOR"],
        "actual_component_arrivals": arrivals[source_count:],
        "output_arrivals": output_arrivals,
        "output_deadlines": list(OUTPUT_DEADLINES),
    }
    decisive = (
        report["mismatch_count"],
        report["bus_conflict_count"],
        report["illegal_z_output_count"],
        report["physical_net_partition_violation_count"],
        report["active_bus_normal_form_violation_count"],
        report["dead_component_count"],
        actual_gate != expected_gate,
        kind_counts["SWITCH"] != expected_switches,
        kind_counts["XOR"] != expected_xors,
        len(network) != expected_components,
        any(
            arrival > deadline
            for arrival, deadline in zip(output_arrivals, OUTPUT_DEADLINES, strict=True)
        ),
    )
    if any(decisive):
        raise RuntimeError(f"independent full replay failed: {report}")
    return report


def force_one_hot(encoder: Any, literals: list[int], selected: int) -> None:
    for index, literal in enumerate(literals):
        encoder.force(literal, index == selected)


def fix_current_witness(
    encoder: Any,
    state: dict[str, Any],
    exact: dict[str, Any],
    args: argparse.Namespace,
) -> None:
    if (args.gate_bound, args.components, args.switches, args.xors) != (6, 4, 2, 0):
        raise ValueError("--seed-current requires g6/components4/switches2/xors0")
    source_count = int(state["source_count"])
    names = list(state["names"])
    source = {name: names.index(name) for name in ("a0", "P1", "V0", "G0")}
    node = lambda slot: source_count + slot
    # Commutative inputs are ordered by their smallest source index.
    network = (
        ("SWITCH", (source["a0"],), (source["V0"],), 2),
        ("SWITCH", (source["G0"],), (source["G0"],), 2),
        ("AND", (source["P1"],), (node(0), node(1)), 3),
        ("NOR", (source["P1"],), (node(0), node(1)), 3),
    )
    for slot, (kind, left_bus, right_bus, arrival) in enumerate(network):
        force_one_hot(encoder, state["kinds"][slot], exact["G"].KINDS.index(kind))
        for candidate, literal in enumerate(state["left_uses"][slot]):
            encoder.force(literal, candidate in left_bus)
        for candidate, literal in enumerate(state["right_uses"][slot]):
            encoder.force(literal, candidate in right_bus)
        force_one_hot(encoder, state["levels"][slot], arrival - 1)
    output_buses = ((node(0), node(1)), (node(2),), (node(3),))
    for uses, selected in zip(state["output_uses"], output_buses, strict=True):
        for candidate, literal in enumerate(uses):
            encoder.force(literal, candidate in selected)


def solve_with_timeout(
    encoder: Any,
    solver_name: str,
    timeout: float,
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
    parser.add_argument("--source-profile", choices=tuple(SOURCE_PROFILES), default="expanded")
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
    if args.components <= 0:
        parser.error("--components must be positive")
    if not (0 <= args.switches <= args.components):
        parser.error("--switches must be in [0, components]")
    if not (0 <= args.xors <= args.components - args.switches):
        parser.error("--xors exceeds remaining components")
    ordinary = args.components - args.switches - args.xors
    weighted = ordinary + 2 * args.switches + 3 * args.xors
    if weighted != args.gate_bound:
        parser.error(
            f"decomposition is not exact: ordinary/switch/xor={ordinary}/{args.switches}/{args.xors} "
            f"has weighted cost {weighted}, not {args.gate_bound}"
        )

    materializer = load_module(MATERIALIZER, "c1_t1_u1_materializer")
    dag = json.loads(args.dag.read_text(encoding="utf-8"))
    if (int(dag["metrics"]["gate"]), int(dag["metrics"]["delay"])) != (80, 7):
        raise RuntimeError("authoritative DAG metrics changed")
    ordered_nodes = tuple(dag["factory_dag"]["nodes"])
    states = materializer.logical_states(ordered_nodes)
    problem, source_drivens, metadata = make_problem(states, args.source_profile)
    exact = load_exact_core(problem, source_drivens)
    exact["_truth_template"] = (
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
        h_arrival=0,
        c5_arrival=0,
        output_deadlines=",".join(map(str, OUTPUT_DEADLINES)),
        solver=args.solver,
        timeout=args.timeout,
        output=args.output,
    )
    started = time.perf_counter()
    encoder, state = fresh_build(exact, internal)
    if tuple(state["allow_z_false_outputs"]) != ALLOW_Z_FALSE_OUTPUTS:
        raise RuntimeError("loaded core output policy changed")
    if args.seed_current:
        fix_current_witness(encoder, state, exact, args)
    build_seconds = time.perf_counter() - started
    solve_started = time.perf_counter()
    answer, model = solve_with_timeout(encoder, args.solver, args.timeout)
    solve_seconds = time.perf_counter() - solve_started
    status = "sat" if answer is True else "unsat" if answer is False else "unknown"
    result: dict[str, Any] = {
        "schema": "byte-adder-80d7-c1-t1-u1-cross-cut-strict-physical-v1",
        "status": status,
        "source": args.dag.resolve().relative_to(ROOT).as_posix(),
        "source_sha256": file_sha256(args.dag),
        "source_structural_sha256": dag["metrics"]["structural_sha256"],
        "source_factory_dag_sha256": dag["factory_dag"]["sha256"],
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "dependency_sha256": {
            "materializer": file_sha256(MATERIALIZER),
            "exact_core": file_sha256(EXACT_CORE),
        },
        "cut_node_ids": list(CUT_NODE_IDS),
        "current_cut_gate": 6,
        "target_cut_gate": 5,
        "fixed_shell_gate": 74,
        "projected_complete_gate_at_target": 79,
        "projected_complete_delay": 7,
        "projected_complete_energy": 553,
        "full_truth_rows": FULL_ROWS,
        **metadata,
        "output_deadlines": list(OUTPUT_DEADLINES),
        "allow_z_false_outputs": list(ALLOW_Z_FALSE_OUTPUTS),
        "gate_bound": args.gate_bound,
        "components": args.components,
        "exact_ordinary": ordinary,
        "exact_switches": args.switches,
        "exact_xors": args.xors,
        "weighted_gate": weighted,
        "seed_current": args.seed_current,
        "physical_nets": True,
        "all_components_live": True,
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
        full = independent_full_replay(
            witness,
            states,
            args.source_profile,
            args.components,
            args.switches,
            args.xors,
            args.gate_bound,
        )
        if any(int(value) for value in compressed.values()):
            raise RuntimeError(f"compressed verification failed: {compressed}")
        if int(witness["actual_gate"]) != args.gate_bound:
            raise RuntimeError("decoded weighted gate differs from exact decomposition")
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
                "source_profile": args.source_profile,
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
