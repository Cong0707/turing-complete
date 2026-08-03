"""Exhaust the valid load/steady domain of one late phase correction cell."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    # (mode, lane, base, ready, not_ready, target).  During load ``base`` is
    # zero and lane carries the seed.  In steady mode lane's mapped q bit and
    # the desired base n are independent linear forms, so all four q/n rows
    # occur.
    rows = (
        ("load_s0", 0, 0, 0, 1, 0),
        ("load_s1", 1, 0, 0, 1, 1),
        ("steady_q0_n0", 0, 0, 1, 0, 0),
        ("steady_q0_n1", 0, 1, 1, 0, 1),
        ("steady_q1_n0", 1, 0, 1, 0, 0),
        ("steady_q1_n1", 1, 1, 1, 0, 1),
    )
    sources = {
        "lane": tuple(row[1] for row in rows),
        "base": tuple(row[2] for row in rows),
        "ready": tuple(row[3] for row in rows),
        "not_ready": tuple(row[4] for row in rows),
        "const0": (0,) * len(rows),
        "const1": (1,) * len(rows),
    }
    target = tuple(row[5] for row in rows)

    zero_gate = [name for name, table in sources.items() if table == target]
    one_gate = []
    unary = {"NOT": lambda value: 1 - value}
    binary = {
        "AND": lambda left, right: left & right,
        "OR": lambda left, right: left | right,
        "NAND": lambda left, right: 1 - (left & right),
        "NOR": lambda left, right: 1 - (left | right),
    }
    for operation, function in unary.items():
        for source, table in sources.items():
            if tuple(function(value) for value in table) == target:
                one_gate.append({"operation": operation, "inputs": [source]})
    for operation, function in binary.items():
        for left_name, left in sources.items():
            for right_name, right in sources.items():
                if tuple(function(a, b) for a, b in zip(left, right, strict=True)) == target:
                    one_gate.append(
                        {"operation": operation, "inputs": [left_name, right_name]}
                    )

    # One Switch costs two gates.  Its numerical value is enable & data; Z on
    # disabled rows is read as zero by the following ordinary XOR input.
    one_switch = []
    for enable_name, enable in sources.items():
        for data_name, data in sources.items():
            value = tuple(a & b for a, b in zip(enable, data, strict=True))
            if value == target:
                one_switch.append(
                    {"enable": enable_name, "data": data_name, "cost": 2}
                )

    pulse = tuple(
        left & right
        for left, right in zip(sources["lane"], sources["not_ready"], strict=True)
    )
    witness = tuple(
        left | right for left, right in zip(pulse, sources["base"], strict=True)
    )
    if witness != target or zero_gate or one_gate or one_switch:
        raise AssertionError("phase correction lower-bound enumeration changed")

    lower = HERE / "zero-lane-phase-b29.json"
    upper = HERE / "zero-lane-phase-b30.json"
    lower_payload = json.loads(lower.read_text(encoding="utf-8"))
    upper_payload = json.loads(upper.read_text(encoding="utf-8"))
    if lower_payload["status"] != "unsat" or upper_payload["status"] != "sat":
        raise AssertionError("zero-lane frontier certificates changed")
    if upper_payload["correction_cost"] != 30 or upper_payload["total_gate"] != 443:
        raise AssertionError("zero-lane upper bound accounting changed")

    result = {
        "schema": 1,
        "model": "late phase correction over all physically reachable load/steady rows",
        "rows": [
            {
                "name": name,
                "lane": lane,
                "base": base,
                "ready": ready,
                "not_ready": not_ready,
                "target": wanted,
            }
            for name, lane, base, ready, not_ready, wanted in rows
        ],
        "zero_gate_matches": zero_gate,
        "one_gate_matches": one_gate,
        "one_switch_matches": one_switch,
        "minimum_gate": 2,
        "witness": {
            "gate0": "pulse = AND(lane, not_ready)",
            "gate1": "result = OR(pulse, base)",
            "truth_table": list(witness),
            "delay": 2,
        },
        "fixed_dag_zero_lane_frontier": {
            "29": "unsat",
            "30": "sat",
            "total_gate": 443,
            "lower_sha256": digest(lower),
            "upper_sha256": digest(upper),
        },
    }
    output = HERE / "phase_correction_cell.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
