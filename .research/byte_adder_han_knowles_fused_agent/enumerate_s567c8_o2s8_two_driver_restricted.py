"""Enumerate a restricted D5 S5/S6/S7/C8 cost-18 family.

The authoritative paid-source truth domain comes from
``byte_adder_phase_shortcut_restart/physical_exact.py``.  This worker studies
only the following topology:

* two ordinary unit-cost gates, both before all Switches;
* ordinary kinds NOT/AND/OR/NAND/NOR, with single-source Boolean inputs;
* the second ordinary gate may consume the first ordinary gate;
* eight Switches, exactly two private Switch drivers per final output BUS;
* every Switch enable and data port is one paid source or ordinary output;
* ordinary outputs arrive by 4 and Switch outputs arrive by the D5 deadline 5.

The search is a functional quotient.  For each truth table it retains the
earliest arrival, because a slower duplicate never adds capability to this
single-source topology.  Likewise, a second ordinary output equal to an
already available source is omitted: it adds neither a new Boolean function
nor an earlier arrival.  Ordinary deadness is deliberately relaxed, so an
UNSAT result here also covers the stricter live-component version of this
topology.

This script is save-independent and game-independent.  It does not import the
game runtime or read/write a Turing Complete save.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import sys
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHYSICAL_EXACT = (
    ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
)
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")
OUTPUT_NAMES = ("S5", "S6", "S7", "C8")
DEFAULT_OUTPUT = HERE / "s567c8_o2s8_two_driver_restricted_result.json"


def load_physical_exact():
    spec = importlib.util.spec_from_file_location(
        "han_tail_restricted_physical_exact", PHYSICAL_EXACT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(PHYSICAL_EXACT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


physical_exact = load_physical_exact()


@dataclass(frozen=True)
class Source:
    name: str
    mask: int
    arrival: int


@dataclass(frozen=True)
class Candidate:
    arrival: int
    witness: tuple[str, str, str | None]


def mask_sha256(mask: int, rows: int) -> str:
    width = (rows + 7) // 8
    return sha256(mask.to_bytes(width, "little")).hexdigest()


def apply_gate(kind: str, left: int, right: int | None, all_mask: int) -> int:
    if kind == "NOT":
        return all_mask ^ left
    if right is None:
        raise AssertionError(kind)
    if kind == "AND":
        return left & right
    if kind == "OR":
        return left | right
    if kind == "NAND":
        return all_mask ^ (left & right)
    if kind == "NOR":
        return all_mask ^ (left | right)
    raise AssertionError(kind)


def enumerate_ordinary(
    sources: Sequence[Source],
    all_mask: int,
    *,
    minimize_arrival: bool,
    include_equal_binary_inputs: bool = False,
) -> dict[int, Candidate]:
    """Return one-gate truth functions and a deterministic arrival witness."""

    result: dict[int, Candidate] = {}

    def record(mask: int, candidate: Candidate) -> None:
        previous = result.get(mask)
        if previous is None:
            result[mask] = candidate
        elif minimize_arrival and (
            candidate.arrival,
            candidate.witness,
        ) < (
            previous.arrival,
            previous.witness,
        ):
            result[mask] = candidate

    # This order intentionally also reproduces the old first-witness count
    # when minimize_arrival=False.
    for source in sources:
        arrival = source.arrival + 1
        if arrival <= 4:
            record(
                all_mask ^ source.mask,
                Candidate(arrival, ("NOT", source.name, None)),
            )

    for left_index, left in enumerate(sources):
        right_start = left_index if include_equal_binary_inputs else left_index + 1
        for right in sources[right_start:]:
            arrival = max(left.arrival, right.arrival) + 1
            if arrival > 4:
                continue
            for kind in ORDINARY_KINDS[1:]:
                record(
                    apply_gate(kind, left.mask, right.mask, all_mask),
                    Candidate(arrival, (kind, left.name, right.name)),
                )
    return result


class TargetProfile:
    """O(1)-amortized two-Switch cover test for up to two new sources."""

    def __init__(self, target: int, base_masks: Sequence[int], all_mask: int):
        self.target = target
        self.base_masks = tuple(base_masks)
        self.base_mask_set = frozenset(base_masks)
        self.all_mask = all_mask
        self.base_feasible = 0
        for enable_index, enable in enumerate(base_masks):
            if any(self.valid_driver(enable, data) for data in base_masks):
                self.base_feasible |= 1 << enable_index
        self.base_cover_pairs = tuple(
            (1 << left_index) | (1 << right_index)
            for left_index, left in enumerate(base_masks)
            for right_index in range(left_index, len(base_masks))
            if (left | base_masks[right_index]) == all_mask
        )
        self._source_profiles: dict[int, tuple[int, int, bool, bool]] = {}
        self._base_pair_cache: dict[int, bool] = {}
        self._base_union_cache: dict[int, int] = {}

    def valid_driver(self, enable: int, data: int) -> bool:
        # A Switch is active exactly on enable=1 rows.  Its data must equal the
        # target on every active row; disabled rows are Z and impose no value.
        return (enable & (data ^ self.target)) == 0

    def source_profile(self, source: int) -> tuple[int, int, bool, bool]:
        cached = self._source_profiles.get(source)
        if cached is not None:
            return cached
        feasible_base_enables = 0
        union_base_enables = 0
        for index, base in enumerate(self.base_masks):
            if self.valid_driver(base, source):
                feasible_base_enables |= 1 << index
            if (base | source) == self.all_mask:
                union_base_enables |= 1 << index
        source_has_base_data = any(
            self.valid_driver(source, data) for data in self.base_masks
        )
        source_has_self_data = self.valid_driver(source, source)
        cached = (
            feasible_base_enables,
            union_base_enables,
            source_has_base_data,
            source_has_self_data,
        )
        self._source_profiles[source] = cached
        return cached

    def base_pair_covers(self, feasible: int) -> bool:
        cached = self._base_pair_cache.get(feasible)
        if cached is None:
            cached = any(
                (feasible & pair) == pair for pair in self.base_cover_pairs
            )
            self._base_pair_cache[feasible] = cached
        return cached

    def base_enable_union(self, feasible: int) -> int:
        cached = self._base_union_cache.get(feasible)
        if cached is None:
            cached = 0
            for index, source in enumerate(self.base_masks):
                if feasible & (1 << index):
                    cached |= source
            self._base_union_cache[feasible] = cached
        return cached

    def feasible_enable_union(self, additions: Iterable[int]) -> int:
        """Return rows coverable by any number of valid single-source drivers."""

        dynamic: list[int] = []
        for source in additions:
            if source not in self.base_mask_set and source not in dynamic:
                dynamic.append(source)
        if len(dynamic) > 2:
            raise ValueError("this profile supports at most two dynamic sources")

        feasible_base = self.base_feasible
        for source in dynamic:
            feasible_base |= self.source_profile(source)[0]
        covered = self.base_enable_union(feasible_base)
        for source in dynamic:
            _data_bits, _union_bits, base_data, self_data = self.source_profile(
                source
            )
            other_data = any(
                self.valid_driver(source, other)
                for other in dynamic
                if other != source
            )
            if base_data or self_data or other_data:
                covered |= source
        return covered

    def has_any_number_switch_cover(self, additions: Iterable[int]) -> bool:
        return self.feasible_enable_union(additions) == self.all_mask

    def has_two_switch_cover(self, additions: Iterable[int]) -> bool:
        dynamic: list[int] = []
        for source in additions:
            if source not in self.base_mask_set and source not in dynamic:
                dynamic.append(source)
        if len(dynamic) > 2:
            raise ValueError("this profile supports at most two dynamic sources")
        if not dynamic:
            return self.base_pair_covers(self.base_feasible)

        left = dynamic[0]
        left_data_bits, left_union_bits, left_base_data, left_self_data = (
            self.source_profile(left)
        )
        if len(dynamic) == 1:
            feasible_base = self.base_feasible | left_data_bits
            feasible_left = left_base_data or left_self_data
            return (
                self.base_pair_covers(feasible_base)
                or (feasible_left and bool(left_union_bits & feasible_base))
                or (feasible_left and left == self.all_mask)
            )

        right = dynamic[1]
        right_data_bits, right_union_bits, right_base_data, right_self_data = (
            self.source_profile(right)
        )
        feasible_base = self.base_feasible | left_data_bits | right_data_bits
        feasible_left = (
            left_base_data
            or left_self_data
            or self.valid_driver(left, right)
        )
        feasible_right = (
            right_base_data
            or right_self_data
            or self.valid_driver(right, left)
        )
        return (
            self.base_pair_covers(feasible_base)
            or (feasible_left and bool(left_union_bits & feasible_base))
            or (feasible_right and bool(right_union_bits & feasible_base))
            or (
                feasible_left
                and feasible_right
                and (left | right) == self.all_mask
            )
            or (feasible_left and left == self.all_mask)
            or (feasible_right and right == self.all_mask)
        )


def naive_two_switch_cover(
    base_masks: Sequence[int],
    additions: Iterable[int],
    target: int,
    all_mask: int,
) -> bool:
    """Literal driver-pair enumeration used only to audit the fast profile."""

    sources = list(base_masks)
    for source in additions:
        if source not in sources:
            sources.append(source)
    drivers = [
        (enable_index, data_index, enable)
        for enable_index, enable in enumerate(sources)
        for data_index, data in enumerate(sources)
        if (enable & (data ^ target)) == 0
    ]
    for left_index, (_le, _ld, left_enable) in enumerate(drivers):
        for _re, _rd, right_enable in drivers[left_index:]:
            if (left_enable | right_enable) == all_mask:
                return True
    return False


def naive_feasible_enable_union(
    base_masks: Sequence[int],
    additions: Iterable[int],
    target: int,
) -> int:
    """Union enables of every literal valid driver in the sampled source pool."""

    sources = list(base_masks)
    for source in additions:
        if source not in sources:
            sources.append(source)
    covered = 0
    for enable in sources:
        if any((enable & (data ^ target)) == 0 for data in sources):
            covered |= enable
    return covered


def make_sources(domain) -> tuple[list[Source], int]:
    all_mask = (1 << domain.rows) - 1
    sources = [
        Source(
            name,
            sum(int(value) << row for row, value in enumerate(column)),
            domain.arrivals[name],
        )
        for name, column in zip(domain.names, domain.columns, strict=True)
    ]
    sources.extend((Source("0", 0, 0), Source("1", all_mask, 0)))
    if len(sources) != 29 or len({source.mask for source in sources}) != 29:
        raise AssertionError("unexpected paid-source domain")
    return sources, all_mask


def count_two_node_networks(
    base_sources: Sequence[Source],
    all_mask: int,
    first: dict[int, Candidate],
    *,
    minimize_arrival: bool,
) -> int:
    base_masks = {source.mask for source in base_sources}
    count = 0
    for first_mask, first_candidate in first.items():
        second = enumerate_ordinary(
            [
                *base_sources,
                Source("O1", first_mask, first_candidate.arrival),
            ],
            all_mask,
            minimize_arrival=minimize_arrival,
        )
        count += sum(
            second_mask not in base_masks and second_mask != first_mask
            for second_mask in second
        )
    return count


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-check-samples", type=int, default=256)
    args = parser.parse_args()
    if args.self_check_samples < 1:
        raise ValueError("--self-check-samples must be positive")

    full_domain = physical_exact.domain_s34567c8_leaf()
    target_indices = tuple(
        full_domain.output_names.index(name) for name in OUTPUT_NAMES
    )
    targets = tuple(full_domain.targets[index] for index in target_indices)
    base_sources, all_mask = make_sources(full_domain)
    base_masks = tuple(source.mask for source in base_sources)
    base_mask_set = frozenset(base_masks)

    first = enumerate_ordinary(
        base_sources,
        all_mask,
        minimize_arrival=True,
    )
    # Equal binary inputs add no function or earlier arrival because paid
    # constants 0/1 are present.  Verify that quotient explicitly.
    first_with_equal_inputs = enumerate_ordinary(
        base_sources,
        all_mask,
        minimize_arrival=True,
        include_equal_binary_inputs=True,
    )
    if {
        mask: candidate.arrival
        for mask, candidate in first_with_equal_inputs.items()
    } != {
        mask: candidate.arrival for mask, candidate in first.items()
    }:
        raise AssertionError("equal-input quotient changed the candidate set")

    legacy_first = enumerate_ordinary(
        base_sources,
        all_mask,
        minimize_arrival=False,
    )
    if set(legacy_first) != set(first):
        raise AssertionError("legacy/corrected truth universes differ")
    stale_arrivals = [
        {
            "truth_sha256": mask_sha256(mask, full_domain.rows),
            "legacy_arrival": legacy_first[mask].arrival,
            "minimal_arrival": first[mask].arrival,
            "legacy_witness": legacy_first[mask].witness,
            "minimal_witness": first[mask].witness,
        }
        for mask in first
        if legacy_first[mask].arrival != first[mask].arrival
    ]

    legacy_two_count = count_two_node_networks(
        base_sources,
        all_mask,
        legacy_first,
        minimize_arrival=False,
    )

    profiles = [TargetProfile(target, base_masks, all_mask) for target in targets]
    paid_cover = {
        name: profile.has_two_switch_cover(())
        for name, profile in zip(OUTPUT_NAMES, profiles, strict=True)
    }
    paid_any_cover = {
        name: profile.has_any_number_switch_cover(())
        for name, profile in zip(OUTPUT_NAMES, profiles, strict=True)
    }
    paid_max_rows = {
        name: profile.feasible_enable_union(()).bit_count()
        for name, profile in zip(OUTPUT_NAMES, profiles, strict=True)
    }
    one_cover_counts = dict.fromkeys(OUTPUT_NAMES, 0)
    one_any_cover_counts = dict.fromkeys(OUTPUT_NAMES, 0)
    one_max_rows = dict.fromkeys(OUTPUT_NAMES, 0)
    one_joint_count = 0
    for first_mask in first:
        answers = [
            profile.has_two_switch_cover((first_mask,)) for profile in profiles
        ]
        any_answers = [
            profile.has_any_number_switch_cover((first_mask,))
            for profile in profiles
        ]
        row_counts = [
            profile.feasible_enable_union((first_mask,)).bit_count()
            for profile in profiles
        ]
        for name, answer, any_answer, row_count in zip(
            OUTPUT_NAMES, answers, any_answers, row_counts, strict=True
        ):
            one_cover_counts[name] += int(answer)
            one_any_cover_counts[name] += int(any_answer)
            one_max_rows[name] = max(one_max_rows[name], row_count)
        one_joint_count += int(all(answers))

    base_source_masks = {source.mask for source in base_sources}
    two_cover_counts = dict.fromkeys(OUTPUT_NAMES, 0)
    two_any_cover_counts = dict.fromkeys(OUTPUT_NAMES, 0)
    two_max_rows = dict.fromkeys(OUTPUT_NAMES, 0)
    two_joint_count = 0
    corrected_two_count = 0
    first_joint_witness = None

    rng = random.Random(0x535635374338)
    reservoir: list[tuple[int, int]] = []
    fixed_pairs: list[tuple[int, int]] = []
    last_pairs: list[tuple[int, int]] = []
    fixed_ordinals = {0, 1, 2, 17, 255, 1024, 8191, 65535}

    for first_mask, first_candidate in first.items():
        second = enumerate_ordinary(
            [
                *base_sources,
                Source("O1", first_mask, first_candidate.arrival),
            ],
            all_mask,
            minimize_arrival=True,
        )
        for second_mask in second:
            if second_mask in base_source_masks or second_mask == first_mask:
                continue
            ordinal = corrected_two_count
            corrected_two_count += 1
            pair = (first_mask, second_mask)
            if ordinal in fixed_ordinals:
                fixed_pairs.append(pair)
            last_pairs.append(pair)
            if len(last_pairs) > 8:
                last_pairs.pop(0)
            if len(reservoir) < args.self_check_samples:
                reservoir.append(pair)
            else:
                replacement = rng.randrange(corrected_two_count)
                if replacement < args.self_check_samples:
                    reservoir[replacement] = pair

            answers = [
                profile.has_two_switch_cover(pair) for profile in profiles
            ]
            any_answers = [
                profile.has_any_number_switch_cover(pair) for profile in profiles
            ]
            row_counts = [
                profile.feasible_enable_union(pair).bit_count()
                for profile in profiles
            ]
            for name, answer, any_answer, row_count in zip(
                OUTPUT_NAMES, answers, any_answers, row_counts, strict=True
            ):
                two_cover_counts[name] += int(answer)
                two_any_cover_counts[name] += int(any_answer)
                two_max_rows[name] = max(two_max_rows[name], row_count)
            if all(answers):
                two_joint_count += 1
                if first_joint_witness is None:
                    first_joint_witness = {
                        "first_truth_sha256": mask_sha256(
                            first_mask, full_domain.rows
                        ),
                        "second_truth_sha256": mask_sha256(
                            second_mask, full_domain.rows
                        ),
                    }

    if corrected_two_count != count_two_node_networks(
        base_sources,
        all_mask,
        first,
        minimize_arrival=True,
    ):
        raise AssertionError("corrected two-node count mismatch")

    # Compare the optimized profile to literal driver-pair enumeration on
    # fixed edge cases plus a deterministic pseudo-random reservoir.
    first_masks = list(first)
    one_samples = [
        first_masks[index]
        for index in (
            0,
            1,
            2,
            3,
            4,
            5,
            7,
            15,
            len(first_masks) // 2,
            -8,
            -5,
            -3,
            -2,
            -1,
        )
    ]
    pair_samples = []
    for pair in [*fixed_pairs, *last_pairs, *reservoir]:
        if pair not in pair_samples:
            pair_samples.append(pair)
    checked_profile_cases = 0
    profile_mismatches = 0
    any_number_profile_mismatches = 0
    sample_pools: list[tuple[int, ...]] = [(), *((mask,) for mask in one_samples)]
    sample_pools.extend(pair_samples)
    for additions in sample_pools:
        for target, profile in zip(targets, profiles, strict=True):
            fast = profile.has_two_switch_cover(additions)
            naive = naive_two_switch_cover(
                base_masks, additions, target, all_mask
            )
            fast_union = profile.feasible_enable_union(additions)
            naive_union = naive_feasible_enable_union(
                base_masks, additions, target
            )
            checked_profile_cases += 1
            profile_mismatches += int(fast != naive)
            any_number_profile_mismatches += int(fast_union != naive_union)
    if profile_mismatches or any_number_profile_mismatches:
        raise AssertionError("fast/naive Switch cover mismatch")

    if not (
        len(first) == 1008
        and legacy_two_count == 1_041_648
        and corrected_two_count == 1_041_696
        and len(stale_arrivals) == 18
    ):
        raise AssertionError("unexpected enumeration cardinality")

    arrival_distribution = {
        str(arrival): sum(
            candidate.arrival == arrival for candidate in first.values()
        )
        for arrival in range(1, 5)
    }
    source_paths = [
        Path(__file__).resolve(),
        PHYSICAL_EXACT.resolve(),
        *(path.resolve() for path in physical_exact.DEPENDENCY_PATHS),
    ]
    source_sha256 = {
        relative(path): sha256(path.read_bytes()).hexdigest()
        for path in source_paths
    }

    full_unsat = (
        not any(paid_cover.values())
        and not any(paid_any_cover.values())
        and not any(one_cover_counts.values())
        and not any(one_any_cover_counts.values())
        and not any(two_cover_counts.values())
        and not any(two_any_cover_counts.values())
        and one_joint_count == 0
        and two_joint_count == 0
    )
    payload = {
        "schema": "s567c8-o2s8-two-driver-restricted-v2",
        "status": "unsat_restricted_family" if full_unsat else "sat_or_partial_cover",
        "domain": {
            "provider": relative(PHYSICAL_EXACT),
            "name": "s34567c8_leaf",
            "rows": full_domain.rows,
            "outputs": list(OUTPUT_NAMES),
            "paid_sources": [
                {"name": source.name, "arrival": source.arrival}
                for source in base_sources
            ],
        },
        "family": {
            "cost": 18,
            "ordinary_components": 2,
            "ordinary_cost_each": 1,
            "ordinary_kinds": list(ORDINARY_KINDS),
            "ordinary_output_deadline": 4,
            "second_ordinary_may_read_first": True,
            "switches": 8,
            "switch_cost_each": 2,
            "switch_output_deadline": 5,
            "switches_per_output": 2,
            "ordinary_ports_are_single_source": True,
            "switch_enable_and_data_are_single_source": True,
            "switch_outputs_are_private_to_one_final_output_bus": True,
            "ordinary_deadness_enforced": False,
            "functional_truth_quotient": True,
        },
        "enumeration": {
            "raw_first_ordinary_operations_without_equal_binary_inputs": 1540,
            "unique_first_ordinary_truths": len(first),
            "first_ordinary_minimal_arrival_distribution": arrival_distribution,
            "legacy_first_witness_stale_arrival_count": len(stale_arrivals),
            "legacy_two_node_count": legacy_two_count,
            "corrected_two_node_count": corrected_two_count,
            "networks_added_by_minimal_arrival_fix": (
                corrected_two_count - legacy_two_count
            ),
            "legacy_arrival_examples": stale_arrivals,
        },
        "cover_results": {
            "paid_only_two_switch_cover": paid_cover,
            "paid_only_any_number_switch_cover": paid_any_cover,
            "paid_only_max_coverable_rows": paid_max_rows,
            "one_ordinary_network_count": len(first),
            "one_ordinary_target_cover_count": one_cover_counts,
            "one_ordinary_any_number_target_cover_count": (
                one_any_cover_counts
            ),
            "one_ordinary_max_coverable_rows": one_max_rows,
            "one_ordinary_joint_cover_count": one_joint_count,
            "two_ordinary_network_count": corrected_two_count,
            "two_ordinary_target_cover_count": two_cover_counts,
            "two_ordinary_any_number_target_cover_count": (
                two_any_cover_counts
            ),
            "two_ordinary_max_coverable_rows": two_max_rows,
            "two_ordinary_joint_cover_count": two_joint_count,
            "first_joint_witness": first_joint_witness,
        },
        "self_check": {
            "equal_binary_input_candidate_map_matches": True,
            "legacy_count_reproduced": legacy_two_count == 1_041_648,
            "minimal_arrival_count_recomputed": True,
            "fixed_one_ordinary_pools": len(one_samples),
            "fixed_and_reservoir_two_ordinary_pools": len(pair_samples),
            "fast_vs_naive_driver_pair_cases": checked_profile_cases,
            "fast_vs_naive_mismatch_count": profile_mismatches,
            "fast_vs_naive_any_number_mismatch_count": (
                any_number_profile_mismatches
            ),
        },
        "scope_exclusions": [
            "ordinary gate reads a resolved Switch BUS",
            "ordinary/Switch interleaving",
            "asymmetric output driver counts",
            "ordinary gate directly drives a final output",
            "multi-source ordinary or Switch input BUS",
            "XOR components",
            "more or fewer than two ordinary components",
        ],
        "conclusion": (
            "No paid-only, one-ordinary, or corrected two-ordinary source pool "
            "can realize even one of S5/S6/S7/C8 with any number of terminal "
            "single-source Switch drivers.  The exact two-driver-per-output "
            "cost-18 family is therefore UNSAT as a strict corollary."
        ),
        "source_sha256": source_sha256,
    }

    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "rows": full_domain.rows,
                "first": len(first),
                "legacy_two": legacy_two_count,
                "corrected_two": corrected_two_count,
                "target_cover_count": two_cover_counts,
                "any_number_target_cover_count": two_any_cover_counts,
                "max_coverable_rows": two_max_rows,
                "joint_cover_count": two_joint_count,
                "fast_vs_naive_mismatch_count": profile_mismatches,
                "fast_vs_naive_any_number_mismatch_count": (
                    any_number_profile_mismatches
                ),
                "output": str(args.output.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
