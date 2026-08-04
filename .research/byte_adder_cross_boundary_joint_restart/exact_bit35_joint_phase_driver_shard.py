"""Refine one C5 normal-form shard by exact T5 and S5 driver counts."""

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

import pysat
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

import bit35_joint_c5_normal_form as c5_normal
import bit35_joint_phase_driver_classes as phase_normal


HERE = Path(__file__).resolve().parent
C5_WORKER_PATH = HERE / "exact_bit35_joint_c5_normal_form_shard.py"


def load_c5_worker():
    spec = importlib.util.spec_from_file_location(
        "bit35_joint_phase_c5_worker",
        C5_WORKER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {C5_WORKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


c5_worker = load_c5_worker()
exact = c5_worker.exact


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def dependency_hashes() -> list[dict[str, str]]:
    paths = (
        Path(c5_normal.__file__).resolve(),
        Path(phase_normal.__file__).resolve(),
        C5_WORKER_PATH,
        c5_worker.EXACT_PATH,
        Path(exact.CORE_PATH),
        Path(exact.core.EXACT_PATH),
        Path(exact.core.exact.GENERIC_PATH),
    )
    return [
        {"path": str(path.resolve()), "sha256": file_sha256(path)} for path in paths
    ]


def add_exact_component_driver_count(
    encoder,
    state: dict[str, object],
    output_index: int,
    driver_count: int,
) -> dict[str, object]:
    source_count = int(state["source_count"])
    output_uses = state["output_uses"][output_index]
    component_uses = output_uses[source_count:]
    for literal in output_uses[:source_count]:
        encoder.clause((-literal,))
    encoder.cnf.extend(
        CardEnc.equals(
            lits=component_uses,
            bound=driver_count,
            vpool=encoder.pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    if driver_count > 1:
        switch_kind = exact.core.G.SWITCH
        for slot, literal in enumerate(component_uses):
            encoder.clause((-literal, state["kinds"][slot][switch_kind]))
    return {
        "output_index": output_index,
        "forbidden_paid_source_selectors": source_count,
        "component_selector_count": len(component_uses),
        "exact_driver_count": driver_count,
        "required_kind_if_selected": "SWITCH" if driver_count > 1 else "any",
    }


def solve(args: argparse.Namespace) -> dict[str, object]:
    started = time.perf_counter()
    internal, encoder, state = exact.build(
        c5_worker.base_args(args.components, args.gate_bound)
    )
    c5_constraint = c5_worker.add_shard_constraints(
        encoder,
        state,
        args.c5_shard,
        args.components,
        args.gate_bound,
    )
    phase_identity = phase_normal.constraint_identity(
        args.components,
        args.gate_bound,
        args.t5_drivers,
        args.s5_drivers,
    )
    phase_evidence = {
        "T5": add_exact_component_driver_count(
            encoder,
            state,
            3,
            args.t5_drivers,
        ),
        "S5": add_exact_component_driver_count(
            encoder,
            state,
            4,
            args.s5_drivers,
        ),
    }
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
        "schema": "tc-byte-adder-bit35-joint-phase-driver-shard-v1",
        "status": "sat" if answer is True else "unsat" if answer is False else "unknown",
        "profile": c5_normal.PROFILE,
        "gate_bound": args.gate_bound,
        "max_delay": 7,
        "components": args.components,
        "c5_shard": args.c5_shard,
        "t5_drivers": args.t5_drivers,
        "s5_drivers": args.s5_drivers,
        "target_names": list(exact.TARGET_NAMES),
        "output_deadlines": list(exact.OUTPUT_DEADLINES),
        "assignments": len(state["source_values"][0]),
        "truth_domain_sha256": state["truth_domain_sha256"],
        "c5_constraint": c5_constraint,
        "c5_constraint_sha256": c5_constraint["constraint_sha256"],
        "phase_constraint": {
            "identity": phase_identity,
            "constraint_sha256": phase_normal.canonical_sha256(phase_identity),
            "encoding_evidence": phase_evidence,
        },
        "phase_constraint_sha256": phase_normal.canonical_sha256(phase_identity),
        "phase_pair_domain": [
            {"t5_drivers": t5, "s5_drivers": s5}
            for t5, s5 in phase_normal.pair_domain(args.components, args.gate_bound)
        ],
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
        "accounting": c5_worker.accounting(args.gate_bound),
        "coverage_argument": (
            "On all 96 correlated rows neither T5 nor S5 equals a paid source or "
            "constant. Each therefore selects component outputs only. A singleton "
            "has driver count one; every multi-driver physical bus contains only "
            "Switch outputs. Enumerating the canonical count-pair domain refines, "
            "without weakening, the complete C5 normal-form shard."
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
            exact.FIXED_SHELL_WITH_PAID_SOURCES + int(certificate["actual_gate"])
        )
        payload["accounting"]["projected_complete_energy_actual"] = (
            int(payload["accounting"]["projected_complete_gate_actual"])
            * exact.CURRENT_COMPLETE_DELAY
        )
        actual_driver_counts = {
            "T5": len(certificate["output_buses"][3]),
            "S5": len(certificate["output_buses"][4]),
        }
        payload["actual_phase_driver_counts"] = actual_driver_counts
        if actual_driver_counts != {
            "T5": args.t5_drivers,
            "S5": args.s5_drivers,
        }:
            raise RuntimeError(f"decoded phase driver count mismatch: {actual_driver_counts}")
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
            raise RuntimeError("decoded witness exceeds weighted gate bound")
    elif payload["status"] == "unknown":
        payload["reason_unknown"] = "solver interrupt at the internal timeout"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-bound", type=int, default=16)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--c5-shard", required=True)
    parser.add_argument("--t5-drivers", type=int, required=True)
    parser.add_argument("--s5-drivers", type=int, required=True)
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        c5_normal.parse_shard(args.c5_shard, args.components, args.gate_bound)
        phase_normal.constraint_identity(
            args.components,
            args.gate_bound,
            args.t5_drivers,
            args.s5_drivers,
        )
    except ValueError as exc:
        parser.error(str(exc))
    if args.timeout < 0:
        parser.error("--timeout must be non-negative")

    payload = solve(args)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(args.output)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "components": args.components,
                "c5_shard": args.c5_shard,
                "t5_drivers": args.t5_drivers,
                "s5_drivers": args.s5_drivers,
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
