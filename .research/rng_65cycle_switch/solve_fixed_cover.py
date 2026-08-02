"""Solve the 65/66-cycle RNG common-word-bus phase-label problem.

This is an offline algebraic model.  It never imports save-writing code,
starts the game, or reads the live save.  A fixed shared depth-two XOR cover
For the 65-cycle contract, the cover must satisfy both labels on the first
visible tick:

    output   = A * seed
    feedback = T * A * seed

The 66-cycle legacy contract instead requires only ``B-load=T``.  In steady
state the same physical signals retain C*q and B*q semantics.
One U32 Word Switch gives occurrence-local raw q inputs either label zero or
one seed unit.  Additional Bit Switch nets are counted by distinct
``(seed, steady_node)`` pairs and may fan out.

All XOR nodes are per-bit XOR2 gates charged at 3 gate / 2 delay.  Word
packaging never changes that linear per-lane cost.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any, Iterable, Sequence


BITS = 32
MASK = (1 << BITS) - 1
FIXED_SHELL_GATE = 160 + 6 + 64
TARGET_GATE = 437
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    rows = [0] * BITS
    for source in range(BITS):
        value = function(1 << source)
        for output in range(BITS):
            if value >> output & 1:
                rows[output] |= 1 << source
    return tuple(rows)


A = matrix_from_function(xorshift32)


def bits(value: int) -> tuple[int, ...]:
    return tuple(index for index in range(BITS) if value >> index & 1)


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << index for index, row in enumerate(matrix))


def matrix(record: dict[str, Any], name: str) -> tuple[int, ...]:
    values = record[name]
    if len(values) != BITS:
        raise ValueError(f"{name} must have 32 rows")
    return tuple(int(str(value), 16) for value in values)


def read_records(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(value, list):
        return value
    if "certificate" in value and all(key in value["certificate"] for key in ("T", "B", "C")):
        return [value["certificate"]]
    if "best_candidate" in value:
        return [value["best_candidate"]]
    return [value]


def pair_partitions(row: int) -> tuple[tuple[int, ...], ...]:
    support = tuple(1 << bit for bit in bits(row))
    if len(support) == 3:
        return tuple((row ^ unit,) for unit in support)
    if len(support) == 4:
        a, b, c, d = support
        return (
            tuple(sorted((a | b, c | d))),
            tuple(sorted((a | c, b | d))),
            tuple(sorted((a | d, b | c))),
        )
    raise ValueError(f"row {row:08x} has weight {len(support)}")


@dataclass(frozen=True)
class Cover:
    pairs: tuple[int, ...]
    finals: tuple[int, ...]
    decompositions: dict[int, tuple[int, ...]]

    @property
    def xor_count(self) -> int:
        return len(self.pairs) + len(self.finals)


def greedy_cover(rows: Iterable[int]) -> Cover:
    targets = frozenset(rows)
    if 0 in targets or any(row.bit_count() > 4 for row in targets):
        raise ValueError("target set is not depth-two realizable")
    required = {row for row in targets if row.bit_count() == 2}
    finals = {row for row in targets if row.bit_count() in (3, 4)}
    selected = set(required)

    def satisfied(row: int, pairs: set[int]) -> bool:
        return any(set(option) <= pairs for option in pair_partitions(row))

    while True:
        unmet = [row for row in finals if not satisfied(row, selected)]
        if not unmet:
            break
        actions = {
            frozenset(option) - selected
            for row in unmet
            for option in pair_partitions(row)
        }
        actions.discard(frozenset())

        def key(action: frozenset[int]):
            gain = sum(satisfied(row, selected | set(action)) for row in unmet)
            return (gain / len(action), gain, -len(action), tuple(-item for item in sorted(action)))

        selected.update(max(actions, key=key))

    changed = True
    while changed:
        changed = False
        for pair in sorted(selected - required, reverse=True):
            candidate = selected - {pair}
            if all(satisfied(row, candidate) for row in finals):
                selected = candidate
                changed = True

    decompositions = {
        row: next(option for option in pair_partitions(row) if set(option) <= selected)
        for row in finals
    }
    return Cover(tuple(sorted(selected)), tuple(sorted(finals)), decompositions)


def cover_from_record(record: dict[str, Any], B: Sequence[int], C: Sequence[int]) -> Cover:
    if "selected_pair_gates" not in record or "decompositions" not in record:
        return greedy_cover((*B, *C))
    pairs = tuple(sorted(int(str(value), 16) for value in record["selected_pair_gates"]))
    finals = tuple(sorted(row for row in frozenset((*B, *C)) if row.bit_count() in (3, 4)))
    raw = record["decompositions"]
    decompositions = {
        row: tuple(int(str(value), 16) for value in raw[f"{row:08x}"])
        for row in finals
    }
    return Cover(pairs, finals, decompositions)


def validate_cover(cover: Cover, B: Sequence[int], C: Sequence[int]) -> None:
    pairs = set(cover.pairs)
    targets = frozenset((*B, *C))
    for target in targets:
        weight = target.bit_count()
        if weight == 1:
            continue
        if weight == 2:
            if target not in pairs:
                raise AssertionError(f"missing pair target {target:08x}")
            continue
        if weight not in (3, 4):
            raise AssertionError(f"invalid target weight {weight}")
        inputs = cover.decompositions[target]
        if not set(inputs) <= pairs:
            raise AssertionError(f"missing decomposition input for {target:08x}")
        actual = inputs[0] ^ (target ^ inputs[0]) if len(inputs) == 1 else inputs[0] ^ inputs[1]
        if actual != target:
            raise AssertionError(f"bad decomposition for {target:08x}")


def switch_budget(xor_count: int) -> int:
    return (TARGET_GATE - (FIXED_SHELL_GATE + 3 * xor_count)) // 2


def solve_record(
    record: dict[str, Any],
    *,
    max_switches: int | None,
    timeout_ms: int,
    contract: str = "65",
    bijective_mapping: bool = False,
) -> dict[str, Any]:
    try:
        import z3
    except ImportError as error:  # pragma: no cover
        raise SystemExit("install z3-solver in the project venv") from error

    started = time.perf_counter()
    T = matrix(record, "T")
    B = matrix(record, "B")
    C = matrix(record, "C")
    if compose(C, T) != A or compose(T, C) != B:
        raise ValueError("matrix identities C*T=A or T*C=B failed")
    TA = compose(T, A)
    cycle_count = 65 if contract == "65" else 66
    cover = cover_from_record(record, B, C)
    validate_cover(cover, B, C)
    allowed_switches = switch_budget(cover.xor_count) if max_switches is None else max_switches
    if allowed_switches < 0:
        return {
            "status": "cost_rejected",
            "xor_count": cover.xor_count,
            "max_bit_switches": allowed_switches,
        }

    solver = z3.Solver()
    solver.set(timeout=timeout_ms, max_memory=650)

    mapping = {
        (seed, state): z3.Bool(f"map_s{seed:02d}_q{state:02d}")
        for seed in range(BITS)
        for state in range(BITS)
    }
    for seed in range(BITS):
        solver.add(z3.PbEq([(mapping[seed, state], 1) for state in range(BITS)], 1))
    if bijective_mapping:
        for state in range(BITS):
            solver.add(z3.PbEq([(mapping[seed, state], 1) for seed in range(BITS)], 1))

    mode_choices: dict[tuple[str, int], tuple[Any, ...]] = {}

    def raw_label(tag: str, state: int) -> tuple[Any, ...]:
        key = (tag, state)
        if key in mode_choices:
            return mode_choices[key]
        choices = tuple(z3.Bool(f"mode_{tag}_q{state:02d}_s{seed:02d}") for seed in range(BITS))
        solver.add(z3.AtMost(*choices, 1))
        for seed, choice in enumerate(choices):
            solver.add(z3.Implies(choice, mapping[seed, state]))
        mode_choices[key] = choices
        return choices

    pair_labels: dict[int, tuple[Any, ...]] = {}
    for pair in cover.pairs:
        left_state, right_state = bits(pair)
        left = raw_label(f"p{pair:08x}l", left_state)
        right = raw_label(f"p{pair:08x}r", right_state)
        pair_labels[pair] = tuple(z3.Xor(left[seed], right[seed]) for seed in range(BITS))

    late_users: dict[tuple[int, int], list[Any]] = defaultdict(list)
    late_occurrences: dict[tuple[str, int], tuple[Any, ...]] = {}

    def canonical(node: int, tag: str) -> tuple[Any, ...]:
        if node in pair_labels:
            return pair_labels[node]
        if node.bit_count() == 1:
            return raw_label(tag, bits(node)[0])
        raise AssertionError(f"unexpected node {node:08x}")

    def selectable(node: int, tag: str) -> tuple[Any, ...]:
        base = canonical(node, tag)
        choices = tuple(z3.Bool(f"late_{tag}_{node:08x}_s{seed:02d}") for seed in range(BITS))
        solver.add(z3.AtMost(*choices, 1))
        base_zero = z3.And(*(z3.Not(value) for value in base))
        for seed, choice in enumerate(choices):
            solver.add(z3.Implies(choice, base_zero))
            late_users[seed, node].append(choice)
        late_occurrences[tag, node] = choices
        return tuple(z3.Xor(base[seed], choices[seed]) for seed in range(BITS))

    signal_labels: dict[int, tuple[Any, ...]] = dict(pair_labels)
    for target in cover.finals:
        inputs = cover.decompositions[target]
        if len(inputs) == 1:
            pair = inputs[0]
            direct = target ^ pair
            left = selectable(pair, f"g{target:08x}l")
            right = selectable(direct, f"g{target:08x}r")
        else:
            left = selectable(inputs[0], f"g{target:08x}l")
            right = selectable(inputs[1], f"g{target:08x}r")
        signal_labels[target] = tuple(z3.Xor(left[seed], right[seed]) for seed in range(BITS))

    final_choices: dict[tuple[str, int], tuple[Any, ...]] = {}

    def constrain_outputs(prefix: str, steady_rows: Sequence[int], wanted_rows: Sequence[int]) -> None:
        for output, (steady, wanted) in enumerate(zip(steady_rows, wanted_rows, strict=True)):
            if steady in signal_labels:
                base = signal_labels[steady]
            elif steady.bit_count() == 1:
                base = raw_label(f"{prefix}{output:02d}", bits(steady)[0])
            else:
                raise AssertionError(f"missing signal {steady:08x}")
            tag = f"{prefix}{output:02d}"
            choices = tuple(z3.Bool(f"final_{tag}_s{seed:02d}") for seed in range(BITS))
            solver.add(z3.AtMost(*choices, 1))
            base_zero = z3.And(*(z3.Not(value) for value in base))
            for seed, choice in enumerate(choices):
                solver.add(z3.Implies(choice, base_zero))
                late_users[seed, steady].append(choice)
                solver.add(z3.Xor(base[seed], choice) == bool(wanted >> seed & 1))
            final_choices[prefix, output] = choices

    if contract == "65":
        constrain_outputs("b", B, TA)
        constrain_outputs("c", C, A)
    elif contract == "old-feedback":
        constrain_outputs("b", B, T)
    else:
        raise ValueError(f"unknown contract {contract}")

    late_used = {
        pair: z3.Bool(f"used_s{pair[0]:02d}_{pair[1]:08x}")
        for pair in sorted(late_users)
    }
    for pair, users in late_users.items():
        solver.add(late_used[pair] == z3.Or(*users))
    solver.add(z3.PbLe([(variable, 1) for variable in late_used.values()], allowed_switches))

    result = solver.check()
    payload: dict[str, Any] = {
        "schema": 1,
        "model": (
            "65-cycle common-U32 Switch; load C=A and B=T*A"
            if contract == "65"
            else "positive control: old feedback-only load B=T"
        ),
        "contract": contract,
        "bijective_word_lane_mapping": bijective_mapping,
        "status": str(result),
        "timeout_ms": timeout_ms,
        "xor_count": cover.xor_count,
        "max_bit_switches": allowed_switches,
        "cost_bound": {
            "fixed_shell": FIXED_SHELL_GATE,
            "xor_gate": 3 * cover.xor_count,
            "bit_switch_gate": 2 * allowed_switches,
            "maximum_gate": FIXED_SHELL_GATE + 3 * cover.xor_count + 2 * allowed_switches,
            "delay": 9,
            "cycles": cycle_count,
            "target_gate": TARGET_GATE,
        },
        "T": [f"{row:08x}" for row in T],
        "B": [f"{row:08x}" for row in B],
        "C": [f"{row:08x}" for row in C],
        "TA": [f"{row:08x}" for row in TA],
        "selected_pair_gates": [f"{pair:08x}" for pair in cover.pairs],
        "decompositions": {
            f"{target:08x}": [f"{node:08x}" for node in cover.decompositions[target]]
            for target in cover.finals
        },
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }
    if result != z3.sat:
        if result == z3.unknown:
            payload["reason_unknown"] = solver.reason_unknown()
        return payload

    model = solver.model()

    def enabled(value: Any) -> bool:
        return z3.is_true(model.eval(value, model_completion=True))

    selected_mapping = [
        next(state for state in range(BITS) if enabled(mapping[seed, state]))
        for seed in range(BITS)
    ]
    selected_modes = {
        f"{tag}@q{state}": next(
            (seed for seed, choice in enumerate(choices) if enabled(choice)), None
        )
        for (tag, state), choices in sorted(mode_choices.items())
    }
    selected_late = tuple(pair for pair, variable in late_used.items() if enabled(variable))
    selected_late_occurrences = [
        {"tag": tag, "node": f"{node:08x}", "seed": seed}
        for (tag, node), choices in sorted(late_occurrences.items())
        for seed, choice in enumerate(choices)
        if enabled(choice)
    ]
    selected_final = [
        {"kind": prefix, "output": output, "seed": seed}
        for (prefix, output), choices in sorted(final_choices.items())
        for seed, choice in enumerate(choices)
        if enabled(choice)
    ]

    gate = FIXED_SHELL_GATE + 3 * cover.xor_count + 2 * len(selected_late)
    payload.update(
        {
            "bit_switch_count": len(selected_late),
            "gate": gate,
            "delay": 9,
            "cycles": cycle_count,
            "energy": gate * 9 * cycle_count,
            "word_lane_state_mapping": selected_mapping,
            "mode_occurrences": selected_modes,
            "late_pairs": [
                {"seed": seed, "node": f"{node:08x}"} for seed, node in selected_late
            ],
            "late_occurrences": selected_late_occurrences,
            "final_late_occurrences": selected_final,
        }
    )
    if contract == "65":
        verify_certificate(payload)
        payload["offline_verification"] = "passed: identities, dual labels, and 65 outputs"
    else:
        payload["offline_verification"] = "positive-control SAT extraction only"
    return payload


def verify_certificate(payload: dict[str, Any]) -> None:
    T = matrix(payload, "T")
    B = matrix(payload, "B")
    C = matrix(payload, "C")
    TA = matrix(payload, "TA")
    if compose(C, T) != A or compose(T, C) != B or compose(T, A) != TA:
        raise AssertionError("certificate matrix identity failed")
    pairs = tuple(int(value, 16) for value in payload["selected_pair_gates"])
    decompositions = {
        int(target, 16): tuple(int(node, 16) for node in nodes)
        for target, nodes in payload["decompositions"].items()
    }
    mapping = tuple(int(value) for value in payload["word_lane_state_mapping"])
    modes = {
        key: value for key, value in payload["mode_occurrences"].items() if value is not None
    }
    late_by_tag = {
        (item["tag"], int(item["node"], 16)): int(item["seed"])
        for item in payload["late_occurrences"]
    }
    final_late = {
        (item["kind"], int(item["output"])): int(item["seed"])
        for item in payload["final_late_occurrences"]
    }

    def raw(tag: str, state: int) -> int:
        seed = modes.get(f"{tag}@q{state}")
        if seed is None:
            return 0
        if mapping[int(seed)] != state:
            raise AssertionError("mode occurrence violates word-lane mapping")
        return 1 << int(seed)

    pair_labels: dict[int, int] = {}
    for pair in pairs:
        left, right = bits(pair)
        pair_labels[pair] = raw(f"p{pair:08x}l", left) ^ raw(f"p{pair:08x}r", right)

    def canonical(node: int, tag: str) -> int:
        if node in pair_labels:
            return pair_labels[node]
        return raw(tag, bits(node)[0])

    def selectable(node: int, tag: str) -> int:
        base = canonical(node, tag)
        seed = late_by_tag.get((tag, node))
        if seed is None:
            return base
        if base != 0:
            raise AssertionError("late switch overlays a nonzero load label")
        return 1 << seed

    signals = dict(pair_labels)
    for target in sorted(decompositions):
        inputs = decompositions[target]
        if len(inputs) == 1:
            left_node, right_node = inputs[0], target ^ inputs[0]
        else:
            left_node, right_node = inputs
        signals[target] = selectable(left_node, f"g{target:08x}l") ^ selectable(
            right_node, f"g{target:08x}r"
        )

    def labels(prefix: str, steady_rows: Sequence[int]) -> tuple[int, ...]:
        result = []
        for output, steady in enumerate(steady_rows):
            base = signals.get(steady, raw(f"{prefix}{output:02d}", bits(steady)[0]))
            seed = final_late.get((prefix, output))
            if seed is not None:
                if base != 0:
                    raise AssertionError("final switch overlays a nonzero load label")
                base = 1 << seed
            result.append(base)
        return tuple(result)

    if labels("b", B) != TA:
        raise AssertionError("feedback load labels are not T*A")
    if labels("c", C) != A:
        raise AssertionError("output load labels are not A")

    unique_late = {
        (int(item["seed"]), int(item["node"], 16)) for item in payload["late_pairs"]
    }
    used_late = {
        (int(item["seed"]), int(item["node"], 16)) for item in payload["late_occurrences"]
    }
    for item in payload["final_late_occurrences"]:
        steady = (B if item["kind"] == "b" else C)[int(item["output"])]
        used_late.add((int(item["seed"]), steady))
    if unique_late != used_late or len(unique_late) != int(payload["bit_switch_count"]):
        raise AssertionError("late switch accounting mismatch")

    for seed in (0, 1, 2, 0x12345678, 0xFFFFFFFF, 0x80000000):
        natural = seed
        q = 0
        for cycle in range(65):
            natural = xorshift32(natural)
            if cycle == 0:
                visible = apply_matrix(A, seed)
                feedback = apply_matrix(TA, seed)
            else:
                visible = apply_matrix(C, q)
                feedback = apply_matrix(B, q)
            if visible != natural:
                raise AssertionError("65-cycle visible sequence mismatch")
            q = feedback
            if q != apply_matrix(T, natural):
                raise AssertionError("encoded state invariant mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--record-index", type=int, default=0)
    parser.add_argument("--max-switches", type=int)
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--contract", choices=("65", "old-feedback"), default="65")
    parser.add_argument("--bijective", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = read_records(args.input)
    record = records[args.record_index]
    payload = solve_record(
        record,
        max_switches=args.max_switches,
        timeout_ms=args.timeout_ms,
        contract=args.contract,
        bijective_mapping=args.bijective,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        key: payload.get(key)
        for key in (
            "status", "xor_count", "max_bit_switches", "bit_switch_count",
            "gate", "delay", "cycles", "energy", "elapsed_seconds", "reason_unknown",
        )
    }, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "sat" else 20 if payload["status"] == "unsat" else 30


if __name__ == "__main__":
    raise SystemExit(main())
