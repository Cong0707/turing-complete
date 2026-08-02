"""Read-only IDA export for Foundry I/O and tri-state code-generation paths."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_kernwin
import ida_name
import ida_ua
import idautils
import idc


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_cost_reverse\ida_custom_io_audit.txt"
)
CODEGEN_OUTPUT = OUTPUT.with_name("ida_add_circuit_code.asm")
STORE_OUTPUT = 0x140437079
ADD_CIRCUIT_CODE = 0x140441388
SEARCH_TERMS = (
    "com_cc_input",
    "com_cc_input_buffer",
    "com_cc_output",
    "store_output",
    "get_output_z_value",
)


def disassembly_window(address: int, before: int = 20, after: int = 12) -> list[str]:
    points = [address]
    cursor = address
    for _ in range(before):
        cursor = idc.prev_head(cursor)
        points.append(cursor)
    cursor = address
    for _ in range(after):
        cursor = idc.next_head(cursor)
        points.append(cursor)
    result: list[str] = []
    for point in sorted(set(points)):
        result.append(f"{point:#x}: {idc.generate_disasm_line(point, 0)}")
    return result


def main() -> None:
    ida_auto.auto_wait()
    lines: list[str] = []
    lines.append(f"store_output={STORE_OUTPUT:#x}")
    lines.append("\n[store_output xrefs]")
    callers: set[int] = set()
    for xref in idautils.XrefsTo(STORE_OUTPUT):
        function = ida_funcs.get_func(xref.frm)
        start = function.start_ea if function else idc.BADADDR
        callers.add(start)
        lines.append(
            f"from={xref.frm:#x} function={start:#x} "
            f"name={ida_name.get_name(start)} type={xref.type}"
        )

    lines.append("\n[matching strings and xrefs]")
    for string in idautils.Strings():
        value = str(string)
        if not any(term in value for term in SEARCH_TERMS):
            continue
        lines.append(f"string={string.ea:#x} {value!r}")
        for xref in idautils.XrefsTo(string.ea):
            function = ida_funcs.get_func(xref.frm)
            start = function.start_ea if function else idc.BADADDR
            lines.append(
                f"  xref={xref.frm:#x} function={start:#x} "
                f"name={ida_name.get_name(start)}"
            )

    lines.append("\n[names]")
    for address, name in idautils.Names():
        if any(term in name for term in SEARCH_TERMS):
            lines.append(f"{address:#x} {name}")

    lines.append("\n[drive-enable globals]")
    for name in (
        "TM__THWBxVSaWN2Zh7OMooFH0w_1604",
        "off_140A294B8",
        "TM__THWBxVSaWN2Zh7OMooFH0w_1961",
        "off_140A2A548",
    ):
        address = ida_name.get_name_ea(idc.BADADDR, name)
        value = ida_bytes.get_qword(address) if address != idc.BADADDR else None
        payload = None
        if value:
            raw = ida_bytes.get_strlit_contents(value, -1, 0)
            payload = raw.decode("utf-8", errors="replace") if raw else None
        lines.append(
            f"{name}: address={address:#x} value={value!r} payload={payload!r}"
        )

    lines.append("\n[store_output call windows]")
    for xref in idautils.XrefsTo(STORE_OUTPUT):
        function = ida_funcs.get_func(xref.frm)
        start = function.start_ea if function else idc.BADADDR
        lines.append(f"\n===== call {xref.frm:#x}, function {start:#x} =====")
        lines.extend(disassembly_window(xref.frm))

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    function = ida_funcs.get_func(ADD_CIRCUIT_CODE)
    if function is None:
        raise RuntimeError(f"no add_circuit_code function at {ADD_CIRCUIT_CODE:#x}")
    CODEGEN_OUTPUT.write_text(
        "\n".join(
            f"{point:#x}: {idc.generate_disasm_line(point, 0)}"
            for point in idautils.FuncItems(function.start_ea)
        )
        + "\n",
        encoding="utf-8",
    )
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"CUSTOM_IO_AUDIT_ERROR: {exc}")
    ida_kernwin.warning(str(exc))
    idc.qexit(1)
