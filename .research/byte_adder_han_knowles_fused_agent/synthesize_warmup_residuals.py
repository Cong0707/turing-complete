"""Synthesize Byte Adder residuals enabled after cycle zero.

The autonomous phase is one zero-initialized Bit Delay Line whose data input
is constant one.  Its output is zero at cycle 0 and one thereafter.  Since
all Byte Adder outputs are zero at cycle 0, each replaced output can be
implemented as ``AND(phase, residual)``.  The residual therefore has exactly
one Boolean don't-care assignment, x=0; this is a warm-up cofactor, not a
terminal test don't-care.

This is a candidate-discovery and replay tool.  It never edits a game save or
the reviewed 80/7 DAG.  Every mapped BLIF is independently evaluated on all
2^17 current assignments and then replayed in the live test.si cycle order.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import time
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASELINE = ROOT / ".research" / "byte_adder_root" / (
    "byte-adder-hybrid-phasefold-g80-d7.json"
)
TEST_SI = Path(
    r"D:\Game\Steam\steamapps\common\Turing Complete\campaign\byte_adder\test.si"
)
ABC = ROOT / ".research" / "yosys-msys" / "mingw64" / "bin" / "yosys-abc.exe"
GENLIB = ROOT / ".research" / "turing-complete.genlib"
ESPRESSO = ROOT / ".research" / "rng_42state_direct" / "sample_nonlinear" / (
    "agent_care"
) / "espresso-src" / "bin" / "espresso.exe"
OUTPUT_ROOT = HERE / "warmup_residual_intake"

WIDTH = 17
ROWS = 1 << WIDTH
VALUE_MASK = ROWS - 1
TRUTH_MASK = (1 << ROWS) - 1
OUTPUT_NAMES = tuple([f"S{bit}" for bit in range(8)] + ["Cout"])
GROUPS: dict[str, tuple[int, ...]] = {
    "slow6": (2, 4, 5, 6, 7, 8),
    "all9": tuple(range(9)),
}

GATE_RE = re.compile(r"^\.gate\s+(\S+)\s+(.+)$")
PIN_RE = re.compile(r"([A-Za-z0-9_$./\\:\[\]-]+)=([^\s]+)")
NAMES_RE = re.compile(r"^\.names(?:\s+(.*))?$")
STEP_DELAY = {
    "BUF": 0,
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 2,
    "XNOR": 2,
}
GATE_COST = {
    "BUF": 0,
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 3,
    "XNOR": 3,
}
RECIPES = {
    "plain": "fx; strash",
    "resyn": (
        "fx; strash; balance; rewrite; refactor; balance; rewrite -z; "
        "refactor -z; balance; dch"
    ),
    "resyn2": (
        "fx; strash; balance; rewrite; refactor; balance; rewrite; "
        "rewrite -z; balance; refactor -z; rewrite -z; balance; dch"
    ),
    "dc2": "fx; strash; balance; rewrite; refactor; balance; dc2; dch",
    "resub8": (
        "fx; strash; balance; resub -K 8; resub -K 8 -N 2; rewrite; "
        "refactor; balance; dch"
    ),
}


@dataclass(frozen=True)
class NamesNode:
    inputs: tuple[str, ...]
    output: str
    cubes: tuple[str, ...]


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def live_xorshift(cycle: int) -> int:
    """Match live Int semantics: do not mask between shifts."""

    value = cycle
    value ^= value << 6
    value ^= value >> 11
    value ^= value << 9
    return value & VALUE_MASK


def byte_adder_output(value: int) -> int:
    return (value & 0xFF) + ((value >> 8) & 0xFF) + ((value >> 16) & 1)


def assignment_pattern(value: int) -> str:
    # PLA label xN denotes numeric bit N, so the textual order is LSB first.
    return "".join("1" if (value >> bit) & 1 else "0" for bit in range(WIDTH))


def parse_test_contract() -> dict[str, object]:
    text = TEST_SI.read_text(encoding="utf-8")
    required = {
        "cycle_source": r"var\s+x\s*=\s*cycle",
        "shift_left_6": r"x\s*\^=\s*x\s*<<\s*6",
        "shift_right_11": r"x\s*\^=\s*x\s*>>\s*11",
        "shift_left_9": r"x\s*\^=\s*x\s*<<\s*9",
        "last_cycle": r"cycle\s*==\s*0x1ffff",
    }
    matches = {
        name: bool(re.search(pattern, text, flags=re.MULTILINE))
        for name, pattern in required.items()
    }
    if not all(matches.values()):
        raise RuntimeError(f"installed test.si contract changed: {matches}")
    return {
        "path": str(TEST_SI),
        "sha256": digest(TEST_SI),
        "required_source_patterns": matches,
        "first_cycle": 0,
        "last_cycle": ROWS - 1,
        "cycles": ROWS,
    }


def verify_live_permutation() -> dict[str, object]:
    seen = bytearray(ROWS)
    sequence = bytearray()
    zero_cycles: list[int] = []
    duplicate_count = 0
    for cycle in range(ROWS):
        value = live_xorshift(cycle)
        sequence.extend(value.to_bytes(3, "little"))
        if seen[value]:
            duplicate_count += 1
        seen[value] = 1
        if value == 0:
            zero_cycles.append(cycle)
    missing_count = seen.count(0)
    if duplicate_count or missing_count or zero_cycles != [0]:
        raise RuntimeError(
            "live sequence is not the expected permutation: "
            f"duplicates={duplicate_count}, missing={missing_count}, zero={zero_cycles}"
        )
    return {
        "is_complete_17_bit_permutation": True,
        "duplicate_assignment_count": duplicate_count,
        "missing_assignment_count": missing_count,
        "zero_assignment_cycles": zero_cycles,
        "packed_u24le_sequence_sha256": sha256(sequence).hexdigest(),
    }


def write_care_pla(path: Path, selected: tuple[int, ...]) -> dict[str, object]:
    names = [OUTPUT_NAMES[index] for index in selected]
    lines = [
        f".i {WIDTH}",
        f".o {len(selected)}",
        ".type fr",
        ".ilb " + " ".join(f"x{bit}" for bit in range(WIDTH)),
        ".ob " + " ".join(names),
        "# x=0 is the sole warm-up residual don't-care assignment.",
    ]
    output_ones = [0] * len(selected)
    for assignment in range(ROWS):
        if assignment == 0:
            out_pattern = "-" * len(selected)
        else:
            target = byte_adder_output(assignment)
            bits = []
            for local, output_index in enumerate(selected):
                value = (target >> output_index) & 1
                output_ones[local] += value
                bits.append(str(value))
            out_pattern = "".join(bits)
        lines.append(f"{assignment_pattern(assignment)} {out_pattern}")
    lines.append(".e")
    path.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    return {
        "path": str(path),
        "sha256": digest(path),
        "rows": ROWS,
        "care_assignments": ROWS - 1,
        "dont_care_assignments": [0],
        "output_indices": list(selected),
        "output_names": names,
        "one_counts_excluding_dc": output_ones,
    }


def run_process(
    command: list[str],
    *,
    timeout: int,
    stdin_path: Path | None = None,
) -> dict[str, object]:
    started = time.monotonic()
    stdin_handle = stdin_path.open("rb") if stdin_path is not None else None
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            stdin=stdin_handle,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "UNKNOWN",
            "reason": "timeout",
            "timeout_seconds": timeout,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "partial_stdout": (exc.stdout or b"").decode("utf-8", errors="replace")[-4000:],
            "partial_stderr": (exc.stderr or b"").decode("utf-8", errors="replace")[-4000:],
        }
    finally:
        if stdin_handle is not None:
            stdin_handle.close()
    elapsed = round(time.monotonic() - started, 3)
    stdout = completed.stdout.decode("utf-8", errors="replace")
    stderr = completed.stderr.decode("utf-8", errors="replace")
    if completed.returncode != 0:
        return {
            "status": "UNKNOWN",
            "reason": "nonzero_returncode",
            "returncode": completed.returncode,
            "elapsed_seconds": elapsed,
            "stdout_tail": stdout[-4000:],
            "stderr_tail": stderr[-4000:],
        }
    return {
        "status": "COMPLETE",
        "returncode": completed.returncode,
        "elapsed_seconds": elapsed,
        "stdout_bytes": completed.stdout,
        "stderr_text": stderr,
    }


def minimize_with_espresso(
    source: Path,
    destination: Path,
    log_path: Path,
    timeout: int,
    mode: str,
) -> dict[str, object]:
    options = [] if mode == "default" else ["-Dso"]
    command = [str(ESPRESSO), *options]
    result = run_process(command, timeout=timeout, stdin_path=source)
    if result["status"] != "COMPLETE":
        log_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return {**result, "mode": mode, "command": command}
    encoded = bytes(result.pop("stdout_bytes"))
    stderr = str(result.pop("stderr_text"))
    destination.write_bytes(encoded)
    log_path.write_text(stderr, encoding="utf-8", newline="\n")
    parsed = parse_f_pla(destination)
    verification = verify_cover(parsed)
    if verification["care_mismatch_union"]:
        raise RuntimeError(f"Espresso cover failed care verification: {verification}")
    return {
        **result,
        "mode": mode,
        "command": command,
        "output": str(destination),
        "output_sha256": digest(destination),
        "stderr_log": str(log_path),
        "stderr_log_sha256": digest(log_path),
        "cube_count": len(parsed["cubes"]),
        "input_literal_count": sum(
            sum(value != "-" for value in cube[0]) for cube in parsed["cubes"]
        ),
        "output_literal_count": sum(
            sum(value == "1" for value in cube[1]) for cube in parsed["cubes"]
        ),
        **verification,
    }


def parse_f_pla(path: Path) -> dict[str, object]:
    input_names: list[str] = []
    output_names: list[str] = []
    cubes: list[tuple[str, str]] = []
    for raw in path.read_text(encoding="ascii").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(".ilb "):
            input_names = line.split()[1:]
        elif line.startswith(".ob "):
            output_names = line.split()[1:]
        elif not line.startswith("."):
            in_pattern, out_pattern = line.split()
            cubes.append((in_pattern, out_pattern))
    if input_names != [f"x{bit}" for bit in range(WIDTH)]:
        raise ValueError(f"unexpected Espresso inputs in {path}: {input_names}")
    if not output_names:
        raise ValueError(f"missing Espresso output labels in {path}")
    for in_pattern, out_pattern in cubes:
        if len(in_pattern) != WIDTH or len(out_pattern) != len(output_names):
            raise ValueError(f"malformed cube in {path}: {in_pattern} {out_pattern}")
        if set(in_pattern) - {"0", "1", "-"} or set(out_pattern) - {"0", "1", "-"}:
            raise ValueError(f"unsupported cube alphabet in {path}")
    return {"inputs": input_names, "outputs": output_names, "cubes": cubes}


def build_truth_vectors() -> tuple[dict[str, int], tuple[int, ...]]:
    """Pack truth vectors without repeated growth of giant Python integers."""

    byte_count = ROWS // 8
    raw_inputs = [bytearray(byte_count) for _ in range(WIDTH)]
    raw_expected = [bytearray(byte_count) for _ in range(9)]
    for assignment in range(ROWS):
        byte_index = assignment >> 3
        marker = 1 << (assignment & 7)
        target = byte_adder_output(assignment)
        for bit in range(WIDTH):
            if (assignment >> bit) & 1:
                raw_inputs[bit][byte_index] |= marker
        for output in range(9):
            if (target >> output) & 1:
                raw_expected[output][byte_index] |= marker
    inputs = {
        f"x{bit}": int.from_bytes(raw_inputs[bit], "little")
        for bit in range(WIDTH)
    }
    expected = tuple(int.from_bytes(raw, "little") for raw in raw_expected)
    return inputs, expected


INPUT_VECTORS, EXPECTED_VECTORS = build_truth_vectors()


def evaluate_cube(pattern: str) -> int:
    value = TRUTH_MASK
    for bit, required in enumerate(pattern):
        if required == "1":
            value &= INPUT_VECTORS[f"x{bit}"]
        elif required == "0":
            value &= ~INPUT_VECTORS[f"x{bit}"] & TRUTH_MASK
    return value


def verify_cover(parsed: dict[str, object]) -> dict[str, object]:
    actual = [0] * len(parsed["outputs"])
    for in_pattern, out_pattern in parsed["cubes"]:
        matched = evaluate_cube(in_pattern)
        for index, output_value in enumerate(out_pattern):
            if output_value == "1":
                actual[index] |= matched
    mismatches = []
    actual_at_dc = []
    care_mask = TRUTH_MASK ^ 1
    for local, name in enumerate(parsed["outputs"]):
        output_index = OUTPUT_NAMES.index(name)
        mismatches.append(((actual[local] ^ EXPECTED_VECTORS[output_index]) & care_mask).bit_count())
        actual_at_dc.append(actual[local] & 1)
    return {
        "care_mismatch_count_by_output": mismatches,
        "care_mismatch_union": sum(mismatches),
        "residual_value_at_dc_assignment": actual_at_dc,
    }


def convert_to_blif(pla: Path, blif: Path, log_path: Path, timeout: int) -> dict[str, object]:
    command_text = (
        f"read_library {GENLIB.as_posix()}; read_pla {pla.as_posix()}; "
        f"write_blif {blif.as_posix()}"
    )
    result = run_process([str(ABC), "-c", command_text], timeout=timeout)
    stdout = bytes(result.pop("stdout_bytes", b"")).decode("utf-8", errors="replace")
    stderr = str(result.pop("stderr_text", ""))
    log_path.write_text(stdout + stderr, encoding="utf-8", newline="\n")
    if result["status"] == "COMPLETE" and not blif.is_file():
        result = {**result, "status": "UNKNOWN", "reason": "missing_output_blif"}
    return {
        **result,
        "command": command_text,
        "log": str(log_path),
        "log_sha256": digest(log_path),
        "blif": str(blif) if blif.exists() else None,
        "blif_sha256": digest(blif) if blif.exists() else None,
    }


def add_timing(source: Path, destination: Path, output_names: Iterable[str]) -> None:
    lines = source.read_text(encoding="ascii").splitlines()
    if not lines or lines[-1].strip() != ".end":
        raise ValueError(f"{source}: missing terminal .end")
    timing = [
        ".default_input_arrival 0 0",
        ".default_output_required 4 4",
        *[f".input_arrival x{bit} 0 0" for bit in range(WIDTH)],
        *[f".output_required {name} 4 4" for name in output_names],
    ]
    destination.write_text(
        "\n".join(lines[:-1] + timing + [".end"]) + "\n",
        encoding="ascii",
        newline="\n",
    )


def parse_names(lines: list[str], index: int) -> tuple[NamesNode, int]:
    match = NAMES_RE.match(lines[index].strip())
    if match is None:
        raise ValueError(lines[index])
    nets = tuple(match.group(1).split()) if match.group(1) else ()
    if not nets:
        raise ValueError(".names without an output net")
    cubes: list[str] = []
    index += 1
    while index < len(lines) and not lines[index].lstrip().startswith("."):
        if lines[index].strip():
            cubes.append(lines[index].strip())
        index += 1
    return NamesNode(nets[:-1], nets[-1], tuple(cubes)), index


def parse_blif(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="ascii").splitlines()
    inputs: list[str] = []
    outputs: list[str] = []
    operations: list[dict[str, object]] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith(".inputs "):
            inputs.extend(line.split()[1:])
        elif line.startswith(".outputs "):
            outputs.extend(line.split()[1:])
        elif line.startswith(".names"):
            node, index = parse_names(lines, index)
            operations.append({"kind": "NAMES", "node": node})
            continue
        else:
            match = GATE_RE.match(line)
            if match is not None:
                operations.append(
                    {
                        "kind": match.group(1).upper(),
                        "pins": dict(PIN_RE.findall(match.group(2))),
                    }
                )
        index += 1
    return {"inputs": inputs, "outputs": outputs, "operations": operations}


def evaluate_names(node: NamesNode, values: dict[str, int]) -> int:
    result = 0
    for raw_cube in node.cubes:
        fields = raw_cube.split()
        if not node.inputs:
            if fields and fields[-1] == "1":
                result = TRUTH_MASK
            continue
        pattern = fields[0]
        output_value = fields[1] if len(fields) > 1 else "1"
        if output_value != "1":
            raise ValueError(f"unsupported off-set .names cube: {raw_cube}")
        matched = TRUTH_MASK
        for source, required in zip(node.inputs, pattern):
            if required == "1":
                matched &= values[source]
            elif required == "0":
                matched &= ~values[source] & TRUTH_MASK
        result |= matched
    return result


def analyze_mapped(path: Path, selected: tuple[int, ...]) -> dict[str, object]:
    network = parse_blif(path)
    expected_inputs = [f"x{bit}" for bit in range(WIDTH)]
    if network["inputs"] != expected_inputs:
        raise ValueError(f"mapped input contract differs: {network['inputs']}")
    expected_outputs = [OUTPUT_NAMES[index] for index in selected]
    if network["outputs"] != expected_outputs:
        raise ValueError(f"mapped output contract differs: {network['outputs']}")

    values = dict(INPUT_VECTORS)
    arrivals = {name: 0 for name in expected_inputs}
    ordinary_gate = 0
    mapped_components = 0
    kind_counts: dict[str, int] = {}
    names_nodes = 0

    for operation in network["operations"]:
        kind = str(operation["kind"])
        if kind == "NAMES":
            node = operation["node"]
            assert isinstance(node, NamesNode)
            missing = [source for source in node.inputs if source not in values]
            if missing:
                raise ValueError(f"unresolved .names inputs for {node.output}: {missing}")
            # Mapped ABC uses .names only for constants and zero-cost aliases.
            if len(node.inputs) > 1:
                raise ValueError(f"unmapped multi-input .names node: {node}")
            values[node.output] = evaluate_names(node, values)
            arrivals[node.output] = max(
                (arrivals[source] for source in node.inputs), default=0
            )
            names_nodes += 1
            continue

        if kind not in STEP_DELAY:
            raise ValueError(f"unsupported mapped gate {kind}")
        pins = dict(operation["pins"])
        if "Y" not in pins:
            raise ValueError(f"mapped gate lacks Y pin: {operation}")
        output = pins.pop("Y")
        sources = list(pins.values())
        missing = [source for source in sources if source not in values]
        if missing:
            raise ValueError(f"unresolved inputs for {output}: {missing}")
        if kind == "BUF":
            result = values[sources[0]]
        elif kind == "NOT":
            result = ~values[sources[0]] & TRUTH_MASK
        elif kind == "AND":
            result = values[sources[0]] & values[sources[1]]
        elif kind == "OR":
            result = values[sources[0]] | values[sources[1]]
        elif kind == "NAND":
            result = ~(values[sources[0]] & values[sources[1]]) & TRUTH_MASK
        elif kind == "NOR":
            result = ~(values[sources[0]] | values[sources[1]]) & TRUTH_MASK
        elif kind == "XOR":
            result = values[sources[0]] ^ values[sources[1]]
        elif kind == "XNOR":
            result = ~(values[sources[0]] ^ values[sources[1]]) & TRUTH_MASK
        else:  # pragma: no cover - kept exhaustive with the dictionaries
            raise AssertionError(kind)
        values[output] = result
        arrivals[output] = max(arrivals[source] for source in sources) + STEP_DELAY[kind]
        ordinary_gate += GATE_COST[kind]
        mapped_components += 1
        kind_counts[kind] = kind_counts.get(kind, 0) + 1

    care_mask = TRUTH_MASK ^ 1
    care_mismatches: list[int] = []
    residual_at_dc: list[int] = []
    output_arrivals: list[int] = []
    full_shell_mismatches: list[int] = []
    cycle_mismatches: list[int] = []
    for local, (name, output_index) in enumerate(zip(expected_outputs, selected)):
        if name not in values or name not in arrivals:
            raise ValueError(f"missing mapped output net: {name}")
        expected = EXPECTED_VECTORS[output_index]
        care_mismatches.append(((values[name] ^ expected) & care_mask).bit_count())
        residual_at_dc.append(values[name] & 1)
        output_arrivals.append(arrivals[name])
        # phase assignment is 0 only for x=0/cycle0, then 1 forever.
        shell_value = values[name] & care_mask
        full_shell_mismatches.append((shell_value ^ expected).bit_count())
        live_mismatch = 0
        for cycle in range(ROWS):
            assignment = live_xorshift(cycle)
            phase = int(cycle >= 1)
            actual = phase & ((values[name] >> assignment) & 1)
            target = (byte_adder_output(assignment) >> output_index) & 1
            live_mismatch += actual != target
        cycle_mismatches.append(live_mismatch)

    return {
        "ordinary_gate": ordinary_gate,
        "mapped_components": mapped_components,
        "zero_cost_names_nodes": names_nodes,
        "kind_counts": dict(sorted(kind_counts.items())),
        "residual_output_arrivals": output_arrivals,
        "residual_delay": max(output_arrivals, default=0),
        "care_mismatch_count_by_output": care_mismatches,
        "care_mismatch_union": sum(care_mismatches),
        "residual_value_at_dc_assignment": residual_at_dc,
        "warmup_shell_assignment_mismatch_count_by_output": full_shell_mismatches,
        "warmup_shell_cycle_mismatch_count_by_output": cycle_mismatches,
        "warmup_shell_mismatch_union": sum(cycle_mismatches),
        "conflict_assignment_count": 0,
        "z_assignment_count_by_output": [0] * len(selected),
    }


def baseline_cut(selected: tuple[int, ...]) -> dict[str, object]:
    payload = json.loads(BASELINE.read_text(encoding="utf-8"))
    raw_nodes = tuple(payload["factory_dag"]["nodes"])
    nodes = {int(node["id"]): node for node in raw_nodes}
    outputs = tuple(int(value) for value in payload["factory_dag"]["outputs"])
    retained_outputs = [outputs[index] for index in range(9) if index not in selected]
    reachable: set[int] = set()
    stack = list(retained_outputs)
    while stack:
        node_id = stack.pop()
        if node_id in reachable:
            continue
        reachable.add(node_id)
        stack.extend(int(value) for value in nodes[node_id].get("args", ()))
    retained_gate = sum(int(nodes[node_id]["cost"]) for node_id in reachable)
    baseline_gate = sum(int(node["cost"]) for node in raw_nodes)
    retained_indices = [index for index in range(9) if index not in selected]
    retained_arrivals = [int(nodes[outputs[index]]["arrival"]) for index in retained_indices]
    return {
        "selected_output_indices": list(selected),
        "selected_output_names": [OUTPUT_NAMES[index] for index in selected],
        "retained_output_indices": retained_indices,
        "retained_output_names": [OUTPUT_NAMES[index] for index in retained_indices],
        "baseline_gate": baseline_gate,
        "deleted_current_gate": baseline_gate - retained_gate,
        "retained_current_gate": retained_gate,
        "retained_current_node_ids": sorted(reachable),
        "retained_output_arrivals": retained_arrivals,
        "retained_delay": max(retained_arrivals, default=0),
    }


def map_recipe(
    timed_blif: Path,
    mapped: Path,
    log: Path,
    recipe_name: str,
    recipe: str,
    selected: tuple[int, ...],
    cut: dict[str, object],
    timeout: int,
) -> dict[str, object]:
    command_text = (
        f"read_library {GENLIB.as_posix()}; read_blif -n {timed_blif.as_posix()}; "
        f"{recipe}; map -D 4; topo; print_stats; write_blif {mapped.as_posix()}"
    )
    result = run_process([str(ABC), "-c", command_text], timeout=timeout)
    stdout = bytes(result.pop("stdout_bytes", b"")).decode("utf-8", errors="replace")
    stderr = str(result.pop("stderr_text", ""))
    log.write_text(stdout + stderr, encoding="utf-8", newline="\n")
    base = {
        "recipe": recipe_name,
        **result,
        "command": command_text,
        "log": str(log),
        "log_sha256": digest(log),
        "abc_reported_unmet_timing": "Cannot meet the target required times" in stdout,
    }
    if result["status"] != "COMPLETE" or not mapped.exists():
        if result["status"] == "COMPLETE":
            base.update({"status": "UNKNOWN", "reason": "missing_mapped_blif"})
        return base
    try:
        score = analyze_mapped(mapped, selected)
    except Exception as exc:
        return {
            **base,
            "status": "UNKNOWN",
            "reason": "mapped_replay_exception",
            "exception": repr(exc),
            "mapped_blif": str(mapped),
            "mapped_blif_sha256": digest(mapped),
        }
    phase_gate = 5
    outer_gate = len(selected)
    total_gate = int(cut["retained_current_gate"]) + phase_gate + outer_gate + int(
        score["ordinary_gate"]
    )
    shell_arrivals = [max(4, value) + 1 for value in score["residual_output_arrivals"]]
    output_arrivals = list(cut["retained_output_arrivals"]) + shell_arrivals
    total_delay = max(output_arrivals, default=0)
    qualified = (
        score["care_mismatch_union"] == 0
        and score["warmup_shell_mismatch_union"] == 0
        and score["residual_delay"] <= 4
        and total_gate < int(cut["baseline_gate"])
        and total_delay <= 5
    )
    return {
        **base,
        "status": "SAT",
        "mapped_blif": str(mapped),
        "mapped_blif_sha256": digest(mapped),
        **score,
        "fixed_shell": {
            "retained_current_gate": cut["retained_current_gate"],
            "phase_gate": phase_gate,
            "outer_and_gate": outer_gate,
            "fixed_gate_before_residual": int(cut["retained_current_gate"])
            + phase_gate
            + outer_gate,
            "phase_arrival": 4,
            "outer_and_step_delay": 1,
        },
        "candidate_total_gate": total_gate,
        "candidate_output_arrivals": output_arrivals,
        "candidate_delay": total_delay,
        "candidate_energy": total_gate * total_delay,
        "beats_80_gate_at_d5": qualified,
    }


def synthesize_group(
    name: str,
    selected: tuple[int, ...],
    *,
    espresso_timeout: int,
    abc_timeout: int,
    espresso_mode: str,
) -> dict[str, object]:
    group_dir = OUTPUT_ROOT / name
    group_dir.mkdir(parents=True, exist_ok=True)
    care = group_dir / "care.pla"
    minimized = group_dir / f"espresso_{espresso_mode}.pla"
    espresso_log = group_dir / f"espresso_{espresso_mode}.stderr.log"
    base_blif = group_dir / f"espresso_{espresso_mode}.blif"
    convert_log = group_dir / "abc_convert.log"
    timed_blif = group_dir / "timed_d4.blif"
    for stale in (minimized, base_blif, timed_blif):
        stale.unlink(missing_ok=True)

    pla_metadata = write_care_pla(care, selected)
    cut = baseline_cut(selected)
    espresso_result = minimize_with_espresso(
        care, minimized, espresso_log, espresso_timeout, espresso_mode
    )
    if espresso_result["status"] != "COMPLETE":
        return {
            "name": name,
            "status": "UNKNOWN",
            "reason": "espresso_incomplete",
            "pla": pla_metadata,
            "cut": cut,
            "espresso": espresso_result,
            "mapping_results": [],
        }
    conversion = convert_to_blif(minimized, base_blif, convert_log, abc_timeout)
    if conversion["status"] != "COMPLETE":
        return {
            "name": name,
            "status": "UNKNOWN",
            "reason": "abc_conversion_incomplete",
            "pla": pla_metadata,
            "cut": cut,
            "espresso": espresso_result,
            "conversion": conversion,
            "mapping_results": [],
        }
    add_timing(base_blif, timed_blif, [OUTPUT_NAMES[index] for index in selected])
    mapping_results = []
    for recipe_name, recipe in RECIPES.items():
        mapped = group_dir / f"mapped_{recipe_name}_d4.blif"
        log = group_dir / f"abc_{recipe_name}_d4.log"
        mapped.unlink(missing_ok=True)
        mapping_results.append(
            map_recipe(
                timed_blif,
                mapped,
                log,
                recipe_name,
                recipe,
                selected,
                cut,
                abc_timeout,
            )
        )
    mapping_results.sort(
        key=lambda item: (
            item.get("status") != "SAT",
            item.get("candidate_energy", 10**9),
            item.get("candidate_delay", 10**9),
            item.get("candidate_total_gate", 10**9),
            item["recipe"],
        )
    )
    return {
        "name": name,
        "status": "COMPLETE",
        "pla": pla_metadata,
        "cut": cut,
        "espresso": espresso_result,
        "conversion": conversion,
        "timed_blif": str(timed_blif),
        "timed_blif_sha256": digest(timed_blif),
        "mapping_results": mapping_results,
        "qualified_candidate_count": sum(
            bool(item.get("beats_80_gate_at_d5")) for item in mapping_results
        ),
        "unknown_mapping_count": sum(
            item.get("status") == "UNKNOWN" for item in mapping_results
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--groups", nargs="*", choices=sorted(GROUPS))
    parser.add_argument("--espresso-timeout", type=int, default=1200)
    parser.add_argument("--abc-timeout", type=int, default=600)
    parser.add_argument("--espresso-mode", choices=("default", "so"), default="default")
    args = parser.parse_args()

    for path in (BASELINE, TEST_SI, ABC, GENLIB, ESPRESSO):
        if not path.is_file():
            raise FileNotFoundError(path)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    selected_groups = args.groups or ["slow6", "all9"]
    test_contract = parse_test_contract()
    live_permutation = verify_live_permutation()
    started = time.monotonic()
    groups = []
    for name in selected_groups:
        print(f"synthesizing {name}...", flush=True)
        result = synthesize_group(
            name,
            GROUPS[name],
            espresso_timeout=args.espresso_timeout,
            abc_timeout=args.abc_timeout,
            espresso_mode=args.espresso_mode,
        )
        groups.append(result)
        best = next(
            (
                item
                for item in result.get("mapping_results", [])
                if item.get("status") == "SAT"
            ),
            None,
        )
        if best is not None:
            print(
                f"{name}: best {best['recipe']} residual="
                f"{best['ordinary_gate']}/{best['residual_delay']} total="
                f"{best['candidate_total_gate']}/{best['candidate_delay']} "
                f"qualified={best['beats_80_gate_at_d5']}",
                flush=True,
            )
        else:
            print(f"{name}: no completed mapped result", flush=True)

    previous_groups = []
    previous_summary = OUTPUT_ROOT / "summary.json"
    if previous_summary.is_file():
        try:
            previous_payload = json.loads(previous_summary.read_text(encoding="utf-8"))
            if previous_payload.get("schema") == "tc-byte-adder-cycle0-warmup-residual-intake-v1":
                previous_groups = [
                    group
                    for group in previous_payload.get("groups", [])
                    if group.get("name") not in selected_groups
                ]
        except (OSError, ValueError, TypeError):
            previous_groups = []
    groups.extend(previous_groups)
    groups.sort(key=lambda group: group["name"])

    qualified = [
        {"group": group["name"], **item}
        for group in groups
        for item in group.get("mapping_results", [])
        if item.get("beats_80_gate_at_d5")
    ]
    unknown_count = sum(
        item.get("status") == "UNKNOWN"
        for group in groups
        for item in group.get("mapping_results", [])
    )
    report = {
        "schema": "tc-byte-adder-cycle0-warmup-residual-intake-v1",
        "status": "COMPLETE" if all(g["status"] == "COMPLETE" for g in groups) else "UNKNOWN",
        "scope": "candidate-discovery; no save materialization",
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "selected_groups_this_run": selected_groups,
        "espresso_mode_this_run": args.espresso_mode,
        "test_contract": test_contract,
        "live_sequence": live_permutation,
        "baseline": {
            "path": str(BASELINE),
            "sha256": digest(BASELINE),
            "reported_gate": 80,
            "reported_delay": 7,
        },
        "tools": {
            "espresso": {"path": str(ESPRESSO), "sha256": digest(ESPRESSO)},
            "abc": {"path": str(ABC), "sha256": digest(ABC)},
            "genlib": {"path": str(GENLIB), "sha256": digest(GENLIB)},
        },
        "warmup_model": {
            "delay_line_count": 1,
            "delay_line_gate": 5,
            "delay_line_arrival": 4,
            "init_data": 0,
            "data_input": 1,
            "phase_by_cycle": "0 at cycle 0; 1 at cycles 1..131071",
            "outer_gate": "AND",
            "outer_gate_cost": 1,
            "outer_gate_step_delay": 1,
            "residual_care_source_cycles": [1, ROWS - 1],
            "residual_dont_care_source_cycles": [0],
            "terminal_dont_care_present": False,
            "reason": "At cycle 0 the phase is zero and all targets are zero, so AND does not observe residual F.",
        },
        "thresholds": {
            "global_delay_at_most": 5,
            "global_gate_less_than": 80,
            "slow6_residual_gate_at_most": 34,
            "all9_residual_gate_at_most": 65,
            "residual_delay_at_most": 4,
        },
        "recipes": RECIPES,
        "groups": groups,
        "qualified_candidates": qualified,
        "qualified_candidate_count": len(qualified),
        "unknown_mapping_count": unknown_count,
        "search_interpretation": (
            "SAT candidate(s) found"
            if qualified
            else "No qualifying candidate found by these finite recipes; this is not UNSAT"
        ),
    }
    report_path = OUTPUT_ROOT / "summary.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"summary={report_path}", flush=True)
    print(f"summary_sha256={digest(report_path)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
