"""Exact physical synthesis worker for one ranked private-frontier case.

The worker consumes the deterministic ranking artifact rather than hard-coding
an interface.  ``expanded`` retains the private frontier and supports a forced
current-network positive regression.  ``no_private`` removes exactly the paid
private node while retaining every other ancestor source and searches at the
same exact weighted cost as the current cut.

Every SAT is replayed over all 131072 U8/U8/U1 assignments by the reviewed
physical-BUS replay.  This file never launches the game or touches a formal
save, shared candidate, history, or stage.
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

import pysat


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FRONTIER_DIR = HERE.parent
DEFAULT_RANKING = HERE / "same_cost_private_frontier_ranking.json"
DEFAULT_DAG = ROOT / ".research/byte_adder_root/byte-adder-hybrid-phasefold-g80-d7.json"
BASE_WORKER = FRONTIER_DIR / "exact_c1_t1_u1_cross_cut_sat.py"
FULL_ROWS = 1 << 17
FULL_MASK = (1 << FULL_ROWS) - 1
COMMUTATIVE = {"AND", "OR", "NAND", "NOR", "XOR"}
KIND_DELAY = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 2, "SWITCH": 1}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def path_ref(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def find_case(ranking: dict[str, Any], case_key: str) -> dict[str, Any]:
    matches = [
        row
        for field in ("ranked_candidates", "frozen_cases")
        for row in ranking.get(field, ())
        if row.get("case_key") == case_key
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected one ranked case {case_key!r}, got {len(matches)}")
    case = matches[0]
    if not case.get("source_shell_functional_audit"):
        raise RuntimeError(f"case {case_key} lacks completed source-shell functional audit")
    return case


def make_problem(
    base: Any,
    states: dict[int, dict[str, int]],
    source_ids: tuple[int, ...],
    source_names: tuple[str, ...],
    target_ids: tuple[int, ...],
    target_names: tuple[str, ...],
    allow_z_false: tuple[bool, ...],
) -> tuple[tuple[Any, ...], dict[str, list[bool]], dict[str, Any]]:
    if len(source_ids) != len(source_names) or len(set(source_names)) != len(source_names):
        raise RuntimeError("source ID/name contract is not one-to-one")
    if len(target_ids) != len(target_names) or len(target_ids) != len(allow_z_false):
        raise RuntimeError("target contract lengths differ")
    source_bits = [int(states[node_id]["bits"]) for node_id in source_ids]
    source_drivens = [int(states[node_id]["driven"]) for node_id in source_ids]
    target_bits = [int(states[node_id]["bits"]) for node_id in target_ids]
    for node_id in (*source_ids, *target_ids):
        if int(states[node_id]["conflict"]):
            raise RuntimeError(f"authoritative node {node_id} has a conflict")
    for output, node_id in enumerate(target_ids):
        driven = int(states[node_id]["driven"])
        if not allow_z_false[output] and driven != FULL_MASK:
            raise RuntimeError(f"strict target {node_id} is not fully driven")
        if ((~driven) & int(states[node_id]["bits"]) & FULL_MASK).bit_count():
            raise RuntimeError(f"target {node_id} is Z on a true row")

    classes: dict[tuple[int, ...], tuple[bool, ...]] = {}
    for row in range(FULL_ROWS):
        signature = tuple(
            item
            for bits, driven in zip(source_bits, source_drivens, strict=True)
            for item in ((bits >> row) & 1, (driven >> row) & 1)
        )
        target = tuple(bool((bits >> row) & 1) for bits in target_bits)
        previous = classes.setdefault(signature, target)
        if previous != target:
            raise RuntimeError(f"targets are not functions of source signature {signature}")
    signatures = sorted(classes)
    values = [[] for _ in source_ids]
    drivens = [[] for _ in source_ids]
    compact_targets = [[] for _ in target_ids]
    for signature in signatures:
        for index in range(len(source_ids)):
            values[index].append(bool(signature[2 * index]))
            drivens[index].append(bool(signature[2 * index + 1]))
        for index, value in enumerate(classes[signature]):
            compact_targets[index].append(bool(value))
    target_masks = tuple(
        sum(int(value) << row for row, value in enumerate(target))
        for target in compact_targets
    )
    arrivals = {
        name: int(states[node_id]["depth"])
        for name, node_id in zip(source_names, source_ids, strict=True)
    }
    source_driven_map = dict(zip(source_names, drivens, strict=True))
    metadata = {
        "source_ids": list(source_ids),
        "source_names": list(source_names),
        "source_arrivals": arrivals,
        "source_driven_one_counts": {
            name: int(states[node_id]["driven"]).bit_count()
            for name, node_id in zip(source_names, source_ids, strict=True)
        },
        "target_ids": list(target_ids),
        "target_names": list(target_names),
        "target_one_counts": {
            name: int(states[node_id]["bits"]).bit_count()
            for name, node_id in zip(target_names, target_ids, strict=True)
        },
        "target_driven_one_counts": {
            name: int(states[node_id]["driven"]).bit_count()
            for name, node_id in zip(target_names, target_ids, strict=True)
        },
        "compressed_truth_rows": len(signatures),
    }
    return (
        (list(source_names), values, target_masks, arrivals),
        source_driven_map,
        metadata,
    )


def selector_mask(bus: tuple[int, ...]) -> int:
    return sum(1 << source for source in bus)


def force_current_seed(
    base: Any,
    exact: dict[str, Any],
    encoder: Any,
    state: dict[str, Any],
    ordered_nodes: tuple[dict[str, Any], ...],
    states: dict[int, dict[str, int]],
    case: dict[str, Any],
) -> dict[str, Any]:
    source_ids = tuple(map(int, case["expanded_source_ids"]))
    source_index = {node_id: index for index, node_id in enumerate(source_ids)}
    source_count = int(state["source_count"])
    if source_count != len(source_ids) + 2:
        raise RuntimeError("loaded source count differs from expanded shell")
    cut = set(map(int, case["cut_node_ids"]))
    target_ids = tuple(map(int, case["target_ids"]))
    arrivals = [int(states[node_id]["depth"]) for node_id in source_ids] + [0, 0]
    node_buses: dict[int, tuple[int, ...]] = {}
    forced_network = []

    def signal_bus(node_id: int) -> tuple[int, ...]:
        if node_id in node_buses:
            return node_buses[node_id]
        if node_id in source_index:
            return (source_index[node_id],)
        raise RuntimeError(f"current cut references unavailable source node {node_id}")

    def append_component(kind: str, left: tuple[int, ...], right: tuple[int, ...]) -> int:
        if kind in COMMUTATIVE and selector_mask(left) > selector_mask(right):
            left, right = right, left
        slot = len(forced_network)
        source = source_count + slot
        arrival = max(arrivals[index] for index in (*left, *right)) + KIND_DELAY[kind]
        if arrival > max(map(int, case["target_deadlines"])):
            raise RuntimeError(f"current component {slot} exceeds encoder max delay")
        forced_network.append(
            {
                "slot": slot,
                "source": source,
                "kind": kind,
                "left_bus": list(left),
                "right_bus": list(right),
                "arrival": arrival,
            }
        )
        arrivals.append(arrival)
        return source

    for node in ordered_nodes:
        node_id = int(node["id"])
        if node_id not in cut:
            continue
        op = str(node["op"])
        if op == "BUS":
            drivers = tuple(node.get("drivers", ()))
            if not drivers or int(node["cost"]) != 2 * len(drivers):
                raise RuntimeError(f"BUS node {node_id} driver/cost contract changed")
            bus = tuple(
                append_component(
                    "SWITCH",
                    signal_bus(int(driver["enable"])),
                    signal_bus(int(driver["data"])),
                )
                for driver in drivers
            )
            node_buses[node_id] = bus
        else:
            arguments = tuple(map(int, node.get("args", ())))
            if op == "NOT":
                if len(arguments) != 1:
                    raise RuntimeError(f"NOT node {node_id} arity changed")
                left, right = signal_bus(arguments[0]), ()
            else:
                if len(arguments) != 2 or op not in KIND_DELAY:
                    raise RuntimeError(f"node {node_id} has unsupported op/arity {op}/{arguments}")
                left, right = signal_bus(arguments[0]), signal_bus(arguments[1])
            node_buses[node_id] = (append_component(op, left, right),)
        actual_node_arrival = max(arrivals[source] for source in node_buses[node_id])
        if actual_node_arrival != int(states[node_id]["depth"]):
            raise RuntimeError(
                f"current node {node_id} arrival {actual_node_arrival} != authoritative {states[node_id]['depth']}"
            )

    decomposition = case["current_decomposition"]
    if len(forced_network) != int(decomposition["components"]):
        raise RuntimeError("forced current component count differs from ranking")
    kind_counts = {kind: sum(item["kind"] == kind for item in forced_network) for kind in KIND_DELAY}
    if kind_counts["SWITCH"] != int(decomposition["switches"]) or kind_counts["XOR"] != int(decomposition["xors"]):
        raise RuntimeError("forced current kind decomposition differs from ranking")

    for item in forced_network:
        slot = int(item["slot"])
        base.force_one_hot(encoder, state["kinds"][slot], exact["G"].KINDS.index(item["kind"]))
        left = set(item["left_bus"])
        right = set(item["right_bus"])
        for candidate, literal in enumerate(state["left_uses"][slot]):
            encoder.force(literal, candidate in left)
        for candidate, literal in enumerate(state["right_uses"][slot]):
            encoder.force(literal, candidate in right)
        base.force_one_hot(encoder, state["levels"][slot], int(item["arrival"]) - 1)
    output_buses = [node_buses[node_id] for node_id in target_ids]
    for uses, selected in zip(state["output_uses"], output_buses, strict=True):
        selected_set = set(selected)
        for candidate, literal in enumerate(uses):
            encoder.force(literal, candidate in selected_set)
    return {"network": forced_network, "output_buses": [list(bus) for bus in output_buses]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranking", type=Path, default=DEFAULT_RANKING)
    parser.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    parser.add_argument("--case-key", required=True)
    parser.add_argument("--source-profile", choices=("expanded", "no_private"), required=True)
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int, required=True)
    parser.add_argument("--xors", type=int, required=True)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=0.0)
    parser.add_argument("--seed-current", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.timeout < 0 or args.components <= 0:
        parser.error("invalid timeout/component count")
    if not (0 <= args.switches <= args.components):
        parser.error("invalid Switch count")
    if not (0 <= args.xors <= args.components - args.switches):
        parser.error("invalid XOR count")
    ordinary = args.components - args.switches - args.xors
    weighted = ordinary + 2 * args.switches + 3 * args.xors
    if weighted != args.gate_bound:
        parser.error(f"decomposition cost {weighted} != gate bound {args.gate_bound}")

    ranking = json.loads(args.ranking.read_text(encoding="utf-8"))
    case = find_case(ranking, args.case_key)
    current_cost = int(case["current_cut_gate"])
    if args.gate_bound != current_cost:
        parser.error(f"same-cost case requires exact gate bound {current_cost}")
    if args.seed_current:
        if args.source_profile != "expanded":
            parser.error("--seed-current requires expanded source profile")
        expected = case["current_decomposition"]
        actual = (args.components, args.switches, args.xors)
        if actual != (int(expected["components"]), int(expected["switches"]), int(expected["xors"])):
            parser.error("--seed-current decomposition differs from current cut")

    base = load_module(BASE_WORKER, "ranked_private_frontier_base_worker")
    target_ids = tuple(map(int, case["target_ids"]))
    target_names = tuple(map(str, case["target_names"]))
    deadlines = tuple(map(int, case["target_deadlines"]))
    allow_z_false = tuple(map(bool, case["target_may_z"]))
    source_ids = tuple(map(int, case[f"{args.source_profile}_source_ids"]))
    source_names = tuple(map(str, case[f"{args.source_profile}_source_names"]))
    base.SOURCE_PROFILES = {args.source_profile: (source_ids, source_names)}
    base.TARGET_IDS = target_ids
    base.TARGET_LABELS = target_names
    base.OUTPUT_DEADLINES = deadlines
    base.ALLOW_Z_FALSE_OUTPUTS = allow_z_false
    base.CUT_NODE_IDS = tuple(map(int, case["cut_node_ids"]))

    dag = json.loads(args.dag.read_text(encoding="utf-8"))
    if (int(dag["metrics"]["gate"]), int(dag["metrics"]["delay"])) != (80, 7):
        raise RuntimeError("authoritative DAG metrics changed")
    if ranking["authoritative"]["dag_sha256"] != digest(args.dag):
        raise RuntimeError("ranking/DAG SHA mismatch")
    ordered_nodes = tuple(dag["factory_dag"]["nodes"])
    by_id = {int(node["id"]): node for node in ordered_nodes}
    consumers = {node_id: set() for node_id in by_id}
    for node in ordered_nodes:
        for predecessor in node.get("args", ()):
            consumers[int(predecessor)].add(int(node["id"]))
    private_id = int(case["private_frontier_id"])
    cut = set(map(int, case["cut_node_ids"]))
    if consumers[private_id] != set(map(int, case["private_frontier_consumers"])) or not consumers[private_id] <= cut:
        raise RuntimeError("private-frontier consumer closure changed")
    private_cost = int(by_id[private_id]["cost"])
    prune_cost = 0 if args.source_profile == "expanded" else private_cost
    prune_ids = [] if args.source_profile == "expanded" else [private_id]
    if private_id in source_ids:
        if args.source_profile != "expanded":
            raise RuntimeError("no-private source shell still contains private node")
    elif args.source_profile == "expanded":
        raise RuntimeError("expanded source shell lost private node")
    fixed_shell = 80 - current_cost - prune_cost
    projected_gate = fixed_shell + args.gate_bound
    expected_projected = 80 if args.source_profile == "expanded" else int(case["projected_complete_gate"])
    if projected_gate != expected_projected:
        raise RuntimeError("same-cost projection accounting changed")

    materializer = load_module(base.MATERIALIZER, "ranked_private_frontier_materializer")
    states = materializer.logical_states(ordered_nodes)
    problem, source_drivens, metadata = make_problem(
        base, states, source_ids, source_names, target_ids, target_names, allow_z_false
    )
    expected_rows = int(case[f"{args.source_profile}_compressed_truth_rows"])
    if int(metadata["compressed_truth_rows"]) != expected_rows:
        raise RuntimeError("ranking/worker compressed source rows differ")
    exact = base.load_exact_core(problem, source_drivens)
    exact["_truth_template"] = (
        tuple(problem[0]), tuple(tuple(row) for row in problem[1]), tuple(problem[2]), dict(problem[3])
    )
    internal = argparse.Namespace(
        interface="dual",
        gate_bound=args.gate_bound,
        max_delay=max(deadlines),
        components=args.components,
        switches=args.switches,
        xors=args.xors,
        h_arrival=0,
        c5_arrival=0,
        output_deadlines=",".join(map(str, deadlines)),
        solver=args.solver,
        timeout=args.timeout,
        output=args.output,
    )
    started = time.perf_counter()
    encoder, state = base.fresh_build(exact, internal)
    if tuple(state["allow_z_false_outputs"]) != allow_z_false:
        raise RuntimeError("loaded core output policy changed")
    seed_contract = None
    if args.seed_current:
        seed_contract = force_current_seed(base, exact, encoder, state, ordered_nodes, states, case)
    build_seconds = time.perf_counter() - started
    solve_started = time.perf_counter()
    answer, model = base.solve_with_timeout(encoder, args.solver, args.timeout)
    solve_seconds = time.perf_counter() - solve_started
    status = "sat" if answer is True else "unsat" if answer is False else "unknown"
    result: dict[str, Any] = {
        "schema": "byte-adder-80d7-ranked-private-frontier-same-cost-v1",
        "status": status,
        "ranking": path_ref(args.ranking),
        "ranking_sha256": digest(args.ranking),
        "case_key": args.case_key,
        "source": path_ref(args.dag),
        "source_sha256": digest(args.dag),
        "source_structural_sha256": dag["metrics"]["structural_sha256"],
        "source_factory_dag_sha256": dag["factory_dag"]["sha256"],
        "script_sha256": digest(Path(__file__).resolve()),
        "dependency_sha256": {
            "base_worker": digest(BASE_WORKER),
            "materializer": digest(base.MATERIALIZER),
            "exact_core": digest(base.EXACT_CORE),
        },
        "cut_node_ids": list(map(int, case["cut_node_ids"])),
        "current_cut_gate": current_cost,
        "source_profile": args.source_profile,
        "private_frontier_id": private_id,
        "private_frontier_consumers": sorted(consumers[private_id]),
        "guaranteed_prune_ids": prune_ids,
        "guaranteed_prune_cost": prune_cost,
        "fixed_shell_after_guaranteed_prune": fixed_shell,
        "projected_complete_gate_at_bound": projected_gate,
        "projected_complete_delay": 7,
        "projected_complete_energy": projected_gate * 7,
        "full_truth_rows": FULL_ROWS,
        "source_profile": args.source_profile,
        **metadata,
        "output_deadlines": list(deadlines),
        "allow_z_false_outputs": list(allow_z_false),
        "gate_bound": args.gate_bound,
        "components": args.components,
        "exact_ordinary": ordinary,
        "exact_switches": args.switches,
        "exact_xors": args.xors,
        "weighted_gate": weighted,
        "seed_current": args.seed_current,
        "seed_contract": seed_contract,
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
        full = base.independent_full_replay(
            witness, states, args.source_profile,
            args.components, args.switches, args.xors, args.gate_bound,
        )
        if any(int(value) for value in compressed.values()):
            raise RuntimeError(f"compressed replay failed: {compressed}")
        result["witness"] = witness
        result["compressed_verification"] = compressed
        result["full_verification"] = full

    output_sha = atomic_write(args.output, result)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "output_sha256": output_sha,
                "status": status,
                "case_key": args.case_key,
                "source_profile": args.source_profile,
                "projected_complete_gate_at_bound": projected_gate,
                "decomposition": [ordinary, args.switches, args.xors],
                "compressed_truth_rows": metadata["compressed_truth_rows"],
                "variables": encoder.pool.top,
                "clauses": len(encoder.cnf.clauses),
                "build_seconds": build_seconds,
                "solve_seconds": solve_seconds,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if status != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
