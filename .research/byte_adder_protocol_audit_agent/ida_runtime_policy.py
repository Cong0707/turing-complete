"""只读导出关卡元件许可与动态成本覆盖路径的关键反编译证据。"""

from __future__ import annotations

import json
from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_hexrays
import ida_lines
import ida_name
import idaapi
import idautils


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\byte_adder_protocol_audit_agent\ida_runtime_policy.json"
)

TARGETS = (
    "is_score_unlocked__modelZboardZschematics_u1782",
    "get_budget__modelZboardZschematics_u2168",
    "preorder__modelZsimulationZcompile95thread_u4293",
    "add_cost__modelZscores_u2110",
    "import_costs__modelZscores_u2127",
    "get_cost__modelZscores_u2321",
    "complete_level__modelZutilities_u8913",
    "process_network_responses__presenterZutilities_u38439",
    "load_level__modelZutilities_u7564",
    "get_level_access__modelZcampaigns_u16649",
    "get_unlocked_levels__modelZcampaigns_u16586",
)

STRING_NEEDLES = (
    "not unlocked in this level",
    "uses a {name} component not unlocked",
)

KEY_SYMBOLS = (
    "TM__DRGBjVoeyzCuYwSWCgAUCw_79",
    "TM__DRGBjVoeyzCuYwSWCgAUCw_80",
)


def clean(value: object) -> str:
    return ida_lines.tag_remove(str(value))


def function_record(ea: int) -> dict[str, object]:
    function = ida_funcs.get_func(ea)
    if function is None:
        return {"address": f"0x{ea:016x}", "error": "not a function"}
    callers: list[dict[str, str]] = []
    for xref in idautils.CodeRefsTo(function.start_ea, False):
        owner = ida_funcs.get_func(xref)
        callers.append(
            {
                "from": f"0x{xref:016x}",
                "function": "" if owner is None else ida_name.get_name(owner.start_ea),
            }
        )
    callees: list[dict[str, str]] = []
    seen: set[tuple[int, int]] = set()
    for insn in idautils.FuncItems(function.start_ea):
        for target in idautils.CodeRefsFrom(insn, False):
            callee = ida_funcs.get_func(target)
            if callee is None:
                continue
            key = (insn, callee.start_ea)
            if key in seen:
                continue
            seen.add(key)
            callees.append(
                {
                    "at": f"0x{insn:016x}",
                    "target": f"0x{callee.start_ea:016x}",
                    "function": ida_name.get_name(callee.start_ea),
                }
            )
    try:
        pseudocode = clean(ida_hexrays.decompile(function.start_ea))
    except Exception as error:  # pragma: no cover - IDA environment only
        pseudocode = f"{type(error).__name__}: {error}"
    return {
        "name": ida_name.get_name(function.start_ea),
        "address": f"0x{function.start_ea:016x}",
        "callers": callers,
        "callees": callees,
        "pseudocode": pseudocode,
    }


def data_record(name: str) -> dict[str, object]:
    ea = ida_name.get_name_ea(idaapi.BADADDR, name)
    if ea == idaapi.BADADDR:
        return {"name": name, "error": "missing"}
    raw = ida_bytes.get_bytes(ea, 96) or b""
    return {
        "name": name,
        "address": f"0x{ea:016x}",
        "qword": ida_bytes.get_qword(ea),
        "bytes_hex": raw.hex(),
        "ascii_prefix": raw.split(b"\0", 1)[0].decode("utf-8", errors="replace"),
    }


def main() -> None:
    ida_auto.auto_wait()
    targets: list[dict[str, object]] = []
    for name in TARGETS:
        ea = ida_name.get_name_ea(idaapi.BADADDR, name)
        if ea == idaapi.BADADDR:
            targets.append({"name": name, "error": "missing"})
        else:
            targets.append(function_record(ea))

    strings: list[dict[str, object]] = []
    for item in idautils.Strings():
        value = str(item)
        if not any(needle in value for needle in STRING_NEEDLES):
            continue
        refs: list[dict[str, object]] = []
        owners: dict[int, dict[str, object]] = {}
        for delta in range(-32, 33, 8):
            for xref in idautils.XrefsTo(item.ea + delta):
                owner = ida_funcs.get_func(xref.frm)
                record = {
                    "from": f"0x{xref.frm:016x}",
                    "target_delta": delta,
                    "function": "" if owner is None else ida_name.get_name(owner.start_ea),
                }
                refs.append(record)
                if owner is not None:
                    owners.setdefault(owner.start_ea, function_record(owner.start_ea))
        strings.append(
            {
                "address": f"0x{item.ea:016x}",
                "text": value,
                "references": refs,
                "owner_functions": list(owners.values()),
            }
        )

    matching_names = [
        {"address": f"0x{ea:016x}", "name": name}
        for ea, name in idautils.Names()
        if any(
            token in name.lower()
            for token in (
                "unlock",
                "allowed_component",
                "component_allowed",
                "level_access",
                "get_budget",
            )
        )
    ]
    OUTPUT.write_text(
        json.dumps(
            {
                "targets": targets,
                "rejection_strings": strings,
                "score_unlock_key_symbols": [data_record(name) for name in KEY_SYMBOLS],
                "matching_names": matching_names,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    idaapi.qexit(0)


main()
