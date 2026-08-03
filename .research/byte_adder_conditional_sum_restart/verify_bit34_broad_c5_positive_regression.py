"""Fixed-witness positive regression for the broad C5 normal form."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

from pysat.solvers import Solver

import bit34_broad_c5_normal_form as normal_form
import exact_bit34_broad_c5_normal_form_shard as broad


HERE = Path(__file__).resolve().parent
SHARD = "multi_d2_k3"
GATE_BOUND = 14
COMPONENTS = 12


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: object) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    internal, encoder, state = broad.exact.build(
        broad.base_args(COMPONENTS, GATE_BOUND)
    )
    constraint = broad.add_shard_constraints(
        encoder,
        state,
        SHARD,
        COMPONENTS,
        GATE_BOUND,
    )
    source_count = int(state["source_count"])
    source = {name: index for index, name in enumerate(state["names"])}
    node = lambda slot: source_count + slot

    # Canonical D7 14-gate residual.  Slots 0..2 are exactly the ancestors of
    # the two independent C5 Switch drivers in slots 3 and 4.
    witness = (
        ("OR", (source["G3"],), (source["G4"],), 2),
        ("NOR", (source["Q3"],), (source["Q4"],), 2),
        ("OR", (source["G4"],), (node(1),), 3),
        ("SWITCH", (node(0),), (node(2),), 4),
        ("SWITCH", (source["C3"],), (node(2),), 4),
        ("AND", (source["C3"],), (source["P3"],), 4),
        ("OR", (source["G3"],), (node(5),), 5),
        ("NOR", (source["C3"],), (source["P3"],), 4),
        ("NOR", (node(5),), (node(7),), 5),
        ("AND", (source["P4"],), (node(6),), 6),
        ("NOR", (source["P4"],), (node(6),), 6),
        ("NOR", (node(9),), (node(10),), 7),
    )
    for slot, (kind, left, right, arrival) in enumerate(witness):
        broad.exact.force_one_hot(
            encoder,
            state["kinds"][slot],
            broad.exact.core.G.KINDS.index(kind),
        )
        for index, literal in enumerate(state["left_uses"][slot]):
            encoder.force(literal, index in left)
        for index, literal in enumerate(state["right_uses"][slot]):
            encoder.force(literal, index in right)
        broad.exact.force_one_hot(
            encoder,
            state["levels"][slot],
            arrival - 1,
        )

    output_buses = ((node(8),), (node(11),), (node(3), node(4)))
    for uses, selected in zip(state["output_uses"], output_buses, strict=True):
        for index, literal in enumerate(uses):
            encoder.force(literal, index in selected)

    started = time.perf_counter()
    model = None
    with Solver(name=args.solver, bootstrap_with=encoder.cnf) as solver:
        if solver.solve():
            model = solver.get_model()

    payload: dict[str, object] = {
        "schema": "tc-byte-adder-bit34-broad-c5-positive-regression-v1",
        "status": "sat" if model is not None else "unsat",
        "profile": "d7_80",
        "gate_bound": GATE_BOUND,
        "max_delay": 7,
        "components": COMPONENTS,
        "exact_switches": None,
        "exact_xors": None,
        "forced_slot_kinds": {},
        "output_deadlines": [5, 7, 4],
        "assignments": len(state["source_values"][0]),
        "shard": SHARD,
        "shard_domain": list(normal_form.shard_domain(COMPONENTS, GATE_BOUND)),
        "constraint": constraint,
        "constraint_sha256": constraint["constraint_sha256"],
        "solver": args.solver,
        "variables": encoder.pool.top,
        "clauses": len(encoder.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "accounting": broad.accounting(GATE_BOUND),
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "broad_search_sha256": file_sha256(Path(broad.__file__).resolve()),
        "normal_form_sha256": file_sha256(Path(normal_form.__file__).resolve()),
        "exact_search_sha256": file_sha256(broad.EXACT_PATH),
    }
    if model is not None:
        certificate = broad.exact.core.decode(internal, state, model)
        verification = broad.exact.core.verify(certificate, state)
        payload.update(certificate)
        payload["verification"] = verification
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

    expected_verification = {
        "mismatch_count": 0,
        "bus_conflict_count": 0,
        "undriven_output_count": 0,
        "physical_net_partition_violation_count": 0,
    }
    checks = {
        "sat": payload["status"] == "sat",
        "actual_gate_14": payload.get("actual_gate") == 14,
        "boundary_rows_48": payload["assignments"] == 48,
        "actual_switches_2": payload.get("actual_switches") == 2,
        "actual_xors_0": payload.get("actual_xors") == 0,
        "strict_replay_clean": payload.get("verification") == expected_verification,
        "constraint_digest_matches": constraint["constraint_sha256"]
        == normal_form.constraint_sha256(SHARD, COMPONENTS, GATE_BOUND),
    }
    payload["checks"] = checks
    payload["passed"] = all(checks.values())
    output_sha256 = atomic_json(args.output, payload)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "passed": payload["passed"],
                "actual_gate": payload.get("actual_gate"),
                "verification": payload.get("verification"),
                "output_sha256": output_sha256,
            },
            separators=(",", ":"),
        )
    )
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
