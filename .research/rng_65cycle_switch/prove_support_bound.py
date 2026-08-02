"""Prove and audit the load-label support obstruction for the 65-cycle model.

The proof is independent of Z3.  Under the exact physical semantics inherited
from ``search_word_bus_phase.py``:

* one raw q occurrence is either load-zero or one Word-Switch seed lane;
* an eligible Bit Switch may replace only a load-zero subtree with one seed;
* a depth-one XOR therefore has load support at most two;
* a depth-two XOR therefore has load support at most four;
* a final switched output is either unchanged or one seed, so also at most four.

The required first visible output is A*seed, but 15 rows of xorshift32 matrix A
have support five through seven.  Consequently no fixed depth-two B/C cover can
satisfy the 65-cycle contract, regardless of T, XOR count, or Bit-Switch budget.
"""

from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent


def load_solver():
    path = HERE / "solve_fixed_cover.py"
    spec = importlib.util.spec_from_file_location("rng65_fixed", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["rng65_fixed"] = module
    spec.loader.exec_module(module)
    return module


def scan_records(path: Path, wanted: set[int]) -> dict[str, Any]:
    counts: Counter[int] = Counter()
    structural_failures: Counter[int] = Counter()
    total = 0
    identity_checks = 0
    identity_failures = 0
    with path.open("r", encoding="utf-8-sig") as source:
        for line in source:
            if not line.strip():
                continue
            total += 1
            record = json.loads(line)
            xor_count = int(record.get("cover", {}).get("greedy_xor", -1))
            if xor_count not in wanted:
                continue
            counts[xor_count] += 1
            matrices = []
            for name in ("T", "B", "C"):
                values = tuple(int(str(value), 16) for value in record[name])
                if len(values) != 32:
                    structural_failures[xor_count] += 1
                    break
                matrices.append(values)
            else:
                T, B, C = matrices
                if any(row == 0 or row.bit_count() > 4 for row in (*B, *C)):
                    structural_failures[xor_count] += 1
                # Matrix identities are sampled for every selected record.  The
                # operation is cheap for the radius-7 corpus and prevents stale
                # sampler metrics from entering the audit count.
                identity_checks += 1
                if solver.compose(C, T) != solver.A or solver.compose(T, C) != B:
                    identity_failures += 1
    return {
        "source": str(path),
        "total_records": total,
        "selected_by_xor": {str(key): counts[key] for key in sorted(counts)},
        "structural_failure_by_xor": {
            str(key): structural_failures[key] for key in sorted(structural_failures)
        },
        "identity_checks": identity_checks,
        "identity_failures": identity_failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--xor", type=int, nargs="+", default=(61, 60, 59))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    global solver
    solver = load_solver()
    heavy = [
        {"output": index, "row": f"{row:08x}", "weight": row.bit_count()}
        for index, row in enumerate(solver.A)
        if row.bit_count() > 4
    ]
    histogram = Counter(row.bit_count() for row in solver.A)
    if len(heavy) != 15 or max(row.bit_count() for row in solver.A) != 7:
        raise AssertionError("xorshift32 support profile changed")

    costs = {}
    for xor_count in args.xor:
        maximum_switches = solver.switch_budget(xor_count)
        maximum_gate = solver.FIXED_SHELL_GATE + 3 * xor_count + 2 * maximum_switches
        costs[str(xor_count)] = {
            "fixed_and_xor_gate": solver.FIXED_SHELL_GATE + 3 * xor_count,
            "maximum_bit_switches": maximum_switches,
            "maximum_gate": maximum_gate,
            "delay": 9,
            "cycles": 65,
            "maximum_energy": maximum_gate * 9 * 65,
        }

    document: dict[str, Any] = {
        "schema": 1,
        "status": "unsat-by-support-bound",
        "scope": (
            "common U32 Word Switch plus Bit Switch replacements and a shared "
            "depth-two two-input-XOR B/C DAG, exactly as search_word_bus_phase.py"
        ),
        "required_load_labels": {"output": "A", "feedback": "T*A"},
        "proof": [
            "Every raw occurrence has load-label support at most one.",
            "A Bit Switch is selectable only when its base load label is zero and replaces it with one seed unit.",
            "Every depth-one XOR label has support at most two.",
            "Every depth-two/final XOR label has support at most four.",
            "A final Bit Switch either leaves that label unchanged or replaces a zero label with one unit.",
            "Therefore every first-tick output label has support at most four.",
            "The required A matrix has 15 rows of support greater than four, so C-load=A is impossible.",
        ],
        "A_weight_histogram": {str(key): histogram[key] for key in sorted(histogram)},
        "obstructing_A_rows": heavy,
        "costs": costs,
        "globality": (
            "The contradiction does not depend on T, B, C, the chosen pair cover, "
            "the XOR count, or the number of available Bit Switches."
        ),
        "escape_conditions": [
            "allow a load source carrying a multi-bit linear seed form",
            "allow a deeper first-tick XOR network (which increases delay)",
            "change the switch-composition semantics beyond search_word_bus_phase.py",
        ],
    }
    if args.input:
        document["corpus_audit"] = scan_records(args.input, set(args.xor))
        if document["corpus_audit"]["identity_failures"]:
            raise AssertionError("corpus contains invalid matrix identities")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": document["status"],
        "obstructing_A_rows": len(heavy),
        "maximum_A_weight": max(row.bit_count() for row in solver.A),
        "costs": costs,
        "corpus_audit": document.get("corpus_audit"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
