"""Exact Switch/Z synthesis for fast-negative Byte Adder boundaries.

The Boolean functions in this file are small correlated interfaces cut out of
the reviewed fast complemented-A/V shell.  The SAT implementation is reused
from ``exact_free_ling_pair_sat.py`` so that gate costs, Switch high-Z state,
BUS conflicts, and physical net partitioning stay identical to the audited
models used elsewhere in this repository.

This worker is intentionally save-independent.  It neither imports the game
runtime nor reads or writes a Turing Complete save.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import threading
import time
from typing import Callable, Iterable

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UPSTREAM_PATH = (
    ROOT / ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py"
)
DEPENDENCY_PATHS = (
    UPSTREAM_PATH,
    ROOT / ".research/byte_adder_boolean_superopt_agent/exact_adder_block_sat.py",
    ROOT / ".research/rng_468_joint_macro/joint_parity_cnf.py",
)


def dependency_sha256() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path.read_bytes()).hexdigest()
        for path in DEPENDENCY_PATHS
    }


def _load_upstream():
    spec = importlib.util.spec_from_file_location(
        "phase_shortcut_physical_upstream", UPSTREAM_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(UPSTREAM_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


upstream = _load_upstream()
G = upstream.G


@dataclass(frozen=True)
class Domain:
    names: tuple[str, ...]
    columns: tuple[tuple[bool, ...], ...]
    targets: tuple[int, ...]
    arrivals: dict[str, int]
    output_names: tuple[str, ...]

    @property
    def rows(self) -> int:
        return len(self.columns[0])


def _pack(values: Iterable[bool]) -> int:
    return sum(int(value) << case for case, value in enumerate(values))


def _finish_domain(
    rows: list[dict[str, bool]],
    targets: list[tuple[bool, ...]],
    arrivals: dict[str, int],
    output_names: tuple[str, ...],
) -> Domain:
    names = tuple(arrivals)
    columns = tuple(tuple(row[name] for row in rows) for name in names)
    packed_targets = tuple(
        _pack(target[index] for target in targets)
        for index in range(len(output_names))
    )
    if not rows or any(len(column) != len(rows) for column in columns):
        raise AssertionError("invalid truth domain")
    return Domain(names, columns, packed_targets, arrivals, output_names)


def _local_state(state: int) -> tuple[bool, bool, bool, bool]:
    """Return G/Q/P/N for kill, propagate, or generate."""

    if state not in range(3):
        raise ValueError(state)
    q = state == 0
    p = state == 1
    g = state == 2
    return g, q, p, not g


def _prefix_values(
    local: dict[int, tuple[bool, bool, bool, bool]], nc3: bool
) -> dict[str, bool]:
    g3, q3, p3, n3 = local[3]
    g4, q4, p4, n4 = local[4]
    g5, q5, p5, n5 = local[5]
    g6, q6, p6, n6 = local[6]
    a34 = q3 or q4
    v34 = n4 and (q4 or n3)
    a56 = q5 or q6
    v56 = n6 and (q6 or n5)
    a36 = a34 or a56
    v36 = v56 and (a56 or v34)
    nc4 = q3 or (p3 and nc3)
    nc5 = q4 or (p4 and nc4)
    nc6 = q5 or (p5 and nc5)
    nc7 = q6 or (p6 and nc6)
    return {
        "A34n": a34,
        "V34n": v34,
        "A56n": a56,
        "V56n": v56,
        "A36n": a36,
        "V36n": v36,
        "nC4": nc4,
        "nC5": nc5,
        "nC6": nc6,
        "nC7": nc7,
    }


def domain_s56() -> Domain:
    """Paid fast-negative S5/S6 boundary, including raw local inputs."""

    arrivals = {
        "A34n": 2,
        "V34n": 2,
        "nC3": 3,
        "a5": 0,
        "b5": 0,
        "a6": 0,
        "b6": 0,
        "G5": 1,
        "Q5": 1,
        "P5": 2,
        "N5": 1,
        "G6": 1,
        "Q6": 1,
        "P6": 2,
        "N6": 1,
        "A56n": 2,
        "V56n": 2,
        "A36n": 3,
        "V36n": 3,
        "nC7": 4,
    }
    rows: list[dict[str, bool]] = []
    targets: list[tuple[bool, bool]] = []
    # A=>V is the exact set of reachable complemented-A/V states.
    for a34, v34 in ((False, False), (False, True), (True, True)):
        for nc3 in (False, True):
            for raw5 in range(4):
                a5, b5 = bool(raw5 & 1), bool(raw5 & 2)
                for raw6 in range(4):
                    a6, b6 = bool(raw6 & 1), bool(raw6 & 2)
                    g5, q5, p5, n5 = (
                        a5 and b5,
                        not (a5 or b5),
                        a5 ^ b5,
                        not (a5 and b5),
                    )
                    g6, q6, p6, n6 = (
                        a6 and b6,
                        not (a6 or b6),
                        a6 ^ b6,
                        not (a6 and b6),
                    )
                    a56 = q5 or q6
                    v56 = n6 and (q6 or n5)
                    a36 = a34 or a56
                    v36 = v56 and (a56 or v34)
                    nc5 = v34 and (a34 or nc3)
                    nc6 = q5 or (p5 and nc5)
                    nc7 = q6 or (p6 and nc6)
                    rows.append(
                        {
                            "A34n": a34,
                            "V34n": v34,
                            "nC3": nc3,
                            "a5": a5,
                            "b5": b5,
                            "a6": a6,
                            "b6": b6,
                            "G5": g5,
                            "Q5": q5,
                            "P5": p5,
                            "N5": n5,
                            "G6": g6,
                            "Q6": q6,
                            "P6": p6,
                            "N6": n6,
                            "A56n": a56,
                            "V56n": v56,
                            "A36n": a36,
                            "V36n": v36,
                            "nC7": nc7,
                        }
                    )
                    targets.append((p5 == nc5, p6 == nc6))
    return _finish_domain(rows, targets, arrivals, ("S5", "S6"))


def domain_s12_leaf() -> Domain:
    """D5 search boundary for S1/S2 with the fast nC1 prefix paid."""

    arrivals = {
        "nC1": 2,
        "G1": 1,
        "Q1": 1,
        "P1": 2,
        "N1": 1,
        "G2": 1,
        "Q2": 1,
        "P2": 2,
        "N2": 1,
        "A12n": 2,
        "V12n": 2,
        "nC3": 3,
    }
    rows: list[dict[str, bool]] = []
    targets: list[tuple[bool, bool]] = []
    for nc1 in (False, True):
        for state1, state2 in itertools.product(range(3), repeat=2):
            g1, q1, p1, n1 = _local_state(state1)
            g2, q2, p2, n2 = _local_state(state2)
            a12 = q1 or q2
            v12 = n2 and (q2 or n1)
            nc2 = q1 or (p1 and nc1)
            nc3 = q2 or (p2 and nc2)
            rows.append(
                {
                    "nC1": nc1,
                    "G1": g1,
                    "Q1": q1,
                    "P1": p1,
                    "N1": n1,
                    "G2": g2,
                    "Q2": q2,
                    "P2": p2,
                    "N2": n2,
                    "A12n": a12,
                    "V12n": v12,
                    "nC3": nc3,
                }
            )
            targets.append((p1 == nc1, p2 == nc2))
    return _finish_domain(rows, targets, arrivals, ("S1", "S2"))


def domain_s3456_leaf() -> Domain:
    """Joint four-sum window over paid ternary G/Q/P/N leaves."""

    arrivals = {"nC3": 3}
    for bit in range(3, 7):
        arrivals.update(
            {
                f"G{bit}": 1,
                f"Q{bit}": 1,
                f"P{bit}": 2,
                f"N{bit}": 1,
            }
        )
    arrivals.update(
        {
            "A34n": 2,
            "V34n": 2,
            "A56n": 2,
            "V56n": 2,
            "A36n": 3,
            "V36n": 3,
            "nC7": 4,
        }
    )
    rows: list[dict[str, bool]] = []
    targets: list[tuple[bool, bool, bool, bool]] = []
    for nc3 in (False, True):
        for states in itertools.product(range(3), repeat=4):
            local = {
                bit: _local_state(state)
                for bit, state in zip(range(3, 7), states, strict=True)
            }
            prefix = _prefix_values(local, nc3)
            row = {"nC3": nc3}
            for bit, (g, q, p, n) in local.items():
                row.update(
                    {f"G{bit}": g, f"Q{bit}": q, f"P{bit}": p, f"N{bit}": n}
                )
            row.update({name: prefix[name] for name in arrivals if name in prefix})
            rows.append(row)
            targets.append(
                tuple(
                    local[bit][2] == (nc3 if bit == 3 else prefix[f"nC{bit}"])
                    for bit in range(3, 7)
                )
            )
    return _finish_domain(rows, targets, arrivals, ("S3", "S4", "S5", "S6"))


def domain_s34567c8_leaf() -> Domain:
    """D5 high window used by the conditional 102/5 construction."""

    arrivals = {"nC3": 3}
    for bit in range(3, 7):
        arrivals.update(
            {
                f"G{bit}": 1,
                f"Q{bit}": 1,
                f"P{bit}": 2,
                f"N{bit}": 1,
            }
        )
    arrivals.update({"G7": 1, "Q7": 1, "P7": 2})
    arrivals.update(
        {
            "A34n": 2,
            "V34n": 2,
            "A56n": 2,
            "V56n": 2,
            "A36n": 3,
            "V36n": 3,
            "nC7": 4,
        }
    )
    rows: list[dict[str, bool]] = []
    targets: list[tuple[bool, ...]] = []
    for nc3 in (False, True):
        for states in itertools.product(range(3), repeat=5):
            local = {
                bit: _local_state(state)
                for bit, state in zip(range(3, 8), states, strict=True)
            }
            prefix = _prefix_values(local, nc3)
            row = {"nC3": nc3}
            for bit in range(3, 7):
                g, q, p, n = local[bit]
                row.update(
                    {f"G{bit}": g, f"Q{bit}": q, f"P{bit}": p, f"N{bit}": n}
                )
            g7, q7, p7, _n7 = local[7]
            row.update({"G7": g7, "Q7": q7, "P7": p7})
            row.update({name: prefix[name] for name in arrivals if name in prefix})
            nc7 = prefix["nC7"]
            nc8 = q7 or (p7 and nc7)
            rows.append(row)
            targets.append(
                (
                    *(local[bit][2] == (nc3 if bit == 3 else prefix[f"nC{bit}"])
                      for bit in range(3, 7)),
                    p7 == nc7,
                    not nc8,
                )
            )
    return _finish_domain(
        rows,
        targets,
        arrivals,
        ("S3", "S4", "S5", "S6", "S7", "C8"),
    )


DOMAINS: dict[str, Callable[[], Domain]] = {
    "s56": domain_s56,
    "s12_leaf": domain_s12_leaf,
    "s3456_leaf": domain_s3456_leaf,
    "s34567c8_leaf": domain_s34567c8_leaf,
}


def suffix_universe(
    *, components: int, split_slots: int, switches: int, xors: int
) -> tuple[tuple[int, ...], ...]:
    width = min(components, split_slots)
    ordinary = components - switches - xors
    result = []
    for signature in itertools.product(range(len(G.KINDS)), repeat=width):
        signature_switches = signature.count(G.SWITCH)
        signature_xors = signature.count(G.XOR)
        signature_ordinary = width - signature_switches - signature_xors
        if signature_switches > switches or signature_xors > xors:
            continue
        if signature_ordinary > ordinary:
            continue
        result.append(signature)
    return tuple(result)


def _signature_payload(signatures: Iterable[tuple[int, ...]]) -> list[list[str]]:
    return [[G.KINDS[kind] for kind in signature] for signature in signatures]


def constrain_shard(enc, state, args) -> dict[str, object]:
    universe = suffix_universe(
        components=args.components,
        split_slots=args.split_slots,
        switches=args.switches,
        xors=args.xors,
    )
    assigned = tuple(
        signature
        for index, signature in enumerate(universe)
        if index % args.shard_count == args.shard_index
    )
    width = min(args.components, args.split_slots)
    first_slot = args.components - width
    selectors = []
    for index, signature in enumerate(assigned):
        selector = enc.var(f"suffix_shard_{args.shard_index}_choice_{index}")
        selectors.append(selector)
        for offset, kind in enumerate(signature):
            enc.clause((-selector, state["kinds"][first_slot + offset][kind]))
    enc.clause(selectors)
    encoded_universe = json.dumps(
        _signature_payload(universe), sort_keys=True, separators=(",", ":")
    ).encode()
    return {
        "split_slots": width,
        "shard_count": args.shard_count,
        "shard_index": args.shard_index,
        "suffix_universe_count": len(universe),
        "suffix_universe_sha256": sha256(encoded_universe).hexdigest(),
        "assigned_suffix_signatures": _signature_payload(assigned),
    }


def constrain_fixed_kinds(enc, state, args) -> tuple[str, ...] | None:
    if not args.fixed_kinds:
        return None
    names = tuple(filter(None, args.fixed_kinds.split(",")))
    if len(names) != args.components:
        raise ValueError(
            f"fixed-kinds has {len(names)} entries, expected {args.components}"
        )
    unknown = sorted(set(names) - {*G.KINDS, "*"})
    if unknown:
        raise ValueError(f"unknown fixed gate kinds: {unknown}")
    if names.count("SWITCH") > args.switches or names.count("XOR") > args.xors:
        raise ValueError("fixed-kinds exceeds the Switch/XOR decomposition")
    for slot, name in enumerate(names):
        if name != "*":
            enc.clause((state["kinds"][slot][G.KINDS.index(name)],))
    return names


def verify_timing(payload, state) -> dict[str, object]:
    arrivals = list(state["source_arrivals"])
    bound_violations = 0
    for item in payload["network"]:
        inputs = item["left_bus"] + item["right_bus"]
        input_arrival = max((arrivals[source] for source in inputs), default=0)
        kind = G.KINDS.index(item["kind"])
        actual = input_arrival + G.DELAY[kind]
        arrivals.append(actual)
        bound_violations += actual > int(item["depth_upper_bound"])
    output_arrivals = [
        max((arrivals[source] for source in bus), default=0)
        for bus in payload["output_buses"]
    ]
    deadline_violations = sum(
        arrival > deadline
        for arrival, deadline in zip(
            output_arrivals, state["output_deadlines"], strict=True
        )
    )
    return {
        "actual_output_arrivals": output_arrivals,
        "actual_max_delay": max(output_arrivals, default=0),
        "depth_upper_bound_violation_count": bound_violations,
        "output_deadline_violation_count": deadline_violations,
    }


def solve(args: argparse.Namespace) -> dict[str, object]:
    if args.domain not in DOMAINS:
        raise ValueError(args.domain)
    domain = DOMAINS[args.domain]()
    if args.outputs:
        requested_outputs = tuple(filter(None, args.outputs.split(",")))
        unknown = sorted(set(requested_outputs) - set(domain.output_names))
        if unknown:
            raise ValueError(f"unknown outputs for {args.domain}: {unknown}")
        indices = tuple(domain.output_names.index(name) for name in requested_outputs)
        domain = Domain(
            domain.names,
            domain.columns,
            tuple(domain.targets[index] for index in indices),
            domain.arrivals,
            requested_outputs,
        )
    expected_gate = args.components + args.switches + 2 * args.xors
    if expected_gate != args.gate_bound:
        raise ValueError(
            "inconsistent decomposition: "
            f"components({args.components}) + switches({args.switches}) + "
            f"2*xors({args.xors}) != gate_bound({args.gate_bound})"
        )
    ordinary = args.components - args.switches - args.xors
    if ordinary < 0:
        raise ValueError("negative ordinary component count")
    if not 0 <= args.shard_index < args.shard_count:
        raise ValueError("shard index is outside shard count")

    def truth_tables(_interface: str):
        return (
            list(domain.names),
            [list(column) for column in domain.columns],
            domain.targets,
            domain.arrivals,
        )

    upstream.truth_tables = truth_tables
    build_args = argparse.Namespace(
        interface=f"phase_{args.domain}",
        gate_bound=args.gate_bound,
        max_delay=args.max_delay,
        components=args.components,
        switches=args.switches,
        xors=args.xors,
        h_arrival=4,
        c5_arrival=4,
        output_deadlines=",".join([str(args.max_delay)] * len(domain.targets)),
    )
    started = time.perf_counter()
    enc, state = upstream.build(build_args)
    fixed_kinds = constrain_fixed_kinds(enc, state, args)
    shard = constrain_shard(enc, state, args)
    model = None
    answer = None
    timer = None
    timer_errors: list[str] = []
    with Solver(name=args.solver, bootstrap_with=enc.cnf) as solver:
        if args.timeout:
            if "cadical" in args.solver.lower() or args.solver.lower().startswith("cd"):
                raise ValueError(
                    "PySAT CaDiCaL does not support interrupt reliably; use "
                    "--timeout 0 under the outer hard-timeout sweep runner"
                )

            def interrupt() -> None:
                try:
                    solver.interrupt()
                except Exception as exc:  # pragma: no cover - backend-specific
                    timer_errors.append(repr(exc))

            timer = threading.Timer(args.timeout, interrupt)
            timer.start()
        try:
            if args.timeout:
                answer = solver.solve_limited(expect_interrupt=True)
            else:
                answer = solver.solve()
            if answer is True:
                model = solver.get_model()
        finally:
            if timer:
                timer.cancel()

    status = "sat" if answer is True else "unsat" if answer is False else "unknown"
    payload: dict[str, object] = {
        "schema": "exact-fast-negative-physical-shard-v2",
        "status": status,
        "domain": args.domain,
        "rows": domain.rows,
        "output_names": domain.output_names,
        "free_sources": [*domain.names, "0", "1"],
        "source_arrivals": dict(
            zip(state["names"], state["source_arrivals"], strict=True)
        ),
        "gate_bound": args.gate_bound,
        "max_delay": args.max_delay,
        "components": args.components,
        "ordinary": ordinary,
        "exact_switches": args.switches,
        "exact_xors": args.xors,
        "fixed_kinds": fixed_kinds,
        "solver": args.solver,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "physical_nets": True,
        "public_outputs_must_be_driven": True,
        "shard": shard,
        "timer_errors": timer_errors,
        "dependency_sha256": dependency_sha256(),
    }
    if model is not None:
        payload.update(upstream.decode(build_args, state, model))
        semantic = upstream.verify(payload, state)
        timing = verify_timing(payload, state)
        payload["verification"] = {**semantic, **timing}
        failures = sum(int(value) for key, value in semantic.items() if key.endswith("count"))
        failures += timing["depth_upper_bound_violation_count"]
        failures += timing["output_deadline_violation_count"]
        if payload["actual_gate"] > args.gate_bound or failures:
            raise RuntimeError(f"decoded witness failed verification: {payload['verification']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", choices=tuple(DOMAINS), required=True)
    parser.add_argument(
        "--outputs",
        help="comma-separated output subset for focused exact searches",
    )
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int, required=True)
    parser.add_argument("--xors", type=int, required=True)
    parser.add_argument(
        "--fixed-kinds",
        help="comma-separated exact kind for every topological component slot",
    )
    parser.add_argument("--split-slots", type=int, default=3)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--timeout", type=float, default=0.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = solve(args)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    summary = {key: value for key, value in payload.items() if key != "network"}
    summary["output"] = str(args.output)
    summary["sha256"] = sha256(encoded.encode()).hexdigest()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
