"""Exact structural shards for a single-driver C5 output.

The strict-C3 D7 ``g13/n11/s2/x0`` CNF permits either one output driver or a
compatible two-Switch bus.  This script covers the single-driver half.  A
component driver is normalized by placing all of its component ancestors
first, the driver next, and every non-ancestor afterward.  A separate shard
covers direct paid-source or constant drivers.

The script is offline only and does not access Turing Complete saves or the
shared Byte Adder candidate.
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
from types import SimpleNamespace

import pysat
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
EXACT_PATH = HERE / "exact_bit34_joint_sat.py"
SOURCE_SHARD = "source"
COMPONENT_SHARDS = tuple(f"k{count}" for count in range(11))
ALL_SHARDS = (SOURCE_SHARD, *COMPONENT_SHARDS)


def load_exact():
    spec = importlib.util.spec_from_file_location(
        "bit34_c5_single_driver_exact", EXACT_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load exact search: {EXACT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


exact = load_exact()


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def atomic_write(path: Path, payload: dict[str, object]) -> None:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)


def base_args() -> SimpleNamespace:
    return SimpleNamespace(
        profile="d7_80",
        gate_bound=13,
        max_delay=7,
        components=11,
        switches=2,
        xors=0,
        output_deadlines="5,7,4",
        slot_kind=[],
        seed_current=False,
    )


def add_shard_constraints(
    encoder,
    state: dict[str, object],
    shard: str,
) -> dict[str, object]:
    output_uses = state["output_uses"][2]
    source_count = int(state["source_count"])

    if shard == SOURCE_SHARD:
        units = [
            -output_uses[source_count + slot]
            for slot in range(base_args().components)
        ]
        encoder.cnf.extend([[literal] for literal in units])
        description = {
            "shard": shard,
            "driver_class": "paid source or free constant",
            "forbidden_component_output_slots": list(range(base_args().components)),
        }
    elif shard in COMPONENT_SHARDS:
        ancestor_count = int(shard[1:])
        driver_slot = ancestor_count
        driver_source = source_count + driver_slot
        units = [
            literal if source == driver_source else -literal
            for source, literal in enumerate(output_uses)
        ]
        encoder.cnf.extend([[literal] for literal in units])

        ancestor_user_clause_lengths = []
        for slot in range(ancestor_count):
            source = source_count + slot
            users = []
            for later in range(slot + 1, driver_slot + 1):
                users.extend(
                    (
                        state["left_uses"][later][source],
                        state["right_uses"][later][source],
                    )
                )
            encoder.clause(users)
            ancestor_user_clause_lengths.append(len(users))

        description = {
            "shard": shard,
            "driver_class": "component",
            "ancestor_count": ancestor_count,
            "ancestor_slots": list(range(ancestor_count)),
            "driver_slot": driver_slot,
            "driver_source": driver_source,
            "ancestor_user_clause_lengths": ancestor_user_clause_lengths,
            "normal_form": (
                "all component ancestors first; the singleton C5 driver next; "
                "all non-ancestor components last"
            ),
        }
    else:
        raise ValueError(f"unknown shard {shard!r}; expected one of {ALL_SHARDS}")

    description["constraint_sha256"] = canonical_sha256(description)
    return description


def solve_shard(shard: str, solver_name: str, timeout: float) -> dict[str, object]:
    started = time.perf_counter()
    internal, encoder, state = exact.build(base_args())
    constraint = add_shard_constraints(encoder, state, shard)
    build_seconds = time.perf_counter() - started

    answer = None
    model = None
    solve_started = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=encoder.cnf) as solver:
        timer = threading.Timer(timeout, solver.interrupt) if timeout > 0 else None
        if timer is not None:
            timer.start()
        try:
            answer = solver.solve_limited(expect_interrupt=True)
        finally:
            if timer is not None:
                timer.cancel()
        if answer is True:
            model = solver.get_model()

    result: dict[str, object] = {
        **constraint,
        "status": "sat" if answer is True else "unsat" if answer is False else "unknown",
        "variables": encoder.pool.top,
        "clauses": len(encoder.cnf.clauses),
        "build_seconds": build_seconds,
        "solve_seconds": time.perf_counter() - solve_started,
        "elapsed_seconds": time.perf_counter() - started,
    }
    if model is not None:
        decoded = exact.core.decode(internal, state, model)
        result["certificate"] = decoded
        result["verification"] = exact.core.verify(decoded, state)
    return result


def shard_sort_key(shard: str) -> tuple[int, int]:
    return (0, -1) if shard == SOURCE_SHARD else (1, int(shard[1:]))


def make_payload(
    requested: tuple[str, ...],
    solver_name: str,
    timeout: float,
    results: list[dict[str, object]],
) -> dict[str, object]:
    by_shard = {str(item["shard"]): item for item in results}
    terminal = sorted(
        (
            shard
            for shard, item in by_shard.items()
            if item["status"] in {"sat", "unsat"}
        ),
        key=shard_sort_key,
    )
    unknown = sorted(
        (
            shard
            for shard, item in by_shard.items()
            if item["status"] == "unknown"
        ),
        key=shard_sort_key,
    )
    missing = sorted(set(ALL_SHARDS) - set(by_shard), key=shard_sort_key)
    sat = sorted(
        (
            shard
            for shard, item in by_shard.items()
            if item["status"] == "sat"
        ),
        key=shard_sort_key,
    )
    all_unsat = (
        not missing
        and not unknown
        and not sat
        and all(by_shard[shard]["status"] == "unsat" for shard in ALL_SHARDS)
    )
    return {
        "schema": "tc-byte-adder-bit34-c5-single-driver-cone-shards-v1",
        "scope": {
            "profile": "d7_80",
            "gate_bound": 13,
            "components": 11,
            "exact_switches": 2,
            "exact_xors": 0,
            "output_deadlines": [5, 7, 4],
            "physical_nets": True,
            "restriction": "C5 has exactly one selected output driver",
        },
        "coverage_argument": (
            "A singleton C5 driver is either a paid source/free constant or one "
            "component.  For a component driver, topologically order all of its "
            "component ancestors first, the driver next, and every non-ancestor "
            "afterward.  Its ancestor count is exactly one k in 0..10."
        ),
        "shard_domain": list(ALL_SHARDS),
        "requested_shards": list(requested),
        "solver": solver_name,
        "timeout_seconds_per_shard": timeout,
        "pysat_version": pysat.__version__,
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "exact_search_path": str(EXACT_PATH),
        "exact_search_sha256": file_sha256(EXACT_PATH),
        "results": sorted(results, key=lambda item: shard_sort_key(str(item["shard"]))),
        "terminal_shards": terminal,
        "unknown_shards": unknown,
        "missing_shards": missing,
        "sat_shards": sat,
        "coverage_complete": not missing and not unknown,
        "all_unsat": all_unsat,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--shard",
        action="append",
        choices=ALL_SHARDS,
        help="repeatable shard; default is the complete domain",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    requested = tuple(
        sorted(set(args.shard if args.shard is not None else ALL_SHARDS), key=shard_sort_key)
    )
    if args.timeout < 0:
        parser.error("--timeout must be non-negative")

    results = []
    for shard in requested:
        result = solve_shard(shard, args.solver, args.timeout)
        results.append(result)
        payload = make_payload(requested, args.solver, args.timeout, results)
        atomic_write(args.output, payload)
        print(
            json.dumps(
                {
                    "shard": shard,
                    "status": result["status"],
                    "solve_seconds": result["solve_seconds"],
                    "output": str(args.output),
                },
                separators=(",", ":"),
            ),
            flush=True,
        )
        if result["status"] == "sat":
            break

    payload = make_payload(requested, args.solver, args.timeout, results)
    atomic_write(args.output, payload)
    print(
        json.dumps(
            {
                "coverage_complete": payload["coverage_complete"],
                "all_unsat": payload["all_unsat"],
                "sat_shards": payload["sat_shards"],
                "unknown_shards": payload["unknown_shards"],
                "missing_shards": payload["missing_shards"],
                "output_sha256": file_sha256(args.output),
            },
            separators=(",", ":"),
        )
    )
    return 0 if payload["coverage_complete"] or payload["sat_shards"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
