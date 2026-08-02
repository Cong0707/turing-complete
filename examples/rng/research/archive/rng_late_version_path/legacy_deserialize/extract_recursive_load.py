from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_name
import ida_pro
import idautils


OUT = Path(r"D:\Develop\Other\turing-complete\.research\rng_late_version_path\legacy_deserialize")
TARGETS = (0x14067F85F, 0x140681A0B)


ida_auto.auto_wait()
OUT.mkdir(parents=True, exist_ok=True)

for ea in TARGETS:
    func = ida_funcs.get_func(ea)
    name = ida_name.get_name(ea) or f"sub_{ea:X}"
    lines = [
        f"// address: {func.start_ea:#x}-{func.end_ea:#x}",
        f"// name: {name}",
        str(ida_hexrays.decompile(ea)),
    ]
    (OUT / f"{ea:016x}.c").write_text("\n".join(lines) + "\n", encoding="utf-8")
    refs = [f"{xref.frm:#x}\t{xref.type}" for xref in idautils.XrefsTo(ea, 0)]
    (OUT / f"{ea:016x}.xrefs.txt").write_text("\n".join(refs) + "\n", encoding="utf-8")

ida_pro.qexit(0)
