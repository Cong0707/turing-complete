"""Deterministic audit of the Patchouli 84/6 screenshot bottom high tail.

The screenshot is traced into one fixed architecture.  This script does not
search circuits.  It replays all 18 legal states of (C6, bit6, bit7), models
the two physical Switch drivers, and emits a compact machine ledger.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "patchouli-bottom-high-audit-v1.json"

BIT_STATES = {
    "K": {"G": 0, "Q": 1, "P": 0},
    "P": {"G": 0, "Q": 0, "P": 1},
    "G": {"G": 1, "Q": 0, "P": 0},
}


def switch(enable: int, data: int) -> int | None:
    """Return None for Z, otherwise the actively driven Boolean value."""

    return int(data) if enable else None


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rows: list[dict[str, object]] = []
    for c6 in (0, 1):
        for name6, bit6 in BIT_STATES.items():
            for name7, bit7 in BIT_STATES.items():
                g6, q6, p6 = (bit6[key] for key in ("G", "Q", "P"))
                g7, q7, p7 = (bit7[key] for key in ("G", "Q", "P"))

                np6 = g6 | q6
                t67 = q6 & p7
                r67 = int(not (q6 | p7))
                e7 = t67 | r67
                h7 = t67 | q7
                k67 = g6 | g7

                a6 = c6 | np6
                b6 = int(not (c6 & np6))
                s6 = int(not (a6 & b6))
                z7 = int(not (c6 | k67))

                driver_e = switch(e7, a6)
                driver_z = switch(z7, p7)
                conflict = (
                    driver_e is not None
                    and driver_z is not None
                    and driver_e != driver_z
                )
                driven = driver_e is not None or driver_z is not None
                s7 = int(bool(driver_e) or bool(driver_z))
                c8 = int(not (z7 | h7))

                expected_s6 = p6 ^ c6
                c7 = g6 | (p6 & c6)
                expected_s7 = p7 ^ c7
                expected_c8 = g7 | (p7 & c7)

                rows.append(
                    {
                        "C6": c6,
                        "bit6": name6,
                        "bit7": name7,
                        "driver_E": driver_e,
                        "driver_Z": driver_z,
                        "driven": driven,
                        "conflict": conflict,
                        "actual": [s6, s7, c8],
                        "expected": [expected_s6, expected_s7, expected_c8],
                    }
                )

    mismatch_rows = sum(row["actual"] != row["expected"] for row in rows)
    conflict_rows = sum(bool(row["conflict"]) for row in rows)

    def driver_counts(name: str) -> dict[str, int]:
        values = [row[name] for row in rows]
        return {
            "active_one": sum(value == 1 for value in values),
            "active_zero": sum(value == 0 for value in values),
            "z": sum(value is None for value in values),
        }

    overlap_rows = [
        row
        for row in rows
        if row["driver_E"] is not None and row["driver_Z"] is not None
    ]
    resolved = {
        "active_one": sum(
            bool(row["driver_E"]) or bool(row["driver_Z"]) for row in rows
        ),
        "active_zero": sum(
            bool(row["driven"])
            and not (bool(row["driver_E"]) or bool(row["driver_Z"]))
            for row in rows
        ),
        "z": sum(not bool(row["driven"]) for row in rows),
        "conflict": conflict_rows,
    }

    payload = {
        "schema": "patchouli-byte84-bottom-high-audit-v1",
        "scope": {
            "method": "manual screenshot trace plus fixed 18-state replay",
            "rows": len(rows),
            "inputs": ["C6", "bit6 in K/P/G", "bit7 in K/P/G"],
            "no_search": True,
        },
        "evidence": {
            name: {
                "path": name,
                "sha256": digest(HERE / name),
            }
            for name in (
                "04-bottom-high.png",
                "05-output-owner.png",
                "06-full-logic.png",
            )
        },
        "architecture": {
            "state": [
                "G6=AND(a6,b6)",
                "Q6=NOR(a6,b6)",
                "nP6=OR(G6,Q6)",
                "G7=AND(a7,b7)",
                "Q7=NOR(a7,b7)",
                "P7=NOR(G7,Q7)",
            ],
            "reason": [
                "T67=AND(Q6,P7)",
                "R67=NOR(Q6,P7)",
                "E7=OR(T67,R67)",
                "H7=OR(T67,Q7)",
                "K67=OR(G6,G7)",
            ],
            "outputs": [
                "A6=OR(C6,nP6)",
                "B6=NAND(C6,nP6)",
                "S6=NAND(A6,B6)",
                "Z7=NOR(C6,K67)",
                "S7=BUS(SW(E7,A6),SW(Z7,P7))",
                "C8=NOR(Z7,H7)",
            ],
        },
        "ledger": {
            "G6_Q6_nP6_G7_Q7_P7": 6,
            "T67_R67_E7_H7_K67": 5,
            "A6_B6_S6": 3,
            "Z7_C8": 2,
            "S7_two_switch_owner": 4,
            "total": 20,
        },
        "arrival": {
            "G6_Q6_G7_Q7": 1,
            "nP6_P7_K67": 2,
            "T67_R67": 3,
            "E7_H7_C6_input": 4,
            "A6_B6_Z7": 5,
            "S6_S7_C8": 6,
        },
        "fanout": {
            "C6": ["A6", "B6", "Z7", "D5 outside this crop"],
            "G6": ["nP6", "K67"],
            "Q6": ["nP6", "T67", "R67"],
            "nP6": ["A6", "B6"],
            "G7": ["P7", "K67"],
            "Q7": ["P7", "H7"],
            "P7": ["T67", "R67", "S7 driver Z data"],
            "T67": ["E7", "H7"],
            "R67": ["E7"],
            "E7": ["S7 driver E enable"],
            "H7": ["C8"],
            "K67": ["Z7"],
            "A6": ["S6", "S7 driver E data"],
            "B6": ["S6"],
            "Z7": ["S7 driver Z enable", "C8"],
        },
        "three_state": {
            "enabled_data_z": "not exercised: both S7 data rails are ordinary active rails",
            "driver_E": driver_counts("driver_E"),
            "driver_Z": driver_counts("driver_Z"),
            "overlap": {
                "rows": len(overlap_rows),
                "both_one": sum(
                    row["driver_E"] == 1 and row["driver_Z"] == 1
                    for row in overlap_rows
                ),
                "both_zero": sum(
                    row["driver_E"] == 0 and row["driver_Z"] == 0
                    for row in overlap_rows
                ),
                "disagreement": sum(
                    row["driver_E"] != row["driver_Z"] for row in overlap_rows
                ),
            },
            "resolved_S7": resolved,
        },
        "semantic": {
            "mismatch_rows": mismatch_rows,
            "conflict_rows": conflict_rows,
        },
        "conclusion": {
            "matches_verified_human85_high_tail": True,
            "is_19_gate_high_tail": False,
            "is_20_gate_high_tail": True,
            "implication": "Patchouli's 84th-gate saving is above the bits6:7 high tail.",
        },
    }

    if mismatch_rows or conflict_rows:
        raise RuntimeError(
            f"bottom high replay failed: mismatch={mismatch_rows} conflict={conflict_rows}"
        )
    if payload["ledger"]["total"] != 20:
        raise RuntimeError("bottom high-tail gate ledger changed")
    if payload["arrival"]["S6_S7_C8"] != 6:
        raise RuntimeError("bottom high-tail delay ledger changed")

    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(payload["conclusion"], ensure_ascii=False, indent=2))
    print(json.dumps(payload["semantic"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
