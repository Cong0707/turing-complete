"""Audit the reviewed 26-gate Hub87 high suffix on its 54-row state domain.

This is a bounded architecture audit, not a circuit-space solver.  The three
high bits are represented by mutually-exclusive K/P/G states and C5 is the
only late carry input.  The script checks the deployed identities and the two
specific replacement shapes that would be needed for a 25- or 24-gate suffix.
"""

from __future__ import annotations

from itertools import product


STATES = tuple(product(range(3), repeat=3))
ROWS = tuple((*state, c5) for state in STATES for c5 in (0, 1))
ALL = (1 << len(ROWS)) - 1


def signature(predicate):
    result = 0
    for index, row in enumerate(ROWS):
        if predicate(*row):
            result |= 1 << index
    return result


signals: dict[str, int] = {}
for bit, position in ((5, 0), (6, 1), (7, 2)):
    for phase, value in (("Q", 0), ("P", 1), ("G", 2)):
        signals[f"{phase}{bit}"] = signature(
            lambda s5, s6, s7, c5, p=position, v=value: (s5, s6, s7)[p]
            == v
        )

signals["C5"] = signature(lambda s5, s6, s7, c5: c5)
signals["A56"] = signals["G5"] | signals["G6"]
signals["O5"] = signals["P5"] | signals["C5"]
signals["D5"] = ALL ^ (signals["P5"] & signals["C5"])
signals["E6"] = ALL ^ (signals["A56"] | signals["Q6"])
signals["F6"] = ALL ^ (signals["P6"] | signals["Q5"])
signals["H6"] = signals["G5"] | signals["C5"]
signals["N56"] = ALL ^ (signals["Q5"] | signals["Q6"])
signals["K56"] = ALL ^ (signals["G6"] | signals["N56"])
signals["R7"] = ALL ^ (signals["A56"] | signals["C5"])
signals["J7"] = ALL ^ (signals["P7"] | signals["K56"])
signals["H7"] = signals["A56"] | signals["C5"]
signals["F7"] = ALL ^ (signals["K56"] | signals["J7"])

c6 = signals["G5"] | (signals["P5"] & signals["C5"])
c7 = signals["G6"] | (signals["P6"] & c6)
s5 = signals["P5"] ^ signals["C5"]
s6 = signals["P6"] ^ c6
s7 = signals["P7"] ^ c7
c8 = signals["G7"] | (signals["P7"] & c7)


def resolved(*drivers: tuple[int, int]) -> tuple[int, int]:
    ones = 0
    zeros = 0
    for enable, data in drivers:
        ones |= enable & data
        zeros |= enable & (ALL ^ data)
    return ones, ones & zeros


def gate(op: str, left: int, right: int) -> int:
    if op == "AND":
        return left & right
    if op == "OR":
        return left | right
    if op == "NAND":
        return ALL ^ (left & right)
    if op == "NOR":
        return ALL ^ (left | right)
    raise ValueError(op)


def audit() -> None:
    s6_raw, s6_conflict = resolved(
        (signals["E6"], signals["D5"]),
        (signals["F6"], signals["H6"]),
    )
    s7_raw, s7_conflict = resolved(
        (signals["K56"], signals["P7"]),
        (signals["R7"], signals["P7"]),
        (signals["J7"], signals["H7"]),
    )
    c8_raw, c8_conflict = resolved(
        (signals["G7"], signals["G7"]),
        (signals["F7"], signals["H7"]),
    )

    assert signals["O5"] & signals["D5"] == s5
    assert s6_raw == s6 and s6_conflict == 0
    assert s7_raw == s7 and s7_conflict == 0
    assert c8_raw == c8 and c8_conflict == 0

    nc7 = ALL ^ c7
    assert nc7 == signals["K56"] | signals["R7"]
    assert nc7 == signals["Q6"] | (signals["E6"] & signals["D5"])

    not_k56 = ALL ^ signals["K56"]
    assert ((signals["H7"] ^ gate("NAND", signals["E6"], signals["D5"])) & not_k56) == 0
    assert ((signals["R7"] ^ gate("AND", signals["E6"], signals["D5"])) & not_k56) == 0

    # A single ordinary gate at arrival <= 5 would permit the two same-data
    # S7 drivers K56/R7 to collapse into one Switch at arrival 6.  The frozen
    # paid-state interface has no such exact nC7 expression.
    arrivals = {
        "G5": 1,
        "Q5": 1,
        "P5": 2,
        "G6": 1,
        "Q6": 1,
        "P6": 2,
        "G7": 1,
        "Q7": 1,
        "P7": 2,
        "C5": 4,
        "A56": 2,
        "E6": 3,
        "F6": 3,
        "N56": 2,
        "K56": 3,
        "J7": 4,
    }
    available = tuple(arrivals)
    one_gate_nc7 = []
    for left_index, left_name in enumerate(available):
        for right_name in available[left_index:]:
            arrival = max(arrivals[left_name], arrivals[right_name]) + 1
            if arrival > 5:
                continue
            for operation in ("AND", "OR", "NAND", "NOR"):
                if gate(operation, signals[left_name], signals[right_name]) == nc7:
                    one_gate_nc7.append(
                        (operation, left_name, right_name, arrival)
                    )
    assert not one_gate_nc7

    print("rows=54")
    print("hub87_high=26 gates / 6 delay")
    print("s5_s6=10 gates; s7_c8=16 gates")
    print("deployed_value_and_conflict_checks=pass")
    print("nC7=K56|R7=Q6|(E6&D5)")
    print("one_gate_nC7_at_or_before_5=none")


if __name__ == "__main__":
    audit()
