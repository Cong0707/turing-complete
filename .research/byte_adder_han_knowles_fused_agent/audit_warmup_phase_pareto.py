"""Pareto-filter the 79 autonomous-phase residual records.

The input records come from ``audit_delayline_autonomous_phases.py``.  This
audit expands every feasible shared phase/output subset, computes the exact
connected-cut deletion in the reviewed 80/7 DAG, accounts for Delay-Line and
outer-gate cost, and distinguishes structural cofactor don't-cares from the
test's terminal don't-care.  Residual synthesis remains UNKNOWN unless an
explicit intake artifact is available; optimistic shell bounds are never
reported as SAT or UNSAT.
"""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

import audit_delayline_autonomous_phases as autonomous


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = HERE / "delayline_autonomous_phase_audit.json"
BASELINE = ROOT / ".research" / "byte_adder_root" / (
    "byte-adder-hybrid-phasefold-g80-d7.json"
)
INTAKE = HERE / "warmup_residual_intake" / "summary.json"
OUTPUT = HERE / "warmup_phase_residual_pareto_audit.json"
ROWS = 1 << 17
MASK = (1 << ROWS) - 1
OUTPUT_NAMES = tuple([f"S{bit}" for bit in range(8)] + ["Cout"])


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def phase_key(phase: dict[str, object]) -> tuple[object, ...]:
    return (
        int(phase["delay_line_count"]),
        tuple(phase["updates"]),
        str(phase["output"]),
        int(phase["decode_gate"]),
        int(phase["decode_delay"]),
        int(phase["preperiod"]),
        int(phase["period"]),
    )


def truth_by_phase_key() -> dict[tuple[object, ...], int]:
    phases, _summary, _aliases = autonomous.enumerate_phases()
    result = {}
    for truth, recipe in phases.items():
        result[phase_key(recipe.serialized())] = truth
    return result


def retained_cut(
    nodes: dict[int, dict[str, object]],
    outputs: tuple[int, ...],
    selected: tuple[int, ...],
) -> dict[str, object]:
    retained_output_ids = [
        node_id for index, node_id in enumerate(outputs) if index not in selected
    ]
    reachable: set[int] = set()
    stack = list(retained_output_ids)
    while stack:
        node_id = stack.pop()
        if node_id in reachable:
            continue
        reachable.add(node_id)
        stack.extend(int(value) for value in nodes[node_id].get("args", ()))
    retained_gate = sum(int(nodes[node_id]["cost"]) for node_id in reachable)
    retained_arrivals = [
        int(nodes[node_id]["arrival"]) for node_id in retained_output_ids
    ]
    return {
        "retained_current_gate": retained_gate,
        "deleted_current_gate": 80 - retained_gate,
        "retained_current_node_ids": sorted(reachable),
        "retained_output_indices": [
            index for index in range(9) if index not in selected
        ],
        "retained_output_names": [
            OUTPUT_NAMES[index] for index in range(9) if index not in selected
        ],
        "retained_delay": max(retained_arrivals, default=0),
    }


def subsets(indices: tuple[int, ...]):
    for width in range(1, len(indices) + 1):
        yield from combinations(indices, width)


def intake_index() -> dict[tuple[int, ...], dict[str, object]]:
    if not INTAKE.is_file():
        return {}
    payload = json.loads(INTAKE.read_text(encoding="utf-8"))
    result = {}
    for group in payload.get("groups", []):
        selected = tuple(group["cut"]["selected_output_indices"])
        completed = [
            row
            for row in group.get("mapping_results", [])
            if row.get("status") == "SAT"
        ]
        best = min(
            completed,
            key=lambda row: (
                row["candidate_energy"],
                row["candidate_delay"],
                row["candidate_total_gate"],
            ),
            default=None,
        )
        result[selected] = {
            "input_summary": str(INTAKE),
            "input_summary_sha256": digest(INTAKE),
            "group": group["name"],
            "completed_recipe_count": len(completed),
            "qualified_candidate_count": group.get("qualified_candidate_count", 0),
            "best_completed": None
            if best is None
            else {
                "recipe": best["recipe"],
                "residual_gate": best["ordinary_gate"],
                "residual_delay": best["residual_delay"],
                "candidate_total_gate": best["candidate_total_gate"],
                "candidate_delay": best["candidate_delay"],
                "care_mismatch_union": best["care_mismatch_union"],
                "warmup_shell_mismatch_union": best["warmup_shell_mismatch_union"],
                "abc_reported_unmet_timing": best["abc_reported_unmet_timing"],
            },
            "interpretation": "finite recipes only; no qualifying result is not UNSAT",
        }
    return result


