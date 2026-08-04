"""Exact physical synthesis for arbitrary scalar multi-output truth tuples.

This is a thin, hash-separate generalization layer over the frozen reviewed
physical CNF model.  It adds caller-supplied truth masks and an independent
arrival bound for every output without modifying the baseline solver used by
the FullAdder closure certificates.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import threading
import time


ROOT = Path(__file__).resolve().parents[2]
BASE_SOLVER = (
    ROOT
    / ".research"
    / "byte_adder_component_byproduct_catalog"
    / "exact_pretarget_physical.py"
)


def _load_base():
    spec = importlib.util.spec_from_file_location("tuple_exact_physical_base", BASE_SOLVER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load physical base solver {BASE_SOLVER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


P = _load_base()


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


@contextmanager
def custom_target(spec: dict[str, object]):
    original = P.target_spec
    P.target_spec = lambda _name: spec
    try:
        yield
    finally:
        P.target_spec = original


def truth_spec(
    input_count: int,
    masks: list[int],
    output_names: list[str],
) -> dict[str, object]:
    assignments = 1 << input_count
    limit = 1 << assignments
    if not masks:
        raise ValueError("at least one truth mask is required")
    if len(output_names) != len(masks):
        raise ValueError("output-name count differs from truth-mask count")
    for mask in masks:
        if not 0 <= mask < limit:
            raise ValueError(
                f"truth mask {mask:#x} does not fit {assignments} assignments"
            )
    return {
        "name": "truth-tuple",
        "input_names": tuple(f"Input {index}" for index in range(input_count)),
        "output_names": tuple(output_names),
        "assignments": assignments,
        "targets": tuple(masks),
    }


def add_output_arrival_bounds(
    enc,
    state: dict[str, object],
    output_max_delays: list[int],
    global_max_delay: int,
) -> None:
    source_count = int(state["source_count"])
    output_uses = state["output_uses"]
    levels = state["levels"]
    if len(output_uses) != len(output_max_delays):
        raise RuntimeError("output arrival-bound count drift")
    for uses, bound in zip(output_uses, output_max_delays, strict=True):
        for source in range(source_count, len(uses)):
            slot = source - source_count
            for depth in range(bound + 1, global_max_delay + 1):
                enc.clause((-uses[source], -levels[slot][depth]))


def replay_output_arrivals(payload: dict[str, object]) -> list[int]:
    input_count = int(payload["input_count"])
    source_count = input_count + 2
    depths = [0] * source_count
    for item in payload["network"]:
        predecessors = [*item["left_bus"], *item["right_bus"]]
        depth = max((depths[source] for source in predecessors), default=0) + int(
            item["delay"]
        )
        if depth > int(item["depth_upper_bound"]):
            raise RuntimeError("decoded component arrival exceeds its CNF level")
        depths.append(depth)
    return [
        max((depths[source] for source in bus), default=0)
        for bus in payload["output_buses"]
    ]


def physical_owner_manifest(payload: dict[str, object]) -> dict[str, object]:
    buses: list[tuple[str, tuple[int, ...]]] = []
    for item in payload["network"]:
        buses.append((f"slot:{item['slot']}:left", tuple(sorted(item["left_bus"]))))
        if item["right_bus"]:
            buses.append((f"slot:{item['slot']}:right", tuple(sorted(item["right_bus"]))))
    for index, bus in enumerate(payload["output_buses"]):
        buses.append((f"output:{index}", tuple(sorted(bus))))
    unique_sets = sorted({drivers for _label, drivers in buses})
    owner_by_set = {
        drivers: f"physical_net_owner_{index:03d}"
        for index, drivers in enumerate(unique_sets)
    }
    references = [
        {"reference": label, "drivers": list(drivers), "owner": owner_by_set[drivers]}
        for label, drivers in buses
    ]
    source_owners: dict[int, set[str]] = {}
    for _label, drivers in buses:
        owner = owner_by_set[drivers]
        for source in drivers:
            source_owners.setdefault(source, set()).add(owner)
    for source, owners in source_owners.items():
        if len(owners) > 1:
            raise RuntimeError(
                f"physical source {source} appears in partially overlapping owners {owners}"
            )

    source_count = int(payload["input_count"]) + 2
    component_owners = []
    for item in payload["network"]:
        source = source_count + int(item["slot"])
        output_owner = next(iter(source_owners.get(source, {f"private_source_{source}"})))
        left_owner = owner_by_set[tuple(sorted(item["left_bus"]))]
        right_owner = (
            owner_by_set[tuple(sorted(item["right_bus"]))]
            if item["right_bus"]
            else None
        )
        row = {
            "slot": item["slot"],
            "source": source,
            "kind": item["kind"],
            "left_bus_owner": left_owner,
            "right_bus_owner": right_owner,
            "output_net_owner": output_owner,
        }
        if item["kind"] == "SWITCH":
            row["partial_driver_owner"] = output_owner
        if item["kind"] == "NORMALIZE":
            row["maker_splitter_physical_owner"] = f"maker_splitter_slot_{item['slot']}"
            row["normalizes_bus_owner"] = left_owner
        component_owners.append(row)
    return {
        "wire_net_partition_enforced": bool(payload["physical_nets"]),
        "owner_count": len(unique_sets),
        "owners": [
            {"owner": owner_by_set[drivers], "drivers": list(drivers)}
            for drivers in unique_sets
        ],
        "references": references,
        "components": component_owners,
        "output_owners": [
            owner_by_set[tuple(sorted(bus))] for bus in payload["output_buses"]
        ],
    }


def solve(args: argparse.Namespace) -> dict[str, object]:
    masks = [int(value, 0) for value in args.truth_mask]
    output_names = args.output_name or [f"Output {index}" for index in range(len(masks))]
    if len(args.output_max_delay) != len(masks):
        raise ValueError("one --output-max-delay is required for every truth mask")
    if any(value < 0 for value in args.output_max_delay):
        raise ValueError("output delay bounds must be nonnegative")
    global_max_delay = max(args.output_max_delay, default=0)
    spec = truth_spec(args.input_count, masks, output_names)
    started = time.perf_counter()
    with custom_target(spec):
        enc, state = P.build(
            "truth-tuple",
            args.gate_bound,
            global_max_delay,
            args.components,
            args.normalizers,
            allow_z_false=args.allow_z_false,
            exact_switches=args.switches,
            exact_xors=args.xors,
            physical_nets=not args.abstract_buses,
        )
        add_output_arrival_bounds(
            enc,
            state,
            args.output_max_delay,
            global_max_delay,
        )
        status = "unknown"
        model = None
        timer = None
        with P.Solver(name=args.solver, bootstrap_with=enc.cnf) as solver:
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

        assignments = int(spec["assignments"])
        hex_width = (assignments + 3) // 4
        payload: dict[str, object] = {
            "schema": "tc-arbitrary-truth-tuple-exact-physical-v1",
            "status": status,
            "target": "truth-tuple",
            "input_count": args.input_count,
            "input_ports": list(spec["input_names"]),
            "output_ports": list(spec["output_names"]),
            "target_truth_tables_hex": [f"{mask:0{hex_width}x}" for mask in masks],
            "output_max_delays": list(args.output_max_delay),
            "gate_bound": args.gate_bound,
            "max_delay": global_max_delay,
            "components": args.components,
            "exact_normalizers": args.normalizers,
            "exact_switches": args.switches,
            "exact_xors": args.xors,
            "allow_z_false": args.allow_z_false,
            "physical_nets": not args.abstract_buses,
            "solver": args.solver,
            "timeout_seconds": args.timeout,
            "conflict_budget": args.conflicts,
            "variables": enc.pool.top,
            "clauses": len(enc.cnf.clauses),
            "solve_seconds": time.perf_counter() - started,
            "library": {
                kind: {"gate": P.COST[index], "delay": P.DELAY[index]}
                for index, kind in enumerate(P.KINDS)
            },
            "semantics": {
                "switch": "value=enable&data; driven=enable; disabled output is Z",
                "ordinary_gate_reads_z_as_zero": True,
                "normalizer": "Maker/Splitter physical owner: Z is read as numeric 0 and emitted driven at gate/delay 0/0",
                "normalizer_complete_normal_form": "normalizer inputs contain only Switch output pins",
                "multi_driver_conflict_forbidden": True,
                "physical_driver_sets_form_wire_net_partitions": not args.abstract_buses,
                "primary_output_policy": (
                    "target zero may be Z" if args.allow_z_false else "fully driven on every row"
                ),
                "free_sources": "real raw input ports plus constants 0 and 1; complements are not free",
            },
            "dependencies": {
                str(BASE_SOLVER): sha256(BASE_SOLVER.read_bytes()).hexdigest(),
                str(Path(__file__).resolve()): sha256(Path(__file__).read_bytes()).hexdigest(),
            },
        }
        if model is not None:
            payload.update(P.decode(state, model))
            payload["verification"] = P.verify_payload(payload)
            bad_keys = (
                "mismatch_count",
                "bus_conflict_count",
                "undriven_output_count",
                "normalizer_normal_form_violation_count",
                "physical_net_partition_violation_count",
            )
            if any(payload["verification"][key] for key in bad_keys):
                raise RuntimeError("decoded tuple witness failed base physical replay")
            arrivals = replay_output_arrivals(payload)
            if any(
                actual > bound
                for actual, bound in zip(arrivals, args.output_max_delay, strict=True)
            ):
                raise RuntimeError(
                    f"decoded output arrivals {arrivals} exceed {args.output_max_delay}"
                )
            payload["verification"]["replayed_output_arrivals"] = arrivals
            payload["physical_owners"] = physical_owner_manifest(payload)
        elif status == "unknown":
            payload["reason_unknown"] = "timeout-or-conflict-budget"
        payload["case_sha256"] = sha256(
            canonical_json(
                {
                    "input_count": args.input_count,
                    "truth_masks": masks,
                    "output_names": output_names,
                    "output_max_delays": args.output_max_delay,
                    "gate_bound": args.gate_bound,
                    "components": args.components,
                    "normalizers": args.normalizers,
                    "switches": args.switches,
                    "xors": args.xors,
                    "allow_z_false": args.allow_z_false,
                    "physical_nets": not args.abstract_buses,
                }
            )
        ).hexdigest()
        return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-count", type=int, required=True)
    parser.add_argument("--truth-mask", action="append", required=True)
    parser.add_argument("--output-name", action="append")
    parser.add_argument("--output-max-delay", action="append", type=int, required=True)
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--normalizers", type=int, default=0)
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int)
    parser.add_argument("--allow-z-false", action="store_true")
    parser.add_argument("--abstract-buses", action="store_true")
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--conflicts", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.input_count <= 6:
        parser.error("--input-count must be in 1..6")
    if args.gate_bound < 0 or args.components < 0 or args.normalizers < 0:
        parser.error("bounds must be nonnegative")
    if args.normalizers > args.components:
        parser.error("normalizers cannot exceed components")
    payload = solve(args)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
