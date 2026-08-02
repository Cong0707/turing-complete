"""Exact joint pair-cover/tick-zero audit for the RNG OR frontier.

Each basis is solved independently.  The Boolean model jointly chooses the
pair cover, final decompositions, pair seed labels, pin orientations, and the
union of physical (seed bit, state bit) OR leaves.  No cover list or global
label beam is materialized.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
import gc
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

import z3


BITS = 32


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rows(record: dict[str, object], key: str) -> tuple[int, ...]:
    values = record.get(key)
    if not isinstance(values, list) or len(values) != BITS:
        raise ValueError(f"{key} must have 32 rows")
    return tuple(int(str(value), 16) for value in values)


def support(value: int) -> tuple[int, ...]:
    return tuple(bit for bit in range(BITS) if value >> bit & 1)


def bool_sum(expressions) -> z3.ArithRef:
    return z3.Sum([z3.If(expression, 1, 0) for expression in expressions])


def actual_test_seeds() -> tuple[int, ...]:
    modulus = 0xFFFFFFFE
    multiplier = 0x4848F09881D3DDD1
    return tuple(
        1 + ((((test_id + 1) * multiplier) & 0xFFFFFFFFFFFFFFFF) % modulus)
        for test_id in range(256)
    )


def verify_256x65(init, T, B, C) -> str:
    seeds = actual_test_seeds()
    packed = b"".join(seed.to_bytes(4, "little") for seed in seeds)
    seed_hash = hashlib.sha256(packed).hexdigest()
    if seed_hash != "d8ef931e5eb213217aa4faedc43783f0875e52607f991e89080c6046aad1e24b":
        raise AssertionError("actual test seed vector hash changed")
    for seed in seeds:
        natural = seed
        encoded = init.apply_matrix(T, seed)
        for _ in range(65):
            natural = init.xorshift32(natural)
            if init.apply_matrix(C, encoded) != natural:
                raise AssertionError(f"256x65 output mismatch for seed {seed:08x}")
            encoded = init.apply_matrix(B, encoded)
    return seed_hash


def solve_basis(record, init, dual, *, logic_budget: int, timeout_ms: int):
    T, B, C = (rows(record, key) for key in ("T", "B", "C"))
    if init.compose(C, T) != init.A or init.compose(T, C) != B:
        raise AssertionError("matrix identities failed before SMT")

    targets = frozenset((*B, *C))
    required = frozenset(row for row in targets if row.bit_count() == 2)
    finals = frozenset(row for row in targets if row.bit_count() in (3, 4))
    options = {row: dual.pair_partitions(row) for row in finals}
    pair_universe = frozenset(required).union(
        pair for row_options in options.values() for option in row_options for pair in option
    )
    ordered_pairs = tuple(sorted(pair_universe))
    ordered_finals = tuple(sorted(finals))

    solver = z3.Solver()
    solver.set(timeout=timeout_ms, random_seed=0x387)
    selected = {pair: z3.Bool(f"s_{pair:08x}") for pair in ordered_pairs}
    labels = {
        (pair, seed): z3.Bool(f"l_{pair:08x}_{seed}")
        for pair in ordered_pairs
        for seed in range(BITS)
    }
    orientations = {
        (pair, seed): z3.Bool(f"o_{pair:08x}_{seed}")
        for pair in ordered_pairs
        for seed in range(BITS)
    }
    choices = {
        (row, index): z3.Bool(f"d_{row:08x}_{index}")
        for row in ordered_finals
        for index in range(len(options[row]))
    }

    pair_uses: dict[int, list[z3.BoolRef]] = defaultdict(list)
    for row in ordered_finals:
        row_choices = [choices[(row, index)] for index in range(len(options[row]))]
        solver.add(z3.PbEq([(choice, 1) for choice in row_choices], 1))
        for index, option in enumerate(options[row]):
            choice = choices[(row, index)]
            for pair in option:
                solver.add(z3.Implies(choice, selected[pair]))
                pair_uses[pair].append(choice)

    for pair in ordered_pairs:
        if pair in required:
            solver.add(selected[pair])
        else:
            uses = pair_uses[pair]
            solver.add(selected[pair] == (z3.Or(uses) if uses else z3.BoolVal(False)))
        label_bits = [labels[(pair, seed)] for seed in range(BITS)]
        solver.add(bool_sum(label_bits) <= 2)
        solver.add(
            z3.Implies(z3.Not(selected[pair]), z3.And([z3.Not(bit) for bit in label_bits]))
        )
        first_pin = [
            z3.And(labels[(pair, seed)], orientations[(pair, seed)])
            for seed in range(BITS)
        ]
        second_pin = [
            z3.And(labels[(pair, seed)], z3.Not(orientations[(pair, seed)]))
            for seed in range(BITS)
        ]
        solver.add(bool_sum(first_pin) <= 1, bool_sum(second_pin) <= 1)

    contributors: dict[tuple[int, int], list[z3.BoolRef]] = defaultdict(list)
    for pair in ordered_pairs:
        state_left, state_right = support(pair)
        for seed in range(BITS):
            contributors[(seed, state_left)].append(
                z3.And(selected[pair], labels[(pair, seed)], orientations[(pair, seed)])
            )
            contributors[(seed, state_right)].append(
                z3.And(
                    selected[pair], labels[(pair, seed)], z3.Not(orientations[(pair, seed)])
                )
            )

    exact_labels: dict[int, int] = {}
    for target, steady in zip(T, B):
        weight = steady.bit_count()
        if weight == 1:
            if target.bit_count() != 1:
                return "structural_unsat", None, {"reason": "direct_target_not_unit"}
            contributors[(support(target)[0], support(steady)[0])].append(z3.BoolVal(True))
        elif weight == 2:
            if target.bit_count() > 2:
                return "structural_unsat", None, {"reason": "pair_exact_target_invalid"}
            previous = exact_labels.setdefault(steady, target)
            if previous != target:
                return "structural_unsat", None, {"reason": "pair_exact_label_conflict"}
            for seed in range(BITS):
                solver.add(labels[(steady, seed)] == z3.BoolVal(bool(target >> seed & 1)))
        elif weight == 3:
            for index, option in enumerate(options[steady]):
                pair = option[0]
                state = support(steady ^ pair)[0]
                choice = choices[(steady, index)]
                residuals = [
                    z3.Xor(labels[(pair, seed)], z3.BoolVal(bool(target >> seed & 1)))
                    for seed in range(BITS)
                ]
                solver.add(z3.Implies(choice, bool_sum(residuals) <= 1))
                for seed, residual in enumerate(residuals):
                    contributors[(seed, state)].append(z3.And(choice, residual))
        elif weight == 4:
            for index, option in enumerate(options[steady]):
                left, right = option
                choice = choices[(steady, index)]
                for seed in range(BITS):
                    solver.add(
                        z3.Implies(
                            choice,
                            z3.Xor(labels[(left, seed)], labels[(right, seed)])
                            == z3.BoolVal(bool(target >> seed & 1)),
                        )
                    )
        else:
            return "structural_unsat", None, {"reason": "unsupported_B_weight"}

    mapping_expressions = {
        atom: z3.Or(expressions) for atom, expressions in contributors.items()
    }
    for seed in range(BITS):
        seed_mappings = [
            expression
            for (mapped_seed, _), expression in mapping_expressions.items()
            if mapped_seed == seed
        ]
        solver.add(z3.Or(seed_mappings) if seed_mappings else z3.BoolVal(False))

    pair_count = bool_sum(selected.values())
    xor_count = pair_count + len(finals)
    or_count = bool_sum(mapping_expressions.values())
    solver.add(z3.Or(xor_count == 61, xor_count == 62, xor_count == 63))
    solver.add(3 * xor_count + or_count <= logic_budget)

    started = time.perf_counter()
    checked = solver.check()
    elapsed = time.perf_counter() - started
    statistics = {
        "elapsed_seconds": round(elapsed, 6),
        "required_pair_count": len(required),
        "final_count": len(finals),
        "pair_universe_count": len(pair_universe),
        "mapping_atom_universe_count": len(mapping_expressions),
    }
    if checked == z3.unsat:
        return "unsat", None, statistics
    if checked == z3.unknown:
        statistics["reason_unknown"] = solver.reason_unknown()
        return "unknown", None, statistics

    model = solver.model()
    chosen_pairs = frozenset(
        pair for pair in ordered_pairs if z3.is_true(model.eval(selected[pair], model_completion=True))
    )
    decompositions = {}
    for row in ordered_finals:
        selected_indexes = [
            index
            for index in range(len(options[row]))
            if z3.is_true(model.eval(choices[(row, index)], model_completion=True))
        ]
        if len(selected_indexes) != 1:
            raise AssertionError("SMT decomposition is not one-hot")
        decompositions[row] = options[row][selected_indexes[0]]

    pair_labels = {}
    pin_orientations = {}
    for pair in chosen_pairs:
        label = sum(
            (1 << seed)
            for seed in range(BITS)
            if z3.is_true(model.eval(labels[(pair, seed)], model_completion=True))
        )
        pair_labels[pair] = label
        state_left, state_right = support(pair)
        pins: list[int | None] = [None, None]
        for seed in support(label):
            side = 0 if z3.is_true(
                model.eval(orientations[(pair, seed)], model_completion=True)
            ) else 1
            if pins[side] is not None:
                raise AssertionError("multiple seed labels assigned to one XOR pin")
            pins[side] = seed
        pin_orientations[pair] = (pins[0], pins[1])

    mappings = frozenset(
        atom
        for atom, expression in mapping_expressions.items()
        if z3.is_true(model.eval(expression, model_completion=True))
    )
    result = dual.DualResult(
        len(mappings), mappings, pair_labels, pin_orientations, decompositions
    )
    dual.verify_candidate(init, T, B, C, chosen_pairs, result)
    seed_hash = verify_256x65(init, T, B, C)
    actual_xor = len(chosen_pairs) + len(finals)
    certificate = {
        "T": [f"{row:08x}" for row in T],
        "B": [f"{row:08x}" for row in B],
        "C": [f"{row:08x}" for row in C],
        "selected_pair_gates": [f"{pair:08x}" for pair in sorted(chosen_pairs)],
        "decompositions": {
            f"{row:08x}": [f"{pair:08x}" for pair in option]
            for row, option in sorted(decompositions.items())
        },
        "pair_labels": {
            f"{pair:08x}": f"{label:08x}" for pair, label in sorted(pair_labels.items())
        },
        "pair_pin_seed_bits": {
            f"{pair:08x}": list(pin_orientations[pair]) for pair in sorted(chosen_pairs)
        },
        "mode_pairs": [
            {"seed": seed, "state": state} for seed, state in sorted(mappings)
        ],
        "metrics": {
            "xor": actual_xor,
            "or": len(mappings),
            "three_xor_plus_or": 3 * actual_xor + len(mappings),
            "gate": 166 + 3 * actual_xor + len(mappings),
            "delay": 10,
            "cycles": 66,
            "energy": (166 + 3 * actual_xor + len(mappings)) * 10 * 66,
        },
        "verification": {
            "matrix_identities": True,
            "actual_test_seeds": 256,
            "ticks_per_seed": 65,
            "seed_vector_sha256": seed_hash,
        },
    }
    return "sat", certificate, statistics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--records-output", required=True, type=Path)
    parser.add_argument("--source-xor", type=int, choices=(61, 62, 63))
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--max-records", type=int)
    parser.add_argument("--logic-budget", type=int, default=221)
    parser.add_argument("--timeout-ms", type=int, default=5000)
    parser.add_argument("--memory-limit-mb", type=int, default=512)
    args = parser.parse_args()

    z3.set_param("memory_max_size", args.memory_limit_mb)
    root = Path(__file__).resolve().parents[2]
    init = load_module(
        "rng_or_joint_init", root / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    dual = load_module(
        "rng_or_joint_dual", root / ".research/rng_cost387/search_basis_dualmode.py"
    )

    started = time.perf_counter()
    counts: Counter[str] = Counter()
    matching_index = 0
    processed = 0
    candidates = []
    args.records_output.parent.mkdir(parents=True, exist_ok=True)
    with args.input.open(encoding="utf-8-sig") as source, args.records_output.open(
        "w", encoding="utf-8", newline="\n"
    ) as record_output:
        for source_line, line in enumerate(source, 1):
            record = json.loads(line)
            source_xor = int(record["cover"]["greedy_xor"])
            if args.source_xor is not None and source_xor != args.source_xor:
                continue
            if matching_index < args.start_index:
                matching_index += 1
                continue
            if args.max_records is not None and processed >= args.max_records:
                break
            matching_index += 1
            processed += 1
            status, certificate, statistics = solve_basis(
                record,
                init,
                dual,
                logic_budget=args.logic_budget,
                timeout_ms=args.timeout_ms,
            )
            counts[status] += 1
            item = {
                "source_line": source_line,
                "source_index": matching_index - 1,
                "hash": record["hash"],
                "step": record["step"],
                "source_greedy_xor": source_xor,
                "status": status,
                **statistics,
            }
            if certificate is not None:
                item["certificate"] = certificate
                candidates.append(item)
            record_output.write(json.dumps(item, separators=(",", ":")) + "\n")
            record_output.flush()
            if not processed % 25:
                print(f"processed={processed} counts={dict(counts)}", flush=True)
            if not processed % 100:
                gc.collect()

    with args.records_output.open("rb") as stream:
        records_sha256 = hashlib.file_digest(stream, "sha256").hexdigest()
    document = {
        "status": "candidate" if candidates else ("complete" if not counts["unknown"] else "incomplete"),
        "input": str(args.input),
        "source_xor": args.source_xor,
        "start_index": args.start_index,
        "max_records": args.max_records,
        "processed_record_count": processed,
        "logic_budget": args.logic_budget,
        "equivalent_or_bounds": {"61": args.logic_budget - 183, "62": args.logic_budget - 186, "63": args.logic_budget - 189},
        "timeout_ms": args.timeout_ms,
        "memory_limit_mb": args.memory_limit_mb,
        "result_counts": dict(sorted(counts.items())),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "records_output": str(args.records_output),
        "records_sha256": records_sha256,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in document.items() if key != "candidates"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
