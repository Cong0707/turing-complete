#!/usr/bin/env python3
"""Reproduce the native RAM-port audit without starting the game."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re

from tc_save_lab.analysis import wire_points
from tc_save_lab.codec import decode_v15


ROOT = Path(__file__).resolve().parents[5]
AUDIT_DIR = Path(__file__).resolve().parent
NATIVE_PROTOTYPES = (
    ROOT / ".research" / "rng_primitive_zero_audit" / "native_prototypes.json"
)
DESERIALIZE_DIR = (
    ROOT
    / ".research"
    / "rng_primitive_zero_audit"
    / "ram_enum_acceptance"
    / "deserialize_ui"
)
CONNECT_TO_RAM = (
    ROOT
    / ".research"
    / "rng_score_bypass"
    / "ida"
    / "ram"
    / "connect_to_ram.c"
)
SOURCE_CANDIDATE = ROOT / "src" / "tc_save_lab" / "rng_ram_asic.py"
GAME_BINARY = Path(
    r"D:\Game\Steam\steamapps\common\Turing Complete\Turing Complete.exe"
)
LIVE_MEMORYREGFILE = Path(
    r"C:\Users\cong\AppData\Roaming\Turing Complete\schematics"
    r"\foundry\RISCV\MEMORYREGFILE\circuit.data"
)


# Native prototype coordinates. The extra unnamed placeholder pins in kinds
# 54/56 are intentionally omitted because no wire may terminate on them.
NATIVE_PINS = {
    54: (("enable", (-15, -1)), ("address", (-15, 0)), ("out", (16, -1))),
    56: (("enable", (-15, -1)), ("address", (-15, 0)), ("data", (-15, 1))),
    118: (),
}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def pin_position(position: tuple[int, int], offset: tuple[int, int], rotation: int):
    x, y = offset
    dx, dy = ((x, y), (-y, x), (-x, -y), (y, -x))[rotation]
    return position[0] + dx, position[1] + dy


def sample_record(path: Path) -> dict[str, object]:
    circuit = decode_v15(path.read_bytes())
    endpoints = Counter(
        point
        for wire in circuit.wires
        for point in (wire_points(wire)[0], wire_points(wire)[-1])
    )
    components = []
    for component in circuit.components:
        if component.kind not in NATIVE_PINS:
            continue
        pins = {
            name: pin_position(component.position, offset, component.rotation)
            for name, offset in NATIVE_PINS[component.kind]
        }
        components.append(
            {
                "kind": component.kind,
                "position": list(component.position),
                "rotation": component.rotation,
                "word_size": component.word_size,
                "buffer_size": component.buffer_size,
                "settings": list(component.settings),
                "native_pins": {name: list(point) for name, point in pins.items()},
                "wire_endpoint_hits": {
                    name: endpoints[point] for name, point in pins.items()
                },
            }
        )
    try:
        display_path = str(path.relative_to(ROOT))
    except ValueError:
        display_path = str(path)
    return {
        "path": display_path,
        "sha256": digest(path),
        "component_counts": {
            str(kind): sum(item.kind == kind for item in circuit.components)
            for kind in NATIVE_PINS
        },
        "ram_components": components,
    }


def require(pattern: str, text: str, description: str) -> str:
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if match is None:
        raise RuntimeError(f"missing expected native evidence: {description}")
    return match.group(0)


def main() -> None:
    prototypes = json.loads(NATIVE_PROTOTYPES.read_text(encoding="utf-8"))["records"]
    prototype_port_counts = {
        kind: {
            offset: prototypes[kind]["pin_sequences"][offset]["length"]
            for offset in ("96", "112", "128")
        }
        for kind in ("54", "56", "118")
    }
    if prototype_port_counts["118"] != {"96": 0, "112": 0, "128": 0}:
        raise RuntimeError("native kind 118 unexpectedly gained pins")
    if prototype_port_counts["54"] != {"96": 3, "112": 0, "128": 2}:
        raise RuntimeError("native kind 54 prototype changed")
    if prototype_port_counts["56"] != {"96": 5, "112": 0, "128": 1}:
        raise RuntimeError("native kind 56 prototype changed")

    load_source = (DESERIALIZE_DIR / "load_schematic_raw.c").read_text(
        encoding="utf-8"
    )
    board_source = (DESERIALIZE_DIR / "board_add_component.c").read_text(
        encoding="utf-8"
    )
    compiler_source = CONNECT_TO_RAM.read_text(encoding="utf-8")
    candidate_source = SOURCE_CANDIDATE.read_text(encoding="utf-8")

    load_loop = require(
        r"while \( v116 < v103 \).*?board_add_component__modelZboardZboard_u21118\(",
        load_source,
        "one board-add call inside the serialized-component loop",
    )
    if load_loop.count("board_add_component__modelZboardZboard_u21118(") != 1:
        raise RuntimeError("load loop no longer has exactly one board-add call")
    if "v172 == 118" in board_source or "v172 == 0x76" in board_source:
        raise RuntimeError("board_add_component gained a kind-118 expansion branch")
    require(
        r"v82 = v111 \+ v112;",
        board_source,
        "board allocation from prototype pin groups 96 and 112",
    )
    require(
        r"v124 = v113;",
        board_source,
        "board allocation from prototype pin group 128",
    )

    require(
        r"LOBYTE\(v76\[0\]\) == 54 \|\| LOBYTE\(v76\[0\]\) == 56",
        compiler_source,
        "compiler RAM-port kind dispatch",
    )
    require(
        r"if \( LOBYTE\(v73\[0\]\) == 118 \)",
        compiler_source,
        "compiler backing-RAM target check",
    )

    candidate_kind_counts = {
        "kind_118_literals": len(re.findall(r"\b118\b", candidate_source)),
        "kind_54_literals": len(re.findall(r"\b54\b", candidate_source)),
        "kind_56_literals": len(re.findall(r"\b56\b", candidate_source)),
    }
    require(
        r"route\(_pin\(one, \"out\"\), _pin\(ram, \"load\"\)\)",
        candidate_source,
        "202 candidate directly wiring a fabricated RAM load pin",
    )
    require(
        r"route\(_pin\(feedback_word_maker, \"out\"\), _pin\(ram, \"in\"\)\)",
        candidate_source,
        "202 candidate directly wiring a fabricated RAM data pin",
    )

    sample_paths = (
        LIVE_MEMORYREGFILE,
        ROOT / "examples" / "_architectures" / "RV64" / "baseline" / "circuit.data",
        ROOT
        / "examples"
        / "symphony_12_budget"
        / "baseline"
        / "circuit.data",
        ROOT
        / ".research"
        / "rng_primitive_zero_audit"
        / "ram2_candidate"
        / "circuit.data",
    )
    result = {
        "schema": 1,
        "game_binary": {
            "path": str(GAME_BINARY),
            "sha256": digest(GAME_BINARY),
        },
        "native_prototype_port_counts": prototype_port_counts,
        "v15_and_board_load": {
            "serialized_component_loop_found": True,
            "board_add_calls_per_loop_iteration": 1,
            "kind_118_auto_expansion_branch": False,
            "runtime_pin_groups_are_native_prototype_groups_96_112_128": True,
        },
        "compiler_association": {
            "port_kinds": [54, 56],
            "backing_ram_kind": 118,
            "direction": "kind 54/56 searches spatially for kind 118",
        },
        "candidate_source": {
            "path": str(SOURCE_CANDIDATE.relative_to(ROOT)),
            "sha256": digest(SOURCE_CANDIDATE),
            **candidate_kind_counts,
            "uses_fabricated_aggregate_ram_pins": True,
        },
        "samples": [sample_record(path) for path in sample_paths],
        "verdict": {
            "kind_118_has_aggregate_wire_ports": False,
            "kind_54_load_component_required": True,
            "kind_56_store_component_required": True,
            "ram202_candidate_native_compile_ready": False,
        },
    }
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    (AUDIT_DIR / "evidence.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps(result["verdict"], sort_keys=True))


if __name__ == "__main__":
    main()
