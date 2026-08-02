"""Export small code-generation helpers and xrefs without executing the game."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_kernwin
import ida_lines
import ida_xref
import idautils
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit"
    r"\ram_tick_semantics"
)

TARGETS = {
    "add_line": 0x140436A70,
    "add_circuit_code": 0x140441388,
    "generate_source": 0x14048B0BD,
    "process_compile_request": 0x1404A7410,
    "prototype_init": 0x140237BFF,
}


def decompile_one(label: str, address: int) -> str:
    fn = ida_funcs.get_func(address)
    if fn is None:
        return f"no function at {address:#x}\n"
    try:
        pseudocode = ida_hexrays.decompile(fn)
    except Exception as exc:
        return f"decompile failed for {label} at {address:#x}: {exc}\n"
    if pseudocode is None:
        return f"decompile returned None for {label} at {address:#x}\n"
    return "\n".join(
        ida_lines.tag_remove(line.line) for line in pseudocode.get_pseudocode()
    ) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ida_auto.auto_wait()
    if not ida_hexrays.init_hexrays_plugin():
        raise RuntimeError("Hex-Rays decompiler is unavailable")

    for label in (
        "add_line",
        "generate_source",
        "process_compile_request",
        "prototype_init",
    ):
        (OUT / f"{label}.c").write_text(
            decompile_one(label, TARGETS[label]), encoding="utf-8"
        )

    rows = ["target\tcallsite\tcaller"]
    for label, target in TARGETS.items():
        for callsite in idautils.CodeRefsTo(target, False):
            caller = ida_funcs.get_func(callsite)
            rows.append(
                f"{label}\t{callsite:#x}\t"
                f"{ida_funcs.get_func_name(caller.start_ea) if caller else ''}"
            )
    (OUT / "codegen_helper_xrefs.tsv").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )
    idc.qexit(0)


try:
    main()
except Exception as exc:
    (OUT / "decompile_codegen_helpers.error.txt").write_text(
        repr(exc), encoding="utf-8"
    )
    ida_kernwin.warning(str(exc))
    idc.qexit(1)
