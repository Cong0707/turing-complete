"""Find same-XOR-count noncanonical pair-output mediators in RNG bases."""

from __future__ import annotations

import argparse
from itertools import product
import importlib.util
import json
from pathlib import Path
import sys


BITS = 32


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rows(record: dict[str, object], key: str) -> tuple[int, ...]:
    return tuple(int(str(value), 16) for value in record[key])


def bits(mask: int) -> tuple[int, ...]:
    return tuple(bit for bit in range(BITS) if mask >> bit & 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variant-limit", type=int, default=4096)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    cover_module = load_module(
        "rng_or_mediator_cover", root / ".research/rng_joint_search_resume/search.py"
    )
    dual = load_module(
        "rng_or_mediator_dual", root / ".research/rng_cost387/search_basis_dualmode.py"
    )

    cases: list[dict[str, object]] = []
    record_count = 0
    truncated = 0
    with_case: set[int] = set()
    with_case_by_xor: dict[int, int] = {}
    with args.source.open(encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            record_count += 1
            record = json.loads(line)
            T, B, C = (rows(record, key) for key in ("T", "B", "C"))
            cover = cover_module.depth_two_cost((*B, *C))
            xor_count = cover.greedy_upper_bound
            if xor_count is None:
                continue
            selected = frozenset(cover.selected_pair_gates)
            finals = tuple(
                row for row in dict.fromkeys((*B, *C)) if row.bit_count() in (3, 4)
            )
            options = {
                row: tuple(
                    option for option in dual.pair_partitions(row) if set(option) <= selected
                )
                for row in finals
            }
            if any(not value for value in options.values()):
                raise AssertionError("greedy cover does not cover a heavy target")
            variant_total = 1
            for value in options.values():
                variant_total *= len(value)
            if variant_total > args.variant_limit:
                truncated += 1
            choices = product(*(options[row] for row in finals))
            for variant_index, selected_options in enumerate(choices):
                if variant_index >= args.variant_limit:
                    break
                decomposition = dict(zip(finals, selected_options))
                heavy_use = {
                    pair: sum(pair in option for option in decomposition.values())
                    for pair in selected
                }
                for output, (target, steady) in enumerate(zip(T, B)):
                    if steady.bit_count() != 2 or heavy_use.get(steady, 0):
                        continue
                    left, right = bits(steady)
                    for common in range(BITS):
                        if common in (left, right):
                            continue
                        first = (1 << left) | (1 << common)
                        second = (1 << right) | (1 << common)
                        if first not in selected or second not in selected:
                            continue
                        cases.append(
                            {
                                "source_line": line_number,
                                "step": record.get("step"),
                                "xor": xor_count,
                                "variant_index": variant_index,
                                "output_index": output,
                                "steady_target": f"{steady:08x}",
                                "seed_target": f"{target:08x}",
                                "mediators": [f"{first:08x}", f"{second:08x}"],
                                "selected_pair_count": len(selected),
                                "heavy_final_count": len(finals),
                            }
                        )
                        if line_number not in with_case:
                            with_case.add(line_number)
                            with_case_by_xor[xor_count] = with_case_by_xor.get(xor_count, 0) + 1

    document = {
        "scope": "greedy pair sets; same-count noncanonical B weight-2 replacement",
        "source": str(args.source),
        "record_count": record_count,
        "record_with_case_count": len(with_case),
        "record_with_case_count_by_xor": {
            str(key): value for key, value in sorted(with_case_by_xor.items())
        },
        "case_count": len(cases),
        "truncated_variant_record_count": truncated,
        "variant_limit": args.variant_limit,
        "cases": cases,
    }
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in document.items() if key != "cases"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
