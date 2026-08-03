"""One exact broad-g13 shard in the exhaustive C5 normal form.

Unlike the fixed ``n11/s2/x0`` searches, Switch and XOR counts are left
unconstrained and only the weighted gate bound is fixed.  For one component
count, C5 is partitioned into a direct-source shard, singleton-component
driver shards, and multi-Switch driver shards.  Component ancestors are
topologically normalized before the selected C5 driver or driver group.

This script is offline only.  It does not access the game, save, or shared
Byte Adder candidate.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import platform
import sys
import threading
import time
from types import SimpleNamespace

import pysat
from pysat.solvers import Solver

import bit34_broad_c5_normal_form as normal_form


HERE = Path(__file__).resolve().parent
EXACT_PATH = HERE / "exact_bit34_joint_sat.py"


def load_exact():
    spec = importlib.util.spec_from_file_location("bit34_broad_c5_exact", EXACT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load exact search: {EXACT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


exact = load_exact()


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def dependency_hashes() -> list[dict[str, str]]:
    paths = (
        Path(normal_form.__file__).resolve(),
        EXACT_PATH,
        Path(exact.CORE_PATH),
        Path(exact.core.EXACT_PATH),
        Path(exact.core.exact.GENERIC_PATH),
    )
    return [
        {"path": str(path.resolve()), "sha256": file_sha256(path)} for path in paths
    ]


def maximum_switches(components: int, gate_bound: int) -> int:
    return normal_form.maximum_switches(components, gate_bound)


def shard_domain(components: int, gate_bound: int) -> tuple[str, ...]:
    return normal_form.shard_domain(components, gate_bound)


def parse_shard(shard: str, components: int, gate_bound: int) -> dict[str, int | str]:
    return normal_form.parse_shard(shard, components, gate_bound)


def constraint_identity(
    shard: str,
    components: int,
    gate_bound: int,
) -> dict[str, object]:
    return normal_form.constraint_identity(shard, components, gate_bound)


def base_args(components: int, gate_bound: int) -> SimpleNamespace:
    return SimpleNamespace(
        profile="d7_80",
        gate_bound=gate_bound,
        max_delay=7,
        components=components,
        switches=None,
        xors=None,
        output_deadlines="5,7,4",
        slot_kind=[],
        seed_current=False,
    )


def add_ancestor_closure(
    encoder,
    state: dict[str, object],
    ancestor_count: int,
    terminal_end: int,
) -> list[int]:
    """Require every prefix component to reach a normalized terminal group."""

    source_count = int(state["source_count"])
    clause_lengths = []
    for slot in range(ancestor_count):
        source = source_count + slot
        users = []
        for later in range(slot + 1, terminal_end):
            users.extend(
                (
                    state["left_uses"][later][source],
                    state["right_uses"][later][source],
                )
            )
        encoder.clause(users)
        if not users:
            raise AssertionError("ancestor closure produced an empty user clause")
        clause_lengths.append(len(users))
    return clause_lengths


def add_shard_constraints(
    encoder,
    state: dict[str, object],
    shard: str,
    components: int,
    gate_bound: int,
) -> dict[str, object]:
    parsed = parse_shard(shard, components, gate_bound)
    identity = constraint_identity(shard, components, gate_bound)
    output_uses = state["output_uses"][2]
    source_count = int(state["source_count"])
    driver_class = parsed["driver_class"]

    if driver_class == "source":
        encoder.cnf.extend(
            [[-output_uses[source_count + slot]] for slot in range(components)]
        )
        encoding_evidence: dict[str, object] = {
            "forbidden_component_output_sources": list(
                range(source_count, source_count + components)
            ),
        }
    elif driver_class == "single_component":
        ancestor_count = int(parsed["ancestor_count"])
        driver_slot = ancestor_count
        driver_source = source_count + driver_slot
        encoder.cnf.extend(
            [
                [literal if source == driver_source else -literal]
                for source, literal in enumerate(output_uses)
            ]
        )
        clause_lengths = add_ancestor_closure(
            encoder,
            state,
            ancestor_count,
            driver_slot + 1,
        )
        encoding_evidence = {
            "driver_slot": driver_slot,
            "driver_source": driver_source,
            "ancestor_user_clause_lengths": clause_lengths,
        }
    else:
        ancestor_count = int(parsed["ancestor_count"])
        driver_count = int(parsed["driver_count"])
        driver_slots = tuple(
            range(ancestor_count, ancestor_count + driver_count)
        )
        driver_sources = tuple(source_count + slot for slot in driver_slots)
        driver_source_set = set(driver_sources)
        switch_kind = exact.core.G.SWITCH
        encoder.cnf.extend(
            [[state["kinds"][slot][switch_kind]] for slot in driver_slots]
        )
        encoder.cnf.extend(
            [
                [literal if source in driver_source_set else -literal]
                for source, literal in enumerate(output_uses)
            ]
        )
        clause_lengths = add_ancestor_closure(
            encoder,
            state,
            ancestor_count,
            ancestor_count + driver_count,
        )
        encoding_evidence = {
            "driver_slots": list(driver_slots),
            "driver_sources": list(driver_sources),
            "ancestor_user_clause_lengths": clause_lengths,
        }

    return {
        "identity": identity,
        "constraint_sha256": normal_form.canonical_sha256(identity),
        "encoding_evidence": encoding_evidence,
    }


def accounting(gate_bound: int) -> dict[str, int]:
    return {
        "current_complete_gate": 80,
        "current_complete_delay": 7,
        "current_region_gate_with_paid_leaves": 20,
        "paid_leaf_gate": 6,
        "current_residual_gate": 14,
        "current_residual_components": 12,
        "fixed_shell_with_paid_leaves": 66,
        "projected_complete_gate_at_bound": 66 + gate_bound,
        "projected_complete_delay": 7,
        "target_complete_gate": 73,
        "gate_gap_at_bound_to_target": 66 + gate_bound - 73,
    }


def solve(args: argparse.Namespace) -> dict[str, object]:
    started = time.perf_counter()
    internal, encoder, state = exact.build(
        base_args(args.components, args.gate_bound)
    )
    constraint = add_shard_constraints(
        encoder,
        state,
        args.shard,
        args.components,
        args.gate_bound,
    )
    build_seconds = time.perf_counter() - started

    model = None
    answer = None
    solve_started = time.perf_counter()
    with Solver(name=args.solver, bootstrap_with=encoder.cnf) as solver:
        timer = (
            threading.Timer(args.timeout, solver.interrupt)
            if args.timeout > 0
            else None
        )
        if timer is not None:
            timer.start()
        try:
            answer = solver.solve_limited(expect_interrupt=True)
        finally:
            if timer is not None:
                timer.cancel()
        if answer is True:
            model = solver.get_model()

    payload: dict[str, object] = {
        "schema": "tc-byte-adder-bit34-broad-c5-normal-form-shard-v1",
        "status": "sat" if answer is True else "unsat" if answer is False else "unknown",
        "profile": "d7_80",
        "gate_bound": args.gate_bound,
        "max_delay": 7,
        "components": args.components,
        "shard": args.shard,
        "exact_switches": None,
        "exact_xors": None,
        "forced_slot_kinds": {},
        "output_deadlines": [5, 7, 4],
        "assignments": len(state["source_values"][0]),
        "scope": {
            "profile": "d7_80",
            "gate_bound": args.gate_bound,
            "components": args.components,
            "switches": None,
            "xors": None,
            "maximum_switches_by_weight": maximum_switches(
                args.components, args.gate_bound
            ),
            "output_deadlines": [5, 7, 4],
            "physical_nets": True,
            "boundary_rows": len(state["source_values"][0]),
        },
        "shard_domain": list(shard_domain(args.components, args.gate_bound)),
        "constraint": constraint,
        "constraint_sha256": constraint["constraint_sha256"],
        "solver": args.solver,
        "timeout_seconds": args.timeout,
        "variables": encoder.pool.top,
        "clauses": len(encoder.cnf.clauses),
        "build_seconds": build_seconds,
        "solve_seconds": time.perf_counter() - solve_started,
        "elapsed_seconds": time.perf_counter() - started,
        "runtime": {
            "python": platform.python_version(),
            "pysat": pysat.__version__,
        },
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "dependencies": dependency_hashes(),
        "accounting": accounting(args.gate_bound),
        "coverage_argument": (
            "C5 is non-empty. A paid-source or constant driver excludes every "
            "other driver; a singleton component has one ancestor count. A "
            "multi-driver C5 bus contains only Switch outputs. For d selected "
            "Switch drivers, physical-net partition makes them mutually "
            "independent, so all component ancestors can be ordered first, the "
            "d drivers next, and every non-ancestor last. The weighted bound "
            "implies d <= min(components, gate_bound-components)."
        ),
    }
    if model is not None:
        certificate = exact.core.decode(internal, state, model)
        payload.update(certificate)
        payload["verification"] = exact.core.verify(certificate, state)
        payload["actual_switches"] = sum(
            item["kind"] == "SWITCH" for item in certificate["network"]
        )
        payload["actual_xors"] = sum(
            item["kind"] == "XOR" for item in certificate["network"]
        )
        payload["accounting"]["projected_complete_gate_actual"] = (
            66 + int(certificate["actual_gate"])
        )
        payload["accounting"]["gate_gap_actual_to_target"] = (
            int(payload["accounting"]["projected_complete_gate_actual"]) - 73
        )
        bad = (
            "mismatch_count",
            "bus_conflict_count",
            "undriven_output_count",
            "physical_net_partition_violation_count",
        )
        if any(payload["verification"][key] for key in bad):
            raise RuntimeError(
                f"decoded witness failed strict replay: {payload['verification']}"
            )
        if int(certificate["actual_gate"]) > args.gate_bound:
            raise RuntimeError("decoded witness exceeds the weighted gate bound")
    elif payload["status"] == "unknown":
        payload["reason_unknown"] = (
            "solver interrupt at the internal timeout"
            if args.timeout > 0
            else "solver returned no terminal answer"
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-bound", type=int, default=13)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--shard", required=True)
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.components < 0 or args.components > args.gate_bound:
        parser.error("require 0 <= components <= gate bound")
    if args.timeout < 0:
        parser.error("--timeout must be non-negative")
    try:
        parse_shard(args.shard, args.components, args.gate_bound)
    except ValueError as exc:
        parser.error(str(exc))

    payload = solve(args)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(args.output)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "components": args.components,
                "shard": args.shard,
                "solve_seconds": payload["solve_seconds"],
                "output": str(args.output),
                "output_sha256": sha256(encoded).hexdigest(),
            },
            separators=(",", ":"),
        )
    )
    return 0 if payload["status"] in {"sat", "unsat"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
