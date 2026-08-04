"""Map a minimized history-feature cover under Turing Complete costs.

Current input bits arrive at zero.  Every used ``hN`` input represents one
physical Bit Delay Line, costs five gates, and arrives at four.  ABC maps only
the ordinary Boolean suffix.  The report adds Delay Line costs explicitly and
replays every mapped result over the exact 131072-cycle sequence.

The current 2.1.292 runtime audit proves reset-to-zero, driven output, and
read-old/write-new behavior.  Results remain candidate discovery because they
still require physical materialization and the normal complete validation
chain.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess


WIDTH = 17
ROWS = 1 << WIDTH
MASK = ROWS - 1
GATE_RE = re.compile(r"^\.gate\s+(\S+)\s+(.+)$")
PIN_RE = re.compile(r"([A-Za-z0-9_]+)=([^\s]+)")
NAMES_RE = re.compile(r"^\.names(?:\s+(.*))?$")
HISTORY_RE = re.compile(r"^h(\d+)$")

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
    "plain": "fx; strash",
    "balanced": "fx; strash; balance; rewrite; refactor; balance",
    "dch": (
        "fx; strash; balance; rewrite; refactor; balance; rewrite -z; "
        "refactor -z; balance; dch"
    ),
    "dc2": "fx; strash; dc2; dch",
    "resub8": (
        "fx; strash; balance; resub -K 8; resub -K 8 -N 2; "
        "rewrite; refactor; balance; dch"
    ),
}


def xorshift_cycle(cycle: int) -> int:
    # The level script keeps a wide Int through all three operations.
    value = cycle
    value ^= value << 6
    value ^= value >> 11
    value ^= value << 9
    return value & MASK


def byte_adder_output(value: int) -> int:
    return (value & 0xFF) + ((value >> 8) & 0xFF) + ((value >> 16) & 1)


def run(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed with {completed.returncode}: {command!r}\n"
            f"{completed.stdout}"
        )
    return completed.stdout


def add_timing(source: Path, destination: Path, required: int) -> None:
    lines = source.read_text(encoding="ascii").splitlines()
    if not lines or lines[-1].strip() != ".end":
        raise ValueError(f"{source}: missing .end")
    timing = [
        ".default_input_arrival 0 0",
        f".default_output_required {required} {required}",
    ]
    for bit in range(WIDTH):
        timing.append(f".input_arrival h{bit} 4 4")
    for bit in range(8):
        timing.append(f".output_required s{bit} {required} {required}")
    timing.append(f".output_required cout {required} {required}")
    destination.write_text(
        "\n".join(lines[:-1] + timing + [".end"]) + "\n",
        encoding="ascii",
        newline="\n",
    )


def parse_names(lines: list[str], index: int) -> tuple[list[str], list[str], int]:
    match = NAMES_RE.match(lines[index].strip())
    if match is None:
        raise ValueError(lines[index])
    nets = match.group(1).split() if match.group(1) else []
    cubes: list[str] = []
    index += 1
    while index < len(lines) and not lines[index].lstrip().startswith("."):
        if lines[index].strip():
            cubes.append(lines[index].strip())
        index += 1
    return nets, cubes, index


def parse_mapped(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="ascii").splitlines()
    inputs: list[str] = []
    outputs: list[str] = []
    gates: list[dict[str, object]] = []
    names: list[dict[str, object]] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith(".inputs "):
            inputs.extend(line.split()[1:])
        elif line.startswith(".outputs "):
            outputs.extend(line.split()[1:])
        else:
            gate_match = GATE_RE.match(line)
            if gate_match is not None:
                kind = gate_match.group(1).upper()
                pins = dict(PIN_RE.findall(gate_match.group(2)))
                gates.append({"kind": kind, "pins": pins})
            elif line.startswith(".names"):
                nets, cubes, index = parse_names(lines, index)
                names.append({"nets": nets, "cubes": cubes})
                continue
        index += 1
    return {"inputs": inputs, "outputs": outputs, "gates": gates, "names": names}


def evaluate_names(nets: list[str], cubes: list[str], values: dict[str, int]) -> int:
    if not nets:
        raise ValueError(".names without output")
    output = 0
    inputs = nets[:-1]
    for cube in cubes:
        fields = cube.split()
        if not inputs:
            if fields[0] == "1":
                output = MASK_VECTOR
            continue
        pattern = fields[0]
        result = MASK_VECTOR
        for name, required in zip(inputs, pattern):
            if required == "1":
                result &= values[name]
            elif required == "0":
                result &= (~values[name]) & MASK_VECTOR
        if len(fields) == 1 or fields[1] == "1":
            output |= result
    return output


def packed_inputs() -> tuple[dict[str, int], list[int]]:
    values = {f"x{bit}": 0 for bit in range(WIDTH)}
    values.update({f"h{bit}": 0 for bit in range(WIDTH)})
    expected = [0] * 9
    for cycle in range(ROWS):
        current = xorshift_cycle(cycle)
        previous = xorshift_cycle(cycle - 1) if cycle else 0
        result = byte_adder_output(current)
        marker = 1 << cycle
        for bit in range(WIDTH):
            if (current >> bit) & 1:
                values[f"x{bit}"] |= marker
            if (previous >> bit) & 1:
                values[f"h{bit}"] |= marker
        for bit in range(9):
            if (result >> bit) & 1:
                expected[bit] |= marker
    return values, expected


MASK_VECTOR = (1 << ROWS) - 1


def analyze_and_replay(path: Path) -> dict[str, object]:
    network = parse_mapped(path)
    values, expected = packed_inputs()
    arrivals = {f"x{bit}": 0 for bit in range(WIDTH)}
    arrivals.update({f"h{bit}": 4 for bit in range(WIDTH)})
    used_history: set[int] = set()
    ordinary_gate = 0
    kind_counts: dict[str, int] = {}

    def note_input(name: str) -> None:
        match = HISTORY_RE.match(name)
        if match is not None:
            used_history.add(int(match.group(1)))

    for gate in network["gates"]:
        kind = str(gate["kind"])
        pins = dict(gate["pins"])
        if kind not in STEP_DELAY:
            raise ValueError(f"unsupported mapped gate {kind}")
        output = pins.pop("Y")
        sources = list(pins.values())
        for source in sources:
            note_input(source)
        if any(source not in values for source in sources):
            raise ValueError(f"unresolved gate inputs for {output}: {sources}")
        if kind == "BUF":
            result = values[sources[0]]
        elif kind == "NOT":
            result = (~values[sources[0]]) & MASK_VECTOR
        elif kind == "AND":
            result = values[sources[0]] & values[sources[1]]
        elif kind == "NAND":
            result = (~(values[sources[0]] & values[sources[1]])) & MASK_VECTOR
        elif kind == "OR":
            result = values[sources[0]] | values[sources[1]]
        elif kind == "NOR":
            result = (~(values[sources[0]] | values[sources[1]])) & MASK_VECTOR
        elif kind == "XOR":
            result = values[sources[0]] ^ values[sources[1]]
        elif kind == "XNOR":
            result = (~(values[sources[0]] ^ values[sources[1]])) & MASK_VECTOR
        else:
            raise AssertionError(kind)
        values[output] = result
        arrivals[output] = max((arrivals[source] for source in sources), default=0) + STEP_DELAY[kind]
        ordinary_gate += GATE_COST[kind]
        kind_counts[kind] = kind_counts.get(kind, 0) + 1

    for record in network["names"]:
        nets = list(record["nets"])
        for source in nets[:-1]:
            note_input(source)
        values[nets[-1]] = evaluate_names(nets, list(record["cubes"]), values)
        arrivals[nets[-1]] = max((arrivals[source] for source in nets[:-1]), default=0)

    outputs = [f"s{bit}" for bit in range(8)] + ["cout"]
    mismatches = []
    for bit, name in enumerate(outputs):
        difference = values[name] ^ expected[bit]
        mismatches.append(difference.bit_count())
    delay_line_gate = 5 * len(used_history)
    total_gate = ordinary_gate + delay_line_gate
    output_arrivals = [arrivals[name] for name in outputs]
    delay = max(output_arrivals)
    return {
        "ordinary_gate": ordinary_gate,
        "delay_line_gate": delay_line_gate,
        "total_gate": total_gate,
        "delay": delay,
        "energy": total_gate * delay,
        "used_history_bits": sorted(used_history),
        "used_history_count": len(used_history),
        "kind_counts": dict(sorted(kind_counts.items())),
        "output_arrivals": output_arrivals,
        "mismatch_count_by_output": mismatches,
        "mismatch_union": sum(mismatches),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cover", type=Path, required=True)
    parser.add_argument("--abc", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--required", type=int, nargs="+", default=[5, 6, 7])
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    base_blif = output_dir / "cover.blif"
    conversion_log = run(
        [
            str(args.abc),
            "-c",
            f"read_library {args.library}; read_pla {args.cover}; write_blif {base_blif}",
        ]
    )
    (output_dir / "convert.log").write_text(conversion_log, encoding="utf-8", newline="\n")

    results: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    for required in args.required:
        timed = output_dir / f"timed_d{required}.blif"
        add_timing(base_blif, timed, required)
        for name, prefix in RECIPES.items():
            mapped = output_dir / f"mapped_d{required}_{name}.blif"
            log = output_dir / f"abc_d{required}_{name}.log"
            command = (
                f"read_library {args.library}; read_blif -n {timed}; "
                f"{prefix}; map -D {required}; print_stats; write_blif {mapped}"
            )
            try:
                output = run([str(args.abc), "-c", command])
                log.write_text(output, encoding="utf-8", newline="\n")
                score = analyze_and_replay(mapped)
                results.append(
                    {
                        "required": required,
                        "recipe": name,
                        **score,
                        "abc_unmet_timing": "Cannot meet the target required times" in output,
                        "mapped": str(mapped),
                        "mapped_sha256": sha256(mapped.read_bytes()).hexdigest(),
                        "log": str(log),
                        "log_sha256": sha256(log.read_bytes()).hexdigest(),
                    }
                )
            except Exception as exc:
                errors.append({"required": required, "recipe": name, "error": repr(exc)})

    results.sort(key=lambda item: (item["energy"], item["delay"], item["total_gate"]))
    report = {
        "schema": "tc-byte-adder-history-cover-map-v1",
        "status": "candidate-discovery-only",
        "cover": str(args.cover.resolve()),
        "cover_sha256": sha256(args.cover.read_bytes()).hexdigest(),
        "abc": str(args.abc.resolve()),
        "library": str(args.library.resolve()),
        "delay_line_model": {
            "gate": 5,
            "arrival": 4,
            "initial_state": 0,
            "cycle_zero_driven": True,
            "timing_cut": False,
        },
        "results": results,
        "errors": errors,
    }
    report_path = output_dir / "summary.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
