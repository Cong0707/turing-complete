"""Independent dual-solver closure audit for ranked case 56-80__no_55.

This auditor intentionally imports neither the ranker, synthesis worker, exact
core, nor materializer.  It recomputes the authoritative Factory DAG packed
semantics over all 2^17 inputs, the no-private source shell and exact source
partition, then checks every persisted CaDiCaL/Glucose result and its summary.

The conclusion is deliberately local: it closes weighted cost five only for
the recorded no-private source shell and does not establish a lower bound for
any other source shell or connected cut.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RANKING = HERE / "same_cost_private_frontier_ranking.json"
DAG = ROOT / ".research/byte_adder_root/byte-adder-hybrid-phasefold-g80-d7.json"
SOURCE_AUDIT = HERE / "case_56_80_no55_source_shell_audit.json"
POSITIVE = HERE / "case_56_80_expanded_g5_positive.json"
WORKER = HERE / "exact_ranked_private_frontier_sat.py"
RUNNER = HERE / "run_ranked_private_frontier_sweep.py"
SOLVER_DIRS = {
    "cadical195": HERE / "case_56_80_no55_cadical195",
    "glucose42": HERE / "case_56_80_no55_glucose42",
}

ROWS = 1 << 17
ALL = (1 << ROWS) - 1
EXPECTED_COMPOSITIONS = (
    (0, 2, 1, 1),
    (1, 3, 2, 0),
    (2, 3, 0, 1),
    (3, 4, 1, 0),
    (5, 5, 0, 0),
)
GATE_SPECS = {
    "NOT": (1, 1, 1),
    "AND": (1, 1, 2),
    "NAND": (1, 1, 2),
    "OR": (1, 1, 2),
    "NOR": (1, 1, 2),
    "XOR": (3, 2, 2),
    "XNOR": (3, 2, 2),
}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)
    return sha256(data).hexdigest()


def variable(index: int) -> int:
    if index < 3:
        return int.from_bytes(bytes([(0xAA, 0xCC, 0xF0)[index]]) * (ROWS // 8), "little")
    block = 1 << (index - 3)
    data = (bytes(block) + bytes([0xFF]) * block) * (ROWS // (16 * block))
    return int.from_bytes(data, "little")


def replay(nodes: tuple[dict[str, Any], ...]) -> dict[int, dict[str, int]]:
    inputs = {
        **{f"a{bit}": variable(bit) for bit in range(8)},
        **{f"b{bit}": variable(8 + bit) for bit in range(8)},
        "cin": variable(16),
    }
    states: dict[int, dict[str, int]] = {}
    for node in nodes:
        node_id = int(node["id"])
        op = str(node["op"])
        arguments = tuple(int(value) for value in node.get("args", ()))
        if any(argument not in states for argument in arguments):
            raise RuntimeError(f"node {node_id} is not topologically serialized")
        args = tuple(states[argument] for argument in arguments)
        if op == "CONST":
            bits = ALL if str(node.get("label")) == "1" else 0
            state = {"bits": bits, "driven": ALL, "conflict": 0, "arrival": 0}
            expected_cost, expected_step, expected_arity = 0, 0, 0
        elif op == "INPUT":
            if str(node.get("label")) not in inputs:
                raise RuntimeError(f"unknown input at node {node_id}")
            state = {
                "bits": inputs[str(node["label"])],
                "driven": ALL,
                "conflict": 0,
                "arrival": 0,
            }
            expected_cost, expected_step, expected_arity = 0, 0, 0
        elif op == "BUS":
            if not arguments or len(arguments) % 2:
                raise RuntimeError(f"BUS {node_id} has incomplete drivers")
            ones = zeros = driven = conflict = 0
            for offset in range(0, len(args), 2):
                enable, data = args[offset : offset + 2]
                active = enable["bits"]
                ones |= active & data["bits"]
                zeros |= active & (~data["bits"] & ALL)
                driven |= active
                conflict |= enable["conflict"] | data["conflict"]
            conflict |= ones & zeros
            state = {
                "bits": ones & ALL,
                "driven": driven & ALL,
                "conflict": conflict & ALL,
                "arrival": max(value["arrival"] for value in args) + 1,
            }
            expected_cost = len(arguments)
            expected_step = 1
            expected_arity = len(arguments)
            drivers = node.get("drivers")
            if not isinstance(drivers, list) or len(drivers) * 2 != len(arguments):
                raise RuntimeError(f"BUS {node_id} driver metadata differs")
            for index, driver in enumerate(drivers):
                if (
                    int(driver["enable"]) != arguments[index * 2]
                    or int(driver["data"]) != arguments[index * 2 + 1]
                    or driver.get("owner") != node.get("resolved_network")
                ):
                    raise RuntimeError(f"BUS {node_id} driver ownership differs")
        elif op in GATE_SPECS:
            expected_cost, expected_step, expected_arity = GATE_SPECS[op]
            if len(args) != expected_arity:
                raise RuntimeError(f"{op} {node_id} arity differs")
            left = args[0]["bits"]
            right = args[1]["bits"] if len(args) == 2 else 0
            if op == "NOT":
                bits = ~left
            elif op == "AND":
                bits = left & right
            elif op == "NAND":
                bits = ~(left & right)
            elif op == "OR":
                bits = left | right
            elif op == "NOR":
                bits = ~(left | right)
            elif op == "XOR":
                bits = left ^ right
            else:
                bits = ~(left ^ right)
            conflict = 0
            for value in args:
                conflict |= value["conflict"]
            state = {
                "bits": bits & ALL,
                "driven": ALL,
                "conflict": conflict & ALL,
                "arrival": max(value["arrival"] for value in args) + expected_step,
            }
        else:
            raise RuntimeError(f"unsupported operation {op!r}")
        if len(arguments) != expected_arity:
            raise RuntimeError(f"node {node_id} arity annotation differs")
        if (
            int(node.get("cost", -1)) != expected_cost
            or int(node.get("step_delay", -1)) != expected_step
            or int(node.get("arrival", -1)) != state["arrival"]
            or bool(node.get("may_z")) != (op == "BUS")
        ):
            raise RuntimeError(f"node {node_id} cost/delay/Z annotation differs")
        states[node_id] = state
    return states


def exact_partition(source_ids: tuple[int, ...], states: dict[int, dict[str, int]]) -> list[int]:
    blocks = [ALL]
    for node_id in source_ids:
        for field in ("bits", "driven", "conflict"):
            mask = int(states[node_id][field])
            if mask in (0, ALL):
                continue
            inverse = ALL ^ mask
            refined = []
            for block in blocks:
                zero = block & inverse
                one = block & mask
                if zero:
                    refined.append(zero)
                if one:
                    refined.append(one)
            blocks = refined
    return blocks


def signals_are_functions(
    blocks: list[int], target_ids: tuple[int, ...], states: dict[int, dict[str, int]]
) -> bool:
    for target_id in target_ids:
        for field in ("bits", "driven", "conflict"):
            mask = int(states[target_id][field])
            inverse = ALL ^ mask
            if any(block & mask and block & inverse for block in blocks):
                return False
    return True


def ancestors_of_frontier(
    frontier: tuple[int, ...],
    cut: set[int],
    predecessors: dict[int, tuple[int, ...]],
    order: dict[int, int],
) -> tuple[int, ...]:
    seen: set[int] = set()
    pending = list(frontier)
    while pending:
        node_id = pending.pop()
        if node_id in seen:
            continue
        seen.add(node_id)
        pending.extend(predecessors[node_id])
    return tuple(sorted(seen - cut, key=order.__getitem__))


def find_case(ranking: dict[str, Any], case_key: str) -> dict[str, Any]:
    matches = [
        row
        for field in ("ranked_candidates", "frozen_cases")
        for row in ranking.get(field, ())
        if row.get("case_key") == case_key
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one ranked case {case_key!r}")
    return matches[0]


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def check_summary(
    solver: str,
    directory: Path,
    expected_case: dict[str, Any],
    common_reference: dict[tuple[int, int, int, int], dict[str, Any]] | None,
) -> tuple[dict[str, Any], dict[tuple[int, int, int, int], dict[str, Any]]]:
    authority = json.loads(DAG.read_text(encoding="utf-8"))
    summary_path = directory / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if (
        summary.get("schema") != "byte-adder-80d7-ranked-private-frontier-sweep-v1"
        or summary.get("case_key") != "56-80__no_55"
        or summary.get("source_profile") != "no_private"
        or summary.get("solver") != solver
        or int(summary.get("gate_bound", -1)) != 5
        or int(summary.get("projected_complete_gate", -1)) != 76
        or int(summary.get("expected_case_count", -1)) != 5
        or int(summary.get("executed_case_count", -1)) != 5
        or not bool(summary.get("complete_without_sat"))
        or bool(summary.get("stopped_on_sat"))
        or summary.get("status_counts") != {"unsat": 5}
    ):
        raise RuntimeError(f"{solver} summary closure contract differs")
    if summary.get("ranking_sha256") != digest(RANKING):
        raise RuntimeError(f"{solver} ranking hash differs")
    if summary.get("worker_sha256") != digest(WORKER):
        raise RuntimeError(f"{solver} worker hash differs")
    if summary.get("runner_sha256") != digest(RUNNER):
        raise RuntimeError(f"{solver} runner hash differs")
    expected_rows = [
        {"ordinary": o, "components": n, "switches": s, "xors": x}
        for o, n, s, x in EXPECTED_COMPOSITIONS
    ]
    if summary.get("expected_decompositions") != expected_rows:
        raise RuntimeError(f"{solver} expected composition order differs")

    records: dict[tuple[int, int, int, int], dict[str, Any]] = {}
    result_audit = []
    for summary_row in summary.get("results", ()):
        key = tuple(
            int(summary_row[field])
            for field in ("ordinary", "components", "switches", "xors")
        )
        if key in records:
            raise RuntimeError(f"{solver} repeats composition {key}")
        result_path = ROOT / str(summary_row["result"])
        if result_path.parent.resolve() != (directory / "results").resolve():
            raise RuntimeError(f"{solver} result escapes its evidence directory")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        result_sha = digest(result_path)
        if result_sha != summary_row.get("result_sha256"):
            raise RuntimeError(f"{solver} result hash differs for {key}")
        invariant = {
            "schema": "byte-adder-80d7-ranked-private-frontier-same-cost-v1",
            "status": "unsat",
            "case_key": "56-80__no_55",
            "source_profile": "no_private",
            "private_frontier_id": 55,
            "private_frontier_consumers": [56],
            "guaranteed_prune_ids": [55],
            "guaranteed_prune_cost": 4,
            "fixed_shell_after_guaranteed_prune": 71,
            "projected_complete_gate_at_bound": 76,
            "projected_complete_delay": 7,
            "projected_complete_energy": 532,
            "full_truth_rows": ROWS,
            "compressed_truth_rows": 128,
            "cut_node_ids": [56, 80],
            "target_ids": [56, 80],
            "target_names": ["C3", "n80"],
            "output_deadlines": [3, 6],
            "allow_z_false_outputs": [True, False],
            "gate_bound": 5,
            "weighted_gate": 5,
            "seed_current": False,
            "seed_contract": None,
            "physical_nets": True,
            "all_components_live": True,
            "solver": solver,
        }
        for field, expected in invariant.items():
            if result.get(field) != expected:
                raise RuntimeError(f"{solver} result {key} field {field} differs")
        if (
            int(result.get("exact_ordinary", -1)) != key[0]
            or int(result.get("components", -1)) != key[1]
            or int(result.get("exact_switches", -1)) != key[2]
            or int(result.get("exact_xors", -1)) != key[3]
            or key[0] + key[2] + key[3] != key[1]
            or key[0] + 2 * key[2] + 3 * key[3] != 5
        ):
            raise RuntimeError(f"{solver} result {key} composition differs")
        if (
            result.get("ranking_sha256") != digest(RANKING)
            or result.get("source_sha256") != digest(DAG)
            or result.get("source_structural_sha256")
            != authority["metrics"]["structural_sha256"]
            or result.get("source_factory_dag_sha256")
            != authority["factory_dag"]["sha256"]
            or result.get("script_sha256") != digest(WORKER)
        ):
            raise RuntimeError(f"{solver} result {key} authority hash differs")
        if list(map(int, result.get("source_ids", ()))) != list(
            map(int, expected_case["no_private_source_ids"])
        ):
            raise RuntimeError(f"{solver} result {key} source shell differs")
        for numeric in ("variables", "clauses"):
            if int(result.get(numeric, 0)) <= 0 or int(summary_row.get(numeric, -1)) != int(
                result[numeric]
            ):
                raise RuntimeError(f"{solver} result {key} {numeric} differs")
        records[key] = result
        result_audit.append(
            {
                "ordinary": key[0],
                "components": key[1],
                "switches": key[2],
                "xors": key[3],
                "variables": int(result["variables"]),
                "clauses": int(result["clauses"]),
                "status": "unsat",
                "path": relative(result_path),
                "sha256": result_sha,
            }
        )
    if set(records) != set(EXPECTED_COMPOSITIONS):
        raise RuntimeError(f"{solver} composition coverage differs")
    if common_reference is not None:
        paired_fields = (
            "ranking_sha256",
            "source_sha256",
            "source_structural_sha256",
            "source_factory_dag_sha256",
            "script_sha256",
            "dependency_sha256",
            "source_ids",
            "source_names",
            "source_arrivals",
            "source_driven_one_counts",
            "target_one_counts",
            "target_driven_one_counts",
            "variables",
            "clauses",
        )
        for key, result in records.items():
            if any(result.get(field) != common_reference[key].get(field) for field in paired_fields):
                raise RuntimeError(f"dual-solver CNF/interface mismatch for {key}")
    return (
        {
            "summary": relative(summary_path),
            "summary_sha256": digest(summary_path),
            "launch_stdout_sha256": digest(directory / "launch.stdout.log"),
            "launch_stderr_sha256": digest(directory / "launch.stderr.log"),
            "expected_case_count": 5,
            "executed_case_count": 5,
            "status_counts": {"unsat": 5},
            "complete_without_sat": True,
            "results": result_audit,
        },
        records,
    )


def format_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Byte Adder 80/7: C3/n80 no-BUS55 dual-solver closure",
        "",
        "## Conclusion",
        "",
        "The exact weighted-cost-5 domain for ranked case `56-80__no_55` is "
        "closed as `10/10 UNSAT` across CaDiCaL 1.9.5 and Glucose 4.2.",
        "",
        "- source shell: the complete retained-frontier ancestor closure, minus cut `{56,80}` and exactly private `BUS55`;",
        "- exact packed partition: `128` rows derived from all `131072` U8/U8/U1 assignments;",
        "- projected score at the rejected bound: `76/7/532`;",
        "- positive worker regression: current expanded-shell `g5/n3/s2/x0` is SAT and passes full replay;",
        "- both solvers cover the same five weighted compositions, with identical variables/clauses for every pair;",
        "- all ten result hashes, both summary hashes, source/ranking/worker/runner hashes, and empty stderr logs were checked.",
        "",
        "## CNF Pairs",
        "",
        "| ordinary | components | switches | xors | variables | clauses | CaDiCaL | Glucose |",
        "|---:|---:|---:|---:|---:|---:|:---:|:---:|",
    ]
    for row in payload["paired_cnf_counts"]:
        lines.append(
            f"| {row['ordinary']} | {row['components']} | {row['switches']} | {row['xors']} | "
            f"{row['variables']} | {row['clauses']} | UNSAT | UNSAT |"
        )
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "This is a complete closure only for the recorded no-private source shell and weighted-cost-5 primitive domain. "
            "It is not a lower bound for any different source shell, cut, primitive contract, or projected gate cost.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=HERE / "case_56_80_no55_dual_solver_closure_audit.json"
    )
    parser.add_argument(
        "--report", type=Path, default=HERE / "2026-08-04-C3N80-no55-dual-solver-closure.md"
    )
    args = parser.parse_args()

    ranking = json.loads(RANKING.read_text(encoding="utf-8"))
    dag = json.loads(DAG.read_text(encoding="utf-8"))
    source_audit = json.loads(SOURCE_AUDIT.read_text(encoding="utf-8"))
    positive = json.loads(POSITIVE.read_text(encoding="utf-8"))
    case = find_case(ranking, "56-80__no_55")
    if ranking["authoritative"]["dag_sha256"] != digest(DAG):
        raise RuntimeError("ranking/source DAG hash differs")
    if not source_audit.get("audit_pass") or source_audit.get("case_key") != "56-80__no_55":
        raise RuntimeError("source-shell audit is not a passing record for this case")

    nodes_raw = tuple(dag["factory_dag"]["nodes"])
    nodes = {int(node["id"]): node for node in nodes_raw}
    ordered_ids = tuple(nodes)
    order = {node_id: index for index, node_id in enumerate(ordered_ids)}
    predecessors = {
        node_id: tuple(map(int, nodes[node_id].get("args", ()))) for node_id in ordered_ids
    }
    consumers = {node_id: set() for node_id in ordered_ids}
    for node_id, arguments in predecessors.items():
        for argument in arguments:
            consumers[argument].add(node_id)
    outputs = tuple(map(int, dag["factory_dag"]["outputs"]))
    cut = set(map(int, case["cut_node_ids"]))
    retained = tuple(map(int, case["retained_frontier_ids"]))
    expanded = ancestors_of_frontier(retained, cut, predecessors, order)
    no_private = tuple(node_id for node_id in expanded if node_id != 55)
    if expanded != tuple(map(int, case["expanded_source_ids"])):
        raise RuntimeError("independent expanded source closure differs")
    if no_private != tuple(map(int, case["no_private_source_ids"])):
        raise RuntimeError("independent no-private source closure differs")
    if set(expanded) - set(no_private) != {55} or consumers[55] != {56}:
        raise RuntimeError("private BUS55 removal/consumer closure differs")

    states = replay(nodes_raw)
    blocks = exact_partition(no_private, states)
    targets = tuple(map(int, case["target_ids"]))
    if len(blocks) != 128 or not signals_are_functions(blocks, targets, states):
        raise RuntimeError("independent packed source partition differs")
    if any(states[node_id]["conflict"] for node_id in ordered_ids):
        raise RuntimeError("authoritative DAG contains packed BUS conflicts")

    expected = []
    carry = variable(16)
    for bit in range(8):
        left = variable(bit)
        right = variable(8 + bit)
        propagate = left ^ right
        expected.append(propagate ^ carry)
        carry = (left & right) | (propagate & carry)
    expected.append(carry)
    for node_id, truth in zip(outputs, expected):
        state = states[node_id]
        if state["bits"] != truth or state["driven"] != ALL or state["conflict"]:
            raise RuntimeError(f"authoritative output {node_id} fails complete replay")
    live = set(outputs)
    pending = list(outputs)
    while pending:
        node_id = pending.pop()
        for argument in predecessors[node_id]:
            if argument not in live:
                live.add(argument)
                pending.append(argument)
    if live != set(ordered_ids):
        raise RuntimeError("authoritative DAG contains dead nodes")
    gate = sum(int(nodes[node_id]["cost"]) for node_id in live)
    output_arrivals = [states[node_id]["arrival"] for node_id in outputs]
    if gate != 80 or max(output_arrivals) != 7 or gate * max(output_arrivals) != 560:
        raise RuntimeError("authoritative score differs")

    full = positive.get("full_verification", {})
    if (
        positive.get("status") != "sat"
        or positive.get("source_profile") != "expanded"
        or positive.get("seed_current") is not True
        or (positive.get("exact_ordinary"), positive.get("components"), positive.get("exact_switches"), positive.get("exact_xors"))
        != (1, 3, 2, 0)
        or int(full.get("full_truth_rows", -1)) != ROWS
        or int(full.get("actual_gate", -1)) != 5
        or int(full.get("mismatch_count", -1))
        or int(full.get("bus_conflict_count", -1))
        or int(full.get("illegal_z_output_count", -1))
        or int(full.get("physical_net_partition_violation_count", -1))
        or int(full.get("active_bus_normal_form_violation_count", -1))
        or int(full.get("dead_component_count", -1))
    ):
        raise RuntimeError("expanded-shell positive worker regression differs")

    solver_payloads: dict[str, Any] = {}
    reference: dict[tuple[int, int, int, int], dict[str, Any]] | None = None
    records_by_solver: dict[str, dict[tuple[int, int, int, int], dict[str, Any]]] = {}
    for solver in ("cadical195", "glucose42"):
        solver_payloads[solver], records = check_summary(
            solver, SOLVER_DIRS[solver], case, reference
        )
        records_by_solver[solver] = records
        if reference is None:
            reference = records
    paired_cnf = []
    for key in EXPECTED_COMPOSITIONS:
        left = records_by_solver["cadical195"][key]
        right = records_by_solver["glucose42"][key]
        if left["variables"] != right["variables"] or left["clauses"] != right["clauses"]:
            raise RuntimeError(f"paired CNF size differs for {key}")
        paired_cnf.append(
            {
                "ordinary": key[0],
                "components": key[1],
                "switches": key[2],
                "xors": key[3],
                "variables": int(left["variables"]),
                "clauses": int(left["clauses"]),
                "cadical195_status": "unsat",
                "glucose42_status": "unsat",
                "variables_clauses_identical": True,
            }
        )

    payload = {
        "schema": "byte-adder-80d7-ranked-private-frontier-dual-solver-closure-audit-v1",
        "audit_pass": True,
        "case_key": "56-80__no_55",
        "scope": "only the recorded no-private source shell at exact weighted cost 5",
        "authority": {
            "ranking": relative(RANKING),
            "ranking_sha256": digest(RANKING),
            "dag": relative(DAG),
            "dag_sha256": digest(DAG),
            "factory_dag_sha256": dag["factory_dag"]["sha256"],
            "structural_sha256": dag["metrics"]["structural_sha256"],
            "source_shell_audit": relative(SOURCE_AUDIT),
            "source_shell_audit_sha256": digest(SOURCE_AUDIT),
            "worker_sha256": digest(WORKER),
            "runner_sha256": digest(RUNNER),
            "auditor_sha256": digest(Path(__file__).resolve()),
        },
        "independent_full_replay": {
            "rows": ROWS,
            "output_mismatch_count": 0,
            "conflict_assignment_count": 0,
            "illegal_z_output_count": 0,
            "all_nodes_live": True,
            "gate": gate,
            "delay": max(output_arrivals),
            "energy": gate * max(output_arrivals),
            "output_arrivals": output_arrivals,
        },
        "source_shell": {
            "cut_node_ids": sorted(cut, key=order.__getitem__),
            "target_ids": list(targets),
            "retained_frontier_ids": list(retained),
            "expanded_source_ids": list(expanded),
            "no_private_source_ids": list(no_private),
            "removed_exactly": [55],
            "private_frontier_consumers": sorted(consumers[55]),
            "compressed_truth_rows": len(blocks),
            "targets_bits_driven_conflict_functional": True,
        },
        "accounting": {
            "current_complete_gate": 80,
            "current_cut_gate": 5,
            "guaranteed_private_prune_gate": 4,
            "fixed_shell_after_prune": 71,
            "replacement_bound": 5,
            "projected_complete_gate": 76,
            "projected_complete_delay": 7,
            "projected_complete_energy": 532,
        },
        "positive_regression": {
            "path": relative(POSITIVE),
            "sha256": digest(POSITIVE),
            "status": "sat",
            "composition": {"ordinary": 1, "components": 3, "switches": 2, "xors": 0},
            "full_truth_rows": ROWS,
            "full_replay_clean": True,
        },
        "solvers": solver_payloads,
        "paired_cnf_counts": paired_cnf,
        "coverage": {
            "expected_compositions": 5,
            "results_per_solver": 5,
            "total_results": 10,
            "status_counts": {"unsat": 10},
            "timeout_count": 0,
            "unknown_count": 0,
            "paired_variables_clauses_identical": True,
            "complete": True,
        },
        "conclusion": "exact weighted cost 5 is dual-solver UNSAT for this no-private source shell only",
        "non_claims": [
            "not a lower bound for another source shell",
            "not a lower bound for another connected cut",
            "not a lower bound outside the recorded primitive, liveness, physical-net, timing, and Z/conflict contract",
        ],
    }
    output_sha = atomic_write(
        args.output, (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    report_sha = atomic_write(args.report, format_report(payload).encode("utf-8"))
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "output_sha256": output_sha,
                "report": str(args.report.resolve()),
                "report_sha256": report_sha,
                "audit_pass": True,
                "dual_solver_status_counts": {"unsat": 10},
                "paired_cnf_counts_identical": True,
                "source_shell_rows": len(blocks),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
