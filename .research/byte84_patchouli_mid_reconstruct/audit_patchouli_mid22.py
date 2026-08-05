"""Deterministic audit of Patchouli's 22-gate bits4:5/C6 block.

The topology is reconstructed pin-by-pin from the public 84/6 screenshot.  It
enumerates all 512 assignments of C2 and raw A/B bits 2..5, retaining active
zero, active one and Z states on both visible BUS owners.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "patchouli-mid22-audit-v1.json"
IMAGE = (
    HERE.parent
    / "byte84_patchouli_image"
    / "Patchouli-84门6延迟原始截图.jpg"
)

Z = -1
ZERO = 0
ONE = 1


def switch(enable: int, data: int) -> int:
    return data if enable else Z


def read(state: int) -> int:
    return int(state == ONE)


def resolve(*drivers: int) -> tuple[int, bool]:
    active = [state for state in drivers if state != Z]
    if not active:
        return Z, False
    conflict = any(state != active[0] for state in active[1:])
    return active[0], conflict


def state_name(state: int) -> str:
    return {Z: "z", ZERO: "active_zero", ONE: "active_one"}[state]


def inc_state(counter: dict[str, int], state: int) -> None:
    counter[state_name(state)] += 1


def build_ledger() -> list[dict[str, object]]:
    # External low-block rails are included at zero local cost.
    nodes: list[dict[str, object]] = [
        {"name": "G3", "op": "BOUNDARY", "args": [], "cost": 0, "arrival": 1},
        {"name": "B23", "op": "BOUNDARY_BUS", "args": [], "cost": 0, "arrival": 3, "may_z": True},
        {"name": "C4", "op": "OR", "args": ["G3", "B23"], "cost": 0, "arrival": 4},
        {"name": "G4", "op": "AND", "args": ["A4", "B4"], "cost": 1, "arrival": 1},
        {"name": "Q4", "op": "NOR", "args": ["A4", "B4"], "cost": 1, "arrival": 1},
        {"name": "P4", "op": "NOR", "args": ["Q4", "G4"], "cost": 1, "arrival": 2},
        {"name": "G5", "op": "AND", "args": ["A5", "B5"], "cost": 1, "arrival": 1},
        {"name": "Q5", "op": "NOR", "args": ["A5", "B5"], "cost": 1, "arrival": 1},
        {"name": "P5", "op": "NOR", "args": ["Q5", "G5"], "cost": 1, "arrival": 2},
        {"name": "K34", "op": "OR", "args": ["G3", "G4"], "cost": 1, "arrival": 2},
        {"name": "G345", "op": "OR", "args": ["K34", "G5"], "cost": 1, "arrival": 3},
        {"name": "V45", "op": "NOR", "args": ["Q4", "Q5"], "cost": 1, "arrival": 2},
        {"name": "D45", "op": "OR", "args": ["G5", "V45"], "cost": 1, "arrival": 3},
        {
            "name": "C6.driver.B23",
            "op": "SWITCH",
            "data": "D45",
            "enable": "B23",
            "cost": 2,
            "arrival": 4,
            "may_z": True,
        },
        {
            "name": "C6.driver.G345",
            "op": "SWITCH",
            "data": "D45",
            "enable": "G345",
            "cost": 2,
            "arrival": 4,
            "may_z": True,
        },
        {
            "name": "C6",
            "op": "RESOLVED_BUS",
            "drivers": ["C6.driver.B23", "C6.driver.G345"],
            "cost": 0,
            "arrival": 4,
            "may_z": True,
        },
        {"name": "T4", "op": "AND", "args": ["P4", "C4"], "cost": 1, "arrival": 5},
        {"name": "R4", "op": "NOR", "args": ["P4", "C4"], "cost": 1, "arrival": 5},
        {"name": "S4", "op": "NOR", "args": ["T4", "R4"], "cost": 1, "arrival": 6},
        {"name": "U45", "op": "OR", "args": ["B23", "K34"], "cost": 1, "arrival": 4},
        {"name": "H5", "op": "NOR", "args": ["Q4", "P5"], "cost": 1, "arrival": 3},
        {"name": "T5", "op": "AND", "args": ["U45", "H5"], "cost": 1, "arrival": 5},
        {"name": "J5", "op": "NOR", "args": ["Q5", "C6"], "cost": 1, "arrival": 5},
        {"name": "S5", "op": "OR", "args": ["T5", "J5"], "cost": 1, "arrival": 6},
    ]
    return nodes


def audit() -> dict[str, object]:
    mismatch = {name: 0 for name in ("C4", "C6", "S4", "S5")}
    conflict = {"B23": 0, "C6": 0}
    expected_one_undriven = {"B23": 0, "C6": 0}
    bus_state = {
        "B23": {"active_one": 0, "active_zero": 0, "z": 0},
        "C6": {"active_one": 0, "active_zero": 0, "z": 0},
    }
    c6_driver_state = {
        "B23_enable": {"active_one": 0, "active_zero": 0, "z": 0},
        "G345_enable": {"active_one": 0, "active_zero": 0, "z": 0},
    }
    c6_overlap = 0
    c6_overlap_disagreement = 0
    rows = 0

    for word in range(1 << 9):
        rows += 1
        bits = [(word >> index) & 1 for index in range(9)]
        c2, a2, b2, a3, b3, a4, b4, a5, b5 = bits

        g2, q2, p2 = a2 & b2, 1 ^ (a2 | b2), a2 ^ b2
        g3, q3, p3 = a3 & b3, 1 ^ (a3 | b3), a3 ^ b3
        g4, q4, p4 = a4 & b4, 1 ^ (a4 | b4), a4 ^ b4
        g5, q5, p5 = a5 & b5, 1 ^ (a5 | b5), a5 ^ b5

        r23 = 1 ^ (q2 | q3)
        b23_d0 = switch(c2, r23)
        b23_d1 = switch(g2, r23)
        b23_state, b23_conflict = resolve(b23_d0, b23_d1)
        b23 = read(b23_state)
        conflict["B23"] += b23_conflict
        inc_state(bus_state["B23"], b23_state)

        c3_expected = g2 | (p2 & c2)
        c4_expected = g3 | (p3 & c3_expected)
        c4 = g3 | b23
        mismatch["C4"] += c4 != c4_expected

        k34 = g3 | g4
        g345 = k34 | g5
        v45 = 1 ^ (q4 | q5)
        d45 = g5 | v45

        c6_d0 = switch(b23, d45)
        c6_d1 = switch(g345, d45)
        c6_state, c6_conflict = resolve(c6_d0, c6_d1)
        c6 = read(c6_state)
        conflict["C6"] += c6_conflict
        inc_state(bus_state["C6"], c6_state)
        inc_state(c6_driver_state["B23_enable"], c6_d0)
        inc_state(c6_driver_state["G345_enable"], c6_d1)
        if c6_d0 != Z and c6_d1 != Z:
            c6_overlap += 1
            c6_overlap_disagreement += c6_d0 != c6_d1

        c5_expected = g4 | (p4 & c4_expected)
        c6_expected = g5 | (p5 & c5_expected)
        mismatch["C6"] += c6 != c6_expected
        expected_one_undriven["B23"] += bool(c4_expected and not g3 and b23_state == Z)
        expected_one_undriven["C6"] += bool(c6_expected and c6_state == Z)

        t4 = p4 & c4
        r4 = 1 ^ (p4 | c4)
        s4 = 1 ^ (t4 | r4)
        mismatch["S4"] += s4 != (p4 ^ c4_expected)

        u45 = b23 | k34
        h5 = 1 ^ (q4 | p5)
        t5 = u45 & h5
        # Ordinary gates read a Z C6 bus as data-plane zero.
        j5 = 1 ^ (q5 | c6)
        s5 = t5 | j5
        mismatch["S5"] += s5 != (p5 ^ c5_expected)

    ledger = build_ledger()
    gate = sum(int(node["cost"]) for node in ledger)
    arrivals = {
        str(node["name"]): int(node["arrival"])
        for node in ledger
        if int(node["cost"]) or node["name"] in {"C6", "S4", "S5"}
    }
    image_sha256 = hashlib.sha256(IMAGE.read_bytes()).hexdigest() if IMAGE.exists() else None

    payload: dict[str, object] = {
        "schema": "patchouli-byte-adder-mid22-audit-v1",
        "source_image": {"path": str(IMAGE), "sha256": image_sha256},
        "scope": "bits4:5 plus C6, with G3/B23/C4 as the low-boundary ABI",
        "rows": rows,
        "metrics": {
            "gate": gate,
            "delay": max(arrivals["S4"], arrivals["S5"], arrivals["C6"]),
            "block_output_arrivals": {"C6": arrivals["C6"], "S4": arrivals["S4"], "S5": arrivals["S5"]},
            "complete_score_with_frozen_low42_high20": [42 + gate + 20, 6, (42 + gate + 20) * 6],
        },
        "semantic": {
            "mismatch_count": mismatch,
            "conflict_count": conflict,
            "expected_one_undriven": expected_one_undriven,
            "bus_state_count": bus_state,
            "c6_driver_state_count": c6_driver_state,
            "c6_driver_overlap": c6_overlap,
            "c6_overlap_disagreement": c6_overlap_disagreement,
            "ordinary_gate_z_rule_exercised": bus_state["C6"]["z"] > 0,
        },
        "cost_partition": {
            "GQP4_GQP5": 6,
            "C6_support_K34_G345_V45_D45_plus_two_switches": 8,
            "S4": 3,
            "S5_U45_H5_T5_J5_output_or": 5,
            "total": gate,
        },
        "formula": {
            "K34": "G3 OR G4",
            "G345": "K34 OR G5",
            "V45": "NOR(Q4,Q5)",
            "D45": "G5 OR V45",
            "C6": "BUS(SW(enable=B23,data=D45),SW(enable=G345,data=D45))",
            "S4": "NOR(AND(P4,C4),NOR(P4,C4))",
            "U45": "B23 OR K34 = C4 OR G4",
            "H5": "NOR(Q4,P5)",
            "T5": "U45 AND H5",
            "J5": "NOR(Q5,C6)",
            "S5": "T5 OR J5",
        },
        "ledger": ledger,
    }
    if gate != 22:
        raise RuntimeError(f"unexpected gate count: {gate}")
    if any(mismatch.values()) or any(conflict.values()):
        raise RuntimeError(f"semantic failure: mismatch={mismatch} conflict={conflict}")
    if any(expected_one_undriven.values()) or c6_overlap_disagreement:
        raise RuntimeError("unsafe BUS owner state")
    return payload


def main() -> int:
    payload = audit()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.write_text(encoded, encoding="utf-8", newline="\n")
    print(encoded, end="")
    print(f"sha256={hashlib.sha256(encoded.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
