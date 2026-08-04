"""Export current 2.1.292 cost-frontier insertion and import call paths."""

from __future__ import annotations

import hashlib
import json
import os

import ida_auto
import ida_bytes
import ida_funcs
import ida_hexrays
import ida_nalt
import idaapi
import idautils
import idc


OUTPUT = os.environ.get("TC_IDA_OUTPUT")
TARGET_PREFIXES = (
    "insert_cost__modelZscores",
    "add_cost__modelZscores",
    "import_costs__modelZscores",
    "get_level_score__modelZscores",
)
CONTEXT_PREFIXES = (
    "game_initialize__modelZinitialize",
    "complete_level__modelZutilities",
    "process_network_responses__presenterZutilities",
    "get_displayed_level_scores__presenterZutilities",
    "get_component_cost__presenterZutilities",
)


def record(ea: int) -> dict[str, object]:
    func = ida_funcs.get_func(ea)
    if func is None:
        raise RuntimeError(f"no function at {ea:#x}")
    raw = ida_bytes.get_bytes(func.start_ea, func.end_ea - func.start_ea) or b""
    try:
        pseudocode = str(ida_hexrays.decompile(func.start_ea))
        decompile_error = None
    except Exception as exc:
        pseudocode = ""
        decompile_error = repr(exc)
    return {
        "address": f"0x{func.start_ea:016x}",
        "end_address": f"0x{func.end_ea:016x}",
        "name": idc.get_func_name(func.start_ea),
        "size": func.end_ea - func.start_ea,
        "machine_sha256": hashlib.sha256(raw).hexdigest(),
        "pseudocode_sha256": hashlib.sha256(pseudocode.encode("utf-8")).hexdigest(),
        "pseudocode": pseudocode,
        "decompile_error": decompile_error,
    }


def main() -> None:
    if not OUTPUT:
        raise RuntimeError("TC_IDA_OUTPUT is required")
    ida_auto.auto_wait()
    all_functions = [(ea, idc.get_func_name(ea)) for ea in idautils.Functions()]
    target_eas = {
        ea for ea, name in all_functions if name.startswith(TARGET_PREFIXES)
    }
    selected = set(target_eas)
    selected.update(
        ea for ea, name in all_functions if name.startswith(CONTEXT_PREFIXES)
    )
    call_edges = []
    for target in sorted(target_eas):
        for caller in idautils.CodeRefsTo(target, False):
            func = ida_funcs.get_func(caller)
            if func is None:
                continue
            selected.add(func.start_ea)
            call_edges.append(
                {
                    "caller_address": f"0x{func.start_ea:016x}",
                    "caller": idc.get_func_name(func.start_ea),
                    "call_site": f"0x{caller:016x}",
                    "callee_address": f"0x{target:016x}",
                    "callee": idc.get_func_name(target),
                }
            )
    digest = ida_nalt.retrieve_input_file_sha256()
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "schema": 1,
                "input_file": ida_nalt.get_input_file_path(),
                "input_sha256": digest.hex() if digest else None,
                "image_base": f"0x{idaapi.get_imagebase():016x}",
                "call_edges": call_edges,
                "functions": [record(ea) for ea in sorted(selected)],
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
        handle.write("\n")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"COST_IMPORT_EXPORT_ERROR: {type(exc).__name__}: {exc}")
    idc.qexit(1)
