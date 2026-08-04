"""Exhaust the output-pair normal form for an 18-gate o2/s8 tail.

Normal form under review:

* two always-driven ordinary gates are computed before all Switches;
* each public tail output is one resolved BUS of exactly two Switch drivers;
* every Switch enable/data is a paid source or one of the two ordinary nodes;
* all Switch inputs arrive by D4, hence every public BUS arrives by D5.

The audit deliberately relaxes liveness and cross-output physical-net reuse.
Therefore UNSAT is valid for this normal form.  It is not a global o2/s8
lower bound: interleaved Switch->ordinary structures remain outside scope.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DOMAIN_WORKER = HERE / "exact_tail_with_s34_free.py"
ORDINARY = ("NOT", "AND", "OR", "NAND", "NOR")
TARGETS = ("S5", "S6", "S7", "C8")


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


domain_worker = _load_module("o2s8_normal_domain", DOMAIN_WORKER)


def apply_gate(kind: str, left: int, right: int, mask: int) -> int:
    if kind == "NOT":
        return mask ^ left
    if kind == "AND":
        return left & right
    if kind == "OR":
        return left | right
    if kind == "NAND":
        return mask ^ (left & right)
    if kind == "NOR":
        return mask ^ (left | right)
    raise ValueError(kind)


def pack(column) -> int:
    return sum(int(value) << case for case, value in enumerate(column))


def build_problem() -> dict[str, object]:
    domain = domain_worker.build_domain()
    mask = (1 << domain.rows) - 1
    functions = {
        name: pack(column) for name, column in zip(domain.names, domain.columns, strict=True)
    }
    arrivals = dict(domain.arrivals)
    functions.update({"0": 0, "1": mask})
    arrivals.update({"0": 0, "1": 0})
    base_names = tuple(name for name in functions if arrivals[name] <= 4)
    if "s34_u6" in base_names:
        raise AssertionError("D5 u6 cannot feed a D5 output Switch")
    targets = {
        name: domain.targets[domain.output_names.index(name)] for name in TARGETS
    }
    return {
        "domain": domain,
        "mask": mask,
        "functions": functions,
        "arrivals": arrivals,
        "base_names": base_names,
        "base_values": tuple(functions[name] for name in base_names),
        "targets": targets,
    }


def enumerate_one_gate(
    problem: dict[str, object], *, deadline: int
) -> dict[int, tuple[str, str, str | None, int]]:
    names = problem["base_names"]
    functions = problem["functions"]
    arrivals = problem["arrivals"]
    mask = problem["mask"]
    base_truth = {functions[name] for name in names}
    result: dict[int, tuple[str, str, str | None, int]] = {}
    for kind in ORDINARY:
        if kind == "NOT":
            for left in names:
                arrival = arrivals[left] + 1
                if arrival <= deadline:
                    truth = apply_gate(kind, functions[left], 0, mask)
                    if truth not in base_truth:
                        result.setdefault(truth, (kind, left, None, arrival))
            continue
        for left_index, left in enumerate(names):
            for right in names[left_index:]:
                arrival = max(arrivals[left], arrivals[right]) + 1
                if arrival <= deadline:
                    truth = apply_gate(
                        kind, functions[left], functions[right], mask
                    )
                    if truth not in base_truth:
                        result.setdefault(truth, (kind, left, right, arrival))
    return result


class PairSwitchOracle:
    """Fast exact predicate for a two-Switch fully-driven target BUS."""

    def __init__(self, base_values: tuple[int, ...], target: int, mask: int):
        self.base = base_values
        self.target = target
        self.mask = mask
        self.base_valid = 0
        self.base_cover_partners: list[int] = []
        for index, enable in enumerate(self.base):
            if any((enable & (data ^ target)) == 0 for data in self.base):
                self.base_valid |= 1 << index
            partners = 0
            for other, candidate in enumerate(self.base):
                if (enable | candidate) == mask:
                    partners |= 1 << other
            self.base_cover_partners.append(partners)
        self._cache: dict[int, tuple[int, bool, int]] = {}

    def info(self, value: int) -> tuple[int, bool, int]:
        if value not in self._cache:
            matches_as_data = 0
            covers_with_base = 0
            for index, base in enumerate(self.base):
                if (base & (value ^ self.target)) == 0:
                    matches_as_data |= 1 << index
                if (value | base) == self.mask:
                    covers_with_base |= 1 << index
            base_data_matches_enable = any(
                (value & (data ^ self.target)) == 0 for data in self.base
            )
            self._cache[value] = (
                matches_as_data,
                base_data_matches_enable,
                covers_with_base,
            )
        return self._cache[value]

    def accepts(self, first: int, second: int) -> bool:
        first_data, first_base_data, first_cover = self.info(first)
        second_data, second_base_data, second_cover = self.info(second)
        valid_base = self.base_valid | first_data | second_data

        remaining = valid_base
        while remaining:
            lowest = remaining & -remaining
            index = lowest.bit_length() - 1
            if self.base_cover_partners[index] & valid_base:
                return True
            remaining -= lowest

        first_valid = (
            first_base_data
            or (first & (first ^ self.target)) == 0
            or (first & (second ^ self.target)) == 0
        )
        second_valid = (
            second_base_data
            or (second & (first ^ self.target)) == 0
            or (second & (second ^ self.target)) == 0
        )
        if first_valid and first_cover & valid_base:
            return True
        if second_valid and second_cover & valid_base:
            return True
        return bool(
            first_valid
            and second_valid
            and (first | second) == self.mask
        )


def brute_pair_switch_repr(
    base_values: tuple[int, ...], first: int, second: int, target: int, mask: int
) -> bool:
    signals = (*base_values, first, second)
    for enable1 in signals:
        for data1 in signals:
            if enable1 & (data1 ^ target):
                continue
            for enable2 in signals:
                if (enable1 | enable2) != mask:
                    continue
                for data2 in signals:
                    if not (enable2 & (data2 ^ target)):
                        return True
    return False


def enumerate_dependent_pairs(
    problem: dict[str, object],
    gate1: dict[int, tuple[str, str, str | None, int]],
):
    names = problem["base_names"]
    functions = problem["functions"]
    arrivals = problem["arrivals"]
    mask = problem["mask"]
    base_truth = {functions[name] for name in names}
    for first_truth, first_formula in gate1.items():
        first_arrival = first_formula[3]
        seen: dict[int, tuple[str, str, str | None, int]] = {}
        if first_arrival + 1 <= 4:
            truth = apply_gate("NOT", first_truth, 0, mask)
            if truth not in base_truth and truth != first_truth:
                seen.setdefault(truth, ("NOT", "g1", None, first_arrival + 1))
        for kind in ("AND", "OR", "NAND", "NOR"):
            for right in (*names, "g1"):
                right_truth = first_truth if right == "g1" else functions[right]
                right_arrival = first_arrival if right == "g1" else arrivals[right]
                output_arrival = max(first_arrival, right_arrival) + 1
                if output_arrival > 4:
                    continue
                truth = apply_gate(kind, first_truth, right_truth, mask)
                if truth not in base_truth and truth != first_truth:
                    seen.setdefault(
                        truth, (kind, "g1", right, output_arrival)
                    )
        for second_truth, second_formula in seen.items():
            yield first_truth, first_formula, second_truth, second_formula


def _universe_hash(records) -> str:
    hasher = sha256()
    for record in records:
        hasher.update(json.dumps(record, sort_keys=True, separators=(",", ":")).encode())
        hasher.update(b"\n")
    return hasher.hexdigest()


def audit() -> dict[str, object]:
    started = time.perf_counter()
    problem = build_problem()
    base = problem["base_values"]
    oracles = {
        name: PairSwitchOracle(base, target, problem["mask"])
        for name, target in problem["targets"].items()
    }
    one_d4 = enumerate_one_gate(problem, deadline=4)
    independent_counts = {name: 0 for name in TARGETS}
    independent_score = {score: 0 for score in range(len(TARGETS) + 1)}
    independent_pairs = 0
    independent_hasher = sha256()
    truths = tuple(one_d4)
    for first_index, first in enumerate(truths):
        for second in truths[first_index:]:
            independent_pairs += 1
            accepted = tuple(
                name for name, oracle in oracles.items() if oracle.accepts(first, second)
            )
            independent_score[len(accepted)] += 1
            for name in accepted:
                independent_counts[name] += 1
            independent_hasher.update(first.to_bytes(61, "little"))
            independent_hasher.update(second.to_bytes(61, "little"))

    gate1 = enumerate_one_gate(problem, deadline=3)
    dependent_counts = {name: 0 for name in TARGETS}
    dependent_score = {score: 0 for score in range(len(TARGETS) + 1)}
    dependent_pairs = 0
    dependent_hasher = sha256()
    for first, first_formula, second, second_formula in enumerate_dependent_pairs(
        problem, gate1
    ):
        dependent_pairs += 1
        accepted = tuple(
            name for name, oracle in oracles.items() if oracle.accepts(first, second)
        )
        dependent_score[len(accepted)] += 1
        for name in accepted:
            dependent_counts[name] += 1
        dependent_hasher.update(first.to_bytes(61, "little"))
        dependent_hasher.update(second.to_bytes(61, "little"))
        dependent_hasher.update(
            json.dumps(
                (first_formula, second_formula), separators=(",", ":")
            ).encode()
        )

    success = any(independent_counts.values()) or any(dependent_counts.values())
    payload = {
        "schema": "s34-free-o2s8-output-pair-normal-form-audit-v1",
        "status": "sat" if success else "unsat_within_normal_form",
        "global_o2s8_lower_bound_proved": False,
        "scope": {
            "ordinary_components": 2,
            "switch_components": 8,
            "ordinary_nodes_precede_all_switches": True,
            "exactly_two_switch_drivers_per_public_output": True,
            "switch_inputs_arrive_by": 4,
            "public_output_deadline": 5,
            "interleaved_switch_to_ordinary_topologies_in_scope": False,
            "cross_output_physical_partition_relaxed": True,
            "component_liveness_relaxed": True,
        },
        "domain": {
            "rows": problem["domain"].rows,
            "base_source_count": len(problem["base_names"]),
            "base_sources": problem["base_names"],
            "targets": TARGETS,
        },
        "independent": {
            "unique_one_gate_functions_d4": len(one_d4),
            "unordered_function_pairs": independent_pairs,
            "pair_stream_sha256": independent_hasher.hexdigest(),
            "representable_pair_count_by_target": independent_counts,
            "representable_target_count_histogram": independent_score,
        },
        "dependent_chain": {
            "unique_first_gate_functions_d3": len(gate1),
            "topological_function_pairs": dependent_pairs,
            "pair_stream_sha256": dependent_hasher.hexdigest(),
            "representable_pair_count_by_target": dependent_counts,
            "representable_target_count_histogram": dependent_score,
        },
        "dependency_sha256": {
            str(DOMAIN_WORKER.relative_to(ROOT)).replace("\\", "/"): digest(
                DOMAIN_WORKER
            ),
            str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"): digest(
                Path(__file__).resolve()
            ),
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = audit()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded.encode("utf-8"))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "independent": payload["independent"],
                "dependent_chain": payload["dependent_chain"],
                "output": str(args.output),
                "sha256": digest(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
