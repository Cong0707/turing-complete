"""Enumerate diverse exact S3/S4 witnesses and score their paid D4 phases.

The fixed73+high29 programme currently reuses the ordinary intermediate
signals of one 11-gate S3/S4 witness.  That is sound, but it needlessly fixes
one arbitrary phase basis.  This tool keeps the authoritative physical
Switch/Z/net-partition encoding and incrementally enumerates *structurally*
different 11-gate, D5, two-Switch S3/S4 witnesses.  For every witness it:

* independently replays all 162 correlated rows;
* computes the real recursive arrival of every component;
* records all always-driven ordinary phases available by D4;
* measures the minimum number of terminal Switch drivers needed to cover
  each of S5/S6/S7/C8 using the paid sources plus those phases.

The cover score is only a necessary/heuristic tail score.  It deliberately
does not claim that four independently coverable outputs obey the global
physical-net partition or fit the complete 18-gate tail.  Any promising
witness must still be passed to the authoritative tail SAT and production
pipeline.

This program is save-independent and never starts Turing Complete.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import time
from typing import Iterable

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHYSICAL_PATH = ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
TAIL_WORKER_PATH = HERE / "exact_tail_with_s34_free.py"
TARGET_NAMES = ("S5", "S6", "S7", "C8")
ORDINARY = {"NOT", "AND", "OR", "NAND", "NOR"}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


physical = _load_module("s34_family_physical", PHYSICAL_PATH)


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _pack(values: Iterable[bool]) -> int:
    return sum(int(value) << case for case, value in enumerate(values))


def _resolve(values: list[bool], drivens: list[bool], bus: list[int]):
    active = {values[source] for source in bus if drivens[source]}
    if len(active) > 1:
        raise ValueError("BUS conflict")
    if not active:
        return False, False
    return next(iter(active)), True


def _replay(domain, payload: dict[str, object]) -> tuple[list[int], list[int]]:
    """Return packed component values and exact arrivals after strict replay."""

    source_values = [list(column) for column in domain.columns]
    source_values.extend(([False] * domain.rows, [True] * domain.rows))
    source_arrivals = [domain.arrivals[name] for name in domain.names] + [0, 0]
    packed: list[int] = []
    arrivals = list(source_arrivals)
    per_component_rows: list[list[bool]] = [[] for _ in payload["network"]]

    for case in range(domain.rows):
        values = [column[case] for column in source_values]
        drivens = [True] * len(values)
        for index, item in enumerate(payload["network"]):
            left, _left_driven = _resolve(values, drivens, item["left_bus"])
            right, _right_driven = _resolve(values, drivens, item["right_bus"])
            kind = item["kind"]
            if kind == "NOT":
                value, driven = not left, True
            elif kind == "AND":
                value, driven = left and right, True
            elif kind == "OR":
                value, driven = left or right, True
            elif kind == "NAND":
                value, driven = not (left and right), True
            elif kind == "NOR":
                value, driven = not (left or right), True
            elif kind == "SWITCH":
                value, driven = left and right, left
            else:  # the decomposition excludes XOR
                raise ValueError(kind)
            values.append(bool(value))
            drivens.append(bool(driven))
            per_component_rows[index].append(bool(value))

        for output, target in enumerate(domain.targets[:2]):
            value, driven = _resolve(values, drivens, payload["output_buses"][output])
            expected = bool((target >> case) & 1)
            if not driven or value != expected:
                raise ValueError(f"S3/S4 replay mismatch at row {case}, output {output}")

    for item in payload["network"]:
        inputs = [*item["left_bus"], *item["right_bus"]]
        input_arrival = max((arrivals[source] for source in inputs), default=0)
        arrival = input_arrival + 1
        if arrival > int(item["depth_upper_bound"]):
            raise ValueError("decoded depth bound is smaller than real arrival")
        arrivals.append(arrival)

    for rows in per_component_rows:
        packed.append(_pack(rows))
    return packed, arrivals[len(source_arrivals) :]


@dataclass(frozen=True)
class DriverCover:
    minimum: int | None
    valid_enable_count: int
    example_enables: tuple[int, ...]


def _minimum_driver_cover(signals: tuple[int, ...], target: int, mask: int) -> DriverCover:
    """Exact minimum terminal-Switch enable cover for a fixed signal set.

    An enable is usable when at least one available data signal agrees with
    the target on the enable support.  Covering the complete mask with usable
    enables is then exactly the minimum number of terminal Switch drivers.
    Duplicate truth functions are removed before the tiny set-cover search.
    """

    unique = tuple(dict.fromkeys(signals))
    valid = tuple(
        enable
        for enable in unique
        if enable and any((enable & (data ^ target)) == 0 for data in unique)
    )
    if not valid:
        return DriverCover(None, 0, ())
    for enable in valid:
        if enable == mask:
            return DriverCover(1, len(valid), (enable,))

    by_complement: dict[int, int] = {}
    for index, enable in enumerate(valid):
        by_complement.setdefault(mask ^ enable, index)
    for left_index, left in enumerate(valid):
        missing = mask ^ left
        for right_index, right in enumerate(valid):
            if right & missing == missing:
                return DriverCover(2, len(valid), (left, right))

    # The signal universe is small (normally <40).  Pair unions make the
    # three/four-driver test deterministic and much cheaper than combinations.
    unions: dict[int, tuple[int, int]] = {}
    for left_index, left in enumerate(valid):
        for right_index in range(left_index, len(valid)):
            union = left | valid[right_index]
            unions.setdefault(union, (left_index, right_index))
    for union, pair in unions.items():
        missing = mask ^ union
        for third_index, third in enumerate(valid):
            if third & missing == missing:
                a, b = pair
                return DriverCover(3, len(valid), (valid[a], valid[b], third))
    union_items = tuple(unions.items())
    for left_union, left_pair in union_items:
        missing = mask ^ left_union
        for right_union, right_pair in union_items:
            if right_union & missing == missing:
                a, b = left_pair
                c, d = right_pair
                return DriverCover(
                    4,
                    len(valid),
                    (valid[a], valid[b], valid[c], valid[d]),
                )
    return DriverCover(None, len(valid), ())


def _structural_block(state: dict[str, object], model: list[int]) -> list[int]:
    enabled = {literal for literal in model if literal > 0}
    chosen: list[int] = []
    for slot in range(len(state["kinds"])):
        chosen.extend(literal for literal in state["kinds"][slot] if literal in enabled)
        chosen.extend(literal for literal in state["left_uses"][slot] if literal in enabled)
        chosen.extend(literal for literal in state["right_uses"][slot] if literal in enabled)
    for uses in state["output_uses"]:
        chosen.extend(literal for literal in uses if literal in enabled)
    if not chosen:
        raise AssertionError("empty structural block")
    return [-literal for literal in chosen]


def enumerate_family(args: argparse.Namespace) -> dict[str, object]:
    full_domain = physical.domain_s34567c8_leaf()
    s34_domain = physical.domain_s3456_leaf()
    # Only S3/S4 are public outputs of this synthesis problem.
    domain = physical.Domain(
        s34_domain.names,
        s34_domain.columns,
        s34_domain.targets[:2],
        s34_domain.arrivals,
        s34_domain.output_names[:2],
    )

    def truth_tables(_interface: str):
        return (
            list(domain.names),
            [list(column) for column in domain.columns],
            domain.targets,
            domain.arrivals,
        )

    physical.upstream.truth_tables = truth_tables
    build_args = argparse.Namespace(
        interface="s34_internal_phase_family",
        gate_bound=11,
        max_delay=5,
        components=9,
        switches=2,
        xors=0,
        h_arrival=4,
        c5_arrival=4,
        output_deadlines="5,5",
    )
    started = time.perf_counter()
    enc, state = physical.upstream.build(build_args)

    full_by_name = {
        name: _pack(column)
        for name, column in zip(full_domain.names, full_domain.columns, strict=True)
    }
    full_mask = (1 << full_domain.rows) - 1
    tail_targets = {
        name: full_domain.targets[full_domain.output_names.index(name)]
        for name in TARGET_NAMES
    }
    base_d4 = tuple(
        full_by_name[name]
        for name in full_domain.names
        if full_domain.arrivals[name] <= 4
    ) + (0, full_mask)

    records: list[dict[str, object]] = []
    family_seen: set[str] = set()
    exact_models = 0
    deadline = started + args.wall_seconds if args.wall_seconds else None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with Solver(name=args.solver, bootstrap_with=enc.cnf) as solver:
        while exact_models < args.max_models and (deadline is None or time.perf_counter() < deadline):
            answer = solver.solve()
            if answer is not True:
                terminal = "unsat" if answer is False else "unknown"
                break
            model = solver.get_model()
            exact_models += 1
            payload = physical.upstream.decode(build_args, state, model)
            semantic = physical.upstream.verify(payload, state)
            timing = physical.verify_timing(payload, state)
            if any(int(value) for key, value in semantic.items() if key.endswith("count")):
                raise RuntimeError(semantic)
            if timing["depth_upper_bound_violation_count"] or timing["output_deadline_violation_count"]:
                raise RuntimeError(timing)

            packed, arrivals = _replay(domain, payload)
            useful_slots = tuple(
                index
                for index, (item, arrival) in enumerate(zip(payload["network"], arrivals, strict=True))
                if item["kind"] in ORDINARY and arrival <= 4
            )

            # Replay each useful phase on the full 486-row domain.  The S3/S4
            # network only references names shared by the two domains.
            full_columns = [
                [bool((full_by_name[name] >> case) & 1) for case in range(full_domain.rows)]
                for name in domain.names
            ]
            full_columns.extend(([False] * full_domain.rows, [True] * full_domain.rows))
            full_values_by_slot: list[list[bool]] = [[] for _ in payload["network"]]
            for case in range(full_domain.rows):
                values = [column[case] for column in full_columns]
                drivens = [True] * len(values)
                for index, item in enumerate(payload["network"]):
                    left, _ = _resolve(values, drivens, item["left_bus"])
                    right, _ = _resolve(values, drivens, item["right_bus"])
                    kind = item["kind"]
                    if kind == "NOT":
                        value, driven = not left, True
                    elif kind == "AND":
                        value, driven = left and right, True
                    elif kind == "OR":
                        value, driven = left or right, True
                    elif kind == "NAND":
                        value, driven = not (left and right), True
                    elif kind == "NOR":
                        value, driven = not (left or right), True
                    elif kind == "SWITCH":
                        value, driven = left and right, left
                    else:
                        raise ValueError(kind)
                    values.append(bool(value))
                    drivens.append(bool(driven))
                    full_values_by_slot[index].append(bool(value))
            useful_truths = tuple(_pack(full_values_by_slot[index]) for index in useful_slots)
            family_key = sha256(
                b"".join(value.to_bytes(61, "little") for value in sorted(set(useful_truths)))
            ).hexdigest()

            signals = tuple(dict.fromkeys((*base_d4, *useful_truths)))
            covers = {
                name: _minimum_driver_cover(signals, target, full_mask)
                for name, target in tail_targets.items()
            }
            score = sum(cover.minimum if cover.minimum is not None else 99 for cover in covers.values())
            direct = tuple(name for name, target in tail_targets.items() if target in signals)
            record = {
                "model_index": exact_models,
                "new_phase_family": family_key not in family_seen,
                "phase_family_sha256": family_key,
                "useful_slots": useful_slots,
                "useful_phase_count": len(set(useful_truths)),
                "tail_terminal_switch_minimum": {
                    name: cover.minimum for name, cover in covers.items()
                },
                "tail_terminal_switch_score": score,
                "direct_tail_targets": direct,
                "valid_enable_count": {
                    name: cover.valid_enable_count for name, cover in covers.items()
                },
                "network": payload["network"],
                "output_buses": payload["output_buses"],
                "verification": {**semantic, **timing},
            }
            if family_key not in family_seen:
                family_seen.add(family_key)
                records.append(record)
                args.output.write_text(
                    json.dumps(
                        {
                            "schema": "s34-internal-phase-family-enumeration-v1",
                            "status": "running",
                            "exact_models": exact_models,
                            "unique_phase_families": len(records),
                            "records": sorted(
                                records,
                                key=lambda item: (
                                    item["tail_terminal_switch_score"],
                                    -item["useful_phase_count"],
                                    item["model_index"],
                                ),
                            ),
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
            solver.add_clause(_structural_block(state, model))
        else:
            terminal = "limit"

    records.sort(
        key=lambda item: (
            item["tail_terminal_switch_score"],
            -item["useful_phase_count"],
            item["model_index"],
        )
    )
    result = {
        "schema": "s34-internal-phase-family-enumeration-v1",
        "status": terminal,
        "exact_models": exact_models,
        "unique_phase_families": len(records),
        "elapsed_seconds": time.perf_counter() - started,
        "solver": args.solver,
        "limits": {"max_models": args.max_models, "wall_seconds": args.wall_seconds},
        "scope": {
            "s34_gate": 11,
            "s34_delay": 5,
            "components": 9,
            "ordinary": 7,
            "switches": 2,
            "xors": 0,
            "tail_cover_is_only_a_heuristic": True,
            "complete_high29_claimed": False,
        },
        "dependency_sha256": {
            str(PHYSICAL_PATH.relative_to(ROOT)).replace("\\", "/"): _digest(PHYSICAL_PATH),
            str(TAIL_WORKER_PATH.relative_to(ROOT)).replace("\\", "/"): _digest(TAIL_WORKER_PATH),
            str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"): _digest(Path(__file__).resolve()),
        },
        "records": records,
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-models", type=int, default=1000)
    parser.add_argument("--wall-seconds", type=float, default=600.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = enumerate_family(args)
    print(
        json.dumps(
            {
                key: result[key]
                for key in ("status", "exact_models", "unique_phase_families", "elapsed_seconds")
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
