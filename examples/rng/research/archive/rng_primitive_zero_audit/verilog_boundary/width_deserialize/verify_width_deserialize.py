#!/usr/bin/env python3
"""Verify the kind 95/96 width and v15 retention evidence without running the game."""

from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXE = Path(r"D:\Game\Steam\steamapps\common\Turing Complete\Turing Complete.exe")
RESEARCH = Path(r"D:\Develop\Other\turing-complete\.research")
AUDIT_ROOT = RESEARCH / "rng_primitive_zero_audit"
NATIVE_PROTOTYPES = AUDIT_ROOT / "native_prototypes.json"
V15_SOURCE = RESEARCH / "save_monger_current" / "versions" / "v15.nim"
COMMON_SOURCE = RESEARCH / "save_monger_current" / "common.nim"
DECOMPILE_DIR = AUDIT_ROOT / "ram_enum_acceptance" / "deserialize_ui"

EXPECTED_EXE_SHA256 = "C93F5E8E826050C3F92E2B3891D26FCDFC933658614185CB9B2EB6A34C5B8D1C"

CONSTANTS = {
    "AUTO_SIZE": (0x140995870, 0x8000000000000000),
    "VARIABLE_WIDTH": (0x140995878, 0x7FFFFFFFFFFFFFFF),
    "VARIABLE_WIDTH2": (0x140995880, 0x7FFFFFFFFFFFFFFE),
    "VARIABLE_WIDTH4": (0x140995888, 0x7FFFFFFFFFFFFFFD),
    "VARIABLE_WIDTH8": (0x140995890, 0x7FFFFFFFFFFFFFFC),
    "MAX_WIRE_WIDTH": (0x140995898, 2048),
}

OPCODE_CHECKS = {
    "reject_custom_kind_78": (0x14023683D, "807d104e"),
    "auto_size_fallback_bits_2": (0x1402368C2, "b902000000"),
    "output_index_bounds_check": (0x140236920, "0fb75518"),
    "variable_width_x1": (0x1402369C6, "ba01000000"),
    "variable_width2_x2": (0x140236A2D, "ba02000000"),
    "variable_width4_x4": (0x140236A94, "ba04000000"),
    "variable_width8_x8": (0x140236AF8, "ba08000000"),
}

JUMP_TABLE_VA = 0x140A0392C
CLAMP_TARGET_VA = 0x140237379


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


class PEImage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.stream = path.open("rb")
        require(self.read_at(0, 2) == b"MZ", "missing DOS MZ signature")
        pe_offset = self.unpack_at("<I", 0x3C)[0]
        require(self.read_at(pe_offset, 4) == b"PE\0\0", "missing PE signature")

        coff_offset = pe_offset + 4
        section_count = self.unpack_at("<H", coff_offset + 2)[0]
        optional_size = self.unpack_at("<H", coff_offset + 16)[0]
        optional_offset = coff_offset + 20
        require(self.unpack_at("<H", optional_offset)[0] == 0x20B, "expected PE32+")
        self.image_base = self.unpack_at("<Q", optional_offset + 24)[0]

        self.sections: list[dict[str, int | str]] = []
        section_offset = optional_offset + optional_size
        for index in range(section_count):
            raw = self.read_at(section_offset + index * 40, 40)
            name = raw[:8].split(b"\0", 1)[0].decode("ascii", errors="replace")
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", raw, 8)
            self.sections.append(
                {
                    "name": name,
                    "virtual_size": virtual_size,
                    "virtual_address": virtual_address,
                    "raw_size": raw_size,
                    "raw_offset": raw_offset,
                }
            )

    def close(self) -> None:
        self.stream.close()

    def __enter__(self) -> "PEImage":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def read_at(self, offset: int, size: int) -> bytes:
        self.stream.seek(offset)
        data = self.stream.read(size)
        require(len(data) == size, f"short read at file offset 0x{offset:x}")
        return data

    def unpack_at(self, fmt: str, offset: int) -> tuple[object, ...]:
        return struct.unpack(fmt, self.read_at(offset, struct.calcsize(fmt)))

    def va_to_offset(self, va: int) -> int:
        rva = va - self.image_base
        require(rva >= 0, f"VA 0x{va:x} precedes image base")
        for section in self.sections:
            start = int(section["virtual_address"])
            raw_size = int(section["raw_size"])
            span = max(int(section["virtual_size"]), raw_size)
            if start <= rva < start + span:
                delta = rva - start
                require(delta < raw_size, f"VA 0x{va:x} has no file-backed bytes")
                return int(section["raw_offset"]) + delta
        raise AssertionError(f"VA 0x{va:x} is outside all PE sections")

    def read_va(self, va: int, size: int) -> bytes:
        return self.read_at(self.va_to_offset(va), size)

    def u64_va(self, va: int) -> int:
        return struct.unpack("<Q", self.read_va(va, 8))[0]

    def i32_va(self, va: int) -> int:
        return struct.unpack("<i", self.read_va(va, 4))[0]


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require_all(text: str, patterns: dict[str, str], source_name: str) -> dict[str, bool]:
    result: dict[str, bool] = {}
    for name, pattern in patterns.items():
        matched = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL) is not None
        require(matched, f"{source_name}: missing evidence pattern {name!r}")
        result[name] = True
    return result


