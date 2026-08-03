"""Exact joint resynthesis of the current 80/7 S1 and S2 private cone.

Cutting outputs S1 and S2 from the reviewed 80/7 DAG removes ten gates:
nodes 23, 24, 52, 53, 76--81.  This wrapper exposes only signals which stay
live outside that cut and asks whether both sums fit in a cheaper weighted
network.  The first run uses nine ordinary gates; later runs may enumerate
the exact cost-nine Switch/XOR decompositions with the same model.

The source is deliberately generated from the already reviewed exact
tri-state/physical-net SAT core.  This script is offline only and never reads
or writes the game save.
"""

from __future__ import annotations

from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py"


CUSTOM_TRUTH = r'''
def truth_tables(interface: str):
    # C1 is the carry from bit 0.  Together with bits 1 and 2 it spans the
    # complete correlated domain needed by this cut.  G1 is retained by the
    # rest of the DAG; G2/V2 and C3 are likewise already-paid boundary nodes.
    assignments = 32
    independent = [
        [bool((case >> bit) & 1) for case in range(assignments)]
        for bit in range(5)
    ]
    a1, b1, a2, b2, c1 = independent

    def pw(fn, *rows):
        return [
            bool(fn(*(int(row[case]) for row in rows)))
            for case in range(assignments)
        ]

    g1 = pw(lambda a, b: a & b, a1, b1)
    p1 = pw(lambda a, b: a ^ b, a1, b1)
    c2 = pw(lambda g, p, c: g | (p & c), g1, p1, c1)
    s1 = pw(lambda p, c: p ^ c, p1, c1)

    g2 = pw(lambda a, b: a & b, a2, b2)
    v2 = pw(lambda a, b: a | b, a2, b2)
    p2 = pw(lambda a, b: a ^ b, a2, b2)
    c3 = pw(lambda g, p, c: g | (p & c), g2, p2, c2)
    s2 = pw(lambda p, c: p ^ c, p2, c2)

    names = ["a1", "b1", "G1", "G2", "V2", "C1", "C3"]
    rows = [a1, b1, g1, g2, v2, c1, c3]

    def pack(row):
        return sum(int(value) << case for case, value in enumerate(row))

    arrivals = {
        "a1": 0,
        "b1": 0,
        "G1": 1,
        "G2": 1,
        "V2": 1,
        "C1": 2,
        "C3": 3,
    }
    return names, rows, (pack(s1), pack(s2)), arrivals
'''


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    begin = text.index("def truth_tables(")
    end = text.index("def weighted_bound", begin)
    text = text[:begin] + CUSTOM_TRUTH + "\n\n" + text[end:]
    text = text.replace(
        'choices=("single", "dual", "s2", "s4", "s6", "bit56", "tail7dual"),',
        'choices=("s1_s2_current80",),',
    )
    text = text.replace(
        '"schema": "exact-paid-gp-ling-pair-v1",',
        '"schema": "exact-80d7-s1-s2-joint-v1",',
    )
    text = text.replace(
        '    parser.add_argument("--solver", default="cadical195")',
        '    parser.add_argument("--last-output", type=int, choices=(0, 1))\n'
        '    parser.add_argument("--other-output-gate", type=int)\n'
        '    parser.add_argument("--other-output-kind", choices=("NOT", "AND", "OR", "NAND", "NOR"))\n'
        '    parser.add_argument("--solver", default="cadical195")',
    )
    text = text.replace(
        "    enc, state = build(args)\n    timer = None",
        "    enc, state = build(args)\n"
        "    if args.last_output is not None:\n"
        "        last_source = int(state['source_count']) + args.components - 1\n"
        "        enc.force(state['output_uses'][args.last_output][last_source], True)\n"
        "    if args.other_output_gate is not None:\n"
        "        if args.last_output != 1:\n"
        "            raise ValueError('--other-output-gate requires --last-output 1')\n"
        "        if not 0 <= args.other_output_gate < args.components - 1:\n"
        "            raise ValueError('--other-output-gate must name a non-final gate')\n"
        "        source = int(state['source_count']) + args.other_output_gate\n"
        "        enc.force(state['output_uses'][0][source], True)\n"
        "    if args.other_output_kind is not None:\n"
        "        if args.other_output_gate is None:\n"
        "            raise ValueError('--other-output-kind requires --other-output-gate')\n"
        "        kind = G.KINDS.index(args.other_output_kind)\n"
        "        enc.force(state['kinds'][args.other_output_gate][kind], True)\n"
        "    timer = None",
    )
    text = text.replace(
        '        "physical_nets": True,',
        '        "physical_nets": True,\n'
        '        "last_output_shard": args.last_output,\n'
        '        "other_output_gate_shard": args.other_output_gate,\n'
        '        "other_output_kind_shard": args.other_output_kind,',
    )
    namespace = {"__name__": "__main__", "__file__": str(SOURCE), "__package__": None}
    try:
        exec(compile(text, str(SOURCE), "exec"), namespace)
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
