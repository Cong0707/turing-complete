#!/usr/bin/env python3
"""Generate and verify sparse-care RNG synthesis experiments.

The live level tests 256 fixed seeds.  This script models the existing gated
seed/state protocol and emits an incompletely specified PLA over 64 inputs:

* load:   (seed, q=0), feedback=T(seed), visible output is don't-care
* steady: (seed=0, q=T(A^k(seed))), k=0..64

At steady k<64 both feedback and visible output are cared for; at k=64 only
the visible output is cared for.  Every other 64-bit input is a don't-care.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / ".research" / "rng_test_specialization"))

from src.tc_save_lab.rng_encoded_asic import (  # noqa: E402
    B,
    C,
    FIRST_SEED_LABELS,
    GATES,
    T,
    apply_matrix,
)
from verify_rng_contract import initial_seed, xorshift32  # noqa: E402


WORD_BITS = 32
INPUT_BITS = 64
OUTPUT_BITS = 64
WORD_MASK = (1 << WORD_BITS) - 1


@dataclass(frozen=True)
class CarePoint:
    input_value: int
    expected: int
    cared: int
    phase: str
    test_id: int
    offset: int


def bit_string(value: int, width: int) -> str:
    """Return bits in PLA variable order: bit 0 first."""

    return "".join("1" if value >> bit & 1 else "0" for bit in range(width))


def output_string(point: CarePoint, outputs: Sequence[int]) -> str:
    chars: list[str] = []
    for output in outputs:
        if not (point.cared >> output) & 1:
            chars.append("-")
        else:
            chars.append("1" if (point.expected >> output) & 1 else "0")
    return "".join(chars)


def build_points() -> tuple[CarePoint, ...]:
    points: list[CarePoint] = []
    all_feedback = WORD_MASK
    all_visible = WORD_MASK << WORD_BITS
    for test_id in range(256):
        seed = initial_seed(test_id)
        points.append(
            CarePoint(
                input_value=seed,
                expected=apply_matrix(T, seed),
                cared=all_feedback,
                phase="load",
                test_id=test_id,
                offset=-1,
            )
        )
        natural = seed
        for offset in range(65):
            q = apply_matrix(T, natural)
            successor = xorshift32(natural)
            feedback = apply_matrix(T, successor)
            cared = all_visible | (all_feedback if offset < 64 else 0)
            expected = (successor << WORD_BITS) | feedback
            points.append(
                CarePoint(
                    input_value=q << WORD_BITS,
                    expected=expected,
                    cared=cared,
                    phase="steady",
                    test_id=test_id,
                    offset=offset,
                )
            )
            natural = successor

    by_input: dict[int, CarePoint] = {}
    for point in points:
        previous = by_input.setdefault(point.input_value, point)
        if previous != point:
            overlap = previous.cared & point.cared
            if (previous.expected ^ point.expected) & overlap:
                raise AssertionError("contradictory care points")
            raise AssertionError("unexpected duplicate input care point")
    if len(points) != 256 * 66 or len(by_input) != len(points):
        raise AssertionError("care point count changed")
    return tuple(points)


def output_indices(group: str) -> tuple[int, ...]:
    if group == "all":
        return tuple(range(OUTPUT_BITS))
    if group == "feedback":
        return tuple(range(WORD_BITS))
    if group == "visible":
        return tuple(range(WORD_BITS, OUTPUT_BITS))
    match = re.fullmatch(r"(?:f|feedback)(\d+)", group)
    if match:
        bit = int(match.group(1))
        if 0 <= bit < WORD_BITS:
            return (bit,)
    match = re.fullmatch(r"(?:v|visible)(\d+)", group)
    if match:
        bit = int(match.group(1))
        if 0 <= bit < WORD_BITS:
            return (WORD_BITS + bit,)
    raise ValueError(f"unknown output group: {group}")


def output_name(index: int) -> str:
    return f"f{index}" if index < WORD_BITS else f"v{index - WORD_BITS}"


def emit_pla(path: Path, points: Sequence[CarePoint], group: str) -> dict[str, int]:
    outputs = output_indices(group)
    lines = [
        f".i {INPUT_BITS}",
        f".o {len(outputs)}",
        ".ilb " + " ".join([*(f"s{i}" for i in range(32)), *(f"q{i}" for i in range(32))]),
        ".ob " + " ".join(output_name(output) for output in outputs),
        ".type fr",
    ]
    emitted = 0
    for point in points:
        result = output_string(point, outputs)
        if set(result) == {"-"}:
            continue
        lines.append(f"{bit_string(point.input_value, INPUT_BITS)} {result}")
        emitted += 1
    lines.append(".e")
    path.write_text("\n".join(lines) + "\n", encoding="ascii")
    return {"rows": emitted, "outputs": len(outputs)}


def emit_care_blif(path: Path, points: Sequence[CarePoint]) -> dict[str, int]:
    inputs = [*(f"s{i}" for i in range(32)), *(f"q{i}" for i in range(32))]
    lines = [
        ".model rng_exact_sample_care",
        ".inputs " + " ".join(inputs),
        ".outputs care",
        ".names " + " ".join(inputs) + " care",
    ]
    lines.extend(f"{bit_string(point.input_value, INPUT_BITS)} 1" for point in points)
    lines.append(".end")
    path.write_text("\n".join(lines) + "\n", encoding="ascii")
    return {"rows": len(points), "outputs": 1}


@dataclass(frozen=True)
class Pla:
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    cubes: tuple[tuple[str, str], ...]


def parse_pla(path: Path) -> Pla:
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    cubes: list[tuple[str, str]] = []
    for raw in path.read_text(encoding="ascii", errors="strict").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(".ilb "):
            inputs = tuple(line.split()[1:])
        elif line.startswith(".ob "):
            outputs = tuple(line.split()[1:])
        elif line.startswith("."):
            continue
        else:
            fields = line.split()
            if len(fields) != 2:
                raise ValueError(f"unsupported PLA row: {line}")
            cubes.append((fields[0], fields[1]))
    if len(inputs) != INPUT_BITS:
        raise ValueError(f"PLA has {len(inputs)} named inputs, expected {INPUT_BITS}")
    if not outputs:
        raise ValueError("PLA has no named outputs")
    return Pla(inputs, outputs, tuple(cubes))


def expected_for_name(point: CarePoint, name: str) -> tuple[bool, bool]:
    match = re.fullmatch(r"([fv])(\d+)", name)
    if match is None:
        raise ValueError(f"unknown output name: {name}")
    index = int(match.group(2)) + (0 if match.group(1) == "f" else WORD_BITS)
    return bool(point.expected >> index & 1), bool(point.cared >> index & 1)


def point_bitsets(points: Sequence[CarePoint]) -> tuple[tuple[int, int], ...]:
    all_points = (1 << len(points)) - 1
    result: list[tuple[int, int]] = []
    for variable in range(INPUT_BITS):
        ones = sum(1 << index for index, point in enumerate(points) if point.input_value >> variable & 1)
        result.append((all_points ^ ones, ones))
    return tuple(result)


def verify_pla(path: Path, points: Sequence[CarePoint]) -> dict[str, object]:
    pla = parse_pla(path)
    all_points = (1 << len(points)) - 1
    literals = point_bitsets(points)
    required_one: list[int] = []
    required_zero: list[int] = []
    for name in pla.outputs:
        ones = 0
        zeros = 0
        for index, point in enumerate(points):
            expected, cared = expected_for_name(point, name)
            if cared:
                if expected:
                    ones |= 1 << index
                else:
                    zeros |= 1 << index
        required_one.append(ones)
        required_zero.append(zeros)

    covered = [0] * len(pla.outputs)
    literal_count = 0
    for input_pattern, output_pattern in pla.cubes:
        if len(input_pattern) != INPUT_BITS or len(output_pattern) != len(pla.outputs):
            raise AssertionError("PLA cube width mismatch")
        matched = all_points
        for variable, value in enumerate(input_pattern):
            if value in "01":
                literal_count += 1
                matched &= literals[variable][int(value)]
        for output, value in enumerate(output_pattern):
            if value == "1":
                if matched & required_zero[output]:
                    raise AssertionError(f"cube covers cared zero for {pla.outputs[output]}")
                covered[output] |= matched

    for output, name in enumerate(pla.outputs):
        missing = required_one[output] & ~covered[output]
        if missing:
            raise AssertionError(f"PLA misses {missing.bit_count()} cared ones for {name}")
    return {
        "path": str(path),
        "outputs": len(pla.outputs),
        "cubes": len(pla.cubes),
        "input_literals": literal_count,
        "verified_points": len(points),
    }


def logical_blif_lines(path: Path) -> tuple[str, ...]:
    result: list[str] = []
    pending = ""
    for raw in path.read_text(encoding="ascii", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if pending:
            line = pending + " " + line
            pending = ""
        if line.endswith("\\"):
            pending = line[:-1].rstrip()
        else:
            result.append(line)
    if pending:
        result.append(pending)
    return tuple(result)


def verify_mapped_blif(path: Path, points: Sequence[CarePoint]) -> dict[str, object]:
    lines = logical_blif_lines(path)
    all_points = (1 << len(points)) - 1
    values: dict[str, int] = {}
    input_names: tuple[str, ...] = ()
    output_names: tuple[str, ...] = ()
    gates: Counter[str] = Counter()
    unmapped_names = 0

    index = 0
    while index < len(lines):
        line = lines[index]
        fields = line.split()
        if fields[0] == ".inputs":
            input_names = tuple(fields[1:])
            for name in input_names:
                match = re.fullmatch(r"([sq])(\d+)", name)
                if match is None:
                    raise ValueError(f"unknown BLIF input {name}")
                bit = int(match.group(2)) + (0 if match.group(1) == "s" else WORD_BITS)
                values[name] = sum(
                    1 << point_index
                    for point_index, point in enumerate(points)
                    if point.input_value >> bit & 1
                )
        elif fields[0] == ".outputs":
            output_names = tuple(fields[1:])
        elif fields[0] == ".gate":
            gate = fields[1]
            pins = dict(field.split("=", 1) for field in fields[2:])
            output = pins["Y"]
            a = values[pins["A"]]
            b = values[pins["B"]] if "B" in pins else 0
            if gate == "BUF":
                result = a
            elif gate == "NOT":
                result = all_points ^ a
            elif gate == "AND":
                result = a & b
            elif gate == "OR":
                result = a | b
            elif gate == "NAND":
                result = all_points ^ (a & b)
            elif gate == "NOR":
                result = all_points ^ (a | b)
            elif gate == "XOR":
                result = a ^ b
            elif gate == "XNOR":
                result = all_points ^ (a ^ b)
            elif gate == "$__ZERO":
                result = 0
            elif gate == "$__ONE":
                result = all_points
            else:
                raise ValueError(f"unsupported mapped gate {gate}")
            values[output] = result
            gates[gate] += 1
        elif fields[0] == ".names":
            fanins = fields[1:-1]
            output = fields[-1]
            result = 0
            index += 1
            while index < len(lines) and not lines[index].startswith("."):
                cube = lines[index].split()
                if fanins:
                    pattern, output_value = cube
                    matched = all_points
                    for fanin, value in zip(fanins, pattern):
                        if value == "1":
                            matched &= values[fanin]
                        elif value == "0":
                            matched &= all_points ^ values[fanin]
                    if output_value == "1":
                        result |= matched
                elif cube == ["1"]:
                    result = all_points
                index += 1
            values[output] = result
            if len(fanins) > 1:
                unmapped_names += 1
            continue
        index += 1

    if not input_names or not output_names:
        raise ValueError("BLIF lacks inputs or outputs")
    mismatches: dict[str, int] = {}
    for name in output_names:
        actual = values[name]
        count = 0
        for point_index, point in enumerate(points):
            expected, cared = expected_for_name(point, name)
            if cared and bool(actual >> point_index & 1) != expected:
                count += 1
        if count:
            mismatches[name] = count
    if mismatches:
        raise AssertionError(f"mapped BLIF care mismatches: {mismatches}")

    costs = {"BUF": 0, "$__ZERO": 0, "$__ONE": 0, "NOT": 1, "AND": 1,
             "OR": 1, "NAND": 1, "NOR": 1, "XOR": 3, "XNOR": 3}
    weighted = sum(costs[gate] * count for gate, count in gates.items())
    return {
        "path": str(path),
        "outputs": len(output_names),
        "verified_points": len(points),
        "gate_counts": dict(sorted(gates.items())),
        "weighted_logic_cost": weighted,
        "unmapped_names": unmapped_names,
    }


def generate(points: Sequence[CarePoint]) -> dict[str, object]:
    files: dict[str, object] = {}
    for group in ("all", "feedback", "visible"):
        path = HERE / f"rng_care_{group}.pla"
        files[group] = {"path": str(path), **emit_pla(path, points, group)}
    for bit in range(WORD_BITS):
        for prefix in ("f", "v"):
            group = f"{prefix}{bit}"
            path = HERE / "single" / f"rng_care_{group}.pla"
            path.parent.mkdir(parents=True, exist_ok=True)
            emit_pla(path, points, group)
    care_path = HERE / "rng_exact_sample_care.blif"
    files["care"] = {"path": str(care_path), **emit_care_blif(care_path, points)}
    return files


def point_summary(points: Sequence[CarePoint]) -> dict[str, object]:
    return {
        "points": len(points),
        "unique_inputs": len({point.input_value for point in points}),
        "load_points": sum(point.phase == "load" for point in points),
        "steady_points": sum(point.phase == "steady" for point in points),
        "feedback_cared_points": sum(bool(point.cared & WORD_MASK) for point in points),
        "visible_cared_points": sum(bool(point.cared >> WORD_BITS) for point in points),
    }


def projection_patterns(values: Sequence[int], row: int) -> int:
    support = tuple(bit for bit in range(WORD_BITS) if row >> bit & 1)
    patterns = {
        sum(((value >> bit) & 1) << position for position, bit in enumerate(support))
        for value in values
    }
    return len(patterns)


def audit_projections(points: Sequence[CarePoint]) -> dict[str, object]:
    steady = tuple(point.input_value >> WORD_BITS for point in points if point.phase == "steady")
    load = tuple(point.input_value & WORD_MASK for point in points if point.phase == "load")
    q_rows = set(B) | set(C) | {gate.output for gate in GATES}
    seed_rows = set(T) | set(FIRST_SEED_LABELS.values())

    def summarize(values: Sequence[int], rows: Iterable[int]) -> dict[str, object]:
        records = []
        for row in sorted(set(rows)):
            weight = row.bit_count()
            observed = projection_patterns(values, row)
            records.append((weight, observed, 1 << weight, row))
        by_weight: dict[str, dict[str, int]] = {}
        for weight in sorted({record[0] for record in records}):
            group = [record for record in records if record[0] == weight]
            by_weight[str(weight)] = {
                "rows": len(group),
                "full_rows": sum(observed == possible for _, observed, possible, _ in group),
                "minimum_patterns": min(observed for _, observed, _, _ in group),
                "maximum_patterns": max(observed for _, observed, _, _ in group),
                "possible_patterns": 1 << weight,
            }
        return {
            "rows": len(records),
            "all_full": all(observed == possible for _, observed, possible, _ in records),
            "by_weight": by_weight,
            "nonfull_rows": [
                f"{row:08x}" for _, observed, possible, row in records if observed != possible
            ],
        }

    return {
        "steady_q_target_supports": summarize(steady, q_rows),
        "load_seed_target_supports": summarize(load, seed_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=("generate", "verify-pla", "verify-blif", "audit-projections")
    )
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    points = build_points()
    result: dict[str, object] = {"care": point_summary(points)}
    if args.command == "generate":
        result["generated"] = generate(points)
    elif args.command == "verify-pla":
        if args.path is None:
            parser.error("verify-pla requires a path")
        result["pla"] = verify_pla(args.path, points)
    elif args.command == "verify-blif":
        if args.path is None:
            parser.error("verify-blif requires a path")
        result["blif"] = verify_mapped_blif(args.path, points)
    else:
        result["projections"] = audit_projections(points)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
