"""审计 Yosys/ABC 映射网表的 TC 加权门数、延迟与完整真值表。"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


CELL_RE = re.compile(
    r"\b(NOT|AND|NAND|OR|NOR|XOR|XNOR)\s+\S+\s*\(\s*"
    r"(?:\.A\(([^)]+)\),\s*)?"
    r"(?:\.B\(([^)]+)\),\s*)?"
    r"\.Y\(([^)]+)\)\s*\);",
    re.S,
)
ASSIGN_RE = re.compile(r"assign\s+([^=;]+?)\s*=\s*([^;]+);", re.S)
COST = {"NOT": 1, "AND": 1, "NAND": 1, "OR": 1, "NOR": 1, "XOR": 3, "XNOR": 3}
DELAY = {"NOT": 1, "AND": 1, "NAND": 1, "OR": 1, "NOR": 1, "XOR": 2, "XNOR": 2}


def clean(signal: str) -> str:
    return re.sub(r"\s+", "", signal)


def parse(path: Path) -> tuple[list[tuple[str, str | None, str | None, str]], dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    cells = [
        (op, clean(a) if a else None, clean(b) if b else None, clean(y))
        for op, a, b, y in CELL_RE.findall(text)
    ]
    aliases: dict[str, str] = {}
    for left, right in ASSIGN_RE.findall(text):
        left, right = clean(left), clean(right)
        if re.fullmatch(r"(?:_[0-9]+_|sum\[[0-7]\]|cout)", left) and re.fullmatch(
            r"(?:_[0-9]+_|a\[[0-7]\]|b\[[0-7]\]|cin)", right
        ):
            aliases[left] = right
    return cells, aliases


def resolve_alias(signal: str, aliases: dict[str, str]) -> str:
    seen: set[str] = set()
    while signal in aliases:
        if signal in seen:
            raise RuntimeError(f"alias cycle at {signal}")
        seen.add(signal)
        signal = aliases[signal]
    return signal


def source_patterns() -> tuple[dict[str, int], int]:
    input_names = [*(f"a[{i}]" for i in range(8)), *(f"b[{i}]" for i in range(8)), "cin"]
    rows = 1 << len(input_names)
    values: dict[str, int] = {}
    for index, name in enumerate(input_names):
        block = 1 << index
        pattern = 0
        for start in range(block, rows, 2 * block):
            pattern |= ((1 << block) - 1) << start
        values[name] = pattern
    return values, rows


def analyze(path: Path) -> dict[str, object]:
    cells, aliases = parse(path)
    values, rows = source_patterns()
    arrivals = {name: 0 for name in values}
    mask = (1 << rows) - 1
    unresolved = list(cells)
    ordered: list[tuple[str, str | None, str | None, str]] = []
    while unresolved:
        progress = False
        for cell in tuple(unresolved):
            op, a, b, y = cell
            inputs = [resolve_alias(signal, aliases) for signal in (a, b) if signal is not None]
            if not all(signal in values for signal in inputs):
                continue
            if op == "NOT":
                result = ~values[inputs[0]]
            elif op == "AND":
                result = values[inputs[0]] & values[inputs[1]]
            elif op == "NAND":
                result = ~(values[inputs[0]] & values[inputs[1]])
            elif op == "OR":
                result = values[inputs[0]] | values[inputs[1]]
            elif op == "NOR":
                result = ~(values[inputs[0]] | values[inputs[1]])
            elif op == "XOR":
                result = values[inputs[0]] ^ values[inputs[1]]
            elif op == "XNOR":
                result = ~(values[inputs[0]] ^ values[inputs[1]])
            else:  # pragma: no cover
                raise AssertionError(op)
            values[y] = result & mask
            arrivals[y] = max(arrivals[signal] for signal in inputs) + DELAY[op]
            unresolved.remove(cell)
            ordered.append(cell)
            progress = True
        if not progress:
            raise RuntimeError(f"cannot topologically resolve {len(unresolved)} cells: {unresolved[:3]}")

    output_values = {
        name: values[resolve_alias(name, aliases)]
        for name in [*(f"sum[{i}]" for i in range(8)), "cout"]
    }
    output_arrivals = {
        name: arrivals[resolve_alias(name, aliases)]
        for name in output_values
    }
    mismatches = 0
    first_mismatch = None
    for row in range(rows):
        a = row & 0xFF
        b = (row >> 8) & 0xFF
        cin = (row >> 16) & 1
        expected = a + b + cin
        actual = sum(((output_values[f"sum[{i}]"] >> row) & 1) << i for i in range(8))
        actual |= ((output_values["cout"] >> row) & 1) << 8
        if actual != expected:
            mismatches += 1
            if first_mismatch is None:
                first_mismatch = {"row": row, "a": a, "b": b, "cin": cin, "expected": expected, "actual": actual}
    counts = Counter(op for op, _, _, _ in cells)
    gate = sum(COST[op] * count for op, count in counts.items())
    delay = max(output_arrivals.values())
    return {
        "source": str(path),
        "cell_count": len(cells),
        "kind_counts": dict(sorted(counts.items())),
        "gate": gate,
        "delay": delay,
        "energy": gate * delay,
        "output_arrivals": output_arrivals,
        "truth_table_rows": rows,
        "mismatch_count": mismatches,
        "first_mismatch": first_mismatch,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("netlists", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = [analyze(path) for path in args.netlists]
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
