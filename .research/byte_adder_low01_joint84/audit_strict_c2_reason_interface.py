"""Replay the hand-derived D1 reason interface required by strict C2@2.

This is a fixed 32-row audit.  It does not synthesize or enumerate circuits.
The purpose is to keep the indispensable Cin*P0*V1 term and the physical BUS
conflict contract visible when comparing the 11-gate strict bit-0 macro with
the mature 10-gate, slow-carry full-adder macro.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "strict-c2-reason-interface-audit-v1.json"


@dataclass(frozen=True)
class State:
    value: int
    driven: bool
    conflict: bool = False

    @property
    def effective(self) -> int:
        return self.value if self.driven and not self.conflict else 0


def scalar(value: int | bool) -> State:
    return State(int(bool(value)), True, False)


def switch(enable: State, data: State) -> State:
    if enable.effective == 0:
        return State(0, False, False)
    return State(data.effective, True, data.conflict)


def bus(*drivers: State) -> State:
    active = [driver for driver in drivers if driver.driven]
    if not active:
        return State(0, False, False)
    conflict = any(driver.conflict for driver in active)
    values = {driver.value for driver in active if not driver.conflict}
    conflict |= len(values) > 1
    return State(0 if conflict else next(iter(values)), True, conflict)


def main() -> int:
    mismatch = {
        "majority_pair_cover": 0,
        "rotated_reason_cover": 0,
        "strict_c2_value": 0,
        "strict_c2_conflict": 0,
        "joint10_c1": 0,
        "joint10_s0": 0,
        "joint10_slow_c2": 0,
    }
    missing_term_rows = 0
    unsafe_cin_v1_rows = 0
    unsafe_v0_v1_rows = 0
    rows = []
    digest = hashlib.sha256()

    for a0, b0, cin, a1, b1 in itertools.product((0, 1), repeat=5):
        sa0, sb0, scin = scalar(a0), scalar(b0), scalar(cin)
        g0 = a0 & b0
        v0 = a0 | b0
        p0 = v0 & (1 - g0)
        g1 = a1 & b1
        v1 = a1 | b1
        p1 = v1 & (1 - g1)
        c1 = g0 | (p0 & cin)
        c2 = g1 | (p1 & c1)
        s0 = a0 ^ b0 ^ cin

        ab = a0 & b0
        ac = a0 & cin
        bc = b0 & cin
        mismatch["majority_pair_cover"] += int((ab | ac | bc) != c1)

        # One of the three symmetric two-reason decompositions.  Rotating the
        # selector only renames the variables and has the same cost/state law.
        t0 = bus(switch(sa0, scin), switch(sb0, scin))
        mismatch["rotated_reason_cover"] += int((t0.effective | g0) != c1)

        sg0, sg1, sv1 = scalar(g0), scalar(g1), scalar(v1)
        strict_c2 = bus(
            switch(t0, sv1),
            switch(sg0, sv1),
            switch(sg1, sv1),
        )
        mismatch["strict_c2_value"] += int(strict_c2.effective != c2)
        mismatch["strict_c2_conflict"] += int(strict_c2.conflict)

        # Mature 10-gate bit-0 macro: resolve C1 at D2, then use a two-driver
        # C2 owner.  It is value-correct but the owner necessarily arrives D3.
        sv0 = scalar(v0)
        joint_c1 = bus(switch(scin, sv0), switch(sg0, sg0))
        zero_count = 1 - (cin | v0)
        not_all_three = 1 - (cin & g0)
        exactly_two = joint_c1.effective & not_all_three
        joint_s0 = 1 - (zero_count | exactly_two)
        joint_slow_c2 = bus(switch(joint_c1, sv1), switch(sg1, sv1))
        mismatch["joint10_c1"] += int(joint_c1.effective != c1)
        mismatch["joint10_s0"] += int(joint_s0 != s0)
        mismatch["joint10_slow_c2"] += int(joint_slow_c2.effective != c2)

        without_t0 = v1 & (g1 | g0)
        missing_term = v1 & cin & p0
        missing_term_rows += int(c2 != without_t0)
        if c2 != without_t0 and not missing_term:
            raise RuntimeError("a strict-C2 mismatch escaped the Cin*P0*V1 term")

        # These are the two tempting one-Switch substitutions.  Both drop one
        # factor and therefore create false positives on a reachable row.
        unsafe_cin_v1_rows += int((cin & v1) and not c2)
        unsafe_v0_v1_rows += int((v0 & v1) and not c2)

        rows.append(
            {
                "a0": a0,
                "b0": b0,
                "cin": cin,
                "bit1": "G" if g1 else ("P" if p1 else "K"),
                "C1": c1,
                "C2": c2,
                "strict_T0_physical": (
                    "Z" if not t0.driven else str(t0.effective)
                ),
                "missing_Cin_P0_V1": missing_term,
            }
        )
        digest.update(bytes((a0, b0, cin, a1, b1, c1, c2, s0)))

    if any(mismatch.values()):
        raise RuntimeError(f"strict C2 reason audit mismatch: {mismatch}")
    if missing_term_rows != 4:
        raise RuntimeError(f"unexpected missing-term row count: {missing_term_rows}")
    if unsafe_cin_v1_rows == 0 or unsafe_v0_v1_rows == 0:
        raise RuntimeError("a dropped-factor counterexample disappeared")

    payload = {
        "schema": "tc-byte-adder-strict-c2-reason-interface-audit-v1",
        "scope": {
            "rows": len(rows),
            "method": "fixed replay of one hand-derived majority/reason factorization",
            "search": False,
        },
        "identities": {
            "C1": "A0*B0 | Cin*(A0|B0)",
            "pair_cover": "A0*B0 | A0*Cin | B0*Cin",
            "strict_reasons": "G0 | T0, T0=Cin*(A0|B0)",
            "C2": "G1 | P1*C1 = V1*(G1|G0|T0)",
            "indispensable_residual": "V1*Cin*P0",
        },
        "mismatch_rows": mismatch,
        "counterexamples": {
            "remove_T0_missing_rows": missing_term_rows,
            "replace_T0_by_Cin_false_positive_rows": unsafe_cin_v1_rows,
            "replace_T0_by_V0_false_positive_rows": unsafe_v0_v1_rows,
        },
        "gate_ledgers": {
            "strict_two_reason_interface": {
                "T0_two_switch_owner_at_D1": 4,
                "remaining_pair_reason_G0_at_D1": 1,
                "two_bit0_C2_switches_at_D2": 4,
                "interface_subtotal_excluding_G1_driver": 9,
            },
            "expanded_three_pair_interface": {
                "three_pair_AND_reasons_at_D1": 3,
                "three_bit0_C2_switches_at_D2": 6,
                "interface_subtotal_excluding_G1_driver": 9,
            },
            "mature_joint10": {
                "bit0_macro": 10,
                "C1_arrival": 2,
                "two_switch_C2_owner_arrival": 3,
            },
            "authoritative_strict": {
                "bit0_macro": 11,
                "T0_arrival": 1,
                "C2_arrival": 2,
            },
        },
        "rows": rows,
        "digest_sha256": digest.hexdigest(),
        "conclusion": (
            "The 10-gate population-count macro saves its gate by resolving C1 at D2. "
            "Strict C2@2 still needs the D1 Cin*(A0|B0) reason.  Publishing that "
            "reason as a two-Switch owner or expanding it into two pair products has "
            "the same nine-gate reason-plus-C2-interface cost; neither preserves the "
            "10-gate saving.  This is an interface result, not a global circuit lower bound."
        ),
    }
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(payload["mismatch_rows"], ensure_ascii=False, indent=2))
    print(json.dumps(payload["counterexamples"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
