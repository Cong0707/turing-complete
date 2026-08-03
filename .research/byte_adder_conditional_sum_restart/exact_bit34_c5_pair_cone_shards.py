"""Exact structural shards for a two-Switch C5 output net.

This is a restricted companion to ``exact_bit34_joint_sat.py``.  It keeps the
strict-C3 D7 ``g13/n11/s2/x0`` CNF unchanged, then partitions every topology
whose two Switch outputs are exactly the physical C5 net by the number of
ordinary gates in the Switch-input ancestor cone.

The script is offline only.  It does not start Turing Complete or access the
official save or shared Byte Adder candidate.
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
ALL_CONE_SIZES = tuple(range(10))


def load_exact():
    spec = importlib.util.spec_from_file_location("bit34_c5_pair_exact", EXACT_PATH)
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


def add_cone_constraints(encoder, state: dict[str, object], cone_size: int) -> dict[str, object]:
    """Canonicalize one exact C5-pair topology family.

    Slots ``0..k-1`` are the ordinary ancestors of the two Switches in slots
    ``k,k+1``.  Requiring each prefix output to have a user within that prefix
    or the two Switches makes every prefix gate transitively reach a Switch.
    The base exact-two-Switch constraint makes every other slot ordinary.
    """

    if cone_size not in ALL_CONE_SIZES:
        raise ValueError(f"cone size must be in {ALL_CONE_SIZES}")

    switch_kind = exact.core.G.SWITCH
    source_count = int(state["source_count"])
    switch_slots = (cone_size, cone_size + 1)
    switch_sources = tuple(source_count + slot for slot in switch_slots)

    units = [state["kinds"][slot][switch_kind] for slot in switch_slots]
    output_uses = state["output_uses"][2]
    switch_source_set = set(switch_sources)
    units.extend(
        literal if source in switch_source_set else -literal
        for source, literal in enumerate(output_uses)
    )
    encoder.cnf.extend([[literal] for literal in units])

    cone_user_clauses = []
    for slot in range(cone_size):
        source = source_count + slot
        users = []
        for later in range(slot + 1, cone_size + 2):
            users.extend(
                (
                    state["left_uses"][later][source],
                    state["right_uses"][later][source],
                )
            )
        encoder.clause(users)
        cone_user_clauses.append(len(users))

    description = {
        "cone_size": cone_size,
        "ordinary_ancestor_slots": list(range(cone_size)),
        "switch_slots": list(switch_slots),
        "c5_output_sources": list(switch_sources),
        "prefix_user_clause_lengths": cone_user_clauses,
        "normal_form": (
            "all ordinary Switch ancestors first; the two independent C5-net "
            "Switches next; all remaining ordinary gates last"
        ),
    }
    description["constraint_sha256"] = canonical_sha256(description)
    return description


def solve_shard(cone_size: int, solver_name: str, timeout: float) -> dict[str, object]:
    started = time.perf_counter()
    internal, encoder, state = exact.build(base_args())
    constraint = add_cone_constraints(encoder, state, cone_size)
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


def make_payload(
    requested: tuple[int, ...],
    solver_name: str,
    timeout: float,
    results: list[dict[str, object]],
) -> dict[str, object]:
    by_size = {int(item["cone_size"]): item for item in results}
    terminal = sorted(
        size
        for size, item in by_size.items()
        if item["status"] in {"sat", "unsat"}
    )
    unknown = sorted(
        size for size, item in by_size.items() if item["status"] == "unknown"
    )
    missing = sorted(set(ALL_CONE_SIZES) - set(by_size))
    sat = sorted(size for size, item in by_size.items() if item["status"] == "sat")
    all_unsat = (
        not missing
        and not unknown
        and not sat
        and all(by_size[size]["status"] == "unsat" for size in ALL_CONE_SIZES)
    )
    return {
        "schema": "tc-byte-adder-bit34-c5-pair-cone-shards-v1",
        "scope": {
            "profile": "d7_80",
            "gate_bound": 13,
            "components": 11,
            "exact_switches": 2,
            "exact_xors": 0,
            "output_deadlines": [5, 7, 4],
            "physical_nets": True,
            "restriction": "the two Switch outputs are exactly the C5 physical net",
        },
        "coverage_argument": (
            "The C5 physical-net partition forbids either selected Switch output "
            "from feeding the other through a different bus.  For any covered "
            "DAG, topologically order all ordinary ancestors of the two Switches "
            "first, then the two Switches, then every remaining ordinary gate.  "
            "The ancestor count is exactly one k in 0..9."
        ),
        "cone_size_domain": list(ALL_CONE_SIZES),
        "requested_cone_sizes": list(requested),
        "solver": solver_name,
        "timeout_seconds_per_shard": timeout,
        "pysat_version": pysat.__version__,
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "exact_search_path": str(EXACT_PATH),
        "exact_search_sha256": file_sha256(EXACT_PATH),
        "results": sorted(results, key=lambda item: int(item["cone_size"])),
        "terminal_cone_sizes": terminal,
        "unknown_cone_sizes": unknown,
        "missing_cone_sizes": missing,
        "sat_cone_sizes": sat,
        "coverage_complete": not missing and not unknown,
        "all_unsat": all_unsat,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--cone-size",
        type=int,
        action="append",
        dest="cone_sizes",
        help="repeatable k in 0..9; default is the complete domain",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    requested = tuple(
        sorted(set(args.cone_sizes if args.cone_sizes is not None else ALL_CONE_SIZES))
    )
    if not requested or any(size not in ALL_CONE_SIZES for size in requested):
        parser.error(f"--cone-size values must be in {ALL_CONE_SIZES}")
    if args.timeout < 0:
        parser.error("--timeout must be non-negative")

    results = []
    for cone_size in requested:
        result = solve_shard(cone_size, args.solver, args.timeout)
        results.append(result)
        payload = make_payload(requested, args.solver, args.timeout, results)
        atomic_write(args.output, payload)
        print(
            json.dumps(
                {
                    "cone_size": cone_size,
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
                "sat_cone_sizes": payload["sat_cone_sizes"],
                "unknown_cone_sizes": payload["unknown_cone_sizes"],
                "missing_cone_sizes": payload["missing_cone_sizes"],
                "output_sha256": file_sha256(args.output),
            },
            separators=(",", ":"),
        )
    )
    return 0 if payload["coverage_complete"] or payload["sat_cone_sizes"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
