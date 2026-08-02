"""Assemble and verify the exact local-search coverage certificate."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CLOSURE = {2, 3, 5, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 31}
OUTSIDE = set(range(32)) - CLOSURE


def read(name: str) -> dict[str, object]:
    return json.loads((HERE / name).read_text(encoding="ascii"))


def require_unsat(name: str, radius: int, x_flips: int) -> None:
    value = read(name)
    assert value["radius"] == radius
    assert value["x_flips"] == x_flips
    assert value["d_flips"] == radius - x_flips
    assert value["status"] == "unsat"


def main() -> None:
    center = read("center_excess3_verified.json")
    assert center["verified_sequences"] == {"seeds": 256, "outputs_per_seed": 65}
    assert center["support"]["excess_over_4"] == 3
    assert center["support"]["maximum"] == 5

    radius7 = read("qffd_radius7_110s.json")
    assert radius7["attempts"] == [
        {
            "hamming_bound": 7,
            "status": "unsat",
            "seconds": radius7["attempts"][0]["seconds"],
        }
    ]

    for x_flips in range(9):
        require_unsat(f"r8_x{x_flips}.json", 8, x_flips)

    for x_flips in (*range(5), *range(6, 10)):
        require_unsat(f"r9_x{x_flips}.json", 9, x_flips)

    for changed in ("yes", "no"):
        name = f"r9_x5_closure_row24_{changed}.json"
        require_unsat(name, 9, 5)
        value = read(name)
        assert {int(item) for item in str(value["free_x_rows"]).split(",")} == CLOSURE
        assert value["branch_x_row"] == 24
        assert value["branch_x_changed"] == changed

    outside = read("r9_x5_require_outside_closure.json")
    assert outside["radius"] == 9 and outside["x_flips"] == 5
    assert outside["status"] == "unsat"
    assert {int(item) for item in str(outside["require_x_rows"]).split(",")} == OUTSIDE

    radius10 = {}
    for x_flips in range(11):
        value = read(f"r10_x{x_flips}.json")
        assert value["radius"] == 10 and value["x_flips"] == x_flips
        radius10[str(x_flips)] = value["status"]
    assert radius10 == {
        "0": "unsat", "1": "unsat", "2": "unsat", "3": "unsat",
        "4": "unsat", "5": "unknown", "6": "unknown", "7": "unsat",
        "8": "unsat", "9": "unsat", "10": "unsat",
    }

    evidence_names = [
        "center_excess3_verified.json", "qffd_radius7_110s.json",
        *(f"r8_x{i}.json" for i in range(9)),
        *(f"r9_x{i}.json" for i in (*range(5), *range(6, 10))),
        "r9_x5_closure_row24_yes.json", "r9_x5_closure_row24_no.json",
        "r9_x5_require_outside_closure.json",
        *(f"r10_x{i}.json" for i in range(11)),
        "split_radius_qffd.py", "verify_boundary.py",
    ]
    hashes = {
        name: sha256((HERE / name).read_bytes()).hexdigest()
        for name in evidence_names
    }
    result = {
        "schema": 1,
        "status": "verified-no-candidate",
        "center": {
            "verified_sequences": center["verified_sequences"],
            "support": center["support"],
            "bad_H_rows": center["bad_H_rows"],
        },
        "exact_boundary": {
            "bitwise_hamming_distance_at_most": 9,
            "result": "UNSAT",
            "variables": "all 320 X bits and 420 D bits",
            "constraints": "wt(X_i)<=3, 1<=wt(D_j)<=4, wt(H_i)<=4, O*H=A*O",
        },
        "radius_10_partitions": radius10,
        "radius_10_conclusion": "unknown: only X-flips 5 and 6 remain globally undecided",
        "sha256": hashes,
    }
    output = HERE / "boundary_certificate.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
