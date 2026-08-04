"""Export the current EXE code-generator bodies for all pre-Byte-Adder kinds.

This is an IDAPython batch script.  It only reads the temporary research IDB
and writes one JSON audit artifact selected by ``TC_IDA_OUTPUT``.
"""

from __future__ import annotations

import hashlib
import json
import os
import re

import ida_auto
import ida_bytes
import ida_funcs
import ida_lines
import ida_nalt
import ida_xref
import idaapi
import idautils
import idc


OUTPUT = os.environ.get("TC_IDA_OUTPUT")
FUNCTION_EA = 0x1404432F8
SELECTED_KINDS = (
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    15,
    16,
    17,
    18,
    21,
    25,
    109,
    110,
    111,
    112,
)

# kind 13 intentionally contains an entry reused by RAM kinds 55/119.  The
# next *semantic* component body is kind 14, not the first numerically greater
# switch target inside the Delay Line body.
CASE_END_OVERRIDES = {13: 0x14044CDCE}


def mapped(ea: int, size: int = 1) -> bool:
    return ea != idaapi.BADADDR and all(ida_bytes.is_loaded(ea + i) for i in range(size))


def decode_string_at(ea: int) -> str | None:
    raw = idc.get_strlit_contents(ea, -1, idc.STRTYPE_C)
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw
    try:
        return bytes(raw).decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        return None


def static_text_pair(ea: int, limit: int) -> str | None:
    """Decode a Nim (length, payload-object pointer) pair used by appendString."""
    if idc.print_insn_mnem(ea) != "mov":
        return None
    length_address = idc.get_operand_value(ea, 1)
    next_ea = idc.next_head(ea, limit)
    if next_ea == idc.BADADDR or idc.print_insn_mnem(next_ea) != "mov":
        return None
    pointer_address = idc.get_operand_value(next_ea, 1)
    if not (mapped(length_address, 8) and mapped(pointer_address, 8)):
        return None
    length = ida_bytes.get_qword(length_address)
    pointer = ida_bytes.get_qword(pointer_address)
    if not (0 < length <= 16384 and mapped(pointer + 8, length)):
        return None
    raw = ida_bytes.get_bytes(pointer + 8, length)
    if raw is None:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def switch_targets(func) -> tuple[int, dict[int, int], dict[int, list[int]]]:
    switch_ea = idaapi.BADADDR
    kind_to_target: dict[int, int] = {}
    target_to_kinds: dict[int, list[int]] = {}
    for ea in idautils.Heads(func.start_ea, func.end_ea):
        if not ida_bytes.is_code(ida_bytes.get_flags(ea)):
            continue
        info = ida_nalt.get_switch_info(ea)
        if info is None:
            continue
        result = ida_xref.calc_switch_cases(ea, info)
        if result is None:
            continue
        switch_ea = ea
        for index in range(len(result.cases)):
            target = int(result.targets[index])
            cases = [int(result.cases[index][i]) for i in range(len(result.cases[index]))]
            target_to_kinds.setdefault(target, []).extend(cases)
            for kind in cases:
                if kind in kind_to_target and kind_to_target[kind] != target:
                    raise RuntimeError(f"kind {kind} has multiple targets")
                kind_to_target[kind] = target
    if switch_ea == idaapi.BADADDR:
        raise RuntimeError("cannot find codegen switch")
    return switch_ea, kind_to_target, target_to_kinds


