"""Independent row-by-row replay for ordinary-gate V-cone witnesses.

This verifier deliberately does not import the CNF encoder.  It reconstructs
all 64 input assignments, evaluates every gate as a scalar Boolean operation,
and derives depth from graph dependencies instead of trusting SAT metadata.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SUPPORTED_KINDS = {"NOT", "AND", "OR", "NAND", "NOR"}
EXPECTED_SUPPORTS = ((0, 1, 2, 3), (0, 1, 4, 5))


def apply_gate(kind: str, left: bool, right: bool) -> bool:
    if kind == "NOT":
        return not left
    if kind == "AND":
        return left and right
    if kind == "OR":
        return left or right
    if kind == "NAND":
        return not (left and right)
    if kind == "NOR":
        return not (left or right)
    raise ValueError(f"unsupported gate kind: {kind}")


def pack_rows(rows: list[bool]) -> int:
    return sum(int(value) << case for case, value in enumerate(rows))


def verify(payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []
    if payload.get("status") != "sat":
        errors.append("artifact status is not sat")

    input_count = int(payload.get("inputs", -1))
    if input_count != 6:
        errors.append(f"expected 6 inputs, got {input_count}")
    assignments = 1 << max(input_count, 0)

    expected_names = [
        name
        for bit in range(6)
        for name in (f"x{bit}", f"not_x{bit}")
    ] + ["const0", "const1"]
    source_names = [str(name) for name in payload.get("source_names", [])]
    if source_names != expected_names:
        errors.append("source_names do not match the independent V-cone convention")

    gates = list(payload.get("gates", []))
    declared_slots = int(payload.get("slots", -1))
    if declared_slots != len(gates):
        errors.append(f"declared slots {declared_slots} != gate records {len(gates)}")

    source_count = len(expected_names)
    values_by_case: list[list[bool]] = []
    depths = [0] * source_count
    actual_levels: list[int] = []
    used_sources: set[int] = set()

    for case in range(assignments):
        values = [
            value
            for bit in range(6)
            for value in (bool((case >> bit) & 1), not bool((case >> bit) & 1))
        ] + [False, True]
        values_by_case.append(values)

    for expected_slot, raw_gate in enumerate(gates):
        gate = dict(raw_gate)
        slot = int(gate.get("slot", -1))
        source = int(gate.get("source", -1))
        kind = str(gate.get("kind", ""))
        left = int(gate.get("left", -1))
        right = int(gate.get("right", -1))
        declared_level = int(gate.get("level", -1))
        expected_source = source_count + expected_slot

        if slot != expected_slot:
            errors.append(f"gate {expected_slot}: slot is {slot}")
        if source != expected_source:
            errors.append(f"gate {expected_slot}: source is {source}, expected {expected_source}")
        if kind not in SUPPORTED_KINDS:
            errors.append(f"gate {expected_slot}: unsupported kind {kind}")
            continue
        if not (0 <= left < expected_source):
            errors.append(f"gate {expected_slot}: non-topological left source {left}")
            continue
        if not (0 <= right < expected_source):
            errors.append(f"gate {expected_slot}: non-topological right source {right}")
            continue

        used_sources.add(left)
        if kind != "NOT":
            used_sources.add(right)
        actual_level = depths[left] + 1 if kind == "NOT" else max(depths[left], depths[right]) + 1
        actual_levels.append(actual_level)
        depths.append(actual_level)
        if declared_level != actual_level:
            errors.append(
                f"gate {expected_slot}: declared level {declared_level} != replay depth {actual_level}"
            )

        for values in values_by_case:
            values.append(apply_gate(kind, values[left], values[right]))

    outputs = [int(source) for source in payload.get("outputs", [])]
    if len(outputs) != len(EXPECTED_SUPPORTS):
        errors.append(f"expected 2 outputs, got {len(outputs)}")

    replay_targets: list[int] = []
    expected_targets: list[int] = []
    output_depths: list[int] = []
    row_mismatches: list[dict[str, object]] = []
    for output_index, support in enumerate(EXPECTED_SUPPORTS):
        expected_rows = [
            bool(sum((case >> bit) & 1 for bit in support) & 1)
            for case in range(assignments)
        ]
        expected_targets.append(pack_rows(expected_rows))
        if output_index >= len(outputs):
            continue
        output = outputs[output_index]
        if not (0 <= output < source_count + len(gates)):
            errors.append(f"output {output_index}: invalid source {output}")
            continue
        used_sources.add(output)
        replay_rows = [values[output] for values in values_by_case]
        replay_targets.append(pack_rows(replay_rows))
        output_depths.append(depths[output])
        for case, (actual, expected) in enumerate(zip(replay_rows, expected_rows, strict=True)):
            if actual != expected:
                row_mismatches.append(
                    {
                        "output": output_index,
                        "case": case,
                        "actual": int(actual),
                        "expected": int(expected),
                    }
                )

    declared_target_strings = [str(value).lower() for value in payload.get("targets_hex", [])]
    expected_target_strings = [f"{value:016x}" for value in expected_targets]
    if declared_target_strings != expected_target_strings:
        errors.append("declared targets_hex do not match independently derived parity targets")

    unused_gates = [source for source in range(source_count, source_count + len(gates)) if source not in used_sources]
    if unused_gates:
        errors.append(f"unused paid gate sources: {unused_gates}")

    replay_depth = max(output_depths, default=-1)
    declared_max_delay = int(payload.get("max_delay", -1))
    if replay_depth > declared_max_delay:
        errors.append(f"replay depth {replay_depth} exceeds max_delay {declared_max_delay}")

    return {
        "schema": 1,
        "valid": not errors and not row_mismatches,
        "independent_from_encoder": True,
        "assignments_replayed": assignments,
        "gate_count": len(gates),
        "gate_cost": len(gates),
        "actual_gate_levels": actual_levels,
        "output_depths": output_depths,
        "maximum_output_depth": replay_depth,
        "expected_targets_hex": expected_target_strings,
        "replayed_targets_hex": [f"{value:016x}" for value in replay_targets],
        "unused_gate_sources": unused_gates,
        "row_mismatches": row_mismatches,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = verify(payload)
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
