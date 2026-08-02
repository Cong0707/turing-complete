"""Exact SAT search for a depth-two XOR2/XOR3 xorshift32 network.

The circuit model is deliberately narrow and completely linear:

* level zero contains the 32 input bits;
* level one may contain any XOR2 (cost 3) or XOR3 (cost 12) of inputs;
* every output is either a level-one signal directly, or one XOR2/XOR3 of
  level-zero/level-one signals;
* shared level-one signals are charged exactly once.

All linear forms are represented as 32-bit masks.  This makes cancellation
explicit: output gate inputs may overlap, and their masks are XORed rather
than unioned.  The SAT encoding uses Tseitin variables for the monotone DNF
cover choices and a generalized sequential weighted counter for gate cost.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
import os
from pathlib import Path
import sys
import threading
import time
from typing import Iterable, Sequence

from pysat.formula import IDPool
from pysat.solvers import Solver


BITS = 32
MASK = (1 << BITS) - 1
SCALE = 3
XOR2_COST = 3
XOR3_COST = 12


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


def all_forms(bits: int = BITS) -> tuple[tuple[int, ...], dict[int, int]]:
    basis = tuple(1 << bit for bit in range(bits))
    level_one = tuple(left ^ right for left, right in combinations(basis, 2))
    level_one += tuple(
        first ^ second ^ third
        for first, second, third in combinations(basis, 3)
    )
    costs = {
        value: XOR2_COST if value.bit_count() == 2 else XOR3_COST
        for value in level_one
    }
    return tuple(sorted(basis + level_one)), costs


@dataclass(frozen=True)
class Option:
    """One output implementation after first-level forms are selected."""

    final_cost: int
    required: tuple[int, ...]
    sources: tuple[int, ...]


def enumerate_options(
    target: int,
    sources: tuple[int, ...],
    primary_cost: dict[int, int],
) -> dict[int, dict[tuple[int, ...], tuple[int, ...]]]:
    """Enumerate canonical output gates, preserving arbitrary cancellation.

    The return value maps final gate cost to
    ``required level-one forms -> complete gate source tuple``.  If several
    source tuples have identical requirements, only the lexical minimum is
    needed because they have identical global sharing behavior.
    """

    source_set = set(sources)
    by_cost: dict[int, dict[tuple[int, ...], tuple[int, ...]]] = {
        0: {},
        XOR2_COST: {},
        XOR3_COST: {},
    }

    if target in primary_cost:
        by_cost[0][(target,)] = (target,)

    for left in sources:
        right = target ^ left
        if right not in source_set or left >= right:
            continue
        gate_sources = (left, right)
        required = tuple(value for value in gate_sources if value in primary_cost)
        previous = by_cost[XOR2_COST].get(required)
        if previous is None or gate_sources < previous:
            by_cost[XOR2_COST][required] = gate_sources

    for left_index, left in enumerate(sources):
        for right in sources[left_index + 1 :]:
            third = target ^ left ^ right
            if third not in source_set or right >= third:
                continue
            gate_sources = (left, right, third)
            required = tuple(value for value in gate_sources if value in primary_cost)
            previous = by_cost[XOR3_COST].get(required)
            if previous is None or gate_sources < previous:
                by_cost[XOR3_COST][required] = gate_sources

    return by_cost


def remove_supersets(
    choices: dict[tuple[int, ...], tuple[int, ...]],
) -> dict[tuple[int, ...], tuple[int, ...]]:
    """Remove DNF terms implied by a strict subset term of equal final cost."""

    requirements = set(choices)
    kept: dict[tuple[int, ...], tuple[int, ...]] = {}
    for required, gate_sources in choices.items():
        redundant = any(
            subset != required and subset in requirements
            for size in range(len(required))
            for subset in combinations(required, size)
        )
        if not redundant:
            kept[required] = gate_sources
    return kept


def remove_xor3_dominated_by_xor2(
    xor2: dict[tuple[int, ...], tuple[int, ...]],
    xor3: dict[tuple[int, ...], tuple[int, ...]],
    primary_cost: dict[int, int],
) -> dict[tuple[int, ...], tuple[int, ...]]:
    """Apply an exact cost dominance rule between final XOR3 and XOR2 gates.

    Replacing a final XOR3 by an XOR2 saves 9.  If an XOR2 requirement set can
    be enabled from the XOR3 set for at most 9, the XOR3 term cannot be needed
    by a cost-bounded solution; forms removed from the old term can only make
    the replacement cheaper.
    """

    kept: dict[tuple[int, ...], tuple[int, ...]] = {}
    for required, gate_sources in xor3.items():
        present = set(required)
        dominated = any(
            sum(
                primary_cost[value]
                for value in alternative
                if value not in present
            )
            <= XOR3_COST - XOR2_COST
            for alternative in xor2
        )
        if not dominated:
            kept[required] = gate_sources
    return kept


def reduced_options(
    target: int,
    sources: tuple[int, ...],
    primary_cost: dict[int, int],
) -> dict[int, dict[tuple[int, ...], tuple[int, ...]]]:
    choices = enumerate_options(target, sources, primary_cost)
    choices = {cost: remove_supersets(entries) for cost, entries in choices.items()}
    choices[XOR3_COST] = remove_xor3_dominated_by_xor2(
        choices[XOR2_COST], choices[XOR3_COST], primary_cost
    )
    return {cost: entries for cost, entries in choices.items() if entries}


class ClauseSink:
    """Count clauses while streaming them directly into a native SAT solver."""

    def __init__(self, solver: Solver) -> None:
        self.solver = solver
        self.count = 0

    def add(self, clause: Iterable[int]) -> None:
        values = list(clause)
        self.solver.add_clause(values)
        self.count += 1


def encode_weighted_atmost(
    sink: ClauseSink,
    pool: IDPool,
    weighted_literals: Sequence[tuple[int, int]],
    bound: int,
) -> None:
    """Encode ``sum(weight * literal) <= bound`` with a sequential counter.

    Counter variable ``s[i,j]`` means that the first ``i`` literals have
    accumulated at least ``j`` units.  Only forward implications are needed
    for an equisatisfiable at-most encoding.  Downward monotonicity clauses
    improve propagation at modest cost because the bound here is only 67.
    """

    if bound < 0:
        sink.add(())
        return
    if not weighted_literals:
        return

    previous: list[int] | None = None
    for index, (literal, weight) in enumerate(weighted_literals):
        if weight <= 0:
            raise ValueError(f"non-positive weight: {weight}")
        if weight > bound:
            sink.add((-literal,))
            continue

        current = [pool.id(("sum", index, threshold)) for threshold in range(1, bound + 1)]

        for threshold in range(1, weight + 1):
            sink.add((-literal, current[threshold - 1]))

        if previous is not None:
            for threshold in range(1, bound + 1):
                sink.add((-previous[threshold - 1], current[threshold - 1]))

            for threshold in range(1, bound + 1):
                if threshold + weight <= bound:
                    sink.add(
                        (
                            -literal,
                            -previous[threshold - 1],
                            current[threshold + weight - 1],
                        )
                    )
                else:
                    sink.add((-literal, -previous[threshold - 1]))

        for threshold in range(1, bound):
            sink.add((-current[threshold], current[threshold - 1]))

        previous = current


def working_set_bytes() -> int:
    """Return this process's Windows working set without third-party modules."""

    if os.name != "nt":
        return 0
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
    get_memory = kernel32.K32GetProcessMemoryInfo
    get_memory.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(ProcessMemoryCounters),
        wintypes.DWORD,
    ]
    get_memory.restype = wintypes.BOOL
    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    handle = kernel32.GetCurrentProcess()
    ok = get_memory(handle, ctypes.byref(counters), counters.cb)
    return int(counters.WorkingSetSize) if ok else 0


