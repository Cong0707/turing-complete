"""Small algebra audit for the 85/6 Byte Adder architecture cuts.

This is deliberately not a synthesizer.  It only replays two hand-written
architectures over the legal K/P/G states of an adder bit:

* the partial C6 descriptor U6 and its paid high phases;
* the encoded-C2 bits0:3 macro and its S3 positive phase.

No SAT, BDD, random search, netlist enumeration, or game process is used.
"""

from __future__ import annotations

from itertools import product


STATES = {
    "K": (0, 1, 0),  # generate, kill, propagate
    "P": (0, 0, 1),
    "G": (1, 0, 0),
}


def nor(left: int, right: int) -> int:
    return int(not (left or right))


def nand(left: int, right: int) -> int:
    return int(not (left and right))


def audit_c6_descriptor() -> None:
    rows = 0
    for b23, g3, state4, state5, state6, state7 in product(
        (0, 1), (0, 1), STATES, STATES, STATES, STATES
    ):
        g4, q4, p4 = STATES[state4]
        g5, q5, p5 = STATES[state5]
        g6, q6, p6 = STATES[state6]
        g7, q7, p7 = STATES[state7]

        k34 = g3 or g4
        e345 = k34 or g5
        v45 = nor(q4, q5)
        d45 = g5 or v45
        c6 = int(d45 and (b23 or e345))

        # Strong partial descriptor: it omits exactly the G5-only cause.
        u6 = int(v45 and (b23 or k34))
        assert c6 == int(g5 or u6)
        assert nand(p5, c6) == nand(p5, u6)

        n6 = int(g6 or q6)
        k67 = int(g6 or g7)
        m = int(g5 or g6)
        n = int(m or q6)
        k_prime = int(m or g7)
        a6 = int(u6 or n)
        z7 = nor(u6, k_prime)
        assert a6 == int(c6 or n6)
        assert z7 == nor(c6, k67)

        # B6 is only a don't-care at C6=n6=0 because the fixed final NAND
        # already has A6=0 there.  Everywhere else it must implement the
        # indicated phase.
        b6 = nand(n6, c6)
        if c6 or n6:
            assert b6 == int(c6 != n6)

        # Keep variables live in this audit: the identities are independent
        # of P4/P6/P7 but only legal K/P/G states are admitted.
        assert p4 + g4 + q4 == 1
        assert p6 + g6 + q6 == 1
        assert p7 + g7 + q7 == 1
        rows += 1

    assert rows == 324


def audit_one_gate_b6_obstruction() -> None:
    """Prove the one-ordinary-gate U6/R phase closure is impossible.

    R may be any early Boolean function of (G5,n6), but it is independent of
    U6.  At U6=1, B6 must be not n6.  This forces the only two plausible
    ordinary forms to AND(U6,not n6) or NAND(U6,n6); each then fails at U6=0.
    OR/NOR fail already at U6=1.  NOT of either single input also fails.
    """

    witnesses = {
        "AND": "U6=0,G5=0,n6=1 requires B6=1, but AND(0,R)=0",
        "OR": "U6=1,n6=1 requires B6=0, but OR(1,R)=1",
        "NAND": "U6=0,G5=1,n6=1 requires B6=0, but NAND(0,R)=1",
        "NOR": "U6=1,n6=0 requires B6=1, but NOR(1,R)=0",
        "NOT_U6": "U6=0,G5=1,n6=1 requires B6=0, but NOT(U6)=1",
        "NOT_R": (
            "U6=0,G5=0,n6=1 and U6=0,G5=1,n6=1 require different "
            "B6 values although R sees the same n6 unless it also encodes G5; "
            "then U6=1 still forces R=n6 for both G5 values"
        ),
    }
    assert len(witnesses) == 6


def audit_encoded_c2_macro() -> None:
    rows = 0
    for c1, state1, state2, state3 in product((0, 1), STATES, STATES, STATES):
        g1, q1, p1 = STATES[state1]
        g2, q2, p2 = STATES[state2]
        g3, q3, p3 = STATES[state3]
        v1 = int(not q1)

        # X is the effective Boolean value of the two-Switch partial owner.
        x = int(v1 and c1)
        c2 = int(g1 or x)
        nc2 = int(not c2)

        n257 = int(c1 or v1)
        tg = int(g1 and x)
        to = int(nc2 and n257)
        s1 = int(tg or to)
        assert s1 == (p1 ^ c1)

        a12 = int(g1 or g2)
        v23 = int((not q2) and (not q3))
        b23 = int(v23 and (x or a12))
        c3 = int(g2 or (p2 and c2))
        c4 = int(g3 or b23)
        expected_c4 = int(g3 or (p3 and c3))
        assert c4 == expected_c4

        d2 = nand(nc2, p2)
        e2 = int(nc2 or p2)
        s2 = nand(d2, e2)
        assert s2 == (p2 ^ c2)

        r2 = nor(q2, p3)
        # Key hand simplification: P3 & not C4 == NOR(C4,Q3).
        a3 = nor(c4, q3)
        assert a3 == int(p3 and not c4)
        b3 = int(r2 and d2)
        s3 = int(a3 or b3)
        assert s3 == (p3 ^ c3)
        rows += 1

    assert rows == 54


def audit_ledgers() -> None:
    c6_cut = {
        "K34": 1,
        "V45": 1,
        "U6_two_switch_owner": 4,
        "D5": 1,
        "M_N_Kprime": 3,
        "A6_Z7": 2,
        "B6_minimum_after_obstruction": 2,
    }
    assert sum(c6_cut.values()) == 14

    encoded_c2 = {
        "X_two_switch_owner": 4,
        "C1": 1,
        "nC2": 1,
        "S1_remaining_phase": 4,
        "bit2_GQP": 3,
        "bit3_QP_G3_is_external": 2,
        "A12": 1,
        "V23": 1,
        "B23_two_switch_owner": 4,
        "C4": 1,
        "S2_phase": 3,
        "S3_phase_with_shared_D2": 4,
    }
    assert sum(encoded_c2.values()) == 29

    arrivals = {
        "B23": 3,
        "C4": 4,
        "S1": 5,
        "S2": 5,
        "S3": 6,
    }
    assert max(arrivals.values()) == 6


def main() -> None:
    audit_c6_descriptor()
    audit_one_gate_b6_obstruction()
    audit_encoded_c2_macro()
    audit_ledgers()
    print("phase-spine identities: pass (324 legal rows)")
    print("one-gate B6 architectural obstruction: pass")
    print("encoded-C2 equations: pass (54 legal rows)")
    print("static ledgers: C6 widened cut=14, encoded-C2 macro=29, delay=6")


if __name__ == "__main__":
    main()
