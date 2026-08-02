"""Decompile only the small helpers needed to audit Foundry input-buffer Z."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_kernwin
import ida_lines
import ida_name
import idautils
import idc


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_cost_reverse\ida_custom_io_helpers.c"
)
TARGETS = {
    "store_output": 0x140437079,
    "store_output_early_return": 0x140436D0B,
    "get_output_z_value_1": 0x140440A21,
    "get_output_z_value_2": 0x140440E57,
}


def decompile(address: int) -> str:
    function = ida_funcs.get_func(address)
    if function is None:
        return f"<no function at {address:#x}>"
    pseudocode = ida_hexrays.decompile(function)
    if pseudocode is None:
        return f"<decompile failed at {function.start_ea:#x}>"
    return "\n".join(
        ida_lines.tag_remove(line.line) for line in pseudocode.get_pseudocode()
    )


def main() -> None:
    ida_auto.auto_wait()
    if not ida_hexrays.init_hexrays_plugin():
        raise RuntimeError("Hex-Rays unavailable")
    sections: list[str] = []
    for label, address in TARGETS.items():
        sections.append(f"===== {label} {address:#x} =====")
        sections.append(decompile(address))
    for address, name in idautils.Names():
        if name.startswith("input__modelZsimulationZcode95gen_u"):
            sections.append(f"===== {name} {address:#x} =====")
            sections.append(decompile(address))
    OUTPUT.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"CUSTOM_IO_HELPERS_ERROR: {exc}")
    idc.qexit(1)
