"""Exact C3/C5/C7@4 retiming across the paid Q12/Q34/AV56 boundary.

The 91/7 reference already pays for ``A12,N12,A34,N34,A56,V56`` and the
single-bit generators needed to reconstruct both Q valency rails::

    V12 = G2 | N12
    V34 = G4 | N34

Its remaining carry spine costs 21 gates but reaches C5/C7 at arrival 5.
This model asks whether no more than 23 residual gates can jointly expose all
three positive carry rails at arrival 4.  False carries may be Z; true carries
must be actively driven.  C1 and V56 are supplied with their exact possible
active-zero/Z masks, and the imported encoder enforces physical resolved-net
partitioning.

The script is offline only and never touches the live save.
"""

from __future__ import annotations

from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "byte_adder_pair_macro_exact/exact_paid_physical_search_core.py"


CUSTOM_TRUTH = r'''
def truth_tables(interface: str):
    bit_states = (
        (False, True),   # K: G=0,Q=1
        (False, False),  # P: G=0,Q=0
        (True, False),   # G: G=1,Q=0
    )
    carry_states = ((False, False), (False, True), (True, True))
    high_states = (
        (False, False, False),
        (False, False, True),
        (False, True, True),
        (True, False, True),
        (True, True, True),
    )

    # Quotient raw input assignments by every value and driven mask visible
    # at this paid interface.  This preserves the complete reachable domain
    # while reducing 1215 state combinations to 540 distinct rows.
    cases = set()
    for c1, c1_driven in carry_states:
        for g1, q1 in bit_states:
            for g2, q2 in bit_states:
                a12 = g1 or g2
                n12 = not (q1 or q2)
                v12 = g2 or n12
                c3 = v12 and (a12 or c1)
                for g3, q3 in bit_states:
                    for g4, q4 in bit_states:
                        a34 = g3 or g4
                        n34 = not (q3 or q4)
                        v34 = g4 or n34
                        c5 = v34 and (a34 or c3)
                        for a56, v56, v56_driven in high_states:
                            c7 = v56 and (a56 or c5)
                            cases.add((
                                c1, c1_driven,
                                a12, n12, g2,
                                a34, n34, g4,
                                a56, v56, v56_driven,
                                c3, c5, c7,
                            ))
    cases = sorted(cases)
    requested_rows = __import__("os").environ.get("TC_Q12_Q34_ROWS")
    if requested_rows:
        selected = tuple(sorted({int(item) for item in requested_rows.split(",")}))
        if not selected or selected[0] < 0 or selected[-1] >= len(cases):
            raise ValueError(f"invalid TC_Q12_Q34_ROWS={requested_rows!r}")
    else:
        selected = tuple(range(len(cases)))
    global CUSTOM_CASE_INDICES
    CUSTOM_CASE_INDICES = selected
    cases = [cases[index] for index in selected]
    columns = [[bool(case[column]) for case in cases] for column in range(14)]
    (
        c1, c1_driven,
        a12, n12, g2,
        a34, n34, g4,
        a56, v56, v56_driven,
        c3, c5, c7,
    ) = columns
    names = ["C1", "A12", "N12", "G2", "A34", "N34", "G4", "A56", "V56"]
    rows = [c1, a12, n12, g2, a34, n34, g4, a56, v56]

    def pack(row):
        return sum(int(value) << case for case, value in enumerate(row))

    arrivals = {
        "C1": 2,
        "A12": 2, "N12": 2, "G2": 1,
        "A34": 2, "N34": 2, "G4": 1,
        "A56": 2, "V56": 2,
    }
    global CUSTOM_SOURCE_DRIVENS
    CUSTOM_SOURCE_DRIVENS = {"C1": c1_driven, "V56": v56_driven}
    return names, rows, (pack(c3), pack(c5), pack(c7)), arrivals
'''


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    begin = text.index("def truth_tables(")
    end = text.index("def weighted_bound", begin)
    text = text[:begin] + CUSTOM_TRUTH + "\n\n" + text[end:]
    text = text.replace(
        'choices=("single", "dual", "s2", "s4", "s6", "bit56", "tail7dual"),',
        'choices=("q12_q34_carry_retime",),',
    )
    text = text.replace(
        '''    allow_z_false_outputs = tuple(
        args.interface == "bit56" and output == 2 for output in range(len(targets))
    )''',
        "    allow_z_false_outputs = (True, True, True)",
    )
    text = text.replace(
        '"schema": "exact-paid-gp-ling-pair-v1",',
        '"schema": "exact-q12-q34-carry-retime-v1",',
    )
    text = text.replace(
        '"schema": "exact-q12-q34-carry-retime-v1",',
        '"schema": "exact-q12-q34-carry-retime-v1",\n        "case_indices": CUSTOM_CASE_INDICES,',
    )
    # The generic core exposes conceptual 0/1 rails for optimistic lower-bound
    # work.  They are not free physical components in Byte Adder, so remove
    # them from this constructive search.  A witness therefore maps directly
    # to paid ordinary/XOR/Switch components without a hidden constant source.
    constant_anchor = '''    source_values.extend(([False] * assignments, [True] * assignments))
    names.extend(("0", "1"))'''
    if constant_anchor not in text:
        raise RuntimeError("constant-source anchor changed")
    text = text.replace(constant_anchor, "")
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
