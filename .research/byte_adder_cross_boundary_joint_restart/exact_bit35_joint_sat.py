"""Strict-Z exact synthesis for the verified 80/7 adder's bit-3:5 joint cut.

Paid sources::

    raw a3,b3,a4,b4; G/Q/P3:4; P5@2; C3@3 with exact Z0/D0/D1

Required outputs::

    S3@5, S4@7, C5@4, T5@5, S5@6

``T5=P5&C5`` is part of the cut because the fixed downstream S6 network consumes
it.  The complete correlated domain is 16 raw bit-3:4 assignments x 2 P5
values x 3 exact C3 drive states = 96 rows.  C5 alone may be Z on Boolean-zero
rows; all other outputs must be actively driven.

The generic physical encoder is imported read-only from the reviewed frozen
bit-3:4 proof dependencies.  This wrapper changes only the correlated truth
tables and the per-row driven mask of paid source C3.
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
from types import SimpleNamespace
from typing import Iterator

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORE_PATH = (
    ROOT
    / ".research"
    / "byte_adder_pair_macro_exact"
    / "exact_paid_physical_search_core.py"
)

BOUNDARY_STATES = ("Z0", "D0", "D1")
TARGET_NAMES = ("S3", "S4", "C5", "T5", "S5")
OUTPUT_DEADLINES = (5, 7, 4, 5, 6)
ALLOW_Z_FALSE_OUTPUTS = (False, False, True, False, False)
CURRENT_JOINT_GATE = 17
CURRENT_JOINT_COMPONENTS = 15
CURRENT_COMPLETE_GATE = 80
CURRENT_COMPLETE_DELAY = 7
FIXED_SHELL_WITH_PAID_SOURCES = 63


def load_core():
    spec = importlib.util.spec_from_file_location("bit35_paid_physical_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load exact core: {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = load_core()


def pointwise(function, *rows: list[bool]) -> list[bool]:
    return [
        bool(function(*(int(row[index]) for row in rows)))
        for index in range(len(rows[0]))
    ]


def pack(row: list[bool]) -> int:
    return sum(int(value) << index for index, value in enumerate(row))


def bit35_problem(_interface: str):
    """Return the complete 96-row strict-three-state bit-3:5 problem."""

    names = ["a3", "b3", "a4", "b4", "C3", "P5"]
    rows = [[] for _ in names]
    c3_driven: list[bool] = []
    boundary_state_by_case: list[str] = []
    raw_assignment_by_case: list[int] = []
    p5_by_case: list[bool] = []

    for raw in range(16):
        raw_bits = [bool((raw >> bit) & 1) for bit in range(4)]
        for p5 in (False, True):
            for state in BOUNDARY_STATES:
                c3_value = state == "D1"
                driven = state != "Z0"
                values = (*raw_bits, c3_value, p5)
                for index, value in enumerate(values):
                    rows[index].append(bool(value))
                c3_driven.append(driven)
                boundary_state_by_case.append(state)
                raw_assignment_by_case.append(raw)
                p5_by_case.append(p5)

    a3, b3, a4, b4, c3, p5 = rows
    g3 = pointwise(lambda a, b: a & b, a3, b3)
    q3 = pointwise(lambda a, b: 1 ^ (a | b), a3, b3)
    p3 = pointwise(lambda g, q: 1 ^ (g | q), g3, q3)
    g4 = pointwise(lambda a, b: a & b, a4, b4)
    q4 = pointwise(lambda a, b: 1 ^ (a | b), a4, b4)
    p4 = pointwise(lambda g, q: 1 ^ (g | q), g4, q4)
    c4 = pointwise(lambda g, p, c: g | (p & c), g3, p3, c3)
    s3 = pointwise(lambda p, c: p ^ c, p3, c3)
    s4 = pointwise(lambda p, c: p ^ c, p4, c4)
    c5 = pointwise(lambda g, p, c: g | (p & c), g4, p4, c4)
    t5 = pointwise(lambda p, c: p & c, p5, c5)
    s5 = pointwise(lambda p, c: p ^ c, p5, c5)

    names.extend(("G3", "Q3", "P3", "G4", "Q4", "P4"))
    rows.extend((g3, q3, p3, g4, q4, p4))
    arrivals = {
        "a3": 0,
        "b3": 0,
        "a4": 0,
        "b4": 0,
        "C3": 3,
        "P5": 2,
        "G3": 1,
        "Q3": 1,
        "P3": 2,
        "G4": 1,
        "Q4": 1,
        "P4": 2,
    }
    targets = (s3, s4, c5, t5, s5)
    domain_digest = sha256()
    for case in range(len(c3_driven)):
        domain_digest.update(
            bytes(
                [
                    *(int(row[case]) for row in rows),
                    int(c3_driven[case]),
                    *(int(target[case]) for target in targets),
                ]
            )
        )
    metadata = {
        "c3_source_index": names.index("C3"),
        "c3_driven": c3_driven,
        "boundary_state_by_case": boundary_state_by_case,
        "raw_assignment_by_case": raw_assignment_by_case,
        "p5_by_case": p5_by_case,
        "truth_domain_sha256": domain_digest.hexdigest(),
    }
    bit35_problem.metadata = metadata
    return names, rows, tuple(pack(target) for target in targets), arrivals


bit35_problem.metadata = {}


def case_index(name: str) -> int:
    try:
        return int(name.rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise RuntimeError(f"cannot recover truth-table row from bus name {name!r}") from exc


def parse_slot_kind_constraints(args: argparse.Namespace) -> dict[int, str]:
    result: dict[int, str] = {}
    for raw in getattr(args, "slot_kind", ()):
        try:
            slot_text, kind_text = raw.split(":", 1)
            slot = int(slot_text)
        except (AttributeError, ValueError) as exc:
            raise ValueError(f"invalid --slot-kind {raw!r}; expected SLOT:KIND") from exc
        kind = kind_text.upper()
        if not 0 <= slot < args.components:
            raise ValueError(
                f"--slot-kind slot {slot} is outside 0..{args.components - 1}"
            )
        if kind not in core.G.KINDS:
            raise ValueError(
                f"unknown gate kind {kind!r}; expected one of {tuple(core.G.KINDS)}"
            )
        if slot in result and result[slot] != kind:
            raise ValueError(
                f"conflicting --slot-kind constraints for slot {slot}: "
                f"{result[slot]} vs {kind}"
            )
        result[slot] = kind
    return dict(sorted(result.items()))


@contextmanager
def strict_c3_patch() -> Iterator[None]:
    """Install the exact per-row driven mask for paid source C3."""

    original_truth_tables = core.truth_tables
    original_bus_case = core.G.Encoder.bus_case
    original_output_bus = core.exact.output_bus

    def patched_bus_case(encoder, name, selected, driver_values, driver_drivens):
        metadata = bit35_problem.metadata
        driven = list(driver_drivens)
        driven[metadata["c3_source_index"]] = metadata["c3_driven"][case_index(name)]
        return original_bus_case(encoder, name, selected, driver_values, driven)

    def patched_output_bus(encoder, name, selected, driver_values, driver_drivens):
        metadata = bit35_problem.metadata
        driven = list(driver_drivens)
        driven[metadata["c3_source_index"]] = metadata["c3_driven"][case_index(name)]
        return original_output_bus(encoder, name, selected, driver_values, driven)

    core.truth_tables = bit35_problem
    core.G.Encoder.bus_case = patched_bus_case
    core.exact.output_bus = patched_output_bus
    try:
        yield
    finally:
        core.truth_tables = original_truth_tables
        core.G.Encoder.bus_case = original_bus_case
        core.exact.output_bus = original_output_bus


def force_one_hot(encoder, literals: list[int], selected: int) -> None:
    for index, literal in enumerate(literals):
        encoder.force(literal, index == selected)


def fix_current_joint(encoder, state: dict[str, object], args: argparse.Namespace) -> None:
    """Fix the CNF to the authoritative weighted-17 joint witness."""

    if (args.gate_bound, args.components, args.switches, args.xors) != (17, 15, 2, 0):
        raise ValueError(
            "--seed-current requires --gate-bound 17 --components 15 "
            "--switches 2 --xors 0"
        )
    source_count = int(state["source_count"])
    source = {name: index for index, name in enumerate(state["names"])}
    node = lambda slot: source_count + slot
    c5_bus = (node(5), node(6))
    witness = (
        ("AND", (source["C3"],), (source["P3"],), 4),
        ("OR", (source["G3"],), (node(0),), 5),
        ("OR", (source["G3"],), (source["G4"],), 2),
        ("NOR", (source["Q3"],), (source["Q4"],), 2),
        ("OR", (source["G4"],), (node(3),), 3),
        ("SWITCH", (node(2),), (node(4),), 4),
        ("SWITCH", (source["C3"],), (node(4),), 4),
        ("NOR", (source["C3"],), (source["P3"],), 4),
        ("NOR", (node(0),), (node(7),), 5),
        ("AND", (source["P4"],), (node(1),), 6),
        ("NOR", (source["P4"],), (node(1),), 6),
        ("NOR", (node(9),), (node(10),), 7),
        ("AND", (source["P5"],), c5_bus, 5),
        ("NOR", (source["P5"],), c5_bus, 5),
        ("NOR", (node(12),), (node(13),), 6),
    )
    output_buses = (
        (node(8),),
        (node(11),),
        c5_bus,
        (node(12),),
        (node(14),),
    )

    for slot, (kind, left, right, arrival) in enumerate(witness):
        force_one_hot(encoder, state["kinds"][slot], core.G.KINDS.index(kind))
        for index, literal in enumerate(state["left_uses"][slot]):
            encoder.force(literal, index in left)
        for index, literal in enumerate(state["right_uses"][slot]):
            encoder.force(literal, index in right)
        force_one_hot(encoder, state["levels"][slot], arrival - 1)

    for literals, selected in zip(state["output_uses"], output_buses, strict=True):
        for index, literal in enumerate(literals):
            encoder.force(literal, index in selected)


def normalize_args(args: argparse.Namespace) -> None:
    if args.max_delay is None:
        args.max_delay = CURRENT_COMPLETE_DELAY
    elif args.max_delay != CURRENT_COMPLETE_DELAY:
        raise ValueError(f"bit35 joint profile fixes --max-delay at {CURRENT_COMPLETE_DELAY}")
    if args.output_deadlines is None:
        args.output_deadlines = ",".join(str(value) for value in OUTPUT_DEADLINES)
    else:
        supplied = tuple(int(value) for value in args.output_deadlines.split(","))
        if supplied != OUTPUT_DEADLINES:
            raise ValueError(
                f"bit35 joint profile fixes output deadlines at {OUTPUT_DEADLINES}, got {supplied}"
            )


def build(args: argparse.Namespace):
    deadlines = tuple(int(value) for value in args.output_deadlines.split(","))
    if deadlines != OUTPUT_DEADLINES:
        raise ValueError(f"unexpected output deadlines: {deadlines}")

    # The generic core's bit56 policy permits Z only for target index 2.  With
    # our patched five-target table that index is C5, exactly as required.
    internal = SimpleNamespace(
        interface="bit56",
        gate_bound=args.gate_bound,
        max_delay=args.max_delay,
        components=args.components,
        switches=args.switches,
        xors=args.xors,
        h_arrival=4,
        c5_arrival=4,
        output_deadlines=args.output_deadlines,
    )
    with strict_c3_patch():
        encoder, state = core.build(internal)

    if tuple(state["allow_z_false_outputs"]) != ALLOW_Z_FALSE_OUTPUTS:
        raise RuntimeError(
            f"generic output drive policy changed: {state['allow_z_false_outputs']}"
        )
    forced_slot_kinds = parse_slot_kind_constraints(args)
    for slot, kind in forced_slot_kinds.items():
        force_one_hot(encoder, state["kinds"][slot], core.G.KINDS.index(kind))

    c3_index = bit35_problem.metadata["c3_source_index"]
    state["source_drivens"][c3_index] = list(bit35_problem.metadata["c3_driven"])
    state["target_names"] = TARGET_NAMES
    state["boundary_state_by_case"] = list(
        bit35_problem.metadata["boundary_state_by_case"]
    )
    state["raw_assignment_by_case"] = list(
        bit35_problem.metadata["raw_assignment_by_case"]
    )
    state["p5_by_case"] = list(bit35_problem.metadata["p5_by_case"])
    state["forced_slot_kinds"] = forced_slot_kinds
    state["truth_domain_sha256"] = bit35_problem.metadata["truth_domain_sha256"]
    if args.seed_current:
        fix_current_joint(encoder, state, args)
    return internal, encoder, state


def solve(args: argparse.Namespace) -> dict[str, object]:
    started = time.perf_counter()
    normalize_args(args)
    internal, encoder, state = build(args)
    model = None
    status = "unknown"
    with Solver(name=args.solver, bootstrap_with=encoder.cnf) as solver:
        timer = threading.Timer(args.timeout, solver.interrupt) if args.timeout > 0 else None
        if timer is not None:
            timer.start()
        try:
            answer = solver.solve_limited(expect_interrupt=True)
        finally:
            if timer is not None:
                timer.cancel()
        if answer is True:
            status = "sat"
            model = solver.get_model()
        elif answer is False:
            status = "unsat"

    payload: dict[str, object] = {
        "schema": "tc-byte-adder-bit35-joint-strict-z-exact-v1",
        "status": status,
        "interface": "bit35_joint",
        "target_names": list(TARGET_NAMES),
        "boundary_states": list(BOUNDARY_STATES),
        "assignments": len(state["source_values"][0]),
        "truth_domain_sha256": state["truth_domain_sha256"],
        "free_sources": list(state["names"]),
        "source_arrivals": dict(
            zip(state["names"], state["source_arrivals"], strict=True)
        ),
        "source_driven_policy": {
            "C3": "independent Z0/D0/D1; all other paid sources driven",
        },
        "gate_bound": args.gate_bound,
        "max_delay": args.max_delay,
        "components": args.components,
        "forced_slot_kinds": {
            str(slot): kind for slot, kind in state["forced_slot_kinds"].items()
        },
        "exact_switches": args.switches,
        "exact_xors": args.xors,
        "seed_current": args.seed_current,
        "output_deadlines": list(state["output_deadlines"]),
        "allow_z_false_outputs": list(state["allow_z_false_outputs"]),
        "physical_nets": True,
        "solver": args.solver,
        "variables": encoder.pool.top,
        "clauses": len(encoder.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "accounting": {
            "current_complete_gate": CURRENT_COMPLETE_GATE,
            "current_complete_delay": CURRENT_COMPLETE_DELAY,
            "current_complete_energy": CURRENT_COMPLETE_GATE * CURRENT_COMPLETE_DELAY,
            "current_joint_gate": CURRENT_JOINT_GATE,
            "current_joint_components": CURRENT_JOINT_COMPONENTS,
            "fixed_shell_with_paid_sources": FIXED_SHELL_WITH_PAID_SOURCES,
            "projected_complete_gate_at_bound": (
                FIXED_SHELL_WITH_PAID_SOURCES + args.gate_bound
            ),
            "projected_complete_delay": CURRENT_COMPLETE_DELAY,
            "projected_complete_energy_at_bound": (
                (FIXED_SHELL_WITH_PAID_SOURCES + args.gate_bound)
                * CURRENT_COMPLETE_DELAY
            ),
        },
    }
    if model is not None:
        payload.update(core.decode(internal, state, model))
        payload["accounting"]["projected_complete_gate_actual"] = (
            FIXED_SHELL_WITH_PAID_SOURCES + int(payload["actual_gate"])
        )
        payload["accounting"]["projected_complete_energy_actual"] = (
            int(payload["accounting"]["projected_complete_gate_actual"])
            * CURRENT_COMPLETE_DELAY
        )
        payload["verification"] = core.verify(payload, state)
        bad = (
            "mismatch_count",
            "bus_conflict_count",
            "undriven_output_count",
            "physical_net_partition_violation_count",
        )
        if any(payload["verification"][key] for key in bad):
            raise RuntimeError(f"decoded witness failed replay: {payload['verification']}")
    elif status == "unknown":
        payload["reason_unknown"] = "timeout"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument(
        "--slot-kind",
        action="append",
        default=[],
        metavar="SLOT:KIND",
        help="repeatable exact gate-kind constraint for a component slot",
    )
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int)
    parser.add_argument(
        "--seed-current",
        action="store_true",
        help="fix the authoritative weighted-17 joint witness for calibration",
    )
    parser.add_argument("--output-deadlines")
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = solve(args)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {key: value for key, value in payload.items() if key != "network"},
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
