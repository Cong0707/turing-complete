"""Audit the complete sparse two-row Woodbury partition for RNG 66/8."""

from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "rank2_woodbury_66_certificate.json"


def load_algebra():
    path = HERE / "audit_structured_shear_66.py"
    spec = importlib.util.spec_from_file_location("structured_shear_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load algebra audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ALGEBRA = load_algebra()


def lines(name: str) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in (HERE / name).read_text(encoding="utf-8").splitlines()
    ]


def last(name: str) -> dict[str, object]:
    return lines(name)[-1]


def first_matrix(name: str) -> dict[str, object]:
    return next(record for record in lines(name) if "C" in record)


def audit_center(name: str, expected_bad: list[int]) -> dict[str, object]:
    record = first_matrix(name)
    C = [int(value, 16) for value in record["C"]]
    T0, B, D = ALGEBRA.derive(C)
    score = ALGEBRA.score(C)
    assert score == {
        "over": 3,
        "excess": 20,
        "maximum": 34,
        "B_plus_D_weight": 181,
        "C_weight": 68,
        "C_maximum_row_weight": 3,
    }
    assert [f"{value:08x}" for value in T0] == record["T0"]
    assert [f"{value:08x}" for value in B] == record["B"]
    assert [f"{value:08x}" for value in D] == record["D"]
    bad = [
        row for row in range(32)
        if 4 * B[row].bit_count() + D[row].bit_count() > 16
    ]
    assert bad == expected_bad
    replay = ALGEBRA.replay(C, T0, B, D)
    assert replay["passed"] and replay["checked_outputs"] == 22_360
    return {"score": score, "bad_rows": bad, "protocol_replay": replay}


def check(record: dict[str, object], expected: dict[str, object]) -> None:
    for key, value in expected.items():
        if record.get(key) != value:
            raise AssertionError(f"{record.get('mode')} {key}: {record.get(key)} != {value}")


def digest(name: str) -> str:
    return sha256((HERE / name).read_bytes()).hexdigest()


def main() -> None:
    regular_names = ["over3-rank2bad.jsonl", "joint-rank2bad.jsonl"]
    singular_names = ["over3-rank2singular.jsonl", "joint-rank2singular.jsonl"]
    mixed_names = ["over3-rank2mixed.jsonl", "joint-rank2mixed.jsonl"]

    regular_expected = {
        "mode": "rank2bad-summary",
        "sensitive": 16,
        "rank1_checked": 87_808,
        "pairs": 101_556_491,
        "nonsingular": 96_328_270,
        "best": [3, 20, 34],
    }
    singular_expected = {
        "mode": "rank2singular-summary",
        "sensitive": 16,
        "raw_pairs": 2_490_870_641,
        "cross_coupled": 65_017_330,
        "formula_audited": 4_096,
        "bad_row_prefilter": 739_982,
        "full_scored": 28,
        "best": [3, 20, 34],
    }
    mixed_expected = {
        "mode": "rank2mixed-summary",
        "sensitive": 16,
        "raw_pairs": 1_020_433_148,
        "jointly_invertible": 31_534_050,
        "formula_audited": 4_096,
        "bad_row_prefilter": 445_845,
        "full_scored": 0,
        "best": [3, 20, 34],
    }
    for name in regular_names:
        check(last(name), regular_expected)
    for name in singular_names:
        check(last(name), singular_expected)
    for name in mixed_names:
        check(last(name), mixed_expected)

    destinations = 16
    sparse_nonzero_rows = 5_488
    replacements_per_row = sparse_nonzero_rows - 1
    destination_pairs = destinations * (destinations - 1) // 2
    expected_total = destination_pairs * replacements_per_row**2
    partition_total = (
        regular_expected["pairs"]
        + singular_expected["raw_pairs"]
        + mixed_expected["raw_pairs"]
    )
    assert expected_total == partition_total == 3_612_860_280
    invertible_total = (
        regular_expected["nonsingular"]
        + singular_expected["cross_coupled"]
        + mixed_expected["jointly_invertible"]
    )
    assert invertible_total == 192_879_650

    artifact_names = [
        "search_sparse_c_66.cpp",
        "search_rank2_mixed_66.cpp",
        *regular_names,
        *singular_names,
        *mixed_names,
    ]
    result = {
        "schema": 1,
        "status": "complete 16-coordinate sparse rank-2 obstruction",
        "model": "66-cycle persistent seed, delay-8 mixed-Kraft necessity",
        "centers": {
            "annealed_over3": audit_center(regular_names[0], [13, 16, 27]),
            "joint_basis_over3": audit_center(regular_names[1], [12, 16, 18]),
        },
        "per_center_partition": {
            "destination_count": destinations,
            "destination_pairs": destination_pairs,
            "replacement_rows_per_destination": replacements_per_row,
            "regular_regular_raw": regular_expected["pairs"],
            "singular_singular_raw": singular_expected["raw_pairs"],
            "mixed_raw": mixed_expected["raw_pairs"],
            "all_raw": expected_total,
            "jointly_invertible": invertible_total,
            "best": [3, 20, 34],
        },
        "scope": {
            "proves": (
                "No score improvement exists among all weight-1..3 two-row "
                "replacements on the 16 coordinates directly sensitive to the "
                "three violating rows, for either audited center."
            ),
            "does_not_prove": (
                "Global UNSAT, replacements involving coordinates outside the "
                "sensitive union, rank-3 moves, or physical Switch/Z synthesis."
            ),
            "game_started": False,
            "live_save_read_or_written": False,
        },
        "sha256": {name: digest(name) for name in artifact_names},
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "all_raw_per_center": expected_total,
        "jointly_invertible_per_center": invertible_total,
        "best": [3, 20, 34],
        "certificate_sha256": sha256(OUT.read_bytes()).hexdigest(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
