"""Exact retiming obstruction for the canonical 61-XOR xorshift32 DAG.

The model is deliberately independent of the game save writer.  A binary XOR
has delay 2, the steady-state initialization OR has delay 1, and every output
bit is fed back through one register.  Replacing an adjacent XOR->XOR chain by
one XOR3 can remove at most two delay units from a physical path.

For a Leiserson-Saxe retiming r, an edge register count changes as

    w_r(u, v) = w(u, v) + r(v) - r(u).

The r terms telescope around a directed cycle, so the register count of every
cycle is invariant.  The cycle list below is therefore a compact certificate
that five XOR3 substitutions cannot reach period 6 or period 5, irrespective
of how many *duplicated* registers the retiming has globally.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
import json


BITS = 32
MASK = (1 << BITS) - 1
XOR_DELAY = 2
OR_DELAY = 1


def xorshift32(value: int) -> int:
    value &= MASK
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def build_dag() -> tuple[dict[str, tuple[str, str]], tuple[str, ...]]:
    gates: dict[str, tuple[str, str]] = {}
    for bit in range(19):
        gates[f"a{bit}"] = (f"x{bit}", f"x{bit + 13}")

    def a(bit: int) -> str:
        return f"a{bit}" if bit < 19 else f"x{bit}"

    for bit in range(17, 32):
        gates[f"b{bit}"] = (a(bit), a(bit - 17))

    def b(bit: int) -> str:
        return f"b{bit}" if bit >= 17 else a(bit)

    for bit in range(27):
        gates[f"y{bit}"] = (b(bit), b(bit + 5))

    outputs = tuple(f"y{bit}" if bit < 27 else b(bit) for bit in range(32))
    assert len(gates) == 61
    return gates, outputs


GATES, OUTPUTS = build_dag()


@cache
def linear_form(node: str) -> int:
    if node.startswith("x"):
        return 1 << int(node[1:])
    left, right = GATES[node]
    return linear_form(left) ^ linear_form(right)


@cache
def physical_paths(node: str) -> tuple[tuple[int, tuple[str, ...]], ...]:
    """Return every structural input path as (source bit, gate chain)."""

    if node.startswith("x"):
        return ((int(node[1:]), ()),)
    result: list[tuple[int, tuple[str, ...]]] = []
    for source in GATES[node]:
        for bit, chain in physical_paths(source):
            result.append((bit, chain + (node,)))
    return tuple(result)


@dataclass(frozen=True)
class Arc:
    source: int
    target: int
    chain: tuple[str, ...]

    @property
    def delay(self) -> int:
        return OR_DELAY + XOR_DELAY * len(self.chain)

    @property
    def substitutions(self) -> frozenset[tuple[str, str]]:
        # Each pair is (child, parent).  Replacing that adjacent pair by one
        # XOR3 is the only local substitution that can shorten this path.
        return frozenset(zip(self.chain[1:], self.chain[:-1]))


ARCS: dict[tuple[int, int], tuple[Arc, ...]] = {}
_arcs: defaultdict[tuple[int, int], list[Arc]] = defaultdict(list)
for target, output in enumerate(OUTPUTS):
    for source, chain in physical_paths(output):
        _arcs[source, target].append(Arc(source, target, chain))
ARCS = {key: tuple(value) for key, value in _arcs.items()}


# Two critical self loops followed by five length-five cycles.  For every
# state transition i -> j, the certificate selects one exact structural path
# from x_i to y_j.  The seven substitution sets are pairwise disjoint.
CERTIFICATE_CYCLES = (
    (17,),
    (18,),
    (0, 12, 7, 19, 18),
    (1, 13, 25, 24, 6),
    (2, 14, 26, 8, 20),
    (3, 15, 10, 22, 21),
    (5, 17, 16, 11, 23),
)


def selected_arc(source: int, target: int) -> Arc:
    """Select the longest physical path for one certificate transition."""

    return max(ARCS[source, target], key=lambda arc: (arc.delay, arc.chain))


def matrix_rows() -> tuple[int, ...]:
    return tuple(linear_form(output) for output in OUTPUTS)


def apply_matrix(rows: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(rows))


def verify() -> dict[str, object]:
    rows = matrix_rows()
    for bit in range(BITS):
        assert apply_matrix(rows, 1 << bit) == xorshift32(1 << bit)

    consumers: defaultdict[str, list[str]] = defaultdict(list)
    for child, inputs in GATES.items():
        for parent in inputs:
            consumers[parent].append(child)
    for bit, output in enumerate(OUTPUTS):
        consumers[output].append(f"OUT{bit}")
    deletable_chains = tuple(
        (parent, uses[0])
        for parent, uses in sorted(consumers.items())
        if parent in GATES and len(uses) == 1 and uses[0] in GATES
    )
    assert deletable_chains == (("a17", "b17"), ("a18", "b18"))

    cycle_records: list[dict[str, object]] = []
    substitution_groups: list[frozenset[tuple[str, str]]] = []
    for cycle in CERTIFICATE_CYCLES:
        arcs: list[Arc] = []
        for source, target in zip(cycle, cycle[1:] + cycle[:1]):
            arc = selected_arc(source, target)
            assert arc.delay in (5, 7)
            arcs.append(arc)

        register_count = len(cycle)
        delay_sum = sum(arc.delay for arc in arcs)
        substitutions = frozenset().union(*(arc.substitutions for arc in arcs))
        assert len(substitutions) == sum(len(arc.substitutions) for arc in arcs)
        # A single local XOR3 substitution can save at most two delay units on
        # this selected physical cycle.
        min_for_period_6 = max(0, (delay_sum - 6 * register_count + 1) // 2)
        min_for_period_5 = max(0, (delay_sum - 5 * register_count + 1) // 2)
        assert min_for_period_6 == 1
        assert min_for_period_5 == (1 if register_count == 1 else 3)

        for previous in substitution_groups:
            assert substitutions.isdisjoint(previous)
        substitution_groups.append(substitutions)

        cycle_records.append(
            {
                "state_cycle": list(cycle),
                "register_count": register_count,
                "combinational_delay": delay_sum,
                "period_6_budget": 6 * register_count,
                "period_5_budget": 5 * register_count,
                "minimum_substitutions_for_period_6": min_for_period_6,
                "minimum_substitutions_for_period_5": min_for_period_5,
                "arcs": [
                    {
                        "source": arc.source,
                        "target": arc.target,
                        "delay": arc.delay,
                        "chain": list(arc.chain),
                        "shortening_substitutions": [
                            list(pair) for pair in sorted(arc.substitutions)
                        ],
                    }
                    for arc in arcs
                ],
                "substitution_group": [list(pair) for pair in sorted(substitutions)],
            }
        )

    lower_bound_6 = sum(record["minimum_substitutions_for_period_6"] for record in cycle_records)
    lower_bound_5 = sum(record["minimum_substitutions_for_period_5"] for record in cycle_records)
    assert lower_bound_6 == 7
    assert lower_bound_5 == 17

    matrix_payload = b"".join(row.to_bytes(4, "little") for row in rows)
    return {
        "model": {
            "xor2_delay": XOR_DELAY,
            "xor3_delay": XOR_DELAY,
            "steady_state_or_delay": OR_DELAY,
            "canonical_xor2_count": len(GATES),
            "feedback_register_count": BITS,
            "retiming_equation": "w_r(u,v)=w(u,v)+r(v)-r(u)",
            "cycle_invariant": "sum_C(w_r)=sum_C(w)",
        },
        "function": {
            "name": "xorshift32",
            "expression": "x ^= x >> 13; x ^= x << 17; x ^= x >> 5 (U32)",
            "matrix_sha256": sha256(matrix_payload).hexdigest(),
            "basis_vectors_verified": BITS,
        },
        "certificate_cycles": cycle_records,
        "pairwise_disjoint_substitution_groups": True,
        "single_consumer_deletable_xor2_chains": [
            list(pair) for pair in deletable_chains
        ],
        "maximum_local_two_xor2_to_one_xor3_replacements": len(deletable_chains),
        "xor3_lower_bound_for_period_6": lower_bound_6,
        "xor3_lower_bound_for_period_5": lower_bound_5,
        "five_xor3_period_6_possible": False,
        "five_xor3_period_5_possible": False,
        "scope": (
            "canonical 61-XOR DAG, local adjacent XOR2-chain replacement, "
            "and synchronous retiming only"
        ),
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
