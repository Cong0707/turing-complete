"""Merge and validate the complete exact-cost-nine S1+S2 closure.

The all-ordinary decomposition was solved by the root-task Boolean model.
The other eleven decompositions were solved by the strict value/driven model.
This script verifies both evidence families, the positive regressions, and the
ordinary-only projection equivalence against the authoritative 80/7 DAG.

It is an offline read-only auditor apart from atomically writing its summary.
It does not launch the game or read/write a formal save or candidate.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROOT_RESEARCH = ROOT / ".research" / "byte_adder_root"

MIXED_SUMMARY = HERE / "s1s2_joint_strict_cost9_mixed_summary.json"
MIXED_SUMMARIZER = HERE / "summarize_80d7_s1_s2_joint_strict_mixed.py"
STRICT_WORKER = HERE / "exact_80d7_s1_s2_joint_strict_sat.py"
MIXED_RESULT_DIR = HERE / "s1s2_joint_cost9_results"
REGRESSIONS = {
    "cadical195": HERE / "s1s2_joint_strict_g10_regression_cadical195.json",
    "glucose42": HERE / "s1s2_joint_strict_g10_regression_glucose42.json",
}

N9_WRAPPER = ROOT_RESEARCH / "exact_80d7_s1_s2_joint_sat.py"
N9_RESULT = ROOT_RESEARCH / "s1-s2-current80-g9-n9-s0-x0.json"
N9_BASE = (
    ROOT / ".research" / "byte_adder_ling_theory_agent"
    / "exact_free_ling_pair_sat.py"
)
N9_EXACT_CORE = (
    ROOT / ".research" / "byte_adder_boolean_superopt_agent"
    / "exact_adder_block_sat.py"
)
GENERIC_CNF = ROOT / ".research" / "rng_468_joint_macro" / "joint_parity_cnf.py"

AUTHORITATIVE_DAG = ROOT_RESEARCH / "byte-adder-hybrid-phasefold-g80-d7.json"
MATERIALIZER = (
    ROOT / ".research" / "byte_adder_builder_layout_agent"
    / "materialize_factory_dag.py"
)
EXACT_ADAPTER = (
    ROOT / ".research" / "byte_adder_han_knowles_fused_agent"
    / "search_av97_local_suffix.py"
)

EXPECTED_SHA256 = {
    MIXED_SUMMARY: "9016d882f208bada6ee0c84cfbc1bccbf593f4d9d41071fe4ef6053446a349a9",
    MIXED_SUMMARIZER: "8d7b7f5cd17dc1b96c83701e27515773a99386f01186c57ad990fdeef9a2aa03",
    STRICT_WORKER: "7417c004c21bb45d66741a9a99291b0119eaf840b509f56edc7dc063a988768c",
    REGRESSIONS["cadical195"]: "8093cccae2bebc5acac2aa3420f5b02ece621019b3aa8f1a635168d8dcca34a2",
    REGRESSIONS["glucose42"]: "c5b84a7eeffb76363f74ee7a0f2eb6bff75254abd81be203bb9819722a210015",
    N9_WRAPPER: "854dc6888090442dc64e33e2878177885dc6f9157cffa52cf0edf446726651f2",
    N9_RESULT: "7a56e59ff89237efedbd0e45641fbfe1c1cca307cd966ba26b4905170e5586e9",
    N9_BASE: "49bb2640e1cb08c6e2b9ac412a8cf56c058f27966e1dd799d1d813c8f1821017",
    N9_EXACT_CORE: "f320ed3029b949185acd13b5462b659502a970406d1bf5047713279e152f56de",
    GENERIC_CNF: "a565201bf7e99f6ded6732e70d883cd9a90e5da2e42d72171f11952bb3566ca4",
    AUTHORITATIVE_DAG: "71625de2b86ea03127415802dbc68f605ac16d69da6d9e8b3ade35db317ec884",
    MATERIALIZER: "cc15810d423706a65f7d55a90b5cfe02c8966b84c9447da4172a35158524a3cf",
    EXACT_ADAPTER: "08ba4041b3e01ee5a48c9736a72767c6a4e90a105e75a2634f2fd13c9f7a4f56",
}

CUT_NODE_IDS = [23, 24, 52, 53, 76, 77, 78, 79, 80, 81]
SOURCE_IDS = [4, 5, 22, 25, 51, 45, 56]
SOURCE_NAMES = ["a1", "b1", "G1", "G2", "V2", "C1", "C3"]
SOURCE_ARRIVALS = {
    "a1": 0,
    "b1": 0,
    "G1": 1,
    "G2": 1,
    "V2": 1,
    "C1": 2,
    "C3": 3,
}
TARGET_IDS = [77, 81]
TARGET_NAMES = ["S1", "S2"]
OUTPUT_DEADLINES = [4, 7]
FULL_ROWS = 1 << 17

SOLVERS = ("cadical195", "glucose42")
MIXED_CASES = (
    ("o7_s1_x0", 7, 1, 0),
    ("o5_s2_x0", 5, 2, 0),
    ("o3_s3_x0", 3, 3, 0),
    ("o1_s4_x0", 1, 4, 0),
    ("o6_s0_x1", 6, 0, 1),
    ("o4_s1_x1", 4, 1, 1),
    ("o2_s2_x1", 2, 2, 1),
    ("o0_s3_x1", 0, 3, 1),
    ("o3_s0_x2", 3, 0, 2),
    ("o1_s1_x2", 1, 1, 2),
    ("o0_s0_x3", 0, 0, 3),
)
ALL_DECOMPOSITIONS = (("o9_s0_x0", 9, 0, 0), *MIXED_CASES)


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def record_file(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "sha256": file_sha256(path)}


def verify_pinned_files(errors: list[str]) -> list[dict[str, Any]]:
    records = []
    for path, expected in EXPECTED_SHA256.items():
        if not path.is_file():
            errors.append(f"missing pinned file: {path}")
            continue
        actual = file_sha256(path)
        require(errors, actual == expected, f"{path.name}: pinned SHA-256 mismatch")
        records.append(
            {
                "path": str(path.resolve()),
                "sha256": actual,
                "expected_sha256": expected,
                "match": actual == expected,
            }
        )
    return records


def expect_fields(
    errors: list[str], payload: dict[str, Any], expected: dict[str, Any], label: str
) -> None:
    for field, value in expected.items():
        require(
            errors,
            payload.get(field) == value,
            f"{label}: {field} mismatch ({payload.get(field)!r} != {value!r})",
        )


def verify_strict_common(
    errors: list[str], payload: dict[str, Any], path: Path
) -> None:
    label = path.name
    expect_fields(
        errors,
        payload,
        {
            "schema": "byte-adder-80d7-s1-s2-joint-strict-physical-v1",
            "source_sha256": EXPECTED_SHA256[AUTHORITATIVE_DAG],
            "script_sha256": EXPECTED_SHA256[STRICT_WORKER],
            "cut_node_ids": CUT_NODE_IDS,
            "full_truth_rows": FULL_ROWS,
            "source_ids": SOURCE_IDS,
            "source_names": SOURCE_NAMES,
            "source_arrivals": SOURCE_ARRIVALS,
            "source_driven_one_counts": {
                "a1": FULL_ROWS,
                "b1": FULL_ROWS,
                "G1": FULL_ROWS,
                "G2": FULL_ROWS,
                "V2": FULL_ROWS,
                "C1": 81920,
                "C3": 94208,
            },
            "source_conflict_one_counts": {name: 0 for name in SOURCE_NAMES},
            "target_ids": TARGET_IDS,
            "target_names": TARGET_NAMES,
            "target_one_counts": {"S1": 65536, "S2": 65536},
            "target_driven_one_counts": {"S1": FULL_ROWS, "S2": FULL_ROWS},
            "compressed_truth_rows": 36,
            "output_deadlines": OUTPUT_DEADLINES,
            "physical_nets": True,
            "all_components_live": True,
            "final_outputs_fully_driven": True,
        },
        label,
    )
    expect_fields(
        errors,
        payload.get("script_sha256_dependencies", {}),
        {
            "materializer": EXPECTED_SHA256[MATERIALIZER],
            "exact_adapter": EXPECTED_SHA256[EXACT_ADAPTER],
        },
        f"{label}: dependencies",
    )


def verify_regression(
    errors: list[str], solver: str, path: Path
) -> dict[str, Any]:
    payload = load_json(path)
    verify_strict_common(errors, payload, path)
    expect_fields(
        errors,
        payload,
        {
            "status": "sat",
            "solver": solver,
            "gate_bound": 10,
            "components": 10,
            "exact_ordinary": 10,
            "exact_switches": 0,
            "exact_xors": 0,
            "weighted_gate": 10,
            "seed_current": True,
            "variables": 15464,
            "clauses": 122370,
        },
        path.name,
    )
    compressed = payload.get("compressed_verification", {})
    for field in (
        "mismatch_count",
        "bus_conflict_count",
        "undriven_output_count",
        "physical_net_partition_violation_count",
    ):
        require(
            errors,
            compressed.get(field) == 0,
            f"{path.name}: compressed replay {field} is not zero",
        )
    full = payload.get("full_verification", {})
    for field in (
        "mismatch_count",
        "bus_conflict_count",
        "undriven_output_count",
        "physical_net_partition_violation_count",
        "dead_component_count",
    ):
        require(
            errors,
            full.get(field) == 0,
            f"{path.name}: full replay {field} is not zero",
        )
    require(errors, full.get("actual_gate") == 10, f"{path.name}: gate replay mismatch")
    require(
        errors,
        full.get("actual_component_arrivals") == [1, 2, 3, 4, 3, 4, 5, 5, 6, 7],
        f"{path.name}: component arrivals mismatch",
    )
    require(
        errors,
        full.get("output_arrivals") == OUTPUT_DEADLINES,
        f"{path.name}: output arrivals mismatch",
    )
    return {
        "solver": solver,
        **record_file(path),
        "status": payload.get("status"),
        "variables": payload.get("variables"),
        "clauses": payload.get("clauses"),
        "solve_seconds": payload.get("solve_seconds"),
        "full_verification": full,
    }


def verify_mixed(errors: list[str]) -> dict[str, Any]:
    summary = load_json(MIXED_SUMMARY)
    expect_fields(
        errors,
        summary,
        {
            "schema": "byte-adder-80d7-s1-s2-joint-strict-mixed-cost9-summary-v1",
            "worker_sha256": EXPECTED_SHA256[STRICT_WORKER],
            "summarizer_sha256": EXPECTED_SHA256[MIXED_SUMMARIZER],
            "errors": [],
            "coverage_complete": True,
            "all_mixed_unsat": True,
            "status": "all-mixed-cost9-unsat",
        },
        MIXED_SUMMARY.name,
    )
    scope = summary.get("scope", {})
    expect_fields(
        errors,
        scope,
        {
            "cut_node_ids": CUT_NODE_IDS,
            "source_ids": SOURCE_IDS,
            "target_ids": TARGET_IDS,
            "target_names": TARGET_NAMES,
            "output_deadlines": OUTPUT_DEADLINES,
            "full_truth_rows": FULL_ROWS,
            "compressed_truth_rows": 36,
            "strict_source_drivens": {"C1": 81920, "C3": 94208},
            "physical_nets": True,
            "all_components_live": True,
            "final_outputs_fully_driven": True,
        },
        f"{MIXED_SUMMARY.name}: scope",
    )
    expect_fields(
        errors,
        summary.get("library_costs", {}),
        {"ordinary": 1, "switch": 2, "xor": 3},
        f"{MIXED_SUMMARY.name}: costs",
    )
    expect_fields(
        errors,
        summary.get("excluded_decomposition", {}),
        {"ordinary": 9, "switches": 0, "xors": 0},
        f"{MIXED_SUMMARY.name}: excluded decomposition",
    )

    expected_by_name = {
        name: (ordinary, switches, xors)
        for name, ordinary, switches, xors in MIXED_CASES
    }
    summary_cases = summary.get("cases", [])
    require(errors, len(summary_cases) == 11, "mixed summary: case count is not 11")
    names = [item.get("name") for item in summary_cases]
    require(errors, len(set(names)) == len(names), "mixed summary: duplicate case names")
    require(
        errors,
        set(names) == set(expected_by_name),
        "mixed summary: decomposition names do not match the exact expected set",
    )

    normalized_cases = []
    raw_files = []
    for item in summary_cases:
        name = item.get("name")
        if name not in expected_by_name:
            continue
        ordinary, switches, xors = expected_by_name[name]
        decomposition = {
            "ordinary": ordinary,
            "switches": switches,
            "xors": xors,
            "components": ordinary + switches + xors,
            "weighted_gate": ordinary + 2 * switches + 3 * xors,
        }
        require(
            errors,
            item.get("decomposition") == decomposition,
            f"{name}: decomposition mismatch in mixed summary",
        )
        require(errors, item.get("status") == "unsat", f"{name}: summary is not UNSAT")
        runs = item.get("solver_runs", [])
        require(errors, len(runs) == 2, f"{name}: solver-run count is not two")
        run_by_solver = {run.get("solver"): run for run in runs}
        require(
            errors,
            set(run_by_solver) == set(SOLVERS),
            f"{name}: solver set mismatch",
        )
        normalized_runs = []
        for solver in SOLVERS:
            path = MIXED_RESULT_DIR / f"{name}_{solver}.json"
            if not path.is_file():
                errors.append(f"missing mixed result: {path}")
                continue
            payload = load_json(path)
            verify_strict_common(errors, payload, path)
            expect_fields(
                errors,
                payload,
                {
                    "status": "unsat",
                    "solver": solver,
                    "gate_bound": 9,
                    "components": decomposition["components"],
                    "exact_ordinary": ordinary,
                    "exact_switches": switches,
                    "exact_xors": xors,
                    "weighted_gate": 9,
                    "seed_current": False,
                },
                path.name,
            )
            run = run_by_solver.get(solver, {})
            digest = file_sha256(path)
            require(errors, run.get("status") == "unsat", f"{path.name}: ledger status mismatch")
            require(errors, run.get("sha256") == digest, f"{path.name}: ledger SHA-256 mismatch")
            require(
                errors,
                Path(str(run.get("path", ""))).resolve() == path.resolve(),
                f"{path.name}: ledger path mismatch",
            )
            for field in ("variables", "clauses", "build_seconds", "solve_seconds"):
                require(
                    errors,
                    run.get(field) == payload.get(field),
                    f"{path.name}: ledger {field} mismatch",
                )
            record = {
                "solver": solver,
                "path": str(path.resolve()),
                "sha256": digest,
                "status": payload.get("status"),
                "variables": payload.get("variables"),
                "clauses": payload.get("clauses"),
                "build_seconds": payload.get("build_seconds"),
                "solve_seconds": payload.get("solve_seconds"),
            }
            normalized_runs.append(record)
            raw_files.append(record_file(path))
        if len(normalized_runs) == 2:
            require(
                errors,
                len({run["variables"] for run in normalized_runs}) == 1,
                f"{name}: solver variable counts differ",
            )
            require(
                errors,
                len({run["clauses"] for run in normalized_runs}) == 1,
                f"{name}: solver clause counts differ",
            )
        normalized_cases.append(
            {
                "name": name,
                "decomposition": decomposition,
                "status": "unsat" if len(normalized_runs) == 2 else "incomplete",
                "solver_runs": normalized_runs,
            }
        )

    expected_files = {
        f"{name}_{solver}.json"
        for name, _ordinary, _switches, _xors in MIXED_CASES
        for solver in SOLVERS
    }
    actual_files = {path.name for path in MIXED_RESULT_DIR.glob("*.json")}
    require(
        errors,
        actual_files == expected_files,
        "mixed result directory does not contain exactly the expected 22 JSON files",
    )

    regression_records = []
    summary_regressions = {
        item.get("solver"): item for item in summary.get("positive_regressions", [])
    }
    require(
        errors,
        set(summary_regressions) == set(SOLVERS),
        "mixed summary: positive-regression solver set mismatch",
    )
    for solver, path in REGRESSIONS.items():
        record = verify_regression(errors, solver, path)
        regression_records.append(record)
        ledger = summary_regressions.get(solver, {})
        for field in ("status", "sha256", "variables", "clauses", "solve_seconds"):
            require(
                errors,
                ledger.get(field) == record.get(field),
                f"{path.name}: regression ledger {field} mismatch",
            )
        require(
            errors,
            Path(str(ledger.get("path", ""))).resolve() == path.resolve(),
            f"{path.name}: regression ledger path mismatch",
        )

    return {
        "summary": record_file(MIXED_SUMMARY),
        "status": summary.get("status"),
        "case_count": len(normalized_cases),
        "solver_run_count": len(raw_files),
        "cases": normalized_cases,
        "raw_result_files": raw_files,
        "positive_regressions": regression_records,
    }


def verify_n9_common(
    errors: list[str], payload: dict[str, Any], path: Path, clauses: int
) -> None:
    expect_fields(
        errors,
        payload,
        {
            "schema": "exact-80d7-s1-s2-joint-v1",
            "status": "unsat",
            "interface": "s1_s2_current80",
            "free_sources": [*SOURCE_NAMES, "0", "1"],
            "source_arrivals": {**SOURCE_ARRIVALS, "0": 0, "1": 0},
            "gate_bound": 9,
            "max_delay": 7,
            "components": 9,
            "exact_switches": 0,
            "exact_xors": 0,
            "solver": "cadical195",
            "variables": 11923,
            "clauses": clauses,
            "physical_nets": True,
            "output_deadlines": OUTPUT_DEADLINES,
        },
        path.name,
    )


def verify_n9(errors: list[str]) -> dict[str, Any]:
    payload = load_json(N9_RESULT)
    verify_n9_common(errors, payload, N9_RESULT, 95705)
    for field in (
        "last_output_shard",
        "other_output_gate_shard",
        "other_output_kind_shard",
    ):
        require(
            errors,
            payload.get(field) is None,
            f"{N9_RESULT.name}: main result unexpectedly has {field}",
        )

    auxiliary = []
    expected_names = set()
    for gate in range(8):
        path = ROOT_RESEARCH / (
            "s1-s2-current80-g9-n9-s0-x0-last1-"
            f"other{gate}-cadical195.json"
        )
        expected_names.add(path.name)
        if not path.is_file():
            errors.append(f"missing n9 auxiliary shard: {path}")
            continue
        item = load_json(path)
        verify_n9_common(errors, item, path, 95707)
        expect_fields(
            errors,
            item,
            {"last_output_shard": 1, "other_output_gate_shard": gate},
            path.name,
        )
        require(
            errors,
            item.get("other_output_kind_shard") is None,
            f"{path.name}: unexpected kind subshard",
        )
        auxiliary.append(
            {
                "other_output_gate": gate,
                **record_file(path),
                "status": item.get("status"),
                "variables": item.get("variables"),
                "clauses": item.get("clauses"),
                "solve_seconds": item.get("solve_seconds"),
            }
        )
    actual_names = {
        path.name
        for path in ROOT_RESEARCH.glob(
            "s1-s2-current80-g9-n9-s0-x0-last1-other*-cadical195.json"
        )
    }
    require(
        errors,
        actual_names == expected_names,
        "n9 auxiliary shard set is not exactly other_output_gate=0..7",
    )
    require(
        errors,
        len({item["other_output_gate"] for item in auxiliary}) == 8,
        "n9 auxiliary selector values are not pairwise distinct",
    )
    return {
        "main_unsharded_result": {
            **record_file(N9_RESULT),
            "status": payload.get("status"),
            "solver": payload.get("solver"),
            "variables": payload.get("variables"),
            "clauses": payload.get("clauses"),
            "solve_seconds": payload.get("solve_seconds"),
            "decomposition": {
                "ordinary": 9,
                "switches": 0,
                "xors": 0,
                "components": 9,
                "weighted_gate": 9,
            },
            "decisive": True,
        },
        "auxiliary_last_output_shards": {
            "decisive": False,
            "role": "diagnostic mutually exclusive selector subcases; the unsharded result is decisive",
            "last_output": 1,
            "other_output_gate_values": list(range(8)),
            "pairwise_disjoint_under_singleton_output_bus": True,
            "all_unsat": len(auxiliary) == 8
            and {item["status"] for item in auxiliary} == {"unsat"},
            "results": auxiliary,
        },
        "replay_entrypoint": record_file(N9_WRAPPER),
        "dynamic_dependencies": [
            record_file(N9_BASE),
            record_file(N9_EXACT_CORE),
            record_file(GENERIC_CNF),
        ],
        "provenance_note": (
            "The root artifact has no embedded script digest. Its own SHA-256 is "
            "therefore the primary immutable evidence; the pinned wrapper and "
            "dependencies are the reviewed replay entrypoint."
        ),
    }


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def root_boolean_projection() -> tuple[dict[tuple[int, ...], tuple[int, int]], int]:
    mapping: dict[tuple[int, ...], tuple[int, int]] = {}
    for case in range(32):
        a1, b1, a2, b2, c1 = ((case >> bit) & 1 for bit in range(5))
        g1 = a1 & b1
        p1 = a1 ^ b1
        c2 = g1 | (p1 & c1)
        s1 = p1 ^ c1
        g2 = a2 & b2
        v2 = a2 | b2
        p2 = a2 ^ b2
        c3 = g2 | (p2 & c2)
        s2 = p2 ^ c2
        sources = (a1, b1, g1, g2, v2, c1, c3)
        targets = (s1, s2)
        previous = mapping.get(sources)
        if previous is not None and previous != targets:
            raise RuntimeError("root Boolean projection is internally inconsistent")
        mapping[sources] = targets
    return mapping, 32


def verify_projection(errors: list[str]) -> dict[str, Any]:
    materializer = load_module(MATERIALIZER, "s1s2_cost9_complete_materializer")
    dag = load_json(AUTHORITATIVE_DAG)
    states = materializer.logical_states(tuple(dag["factory_dag"]["nodes"]))
    source_bits = [int(states[node_id]["bits"]) for node_id in SOURCE_IDS]
    source_drivens = [int(states[node_id]["driven"]) for node_id in SOURCE_IDS]
    target_bits = [int(states[node_id]["bits"]) for node_id in TARGET_IDS]

    strict_mapping: dict[tuple[int, ...], tuple[int, int]] = {}
    boolean_mapping: dict[tuple[int, ...], tuple[int, int]] = {}
    driven_variants: dict[tuple[int, ...], set[tuple[int, ...]]] = defaultdict(set)
    strict_conflicts = 0
    boolean_conflicts = 0
    for row in range(FULL_ROWS):
        values = tuple((bits >> row) & 1 for bits in source_bits)
        drivens = tuple((bits >> row) & 1 for bits in source_drivens)
        targets = tuple((bits >> row) & 1 for bits in target_bits)
        strict_signature = tuple(
            item for pair in zip(values, drivens, strict=True) for item in pair
        )
        previous = strict_mapping.get(strict_signature)
        if previous is not None and previous != targets:
            strict_conflicts += 1
        strict_mapping[strict_signature] = targets
        previous = boolean_mapping.get(values)
        if previous is not None and previous != targets:
            boolean_conflicts += 1
        boolean_mapping[values] = targets
        driven_variants[values].add(drivens)

    root_mapping, root_assignments = root_boolean_projection()
    variant_histogram = Counter(len(items) for items in driven_variants.values())
    z_stats = {}
    for label, node_id in (("C1", 45), ("C3", 56)):
        bits = int(states[node_id]["bits"])
        driven = int(states[node_id]["driven"])
        z_stats[label] = {
            "driven_rows": driven.bit_count(),
            "z_rows": FULL_ROWS - driven.bit_count(),
            "one_while_z_rows": (bits & ~driven).bit_count(),
        }

    checks = {
        "strict_signature_count_36": len(strict_mapping) == 36,
        "boolean_unique_signature_count_24": len(boolean_mapping) == 24,
        "root_assignment_count_32": root_assignments == 32,
        "root_unique_signature_count_24": len(root_mapping) == 24,
        "strict_targets_determined": strict_conflicts == 0,
        "boolean_targets_determined": boolean_conflicts == 0,
        "authoritative_boolean_map_equals_root_map": boolean_mapping == root_mapping,
        "driven_variant_histogram_is_12x1_plus_12x2": dict(variant_histogram)
        == {1: 12, 2: 12},
        "undriven_C1_C3_bits_are_zero": all(
            item["one_while_z_rows"] == 0 for item in z_stats.values()
        ),
    }
    for name, passed in checks.items():
        require(errors, passed, f"ordinary projection check failed: {name}")

    return {
        "authoritative_source": record_file(AUTHORITATIVE_DAG),
        "full_truth_rows": FULL_ROWS,
        "strict_value_driven_signature_count": len(strict_mapping),
        "boolean_assignment_count_in_n9_model": root_assignments,
        "boolean_unique_boundary_signature_count": len(boolean_mapping),
        "root_unique_boundary_signature_count": len(root_mapping),
        "driven_variants_per_boolean_signature_histogram": {
            str(key): value for key, value in sorted(variant_histogram.items())
        },
        "z_stats": z_stats,
        "checks": checks,
        "equivalence_scope": {
            "decomposition": {"ordinary": 9, "switches": 0, "xors": 0},
            "reason": [
                "active-bus normalization makes every selected ordinary input/output bus singleton",
                "ordinary component outputs are always driven",
                "authoritative C1/C3 undriven rows carry value bit zero, so Z0 and driven zero have the same ordinary Boolean input value",
                "authoritative value-only boundary-to-target map exactly equals the 32-assignment root truth-table map",
            ],
            "not_extended_to_switch_cases": True,
        },
    }


def enumerate_cost9() -> list[dict[str, int | str]]:
    items = []
    for xors in range(4):
        for switches in range((9 - 3 * xors) // 2 + 1):
            ordinary = 9 - 2 * switches - 3 * xors
            items.append(
                {
                    "name": f"o{ordinary}_s{switches}_x{xors}",
                    "ordinary": ordinary,
                    "switches": switches,
                    "xors": xors,
                    "components": ordinary + switches + xors,
                    "weighted_gate": ordinary + 2 * switches + 3 * xors,
                }
            )
    return items


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "s1s2_joint_strict_cost9_complete_summary.json",
    )
    args = parser.parse_args()

    errors: list[str] = []
    pinned_files = verify_pinned_files(errors)
    mixed = verify_mixed(errors)
    n9 = verify_n9(errors)
    projection = verify_projection(errors)

    enumerated = enumerate_cost9()
    expected = [
        {
            "name": name,
            "ordinary": ordinary,
            "switches": switches,
            "xors": xors,
            "components": ordinary + switches + xors,
            "weighted_gate": ordinary + 2 * switches + 3 * xors,
        }
        for name, ordinary, switches, xors in ALL_DECOMPOSITIONS
    ]
    require(
        errors,
        {tuple(sorted(item.items())) for item in enumerated}
        == {tuple(sorted(item.items())) for item in expected},
        "cost equation enumeration does not equal n9 plus the eleven mixed cases",
    )
    require(errors, len(enumerated) == 12, "cost-nine decomposition count is not 12")

    complete = not errors
    payload: dict[str, Any] = {
        "schema": "byte-adder-80d7-s1-s2-joint-exact-cost9-complete-summary-v1",
        "scope": {
            "authoritative_frontier": {"gate": 80, "delay": 7, "nand": 560},
            "cut_node_ids": CUT_NODE_IDS,
            "source_ids": SOURCE_IDS,
            "source_names": SOURCE_NAMES,
            "source_arrivals": SOURCE_ARRIVALS,
            "target_ids": TARGET_IDS,
            "target_names": TARGET_NAMES,
            "output_deadlines": OUTPUT_DEADLINES,
            "full_truth_rows": FULL_ROWS,
            "strict_compressed_signature_rows": 36,
            "fixed_retained_source_pool": True,
            "co_synthesizes_retained_boundary": False,
        },
        "library_costs": {"ordinary": 1, "switch": 2, "xor": 3},
        "cost_equation": "ordinary + 2*switches + 3*xors = 9",
        "all_nonnegative_integer_decompositions": enumerated,
        "decomposition_count": len(enumerated),
        "partition": {
            "all_ordinary": {
                "decomposition": expected[0],
                "evidence_family": "root Boolean ordinary-only physical-net model",
                "status": n9["main_unsharded_result"]["status"],
                "solver_runs": 1,
            },
            "mixed": {
                "decompositions": expected[1:],
                "evidence_family": "strict value/driven physical-net model",
                "status": mixed["status"],
                "solver_runs": mixed["solver_run_count"],
            },
            "covered_decomposition_count": 1 + mixed["case_count"],
            "complete": complete and 1 + mixed["case_count"] == 12,
        },
        "ordinary_projection_equivalence": projection,
        "all_ordinary_evidence": n9,
        "mixed_evidence": mixed,
        "pinned_files": pinned_files,
        "errors": errors,
        "coverage_complete": complete,
        "all_exact_cost9_unsat": complete,
        "status": "all-exact-cost9-unsat" if complete else "incomplete",
        "limitations": [
            "fixed retained source pool only",
            "does not co-synthesize the retained boundary",
            "does not cover alternate cross-output cuts",
            "is not a global 79/7 lower bound",
        ],
        "summarizer_sha256": file_sha256(Path(__file__).resolve()),
    }
    output_sha = atomic_write(args.output, payload)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "status": payload["status"],
                "decompositions": payload["decomposition_count"],
                "mixed_solver_runs": mixed["solver_run_count"],
                "n9_auxiliary_shards": len(
                    n9["auxiliary_last_output_shards"]["results"]
                ),
                "positive_regressions": len(mixed["positive_regressions"]),
                "errors": len(errors),
                "output_sha256": output_sha,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
