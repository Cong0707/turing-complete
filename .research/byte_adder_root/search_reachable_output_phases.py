"""Enumerate all output phases of the reachable-domain byte-adder PLA.

Each phase is minimized independently with PyEDA Espresso.  The selected
phase is then converted back to the original output polarity, mapped by ABC,
and scored with the authoritative Turing Complete gate costs and boundary
arrival times.  This is candidate discovery only; every improvement still has
to pass the full DAG, BUS/Z, physical-net, geometry and v15 pipeline.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Iterable

from pyeda.boolalg.espresso import FTYPE, RTYPE, espresso


Implicant = tuple[tuple[int, ...], tuple[int, ...]]
WorkerContext = tuple[object, ...]
WORKER_CONTEXT: WorkerContext | None = None
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


def parse_pla(path: Path) -> tuple[list[str], list[str], tuple[Implicant, ...]]:
    input_names: list[str] = []
    output_names: list[str] = []
    cover: set[Implicant] = set()
    ninputs = noutputs = None
    pla_type = None
    for raw_line in path.read_text(encoding="ascii").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(".i "):
            ninputs = int(line.split()[1])
        elif line.startswith(".o "):
            noutputs = int(line.split()[1])
        elif line.startswith(".type "):
            pla_type = line.split()[1]
        elif line.startswith(".ilb "):
            input_names = line.split()[1:]
        elif line.startswith(".ob "):
            output_names = line.split()[1:]
        elif line.startswith("."):
            continue
        else:
            in_pattern, out_pattern = line.split()
            in_vector = tuple({"0": 1, "1": 2, "-": 3}[value] for value in in_pattern)
            out_vector = tuple({"0": 0, "1": 1, "-": 2}[value] for value in out_pattern)
            cover.add((in_vector, out_vector))
    if pla_type != "fr":
        raise ValueError(f"expected .type fr, got {pla_type!r}")
    if ninputs != len(input_names) or noutputs != len(output_names):
        raise ValueError("PLA label counts do not match .i/.o")
    if any(value not in (0, 1) for _, outputs in cover for value in outputs):
        raise ValueError("care relation must fully specify every output")
    by_point: dict[tuple[int, ...], tuple[int, ...]] = {}
    for point, outputs in cover:
        previous = by_point.setdefault(point, outputs)
        if previous != outputs:
            raise ValueError(f"care relation is not functional at point {point!r}")
    return input_names, output_names, tuple(sorted(cover))


def cube_matches(cube: tuple[int, ...], point: tuple[int, ...]) -> bool:
    return all(required == 3 or required == actual for required, actual in zip(cube, point))


def evaluate_cover(
    cover: Iterable[Implicant], point: tuple[int, ...], noutputs: int
) -> tuple[int, ...]:
    values = [0] * noutputs
    for cube, outputs in cover:
        if not cube_matches(cube, point):
            continue
        for index, value in enumerate(outputs):
            if value == 1:
                values[index] = 1
    return tuple(values)


def write_phase_blif(
    path: Path,
    input_names: list[str],
    output_names: list[str],
    minimized: Iterable[Implicant],
    mask: int,
) -> None:
    ordered = sorted(minimized)
    lines = [
        f".model reachable_phase_{mask:03x}",
        ".inputs " + " ".join(input_names),
        ".outputs " + " ".join(output_names),
    ]
    for output_index, output_name in enumerate(output_names):
        phase_output = f"phase_{output_name}" if (mask >> output_index) & 1 else output_name
        lines.append(".names " + " ".join(input_names) + " " + phase_output)
        for cube, outputs in ordered:
            if outputs[output_index] != 1:
                continue
            pattern = "".join({1: "0", 2: "1", 3: "-"}[value] for value in cube)
            lines.append(f"{pattern} 1")
        if (mask >> output_index) & 1:
            lines.extend((f".names {phase_output} {output_name}", "0 1"))
    lines.append(".end")
    path.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")


def analyze_mapped(path: Path, metadata: dict[str, object]) -> dict[str, object]:
    arrivals = {f"n{item['id']}": int(item["arrival"]) for item in metadata["boundary"]}
    residual_gate = 0
    components = 0
    kind_counts: dict[str, int] = {}
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
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
    output_arrivals = [arrivals[f"out{index}"] for index in range(len(metadata["outputs"]))]
    total_gate = int(metadata["fixed_gate"]) + residual_gate
    delay = max(output_arrivals)
    return {
        "mapped_components": components,
        "kind_counts": dict(sorted(kind_counts.items())),
        "residual_gate": residual_gate,
        "total_gate": total_gate,
        "output_arrivals": output_arrivals,
        "delay": delay,
        "energy": total_gate * delay,
    }


def init_worker(*context: object) -> None:
    global WORKER_CONTEXT
    WORKER_CONTEXT = context


def solve_mask(mask: int) -> dict[str, object]:
    if WORKER_CONTEXT is None:
        raise RuntimeError("worker context is not initialized")
    (
        input_names,
        output_names,
        care_cover,
        metadata,
        abc,
        library,
        output_dir,
        abc_commands,
    ) = WORKER_CONTEXT
    input_names = list(input_names)
    output_names = list(output_names)
    care_cover = tuple(care_cover)
    output_dir = Path(output_dir)
    phase_cover: set[Implicant] = set()
    for point, expected in care_cover:
        phased = tuple(value ^ ((mask >> index) & 1) for index, value in enumerate(expected))
        phase_cover.add((point, phased))

    minimized = espresso(
        len(input_names),
        len(output_names),
        phase_cover,
        intype=FTYPE | RTYPE,
    )
    mismatches = 0
    for point, expected in phase_cover:
        if evaluate_cover(minimized, point, len(output_names)) != expected:
            mismatches += 1
            break
    if mismatches:
        raise RuntimeError(f"phase {mask:#x} failed care verification")

    phase_dir = output_dir / f"phase_{mask:03x}"
    phase_dir.mkdir(parents=True, exist_ok=True)
    input_blif = phase_dir / "input.blif"
    mapped_blif = phase_dir / "mapped.blif"
    log_path = phase_dir / "abc.log"
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
        raise RuntimeError(f"ABC failed for phase {mask:#x}: rc={completed.returncode}")

    score = analyze_mapped(mapped_blif, metadata)
    ordered = sorted(minimized)
    result = {
        "mask": mask,
        "mask_hex": f"0x{mask:03x}",
        "inverted_outputs": [index for index in range(len(output_names)) if (mask >> index) & 1],
        "implicants": len(ordered),
        "input_literals": sum(sum(value != 3 for value in cube) for cube, _ in ordered),
        "output_literals": sum(sum(value == 1 for value in outputs) for _, outputs in ordered),
        "care_mismatches": mismatches,
        **score,
        "input_blif": str(input_blif),
        "input_blif_sha256": sha256(input_blif.read_bytes()).hexdigest(),
        "mapped_blif": str(mapped_blif),
        "mapped_blif_sha256": sha256(mapped_blif.read_bytes()).hexdigest(),
        "abc_log": str(log_path),
        "abc_log_sha256": sha256(log_path.read_bytes()).hexdigest(),
    }
    (phase_dir / "result.json").write_text(
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
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--expected-care-rows", type=int, default=23328)
    parser.add_argument("--start-mask", type=int, default=0)
    parser.add_argument("--stop-mask", type=int)
    parser.add_argument(
        "--abc-commands",
        default="fx; strash; dch; map -a",
    )
    args = parser.parse_args()

    input_names, output_names, care_cover = parse_pla(args.input)
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    expected_inputs = [f"n{item['id']}" for item in metadata["boundary"]]
    expected_outputs = [f"out{index}" for index in range(len(metadata["outputs"]))]
    if input_names != expected_inputs:
        raise ValueError(f"boundary labels/order mismatch: {input_names!r} != {expected_inputs!r}")
    if output_names != expected_outputs:
        raise ValueError(f"output labels/order mismatch: {output_names!r} != {expected_outputs!r}")
    if len(care_cover) != args.expected_care_rows:
        raise ValueError(
            f"care row count mismatch: {len(care_cover)} != {args.expected_care_rows}"
        )
    stop_mask = args.stop_mask if args.stop_mask is not None else 1 << len(output_names)
    if not (0 <= args.start_mask < stop_mask <= 1 << len(output_names)):
        raise ValueError("invalid phase-mask interval")
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
    results: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    with ProcessPoolExecutor(
        max_workers=args.workers,
        initializer=init_worker,
        initargs=common,
    ) as executor:
        futures = {
            executor.submit(solve_mask, mask): mask
            for mask in range(args.start_mask, stop_mask)
        }
        for future in as_completed(futures):
            mask = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # pragma: no cover - remote worker diagnostics
                errors.append({"mask": mask, "error": repr(exc)})
                print(f"ERROR phase={mask:#05x}: {exc!r}", flush=True)
                continue
            results.append(result)
            print(
                f"phase={mask:#05x} {result['total_gate']}/{result['delay']}/"
                f"{result['energy']} residual={result['residual_gate']} "
                f"imp={result['implicants']} lit={result['input_literals']}",
                flush=True,
            )

    results.sort(key=lambda item: (item["energy"], item["delay"], item["total_gate"], item["mask"]))
    errors.sort(key=lambda item: item["mask"])
    report = {
        "schema": "byte-adder-reachable-output-phase-search-v1",
        "input": str(args.input.resolve()),
        "input_sha256": sha256(args.input.read_bytes()).hexdigest(),
        "metadata": str(args.metadata.resolve()),
        "metadata_sha256": sha256(args.metadata.read_bytes()).hexdigest(),
        "abc": str(args.abc.resolve()),
        "library": str(args.library.resolve()),
        "library_sha256": sha256(args.library.read_bytes()).hexdigest(),
        "abc_commands": args.abc_commands,
        "workers": args.workers,
        "start_mask": args.start_mask,
        "stop_mask": stop_mask,
        "expected_masks": stop_mask - args.start_mask,
        "completed_masks": len(results),
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
            f"best phase={best['mask_hex']} {best['total_gate']}/{best['delay']}/"
            f"{best['energy']} residual={best['residual_gate']}"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
