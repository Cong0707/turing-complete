"""Independent source-shell, liveness, and accounting audit for one ranked case.

The auditor does not import the ranker or synthesis worker.  It recomputes the
cut interface, latest deadlines, private consumer closure, ancestor source
shells, exact packed truth partitions, structural cut liveness, current
primitive decomposition, and same-cost complete-gate projection directly from
the authoritative Factory DAG and connected-cut catalogue.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FRONTIER_DIR = HERE.parent
DEFAULT_RANKING = HERE / "same_cost_private_frontier_ranking.json"
CATALOGUE = FRONTIER_DIR / "connected_multi_output_cuts_cost12.json"
DAG = ROOT / ".research/byte_adder_root/byte-adder-hybrid-phasefold-g80-d7.json"
MATERIALIZER = ROOT / ".research/byte_adder_builder_layout_agent/materialize_factory_dag.py"
FULL_ROWS = 1 << 17
FULL_MASK = (1 << FULL_ROWS) - 1


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def atomic_write(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)
    return sha256(data).hexdigest()


def find_case(ranking: dict[str, Any], case_key: str) -> dict[str, Any]:
    matches = [
        row
        for field in ("ranked_candidates", "frozen_cases")
        for row in ranking.get(field, ())
        if row.get("case_key") == case_key
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected one case {case_key!r}, got {len(matches)}")
    return matches[0]


def exact_partition(source_ids: tuple[int, ...], states: dict[int, dict[str, int]]) -> list[int]:
    blocks = [FULL_MASK]
    for node_id in source_ids:
        for mask in (int(states[node_id]["bits"]), int(states[node_id]["driven"])):
            if mask in (0, FULL_MASK):
                continue
            inverse = FULL_MASK ^ mask
            refined = []
            for block in blocks:
                one = block & mask
                zero = block & inverse
                if one:
                    refined.append(one)
                if zero:
                    refined.append(zero)
            blocks = refined
    return blocks


def targets_are_functions(
    blocks: list[int], target_ids: tuple[int, ...], states: dict[int, dict[str, int]]
) -> bool:
    for target_id in target_ids:
        bits = int(states[target_id]["bits"])
        inverse = FULL_MASK ^ bits
        for block in blocks:
            if block & bits and block & inverse:
                return False
    return True


def compositions(bound: int) -> list[dict[str, int]]:
    rows = []
    for ordinary in range(bound + 1):
        for switches in range(bound // 2 + 1):
            for xors in range(bound // 3 + 1):
                if ordinary + 2 * switches + 3 * xors == bound:
                    rows.append(
                        {
                            "ordinary": ordinary,
                            "components": ordinary + switches + xors,
                            "switches": switches,
                            "xors": xors,
                        }
                    )
    return sorted(rows, key=lambda row: (-row["components"], -row["switches"], row["xors"]))


def current_decomposition(cut: tuple[int, ...], nodes: dict[int, dict[str, Any]]) -> dict[str, int]:
    ordinary = switches = xors = 0
    for node_id in cut:
        node = nodes[node_id]
        if node["op"] == "BUS":
            switches += len(node.get("drivers", ()))
        elif node["op"] == "XOR":
            xors += 1
        else:
            ordinary += 1
    return {
        "ordinary": ordinary,
        "components": ordinary + switches + xors,
        "switches": switches,
        "xors": xors,
        "weighted_gate": ordinary + 2 * switches + 3 * xors,
    }


def latest_deadlines(
    ordered_ids: tuple[int, ...],
    nodes: dict[int, dict[str, Any]],
    consumers: dict[int, set[int]],
    outputs: set[int],
) -> dict[int, int]:
    infinity = 1 << 30
    latest = {node_id: infinity for node_id in ordered_ids}
    for node_id in outputs:
        latest[node_id] = 7
    for node_id in reversed(ordered_ids):
        downstream = [
            latest[consumer] - int(nodes[consumer]["step_delay"])
            for consumer in consumers[node_id]
            if latest[consumer] < infinity
        ]
        if downstream:
            latest[node_id] = min(latest[node_id], min(downstream))
    if any(latest[node_id] == infinity for node_id in ordered_ids):
        raise RuntimeError("authoritative DAG contains a node not reaching a public output")
    return latest


def ancestors_of_frontier(
    frontier: tuple[int, ...],
    cut: set[int],
    predecessors: dict[int, tuple[int, ...]],
    order: dict[int, int],
) -> tuple[int, ...]:
    seen = set()
    stack = list(frontier)
    while stack:
        node_id = stack.pop()
        if node_id in seen:
            continue
        seen.add(node_id)
        stack.extend(predecessors[node_id])
    return tuple(sorted(seen - cut, key=order.__getitem__))


def format_report(payload: dict[str, Any]) -> str:
    lines = [
        f"# Byte Adder 80/7：{payload['case_key']} source-shell/liveness 独立审计",
        "",
        "## 结论",
        "",
        f"cut `{payload['cut_node_ids']}`、targets `{payload['target_names']}`、private frontier "
        f"`{payload['private_frontier_id']}` 的同成本 shell 会计与完整 source partition 均通过。",
        "",
        f"- current/local exact cost：{payload['current_cut_gate']}；",
        f"- guaranteed prune：`{payload['guaranteed_prune_ids']}` / cost {payload['guaranteed_prune_cost']}；",
        f"- projected complete：`{payload['projected_complete_gate']}/7/{payload['projected_complete_energy']}`；",
        f"- expanded/no-private rows：{payload['expanded_compressed_truth_rows']}/{payload['no_private_compressed_truth_rows']}；",
        f"- no-private sources：{payload['no_private_source_count']}；exact compositions：{payload['exact_composition_count']}。",
        "",
        "## 已独立复核",
        "",
        "- cut paid/connectivity/convexity、target boundary、retained frontier 与 backward latest deadlines；",
        "- 每个 cut 组件在 cut 内可达至少一个 target，当前 primitive decomposition 与 weighted cost 精确；",
        "- private node 的完整 consumer 集非空且完全位于 cut，且 no-private shell 中不存在其 descendant；",
        "- 两个 source shells 均来自 retained frontier 的完整祖先闭包，targets 对完整 packed source signature 函数确定；",
        "- 此报告只证明 source-shell/liveness/accounting 合同，不预先宣称 exact SAT/UNSAT。",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranking", type=Path, default=DEFAULT_RANKING)
    parser.add_argument("--case-key", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    ranking = json.loads(args.ranking.read_text(encoding="utf-8"))
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    dag = json.loads(DAG.read_text(encoding="utf-8"))
    case = find_case(ranking, args.case_key)
    if ranking["authoritative"]["catalogue_sha256"] != digest(CATALOGUE):
        raise RuntimeError("ranking/catalogue SHA mismatch")
    if ranking["authoritative"]["dag_sha256"] != digest(DAG):
        raise RuntimeError("ranking/DAG SHA mismatch")
    catalogue_rows = [row for row in catalogue["cuts"] if row["cut_key"] == case["cut_key"]]
    if len(catalogue_rows) != 1:
        raise RuntimeError("catalogue cut key is not unique")
    catalogue_case = catalogue_rows[0]

    ordered_nodes_raw = tuple(dag["factory_dag"]["nodes"])
    ordered_ids = tuple(int(node["id"]) for node in ordered_nodes_raw)
    nodes = {int(node["id"]): node for node in ordered_nodes_raw}
    order = {node_id: index for index, node_id in enumerate(ordered_ids)}
    predecessors = {
        node_id: tuple(map(int, nodes[node_id].get("args", ()))) for node_id in ordered_ids
    }
    consumers = {node_id: set() for node_id in ordered_ids}
    for node_id, pred in predecessors.items():
        for predecessor in pred:
            consumers[predecessor].add(node_id)
    outputs = set(map(int, dag["factory_dag"]["outputs"]))
    latest = latest_deadlines(ordered_ids, nodes, consumers, outputs)
    cut_tuple = tuple(map(int, case["cut_node_ids"]))
    cut = set(cut_tuple)
    private_id = int(case["private_frontier_id"])
    target_ids = tuple(
        node_id for node_id in cut_tuple
        if node_id in outputs or bool(consumers[node_id] - cut)
    )
    retained = tuple(sorted(
        {predecessor for node_id in cut for predecessor in predecessors[node_id] if predecessor not in cut},
        key=order.__getitem__,
    ))
    if list(cut_tuple) != list(map(int, catalogue_case["cut_node_ids"])):
        raise RuntimeError("ranking/catalogue cut differs")
    if target_ids != tuple(map(int, case["target_ids"])) or target_ids != tuple(map(int, catalogue_case["target_ids"])):
        raise RuntimeError("target boundary differs")
    if retained != tuple(map(int, case["retained_frontier_ids"])):
        raise RuntimeError("retained frontier differs")
    deadlines = tuple(latest[node_id] for node_id in target_ids)
    if deadlines != tuple(map(int, case["target_deadlines"])):
        raise RuntimeError("latest target deadlines differ")
    if tuple(bool(nodes[node_id]["may_z"]) for node_id in target_ids) != tuple(map(bool, case["target_may_z"])):
        raise RuntimeError("target Z policy differs")

    paid = {node_id for node_id in ordered_ids if int(nodes[node_id]["cost"]) > 0}
    if not cut <= paid:
        raise RuntimeError("cut contains a free node")
    adjacency = {node_id: set() for node_id in cut}
    for node_id in cut:
        for predecessor in predecessors[node_id]:
            if predecessor in cut:
                adjacency[node_id].add(predecessor)
                adjacency[predecessor].add(node_id)
    visited = set()
    stack = [cut_tuple[0]]
    while stack:
        node_id = stack.pop()
        if node_id in visited:
            continue
        visited.add(node_id)
        stack.extend(adjacency[node_id] - visited)
    if visited != cut:
        raise RuntimeError("cut is not connected")
    ancestors = {node_id: set() for node_id in ordered_ids}
    for node_id in ordered_ids:
        for predecessor in predecessors[node_id]:
            ancestors[node_id].add(predecessor)
            ancestors[node_id].update(ancestors[predecessor])
    descendants = {node_id: set() for node_id in ordered_ids}
    for node_id in reversed(ordered_ids):
        for consumer in consumers[node_id]:
            descendants[node_id].add(consumer)
            descendants[node_id].update(descendants[consumer])
    if any(ancestors[outside] & cut and descendants[outside] & cut for outside in set(ordered_ids) - cut):
        raise RuntimeError("cut is not DAG-convex")
    live = set(target_ids)
    changed = True
    while changed:
        changed = False
        for node_id in cut - live:
            if consumers[node_id] & live:
                live.add(node_id)
                changed = True
    if live != cut:
        raise RuntimeError(f"cut contains target-dead nodes: {sorted(cut-live)}")

    private_consumers = consumers[private_id]
    if not private_consumers or not private_consumers <= cut or private_id in outputs:
        raise RuntimeError("private frontier is not guaranteed prunable")
    expanded_sources = ancestors_of_frontier(retained, cut, predecessors, order)
    no_private_sources = tuple(node_id for node_id in expanded_sources if node_id != private_id)
    if private_id not in expanded_sources or descendants[private_id] & set(no_private_sources):
        raise RuntimeError("no-private source shell still depends on private node")
    if list(expanded_sources) != list(map(int, case["expanded_source_ids"])):
        raise RuntimeError("expanded source shell differs from ranking")
    if list(no_private_sources) != list(map(int, case["no_private_source_ids"])):
        raise RuntimeError("no-private source shell differs from ranking")

    materializer = load_module(MATERIALIZER, "ranked_private_case_audit_materializer")
    states = materializer.logical_states(ordered_nodes_raw)
    expanded_blocks = exact_partition(expanded_sources, states)
    no_private_blocks = exact_partition(no_private_sources, states)
    if not targets_are_functions(expanded_blocks, target_ids, states) or not targets_are_functions(no_private_blocks, target_ids, states):
        raise RuntimeError("target/source functional audit failed")
    if len(expanded_blocks) != int(case["expanded_compressed_truth_rows"]):
        raise RuntimeError("expanded row count differs from ranking")
    if len(no_private_blocks) != int(case["no_private_compressed_truth_rows"]):
        raise RuntimeError("no-private row count differs from ranking")

    decomposition = current_decomposition(cut_tuple, nodes)
    current_cost = sum(int(nodes[node_id]["cost"]) for node_id in cut)
    private_cost = int(nodes[private_id]["cost"])
    projected = 80 - current_cost - private_cost + current_cost
    if decomposition != case["current_decomposition"] or decomposition["weighted_gate"] != current_cost:
        raise RuntimeError("current decomposition/cost differs")
    if projected != int(case["projected_complete_gate"]):
        raise RuntimeError("same-cost projection differs")
    domain = compositions(current_cost)
    if {
        (row["ordinary"], row["components"], row["switches"], row["xors"])
        for row in domain
    } != {
        (int(row["ordinary"]), int(row["components"]), int(row["switches"]), int(row["xors"]))
        for row in case["exact_compositions"]
    }:
        raise RuntimeError("exact composition domain differs")

    payload = {
        "schema": "byte-adder-80d7-ranked-private-frontier-case-audit-v1",
        "audit_pass": True,
        "case_key": args.case_key,
        "ranking": args.ranking.resolve().relative_to(ROOT).as_posix(),
        "ranking_sha256": digest(args.ranking),
        "catalogue_sha256": digest(CATALOGUE),
        "dag_sha256": digest(DAG),
        "materializer_sha256": digest(MATERIALIZER),
        "auditor_sha256": digest(Path(__file__).resolve()),
        "cut_node_ids": list(cut_tuple),
        "cut_connected": True,
        "cut_convex": True,
        "cut_liveness_complete": True,
        "current_cut_gate": current_cost,
        "current_decomposition": decomposition,
        "target_ids": list(target_ids),
        "target_names": list(case["target_names"]),
        "target_deadlines": list(deadlines),
        "target_may_z": list(map(bool, case["target_may_z"])),
        "retained_frontier_ids": list(retained),
        "private_frontier_id": private_id,
        "private_frontier_consumers": sorted(private_consumers),
        "guaranteed_prune_ids": [private_id],
        "guaranteed_prune_cost": private_cost,
        "expanded_source_ids": list(expanded_sources),
        "expanded_source_count": len(expanded_sources),
        "expanded_compressed_truth_rows": len(expanded_blocks),
        "no_private_source_ids": list(no_private_sources),
        "no_private_source_count": len(no_private_sources),
        "no_private_compressed_truth_rows": len(no_private_blocks),
        "targets_functional_in_both_shells": True,
        "private_descendant_absent_from_no_private_shell": True,
        "replacement_exact_bound": current_cost,
        "fixed_shell_after_guaranteed_prune": 80 - current_cost - private_cost,
        "projected_complete_gate": projected,
        "projected_complete_delay": 7,
        "projected_complete_energy": projected * 7,
        "exact_compositions": domain,
        "exact_composition_count": len(domain),
        "conclusion": "source-shell, liveness, and same-cost private-prune accounting are complete; exact SAT status remains to be solved",
    }
    output_sha = atomic_write(
        args.output, (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    report_sha = atomic_write(args.report, format_report(payload).encode("utf-8"))
    print(json.dumps({
        "output": str(args.output.resolve()), "output_sha256": output_sha,
        "report": str(args.report.resolve()), "report_sha256": report_sha,
        "audit_pass": True, "case_key": args.case_key,
        "projected_complete_gate": projected,
        "expanded_rows": len(expanded_blocks), "no_private_rows": len(no_private_blocks),
        "exact_composition_count": len(domain),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
