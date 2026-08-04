"""Map the six required output truth tables to k512 mixed-target statistics."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import search_phase_high_global_map as phase


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_mapping(enumeration_result: Path) -> dict[str, object]:
    result = json.loads(enumeration_result.read_text(encoding="utf-8"))
    if result.get("status") != "enumerated":
        raise ValueError("expected an enumeration-only result")
    if result.get("mode") != "integrated-nc7":
        raise ValueError("expected the integrated-nc7 phase model")

    target_rows = result["mixed_source1_data_bus2_per_target"]
    by_sha256 = {
        row["target_sha256"]: (index, row)
        for index, row in enumerate(target_rows)
    }
    if len(by_sha256) != len(target_rows):
        raise RuntimeError("duplicate target SHA256 in enumeration result")

    engine = phase.gm.load_engine()
    _named, _sources, _source_labels, outputs, _fixed_gate = (
        phase.build_phase_problem(engine, "integrated-nc7")
    )
    byte_count = engine.ASSIGNMENTS // 8
    rows: list[dict[str, object]] = []
    for name, truth in outputs:
        target_sha256 = phase.gm.digest(truth, byte_count)
        hit = by_sha256.get(target_sha256)
        if hit is None:
            raise RuntimeError(
                f"output {name} SHA256 is absent from the k512 target profile: "
                f"{target_sha256}"
            )
        index, stats = hit
        rows.append(
            {
                "name": name,
                "target_index_zero_based": index,
                "target_index_one_based": index + 1,
                "target_sha256": target_sha256,
                "retained_recipes": stats["retained_recipes"],
                "valid_drivers": stats["valid_drivers"],
                "mixed_coverages": stats["mixed_coverages"],
                "candidate_expanded_enables": stats[
                    "candidate_expanded_enables"
                ],
                "exact_verifications": stats["exact_verifications"],
                "enumeration_seconds": stats["seconds"],
            }
        )

    return {
        "schema": "source1-data-output-target-mapping-v1",
        "mode": result["mode"],
        "vectors": result["vectors"],
        "target_profile": result["mixed_bus2_target_profile"],
        "target_count": result["mixed_source1_data_bus2_target_count"],
        "enumeration_result": str(enumeration_result.resolve()),
        "enumeration_result_sha256": file_sha256(enumeration_result),
        "mapping_script_sha256": file_sha256(Path(__file__)),
        "outputs": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--enumeration-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = build_mapping(args.enumeration_result)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": hashlib.sha256(encoded.encode()).hexdigest(),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
