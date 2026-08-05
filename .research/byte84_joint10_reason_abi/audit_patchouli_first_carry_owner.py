"""Deterministically audit the first multi-Switch carry owner in the 84/6 image.

This script does not search for circuits.  It replays the hand-traced topology
visible in ``byte84_patchouli_image/02-upper-mid.png`` over its complete 32-row
input domain while preserving active-zero, Z, and BUS-conflict state.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMAGE = ROOT / ".research" / "byte84_patchouli_image" / "02-upper-mid.png"
GRID_IMAGE = (
    ROOT / ".research" / "byte84_patchouli_image" / "12-upper-mid-grid-2x.png"
)
OUTPUT = HERE / "patchouli-first-carry-owner-audit-v1.json"
VARIABLES = ("a0", "b0", "a1", "b1", "cin")
ROWS = tuple(
    dict(zip(VARIABLES, values, strict=True))
    for values in itertools.product((0, 1), repeat=len(VARIABLES))
)


@dataclass(frozen=True)
class State:
    value: int
    driven: bool = True
    conflict: bool = False

    @property
    def effective(self) -> int:
        return self.value if self.driven else 0


def scalar(value: int | bool) -> State:
    return State(int(bool(value)), True, False)


def gate(op: str, left: State, right: State) -> State:
    a, b = left.effective, right.effective
    value = {
        "AND": a & b,
        "OR": a | b,
        "NAND": 1 - (a & b),
        "NOR": 1 - (a | b),
    }[op]
    return State(value, True, left.conflict or right.conflict)


def switch(enable: State, data: State) -> State:
    if not enable.effective:
        return State(0, False, False)
    # Current-game behavior: enabled Switch samples Z as zero and drives it.
    return State(data.effective, True, data.conflict)


def resolve(*drivers: State) -> State:
    active = tuple(driver for driver in drivers if driver.driven)
    if not active:
        return State(0, False, False)
    conflict = any(driver.conflict for driver in active) or any(
        driver.value != active[0].value for driver in active[1:]
    )
    return State(int(any(driver.value for driver in active)), True, conflict)


def bus(*pairs: tuple[State, State]) -> tuple[State, tuple[State, ...]]:
    drivers = tuple(switch(enable, data) for enable, data in pairs)
    return resolve(*drivers), drivers


def replay(row: dict[str, int]) -> dict[str, object]:
    a0, b0, a1, b1, cin = (scalar(row[name]) for name in VARIABLES)

    # The two Switches directly above the audited three-Switch owner.
    t0, t0_drivers = bus((a0, cin), (b0, cin))
    g0 = gate("AND", a0, b0)
    c1 = gate("OR", t0, g0)

    # The OR/AND pair immediately to the left of the three-Switch owner.
    v1 = gate("OR", a1, b1)
    g1 = gate("AND", a1, b1)

    # The first three-Switch common-data owner in 02-upper-mid.png.
    c2, c2_drivers = bus((t0, v1), (g0, v1), (g1, v1))

    # The four-gate S1 closure used by the authority DAG and visible after C2.
    d1 = gate("NAND", g1, c1)
    e1 = gate("NAND", d1, c2)
    o1 = gate("OR", c1, v1)
    s1 = gate("AND", o1, e1)

    strict_c1 = (row["a0"] & row["b0"]) | (
        (row["a0"] | row["b0"]) & row["cin"]
    )
    strict_c2 = (row["a1"] & row["b1"]) | (
        (row["a1"] | row["b1"]) & strict_c1
    )
    strict_s1 = row["a1"] ^ row["b1"] ^ strict_c1
    return {
        "t0": t0,
        "t0_drivers": t0_drivers,
        "g0": g0,
        "c1": c1,
        "v1": v1,
        "g1": g1,
        "c2": c2,
        "c2_drivers": c2_drivers,
        "s1": s1,
        "strict_c1": strict_c1,
        "strict_c2": strict_c2,
        "strict_s1": strict_s1,
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    results = tuple(replay(row) for row in ROWS)
    c2_states = tuple(result["c2"] for result in results)
    c2_driver_rows = [0, 0, 0]
    overlap_rows = 0
    for result in results:
        active = [driver.driven for driver in result["c2_drivers"]]
        for index, driven in enumerate(active):
            c2_driver_rows[index] += int(driven)
        overlap_rows += int(sum(active) >= 2)

    mismatch_c1 = sum(
        result["c1"].effective != result["strict_c1"] for result in results
    )
    mismatch_c2 = sum(
        result["c2"].effective != result["strict_c2"] for result in results
    )
    mismatch_s1 = sum(
        result["s1"].effective != result["strict_s1"] for result in results
    )
    conflicts = sum(state.conflict for state in c2_states)
    if mismatch_c1 or mismatch_c2 or mismatch_s1 or conflicts:
        raise RuntimeError(
            f"audit failed: C1={mismatch_c1}, C2={mismatch_c2}, "
            f"S1={mismatch_s1}, conflicts={conflicts}"
        )

    cofactor = {}
    for name, a1, b1 in (("K", 0, 0), ("P0", 0, 1), ("P1", 1, 0), ("G", 1, 1)):
        rows = []
        for c1_value in (0, 1):
            matching = [
                result["c2"]
                for result in results
                if result["c1"].effective == c1_value
                and result["v1"].effective == (a1 | b1)
                and result["g1"].effective == (a1 & b1)
            ]
            rows.append(
                {
                    "c1": c1_value,
                    "effective_values": sorted({state.effective for state in matching}),
                    "driven_values": sorted({int(state.driven) for state in matching}),
                }
            )
        cofactor[name] = rows

    vector = bytes(
        (state.effective | (int(state.driven) << 1) | (int(state.conflict) << 2))
        for state in c2_states
    )
    payload = {
        "schema": "tc-byte-adder-patchouli-first-carry-owner-v1",
        "scope": {
            "rows": len(ROWS),
            "search": False,
            "game_started": False,
            "save_modified": False,
        },
        "evidence": {
            "image": str(IMAGE.relative_to(ROOT)).replace("\\", "/"),
            "image_sha256": sha256(IMAGE),
            "grid_image": str(GRID_IMAGE.relative_to(ROOT)).replace("\\", "/"),
            "grid_image_sha256": sha256(GRID_IMAGE),
            "visible_owner": "three vertically stacked Switches near x=350,y=80..120 in the 760x420 crop",
        },
        "trace": {
            "upstream": [
                "T0=BUS(SW(a0,cin),SW(b0,cin)) @1",
                "G0=a0 AND b0 @1",
                "C1=T0 OR G0 @2",
                "V1=a1 OR b1 @1",
                "G1=a1 AND b1 @1",
            ],
            "owner": "C2=BUS(SW(T0,V1),SW(G0,V1),SW(G1,V1)) @2",
            "downstream": [
                "NAND(D1,C2) in the S1 four-gate phase closure",
                "NOR(C2,P2) in the S2 zero phase",
                "AND(C2,P2) in the S2 one phase",
                "SW(enable=C2,data=N23) in the B23 carry-reason owner",
            ],
        },
        "ledger": {
            "t0_owner_gate": 4,
            "g0_v1_g1_gate": 3,
            "c1_gate": 1,
            "c2_owner_gate": 6,
            "s1_tail_gate": 4,
            "c1_arrival": 2,
            "c2_arrival": 2,
            "s1_arrival": 5,
            "full_bits0_to_1_gate_with_q0_p0_s0": 23,
        },
        "semantic": {
            "c1_mismatch": mismatch_c1,
            "c2_mismatch": mismatch_c2,
            "s1_mismatch": mismatch_s1,
            "c2_conflict_rows": conflicts,
            "c2_active_one_rows": sum(state.driven and state.value for state in c2_states),
            "c2_active_zero_rows": sum(state.driven and not state.value for state in c2_states),
            "c2_z_rows": sum(not state.driven for state in c2_states),
            "c2_driver_active_rows": c2_driver_rows,
            "c2_multi_driver_overlap_rows": overlap_rows,
            "c2_state_vector_sha256": hashlib.sha256(vector).hexdigest(),
            "cofactor_by_bit1_state": cofactor,
        },
        "architectural_conclusion": {
            "matches_strict_d2_carry_owner": True,
            "matches_joint10_slow_c2": False,
            "reason": "the image has three common-data drivers and the owner must feed D2 fanouts",
            "leaderboard_84_gate_saving_is_in_this_slice": False,
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
