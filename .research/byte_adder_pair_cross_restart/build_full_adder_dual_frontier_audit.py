"""Build a read-only audit for the joint FullAdder 7/4 and 10/3 frontier."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
COST_EVIDENCE = (
    ROOT
    / ".research"
    / "byte_adder_component_byproduct_catalog"
    / "cost-import-semantics-2.1.292.json"
)
RUNTIME_EVIDENCE = (
    ROOT
    / ".research"
    / "byte_adder_component_byproduct_catalog"
    / "runtime-evidence-2.1.292.json"
)
PRIOR_EFFECTIVE_AUDIT = (
    ROOT
    / ".research"
    / "byte_adder_component_byproduct_catalog"
    / "full-adder-effective-cost-audit-2.1.292.json"
)
TEN_THREE_CERTIFICATE = HERE / "full_adder_10_3" / "physical_certificate.json"
OUT = HERE / "full_adder_10_3" / "dual_frontier_audit.json"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def nondominated(points: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    unique = sorted(set(points))
    return [
        point
        for point in unique
        if not any(
            other != point
            and all(left <= right for left, right in zip(other, point, strict=True))
            for other in unique
        )
    ]


def component_frontier(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    unique = sorted(set(points))
    result = [
        point
        for point in unique
        if not any(
            other != point
            and other[0] <= point[0]
            and other[1] <= point[1]
            for other in unique
        )
    ]
    for left, right in zip(result, result[1:]):
        require(left[0] < right[0], "component frontier gate order is not strict")
        require(left[1] > right[1], "component frontier delay order is not strict")
    return result


def select(frontier: list[tuple[int, int]], cost_gate: int, cost_delay: int) -> tuple[int, int]:
    require(bool(frontier), "cannot select from an empty frontier")
    if (cost_gate, cost_delay) == (-1, 0):
        return frontier[0]
    if (cost_gate, cost_delay) == (0, -1):
        return frontier[-1]
    require(cost_gate >= 0 and cost_delay >= 0, "invalid serialized selector")
    return next(
        (
            point
            for point in frontier
            if point[0] <= cost_gate and point[1] <= cost_delay
        ),
        frontier[0],
    )


def function_map(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in payload["functions"]}


def function_record(
    functions: dict[str, dict[str, object]],
    name: str,
    fragments: tuple[str, ...],
) -> dict[str, object]:
    row = functions[name]
    pseudocode = str(row["pseudocode"])
    for fragment in fragments:
        require(fragment in pseudocode, f"{name} lacks decisive fragment {fragment!r}")
    return {
        "name": name,
        "address": row["address"],
        "size": row["size"],
        "machine_sha256": row["machine_sha256"],
        "pseudocode_sha256": row["pseudocode_sha256"],
        "decisive_fragments": list(fragments),
    }


def main() -> None:
    costs = load(COST_EVIDENCE)
    runtime = load(RUNTIME_EVIDENCE)
    prior = load(PRIOR_EFFECTIVE_AUDIT)
    certificate = load(TEN_THREE_CERTIFICATE)
    require(prior["status"] == "pass", "prior 7/4 effective-cost audit is not passing")
    require(certificate["status"] == "verified", "10/3 physical certificate is not verified")
    require(certificate["score"]["replayed"][:2] == [10, 3], "10/3 replay score drift")

    cost_functions = function_map(costs)
    runtime_functions = function_map(runtime)
    evidence = {
        "insert_cost": function_record(
            cost_functions,
            "insert_cost__modelZscores_u13",
            (
                "component_cost_buffer__modelZscores_u12 + 2 * v64) >= v41",
                "v42 < qword_146772D68[2 * v50]",
                "v42 > qword_146772D68[2 * v69]",
            ),
        ),
        "add_cost": function_record(
            cost_functions,
            "add_cost__modelZscores_u2110",
            ("insert_cost__modelZscores_u49(a1, &v6)",),
        ),
        "complete_level": function_record(
            cost_functions,
            "complete_level__modelZutilities_u9086",
            (
                "add_cost__modelZscores_u2110(v10, &v22)",
                "update_efficient_frontier__modelZutilities_u9054(v49 + 48, v21)",
                "save_level_data__modelZutilities_u5683",
            ),
        ),
        "get_cost": function_record(
            runtime_functions,
            "get_cost__modelZscores_u2321",
            (
                "if ( (unsigned __int8)v84 == 2 )",
                "v105 = v36 <= v85",
                "v105 = v37 <= v86",
                "v33 = get_gate_cost__modelZscores_u2304((unsigned __int8 *)a2, v36)",
                "v34 = get_delay_cost__modelZscores_u2316((unsigned __int8 *)a2, v37)",
                "v89 = v33",
                "v90 = v34",
            ),
        ),
    }

    old = (16, 8, 1)
    seven = (7, 4, 1)
    ten = (10, 3, 1)
    saved_after_seven = nondominated([old, seven])
    saved_after_both = nondominated([*saved_after_seven, ten])
    saved_reverse = nondominated([old, ten, seven])
    require(saved_after_seven == [seven], "7/4 does not dominate legacy 16/8/1")
    require(saved_after_both == [seven, ten], "saved dual frontier differs")
    require(saved_reverse == saved_after_both, "saved frontier depends on acceptance order")

    component_after_both = component_frontier([(16, 8), (7, 4), (10, 3)])
    component_reverse = component_frontier([(16, 8), (10, 3), (7, 4)])
    require(component_after_both == [(7, 4), (10, 3)], "component dual frontier differs")
    require(component_reverse == component_after_both, "component frontier depends on order")
    selections = {
        "minimum_gate": select(component_after_both, -1, 0),
        "minimum_delay": select(component_after_both, 0, -1),
        "explicit_7_4": select(component_after_both, 7, 4),
        "explicit_10_3": select(component_after_both, 10, 3),
    }
    require(selections["minimum_gate"] == (7, 4), "minimum-gate selection drift")
    require(selections["minimum_delay"] == (10, 3), "minimum-delay selection drift")
    require(selections["explicit_7_4"] == (7, 4), "explicit 7/4 selection drift")
    require(selections["explicit_10_3"] == (10, 3), "explicit 10/3 selection drift")

    payload = {
        "schema": "full-adder-7-4-10-3-dual-frontier-audit-v1",
        "status": "verified",
        "scope": {
            "game_launched": False,
            "formal_save_modified": False,
            "levels_txt_read_or_modified": False,
            "remote_submission_performed": False,
            "server_private_acceptance_implementation_claimed": False,
        },
        "premise": (
            "Both physically verified FullAdder points are genuinely accepted and persisted; "
            "the audit proves client insertion, persistence shape, restart import/selection, "
            "and parent-instance use under that premise."
        ),
        "dependencies": {
            str(path): digest(path)
            for path in (
                COST_EVIDENCE,
                RUNTIME_EVIDENCE,
                PRIOR_EFFECTIVE_AUDIT,
                TEN_THREE_CERTIFICATE,
            )
        },
        "accepted_points": {
            "legacy": list(old),
            "seven_four": list(seven),
            "ten_three": list(ten),
            "seven_four_dominates_legacy": True,
            "seven_four_vs_ten_three": {
                "gate_relation": "7 < 10",
                "delay_relation": "4 > 3",
                "mutually_nondominated": True,
            },
        },
        "level_progress_frontier": {
            "after_7_4": [list(point) for point in saved_after_seven],
            "after_7_4_then_10_3": [list(point) for point in saved_after_both],
            "after_10_3_then_7_4": [list(point) for point in saved_reverse],
            "both_points_retained": True,
            "acceptance_order_independent": True,
            "third_metric": 1,
        },
        "kind_15_component_cost_frontier": {
            "after_both": [list(point) for point in component_after_both],
            "gate_strictly_increases": True,
            "delay_strictly_decreases": True,
            "add_cost_retains_both_points": True,
            "restart_import_retains_both_points_under_server_or_saved_dual-frontier_premise": True,
        },
        "instance_selection": {
            "serialized_modes": {
                "cost_gate=-1,cost_delay=0": "minimum gate; selects 7/4",
                "cost_gate=0,cost_delay=-1": "minimum delay; selects 10/3",
                "cost_gate=7,cost_delay=4": "explicit frontier point 7/4",
                "cost_gate=10,cost_delay=3": "explicit frontier point 10/3",
            },
            "replayed": {key: list(value) for key, value in selections.items()},
            "selection_granularity": "one atomic (gate,delay) row per component instance",
            "same_instance_gate_delay_mixing_allowed": False,
            "impossible_synthetic_pair": [7, 3],
            "different_instances_may_choose_different_rows": True,
            "builder_requirement_for_low_delay": (
                "A kind-15 instance must use cost_gate=10,cost_delay=3 or minimum-delay "
                "cost_gate=0,cost_delay=-1; the default minimum-gate fields select 7/4."
            ),
        },
        "parent_scoring": {
            "gate": "sum the gate coordinate from each instance's selected atomic row",
            "delay": "schedule each opaque instance with the delay coordinate from that same selected row",
            "no_cross_coordinate_selection": True,
            "mixed_instance_example": (
                "A parent may deliberately contain one FullAdder at 7/4 and another at 10/3, "
                "but neither instance is priced as 7/3."
            ),
        },
        "evidence": evidence,
        "auditor": {
            "path": str(Path(__file__).resolve()),
            "sha256": digest(Path(__file__).resolve()),
        },
    }
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(json.dumps({
        "status": payload["status"],
        "output": str(OUT),
        "output_sha256": sha256(encoded).hexdigest(),
        "component_frontier": payload["kind_15_component_cost_frontier"]["after_both"],
        "instance_selection": payload["instance_selection"]["replayed"],
        "same_instance_gate_delay_mixing_allowed": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
