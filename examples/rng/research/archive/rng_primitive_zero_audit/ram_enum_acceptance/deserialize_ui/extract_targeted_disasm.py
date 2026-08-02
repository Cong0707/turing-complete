"""Export narrow RAM UI disassembly and the top-level save version router.

Run under IDA in batch mode against the existing Turing Complete database.
This deliberately does not decompile the very large component panel function.
"""

from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_hexrays
import ida_kernwin
import ida_lines
import ida_name
import idautils
import idc


OUTPUT_DIR = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit"
    r"\ram_enum_acceptance\deserialize_ui"
)

RANGES = {
    "ui_ram_depth": (0x14076C360, 0x14076C730),
    "ui_ram_mode": (0x14077DEA0, 0x14077E910),
}


def clean_name(ea: int) -> str:
    return ida_name.get_name(ea) or idc.get_func_name(ea) or ""


def dump_range(label: str, start: int, end: int) -> None:
    rows = [f"range\t{start:#x}-{end:#x}"]
    for ea in idautils.Heads(start, end):
        if not ida_bytes.is_code(ida_bytes.get_full_flags(ea)):
            continue
        size = ida_bytes.get_item_size(ea)
        raw = ida_bytes.get_bytes(ea, size) or b""
        encoded = " ".join(f"{byte:02x}" for byte in raw)
        disasm = ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or "")
        rows.append(f"{ea:016x}  {encoded:<32}  {disasm}")
    (OUTPUT_DIR / f"{label}.disasm.txt").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def decompile_parse_state() -> None:
    ea = 0x1401C05E5
    function = ida_funcs.get_func(ea)
    if function is None:
        raise RuntimeError(f"No function at {ea:#x}")
    pseudocode = ida_hexrays.decompile(function)
    if pseudocode is None:
        raise RuntimeError("Decompiler returned None for parse_state")
    lines = [
        ida_lines.tag_remove(line.line) for line in pseudocode.get_pseudocode()
    ]
    header = (
        f"// address: {function.start_ea:#x}-{function.end_ea:#x}\n"
        f"// name: {clean_name(function.start_ea)}\n"
    )
    (OUTPUT_DIR / "parse_state.c").write_text(
        header + "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> None:
    ida_auto.auto_wait()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not ida_hexrays.init_hexrays_plugin():
        raise RuntimeError("Hex-Rays decompiler is unavailable")
    for label, bounds in RANGES.items():
        dump_range(label, *bounds)
    decompile_parse_state()
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"EXTRACT_ERROR: {exc}")
    ida_kernwin.warning(str(exc))
    idc.qexit(1)
