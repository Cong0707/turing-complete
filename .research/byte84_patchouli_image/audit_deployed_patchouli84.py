#!/usr/bin/env python3
"""Read-only audit for the deployed Patchouli 84/6 Byte Adder candidate."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "turingsynth" / "src"))

from tc_save_lab.analysis import analyze_file
from turingsynth.audit.relayout import audit_relayout
from turingsynth.formats.v15 import decode_v15


EXPECTED_SOURCE_SHA256 = (
    "16ad06eff5eb93e8bada90f5284ae4e3b1e21848e18319ccb11e6d6006030a51"
)
EXPECTED_DEPLOYED_SHA256 = (
    "0484d0e07822a774fb2e46cade58fb633259ec1477572f93dcf409ad3064799c"
)
EXPECTED_SCORE = (84, 6, 504)


def _digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _default_save() -> Path:
    appdata = Path(os.environ["APPDATA"])
    return appdata / "Turing Complete" / "schematics" / "byte_adder" / "Default" / "circuit.data"


def audit(save: Path) -> dict[str, object]:
    source_path = (
        HERE
        / "materialized_patchouli84_s5_five_gate"
        / "candidate"
        / "circuit.data"
    )
    candidate_path = ROOT / "examples" / "byte_adder" / "candidate" / "circuit.data"

    source_payload = source_path.read_bytes()
    candidate_payload = candidate_path.read_bytes()
    save_payload = save.read_bytes()
    source_hash = _digest(source_payload)
    candidate_hash = _digest(candidate_payload)
    save_hash = _digest(save_payload)

    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"unexpected materialized source hash: {source_hash}")
    if candidate_hash != EXPECTED_DEPLOYED_SHA256:
        raise RuntimeError(f"unexpected repository candidate hash: {candidate_hash}")
    if save_hash != candidate_hash or save_payload != candidate_payload:
        raise RuntimeError("formal save differs from repository candidate")

    analysis = analyze_file(candidate_path)
    metrics = analysis["metrics"]
    score = (
        metrics["declared_gate"],
        metrics["declared_delay"],
        metrics["declared_energy_gate_delay"],
    )
    if score != EXPECTED_SCORE:
        raise RuntimeError(f"unexpected score: {score!r}")
    connectivity = metrics["connectivity"]
    for key in (
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[key] != 0:
            raise RuntimeError(f"connectivity audit failed: {key}={connectivity[key]}")
    if metrics["component_kind_counts"].get(30, 0) != 0:
        raise RuntimeError("native com_add is present")

    source = decode_v15(source_payload)
    candidate = decode_v15(candidate_payload)
    relayout = audit_relayout(source, candidate)
    return {
        "schema": "patchouli-byte-adder-84-deployment-audit-v1",
        "status": "pass",
        "score": list(score),
        "source": str(source_path.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": source_hash,
        "candidate": str(candidate_path.relative_to(ROOT)).replace("\\", "/"),
        "candidate_sha256": candidate_hash,
        "formal_save": str(save),
        "formal_save_sha256": save_hash,
        "formal_save_matches": True,
        "component_count": metrics["component_count"],
        "wire_count": metrics["wire"]["wire_count"],
        "logical_network_count": connectivity["logical_network_count"],
        "native_com_add_count": 0,
        "connectivity": {
            key: connectivity[key]
            for key in (
                "unconnected_pin_count",
                "multi_driver_network_count",
                "undriven_network_count",
                "sinkless_network_count",
                "width_mismatch_network_count",
                "cycle_component_count",
            )
        },
        "relayout": relayout,
        "backup_created": False,
        "game_started": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", type=Path, default=_default_save())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.save)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
