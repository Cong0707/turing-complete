"""Low-memory layered solver for the shared-control RNG model.

The full model in ``rng_switch_cover_next/search_shared_controls.py`` charges
three gates for XOR2, eight data gates for a four-Switch XOR3, and at least
one extra gate for every selected canonical AND/NOR control.  Therefore the
same partition model with all control gates made free is an exact lower-bound
problem.  If that optimum already exceeds the requested bound, constructing
the much larger orientation/control instance is unnecessary.

This script deliberately does not read or write the game save.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
import time
from typing import Iterable


BITS = 32
MASK = (1 << BITS) - 1
XOR2_COST = 3
SWITCH_XOR3_DATA_COST = 8
MATRIX_SHA256 = "b05c6d821814fb084ee2ade6d742a4b91f9a9f749dcb313836469be43bd7e97f"


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def target_rows() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << source) for source in range(BITS))
    return tuple(
        sum(((columns[source] >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


def bit_masks(value: int) -> tuple[int, ...]:
    return tuple(1 << bit for bit in range(BITS) if value >> bit & 1)


def set_partitions(items: tuple[int, ...], block_count: int) -> Iterable[tuple[int, ...]]:
    blocks: list[list[int]] = []

    def visit(index: int) -> Iterable[tuple[int, ...]]:
        if index == len(items):
            if len(blocks) == block_count and all(1 <= len(block) <= 3 for block in blocks):
                yield tuple(sorted(sum(block) for block in blocks))
            return
        item = items[index]
        for block in blocks:
            if len(block) < 3:
                block.append(item)
                yield from visit(index + 1)
                block.pop()
        if len(blocks) < block_count:
            blocks.append([item])
            yield from visit(index + 1)
            blocks.pop()

    yield from visit(0)


@dataclass(frozen=True)
class Option:
    final_arity: int
    sources: tuple[int, ...]

    @property
    def required_forms(self) -> tuple[int, ...]:
        return tuple(source for source in self.sources if source.bit_count() > 1)


def output_options(row: int) -> tuple[Option, ...]:
    result: set[Option] = set()
    if row.bit_count() in {1, 2, 3}:
        result.add(Option(0, (row,)))
    for arity in (2, 3):
        for sources in set_partitions(bit_masks(row), arity):
            if all(source.bit_count() <= 3 for source in sources):
                result.add(Option(arity, sources))
    return tuple(sorted(result, key=lambda option: (option.final_arity, option.sources)))


def gate_cost(arity: int) -> int:
    if arity == 2:
        return XOR2_COST
    if arity == 3:
        return SWITCH_XOR3_DATA_COST
    if arity == 0:
        return 0
    raise ValueError(f"unsupported arity {arity}")


def peak_working_set_mib() -> float | None:
    """Return the Windows process peak working set without adding psutil."""

    if sys.platform != "win32":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        kernel32.K32GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(ProcessMemoryCounters),
            wintypes.DWORD,
        ]
        kernel32.K32GetProcessMemoryInfo.restype = wintypes.BOOL
        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        ok = kernel32.K32GetProcessMemoryInfo(
            kernel32.GetCurrentProcess(),
            ctypes.byref(counters),
            counters.cb,
        )
        return counters.PeakWorkingSetSize / (1024 * 1024) if ok else None
    except (AttributeError, OSError):
        return None


def solve_free_control_lower_bound(solver_name: str) -> dict[str, object]:
    try:
        from pysat.card import CardEnc, EncType
        from pysat.examples.rc2 import RC2
        from pysat.formula import IDPool, WCNF
    except ImportError as error:  # pragma: no cover
        raise SystemExit("requires python-sat") from error

    rows = target_rows()
    choices = tuple(output_options(row) for row in rows)
    forms = tuple(
        sorted(
            {
                form
                for output_choices in choices
                for option in output_choices
                for form in option.required_forms
            }
        )
    )
    pool = IDPool()
    choice_var = {
        (output, option_index): pool.id(f"y{output:02d}_o{option_index:04d}")
        for output, output_choices in enumerate(choices)
        for option_index in range(len(output_choices))
    }
    form_var = {form: pool.id(f"f_{form:08x}") for form in forms}
    formula = WCNF()

    form_users: dict[int, list[int]] = defaultdict(list)
    for output, output_choices in enumerate(choices):
        variables = [
            choice_var[output, option_index]
            for option_index in range(len(output_choices))
        ]
        exactly_one = CardEnc.equals(
            variables,
            bound=1,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
        formula.extend(exactly_one.clauses)
        for option_index, option in enumerate(output_choices):
            active = choice_var[output, option_index]
            for form in option.required_forms:
                formula.append([-active, form_var[form]])
                form_users[form].append(active)
            cost = gate_cost(option.final_arity)
            if cost:
                formula.append([-active], weight=cost)

    for form in forms:
        variable = form_var[form]
        formula.append([-variable, *form_users[form]])
        formula.append([-variable], weight=gate_cost(form.bit_count()))

    started = time.perf_counter()
    with RC2(
        formula,
        solver=solver_name,
        adapt=True,
        exhaust=True,
        incr=True,
        verbose=0,
    ) as solver:
        model = solver.compute()
        optimum = solver.cost
    elapsed = time.perf_counter() - started
    if model is None:
        raise RuntimeError("the partition selection constraints are unexpectedly UNSAT")

    positive = {literal for literal in model if literal > 0}
    selected = tuple(
        next(
            option_index
            for option_index in range(len(output_choices))
            if choice_var[output, option_index] in positive
        )
        for output, output_choices in enumerate(choices)
    )
    selected_forms = tuple(form for form in forms if form_var[form] in positive)
    outputs = []
    for output, option_index in enumerate(selected):
        option = choices[output][option_index]
        rebuilt = 0
        for source in option.sources:
            rebuilt ^= source
        if rebuilt != rows[output]:
            raise AssertionError(f"bad decomposition for output {output}")
        outputs.append(
            {
                "output": output,
                "target": f"{rows[output]:08x}",
                "option_index": option_index,
                "final_arity": option.final_arity,
                "sources": [f"{source:08x}" for source in option.sources],
            }
        )

    pair_forms = sum(form.bit_count() == 2 for form in selected_forms)
    triple_forms = sum(form.bit_count() == 3 for form in selected_forms)
    final_pair = sum(record["final_arity"] == 2 for record in outputs)
    final_triple = sum(record["final_arity"] == 3 for record in outputs)
    rebuilt_cost = 3 * (pair_forms + final_pair) + 8 * (triple_forms + final_triple)
    if rebuilt_cost != optimum:
        raise AssertionError(f"RC2 cost {optimum} != extracted cost {rebuilt_cost}")

    return {
        "optimum": optimum,
        "counts": {
            "first_xor2": pair_forms,
            "first_switch_xor3": triple_forms,
            "final_xor2": final_pair,
            "final_switch_xor3": final_triple,
            "bit_switch": 4 * (triple_forms + final_triple),
        },
        "selected_first_forms": [f"{form:08x}" for form in selected_forms],
        "outputs": outputs,
        "solver": solver_name,
        "solve_seconds": elapsed,
        "variables": pool.top,
        "hard_clauses": len(formula.hard),
        "soft_clauses": len(formula.soft),
        "peak_working_set_mib": peak_working_set_mib(),
        "universe": {
            "forms": len(forms),
            "options": sum(len(output_choices) for output_choices in choices),
        },
    }


def solve(bound: int, solver_name: str) -> dict[str, object]:
    rows = target_rows()
    matrix_hash = sha256(b"".join(row.to_bytes(4, "little") for row in rows)).hexdigest()
    if matrix_hash != MATRIX_SHA256:
        raise AssertionError("xorshift32 matrix changed")
    lower = solve_free_control_lower_bound(solver_name)
    optimum = int(lower["optimum"])
    impossible = optimum > bound
    return {
        "schema_version": 1,
        "status": "unsat-within-model" if impossible else "lower-bound-does-not-decide",
        "model": "cancellation-free depth-4 XOR2/shared-control Switch-XOR3",
        "requested_bound": bound,
        "matrix_sha256": matrix_hash,
        "cost_rules": {
            "xor2": {"gate": 3, "delay": 2},
            "bit_switch": {"gate": 2, "delay": 1},
            "switch_xor3_data": {"bit_switch_count": 4, "gate": 8},
            "canonical_control": {"gate": 1, "lower_bound_assumption": "free"},
        },
        "free_control_lower_bound": lower,
        "proof": {
            "argument": (
                "Every full-model assignment projects to the same option/form assignment. "
                "Deleting all nonnegative AND/NOR control costs leaves an RC2 optimum of "
                f"{optimum}, which is greater than the requested bound {bound}."
            ),
            "gap": optimum - bound,
            "full_control_instance_needed": not impossible,
        },
        "scope_warning": (
            "This is exact only for the cancellation-free two-level partition family; "
            "it is not a lower bound for arbitrary multilevel tristate networks."
        ),
    }


def verify_witness(payload: dict[str, object]) -> None:
    rows = target_rows()
    lower = payload["free_control_lower_bound"]
    selected = {int(value, 16) for value in lower["selected_first_forms"]}
    for form in selected:
        if form.bit_count() not in {2, 3}:
            raise AssertionError("selected form has invalid weight")
    pair_forms = sum(form.bit_count() == 2 for form in selected)
    triple_forms = sum(form.bit_count() == 3 for form in selected)
    final_pair = 0
    final_triple = 0
    for output, record in enumerate(lower["outputs"]):
        if record["output"] != output or int(record["target"], 16) != rows[output]:
            raise AssertionError("output record order/target mismatch")
        sources = tuple(int(value, 16) for value in record["sources"])
        if any(source.bit_count() > 1 and source not in selected for source in sources):
            raise AssertionError("output references an unselected first form")
        rebuilt = 0
        for source in sources:
            rebuilt ^= source
        if rebuilt != rows[output]:
            raise AssertionError("output linear form mismatch")
        final_pair += record["final_arity"] == 2
        final_triple += record["final_arity"] == 3
    cost = 3 * (pair_forms + final_pair) + 8 * (triple_forms + final_triple)
    if cost != lower["optimum"]:
        raise AssertionError("lower-bound witness cost mismatch")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=233)
    parser.add_argument("--solver", default="g4")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("shared_control_bound233.json"),
    )
    parser.add_argument("--verify", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.verify is not None:
        verify_witness(json.loads(args.verify.read_text(encoding="utf-8")))
        print(f"verified witness: {args.verify}")
        return 0
    payload = solve(args.bound, args.solver)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lower = payload["free_control_lower_bound"]
    print(
        json.dumps(
            {
                "status": payload["status"],
                "requested_bound": payload["requested_bound"],
                "free_control_lower_bound": lower["optimum"],
                "counts": lower["counts"],
                "solve_seconds": lower["solve_seconds"],
                "peak_working_set_mib": lower["peak_working_set_mib"],
            },
            indent=2,
        )
    )
    return 20 if payload["status"] == "unsat-within-model" else 0


if __name__ == "__main__":
    sys.exit(main())
