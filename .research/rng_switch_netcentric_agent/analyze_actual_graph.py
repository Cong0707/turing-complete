"""Analyze global sharing opportunities in the verified RNG XOR DAG.

The generated ``actual_cones.json`` records the 27 first-layer XOR nodes and
the 24 second-layer edges whose two operands are both first-layer nodes.  This
script reconstructs the undirected graph, its path/cycle components, the raw
leaf vectors behind every vertex, and GF(2) ranks of the requested outputs.
It is deliberately read-only with respect to the game save.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
import json
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent


def gf2_rank(rows: Iterable[int]) -> int:
    """Return the rank of integer bit vectors over GF(2)."""

    basis: dict[int, int] = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def canonical_leaf(raw: object) -> tuple[int, int | None]:
    if not isinstance(raw, list) or len(raw) != 2:
        raise ValueError(f"invalid leaf: {raw!r}")
    return int(raw[0]), None if raw[1] is None else int(raw[1])


def leaf_sort_key(leaf: tuple[int, int | None]) -> tuple[int, int]:
    return leaf[0], -1 if leaf[1] is None else leaf[1]


def main() -> int:
    payload = json.loads((HERE / "actual_cones.json").read_text(encoding="utf-8"))
    adjacency: dict[str, set[str]] = defaultdict(set)
    leaves: dict[str, tuple[tuple[int, int | None], ...]] = {}
    edges: set[tuple[str, str]] = set()

    for cone in payload["v_cones"]:
        center = str(cone["center"])
        for node, raw_leaves in cone["leaf_keys"].items():
            current = tuple(canonical_leaf(leaf) for leaf in raw_leaves)
            previous = leaves.setdefault(str(node), current)
            if previous != current:
                raise ValueError(f"inconsistent leaves for {node}: {previous} != {current}")
        for arm in cone["arms"]:
            arm = str(arm)
            edge = tuple(sorted((center, arm)))
            edges.add(edge)
            adjacency[center].add(arm)
            adjacency[arm].add(center)

    components: list[list[str]] = []
    unseen = set(adjacency)
    while unseen:
        seed = min(unseen)
        queue = deque((seed,))
        members = []
        unseen.remove(seed)
        while queue:
            node = queue.popleft()
            members.append(node)
            for neighbor in sorted(adjacency[node]):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
        components.append(members)

    all_raw_leaves = sorted(
        {leaf for node_leaves in leaves.values() for leaf in node_leaves},
        key=leaf_sort_key,
    )
    leaf_index = {leaf: index for index, leaf in enumerate(all_raw_leaves)}
    vectors = {
        node: sum(1 << leaf_index[leaf] for leaf in node_leaves)
        for node, node_leaves in leaves.items()
    }

    result_components = []
    all_output_vectors = []
    for members in sorted(components, key=lambda item: min(item)):
        degree_histogram = Counter(len(adjacency[node]) for node in members)
        endpoints = sorted(node for node in members if len(adjacency[node]) == 1)
        ordered: list[str] = []
        if len(endpoints) == 2:
            previous = None
            current = endpoints[0]
            while current is not None:
                ordered.append(current)
                following = [neighbor for neighbor in adjacency[current] if neighbor != previous]
                previous, current = current, (following[0] if following else None)
        else:
            ordered = sorted(members)

        component_edges = [
            edge for edge in sorted(edges) if edge[0] in members and edge[1] in members
        ]
        output_vectors = [vectors[left] ^ vectors[right] for left, right in component_edges]
        all_output_vectors.extend(output_vectors)
        result_components.append(
            {
                "vertices": len(members),
                "edges": len(component_edges),
                "degree_histogram": dict(sorted(degree_histogram.items())),
                "is_path": len(endpoints) == 2 and len(component_edges) + 1 == len(members),
                "ordered_nodes": ordered,
                "ordered_leaf_pairs": [leaves[node] for node in ordered],
                "distinct_raw_leaves": len(
                    {leaf for node in members for leaf in leaves[node]}
                ),
                "vertex_rank": gf2_rank(vectors[node] for node in members),
                "output_rank": gf2_rank(output_vectors),
                "raw_leaf_reuse": {
                    repr(leaf): count
                    for leaf, count in sorted(
                        Counter(leaf for node in members for leaf in leaves[node]).items(),
                        key=lambda item: leaf_sort_key(item[0]),
                    )
                    if count > 1
                },
            }
        )

    result = {
        "schema": 1,
        "model": "undirected graph of real first-layer XOR terminals",
        "vertices": len(adjacency),
        "edges": len(edges),
        "components": result_components,
        "all_distinct_raw_leaves": len(all_raw_leaves),
        "all_vertex_rank": gf2_rank(vectors.values()),
        "all_output_rank": gf2_rank(all_output_vectors),
        "global_raw_leaf_reuse": {
            repr(leaf): count
            for leaf, count in sorted(
                Counter(leaf for node_leaves in leaves.values() for leaf in node_leaves).items(),
                key=lambda item: leaf_sort_key(item[0]),
            )
            if count > 1
        },
    }
    output = HERE / "actual_graph_analysis.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
