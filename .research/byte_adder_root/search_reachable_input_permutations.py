"""Search Espresso extensions induced by deterministic input permutations."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import subprocess

from pyeda.boolalg.espresso import FTYPE, RTYPE, espresso

from search_reachable_output_phases import (
    Implicant,
    analyze_mapped,
    evaluate_cover,
    parse_pla,
    write_phase_blif,
)


WORKER_CONTEXT: tuple[object, ...] | None = None


def make_permutations(count: int, arrivals: list[int]) -> list[tuple[int, ...]]:
    if count < 1:
        raise ValueError("count must be positive")
    width = len(arrivals)
    candidates: list[tuple[int, ...]] = [
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


def init_worker(*context: object) -> None:
    global WORKER_CONTEXT
    WORKER_CONTEXT = context


def solve_one(permutation_index: int, mask: int) -> dict[str, object]:
    if WORKER_CONTEXT is None:
        raise RuntimeError("worker context is not initialized")
    (
        permutations,
        input_names,
        output_names,
        care_cover,
        metadata,
        abc,
        library,
        output_root,
        abc_commands,
    ) = WORKER_CONTEXT
    permutation = tuple(permutations[permutation_index])
    input_names = list(input_names)
    output_names = list(output_names)
    care_cover = tuple(care_cover)

    permuted_cover: set[Implicant] = set()
    original_phased: set[Implicant] = set()
    for point, expected in care_cover:
        phased = tuple(value ^ ((mask >> index) & 1) for index, value in enumerate(expected))
        permuted_point = tuple(point[old_index] for old_index in permutation)
        permuted_cover.add((permuted_point, phased))
        original_phased.add((point, phased))
    minimized_permuted = espresso(
        len(input_names),
        len(output_names),
        permuted_cover,
        intype=FTYPE | RTYPE,
    )

    minimized: set[Implicant] = set()
    for cube, outputs in minimized_permuted:
        original_cube = [3] * len(input_names)
        for new_index, old_index in enumerate(permutation):
            original_cube[old_index] = cube[new_index]
        minimized.add((tuple(original_cube), outputs))
    for point, expected in original_phased:
        if evaluate_cover(minimized, point, len(output_names)) != expected:
            raise RuntimeError(
                f"permutation {permutation_index} phase {mask:#x} failed care verification"
            )

    output_dir = Path(output_root) / f"perm_{permutation_index:03d}_phase_{mask:03x}"
    output_dir.mkdir(parents=True, exist_ok=True)
    input_blif = output_dir / "input.blif"
    mapped_blif = output_dir / "mapped.blif"
    log_path = output_dir / "abc.log"
    mapped_blif.unlink(missing_ok=True)
    log_path.unlink(missing_ok=True)
    write_phase_blif(input_blif, input_names, output_names, minimized, mask)
    command = (
        f"read_library {library}; read_blif {input_blif}; {abc_commands}; "
        f"print_stats; write_blif {mapped_blif}"
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
    if completed.returncode != 0 or not mapped_blif.exists():
        raise RuntimeError(
            f"ABC failed for permutation {permutation_index} phase {mask:#x}: "
            f"rc={completed.returncode}"
        )
    score = analyze_mapped(mapped_blif, metadata)
    result = {
        "permutation_index": permutation_index,
        "permutation": list(permutation),
        "permuted_input_names": [input_names[index] for index in permutation],
        "mask": mask,
        "mask_hex": f"0x{mask:03x}",
        "implicants": len(minimized),
        "input_literals": sum(sum(value != 3 for value in cube) for cube, _ in minimized),
        "output_literals": sum(sum(value == 1 for value in outputs) for _, outputs in minimized),
        "care_mismatches": 0,
        **score,
        "input_blif": str(input_blif),
        "input_blif_sha256": sha256(input_blif.read_bytes()).hexdigest(),
        "mapped_blif": str(mapped_blif),
        "mapped_blif_sha256": sha256(mapped_blif.read_bytes()).hexdigest(),
        "abc_log": str(log_path),
        "abc_log_sha256": sha256(log_path.read_bytes()).hexdigest(),
    }
    (output_dir / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def parse_masks(value: str, output_count: int) -> list[int]:
    masks = sorted({int(item.strip(), 0) for item in value.split(",") if item.strip()})
    if not masks or any(mask < 0 or mask >= 1 << output_count for mask in masks):
        raise ValueError(f"invalid masks {masks!r}")
    return masks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--abc", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--permutations", type=int, default=64)
    parser.add_argument("--permutation-start", type=int, default=0)
    parser.add_argument("--masks", default="0x000,0x086")
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--expected-care-rows", type=int, default=23328)
    parser.add_argument("--abc-commands", default="fx; strash; dch; map -a")
    args = parser.parse_args()

    input_names, output_names, care_cover = parse_pla(args.input)
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    expected_inputs = [f"n{item['id']}" for item in metadata["boundary"]]
    expected_outputs = [f"out{index}" for index in range(len(metadata["outputs"]))]
    if input_names != expected_inputs or output_names != expected_outputs:
        raise ValueError("PLA labels/order do not match metadata")
    if len(care_cover) != args.expected_care_rows:
        raise ValueError(
            f"care row count mismatch: {len(care_cover)} != {args.expected_care_rows}"
        )
    if args.permutations < 1:
        raise ValueError("permutations must be positive")
    if args.permutation_start < 0:
        raise ValueError("permutation-start must be non-negative")
    arrivals = [int(item["arrival"]) for item in metadata["boundary"]]
    permutation_stop = args.permutation_start + args.permutations
    permutations = make_permutations(permutation_stop, arrivals)
    masks = parse_masks(args.masks, len(output_names))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    context = (
        tuple(permutations),
        tuple(input_names),
        tuple(output_names),
        care_cover,
        metadata,
        str(args.abc.resolve()),
        str(args.library.resolve()),
        str(args.output_dir.resolve()),
        args.abc_commands,
    )
    expected_tasks = [
        (index, mask)
        for index in range(args.permutation_start, permutation_stop)
        for mask in masks
    ]
    results: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    with ProcessPoolExecutor(
        max_workers=args.workers,
        initializer=init_worker,
        initargs=context,
    ) as executor:
        futures = {
            executor.submit(solve_one, permutation_index, mask): (permutation_index, mask)
            for permutation_index, mask in expected_tasks
        }
        for future in as_completed(futures):
            permutation_index, mask = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # pragma: no cover - remote diagnostics
                errors.append(
                    {
                        "permutation_index": permutation_index,
                        "mask": mask,
                        "error": repr(exc),
                    }
                )
                print(f"ERROR perm={permutation_index} phase={mask:#05x}: {exc!r}", flush=True)
                continue
            results.append(result)
            print(
                f"perm={permutation_index:03d} phase={mask:#05x} "
                f"{result['total_gate']}/{result['delay']}/{result['energy']} "
                f"residual={result['residual_gate']} imp={result['implicants']}",
                flush=True,
            )
    results.sort(
        key=lambda item: (
            item["energy"],
            item["delay"],
            item["total_gate"],
            item["permutation_index"],
            item["mask"],
        )
    )
    errors.sort(key=lambda item: (item["permutation_index"], item["mask"]))
    report = {
        "schema": "byte-adder-reachable-input-permutation-search-v1",
        "input": str(args.input.resolve()),
        "input_sha256": sha256(args.input.read_bytes()).hexdigest(),
        "metadata": str(args.metadata.resolve()),
        "metadata_sha256": sha256(args.metadata.read_bytes()).hexdigest(),
        "library": str(args.library.resolve()),
        "library_sha256": sha256(args.library.read_bytes()).hexdigest(),
        "abc_commands": args.abc_commands,
        "permutation_start": args.permutation_start,
        "permutation_stop": permutation_stop,
        "permutation_count": args.permutations,
        "masks": masks,
        "expected_tasks": len(expected_tasks),
        "completed_tasks": len(results),
        "error_count": len(errors),
        "errors": errors,
        "results": results,
    }
    report_path = args.output_dir / "summary.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"summary={report_path}")
    if results:
        best = results[0]
        print(
            f"best perm={best['permutation_index']} phase={best['mask_hex']} "
            f"{best['total_gate']}/{best['delay']}/{best['energy']}"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
