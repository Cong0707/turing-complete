"""Build the current 2.1.292 pre-Byte-Adder component/byproduct catalog.

The output deliberately separates five evidence classes:

* current executable static evidence (prototype, score table and codegen);
* current installed campaign metadata/tests;
* legacy generated certificates (saved/imported frontiers and exact proofs);
* repository offline models (the reviewed 80/7 Factory DAG);
* derived truth-table and structural consequences.

The script never reads a live save/candidate/history tree, never launches the
game and never materializes a circuit.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import itertools
import json
from pathlib import Path
import re
from typing import Callable, Iterable, Sequence

import build_truth_byproduct_catalog as truth


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXE_PATH = Path(r"D:\Game\Steam\steamapps\common\Turing Complete\Turing Complete.exe")
STEAM_MANIFEST_PATH = Path(r"D:\Game\Steam\steamapps\appmanifest_1444480.acf")
CAMPAIGN_PATH = Path(r"D:\Game\Steam\steamapps\common\Turing Complete\campaign")

PROTOTYPE_PATH = HERE / "pretarget-prototypes-2.1.292.json"
RUNTIME_PATH = HERE / "runtime-evidence-2.1.292.json"
COST_IMPORT_PATH = HERE / "cost-import-semantics-2.1.292.json"
CODEGEN_CASE_PATH = HERE / "pretarget-codegen-cases-2.1.292.json"
CODEGEN_SWITCH_PATH = HERE / "codegen-switches-2.1.292.json"
CODEGEN_CORE_PATH = HERE / "codegen-core-evidence-2.1.292.json"
DELAY_DISASM_PATH = HERE / "delay-codegen-disasm-2.1.292.json"
AVAILABILITY_PATH = (
    ROOT / ".research/byte_adder_component_costs_agent/byte_adder_available_primitives.json"
)
DAG_PATH = (
    ROOT
    / ".research/byte_adder_av_reduced_forward/byte-adder-hybrid-shared-s34-audit-g80-d7.json"
)
FULL_ADDER_AUDIT_PATH = (
    ROOT
    / ".research/byte_adder_hybrid_native_agent/full_adder_macro/full_adder_macro_audit.json"
)

DEFAULT_OUTPUT = HERE / "component-catalog-v1.json"
DEFAULT_REPORT = HERE / "2026-08-04-字节加法器全元件副产物与短弧审计.md"

CURRENT_EXE_SHA256 = "fcfe38fc349ea0f481ba7ece557d195da0b68b8b63b6371b4b4920ad27eccf11"
CURRENT_EXE_SIZE = 15_801_878
CURRENT_VERSION = "2.1.292"
CURRENT_BUILD_ID = "24536614"

SELECTED_KINDS = (
    1,
    2,
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
    13,
    15,
    16,
    17,
    18,
    21,
    25,
    109,
    110,
    111,
    112,
)

# These are the enum/campaign symbols in the pre-target closure certificate.
# kind 16/17 are intentionally retained verbatim even though the current
# prototype and codegen prove that their display/behavior roles are Maker and
# Splitter respectively.  The catalog calls that naming mismatch out explicitly.
SYMBOL_NAMES = {
    1: "com_off",
    2: "com_on",
    3: "com_not_bit",
    4: "com_and_bit",
    5: "com_and_3_bit",
    6: "com_nand_bit",
    7: "com_or_bit",
    8: "com_or_3_bit",
    9: "com_nor_bit",
    10: "com_xor_bit",
    11: "com_xnor_bit",
    12: "com_switch_bit",
    13: "com_delay_line_bit",
    15: "com_full_adder",
    16: "com_splitter_bit_8",
    17: "com_maker_bit_8",
    18: "com_not_word",
    21: "com_nand_word",
    25: "com_switch_word",
    109: "com_splitter_bit_2",
    110: "com_splitter_bit_4",
    111: "com_maker_bit_2",
    112: "com_maker_bit_4",
}

SEMANTIC_ROLES = {
    1: "constant_active_zero",
    2: "constant_active_one",
    3: "bit_not",
    4: "bit_and2",
    5: "bit_and3",
    6: "bit_nand2",
    7: "bit_or2",
    8: "bit_or3",
    9: "bit_nor2",
    10: "bit_xor2",
    11: "bit_xnor2",
    12: "bit_tristate_switch",
    13: "one_tick_bit_delay",
    15: "bit_full_adder",
    16: "maker_word_8",
    17: "splitter_word_8",
    18: "word_not_lane_parallel",
    21: "word_nand_lane_parallel",
    25: "word_tristate_switch_shared_enable",
    109: "splitter_word_2",
    110: "splitter_word_4",
    111: "maker_word_2",
    112: "maker_word_4",
}

# Legacy saved/imported frontier certificate.  These are not current EXE
# defaults and are never merged with the defaults.  The current EXE import
# semantics prove that a non-empty frontier replaces the default candidate set.
IMPORTED_FRONTIERS = {
    3: [(1, 1, 1)],
    5: [(3, 2, 1)],
    8: [(3, 2, 1)],
    10: [(3, 2, 1)],
    11: [(5, 4, 1)],
    15: [(16, 8, 1)],
    18: [(8, 1, 1)],
    21: [(8, 1, 1)],
}

CAMPAIGN_FILES = (
    "always_on/meta.txt",
    "nand_gate/meta.txt",
    "not_gate/meta.txt",
    "and_gate/meta.txt",
    "nor_gate/meta.txt",
    "or_gate/meta.txt",
    "second_tick/meta.txt",
    "xor_gate/meta.txt",
    "or_gate_3/meta.txt",
    "and_gate_3/meta.txt",
    "xnor/meta.txt",
    "double_number/meta.txt",
    "full_adder/meta.txt",
    "bit_switch/meta.txt",
    "byte_nand/meta.txt",
    "byte_not/meta.txt",
    "double_buffer/meta.txt",
    "double_buffer/test.si",
    "odd_ticks/meta.txt",
    "odd_ticks/test.si",
    "byte_adder/meta.txt",
    "byte_mux/meta.txt",
)

FUNCTION_EVIDENCE = {
    "get_cost": {
        "address": "0x0000000140279367",
        "machine_sha256": "6215c4710e2b74fa81b4ea7445d8a2e3aebd192498c5a3c1173cf4eb16a454b8",
    },
    "insert_cost_low_level": {
        "address": "0x000000014027abe9",
        "machine_sha256": "f5797ff58447a509863ab7c98f3423e2fe85cad83db59e8382676105f5955a84",
    },
    "insert_cost_wrapper": {
        "address": "0x000000014027b949",
        "machine_sha256": "797b3ee15719887a49415864601c9de36151c1cedd8b3b30f8ff7924b38dae1c",
    },
    "add_cost": {
        "address": "0x000000014027c64a",
        "machine_sha256": "d919f81ecc7c08f8da8d2263a8f215f6b269a8aacd960cbabc8b28161109acad",
    },
    "import_costs": {
        "address": "0x000000014027cad9",
        "machine_sha256": "729e3f9eade5be5227b92e549d5750af488b2554cd19b1a9a85cf5ca334ef05a",
    },
    "complete_level": {
        "address": "0x00000001405ab6d5",
        "machine_sha256": "1c3d03307046b0bcb931f2518262da1e641f51f94f9a88fec1c93f7bdb4f5d43",
    },
    "process_network_responses": {
        "address": "0x000000014065735f",
        "machine_sha256": "6c72ea05ee275aef5ac0ed90d3d6a3d8f0043dc5bbf5633dd3abfb247c435ce3",
    },
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def packed_bytes(mask: int, rows: int) -> bytes:
    return (mask & ((1 << rows) - 1)).to_bytes((rows + 7) // 8, "little")


def mask_record(mask: int, rows: int) -> dict[str, object]:
    raw = packed_bytes(mask, rows)
    return {
        "encoding": "row-index bitset, little-endian within and across bytes",
        "row_count": rows,
        "byte_count": len(raw),
        "ones": mask.bit_count(),
        "sha256": sha256(raw).hexdigest(),
    }


def physical_truth_sha(value: int, driven: int, conflict: int, rows: int) -> str:
    return sha256(
        canonical_json(
            {
                "schema": "tc-physical-truth-summary-v1",
                "rows": rows,
                "value": mask_record(value, rows)["sha256"],
                "driven": mask_record(driven, rows)["sha256"],
                "conflict": mask_record(conflict, rows)["sha256"],
            }
        )
    ).hexdigest()


def normalized_word_size(token: int) -> int | str:
    return "component_word_width" if token == 0x7FFFFFFFFFFFFFFF else token


def pin_label(pin: dict[str, object], fallback: str) -> str:
    labels = [str(item["text"]) for item in pin["labels"]]
    return labels[0] if labels else fallback


def flatten_pins(record: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for sequence_name in ("inputs", "bidirectional", "outputs"):
        for index, pin in enumerate(record["pin_sequences"][sequence_name]["pins"]):
            raw = bytes.fromhex(str(pin["raw_hex"]))
            rows.append(
                {
                    "pin_id": f"{sequence_name}.{index}",
                    "sequence": sequence_name,
                    "sequence_index": index,
                    "direction_code": int(pin["direction_code"]),
                    "direction": pin["direction"],
                    "offset": pin["offset"],
                    "word_size_token_raw": int(pin["word_size_token"]),
                    "word_size": normalized_word_size(int(pin["word_size_token"])),
                    "labels": [item["text"] for item in pin["labels"]],
                    "semantic_name": pin_label(pin, f"{sequence_name}_{index}"),
                    "raw_record_sha256": sha256(raw).hexdigest(),
                    "public": True,
                }
            )
    return rows


def codegen_summary(case: dict[str, object]) -> dict[str, object]:
    symbols = (
        "input__modelZsimulationZcode95gen_u4256",
        "input__modelZsimulationZcode95gen_u4120",
        "store_output__modelZsimulationZcode95gen_u2219",
        "load_and_output__modelZsimulationZcode95gen_u3938",
        "store_bit__modelZsimulationZcode95gen_u2177",
        "store_word__modelZsimulationZcode95gen_u2199",
        "add_line__modelZsimulationZcode95gen_u2129",
    )
    counts = {
        symbol: sum(symbol in str(ins["text"]) for ins in case["instructions"])
        for symbol in symbols
    }
    ignore = {
        "USH",
        "UH",
        "UWVSH",
        "\n",
        r"D:\TuringComplete_Phu\model\simulation\code_gen.nim",
        r"C:\Users\Admin\.choosenim\toolchains\nim-2.2.6\lib\system.nim",
    }
    fragments = []
    for item in case["static_strings"]:
        value = str(item["value"])
        if value in ignore or value.endswith(".nim") or value in fragments:
            continue
        fragments.append(value)
    input_call_sites = []
    instructions = case["instructions"]
    for index, instruction in enumerate(instructions):
        text = str(instruction["text"])
        match = re.search(
            r"lea\s+rax,\s+(input__modelZsimulationZcode95gen_u(?:4120|4256))",
            text,
        )
        if not match:
            continue
        window = instructions[index : index + 45]
        call_index = next(
            (offset for offset, item in enumerate(window) if str(item["text"]) == "call    r10"),
            None,
        )
        call_window = window if call_index is None else window[: call_index + 1]
        preserve_z_zero = any(
            re.search(r"mov\s+dword ptr \[rsp[^]]+\],\s+0$", str(item["text"]))
            for item in call_window
        )
        pin_index = None
        width: int | str | None = None
        for item in call_window:
            item_text = str(item["text"])
            pin_match = re.fullmatch(r"mov\s+r8d,\s+([0-9A-Fa-f]+)h?", item_text)
            if pin_match:
                pin_index = int(pin_match.group(1), 16 if "h" in item_text.lower() else 10)
            width_match = re.fullmatch(r"mov\s+r9d,\s+([0-9A-Fa-f]+)h?", item_text)
            if width_match:
                width = int(width_match.group(1), 16 if "h" in item_text.lower() else 10)
            if re.fullmatch(r"mov\s+r9,\s+r8", item_text):
                width = "dynamic_component_or_bits_width"
        input_call_sites.append(
            {
                "function": match.group(1),
                "function_pointer_load": instruction["address"],
                "first_indirect_call": (
                    call_window[-1]["address"] if call_index is not None else None
                ),
                "pin_index": pin_index,
                "requested_expression_word_width": width,
                "preserve_z_zero": preserve_z_zero,
                "argument_rule": (
                    "Windows x64: [rsp+0x20] is input() argument 5 preserve_z; the audited call setup writes 0"
                ),
            }
        )
    return {
        "case_target": case["target"],
        "case_range_end": case["range_end"],
        "case_range_rule": case["range_rule"],
        "instruction_count": case["instruction_count"],
        "code_bytes_sha256": case["code_bytes_sha256"],
        "symbol_reference_counts": {key: value for key, value in counts.items() if value},
        "input_call_sites": input_call_sites,
        "template_fragments": fragments,
        "full_instruction_evidence": CODEGEN_CASE_PATH.name,
    }


def logic_spec(
    kind: int,
) -> tuple[tuple[str, ...], tuple[str, ...], Callable[[tuple[int, ...]], tuple[tuple[int, ...], tuple[int, ...]]]] | None:
    active = lambda values: tuple(1 for _ in values)
    if kind == 1:
        return (), ("Output",), lambda _x: ((0,), (1,))
    if kind == 2:
        return (), ("Output",), lambda _x: ((1,), (1,))
    if kind == 3:
        return ("A",), ("Output",), lambda x: ((1 ^ x[0],), (1,))
    if kind == 4:
        return ("A", "B"), ("Output",), lambda x: ((x[0] & x[1],), (1,))
    if kind == 5:
        return ("A", "B", "C"), ("Output",), lambda x: ((x[0] & x[1] & x[2],), (1,))
    if kind == 6:
        return ("A", "B"), ("Output",), lambda x: ((1 ^ (x[0] & x[1]),), (1,))
    if kind == 7:
        return ("A", "B"), ("Output",), lambda x: ((x[0] | x[1],), (1,))
    if kind == 8:
        return ("A", "B", "C"), ("Output",), lambda x: ((x[0] | x[1] | x[2],), (1,))
    if kind == 9:
        return ("A", "B"), ("Output",), lambda x: ((1 ^ (x[0] | x[1]),), (1,))
    if kind == 10:
        return ("A", "B"), ("Output",), lambda x: ((x[0] ^ x[1],), (1,))
    if kind == 11:
        return ("A", "B"), ("Output",), lambda x: ((1 ^ x[0] ^ x[1],), (1,))
    if kind == 12:
        return ("Enable", "Data"), ("Result",), lambda x: ((x[0] & x[1],), (x[0],))
    if kind == 15:
        def full_adder(x: tuple[int, ...]):
            cin, a, b = x
            return ((a ^ b ^ cin, (a & b) | (a & cin) | (b & cin)), (1, 1))

        return ("Cin", "A", "B"), ("Result", "CarryOut"), full_adder
    if kind in {16, 17, 109, 110, 111, 112}:
        return ("LaneValue",), ("LaneResult",), lambda x: ((x[0],), (1,))
    if kind == 18:
        return ("LaneA",), ("LaneResult",), lambda x: ((1 ^ x[0],), (1,))
    if kind == 21:
        return ("LaneA", "LaneB"), ("LaneResult",), lambda x: ((1 ^ (x[0] & x[1]),), (1,))
    if kind == 25:
        return ("Enable", "LaneData"), ("LaneResult",), lambda x: ((x[0] & x[1],), (x[0],))
    return None


def truth_label(variables: Sequence[str], value: int) -> str:
    rows = 1 << len(variables)
    mask = (1 << rows) - 1
    if value == 0:
        return "CONST0"
    if value == mask:
        return "CONST1"
    columns = {}
    for index, name in enumerate(variables):
        column = 0
        for row in range(rows):
            column |= ((row >> index) & 1) << row
        columns[name] = column
    for name, column in columns.items():
        if value == column:
            return name
        if value == ((~column) & mask):
            return f"NOT({name})"
    if len(variables) == 2:
        a, b = (columns[name] for name in variables)
        known = {
            a & b: f"AND({variables[0]},{variables[1]})",
            a | b: f"OR({variables[0]},{variables[1]})",
            (~(a & b)) & mask: f"NAND({variables[0]},{variables[1]})",
            (~(a | b)) & mask: f"NOR({variables[0]},{variables[1]})",
            a ^ b: f"XOR({variables[0]},{variables[1]})",
            (~(a ^ b)) & mask: f"XNOR({variables[0]},{variables[1]})",
        }
        if value in known:
            return known[value]
    if len(variables) == 3:
        a, b, c = (columns[name] for name in variables)
        known = {
            a & b & c: "AND3(" + ",".join(variables) + ")",
            a | b | c: "OR3(" + ",".join(variables) + ")",
            a ^ b ^ c: "PARITY3(" + ",".join(variables) + ")",
            (a & b) | (a & c) | (b & c): "MAJORITY3(" + ",".join(variables) + ")",
        }
        if value in known:
            return known[value]
    return f"truth_bits:0x{value:x}"


def native_truth_and_cofactors(kind: int) -> dict[str, object] | None:
    spec = logic_spec(kind)
    if spec is None:
        return None
    inputs, outputs, evaluator = spec
    full_rows = 1 << len(inputs)
    full_values = [0 for _ in outputs]
    full_driven = [0 for _ in outputs]
    for assignment in range(full_rows):
        vector = tuple((assignment >> index) & 1 for index in range(len(inputs)))
        values, driven = evaluator(vector)
        for index in range(len(outputs)):
            full_values[index] |= values[index] << assignment
            full_driven[index] |= driven[index] << assignment
    full = []
    for index, output in enumerate(outputs):
        full.append(
            {
                "output": output,
                "value": mask_record(full_values[index], full_rows),
                "driven": mask_record(full_driven[index], full_rows),
                "conflict": mask_record(0, full_rows),
                "physical_truth_sha256": physical_truth_sha(
                    full_values[index], full_driven[index], 0, full_rows
                ),
                "value_label": truth_label(inputs, full_values[index]),
            }
        )

    cofactors = []
    # -1 means free, 0/1 mean tied to the corresponding active constant.
    for states in itertools.product((-1, 0, 1), repeat=len(inputs)):
        remaining = tuple(name for name, state in zip(inputs, states, strict=True) if state == -1)
        rows = 1 << len(remaining)
        values_by_output = [0 for _ in outputs]
        driven_by_output = [0 for _ in outputs]
        for assignment in range(rows):
            free_index = 0
            vector = []
            for state in states:
                if state == -1:
                    vector.append((assignment >> free_index) & 1)
                    free_index += 1
                else:
                    vector.append(state)
            values, driven = evaluator(tuple(vector))
            for index in range(len(outputs)):
                values_by_output[index] |= values[index] << assignment
                driven_by_output[index] |= driven[index] << assignment
        fixed = {
            name: state
            for name, state in zip(inputs, states, strict=True)
            if state != -1
        }
        cofactor_outputs = []
        for index, output in enumerate(outputs):
            cofactor_outputs.append(
                {
                    "output": output,
                    "value_label": truth_label(remaining, values_by_output[index]),
                    "value": mask_record(values_by_output[index], rows),
                    "driven": mask_record(driven_by_output[index], rows),
                    "physical_truth_sha256": physical_truth_sha(
                        values_by_output[index], driven_by_output[index], 0, rows
                    ),
                }
            )
        cofactors.append(
            {
                "fixed_active_inputs": fixed,
                "remaining_inputs": list(remaining),
                "row_count": rows,
                "outputs": cofactor_outputs,
            }
        )
    return {
        "domain": {
            "inputs": list(inputs),
            "row_count": full_rows,
            "assignment_order": "row index bits follow inputs[] order, least-significant bit first",
        },
        "outputs": full,
        "complete_active_constant_cofactor_table": cofactors,
        "cofactor_count": len(cofactors),
    }


def relation_catalog(signals: dict[str, tuple[int, int, int]], rows: int) -> dict[str, object]:
    mask = (1 << rows) - 1
    pairwise = []
    names = sorted(signals)
    for index, left_name in enumerate(names):
        lv, ld, lc = signals[left_name]
        for right_name in names[index + 1 :]:
            rv, rd, rc = signals[right_name]
            data_equal = lv == rv
            physical_equal = data_equal and ld == rd and lc == rc
            data_complement = ((lv ^ rv) & mask) == mask
            same_driven_complement = (
                ld == rd and ld != 0 and (((lv ^ rv) & ld) == ld)
            )
            mutex = (lv & rv) == 0
            left_implies_right = (lv & (~rv & mask)) == 0
            right_implies_left = (rv & (~lv & mask)) == 0
            if not any(
                (
                    data_equal,
                    physical_equal,
                    data_complement,
                    same_driven_complement,
                    mutex,
                    left_implies_right,
                    right_implies_left,
                )
            ):
                continue
            pairwise.append(
                {
                    "left": left_name,
                    "right": right_name,
                    "data_plane_equivalent": data_equal,
                    "physical_truth_equivalent": physical_equal,
                    "data_plane_complement": data_complement,
                    "same_driven_domain_complement": same_driven_complement,
                    "mutex": mutex,
                    "left_implies_right": left_implies_right,
                    "right_implies_left": right_implies_left,
                    "strict_left_implies_right": left_implies_right and not data_equal,
                    "strict_right_implies_left": right_implies_left and not data_equal,
                }
            )
    counts = Counter()
    for row in pairwise:
        for key, value in row.items():
            if key not in {"left", "right"} and value:
                counts[key] += 1
    return {"pair_count_with_any_relation": len(pairwise), "counts": dict(counts), "pairs": pairwise}


EXPANSIONS = {
    5: {
        "name": "AND3 two-gate tree",
        "inputs": ["A", "B", "C"],
        "nodes": [
            {"id": "AB", "op": "AND", "args": ["A", "B"]},
            {"id": "Output", "op": "AND", "args": ["AB", "C"]},
        ],
        "outputs": {"Output": "Output"},
        "minimal_gate": 2,
        "proof": "complete one-gate lower-bound enumeration; two-gate witness",
    },
    8: {
        "name": "OR3 two-gate tree",
        "inputs": ["A", "B", "C"],
        "nodes": [
            {"id": "AB", "op": "OR", "args": ["A", "B"]},
            {"id": "Output", "op": "OR", "args": ["AB", "C"]},
        ],
        "outputs": {"Output": "Output"},
        "minimal_gate": 2,
        "proof": "complete one-gate lower-bound enumeration; two-gate witness",
    },
    10: {
        "name": "XOR G/K/P",
        "inputs": ["A", "B"],
        "nodes": [
            {"id": "G", "op": "AND", "args": ["A", "B"]},
            {"id": "K", "op": "NOR", "args": ["A", "B"]},
            {"id": "P", "op": "NOR", "args": ["G", "K"]},
        ],
        "outputs": {"Output": "P"},
        "minimal_gate": 3,
        "proof": "complete one- and two-gate live-DAG enumeration; three-gate witness",
    },
    11: {
        "name": "XNOR G/K/Q",
        "inputs": ["A", "B"],
        "nodes": [
            {"id": "G", "op": "AND", "args": ["A", "B"]},
            {"id": "K", "op": "NOR", "args": ["A", "B"]},
            {"id": "Q", "op": "OR", "args": ["G", "K"]},
        ],
        "outputs": {"Output": "Q"},
        "minimal_gate": 3,
        "proof": "complete one- and two-gate live-DAG enumeration; three-gate witness",
    },
    12: {
        "name": "Switch Boolean data-plane projection",
        "inputs": ["Enable", "Data"],
        "nodes": [{"id": "BooleanValue", "op": "AND", "args": ["Enable", "Data"]}],
        "outputs": {"Result.value_only": "BooleanValue"},
        "minimal_gate": 1,
        "proof": "one ordinary AND",
        "physical_equivalence": False,
    },
    15: {
        "name": "Full Adder seven-gate G/K/P expansion",
        "inputs": ["Cin", "A", "B"],
        "nodes": [
            {"id": "G", "op": "AND", "args": ["A", "B"]},
            {"id": "K", "op": "NOR", "args": ["A", "B"]},
            {"id": "P", "op": "NOR", "args": ["K", "G"]},
            {"id": "PC", "op": "AND", "args": ["P", "Cin"]},
            {"id": "NPC", "op": "NOR", "args": ["P", "Cin"]},
            {"id": "Sum", "op": "NOR", "args": ["NPC", "PC"]},
            {"id": "Cout", "op": "OR", "args": ["G", "PC"]},
        ],
        "outputs": {"Result": "Sum", "CarryOut": "Cout"},
        "minimal_gate": 7,
        "proof": "legacy exact certificate: gates 1..6 UNSAT, 7 gates / delay 4 SAT",
    },
}


def eval_expansion(kind: int, definition: dict[str, object]) -> dict[str, object]:
    inputs = list(definition["inputs"])
    rows = 1 << len(inputs)
    mask = (1 << rows) - 1
    values: dict[str, int] = {}
    driven: dict[str, int] = {}
    conflict: dict[str, int] = {}
    arrivals: dict[str, int] = {}
    arcs: dict[str, dict[str, int]] = {}
    for input_index, name in enumerate(inputs):
        value = 0
        for row in range(rows):
            value |= ((row >> input_index) & 1) << row
        values[name] = value
        driven[name] = mask
        conflict[name] = 0
        arrivals[name] = 0
        arcs[name] = {name: 0}

    def apply(op: str, args: list[str]) -> int:
        a = values[args[0]]
        b = values[args[1]] if len(args) > 1 else a
        if op == "NOT":
            return (~a) & mask
        if op == "AND":
            return a & b
        if op == "OR":
            return a | b
        if op == "NAND":
            return (~(a & b)) & mask
        if op == "NOR":
            return (~(a | b)) & mask
        raise ValueError(op)

    node_rows = []
    for node in definition["nodes"]:
        node_id = str(node["id"])
        args = [str(value) for value in node["args"]]
        values[node_id] = apply(str(node["op"]), args)
        driven[node_id] = mask
        conflict[node_id] = 0
        arrivals[node_id] = max(arrivals[value] for value in args) + 1
        node_arcs: dict[str, int] = {}
        for arg in args:
            for source, depth in arcs[arg].items():
                node_arcs[source] = max(node_arcs.get(source, -1), depth + 1)
        arcs[node_id] = node_arcs
        node_rows.append(
            {
                "id": node_id,
                "op": node["op"],
                "args": args,
                "incremental_gate": 1,
                "step_delay": 1,
                "arrival": arrivals[node_id],
                "input_arc_depths": node_arcs,
                "value": mask_record(values[node_id], rows),
                "driven": mask_record(driven[node_id], rows),
                "conflict": mask_record(0, rows),
                "physical_truth_sha256": physical_truth_sha(
                    values[node_id], driven[node_id], 0, rows
                ),
                "semantic_label": truth_label(inputs, values[node_id]),
                "public_output_names": [
                    output
                    for output, source in definition["outputs"].items()
                    if source == node_id
                ],
                "materialized_component_output": True,
                "native_component_internal": False,
            }
        )

    output_rows = []
    for output, node_id in definition["outputs"].items():
        output_rows.append(
            {
                "output": output,
                "node": node_id,
                "arrival": arrivals[node_id],
                "input_arc_depths": arcs[node_id],
                "value": mask_record(values[node_id], rows),
                "driven": mask_record(driven[node_id], rows),
            }
        )
    signals = {
        name: (values[name], driven[name], conflict[name])
        for name in [*inputs, *(str(node["id"]) for node in definition["nodes"])]
    }
    gate = len(definition["nodes"])
    delay = max(item["arrival"] for item in output_rows)
    native = native_truth_and_cofactors(kind)
    native_value_match = None
    if native is not None and kind != 12:
        native_by_name = {item["output"]: item for item in native["outputs"]}
        native_value_match = all(
            output in native_by_name
            and row["value"]["sha256"] == native_by_name[output]["value"]["sha256"]
            for output, row in ((item["output"], item) for item in output_rows)
        )
    return {
        "available": True,
        "name": definition["name"],
        "domain": {
            "inputs": inputs,
            "row_count": rows,
            "assignment_order": "row index bits follow inputs[] order, least-significant bit first",
        },
        "gate": gate,
        "delay": delay,
        "minimal_gate": definition["minimal_gate"],
        "minimality_evidence": definition["proof"],
        "physical_equivalence_to_native": definition.get("physical_equivalence", True),
        "native_value_outputs_match": native_value_match,
        "nodes": node_rows,
        "outputs": output_rows,
        "relations": relation_catalog(signals, rows),
        "producer_rule": (
            "each listed internal node is a real output of a separately materialized legal primitive; "
            "it is reusable only in the flat expansion, not through the native opaque component"
        ),
    }


def native_arcs(kind: int, pins: list[dict[str, object]], delay: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    input_pins = [pin for pin in pins if pin["sequence"] in {"inputs", "bidirectional"}]
    output_pins = [pin for pin in pins if pin["sequence"] == "outputs"]
    combinational: list[dict[str, object]] = []
    temporal: list[dict[str, object]] = []
    if kind in {1, 2}:
        return combinational, temporal
    if kind == 13:
        temporal.append(
            {
                "from": input_pins[0]["semantic_name"],
                "to": output_pins[0]["semantic_name"],
                "tick_offset": 1,
                "score_delay": delay,
                "equation": "Result(t+1) = data_plane(Input(t))",
            }
        )
        return combinational, temporal
    if kind in {16, 111, 112}:  # current prototype/codegen: Maker
        for pin in input_pins:
            match = re.search(r"(\d+)$", str(pin["semantic_name"]))
            lane = int(match.group(1)) if match else pin["sequence_index"]
            combinational.append(
                {
                    "from": pin["semantic_name"],
                    "to": f"{output_pins[0]['semantic_name']}[{lane}]",
                    "delay": 0,
                    "arc_kind": "same-lane bundle",
                }
            )
        return combinational, temporal
    if kind in {17, 109, 110}:  # current prototype/codegen: Splitter
        for pin in output_pins:
            match = re.search(r"(\d+)$", str(pin["semantic_name"]))
            lane = int(match.group(1)) if match else pin["sequence_index"]
            combinational.append(
                {
                    "from": f"{input_pins[0]['semantic_name']}[{lane}]",
                    "to": pin["semantic_name"],
                    "delay": 0,
                    "arc_kind": "same-lane unbundle",
                }
            )
        return combinational, temporal
    if kind == 18:
        combinational.append(
            {
                "from": "Input[i]",
                "to": "Result[i]",
                "delay": delay,
                "for_each_lane": True,
            }
        )
        return combinational, temporal
    if kind == 21:
        combinational.extend(
            {
                "from": f"{name}[i]",
                "to": "Result[i]",
                "delay": delay,
                "for_each_lane": True,
            }
            for name in ("Input 0", "Input 1")
        )
        return combinational, temporal
    if kind == 25:
        combinational.extend(
            [
                {
                    "from": "Enable",
                    "to": "Output.value_and_driven_whole_word",
                    "delay": delay,
                },
                {
                    "from": "Value[i]",
                    "to": "Output[i]",
                    "delay": delay,
                    "for_each_lane": True,
                },
            ]
        )
        return combinational, temporal
    for source in input_pins:
        for target in output_pins:
            combinational.append(
                {
                    "from": source["semantic_name"],
                    "to": target["semantic_name"],
                    "delay": delay,
                    "arc_kind": "native opaque score arc",
                }
            )
    return combinational, temporal


def z_semantics(kind: int) -> dict[str, object]:
    if kind == 12:
        return {
            "value_equation": "value = Enable & data_plane(Input)",
            "driven_equation": "driven = Enable",
            "z_equation": "is_z = !Enable",
            "enable_0": {"value": 0, "driven": False, "is_z": True},
            "enable_1": {"value": "data_plane(Input)", "driven": True, "is_z": False},
            "input_z_when_enabled": "input() uses preserve_z=0, so the data plane is 0 and the output is active 0",
        }
    if kind == 25:
        return {
            "value_equation": "value[i] = Enable & data_plane(Value[i])",
            "driven_equation": "one whole-word driven flag = Enable",
            "z_granularity": "whole word, never a per-lane Z mask",
            "enable_0": {"value": 0, "driven": False, "is_z": True},
            "enable_1": {"value": "data_plane(Value)", "driven": True, "is_z": False},
            "input_z_when_enabled": "word input uses preserve_z=0, so it becomes an active all-zero word",
        }
    if kind == 13:
        return {
            "input_read": "preserve_z=0",
            "stored_state": "data plane only",
            "output": "always ordinary active output, never tristate",
            "z_input_effect": "Input(t)=Z stores 0; Result(t+1) is active 0",
        }
    if kind in {16, 17, 109, 110, 111, 112}:
        return {
            "input_read": "preserve_z=0",
            "output": "ordinary active output(s)",
            "normalization": "bundle/unbundle propagates the data plane only and restores active drive",
        }
    return {
        "input_read": "all native input() calls use preserve_z=0",
        "ordinary_gate_z_value": 0,
        "output": "ordinary active driven output",
        "conflict": "a conflicting resolved network is a simulator short-circuit/halt, not a Boolean value",
    }


def word_sharing(kind: int) -> dict[str, object]:
    if kind in {18, 21}:
        return {
            "lane_independence": True,
            "cross_lane_logic": False,
            "gate_formula": "w",
            "delay_formula": "1",
            "width_discount": False,
            "byte_adder_width": 8,
        }
    if kind == 25:
        return {
            "lane_independence_of_data": True,
            "shared_enable_across_all_lanes": True,
            "shared_whole_word_driven_state": True,
            "per_lane_z_mask": False,
            "gate_formula": "2*w",
            "delay_formula": "1",
            "width_discount": False,
            "byte_adder_width": 8,
        }
    if kind in {16, 17, 109, 110, 111, 112}:
        return {
            "lane_mapping": "one-to-one by lane index",
            "cross_lane_logic": False,
            "gate": 0,
            "delay": 0,
            "z_normalization": True,
        }
    return {"applicable": False}


def adapter_exact_constraints(
    kind: int,
    pins: list[dict[str, object]],
    codegen: dict[str, object],
) -> dict[str, object] | None:
    if kind not in {16, 17, 109, 110, 111, 112}:
        return None
    is_maker = kind in {16, 111, 112}
    input_pins = [pin for pin in pins if pin["sequence"] == "inputs"]
    output_pins = [pin for pin in pins if pin["sequence"] == "outputs"]
    if is_maker:
        width = int(output_pins[0]["word_size"])
        lane_equations = [
            {
                "lane": lane,
                "value": f"data_plane({input_pins[lane]['semantic_name']})",
                "driven_on_valid_rows": True,
                "z_input_value": 0,
                "step_delay": 0,
                "structural_arc": f"{input_pins[lane]['semantic_name']} -> {output_pins[0]['semantic_name']}[{lane}]",
            }
            for lane in range(width)
        ]
        equation = "Result = OR_i((data_plane(Bit_i) & 1) << i)"
        conflict_equation = "conflict(Result) = OR_i(conflict(Bit_i)); conflicting rows are invalid/halt and must not be normalized to 0"
        arrival = {
            "per_lane": "arrival(Result[i]) = arrival(Bit_i)",
            "public_word_ready": "arrival(Result word pin) = max_i arrival(Bit_i)",
        }
        z_case = "each undriven bit input contributes data 0; the packed word output remains active driven"
        output_owner_count = 1
    else:
        width = len(output_pins)
        lane_equations = [
            {
                "lane": lane,
                "value": f"(data_plane({input_pins[0]['semantic_name']}) >> {lane}) & 1",
                "driven_on_valid_rows": True,
                "z_input_value": 0,
                "step_delay": 0,
                "structural_arc": f"{input_pins[0]['semantic_name']}[{lane}] -> {output_pins[lane]['semantic_name']}",
            }
            for lane in range(width)
        ]
        equation = "Bit_i = (data_plane(Input) >> i) & 1"
        conflict_equation = "for every output i: conflict(Bit_i) = conflict(Input); conflicting rows are invalid/halt and must not be normalized to 0"
        arrival = {
            "per_lane": "arrival(Bit_i) = arrival(Input)",
            "all_public_outputs": "all lane outputs share the same zero-delay input arrival",
        }
        z_case = "an undriven input word has data plane 0; every bit output becomes active driven 0"
        output_owner_count = width
    return {
        "kind": kind,
        "runtime_role": "Maker" if is_maker else "Splitter",
        "width": width,
        "pack_or_extract_equation": equation,
        "lane_equations": lane_equations,
        "arrival_constraints": arrival,
        "input_read": {
            "preserve_z": False,
            "all_codegen_input_calls_prove_preserve_z_zero": all(
                site["preserve_z_zero"] for site in codegen["input_call_sites"]
            ),
            "call_sites": codegen["input_call_sites"],
        },
        "valid_row_output": {
            "driven": True,
            "is_z": False,
            "z_normalization": z_case,
        },
        "conflict_constraint": conflict_equation,
        "conflict_interpretation": (
            "preserve_z=0 changes only the undriven data plane. It does not legalize a BUS short-circuit; exact models must propagate/forbid the conflict predicate."
        ),
        "physical_owner_barrier": {
            "barrier": True,
            "source_resolved_network_owner_preserved": False,
            "new_ordinary_active_output_driver_count": output_owner_count,
            "cost": 0,
            "constraint": (
                "the adapter may create new active output network owner(s), but cannot copy an undriven/tristate partial driver or its resolved BUS owner for free"
            ),
        },
        "searcher_constraint": {
            "value": equation,
            "driven_valid_rows": 1,
            "conflict": conflict_equation,
            "gate": 0,
            "step_delay": 0,
            "do_not_model_as": [
                "identity on physical (value,driven,conflict) truth",
                "free duplication of a partial BUS driver owner",
                "per-lane preservation of Z",
            ],
        },
        "evidence": {
            "prototype_pin_record": PROTOTYPE_PATH.name,
            "codegen_case_record": CODEGEN_CASE_PATH.name,
            "case_target": codegen["case_target"],
            "case_code_sha256": codegen["code_bytes_sha256"],
            "template_fragments": codegen["template_fragments"],
        },
    }


def dominance(kind: int, effective: tuple[int, int]) -> dict[str, object]:
    rows = {
        5: (2, 2, "two ordinary AND gates; exposes selected pair conjunction"),
        8: (2, 2, "two ordinary OR gates; exposes selected pair disjunction"),
        10: (3, 2, "G/K/P expansion; score-equal now and exposes G,K"),
        11: (3, 2, "G/K/Q expansion; strictly dominates 5/4"),
        12: (1, 1, "ordinary AND only for Boolean value; does not preserve Z/driven"),
        15: (7, 4, "seven ordinary gates; exposes G,K,P,PC,NPC and short Cin arcs"),
    }
    if kind not in rows:
        if kind in {18, 21}:
            return {
                "classification": "score-neutral lane expansion",
                "expanded": {"gate_formula": "w", "delay": 1},
                "note": "free Maker/Splitter adapters expose lane ownership but no score discount",
            }
        if kind == 25:
            return {
                "classification": "score-neutral physical lane expansion",
                "expanded": {"gate_formula": "2*w", "delay": 1},
                "note": "all lanes must still share the one enable/driven domain to match the word Switch",
            }
        return {"classification": "not dominated by a smaller required catalog expansion"}
    gate, delay, note = rows[kind]
    physical = kind != 12
    strictly = gate < effective[0] or delay < effective[1]
    return {
        "classification": (
            "strictly dominated" if strictly and physical else "Boolean-projection dominated only"
            if kind == 12
            else "score-equal but byproduct-superior"
        ),
        "native_effective": {"gate": effective[0], "delay": effective[1]},
        "expanded": {"gate": gate, "delay": delay},
        "physical_equivalence": physical,
        "note": note,
    }


def build_component(
    kind: int,
    prototype: dict[str, object],
    default_cost: tuple[int, int],
    availability: dict[str, object],
    case: dict[str, object],
) -> dict[str, object]:
    pins = flatten_pins(prototype)
    frontier = IMPORTED_FRONTIERS.get(kind, [])
    effective = (frontier[0][0], frontier[0][1]) if frontier else default_cost
    combinational_arcs, temporal_arcs = native_arcs(kind, pins, effective[1])
    for arc in combinational_arcs:
        arc["effective_delay"] = arc["delay"]
        arc["current_exe_default_delay"] = (
            0 if int(arc["delay"]) == 0 else default_cost[1]
        )
    for arc in temporal_arcs:
        arc["effective_score_delay"] = arc["score_delay"]
        arc["current_exe_default_score_delay"] = default_cost[1]
    outputs = [pin for pin in pins if pin["sequence"] == "outputs"]
    inputs = [pin for pin in pins if pin["sequence"] in {"inputs", "bidirectional"}]
    codegen = codegen_summary(case)
    adapter_constraints = adapter_exact_constraints(kind, pins, codegen)
    native_internal = []
    if kind == 15:
        native_internal.append(
            {
                "name": "sum",
                "kind": "ephemeral generated-code local",
                "equation": "U2(Input0) + U2(Input1) + U2(CarryIn)",
                "used_for": ["Result = sum & 1", "Carry out = sum >> 1"],
                "pin_accessible": False,
                "stateful": False,
                "importable_as_producer": False,
            }
        )
    if kind in {17, 109, 110}:
        native_internal.append(
            {
                "name": "input_<component-id>",
                "kind": "ephemeral generated-code local",
                "equation": "data_plane(Input)",
                "used_for": "lane extraction",
                "pin_accessible": False,
                "stateful": False,
                "importable_as_producer": False,
            }
        )
    if kind == 13:
        native_internal.append(
            {
                "name": "component state slot",
                "kind": "one-bit sequential state",
                "equation": "Q(t+1)=data_plane(Input(t))",
                "reset": 0,
                "pin_accessible": False,
                "stateful": True,
                "importable_as_same_tick_producer": False,
                "observable_only_via": "Result on the following tick",
            }
        )

    expansion = eval_expansion(kind, EXPANSIONS[kind]) if kind in EXPANSIONS else {"available": False}
    confidence = {
        "pins_and_public_outputs": "current_2.1.292_exe_static",
        "default_cost": "current_2.1.292_exe_static",
        "effective_imported_frontier": "legacy_generated_certificate_plus_current_import_semantics",
        "native_boolean_semantics": "current_2.1.292_codegen_static",
        "flat_expansion": "derived_and_exhaustively_truth_checked",
        "live_server_acceptance_of_new_scores": "not_proven",
    }
    return {
        "kind": kind,
        "symbol_name": SYMBOL_NAMES[kind],
        "prototype_display_name": prototype["name"],
        "semantic_role": SEMANTIC_ROLES[kind],
        "kind16_17_symbol_role_mismatch": kind in {16, 17},
        "availability": {
            "allowed_before_byte_adder": True,
            "unlocked_by": availability.get("unlocked_by", []),
            "source": "legacy pre-target closure certificate, current campaign meta hashes revalidated",
        },
        "cost": {
            "current_exe_default": {"gate": default_cost[0], "delay": default_cost[1]},
            "effective_imported_frontier": [
                {"gate": gate, "delay": delay, "count": count}
                for gate, delay, count in frontier
            ],
            "effective_now": {"gate": effective[0], "delay": effective[1]},
            "effective_source": (
                "non-empty legacy saved/imported frontier; current EXE get_cost proves it replaces defaults"
                if frontier
                else "current EXE default because no imported frontier is evidenced"
            ),
            "scope": "U8 instance at Byte Adder for generic word kinds" if kind in {18, 21, 25} else "component instance",
        },
        "prototype": {
            "slot": prototype["slot"],
            "record_va": prototype["record_va"],
            "current_exe_static": True,
        },
        "pins": pins,
        "native_public_inputs": [pin["semantic_name"] for pin in inputs],
        "native_public_outputs": [pin["semantic_name"] for pin in outputs],
        "native_public_output_count": len(outputs),
        "native_output_owner_rule": (
            "all public outputs belong to one paid component instance; a multi-output component cost cannot be split per output"
        ),
        "native_internal_access": False,
        "native_internal_codegen_artifacts": native_internal,
        "native_hidden_wireable_outputs_found": False,
        "native_combinational_arcs": combinational_arcs,
        "native_temporal_arcs": temporal_arcs,
        "native_truth_and_complete_active_constant_cofactors": native_truth_and_cofactors(kind),
        "value_driven_z": z_semantics(kind),
        "bus_owner_rules": {
            "may_drive_resolved_bus": kind in {12, 25},
            "tristate_output": kind in {12, 25},
            "rule": (
                "a Switch output is one partial driver; after connection it belongs to the complete resolved network owner"
                if kind in {12, 25}
                else "ordinary output is an active driver"
            ),
        },
        "word_sharing": word_sharing(kind),
        "maker_splitter_exact_constraints": adapter_constraints,
        "codegen_case": codegen,
        "flat_expansion": expansion,
        "dominance": dominance(kind, effective),
        "evidence": [
            {"class": "current_exe_static", "artifact": PROTOTYPE_PATH.name},
            {"class": "current_exe_static", "artifact": RUNTIME_PATH.name},
            {"class": "current_exe_static", "artifact": CODEGEN_CASE_PATH.name},
            {"class": "legacy_generated_certificate", "artifact": str(AVAILABILITY_PATH.relative_to(ROOT)).replace("\\", "/")},
        ],
        "confidence": confidence,
    }


def build_dag_audit(payload: dict[str, object]) -> dict[str, object]:
    inputs = tuple([item for bit in range(8) for item in (f"a{bit}", f"b{bit}")] + ["cin"])
    domain = truth.make_domain("byte-adder-u8-u8-cin-complete", inputs)
    truth.OWNER_COSTS.clear()
    replay = truth.replay_dag(domain, payload["factory_dag"])
    dag = payload["factory_dag"]
    nodes = {int(node["id"]): node for node in dag["nodes"]}
    output_names = [f"S{bit}" for bit in range(8)] + ["C8"]
    outputs = [int(node_id) for node_id in dag["outputs"]]
    output_map = dict(zip(outputs, output_names, strict=True))

    consumer_nodes: dict[int, set[int]] = defaultdict(set)
    consumer_refs: Counter[int] = Counter()
    for node_id, node in nodes.items():
        for reference in truth.node_references(node):
            consumer_nodes[reference].add(node_id)
            consumer_refs[reference] += 1

    reachable_outputs: dict[int, set[str]] = defaultdict(set)
    for output_id, output_name in output_map.items():
        stack = [output_id]
        seen = set()
        while stack:
            node_id = stack.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            reachable_outputs[node_id].add(output_name)
            stack.extend(truth.node_references(nodes[node_id]))

    semantic_labels = truth.arithmetic_labels(domain)
    node_records = []
    for node_id in sorted(replay["reachable"]):
        node = nodes[node_id]
        signal = replay["signals"][node_id]
        node_records.append(
            {
                "id": node_id,
                "op": node["op"],
                "args": truth.node_references(node),
                "cost": int(node["cost"]),
                "step_delay": int(node["step_delay"]),
                "arrival": signal.arrival,
                "may_z_static": bool(node["may_z"]),
                "actual_may_z": signal.driven != domain.mask,
                "semantic_labels": sorted(semantic_labels.get(signal.value, set())),
                "value_truth": mask_record(signal.value, domain.row_count),
                "driven_truth": mask_record(signal.driven, domain.row_count),
                "conflict_truth": mask_record(signal.conflict, domain.row_count),
                "physical_truth_sha256": physical_truth_sha(
                    signal.value, signal.driven, signal.conflict, domain.row_count
                ),
                "consumer_node_count": len(consumer_nodes[node_id]),
                "consumer_reference_count": consumer_refs[node_id],
                "consumer_nodes": sorted(consumer_nodes[node_id]),
                "reachable_public_outputs": sorted(reachable_outputs[node_id]),
                "longest_structural_arc_from_primary_inputs": dict(signal.arcs),
                "public_output": node_id in output_map,
                "public_output_name": output_map.get(node_id),
                "internal_byproduct": node["op"] != "INPUT" and node_id not in output_map,
                "resolved_network_owner": node.get("resolved_network"),
            }
        )

    bus_records = []
    bus_owner_ok = True
    for node_id in sorted(replay["reachable"]):
        node = nodes[node_id]
        if node["op"] != "BUS":
            continue
        signal = replay["signals"][node_id]
        owner = str(node["resolved_network"])
        drivers = []
        for index, driver in enumerate(node["drivers"]):
            driver_signal = replay["driver_signals"][(node_id, index)]
            owner_match = str(driver["owner"]) == owner
            bus_owner_ok &= owner_match
            drivers.append(
                {
                    "driver_index": index,
                    "enable_node": int(driver["enable"]),
                    "data_node": int(driver["data"]),
                    "owner": driver["owner"],
                    "owner_matches_resolved_network": owner_match,
                    "incremental_switch_gate": 2,
                    "value_truth": mask_record(driver_signal.value, domain.row_count),
                    "driven_truth": mask_record(driver_signal.driven, domain.row_count),
                    "conflict_truth": mask_record(driver_signal.conflict, domain.row_count),
                    "z_assignment_count": domain.row_count - driver_signal.driven.bit_count(),
                    "physical_truth_sha256": physical_truth_sha(
                        driver_signal.value,
                        driver_signal.driven,
                        driver_signal.conflict,
                        domain.row_count,
                    ),
                }
            )
        bus_records.append(
            {
                "node_id": node_id,
                "resolved_network_owner": owner,
                "driver_count": len(drivers),
                "complete_driver_set": drivers,
                "owner_gate": int(node["cost"]),
                "owner_delay": int(node["step_delay"]),
                "resolved_value_truth": mask_record(signal.value, domain.row_count),
                "resolved_driven_truth": mask_record(signal.driven, domain.row_count),
                "resolved_conflict_truth": mask_record(signal.conflict, domain.row_count),
                "z_assignment_count": domain.row_count - signal.driven.bit_count(),
                "conflict_assignment_count": signal.conflict.bit_count(),
                "all_drivers_share_owner": all(
                    driver["owner_matches_resolved_network"] for driver in drivers
                ),
                "indivisible_owner_rule": (
                    "the complete driver set belongs to this one resolved network; individual partial drivers are not free independent BUS owners"
                ),
            }
        )

    relation_signals = {
        str(node_id): (
            replay["signals"][node_id].value,
            replay["signals"][node_id].driven,
            replay["signals"][node_id].conflict,
        )
        for node_id in sorted(replay["reachable"])
    }
    relations = relation_catalog(relation_signals, domain.row_count)
    op_counts = Counter(nodes[node_id]["op"] for node_id in replay["reachable"])
    return {
        "source": str(DAG_PATH.relative_to(ROOT)).replace("\\", "/"),
        "source_file_sha256": file_sha256(DAG_PATH),
        "source_factory_dag_sha256": dag["sha256"],
        "source_structural_sha256": payload["metrics"]["structural_sha256"],
        "truth_domain": {
            "inputs": list(inputs),
            "row_count": domain.row_count,
            "complete_u8_u8_u1": True,
            "assignment_order": "row index bits follow inputs[] order, least-significant bit first",
        },
        "metrics": {
            "gate": replay["gate"],
            "delay": replay["delay"],
            "energy": replay["gate"] * replay["delay"],
            "live_node_count": len(replay["reachable"]),
            "op_counts": dict(sorted(op_counts.items())),
            "output_ids": outputs,
            "output_names": output_names,
            "mismatch_count_by_output": replay["mismatch_count_by_output"],
            "mismatch_union_count": replay["mismatch_union_count"],
            "conflict_assignment_count": replay["conflict_assignment_count"],
            "z_assignment_count_by_output": replay["z_assignment_count_by_output"],
            "replay_structural_sha256": replay["structural_sha256"],
        },
        "nodes": node_records,
        "bus_nodes": bus_records,
        "bus_owner_consistency": bus_owner_ok,
        "global_relations": relations,
        "producer_import_rule": (
            "ordinary/BUS node records are legal reusable producers only with their listed physical owner and complete dependencies; "
            "a BUS partial driver cannot be detached from its resolved_network owner for zero cost"
        ),
    }


def build_runtime_evidence(
    runtime: dict[str, object],
    prototypes: dict[str, object],
    cost_import: dict[str, object],
) -> dict[str, object]:
    manifest = STEAM_MANIFEST_PATH.read_text(encoding="utf-8", errors="replace")
    match = re.search(r'"buildid"\s+"(\d+)"', manifest)
    build_id = match.group(1) if match else None
    campaign = {}
    for relative in CAMPAIGN_FILES:
        path = CAMPAIGN_PATH / relative
        campaign[relative] = {
            "path": str(path),
            "size": path.stat().st_size,
            "sha256": file_sha256(path),
        }
    return {
        "version": CURRENT_VERSION,
        "steam_buildid": build_id,
        "exe": {
            "path": str(EXE_PATH),
            "size": EXE_PATH.stat().st_size,
            "sha256": file_sha256(EXE_PATH),
        },
        "steam_manifest": {
            "path": str(STEAM_MANIFEST_PATH),
            "sha256": file_sha256(STEAM_MANIFEST_PATH),
            "buildid_only_extracted": True,
        },
        "prototype_export": {
            "path": str(PROTOTYPE_PATH),
            "sha256": file_sha256(PROTOTYPE_PATH),
            "record_count": len(prototypes["records"]),
            "slot_table_address": prototypes["prototype_slot_table_address"],
            "slot_table_delta": prototypes["prototype_slot_table_delta"],
        },
        "runtime_score_export": {
            "path": str(RUNTIME_PATH),
            "sha256": file_sha256(RUNTIME_PATH),
            "input_sha256": runtime["input_sha256"],
        },
        "cost_import_export": {
            "path": str(COST_IMPORT_PATH),
            "sha256": file_sha256(COST_IMPORT_PATH),
            "input_sha256": cost_import["input_sha256"],
            "functions": FUNCTION_EVIDENCE,
        },
        "codegen_case_export": {
            "path": str(CODEGEN_CASE_PATH),
            "sha256": file_sha256(CODEGEN_CASE_PATH),
        },
        "current_campaign_assets": campaign,
    }


def build_cost_policy() -> dict[str, object]:
    return {
        "default_vs_imported": (
            "get_cost uses DEFAULT_COMPONENT_SCORES only when component_costs[kind] is empty; "
            "a non-empty saved/server frontier replaces, rather than merges with, the default"
        ),
        "frontier_invariant": "gate strictly increases while delay strictly decreases; dominated points are rejected or removed",
        "selector_modes": {
            "0": "first frontier point: minimum gate",
            "1": "last frontier point: minimum delay",
            "2": "first point satisfying gate/delay ceilings; fallback to first point",
        },
        "local_completion": (
            "complete_level invokes add_cost for each unlocks_components entry before saving; a validated 7/4 Full Adder would replace legacy 16/8 locally"
        ),
        "server_import": (
            "process_network_responses clears the client frontier and rebuilds it with import_costs; client capability does not prove server acceptance"
        ),
        "server_acceptance_of_7_4": "requires captured live response; not proven by static evidence",
        "function_evidence": FUNCTION_EVIDENCE,
    }


def build_delay_evidence() -> dict[str, object]:
    return {
        "kind": 13,
        "case_entry": "0x000000014044c671",
        "case_end_before_kind14": "0x000000014044cdce",
        "two_phase_codegen": {
            "read_phase": "load_and_output(output pin 0, width 1, component state slot)",
            "write_phase": "input(pin 0, width 1, preserve_z=0) then store_bit(component state slot)",
        },
        "state_equations": ["Q(0)=0", "Result(t)=Q(t)", "Q(t+1)=data_plane(Input(t))"],
        "observable_equation": "Result(0)=0; Result(t)=Input(t-1) for t>=1 on active Boolean inputs",
        "first_cycle": "active driven 0",
        "z_rule": "Z is not stored; its data plane 0 becomes active 0 on the next tick",
        "chainable": True,
        "feedback_allowed": True,
        "same_tick_byte_adder_candidate": False,
        "current_campaign_cross_checks": {
            "double_buffer_meta_sha256": file_sha256(CAMPAIGN_PATH / "double_buffer/meta.txt"),
            "double_buffer_test_sha256": file_sha256(CAMPAIGN_PATH / "double_buffer/test.si"),
            "odd_ticks_meta_sha256": file_sha256(CAMPAIGN_PATH / "odd_ticks/meta.txt"),
            "odd_ticks_test_sha256": file_sha256(CAMPAIGN_PATH / "odd_ticks/test.si"),
        },
        "evidence": [
            DELAY_DISASM_PATH.name,
            CODEGEN_SWITCH_PATH.name,
            CODEGEN_CORE_PATH.name,
            "current campaign double_buffer/odd_ticks metadata and tests",
        ],
        "excluded_decoy_probe": (
            "delay-codegen-xrefs-2.1.292.json targets a RAM .cycle+2 pipeline and is not used as Delay Line semantic evidence"
        ),
    }


def build_searcher_contract(components: list[dict[str, object]]) -> dict[str, object]:
    native_groups = []
    flat_groups = []
    for component_index, component in enumerate(components):
        outputs = []
        for output in component["native_public_outputs"]:
            outputs.append(
                {
                    "name": output,
                    "physical_output_kind": (
                        "tristate_partial_driver"
                        if component["kind"] in {12, 25}
                        else "ordinary_active_driver"
                    ),
                    "combinational_arcs": [
                        arc
                        for arc in component["native_combinational_arcs"]
                        if str(arc["to"]).startswith(str(output))
                        or component["native_public_output_count"] == 1
                    ],
                    "temporal_arcs": [
                        arc
                        for arc in component["native_temporal_arcs"]
                        if str(arc["to"]).startswith(str(output))
                    ],
                }
            )
        native_groups.append(
            {
                "kind": component["kind"],
                "symbol_name": component["symbol_name"],
                "runtime_semantic_role": component["semantic_role"],
                "owner_template": f"native_kind_{component['kind']}_instance_<id>",
                "pay_cost_once_for_owner": True,
                "current_exe_default": component["cost"]["current_exe_default"],
                "effective_now": component["cost"]["effective_now"],
                "inputs": component["native_public_inputs"],
                "outputs": outputs,
                "hidden_wireable_outputs": [],
                "native_internal_import_forbidden": True,
                "temporal_only": component["kind"] == 13,
                "same_tick_combinational_allowed": component["kind"] != 13,
                "value_driven_z_constraint_pointer": f"/components/{component_index}/value_driven_z",
                "complete_cofactor_producer_pointer": f"/components/{component_index}/native_truth_and_complete_active_constant_cofactors",
                "adapter_constraint_pointer": (
                    f"/components/{component_index}/maker_splitter_exact_constraints"
                    if component["maker_splitter_exact_constraints"] is not None
                    else None
                ),
            }
        )
        expansion = component["flat_expansion"]
        if not expansion.get("available"):
            continue
        flat_groups.append(
            {
                "replaces_native_kind": component["kind"],
                "name": expansion["name"],
                "total_gate": expansion["gate"],
                "total_delay": expansion["delay"],
                "physical_equivalence_to_native": expansion["physical_equivalence_to_native"],
                "node_owners": [
                    {
                        "node": node["id"],
                        "owner_template": f"flat_kind_{component['kind']}_{node['id']}_instance_<id>",
                        "op": node["op"],
                        "args": node["args"],
                        "incremental_gate": node["incremental_gate"],
                        "step_delay": node["step_delay"],
                        "arrival": node["arrival"],
                        "input_arc_depths": node["input_arc_depths"],
                        "public_output_names": node["public_output_names"],
                        "reusable_internal_byproduct": not bool(node["public_output_names"]),
                        "physical_output_kind": "ordinary_active_driver",
                    }
                    for node in expansion["nodes"]
                ],
                "relations_pointer": f"/components/{component_index}/flat_expansion/relations",
            }
        )
    return {
        "schema": "tc-byte-adder-searcher-producer-contract-v1",
        "native_owner_groups": native_groups,
        "flat_expansion_owner_groups": flat_groups,
        "global_constraints": [
            "pay each native or flat component owner once; all listed outputs then exist simultaneously",
            "do not import native_internal_codegen_artifacts as wireable producers",
            "ordinary gates and Maker/Splitter read Z data as 0 and produce active outputs",
            "Switch outputs are partial drivers and require complete resolved BUS ownership",
            "BUS partial drivers cannot be detached from their resolved_network owner",
            "conflict rows are invalid/halt and cannot be normalized to Boolean 0",
            "Delay Line is temporal-only and forbidden in same-tick Byte Adder combinational cones",
            "use effective_now for the legacy saved/imported profile; retain current_exe_default as a separate counterfactual profile",
        ],
    }


def build() -> dict[str, object]:
    prototypes = load_json(PROTOTYPE_PATH)
    runtime = load_json(RUNTIME_PATH)
    cost_import = load_json(COST_IMPORT_PATH)
    codegen_cases = load_json(CODEGEN_CASE_PATH)
    availability = load_json(AVAILABILITY_PATH)
    dag_payload = load_json(DAG_PATH)
    full_adder_audit = load_json(FULL_ADDER_AUDIT_PATH)

    runtime_rows = {
        int(item["kind"]): (int(item["default_gate"]), int(item["default_delay"]))
        for item in runtime["score_table"]["rows"]
    }
    availability_rows = {
        int(item["kind"]): item for item in availability["globally_unlocked_native_primitives"]
    }
    case_rows = {int(item["kind"]): item for item in codegen_cases["cases"]}
    prototype_rows = {int(kind): row for kind, row in prototypes["records"].items()}

    components = [
        build_component(
            kind,
            prototype_rows[kind],
            runtime_rows[kind],
            availability_rows[kind],
            case_rows[kind],
        )
        for kind in SELECTED_KINDS
    ]
    searcher_contract = build_searcher_contract(components)
    dag_audit = build_dag_audit(dag_payload)
    runtime_evidence = build_runtime_evidence(runtime, prototypes, cost_import)

    expected_defaults = {
        1: (0, 0),
        2: (0, 0),
        3: (1, 1),
        4: (1, 1),
        5: (2, 2),
        6: (1, 1),
        7: (1, 1),
        8: (2, 2),
        9: (1, 1),
        10: (4, 3),
        11: (4, 3),
        12: (2, 1),
        13: (5, 4),
        15: (8, 4),
        16: (0, 0),
        17: (0, 0),
        18: (8, 1),
        21: (8, 1),
        25: (16, 1),
        109: (0, 0),
        110: (0, 0),
        111: (0, 0),
        112: (0, 0),
    }
    output_counts_match = True
    for component in components:
        kind = component["kind"]
        prototype_count = component["native_public_output_count"]
        references = component["codegen_case"]["symbol_reference_counts"]
        if kind == 13:
            output_counts_match &= prototype_count == 1
        else:
            output_counts_match &= references.get(
                "store_output__modelZsimulationZcode95gen_u2219", 0
            ) == prototype_count

    adapter_components = [
        component
        for component in components
        if component["maker_splitter_exact_constraints"] is not None
    ]

    fa_expansion = next(item for item in components if item["kind"] == 15)["flat_expansion"]
    fa_outputs = {item["output"]: item for item in fa_expansion["outputs"]}
    self_checks = {
        "exe_sha256": runtime_evidence["exe"]["sha256"] == CURRENT_EXE_SHA256,
        "exe_size": runtime_evidence["exe"]["size"] == CURRENT_EXE_SIZE,
        "steam_buildid": runtime_evidence["steam_buildid"] == CURRENT_BUILD_ID,
        "prototype_input_sha": prototypes["input_sha256"] == CURRENT_EXE_SHA256,
        "runtime_input_sha": runtime["input_sha256"] == CURRENT_EXE_SHA256,
        "cost_import_input_sha": cost_import["input_sha256"] == CURRENT_EXE_SHA256,
        "selected_kind_count_23": len(SELECTED_KINDS) == 23,
        "prototype_kind_set": set(prototype_rows) == set(SELECTED_KINDS),
        "codegen_case_kind_set": set(case_rows) == set(SELECTED_KINDS),
        "availability_kind_set": set(availability_rows) == set(SELECTED_KINDS),
        "runtime_default_table": all(runtime_rows[kind] == value for kind, value in expected_defaults.items()),
        "prototype_codegen_public_output_counts": output_counts_match,
        "maker_splitter_kind_count_6": len(adapter_components) == 6,
        "maker_splitter_all_preserve_z_zero": all(
            component["maker_splitter_exact_constraints"]["input_read"][
                "all_codegen_input_calls_prove_preserve_z_zero"
            ]
            for component in adapter_components
        ),
        "maker_splitter_all_owner_barriers": all(
            component["maker_splitter_exact_constraints"]["physical_owner_barrier"][
                "barrier"
            ]
            for component in adapter_components
        ),
        "maker_splitter_all_zero_delay": all(
            all(
                lane["step_delay"] == 0
                for lane in component["maker_splitter_exact_constraints"]["lane_equations"]
            )
            for component in adapter_components
        ),
        "searcher_native_owner_group_count_23": len(searcher_contract["native_owner_groups"])
        == 23,
        "all_native_internal_access_false": all(not item["native_internal_access"] for item in components),
        "all_hidden_wireable_outputs_false": all(not item["native_hidden_wireable_outputs_found"] for item in components),
        "flat_expansion_value_checks": all(
            item["flat_expansion"].get("native_value_outputs_match") is not False
            for item in components
        ),
        "full_adder_expansion_7_4": fa_expansion["gate"] == 7 and fa_expansion["delay"] == 4,
        "full_adder_short_arcs": fa_outputs["Result"]["input_arc_depths"] == {"A": 4, "B": 4, "Cin": 2}
        and fa_outputs["CarryOut"]["input_arc_depths"] == {"A": 4, "B": 4, "Cin": 2},
        "legacy_full_adder_exact_7_gate_sat": full_adder_audit["exact_full_adder_bounds"]["gate_7_delay_4"]["status"] == "sat",
        "legacy_full_adder_gate_6_unsat": full_adder_audit["exact_full_adder_bounds"]["gate_6_any_delay"]["status"] == "unsat",
        "dag_source_factory_sha": dag_payload["factory_dag"]["sha256"]
        == "25760da9cc0a859a7bd0bec82c6fc97c184093a80aa2f2869a004a01c823f575",
        "dag_gate_80": dag_audit["metrics"]["gate"] == 80,
        "dag_delay_7": dag_audit["metrics"]["delay"] == 7,
        "dag_rows_131072": dag_audit["truth_domain"]["row_count"] == 131072,
        "dag_live_nodes_82": dag_audit["metrics"]["live_node_count"] == 82,
        "dag_truth": dag_audit["metrics"]["mismatch_union_count"] == 0,
        "dag_conflict_free": dag_audit["metrics"]["conflict_assignment_count"] == 0,
        "dag_public_outputs_driven": not any(dag_audit["metrics"]["z_assignment_count_by_output"]),
        "dag_bus_count_5": len(dag_audit["bus_nodes"]) == 5,
        "dag_bus_owner_consistency": dag_audit["bus_owner_consistency"],
        "dag_bus_conflict_free": all(item["conflict_assignment_count"] == 0 for item in dag_audit["bus_nodes"]),
    }
    failed = sorted(key for key, value in self_checks.items() if not value)
    if failed:
        raise RuntimeError(f"self-check failed: {failed}")

    evidence_artifacts = {}
    for path, evidence_class in (
        (PROTOTYPE_PATH, "current_exe_static"),
        (RUNTIME_PATH, "current_exe_static"),
        (COST_IMPORT_PATH, "current_exe_static"),
        (CODEGEN_CASE_PATH, "current_exe_static"),
        (CODEGEN_SWITCH_PATH, "current_exe_static"),
        (CODEGEN_CORE_PATH, "current_exe_static"),
        (DELAY_DISASM_PATH, "current_exe_static"),
        (AVAILABILITY_PATH, "legacy_generated_certificate"),
        (FULL_ADDER_AUDIT_PATH, "legacy_generated_certificate"),
        (DAG_PATH, "repository_offline_model"),
    ):
        key = str(path.relative_to(ROOT)).replace("\\", "/")
        evidence_artifacts[key] = {"class": evidence_class, "sha256": file_sha256(path)}

    findings = [
        {
            "id": "no-native-hidden-wireable-byproducts",
            "outcome": (
                "all 23 current prototypes expose exactly the codegen public outputs; no extra internal value is wireable through a hidden pin"
            ),
            "important_exceptions": (
                "Full Adder has an inaccessible ephemeral U2 sum; Delay Line has an inaccessible persistent state slot; Splitters have inaccessible input locals"
            ),
        },
        {
            "id": "flat-expansions-create-real-producers",
            "outcome": (
                "G/K/P/PC/NPC and pairwise AND/OR values become real reusable outputs only when the dominated native primitive is flattened"
            ),
        },
        {
            "id": "full-adder-short-arcs",
            "outcome": "7/4 flat Full Adder has A/B->Sum,Cout depth 4 and Cin->Sum,Cout depth 2; native opaque 16/8 charges every input/output arc 8",
        },
        {
            "id": "switch-boolean-vs-physical",
            "outcome": "AND strictly dominates Switch only in a proof that driven/Z and BUS ownership are irrelevant",
        },
        {
            "id": "word-boundary",
            "outcome": "word NOT/NAND are lane-parallel without discount; word Switch shares one enable and one whole-word driven state",
        },
        {
            "id": "maker-splitter-normalize-z",
            "outcome": "0/0 Maker/Splitter preserve data lanes but not undriven state; their outputs are active",
        },
        {
            "id": "delay-line-boundary",
            "outcome": "Delay Line is a one-tick state producer only and cannot contribute to same-tick Byte Adder logic",
        },
        {
            "id": "kind16-17-name-mismatch",
            "outcome": "legacy symbol names say kind16 Splitter/kind17 Maker, while current prototype plus codegen prove kind16 is Maker8 and kind17 is Splitter8; runtime behavior wins",
        },
    ]

    return {
        "schema": "byte-adder-component-byproduct-catalog-v1",
        "status": "pass",
        "runtime": runtime_evidence,
        "permission_boundary": {
            "allowed_count": 23,
            "allowed_kinds": list(SELECTED_KINDS),
            "allowed_symbol_names": [SYMBOL_NAMES[kind] for kind in SELECTED_KINDS],
            "source": "legacy read-only pre-target closure certificate with current campaign metadata hashes revalidated",
            "forbidden": {
                "com_add": "unlocked only by completing byte_adder",
                "com_mux": "unlocked by downstream byte_mux",
            },
            "game_launched": False,
            "candidate_or_save_read_or_modified": False,
            "history_read_or_modified": False,
        },
        "evidence_policy": {
            "priority": [
                "live runtime behavior (not exercised in this static-only audit)",
                "captured traffic (none)",
                "actively served/current installed assets",
                "current process/executable configuration",
                "persisted challenge state (not read)",
                "generated artifacts",
                "checked-in source/comments",
            ],
            "classes": {
                "current_exe_static": "current 2.1.292 machine code/data",
                "current_campaign_metadata": "current installed campaign meta/test",
                "legacy_generated_certificate": "older generated audit; never promoted to current EXE fact",
                "repository_offline_model": "checked/replayed challenge model",
                "derived": "truth-table or structural consequence of cited evidence",
                "requires_live_test": "not claimed",
            },
            "artifacts": evidence_artifacts,
        },
        "cost_import_semantics": build_cost_policy(),
        "global_z_bus_rules": {
            "all_z": {"value": 0, "driven": False, "conflict": False},
            "active_drivers_all_same": {"value": "shared active value", "driven": True, "conflict": False},
            "active_zero_and_one": {"conflict": True, "effect": "short-circuit/halt"},
            "ordinary_gate_input": "reads the resolved data plane; Z data plane is 0",
            "ordinary_gate_output": "active driven",
            "bus_owner": "the complete resolved network owns its entire driver set; partial drivers cannot be split into free independent owners",
        },
        "components": components,
        "searcher_import_contract": searcher_contract,
        "maker_splitter_exact_constraints": {
            "purpose": "direct import constraints for Ling/Conditional/physical exact models",
            "valid_row_convention": "value/driven equations apply on conflict-free rows; conflict rows halt and are infeasible",
            "components": [
                component["maker_splitter_exact_constraints"]
                for component in adapter_components
            ],
        },
        "delay_line_current_static_audit": build_delay_evidence(),
        "authoritative_80_7_dag": dag_audit,
        "findings": findings,
        "self_checks": self_checks,
    }


def report_markdown(payload: dict[str, object], catalog_sha: str) -> str:
    dag = payload["authoritative_80_7_dag"]
    lines = [
        "# 字节加法器全元件副产物与短弧审计",
        "",
        "## 结论",
        "",
        f"- 主目录状态：`{payload['status']}`；JSON SHA-256：`{catalog_sha}`。",
        "- 当前 23 种合法原语的 prototype 公共输出与 codegen 写出数量一致；未发现隐藏可接线输出。",
        "- 原生内部值只有不可接线的生成代码局部量或状态槽：Full Adder 的 `U2 sum`、Delay Line 的一位状态、Splitter 的输入缓存局部量。",
        "- G/K/P/PC/NPC 等真实 producer 只在拆平后出现；不能从 opaque native 实例免费导入。",
        "- `80/7/560` 权威 DAG 已对 `131072` 行完整输入域重放，全部输出正确、无冲突、无 Z。",
        "",
        "## 当前版本锚点",
        "",
        f"- Version：`{payload['runtime']['version']}`",
        f"- Steam buildid：`{payload['runtime']['steam_buildid']}`",
        f"- EXE：`{payload['runtime']['exe']['path']}`",
        f"- EXE SHA-256：`{payload['runtime']['exe']['sha256']}`",
        f"- EXE size：`{payload['runtime']['exe']['size']}` bytes",
        "",
        "## 成本选择语义",
        "",
        "- default 只在该 kind frontier 为空时使用；saved/server frontier 非空时完全替代 default，不做二者取 min。",
        "- frontier 自身按 gate 递增、delay 递减维护 Pareto 集。",
        "- selector 0 取最小 gate 端，1 取最小 delay 端，2 按 gate/delay ceiling 选点。",
        "- 因此 Full Adder 当前双列必须写成 default `8/4`、旧证书 effective `16/8`；只有关卡重新验收或服务端导入后才可能变成 `7/4`。",
        "",
        "## 23 种原语",
        "",
        "| kind | symbol | 当前 prototype 语义 | default | effective | 公共输出 | native 内部可接线 |",
        "|---:|---|---|---:|---:|---|---|",
    ]
    for component in payload["components"]:
        default = component["cost"]["current_exe_default"]
        effective = component["cost"]["effective_now"]
        outputs = ", ".join(component["native_public_outputs"])
        lines.append(
            f"| {component['kind']} | `{component['symbol_name']}` | `{component['semantic_role']}` | "
            f"{default['gate']}/{default['delay']} | {effective['gate']}/{effective['delay']} | "
            f"{outputs or '-'} | 否 |"
        )
    lines.extend(["", "## 逐 kind 静态目录", ""])
    for component in payload["components"]:
        default = component["cost"]["current_exe_default"]
        effective = component["cost"]["effective_now"]
        lines.extend(
            [
                f"### kind {component['kind']} - `{component['symbol_name']}` / `{component['semantic_role']}`",
                "",
                f"- prototype：`{component['prototype_display_name']}`，slot `{component['prototype']['slot']}`，record `{component['prototype']['record_va']}`。",
                f"- 成本：current EXE default `{default['gate']}/{default['delay']}`；effective `{effective['gate']}/{effective['delay']}`；来源：{component['cost']['effective_source']}。",
                "- pins："
                + "; ".join(
                    f"`{pin['pin_id']}` {pin['direction']} `{pin['semantic_name']}` width=`{pin['word_size']}` offset=`{pin['offset']}`"
                    for pin in component["pins"]
                )
                + "。",
                f"- 公共输出：`{component['native_public_outputs']}`；隐藏可接线输出：`{component['native_hidden_wireable_outputs_found']}`。",
                f"- codegen：case `{component['codegen_case']['case_target']}`，machine SHA `{component['codegen_case']['code_bytes_sha256']}`，symbol counts `{json.dumps(component['codegen_case']['symbol_reference_counts'], ensure_ascii=False)}`。",
                f"- 组合弧：`{json.dumps(component['native_combinational_arcs'], ensure_ascii=False)}`。",
                f"- 时序弧：`{json.dumps(component['native_temporal_arcs'], ensure_ascii=False)}`。",
                f"- Z/driven：`{json.dumps(component['value_driven_z'], ensure_ascii=False)}`。",
                f"- native 内部对象：`{json.dumps(component['native_internal_codegen_artifacts'], ensure_ascii=False)}`。",
                f"- 拆平/支配：`{json.dumps(component['dominance'], ensure_ascii=False)}`。",
                f"- complete active-constant cofactor producer：`{component['native_truth_and_complete_active_constant_cofactors']['cofactor_count'] if component['native_truth_and_complete_active_constant_cofactors'] else 'N/A'}` 行，完整内容见 JSON。",
                "",
            ]
        )
    lines.extend(
        [
            "",
            "### kind 16/17 命名异常",
            "",
            "旧闭包证书的 symbol 名称把 kind 16 写作 Splitter、kind 17 写作 Maker；当前 EXE prototype 与 codegen 均证明实际运行语义相反：kind 16 是 Maker8，kind 17 是 Splitter8。目录同时保留 symbol 与 runtime semantic role，并以当前运行证据为准。",
            "",
            "## 被支配原语的最小拆平",
            "",
            "- XOR：`G=AND(A,B)`、`K=NOR(A,B)`、`P=NOR(G,K)`，`3/2`；G/K 互斥，和当前 native `3/2` 同分但多两个 D1 producer。",
            "- XNOR：`G=AND(A,B)`、`K=NOR(A,B)`、`Q=OR(G,K)`，`3/2`，严格支配 effective `5/4`。",
            "- AND3/OR3：两门树 `2/2`，可选择最值得复用的一对先合并。",
            "- Full Adder：七门 `7/4`，公开 Sum/Cout，内部真实输出 G/K/P/PC/NPC；`A/B -> outputs` 深度 4，`Cin -> outputs` 深度 2。",
            "- Switch：Boolean 数据面等价 `Enable AND Data`，但 AND 不保留 Z/driven/owner，因此只在已证明物理状态无关时支配。",
            "",
            "## Switch / BUS",
            "",
            "- bit Switch：`Enable=0 -> value=0, driven=false, Z`；`Enable=1 -> value=data_plane(Input), driven=true`。",
            "- word Switch：一个 Enable 控制整字；Z/driven 是整字状态，不是逐 lane mask。",
            "- BUS：全 Z 时数据面为 0；活动 driver 全同值时正常；活动 0/1 同时存在时 short-circuit/halt。",
            "- 同一 resolved network 的 driver set 不可拆成免费独立 owner。权威 DAG 的 5 个 BUS 均已逐 driver 记录 owner、enable/data、value/driven/conflict SHA。",
            "",
            "## Maker / Splitter 精确约束",
            "",
            "- kind 16/111/112 是 Maker8/2/4：`Result[i]=data_plane(Bit_i)`；逐 lane step delay 为 0，整字 public pin ready arrival 为所有输入 lane arrival 的最大值。",
            "- kind 17/109/110 是 Splitter8/2/4：`Bit_i=(data_plane(Input)>>i)&1`；每个输出 arrival 等于输入 arrival。",
            "- 六种 codegen 的每个 `input()` 调用均静态证明 `preserve_z=0`，每个公开输出均由 ordinary `store_output` 写出，所以 Z 被转为 active 0。",
            "- conflict 不是可归一化数据：Maker 输出 conflict predicate 是各输入 conflict 的 OR；Splitter 各输出继承输入 conflict；相应行 short-circuit/halt，exact 模型必须禁止或传播。",
            "- 六种转换器都是 0/0 physical-owner barrier：输出是新的 active owner，不能免费复制输入 tristate partial driver、Z 或 resolved BUS owner。",
            "",
            "## Delay Line",
            "",
            "- `Q(0)=0`，`Result(t)=Q(t)`，`Q(t+1)=data_plane(Input(t))`。",
            "- reset/首周期输出均为 active 0；输入 Z 不传播，下一 tick 得到 active 0。",
            "- 可串联、可反馈，但不是 same-tick Byte Adder producer。",
            "",
            "## 权威 80/7 DAG",
            "",
            f"- Source：`{dag['source']}`",
            f"- Factory DAG SHA-256：`{dag['source_factory_dag_sha256']}`",
            f"- Metrics：`{dag['metrics']['gate']}/{dag['metrics']['delay']}/{dag['metrics']['energy']}`",
            f"- Live nodes：`{dag['metrics']['live_node_count']}`；op counts：`{json.dumps(dag['metrics']['op_counts'], ensure_ascii=False)}`",
            f"- Outputs：`{dag['metrics']['output_ids']}` -> `{dag['metrics']['output_names']}`",
            f"- 完整域：`{dag['truth_domain']['row_count']}` 行；mismatch=`{dag['metrics']['mismatch_union_count']}`，conflict=`{dag['metrics']['conflict_assignment_count']}`，output Z=`{dag['metrics']['z_assignment_count_by_output']}`。",
            f"- 全局关系统计：`{json.dumps(dag['global_relations']['counts'], ensure_ascii=False)}`。",
            "",
            "## 已证与待证",
            "",
            "- 已证：当前 EXE 引脚/default/codegen；当前 campaign Delay Line 文本与测试；当前 EXE cost import 行为；指定 80/7 DAG 的完整域 value/driven/conflict；旧证书记录的 saved frontier 与 Full Adder exact bound。",
            "- 待实测：远端服务端是否接受并回传 `7/4`；本静态审计不把客户端 import 能力写成服务端确认。",
            "",
            "## 复现",
            "",
            "```powershell",
            f"python \"{HERE / 'audit_component_catalog.py'}\"",
            "```",
            "",
            "生成器只读研究工件、当前 EXE 与当前 campaign meta/test；不读写正式存档、candidate 或 history，也不启动游戏。",
            "",
            "## 自检",
            "",
        ]
    )
    for key, value in payload["self_checks"].items():
        lines.append(f"- `{key}`: `{'PASS' if value else 'FAIL'}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    payload = build()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.write_bytes(encoded.encode("utf-8"))
    digest = sha256(encoded.encode("utf-8")).hexdigest()
    report = report_markdown(payload, digest)
    args.report.write_bytes(report.encode("utf-8"))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(args.output),
                "output_sha256": digest,
                "report": str(args.report),
                "report_sha256": sha256(report.encode("utf-8")).hexdigest(),
                "component_count": len(payload["components"]),
                "dag_metrics": payload["authoritative_80_7_dag"]["metrics"],
                "self_check_count": len(payload["self_checks"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
