"""C7@4 backend after replacing V3/V4 by a paid Q-phase low pair.

The fixed low front costs seven gates and already produces C5@4:

    A34 = G3 | G4                    @2   (1)
    N34 = NOR(Q3,Q4)                 @2   (1)
    V34 = G4 | N34                   @3   (1)
    C5  = BUS(SW(A34,V34), SW(C3,V34)) @4 (4)

This deletes the V3/V4 leaves but makes V34 one step later.  The exact search
therefore rebuilds C7 directly from this Q-phase front and the fixed fast
AV56 boundary.  Backend cost <=12 gives a complete middle residual <=19 and
thus a <=96/6 adder.  C3 and V56 retain their exact three-state driven masks.
"""

from __future__ import annotations

from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "exact_paid_physical_search_core.py"


CUSTOM_TRUTH = r'''
def truth_tables(interface: str):
    high_states = (
        (False, False, False),
        (True, True, True),
        (False, False, True),
        (False, True, True),
        (True, False, True),
    )
    carry_states = ((False, False), (False, True), (True, True))
    cases = []
    for bits in range(16):
        raw = tuple(bool((bits >> bit) & 1) for bit in range(4))
        for c3_value, c3_driven in carry_states:
            for a56, v56, v56_driven in high_states:
                cases.append((*raw, c3_value, c3_driven, a56, v56, v56_driven))
    assignments = len(cases)
    columns = [[case[column] for case in cases] for column in range(9)]
    a3, b3, a4, b4, c3, c3_driven, a56, v56, v56_driven = columns

    def pw(fn, *args):
        return [
            bool(fn(*(int(row[case]) for row in args)))
            for case in range(assignments)
        ]

    def bit(a, b):
        g = pw(lambda x, y: x & y, a, b)
        q = pw(lambda x, y: 1 ^ (x | y), a, b)
        p = pw(lambda x, y: 1 ^ (x | y), g, q)
        return g, q, p

    g3, q3, p3 = bit(a3, b3)
    g4, q4, p4 = bit(a4, b4)
    a34 = pw(lambda x, y: x | y, g3, g4)
    n34 = pw(lambda x, y: 1 ^ (x | y), q3, q4)
    v34 = pw(lambda g, n: g | n, g4, n34)
    a36 = pw(lambda x, y: x | y, a34, a56)
    v36 = pw(lambda vh, ah, vl: vh & (ah | vl), v56, a56, v34)
    c7 = pw(lambda v, a, c: v & (a | c), v36, a36, c3)

    names = [
        "a3", "b3", "a4", "b4", "C3",
        "G3", "Q3", "P3", "G4", "Q4", "P4",
        "A34", "N34", "V34", "A56", "V56",
    ]
    rows = [
        a3, b3, a4, b4, c3,
        g3, q3, p3, g4, q4, p4,
        a34, n34, v34, a56, v56,
    ]

    def pack(row):
        return sum(int(value) << case for case, value in enumerate(row))

    arrivals = {
        "C3": 3,
        "G3": 1, "Q3": 1, "P3": 2,
        "G4": 1, "Q4": 1, "P4": 2,
        "A34": 2, "N34": 2, "V34": 3,
        "A56": 2, "V56": 2,
    }
    global CUSTOM_SOURCE_DRIVENS
    CUSTOM_SOURCE_DRIVENS = {"C3": c3_driven, "V56": v56_driven}
    return names, rows, (pack(c7),), arrivals
'''


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    begin = text.index("def truth_tables(")
    end = text.index("def weighted_bound", begin)
    text = text[:begin] + CUSTOM_TRUTH + "\n\n" + text[end:]
    text = text.replace(
        'choices=("single", "dual", "s2", "s4", "s6", "bit56", "tail7dual"),',
        'choices=("c7_after_q34",),',
    )
    old_z = '''    allow_z_false_outputs = tuple(
        args.interface == "bit56" and output == 2 for output in range(len(targets))
    )'''
    text = text.replace(old_z, "    allow_z_false_outputs = (True,)")
    text = text.replace(
        '"schema": "exact-paid-gp-ling-pair-v1",',
        '"schema": "exact-97d6-c7-after-q34-v1",',
    )
    old_drivens = "    drivens: list[list[object]] = [[True] * assignments for _ in values]"
    new_drivens = '''    drivens: list[list[object]] = [[True] * assignments for _ in values]
    for source_name, source_mask in CUSTOM_SOURCE_DRIVENS.items():
        drivens[names.index(source_name)] = list(source_mask)'''
    if old_drivens not in text:
        raise RuntimeError("source driven-mask anchor changed")
    text = text.replace(old_drivens, new_drivens)
    namespace = {"__name__": "__main__", "__file__": str(SOURCE), "__package__": None}
    try:
        exec(compile(text, str(SOURCE), "exec"), namespace)
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
