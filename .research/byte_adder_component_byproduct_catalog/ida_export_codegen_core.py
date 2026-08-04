"""Decompile the current simulation code generator for semantic auditing."""

from __future__ import annotations

import hashlib
import json
import os

import ida_auto
import ida_bytes
import ida_funcs
import ida_hexrays
import ida_nalt
import ida_name
import idaapi
import idc


OUTPUT = os.environ.get("TC_IDA_OUTPUT")
FUNCTION_NAMES = (
    "add_circuit_code__modelZsimulationZcode95gen_u4262",
    "input__modelZsimulationZcode95gen_u4120",
    "input__modelZsimulationZcode95gen_u4256",
    "load_and_output__modelZsimulationZcode95gen_u3938",
    "store_bit__modelZsimulationZcode95gen_u2177",
    "store_word__modelZsimulationZcode95gen_u2199",
)


def function_record(name: str) -> dict[str, object]:
    ea = ida_name.get_name_ea(idaapi.BADADDR, name)
    if ea == idaapi.BADADDR:
        raise RuntimeError(f"cannot resolve {name}")
    func = ida_funcs.get_func(ea)
    if func is None:
        raise RuntimeError(f"no function at {ea:#x}: {name}")
    raw = ida_bytes.get_bytes(func.start_ea, func.end_ea - func.start_ea) or b""
    try:
        pseudocode = str(ida_hexrays.decompile(ea))
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
    digest = ida_nalt.retrieve_input_file_sha256()
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "schema": 1,
                "input_file": ida_nalt.get_input_file_path(),
                "input_sha256": digest.hex() if digest else None,
                "image_base": f"0x{idaapi.get_imagebase():016x}",
                "functions": [function_record(name) for name in FUNCTION_NAMES],
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
    print(f"CODEGEN_EXPORT_ERROR: {type(exc).__name__}: {exc}")
    idc.qexit(1)
