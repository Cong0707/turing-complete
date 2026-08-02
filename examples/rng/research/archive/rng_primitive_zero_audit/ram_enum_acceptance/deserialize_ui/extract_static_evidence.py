"""Export static evidence for RAM setting deserialization and UI handling.

Run only under IDA in batch mode against the existing Turing Complete database.
"""

from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_hexrays
import ida_idp
import ida_kernwin
import ida_lines
import ida_name
import ida_search
import ida_xref
import idautils
import idc


OUTPUT_DIR = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit"
    r"\ram_enum_acceptance\deserialize_ui"
)

TARGETS = {
    "get_component_v15": 0x1401BC87F,
    "get_components_v15": 0x1401BE0A7,
    "parse_v15": 0x1401BEB42,
    "deserialize_package": 0x14061F93E,
    "add_component_save_monger": 0x1401C0FF3,
    "get_setting": 0x1405DBD75,
    "set_setting": 0x1405DB3DF,
    "get_byte_buffer_size": 0x1405DBBA9,
    "set_byte_buffer_size": 0x140671CB0,
    "component_panel": 0x1406698B6,
    "deserialize_versions_router": 0x14061E2FD,
    "load_schematic_raw": 0x14027C2C6,
    "load_schematic": 0x14027E073,
    "load_level_model": 0x1405A19FB,
    "board_add_component": 0x140243DCA,
    "config_listbox_ram_mode": 0x1407581CD,
    "config_listbox_ram_depth": 0x14074FA52,
    "get_ram_pipeline_depth": 0x14021A94F,
    "create_buffer_for_component": 0x14023F590,
}

GLOBALS = {
    "component_default_setting": 0x140985060,
    "memory_components": 0x140985080,
}


def clean_name(ea: int) -> str:
    return ida_name.get_name(ea) or idc.get_func_name(ea) or ""


def function_context(ea: int) -> str:
    function = ida_funcs.get_func(ea)
    if function is None:
        return f"{ea:#x}\t<no function>"
    return (
        f"{ea:#x}\t{function.start_ea:#x}-{function.end_ea:#x}"
        f"\t{clean_name(function.start_ea)}"
    )


def decompile(label: str, ea: int) -> None:
    function = ida_funcs.get_func(ea)
    if function is None:
        (OUTPUT_DIR / f"{label}.error.txt").write_text(
            f"No function at {ea:#x}\n", encoding="utf-8"
        )
        return
    try:
        pseudocode = ida_hexrays.decompile(function)
        if pseudocode is None:
            raise RuntimeError("decompiler returned None")
        lines = [
            ida_lines.tag_remove(line.line)
            for line in pseudocode.get_pseudocode()
        ]
        header = (
            f"// address: {function.start_ea:#x}-{function.end_ea:#x}\n"
            f"// name: {clean_name(function.start_ea)}\n"
        )
        (OUTPUT_DIR / f"{label}.c").write_text(
            header + "\n".join(lines) + "\n", encoding="utf-8"
        )
    except Exception as exc:
        (OUTPUT_DIR / f"{label}.error.txt").write_text(
            f"Decompile failed at {function.start_ea:#x}: {exc}\n",
            encoding="utf-8",
        )


def dump_xrefs(label: str, ea: int) -> None:
    rows = [f"target\t{ea:#x}\t{clean_name(ea)}"]
    for xref in idautils.XrefsTo(ea, 0):
        rows.append(
            f"xref\t{xref.frm:#x}\ttype={xref.type}\t{function_context(xref.frm)}"
        )
    (OUTPUT_DIR / f"xrefs_{label}.txt").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def dump_immediate(value: int, label: str) -> None:
    rows = []
    seen = set()
    ea = ida_search.find_imm(0, ida_search.SEARCH_DOWN, value)[0]
    while ea != ida_idaapi.BADADDR:
        function = ida_funcs.get_func(ea)
        key = (ea, function.start_ea if function else None)
        if key not in seen:
            seen.add(key)
            disasm = ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or "")
            rows.append(f"{function_context(ea)}\t{disasm}")
        next_ea = ida_bytes.next_head(ea, idc.get_inf_attr(idc.INF_MAX_EA))
        if next_ea == ida_idaapi.BADADDR:
            break
        ea = ida_search.find_imm(next_ea, ida_search.SEARCH_DOWN, value)[0]
    (OUTPUT_DIR / f"immediate_{label}.txt").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def dump_named_functions() -> None:
    needles = (
        "ram",
        "setting",
        "buffer_size",
        "component_panel",
        "deserialize",
        "get_component",
        "parse__modelZsave95monger",
    )
    rows = []
    for ea in idautils.Functions():
        name = clean_name(ea)
        lowered = name.lower()
        if any(needle.lower() in lowered for needle in needles):
            function = ida_funcs.get_func(ea)
            rows.append(f"{ea:#x}-{function.end_ea:#x}\t{name}")
    (OUTPUT_DIR / "named_functions.txt").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def main() -> None:
    ida_auto.auto_wait()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not ida_hexrays.init_hexrays_plugin():
        raise RuntimeError("Hex-Rays decompiler is unavailable")
    ida_idp.process_config_directive("MAX_FUNCSIZE = 512")

    for label, ea in TARGETS.items():
        decompile(label, ea)
        dump_xrefs(label, ida_funcs.get_func(ea).start_ea)
    for label, ea in GLOBALS.items():
        dump_xrefs(label, ea)
    dump_immediate(118, "118_ram_kind")
    dump_named_functions()
    idc.qexit(0)


try:
    import ida_idaapi

    main()
except Exception as exc:
    print(f"EXTRACT_ERROR: {exc}")
    ida_kernwin.warning(str(exc))
    idc.qexit(1)
