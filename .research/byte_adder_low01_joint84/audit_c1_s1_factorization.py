"""Replay the hand-derived C1/S1 threshold factorization.

No synthesis or expression enumeration is performed.  The 12 rows are the
four reachable (T0,G0) reason pairs crossed with bit1 K/P/G state.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "c1-s1-factorization-audit-v1.json"


def bit_state(name: str) -> tuple[int, int, int]:
    if name == "K":
        return 0, 0, 0
    if name == "P":
        return 1, 0, 1
    if name == "G":
        return 1, 1, 0
    raise ValueError(name)


def main() -> int:
    mismatch = {
        "c2_value": 0,
        "implication_g1_to_c2": 0,
        "implication_c2_to_v1": 0,
        "parity_identity": 0,
        "current_factorization": 0,
        "threshold_factorization": 0,
        "current_equals_threshold": 0,
    }
    c2_state_counts = {"active_one": 0, "active_zero": 0, "z": 0}
    direct_c2_counterexamples = {
        "active_zero_but_s1_one": 0,
        "active_one_but_s1_zero": 0,
        "z_but_s1_one": 0,
    }
    rows = []
    digest = hashlib.sha256()

    for t0, g0, state in itertools.product((0, 1), (0, 1), ("K", "P", "G")):
        v1, g1, p1 = bit_state(state)
        c1 = t0 | g0

        # #26 is a three-driver common-data owner.  Its driven mask is the
        # enable union, while every active driver samples the same V1 data.
        c2_driven = t0 | g0 | g1
        c2_value = v1 if c2_driven else 0
        expected_c2 = g1 | (p1 & c1)
        expected_s1 = p1 ^ c1

        u1 = c1 | v1
        n3 = 1 - (g1 & c1)
        f1 = 1 - (n3 & c2_value)
        current_s1 = u1 & f1

        zero_count = 1 - (c1 | v1)
        not_all_three = 1 - (c1 & g1)
        exactly_two = c2_value & not_all_three
        threshold_s1 = 1 - (zero_count | exactly_two)
        parity_s1 = c1 ^ v1 ^ g1

        mismatch["c2_value"] += int(c2_value != expected_c2)
        mismatch["implication_g1_to_c2"] += int(g1 and not c2_value)
        mismatch["implication_c2_to_v1"] += int(c2_value and not v1)
        mismatch["parity_identity"] += int(parity_s1 != expected_s1)
        mismatch["current_factorization"] += int(current_s1 != expected_s1)
        mismatch["threshold_factorization"] += int(threshold_s1 != expected_s1)
        mismatch["current_equals_threshold"] += int(current_s1 != threshold_s1)

        if not c2_driven:
            c2_state_counts["z"] += 1
            direct_c2_counterexamples["z_but_s1_one"] += int(expected_s1 == 1)
            physical = "Z"
        elif c2_value:
            c2_state_counts["active_one"] += 1
            direct_c2_counterexamples["active_one_but_s1_zero"] += int(
                expected_s1 == 0
            )
            physical = "1"
        else:
            c2_state_counts["active_zero"] += 1
            direct_c2_counterexamples["active_zero_but_s1_one"] += int(
                expected_s1 == 1
            )
            physical = "0"

        rows.append(
            {
                "T0": t0,
                "G0": g0,
                "bit1": state,
                "C1": c1,
                "V1": v1,
                "G1": g1,
                "C2_physical": physical,
                "S1": expected_s1,
            }
        )
        digest.update(bytes((t0, g0, v1, g1, c2_value, c2_driven, expected_s1)))

    if any(mismatch.values()):
        raise RuntimeError(f"factorization mismatch: {mismatch}")

    payload = {
        "schema": "tc-byte-adder-c1-s1-factorization-audit-v1",
        "scope": {
            "rows": len(rows),
            "method": "deterministic replay of one hand-derived threshold factorization",
            "search": False,
        },
        "identities": {
            "C1": "T0|G0",
            "C2": "G1|P1*C1 = V1*(G1|T0|G0)",
            "implication_chain": "G1 <= C2 <= V1",
            "S1_parity": "C1 XOR V1 XOR G1",
            "zero_count": "NOR(C1,V1)",
            "not_all_three": "NAND(C1,G1)",
            "exactly_two": "C2*not_all_three",
            "S1_threshold": "NOR(zero_count,exactly_two)",
        },
        "mismatch_rows": mismatch,
        "c2_physical_state_counts": c2_state_counts,
        "direct_c2_output_counterexamples": direct_c2_counterexamples,
        "gate_ledger": {
            "C1_from_T0_G0": 1,
            "zero_count": 1,
            "not_all_three": 1,
            "exactly_two": 1,
            "S1": 1,
            "total": 5,
        },
        "arrival": {
            "T0_G0_V1_G1": 1,
            "C1_C2": 2,
            "zero_count_not_all_three": 3,
            "exactly_two": 4,
            "S1": 5,
        },
        "rows": rows,
        "digest_sha256": digest.hexdigest(),
        "conclusion": (
            "The current five paid gates are an XOR-free three-input parity cell: "
            "C2 supplies the threshold bit, while two opposite C1 cofactors separate "
            "zero-count and all-three states.  The replay establishes the identities "
            "and the physical C2 counterexamples; it is not a global lower-bound proof."
        ),
    }
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(payload["mismatch_rows"], ensure_ascii=False, indent=2))
    print(json.dumps(payload["direct_c2_output_counterexamples"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
