"""Exhaust every tick-zero decomposition for the five completed x60 cases."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import random
import sys


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--component-limit", type=int, default=4096)
    parser.add_argument("--global-beam", type=int, default=65536)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[3]
    dual = load_module(
        "finish_labels_dual", repo / ".research/rng_cost387/search_basis_dualmode.py"
    )
    init = load_module(
        "finish_labels_init", repo / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    source = json.loads(args.input.read_text(encoding="utf-8"))

    records = []
    total_variants = 0
    feasible_variants = 0
    within_budget = []
    for source_case in source["cases"]:
        t_rows = tuple(int(item, 16) for item in source_case["T"])
        b_rows = tuple(int(item, 16) for item in source_case["B"])
        c_rows = tuple(int(item, 16) for item in source_case["C"])
        finals = frozenset(
            row for row in (*b_rows, *c_rows) if row.bit_count() in (3, 4)
        )
        case_variants = 0
        case_feasible = 0
        cover_records = []
        for cover_index, encoded_cover in enumerate(source_case["covers"]):
            cover = frozenset(int(item, 16) for item in encoded_cover)
            expected = source_case["decomposition_assignment_counts"][cover_index]
            variants = dual.decomposition_variants(
                cover,
                finals,
                b_rows,
                max(1, expected),
                random.Random(0),
            )
            if len(variants) != expected:
                raise AssertionError(
                    f"case {source_case['case']} cover {cover_index}: "
                    f"expected {expected} exhaustive variants, got {len(variants)}"
                )
            feasible = []
            selected_xor = len(cover) + len(finals)
            for variant_index, decompositions in enumerate(variants):
                case_variants += 1
                total_variants += 1
                result = dual.optimize_labels(
                    t_rows,
                    b_rows,
                    cover,
                    decompositions,
                    component_limit=args.component_limit,
                    global_beam=args.global_beam,
                )
                if result is None:
                    continue
                dual.verify_candidate(init, t_rows, b_rows, c_rows, cover, result)
                case_feasible += 1
                feasible_variants += 1
                budget = 3 * selected_xor + result.or_count
                item = {
                    "variant_index": variant_index,
                    "xor": selected_xor,
                    "or": result.or_count,
                    "three_xor_plus_or": budget,
                }
                feasible.append(item)
                if budget <= 221:
                    within_budget.append(
                        {
                            "case": source_case["case"],
                            "cover_index": cover_index,
                            **item,
                        }
                    )
            cover_records.append(
                {
                    "cover_index": cover_index,
                    "xor": selected_xor,
                    "variant_count": len(variants),
                    "feasible": feasible,
                }
            )
        records.append(
            {
                "case": source_case["case"],
                "variant_count": case_variants,
                "feasible_variant_count": case_feasible,
                "covers": cover_records,
            }
        )
        print(
            f"case={source_case['case']} variants={case_variants} "
            f"feasible={case_feasible}",
            flush=True,
        )

    document = {
        "scope": "all B-row decomposition assignments of the five completed cover searches",
        "init_data": 0,
        "architecture_output_count": 1,
        "component_limit": args.component_limit,
        "global_beam": args.global_beam,
        "total_variants": total_variants,
        "feasible_variants": feasible_variants,
        "within_3xor_plus_or_221": within_budget,
        "cases": records,
        "status": "candidate" if within_budget else "no_candidate",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in document.items() if key != "cases"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
