"""Exact bit-3:4 joint synthesis for verified 80/7 and 95/6 adders.

This is an offline research wrapper around the reviewed paid-source physical
CNF encoder.  It searches only the replaceable bit-3:4 residual::

    paid inputs: raw a3/b3/a4/b4, G/Q/P leaves, C3@3
    D7 outputs:  S3@5 (driven), S4@7 (driven), C5@4 (Z allowed for zero)
    D6 outputs:  S3@5 (driven), S4@6 (driven), C5@4 (Z allowed for zero)

``C3`` is a resolved carry bus in the enclosing adder.  Its Boolean-zero state
can be either actively driven zero or high impedance.  The local domain
therefore contains all 16 raw-bit assignments crossed with the three exact
boundary states ``Z0/D0/D1`` (48 rows), rather than incorrectly treating C3 as
an always-driven Boolean source.

Both verified enclosing adders currently use 14 residual gates (12
components, including two Switches).  The profile-specific complete ledgers
are ``66+g`` for the 80/7 shell and ``81+g`` for the 95/6 shell.  Thus a D7
cost-13 witness would project to 79/7, while a D6 cost-12 witness would project
to 93/6, before materialization and full-chain replay.

The script never starts Turing Complete and never reads or writes the official
save or the shared Byte Adder candidate.
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
TARGET_NAMES = ("S3", "S4", "C5")
CURRENT_RESIDUAL_GATE = 14
CURRENT_RESIDUAL_COMPONENTS = 12
PROFILES = {
    "d7_80": {
        "description": "verified 80/7 hybrid phase-fold shell",
        "output_deadlines": (5, 7, 4),
        "max_delay": 7,
        "current_complete_gate": 80,
        "current_complete_delay": 7,
        "current_region_gate_with_paid_leaves": 20,
        "paid_leaf_gate": 6,
        "fixed_shell_with_paid_leaves": 66,
        "target_complete_gate": 73,
    },
    "d6_95": {
        "description": "verified 95/6 mixed Q34/A-V shell",
        "output_deadlines": (5, 6, 4),
        "max_delay": 6,
        "current_complete_gate": 95,
        "current_complete_delay": 6,
        "current_region_gate_with_paid_leaves": 20,
        "paid_leaf_gate": 6,
        "fixed_shell_with_paid_leaves": 81,
        "target_complete_gate": 85,
    },
}


def load_core():
    spec = importlib.util.spec_from_file_location("bit34_paid_physical_core", CORE_PATH)
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


def bit34_problem(_interface: str):
    """Return the 48-row strict-three-state bit-3:4 problem."""

    names = ["a3", "b3", "a4", "b4", "C3"]
    rows = [[] for _ in names]
    c3_driven: list[bool] = []
    boundary_state_by_case: list[str] = []
    for raw in range(16):
        raw_bits = [bool((raw >> bit) & 1) for bit in range(4)]
        for state in BOUNDARY_STATES:
            c3_value = state == "D1"
            driven = state != "Z0"
            for index, value in enumerate((*raw_bits, c3_value)):
                rows[index].append(bool(value))
            c3_driven.append(driven)
            boundary_state_by_case.append(state)

    a3, b3, a4, b4, c3 = rows
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

    names.extend(("G3", "Q3", "P3", "G4", "Q4", "P4"))
    rows.extend((g3, q3, p3, g4, q4, p4))
    arrivals = {
        "a3": 0,
        "b3": 0,
        "a4": 0,
        "b4": 0,
        "C3": 3,
        "G3": 1,
        "Q3": 1,
        "P3": 2,
        "G4": 1,
        "Q4": 1,
        "P4": 2,
    }
    metadata = {
        "c3_source_index": names.index("C3"),
        "c3_driven": c3_driven,
        "boundary_state_by_case": boundary_state_by_case,
    }
    bit34_problem.metadata = metadata
    return names, rows, (pack(s3), pack(s4), pack(c5)), arrivals


bit34_problem.metadata = {}


def case_index(name: str) -> int:
    try:
        return int(name.rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise RuntimeError(f"cannot recover truth-table row from bus name {name!r}") from exc


def parse_slot_kind_constraints(args: argparse.Namespace) -> dict[int, str]:
    """Parse repeatable ``SLOT:KIND`` constraints into a canonical mapping."""

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
    """Patch the generic builder at its two bus-resolution entry points.

    The upstream encoder intentionally assumes paid sources are driven.  This
    wrapper changes only source ``C3`` to the exact per-row driven mask.  The
    patch is process-local and restored even if CNF construction fails.
    """

    original_truth_tables = core.truth_tables
    original_bus_case = core.G.Encoder.bus_case
    original_output_bus = core.exact.output_bus

    def patched_bus_case(encoder, name, selected, driver_values, driver_drivens):
        metadata = bit34_problem.metadata
        driven = list(driver_drivens)
        driven[metadata["c3_source_index"]] = metadata["c3_driven"][case_index(name)]
        return original_bus_case(encoder, name, selected, driver_values, driven)

    def patched_output_bus(encoder, name, selected, driver_values, driver_drivens):
        metadata = bit34_problem.metadata
        driven = list(driver_drivens)
        driven[metadata["c3_source_index"]] = metadata["c3_driven"][case_index(name)]
        return original_output_bus(encoder, name, selected, driver_values, driven)

    core.truth_tables = bit34_problem
    core.G.Encoder.bus_case = patched_bus_case
    core.exact.output_bus = patched_output_bus
    try:
        yield
    finally:
        core.truth_tables = original_truth_tables
        core.G.Encoder.bus_case = original_bus_case
        core.exact.output_bus = original_output_bus


def build(args: argparse.Namespace):
    deadlines = tuple(int(value) for value in args.output_deadlines.split(","))
    if len(deadlines) != len(TARGET_NAMES):
        raise ValueError(f"expected three deadlines, got {deadlines}")
    if any(value > args.max_delay for value in deadlines):
        raise ValueError("output deadline exceeds --max-delay")

    # The generic core's ``bit56`` policy is exactly the required output
    # policy here: first two outputs fully driven; third output may be Z only
    # on Boolean-zero rows.  All truth tables and source semantics are replaced
    # by this wrapper before construction.
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

    forced_slot_kinds = parse_slot_kind_constraints(args)
    for slot, kind in forced_slot_kinds.items():
        force_one_hot(encoder, state["kinds"][slot], core.G.KINDS.index(kind))

    c3_index = bit34_problem.metadata["c3_source_index"]
    state["source_drivens"][c3_index] = list(bit34_problem.metadata["c3_driven"])
    state["target_names"] = TARGET_NAMES
    state["boundary_state_by_case"] = list(
        bit34_problem.metadata["boundary_state_by_case"]
    )
    state["forced_slot_kinds"] = forced_slot_kinds
    if args.seed_current:
        fix_current_residual(encoder, state, args)
    return internal, encoder, state


def force_one_hot(encoder, literals: list[int], selected: int) -> None:
    for index, literal in enumerate(literals):
        encoder.force(literal, index == selected)


def fix_current_residual(encoder, state: dict[str, object], args: argparse.Namespace) -> None:
    """Fix the CNF to the profile's known 14-gate residual for calibration."""

    if (args.gate_bound, args.components, args.switches, args.xors) != (14, 12, 2, 0):
        raise ValueError(
            "--seed-current requires --gate-bound 14 --components 12 "
            "--switches 2 --xors 0"
        )
    source_count = int(state["source_count"])
    source = {name: index for index, name in enumerate(state["names"])}
    node = lambda slot: source_count + slot
    # kind, left bus, right bus, exact arrival.  In each profile the two
    # Switch outputs form the complete C5 physical net; a consumer may reuse
    # that exact BUS, but no proper subset/superset is permitted elsewhere.
    if args.profile == "d7_80":
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
        )
        output_buses = ((node(8),), (node(11),), (node(5), node(6)))
    elif args.profile == "d6_95":
        witness = (
            ("OR", (source["G3"],), (source["G4"],), 2),
            ("NOR", (source["Q3"],), (source["Q4"],), 2),
            ("OR", (source["G4"],), (node(1),), 3),
            ("SWITCH", (node(0),), (node(2),), 4),
            ("SWITCH", (source["C3"],), (node(2),), 4),
            ("AND", (source["C3"],), (source["P3"],), 4),
            ("NOR", (source["C3"],), (source["P3"],), 4),
            ("NOR", (node(5),), (node(6),), 5),
            ("AND", (source["P4"],), (node(3), node(4)), 5),
            ("OR", (source["G3"],), (source["P4"],), 3),
            ("NOR", (node(5),), (node(9),), 5),
            ("NOR", (node(8),), (node(10),), 6),
        )
        output_buses = ((node(7),), (node(11),), (node(3), node(4)))
    else:  # argparse/profile normalization should make this unreachable.
        raise ValueError(f"no current seed for profile {args.profile!r}")
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


