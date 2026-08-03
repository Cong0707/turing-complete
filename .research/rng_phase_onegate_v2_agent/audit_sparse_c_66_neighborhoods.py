"""Independently audit the sparse-C 66/8 neighborhood certificates.

The script only reads research artifacts beside itself. It does not start the
game and does not access the live save.
"""

from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "sparse_c_66_neighborhood_certificate.json"


def load_algebra():
    path = HERE / "audit_structured_shear_66.py"
    spec = importlib.util.spec_from_file_location("structured_shear_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load structured shear audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ALGEBRA = load_algebra()


def read_jsonl(name: str) -> list[dict[str, object]]:
    path = HERE / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def first_matrix(records: list[dict[str, object]]) -> dict[str, object]:
    return next(record for record in records if "C" in record)


def summary(records: list[dict[str, object]], mode: str) -> dict[str, object]:
    return next(record for record in records if record.get("mode") == mode)


def audit_center(record: dict[str, object], expected_bad: list[int]) -> dict[str, object]:
    C = [int(value, 16) for value in record["C"]]
    T0, B, D = ALGEBRA.derive(C)
    assert [f"{value:08x}" for value in T0] == record["T0"]
    assert [f"{value:08x}" for value in B] == record["B"]
    assert [f"{value:08x}" for value in D] == record["D"]
    score = ALGEBRA.score(C)
    assert score == {
        "over": 3,
        "excess": 20,
        "maximum": 34,
        "B_plus_D_weight": 181,
        "C_weight": 68,
        "C_maximum_row_weight": 3,
    }
    violations = [
        {
            "row": row,
            "B_weight": B[row].bit_count(),
            "D_weight": D[row].bit_count(),
            "metric": 4 * B[row].bit_count() + D[row].bit_count(),
        }
        for row in range(32)
        if 4 * B[row].bit_count() + D[row].bit_count() > 16
    ]
    assert [item["row"] for item in violations] == expected_bad
    replay = ALGEBRA.replay(C, T0, B, D)
    assert replay["passed"] and replay["checked_outputs"] == 22_360
    return {
        "score": score,
        "violating_rows": violations,
        "protocol_replay": replay,
        "C": record["C"],
        "T0": record["T0"],
        "B": record["B"],
        "D": record["D"],
    }


def assert_summary(record: dict[str, object], expected: dict[str, object]) -> None:
    for key, value in expected.items():
        if record.get(key) != value:
            raise AssertionError(f"{record.get('mode')} {key}: {record.get(key)} != {value}")


def file_hash(name: str) -> str:
    return sha256((HERE / name).read_bytes()).hexdigest()


def main() -> None:
    logs = {
        name: read_jsonl(name)
        for name in (
            "over3-radius2.jsonl",
            "over3-rank1.jsonl",
            "over3-rank2pool-2048.jsonl",
            "joint-rank2pool-2048.jsonl",
            "over3-crossmix.jsonl",
            "over3-rank2heavy.jsonl",
            "joint-rank2heavy.jsonl",
            "over3-rank2bad.jsonl",
            "joint-rank2bad.jsonl",
        )
    }

    center_a = audit_center(first_matrix(logs["over3-radius2.jsonl"]), [13, 16, 27])
    center_b = audit_center(first_matrix(logs["joint-rank2pool-2048.jsonl"]), [12, 16, 18])

    assert_summary(summary(logs["over3-radius2.jsonl"], "radius2-summary"), {
        "checked": 983_072,
        "valid_final_C": 63_534,
        "best": [3, 20, 34],
    })
    assert_summary(summary(logs["over3-rank1.jsonl"], "rank1-summary"), {
        "checked": 175_616,
        "best": [3, 20, 34],
    })
    for name, nonsingular in (
        ("over3-rank2pool-2048.jsonl", 5_390_563),
        ("joint-rank2pool-2048.jsonl", 5_390_594),
    ):
        assert_summary(summary(logs[name], "rank2pool-summary"), {
            "rank1_checked": 175_616,
            "legal_rank1": 28_055,
            "pool": 3_431,
            "pairs": 5_466_225,
            "nonsingular": nonsingular,
            "best": [3, 20, 34],
        })
    assert_summary(summary(logs["over3-crossmix.jsonl"], "crossmix-summary"), {
        "differing_rows": 21,
        "combinations": 2_097_152,
        "nonsingular": 2_560,
        "best": [3, 20, 34],
    })
    for name in ("over3-rank2heavy.jsonl", "joint-rank2heavy.jsonl"):
        assert_summary(summary(logs[name], "rank2heavy-summary"), {
            "heavy_row": 16,
            "sensitive": 8,
            "rank1_checked": 43_904,
            "pairs": 28_328_719,
            "nonsingular": 26_380_369,
            "best": [3, 20, 34],
        })
    for name in ("over3-rank2bad.jsonl", "joint-rank2bad.jsonl"):
        assert_summary(summary(logs[name], "rank2bad-summary"), {
            "heavy_row": 16,
            "sensitive": 16,
            "rank1_checked": 87_808,
            "pairs": 101_556_491,
            "nonsingular": 96_328_270,
            "best": [3, 20, 34],
        })

    artifact_names = [
        "audit_structured_shear_66.py",
        "structured_shear_66_frontier.json",
        "search_sparse_c_66.cpp",
        *logs.keys(),
    ]
    result = {
        "schema": 1,
        "status": "verified local-obstruction certificate; not a physical circuit",
        "model": "66-cycle persistent seed, delay-8 mixed-Kraft necessity",
        "centers": {
            "annealed_over3": center_a,
            "joint_basis_over3": center_b,
        },
        "search_summaries": {
            name: records[-1] for name, records in logs.items()
        },
        "scope": {
            "proves": (
                "No improvement exists in the enumerated radius-2 transvection, "
                "single sparse-row, crossmix, or individually nonsingular targeted "
                "two-row neighborhoods."
            ),
            "does_not_prove": (
                "Global UNSAT, jointly nonsingular pairs whose individual replacements "
                "are singular, rank-3 moves, or physical Switch/Z synthesis."
            ),
            "game_started": False,
            "live_save_read_or_written": False,
        },
        "sha256": {name: file_hash(name) for name in artifact_names},
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "centers": {
            name: value["score"] for name, value in result["centers"].items()
        },
        "certificate_sha256": sha256(OUT.read_bytes()).hexdigest(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
