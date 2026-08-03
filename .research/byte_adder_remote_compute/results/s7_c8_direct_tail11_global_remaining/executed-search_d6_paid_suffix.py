"""Low-memory exact D6 search over the paid 80/7 suffix phases.

Paid sources reproduce the live 80/7 suffix exactly: C5@4, G/Q/P leaves,
T=P5P6@3, D=~(Q6|T)@4, A=G5|G6@2, the resolved C7@5 rail, and
T5=P5&C5@5.  Modes synthesize S6 alone, the S7/C8 tail, or all four suffix
outputs with absolute deadline 6.  The script only builds one CNF and exits.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import threading
import time

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py"


def load_core():
    text = SOURCE.read_text(encoding="utf-8")
    begin = text.index("def truth_tables(")
    end = text.index("def weighted_bound", begin)
    text = text[:begin] + "def truth_tables(_interface):\n    return CURRENT_TRUTH\n\n\n" + text[end:]
    old = '''    if args.interface == "s6":
        t_values = source_values[names.index("T")]
        a_values = source_values[names.index("G")]
        drivens[names.index("C7")] = [
            bool(t_values[case] or a_values[case]) for case in range(assignments)
        ]'''
    new = '''    if args.interface == "s6":
        drivens[names.index("C7")] = list(CURRENT_C7_DRIVEN)'''
    if old not in text:
        raise RuntimeError("C7 driven-mask anchor changed")
    text = text.replace(old, new)
    namespace = {
        "__name__": "d6_paid_suffix_exact_core",
        "__file__": str(SOURCE),
        "__package__": None,
        "CURRENT_TRUTH": None,
        "CURRENT_C7_DRIVEN": None,
    }
    exec(compile(text, str(SOURCE), "exec"), namespace)
    return namespace


def problem(mode: str):
    assignments = 128
    variables = [
        [bool((case >> index) & 1) for case in range(assignments)]
        for index in range(7)
    ]
    a5, b5, a6, b6, a7, b7, c5 = variables

    def pw(fn, *rows):
        return [bool(fn(*(int(row[index]) for row in rows))) for index in range(assignments)]

    g5 = pw(lambda a, b: a & b, a5, b5)
    q5 = pw(lambda a, b: 1 ^ (a | b), a5, b5)
    p5 = pw(lambda g, q: 1 ^ (g | q), g5, q5)
    g6 = pw(lambda a, b: a & b, a6, b6)
    q6 = pw(lambda a, b: 1 ^ (a | b), a6, b6)
    p6 = pw(lambda g, q: 1 ^ (g | q), g6, q6)
    g7 = pw(lambda a, b: a & b, a7, b7)
    q7 = pw(lambda a, b: 1 ^ (a | b), a7, b7)
    p7 = pw(lambda g, q: 1 ^ (g | q), g7, q7)
    np7 = pw(lambda p: 1 ^ p, p7)
    transfer = pw(lambda a, b: a & b, p5, p6)
    phase = pw(lambda q, t: 1 ^ (q | t), q6, transfer)
    any_generate = pw(lambda a, b: a | b, g5, g6)
    c7 = pw(
        lambda t, c, a, d: (t & c) | (a & d),
        transfer,
        c5,
        any_generate,
        phase,
    )
    t5 = pw(lambda p, c: p & c, p5, c5)
    c6 = pw(lambda g, p, c: g | (p & c), g5, p5, c5)
    c8 = pw(lambda g, p, c: g | (p & c), g7, p7, c7)
    s5 = pw(lambda p, c: p ^ c, p5, c5)
    s6 = pw(lambda p, c: p ^ c, p6, c6)
    s7 = pw(lambda p, c: p ^ c, p7, c7)
    # Ordinary intermediate phases from the exact eight-gate D6 S6 macro:
    #
    #   N0 = NAND(C5,P5)      @5  (the complement of T5)
    #   O0 = NOR(G5,P6)       @3
    #   X0 = AND(P6,A)        @3
    #   Y0 = NOR(O0,X0)       @4
    #   S6 = BUS(Switch(T5,O0), Switch(N0,Y0)) @6
    #
    # Only the four ordinary phases and the fully resolved S6 rail are
    # reusable.  The two individual Switch drivers must remain on their own
    # physical nets and therefore are deliberately not exposed as sources.
    n0 = pw(lambda c, p: 1 ^ (c & p), c5, p5)
    o0 = pw(lambda g, p: 1 ^ (g | p), g5, p6)
    x0 = pw(lambda p, a: p & a, p6, any_generate)
    y0 = pw(lambda o, x: 1 ^ (o | x), o0, x0)
    names = [
        "a5", "b5", "a6", "b6", "a7", "b7", "C5",
        "G5", "Q5", "P5", "G6", "Q6", "P6",
        "G7", "Q7", "P7", "T", "D", "A", "C7", "T5",
    ]
    rows = [
        a5, b5, a6, b6, a7, b7, c5,
        g5, q5, p5, g6, q6, p6,
        g7, q7, p7, transfer, phase, any_generate, c7, t5,
    ]
    arrivals = {
        "C5": 4,
        "G5": 1, "Q5": 1, "P5": 2,
        "G6": 1, "Q6": 1, "P6": 2,
        "G7": 1, "Q7": 1, "P7": 2,
        "T": 3, "D": 4, "A": 2, "C7": 5, "T5": 5,
    }
    if mode == "tail_s6phases":
        names.extend(("N0", "O0", "X0", "Y0", "S6"))
        rows.extend((n0, o0, x0, y0, s6))
        arrivals.update({"N0": 5, "O0": 3, "X0": 3, "Y0": 4, "S6": 6})
    if mode == "s7_np":
        # The minimum D6 C8 macro already pays NP7=~P7 at arrival three:
        # C8=BUS(SW(P7,C7),SW(NP7,G7)).  Exposing that ordinary phase tests
        # whether S7 can be appended for <=6 additional gates, yielding an
        # eleven-gate shared tail in total.
        names.append("NP7")
        rows.append(np7)
        arrivals["NP7"] = 3
    choices = {
        "s6": (s6,),
        "s7": (s7,),
        "s7_np": (s7,),
        "c8": (c8,),
        "tail": (s7, c8),
        "tail_s6phases": (s7, c8),
        "joint": (s6, s7, c8),
        "joint_reduced": (s6, s7, c8),
        "all": (s5, s6, s7, c8),
    }
    targets = tuple(
        sum(int(value) << case for case, value in enumerate(target))
        for target in choices[mode]
    )
    if mode == "joint_reduced":
        # Candidate-oriented interface: retain every already-paid suffix phase
        # but omit the six redundant raw operand bits.  This is deliberately
        # a narrower search than ``joint`` and is used only to find a compact
        # shared network before replaying it against the full interface.
        keep = {
            "C5",
            "G5", "Q5", "P5",
            "G6", "Q6", "P6",
            "G7", "Q7", "P7",
            "T", "D", "A", "C7", "T5",
        }
        filtered = [(name, row) for name, row in zip(names, rows, strict=True) if name in keep]
        names = [name for name, _row in filtered]
        rows = [row for _name, row in filtered]
    driven = [bool(transfer[case] or any_generate[case]) for case in range(assignments)]
    return (names, rows, targets, arrivals), driven


def solve(enc, name: str, timeout: float):
    with Solver(name=name, bootstrap_with=enc.cnf) as solver:
        timer = None
        if timeout:
            timer = threading.Timer(timeout, solver.interrupt)
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
    parser.add_argument(
        "--mode",
        choices=(
            "s6", "s7", "s7_np", "c8", "tail", "tail_s6phases", "joint", "joint_reduced", "all"
        ),
        required=True,
    )
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument(
        "--slot0-kind",
        choices=("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH"),
        help="Optional complete-search shard fixing the first component kind.",
    )
    parser.add_argument("--output", type=Path, required=True)
    args_cli = parser.parse_args()
    args_cli.output.parent.mkdir(parents=True, exist_ok=True)
    core = load_core()
    truth, driven = problem(args_cli.mode)
    core["CURRENT_TRUTH"] = truth
    core["CURRENT_C7_DRIVEN"] = driven
    output_count = len(truth[2])
    args = argparse.Namespace(
        interface="s6",
        gate_bound=args_cli.gate_bound,
        max_delay=6,
        components=args_cli.components,
        switches=args_cli.switches,
        xors=args_cli.xors,
        h_arrival=4,
        c5_arrival=4,
        output_deadlines=",".join("6" for _ in range(output_count)),
        solver=args_cli.solver,
        timeout=args_cli.timeout,
        output=args_cli.output,
    )
    started = time.perf_counter()
    enc, state = core["build"](args)
    if args_cli.slot0_kind:
        if not state["kinds"]:
            raise ValueError("--slot0-kind requires at least one component")
        kind = core["G"].KINDS.index(args_cli.slot0_kind)
        enc.cnf.append([state["kinds"][0][kind]])
    answer, model = solve(enc, args.solver, args_cli.timeout)
    status = "sat" if answer is True else "unsat" if answer is False else "unknown"
    payload = {
        "schema": "d6-paid-80-suffix-exact-v1",
        "mode": args_cli.mode,
        "status": status,
        "gate_bound": args_cli.gate_bound,
        "components": args_cli.components,
        "exact_switches": args_cli.switches,
        "exact_xors": args_cli.xors,
        "slot0_kind": args_cli.slot0_kind,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "paid_sources": truth[0],
        "source_arrivals": truth[3],
        "output_deadlines": [6] * output_count,
    }
    if model is not None:
        payload.update(core["decode"](args, state, model))
        payload["verification"] = core["verify"](payload, state)
    args_cli.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in payload if key not in ("network", "paid_sources", "source_arrivals")}, ensure_ascii=False, indent=2))
    return 0 if status != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
