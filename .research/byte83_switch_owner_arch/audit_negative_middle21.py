"""Deterministic audit for the hand-derived 21-gate negative-carry middle.

This is not a synthesizer or a search program.  It replays the fixed formulas
for bits 4 and 5 over the 18 legal K/P/G x K/P/G x nC4 states and records the
resolved Switch owner state, including active-zero, active-one, Z, overlap,
and conflict counts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "negative-middle21-audit-v1.json"


@dataclass(frozen=True)
class BusState:
    value: int
    driven: int
    conflict: int

    @property
    def z(self) -> int:
        return 1 - self.driven


def resolve(*drivers: tuple[int, int]) -> BusState:
    active = [data for enable, data in drivers if enable]
    if not active:
        return BusState(value=0, driven=0, conflict=0)
    return BusState(
        value=int(any(active)),
        driven=1,
        conflict=int(any(data != active[0] for data in active[1:])),
    )


def state(name: str) -> tuple[int, int, int]:
    # Q/P/G are the carry-kill, propagate, and generate one-hot states.
    return (
        int(name == "Q"),
        int(name == "P"),
        int(name == "G"),
    )


def main() -> int:
    rows: list[dict[str, object]] = []
    for bit4 in ("Q", "P", "G"):
        q4, p4, g4 = state(bit4)
        for bit5 in ("Q", "P", "G"):
            q5, p5, g5 = state(bit5)
            for nc4 in (0, 1):
                c4 = 1 - nc4
                c5 = g4 | (p4 & c4)
                c6 = g5 | (p5 & c5)
                expected_nc6 = 1 - c6

                # Negative group-carry owner.
                r45 = 1 - (q5 | q4)
                k45 = 1 - (g5 | r45)
                p45 = p4 & p5
                nc6 = resolve((k45, 1), (p45, nc4))

                # Consumer-specific negative-phase sums.
                s4_left = 1 - (p4 | nc4)
                s4_right = p4 & nc4
                s4 = s4_left | s4_right

                u45n = 1 - (nc4 & p4)
                h5 = 1 - (q4 | p5)
                t5 = u45n & h5
                j5 = p5 & nc6.value
                s5 = t5 | j5

                nc6_state = asdict(nc6)
                nc6_state["z"] = nc6.z
                row = {
                    "bit4": bit4,
                    "bit5": bit5,
                    "nC4": nc4,
                    "R45": r45,
                    "K45": k45,
                    "P45": p45,
                    "K45_and_P45": k45 & p45,
                    "nC6": nc6_state,
                    "expected_nC6": expected_nc6,
                    "S4": s4,
                    "expected_S4": p4 ^ c4,
                    "U45n": u45n,
                    "H5": h5,
                    "T5": t5,
                    "J5": j5,
                    "S5": s5,
                    "expected_S5": p5 ^ c5,
                }
                assert nc6.value == expected_nc6
                assert not nc6.conflict
                assert not (k45 & p45)
                assert s4 == (p4 ^ c4)
                assert s5 == (p5 ^ c5)
                rows.append(row)

    arrivals = {
        "Q4/G4/Q5/G5": 1,
        "P4/P5": 2,
        "R45": 2,
        "K45/P45": 3,
        "nC4_input": 3,
        "nC6": 4,
        "S4_phase": 4,
        "S4": 5,
        "U45n": 4,
        "H5": 3,
        "T5/J5": 5,
        "S5": 6,
    }
    ledger = {
        "bit4_bit5_QGP_leaves": 6,
        "R45_K45_P45": 3,
        "nC6_two_switch_owner": 4,
        "S4_three_gate_xnor": 3,
        "U45n_H5_T5_J5_S5": 5,
    }
    assert sum(ledger.values()) == 21
    assert max(arrivals["S4"], arrivals["S5"]) == 6

    result = {
        "schema": "byte-adder-negative-middle21-audit-v1",
        "status": "fixed_formula_verified_conditional_on_nC4_at_D3",
        "truth_rows": len(rows),
        "mismatch": {"nC6": 0, "S4": 0, "S5": 0},
        "owner": {
            "overlap_rows": sum(
                int(row["K45_and_P45"]) for row in rows
            ),
            "conflict_rows": sum(
                int(row["nC6"]["conflict"]) for row in rows
            ),
            "active_one_rows": sum(
                int(row["nC6"]["driven"] and row["nC6"]["value"])
                for row in rows
            ),
            "active_zero_rows": sum(
                int(row["nC6"]["driven"] and not row["nC6"]["value"])
                for row in rows
            ),
            "z_rows": sum(int(row["nC6"]["z"]) for row in rows),
        },
        "gate_ledger": ledger,
        "gate_total": sum(ledger.values()),
        "arrivals": arrivals,
        "rows": rows,
        "candidate_generated": False,
        "missing_contract": (
            "S0..S3 plus a data-correct, conflict-free nC4 arriving at D3 "
            "must close in no more than 42 gates"
        ),
    }
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
