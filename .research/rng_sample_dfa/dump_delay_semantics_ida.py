"""Export the native Delay Bit code-generation path without running the game.

Run this script in IDA batch mode against the already analysed v2.1.281
database.  Besides pseudocode, it records every Nim string literal referenced
by each helper.  The literals are decisive because these helpers construct the
simulation source code at runtime.
"""

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
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_sample_dfa"
    r"\delay-native-audit"
)

TARGETS = {
    "input_word": 0x140433BA5,
    "input_bit": 0x14043DE0D,
    "store_output": 0x140437079,
    "load_and_output": 0x14043DF90,
    "store_bit": 0x14043ED1A,
    "store_word": 0x14043F4C0,
    "get_output_z_value_bus": 0x140440A21,
    "get_output_z_value_bit": 0x140440E57,
}

EXPLICIT_LITERALS = (
    "TM__THWBxVSaWN2Zh7OMooFH0w_532",
    "TM__THWBxVSaWN2Zh7OMooFH0w_934",
    "TM__THWBxVSaWN2Zh7OMooFH0w_2019",
    "TM__THWBxVSaWN2Zh7OMooFH0w_2021",
)

RAW_LITERALS = {
    "TM__THWBxVSaWN2Zh7OMooFH0w_2019": 4,
    "TM__THWBxVSaWN2Zh7OMooFH0w_2021": 5,
}


def decompile(address: int) -> tuple[int, int, str]:
    function = ida_funcs.get_func(address)
    if function is None:
        raise RuntimeError(f"no function at {address:#x}")
    pseudocode = ida_hexrays.decompile(function.start_ea)
    if pseudocode is None:
        raise RuntimeError(f"decompilation failed at {address:#x}")
    text = "\n".join(
        ida_lines.tag_remove(line.line) for line in pseudocode.get_pseudocode()
    )
    return function.start_ea, function.end_ea, text + "\n"


def read_nim_string(address: int) -> str | None:
    length = ida_bytes.get_qword(address)
    pointer = ida_bytes.get_qword(address + 8)
    if not (0 <= length <= 1 << 20):
        return None
    raw = ida_bytes.get_bytes(pointer + 8, length)
    if raw is None:
        return None
    return raw.decode("utf-8", "backslashreplace")


def read_inline_nim_string(address: int) -> str | None:
    tagged_length = ida_bytes.get_qword(address)
    if tagged_length & 0x4000000000000000 == 0:
        return None
    length = tagged_length & 0x3FFFFFFFFFFFFFFF
    if length > 1 << 20:
        return None
    raw = ida_bytes.get_bytes(address + 8, length)
    if raw is None:
        return None
    return raw.decode("utf-8", "backslashreplace")


def referenced_literals(start: int, end: int) -> list[dict[str, object]]:
    rows: dict[int, dict[str, object]] = {}
    for address in idautils.Heads(start, end):
        for target in idautils.DataRefsFrom(address):
            name = ida_name.get_name(target)
            if not name.startswith("TM__"):
                continue
            value = read_nim_string(target)
            if value is None:
                continue
            row = rows.setdefault(
                target,
                {
                    "address": f"0x{target:016x}",
                    "name": name,
                    "text": value,
                    "references": [],
                },
            )
            row["references"].append(f"0x{address:016x}")
    return [rows[address] for address in sorted(rows)]


def helper_callers(address: int) -> list[dict[str, str]]:
    rows = []
    for callsite in sorted(idautils.CodeRefsTo(address, False)):
        function = ida_funcs.get_func(callsite)
        rows.append(
            {
                "callsite": f"0x{callsite:016x}",
                "caller": (
                    ida_funcs.get_func_name(function.start_ea) if function else ""
                ),
                "disassembly": ida_lines.tag_remove(
                    idc.generate_disasm_line(callsite, 0) or ""
                ),
            }
        )
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ida_auto.auto_wait()
    if not ida_hexrays.init_hexrays_plugin():
        raise RuntimeError("Hex-Rays is unavailable")

    manifest: dict[str, object] = {
        "schema": 1,
        "input_file": idc.get_input_file_path(),
        "image_base": f"0x{idaapi.get_imagebase():016x}",
        "explicit_literals": {},
        "targets": {},
    }
    for name in EXPLICIT_LITERALS:
        address = ida_name.get_name_ea(idaapi.BADADDR, name)
        if address == idaapi.BADADDR:
            raise RuntimeError(f"missing literal symbol {name}")
        manifest["explicit_literals"][name] = {
            "address": f"0x{address:016x}",
            "text": read_nim_string(address),
            "inline_text": read_inline_nim_string(address),
            "raw_hex_32": ida_bytes.get_bytes(address, 32).hex(),
            "raw_ascii": (
                ida_bytes.get_bytes(address, RAW_LITERALS[name]).decode(
                    "ascii", "backslashreplace"
                )
                if name in RAW_LITERALS
                else None
            ),
        }
    for label, address in TARGETS.items():
        start, end, text = decompile(address)
        (OUT / f"{label}.c").write_text(text, encoding="utf-8")
        manifest["targets"][label] = {
            "requested_address": f"0x{address:016x}",
            "start": f"0x{start:016x}",
            "end": f"0x{end:016x}",
            "symbol": ida_funcs.get_func_name(start),
            "literals": referenced_literals(start, end),
            "callers": helper_callers(start),
        }

    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    idc.qexit(0)


try:
    main()
except Exception as exc:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "error.txt").write_text(repr(exc) + "\n", encoding="utf-8")
    idc.qexit(1)