def main() -> None:
    if not OUTPUT:
        raise RuntimeError("TC_IDA_OUTPUT is required")
    ida_auto.auto_wait()
    func = ida_funcs.get_func(FUNCTION_EA)
    if func is None:
        raise RuntimeError("cannot resolve add_circuit_code")
    switch_ea, kind_to_target, target_to_kinds = switch_targets(func)
    missing = sorted(set(SELECTED_KINDS) - set(kind_to_target))
    if missing:
        raise RuntimeError(f"missing switch targets: {missing}")
    ordered_targets = sorted(target_to_kinds)

    rows = []
    for kind in SELECTED_KINDS:
        start = kind_to_target[kind]
        greater = [target for target in ordered_targets if target > start]
        end = CASE_END_OVERRIDES.get(kind, greater[0] if greater else func.end_ea)
        if not (func.start_ea <= start < end <= func.end_ea):
            raise RuntimeError(f"invalid range for kind {kind}: {start:x}..{end:x}")

        instructions = []
        referenced_names: set[str] = set()
        direct_calls = []
        strings: dict[tuple[int, str], dict[str, object]] = {}
        raw_parts = []
        for ea in idautils.Heads(start, end):
            if not ida_bytes.is_code(ida_bytes.get_flags(ea)):
                continue
            size = idc.get_item_size(ea)
            raw = ida_bytes.get_bytes(ea, size) or b""
            raw_parts.append(raw)
            text = ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or "")
            for token in re.findall(r"[A-Za-z_.$?][A-Za-z0-9_.$?@]*", text):
                if "__modelZ" in token or token.startswith("PROTOTYPES__"):
                    referenced_names.add(token)
            code_refs = []
            for ref in idautils.CodeRefsFrom(ea, False):
                name = idc.get_name(ref) or idc.get_func_name(ref)
                code_refs.append({"address": f"0x{int(ref):016x}", "name": name})
                if name:
                    referenced_names.add(name)
            if idc.print_insn_mnem(ea) == "call":
                direct_calls.append(
                    {
                        "address": f"0x{ea:016x}",
                        "text": text,
                        "targets": code_refs,
                    }
                )
            data_refs = []
            for ref in idautils.DataRefsFrom(ea):
                name = idc.get_name(ref)
                value = decode_string_at(ref)
                data_refs.append(
                    {
                        "address": f"0x{int(ref):016x}",
                        "name": name,
                        "string": value,
                    }
                )
                if name:
                    referenced_names.add(name)
                if value:
                    strings[(int(ref), value)] = {
                        "address": f"0x{int(ref):016x}",
                        "value": value,
                        "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
                        "source": "direct-data-reference",
                    }
            static_text = static_text_pair(ea, end)
            if static_text:
                strings[(ea, static_text)] = {
                    "address": f"0x{ea:016x}",
                    "value": static_text,
                    "sha256": hashlib.sha256(static_text.encode("utf-8")).hexdigest(),
                    "source": "nim-length-pointer-pair",
                }
            instructions.append(
                {
                    "address": f"0x{ea:016x}",
                    "bytes": raw.hex(),
                    "text": text,
                    "code_refs": code_refs,
                    "data_refs": data_refs,
                    "static_text_pair": static_text,
                }
            )
        rows.append(
            {
                "kind": kind,
                "target": f"0x{start:016x}",
                "range_end": f"0x{end:016x}",
                "range_rule": "explicit-delay-line-override" if kind in CASE_END_OVERRIDES else "next-switch-target",
                "instruction_count": len(instructions),
                "code_bytes_sha256": hashlib.sha256(b"".join(raw_parts)).hexdigest(),
                "referenced_names": sorted(referenced_names),
                "direct_calls": direct_calls,
                "static_strings": sorted(strings.values(), key=lambda item: (item["address"], item["value"])),
                "instructions": instructions,
            }
        )

    encoded = json.dumps(
        {
            "schema": 1,
            "input_file": idc.get_input_file_path(),
            "function": idc.get_func_name(func.start_ea),
            "function_address": f"0x{func.start_ea:016x}",
            "function_end": f"0x{func.end_ea:016x}",
            "switch_address": f"0x{switch_ea:016x}",
            "selected_kinds": list(SELECTED_KINDS),
            "missing_kinds": [],
            "cases": rows,
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n"
    with open(OUTPUT, "wb") as handle:
        handle.write(encoded.encode("utf-8"))
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"PRETARGET_CODEGEN_CASE_ERROR: {type(exc).__name__}: {exc}")
    idc.qexit(1)
