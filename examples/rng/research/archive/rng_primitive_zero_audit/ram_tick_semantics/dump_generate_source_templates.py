"""Dump selected Nim string constants surrounding the two circuit-code passes."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_bytes
import idautils
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit"
    r"\ram_tick_semantics\generate_source_templates.txt"
)
SCAN_OUT = OUT.with_name("generate_source_mode_templates.txt")
PREFIX = "TM__THWBxVSaWN2Zh7OMooFH0w_"
IDS = {
    507,
    508,
    2425,
    2426,
    2427,
    2428,
    2430,
    2431,
    2433,
    2434,
    2437,
    2438,
    2439,
    2440,
    2442,
    2443,
    2445,
    2446,
    2447,
    2448,
    2449,
    2450,
    2483,
    2484,
    2486,
    2488,
    2489,
    2490,
    2492,
}


def main() -> None:
    ida_auto.auto_wait()
    chunks: list[str] = []
    names = {name: ea for ea, name in idautils.Names()}
    for ident in sorted(IDS):
        name = PREFIX + str(ident)
        ea = names.get(name, idc.BADADDR)
        if ea == idc.BADADDR:
            chunks.append(f"## {name}\nMISSING\n")
            continue
        length = ida_bytes.get_qword(ea)
        ptr = ida_bytes.get_qword(ea + 8)
        raw = ida_bytes.get_bytes(ptr + 8, length) if 0 <= length < 1_000_000 else None
        value = raw.decode("utf-8", "backslashreplace") if raw is not None else "<invalid>"
        chunks.append(
            f"## {name} @ {ea:#x}\nlength={length} ptr={ptr:#x}\n{value!r}\n"
        )
    OUT.write_text("\n".join(chunks), encoding="utf-8")
    mode_chunks: list[str] = []
    for name, ea in sorted(names.items(), key=lambda item: item[1]):
        if not name.startswith("TM__"):
            continue
        length = ida_bytes.get_qword(ea)
        ptr = ida_bytes.get_qword(ea + 8)
        if not (0 < length < 100_000):
            continue
        raw = ida_bytes.get_bytes(ptr + 8, length)
        if raw is None:
            continue
        value = raw.decode("utf-8", "backslashreplace")
        if not any(
            needle in value
            for needle in ("mode_refresh", "mode_run", "burst_target_tick", ".tick += 1")
        ):
            continue
        mode_chunks.append(f"## {name} @ {ea:#x}\n{value!r}\n")
    SCAN_OUT.write_text("\n".join(mode_chunks), encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    OUT.with_suffix(".error.txt").write_text(repr(exc), encoding="utf-8")
    idc.qexit(1)
