"""Build a static evidence chain for a genuinely accepted 7/4 Full Adder.

The audit is deliberately read-only with respect to game state.  It consumes
previously captured runtime/IDA evidence and the installed campaign metadata;
it does not launch the game, read levels.txt, submit a score, or edit a save.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMPONENT_EVIDENCE = (
    ROOT / ".research/byte_adder_component_costs_agent/component_evidence.json"
)
RUNTIME_EVIDENCE = HERE / "runtime-evidence-2.1.292.json"
COST_IMPORT_EVIDENCE = HERE / "cost-import-semantics-2.1.292.json"
TRUTH_CATALOG = HERE / "truth-byproduct-catalog-v1.json"
FULL_ADDER_META = Path(
    r"D:\Game\Steam\steamapps\common\Turing Complete\campaign\full_adder\meta.txt"
)
DEFAULT_OUTPUT = HERE / "full-adder-effective-cost-audit-2.1.292.json"
DEFAULT_REPORT = HERE / "full-adder-effective-cost-audit-2.1.292.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def nondominated(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    unique = sorted(set(points))
    return [
        point
        for point in unique
        if not any(
            other != point
            and other[0] <= point[0]
            and other[1] <= point[1]
            for other in unique
        )
    ]


def function_map(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in payload["functions"]}


def evidence_record(row: dict[str, object], decisive_fragments: list[str]) -> dict[str, object]:
    pseudocode = str(row.get("pseudocode", ""))
    for fragment in decisive_fragments:
        require(fragment in pseudocode, f"missing pseudocode fragment in {row['name']}: {fragment}")
    return {
        "name": row["name"],
        "address": row["address"],
        "size": row["size"],
        "machine_sha256": row["machine_sha256"],
        "pseudocode_sha256": row["pseudocode_sha256"],
        "decisive_fragments": decisive_fragments,
    }


def build() -> dict[str, object]:
    component = json.loads(COMPONENT_EVIDENCE.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME_EVIDENCE.read_text(encoding="utf-8"))
    costs = json.loads(COST_IMPORT_EVIDENCE.read_text(encoding="utf-8"))
    catalog = json.loads(TRUTH_CATALOG.read_text(encoding="utf-8"))
    meta_text = FULL_ADDER_META.read_text(encoding="utf-8")

    saved = component["current_level_state"]["full_adder"]
    require(saved["complete"] is True, "captured Full Adder level is not complete")
    require(saved["saved_frontier"] == [[16, 8, 1]], "captured Full Adder frontier changed")
    require(
        saved["unlock_declaration"] == "unlocks_components = [com_full_adder]",
        "Full Adder unlock declaration changed",
    )
    require("kind = combinational" in meta_text, "Full Adder level kind changed")
    require("unlocks_components = [com_full_adder]" in meta_text, "installed unlock changed")

    static_full_adder = component["static_executable_score_table"]["components"]["15"]
    require(static_full_adder["name"] == "com_full_adder", "kind 15 mapping changed")
    require(static_full_adder["default"] == [8, 4], "kind 15 runtime default changed")
    require(static_full_adder["score_source"] == "level_override_allowed", "override policy changed")

    exact = catalog["primitive_library"]["full_adder_exact_minimum"]
    require(exact["status"] == "sat" and exact["gate"] == 7 and exact["delay"] == 4, "7/4 proof missing")
    require(catalog["claims"]["full_adder_7gate_minimum_z3_exact"] is True, "minimum claim missing")

    old_point = (16, 8)
    accepted_point = (7, 4)
    new_frontier = nondominated([old_point, accepted_point])
    require(new_frontier == [accepted_point], "7/4 did not dominate 16/8")
    score_transition = {
        "old": {"gate": 16, "delay": 8, "score_product": 128},
        "accepted": {"gate": 7, "delay": 4, "score_product": 28},
        "strictly_better_product": 28 < 128,
        "strictly_dominates_in_both_axes": 7 < 16 and 4 < 8,
        "resulting_gate_delay_frontier": [[7, 4]],
    }

    runtime_functions = function_map(runtime)
    cost_functions = function_map(costs)
    runtime_chain = [
        evidence_record(
            runtime_functions["get_gate_cost__modelZscores_u2232"],
            ["if ( a1 > 0x11u", "v42 = a3;"],
        ),
        evidence_record(
            runtime_functions["get_delay_cost__modelZscores_u2270"],
            ["if ( a1 <= 0x11u", "v28 = a3;"],
        ),
        evidence_record(
            runtime_functions["get_cost__modelZscores_u2321"],
            [
                "component_costs__modelZscores_u10",
                "get_gate_cost__modelZscores_u2304",
                "get_delay_cost__modelZscores_u2316",
            ],
        ),
        evidence_record(
            runtime_functions["get_gate_cost__modelZscores_u2556"],
            ["get_cost__modelZscores_u2321", "v27 = v12;"],
        ),
    ]
    persistence_chain = [
        evidence_record(
            cost_functions["complete_level__modelZutilities_u9086"],
            [
                "add_cost__modelZscores_u2110",
                "update_efficient_frontier__modelZutilities_u9054",
                "save_level_data__modelZutilities_u5683",
            ],
        ),
        evidence_record(
            cost_functions["game_initialize__modelZinitialize_u17"],
            ["add_cost__modelZscores_u2110"],
        ),
        evidence_record(
            cost_functions["insert_cost__modelZscores_u13"],
            ["v42 > qword_146772D68", "v42 < qword_146772D68"],
        ),
        evidence_record(
            cost_functions["import_costs__modelZscores_u2127"],
            ["insert_cost__modelZscores_u49", "component_cost_buffer_len__modelZscores_u11 - 1"],
        ),
        evidence_record(
            cost_functions["process_network_responses__presenterZutilities_u38339"],
            ["import_costs__modelZscores_u2127", "save_level_data__modelZutilities_u5683"],
        ),
    ]

    complete_pseudocode = cost_functions["complete_level__modelZutilities_u9086"]["pseudocode"]
    require("newSeqPayload(1i64, 24i64, 8i64)" in complete_pseudocode, "single-point special branch missing")
    require("v49 + 48" in complete_pseudocode, "efficient frontier field missing")
    initialize_pseudocode = cost_functions["game_initialize__modelZinitialize_u17"]["pseudocode"]
    require("v398 + 48" in initialize_pseudocode, "frontier reload field missing")
    require("while ( v469 < (__int64)v396 )" in initialize_pseudocode, "frontier reload loop missing")

    hint = component["circuits"]["campaign_byte_adder_hint"]
    full_adder_count = int(hint["kind_width_counts"]["15:1"])
    require(full_adder_count == 8, "campaign Byte Adder hint no longer has eight Full Adders")
    require(hint["header"][:2] == [64, 32], "campaign hint header changed")
    ripple_examples = {
        "component_count": full_adder_count,
        "shipped_file_header_using_runtime_default_8_4": [64, 32],
        "captured_imported_frontier_16_8_recomputed": [16 * full_adder_count, 8 * full_adder_count],
        "genuinely_accepted_7_4_recomputed": [7 * full_adder_count, 4 * full_adder_count],
        "note": (
            "This is the all-eight-FullAdder serial hint topology. Gate totals add; "
            "the 32-cycle delay assumes all eight opaque FullAdder delays lie on the ripple path."
        ),
    }

    dag = json.loads(
        (ROOT / ".research/byte_adder_root/byte-adder-hybrid-phasefold-g80-d7.json").read_text(
            encoding="utf-8"
        )
    )
    opaque_full_adder_nodes = [
        node for node in dag["factory_dag"]["nodes"] if str(node["op"]).lower() in {"fulladder", "full_adder"}
    ]
    require(not opaque_full_adder_nodes, "authoritative 80/7 unexpectedly uses opaque FullAdder")

    call_edges = costs["call_edges"]
    require(
        any(
            edge["caller"] == "complete_level__modelZutilities_u9086"
            and edge["callee"] == "add_cost__modelZscores_u2110"
            for edge in call_edges
        ),
        "complete_level -> add_cost call edge missing",
    )
    require(
        any(
            edge["caller"] == "game_initialize__modelZinitialize_u17"
            and edge["callee"] == "add_cost__modelZscores_u2110"
            for edge in call_edges
        ),
        "initialize -> add_cost call edge missing",
    )
    require(
        any(
            edge["caller"] == "process_network_responses__presenterZutilities_u38339"
            and edge["callee"] == "import_costs__modelZscores_u2127"
            for edge in call_edges
        ),
        "network response -> import_costs call edge missing",
    )

    return {
        "schema": "tc-full-adder-effective-cost-audit-2.1.292-v1",
        "status": "pass",
        "scope": {
            "premise": "the Full Adder level is genuinely accepted and persisted at 7/4",
            "game_launched": False,
            "save_or_levels_txt_read_or_modified_by_this_audit": False,
            "remote_submission_performed": False,
            "evidence_kind": "installed campaign metadata + previously captured runtime/IDA/derived research",
        },
        "dependencies": {
            str(path): file_sha(path)
            for path in (
                COMPONENT_EVIDENCE,
                RUNTIME_EVIDENCE,
                COST_IMPORT_EVIDENCE,
                TRUTH_CATALOG,
                FULL_ADDER_META,
            )
        },
        "kind_mapping": {
            "component_kind": 15,
            "name": "com_full_adder",
            "runtime_default_separate_profile": [8, 4],
            "level_override_allowed": True,
            "installed_level_kind": "combinational",
            "unlock_declaration": "unlocks_components = [com_full_adder]",
        },
        "captured_before_acceptance": {
            "saved_frontier": saved["saved_frontier"],
            "custom_circuit_file_header": component["derived_facts"]["custom_full_adder_current_file_header"],
            "file_header_is_not_effective_runtime_cost_proof": True,
        },
        "accepted_7_4": {
            "exact_minimum_proof": {
                "status": exact["status"],
                "gate": exact["gate"],
                "delay": exact["delay"],
                "seconds": exact["seconds"],
                "scope": exact["scope"],
            },
            "frontier_transition": score_transition,
            "effective_cost_after_successful_local_completion": [7, 4],
            "effective_cost_after_restart_from_persisted_frontier": [7, 4],
        },
        "runtime_recalculation": {
            "kind_15_gate_and_delay_are_pass_through_from_selected_cost_point": True,
            "parent_gate_total_sums_per_component_get_cost_results": True,
            "parent_delay_uses_selected_component_delay_in_runtime_scheduling": True,
            "formula_for_parent_with_n_full_adders": {
                "gate": "G_other + 7*n",
                "delay": "recompute critical path with each opaque FullAdder arc weighted 4",
            },
            "evidence": runtime_chain,
        },
        "persistence_and_pareto": {
            "component_cost_table_supports_multiple_nondominated_gate_delay_points": True,
            "level_progress_frontier_is_a_sequence_of_24_byte_gate_delay_third_metric_triples": True,
            "ordinary_frontier_path_calls_update_efficient_frontier": True,
            "special_level_kind_3_path_replaces_frontier_with_one_point_when_product_improves": True,
            "for_7_4_vs_16_8_branch_choice_does_not_change_result": "7/4 strictly dominates 16/8 and has product 28 < 128",
            "component_instance_can_select_from_a_multi_point_runtime_frontier": True,
            "evidence": persistence_chain,
        },
        "network_service_boundary": {
            "client_network_response_imports_server_supplied_cost_frontiers": True,
            "server_response_can_replace_local_component_cost_table": True,
            "conditional_conclusion": (
                "If 'genuinely accepted' includes server persistence of the 7/4 Full Adder score, "
                "the returned/imported frontier makes parent scoring use 7/4."
            ),
            "not_claimed_offline": (
                "This static audit does not directly observe the service's private recomputation or acceptance; "
                "no remote submission was permitted."
            ),
        },
        "eight_stage_ripple_example": ripple_examples,
        "authoritative_80d7_impact": {
            "opaque_full_adder_node_count": 0,
            "score_before_and_after_7_4_acceptance": [80, 7],
            "conclusion": "the current 80/7 ordinary/Switch/BUS DAG is unaffected by com_full_adder cost changes",
        },
        "final_conclusions": {
            "com_full_adder_imports_as_7_4_after_genuine_acceptance": True,
            "local_parent_gate_and_delay_are_recomputed_from_7_4": True,
            "multiple_pareto_points_are_supported_but_not_needed_for_this_strictly_dominating_update": True,
            "server_internal_recalculation_directly_proven_offline": False,
            "server_authoritative_frontier_reimport_path_proven": True,
        },
    }


def report(payload: dict[str, object], digest: str) -> str:
    return "\n".join(
        [
            "# Full Adder 7/4 effective-cost audit (Turing Complete 2.1.292)",
            "",
            f"- Status: `{payload['status']}`",
            f"- JSON SHA256: `{digest}`",
            "- Premise: the `full_adder` level is genuinely accepted and persisted at `7/4`.",
            "- Result: `com_full_adder` becomes effective `7/4` locally and after restart.",
            "- Parent scoring: gate totals and delay scheduling consume the selected runtime cost point; opaque FullAdder arcs therefore use `7/4`.",
            "- Pareto: component tables support multiple nondominated points; here `7/4` strictly dominates the captured `16/8`, so the result is a single point.",
            "- Network boundary: server-supplied frontiers are authoritative on import. Static evidence proves that import path, not the service's private acceptance implementation.",
            "- Current authoritative `80/7`: unchanged because it contains no opaque FullAdder node.",
            "",
            "## Eight-stage ripple example",
            "",
            "- Shipped header/default `8/4`: `64/32`.",
            "- Captured imported `16/8`: recomputed `128/64`.",
            "- Genuinely accepted `7/4`: recomputed `56/32`.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    payload = build()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.write_bytes(encoded.encode("utf-8"))
    digest = sha256(encoded.encode("utf-8")).hexdigest()
    markdown = report(payload, digest)
    args.report.write_bytes(markdown.encode("utf-8"))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(args.output),
                "output_sha256": digest,
                "report": str(args.report),
                "report_sha256": sha256(markdown.encode("utf-8")).hexdigest(),
                "final_conclusions": payload["final_conclusions"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
