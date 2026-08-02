"""Depth bounds for the constant-seed RNG construction with T = I.

Research only.  This module does not import the save writer, touch a live
schematic, or start the game.  It builds the 64-input linear targets

    F = A*q xor (A+I)*s
    Y = A*q xor A*s

and checks two certificates:

* q-to-target XOR depth at most two is impossible;
* q-to-target XOR depth at most three needs at least 80 XOR2 gates.

It also emits a deliberately simple 294-XOR constructive upper bound whose
q-to-target depth is three.  The upper bound is not intended as a layout.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import random
from typing import Iterable, Sequence


BITS = 32
INPUTS = 64
MASK = (1 << BITS) - 1
EXPECTED_CYCLES = 65
PUBLIC_REFERENCE = (431, 9, 66, 256_014)


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << bit) for bit in range(BITS))
    return tuple(
        sum(((columns[source] >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


A = matrix_from_function()
Y_TARGETS = tuple(row | (row << BITS) for row in A)
F_TARGETS = tuple(
    row | ((row ^ (1 << bit)) << BITS) for bit, row in enumerate(A)
)
TARGETS = F_TARGETS + Y_TARGETS


def gf2_rank(rows: Iterable[int]) -> int:
    basis: dict[int, int] = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def apply_row(row: int, q: int, seed: int) -> int:
    value = q | (seed << BITS)
    return (row & value).bit_count() & 1


def apply_targets(rows: Sequence[int], q: int, seed: int) -> int:
    return sum(apply_row(row, q, seed) << bit for bit, row in enumerate(rows))


def vector_digest(values: Iterable[int]) -> str:
    payload = b"".join(value.to_bytes(8, "little") for value in values)
    return sha256(payload).hexdigest()


@dataclass(frozen=True)
class Signal:
    name: str
    value: int
    q_depth: int | None
    seed_depth: int | None
    total_depth: int


@dataclass(frozen=True)
class Gate:
    index: int
    name: str
    left: int
    right: int
    value: int
    q_depth: int | None
    seed_depth: int | None
    total_depth: int


class Network:
    def __init__(self) -> None:
        self.signals: list[Signal] = []
        self.gates: list[Gate] = []
        for bit in range(BITS):
            self.signals.append(Signal(f"q{bit}", 1 << bit, 0, None, 0))
        for bit in range(BITS):
            self.signals.append(
                Signal(f"s{bit}", 1 << (BITS + bit), None, 0, 0)
            )

    def add(self, name: str, left: int, right: int) -> int:
        if left == right:
            raise AssertionError(f"{name}: degenerate XOR inputs")
        first = self.signals[left]
        second = self.signals[right]

        q_parents = tuple(
            depth for depth in (first.q_depth, second.q_depth) if depth is not None
        )
        seed_parents = tuple(
            depth
            for depth in (first.seed_depth, second.seed_depth)
            if depth is not None
        )
        q_depth = max(q_parents) + 1 if q_parents else None
        seed_depth = max(seed_parents) + 1 if seed_parents else None
        total_depth = max(first.total_depth, second.total_depth) + 1
        value = first.value ^ second.value
        index = len(self.signals)
        signal = Signal(name, value, q_depth, seed_depth, total_depth)
        self.signals.append(signal)
        self.gates.append(
            Gate(
                index=index,
                name=name,
                left=left,
                right=right,
                value=value,
                q_depth=q_depth,
                seed_depth=seed_depth,
                total_depth=total_depth,
            )
        )
        return index

    def balanced(self, name: str, nodes: Sequence[int]) -> int:
        current = list(nodes)
        if not current:
            raise AssertionError(f"{name}: empty XOR tree")
        layer = 0
        while len(current) > 1:
            following: list[int] = []
            for offset in range(0, len(current) - 1, 2):
                following.append(
                    self.add(
                        f"{name}_d{layer}_{offset // 2}",
                        current[offset],
                        current[offset + 1],
                    )
                )
            if len(current) & 1:
                following.append(current[-1])
            current = following
            layer += 1
        return current[0]


def build_upper_bound() -> tuple[Network, tuple[int, ...], tuple[int, ...], dict[str, int]]:
    network = Network()
    seed = tuple(BITS + bit for bit in range(BITS))
    q = tuple(bit for bit in range(BITS))

    # A*s using the canonical three-shear 61-XOR DAG.
    stage_one = []
    for bit in range(BITS):
        if bit < 19:
            stage_one.append(
                network.add(f"seed_r13_{bit}", seed[bit], seed[bit + 13])
            )
        else:
            stage_one.append(seed[bit])

    stage_two = []
    for bit in range(BITS):
        if bit >= 17:
            stage_two.append(
                network.add(
                    f"seed_l17_{bit}", stage_one[bit], stage_one[bit - 17]
                )
            )
        else:
            stage_two.append(stage_one[bit])

    seed_a = []
    for bit in range(BITS):
        if bit < 27:
            seed_a.append(
                network.add(
                    f"seed_r5_{bit}", stage_two[bit], stage_two[bit + 5]
                )
            )
        else:
            seed_a.append(stage_two[bit])

    seed_d = tuple(
        network.add(f"seed_d_{bit}", seed_a[bit], seed[bit])
        for bit in range(BITS)
    )
    seed_gate_count = len(network.gates)
    if seed_gate_count != 93:
        raise AssertionError(f"seed A/D network changed: {seed_gate_count}")

    y_outputs: list[int] = []
    f_outputs: list[int] = []
    assembly_start = len(network.gates)
    assembly_histogram: Counter[int] = Counter()

    for bit, row in enumerate(A):
        support = tuple(index for index in range(BITS) if (row >> index) & 1)
        weight = len(support)
        assembly_histogram[weight] += 1

        if weight <= 4:
            u = network.balanced(f"q_u_{bit}", tuple(q[index] for index in support))
            y = network.add(f"Y{bit}", u, seed_a[bit])
            f = network.add(f"F{bit}", u, seed_d[bit])
        else:
            # Keep four q leaves on the shared side.  The remaining one to
            # three q leaves are combined with the two seed forms in parallel.
            u_support = support[:4]
            v_support = support[4:]
            u = network.balanced(
                f"q_u_{bit}", tuple(q[index] for index in u_support)
            )
            if len(v_support) == 1:
                vy = network.add(f"qv_y_{bit}", q[v_support[0]], seed_a[bit])
                vf = network.add(f"qv_f_{bit}", q[v_support[0]], seed_d[bit])
            elif len(v_support) == 2:
                pair = network.add(
                    f"qv_pair_{bit}", q[v_support[0]], q[v_support[1]]
                )
                vy = network.add(f"qv_y_{bit}", pair, seed_a[bit])
                vf = network.add(f"qv_f_{bit}", pair, seed_d[bit])
            elif len(v_support) == 3:
                pair = network.add(
                    f"qv_pair_{bit}", q[v_support[0]], q[v_support[1]]
                )
                y_tail = network.add(
                    f"qv_y_tail_{bit}", q[v_support[2]], seed_a[bit]
                )
                f_tail = network.add(
                    f"qv_f_tail_{bit}", q[v_support[2]], seed_d[bit]
                )
                vy = network.add(f"qv_y_{bit}", pair, y_tail)
                vf = network.add(f"qv_f_{bit}", pair, f_tail)
            else:
                raise AssertionError(f"unexpected q tail weight {len(v_support)}")
            y = network.add(f"Y{bit}", u, vy)
            f = network.add(f"F{bit}", u, vf)

        y_outputs.append(y)
        f_outputs.append(f)

    assembly_gate_count = len(network.gates) - assembly_start
    if assembly_gate_count != 201:
        raise AssertionError(f"target assembly changed: {assembly_gate_count}")
    if len(network.gates) != 294:
        raise AssertionError(f"upper-bound XOR count changed: {len(network.gates)}")

    for bit, node in enumerate(y_outputs):
        if network.signals[node].value != Y_TARGETS[bit]:
            raise AssertionError(f"Y{bit} semantics mismatch")
    for bit, node in enumerate(f_outputs):
        if network.signals[node].value != F_TARGETS[bit]:
            raise AssertionError(f"F{bit} semantics mismatch")

    output_nodes = tuple(f_outputs + y_outputs)
    if max(network.signals[node].q_depth or 0 for node in output_nodes) != 3:
        raise AssertionError("constructive q depth is not exactly three")
    if max(network.signals[node].total_depth for node in output_nodes) != 7:
        raise AssertionError("constructive total depth is not exactly seven")

    return (
        network,
        tuple(f_outputs),
        tuple(y_outputs),
        {
            "seed_gate_count": seed_gate_count,
            "assembly_gate_count": assembly_gate_count,
            "weight_3_rows": assembly_histogram[3],
            "weight_4_rows": assembly_histogram[4],
            "weight_5_rows": assembly_histogram[5],
            "weight_6_rows": assembly_histogram[6],
            "weight_7_rows": assembly_histogram[7],
        },
    )


def verify_protocol(seeds: Iterable[int]) -> int:
    checked = 0
    for seed in seeds:
        q = 0
        natural = seed
        for _ in range(EXPECTED_CYCLES):
            visible = apply_targets(Y_TARGETS, q, seed)
            following = apply_targets(F_TARGETS, q, seed)
            natural = xorshift32(natural)
            if visible != natural:
                raise AssertionError(f"visible mismatch for seed {seed:08x}")
            expected_q = natural ^ seed
            if following != expected_q:
                raise AssertionError(f"feedback mismatch for seed {seed:08x}")
            q = following
        checked += 1
    return checked


def prove_lower_bounds() -> dict[str, object]:
    row_weights = Counter(row.bit_count() for row in A)
    heavy_bits = tuple(bit for bit, row in enumerate(A) if row.bit_count() > 4)
    light_bits = tuple(bit for bit, row in enumerate(A) if row.bit_count() <= 4)
    heavy_targets = tuple(
        TARGETS[index]
        for index in range(len(TARGETS))
        if A[index % BITS].bit_count() > 4
    )
    light_targets = tuple(
        TARGETS[index]
        for index in range(len(TARGETS))
        if A[index % BITS].bit_count() <= 4
    )

    if len(heavy_bits) != 15 or len(heavy_targets) != 30:
        raise AssertionError("heavy-row count changed")
    if max(row_weights) != 7:
        raise AssertionError("A row support changed")

    # The 64 requested signals form a basis.  In particular every subset,
    # including the 30 heavy targets, is linearly independent.
    target_rank = gf2_rank(TARGETS)
    heavy_rank = gf2_rank(heavy_targets)
    if target_rank != 64 or heavy_rank != 30:
        raise AssertionError("target independence certificate failed")
    if len(set(TARGETS)) != 64 or min(row.bit_count() for row in TARGETS) <= 1:
        raise AssertionError("targets are not 64 distinct non-input forms")

    # Relax the possible parents of a heavy terminal by making every raw
    # input and every light target available regardless of topological order.
    eligible = tuple(1 << bit for bit in range(INPUTS)) + light_targets
    heavy_set = frozenset(heavy_targets)
    eligible_pair_hits = 0
    for left_index, left in enumerate(eligible):
        for right in eligible[left_index + 1 :]:
            eligible_pair_hits += (left ^ right) in heavy_set
    if eligible_pair_hits:
        raise AssertionError("two eligible parents unexpectedly make a heavy target")

    # For a fixed non-target parent n there is at most one pair (H,e) with
    # n = H xor e.  This is checked exhaustively over 30*98 fixed values.
    translations = tuple(
        heavy ^ parent for heavy in heavy_targets for parent in eligible
    )
    translation_counts = Counter(translations)
    maximum_translation_multiplicity = max(translation_counts.values())
    if maximum_translation_multiplicity != 1:
        raise AssertionError("heavy/eligible translation uniqueness changed")

    # Graph certificate: the 30 final heavy gates are edges labelled by the
    # 30 independent heavy target vectors.  Their graph is a forest.  No edge
    # joins two eligible vertices, and translation uniqueness limits every
    # non-target vertex to one eligible neighbor.  With h non-target vertices
    # there are at most h cross edges and h-1 internal forest edges, hence
    # 30 <= 2*h-1 and h >= 16.  Add the 64 distinct target-producing gates.
    non_target_lower_bound = (len(heavy_targets) + 2) // 2
    if non_target_lower_bound != 16:
        raise AssertionError("non-target lower bound changed")
    xor_lower_bound = len(TARGETS) + non_target_lower_bound
    if xor_lower_bound != 80:
        raise AssertionError("XOR lower bound changed")

    return {
        "A_row_weight_histogram": dict(sorted(row_weights.items())),
        "depth2_max_q_support": 4,
        "depth2_obstructing_A_rows": list(heavy_bits),
        "depth2_obstructing_target_count": len(heavy_targets),
        "target_count": len(TARGETS),
        "target_rank": target_rank,
        "heavy_target_rank": heavy_rank,
        "eligible_parent_count": len(eligible),
        "eligible_pair_heavy_hits": eligible_pair_hits,
        "translation_count": len(translations),
        "distinct_translation_count": len(translation_counts),
        "maximum_translation_multiplicity": maximum_translation_multiplicity,
        "translation_sha256": vector_digest(sorted(translations)),
        "non_target_gate_lower_bound": non_target_lower_bound,
        "xor_gate_lower_bound": xor_lower_bound,
    }


def make_certificate() -> dict[str, object]:
    lower = prove_lower_bounds()
    network, f_nodes, y_nodes, construction = build_upper_bound()

    generator = random.Random(20260801)
    seeds = (0, 1, 2, 0x12345678, 0xFFFFFFFF) + tuple(
        generator.getrandbits(BITS) for _ in range(64)
    )
    checked_seeds = verify_protocol(seeds)

    output_nodes = f_nodes + y_nodes
    q_depth = max(network.signals[node].q_depth or 0 for node in output_nodes)
    seed_depth = max(network.signals[node].seed_depth or 0 for node in output_nodes)
    total_depth = max(network.signals[node].total_depth for node in output_nodes)

    lower_xor = int(lower["xor_gate_lower_bound"])
    lower_gate = 32 * 5 + lower_xor * 3
    lower_delay = 4 + 3 * 2
    lower_energy = lower_gate * lower_delay * EXPECTED_CYCLES

    upper_xor = len(network.gates)
    upper_gate = 32 * 5 + upper_xor * 3
    upper_delay = max(4 + 2 * q_depth, 2 * seed_depth)
    upper_energy = upper_gate * upper_delay * EXPECTED_CYCLES

    return {
        "schema": 1,
        "construction": "constant seed, T=I",
        "equations": {
            "feedback": "F=A*q+(A+I)*s",
            "output": "Y=A*q+A*s",
        },
        "lower_bound": {
            **lower,
            "gate_lower_bound": lower_gate,
            "delay_lower_bound": lower_delay,
            "cycles": EXPECTED_CYCLES,
            "energy_lower_bound": lower_energy,
            "public_reference_energy": PUBLIC_REFERENCE[3],
            "energy_gap_above_reference": lower_energy - PUBLIC_REFERENCE[3],
        },
        "upper_bound": {
            **construction,
            "xor_gate_count": upper_xor,
            "gate": upper_gate,
            "q_xor_depth": q_depth,
            "seed_xor_depth": seed_depth,
            "total_xor_depth": total_depth,
            "predicted_delay": upper_delay,
            "cycles": EXPECTED_CYCLES,
            "predicted_energy": upper_energy,
            "feedback_output_nodes": list(f_nodes),
            "visible_output_nodes": list(y_nodes),
        },
        "verification": {
            "seed_count": checked_seeds,
            "ticks_per_seed": EXPECTED_CYCLES,
            "target_sha256": vector_digest(TARGETS),
            "gate_semantics_sha256": vector_digest(gate.value for gate in network.gates),
        },
        "gates": [asdict(gate) for gate in network.gates],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    certificate = make_certificate()
    if args.json:
        args.json.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    displayed = certificate if args.full else {
        "construction": certificate["construction"],
        "lower_bound": certificate["lower_bound"],
        "upper_bound": {
            key: value
            for key, value in certificate["upper_bound"].items()
            if not key.endswith("_nodes")
        },
        "verification": certificate["verification"],
    }
    print(json.dumps(displayed, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
