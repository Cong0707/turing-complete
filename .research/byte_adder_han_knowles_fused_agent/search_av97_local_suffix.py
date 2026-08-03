"""Exact low-memory search of the live 97/6 adder's local D6 suffix.

The paid source interface is extracted from ``build_av_reduced_97_d6.py``
instead of being re-described algebraically.  This matters because C5, V56,
V3456 and C7 are physical three-state rails: their value and driven masks are
both part of the interface.  Full 2^17 traces are deduplicated before CNF
construction, so the exact solver sees only behaviourally distinct rows.

The searched outputs are S6, S7 and C8.  The current implementation costs
eleven local gates (two Switches and seven ordinary components).  A witness at
cost ten or less can therefore replace that region and produce a <=96/6 full
adder after structural replay.

This script is offline only.  It does not touch the save and never launches
the game.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import threading
import time

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILDER = ROOT / ".research/byte_adder_av_reduced_forward/build_av_reduced_97_d6.py"
CORE = ROOT / ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def capture_live_factory():
    builder = _load(BUILDER, "av97_suffix_builder")
    captured = {}
    original = builder.serialize

    def capture(factory, outputs):
        captured["factory"] = factory
        captured["outputs"] = tuple(outputs)
        return original(factory, outputs)

    builder.serialize = capture
    payload = builder.build()
    return captured["factory"], captured["outputs"], payload


def make_problem(source_profile: str = "paid"):
    factory, outputs, payload = capture_live_factory()
    # IDs are stable structural anchors in the reviewed 97/6 builder.  Every
    # non-input source below is already reachable from either S0..S5 or the
    # retained fast C7 prefix.  Final materialisation must still recompute the
    # whole-DAG cost, because an unused paid source can disappear.
    expanded_source_ids = {
        "a5": factory.inputs["a5"],
        "b5": factory.inputs["b5"],
        "a6": factory.inputs["a6"],
        "b6": factory.inputs["b6"],
        "a7": factory.inputs["a7"],
        "b7": factory.inputs["b7"],
        "C3": 53,
        "A34": 54,
        "V34": 55,
        "C5": 56,
        "G5": 37,
        "Q5": 38,
        "P5": 39,
        "V5": 40,
        "G6": 41,
        "Q6": 42,
        "P6": 43,
        "V6": 44,
        "G7": 45,
        "Q7": 46,
        "P7": 47,
        "A56": 57,
        "V56": 58,
        "A3456": 59,
        "V3456": 60,
        "C7": 61,
        "T5": 80,
    }
    profiles = {
        # Smallest complete paid-phase interface.  It exactly contains every
        # source used by the existing eleven-gate suffix and collapses the
        # full trace to only 81 rows.
        "paid": (
            "C5", "G5", "Q5", "P5", "G6", "Q6", "P6",
            "G7", "Q7", "P7", "C7", "T5",
        ),
        # Add raw suffix operands, allowing a witness to bypass a paid leaf.
        "raw": (
            "a5", "b5", "a6", "b6", "a7", "b7",
            "C5", "G5", "Q5", "P5", "G6", "Q6", "P6",
            "G7", "Q7", "P7", "C7", "T5",
        ),
        # Diagnostic superset for later C7-prefix co-synthesis.
        "expanded": tuple(expanded_source_ids),
    }
    source_ids = {
        name: expanded_source_ids[name] for name in profiles[source_profile]
    }
    target_ids = (outputs[6], outputs[7], outputs[8])
    packed, _report = factory.evaluate(tuple(source_ids.values()) + target_ids)

    # Deduplicate full trace rows by source value+driven state and targets.
    signatures = set()
    for case in range(factory.core.ASSIGNMENTS if hasattr(factory, "core") else 1 << 17):
        key = []
        for node in source_ids.values():
            signal = packed[node]
            key.extend(((signal.value >> case) & 1, (signal.driven >> case) & 1))
        key.extend((packed[node].value >> case) & 1 for node in target_ids)
        signatures.add(tuple(key))
    signatures = sorted(signatures)

    names = list(source_ids)
    rows = [[] for _ in names]
    driven_rows = [[] for _ in names]
    targets = [[] for _ in target_ids]
    for signature in signatures:
        for index in range(len(names)):
            rows[index].append(bool(signature[index * 2]))
            driven_rows[index].append(bool(signature[index * 2 + 1]))
        offset = len(names) * 2
        for output in range(len(target_ids)):
            targets[output].append(bool(signature[offset + output]))

    target_masks = tuple(
        sum(int(value) << case for case, value in enumerate(row))
        for row in targets
    )
    arrivals = {
        name: factory.nodes[node].arrival for name, node in source_ids.items()
    }
    return (
        (names, rows, target_masks, arrivals),
        dict(zip(names, driven_rows, strict=True)),
        {
            "deduplicated_rows": len(signatures),
            "source_profile": source_profile,
            "source_node_ids": source_ids,
            "target_node_ids": target_ids,
            "baseline_metrics": payload["metrics"],
        },
    )


def load_core(problem, source_drivens):
    text = CORE.read_text(encoding="utf-8")
    begin = text.index("def truth_tables(")
    end = text.index("def weighted_bound", begin)
    text = text[:begin] + "def truth_tables(_interface):\n    return CURRENT_TRUTH\n\n\n" + text[end:]
    old = '''    # The current phase-fold C7 is a resolved BUS.  It is active whenever
    # either of its two switch enables (T or A, named ``G`` here) is true;
    # otherwise a Boolean-zero carry is represented by Z.  Keeping this mask
    # exact is essential when a synthesized Switch consumes C7.
    if args.interface == "s6":
        t_values = source_values[names.index("T")]
        a_values = source_values[names.index("G")]
        drivens[names.index("C7")] = [
            bool(t_values[case] or a_values[case]) for case in range(assignments)
        ]'''
    new = '''    for source_name, source_driven in CURRENT_SOURCE_DRIVENS.items():
        drivens[names.index(source_name)] = list(source_driven)'''
    if old not in text:
        raise RuntimeError("source-driven patch anchor changed")
    text = text.replace(old, new)
    namespace = {
        "__name__": "av97_local_suffix_exact_core",
        "__file__": str(CORE),
        "__package__": None,
        "CURRENT_TRUTH": problem,
        "CURRENT_SOURCE_DRIVENS": source_drivens,
    }
    exec(compile(text, str(CORE), "exec"), namespace)
    return namespace


def solve(enc, solver_name: str, timeout: float):
    with Solver(name=solver_name, bootstrap_with=enc.cnf) as solver:
        timer = threading.Timer(timeout, solver.interrupt) if timeout else None
        if timer:
            timer.start()
        try:
            answer = solver.solve_limited(expect_interrupt=True) if timeout else solver.solve()
            model = solver.get_model() if answer is True else None
        finally:
            if timer:
                timer.cancel()
    return answer, model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument(
        "--source-profile", choices=("paid", "raw", "expanded"), default="paid"
    )
    parser.add_argument("--output", type=Path, required=True)
    args_cli = parser.parse_args()

    problem, source_drivens, metadata = make_problem(args_cli.source_profile)
    core = load_core(problem, source_drivens)
    args = argparse.Namespace(
        interface="s6",
        gate_bound=args_cli.gate_bound,
        max_delay=6,
        components=args_cli.components,
        switches=args_cli.switches,
        xors=args_cli.xors,
        h_arrival=4,
        c5_arrival=4,
        output_deadlines="6,6,6",
        solver=args_cli.solver,
        timeout=args_cli.timeout,
        output=args_cli.output,
    )
    started = time.perf_counter()
    enc, state = core["build"](args)
    answer, model = solve(enc, args.solver, args_cli.timeout)
    status = "sat" if answer is True else "unsat" if answer is False else "unknown"
    payload = {
        "schema": "av97-local-suffix-exact-v1",
        "status": status,
        "gate_bound": args_cli.gate_bound,
        "components": args_cli.components,
        "exact_switches": args_cli.switches,
        "exact_xors": args_cli.xors,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "paid_sources": state["names"],
        "source_arrivals": dict(zip(state["names"], state["source_arrivals"], strict=True)),
        "output_deadlines": [6, 6, 6],
        **metadata,
    }
    if model is not None:
        payload.update(core["decode"](args, state, model))
        payload["verification"] = core["verify"](payload, state)
    args_cli.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in payload.items() if k not in ("network", "paid_sources", "source_arrivals", "source_node_ids")}, ensure_ascii=False, indent=2))
    return 0 if status != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
