"""Extract small shared-output cones from the verified 402/468 RNG DAG.

Only repository constants are read.  The report is written beside this script
and is intended to drive bounded net-centric synthesis queries.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab import rng_encoded_asic as base  # noqa: E402


def leaf_keys(node: int) -> tuple[tuple[int, int | None], ...]:
    """Return physical (state bit, optional seed bit) first-layer leaves."""
    gate = base.GATE_BY_OUTPUT[node]
    if gate.depth != 1:
        raise ValueError(f"{node:08x} is not first layer")
    return tuple(
        (state, seed)
        for state, seed in zip(base.bits(node), base.FIRST_LEAF_SEEDS[node], strict=True)
    )


def main() -> None:
    first = {gate.output: gate for gate in base.GATES if gate.depth == 1}
    second = tuple(gate for gate in base.GATES if gate.depth == 2)
    adjacency: dict[int, set[int]] = defaultdict(set)
    edge_outputs: dict[tuple[int, int], int] = {}
    first_only = []
    for gate in second:
        if gate.left in first and gate.right in first:
            edge = tuple(sorted((gate.left, gate.right)))
            adjacency[edge[0]].add(edge[1])
            adjacency[edge[1]].add(edge[0])
            edge_outputs[edge] = gate.output
            first_only.append(gate)

    triangles = []
    nodes = sorted(adjacency)
    for pos, a in enumerate(nodes):
        for b in sorted(node for node in adjacency[a] if node > a):
            for c in sorted(node for node in adjacency[a] & adjacency[b] if node > b):
                edges = ((a, b), (a, c), (b, c))
                triangles.append(
                    {
                        "nodes": [f"{node:08x}" for node in (a, b, c)],
                        "outputs": [f"{edge_outputs[edge]:08x}" for edge in edges],
                        "leaf_keys": {
                            f"{node:08x}": [[state, seed] for state, seed in leaf_keys(node)]
                            for node in (a, b, c)
                        },
                        "distinct_physical_leaves": len(
                            set().union(*(set(leaf_keys(node)) for node in (a, b, c)))
                        ),
                        "baseline_402_gate": 3 * 3 + 3 * 3,
                        "baseline_468_gate": 3 * 4 + 3 * 4,
                    }
                )

    v_cones = []
    for center in sorted(adjacency):
        neighbors = sorted(adjacency[center])
        for left_pos, left in enumerate(neighbors):
            for right in neighbors[left_pos + 1 :]:
                nodes3 = (center, left, right)
                physical_leaves = set().union(*(set(leaf_keys(node)) for node in nodes3))
                v_cones.append(
                    {
                        "center": f"{center:08x}",
                        "arms": [f"{left:08x}", f"{right:08x}"],
                        "outputs": [
                            f"{edge_outputs[tuple(sorted((center, left)))]:08x}",
                            f"{edge_outputs[tuple(sorted((center, right)))]:08x}",
                        ],
                        "leaf_keys": {
                            f"{node:08x}": [[state, seed] for state, seed in leaf_keys(node)]
                            for node in nodes3
                        },
                        "distinct_physical_leaves": len(physical_leaves),
                        "baseline_402_gate": 3 * 3 + 2 * 3,
                        "baseline_468_gate": 3 * 4 + 2 * 4,
                        "is_triangle_subset": left in adjacency[right],
                    }
                )
    v_cones.sort(
        key=lambda cone: (
            cone["distinct_physical_leaves"],
            not cone["is_triangle_subset"],
            cone["center"],
            cone["arms"],
        )
    )

    payload = {
        "schema": 1,
        "source": "src/tc_save_lab/rng_encoded_asic.py:GATES",
        "first_layer_nodes": len(first),
        "second_layer_nodes": len(second),
        "second_edges_with_two_first_operands": len(first_only),
        "first_operand_degree": {
            f"{node:08x}": len(neighbors)
            for node, neighbors in sorted(adjacency.items())
        },
        "degree_histogram": {
            str(degree): count
            for degree, count in sorted(Counter(map(len, adjacency.values())).items())
        },
        "triangles": triangles,
        "v_cone_count": len(v_cones),
        "v_cones": v_cones,
    }
    path = HERE / "actual_cones.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "path": str(path),
                "first_only_edges": len(first_only),
                "triangles": len(triangles),
                "v_cones": len(v_cones),
                "minimum_v_distinct_leaves": min(
                    (cone["distinct_physical_leaves"] for cone in v_cones), default=None
                ),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
