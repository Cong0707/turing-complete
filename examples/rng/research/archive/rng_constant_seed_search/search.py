"""Low-memory search for an RNG state encoding with the seed always present.

This research-only program never imports the save writer and never touches the
live Turing Complete save.  Matrices are over GF(2); bit ``j`` in row ``i``
means that output ``i`` depends on input ``j``.

For the natural xorshift state ``x`` and the constant level input ``s`` use

    q = T (x xor s)

so that the physical Delay Bits may start at zero.  With ``R = T^-1``:

    q_next = B q xor D s,  B = T A R,  D = T (A + I)
    x_next = R q_next xor s

The feedback rows are masks over the 64 primary leaves ``(q, s)``.  The
decoder rows are masks over the 64 leaves ``(q_next, s)``.  Both fixed matrices
can therefore be synthesized and checked independently.  Their cascade emits
the first required value on tick zero and needs 65 cycles, but its static delay
depends on the arrival depths of the selected feedback nodes.  The verifier
also records the equivalent direct output matrix over ``(q, s)``:

    x_next = A R q xor A s

which is useful for proving that a globally depth-two implementation is
impossible for every T: several fixed ``A s`` row supports exceed four.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import random
import time
from typing import Iterable, Sequence


N = 32
MASK32 = (1 << N) - 1
IDENTITY = tuple(1 << i for i in range(N))
XOR_GATE_COST = 3
XOR_DELAY = 2
DELAY_BIT_GATE_COST = 5
DELAY_BIT_DELAY = 4
CYCLES = 65
REFERENCE_ENERGY = 256_014


def xorshift32(value: int) -> int:
    value &= MASK32
    value ^= value >> 13
    value &= MASK32
    value ^= (value << 17) & MASK32
    value &= MASK32
    value ^= value >> 5
    return value & MASK32


def apply_matrix(rows: Sequence[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << i for i, row in enumerate(rows))


def matrix_from_function(function) -> tuple[int, ...]:
    rows = [0] * N
    for source in range(N):
        output = function(1 << source)
        for target in range(N):
            if output >> target & 1:
                rows[target] |= 1 << source
    return tuple(rows)


A = matrix_from_function(xorshift32)
A_PLUS_I = tuple(row ^ (1 << i) for i, row in enumerate(A))


def matrix_multiply(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    result: list[int] = []
    for row in left:
        value = 0
        remaining = row
        while remaining:
            bit = remaining & -remaining
            value ^= right[bit.bit_length() - 1]
            remaining ^= bit
        result.append(value)
    return tuple(result)


def matrix_inverse(rows: Sequence[int]) -> tuple[int, ...]:
    work = list(rows)
    inverse = list(IDENTITY)
    for column in range(N):
        try:
            pivot = next(i for i in range(column, N) if work[i] >> column & 1)
        except StopIteration as exc:
            raise ValueError("matrix is singular") from exc
        work[column], work[pivot] = work[pivot], work[column]
        inverse[column], inverse[pivot] = inverse[pivot], inverse[column]
        for row in range(N):
            if row != column and work[row] >> column & 1:
                work[row] ^= work[column]
                inverse[row] ^= inverse[column]
    return tuple(inverse)


def right_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(lambda value: value ^ (value >> distance))


# The deployed 396-gate candidate's encoding is a useful deterministic start.
FIXED_T = matrix_multiply(right_shear(17), right_shear(13))
SINGLE_SHEAR_T = right_shear(17)


@dataclass(frozen=True)
class Matrices:
    encoding: tuple[int, ...]
    decoder: tuple[int, ...]
    transition: tuple[int, ...]
    seed_injection: tuple[int, ...]

    @classmethod
    def from_encoding(cls, encoding: Sequence[int]) -> "Matrices":
        encoding = tuple(encoding)
        decoder = matrix_inverse(encoding)
        transition = matrix_multiply(matrix_multiply(encoding, A), decoder)
        seed_injection = matrix_multiply(encoding, A_PLUS_I)
        return cls(encoding, decoder, transition, seed_injection)

    def feedback_rows(self) -> tuple[int, ...]:
        return tuple(
            transition | (injection << N)
            for transition, injection in zip(self.transition, self.seed_injection)
        )

    def decoder_rows(self) -> tuple[int, ...]:
        return tuple(row | (1 << (N + i)) for i, row in enumerate(self.decoder))

    def direct_output_rows(self) -> tuple[int, ...]:
        natural_from_q = matrix_multiply(A, self.decoder)
        return tuple(row | (A[i] << N) for i, row in enumerate(natural_from_q))


def mutate(matrices: Matrices, dst: int, src: int) -> Matrices:
    """Apply one elementary encoded-state row operation, exactly and cheaply."""

    encoding = list(matrices.encoding)
    decoder = list(matrices.decoder)
    transition = list(matrices.transition)
    injection = list(matrices.seed_injection)

    encoding[dst] ^= encoding[src]

    # T' = E*T, so R' = R*E.  For row masks, right multiplication by E
    # toggles column src when column dst is present.
    dst_bit = 1 << dst
    src_bit = 1 << src
    for index, row in enumerate(decoder):
        if row & dst_bit:
            decoder[index] ^= src_bit

    # B' = E*B*E.  Perform the right multiplication before the row update.
    for index, row in enumerate(transition):
        if row & dst_bit:
            transition[index] ^= src_bit
    transition[dst] ^= transition[src]

    injection[dst] ^= injection[src]
    return Matrices(tuple(encoding), tuple(decoder), tuple(transition), tuple(injection))


@lru_cache(maxsize=262_144)
def pair_options(mask: int) -> tuple[frozenset[int], ...]:
    bits = tuple(1 << i for i in range(mask.bit_length()) if mask >> i & 1)
    if len(bits) == 3:
        return tuple(frozenset((mask ^ unit,)) for unit in bits)
    if len(bits) == 4:
        result = {
            frozenset((left, mask ^ left))
            for i, first in enumerate(bits)
            for second in bits[i + 1 :]
            for left in (first | second,)
        }
        return tuple(sorted(result, key=lambda item: tuple(sorted(item))))
    return ()


@dataclass(frozen=True)
class DepthTwoPlan:
    feasible: bool
    xor_count: int | None
    distinct_targets: int
    non_unit_targets: int
    required_pair_targets: int
    final_targets: int
    selected_pairs: tuple[int, ...]


def greedy_depth_two_plan(rows: Iterable[int]) -> DepthTwoPlan:
    targets = frozenset(rows)
    non_unit = frozenset(row for row in targets if row.bit_count() >= 2)
    if 0 in targets or any(row.bit_count() > 4 for row in targets):
        return DepthTwoPlan(False, None, len(targets), len(non_unit), 0, 0, ())
    required = {row for row in targets if row.bit_count() == 2}
    finals = {row for row in targets if row.bit_count() in (3, 4)}
    selected = set(required)

    def satisfied(row: int, pairs: set[int]) -> bool:
        return any(option <= pairs for option in pair_options(row))

    while True:
        unmet = [row for row in finals if not satisfied(row, selected)]
        if not unmet:
            break
        actions = {
            option - selected
            for row in unmet
            for option in pair_options(row)
            if option - selected
        }
        if not actions:
            raise AssertionError("depth-two row has no pair decomposition")

        def key(action: frozenset[int]):
            gain = sum(satisfied(row, selected | set(action)) for row in unmet)
            return (gain / len(action), gain, -len(action), tuple(-x for x in sorted(action)))

        selected.update(max(actions, key=key))

    changed = True
    while changed:
        changed = False
        for pair in sorted(selected - required, reverse=True):
            candidate = selected - {pair}
            if all(satisfied(row, candidate) for row in finals):
                selected = candidate
                changed = True

    return DepthTwoPlan(
        True,
        len(selected) + len(finals),
        len(targets),
        len(non_unit),
        len(required),
        len(finals),
        tuple(sorted(selected)),
    )


def exact_depth_two_plan(rows: Iterable[int]) -> DepthTwoPlan:
    """Return an exact pair-cover plan; invoke only for a final candidate."""

    targets = frozenset(rows)
    greedy = greedy_depth_two_plan(targets)
    if not greedy.feasible:
        return greedy
    try:
        from z3 import And, Bool, If, Or, Solver, Sum, is_true, sat, unsat
    except ImportError as exc:  # pragma: no cover - optional research dependency
        raise SystemExit("exact verification requires z3-solver") from exc

    required = frozenset(row for row in targets if row.bit_count() == 2)
    finals = frozenset(row for row in targets if row.bit_count() in (3, 4))
    options = {row: pair_options(row) for row in finals}
    candidates = required | frozenset(
        pair for row_options in options.values() for option in row_options for pair in option
    )

    def solver_for_budget(budget: int):
        variables = {pair: Bool(f"p_{pair:016x}") for pair in sorted(candidates)}
        solver = Solver()
        for pair in required:
            solver.add(variables[pair])
        for row, row_options in options.items():
            solver.add(
                Or(*(And(*(variables[pair] for pair in option)) for option in row_options))
            )
        solver.add(Sum(*(If(value, 1, 0) for value in variables.values())) <= budget)
        return solver, variables

    low = len(required)
    high = len(greedy.selected_pairs)
    best_model = None
    best_variables = None
    while low < high:
        middle = (low + high) // 2
        solver, variables = solver_for_budget(middle)
        if solver.check() == sat:
            high = middle
            best_model = solver.model()
            best_variables = variables
        else:
            low = middle + 1
    solver, variables = solver_for_budget(low)
    if solver.check() != sat:
        raise AssertionError("greedy upper bound became unsatisfiable")
    best_model = solver.model()
    best_variables = variables
    if low:
        proof, _ = solver_for_budget(low - 1)
        if proof.check() != unsat:
            raise AssertionError("optimum-minus-one was not proved unsatisfiable")
    selected = tuple(
        pair for pair, variable in sorted(best_variables.items()) if is_true(best_model.eval(variable))
    )
    return DepthTwoPlan(
        True,
        len(selected) + len(finals),
        len(targets),
        len(frozenset(row for row in targets if row.bit_count() >= 2)),
        len(required),
        len(finals),
        selected,
    )


@dataclass(frozen=True, order=True)
class SearchScore:
    quadratic_excess: int
    heavy_rows: int
    maximum_weight: int
    greedy_xor_count: int
    total_weight: int


def score(matrices: Matrices) -> SearchScore:
    rows = matrices.feedback_rows() + matrices.decoder_rows()
    weights = tuple(row.bit_count() for row in rows)
    heavy = sum(weight > 4 for weight in weights)
    excess = sum(max(0, weight - 4) ** 2 for weight in weights)
    plan = greedy_depth_two_plan(rows) if not heavy else None
    return SearchScore(
        excess,
        heavy,
        max(weights),
        plan.xor_count if plan and plan.xor_count is not None else 1_000_000,
        sum(weights),
    )


def energy(matrices: Matrices) -> int:
    candidate = score(matrices)
    if candidate.heavy_rows:
        return (
            20_000_000
            + 1_000_000 * candidate.quadratic_excess
            + 50_000 * candidate.heavy_rows
            + 2_000 * candidate.maximum_weight
            + candidate.total_weight
        )
    return 10_000 * candidate.greedy_xor_count + candidate.total_weight


def verify_identities(matrices: Matrices) -> None:
    if matrix_multiply(matrices.encoding, matrices.decoder) != IDENTITY:
        raise AssertionError("T*T^-1 != I")
    expected_b = matrix_multiply(matrix_multiply(matrices.encoding, A), matrices.decoder)
    if matrices.transition != expected_b:
        raise AssertionError("B != T*A*T^-1")
    if matrices.seed_injection != matrix_multiply(matrices.encoding, A_PLUS_I):
        raise AssertionError("D != T*(A+I)")


def verify_sequence(matrices: Matrices) -> None:
    verify_identities(matrices)
    seeds = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    rng = random.Random(20260801)
    seeds.extend(rng.getrandbits(32) for _ in range(64))
    for seed in seeds:
        q = 0
        expected = seed
        for _ in range(CYCLES):
            q_next = apply_matrix(matrices.transition, q) ^ apply_matrix(
                matrices.seed_injection, seed
            )
            visible = apply_matrix(matrices.decoder, q_next) ^ seed
            expected = xorshift32(expected)
            if visible != expected:
                raise AssertionError(
                    f"seed {seed:08x}: got {visible:08x}, expected {expected:08x}"
                )
            q = q_next


def decoder_within(matrices: Matrices, maximum_row_weight: int | None) -> bool:
    return maximum_row_weight is None or all(
        row.bit_count() <= maximum_row_weight for row in matrices.decoder
    )


def random_perturb(
    matrices: Matrices,
    rng: random.Random,
    count: int,
    decoder_max_weight: int | None,
) -> Matrices:
    accepted = 0
    attempts = 0
    while accepted < count and attempts < count * 64:
        attempts += 1
        dst = rng.randrange(N)
        src = rng.randrange(N - 1)
        src += src >= dst
        candidate = mutate(matrices, dst, src)
        if not decoder_within(candidate, decoder_max_weight):
            continue
        matrices = candidate
        accepted += 1
    return matrices


def anneal(
    *,
    seed: int,
    cycles: int,
    steps: int,
    report_every: int = 1,
    decoder_max_weight: int | None = None,
) -> tuple[Matrices, SearchScore]:
    starts = (
        Matrices.from_encoding(IDENTITY),
        Matrices.from_encoding(SINGLE_SHEAR_T),
        Matrices.from_encoding(FIXED_T),
    )
    valid_starts = tuple(item for item in starts if decoder_within(item, decoder_max_weight))
    if not valid_starts:
        raise ValueError("no built-in start satisfies the decoder row-weight limit")
    best = min(((item, score(item)) for item in valid_starts), key=lambda item: item[1])
    print(f"initial best: {best[1]}", flush=True)

    for cycle in range(cycles):
        rng = random.Random(seed + cycle)
        if cycle < len(valid_starts):
            current = valid_starts[cycle]
        elif cycle % 5:
            current = best[0]
        else:
            current = valid_starts[cycle % len(valid_starts)]
        current = random_perturb(
            current, rng, 2 + cycle % 31, decoder_max_weight
        )
        current_energy = energy(current)

        for step in range(steps):
            dst = rng.randrange(N)
            src = rng.randrange(N - 1)
            src += src >= dst
            candidate = mutate(current, dst, src)
            if not decoder_within(candidate, decoder_max_weight):
                continue
            candidate_energy = energy(candidate)
            delta = candidate_energy - current_energy
            temperature = 8_000_000 * (0.00001 ** (step / max(1, steps))) + 10
            if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                current = candidate
                current_energy = candidate_energy

            if not (step & 255):
                candidate_score = score(current)
                if candidate_score < best[1]:
                    best = (current, candidate_score)
                    print(
                        f"best cycle={cycle} step={step}: {candidate_score}",
                        flush=True,
                    )
                    if not candidate_score.heavy_rows:
                        verify_sequence(current)

        if report_every and (cycle + 1) % report_every == 0:
            print(f"cycle {cycle + 1}/{cycles}: {best[1]}", flush=True)
    return best


def matrix_hex(rows: Sequence[int], digits: int = 8) -> list[str]:
    return [f"{row:0{digits}x}" for row in rows]


def digest(matrices: Matrices) -> str:
    payload = b"".join(
        row.to_bytes(4, "little")
        for matrix in (
            matrices.encoding,
            matrices.decoder,
            matrices.transition,
            matrices.seed_injection,
        )
        for row in matrix
    )
    return hashlib.sha256(payload).hexdigest()


def make_document(matrices: Matrices, *, exact: bool, **metadata) -> dict[str, object]:
    verify_sequence(matrices)
    feedback = matrices.feedback_rows()
    decoder = matrices.decoder_rows()
    direct = matrices.direct_output_rows()
    feedback_plan = exact_depth_two_plan(feedback) if exact else greedy_depth_two_plan(feedback)
    decoder_plan = exact_depth_two_plan(decoder) if exact else greedy_depth_two_plan(decoder)
    joint_plan = exact_depth_two_plan(feedback + decoder) if exact else greedy_depth_two_plan(feedback + decoder)
    direct_joint_plan = greedy_depth_two_plan(feedback + direct)

    separate_xor = None
    if feedback_plan.xor_count is not None and decoder_plan.xor_count is not None:
        separate_xor = feedback_plan.xor_count + decoder_plan.xor_count
    gate = None if separate_xor is None else N * DELAY_BIT_GATE_COST + separate_xor * XOR_GATE_COST

    document: dict[str, object] = {
        "convention": "q=T*(x xor seed); q_next=B*q xor D*seed; output=T^-1*q_next xor seed",
        "cycles": CYCLES,
        "sha256": digest(matrices),
        "T": matrix_hex(matrices.encoding),
        "T_inverse": matrix_hex(matrices.decoder),
        "B": matrix_hex(matrices.transition),
        "D": matrix_hex(matrices.seed_injection),
        "feedback_rows_q_seed": matrix_hex(feedback, 16),
        "decoder_rows_qnext_seed": matrix_hex(decoder, 16),
        "direct_output_rows_q_seed": matrix_hex(direct, 16),
        "score": asdict(score(matrices)),
        "feedback_depth2": asdict(feedback_plan),
        "decoder_depth2": asdict(decoder_plan),
        "joint_abstract_depth2": asdict(joint_plan),
        "direct_joint_depth2": asdict(direct_joint_plan),
        "separate_xor_count": separate_xor,
        "gate_if_separate": gate,
        "delay_model": {
            "feedback_xor_layers": 2 if feedback_plan.feasible else None,
            "decoder_xor_layers_after_feedback": 2 if decoder_plan.feasible else None,
            "worst_case_cascade_delay": (
                DELAY_BIT_DELAY + 4 * XOR_DELAY
                if feedback_plan.feasible and decoder_plan.feasible
                else None
            ),
            "note": "arrival-aware resynthesis can be 10 rather than 12 only if every output is scheduled within three XOR layers from (q,seed)",
        },
        "energy_if_delay_10": None if gate is None else gate * 10 * CYCLES,
        "energy_if_delay_12": None if gate is None else gate * 12 * CYCLES,
        "reference_energy": REFERENCE_ENERGY,
        "proof_depth2_direct_impossible": {
            "A_seed_max_weight": max(row.bit_count() for row in A),
            "A_seed_rows_over_4": sum(row.bit_count() > 4 for row in A),
            "reason": "the seed half of every direct output row is fixed to A[row]",
        },
        "memory_model": "four 32-row Python integer matrices; constant-memory annealing",
    }
    document.update(metadata)
    return document


def load_encoding(path: Path) -> tuple[int, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    values = data.get("T") or data.get("encoding")
    if not isinstance(values, list) or len(values) != N:
        raise ValueError(f"{path} has no 32-row T matrix")
    return tuple(int(value, 16) if isinstance(value, str) else int(value) for value in values)


def self_test() -> None:
    if xorshift32(1) != 0x00021001 or xorshift32(0x12345678) != 0x996CC1E4:
        raise AssertionError("xorshift reference changed")
    for start in (IDENTITY, SINGLE_SHEAR_T, FIXED_T):
        matrices = Matrices.from_encoding(start)
        verify_sequence(matrices)
        for dst, src in ((0, 1), (31, 0), (7, 19)):
            changed = mutate(matrices, dst, src)
            verify_identities(changed)
            if mutate(changed, dst, src) != matrices:
                raise AssertionError("elementary mutation is not self-inverse")
    simple = greedy_depth_two_plan((0b11, 0b111, 0b1111))
    if not simple.feasible or simple.xor_count != 4:
        raise AssertionError(f"depth-two planner regression: {simple}")
    direct = Matrices.from_encoding(IDENTITY).direct_output_rows()
    if max(row.bit_count() for row in direct) != 2 * max(row.bit_count() for row in A):
        raise AssertionError("direct output convention changed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0xC057A17)
    parser.add_argument("--cycles", type=int, default=16)
    parser.add_argument("--steps", type=int, default=250_000)
    parser.add_argument("--input", type=Path, help="start from a JSON T certificate")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--exact", action="store_true")
    parser.add_argument(
        "--decoder-max-weight",
        type=int,
        help="reject mutations whose T^-1 row exceeds this weight",
    )
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("self-test: ok", flush=True)

    started = time.perf_counter()
    if args.input:
        matrices = Matrices.from_encoding(load_encoding(args.input))
        candidate_score = score(matrices)
        source = str(args.input)
    elif args.search:
        matrices, candidate_score = anneal(
            seed=args.seed,
            cycles=args.cycles,
            steps=args.steps,
            decoder_max_weight=args.decoder_max_weight,
        )
        source = "constant-memory anneal"
    else:
        matrices = Matrices.from_encoding(FIXED_T)
        candidate_score = score(matrices)
        source = "deployed encoded-state T"

    document = make_document(
        matrices,
        exact=args.exact,
        source=source,
        deterministic_seed=args.seed,
        search_cycles=args.cycles if args.search else 0,
        steps_per_cycle=args.steps if args.search else 0,
        decoder_max_weight=args.decoder_max_weight,
        elapsed_seconds=round(time.perf_counter() - started, 6),
        final_score=asdict(candidate_score),
    )
    encoded = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
