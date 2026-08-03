"""Independently audit downloaded reachable-input-permutation artifacts.

The expensive Espresso/ABC searches are deliberately not rerun.  This tool
checks the complete search summaries, validates every locally present input
and timing artifact, and runs the authoritative mapped-residual importer twice
on each locally available mapped BLIF.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import random
import re
from typing import Any

import audit_reachable_output_phase_artifacts as phase_audit


HERE = Path(__file__).resolve().parent
DEFAULT_DAG = HERE / "byte-adder-hybrid-phasefold-g80-d7.json"
DEFAULT_METADATA = HERE / "abc_residual_current80" / "metadata.json"
DEFAULT_PLA = (
    HERE / "abc_residual_current80" / "care_pla" / "reachable_relation_fr.pla"
)
DEFAULT_LIBRARY = HERE.parent / "turing-complete.genlib"
PERM_RE = re.compile(r"^perm_(\d{3})_phase_([0-9a-fA-F]{3})$")


def make_permutations(count: int, arrivals: list[int]) -> list[tuple[int, ...]]:
    """Mirror the search script's deterministic generator without importing PyEDA."""

    if count < 1:
        raise ValueError("count must be positive")
    width = len(arrivals)
    candidates = [
        tuple(range(width)),
        tuple(reversed(range(width))),
        tuple(sorted(range(width), key=lambda index: (arrivals[index], index))),
        tuple(sorted(range(width), key=lambda index: (-arrivals[index], index))),
    ]
    seen: set[tuple[int, ...]] = set()
    permutations: list[tuple[int, ...]] = []
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            permutations.append(candidate)
    seed = 0
    while len(permutations) < count:
        values = list(range(width))
        random.Random(seed).shuffle(values)
        candidate = tuple(values)
        seed += 1
        if candidate in seen:
            continue
        seen.add(candidate)
        permutations.append(candidate)
    return permutations[:count]


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def resolve_artifact(raw: str, artifact_root: Path) -> Path:
    direct = Path(raw)
    if direct.is_file():
        resolved = direct.resolve()
        if artifact_root != resolved and artifact_root not in resolved.parents:
            raise ValueError(f"artifact escapes root: {raw!r}")
        return resolved
    parts = [part for part in raw.replace("\\", "/").split("/") if part]
    start = next(
        (index for index, part in enumerate(parts) if PERM_RE.fullmatch(part)),
        None,
    )
    if start is None:
        raise ValueError(f"cannot relocate permutation artifact path {raw!r}")
    suffix = parts[start:]
    if any(part in {".", ".."} for part in suffix):
        raise ValueError(f"unsafe artifact path {raw!r}")
    result = artifact_root.joinpath(*suffix).resolve()
    if artifact_root not in result.parents:
        raise ValueError(f"artifact escapes root: {raw!r}")
    return result


def require_record_file(
    record: dict[str, Any],
    path_field: str,
    sha_field: str,
    artifact_root: Path,
    verified: dict[str, str],
) -> Path:
    path = resolve_artifact(str(record[path_field]), artifact_root)
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = file_sha256(path)
    if actual != record[sha_field]:
        raise ValueError(f"{path}: SHA differs from {sha_field}")
    verified[phase_audit.portable(path)] = actual
    return path


