"""Classify where tick-zero labeling fails for the five completed cases."""

from __future__ import annotations

import argparse
from collections import Counter
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


def diagnose(dual, t_rows, b_rows, selected_pairs, decompositions, component_limit, global_beam):
    adjacency = {pair: [] for pair in selected_pairs}
    exact_labels = {}
    residuals = []
    fixed_mappings = set()

    for target, steady in zip(t_rows, b_rows):
        weight = steady.bit_count()
        if weight == 1:
            if target.bit_count() != 1:
                return "direct_target_not_unit", {}
            fixed_mappings.add((dual.bits(target)[0], dual.bits(steady)[0]))
        elif weight == 2:
            if steady not in selected_pairs or target.bit_count() > 2:
                return "pair_exact_target_invalid", {}
            previous = exact_labels.setdefault(steady, target)
            if previous != target:
                return "pair_exact_label_conflict", {}
        elif weight == 3:
            pair = decompositions[steady][0]
            direct = steady ^ pair
            if direct.bit_count() != 1:
                return "weight3_bad_decomposition", {}
            residuals.append((pair, target, dual.bits(direct)[0]))
        elif weight == 4:
            left, right = decompositions[steady]
            adjacency[left].append((right, target))
            adjacency[right].append((left, target))
        else:
            return "unsupported_steady_weight", {}

    active = set(exact_labels) | {node for node, _, _ in residuals}
    active |= {node for node, edges in adjacency.items() if edges}
    components = []
    visited = set()
    for root in sorted(active):
        if root in visited:
            continue
        offsets = {root: 0}
        stack = [root]
        consistent = True
        while stack and consistent:
            node = stack.pop()
            visited.add(node)
            for neighbor, edge_label in adjacency[node]:
                expected = offsets[node] ^ edge_label
                if neighbor in offsets:
                    consistent &= offsets[neighbor] == expected
                else:
                    offsets[neighbor] = expected
                    stack.append(neighbor)
        if not consistent:
            return "xor_label_graph_inconsistent", {"component_nodes": len(offsets)}
        local_exact = {node: label for node, label in exact_labels.items() if node in offsets}
        local_residuals = tuple(item for item in residuals if item[0] in offsets)
        options = dual.component_options(
            offsets, local_exact, local_residuals, component_limit
        )
        if not options:
            return "component_has_no_labeling", {
                "component_nodes": len(offsets),
                "exact_labels": len(local_exact),
                "residuals": len(local_residuals),
            }
        components.append((offsets, options))

    components.sort(key=lambda item: (len(item[1]), len(item[0])))
    states = {frozenset(fixed_mappings): ()}
    peak_expanded = 0
    for component_index, (_, options) in enumerate(components):
        expanded = {}
        for mappings, choices in states.items():
            for option in options:
                merged = mappings | option.mappings
                expanded.setdefault(merged, choices + (option,))
        peak_expanded = max(peak_expanded, len(expanded))
        ordered = sorted(
            expanded.items(), key=lambda item: (len(item[0]), tuple(sorted(item[0])))
        )
        states = dict(ordered[:global_beam])
        if not states:
            return "global_beam_empty", {"component_index": component_index}

    best_seed_coverage = max(
        (len({seed for seed, _ in mappings}) for mappings in states), default=0
    )
    if best_seed_coverage != 32:
        return "beam_missing_all_seed_coverage", {
            "component_count": len(components),
            "final_state_count": len(states),
            "peak_expanded": peak_expanded,
            "best_seed_coverage": best_seed_coverage,
        }
    return "feasible", {
        "component_count": len(components),
        "final_state_count": len(states),
        "peak_expanded": peak_expanded,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--component-limit", type=int, default=512)
    parser.add_argument("--global-beam", type=int, default=4096)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[3]
    dual = load_module(
        "finish_diagnose_dual", repo / ".research/rng_cost387/search_basis_dualmode.py"
    )
    source = json.loads(args.input.read_text(encoding="utf-8"))
    totals = Counter()
    records = []
    for source_case in source["cases"]:
        t_rows = tuple(int(item, 16) for item in source_case["T"])
        b_rows = tuple(int(item, 16) for item in source_case["B"])
        c_rows = tuple(int(item, 16) for item in source_case["C"])
        finals = frozenset(
            row for row in (*b_rows, *c_rows) if row.bit_count() in (3, 4)
        )
        case_counts = Counter()
        details = []
        for cover_index, encoded_cover in enumerate(source_case["covers"]):
            cover = frozenset(int(item, 16) for item in encoded_cover)
            expected = source_case["decomposition_assignment_counts"][cover_index]
            variants = dual.decomposition_variants(
                cover, finals, b_rows, expected, random.Random(0)
            )
            for variant_index, decompositions in enumerate(variants):
                status, detail = diagnose(
                    dual,
                    t_rows,
                    b_rows,
                    cover,
                    decompositions,
                    args.component_limit,
                    args.global_beam,
                )
                totals[status] += 1
                case_counts[status] += 1
                details.append(
                    {
                        "cover_index": cover_index,
                        "variant_index": variant_index,
                        "status": status,
                        "detail": detail,
                    }
                )
        records.append(
            {
                "case": source_case["case"],
                "counts": dict(sorted(case_counts.items())),
                "variants": details,
            }
        )
        print(f"case={source_case['case']} {dict(case_counts)}", flush=True)

    document = {
        "component_limit": args.component_limit,
        "global_beam": args.global_beam,
        "counts": dict(sorted(totals.items())),
        "cases": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(document["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