def pin_descriptor(pin: dict[str, object]) -> int:
    raw = bytes.fromhex(str(pin["raw_hex"]))
    require(len(raw) >= 16, "pin record is shorter than its width descriptor")
    return struct.unpack_from("<Q", raw, 8)[0]


def verify_prototypes() -> dict[str, object]:
    document = json.loads(NATIVE_PROTOTYPES.read_text(encoding="utf-8"))
    records = document["records"]
    kind95 = records["95"]
    kind96 = records["96"]

    # Recovered Prototype layout: seq at +96 is inputs; seq at +128 is outputs.
    input95 = kind95["pin_sequences"]["96"]
    output95 = kind95["pin_sequences"]["128"]
    input96 = kind96["pin_sequences"]["96"]
    output96 = kind96["pin_sequences"]["128"]

    require(input95["length"] == 0, "kind 95 should have zero inputs")
    require(output95["length"] == 1, "kind 95 should have one output")
    descriptor95 = pin_descriptor(output95["pins"][0])
    require(descriptor95 == CONSTANTS["VARIABLE_WIDTH"][1], "kind 95 output is not VARIABLE_WIDTH")
    require(input96["length"] == 1, "kind 96 should have one input")
    require(output96["length"] == 0, "kind 96 should have zero outputs")
    descriptor96 = pin_descriptor(input96["pins"][0])
    require(descriptor96 == CONSTANTS["VARIABLE_WIDTH"][1], "kind 96 input is not VARIABLE_WIDTH")

    return {
        "kind_95": {
            "name": "com_verilog_input",
            "input_count": 0,
            "output_count": 1,
            "output_0_descriptor": f"0x{descriptor95:016x}",
        },
        "kind_96": {
            "name": "com_verilog_output",
            "input_count": 1,
            "output_count": 0,
            "input_0_descriptor": f"0x{descriptor96:016x}",
        },
    }


def verify_v15_retention() -> dict[str, object]:
    source_checks = require_all(
        load_text(V15_SOURCE),
        {
            "enum_range_acceptance": r"if\s+idx\s*<=\s*ComponentKind\.high\.int",
            "kind_assignment": r"kind\s*=\s*ComponentKind\(idx\)",
            "component_list_has_no_kind_filter": r"let\s+comp\s*=\s*get_component\(.*?\)\s*\r?\n\s*result\.add\(comp\)",
        },
        "v15.nim",
    )

    component_checks = require_all(
        load_text(DECOMPILE_DIR / "get_component_v15.c"),
        {
            "binary_kind_upper_bound_124": r"u16__.*?<=\s*0x7Cui64",
            "accepted_kind_is_stored": r"v111\s*=\s*v103",
        },
        "get_component_v15.c",
    )
    list_checks = require_all(
        load_text(DECOMPILE_DIR / "get_components_v15.c"),
        {
            "every_parsed_component_is_added": r"get_component__.*?\(.*?\);.*?add__modelZsave95mongerZversionsZv0_u1028",
        },
        "get_components_v15.c",
    )
    load_checks = require_all(
        load_text(DECOMPILE_DIR / "load_schematic_raw.c"),
        {
            "only_zero_kind_skips_main_add_path": r"if\s*\(\s*LOBYTE\(v30\[0\]\)\s*\)",
            "custom_kind_has_separate_check": r"if\s*\(\s*v102\s*==\s*78\s*\)",
            "word_size_is_clamped": r"get_clamped_word_size__modelZboardZprototype95list_u4458\(\s*v102,\s*v30\[28\],\s*0\s*\)",
            "component_reaches_board_add": r"board_add_component__modelZboardZboard_u21118\(.*?v102,.*?clamped_word_size__modelZboardZprototype95list_u4458",
        },
        "load_schematic_raw.c",
    )
    board_checks = require_all(
        load_text(DECOMPILE_DIR / "board_add_component.c"),
        {
            "only_custom_78_uses_custom_presence_gate": r"v166\s*=\s*v172\s*==\s*78;\s*if\s*\(\s*v172\s*==\s*78\s*\)",
            "normal_kind_uses_prototype_table": r"X5BX5D___modelZboardZprototype95list_u4239\(refptr_PROTOTYPES.*?,\s*v172\)",
        },
        "board_add_component.c",
    )
    serializer_checks = require_all(
        load_text(DECOMPILE_DIR / "add_component_save_monger.c"),
        {
            "serializer_writes_raw_kind": r"add_component_kind__modelZsave95mongerZcommon_u5826\(a1,\s*\*a2\)",
            "serializer_writes_word_size": r"add_bits__modelZsave95mongerZcommon_u5741\(a1,\s*\*\(\(_QWORD \*\)a2 \+ 28\)\)",
            "only_custom_has_extra_tail": r"if\s*\(\s*\*a2\s*==\s*78\s*\)",
        },
        "add_component_save_monger.c",
    )

    common = load_text(COMMON_SOURCE)
    enum_checks = require_all(
        common,
        {
            "kind_95_enum": r"com_verilog_input\s*=\s*95",
            "kind_96_enum": r"com_verilog_output\s*=\s*96",
            "unused_set_present": r"const\s+UNUSED_COMPONENTS\*\s*=\s*\{.*?\}",
        },
        "common.nim",
    )
    unused_match = re.search(r"const\s+UNUSED_COMPONENTS\*\s*=\s*\{(.*?)\}", common, re.DOTALL)
    require(unused_match is not None, "could not isolate UNUSED_COMPONENTS")
    unused_body = unused_match.group(1)
    require("com_verilog_input" not in unused_body, "kind 95 unexpectedly appears in UNUSED_COMPONENTS")
    require("com_verilog_output" not in unused_body, "kind 96 unexpectedly appears in UNUSED_COMPONENTS")
    enum_checks["kind_95_not_unused"] = True
    enum_checks["kind_96_not_unused"] = True

    return {
        "v15_source": source_checks,
        "v15_binary_component_parser": component_checks,
        "v15_binary_component_list": list_checks,
        "load_schematic_raw": load_checks,
        "board_add_component": board_checks,
        "serializer": serializer_checks,
        "enum_and_unused_set": enum_checks,
        "conclusion": "raw v15 kinds 95/96 are accepted, mounted through the native prototype table, and preserved on save",
    }


