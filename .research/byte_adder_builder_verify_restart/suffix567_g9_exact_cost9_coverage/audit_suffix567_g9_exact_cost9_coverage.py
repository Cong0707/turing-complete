"""Merge and audit the suffix567 exact weighted-cost-nine kind shards.

This is an artifact audit, not a SAT rerun.  It derives the complete weighted
decomposition universe from the primitive costs, verifies every remote sweep
spec/summary/record/output/log chain, and proves that each timeout parent was
replaced by a complete, disjoint next-slot kind partition.

Offline research only: no game launch, save access, candidate write, or
deployment.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
BUILDER_ROOT = HERE.parent
REPO_ROOT = BUILDER_ROOT.parents[1]

GATE_BOUND = 9
KINDS = ("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH")
ORDINARY_KINDS = KINDS[:5]
KIND_COST = {
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 3,
    "SWITCH": 2,
}

FREE_SOURCES = (
    "a5", "b5", "a6", "b6", "a7", "b7", "C5",
    "G5", "Q5", "P5", "G6", "Q6", "P6",
    "G7", "Q7", "P7", "T", "D", "G", "C7", "T5", "0", "1",
)
SOURCE_ARRIVALS = {
    "a5": 0,
    "b5": 0,
    "a6": 0,
    "b6": 0,
    "a7": 0,
    "b7": 0,
    "C5": 4,
    "G5": 1,
    "Q5": 1,
    "P5": 2,
    "G6": 1,
    "Q6": 1,
    "P6": 2,
    "G7": 1,
    "Q7": 1,
    "P7": 2,
    "T": 3,
    "D": 4,
    "G": 2,
    "C7": 5,
    "T5": 5,
    "0": 0,
    "1": 0,
}

SPEC_NAMES = (
    "suffix567_g9_n7_s0_x1_slot0_kind_sweep.json",
    "suffix567_g9_n7_s2_x0_slot0_kind_sweep.json",
    "suffix567_g9_n8_s1_x0_slot0_kind_sweep.json",
    "suffix567_g9_n9_nor_prefix_slot2_kind_sweep.json",
    "suffix567_g9_n9_remaining_slot01_kind_sweep.json",
    "suffix567_g9_n9_s0_x0_slot0_kind_sweep.json",
    "suffix567_g9_priority_slot01_sweep.json",
    "suffix567_g9_switch34_slot0_kind_sweep.json",
    "suffix567_g9_x1_switch123_slot0_kind_sweep.json",
    "suffix567_g9_x23_feasible_slot0_kind_sweep.json",
)

SOURCE_DEPENDENCIES = (
    ".research/byte_adder_builder_verify_restart/exact_suffix567_kind_shard.py",
    ".research/byte_adder_builder_verify_restart/suffix567_kind_shard_constraint_regression.json",
    ".research/byte_adder_advanced_switch_cells_agent/exact_suffix567_phase_sat.py",
    ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py",
    ".research/byte_adder_boolean_superopt_agent/exact_adder_block_sat.py",
    ".research/rng_468_joint_macro/joint_parity_cnf.py",
)


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return payload


def relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError as error:
        raise RuntimeError(f"artifact escapes repository: {resolved}") from error


def same_path(raw: object, expected: Path) -> bool:
    return isinstance(raw, str) and Path(raw).resolve() == expected.resolve()


def composition_name(composition: tuple[int, int, int]) -> str:
    components, switches, xors = composition
    return f"n{components}_s{switches}_x{xors}"


def exact_cost_compositions(bound: int) -> tuple[tuple[int, int, int], ...]:
    """Derive all (components, switches, xors) with exact weighted cost."""

    result: list[tuple[int, int, int]] = []
    for xors in range(bound // 3 + 1):
        for switches in range(bound // 2 + 1):
            components = bound - switches - 2 * xors
            if components <= 0:
                continue
            if switches + xors > components:
                continue
            result.append((components, switches, xors))
    return tuple(result)


def remaining_kinds(
    composition: tuple[int, int, int], prefix: tuple[str, ...]
) -> tuple[str, ...]:
    components, switches, xors = composition
    exact_counts = {
        "ordinary": components - switches - xors,
        "switch": switches,
        "xor": xors,
    }
    used_counts = {
        "ordinary": sum(kind in ORDINARY_KINDS for kind in prefix),
        "switch": prefix.count("SWITCH"),
        "xor": prefix.count("XOR"),
    }
    if any(used_counts[key] > exact_counts[key] for key in exact_counts):
        return ()
    allowed: list[str] = []
    if used_counts["ordinary"] < exact_counts["ordinary"]:
        allowed.extend(ORDINARY_KINDS)
    if used_counts["xor"] < exact_counts["xor"]:
        allowed.append("XOR")
    if used_counts["switch"] < exact_counts["switch"]:
        allowed.append("SWITCH")
    return tuple(allowed)


def ast_literal_assignment(path: Path, name: str) -> object:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == name:
            return ast.literal_eval(node.value)
    raise RuntimeError(f"missing literal assignment {name} in {path}")


def wrapper_constraint_markers(path: Path) -> dict[str, int]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    injected = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == "bound_insert" for target in node.targets):
            injected = ast.literal_eval(node.value)
            break
    if not isinstance(injected, str):
        raise RuntimeError("wrapper bound_insert is not a literal string")
    markers = {
        "slot_range_check": injected.count("if not 0 <= slot < args.components:"),
        "kind_membership_check": injected.count("if kind not in G.KINDS:"),
        "duplicate_slot_check": injected.count("if slot in forced_slot_kinds"),
        "unit_clause": injected.count(
            "enc.clause((kinds[slot][G.KINDS.index(kind)],))"
        ),
        "payload_capture": injected.count("args.forced_slot_kinds ="),
    }
    if any(count != 1 for count in markers.values()):
        raise RuntimeError(f"forced-kind injection contract changed: {markers}")
    return markers


def exact_count_markers(path: Path) -> dict[str, int]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rendered = [
        ast.unparse(node)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "equals"
    ]
    switch_count = sum(
        "row[G.SWITCH]" in call and "bound=args.switches" in call
        for call in rendered
    )
    xor_count = sum(
        "row[G.XOR]" in call and "bound=args.xors" in call
        for call in rendered
    )
    if switch_count != 1 or xor_count != 1:
        raise RuntimeError(
            "exact Switch/XOR cardinality contract changed: "
            f"switch={switch_count}, xor={xor_count}"
        )
    return {"exact_switch_cardinality": switch_count, "exact_xor_cardinality": xor_count}


def parse_command(command: object, wrapper: Path) -> tuple[dict[str, str], tuple[str, ...]]:
    if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
        raise RuntimeError("record command is not a string list")
    if len(command) < 4 or not same_path(command[1], wrapper):
        raise RuntimeError(f"record does not invoke the reviewed wrapper: {command!r}")

    options: dict[str, str] = {}
    forced: dict[int, str] = {}
    index = 2
    while index < len(command):
        option = command[index]
        if not option.startswith("--") or index + 1 >= len(command):
            raise RuntimeError(f"malformed command tail: {command[index:]!r}")
        value = command[index + 1]
        if option == "--slot-kind":
            try:
                raw_slot, kind = value.split(":", 1)
                slot = int(raw_slot)
            except ValueError as error:
                raise RuntimeError(f"invalid forced kind {value!r}") from error
            if slot in forced:
                raise RuntimeError(f"duplicate forced slot {slot}")
            if kind not in KINDS:
                raise RuntimeError(f"unsupported forced kind {kind!r}")
            forced[slot] = kind
        else:
            key = option[2:]
            if key in options:
                raise RuntimeError(f"duplicate command option {option}")
            options[key] = value
        index += 2

    if sorted(forced) != list(range(len(forced))):
        raise RuntimeError(f"forced slots are not a consecutive prefix: {forced!r}")
    return options, tuple(forced[slot] for slot in range(len(forced)))


def format_arguments(arguments: object, value: dict[str, Any]) -> list[str]:
    if not isinstance(arguments, list) or not all(isinstance(item, str) for item in arguments):
        raise RuntimeError("sweep arguments are not a string list")
    try:
        return [item.format_map(value) for item in arguments]
    except KeyError as error:
        raise RuntimeError(f"unresolved sweep placeholder: {error}") from error


def verify_unsat_output(
    path: Path,
    composition: tuple[int, int, int],
    prefix: tuple[str, ...],
) -> dict[str, Any]:
    payload = load_json(path)
    components, switches, xors = composition
    expected = {
        "schema": "exact-suffix567-shared-phase-v1",
        "status": "unsat",
        "interface": "s6",
        "free_sources": list(FREE_SOURCES),
        "source_arrivals": SOURCE_ARRIVALS,
        "gate_bound": GATE_BOUND,
        "max_delay": 7,
        "components": components,
        "exact_switches": switches,
        "exact_xors": xors,
        "solver": "cadical195",
        "physical_nets": True,
        "output_deadlines": [6, 7, 7, 7],
        "forced_slot_kinds": {str(slot): kind for slot, kind in enumerate(prefix)},
    }
    mismatches = {
        key: {"expected": value, "actual": payload.get(key)}
        for key, value in expected.items()
        if payload.get(key) != value
    }
    if mismatches:
        raise RuntimeError(f"UNSAT payload contract mismatch in {path}: {mismatches}")
    for field in ("variables", "clauses"):
        value = payload.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise RuntimeError(f"invalid {field} in {path}: {value!r}")
    solve_seconds = payload.get("solve_seconds")
    if isinstance(solve_seconds, bool) or not isinstance(solve_seconds, (int, float)):
        raise RuntimeError(f"invalid solve_seconds in {path}: {solve_seconds!r}")
    if solve_seconds < 0:
        raise RuntimeError(f"negative solve_seconds in {path}: {solve_seconds!r}")
    if components + switches + 2 * xors != GATE_BOUND:
        raise RuntimeError(f"non-exact weighted composition in {path}")
    return payload


def verify_log(log_path: Path, output_path: Path, output_sha256: str) -> None:
    output_text = output_path.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip("\n")
    log_text = log_path.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip("\n")
    expected = output_text + "\nsha256=" + output_sha256
    if log_text != expected:
        raise RuntimeError(f"log is not the exact normalized output plus SHA: {log_path}")


def prefix_is_ancestor(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    return len(left) < len(right) and right[: len(left)] == left


def audit() -> dict[str, Any]:
    wrapper = BUILDER_ROOT / "exact_suffix567_kind_shard.py"
    discovered_specs = {
        path.name for path in BUILDER_ROOT.glob("suffix567*g9*sweep.json")
    }
    if discovered_specs != set(SPEC_NAMES):
        raise RuntimeError(
            "suffix567 g9 sweep inventory changed: "
            f"missing={sorted(set(SPEC_NAMES) - discovered_specs)!r}, "
            f"extra={sorted(discovered_specs - set(SPEC_NAMES))!r}"
        )
    source_paths = [REPO_ROOT / name for name in SOURCE_DEPENDENCIES]
    for path in source_paths:
        if not path.is_file():
            raise RuntimeError(f"missing source dependency: {path}")

    generic = REPO_ROOT / ".research/rng_468_joint_macro/joint_parity_cnf.py"
    worker = REPO_ROOT / ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py"
    parsed_kinds = tuple(ast_literal_assignment(generic, "KINDS"))
    parsed_costs = tuple(ast_literal_assignment(generic, "COST"))
    parsed_delays = tuple(ast_literal_assignment(generic, "DELAY"))
    if parsed_kinds != KINDS:
        raise RuntimeError(f"primitive kind universe changed: {parsed_kinds!r}")
    if parsed_costs != tuple(KIND_COST[kind] for kind in KINDS):
        raise RuntimeError(f"primitive costs changed: {parsed_costs!r}")
    if parsed_delays != (1, 1, 1, 1, 1, 2, 1):
        raise RuntimeError(f"primitive delays changed: {parsed_delays!r}")
    wrapper_markers = wrapper_constraint_markers(wrapper)
    cardinality_markers = exact_count_markers(worker)

    regression_path = BUILDER_ROOT / "suffix567_kind_shard_constraint_regression.json"
    regression = load_json(regression_path)
    regression_expected = {
        "schema": "exact-suffix567-shared-phase-v1",
        "status": "unsat",
        "interface": "s6",
        "gate_bound": 9,
        "max_delay": 7,
        "components": 9,
        "exact_switches": 0,
        "exact_xors": 0,
        "physical_nets": True,
        "output_deadlines": [6, 7, 7, 7],
        "forced_slot_kinds": {"0": "SWITCH"},
    }
    if any(regression.get(key) != value for key, value in regression_expected.items()):
        raise RuntimeError("forced-kind contradiction regression changed")

    artifact_paths: set[Path] = set(source_paths)
    regions: dict[tuple[tuple[int, int, int], tuple[str, ...]], dict[str, Any]] = {}
    summary_evidence: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()

    for spec_name in SPEC_NAMES:
        spec_path = BUILDER_ROOT / spec_name
        spec = load_json(spec_path)
        artifact_paths.add(spec_path)
        if spec.get("schema") != "tc-byte-adder-remote-sweep-v1":
            raise RuntimeError(f"unexpected sweep schema: {spec_path}")
        if not same_path(spec.get("script"), wrapper):
            raise RuntimeError(f"sweep uses another script: {spec_path}")
        if not same_path(spec.get("working_directory"), REPO_ROOT):
            raise RuntimeError(f"sweep working directory changed: {spec_path}")
        if spec.get("timeout_seconds") != 300 or spec.get("stop_on_first_sat") is not True:
            raise RuntimeError(f"sweep execution contract changed: {spec_path}")

        raw_values = spec.get("values")
        if not isinstance(raw_values, list) or not raw_values:
            raise RuntimeError(f"sweep has no values: {spec_path}")
        values: dict[str, dict[str, Any]] = {}
        for value in raw_values:
            if not isinstance(value, dict) or not isinstance(value.get("name"), str):
                raise RuntimeError(f"invalid sweep value in {spec_path}: {value!r}")
            name = value["name"]
            if name in values:
                raise RuntimeError(f"duplicate sweep value {name}: {spec_path}")
            values[name] = value

        summary_path = BUILDER_ROOT / str(spec.get("summary"))
        summary = load_json(summary_path)
        artifact_paths.add(summary_path)
        expected_summary_fields = {
            "schema": "tc-byte-adder-remote-sweep-summary-v1",
            "name": spec.get("name"),
            "spec_sha256": file_sha256(spec_path),
            "script_sha256": file_sha256(wrapper),
            "workers": spec.get("workers"),
            "timeout_seconds": spec.get("timeout_seconds"),
            "memory_mb_per_process": spec.get("memory_mb_per_process"),
            "stop_on_first_sat": spec.get("stop_on_first_sat"),
            "stop_event_set": False,
            "finished": True,
        }
        mismatches = {
            key: {"expected": value, "actual": summary.get(key)}
            for key, value in expected_summary_fields.items()
            if summary.get(key) != value
        }
        if mismatches:
            raise RuntimeError(f"summary contract mismatch in {summary_path}: {mismatches}")
        if not same_path(summary.get("spec"), spec_path):
            raise RuntimeError(f"summary points at another spec: {summary_path}")
        if not same_path(summary.get("script"), wrapper):
            raise RuntimeError(f"summary points at another script: {summary_path}")

        raw_results = summary.get("results")
        if not isinstance(raw_results, list) or len(raw_results) != len(values):
            raise RuntimeError(f"summary result count mismatch: {summary_path}")
        names_seen: set[str] = set()
        summary_counts: Counter[str] = Counter()
        result_directory = BUILDER_ROOT / str(spec.get("result_directory"))
        log_directory = BUILDER_ROOT / str(spec.get("log_directory"))

        for result in raw_results:
            if not isinstance(result, dict) or not isinstance(result.get("value"), dict):
                raise RuntimeError(f"invalid summary result in {summary_path}")
            value = result["value"]
            name = value.get("name")
            if name not in values or value != values[name] or name in names_seen:
                raise RuntimeError(f"summary value mismatch/duplicate {name}: {summary_path}")
            names_seen.add(name)

            record_path = result_directory / f"{name}.json"
            record = load_json(record_path)
            artifact_paths.add(record_path)
            if record != result:
                raise RuntimeError(f"summary result differs from record: {record_path}")
            expected_tail = format_arguments(spec.get("arguments"), value)
            if record.get("command", [])[2:] != expected_tail:
                raise RuntimeError(f"record command differs from expanded spec: {record_path}")

            options, prefix = parse_command(record.get("command"), wrapper)
            expected_option_keys = {
                "interface", "gate-bound", "max-delay", "components", "switches",
                "xors", "output-deadlines", "solver", "timeout", "output",
            }
            if set(options) != expected_option_keys:
                raise RuntimeError(f"record option set changed in {record_path}: {options}")
            expected_fixed_options = {
                "interface": "s6",
                "gate-bound": "9",
                "max-delay": "7",
                "output-deadlines": "6,7,7,7",
                "solver": "cadical195",
                "timeout": "0",
            }
            if any(options.get(key) != value for key, value in expected_fixed_options.items()):
                raise RuntimeError(f"fixed SAT contract changed in {record_path}")
            try:
                composition = tuple(
                    int(options[key]) for key in ("components", "switches", "xors")
                )
            except ValueError as error:
                raise RuntimeError(f"non-integer composition in {record_path}") from error
            if len(composition) != 3:
                raise AssertionError(composition)
            composition = (composition[0], composition[1], composition[2])
            components, switches, xors = composition
            if (
                components + switches + 2 * xors != GATE_BOUND
                or switches + xors > components
                or len(prefix) > components
            ):
                raise RuntimeError(f"invalid exact-cost composition/prefix in {record_path}")

            output_path = Path(options["output"])
            log_path = log_directory / f"{name}.log"
            if not same_path(record.get("working_directory"), REPO_ROOT):
                raise RuntimeError(f"record working directory changed: {record_path}")
            if not same_path(record.get("output"), output_path):
                raise RuntimeError(f"record output path differs from command: {record_path}")
            if not same_path(record.get("log"), log_path):
                raise RuntimeError(f"record log path differs from spec: {record_path}")
            relative(output_path)
            relative(log_path)
            artifact_paths.add(log_path)

            region_key = (composition, prefix)
            if region_key in regions:
                raise RuntimeError(
                    f"duplicate composition/prefix region {composition_name(composition)} {prefix}"
                )
            state = record.get("state")
            status = record.get("status")
            return_code = record.get("return_code")
            if (state, status, return_code) == ("completed", "unsat", 0):
                classification = "unsat"
                if not output_path.is_file() or not log_path.is_file():
                    raise RuntimeError(f"missing terminal artifact for {record_path}")
                artifact_paths.add(output_path)
                actual_output_sha = file_sha256(output_path)
                actual_log_sha = file_sha256(log_path)
                if record.get("output_sha256") != actual_output_sha:
                    raise RuntimeError(f"output SHA mismatch: {record_path}")
                if record.get("log_sha256") != actual_log_sha:
                    raise RuntimeError(f"log SHA mismatch: {record_path}")
                output = verify_unsat_output(output_path, composition, prefix)
                verify_log(log_path, output_path, actual_output_sha)
                evidence = {
                    "record": relative(record_path),
                    "record_sha256": file_sha256(record_path),
                    "output": relative(output_path),
                    "output_sha256": actual_output_sha,
                    "log": relative(log_path),
                    "log_sha256": actual_log_sha,
                    "variables": output["variables"],
                    "clauses": output["clauses"],
                    "solve_seconds": output["solve_seconds"],
                }
            elif (state, status, return_code) == ("timeout", None, 1):
                classification = "timeout-parent"
                if output_path.exists() or record.get("output_sha256") is not None:
                    raise RuntimeError(f"timeout unexpectedly has an output: {record_path}")
                if not log_path.is_file() or log_path.read_bytes() != b"":
                    raise RuntimeError(f"timeout log is not empty: {record_path}")
                if record.get("log_sha256") != sha256(b"").hexdigest():
                    raise RuntimeError(f"timeout empty-log SHA mismatch: {record_path}")
                elapsed = record.get("elapsed_seconds")
                if not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool) or elapsed < 300:
                    raise RuntimeError(f"timeout elapsed time is invalid: {record_path}")
                evidence = {
                    "record": relative(record_path),
                    "record_sha256": file_sha256(record_path),
                    "missing_output": relative(output_path),
                    "empty_log": relative(log_path),
                    "empty_log_sha256": record["log_sha256"],
                    "elapsed_seconds": elapsed,
                }
            else:
                raise RuntimeError(
                    f"SAT, UNKNOWN output, or runtime failure in {record_path}: "
                    f"state={state!r}, status={status!r}, return_code={return_code!r}"
                )

            status_counts[classification] += 1
            summary_counts[classification] += 1
            regions[region_key] = {
                "composition": composition,
                "prefix": prefix,
                "classification": classification,
                "evidence": evidence,
            }

        if names_seen != set(values):
            raise RuntimeError(f"summary omits values: {summary_path}")
        summary_evidence.append({
            "spec": relative(spec_path),
            "spec_sha256": file_sha256(spec_path),
            "summary": relative(summary_path),
            "summary_sha256": file_sha256(summary_path),
            "record_count": len(raw_results),
            "unsat_count": summary_counts["unsat"],
            "timeout_parent_count": summary_counts["timeout-parent"],
            "python": summary.get("python"),
        })

    expected_compositions = exact_cost_compositions(GATE_BOUND)
    initial_by_composition: dict[tuple[int, int, int], set[tuple[str, ...]]] = defaultdict(set)
    for composition, prefix in regions:
        if len(prefix) == 1:
            initial_by_composition[composition].add(prefix)
    if set(initial_by_composition) != set(expected_compositions):
        raise RuntimeError(
            "initial composition coverage mismatch: "
            f"expected={expected_compositions!r}, actual={tuple(initial_by_composition)!r}"
        )
    expected_slot0 = {(kind,) for kind in KINDS}
    for composition in expected_compositions:
        if initial_by_composition[composition] != expected_slot0:
            raise RuntimeError(
                f"slot-0 kind coverage mismatch for {composition_name(composition)}"
            )

    visited: set[tuple[tuple[int, int, int], tuple[str, ...]]] = set()
    terminal_leaves: list[dict[str, Any]] = []
    timeout_parents: list[dict[str, Any]] = []
    composition_results: list[dict[str, Any]] = []

    def visit(
        composition: tuple[int, int, int], prefix: tuple[str, ...]
    ) -> tuple[int, int]:
        key = (composition, prefix)
        if key not in regions:
            raise RuntimeError(
                f"missing region {composition_name(composition)} prefix={prefix!r}"
            )
        if key in visited:
            raise RuntimeError(f"region visited twice: {key!r}")
        visited.add(key)
        region = regions[key]
        if region["classification"] == "unsat":
            terminal_leaves.append({
                "composition": composition_name(composition),
                "forced_prefix": list(prefix),
                **region["evidence"],
            })
            return 1, 0

        allowed = remaining_kinds(composition, prefix)
        if not allowed:
            raise RuntimeError(f"timeout cannot be subdivided further: {key!r}")
        expected_children = {prefix + (kind,) for kind in allowed}
        actual_children = {
            child_prefix
            for child_composition, child_prefix in regions
            if child_composition == composition
            and len(child_prefix) == len(prefix) + 1
            and child_prefix[:-1] == prefix
        }
        if actual_children != expected_children:
            raise RuntimeError(
                f"incomplete timeout refinement for {composition_name(composition)} "
                f"{prefix!r}: missing={sorted(expected_children - actual_children)!r}, "
                f"extra={sorted(actual_children - expected_children)!r}"
            )
        timeout_parents.append({
            "composition": composition_name(composition),
            "forced_prefix": list(prefix),
            "next_slot": len(prefix),
            "partition_kinds": list(allowed),
            "child_count": len(expected_children),
            **region["evidence"],
        })
        leaves = timeouts = 0
        for child in sorted(expected_children):
            child_leaves, child_timeouts = visit(composition, child)
            leaves += child_leaves
            timeouts += child_timeouts
        return leaves, timeouts + 1

    for composition in expected_compositions:
        before_leaves = len(terminal_leaves)
        before_timeouts = len(timeout_parents)
        for prefix in sorted(expected_slot0):
            visit(composition, prefix)
        composition_results.append({
            "name": composition_name(composition),
            "components": composition[0],
            "ordinary": composition[0] - composition[1] - composition[2],
            "switches": composition[1],
            "xors": composition[2],
            "weighted_cost": composition[0] + composition[1] + 2 * composition[2],
            "slot0_partition_kind_count": len(KINDS),
            "terminal_unsat_leaf_count": len(terminal_leaves) - before_leaves,
            "resolved_timeout_parent_count": len(timeout_parents) - before_timeouts,
            "status": "unsat-covered",
        })

    if visited != set(regions):
        missing = sorted(set(regions) - visited)
        raise RuntimeError(f"orphan or unreachable shard records: {missing!r}")
    for index, left in enumerate(terminal_leaves):
        left_comp = left["composition"]
        left_prefix = tuple(left["forced_prefix"])
        for right in terminal_leaves[index + 1 :]:
            if right["composition"] != left_comp:
                continue
            right_prefix = tuple(right["forced_prefix"])
            if prefix_is_ancestor(left_prefix, right_prefix) or prefix_is_ancestor(
                right_prefix, left_prefix
            ):
                raise RuntimeError(
                    f"terminal regions overlap by prefix: {left_comp} "
                    f"{left_prefix!r} {right_prefix!r}"
                )

    if status_counts != Counter({"unsat": 108, "timeout-parent": 6}):
        raise RuntimeError(f"unexpected raw status counts: {status_counts!r}")
    if len(terminal_leaves) != 108 or len(timeout_parents) != 6:
        raise RuntimeError("unexpected terminal/timeout tree counts")

    n9 = (9, 0, 0)
    n9_timeouts = {
        prefix for composition, prefix in regions
        if composition == n9 and regions[(composition, prefix)]["classification"] == "timeout-parent"
    }
    expected_n9_timeouts = {
        ("AND",), ("NAND",), ("NOR",), ("OR",),
        ("NOR", "NOR"), ("NOR", "OR"),
    }
    if n9_timeouts != expected_n9_timeouts:
        raise RuntimeError(f"n9 timeout tree changed: {n9_timeouts!r}")

    artifact_hashes = {
        relative(path): file_sha256(path)
        for path in sorted(artifact_paths, key=lambda item: relative(item))
    }
    terminal_leaves.sort(key=lambda item: (item["composition"], item["forced_prefix"]))
    timeout_parents.sort(key=lambda item: (item["composition"], item["forced_prefix"]))

    return {
        "schema": "suffix567-exact-cost9-independent-coverage-audit-v1",
        "status": "complete-exact-cost9-unsat-coverage",
        "scope": {
            "interface": "s6",
            "outputs": ["S5", "S6", "S7", "C8"],
            "gate_bound": GATE_BOUND,
            "max_delay": 7,
            "output_deadlines": [6, 7, 7, 7],
            "solver": "cadical195",
            "physical_nets": True,
            "claim": (
                "No exact weighted-cost-nine suffix567 network exists within the "
                "fixed source/interface/encoding contract represented by these shards."
            ),
            "not_claimed": (
                "This is not a global 79/7 lower bound and does not vary the fixed "
                "upstream suffix source shell."
            ),
        },
        "primitive_contract": {
            "kinds": list(parsed_kinds),
            "costs": dict(zip(parsed_kinds, parsed_costs, strict=True)),
            "delays": dict(zip(parsed_kinds, parsed_delays, strict=True)),
            "exact_cost_equation": "components + switches + 2*xors = 9",
            "ordinary_count_equation": "components - switches - xors",
            "exact_switch_xor_cardinality_markers": cardinality_markers,
            "forced_kind_wrapper_markers": wrapper_markers,
            "forced_kind_contradiction_regression": {
                "path": relative(regression_path),
                "sha256": file_sha256(regression_path),
                "forced_slot_kinds": regression["forced_slot_kinds"],
                "status": regression["status"],
            },
        },
        "coverage_proof": {
            "derived_composition_count": len(expected_compositions),
            "observed_composition_count": len(initial_by_composition),
            "missing_compositions": [],
            "extra_compositions": [],
            "slot0_kind_partition": list(KINDS),
            "slot0_partition_complete_for_all_compositions": True,
            "raw_job_count": len(regions),
            "raw_unsat_count": status_counts["unsat"],
            "raw_timeout_parent_count": status_counts["timeout-parent"],
            "raw_sat_count": 0,
            "raw_runtime_failure_count": 0,
            "terminal_unsat_leaf_count": len(terminal_leaves),
            "resolved_timeout_parent_count": len(timeout_parents),
            "unresolved_timeout_parent_count": 0,
            "orphan_record_count": 0,
            "duplicate_region_count": 0,
            "terminal_prefix_overlap_count": 0,
            "all_terminal_leaves_unsat": True,
            "coverage_complete": True,
        },
        "compositions": composition_results,
        "n9_ordinary_refinement": {
            "composition": "n9_s0_x0",
            "initial_timeout_prefixes": [[kind] for kind in ("AND", "NAND", "NOR", "OR")],
            "slot1_partition_kinds": list(ORDINARY_KINDS),
            "slot1_partition_count": 20,
            "slot1_unsat_count": 18,
            "slot1_timeout_prefixes": [["NOR", "NOR"], ["NOR", "OR"]],
            "slot2_partition_kinds": list(ORDINARY_KINDS),
            "slot2_partition_count": 10,
            "slot2_unsat_count": 10,
            "remaining_unknown_count": 0,
            "partition_reason": (
                "exact_switches=0 and exact_xors=0 make the five ordinary kinds "
                "the complete feasible next-slot kind universe"
            ),
        },
        "summary_evidence": sorted(summary_evidence, key=lambda item: item["spec"]),
        "timeout_parent_evidence": timeout_parents,
        "terminal_leaf_evidence": terminal_leaves,
        "artifact_integrity": {
            "file_count": len(artifact_hashes),
            "files": artifact_hashes,
        },
    }


def write_manifest(
    manifest_path: Path,
    audit_path: Path,
    report_path: Path,
    result: dict[str, Any],
    extra_paths: Iterable[Path] = (),
) -> None:
    paths = [REPO_ROOT / name for name in result["artifact_integrity"]["files"]]
    paths.extend((Path(__file__).resolve(), audit_path.resolve(), report_path.resolve()))
    paths.extend(path.resolve() for path in extra_paths)
    unique = {path.resolve() for path in paths}
    if manifest_path.resolve() in unique:
        raise RuntimeError("manifest must exclude itself")
    entries = sorted((relative(path), file_sha256(path)) for path in unique)
    lines = [
        "# suffix567 exact weighted-cost-nine independent coverage closure",
        "# SHA-256, lowercase. Paths are repository-relative.",
        "# This manifest intentionally excludes itself.",
        f"# entries={len(entries)}",
        "",
    ]
    lines.extend(f"{digest}  {name}" for name, digest in entries)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "independent_coverage_audit.json",
    )
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--history", type=Path)
    args = parser.parse_args()

    result = audit()
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(encoded, encoding="utf-8", newline="\n")
    if args.manifest is not None:
        if args.report is None or not args.report.resolve().is_file():
            raise RuntimeError("--manifest requires an existing --report")
        extra_paths: tuple[Path, ...] = ()
        if args.history is not None:
            if not args.history.resolve().is_file():
                raise RuntimeError("--history must name an existing file")
            extra_paths = (args.history.resolve(),)
        write_manifest(
            args.manifest.resolve(),
            output,
            args.report.resolve(),
            result,
            extra_paths,
        )
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
