#!/usr/bin/env python3
"""List focused RIP-relative references in the current Windows executable."""

from __future__ import annotations

import argparse
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
import struct

from capstone import CS_ARCH_X86, CS_MODE_64, Cs
from capstone.x86 import X86_OP_MEM, X86_REG_RIP
import pefile


@dataclass(frozen=True)
class Symbol:
    name: str
    value: int
    section: int
    aux_count: int


def read_symbols(path: Path) -> tuple[pefile.PE, list[Symbol]]:
    pe = pefile.PE(str(path), fast_load=True)
    pointer = pe.FILE_HEADER.PointerToSymbolTable
    count = pe.FILE_HEADER.NumberOfSymbols
    if not pointer or not count:
        raise ValueError(f"{path} has no COFF symbol table")

    with path.open("rb") as stream:
        stream.seek(pointer)
        table = stream.read(count * 18)
        raw_size = stream.read(4)
        if len(raw_size) != 4:
            raise ValueError("truncated COFF string table")
        string_size = struct.unpack("<I", raw_size)[0]
        strings = raw_size + stream.read(max(0, string_size - 4))

    def decode_name(raw: bytes) -> str:
        zeroes, offset = struct.unpack("<II", raw)
        if zeroes:
            return raw.rstrip(b"\0").decode("utf-8", errors="replace")
        if offset < 4 or offset >= len(strings):
            return f"<bad-string-offset:{offset}>"
        end = strings.find(b"\0", offset)
        if end < 0:
            end = len(strings)
        return strings[offset:end].decode("utf-8", errors="replace")

    symbols: list[Symbol] = []
    index = 0
    while index < count:
        raw = table[index * 18 : (index + 1) * 18]
        if len(raw) != 18:
            break
        name_raw, value, section, _type, _storage, aux_count = struct.unpack(
            "<8sIhHBB", raw
        )
        symbols.append(Symbol(decode_name(name_raw), value, section, aux_count))
        index += 1 + aux_count
    return pe, symbols


def virtual_address(pe: pefile.PE, symbol: Symbol) -> int | None:
    if symbol.section <= 0 or symbol.section > len(pe.sections):
        return None
    section = pe.sections[symbol.section - 1]
    return pe.OPTIONAL_HEADER.ImageBase + section.VirtualAddress + symbol.value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path)
    parser.add_argument("targets", nargs="+", type=lambda value: int(value, 0))
    args = parser.parse_args()

    pe, symbols = read_symbols(args.exe)
    named = sorted(
        (address, symbol.name)
        for symbol in symbols
        if (address := virtual_address(pe, symbol)) is not None
    )
    addresses = [entry[0] for entry in named]
    names_at = {address: name for address, name in named}
    targets = set(args.targets)

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    image_base = pe.OPTIONAL_HEADER.ImageBase
    for section in pe.sections:
        if not section.Characteristics & 0x20000000:
            continue
        start = image_base + section.VirtualAddress
        for instruction in md.disasm(section.get_data(), start):
            for operand in instruction.operands:
                if operand.type != X86_OP_MEM or operand.mem.base != X86_REG_RIP:
                    continue
                target = instruction.address + instruction.size + operand.mem.disp
                if target not in targets:
                    continue
                index = bisect_right(addresses, instruction.address) - 1
                caller_address, caller_name = (
                    named[index] if index >= 0 else (0, "<unknown>")
                )
                target_name = names_at.get(target, "<unnamed>")
                print(
                    f"{instruction.address:#x} target={target:#x} {target_name} "
                    f"{instruction.mnemonic} {instruction.op_str} "
                    f"caller={caller_name}+{instruction.address - caller_address:#x}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
