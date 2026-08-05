"""Probe the four-ordinary-gate S5 topology visible in Patchouli's 84/6 image.

This is a deliberately small architecture decoder, not a general circuit
enumerator.  It checks the single topology read directly from the screenshot:

    OR(AND(NOR(e, f), b), NOR(c, d))

Only already-visible/paid rails from the C4/C6 boundary are admitted, and
arrival constraints are enforced before a formula is reported.
"""

from __future__ import annotations

from itertools import combinations_with_replacement, product


def main() -> None:
    rows: list[dict[str, int]] = []
    for c2, g2, q2, g3, q3, g4, q4, g5, q5 in product((0, 1), repeat=9):
        # Legal bit-state rows only: exactly one of K/P/G.  Q and G cannot
        # overlap; P is the remaining state.
        if g2 & q2 or g3 & q3 or g4 & q4 or g5 & q5:
            continue
        p2 = 1 ^ g2 ^ q2
        p3 = 1 ^ g3 ^ q3
        p4 = 1 ^ g4 ^ q4
        p5 = 1 ^ g5 ^ q5
        v4 = g4 | p4
        v5 = g5 | p5
        b23 = (1 ^ (q2 | q3)) & (c2 | g2)
        c4 = g3 | b23
        c5 = g4 | (p4 & c4)
        c6 = g5 | (p5 & c5)
        rows.append(
            {
                "C2": c2,
                "G2": g2,
                "Q2": q2,
                "P2": p2,
                "G3": g3,
                "Q3": q3,
                "P3": p3,
                "G4": g4,
                "Q4": q4,
                "P4": p4,
                "V4": v4,
                "G5": g5,
                "Q5": q5,
                "P5": p5,
                "V5": v5,
                "B23": b23,
                "C4": c4,
                "C5": c5,
                "C6": c6,
                "K34": g3 | g4,
                "G345": g3 | g4 | g5,
                "V45": v4 & v5,
                "D45": g5 | (v4 & v5),
                "S5": p5 ^ c5,
            }
        )

    # The direct screenshot reconstruction supplied by the fixed topology is:
    #
    #   U45 = B23 OR K34
    #   H5  = NOR(Q4,P5)
    #   T5  = U45 AND H5
    #   J5  = NOR(Q5,C6)
    #   S5  = T5 OR J5
    #
    # Verify it before running the intentionally broader diagnostic probes.
    exact_mismatch = 0
    for row in rows:
        u45 = row["B23"] | row["K34"]
        h5 = 1 ^ (row["Q4"] | row["P5"])
        t5 = u45 & h5
        j5 = 1 ^ (row["Q5"] | row["C6"])
        exact_mismatch += (t5 | j5) != row["S5"]
    print(f"exact_patchouli_s5_mismatch={exact_mismatch}")

    arrivals = {
        "C2": 2,
        "G2": 1,
        "Q2": 1,
        "P2": 2,
        "G3": 1,
        "Q3": 1,
        "P3": 2,
        "G4": 1,
        "Q4": 1,
        "P4": 2,
        "V4": 1,
        "G5": 1,
        "Q5": 1,
        "P5": 2,
        "V5": 1,
        "B23": 3,
        "C4": 4,
        "C5": 5,  # Not actually available this early; retained as a control.
        "C6": 4,
        "K34": 2,
        "G345": 3,
        "V45": 2,
        "D45": 3,
    }
    names = tuple(arrivals)

    # First test the visible S1-style four-gate closure around a single paid
    # early carry-reason X:
    #
    #   OR(AND(G5,X), NOR(NOR(X,V5),C6))
    #
    # X may be a visible source rail or one ordinary gate over D2 rails.
    vectors = {name: tuple(row[name] for row in rows) for name in names}
    early = [name for name in names if arrivals[name] <= 2]
    x_candidates: dict[tuple[int, ...], str] = {
        vectors[name]: name for name in names if arrivals[name] <= 3
    }
    for left, right in combinations_with_replacement(early, 2):
        lv = vectors[left]
        rv = vectors[right]
        for op in ("AND", "OR", "NAND", "NOR"):
            if op == "AND":
                value = tuple(a & b for a, b in zip(lv, rv, strict=True))
            elif op == "OR":
                value = tuple(a | b for a, b in zip(lv, rv, strict=True))
            elif op == "NAND":
                value = tuple(1 ^ (a & b) for a, b in zip(lv, rv, strict=True))
            else:
                value = tuple(1 ^ (a | b) for a, b in zip(lv, rv, strict=True))
            x_candidates.setdefault(value, f"{op}({left},{right})")

    direct_hits: list[str] = []
    for vector, label in x_candidates.items():
        ok = True
        for index, row in enumerate(rows):
            x = vector[index]
            result = (row["G5"] & x) | (
                1 ^ ((1 ^ (x | row["V5"])) | row["C6"])
            )
            if result != row["S5"]:
                ok = False
                break
        if ok:
            direct_hits.append(label)
    print(f"s1_style_x_hits={len(direct_hits)}")
    for label in direct_hits:
        print(f"X={label}")

    pairs_d3 = [
        pair
        for pair in combinations_with_replacement(names, 2)
        if max(arrivals[pair[0]], arrivals[pair[1]]) + 1 <= 4
    ]
    pairs_d4 = [
        pair
        for pair in combinations_with_replacement(names, 2)
        if max(arrivals[pair[0]], arrivals[pair[1]]) + 1 <= 5
    ]
    b_inputs = [name for name in names if arrivals[name] <= 4]

    hits: list[tuple[str, str, str, str, str]] = []
    for e, f in pairs_d3:
        for b in b_inputs:
            for c, d in pairs_d4:
                ok = True
                for row in rows:
                    n0 = 1 ^ (row[e] | row[f])
                    a0 = n0 & row[b]
                    n1 = 1 ^ (row[c] | row[d])
                    if (a0 | n1) != row["S5"]:
                        ok = False
                        break
                if ok:
                    hits.append((e, f, b, c, d))

    print(f"legal_rows={len(rows)}")
    print(f"hits={len(hits)}")
    for hit in hits[:200]:
        print("S5 = OR(AND(NOR(%s,%s),%s), NOR(%s,%s))" % hit)


if __name__ == "__main__":
    main()
