#!/usr/bin/env python3
"""Audit cheap nonlinear resubstitutions on the fixed RNG live care set.

The audit is deliberately narrower than arbitrary sequential synthesis.  It
keeps the checked 61-XOR/47-OR DAG topology and asks whether any XOR node can
be replaced by a wire, inverter, or one cheap two-input Boolean gate while
preserving that node on every combinational point reached by the 256 tests.
An equality at the replaced node is sufficient for every downstream use.

No save files or game processes are accessed.
"""

from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = ROOT / "src"
for path in (ROOT, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tc_save_lab.rng_encoded_asic import T, apply_matrix, xorshift32  # noqa: E402


def _load_joint_builder():
    path = ROOT / ".research" / "rng_joint_boolean" / "generate_joint.py"
    spec = importlib.util.spec_from_file_location("rng_joint_generate", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_full_extension


build_full_extension = _load_joint_builder()


MASK64 = (1 << 64) - 1
SCRIPT_RANDOM_MODULUS = 0xFFFFFFFE
XORSHIFT64_STAR_MULTIPLIER = 0x2545F4914F6CDD1


def xorshift64_star(value: int) -> int:
    value &= MASK64
    value ^= (value << 12) & MASK64
    value ^= value >> 25
    value ^= value >> 27
    return (value * XORSHIFT64_STAR_MULTIPLIER) & MASK64


def initial_seed(test_id: int) -> int:
    return 1 + xorshift64_star(test_id + 1) % SCRIPT_RANDOM_MODULUS


def legal_points() -> list[tuple[int, int, str]]:
    """Return load points followed by 65 enabled-output states per test.

    The encoded implementation stores q=T*x.  At load, q is the mandated
    all-zero initial state and the architecture seed pins carry ``seed``.
    During output ticks the input is disabled (logic-zero at the mode gates),
    while q successively encodes seed, A*seed, ..., A^64*seed.
    """

    result: list[tuple[int, int, str]] = []
    seeds = [initial_seed(test_id) for test_id in range(256)]
    result.extend((seed, 0, "load") for seed in seeds)
    for test_id, seed in enumerate(seeds):
        value = seed
        for tick in range(65):
            result.append((0, apply_matrix(T, value), f"steady:{test_id}:{tick}"))
            value = xorshift32(value)
    return result


def signatures(points: list[tuple[int, int, str]]) -> tuple[dict[str, int], list[dict[str, object]]]:
    gates, _, _ = build_full_extension()
    values: dict[str, int] = {}
    for bit in range(32):
        values[f"s{bit}"] = sum(((seed >> bit) & 1) << index for index, (seed, _, _) in enumerate(points))
        values[f"q{bit}"] = sum(((state >> bit) & 1) << index for index, (_, state, _) in enumerate(points))

    records: list[dict[str, object]] = []
    for index, (kind, output, left, right) in enumerate(gates):
        a, b = values[left], values[right]
        values[output] = a | b if kind == "OR" else a ^ b
        records.append(
            {
                "index": index,
                "kind": kind,
                "output": output,
                "left": left,
                "right": right,
            }
        )
    return values, records


def audit() -> dict[str, object]:
    points = legal_points()
    all_mask = (1 << len(points)) - 1
    values, records = signatures(points)
    available = [*(f"s{i}" for i in range(32)), *(f"q{i}" for i in range(32))]
    replacements: list[dict[str, object]] = []
    per_xor: list[dict[str, object]] = []

    for record in records:
        output = str(record["output"])
        target = values[output]
        found: list[dict[str, object]] = []

        for name in available:
            if values[name] == target:
                found.append({"kind": "WIRE", "inputs": [name], "cost": 0})
            if ((~values[name]) & all_mask) == target:
                found.append({"kind": "NOT", "inputs": [name], "cost": 1})

        # Necessary subset/superset filters make the exact pair audit small.
        subsets_target = [name for name in available if values[name] & ~target == 0]
        supersets_target = [name for name in available if target & ~values[name] == 0]
        complement = target ^ all_mask
        subsets_complement = [name for name in available if values[name] & ~complement == 0]
        supersets_complement = [name for name in available if complement & ~values[name] == 0]

        def pair_matches(names: list[str], operation: str, wanted: int) -> None:
            for left_index, left in enumerate(names):
                a = values[left]
                for right in names[left_index:]:
                    b = values[right]
                    actual = a | b if operation == "OR" else a & b
                    if actual == wanted:
                        kind = operation
                        if wanted == complement:
                            kind = "NOR" if operation == "OR" else "NAND"
                        found.append({"kind": kind, "inputs": [left, right], "cost": 1})

        pair_matches(subsets_target, "OR", target)
        pair_matches(supersets_target, "AND", target)
        pair_matches(subsets_complement, "OR", complement)
        pair_matches(supersets_complement, "AND", complement)

        # Remove expression duplicates while retaining concrete witnesses.
        unique: dict[str, dict[str, object]] = {}
        for item in found:
            key = json.dumps(item, sort_keys=True)
            unique[key] = item
        found = list(unique.values())

        if record["kind"] == "XOR":
            entry = {
                **record,
                "left_and_right_one_count": (values[str(record["left"])] & values[str(record["right"])]).bit_count(),
                "replacement_count": len(found),
                "replacements": found[:32],
            }
            per_xor.append(entry)
            if found:
                replacements.append(entry)
        available.append(output)

    mode_counts = Counter(label.split(":", 1)[0] for _, _, label in points)
    return {
        "schema": 1,
        "scope": "fixed-DAG node-preserving one-cheap-gate restricted-care resubstitution",
        "care_points": len(points),
        "care_modes": dict(mode_counts),
        "unique_input_pairs": len({(seed, state) for seed, state, _ in points}),
        "gate_counts": dict(Counter(str(record["kind"]) for record in records)),
        "xor_nodes_audited": len(per_xor),
        "replaceable_xor_nodes": len(replacements),
        "maximum_direct_saving": sum(3 - min(int(rep["cost"]) for rep in entry["replacements"]) for entry in replacements),
        "replacements": replacements,
        "xor_input_overlap": {
            "minimum": min(int(entry["left_and_right_one_count"]) for entry in per_xor),
            "maximum": max(int(entry["left_and_right_one_count"]) for entry in per_xor),
            "zero_count": sum(int(entry["left_and_right_one_count"]) == 0 for entry in per_xor),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "restricted_resub_certificate.json")
    args = parser.parse_args()
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
