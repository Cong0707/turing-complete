"""Exact joint phase synthesis for the fixed 81/7 bits5..7 carry spine.

The current conflict-safe Manchester/Switch-Z carry network through bit 6 and
the shared ``T5=P5&C5`` term are treated as already paid.  The solver jointly
reconstructs ``S5,S6,S7,C8`` and can therefore discover sharing across the
former bit5:6 and bit7 boundaries.  A nine-gate witness would reduce the
complete adder from 81/7 to 80/7.

Run the ordinary-only boundary first (``--components 9 --switches 0``).  Any
decoded witness must additionally be rejected if an operand bus directly
merges the free resolved ``C7`` source with another source; the upstream net
partition checker cannot identify the internal drivers of a free source.
"""

from __future__ import annotations

from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py"


CUSTOM_TRUTH = r'''
def truth_tables(_interface: str):
    assignments = 128
    independent = [
        [bool((case >> bit) & 1) for case in range(assignments)]
        for bit in range(7)
    ]
    a5, b5, a6, b6, a7, b7, c5 = independent

    def pw(fn, *rows):
        return [bool(fn(*(int(row[i]) for row in rows))) for i in range(assignments)]

    g5 = pw(lambda a, b: a & b, a5, b5)
    q5 = pw(lambda a, b: 1 ^ (a | b), a5, b5)
    p5 = pw(lambda g, q: 1 ^ (g | q), g5, q5)
    g6 = pw(lambda a, b: a & b, a6, b6)
    q6 = pw(lambda a, b: 1 ^ (a | b), a6, b6)
    p6 = pw(lambda g, q: 1 ^ (g | q), g6, q6)
    g7 = pw(lambda a, b: a & b, a7, b7)
    q7 = pw(lambda a, b: 1 ^ (a | b), a7, b7)
    p7 = pw(lambda g, q: 1 ^ (g | q), g7, q7)

    both_p = pw(lambda x, y: x & y, p5, p6)
    phase_d = pw(lambda q, t: 1 ^ (q | t), q6, both_p)
    any_g = pw(lambda x, y: x | y, g5, g6)
    c7 = pw(lambda t, c, a, d: (t & c) | (a & d), both_p, c5, any_g, phase_d)
    t5 = pw(lambda p, c: p & c, p5, c5)
    c6 = pw(lambda g, p, c: g | (p & c), g5, p5, c5)
    c8 = pw(lambda g, p, c: g | (p & c), g7, p7, c7)
    s5 = pw(lambda p, c: p ^ c, p5, c5)
    s6 = pw(lambda p, c: p ^ c, p6, c6)
    s7 = pw(lambda p, c: p ^ c, p7, c7)

    names = [
        "a5", "b5", "a6", "b6", "a7", "b7", "C5",
        "G5", "Q5", "P5", "G6", "Q6", "P6",
        "G7", "Q7", "P7", "T", "D", "G", "C7", "T5",
    ]
    rows = [
        a5, b5, a6, b6, a7, b7, c5,
        g5, q5, p5, g6, q6, p6,
        g7, q7, p7, both_p, phase_d, any_g, c7, t5,
    ]
    targets = []
    for output in (s5, s6, s7, c8):
        packed = 0
        for case, value in enumerate(output):
            packed |= int(value) << case
        targets.append(packed)
    arrivals = {
        "G5": 1, "Q5": 1, "P5": 2,
        "G6": 1, "Q6": 1, "P6": 2,
        "G7": 1, "Q7": 1, "P7": 2,
        "T": 3, "D": 4, "G": 2, "C7": 5, "T5": 5,
        "C5": 4,
    }
    return names, rows, tuple(targets), arrivals
'''


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    begin = text.index("def truth_tables(")
    end = text.index("def weighted_bound", begin)
    text = text[:begin] + CUSTOM_TRUTH + "\n\n" + text[end:]
    text = text.replace(
        '"schema": "exact-paid-gp-ling-pair-v1",',
        '"schema": "exact-suffix567-shared-phase-v1",',
    )
    namespace = {
        "__name__": "__main__",
        "__file__": str(SOURCE),
        "__package__": None,
    }
    try:
        exec(compile(text, str(SOURCE), "exec"), namespace)
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