def start_memory_watchdog(limit_mb: int) -> tuple[threading.Event, list[int]]:
    stopped = threading.Event()
    peak = [0]

    def watch() -> None:
        limit = limit_mb * 1024 * 1024
        while not stopped.wait(0.25):
            current = working_set_bytes()
            peak[0] = max(peak[0], current)
            if current > limit:
                message = (
                    f"memory_limit_exceeded working_set_mb={current / 1048576:.1f} "
                    f"limit_mb={limit_mb}\n"
                )
                os.write(2, message.encode("ascii"))
                os._exit(75)

    threading.Thread(target=watch, name="memory-watchdog", daemon=True).start()
    return stopped, peak


def solve_with_timeout(solver: Solver, timeout_s: float | None) -> bool | None:
    if timeout_s is None or timeout_s <= 0:
        return solver.solve()
    timer = threading.Timer(timeout_s, solver.interrupt)
    timer.daemon = True
    timer.start()
    try:
        return solver.solve_limited(expect_interrupt=True)
    finally:
        timer.cancel()
        solver.clear_interrupt()


def mode_name(final_cost: int) -> str:
    return {0: "direct", XOR2_COST: "xor2", XOR3_COST: "xor3"}[final_cost]


def matrix_fingerprint(rows: Sequence[int]) -> str:
    raw = b"".join(value.to_bytes(4, "little") for value in rows)
    return sha256(raw).hexdigest()


