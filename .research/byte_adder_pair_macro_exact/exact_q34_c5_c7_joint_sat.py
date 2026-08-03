"""Exact C5@4/C7@4 synthesis from paid bit-3:4 Q leaves and AV56.

This crosses the previous Q-front/backend boundary.  A34, N34 and V34 are
not free sources: the current 95/6 witness must pay for them inside the search.
C3 and V56 retain exact three-state driven masks, and both false carry outputs
may legally be represented by Z.  The imported encoder enforces complete
physical resolved-net partitions.
"""

from __future__ import annotations

from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "exact_paid_physical_search_core.py"


CUSTOM_TRUTH = r'''
def truth_tables(interface: str):
    high_states = (
        (False, False, False),
        (True,  True,  True),
        (False, False, True),
        (False, True,  True),
        (True,  False, True),
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
    c5 = pw(lambda v, a, c: v & (a | c), v34, a34, c3)
    c7 = pw(lambda v, a, c: v & (a | c), v56, a56, c5)

    names = [
        "a3", "b3", "a4", "b4", "C3",
        "G3", "Q3", "P3", "G4", "Q4", "P4",
        "A56", "V56",
    ]
    rows = [
        a3, b3, a4, b4, c3,
        g3, q3, p3, g4, q4, p4,
        a56, v56,
    ]

    def pack(row):
        return sum(int(value) << case for case, value in enumerate(row))

    arrivals = {
        "C3": 3,
        "G3": 1, "Q3": 1, "P3": 2,
        "G4": 1, "Q4": 1, "P4": 2,
        "A56": 2, "V56": 2,
    }
    global CUSTOM_SOURCE_DRIVENS
    CUSTOM_SOURCE_DRIVENS = {"C3": c3_driven, "V56": v56_driven}
    return names, rows, (pack(c5), pack(c7)), arrivals
'''


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    begin = text.index("def truth_tables(")
    end = text.index("def weighted_bound", begin)
    text = text[:begin] + CUSTOM_TRUTH + "\n\n" + text[end:]
    text = text.replace(
        'choices=("single", "dual", "s2", "s4", "s6", "bit56", "tail7dual"),',
        'choices=("q34_c5_c7",),',
    )
    old_z = '''    allow_z_false_outputs = tuple(
        args.interface == "bit56" and output == 2 for output in range(len(targets))
    )'''
    text = text.replace(old_z, "    allow_z_false_outputs = (True, True)")
    text = text.replace(
        '"schema": "exact-paid-gp-ling-pair-v1",',
        '"schema": "exact-q34-c5-c7-joint-v1",',
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
