"""Exact tree-aware search in C-row radius four around a research candidate.

Removing four labelled edges from the candidate tree produces five connected
components.  Every kept edge fixes relative T values inside its component, so
all T rows in component c change by one common XOR offset delta[c].  A new
labelled edge determines the child offset immediately.  This script enumerates
all 125 component-tree shapes, all 24 assignments of the removed labels, and
all endpoint choices, pruning as soon as a component contains a T row heavier
than four or a fully determined B row violates its weight/capacity bound.

The search is offline and reads only the explicitly supplied research JSONL.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
import ctypes
from itertools import combinations, permutations, product
import json
import os
from pathlib import Path
import random
import threading
import time
from typing import Iterable, Sequence


N = 32
GROUND = N
MASK = (1 << N) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    return tuple(
        sum(((function(1 << source) >> output) & 1) << source for source in range(N))
        for output in range(N)
    )


A = matrix_from_function(xorshift32)


def support(mask: int) -> tuple[int, ...]:
    result = []
    while mask:
        low = mask & -mask
        result.append(low.bit_length() - 1)
        mask ^= low
    return tuple(result)


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
    return sum(
        ((row & value).bit_count() & 1) << output
        for output, row in enumerate(matrix)
    )


def working_set_bytes() -> int:
    if os.name != "nt":
        try:
            import resource

            return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
        except (ImportError, OSError):
            return 0
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    query = kernel32.K32GetProcessMemoryInfo
    query.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    query.restype = wintypes.BOOL
    if not query(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        return 0
    return int(counters.WorkingSetSize)


def load_candidate(path: Path) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    record = None
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                candidate = json.loads(line)
                if all(key in candidate for key in ("C", "T", "B")):
                    record = candidate
    if record is None:
        raise ValueError(f"no complete candidate in {path}")
    return tuple(
        tuple(int(value, 16) for value in record[key])
        for key in ("C", "T", "B")
    )


def edge_from_row(row: int) -> tuple[int, int]:
    vertices = support(row)
    if len(vertices) == 1:
        return (vertices[0], GROUND)
    if len(vertices) == 2:
        return vertices
    raise ValueError("C row is not a tree edge")


def row_from_edge(edge: tuple[int, int]) -> int:
    result = 0
    for vertex in edge:
        if vertex != GROUND:
            result ^= 1 << vertex
    return result


def component_tree_shapes(count: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    """All labelled trees via their Prufer sequences."""

    result = []
    for code in product(range(count), repeat=count - 2):
        degree = [1] * count
        for value in code:
            degree[value] += 1
        edges = []
        for value in code:
            leaf = next(index for index, item in enumerate(degree) if item == 1)
            edges.append(tuple(sorted((leaf, value))))
            degree[leaf] -= 1
            degree[value] -= 1
        leaves = [index for index, item in enumerate(degree) if item == 1]
        edges.append(tuple(sorted(leaves)))
        result.append(tuple(sorted(edges)))
    if len(result) != count ** (count - 2) or len(set(result)) != len(result):
        raise AssertionError("Prufer tree enumeration failed")
    return tuple(result)


SHAPES = component_tree_shapes(5)


def split_components(
    edges: Sequence[tuple[int, int]], removed: frozenset[int]
) -> tuple[tuple[int, ...], ...]:
    adjacency = [[] for _ in range(N + 1)]
    for label, (left, right) in enumerate(edges):
        if label in removed:
            continue
        adjacency[left].append(right)
        adjacency[right].append(left)
    unseen = set(range(N + 1))
    components = []
    while unseen:
        start = GROUND if GROUND in unseen else min(unseen)
        queue = [start]
        unseen.remove(start)
        component = []
        while queue:
            vertex = queue.pop()
            component.append(vertex)
            for neighbour in adjacency[vertex]:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    queue.append(neighbour)
        components.append(tuple(sorted(component)))
    components.sort(key=lambda value: (GROUND not in value, value))
    if len(components) != 5 or GROUND not in components[0]:
        raise AssertionError("four tree edges did not produce five components")
    return tuple(components)


def orient_shape(
    shape: Sequence[tuple[int, int]], labels: Sequence[int]
) -> tuple[tuple[int, int, int], ...]:
    label_by_edge = dict(zip(shape, labels))
    adjacency = [[] for _ in range(5)]
    for left, right in shape:
        label = label_by_edge[(left, right)]
        adjacency[left].append((right, label))
        adjacency[right].append((left, label))
    queue = deque([0])
    seen = {0}
    directed = []
    while queue:
        parent = queue.popleft()
        for child, label in sorted(adjacency[parent]):
            if child in seen:
                continue
            seen.add(child)
            queue.append(child)
            directed.append((parent, child, label))
    if len(directed) != 4:
        raise AssertionError("component tree orientation failed")
    return tuple(directed)


def verify_candidate(C: Sequence[int], T: Sequence[int], B: Sequence[int]) -> dict[str, object]:
    if compose(C, T) != A:
        raise AssertionError("C*T != A")
    if compose(T, C) != tuple(B):
        raise AssertionError("T*C != B")
    if max(row.bit_count() for row in C) > 2:
        raise AssertionError("C is not shallow")
    if max(row.bit_count() for row in T) > 4:
        raise AssertionError("T exceeds support four")
    if max(row.bit_count() for row in B) > 4:
        raise AssertionError("B exceeds support four")
    if any(t.bit_count() > b.bit_count() for t, b in zip(T, B)):
        raise AssertionError("tick-zero label capacity failed")

    seeds = [0, 1, 2, 0x12345678, MASK]
    seeds.extend(random.Random(0x5A1109).getrandbits(32) for _ in range(64))
    for seed in seeds:
        encoded = apply_matrix(T, seed)
        natural = seed
        for _ in range(65):
            natural = xorshift32(natural)
            if apply_matrix(C, encoded) != natural:
                raise AssertionError("visible replay failed")
            encoded = apply_matrix(B, encoded)

    def histogram(rows: Sequence[int]) -> dict[str, int]:
        return {
            str(weight): count
            for weight, count in sorted(Counter(row.bit_count() for row in rows).items())
        }

    return {
        "C": [f"{row:08x}" for row in C],
        "T": [f"{row:08x}" for row in T],
        "B": [f"{row:08x}" for row in B],
        "row_weight_histograms": {
            "C": histogram(C),
            "T": histogram(T),
            "B": histogram(B),
        },
        "verified_seed_count": len(seeds),
        "verified_outputs_per_seed": 65,
    }


def solve(args: argparse.Namespace) -> dict[str, object]:
    started = time.perf_counter()
    C0, T0, B0 = load_candidate(args.start)
    if compose(C0, T0) != A or compose(T0, C0) != B0:
        raise AssertionError("start matrices are inconsistent")
    edges0 = tuple(edge_from_row(row) for row in C0)
    state0 = tuple(T0) + (0,)
    heavy = tuple(
        row
        for row in range(N)
        if T0[row].bit_count() > 4
    )
    if not heavy:
        raise ValueError("start has no heavy T row")

    stopped = threading.Event()
    stop_reason = [None]
    peak = [working_set_bytes()]

    def watchdog() -> None:
        deadline = started + args.timeout_seconds
        limit = args.memory_mb * 1024 * 1024
        while not stopped.wait(0.05):
            current = working_set_bytes()
            peak[0] = max(peak[0], current)
            if current > limit:
                stop_reason[0] = "memory_limit"
                return
            if time.perf_counter() >= deadline:
                stop_reason[0] = "timeout"
                return

    thread = threading.Thread(target=watchdog, daemon=True)
    thread.start()

    removed_sets_total = 0
    removed_sets_pruned_root = 0
    removed_sets_searched = 0
    shape_assignments = 0
    offset_branches = 0
    full_trees = 0
    partial_b_prunes = 0
    result_matrices = None
    result_removed = None
    result_edges = None

    all_removed = [
        tuple(values)
        for values in combinations(range(N), 4)
        if 16 in values and (12 in values or 29 in values)
    ]
    # Search subsets touching the heavy paths and small branches first, while
    # preserving a deterministic order for reproducibility.
    all_removed.sort(
        key=lambda values: (
            -(12 in values) - (29 in values),
            sum(T0[vertex].bit_count() for label in values for vertex in edges0[label] if vertex != GROUND),
            values,
        )
    )

    def partial_rows_valid(
        components: Sequence[Sequence[int]],
        deltas: Sequence[int | None],
        chosen_edges: Sequence[tuple[int, int] | None],
    ) -> bool:
        nonlocal partial_b_prunes
        for component_index, component in enumerate(components):
            delta = deltas[component_index]
            if delta is None:
                continue
            for vertex in component:
                if vertex == GROUND:
                    continue
                t_row = T0[vertex] ^ delta
                if t_row.bit_count() > 4:
                    partial_b_prunes += 1
                    return False
                labels = support(t_row)
                if any(chosen_edges[label] is None for label in labels):
                    continue
                b_row = 0
                for label in labels:
                    edge = chosen_edges[label]
                    assert edge is not None
                    b_row ^= row_from_edge(edge)
                b_weight = b_row.bit_count()
                if b_weight > 4 or t_row.bit_count() > b_weight:
                    partial_b_prunes += 1
                    return False
        return True

    try:
        for removed_tuple in all_removed:
            if stop_reason[0] is not None or result_matrices is not None:
                break
            removed_sets_total += 1
            removed = frozenset(removed_tuple)
            components = split_components(edges0, removed)
            root_component = set(components[0])
            if any(vertex in root_component for vertex in heavy):
                removed_sets_pruned_root += 1
                continue
            removed_sets_searched += 1
            component_of = {
                vertex: index
                for index, component in enumerate(components)
                for vertex in component
            }
            if any(
                component_of[left] == component_of[right]
                for label in removed
                for left, right in (edges0[label],)
            ):
                raise AssertionError("removed edge endpoints stayed in one component")

            chosen_edges: list[tuple[int, int] | None] = [
                None if label in removed else edge
                for label, edge in enumerate(edges0)
            ]
            deltas: list[int | None] = [0, None, None, None, None]

            # Kept-only B rows in the root component can reject the subset
            # before any component topology is considered.
            if not partial_rows_valid(components, deltas, chosen_edges):
                continue

            for shape in SHAPES:
                if stop_reason[0] is not None or result_matrices is not None:
                    break
                for assigned_labels in permutations(removed_tuple):
                    if stop_reason[0] is not None or result_matrices is not None:
                        break
                    shape_assignments += 1
                    directed = orient_shape(shape, assigned_labels)

                    def dfs(depth: int) -> None:
                        nonlocal offset_branches, full_trees, result_matrices
                        nonlocal result_removed, result_edges
                        if stop_reason[0] is not None or result_matrices is not None:
                            return
                        if depth == len(directed):
                            full_trees += 1
                            C = tuple(row_from_edge(edge) for edge in chosen_edges if edge is not None)
                            if len(C) != N:
                                raise AssertionError("incomplete C at DFS leaf")
                            T = tuple(
                                T0[vertex] ^ int(deltas[component_of[vertex]])
                                for vertex in range(N)
                            )
                            B = compose(T, C)
                            if max(row.bit_count() for row in B) > 4:
                                return
                            if any(t.bit_count() > b.bit_count() for t, b in zip(T, B)):
                                return
                            result_matrices = (C, T, B)
                            result_removed = removed_tuple
                            result_edges = tuple(chosen_edges)
                            return

                        parent, child, label = directed[depth]
                        parent_delta = deltas[parent]
                        if parent_delta is None or deltas[child] is not None:
                            raise AssertionError("component traversal order is invalid")

                        # Equal child offsets can arise from several endpoint
                        # pairs.  Keep all pairs because B depends on endpoints,
                        # but reject the entire offset group if T is heavy.
                        by_delta: dict[int, list[tuple[int, int]]] = {}
                        for left in components[parent]:
                            for right in components[child]:
                                child_delta = int(parent_delta) ^ state0[left] ^ state0[right] ^ A[label]
                                by_delta.setdefault(child_delta, []).append((left, right))
                        for child_delta, endpoint_pairs in by_delta.items():
                            if any(
                                vertex != GROUND
                                and (T0[vertex] ^ child_delta).bit_count() > 4
                                for vertex in components[child]
                            ):
                                continue
                            deltas[child] = child_delta
                            for edge in endpoint_pairs:
                                offset_branches += 1
                                chosen_edges[label] = edge
                                if partial_rows_valid(components, deltas, chosen_edges):
                                    dfs(depth + 1)
                                chosen_edges[label] = None
                                if stop_reason[0] is not None or result_matrices is not None:
                                    break
                            deltas[child] = None
                            if stop_reason[0] is not None or result_matrices is not None:
                                break

                    dfs(0)
                    if args.max_shape_assignments and shape_assignments >= args.max_shape_assignments:
                        stop_reason[0] = "assignment_limit"
                        break
            if removed_sets_searched % 10 == 0:
                print(
                    json.dumps(
                        {
                            "removed_sets_searched": removed_sets_searched,
                            "shape_assignments": shape_assignments,
                            "offset_branches": offset_branches,
                            "full_trees": full_trees,
                        }
                    ),
                    flush=True,
                )
            if args.max_removed_sets and removed_sets_searched >= args.max_removed_sets:
                stop_reason[0] = "subset_limit"
                break
    finally:
        stopped.set()
        thread.join(timeout=1.0)
        peak[0] = max(peak[0], working_set_bytes())

    status = "sat" if result_matrices is not None else (
        "unsat" if stop_reason[0] is None else "unknown"
    )
    report: dict[str, object] = {
        "schema": 1,
        "status": status,
        "reason_unknown": stop_reason[0],
        "scope": "exact C-row Hamming radius <=4 around start; shallow C, T/B<=4, tick-zero capacity",
        "start": str(args.start),
        "start_heavy_T_rows": list(heavy),
        "forced_removed_labels": [16, "12_or_29"],
        "eligible_removed_set_count": len(all_removed),
        "removed_sets_visited": removed_sets_total,
        "removed_sets_pruned_by_root_component": removed_sets_pruned_root,
        "removed_sets_searched": removed_sets_searched,
        "component_tree_shape_count": len(SHAPES),
        "shape_assignments": shape_assignments,
        "offset_endpoint_branches": offset_branches,
        "complete_trees_checked": full_trees,
        "partial_B_or_T_prunes": partial_b_prunes,
        "timeout_seconds": args.timeout_seconds,
        "memory_limit_mb": args.memory_mb,
        "peak_working_set_mb": peak[0] / 1048576,
        "elapsed_seconds": time.perf_counter() - started,
    }
    if result_matrices is not None:
        C, T, B = result_matrices
        report["changed_labels"] = [
            label for label in range(N) if C[label] != C0[label]
        ]
        report["enumerated_removed_labels"] = list(result_removed or ())
        report["selected_edges"] = [list(edge) for edge in result_edges or ()]
        report["certificate"] = verify_candidate(C, T, B)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=600.0)
    parser.add_argument("--memory-mb", type=int, default=680)
    parser.add_argument("--max-removed-sets", type=int, default=0)
    parser.add_argument("--max-shape-assignments", type=int, default=0)
    args = parser.parse_args()
    result = solve(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps({key: value for key, value in result.items() if key != "certificate"}, indent=2),
        flush=True,
    )
    return 0 if result["status"] in {"sat", "unsat"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
