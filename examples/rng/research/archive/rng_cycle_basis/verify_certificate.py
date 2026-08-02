"""Verify the cycle-sensitive 61-XOR xorshift32 basis certificate.

This research tool is self-contained.  It does not import the save builder,
write a game save, or start the game.  GF(2) matrices use row form: bit j in
row i is the coefficient of input bit j in output bit i.

Architecture (phase selectors are outside the XOR count)::

    P = I + R17, P^-1 = P
    B = P A P

    load:    q <- B(P(seed)) = P A seed
    running: output <- P(q); q <- B(q)

The physical P block is time-multiplexed: it preprocesses the seed on the load
tick and decodes q on output ticks.  The registered feedback path bypasses P,
so it crosses one selector and at most two XOR2 gates in B.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable, Sequence


N = 32
MASK = (1 << N) - 1
IDENTITY = tuple(1 << bit for bit in range(N))

# Optimum non-output depth-one pair nodes for the fixed B target set.
B_EXTRA_PAIRS = frozenset(
    int(value, 16)
    for value in """
        00002001 00004002 00008004 00010008 00020010 00040020 00080040
        00100080 00200100 00400200 00420000 00840000 10008000 20010000
    """.split()
)


def xorshift32(value: int) -> int:
    value &= MASK
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    rows = [0] * N
    for source in range(N):
        output = function(1 << source)
        for target in range(N):
            if (output >> target) & 1:
                rows[target] |= 1 << source
    return tuple(rows)


def apply_matrix(rows: Sequence[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(rows))


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    """Return the row matrix for left(right(x))."""

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


def right_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(lambda value: value ^ (value >> distance))


A = matrix_from_function(xorshift32)
P = right_shear(17)
B = compose(compose(P, A), P)
T = compose(P, A)
C = P


@dataclass(frozen=True)
class Gate:
    id: str
    left: str
    right: str
    vector: str
    depth: int


@dataclass(frozen=True)
class Network:
    gates: tuple[Gate, ...]
    output_ids: tuple[str, ...]
    output_rows: tuple[int, ...]

    @property
    def gate_count(self) -> int:
        return len(self.gates)

    @property
    def depth(self) -> int:
        return max((gate.depth for gate in self.gates), default=0)


def pair_partitions(row: int) -> tuple[tuple[int, int], ...]:
    bits = tuple(bit for bit in range(N) if (row >> bit) & 1)
    if len(bits) == 3:
        return tuple((1 << lone, row ^ (1 << lone)) for lone in bits)
    if len(bits) == 4:
        a, b, c, d = bits
        return (
            ((1 << a) | (1 << b), (1 << c) | (1 << d)),
            ((1 << a) | (1 << c), (1 << b) | (1 << d)),
            ((1 << a) | (1 << d), (1 << b) | (1 << c)),
        )
    raise ValueError(f"row {row:08x} has no weight-3/4 partition")


def input_id(vector: int, prefix: str) -> str:
    if vector.bit_count() != 1:
        raise ValueError(f"{vector:08x} is not an input vector")
    return f"{prefix}{vector.bit_length() - 1:02d}"


def build_p_network() -> Network:
    gates = tuple(
        Gate(
            id=f"p{bit:02d}",
            left=f"u{bit:02d}",
            right=f"u{bit + 17:02d}",
            vector=f"{P[bit]:08x}",
            depth=1,
        )
        for bit in range(15)
    )
    outputs = tuple(f"p{bit:02d}" if bit < 15 else f"u{bit:02d}" for bit in range(N))
    return Network(gates, outputs, P)


def build_b_network() -> Network:
    required_pairs = {row for row in B if row.bit_count() == 2}
    first_layer = required_pairs | set(B_EXTRA_PAIRS)
    gates: list[Gate] = []
    ids: dict[int, str] = {1 << bit: f"x{bit:02d}" for bit in range(N)}
    for index, pair in enumerate(sorted(first_layer)):
        left = pair & -pair
        right = pair ^ left
        gate_id = f"bpair{index:02d}"
        gates.append(
            Gate(
                id=gate_id,
                left=input_id(left, "x"),
                right=input_id(right, "x"),
                vector=f"{pair:08x}",
                depth=1,
            )
        )
        ids[pair] = gate_id

    output_ids: list[str] = []
    for output, row in enumerate(B):
        if row.bit_count() == 2:
            output_ids.append(ids[row])
            continue
        partition = next(
            (
                (left, right)
                for left, right in pair_partitions(row)
                if left in ids and right in ids
            ),
            None,
        )
        if partition is None:
            raise AssertionError(f"no certified partition for B row {output}: {row:08x}")
        left, right = partition
        gate_id = f"bout{output:02d}"
        gates.append(
            Gate(
                id=gate_id,
                left=ids[left],
                right=ids[right],
                vector=f"{row:08x}",
                depth=2,
            )
        )
        ids[row] = gate_id
        output_ids.append(gate_id)
    return Network(tuple(gates), tuple(output_ids), B)


def verify_network(network: Network, input_prefix: str) -> None:
    values = {f"{input_prefix}{bit:02d}": 1 << bit for bit in range(N)}
    depths = {f"{input_prefix}{bit:02d}": 0 for bit in range(N)}
    for gate in network.gates:
        if gate.id in values:
            raise AssertionError(f"duplicate gate id {gate.id}")
        if gate.left not in values or gate.right not in values:
            raise AssertionError(f"gate {gate.id} has a forward or unknown reference")
        vector = values[gate.left] ^ values[gate.right]
        depth = max(depths[gate.left], depths[gate.right]) + 1
        if vector != int(gate.vector, 16):
            raise AssertionError(f"gate {gate.id} vector mismatch")
        if depth != gate.depth:
            raise AssertionError(f"gate {gate.id} depth mismatch")
        values[gate.id] = vector
        depths[gate.id] = depth
    actual_outputs = tuple(values[gate_id] for gate_id in network.output_ids)
    if actual_outputs != network.output_rows:
        raise AssertionError("network output rows do not match the declared matrix")


def weight_histogram(rows: Iterable[int]) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in rows:
        key = str(row.bit_count())
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items(), key=lambda item: int(item[0])))


def verify_sequence() -> None:
    for seed in (0, 1, 2, 0x12345678, 0xFFFFFFFF, 0x80000000):
        expected = seed
        # Load phase: P feeds the B input selector.
        state = apply_matrix(B, apply_matrix(P, seed))
        if state != apply_matrix(T, seed):
            raise AssertionError("load phase does not establish q=P*A*seed")
        for _ in range(65):
            expected = xorshift32(expected)
            if apply_matrix(P, state) != expected:
                raise AssertionError(f"sequence mismatch for seed {seed:08x}")
            state = apply_matrix(B, state)


def prove_b_pair_minimum(expected: int = 14) -> None:
    try:
        from z3 import And, Bool, If, Optimize, Or, Sum, is_true, sat
    except ImportError as error:  # pragma: no cover - optional proof dependency
        raise SystemExit("--prove-minimum requires z3-solver") from error

    required = {row for row in B if row.bit_count() == 2}
    finals = {row for row in B if row.bit_count() >= 3}
    variables: dict[int, object] = {}
    constraints: list[tuple[tuple[int, ...], ...]] = []
    for row in finals:
        row_options = []
        for left, right in pair_partitions(row):
            option = tuple(
                value
                for value in (left, right)
                if value.bit_count() == 2 and value not in required
            )
            row_options.append(option)
            for value in option:
                variables.setdefault(value, Bool(f"pair_{value:08x}"))
        constraints.append(tuple(row_options))

    optimizer = Optimize()
    for row_options in constraints:
        optimizer.add(
            Or(
                *(
                    And(*(variables[value] for value in option)) if option else True
                    for option in row_options
                )
            )
        )
    objective = Sum(*(If(variable, 1, 0) for variable in variables.values()))
    handle = optimizer.minimize(objective)
    if optimizer.check() != sat:
        raise AssertionError("B pair-cover instance is unexpectedly unsatisfiable")
    optimum = int(str(optimizer.lower(handle)))
    selected = {
        value
        for value, variable in variables.items()
        if is_true(optimizer.model().eval(variable))
    }
    if optimum != expected or len(selected) != optimum:
        raise AssertionError(f"expected B pair optimum {expected}, got {optimum}")
    print(f"Z3: B needs exactly {optimum} non-output pair nodes")


def matrix_hex(rows: Sequence[int]) -> list[str]:
    return [f"{row:08x}" for row in rows]


def certificate() -> dict[str, object]:
    p_network = build_p_network()
    b_network = build_b_network()
    gate_payload = {
        "P": [asdict(gate) for gate in p_network.gates],
        "B": [asdict(gate) for gate in b_network.gates],
    }
    digest_payload = json.dumps(
        {
            "A": matrix_hex(A),
            "P": matrix_hex(P),
            "T": matrix_hex(T),
            "B": matrix_hex(B),
            "gates": gate_payload,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return {
        "schema": 1,
        "convention": "row i bit j is coefficient of input j in output i over GF(2)",
        "transition": "A(x): x^=x>>13; x^=x<<17; x^=x>>5, each step U32",
        "architecture": {
            "basis": "P=I+R17=P^-1",
            "load": "q=B(P(seed))=P*A*seed",
            "running_output": "y=P*q",
            "running_feedback": "q_next=B*q",
            "phase_routing": "P input seed/q; B input P(seed)/q",
        },
        "sha256": hashlib.sha256(digest_payload).hexdigest(),
        "matrices": {
            "A": matrix_hex(A),
            "P": matrix_hex(P),
            "T=P*A": matrix_hex(T),
            "B=P*A*P": matrix_hex(B),
            "C=P": matrix_hex(C),
        },
        "metrics": {
            "xor2_total": p_network.gate_count + b_network.gate_count,
            "P_xor2": p_network.gate_count,
            "P_depth": p_network.depth,
            "B_xor2": b_network.gate_count,
            "B_depth": b_network.depth,
            "feedback_xor_depth": b_network.depth,
            "feedback_selector_depth": 1,
            "initialization_xor_depth": p_network.depth + b_network.depth,
            "A_row_weights": weight_histogram(A),
            "B_row_weights": weight_histogram(B),
        },
        "networks": {
            "P": {
                "inputs": [f"u{bit:02d}" for bit in range(N)],
                "gates": gate_payload["P"],
                "outputs": list(p_network.output_ids),
            },
            "B": {
                "inputs": [f"x{bit:02d}" for bit in range(N)],
                "gates": gate_payload["B"],
                "outputs": list(b_network.output_ids),
            },
        },
        "fixed_B_depth2_lower_bound": {
            "distinct_nonunit_outputs": 32,
            "extra_pair_nodes": 14,
            "xor2": 46,
            "scope": "fixed matrix B and depth at most two, not all similar matrices",
        },
    }


def verify() -> dict[str, object]:
    if xorshift32(1) != 0x00021001 or xorshift32(0x12345678) != 0x996CC1E4:
        raise AssertionError("xorshift reference vectors changed")
    if compose(P, P) != IDENTITY:
        raise AssertionError("P is not self-inverse")
    if compose(compose(P, A), P) != B:
        raise AssertionError("B != P*A*P")
    if compose(B, P) != T or compose(P, T) != A:
        raise AssertionError("load/output matrix identities failed")

    p_network = build_p_network()
    b_network = build_b_network()
    verify_network(p_network, "u")
    verify_network(b_network, "x")
    if (p_network.gate_count, p_network.depth) != (15, 1):
        raise AssertionError("P network metrics changed")
    if (b_network.gate_count, b_network.depth) != (46, 2):
        raise AssertionError("B network metrics changed")
    if weight_histogram(A) != {"3": 5, "4": 12, "5": 3, "6": 10, "7": 2}:
        raise AssertionError("natural A row weights changed")
    if weight_histogram(B) != {"2": 13, "3": 7, "4": 12}:
        raise AssertionError("B row weights changed")
    verify_sequence()
    result = certificate()
    if result["metrics"]["xor2_total"] != 61:  # type: ignore[index]
        raise AssertionError("total XOR count changed")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prove-minimum", action="store_true")
    parser.add_argument("--write-certificate", type=Path)
    parser.add_argument("--check-certificate", type=Path)
    args = parser.parse_args()
    result = verify()
    if args.prove_minimum:
        prove_b_pair_minimum()
    if args.write_certificate:
        args.write_certificate.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    check_path = args.check_certificate
    if check_path is None:
        sibling = Path(__file__).with_name("certificate.json")
        check_path = sibling if sibling.is_file() else None
    if check_path is not None:
        persisted = json.loads(check_path.read_text(encoding="utf-8"))
        if persisted != result:
            raise AssertionError(f"persisted certificate differs from recomputed data: {check_path}")
    metrics = result["metrics"]
    print(
        f"verified: {metrics['xor2_total']} XOR2 total; "  # type: ignore[index]
        f"P={metrics['P_xor2']}@d{metrics['P_depth']}; "  # type: ignore[index]
        f"B={metrics['B_xor2']}@d{metrics['B_depth']}"  # type: ignore[index]
    )
    print(f"certificate sha256: {result['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
