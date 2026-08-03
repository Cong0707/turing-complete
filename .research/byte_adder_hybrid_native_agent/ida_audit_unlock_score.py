"""Read-only audit of unlock and score eligibility functions and callers."""

from __future__ import annotations

import json
import os
from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_name
import ida_nalt
import idaapi
import idautils
import idc


OUT = Path(os.environ.get(
    "BYTE_ADDER_UNLOCK_SCORE_OUT",
    r"D:\Develop\Other\turing-complete\.research\byte_adder_hybrid_native_agent"
    r"\unlock_score_static_audit.json",
))

TARGETS = (
    "is_score_unlocked__modelZboardZschematics_u1782",
    "is_unlocked__modelZcampaigns_u16787",
    "get_cost__modelZscores_u2321",
    "import_costs__modelZscores_u2127",
    "insert_cost__modelZscores_u13",
    "insert_cost__modelZscores_u49",
    "get_component_cost__presenterZutilitiesZhelper95functions_u5874",
    "get_component_cost__presenterZutilitiesZhelper95functions_u5877",
)


def decompile(ea: int) -> str | None:
    try:
        return str(ida_hexrays.decompile(ea))
    except Exception as exc:
        return f"DECOMPILE_ERROR: {type(exc).__name__}: {exc}"


def callers(ea: int) -> list[dict[str, object]]:
    found = []
    seen = set()
    for xref in idautils.XrefsTo(ea):
        func = ida_funcs.get_func(xref.frm)
        start = func.start_ea if func else idaapi.BADADDR
        key = (xref.frm, start)
        if key in seen:
            continue
        seen.add(key)
        found.append({
            "from": f"0x{xref.frm:016x}",
            "function": None if start == idaapi.BADADDR else f"0x{start:016x}",
            "name": "" if start == idaapi.BADADDR else ida_name.get_name(start),
            "pseudocode": None if start == idaapi.BADADDR else decompile(start),
        })
    return found


def main() -> None:
    ida_auto.auto_wait()
    records = {}
    for name in TARGETS:
        ea = ida_name.get_name_ea(idaapi.BADADDR, name)
        records[name] = {
            "address": None if ea == idaapi.BADADDR else f"0x{ea:016x}",
            "pseudocode": None if ea == idaapi.BADADDR else decompile(ea),
            "callers": [] if ea == idaapi.BADADDR else callers(ea),
        }
    relevant_names = [
        {"address": f"0x{ea:016x}", "name": name}
        for ea, name in idautils.Names()
        if any(token in name.lower() for token in (
            "unlock", "scoreable", "score_unlocked", "validate_schematic",
            "verify_schematic", "not_unlocked", "component_cost",
        ))
    ]
    digest = ida_nalt.retrieve_input_file_sha256()
    OUT.write_text(json.dumps({
        "input_sha256": digest.hex() if digest else None,
        "targets": records,
        "relevant_names": relevant_names,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"AUDIT_ERROR: {type(exc).__name__}: {exc}")
    idc.qexit(1)
