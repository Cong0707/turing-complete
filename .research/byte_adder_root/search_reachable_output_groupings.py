"""Search alternative reachable-domain extensions by regrouping outputs."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess

from pyeda.boolalg.espresso import FTYPE, RTYPE, espresso

from search_reachable_output_phases import (
    Implicant,
    analyze_mapped,
    evaluate_cover,
    parse_pla,
    write_phase_blif,
)


GROUPINGS: dict[str, tuple[tuple[int, ...], ...]] = {
    "all": (tuple(range(9)),),
    "independent": tuple((index,) for index in range(9)),
    "low6_high3": (tuple(range(6)), (6, 7, 8)),
    "low5_high4": (tuple(range(5)), (5, 6, 7, 8)),
    "low4_mid2_high3": ((0, 1, 2, 3), (4, 5), (6, 7, 8)),
    "three_clusters": ((0, 1, 2), (3, 4, 5), (6, 7, 8)),
    "adjacent_pairs": ((0, 1), (2, 3), (4, 5), (6, 7), (8,)),
    "staggered_pairs": ((0,), (1, 2), (3, 4), (5, 6), (7, 8)),
    "high_independent": (tuple(range(6)), (6,), (7,), (8,)),
    "low_independent": ((0,), (1,), (2,), (3,), (4,), (5,), (6, 7, 8)),
}


def minimize_group(
    care_cover: tuple[Implicant, ...],
    group: tuple[int, ...],
    ninputs: int,
) -> set[Implicant]:
    projected = {
        (point, tuple(expected[index] for index in group))
        for point, expected in care_cover
    }
    minimized = espresso(ninputs, len(group), projected, intype=FTYPE | RTYPE)
    for point, expected in projected:
        if evaluate_cover(minimized, point, len(group)) != expected:
            raise RuntimeError(f"group {group!r} failed care verification")
    return minimized


def solve_grouping(task: tuple[object, ...]) -> dict[str, object]:
    (
        name,
        groups,
        input_names,
        output_names,
        care_cover,
        metadata,
        abc,
        library,
        output_root,
        abc_commands,
    ) = task
    name = str(name)
    groups = tuple(tuple(int(index) for index in group) for group in groups)
    input_names = list(input_names)
    output_names = list(output_names)
    care_cover = tuple(care_cover)
    output_dir = Path(output_root) / name
    output_dir.mkdir(parents=True, exist_ok=True)

    cube_outputs: dict[tuple[int, ...], list[int]] = {}
    group_stats: list[dict[str, object]] = []
    for group in groups:
        minimized = minimize_group(care_cover, group, len(input_names))
        group_stats.append(
            {
                "outputs": list(group),
                "implicants": len(minimized),
                "input_literals": sum(sum(value != 3 for value in cube) for cube, _ in minimized),
                "output_literals": sum(sum(value == 1 for value in outputs) for _, outputs in minimized),
            }
        )
        for cube, group_outputs in minimized:
            expanded = cube_outputs.setdefault(cube, [0] * len(output_names))
            for local_index, output_index in enumerate(group):
                if group_outputs[local_index] == 1:
                    expanded[output_index] = 1

    combined: set[Implicant] = {
        (cube, tuple(outputs)) for cube, outputs in cube_outputs.items()
    }
    for point, expected in care_cover:
        if evaluate_cover(combined, point, len(output_names)) != expected:
            raise RuntimeError(f"grouping {name!r} failed combined care verification")

    input_blif = output_dir / "input.blif"
    mapped_blif = output_dir / "mapped.blif"
    log_path = output_dir / "abc.log"
    write_phase_blif(input_blif, input_names, output_names, combined, 0)
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
        raise RuntimeError(f"ABC failed for grouping {name!r}: rc={completed.returncode}")
    score = analyze_mapped(mapped_blif, metadata)
    result = {
        "name": name,
        "groups": [list(group) for group in groups],
        "group_stats": group_stats,
        "combined_implicants": len(combined),
        "combined_input_literals": sum(sum(value != 3 for value in cube) for cube, _ in combined),
        "combined_output_literals": sum(sum(value == 1 for value in outputs) for _, outputs in combined),
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--abc", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--only", nargs="*", choices=sorted(GROUPINGS))
    parser.add_argument("--abc-commands", default="fx; strash; dch; map -a")
    args = parser.parse_args()

    input_names, output_names, care_cover = parse_pla(args.input)
    if len(output_names) != 9:
        raise ValueError(f"expected 9 outputs, got {len(output_names)}")
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    selected = args.only if args.only else sorted(GROUPINGS)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    common = (
        tuple(input_names),
        tuple(output_names),
        care_cover,
        metadata,
        str(args.abc.resolve()),
        str(args.library.resolve()),
        str(args.output_dir.resolve()),
        args.abc_commands,
    )
    tasks = [(name, GROUPINGS[name], *common) for name in selected]
    results: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(solve_grouping, task): task[0] for task in tasks}
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # pragma: no cover - remote diagnostics
                errors.append({"name": name, "error": repr(exc)})
                print(f"ERROR grouping={name}: {exc!r}", flush=True)
                continue
            results.append(result)
            print(
                f"grouping={name} {result['total_gate']}/{result['delay']}/"
                f"{result['energy']} residual={result['residual_gate']} "
                f"imp={result['combined_implicants']}",
                flush=True,
            )
    results.sort(key=lambda item: (item["energy"], item["delay"], item["total_gate"], item["name"]))
    errors.sort(key=lambda item: item["name"])
    report = {
        "schema": "byte-adder-reachable-output-grouping-search-v1",
        "input": str(args.input.resolve()),
        "input_sha256": sha256(args.input.read_bytes()).hexdigest(),
        "metadata": str(args.metadata.resolve()),
        "metadata_sha256": sha256(args.metadata.read_bytes()).hexdigest(),
        "library": str(args.library.resolve()),
        "library_sha256": sha256(args.library.read_bytes()).hexdigest(),
        "abc_commands": args.abc_commands,
        "expected_groupings": len(tasks),
        "completed_groupings": len(results),
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
        print(f"best grouping={best['name']} {best['total_gate']}/{best['delay']}/{best['energy']}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
