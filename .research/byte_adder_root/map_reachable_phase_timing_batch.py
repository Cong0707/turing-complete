"""Timing-aware ABC remapping for reachable-domain output-phase candidates."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess


GATE_RE = re.compile(r"^\.gate\s+(\S+)\s+(.+)$")
PIN_RE = re.compile(r"([A-Za-z0-9_]+)=([^\s]+)")
STEP_DELAY = {
    "BUF": 0,
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 2,
    "XNOR": 2,
}
GATE_COST = {
    "BUF": 0,
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 3,
    "XNOR": 3,
}
RECIPES = {
    "plain_d6": "fx; strash; map -D 6",
    "dch_d6": (
        "fx; strash; balance; rewrite; refactor; balance; rewrite -z; "
        "refactor -z; balance; dch; map -D 6"
    ),
    "dc2_d6": "fx; strash; dc2; dch; map -D 6",
    "resub8_d6": (
        "fx; strash; balance; resub -K 8; resub -K 8 -N 2; rewrite; "
        "refactor; balance; dch; map -D 6"
    ),
}


def add_timing(input_path: Path, output_path: Path, metadata: dict[str, object], required: int) -> None:
    lines = input_path.read_text(encoding="ascii").splitlines()
    if not lines or lines[-1].strip() != ".end":
        raise ValueError(f"{input_path}: missing terminal .end")
    timing = [
        ".default_input_arrival 0 0",
        f".default_output_required {required} {required}",
    ]
    for item in metadata["boundary"]:
        timing.append(f".input_arrival n{item['id']} {item['arrival']} {item['arrival']}")
    for index in range(len(metadata["outputs"])):
        timing.append(f".output_required out{index} {required} {required}")
    encoded = "\n".join(lines[:-1] + timing + [".end"]) + "\n"
    output_path.write_text(encoded, encoding="ascii", newline="\n")


def analyze_mapped(path: Path, metadata: dict[str, object]) -> dict[str, object]:
    arrivals = {f"n{item['id']}": int(item["arrival"]) for item in metadata["boundary"]}
    residual_gate = 0
    components = 0
    kinds: dict[str, int] = {}
    for raw_line in path.read_text(encoding="ascii").splitlines():
        match = GATE_RE.match(raw_line.strip())
        if match is None:
            continue
        kind = match.group(1).upper()
        if kind not in STEP_DELAY:
            raise ValueError(f"unsupported mapped gate {kind!r}")
        pins = dict(PIN_RE.findall(match.group(2)))
        output = pins["Y"]
        inputs = [value for key, value in pins.items() if key != "Y"]
        missing = [value for value in inputs if value not in arrivals]
        if missing:
            raise ValueError(f"{path}: {output} has unresolved inputs {missing}")
        arrivals[output] = max((arrivals[value] for value in inputs), default=0) + STEP_DELAY[kind]
        residual_gate += GATE_COST[kind]
        components += 1
        kinds[kind] = kinds.get(kind, 0) + 1
    output_arrivals = [arrivals[f"out{index}"] for index in range(len(metadata["outputs"]))]
    total_gate = int(metadata["fixed_gate"]) + residual_gate
    delay = max(output_arrivals)
    return {
        "mapped_components": components,
        "kind_counts": dict(sorted(kinds.items())),
        "residual_gate": residual_gate,
        "total_gate": total_gate,
        "output_arrivals": output_arrivals,
        "delay": delay,
        "energy": total_gate * delay,
    }


def map_phase(task: tuple[object, ...]) -> dict[str, object]:
    phase_dir, metadata, abc, library, required = task
    phase_dir = Path(phase_dir)
    input_path = phase_dir / "input.blif"
    timed_path = phase_dir / f"timed_d{required}.blif"
    add_timing(input_path, timed_path, metadata, int(required))
    results: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    for recipe_name, recipe in RECIPES.items():
        mapped_path = phase_dir / f"mapped_{recipe_name}.blif"
        log_path = phase_dir / f"abc_{recipe_name}.log"
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
    mask = int(phase_dir.name.split("_")[-1], 16)
    result = {
        "mask": mask,
        "mask_hex": f"0x{mask:03x}",
        "timed_blif": str(timed_path),
        "timed_blif_sha256": sha256(timed_path.read_bytes()).hexdigest(),
        "required": required,
        "results": results,
        "errors": errors,
    }
    (phase_dir / f"timing_d{required}_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase-dir", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--abc", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--required", type=int, default=6)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--expected-phases", type=int, default=512)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    phase_dirs = sorted(
        path for path in args.phase_dir.glob("phase_*")
        if path.is_dir() and (path / "input.blif").is_file()
    )
    expected_names = {f"phase_{mask:03x}" for mask in range(args.expected_phases)}
    actual_names = {path.name for path in phase_dirs}
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        raise ValueError(
            f"phase directory coverage mismatch: count={len(actual_names)} "
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
        for path in phase_dirs
    ]
    completed_results: list[dict[str, object]] = []
    worker_errors: list[dict[str, object]] = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(map_phase, task): Path(task[0]).name for task in tasks}
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # pragma: no cover - remote diagnostics
                worker_errors.append({"phase": name, "error": repr(exc)})
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
        {"mask": phase["mask"], "mask_hex": phase["mask_hex"], **candidate}
        for phase in completed_results
        for candidate in phase["results"]
    ]
    flat.sort(key=lambda item: (item["energy"], item["delay"], item["total_gate"], item["mask"], item["recipe"]))
    recipe_errors = [
        {"mask": phase["mask"], "mask_hex": phase["mask_hex"], **error}
        for phase in completed_results
        for error in phase["errors"]
    ]
    report = {
        "schema": "byte-adder-reachable-output-phase-timing-map-v1",
        "phase_dir": str(args.phase_dir.resolve()),
        "metadata": str(args.metadata.resolve()),
        "metadata_sha256": sha256(args.metadata.read_bytes()).hexdigest(),
        "library": str(args.library.resolve()),
        "library_sha256": sha256(args.library.read_bytes()).hexdigest(),
        "required": args.required,
        "recipes": RECIPES,
        "expected_phases": len(tasks),
        "completed_phases": len(completed_results),
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
            f"best phase={best['mask_hex']} {best['total_gate']}/{best['delay']}/"
            f"{best['energy']} recipe={best['recipe']}"
        )
    return 1 if worker_errors or recipe_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
