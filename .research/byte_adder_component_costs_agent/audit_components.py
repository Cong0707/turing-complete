"""Build a read-only Byte Adder component/cost evidence certificate."""

from __future__ import annotations

import csv
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from tc_save_lab.codec import decode_circuit  # noqa: E402


GAME = Path(r"D:\Game\Steam\steamapps\common\Turing Complete")
SAVE = Path(r"C:\Users\cong\AppData\Roaming\Turing Complete")
SCORE_TABLE = (
    PROJECT
    / "examples"
    / "rng"
    / "research"
    / "archive"
    / "rng_score_table"
    / "component_scores.json"
)
RELEVANT_KINDS = {
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    30,
    47,
    48,
    97,
    98,
    99,
    100,
    109,
    110,
    111,
    112,
    114,
    115,
    116,
}
LEVELS = (
    "not_gate",
    "xor_gate",
    "or_gate_3",
    "and_gate_3",
    "xnor",
    "full_adder",
    "bit_switch",
    "byte_nand",
    "byte_not",
    "byte_adder",
    "byte_xor",
    "double_number",
    "one_hot_encoding",
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def parse_frontier(value: str) -> list[list[int]]:
    return [
        [int(field) for field in item.split("&")]
        for item in value.split("|")
        if item
    ]


def level_state() -> dict[str, object]:
    with (SAVE / "levels.txt").open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.reader(stream))
    by_level = {row[0]: row for row in rows if len(row) == 4}
    result = {}
    for level in LEVELS:
        row = by_level[level]
        meta = (GAME / "campaign" / level / "meta.txt").read_text(encoding="utf-8")
        unlock = next(
            (line.strip() for line in meta.splitlines() if line.startswith("unlocks_components")),
            None,
        )
        result[level] = {
            "complete": row[1].lower() == "true",
            "selected": row[2],
            "saved_frontier": parse_frontier(row[3]),
            "unlock_declaration": unlock,
        }
    return result


def circuit_record(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    circuit = decode_circuit(payload)
    return {
        "path": str(path),
        "sha256": sha256(payload).hexdigest(),
        "format_version": payload[0],
        "header": [circuit.gate, circuit.delay, circuit.energy],
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "kind_width_counts": {
            f"{kind}:{width}": sum(
                component.kind == kind and component.word_size == width
                for component in circuit.components
            )
            for kind, width in sorted(
                {(component.kind, component.word_size) for component in circuit.components}
            )
        },
        "all_cost_fields_auto": all(
            (component.cost_gate, component.cost_delay) == (-1, 0)
            for component in circuit.components
        ),
    }


def static_score_records() -> dict[str, object]:
    table = json.loads(SCORE_TABLE.read_text(encoding="utf-8"))
    result = {}
    for component in table["components"]:
        kind = component["kind"]
        if kind not in RELEVANT_KINDS:
            continue
        width_rows = {
            str(item["width"]): [item["gate"], item["delay"]]
            for item in component["costs_by_width"]
            if item["width"] in {1, 2, 3, 4, 8}
        }
        result[str(kind)] = {
            "name": component["name"],
            "default": [component["default_gate"], component["default_delay"]],
            "score_source": component["score_source"],
            "gate_formula": component["gate_formula"],
            "delay_formula": component["delay_formula"],
            "static_width_matrix": width_rows,
        }
    return result


def main() -> None:
    prototype_path = HERE / "native_prototypes.json"
    related = {
        "byte_adder_formal": SAVE / "schematics" / "byte_adder" / "Default" / "circuit.data",
        "byte_adder_candidate": PROJECT / "examples" / "byte_adder" / "candidate" / "circuit.data",
        "bit_xor_direct": SAVE / "schematics" / "bit_inverter" / "Default" / "circuit.data",
        "word_xor_u8_direct": SAVE / "schematics" / "byte_xor" / "Default" / "circuit.data",
        "word_not_u8_direct": SAVE / "schematics" / "byte_not" / "Default" / "circuit.data",
        "word_nand_u8_direct": SAVE / "schematics" / "byte_nand" / "Default" / "circuit.data",
        "switch_bit_equation": SAVE / "schematics" / "bit_switch" / "Default" / "circuit.data",
        "switch_word_u8_equation": SAVE / "schematics" / "the_bus" / "Default" / "circuit.data",
        "split_make_zero_equation": SAVE / "schematics" / "double_number" / "Default" / "circuit.data",
        "full_adder_custom": SAVE / "schematics" / "full_adder" / "Default" / "circuit.data",
        "campaign_byte_adder_scaffold": GAME / "campaign" / "byte_adder" / "circuit.data",
        "campaign_byte_adder_hint": GAME / "campaign" / "byte_adder" / "hint_solution.data",
    }
    evidence = {
        "schema": 1,
        "scope": "read-only static/current-save Byte Adder component audit",
        "runtime_files": {
            "exe": {"path": str(GAME / "Turing Complete.exe"), "sha256": digest(GAME / "Turing Complete.exe")},
            "compile_dll": {"path": str(GAME / "compile.dll"), "sha256": digest(GAME / "compile.dll")},
            "game_engine_dll": {"path": str(GAME / "game_engine.dll"), "sha256": digest(GAME / "game_engine.dll")},
            "byte_adder_meta": {
                "path": str(GAME / "campaign" / "byte_adder" / "meta.txt"),
                "sha256": digest(GAME / "campaign" / "byte_adder" / "meta.txt"),
            },
        },
        "current_level_state": level_state(),
        "circuits": {name: circuit_record(path) for name, path in related.items()},
        "static_executable_score_table": {
            "source": str(SCORE_TABLE),
            "sha256": digest(SCORE_TABLE),
            "warning": (
                "Defaults are only the initial table. score.nim imports level Pareto costs at "
                "runtime; narrow word-XOR values also conflict with current live observations."
            ),
            "components": static_score_records(),
        },
        "native_prototypes": json.loads(prototype_path.read_text(encoding="ascii")),
        "strict_beat_515_thresholds": {
            str(delay): (514 // delay) for delay in range(4, 19)
        },
        "derived_facts": {
            "byte_adder_saved_frontier_is_empty": not level_state()["byte_adder"]["saved_frontier"],
            "direct_com_add_header_is_not_runtime_cost_proof": True,
            "u8_xor_current_file_header": [24, 2],
            "bit_xor_current_file_header": [3, 2],
            "u8_not_current_file_header": [8, 1],
            "u8_nand_current_file_header": [8, 1],
            "bit_switch_cost_derived_from_2_switch_plus_2_not_equals_6": [2, 1],
            "u8_switch_gate_derived_from_4_switch_plus_2_not_equals_66": 16,
            "splitter_maker_cost": [0, 0],
            "custom_full_adder_current_file_header": [7, 4],
            "custom_full_adder_saved_frontier": level_state()["full_adder"]["saved_frontier"],
            "custom_full_adder_file_header_is_not_runtime_cost_proof": True,
        },
    }
    (HERE / "component_evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
