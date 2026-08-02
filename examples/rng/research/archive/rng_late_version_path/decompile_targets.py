"""Export the narrow runtime paths that can write Component.is_late_version."""

from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_lines
import ida_name
import idc


OUTPUT_DIR = Path(r"D:\Develop\Other\turing-complete\.research\rng_late_version_path\ida")

TARGETS = {
    "recursive_load_custom": 0x14067F85F,
    "recursive_load_hub": 0x140681A0B,
    "save_board": 0x1402A649C,
    "serialize_server_request": 0x1404BEFE0,
    "load_schematic_raw": 0x14027C2C6,
    "board_add_component": 0x140243DCA,
    "add_clipboard_to_board": 0x1405E3B59,
    "add_ui_component": 0x1405DA5F4,
    "apply_load_morph": 0x14059F111,
}


def main() -> None:
    ida_auto.auto_wait()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not ida_hexrays.init_hexrays_plugin():
        raise RuntimeError("Hex-Rays decompiler unavailable")

    failures = []
    for label, ea in TARGETS.items():
        try:
            func = ida_funcs.get_func(ea)
            if func is None:
                raise RuntimeError(f"no function at {ea:#x}")
            code = ida_hexrays.decompile(func)
            if code is None:
                raise RuntimeError("decompile returned None")
            name = ida_name.get_name(func.start_ea) or idc.get_func_name(func.start_ea)
            lines = [ida_lines.tag_remove(line.line) for line in code.get_pseudocode()]
            header = f"// address: {func.start_ea:#x}-{func.end_ea:#x}\n// name: {name}\n"
            (OUTPUT_DIR / f"{label}.c").write_text(
                header + "\n".join(lines) + "\n", encoding="utf-8"
            )
        except Exception as exc:
            failures.append(f"{label} {ea:#x}: {exc}")
    for failure in failures:
        print(f"FAIL: {failure}")
    idc.qexit(1 if failures else 0)


try:
    main()
except Exception as exc:
    print(f"DECOMPILE_ERROR: {exc}")
    idc.qexit(1)
