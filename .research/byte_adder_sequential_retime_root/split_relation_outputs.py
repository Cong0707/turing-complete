"""Split a multi-output FR relation without changing its care set."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


def parse_groups(values: list[str], output_names: list[str]) -> list[tuple[str, list[int]]]:
    groups: list[tuple[str, list[int]]] = []
    for value in values:
        label, separator, names = value.partition("=")
        if not separator:
            raise ValueError(f"group must be LABEL=OUT[,OUT...]: {value!r}")
        indexes = [output_names.index(name) for name in names.split(",")]
        if len(indexes) != len(set(indexes)):
            raise ValueError(f"duplicate output in {value!r}")
        groups.append((label, indexes))
    return groups


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--group", action="append", default=[])
    args = parser.parse_args()

    source_lines = args.input.read_text(encoding="ascii").splitlines()
    output_names: list[str] = []
    input_count = output_count = None
    rows: list[tuple[str, str]] = []
    for raw_line in source_lines:
        line = raw_line.strip()
        if line.startswith(".i "):
            input_count = int(line.split()[1])
        elif line.startswith(".o "):
            output_count = int(line.split()[1])
        elif line.startswith(".ob "):
            output_names = line.split()[1:]
        elif line and not line.startswith(".") and not line.startswith("#"):
            rows.append(tuple(line.split()))
    if output_count != len(output_names) or input_count is None:
        raise ValueError("invalid source PLA header")

    requested = args.group or [f"{name}={name}" for name in output_names]
    groups = parse_groups(requested, output_names)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, object]] = []
    header_prefix = []
    for line in source_lines:
        if line.startswith(".o ") or line.startswith(".ob "):
            continue
        if line == ".e" or (line and not line.startswith(".")):
            continue
        header_prefix.append(line)

    for label, indexes in groups:
        names = [output_names[index] for index in indexes]
        lines = list(header_prefix)
        insertion = next(
            index for index, line in enumerate(lines) if line.startswith(".type ")
        )
        lines.insert(insertion, f".o {len(indexes)}")
        lines.insert(insertion + 2, ".ob " + " ".join(names))
        for input_pattern, output_pattern in rows:
            selected = "".join(output_pattern[index] for index in indexes)
            lines.append(f"{input_pattern} {selected}")
        lines.append(".e")
        encoded = ("\n".join(lines) + "\n").encode("ascii")
        path = output_dir / f"{label}_relation_fr.pla"
        path.write_bytes(encoded)
        reports.append(
            {
                "label": label,
                "outputs": names,
                "path": str(path),
                "sha256": sha256(encoded).hexdigest(),
                "bytes": len(encoded),
                "care_rows": len(rows),
            }
        )

    report = {
        "schema": "tc-fr-output-split-v1",
        "source": str(args.input.resolve()),
        "source_sha256": sha256(args.input.read_bytes()).hexdigest(),
        "input_count": input_count,
        "source_outputs": output_names,
        "groups": reports,
    }
    report_path = output_dir / "split.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
