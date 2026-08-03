"""Timing-aware remapping of reachable-domain input-permutation candidates."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess

from map_reachable_phase_timing_batch import RECIPES, add_timing, analyze_mapped


NAME_RE = re.compile(r"^perm_(\d{3})_phase_([0-9a-f]{3})$")


def map_candidate(task: tuple[object, ...]) -> dict[str, object]:
    candidate_dir, metadata, abc, library, required = task
    candidate_dir = Path(candidate_dir)
    match = NAME_RE.fullmatch(candidate_dir.name)
    if match is None:
        raise ValueError(f"invalid candidate directory name {candidate_dir.name!r}")
    permutation_index = int(match.group(1))
    mask = int(match.group(2), 16)
    input_path = candidate_dir / "input.blif"
    timed_path = candidate_dir / f"timed_d{required}.blif"
    add_timing(input_path, timed_path, metadata, int(required))
    results: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    for recipe_name, recipe in RECIPES.items():
        mapped_path = candidate_dir / f"mapped_{recipe_name}.blif"
        log_path = candidate_dir / f"abc_{recipe_name}.log"
        mapped_path.unlink(missing_ok=True)
        log_path.unlink(missing_ok=True)
        command = (
            f"read_library {library}; read_blif -n {timed_path}; {recipe}; "
            f"print_stats; write_blif {mapped_path}"
        )
        completed = subprocess.run(
            [str(abc), "-c", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        log_path.write_text(completed.stdout, encoding="utf-8", newline="\n")
        if completed.returncode != 0 or not mapped_path.exists():
            errors.append({"recipe": recipe_name, "returncode": completed.returncode})
            continue
        score = analyze_mapped(mapped_path, metadata)
        results.append(
            {
                "recipe": recipe_name,
                **score,
                "mapped_blif": str(mapped_path),
                "mapped_blif_sha256": sha256(mapped_path.read_bytes()).hexdigest(),
                "abc_log": str(log_path),
                "abc_log_sha256": sha256(log_path.read_bytes()).hexdigest(),
                "abc_reported_unmet": "Cannot meet the target required times" in completed.stdout,
            }
        )
    results.sort(key=lambda item: (item["energy"], item["delay"], item["total_gate"], item["recipe"]))
    result = {
        "permutation_index": permutation_index,
        "mask": mask,
        "mask_hex": f"0x{mask:03x}",
        "required": required,
        "timed_blif": str(timed_path),
        "timed_blif_sha256": sha256(timed_path.read_bytes()).hexdigest(),
        "results": results,
        "errors": errors,
    }
    (candidate_dir / f"timing_d{required}_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def parse_masks(value: str) -> list[int]:
    masks = sorted({int(item.strip(), 0) for item in value.split(",") if item.strip()})
    if not masks:
        raise ValueError("at least one mask is required")
    return masks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--abc", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--permutations", type=int, required=True)
    parser.add_argument("--permutation-start", type=int, default=0)
    parser.add_argument("--masks", required=True)
    parser.add_argument("--required", type=int, default=6)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.permutations < 1:
        raise ValueError("permutations must be positive")
    if args.permutation_start < 0:
        raise ValueError("permutation-start must be non-negative")
    permutation_stop = args.permutation_start + args.permutations
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    masks = parse_masks(args.masks)
    expected_names = {
        f"perm_{permutation_index:03d}_phase_{mask:03x}"
        for permutation_index in range(args.permutation_start, permutation_stop)
        for mask in masks
    }
    candidate_dirs = sorted(
        path for path in args.candidate_dir.glob("perm_*_phase_*")
        if path.is_dir() and (path / "input.blif").is_file()
    )
    actual_names = {path.name for path in candidate_dirs}
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        raise ValueError(
            f"candidate coverage mismatch: count={len(actual_names)} "
            f"missing={missing[:16]!r} extra={extra[:16]!r}"
        )
    tasks = [
        (
            str(path.resolve()),
            metadata,
            str(args.abc.resolve()),
            str(args.library.resolve()),
            args.required,
        )
        for path in candidate_dirs
    ]
    completed_results: list[dict[str, object]] = []
    worker_errors: list[dict[str, object]] = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(map_candidate, task): Path(task[0]).name for task in tasks}
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # pragma: no cover - remote diagnostics
                worker_errors.append({"candidate": name, "error": repr(exc)})
                print(f"ERROR {name}: {exc!r}", flush=True)
                continue
            completed_results.append(result)
            best = result["results"][0] if result["results"] else None
            if best is not None:
                print(
                    f"{name} {best['total_gate']}/{best['delay']}/{best['energy']} "
                    f"recipe={best['recipe']} unmet={best['abc_reported_unmet']}",
                    flush=True,
                )

    flat = [
        {
            "permutation_index": candidate["permutation_index"],
            "mask": candidate["mask"],
            "mask_hex": candidate["mask_hex"],
            **mapped,
        }
        for candidate in completed_results
        for mapped in candidate["results"]
    ]
    flat.sort(
        key=lambda item: (
            item["energy"],
            item["delay"],
            item["total_gate"],
            item["permutation_index"],
            item["mask"],
            item["recipe"],
        )
    )
    recipe_errors = [
        {
            "permutation_index": candidate["permutation_index"],
            "mask": candidate["mask"],
            **error,
        }
        for candidate in completed_results
        for error in candidate["errors"]
    ]
    report = {
        "schema": "byte-adder-reachable-input-permutation-timing-map-v1",
        "candidate_dir": str(args.candidate_dir.resolve()),
        "metadata": str(args.metadata.resolve()),
        "metadata_sha256": sha256(args.metadata.read_bytes()).hexdigest(),
        "library": str(args.library.resolve()),
        "library_sha256": sha256(args.library.read_bytes()).hexdigest(),
        "permutation_start": args.permutation_start,
        "permutation_stop": permutation_stop,
        "permutations": args.permutations,
        "masks": masks,
        "required": args.required,
        "recipes": RECIPES,
        "expected_candidates": len(tasks),
        "completed_candidates": len(completed_results),
        "worker_error_count": len(worker_errors),
        "worker_errors": worker_errors,
        "recipe_error_count": len(recipe_errors),
        "recipe_errors": recipe_errors,
        "results": flat,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"summary={args.output}")
    if flat:
        best = flat[0]
        print(
            f"best perm={best['permutation_index']} phase={best['mask_hex']} "
            f"{best['total_gate']}/{best['delay']}/{best['energy']} recipe={best['recipe']}"
        )
    return 1 if worker_errors or recipe_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