def solve(args: argparse.Namespace) -> dict[str, object]:
    started = time.perf_counter()
    normalize_profile_args(args)
    profile = PROFILES[args.profile]
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
        "schema": "tc-byte-adder-bit34-strict-z-exact-v1",
        "status": status,
        "interface": "bit34_joint",
        "profile": args.profile,
        "profile_description": profile["description"],
        "target_names": list(TARGET_NAMES),
        "boundary_states": list(BOUNDARY_STATES),
        "assignments": len(state["source_values"][0]),
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
        "allow_z_false_outputs": [False, False, True],
        "physical_nets": True,
        "solver": args.solver,
        "variables": encoder.pool.top,
        "clauses": len(encoder.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "accounting": {
            "current_complete_gate": profile["current_complete_gate"],
            "current_complete_delay": profile["current_complete_delay"],
            "current_region_gate_with_paid_leaves": profile[
                "current_region_gate_with_paid_leaves"
            ],
            "paid_leaf_gate": profile["paid_leaf_gate"],
            "current_residual_gate": CURRENT_RESIDUAL_GATE,
            "current_residual_components": CURRENT_RESIDUAL_COMPONENTS,
            "fixed_shell_with_paid_leaves": profile[
                "fixed_shell_with_paid_leaves"
            ],
            "projected_complete_gate_at_bound": (
                profile["fixed_shell_with_paid_leaves"] + args.gate_bound
            ),
            "projected_complete_delay": profile["current_complete_delay"],
            "target_complete_gate": profile["target_complete_gate"],
            "gate_gap_at_bound_to_target": (
                profile["fixed_shell_with_paid_leaves"]
                + args.gate_bound
                - profile["target_complete_gate"]
            ),
        },
    }
    if model is not None:
        payload.update(core.decode(internal, state, model))
        payload["accounting"]["projected_complete_gate_actual"] = (
            profile["fixed_shell_with_paid_leaves"] + int(payload["actual_gate"])
        )
        payload["accounting"]["gate_gap_actual_to_target"] = (
            int(payload["accounting"]["projected_complete_gate_actual"])
            - profile["target_complete_gate"]
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


def normalize_profile_args(args: argparse.Namespace) -> None:
    """Apply and validate the fixed timing/accounting contract of a profile."""

    profile = PROFILES[args.profile]
    expected_deadlines = tuple(profile["output_deadlines"])
    if args.output_deadlines is None:
        args.output_deadlines = ",".join(str(value) for value in expected_deadlines)
    else:
        supplied = tuple(int(value) for value in args.output_deadlines.split(","))
        if supplied != expected_deadlines:
            raise ValueError(
                f"profile {args.profile} fixes output deadlines at "
                f"{expected_deadlines}, got {supplied}"
            )
    if args.max_delay is None:
        args.max_delay = int(profile["max_delay"])
    elif args.max_delay != profile["max_delay"]:
        raise ValueError(
            f"profile {args.profile} fixes max delay at "
            f"{profile['max_delay']}, got {args.max_delay}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=tuple(PROFILES), default="d7_80")
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
        help="fix the known 14-gate residual to calibrate strict-Z encoding",
    )
    parser.add_argument("--output-deadlines")
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = solve(args)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(json.dumps({key: value for key, value in payload.items() if key != "network"}, ensure_ascii=False, indent=2))
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
