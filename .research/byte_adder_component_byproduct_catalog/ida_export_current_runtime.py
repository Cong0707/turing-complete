"""Export current runtime cost, permission, and tri-state evidence from IDA.

This script is deliberately address-independent: every object is resolved by
its current symbol name in the analyzed database.  It reads the input binary
and IDB and writes only ``TC_IDA_OUTPUT``.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct

import ida_auto
import ida_bytes
import ida_funcs
import ida_hexrays
import ida_nalt
import idaapi
import idautils
import idc


FUNCTION_NEEDLES = (
    "is_free_component_type__modelZscores",
    "get_gate_cost__modelZscores",
    "get_level_score__modelZscores",
    "get_delay_cost__modelZscores",
    "get_cost__modelZscores",
    "add_cost__modelZscores",
    "import_costs__modelZscores",
    "get_all_costs__modelZscores",
    "is_score_unlocked__modelZboardZschematics",
    "get_budget__modelZboardZschematics",
    "is_unlocked__modelZcampaigns",
    "get_completed_levels__modelZutilities",
    "get_level_unlockable_components__presenterZutilities",
    "store_output_early_return__modelZsimulationZcode95gen",
    "store_output__modelZsimulationZcode95gen",
    "is_z__presenterZutilities",
    "update_short_circuit_error__presenterZutilities",
)

SCORE_TABLE_PREFIX = "DEFAULT_COMPONENT_SCORES__modelZscores"
TEMPLATE_ADDRESS_MIN = 0x140A30000
TEMPLATE_ADDRESS_MAX = 0x140A39000
TEMPLATE_NEEDLES = (
    "_is_z",
    "and_field_",
    "short_circuit",
    "halt()",
)


def signed_qword(ea: int) -> int:
    value = ida_bytes.get_qword(ea)
    return value - (1 << 64) if value & (1 << 63) else value


def find_named(prefix: str) -> tuple[int, str]:
    matches = [(ea, name) for ea, name in idautils.Names() if prefix in name]
    if len(matches) != 1:
        raise RuntimeError(f"expected one name containing {prefix!r}, got {matches}")
    return matches[0]


def function_record(ea: int, name: str) -> dict[str, object]:
    func = ida_funcs.get_func(ea)
    if func is None:
        raise RuntimeError(f"no function at {ea:#x}: {name}")
    raw = ida_bytes.get_bytes(func.start_ea, func.end_ea - func.start_ea)
    try:
        pseudocode = str(ida_hexrays.decompile(ea))
        decompile_error = None
    except Exception as exc:
        pseudocode = ""
        decompile_error = repr(exc)
    return {
        "address": f"0x{func.start_ea:016x}",
        "end_address": f"0x{func.end_ea:016x}",
        "name": name,
        "size": func.end_ea - func.start_ea,
        "machine_sha256": hashlib.sha256(raw or b"").hexdigest(),
        "pseudocode_sha256": hashlib.sha256(pseudocode.encode("utf-8")).hexdigest(),
        "pseudocode": pseudocode,
        "decompile_error": decompile_error,
    }


def score_table_record() -> dict[str, object]:
    table, name = find_named(SCORE_TABLE_PREFIX)
    capacity = ida_bytes.get_qword(table)
    allocation = ida_bytes.get_qword(table + 8)
    count = ida_bytes.get_qword(table + 16)
    if not (capacity == 256 and count == 125 and allocation):
        raise RuntimeError(
            f"unexpected score table descriptor: {(capacity, allocation, count)}"
        )
    allocation_header = ida_bytes.get_qword(allocation)
    rows = []
    for slot in range(capacity):
        base = allocation + 8 + 32 * slot
        hash_value = ida_bytes.get_qword(base)
        kind = ida_bytes.get_qword(base + 8)
        gate = signed_qword(base + 16)
        delay = signed_qword(base + 24)
        if hash_value:
            rows.append(
                {
                    "slot": slot,
                    "hash": f"0x{hash_value:016x}",
                    "kind": kind,
                    "default_gate": gate,
                    "default_delay": delay,
                }
            )
        elif kind or gate or delay:
            raise RuntimeError(f"partially populated score slot {slot}")
    if len(rows) != count or {row["kind"] for row in rows} != set(range(125)):
        raise RuntimeError("score table does not contain kinds 0..124 exactly once")
    return {
        "symbol": name,
        "address": f"0x{table:016x}",
        "capacity": capacity,
        "allocation_address": f"0x{allocation:016x}",
        "allocation_header": f"0x{allocation_header:016x}",
        "count": count,
        "rows": sorted(rows, key=lambda row: row["kind"]),
    }


def template_strings() -> list[dict[str, object]]:
    result = []
    for item in idautils.Strings():
        value = str(item)
        if not TEMPLATE_ADDRESS_MIN <= item.ea < TEMPLATE_ADDRESS_MAX:
            continue
        if not any(needle.lower() in value.lower() for needle in TEMPLATE_NEEDLES):
            continue
        result.append(
            {
                "address": f"0x{item.ea:016x}",
                "value": value,
                "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
            }
        )
    return result


def main() -> None:
    ida_auto.auto_wait()
    selected = []
    for ea in idautils.Functions():
        name = idc.get_func_name(ea)
        if any(needle in name for needle in FUNCTION_NEEDLES):
            selected.append(function_record(ea, name))

    expected_minimum = len(FUNCTION_NEEDLES)
    if len(selected) < expected_minimum:
        raise RuntimeError(
            f"missing selected functions: got {len(selected)}, want >= {expected_minimum}"
        )

    digest = ida_nalt.retrieve_input_file_sha256()
    output = os.environ.get("TC_IDA_OUTPUT")
    if not output:
        raise RuntimeError("TC_IDA_OUTPUT is required")
    payload = {
        "schema": 1,
        "input_file": ida_nalt.get_input_file_path(),
        "input_sha256": digest.hex() if digest else None,
        "image_base": f"0x{idaapi.get_imagebase():016x}",
        "score_table": score_table_record(),
        "functions": selected,
        "codegen_template_strings": template_strings(),
    }
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"EXPORT_ERROR: {type(exc).__name__}: {exc}")
    idc.qexit(1)
