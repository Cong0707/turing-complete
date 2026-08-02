#!/usr/bin/env python3
"""Extract and model Turing Complete's component score table.

This script is intentionally read-only with respect to the game and save files.
It validates the exact executable build before decoding fixed virtual addresses,
then writes derived JSON/CSV artifacts next to this file.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import struct
from collections import defaultdict
from pathlib import Path
from typing import Any

import pefile


EXPECTED_SHA256 = "c93f5e8e826050c3f92e2b3891d26fcdfc933658614185cb9b2eb6a34c5b8d1c"
DEFAULT_EXE = Path(r"D:\Game\Steam\steamapps\common\Turing Complete\Turing Complete.exe")

DEFAULT_COMPONENT_SCORES_VA = 0x140A09370
EXPECTED_SCORE_ALLOCATION_VA = 0x140A06D00
DEFAULT_KIND_BITMAP_VA = 0x140A08D10
GATE_JUMP_TABLE_VA = 0x140A093D8
GATE_JUMP_TABLE_FIRST_KIND = 18
GATE_JUMP_TABLE_ENTRY_COUNT = 102  # kinds 18..119 inclusive

SIMPLE_GATE_FUNCTION_VA = 0x140275F1B
COMPONENT_GATE_FUNCTION_VA = 0x140276993
SIMPLE_DELAY_FUNCTION_VA = 0x140276FB1
COMPONENT_DELAY_FUNCTION_VA = 0x14027759B
GET_COST_FUNCTION_VA = 0x140277B05

GATE_TARGET_FORMULAS = {
    0x1402760FC: "byte_piecewise",
    0x1402762FF: "linear_ceil",
    0x140276386: "piecewise_linear_8_7",
    0x1402764C3: "two_per_bit",
    0x140276522: "five_per_bit",
    0x140276581: "shift_logarithmic",
    0x14027674C: "quadratic",
    0x1402768D3: "load_store_component_assert",
    0x1402768FB: "ram_component_assert",
    0x140276939: "jump_table_default_unreachable_for_legal_dispatch",
}

BYTE_PIECEWISE_KINDS = {18, 19, 20, 21, 22, 23, 24, 26, 39, 42, 50}
LINEAR_CEIL_KINDS = {30, 49, 57}
PIECEWISE_LINEAR_KINDS = {27, 28, 29, 38, 104}
TWO_PER_BIT_KINDS = {25}
FIVE_PER_BIT_KINDS = {55, 119}
SHIFT_LOG_KINDS = {33, 34, 35, 36, 37}
QUADRATIC_KINDS = {31, 32, 108}
LOAD_STORE_KINDS = {54, 56}
RAM_KINDS = {118}

DELAY_DEFAULT_KINDS = {18, 19, 20, 21, 22, 23, 24, 25, 39, 42, 50, 55, 119}
DELAY_EQUAL_KINDS = {26}
DELAY_SHIFT_KINDS = {33, 34, 35, 36, 37}
DELAY_LINEAR_KINDS = {27, 28, 29, 30, 31, 32, 38, 49, 57, 104, 108}

COMPONENT_DEPENDENT_GATE = {
    54: "component.calculated_gate (+0x118)",
    56: "component.calculated_gate (+0x118)",
    78: "custom prototype recursively calculated gate",
    118: "RAM settings[0] == 0 ? 50 * component(+0x138) : component(+0x138)",
}
COMPONENT_DEPENDENT_DELAY = {
    54: "component.calculated_delay (+0x120)",
    56: "component.calculated_delay (+0x120)",
    78: "custom prototype recursively calculated delay",
    79: "component.cc_input_custom_delay (+0x130)",
    118: "RAM settings and component(+0x138) dependent",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_component_kinds(common_nim: Path) -> dict[int, str]:
    text = common_nim.read_text(encoding="utf-8")
    match = re.search(
        r"type ComponentKind\* = enum\s*(.*?)\n\s*const UNUSED_COMPONENTS",
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise RuntimeError(f"ComponentKind enum not found in {common_nim}")

    result: dict[int, str] = {}
    for name, value_text in re.findall(r"^\s*(com_[a-z0-9_]+)\s*=\s*(\d+)\s*$", match.group(1), re.MULTILINE):
        value = int(value_text)
        if value in result:
            raise RuntimeError(f"duplicate ComponentKind value {value}")
        result[value] = name

    expected = set(range(125))
    if set(result) != expected:
        raise RuntimeError(
            f"unexpected ComponentKind values: missing={sorted(expected - set(result))}, "
            f"extra={sorted(set(result) - expected)}"
        )
    return result


class PeReader:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = path.read_bytes()
        self.pe = pefile.PE(data=self.data, fast_load=True)
        self.image_base = int(self.pe.OPTIONAL_HEADER.ImageBase)

    def offset(self, va: int) -> int:
        if va < self.image_base:
            raise ValueError(f"VA {va:#x} is below image base {self.image_base:#x}")
        return int(self.pe.get_offset_from_rva(va - self.image_base))

    def unpack(self, fmt: str, va: int) -> tuple[Any, ...]:
        return struct.unpack_from(fmt, self.data, self.offset(va))

    def bytes(self, va: int, length: int) -> bytes:
        offset = self.offset(va)
        return self.data[offset : offset + length]


def extract_score_table(reader: PeReader, names: dict[int, str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    capacity, allocation_va, count = reader.unpack("<QQQ", DEFAULT_COMPONENT_SCORES_VA)
    descriptor = {
        "capacity": capacity,
        "allocation_va": allocation_va,
        "count": count,
    }
    if descriptor != {"capacity": 256, "allocation_va": EXPECTED_SCORE_ALLOCATION_VA, "count": 125}:
        raise RuntimeError(f"unexpected DEFAULT_COMPONENT_SCORES descriptor: {descriptor}")

    allocation_header = reader.unpack("<Q", allocation_va)[0]
    if allocation_header != 0x4000000000000100:
        raise RuntimeError(f"unexpected score allocation header: {allocation_header:#x}")

    entries: list[dict[str, Any]] = []
    for slot in range(capacity):
        hash_value, kind, gate, delay = reader.unpack("<QQqq", allocation_va + 8 + slot * 32)
        if hash_value == 0:
            if kind != 0 or gate != 0 or delay != 0:
                raise RuntimeError(f"partially populated score slot {slot}")
            continue
        if kind not in names:
            raise RuntimeError(f"score slot {slot} has unknown kind {kind}")
        entries.append(
            {
                "slot": slot,
                "hash": f"0x{hash_value:016x}",
                "kind": kind,
                "name": names[kind],
                "default_gate": gate,
                "default_delay": delay,
            }
        )

    if len(entries) != count:
        raise RuntimeError(f"score table count mismatch: descriptor={count}, decoded={len(entries)}")
    decoded_kinds = [entry["kind"] for entry in entries]
    if len(set(decoded_kinds)) != len(decoded_kinds) or set(decoded_kinds) != set(names):
        raise RuntimeError("score table does not contain each ComponentKind exactly once")
    return sorted(entries, key=lambda entry: entry["kind"]), descriptor


def extract_gate_jump_table(reader: PeReader, names: dict[int, str]) -> list[dict[str, Any]]:
    groups: defaultdict[int, list[int]] = defaultdict(list)
    raw_offsets: defaultdict[int, list[int]] = defaultdict(list)
    for index in range(GATE_JUMP_TABLE_ENTRY_COUNT):
        relative = reader.unpack("<i", GATE_JUMP_TABLE_VA + index * 4)[0]
        target = GATE_JUMP_TABLE_VA + relative
        kind = GATE_JUMP_TABLE_FIRST_KIND + index
        groups[target].append(kind)
        raw_offsets[target].append(relative)

    if set(groups) != set(GATE_TARGET_FORMULAS):
        raise RuntimeError(
            "unexpected gate jump targets: "
            f"decoded={[hex(value) for value in sorted(groups)]}"
        )

    return [
        {
            "target_va": f"0x{target:016x}",
            "relative_offset": raw_offsets[target][0],
            "formula": GATE_TARGET_FORMULAS[target],
            "kinds": groups[target],
            "names": [names[kind] for kind in groups[target]],
        }
        for target in sorted(groups)
    ]


def extract_default_kind_bitmap(reader: PeReader, names: dict[int, str]) -> dict[str, Any]:
    raw = reader.bytes(DEFAULT_KIND_BITMAP_VA, 16)
    default_kinds = [kind for kind in names if raw[kind // 8] & (1 << (kind % 8))]
    override_kinds = [kind for kind in names if kind not in default_kinds]
    return {
        "va": f"0x{DEFAULT_KIND_BITMAP_VA:016x}",
        "raw_hex": raw.hex(),
        "default_table_kinds": default_kinds,
        "default_table_names": [names[kind] for kind in default_kinds],
        "level_override_allowed_kinds": override_kinds,
        "level_override_allowed_names": [names[kind] for kind in override_kinds],
    }


def gate_formula_name(kind: int) -> str:
    if kind in BYTE_PIECEWISE_KINDS:
        return "b*(w//8)+(w%8) if w%8<=3 else b*(w//8+1)+(w%8)-8"
    if kind in LINEAR_CEIL_KINDS:
        return "ceil(b*w/8)"
    if kind in PIECEWISE_LINEAR_KINDS:
        return "b+ceil((w-8)*b/(7 if w>8 else 8))"
    if kind in TWO_PER_BIT_KINDS:
        return "2*w"
    if kind in FIVE_PER_BIT_KINDS:
        return "5*w"
    if kind in SHIFT_LOG_KINDS:
        return "max(0, ceil(w*log2(w)*b/24)) if w>8 else max(0, ceil(w*b/8))"
    if kind in QUADRATIC_KINDS:
        return "max(0, ceil(w*w*b/64)) if w>8 else max(0, ceil(w*b/8))"
    if kind in LOAD_STORE_KINDS:
        return "component wrapper assertion; calculated_gate required"
    if kind in RAM_KINDS:
        return "component wrapper assertion; RAM fields required"
    return "b"


def delay_formula_name(kind: int) -> str:
    if kind in DELAY_EQUAL_KINDS:
        return "b+max(0, ceil(log2(w/8)))"
    if kind in DELAY_SHIFT_KINDS:
        return "max(min(b,4), ceil(log2(w)*b/3))"
    if kind in DELAY_LINEAR_KINDS:
        return "max(min(b,4), ceil(w*b/8))"
    if kind in LOAD_STORE_KINDS | RAM_KINDS:
        return "component wrapper assertion; instance fields required"
    return "b"


def simple_gate_cost(kind: int, width: int, default_gate: int) -> int:
    if not 1 <= width <= 64:
        raise ValueError(f"width must be in 1..64, got {width}")
    b = default_gate
    w = width
    if kind in BYTE_PIECEWISE_KINDS:
        quotient, remainder = divmod(w, 8)
        return b * quotient + remainder if remainder <= 3 else b * (quotient + 1) + remainder - 8
    if kind in LINEAR_CEIL_KINDS:
        return math.ceil(b * w / 8)
    if kind in PIECEWISE_LINEAR_KINDS:
        return b + math.ceil((w - 8) * b / (7 if w > 8 else 8))
    if kind in TWO_PER_BIT_KINDS:
        return 2 * w
    if kind in FIVE_PER_BIT_KINDS:
        return 5 * w
    if kind in SHIFT_LOG_KINDS:
        value = w * math.log2(w) * b / 24 if w > 8 else w * b / 8
        return max(0, math.ceil(value))
    if kind in QUADRATIC_KINDS:
        value = w * w * b / 64 if w > 8 else w * b / 8
        return max(0, math.ceil(value))
    if kind in LOAD_STORE_KINDS | RAM_KINDS:
        raise ValueError(f"kind {kind} requires the component wrapper for gate cost")
    return b


def simple_delay_cost(kind: int, width: int, default_delay: int) -> int:
    if not 1 <= width <= 64:
        raise ValueError(f"width must be in 1..64, got {width}")
    b = default_delay
    w = width
    if kind in DELAY_EQUAL_KINDS:
        return b + max(0, math.ceil(math.log2(w / 8)))
    if kind in DELAY_SHIFT_KINDS:
        return max(min(b, 4), math.ceil(math.log2(w) * b / 3))
    if kind in DELAY_LINEAR_KINDS:
        return max(min(b, 4), math.ceil(w * b / 8))
    if kind in LOAD_STORE_KINDS | RAM_KINDS:
        raise ValueError(f"kind {kind} requires the component wrapper for delay cost")
    return b


def width_cost(kind: int, width: int, default_gate: int, default_delay: int) -> dict[str, Any]:
    if kind in COMPONENT_DEPENDENT_GATE:
        gate: int | None = None
    else:
        gate = simple_gate_cost(kind, width, default_gate)
    if kind in COMPONENT_DEPENDENT_DELAY:
        delay: int | None = None
    else:
        delay = simple_delay_cost(kind, width, default_delay)
    return {"width": width, "gate": gate, "delay": delay}


def run_self_tests(by_kind: dict[int, dict[str, Any]]) -> None:
    checks = [
        (23, 1, 1),
        (23, 3, 3),
        (23, 8, 32),
        (19, 1, 1),
        (55, 1, 5),
        (33, 1, 19),
        (31, 1, 50),
    ]
    for kind, width, expected in checks:
        actual = simple_gate_cost(kind, width, by_kind[kind]["default_gate"])
        if actual != expected:
            raise AssertionError(
                f"gate self-test failed for kind={kind}, width={width}: {actual} != {expected}"
            )
    if simple_delay_cost(26, 9, by_kind[26]["default_delay"]) != 11:
        raise AssertionError("delay self-test failed for kind=26, width=9")


def build_output(
    exe: Path,
    exe_sha256: str,
    entries: list[dict[str, Any]],
    descriptor: dict[str, int],
    jump_groups: list[dict[str, Any]],
    bitmap: dict[str, Any],
) -> dict[str, Any]:
    default_kind_set = set(bitmap["default_table_kinds"])
    components: list[dict[str, Any]] = []
    for entry in entries:
        kind = entry["kind"]
        component = dict(entry)
        component.update(
            {
                "score_source": "default_table" if kind in default_kind_set else "level_override_allowed",
                "gate_formula": gate_formula_name(kind),
                "delay_formula": delay_formula_name(kind),
                "component_gate_dependency": COMPONENT_DEPENDENT_GATE.get(kind),
                "component_delay_dependency": COMPONENT_DEPENDENT_DELAY.get(kind),
                "costs_by_width": [
                    width_cost(kind, width, entry["default_gate"], entry["default_delay"])
                    for width in range(1, 65)
                ],
            }
        )
        components.append(component)

    return {
        "metadata": {
            "executable": str(exe),
            "sha256": exe_sha256,
            "image_base": "0x0000000140000000",
            "scope": "read-only static extraction; width matrix covers widths 1..64",
            "null_cost_meaning": "component wrapper requires live instance fields; table default is not final cost",
        },
        "addresses": {
            "default_component_scores": f"0x{DEFAULT_COMPONENT_SCORES_VA:016x}",
            "score_allocation": f"0x{EXPECTED_SCORE_ALLOCATION_VA:016x}",
            "default_kind_bitmap": f"0x{DEFAULT_KIND_BITMAP_VA:016x}",
            "gate_jump_table": f"0x{GATE_JUMP_TABLE_VA:016x}",
            "simple_gate_function": f"0x{SIMPLE_GATE_FUNCTION_VA:016x}",
            "component_gate_function": f"0x{COMPONENT_GATE_FUNCTION_VA:016x}",
            "simple_delay_function": f"0x{SIMPLE_DELAY_FUNCTION_VA:016x}",
            "component_delay_function": f"0x{COMPONENT_DELAY_FUNCTION_VA:016x}",
            "get_cost_function": f"0x{GET_COST_FUNCTION_VA:016x}",
        },
        "score_table_descriptor": descriptor,
        "default_kind_bitmap": bitmap,
        "gate_jump_table": jump_groups,
        "components": components,
    }


def write_csv(path: Path, output: dict[str, Any]) -> None:
    fields = [
        "kind",
        "name",
        "width",
        "default_gate",
        "default_delay",
        "gate_cost",
        "delay_cost",
        "score_source",
        "gate_formula",
        "delay_formula",
        "component_gate_dependency",
        "component_delay_dependency",
        "slot",
        "hash",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for component in output["components"]:
            for cost in component["costs_by_width"]:
                writer.writerow(
                    {
                        "kind": component["kind"],
                        "name": component["name"],
                        "width": cost["width"],
                        "default_gate": component["default_gate"],
                        "default_delay": component["default_delay"],
                        "gate_cost": "" if cost["gate"] is None else cost["gate"],
                        "delay_cost": "" if cost["delay"] is None else cost["delay"],
                        "score_source": component["score_source"],
                        "gate_formula": component["gate_formula"],
                        "delay_formula": component["delay_formula"],
                        "component_gate_dependency": component["component_gate_dependency"] or "",
                        "component_delay_dependency": component["component_delay_dependency"] or "",
                        "slot": component["slot"],
                        "hash": component["hash"],
                    }
                )


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, default=DEFAULT_EXE)
    parser.add_argument(
        "--common-nim",
        type=Path,
        default=repo_root / ".research" / "save_monger_current" / "common.nim",
    )
    parser.add_argument("--json", type=Path, default=script_dir / "component_scores.json")
    parser.add_argument("--csv", type=Path, default=script_dir / "component_scores.csv")
    args = parser.parse_args()

    exe = args.exe.resolve()
    exe_sha256 = sha256_file(exe)
    if exe_sha256 != EXPECTED_SHA256:
        raise SystemExit(
            f"refusing unknown executable build: sha256={exe_sha256}, expected={EXPECTED_SHA256}"
        )

    names = parse_component_kinds(args.common_nim.resolve())
    reader = PeReader(exe)
    entries, descriptor = extract_score_table(reader, names)
    jump_groups = extract_gate_jump_table(reader, names)
    bitmap = extract_default_kind_bitmap(reader, names)
    by_kind = {entry["kind"]: entry for entry in entries}
    run_self_tests(by_kind)

    output = build_output(exe, exe_sha256, entries, descriptor, jump_groups, bitmap)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    write_csv(args.csv, output)

    print(f"verified exe sha256: {exe_sha256}")
    print(f"decoded components: {len(entries)} (kinds {entries[0]['kind']}..{entries[-1]['kind']})")
    print(f"gate jump target groups: {len(jump_groups)}")
    print(f"default-table bitmap: {bitmap['raw_hex']}")
    print(f"wrote {args.json}")
    print(f"wrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
