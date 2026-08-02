"""Export Nim codegen string constants from the existing read-only IDA database."""

from pathlib import Path

import ida_auto
import ida_bytes
import ida_kernwin
import idautils
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_tristate_bus\native\tm_strings.tsv"
)
PREFIX = "TM__THWBxVSaWN2Zh7OMooFH0w_"


def escaped(data: bytes) -> str:
    return data.decode("utf-8", errors="backslashreplace").encode(
        "unicode_escape"
    ).decode("ascii")


def main() -> None:
    ida_auto.auto_wait()
    rows = ["suffix\taddress\tqword\tstatic_length\tbytes"]
    for address, name in idautils.Names():
        if not name.startswith(PREFIX):
            continue
        suffix = name[len(PREFIX) :]
        qword = ida_bytes.get_qword(address)
        static_length = qword & ((1 << 62) - 1) if qword >> 62 == 1 else 0
        if static_length:
            data = ida_bytes.get_bytes(address + 8, static_length)
        else:
            data = None
        rows.append(
            f"{suffix}\t{address:#x}\t{qword}\t{static_length}\t"
            f"{escaped(bytes(data)) if data is not None else ''}"
        )
    OUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    OUT.write_text(repr(exc) + "\n", encoding="utf-8")
    ida_kernwin.warning(str(exc))
    idc.qexit(1)