def main() -> int:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    nodes = {
        int(node["id"]): node for node in baseline["factory_dag"]["nodes"]
    }
    outputs = tuple(int(value) for value in baseline["factory_dag"]["outputs"])
    truth_index = truth_by_phase_key()
    intake = intake_index()

    raw_records = source["matches"][
        "arbitrary_current_residual_outer_gate_feasible_outputs"
    ]
    groups: dict[tuple[tuple[object, ...], str], dict[str, object]] = {}
    for record in raw_records:
        phase = record["phase"]
        key = phase_key(phase)
        truth = truth_index[key]
        output_index = OUTPUT_NAMES.index(record["target"])
        for outer in record["feasible_outer_gates"]:
            group = groups.setdefault(
                (key, outer),
                {
                    "phase": phase,
                    "phase_truth": truth,
                    "outer_gate": outer,
                    "eligible_outputs": set(),
                },
            )
            group["eligible_outputs"].add(output_index)

    rows = []
    for group in groups.values():
        phase = group["phase"]
        truth = int(group["phase_truth"])
        outer = str(group["outer_gate"])
        care = truth if outer in {"AND", "NAND"} else (~truth & MASK)
        dc = (~care) & MASK
        eligible = tuple(sorted(group["eligible_outputs"]))
        for selected in subsets(eligible):
            cut = retained_cut(nodes, outputs, selected)
            phase_gate = int(phase["total_gate"])
            outer_gate = len(selected)
            fixed_shell = cut["retained_current_gate"] + phase_gate + outer_gate
            residual_budget = 79 - fixed_shell
            timing_status = str(phase["native_feedback_timing_status"])
            phase_delay = phase["native_feedback_delay"]
            reasons = []
            if fixed_shell >= 80:
                reasons.append("fixed shell is already at least 80 gates")
            if cut["retained_delay"] > 5:
                reasons.append("a retained output already exceeds D5")
            if timing_status == "PROVEN" and int(phase_delay) > 4:
                reasons.append("phase arrives after D4, so the outer gate exceeds D5")
            if timing_status == "UNKNOWN":
                disposition = "EXACT_SYNTHESIS_AND_NATIVE_TIMING_REQUIRED"
            elif reasons:
                disposition = "PARETO_ELIMINATED_FOR_LT80_D5"
            else:
                disposition = "EXACT_RESIDUAL_SYNTHESIS_REQUIRED"
            # A proven structural reason still eliminates a row even if some
            # unrelated multi-Delay feedback timing remains unknown.
            if reasons:
                disposition = "PARETO_ELIMINATED_FOR_LT80_D5"

            row = {
                "selected_output_indices": list(selected),
                "selected_output_names": [OUTPUT_NAMES[index] for index in selected],
                "selected_mask": sum(1 << index for index in selected),
                "selected_mask_hex": f"0x{sum(1 << index for index in selected):03x}",
                "eligible_output_indices_for_shared_phase": list(eligible),
                "eligible_output_names_for_shared_phase": [
                    OUTPUT_NAMES[index] for index in eligible
                ],
                "phase": phase,
                "outer_gate": outer,
                "residual_care_source_cycles": {
                    "count": care.bit_count(),
                    "first": (care & -care).bit_length() - 1 if care else None,
                    "last": care.bit_length() - 1 if care else None,
                    "sha256": sha256(
                        care.to_bytes(ROWS // 8, "little")
                    ).hexdigest(),
                },
                "residual_dc_source_cycles": {
                    "count": dc.bit_count(),
                    "first": (dc & -dc).bit_length() - 1 if dc else None,
                    "last": dc.bit_length() - 1 if dc else None,
                    "terminal_cycle_is_cofactor_dc": bool((dc >> (ROWS - 1)) & 1),
                    "sha256": sha256(dc.to_bytes(ROWS // 8, "little")).hexdigest(),
                },
                "terminal_test_induced_dc_present": False,
                "dc_origin": "outer-gate insensitive cofactor only",
                "maximum_deleted_current_gate": cut["deleted_current_gate"],
                **cut,
                "phase_gate": phase_gate,
                "phase_delay_status": timing_status,
                "phase_delay": phase_delay,
                "outer_gate_count": outer_gate,
                "fixed_shell_gate": fixed_shell,
                "optimistic_residual_gate_lower_bound": 0,
                "optimistic_total_gate_lower_bound": fixed_shell,
                "residual_gate_budget_for_total_at_most_79": residual_budget,
                "residual_required_arrival_for_global_d5": 4,
                "elimination_reasons": reasons,
                "disposition": disposition,
                "exact_intake": intake.get(selected),
            }
            rows.append(row)

    rows.sort(
        key=lambda row: (
            row["disposition"] == "PARETO_ELIMINATED_FOR_LT80_D5",
            row["optimistic_total_gate_lower_bound"],
            -row["maximum_deleted_current_gate"],
            row["selected_mask"],
            row["phase_gate"],
            row["outer_gate"],
        )
    )
    slow6 = next(
        (
            row
            for row in rows
            if row["selected_output_indices"] == [2, 4, 5, 6, 7, 8]
            and row["phase"]["delay_line_count"] == 1
            and row["phase"]["updates"] == ["1"]
            and row["outer_gate"] == "AND"
        ),
        None,
    )
    all9 = next(
        (
            row
            for row in rows
            if row["selected_output_indices"] == list(range(9))
            and row["phase"]["delay_line_count"] == 1
            and row["phase"]["updates"] == ["1"]
            and row["outer_gate"] == "AND"
        ),
        None,
    )
    report = {
        "schema": "tc-byte-adder-warmup-phase-residual-pareto-v1",
        "status": "COMPLETE",
        "dependencies": {
            "phase_audit": {"path": str(INPUT), "sha256": digest(INPUT)},
            "baseline": {"path": str(BASELINE), "sha256": digest(BASELINE)},
            "intake": None
            if not INTAKE.is_file()
            else {"path": str(INTAKE), "sha256": digest(INTAKE)},
        },
        "source_record_count": len(raw_records),
        "shared_phase_outer_group_count": len(groups),
        "expanded_nonempty_output_subset_count": len(rows),
        "disposition_counts": {
            disposition: sum(row["disposition"] == disposition for row in rows)
            for disposition in sorted({row["disposition"] for row in rows})
        },
        "rules": {
            "objective": "strictly below 80 gates at global delay at most 5",
            "phase_cost_included": True,
            "outer_gate_per_selected_output": 1,
            "terminal_test_dc": False,
            "timeout_or_missing_synthesis": "UNKNOWN, never UNSAT",
            "multi_delay_feedback_timing": "UNKNOWN unless independently proven",
        },
        "priority_slow6": slow6,
        "priority_all9": all9,
        "rows": rows,
        "conclusions": {
            "slow6_fixed_shell_gate": None if slow6 is None else slow6["fixed_shell_gate"],
            "slow6_residual_gate_budget": None
            if slow6 is None
            else slow6["residual_gate_budget_for_total_at_most_79"],
            "all9_fixed_shell_gate": None if all9 is None else all9["fixed_shell_gate"],
            "all9_residual_gate_budget": None
            if all9 is None
            else all9["residual_gate_budget_for_total_at_most_79"],
            "optimistic_shell_elimination_is_not_residual_unsat": True,
        },
    }
    OUTPUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"output={OUTPUT}")
    print(f"sha256={digest(OUTPUT)}")
    print(json.dumps(report["disposition_counts"], indent=2))
    print(
        "slow6=",
        None
        if slow6 is None
        else {
            key: slow6[key]
            for key in (
                "maximum_deleted_current_gate",
                "retained_current_gate",
                "retained_delay",
                "fixed_shell_gate",
                "residual_gate_budget_for_total_at_most_79",
                "disposition",
            )
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