def read_care_rows(
    path: Path,
    metadata: dict[str, Any],
    expected_rows: int,
) -> dict[str, str]:
    expected_inputs = [f"n{item['id']}" for item in metadata["boundary"]]
    expected_outputs = [f"out{index}" for index in range(len(metadata["outputs"]))]
    input_names: list[str] | None = None
    output_names: list[str] | None = None
    ninputs: int | None = None
    noutputs: int | None = None
    pla_type: str | None = None
    ended = False
    rows: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        tokens = line.split()
        directive = tokens[0]
        if ended:
            raise ValueError(f"PLA content after .e at line {line_number}")
        if directive == ".i":
            if ninputs is not None or len(tokens) != 2:
                raise ValueError(f"bad or duplicate .i at line {line_number}")
            ninputs = int(tokens[1])
        elif directive == ".o":
            if noutputs is not None or len(tokens) != 2:
                raise ValueError(f"bad or duplicate .o at line {line_number}")
            noutputs = int(tokens[1])
        elif directive == ".type":
            if pla_type is not None or len(tokens) != 2:
                raise ValueError(f"bad or duplicate .type at line {line_number}")
            pla_type = tokens[1]
        elif directive == ".ilb":
            if input_names is not None:
                raise ValueError(f"duplicate .ilb at line {line_number}")
            input_names = tokens[1:]
        elif directive == ".ob":
            if output_names is not None:
                raise ValueError(f"duplicate .ob at line {line_number}")
            output_names = tokens[1:]
        elif directive == ".p":
            if len(tokens) != 2:
                raise ValueError(f"bad .p at line {line_number}")
        elif directive == ".e":
            if len(tokens) != 1:
                raise ValueError(f"bad .e at line {line_number}")
            ended = True
        elif directive.startswith("."):
            raise ValueError(f"unsupported PLA directive {directive!r}")
        else:
            if len(tokens) != 2 or ninputs is None or noutputs is None:
                raise ValueError(f"bad PLA row at line {line_number}")
            inputs, outputs = tokens
            if len(inputs) != ninputs or set(inputs) - {"0", "1"}:
                raise ValueError(f"care input is not a full point at line {line_number}")
            if len(outputs) != noutputs or set(outputs) - {"0", "1"}:
                raise ValueError(f"care output is not fully specified at line {line_number}")
            previous = rows.setdefault(inputs, outputs)
            if previous != outputs:
                raise ValueError(f"care point {inputs!r} is not functional")
    if not ended or pla_type != "fr":
        raise ValueError("care relation must terminate with .e and use .type fr")
    if input_names != expected_inputs or ninputs != len(expected_inputs):
        raise ValueError("care relation PI labels/order differ from metadata")
    if output_names != expected_outputs or noutputs != len(expected_outputs):
        raise ValueError("care relation PO labels/order differ from metadata")
    if len(rows) != expected_rows:
        raise ValueError(f"care relation has {len(rows)} rows, expected {expected_rows}")
    return rows


def cube_matches(pattern: str, point: str) -> bool:
    return all(required == "-" or required == actual for required, actual in zip(pattern, point))


def validate_local_input_function(
    path: Path,
    mask: int,
    input_names: list[str],
    output_names: list[str],
    care_rows: dict[str, str],
) -> dict[str, Any]:
    structural = phase_audit.validate_phase_input(
        path, mask, input_names, output_names
    )
    parsed = phase_audit.parse_names_blif(path)
    blocks = parsed["blocks"]
    functions: list[list[str]] = []
    position = 0
    for output_index in range(len(output_names)):
        function = blocks[position]
        position += 1
        functions.append([cube.split()[0] for cube in function["cubes"]])
        if (mask >> output_index) & 1:
            position += 1
    mismatches = 0
    for point, expected in care_rows.items():
        actual_bits: list[str] = []
        for output_index, cubes in enumerate(functions):
            phase_value = int(any(cube_matches(cube, point) for cube in cubes))
            actual = phase_value ^ ((mask >> output_index) & 1)
            actual_bits.append(str(actual))
        if "".join(actual_bits) != expected:
            mismatches += 1
            break
    if mismatches:
        raise ValueError(f"{path}: phase restoration fails the care relation")
    return {
        **structural,
        "care_rows_checked": len(care_rows),
        "care_mismatches": 0,
        "phase_function_and_restoration_verified": True,
    }


def validate_metric_record(record: dict[str, Any], fixed_gate: int, output_count: int) -> None:
    arrivals = list(record["output_arrivals"])
    if len(arrivals) != output_count:
        raise ValueError("metric record has wrong output-arrival width")
    if int(record["total_gate"]) != fixed_gate + int(record["residual_gate"]):
        raise ValueError("total_gate differs from fixed_gate + residual_gate")
    if int(record["delay"]) != max(int(value) for value in arrivals):
        raise ValueError("delay differs from output arrivals")
    if int(record["energy"]) != int(record["total_gate"]) * int(record["delay"]):
        raise ValueError("energy differs from total_gate * delay")


