"""Independently audit downloaded reachable-output-phase artifacts.

The expensive Espresso/ABC enumeration is deliberately out of scope here.
This tool validates an already downloaded phase tree, verifies its phase and
timing contracts, then runs the authoritative mapped-residual importer twice
on only the best discovery-ranked mapped BLIFs.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Iterable

import graft_abc_mapped_residual as importer


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_DAG = HERE / "byte-adder-hybrid-phasefold-g80-d7.json"
DEFAULT_METADATA = HERE / "abc_residual_current80" / "metadata.json"
DEFAULT_PLA = (
    HERE / "abc_residual_current80" / "care_pla" / "reachable_relation_fr.pla"
)
PHASE_RE = re.compile(r"^phase_([0-9a-fA-F]{3})$")
EXPECTED_RECIPES = {"plain_d6", "dch_d6", "dc2_d6", "resub8_d6"}
TIMING_DIRECTIVES = {
    ".and_gate_delay",
    ".default_input_arrival",
    ".default_output_required",
    ".input_arrival",
    ".output_required",
}


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def portable(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def encoded(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    raw = encoded(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)
    return sha256(raw).hexdigest()


def parse_care_relation(
    path: Path,
    metadata: dict[str, Any],
    expected_rows: int,
) -> dict[str, Any]:
    ninputs: int | None = None
    noutputs: int | None = None
    pla_type: str | None = None
    input_names: list[str] | None = None
    output_names: list[str] | None = None
    ended = False
    relation: dict[str, str] = {}
    duplicate_rows = 0
    for line_number, raw in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ended:
            raise ValueError(f"PLA content after .e at line {line_number}")
        tokens = line.split()
        directive = tokens[0]
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
            raise ValueError(f"unsupported PLA directive {directive!r} at line {line_number}")
        else:
            if len(tokens) != 2 or ninputs is None or noutputs is None:
                raise ValueError(f"bad PLA row at line {line_number}")
            inputs, outputs = tokens
            if len(inputs) != ninputs or set(inputs) - {"0", "1"}:
                raise ValueError(f"care input is not a full {ninputs}-bit point at line {line_number}")
            if len(outputs) != noutputs or set(outputs) - {"0", "1"}:
                raise ValueError(f"care output is not fully specified at line {line_number}")
            if inputs in relation:
                if relation[inputs] != outputs:
                    raise ValueError(f"care point {inputs!r} has conflicting outputs")
                duplicate_rows += 1
            else:
                relation[inputs] = outputs

    expected_inputs = [f"n{item['id']}" for item in metadata["boundary"]]
    expected_outputs = [f"out{index}" for index in range(len(metadata["outputs"]))]
    if not ended or pla_type != "fr":
        raise ValueError("care relation must terminate with .e and use .type fr")
    if ninputs != len(expected_inputs) or input_names != expected_inputs:
        raise ValueError("care relation input labels differ from metadata boundary order")
    if noutputs != len(expected_outputs) or output_names != expected_outputs:
        raise ValueError("care relation output labels differ from metadata output order")
    if len(relation) != expected_rows:
        raise ValueError(f"care relation has {len(relation)} unique rows, expected {expected_rows}")
    return {
        "path": portable(path),
        "sha256": file_sha256(path),
        "rows": len(relation),
        "input_count": ninputs,
        "output_count": noutputs,
        "duplicate_identical_rows": duplicate_rows,
        "functional_conflicts": 0,
        "input_labels_exact": True,
        "output_labels_exact": True,
        "input_names": expected_inputs,
        "output_names": expected_outputs,
    }


def nonempty_blif_lines(path: Path) -> list[str]:
    return [
        line
        for raw in path.read_text(encoding="ascii").splitlines()
        if (line := raw.split("#", 1)[0].strip())
    ]


def parse_names_blif(path: Path) -> dict[str, Any]:
    lines = nonempty_blif_lines(path)
    model: str | None = None
    inputs: list[str] | None = None
    outputs: list[str] | None = None
    blocks: list[dict[str, Any]] = []
    ended = False
    index = 0
    while index < len(lines):
        line = lines[index]
        tokens = line.split()
        directive = tokens[0]
        if ended:
            raise ValueError(f"{path}: content after .end")
        if directive == ".model":
            if model is not None or len(tokens) != 2:
                raise ValueError(f"{path}: bad or duplicate .model")
            model = tokens[1]
        elif directive == ".inputs":
            if inputs is not None or len(tokens) < 2:
                raise ValueError(f"{path}: bad or duplicate .inputs")
            inputs = tokens[1:]
        elif directive == ".outputs":
            if outputs is not None or len(tokens) < 2:
                raise ValueError(f"{path}: bad or duplicate .outputs")
            outputs = tokens[1:]
        elif directive == ".names":
            if len(tokens) < 2:
                raise ValueError(f"{path}: malformed .names")
            cubes: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].startswith("."):
                cubes.append(lines[index])
                index += 1
            blocks.append({"signals": tokens[1:], "cubes": cubes})
            continue
        elif directive == ".end":
            if len(tokens) != 1:
                raise ValueError(f"{path}: malformed .end")
            ended = True
        else:
            raise ValueError(f"{path}: unsupported directive {directive!r}")
        index += 1
    if model is None or inputs is None or outputs is None or not ended:
        raise ValueError(f"{path}: incomplete BLIF header or terminator")
    return {"model": model, "inputs": inputs, "outputs": outputs, "blocks": blocks}


def validate_phase_input(
    path: Path,
    mask: int,
    input_names: list[str],
    output_names: list[str],
) -> dict[str, Any]:
    parsed = parse_names_blif(path)
    if parsed["model"] != f"reachable_phase_{mask:03x}":
        raise ValueError(f"{path}: model does not match phase mask")
    if parsed["inputs"] != input_names or parsed["outputs"] != output_names:
        raise ValueError(f"{path}: PI/PO order differs from care relation")
    blocks = parsed["blocks"]
    position = 0
    function_cube_count = 0
    for output_index, output_name in enumerate(output_names):
        inverted = bool((mask >> output_index) & 1)
        phase_name = f"phase_{output_name}" if inverted else output_name
        if position >= len(blocks):
            raise ValueError(f"{path}: output {output_name} has no function block")
        function = blocks[position]
        position += 1
        if function["signals"] != [*input_names, phase_name]:
            raise ValueError(f"{path}: output {output_name} function header differs")
        for cube in function["cubes"]:
            tokens = cube.split()
            if (
                len(tokens) != 2
                or len(tokens[0]) != len(input_names)
                or set(tokens[0]) - {"0", "1", "-"}
                or tokens[1] != "1"
            ):
                raise ValueError(f"{path}: malformed function cube {cube!r}")
        function_cube_count += len(function["cubes"])
        if inverted:
            if position >= len(blocks):
                raise ValueError(f"{path}: output {output_name} lacks polarity restoration")
            inverter = blocks[position]
            position += 1
            if inverter["signals"] != [phase_name, output_name] or inverter["cubes"] != [
                "0 1"
            ]:
                raise ValueError(f"{path}: output {output_name} has wrong polarity restoration")
    if position != len(blocks):
        raise ValueError(f"{path}: unexpected extra .names blocks")
    return {
        "path": portable(path),
        "sha256": file_sha256(path),
        "mask": mask,
        "inverted_output_count": mask.bit_count(),
        "function_cube_count": function_cube_count,
        "polarity_restoration_verified": True,
    }


def expected_timing_lines(metadata: dict[str, Any], required: int) -> list[str]:
    result = [
        ".default_input_arrival 0 0",
        f".default_output_required {required} {required}",
    ]
    result.extend(
        f".input_arrival n{item['id']} {item['arrival']} {item['arrival']}"
        for item in metadata["boundary"]
    )
    result.extend(
        f".output_required out{index} {required} {required}"
        for index in range(len(metadata["outputs"]))
    )
    return result


def validate_timed_blif(
    input_path: Path,
    timed_path: Path,
    metadata: dict[str, Any],
    required: int,
) -> dict[str, Any]:
    original = nonempty_blif_lines(input_path)
    timed = nonempty_blif_lines(timed_path)
    if not original or original[-1] != ".end":
        raise ValueError(f"{input_path}: missing terminal .end")
    expected = [*original[:-1], *expected_timing_lines(metadata, required), ".end"]
    if timed != expected:
        raise ValueError(f"{timed_path}: timing augmentation differs from metadata contract")
    return {
        "path": portable(timed_path),
        "sha256": file_sha256(timed_path),
        "required": required,
        "boundary_arrival_count": len(metadata["boundary"]),
        "output_required_count": len(metadata["outputs"]),
        "timing_contract_exact": True,
    }


def expected_mapped_timing_lines(metadata: dict[str, Any], required: int) -> list[str]:
    result = [
        ".and_gate_delay 1",
        ".default_input_arrival 0 0",
        f".default_output_required {required} {required}",
    ]
    result.extend(
        f".input_arrival n{item['id']} {item['arrival']} {item['arrival']}"
        for item in metadata["boundary"]
        if int(item["arrival"]) != 0
    )
    return result


def normalize_timed_mapped_blif(
    source: Path,
    output: Path,
    metadata: dict[str, Any],
    required: int,
) -> dict[str, Any]:
    raw_lines = source.read_text(encoding="ascii").splitlines()
    timing: list[str] = []
    retained: list[str] = []
    allowed_core = {".model", ".inputs", ".outputs", ".gate", ".end"}
    for line in raw_lines:
        stripped = line.strip()
        directive = stripped.split(maxsplit=1)[0] if stripped.startswith(".") else None
        if directive in TIMING_DIRECTIVES:
            timing.append(stripped)
            continue
        if directive is not None and directive not in allowed_core:
            raise ValueError(f"{source}: unsupported non-timing directive {directive!r}")
        retained.append(line)
    expected = expected_mapped_timing_lines(metadata, required)
    if timing != expected:
        raise ValueError(f"{source}: serialized mapped timing differs from metadata/required")
    encoded_blif = ("\n".join(retained) + "\n").encode("ascii")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_bytes(encoded_blif)
    temporary.replace(output)
    return {
        "source": portable(source),
        "source_sha256": file_sha256(source),
        "normalized": portable(output),
        "normalized_sha256": sha256(encoded_blif).hexdigest(),
        "removed_timing_directives": timing,
        "timing_directives_exact": True,
    }


def resolve_phase_path(raw: str, phase_root: Path) -> Path:
    direct = Path(raw)
    if direct.is_file():
        return direct.resolve()
    normalized = raw.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part]
    phase_index = next(
        (index for index, part in enumerate(parts) if PHASE_RE.fullmatch(part)),
        None,
    )
    if phase_index is None:
        raise ValueError(f"cannot relocate phase artifact path {raw!r}")
    suffix = parts[phase_index:]
    if any(part in {".", ".."} for part in suffix):
        raise ValueError(f"unsafe phase artifact path {raw!r}")
    result = phase_root.joinpath(*suffix).resolve()
    if phase_root not in result.parents:
        raise ValueError(f"phase artifact escapes root: {raw!r}")
    return result


def require_record_file(
    record: dict[str, Any],
    path_field: str,
    sha_field: str,
    phase_root: Path,
    verified: dict[str, str],
) -> Path:
    path = resolve_phase_path(str(record[path_field]), phase_root)
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = file_sha256(path)
    if actual != record[sha_field]:
        raise ValueError(f"{path}: SHA differs from {sha_field}")
    verified[portable(path)] = actual
    return path


def validate_search_summary(
    summary: dict[str, Any],
    phase_root: Path,
    expected_phases: int,
    input_names: list[str],
    output_names: list[str],
    verified: dict[str, str],
    require_local_all: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if (
        summary.get("expected_masks") != expected_phases
        or summary.get("completed_masks") != expected_phases
        or summary.get("error_count") != 0
    ):
        raise ValueError("phase-search summary is incomplete or contains errors")
    results = list(summary.get("results", ()))
    masks = [int(item["mask"]) for item in results]
    if len(results) != expected_phases or sorted(masks) != list(range(expected_phases)):
        raise ValueError("phase-search summary does not contain every mask exactly once")
    local_masks: list[int] = []
    for item in results:
        mask = int(item["mask"])
        phase_dir = phase_root / f"phase_{mask:03x}"
        if not phase_dir.is_dir():
            if require_local_all:
                raise FileNotFoundError(phase_dir)
            continue
        input_path = require_record_file(
            item, "input_blif", "input_blif_sha256", phase_root, verified
        )
        validate_phase_input(input_path, mask, input_names, output_names)
        require_record_file(
            item, "mapped_blif", "mapped_blif_sha256", phase_root, verified
        )
        local_masks.append(mask)
    return results, {
        "summary_mask_count": len(results),
        "local_phase_count": len(local_masks),
        "local_masks": local_masks,
        "local_polarity_artifacts_verified": bool(local_masks),
    }


def validate_timing_summary(
    summary: dict[str, Any],
    phase_root: Path,
    expected_phases: int,
    required: int,
    metadata: dict[str, Any],
    verified: dict[str, str],
    require_local_all: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if (
        summary.get("required") != required
        or summary.get("expected_phases") != expected_phases
        or summary.get("completed_phases") != expected_phases
        or summary.get("worker_error_count") != 0
    ):
        raise ValueError("timing-map summary is incomplete, mistimed, or contains worker errors")
    results = list(summary.get("results", ()))
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        grouped[int(item["mask"])].append(item)
    if sorted(grouped) != list(range(expected_phases)):
        raise ValueError("timing-map summary lacks one or more phase masks")
    local_masks: list[int] = []
    unmet_count = sum(bool(item.get("abc_reported_unmet")) for item in results)
    for mask, items in grouped.items():
        recipes = [str(item["recipe"]) for item in items]
        if len(items) != len(EXPECTED_RECIPES) or set(recipes) != EXPECTED_RECIPES:
            raise ValueError(f"phase {mask:#x} does not contain every timing recipe exactly once")
        phase_dir = phase_root / f"phase_{mask:03x}"
        if not phase_dir.is_dir():
            if require_local_all:
                raise FileNotFoundError(phase_dir)
            continue
        phase_result_path = phase_dir / f"timing_d{required}_result.json"
        if not phase_result_path.is_file():
            raise FileNotFoundError(phase_result_path)
        phase_result = json.loads(phase_result_path.read_text(encoding="utf-8"))
        verified[portable(phase_result_path)] = file_sha256(phase_result_path)
        if (
            int(phase_result.get("mask", -1)) != mask
            or phase_result.get("required") != required
            or phase_result.get("errors") != []
        ):
            raise ValueError(f"phase {mask:#x} timing result contains errors or wrong metadata")
        input_path = phase_dir / "input.blif"
        timed_path = require_record_file(
            phase_result, "timed_blif", "timed_blif_sha256", phase_root, verified
        )
        validate_timed_blif(input_path, timed_path, metadata, required)
        for item in items:
            require_record_file(
                item, "mapped_blif", "mapped_blif_sha256", phase_root, verified
            )
        local_masks.append(mask)
    return results, {
        "summary_candidate_count": len(results),
        "expected_candidate_count": expected_phases * len(EXPECTED_RECIPES),
        "abc_reported_unmet_count": unmet_count,
        "abc_reported_met_count": len(results) - unmet_count,
        "local_phase_count": len(local_masks),
        "local_masks": local_masks,
        "local_timing_artifacts_verified": bool(local_masks),
    }


def importer_result(
    record: dict[str, Any],
    source_path: Path,
    import_path: Path,
    dag: Path,
    metadata: Path,
    normalization: dict[str, Any] | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "mask": int(record["mask"]),
        "mask_hex": f"0x{int(record['mask']):03x}",
        "recipe": record.get("recipe"),
        "source_mapped_blif": portable(source_path),
        "source_mapped_blif_sha256": file_sha256(source_path),
        "import_blif": portable(import_path),
        "import_blif_sha256": file_sha256(import_path),
        "normalization": normalization,
        "discovery_metrics": {
            "gate": int(record["total_gate"]),
            "delay": int(record["delay"]),
            "energy": int(record["energy"]),
        },
    }
    try:
        first = importer.build(dag, metadata, import_path)
        second = importer.build(dag, metadata, import_path)
        if encoded(first) != encoded(second):
            raise RuntimeError("same-process importer JSON changed")
        actual = {
            field: int(first["metrics"][field]) for field in ("gate", "delay", "energy")
        }
        checks = {
            "same_process_json_byte_identical": True,
            "discovery_metrics_match": actual == result["discovery_metrics"],
            "fixed_bus_slice_byte_identical": first["partition"][
                "fixed_slice_byte_identical"
            ],
            "full_131072_rows": first["semantic"]["truth_table_rows"] == 131072,
            "mismatch_union_zero": first["semantic"]["mismatch_union_count"] == 0,
            "bus_conflict_zero": first["semantic"]["conflict_assignment_count"] == 0,
            "primary_output_z_zero": not any(
                first["semantic"]["z_assignment_count_by_output"]
            ),
            "physical_net_partition_zero": first["physical"][
                "physical_net_partition_violation_count"
            ]
            == 0,
            "dead_node_zero": all(
                first["dead_node_audit"][field] == 0
                for field in (
                    "mapped_blif_dead_cell_count",
                    "dead_shell_node_count",
                    "dead_generated_node_count",
                )
            ),
        }
        if not all(checks.values()):
            raise RuntimeError(f"importer checks are not all true: {checks!r}")
        result.update(
            {
                "status": "accepted",
                "actual_metrics": first["metrics"],
                "mapped_residual": {
                    key: first["mapped_residual"][key]
                    for key in (
                        "cell_count",
                        "materialized_new_node_count",
                        "kind_counts",
                        "residual_gate",
                    )
                },
                "checks": checks,
                "factory_dag_sha256": first["factory_dag"]["sha256"],
                "output_vector_sha256": first["semantic"]["output_vector_sha256"],
            }
        )
    except Exception as exc:
        result.update(
            {
                "status": "rejected",
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
    return result


def choose_top(
    records: Iterable[dict[str, Any]],
    phase_root: Path,
    top: int,
) -> list[tuple[dict[str, Any], Path]]:
    ranked = sorted(
        records,
        key=lambda item: (
            int(item["energy"]),
            int(item["delay"]),
            int(item["total_gate"]),
            int(item["mask"]),
            str(item.get("recipe", "")),
        ),
    )
    selected: list[tuple[dict[str, Any], Path]] = []
    seen: set[Path] = set()
    for item in ranked:
        path = resolve_phase_path(str(item["mapped_blif"]), phase_root)
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        selected.append((item, path))
        if len(selected) >= top:
            break
    return selected


def run(args: argparse.Namespace) -> dict[str, Any]:
    dag = args.dag.resolve()
    metadata_path = args.metadata.resolve()
    pla = args.pla.resolve()
    phase_root = args.phase_dir.resolve()
    output = args.output.resolve()
    normalized_dir = args.normalized_dir.resolve()
    summaries = [path.resolve() for path in args.summary]
    for path in (dag, metadata_path, pla, Path(importer.__file__).resolve(), *summaries):
        if not path.is_file():
            raise FileNotFoundError(path)
    if not phase_root.is_dir():
        raise NotADirectoryError(phase_root)
    if output == HERE or HERE not in output.parents:
        raise RuntimeError(f"audit output must be below {HERE}: {output}")
    if normalized_dir == HERE or HERE not in normalized_dir.parents:
        raise RuntimeError(f"normalized BLIF directory must be below {HERE}: {normalized_dir}")
    if args.top <= 0 or args.energy_threshold <= 0:
        raise ValueError("top and energy threshold must be positive")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    care = parse_care_relation(pla, metadata, args.expected_care_rows)
    verified: dict[str, str] = {
        portable(dag): file_sha256(dag),
        portable(metadata_path): file_sha256(metadata_path),
        portable(pla): file_sha256(pla),
        portable(Path(importer.__file__)): file_sha256(Path(importer.__file__)),
    }
    all_records: list[dict[str, Any]] = []
    summary_reviews: list[dict[str, Any]] = []
    for path in summaries:
        summary = json.loads(path.read_text(encoding="utf-8"))
        verified[portable(path)] = file_sha256(path)
        schema = summary.get("schema")
        if schema == "byte-adder-reachable-output-phase-search-v1":
            records, local_review = validate_search_summary(
                summary,
                phase_root,
                args.expected_phases,
                care["input_names"],
                care["output_names"],
                verified,
                args.require_local_all,
            )
        elif schema == "byte-adder-reachable-output-phase-timing-map-v1":
            records, local_review = validate_timing_summary(
                summary,
                phase_root,
                args.expected_phases,
                args.required,
                metadata,
                verified,
                args.require_local_all,
            )
        else:
            raise ValueError(f"unsupported phase summary schema {schema!r}")
        all_records.extend(records)
        summary_reviews.append(
            {
                "path": portable(path),
                "sha256": file_sha256(path),
                "schema": schema,
                "record_count": len(records),
                "complete": True,
                **local_review,
            }
        )

    selected = choose_top(all_records, phase_root, args.top)
    if not selected:
        raise RuntimeError("none of the summary-ranked mapped BLIFs is available locally")
    prepared: list[tuple[dict[str, Any], Path, Path, dict[str, Any] | None]] = []
    for record, source_path in selected:
        normalization = None
        import_path = source_path
        if record.get("recipe") is not None:
            mask = int(record["mask"])
            import_path = normalized_dir / f"phase_{mask:03x}" / source_path.name
            normalization = normalize_timed_mapped_blif(
                source_path,
                import_path,
                metadata,
                args.required,
            )
        prepared.append((record, source_path, import_path, normalization))
    import_results = [
        importer_result(record, source, import_path, dag, metadata_path, normalization)
        for record, source, import_path, normalization in prepared
    ]
    accepted = [item for item in import_results if item["status"] == "accepted"]
    rejected = [item for item in import_results if item["status"] == "rejected"]
    hits = [
        item
        for item in accepted
        if int(item["actual_metrics"]["energy"]) < args.energy_threshold
    ]
    actual_ranked = sorted(
        accepted,
        key=lambda item: (
            int(item["actual_metrics"]["energy"]),
            int(item["actual_metrics"]["delay"]),
            int(item["actual_metrics"]["gate"]),
            int(item["mask"]),
            str(item.get("recipe", "")),
        ),
    )
    artifact_items = sorted(verified.items())
    payload = {
        "schema": "byte-adder-reachable-output-phase-independent-audit-v1",
        "status": "accepted" if not rejected else "contains-rejections",
        "care_relation": {
            key: value
            for key, value in care.items()
            if key not in {"input_names", "output_names"}
        },
        "contract": {
            "expected_phases": args.expected_phases,
            "required": args.required,
            "boundary_arrivals": {
                f"n{item['id']}": int(item["arrival"]) for item in metadata["boundary"]
            },
            "old_parser_command": "read_blif -n",
            "phase_polarity_restoration_checked": any(
                item.get("local_polarity_artifacts_verified") is True
                for item in summary_reviews
            ),
            "timing_augmentation_checked": any(
                item.get("local_timing_artifacts_verified") is True
                for item in summary_reviews
            ),
        },
        "summaries": summary_reviews,
        "artifact_set": {
            "verified_file_count": len(artifact_items),
            "path_sha256_set_sha256": canonical_sha256(artifact_items),
        },
        "selection": {
            "requested_top": args.top,
            "selected_count": len(import_results),
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "energy_strictly_below": args.energy_threshold,
            "hit_count": len(hits),
            "hits": [item["import_blif"] for item in hits],
            "best_actual": (
                {
                    "source_mapped_blif": actual_ranked[0]["source_mapped_blif"],
                    "import_blif": actual_ranked[0]["import_blif"],
                    "mask_hex": actual_ranked[0]["mask_hex"],
                    "recipe": actual_ranked[0].get("recipe"),
                    "metrics": actual_ranked[0]["actual_metrics"],
                }
                if actual_ranked
                else None
            ),
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
    output_sha = atomic_write(output, payload)
    print(
        json.dumps(
            {
                "output": str(output),
                "output_sha256": output_sha,
                "status": payload["status"],
                "summaries": summary_reviews,
                "artifact_set": payload["artifact_set"],
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
    result.add_argument("--phase-dir", type=Path, required=True)
    result.add_argument("--summary", type=Path, action="append", required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--normalized-dir", type=Path, required=True)
    result.add_argument("--expected-care-rows", type=int, default=23328)
    result.add_argument("--expected-phases", type=int, default=512)
    result.add_argument("--required", type=int, default=6)
    result.add_argument("--top", type=int, default=32)
    result.add_argument("--energy-threshold", type=int, default=560)
    result.add_argument("--require-local-all", action="store_true")
    return result


def main() -> int:
    payload = run(parser().parse_args())
    return 0 if payload["status"] == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