def main() -> None:
    require(EXE.is_file(), f"missing executable: {EXE}")
    actual_hash = sha256_file(EXE)
    require(actual_hash == EXPECTED_EXE_SHA256, f"unexpected executable SHA-256: {actual_hash}")

    with PEImage(EXE) as image:
        constant_evidence: dict[str, object] = {}
        for name, (va, expected) in CONSTANTS.items():
            actual = image.u64_va(va)
            require(actual == expected, f"{name} mismatch: expected 0x{expected:x}, got 0x{actual:x}")
            constant_evidence[name] = {"va": f"0x{va:x}", "value": actual, "hex": f"0x{actual:016x}"}

        opcode_evidence: dict[str, object] = {}
        for name, (va, expected_hex) in OPCODE_CHECKS.items():
            actual_hex = image.read_va(va, len(expected_hex) // 2).hex()
            require(actual_hex == expected_hex, f"opcode mismatch for {name}: {actual_hex}")
            opcode_evidence[name] = {"va": f"0x{va:x}", "bytes": actual_hex}

        jump_entries: dict[str, object] = {}
        for kind in (95, 96):
            index = kind - 95
            entry_va = JUMP_TABLE_VA + index * 4
            relative = image.i32_va(entry_va)
            target = JUMP_TABLE_VA + relative
            require(target == CLAMP_TARGET_VA, f"kind {kind} clamp target is 0x{target:x}")
            jump_entries[str(kind)] = {
                "index": index,
                "entry_va": f"0x{entry_va:x}",
                "relative": relative,
                "target_va": f"0x{target:x}",
            }

        pe_evidence = {
            "image_base": f"0x{image.image_base:x}",
            "constants": constant_evidence,
            "opcode_checks": opcode_evidence,
            "clamp_jump_table": {
                "base_va": f"0x{JUMP_TABLE_VA:x}",
                "entries": jump_entries,
                "shared_target_semantics": "max(Bits(1), min(serialized_word_size, MAX_WIRE_WIDTH))",
            },
        }

    evidence = {
        "schema_version": 1,
        "result": "pass",
        "binary": {
            "path": str(EXE),
            "size": EXE.stat().st_size,
            "sha256": actual_hash,
            **pe_evidence,
        },
        "get_output_word_size": {
            "address": "0x1402367c6",
            "kind_95_explicit": "returns component word_size because output[0] is VARIABLE_WIDTH",
            "kind_95_auto_size": "AUTO_SIZE first becomes Bits(2), then VARIABLE_WIDTH multiplies by 1",
            "kind_96_output": "no legal output index; output count is zero and bounds checking raises",
            "settings_or_label_dependency": False,
        },
        "prototypes": verify_prototypes(),
        "v15_retention": verify_v15_retention(),
        "strict_conclusion": {
            "explicit_kind_95_width_range_after_mount": [1, 2048],
            "auto_size_kind_95_effective_output_width": 2,
            "proven": "width metadata and v15 retention",
            "not_proven_here": "that changing width yields arbitrary seed-bit extraction or a useful free truncation in generated Verilog",
        },
        "scope": {
            "game_process_started": False,
            "formal_save_files_accessed": False,
            "formal_save_files_modified": False,
        },
    }

    output = HERE / "evidence.json"
    output.write_text(json.dumps(evidence, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"PASS: {len(CONSTANTS)} constants, {len(OPCODE_CHECKS)} opcode sites, 2 clamp entries")
    print(f"EXE SHA-256: {actual_hash}")
    print(f"Evidence: {output}")


if __name__ == "__main__":
    main()