def validate_source_summary(
    summary: dict[str, Any],
    root: Path,
    metadata: dict[str, Any],
    input_names: list[str],
    output_names: list[str],
    care_rows: dict[str, str],
    permutation_start: int,
    expected_permutations: int,
    masks: list[int],
    verified: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    permutation_stop = permutation_start + expected_permutations
    expected_count = expected_permutations * len(masks)
    if summary.get("schema") != "byte-adder-reachable-input-permutation-search-v1":
        raise ValueError("unexpected permutation-search schema")
    if (
        summary.get("permutation_count") != expected_permutations
        or summary.get("masks") != masks
        or summary.get("expected_tasks") != expected_count
        or summary.get("completed_tasks") != expected_count
        or summary.get("error_count") != 0
        or summary.get("errors") != []
    ):
        raise ValueError("permutation-search summary is incomplete or contains errors")
    range_fields_present = (
        "permutation_start" in summary or "permutation_stop" in summary
    )
    if range_fields_present and (
        summary.get("permutation_start") != permutation_start
        or summary.get("permutation_stop") != permutation_stop
    ):
        raise ValueError("permutation-search summary range differs from contract")
    if permutation_start and not range_fields_present:
        raise ValueError("sharded permutation-search summary lacks explicit range fields")
    arrivals = [int(item["arrival"]) for item in metadata["boundary"]]
    expected_values = make_permutations(permutation_stop, arrivals)
    results = list(summary.get("results", ()))
    by_key: dict[tuple[int, int], dict[str, Any]] = {}
    for item in results:
        key = (int(item["permutation_index"]), int(item["mask"]))
        if key in by_key:
            raise ValueError(f"duplicate permutation-search record {key!r}")
        by_key[key] = item
        index, mask = key
        if not permutation_start <= index < permutation_stop or mask not in masks:
            raise ValueError(f"out-of-contract permutation-search key {key!r}")
        expected_permutation = expected_values[index]
        if list(expected_permutation) != item["permutation"]:
            raise ValueError(f"permutation {index} differs from deterministic generator")
        if item["permuted_input_names"] != [input_names[value] for value in expected_permutation]:
            raise ValueError(f"permutation {index} input labels differ")
        if item.get("mask_hex") != f"0x{mask:03x}" or item.get("care_mismatches") != 0:
            raise ValueError(f"permutation-search record {key!r} failed care/mask contract")
        validate_metric_record(item, int(metadata["fixed_gate"]), len(output_names))
    expected_keys = {
        (index, mask)
        for index in range(permutation_start, permutation_stop)
        for mask in masks
    }
    if set(by_key) != expected_keys or len(results) != expected_count:
        raise ValueError("permutation-search summary lacks one or more exact tasks")

    local: list[dict[str, Any]] = []
    for candidate_dir in sorted(root.glob("perm_*_phase_*")):
        match = PERM_RE.fullmatch(candidate_dir.name)
        if not candidate_dir.is_dir() or match is None:
            continue
        key = (int(match.group(1)), int(match.group(2), 16))
        if key not in by_key:
            raise ValueError(f"local candidate {candidate_dir.name} is absent from summary")
        item = by_key[key]
        result_path = candidate_dir / "result.json"
        if not result_path.is_file():
            raise FileNotFoundError(result_path)
        local_result = json.loads(result_path.read_text(encoding="utf-8"))
        if local_result != item:
            raise ValueError(f"{result_path}: content differs from search summary")
        verified[phase_audit.portable(result_path)] = file_sha256(result_path)
        input_path = require_record_file(item, "input_blif", "input_blif_sha256", root, verified)
        mapped_path = require_record_file(item, "mapped_blif", "mapped_blif_sha256", root, verified)
        require_record_file(item, "abc_log", "abc_log_sha256", root, verified)
        function_review = validate_local_input_function(
            input_path, key[1], input_names, output_names, care_rows
        )
        local.append(
            {
                "permutation_index": key[0],
                "mask": key[1],
                "record": item,
                "mapped_path": mapped_path,
                "input_review": function_review,
            }
        )
    return results, local


def validate_timing_summary(
    summary: dict[str, Any],
    root: Path,
    metadata: dict[str, Any],
    permutation_start: int,
    expected_permutations: int,
    masks: list[int],
    required: int,
    verified: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    permutation_stop = permutation_start + expected_permutations
    expected_candidates = expected_permutations * len(masks)
    expected_results = expected_candidates * len(phase_audit.EXPECTED_RECIPES)
    if summary.get("schema") != "byte-adder-reachable-input-permutation-timing-map-v1":
        raise ValueError("unexpected permutation-timing schema")
    if (
        summary.get("permutations") != expected_permutations
        or summary.get("masks") != masks
        or summary.get("required") != required
        or summary.get("expected_candidates") != expected_candidates
        or summary.get("completed_candidates") != expected_candidates
        or summary.get("worker_error_count") != 0
        or summary.get("worker_errors") != []
        or summary.get("recipe_error_count") != 0
        or summary.get("recipe_errors") != []
        or set(summary.get("recipes", {})) != phase_audit.EXPECTED_RECIPES
    ):
        raise ValueError("permutation-timing summary is incomplete or mistimed")
    range_fields_present = (
        "permutation_start" in summary or "permutation_stop" in summary
    )
    if range_fields_present and (
        summary.get("permutation_start") != permutation_start
        or summary.get("permutation_stop") != permutation_stop
    ):
        raise ValueError("permutation-timing summary range differs from contract")
    if permutation_start and not range_fields_present:
        raise ValueError("sharded permutation-timing summary lacks explicit range fields")
    results = list(summary.get("results", ()))
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        validate_metric_record(item, int(metadata["fixed_gate"]), len(metadata["outputs"]))
        grouped[(int(item["permutation_index"]), int(item["mask"]))].append(item)
    expected_keys = {
        (index, mask)
        for index in range(permutation_start, permutation_stop)
        for mask in masks
    }
    if set(grouped) != expected_keys or len(results) != expected_results:
        raise ValueError("permutation-timing summary lacks exact candidate coverage")
    for key, items in grouped.items():
        recipes = [str(item["recipe"]) for item in items]
        if len(items) != len(phase_audit.EXPECTED_RECIPES) or set(recipes) != phase_audit.EXPECTED_RECIPES:
            raise ValueError(f"timing candidate {key!r} lacks one recipe")

    local: list[dict[str, Any]] = []
    for candidate_dir in sorted(root.glob("perm_*_phase_*")):
        match = PERM_RE.fullmatch(candidate_dir.name)
        if not candidate_dir.is_dir() or match is None:
            continue
        key = (int(match.group(1)), int(match.group(2), 16))
        items = grouped[key]
        result_path = candidate_dir / f"timing_d{required}_result.json"
        if not result_path.is_file():
            raise FileNotFoundError(result_path)
        candidate_result = json.loads(result_path.read_text(encoding="utf-8"))
        if (
            int(candidate_result.get("permutation_index", -1)) != key[0]
            or int(candidate_result.get("mask", -1)) != key[1]
            or candidate_result.get("required") != required
            or candidate_result.get("errors") != []
        ):
            raise ValueError(f"{result_path}: timing metadata/errors differ")
        flattened = {
            str(item["recipe"]): {
                "permutation_index": key[0],
                "mask": key[1],
                "mask_hex": f"0x{key[1]:03x}",
                **item,
            }
            for item in candidate_result["results"]
        }
        summary_items = {str(item["recipe"]): item for item in items}
        if flattened != summary_items:
            raise ValueError(f"{result_path}: records differ from timing summary")
        verified[phase_audit.portable(result_path)] = file_sha256(result_path)
        input_path = candidate_dir / "input.blif"
        timed_path = require_record_file(
            candidate_result, "timed_blif", "timed_blif_sha256", root, verified
        )
        timing_review = phase_audit.validate_timed_blif(
            input_path, timed_path, metadata, required
        )
        for item in items:
            mapped_path = require_record_file(
                item, "mapped_blif", "mapped_blif_sha256", root, verified
            )
            require_record_file(item, "abc_log", "abc_log_sha256", root, verified)
            local.append(
                {
                    "permutation_index": key[0],
                    "mask": key[1],
                    "record": item,
                    "mapped_path": mapped_path,
                    "timing_review": timing_review,
                }
            )
    unmet = sum(bool(item.get("abc_reported_unmet")) for item in results)
    return results, local, {
        "abc_reported_unmet_count": unmet,
        "abc_reported_met_count": len(results) - unmet,
    }


def validate_summary_sources(
    summary: dict[str, Any],
    pla: Path,
    metadata: Path,
    library: Path,
) -> None:
    expected = {
        "input_sha256": file_sha256(pla),
        "metadata_sha256": file_sha256(metadata),
        "library_sha256": file_sha256(library),
    }
    for key, value in expected.items():
        if key in summary and summary[key] != value:
            raise ValueError(f"summary {key} differs from current input")
    if summary.get("metadata_sha256") != expected["metadata_sha256"]:
        raise ValueError("summary metadata SHA differs from current metadata")
    if summary.get("library_sha256") != expected["library_sha256"]:
        raise ValueError("summary library SHA differs from current library")


def run(args: argparse.Namespace) -> dict[str, Any]:
    dag = args.dag.resolve()
    metadata_path = args.metadata.resolve()
    pla = args.pla.resolve()
    library = args.library.resolve()
    root = args.candidate_dir.resolve()
    search_summary_path = args.search_summary.resolve()
    timing_summary_path = args.timing_summary.resolve()
    output = args.output.resolve()
    normalized_root = args.normalized_dir.resolve()
    for path in (
        dag,
        metadata_path,
        pla,
        library,
        search_summary_path,
        timing_summary_path,
        Path(phase_audit.importer.__file__).resolve(),
        Path(phase_audit.__file__).resolve(),
        HERE / "search_reachable_input_permutations.py",
    ):
        if not path.is_file():
            raise FileNotFoundError(path)
    if not root.is_dir():
        raise NotADirectoryError(root)
    if args.energy_threshold <= 0:
        raise ValueError("energy threshold must be positive")
    if args.expected_permutations <= 0:
        raise ValueError("expected permutations must be positive")
    if args.permutation_start < 0:
        raise ValueError("permutation start must be non-negative")
    masks = sorted({int(value.strip(), 0) for value in args.masks.split(",") if value.strip()})
    if not masks:
        raise ValueError("at least one phase mask is required")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    care_contract = phase_audit.parse_care_relation(
        pla, metadata, args.expected_care_rows
    )
    care_rows = read_care_rows(pla, metadata, args.expected_care_rows)
    input_names = [f"n{item['id']}" for item in metadata["boundary"]]
    output_names = [f"out{index}" for index in range(len(metadata["outputs"]))]
    search_summary = json.loads(search_summary_path.read_text(encoding="utf-8"))
    timing_summary = json.loads(timing_summary_path.read_text(encoding="utf-8"))
    validate_summary_sources(search_summary, pla, metadata_path, library)
    validate_summary_sources(timing_summary, pla, metadata_path, library)

    verified = {
        phase_audit.portable(path): file_sha256(path)
        for path in (
            dag,
            metadata_path,
            pla,
            library,
            search_summary_path,
            timing_summary_path,
            Path(phase_audit.importer.__file__).resolve(),
            Path(phase_audit.__file__).resolve(),
            HERE / "search_reachable_input_permutations.py",
            HERE / "map_reachable_permutation_timing_batch.py",
        )
    }
    search_results, local_search = validate_source_summary(
        search_summary,
        root,
        metadata,
        input_names,
        output_names,
        care_rows,
        args.permutation_start,
        args.expected_permutations,
        masks,
        verified,
    )
    timing_results, local_timing, unmet = validate_timing_summary(
        timing_summary,
        root,
        metadata,
        args.permutation_start,
        args.expected_permutations,
        masks,
        args.required,
        verified,
    )

    importer_inputs: list[tuple[int, dict[str, Any], Path, Path, dict[str, Any] | None]] = []
    for item in local_search:
        importer_inputs.append(
            (
                int(item["permutation_index"]),
                item["record"],
                item["mapped_path"],
                item["mapped_path"],
                None,
            )
        )
    for item in local_timing:
        source = item["mapped_path"]
        normalized = normalized_root / source.parent.name / source.name
        normalization = phase_audit.normalize_timed_mapped_blif(
            source, normalized, metadata, args.required
        )
        verified[phase_audit.portable(source)] = file_sha256(source)
        verified[phase_audit.portable(normalized)] = file_sha256(normalized)
        importer_inputs.append(
            (
                int(item["permutation_index"]),
                item["record"],
                source,
                normalized,
                normalization,
            )
        )
    import_results: list[dict[str, Any]] = []
    for permutation_index, record, source, import_path, normalization in importer_inputs:
        result = phase_audit.importer_result(
            record, source, import_path, dag, metadata_path, normalization
        )
        result["permutation_index"] = permutation_index
        import_results.append(result)
    accepted = [item for item in import_results if item["status"] == "accepted"]
    rejected = [item for item in import_results if item["status"] != "accepted"]
    hits = [
        item
        for item in accepted
        if int(item["actual_metrics"]["energy"]) < args.energy_threshold
    ]
    summary_hits = [
        item
        for item in [*search_results, *timing_results]
        if int(item["energy"]) < args.energy_threshold
    ]
    best_summary = min(
        [*search_results, *timing_results],
        key=lambda item: (
            int(item["energy"]),
            int(item["delay"]),
            int(item["total_gate"]),
            int(item["permutation_index"]),
            int(item["mask"]),
            str(item.get("recipe", "")),
        ),
    )
    artifact_items = sorted(verified.items())
    payload = {
        "schema": "byte-adder-reachable-input-permutation-independent-audit-v1",
        "status": "accepted" if not rejected else "contains-rejections",
        "care_relation": {
            key: value
            for key, value in care_contract.items()
            if key not in {"input_names", "output_names"}
        },
        "contract": {
            "permutation_start": args.permutation_start,
            "permutation_stop": args.permutation_start + args.expected_permutations,
            "expected_permutations": args.expected_permutations,
            "masks": masks,
            "expected_search_tasks": args.expected_permutations * len(masks),
            "expected_timing_results": (
                args.expected_permutations
                * len(masks)
                * len(phase_audit.EXPECTED_RECIPES)
            ),
            "required": args.required,
            "boundary_arrivals": {
                f"n{item['id']}": int(item["arrival"])
                for item in metadata["boundary"]
            },
            "old_parser_command": "read_blif -n",
        },
        "summaries": {
            "search": {
                "path": phase_audit.portable(search_summary_path),
                "sha256": file_sha256(search_summary_path),
                "record_count": len(search_results),
                "complete": True,
                "local_candidate_count": len(local_search),
                "local_function_reviews": [item["input_review"] for item in local_search],
            },
            "timing": {
                "path": phase_audit.portable(timing_summary_path),
                "sha256": file_sha256(timing_summary_path),
                "record_count": len(timing_results),
                "complete": True,
                "local_recipe_count": len(local_timing),
                **unmet,
            },
            "best_metrics": {
                "gate": int(best_summary["total_gate"]),
                "delay": int(best_summary["delay"]),
                "energy": int(best_summary["energy"]),
            },
            "energy_strictly_below": args.energy_threshold,
            "hit_count": len(summary_hits),
        },
        "artifact_set": {
            "verified_file_count": len(artifact_items),
            "path_sha256_set_sha256": phase_audit.canonical_sha256(artifact_items),
        },
        "selection": {
            "selected_count": len(import_results),
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "energy_strictly_below": args.energy_threshold,
            "hit_count": len(hits),
            "hits": [item["import_blif"] for item in hits],
        },
        "results": import_results,
        "safety": {
            "espresso_enumeration_run": False,
            "abc_mapping_run": False,
            "timing_annotations_validated_before_normalization": True,
            "formal_save_read": False,
            "formal_save_written": False,
            "repository_candidate_written": False,
            "game_started": False,
        },
    }
    output_sha = phase_audit.atomic_write(output, payload)
    print(
        json.dumps(
            {
                "output": str(output),
                "output_sha256": output_sha,
                "status": payload["status"],
                "summaries": payload["summaries"],
                "selection": payload["selection"],
                "safety": payload["safety"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return payload


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    result.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    result.add_argument("--pla", type=Path, default=DEFAULT_PLA)
    result.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    result.add_argument("--candidate-dir", type=Path, required=True)
    result.add_argument("--search-summary", type=Path, required=True)
    result.add_argument("--timing-summary", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--normalized-dir", type=Path, required=True)
    result.add_argument("--expected-care-rows", type=int, default=23328)
    result.add_argument("--permutation-start", type=int, default=0)
    result.add_argument("--expected-permutations", type=int, default=64)
    result.add_argument("--masks", default="0x000,0x086")
    result.add_argument("--required", type=int, default=6)
    result.add_argument("--energy-threshold", type=int, default=560)
    return result


def main() -> int:
    payload = run(parser().parse_args())
    return 0 if payload["status"] == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
