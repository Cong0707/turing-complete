#!/usr/bin/env python3
"""Verify that v2.1.281 Delay Bit stores value but not high-impedance state.

This consumes the checked-in, read-only IDA exports in ``delay-native-audit``.
It never starts the game and never reads or writes a save.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
NATIVE = HERE / "delay-native-audit"
DEFAULT_EXE = Path(
    r"D:\Game\Steam\steamapps\common\Turing Complete\Turing Complete.exe"
)
EXPECTED_EXE_SHA256 = "c93f5e8e826050c3f92e2b3891d26fcdfc933658614185cb9b2eb6a34c5b8d1c"


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def literal_texts(manifest: dict[str, Any], target: str) -> set[str]:
    return {row["text"] for row in manifest["targets"][target]["literals"]}


def window_text(xref: dict[str, Any]) -> str:
    return "\n".join(row["text"] for row in xref["window"])


def build_certificate(executable: Path) -> dict[str, Any]:
    manifest_path = NATIVE / "manifest.json"
    xrefs_path = NATIVE / "xrefs.json"
    manifest = load_json(manifest_path)
    xrefs = load_json(xrefs_path)

    if not executable.is_file():
        raise FileNotFoundError(executable)
    executable_hash = file_sha256(executable)
    if executable_hash != EXPECTED_EXE_SHA256:
        raise AssertionError(
            "executable differs from the audited v2.1.281 image: "
            f"{executable_hash}"
        )

    store_bit_path = NATIVE / "store_bit.c"
    load_path = NATIVE / "load_and_output.c"
    store_output_path = NATIVE / "store_output.c"
    z_bus_path = NATIVE / "get_output_z_value_bus.c"
    store_bit = store_bit_path.read_text(encoding="utf-8")
    load = load_path.read_text(encoding="utf-8")
    store_output = store_output_path.read_text(encoding="utf-8")

    expected_symbols = {
        "store_bit": "store_bit__modelZsimulationZcode95gen_u2179",
        "load_and_output": "load_and_output__modelZsimulationZcode95gen_u3940",
        "store_output": "store_output__modelZsimulationZcode95gen_u2221",
    }
    for key, symbol in expected_symbols.items():
        if manifest["targets"][key]["symbol"] != symbol:
            raise AssertionError(f"unexpected {key} symbol")

    state_getter = "get_state_index__modelZsave95mongerZcommon_u5502("
    forbidden_z_tokens = (
        "get_z_state_index",
        "z_state_index",
        "_is_z",
        ".is_z",
    )
    if store_bit.count(state_getter) != 1:
        raise AssertionError("store_bit must resolve exactly one value state slot")
    if any(token in store_bit for token in forbidden_z_tokens):
        raise AssertionError("store_bit unexpectedly accesses a Z state slot")
    if not {
        "store(#SIMULATION_STATE + ",
        ", U1 ",
        ")",
    }.issubset(literal_texts(manifest, "store_bit")):
        raise AssertionError("store_bit generated-source fragments changed")

    if "store_output__modelZsimulationZcode95gen_u2221" not in load:
        raise AssertionError("load_and_output no longer delegates to store_output")
    literal_one = manifest["explicit_literals"][
        "TM__THWBxVSaWN2Zh7OMooFH0w_934"
    ]
    if literal_one["text"] != "1":
        raise AssertionError("Delay output predicate literal is no longer '1'")

    literal_xrefs = xrefs["symbols"]["literal_one"]["xrefs"]
    fixed_drive_calls = [
        row
        for row in literal_xrefs
        if "load_and_output__modelZsimulationZcode95gen_u3940" in window_text(row)
        and "TM__THWBxVSaWN2Zh7OMooFH0w_934" in window_text(row)
        and "call    r10" in window_text(row)
    ]
    if not fixed_drive_calls:
        raise AssertionError("no caller passes literal '1' to load_and_output")
    delay_call = min(fixed_drive_calls, key=lambda row: int(row["from"], 16))
    load_xrefs = xrefs["symbols"]["load_and_output"]["xrefs"]
    delay_load_refs = [
        row
        for row in load_xrefs
        if row["function_name"] == delay_call["function_name"]
        and 0 <= int(delay_call["from"], 16) - int(row["from"], 16) < 0x100
        and "case 13" in window_text(row)
    ]
    if not delay_load_refs:
        raise AssertionError("fixed-drive call is no longer in component case 13")

    store_xrefs = xrefs["symbols"]["store_bit"]["xrefs"]
    delay_store_calls = [
        row
        for row in store_xrefs
        if row["function_name"] == delay_call["function_name"]
        and 0 < int(row["from"], 16) - int(delay_call["from"], 16) < 0x200
    ]
    if not delay_store_calls:
        raise AssertionError("case 13 no longer contains the matching store_bit path")

    if "if " not in literal_texts(manifest, "store_output") or (
        " != 0 {" not in literal_texts(manifest, "store_output")
    ):
        raise AssertionError("store_output drive-predicate fragments changed")
    if "!z" not in literal_texts(manifest, "get_output_z_value_bus"):
        raise AssertionError("dynamic Z drive polarity evidence changed")
    if "get_z_state_index" not in store_output:
        raise AssertionError("store_output no longer exposes dynamic Z handling")

    component_map = HERE.parents[1] / "src" / "tc_save_lab" / "sprite_geometry.py"
    component_map_text = component_map.read_text(encoding="utf-8")
    if '13: "com_delay_line_bit.png"' not in component_map_text:
        raise AssertionError("component id 13 mapping changed")

    artifact_paths = sorted(NATIVE.glob("*.c")) + [manifest_path, xrefs_path]
    return {
        "schema": 1,
        "scope": "Turing Complete v2.1.281 native simulation code generation",
        "input": {
            "executable": str(executable),
            "executable_sha256": executable_hash,
            "image_base": manifest["image_base"],
        },
        "artifact_sha256": {
            path.relative_to(HERE).as_posix(): file_sha256(path)
            for path in artifact_paths
        },
        "component": {
            "id": 13,
            "name": "com_delay_line_bit",
            "dispatcher_function": delay_call["function_name"],
            "fixed_drive_literal_xref": delay_call["from"],
            "store_bit_xref": min(
                delay_store_calls, key=lambda row: int(row["from"], 16)
            )["from"],
        },
        "assertions": {
            "store_bit_uses_one_value_state_slot": True,
            "store_bit_has_no_z_state_access": True,
            "load_path_passes_literal_one_as_drive_predicate": True,
            "store_output_treats_nonzero_predicate_as_driven": True,
            "dynamic_z_helper_returns_not_z_predicate": True,
        },
        "conclusion": (
            "Delay Bit stores only its U1 value. On the following tick its "
            "loaded value is passed to store_output with the constant non-Z "
            "predicate 1, so input high impedance is neither stored nor restored."
        ),
        "modeling_rule": (
            "Model com_delay_line_bit as one ordinary binary state bit, never "
            "as a ternary value/Z memory cell."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, default=DEFAULT_EXE)
    parser.add_argument(
        "--output", type=Path, default=HERE / "delay-z-storage-certificate.json"
    )
    args = parser.parse_args()
    certificate = build_certificate(args.executable)
    args.output.write_text(
        json.dumps(certificate, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
