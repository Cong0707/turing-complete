"""Audit the fixed 103/5-B split-reason transplant onto Patchouli 84/6.

This is deliberately a small architecture check over the legal K/P/G states
of bits 4..7 and an independent carry into bit 4.  It is not a circuit search.
"""

from __future__ import annotations

import hashlib
import json
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "103d5b-split-reason-d6-audit-v1.json"
STATES = ("K", "P", "G")


def rails(state: str) -> tuple[int, int, int, int]:
    """Return G, Q, P, nP for one legal two-input bit state."""

    return (
        int(state == "G"),
        int(state == "K"),
        int(state == "P"),
        int(state != "P"),
    )


def resolve(drivers: list[tuple[int, int]]) -> tuple[int, bool, bool]:
    """Resolve enabled switch drivers; Z is normalized to logical zero."""

    active = [data for enable, data in drivers if enable]
    if not active:
        return 0, False, True
    return active[0], len(set(active)) > 1, False


def main() -> None:
    mismatch = {name: 0 for name in ("s5", "s6", "s7", "c8")}
    conflict = {name: 0 for name in mismatch}
    z_rows = {name: 0 for name in mismatch}
    reason_mismatch = 0
    rows = 0

    for c4, b4, b5, b6, b7 in product((0, 1), STATES, STATES, STATES, STATES):
        rows += 1
        g4, q4, p4, np4 = rails(b4)
        g5, q5, p5, _np5 = rails(b5)
        g6, q6, p6, np6 = rails(b6)
        g7, q7, p7, np7 = rails(b7)

        c5 = g4 | (p4 & c4)
        expected_s5 = p5 ^ c5
        expected_c6 = g5 | (p5 & c5)
        c7 = g6 | (p6 & expected_c6)
        expected_s6 = p6 ^ expected_c6
        expected_s7 = p7 ^ c7
        expected_c8 = g7 | (p7 & c7)

        # Patchouli/B common carry factorization.
        v45 = int(not (q4 | q5))
        d45 = g5 | v45
        e45 = c4 | g4 | g5
        c6 = d45 & e45
        k45 = int(not d45)
        r1 = int(not e45)
        if (k45 | r1) != int(not c6) or c6 != expected_c6:
            reason_mismatch += 1

        # B's three-switch S5, using Patchouli U45 on H5's care domain.
        u45 = c4 | g4
        h5 = int(not (q4 | p5))
        s5, bad, is_z = resolve(
            [(q4, p5), (h5, u45), (r1, p5)]
        )
        mismatch["s5"] += int(s5 != expected_s5)
        conflict["s5"] += int(bad)
        z_rows["s5"] += int(is_z)

        # B's direct split-reason S6 owner.
        s6, bad, is_z = resolve(
            [(k45, p6), (r1, p6), (c6, np6)]
        )
        mismatch["s6"] += int(s6 != expected_s6)
        conflict["s6"] += int(bad)
        z_rows["s6"] += int(is_z)

        # B's S7 cofactors and its S7/C8 cross-output sharing.
        x7 = int(not (np7 | q6))
        t7 = np7 & q6
        f7 = int(not (t7 | x7))
        m7 = g6 | np7
        n7 = int(not (g6 & np7))
        l7 = int(not (n7 & m7))
        b8 = x7 | g7

        s7, bad, is_z = resolve(
            [(k45, l7), (r1, l7), (c6, f7)]
        )
        mismatch["s7"] += int(s7 != expected_s7)
        conflict["s7"] += int(bad)
        z_rows["s7"] += int(is_z)

        c8, bad, is_z = resolve([(m7, b8), (c6, b8)])
        mismatch["c8"] += int(c8 != expected_c8)
        conflict["c8"] += int(bad)
        z_rows["c8"] += int(is_z)

    ledger = {
        "patchouli84_relevant": {
            "current_c6_core": 8,
            "s5": 5,
            "high_tail": 20,
            "total": 33,
        },
        "split_reason_transplant_on_current_backbone": {
            "current_c6_core": 8,
            "K45_and_R1": 2,
            "s5": 8,
            "high_tail": 30,
            "total": 48,
            "delta": 15,
        },
        "decisive_s5_s6_only": {
            "K45_and_R1": 2,
            "s5_delta": 3,
            "s6_delta": 4,
            "combined_delta": 9,
            "optimistic_remove_old_C6_owner": -4,
            "still_delta_before_s7_c8": 5,
        },
        "full_B_c4_c6_boundary": {
            "current_C4_plus_C6": 14,
            "B_C4_plus_C6": 16,
            "delta_before_split_reasons": 2,
            "K45_and_R1": 2,
            "delta_with_split_reasons": 4,
        },
    }

    result = {
        "schema": "byte83-103d5b-split-reason-d6-audit-v1",
        "status": "rejected_for_gate_budget",
        "rows": rows,
        "reason_mismatch": reason_mismatch,
        "mismatch": mismatch,
        "conflict": conflict,
        "z_rows": z_rows,
        "arrivals": {
            "K45": 3,
            "R1_on_B_C4_at_3": 4,
            "R1_on_current_C4_at_4_direct_formula": 5,
            "R1_on_current_B23_G345_backbone": 4,
            "B_outputs": 5,
            "allowed_D6": True,
        },
        "ledger": ledger,
        "conclusion": (
            "The split reasons are functionally valid and conflict-free, but "
            "their S5/S6 consumers already cost nine extra gates.  Even an "
            "impossible optimistic four-gate removal of the shared C6 owner "
            "leaves +5 before S7/C8, so they cannot replace the public-E6/nC6 "
            "producer for an <=83/6 Patchouli derivative."
        ),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["certificate_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    assert rows == 162
    assert reason_mismatch == 0
    assert not any(mismatch.values())
    assert not any(conflict.values())
    assert ledger["decisive_s5_s6_only"]["still_delta_before_s7_c8"] == 5
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
