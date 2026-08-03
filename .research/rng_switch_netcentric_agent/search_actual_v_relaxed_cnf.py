"""Fast optimistic CNF search for the actual six-leaf RNG V cone.

This deliberately imports the older directed-BUS encoder as a relaxation:

* all six raw input complements are supplied for free;
* one driver may still be selected into differently directed BUS subsets.

Consequently UNSAT is a strict lower bound for a real physical circuit.  SAT
is only a lead and must pass ``audit_cnf_witness.py`` before use.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import threading
import time

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UPSTREAM = ROOT / ".research" / "rng_468_joint_macro"
if str(UPSTREAM) not in sys.path:
    sys.path.insert(0, str(UPSTREAM))

from joint_parity_cnf import COST, KINDS, build  # noqa: E402


def parity_table(inputs: int, support: tuple[int, ...]) -> int:
    return sum(
        (sum((case >> bit) & 1 for bit in support) & 1) << case
        for case in range(1 << inputs)
    )


def enforce_physical_alias_closure(enc: object, state: dict[str, object]) -> None:
    """Make every overlapping logical BUS name the same physical net.

    A component output pin is one physical terminal.  If two logical BUSes
    select that terminal, wires join them and their complete driver sets are
    unioned.  Requiring the two selector vectors to be equal is exactly the
    fixed-point condition of that union closure.  Selector vectors belonging
    to early gates are padded with false entries for not-yet-created outputs;
    this also rules out physical feedback hidden by topological numbering.
    """

    source_count = int(state["source_count"])
    kinds = state["kinds"]
    total_sources = source_count + len(kinds)
    buses = [
        *state["left_uses"],
        *state["right_uses"],
        *state["output_uses"],
    ]
    for left_index, left in enumerate(buses):
        for right_index in range(left_index + 1, len(buses)):
            right = buses[right_index]
            overlap_terms = [
                enc.and_term(
                    f"physical_overlap_{left_index}_{right_index}_{source}",
                    (left[source], right[source]),
                )
                for source in range(min(len(left), len(right)))
            ]
            overlap = enc.var(f"physical_overlap_{left_index}_{right_index}")
            enc.equiv_or(overlap, overlap_terms)
            for source in range(total_sources):
                left_use = left[source] if source < len(left) else False
                right_use = right[source] if source < len(right) else False
                enc.clause((-overlap, enc.neg(left_use), right_use))
                enc.clause((-overlap, enc.neg(right_use), left_use))


def enforce_adjacent_kind_order(enc: object, state: dict[str, object]) -> None:
    """Sort adjacent independent gates by kind to remove topological clones.

    Gate ``i`` cannot depend on gate ``i+1`` in the base encoding.  When gate
    ``i+1`` also does not consume gate ``i``, the two adjacent gates can be
    swapped without changing the circuit.  Keeping only nondecreasing kind
    indexes in that case is therefore complete.
    """

    source_count = int(state["source_count"])
    kinds = state["kinds"]
    left_uses = state["left_uses"]
    right_uses = state["right_uses"]
    for slot in range(len(kinds) - 1):
        source = source_count + slot
        direct_dependency = enc.var(f"adjacent_dependency_{slot}")
        enc.equiv_or(
            direct_dependency,
            (left_uses[slot + 1][source], right_uses[slot + 1][source]),
        )
        for left_kind in range(len(KINDS)):
            for right_kind in range(left_kind):
                enc.clause(
                    (
                        direct_dependency,
                        -kinds[slot][left_kind],
                        -kinds[slot + 1][right_kind],
                    )
                )


def enforce_minimal_switch_nets(enc: object, state: dict[str, object]) -> None:
    """Require every Switch output to share a consumed net with a Switch peer.

    A singleton Switch driver resolves numerically to ``enable & data`` at
    every consumer.  Replacing it by an ordinary AND preserves value and
    delay, makes the signal fully driven, and saves one gate.  Consequently a
    minimum-cost witness never contains a singleton Switch output net.
    """

    source_count = int(state["source_count"])
    kinds = state["kinds"]
    buses = [
        *state["left_uses"],
        *state["right_uses"],
        *state["output_uses"],
    ]
    switch_kind = KINDS.index("SWITCH")
    for slot in range(len(kinds)):
        source = source_count + slot
        partner_terms = []
        for other_slot in range(len(kinds)):
            if other_slot == slot:
                continue
            other_source = source_count + other_slot
            for bus_index, bus in enumerate(buses):
                if max(source, other_source) >= len(bus):
                    continue
                partner_terms.append(
                    enc.and_term(
                        f"switch_partner_{slot}_{other_slot}_{bus_index}",
                        (
                            bus[source],
                            bus[other_source],
                            kinds[other_slot][switch_kind],
                        ),
                    )
                )
        enc.clause((-kinds[slot][switch_kind], *partner_terms))


def solve(args: argparse.Namespace) -> dict[str, object]:
    inputs = 6
    targets = (
        parity_table(inputs, (0, 1, 2, 3)),
        parity_table(inputs, (0, 1, 4, 5)),
    )
    started = time.perf_counter()
    enc, state = build(
        inputs,
        targets,
        "all-dual",
        args.gate_bound,
        args.max_delay,
        args.components,
        args.switches,
        args.xors,
        args.output_drivers,
        args.terminal_switch_drivers,
        None,
    )
    if args.physical_alias_closure:
        enforce_physical_alias_closure(enc, state)
    if args.adjacent_kind_order:
        enforce_adjacent_kind_order(enc, state)
    if args.minimal_switch_nets:
        enforce_minimal_switch_nets(enc, state)
    output_driver_counts = None
    if args.output_driver_counts is not None:
        output_driver_counts = tuple(
            int(item) for item in args.output_driver_counts.split(",")
        )
        output_uses = state["output_uses"]
        if len(output_driver_counts) != len(output_uses):
            raise ValueError("output-driver-counts must contain one value per output")
        for uses, count in zip(output_uses, output_driver_counts, strict=True):
            enc.cnf.extend(
                CardEnc.equals(
                    lits=uses,
                    bound=count,
                    vpool=enc.pool,
                    encoding=EncType.seqcounter,
                ).clauses
            )
    status = "unknown"
    reason = None
    model = None
    with Solver(name=args.solver, bootstrap_with=enc.cnf) as solver:
        timer = threading.Timer(args.timeout, solver.interrupt) if args.timeout > 0 else None
        if timer:
            timer.start()
        try:
            answer = solver.solve_limited(expect_interrupt=True)
        finally:
            if timer:
                timer.cancel()
        if answer is True:
            status = "sat"
            model = solver.get_model()
        elif answer is False:
            status = "unsat"
        else:
            reason = "timeout"
    assignments = 1 << inputs
    payload: dict[str, object] = {
        "schema": 1,
        "model": (
            "actual V targets with physical BUS alias closure and free complements"
            if args.physical_alias_closure
            else "actual V targets in directed-BUS/all-free-complements optimistic relaxation"
        ),
        "status": status,
        "source_mode": "all-dual",
        "inputs": inputs,
        "target_truth_tables_hex": [f"{target:0{assignments // 4}x}" for target in targets],
        "gate_bound": args.gate_bound,
        "max_delay": args.max_delay,
        "components": args.components,
        "exact_switches": args.switches,
        "exact_xors": args.xors,
        "exact_output_drivers": args.output_drivers,
        "terminal_switch_drivers": args.terminal_switch_drivers,
        "physical_alias_closure": args.physical_alias_closure,
        "adjacent_kind_order": args.adjacent_kind_order,
        "minimal_switch_nets": args.minimal_switch_nets,
        "output_driver_counts": output_driver_counts,
        "solver": args.solver,
        "timeout_seconds": args.timeout,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "library": {name: [COST[index], (2 if name == "XOR" else 1)] for index, name in enumerate(KINDS)},
        "relaxations": [
            "all six raw complements are free",
            *([] if args.physical_alias_closure else [
                "directed BUS subsets do not enforce physical net alias closure"
            ]),
            "zero output may be Z",
        ],
        "sat_requires_union_find_replay": True,
    }
    if reason:
        payload["reason_unknown"] = reason
    if status == "sat" and model is not None:
        enabled = {literal for literal in model if literal > 0}
        source_count = int(state["source_count"])
        network = []
        actual_gate = 0
        for slot in range(args.components):
            candidate = next(
                index for index, literal in enumerate(state["kinds"][slot]) if literal in enabled
            )
            actual_gate += COST[candidate]
            depth = next(
                index + 1 for index, literal in enumerate(state["levels"][slot]) if literal in enabled
            )
            network.append(
                {
                    "slot": slot,
                    "source": source_count + slot,
                    "kind": KINDS[candidate],
                    "left_bus": [
                        index for index, literal in enumerate(state["left_uses"][slot]) if literal in enabled
                    ],
                    "right_bus": [
                        index for index, literal in enumerate(state["right_uses"][slot]) if literal in enabled
                    ],
                    "cost": COST[candidate],
                    "depth_upper_bound": depth,
                }
            )
        payload["actual_gate"] = actual_gate
        payload["network"] = network
        payload["output_buses"] = [
            [index for index, literal in enumerate(uses) if literal in enabled]
            for uses in state["output_uses"]
        ]
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int)
    parser.add_argument("--output-drivers", type=int)
    parser.add_argument("--terminal-switch-drivers", type=int)
    parser.add_argument("--physical-alias-closure", action="store_true")
    parser.add_argument("--adjacent-kind-order", action="store_true")
    parser.add_argument("--minimal-switch-nets", action="store_true")
    parser.add_argument("--output-driver-counts")
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = solve(args)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.write_bytes(encoded)
    print(json.dumps({"status": payload["status"], "seconds": payload["solve_seconds"], "variables": payload["variables"], "clauses": payload["clauses"]}))
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 2 if payload["status"] == "unknown" else 0


if __name__ == "__main__":
    raise SystemExit(main())
