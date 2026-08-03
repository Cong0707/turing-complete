"""Positive regression for the normalized C5-pair cone constraints."""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
EXACT_PATH = HERE / "exact_bit34_joint_sat.py"
CONE_PATH = HERE / "exact_bit34_c5_pair_cone_shards.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    exact = load_module("bit34_c5_pair_positive_exact", EXACT_PATH)
    cone = load_module("bit34_c5_pair_positive_cone", CONE_PATH)
    build_args = SimpleNamespace(
        profile="d7_80",
        gate_bound=14,
        max_delay=7,
        components=12,
        switches=2,
        xors=0,
        output_deadlines="5,7,4",
        slot_kind=[],
        seed_current=False,
    )
    internal, encoder, state = exact.build(build_args)
    cone_description = cone.add_cone_constraints(encoder, state, 3)
    source_count = int(state["source_count"])
    source = {name: index for index, name in enumerate(state["names"])}
    node = lambda slot: source_count + slot

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
        exact.force_one_hot(
            encoder,
            state["kinds"][slot],
            exact.core.G.KINDS.index(kind),
        )
        for index, literal in enumerate(state["left_uses"][slot]):
            encoder.force(literal, index in left)
        for index, literal in enumerate(state["right_uses"][slot]):
            encoder.force(literal, index in right)
        exact.force_one_hot(encoder, state["levels"][slot], arrival - 1)

    output_buses = ((node(8),), (node(11),), (node(3), node(4)))
    for uses, selected in zip(state["output_uses"], output_buses, strict=True):
        for index, literal in enumerate(uses):
            encoder.force(literal, index in selected)

    started = time.perf_counter()
    model = None
    with Solver(name=args.solver, bootstrap_with=encoder.cnf) as solver:
        answer = solver.solve()
        if answer:
            model = solver.get_model()
    payload: dict[str, object] = {
        "schema": "tc-byte-adder-bit34-c5-pair-cone-positive-regression-v1",
        "status": "sat" if model is not None else "unsat",
        "profile": "d7_80",
        "gate_bound": 14,
        "components": 12,
        "exact_switches": 2,
        "exact_xors": 0,
        "boundary_rows": len(state["source_values"][0]),
        "output_deadlines": list(state["output_deadlines"]),
        "cone_size": 3,
        "cone_constraint_sha256": cone_description["constraint_sha256"],
        "solver": args.solver,
        "variables": encoder.pool.top,
        "clauses": len(encoder.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "exact_search_sha256": file_sha256(EXACT_PATH),
        "cone_search_sha256": file_sha256(CONE_PATH),
        "script_sha256": file_sha256(Path(__file__).resolve()),
    }
    if model is not None:
        certificate = exact.core.decode(internal, state, model)
        payload["certificate"] = certificate
        payload["verification"] = exact.core.verify(certificate, state)

    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "verification": payload.get("verification"),
                "output_sha256": sha256(encoded).hexdigest(),
            },
            separators=(",", ":"),
        )
    )
    return 0 if model is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
