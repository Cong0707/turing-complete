"""Search exact three-ordinary-gate replacements for private 80/7 output cones.

The reviewed 80/7 Byte Adder has two output roots whose private backward
slices cost four gates: S0 (node 49) and S6 (node 73).  The older local-resub
audit only checked one- and two-gate replacements.  This script closes the
next exact gap by enumerating every live three-gate ordinary topology over a
reviewed local source pool:

* a three-gate chain, including fanout from gate 1 into gate 3;
* two independent first-stage gates followed by a combining gate.

It also enumerates the complete cost-four ordinary formula-tree closure for
the five-gate private S2 and S4 roots.  A separate SAT audit covers arbitrary
internal fanout for those two roots.

All source rows are projected from the complete 2^17 truth domain.  Projection
is lossless: the script rejects a source pool if equal source vectors map to
different target values.  Every ordinary gate costs one and delays one; XOR
and XNOR are intentionally absent because either one consumes the complete
three-gate budget and was already covered by the one-stage audit.

The script is offline only.  It never reads or writes the formal game save.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import NamedTuple


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_DAG = HERE / "byte-adder-hybrid-phasefold-g80-d7.json"
MATERIALIZER = (
    ROOT / ".research" / "byte_adder_builder_layout_agent" / "materialize_factory_dag.py"
)


class Formula(NamedTuple):
    bits: int
    arrival: int
    text: str


BINARY_OPS = {
    "AND": lambda left, right, mask: left & right,
    "NAND": lambda left, right, mask: ~(left & right) & mask,
    "OR": lambda left, right, mask: left | right,
    "NOR": lambda left, right, mask: ~(left | right) & mask,
}


ROOT_POOLS = {
    # Inputs a0/b0/cin, their reviewed OR/AND pair, and resolved C1.
    49: (2, 3, 18, 43, 44, 45),
    # Local bits 5:6 leaves, C5, the reviewed S5 phase, pair state, and C7.
    73: (12, 13, 14, 15, 34, 35, 36, 37, 38, 39, 62, 63, 64, 65, 66, 67, 68, 69),
}


FOUR_GATE_TREE_POOLS = {
    # S2: omit its five-gate private cone (C2 plus the four-gate fused Sum).
    81: (4, 5, 6, 7, 22, 23, 24, 25, 45, 50, 51, 52, 54, 55, 56, 76, 77),
    # S4: omit Q4, C4, and the three-gate Sum cone.
    86: (8, 9, 10, 11, 28, 29, 30, 31, 32, 56, 57, 59, 60, 61, 62, 82, 83),
}


def load_materializer():
    spec = importlib.util.spec_from_file_location("byte_adder_three_gate_materializer", MATERIALIZER)
    if spec is None or spec.loader is None:
        raise RuntimeError(MATERIALIZER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def project_domain(
    source_ids: tuple[int, ...],
    target: int,
    states: dict[int, dict[str, int]],
    full_rows: int,
) -> tuple[tuple[Formula, ...], int, int]:
    """Return exact compressed sources, target bits, and compressed row count."""

    source_bits = tuple(int(states[node_id]["bits"]) for node_id in source_ids)
    target_bits = int(states[target]["bits"])
    classes: dict[int, bool] = {}
    for row in range(full_rows):
        vector = 0
        for index, bits in enumerate(source_bits):
            vector |= ((bits >> row) & 1) << index
        value = bool((target_bits >> row) & 1)
        previous = classes.get(vector)
        if previous is not None and previous != value:
            raise RuntimeError(
                f"target {target} is not a function of source pool {source_ids}: vector={vector}"
            )
        classes[vector] = value

    vectors = tuple(sorted(classes))
    compact_sources = []
    for index, node_id in enumerate(source_ids):
        bits = sum(((vector >> index) & 1) << row for row, vector in enumerate(vectors))
        compact_sources.append(
            Formula(bits, int(states[node_id]["depth"]), f"n{node_id}")
        )
    compact_target = sum(int(classes[vector]) << row for row, vector in enumerate(vectors))
    return tuple(compact_sources), compact_target, len(vectors)


def one_gate_pool(sources: tuple[Formula, ...], mask: int) -> tuple[Formula, ...]:
    """Deduplicate one-gate functions by value, keeping the earliest witness."""

    unique: dict[int, Formula] = {}

    def remember(candidate: Formula) -> None:
        previous = unique.get(candidate.bits)
        if previous is None or (candidate.arrival, candidate.text) < (
            previous.arrival,
            previous.text,
        ):
            unique[candidate.bits] = candidate

    for source in sources:
        remember(Formula(~source.bits & mask, source.arrival + 1, f"NOT({source.text})"))
    for left_index, left in enumerate(sources):
        for right in sources[left_index + 1 :]:
            arrival = max(left.arrival, right.arrival) + 1
            for name, function in BINARY_OPS.items():
                remember(
                    Formula(
                        function(left.bits, right.bits, mask),
                        arrival,
                        f"{name}({left.text},{right.text})",
                    )
                )
    return tuple(unique.values())


def dependent_second_stages(
    first: Formula,
    sources: tuple[Formula, ...],
    mask: int,
) -> tuple[Formula, ...]:
    """Enumerate gate 2 while requiring it to consume gate 1."""

    unique: dict[int, Formula] = {}

    def remember(candidate: Formula) -> None:
        previous = unique.get(candidate.bits)
        if previous is None or (candidate.arrival, candidate.text) < (
            previous.arrival,
            previous.text,
        ):
            unique[candidate.bits] = candidate

    remember(Formula(~first.bits & mask, first.arrival + 1, f"NOT({first.text})"))
    for source in sources:
        arrival = max(first.arrival, source.arrival) + 1
        for name, function in BINARY_OPS.items():
            remember(
                Formula(
                    function(first.bits, source.bits, mask),
                    arrival,
                    f"{name}({first.text},{source.text})",
                )
            )
    return tuple(unique.values())


def search_three_gates(
    sources: tuple[Formula, ...],
    target_bits: int,
    compact_rows: int,
    delay_limit: int,
) -> tuple[list[dict[str, object]], dict[str, int]]:
    mask = (1 << compact_rows) - 1
    first_stages = one_gate_pool(sources, mask)
    hits: dict[str, dict[str, object]] = {}
    chain_second_count = 0
    final_checks = 0

    # Topology A: gate 2 consumes gate 1; gate 3 consumes gate 2 and may also
    # consume gate 1 or a paid source.  This includes all live chain/fanout
    # topologies with three gates.
    for first in first_stages:
        second_stages = dependent_second_stages(first, sources, mask)
        chain_second_count += len(second_stages)
        final_others = sources + (first,)
        for second in second_stages:
            final_checks += 1
            if second.arrival + 1 <= delay_limit and (~second.bits & mask) == target_bits:
                text = f"NOT({second.text})"
                hits[text] = {"topology": "chain", "arrival": second.arrival + 1, "formula": text}
            for other in final_others:
                arrival = max(second.arrival, other.arrival) + 1
                if arrival > delay_limit:
                    continue
                for name, function in BINARY_OPS.items():
                    final_checks += 1
                    if function(second.bits, other.bits, mask) != target_bits:
                        continue
                    text = f"{name}({second.text},{other.text})"
                    hits[text] = {"topology": "chain", "arrival": arrival, "formula": text}

    # Topology B: gates 1 and 2 are independent one-stage gates, and the final
    # binary gate consumes both.  Requiring a strict pair order removes the
    # commutative duplicate without removing any circuit.
    for left_index, left in enumerate(first_stages):
        for right in first_stages[left_index + 1 :]:
            arrival = max(left.arrival, right.arrival) + 1
            if arrival > delay_limit:
                continue
            for name, function in BINARY_OPS.items():
                final_checks += 1
                if function(left.bits, right.bits, mask) != target_bits:
                    continue
                text = f"{name}({left.text},{right.text})"
                hits[text] = {"topology": "parallel", "arrival": arrival, "formula": text}

    return list(hits.values()), {
        "unique_first_stage_functions": len(first_stages),
        "chain_second_stage_functions": chain_second_count,
        "final_function_checks": final_checks,
    }


def search_formula_tree(
    sources: tuple[Formula, ...],
    target_bits: int,
    compact_rows: int,
    gate_cost: int,
    delay_limit: int,
) -> dict[str, object]:
    """Enumerate a superset of exact-cost ordinary formula trees.

    A level maps each Boolean function to its minimum possible arrival.  The
    recurrence combines every partition ``left_cost + right_cost + 1`` and
    also applies unary NOT.  Repeated and semantically redundant children are
    retained, so a miss is not caused by an accidental liveness restriction.
    Internal fanout into two later gates is outside this formula-tree model and
    is stated explicitly in the report.
    """

    mask = (1 << compact_rows) - 1
    level_zero: dict[int, int] = {}
    for source in sources:
        previous = level_zero.get(source.bits)
        if previous is None or source.arrival < previous:
            level_zero[source.bits] = source.arrival
    levels = [level_zero]
    counts = [len(level_zero)]

    for cost in range(1, gate_cost + 1):
        current: dict[int, int] = {}

        def remember(bits: int, arrival: int) -> None:
            previous = current.get(bits)
            if previous is None or arrival < previous:
                current[bits] = arrival

        for bits, arrival in levels[cost - 1].items():
            remember(~bits & mask, arrival + 1)
        for left_cost in range(cost):
            right_cost = cost - 1 - left_cost
            if left_cost > right_cost:
                continue
            left_rows = tuple(levels[left_cost].items())
            right_rows = tuple(levels[right_cost].items())
            for left_index, (left_bits, left_arrival) in enumerate(left_rows):
                start = left_index if left_cost == right_cost else 0
                for right_bits, right_arrival in right_rows[start:]:
                    arrival = max(left_arrival, right_arrival) + 1
                    for function in BINARY_OPS.values():
                        remember(function(left_bits, right_bits, mask), arrival)
        levels.append(current)
        counts.append(len(current))

    target_arrival = levels[gate_cost].get(target_bits)
    return {
        "exact_cost_function_counts": counts,
        "target_found": target_arrival is not None and target_arrival <= delay_limit,
        "target_min_arrival": target_arrival,
        "delay_limit": delay_limit,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    parser.add_argument("--output", type=Path, default=HERE / "three-gate-root-resub-80d7.json")
    args = parser.parse_args()

    materializer = load_materializer()
    payload = json.loads(args.dag.read_text(encoding="utf-8"))
    ordered_nodes = tuple(payload["factory_dag"]["nodes"])
    nodes = {int(node["id"]): node for node in ordered_nodes}
    states = materializer.logical_states(ordered_nodes)
    full_rows = 1 << 17
    results = []
    for target, source_ids in ROOT_POOLS.items():
        compact_sources, compact_target, compact_rows = project_domain(
            source_ids, target, states, full_rows
        )
        hits, counters = search_three_gates(
            compact_sources,
            compact_target,
            compact_rows,
            delay_limit=7,
        )
        results.append(
            {
                "target": target,
                "target_op": nodes[target]["op"],
                "source_ids": list(source_ids),
                "compressed_truth_rows": compact_rows,
                "private_gate_cost": 4,
                "replacement_gate_cost": 3,
                "hits": hits,
                "counters": counters,
            }
        )

    tree_results = []
    for target, source_ids in FOUR_GATE_TREE_POOLS.items():
        compact_sources, compact_target, compact_rows = project_domain(
            source_ids, target, states, full_rows
        )
        audit = search_formula_tree(
            compact_sources,
            compact_target,
            compact_rows,
            gate_cost=4,
            delay_limit=7,
        )
        tree_results.append(
            {
                "target": target,
                "target_op": nodes[target]["op"],
                "source_ids": list(source_ids),
                "compressed_truth_rows": compact_rows,
                "private_gate_cost": 5,
                "replacement_gate_cost": 4,
                **audit,
            }
        )

    result = {
        "schema": "byte-adder-80d7-three-gate-root-resub-v1",
        "source": str(args.dag.resolve()),
        "full_truth_rows": full_rows,
        "ordinary_kinds": ["NOT", *BINARY_OPS],
        "three_gate_dag_targets": results,
        "four_gate_formula_tree_targets": tree_results,
        "status": (
            "improving-local-root-resub-found"
            if any(item["hits"] for item in results)
            or any(item["target_found"] for item in tree_results)
            else "no-improving-local-root-resub-in-audited-families"
        ),
        "limitations": [
            "local source pools are explicit and reviewed, not all DAG signals",
            "covers exactly three cost-one ordinary gates, not Switch or XOR mixtures",
            "the four-gate S2/S4 closure covers formula trees, not arbitrary internal-fanout DAGs",
            "not a global 79/7 lower bound",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