def build_and_solve(
    limit: int,
    timeout_s: float | None,
    memory_mb: int,
    solver_name: str,
    output_path: Path,
) -> int:
    if limit % SCALE:
        raise SystemExit(f"limit must be divisible by {SCALE}")

    rows = target_rows()
    sources, primary_cost = all_forms()
    pool = IDPool()
    stop_watchdog, peak = start_memory_watchdog(memory_mb)
    started = time.perf_counter()

    options_by_output: list[dict[int, dict[tuple[int, ...], tuple[int, ...]]]] = []
    selected_mode_vars: list[dict[int, int]] = []
    primary_vars: dict[int, int] = {}
    term_vars: dict[tuple[int, ...], int] = {}
    weighted_literals: list[tuple[int, int]] = []
    fixed_units = 0

    def primary_var(value: int) -> int:
        variable = primary_vars.get(value)
        if variable is None:
            variable = pool.id(("primary", value))
            primary_vars[value] = variable
        return variable

    with Solver(name=solver_name) as solver:
        sink = ClauseSink(solver)

        def term_literal(required: tuple[int, ...]) -> int | None:
            if not required:
                return None
            if len(required) == 1:
                return primary_var(required[0])
            variable = term_vars.get(required)
            if variable is None:
                variable = pool.id(("term", required))
                term_vars[required] = variable
                for value in required:
                    sink.add((-variable, primary_var(value)))
            return variable

        print("enumerating exact cancellation-aware options", flush=True)
        for output, target in enumerate(rows):
            modes = reduced_options(target, sources, primary_cost)
            options_by_output.append(modes)
            mode_vars: dict[int, int] = {}
            costs = sorted(modes)

            if len(costs) == 1:
                final_cost = costs[0]
                fixed_units += final_cost // SCALE
            else:
                selectors = []
                for final_cost in costs:
                    selector = pool.id(("mode", output, final_cost))
                    mode_vars[final_cost] = selector
                    selectors.append(selector)
                    if final_cost:
                        weighted_literals.append((selector, final_cost // SCALE))
                sink.add(selectors)
                for left, right in combinations(selectors, 2):
                    sink.add((-left, -right))

            for final_cost, choices in modes.items():
                terms: list[int] = []
                always_true = False
                for required in choices:
                    literal = term_literal(required)
                    if literal is None:
                        always_true = True
                    else:
                        terms.append(literal)
                if always_true:
                    continue
                if len(costs) == 1:
                    sink.add(terms)
                else:
                    sink.add((-mode_vars[final_cost], *terms))

            selected_mode_vars.append(mode_vars)
            counts = " ".join(
                f"{mode_name(cost)}={len(choices)}"
                for cost, choices in sorted(modes.items())
            )
            print(
                f"  y{output:02d} weight={target.bit_count()} {counts}",
                flush=True,
            )

        for value, variable in sorted(primary_vars.items()):
            weighted_literals.append((variable, primary_cost[value] // SCALE))

        variable_bound = limit // SCALE - fixed_units
        if variable_bound < 0:
            print(
                f"result=UNSAT fixed_units={fixed_units} limit_units={limit // SCALE}",
                flush=True,
            )
            return 20

        print(
            f"encoding vars_before_counter={pool.top} primary={len(primary_vars)} "
            f"terms={len(term_vars)} clauses_before_counter={sink.count} "
            f"fixed_units={fixed_units} variable_bound={variable_bound}",
            flush=True,
        )
        encode_weighted_atmost(
            sink, pool, weighted_literals, variable_bound
        )
        print(
            f"solving solver={solver_name} vars={pool.top} clauses={sink.count} "
            f"elapsed_build_s={time.perf_counter() - started:.3f}",
            flush=True,
        )

        phases = [-variable for variable in primary_vars.values()]
        for mode_vars in selected_mode_vars:
            if mode_vars:
                cheapest = min(mode_vars)
                phases.extend(
                    variable if cost == cheapest else -variable
                    for cost, variable in mode_vars.items()
                )
        solver.set_phases(phases)
        solving_started = time.perf_counter()
        result = solve_with_timeout(solver, timeout_s)
        solve_elapsed = time.perf_counter() - solving_started
        stats = solver.accum_stats()

        if result is None:
            stop_watchdog.set()
            peak[0] = max(peak[0], working_set_bytes())
            unknown_record = {
                "status": "UNKNOWN",
                "reason": "timeout-or-interrupt",
                "model": "natural-state xorshift32 exact depth<=2 XOR2/XOR3",
                "matrix_fingerprint_sha256": matrix_fingerprint(rows),
                "limit": limit,
                "encoding": {
                    "variables": pool.top,
                    "clauses": sink.count,
                    "primary_forms": len(primary_vars),
                    "dnf_terms": len(term_vars),
                    "fixed_cost_units": fixed_units,
                    "variable_bound_units": variable_bound,
                    "cost_scale": SCALE,
                },
                "solver": {
                    "name": solver_name,
                    "solve_seconds": solve_elapsed,
                    "total_seconds": time.perf_counter() - started,
                    "peak_working_set_mb": peak[0] / 1048576,
                    "stats": stats,
                },
            }
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(unknown_record, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(
                f"result=UNKNOWN reason=timeout solve_s={solve_elapsed:.3f} "
                f"stats={stats}",
                flush=True,
            )
            return 30
        if not result:
            stop_watchdog.set()
            peak[0] = max(peak[0], working_set_bytes())
            unsat_record = {
                "status": "UNSAT",
                "model": "natural-state xorshift32 exact depth<=2 XOR2/XOR3",
                "matrix_fingerprint_sha256": matrix_fingerprint(rows),
                "limit": limit,
                "proved_cost_lower_bound": limit + SCALE,
                "encoding": {
                    "variables": pool.top,
                    "clauses": sink.count,
                    "primary_forms": len(primary_vars),
                    "dnf_terms": len(term_vars),
                    "fixed_cost_units": fixed_units,
                    "variable_bound_units": variable_bound,
                    "cost_scale": SCALE,
                },
                "solver": {
                    "name": solver_name,
                    "solve_seconds": solve_elapsed,
                    "total_seconds": time.perf_counter() - started,
                    "peak_working_set_mb": peak[0] / 1048576,
                    "stats": stats,
                },
            }
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(unsat_record, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(
                f"result=UNSAT certificate={output_path} "
                f"solve_s={solve_elapsed:.3f} stats={stats}",
                flush=True,
            )
            return 20

        model = set(literal for literal in solver.get_model() if literal > 0)

    stop_watchdog.set()
    peak[0] = max(peak[0], working_set_bytes())

    enabled = {value for value, variable in primary_vars.items() if variable in model}
    output_records = []
    actually_used: set[int] = set()
    for output, modes in enumerate(options_by_output):
        mode_vars = selected_mode_vars[output]
        if not mode_vars:
            final_cost = next(iter(modes))
        else:
            chosen_modes = [cost for cost, variable in mode_vars.items() if variable in model]
            if len(chosen_modes) != 1:
                raise AssertionError(f"y{output}: selector model is not one-hot")
            final_cost = chosen_modes[0]

        possible = [
            (required, gate_sources)
            for required, gate_sources in modes[final_cost].items()
            if set(required) <= enabled
        ]
        if not possible:
            raise AssertionError(f"y{output}: selected mode has no enabled term")
        required, gate_sources = min(
            possible,
            key=lambda item: (
                sum(primary_cost[value] for value in item[0]),
                len(item[0]),
                item,
            ),
        )
        actually_used.update(required)
        output_records.append(
            {
                "output": output,
                "target": f"{rows[output]:08x}",
                "mode": mode_name(final_cost),
                "cost": final_cost,
                "required": [f"{value:08x}" for value in required],
                "sources": [f"{value:08x}" for value in gate_sources],
            }
        )

    first_records = []
    for value in sorted(actually_used):
        bits = [bit for bit in range(BITS) if value >> bit & 1]
        cost = primary_cost[value]
        first_records.append(
            {
                "form": f"{value:08x}",
                "mode": mode_name(cost),
                "cost": cost,
                "inputs": bits,
            }
        )

    total_cost = sum(record["cost"] for record in first_records)
    total_cost += sum(record["cost"] for record in output_records)
    certificate = {
        "status": "SAT",
        "model": "natural-state xorshift32 exact depth<=2 XOR2/XOR3",
        "matrix_fingerprint_sha256": matrix_fingerprint(rows),
        "limit": limit,
        "cost": total_cost,
        "gate_counts": dict(
            sorted(
                Counter(
                    record["mode"]
                    for record in first_records + output_records
                    if record["mode"] != "direct"
                ).items()
            )
        ),
        "first_level": first_records,
        "outputs": output_records,
        "solver": {
            "name": solver_name,
            "solve_seconds": solve_elapsed,
            "total_seconds": time.perf_counter() - started,
            "peak_working_set_mb": peak[0] / 1048576,
            "stats": stats,
        },
    }
    verify_certificate(certificate)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(certificate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"result=SAT cost={total_cost} first={len(first_records)} "
        f"certificate={output_path} solve_s={solve_elapsed:.3f}",
        flush=True,
    )
    return 10


def verify_certificate(certificate: dict) -> None:
    rows = target_rows()
    first = {int(record["form"], 16): record for record in certificate["first_level"]}
    cost = 0
    for value, record in first.items():
        inputs = record["inputs"]
        rebuilt = 0
        for bit in inputs:
            rebuilt ^= 1 << bit
        if rebuilt != value:
            raise AssertionError(f"first form {value:08x} has wrong inputs")
        expected_mode = "xor2" if len(inputs) == 2 else "xor3"
        expected_cost = XOR2_COST if len(inputs) == 2 else XOR3_COST
        if len(inputs) not in (2, 3):
            raise AssertionError(f"first form {value:08x} has illegal arity")
        if record["mode"] != expected_mode or record["cost"] != expected_cost:
            raise AssertionError(f"first form {value:08x} has wrong cost/mode")
        cost += expected_cost

    if len(certificate["outputs"]) != BITS:
        raise AssertionError("certificate does not contain 32 outputs")
    for output, record in enumerate(certificate["outputs"]):
        if record["output"] != output:
            raise AssertionError("outputs are not in canonical order")
        sources = [int(value, 16) for value in record["sources"]]
        rebuilt = 0
        for source in sources:
            if source.bit_count() > 1 and source not in first:
                raise AssertionError(
                    f"y{output}: source {source:08x} is not implemented"
                )
            rebuilt ^= source
        if rebuilt != rows[output]:
            raise AssertionError(
                f"y{output}: got {rebuilt:08x}, expected {rows[output]:08x}"
            )
        mode = record["mode"]
        expected_arity = {"direct": 1, "xor2": 2, "xor3": 3}[mode]
        expected_cost = {"direct": 0, "xor2": XOR2_COST, "xor3": XOR3_COST}[mode]
        if len(sources) != expected_arity or record["cost"] != expected_cost:
            raise AssertionError(f"y{output}: wrong arity/cost")
        cost += expected_cost

    if cost != certificate["cost"]:
        raise AssertionError(f"cost mismatch: rebuilt {cost}, stored {certificate['cost']}")
    if matrix_fingerprint(rows) != certificate["matrix_fingerprint_sha256"]:
        raise AssertionError("matrix fingerprint mismatch")


def verify_file(path: Path) -> int:
    certificate = json.loads(path.read_text(encoding="utf-8"))
    verify_certificate(certificate)
    print(
        f"verified=true cost={certificate['cost']} "
        f"first={len(certificate['first_level'])} outputs=32",
        flush=True,
    )
    return 0


def self_test() -> int:
    """Cross-check enumeration and the weighted counter on small instances."""

    small_sources, small_costs = all_forms(bits=5)
    source_set = set(small_sources)
    for target in range(1, 1 << 5):
        actual = enumerate_options(target, small_sources, small_costs)
        for final_cost, arity in ((XOR2_COST, 2), (XOR3_COST, 3)):
            expected: set[tuple[int, ...]] = set()
            for gate_sources in combinations(small_sources, arity):
                value = 0
                for source in gate_sources:
                    value ^= source
                if value == target:
                    expected.add(
                        tuple(source for source in gate_sources if source in small_costs)
                    )
            if set(actual[final_cost]) != expected:
                raise AssertionError(
                    f"enumeration mismatch target={target:02x} arity={arity}"
                )
        if target in small_costs and (target,) not in actual[0]:
            raise AssertionError(f"missing direct option target={target:02x}")

    weighted = ((1, 1), (2, 2), (3, 4), (4, 3), (5, 1))
    for bound in range(0, 12):
        pool = IDPool(start_from=6)
        with Solver(name="cadical195") as solver:
            sink = ClauseSink(solver)
            encode_weighted_atmost(sink, pool, weighted, bound)
            for assignment in range(1 << 5):
                assumptions = [
                    variable if assignment >> (variable - 1) & 1 else -variable
                    for variable in range(1, 6)
                ]
                expected = sum(
                    weight
                    for variable, weight in weighted
                    if assignment >> (variable - 1) & 1
                ) <= bound
                if solver.solve(assumptions=assumptions) != expected:
                    raise AssertionError(
                        f"counter mismatch bound={bound} assignment={assignment:05b}"
                    )

    if any(value not in source_set for value in small_sources):
        raise AssertionError("small source construction is inconsistent")
    print("self_test=PASS enumeration_targets=31 counter_assignments=384", flush=True)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solve", type=int, metavar="COST_LIMIT")
    parser.add_argument("--timeout-s", type=float, default=600.0)
    parser.add_argument("--memory-mb", type=int, default=700)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument(
        "--output", type=Path, default=Path(__file__).with_name("candidate.json")
    )
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()
    if args.verify is not None:
        return verify_file(args.verify)
    if args.solve is None:
        raise SystemExit("choose --self-test, --verify FILE, or --solve COST_LIMIT")
    return build_and_solve(
        args.solve,
        args.timeout_s,
        args.memory_mb,
        args.solver,
        args.output,
    )


if __name__ == "__main__":
    sys.exit(main())
