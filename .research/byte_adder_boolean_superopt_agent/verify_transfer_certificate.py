"""Independently replay exact carry-transfer JSON certificates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import exact_adder_block_sat as exact
from exact_transfer_sat import transfer_targets


def verify(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "exact-carry-transfer-switch-cnf-v1":
        raise ValueError(f"unexpected schema in {path}")
    original_targets = exact.adder_targets
    exact.adder_targets = transfer_targets
    try:
        replay = exact.verify_payload(payload)
    finally:
        exact.adder_targets = original_targets
    return {
        "path": str(path),
        "status": payload.get("status"),
        "actual_gate": payload.get("actual_gate"),
        "replay": replay,
        "matches_embedded_verification": replay == payload.get("verification"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path, nargs="+")
    args = parser.parse_args()
    reports = [verify(path) for path in args.certificate]
    for report in reports:
        replay = report["replay"]
        if report["status"] != "sat" or not report["matches_embedded_verification"]:
            raise RuntimeError(report)
        if any(
            replay[key]
            for key in (
                "mismatch_count",
                "bus_conflict_count",
                "undriven_output_count",
                "physical_net_partition_violation_count",
            )
        ):
            raise RuntimeError(report)
    print(json.dumps(reports, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
