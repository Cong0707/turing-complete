"""Locate RAM load/save prototype registration from descriptive strings."""

from __future__ import annotations

from pathlib import Path
import struct

import ida_auto
import ida_bytes
import ida_funcs
import ida_hexrays
import ida_kernwin
import ida_lines
import ida_name
import ida_xref
import idautils
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit"
    r"\ram_tick_semantics\ram_prototype_xrefs.txt"
)
NEEDLES = (
    "Add a load pin to a memory component",
    "Add a store pin to a memory component",
)


def clean_decompile(address: int) -> str:
    fn = ida_funcs.get_func(address)
    if fn is None:
        return "<no function>"
    try:
        cfunc = ida_hexrays.decompile(fn)
    except Exception as exc:
        return f"<decompile failed: {exc!r}>"
    if cfunc is None:
        return "<decompile returned None>"
    return "\n".join(
        ida_lines.tag_remove(line.line) for line in cfunc.get_pseudocode()
    )


def main() -> None:
    ida_auto.auto_wait()
    ida_hexrays.init_hexrays_plugin()
    rows: list[str] = []
    seen_functions: set[int] = set()
    for needle in NEEDLES:
        rows.append(f"## {needle}")
        string_matches = [item for item in idautils.Strings() if needle in str(item)]
        for item in string_matches:
            rows.append(f"raw string {item.ea:#x}: {str(item)!r}")
            for delta in range(-16, 9):
                target = item.ea + delta
                pattern = " ".join(f"{byte:02X}" for byte in struct.pack("<Q", target))
                cursor = idc.get_inf_attr(idc.INF_MIN_EA)
                while True:
                    found = idc.find_binary(cursor, idc.SEARCH_DOWN, pattern)
                    if found == idc.BADADDR:
                        break
                    rows.append(
                        f"pointer {found:#x} -> {target:#x} (string delta {delta:+d})"
                    )
                    for descriptor in (found - 8, found):
                        for reference in sorted(
                            set(idautils.DataRefsTo(descriptor))
                            | set(idautils.DataRefsTo(descriptor + 8))
                        ):
                            fn = ida_funcs.get_func(reference)
                            start = fn.start_ea if fn else idc.BADADDR
                            rows.append(
                                f"  descriptor {descriptor:#x} xref {reference:#x} "
                                f"function {start:#x} {ida_name.get_name(start)}"
                            )
                            if start != idc.BADADDR:
                                seen_functions.add(start)
                    cursor = found + 1
        for ea, name in idautils.Names():
            if not name.startswith("TM__"):
                continue
            length = ida_bytes.get_qword(ea)
            pointer = ida_bytes.get_qword(ea + 8)
            if not (0 < length < 4096):
                continue
            raw = ida_bytes.get_bytes(pointer + 8, length)
            if raw is None:
                continue
            value = raw.decode("utf-8", "backslashreplace")
            if needle not in value:
                continue
            rows.append(f"descriptor {ea:#x} {name}: {value!r}")
            refs = sorted(
                set(idautils.DataRefsTo(ea)) | set(idautils.DataRefsTo(ea + 8))
            )
            for reference in refs:
                fn = ida_funcs.get_func(reference)
                start = fn.start_ea if fn else idc.BADADDR
                rows.append(
                    f"xref {reference:#x} function {start:#x} "
                    f"{ida_name.get_name(start)}"
                )
                if start != idc.BADADDR:
                    seen_functions.add(start)
        rows.append("")
    for start in sorted(seen_functions):
        rows.append(f"## function {start:#x} {ida_name.get_name(start)}")
        rows.append(clean_decompile(start))
        rows.append("")
    OUT.write_text("\n".join(rows), encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    OUT.with_suffix(".error.txt").write_text(repr(exc), encoding="utf-8")
    ida_kernwin.warning(str(exc))
    idc.qexit(1)
