r"""Reproduce the reviewed Turing Complete Bit Switch semantics.

This is deliberately a small, dependency-free model.  It models the electrical
bus separately from the value seen by ordinary logic: an undriven bus remains Z,
but its data plane reads as zero.  Conflicting active drivers are a short circuit.

Run from the repository root:

    .\.venv\Scripts\python.exe .research\rng_switch_semantics\switch_semantics.py
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
import hashlib
import sys


Z = None


class ShortCircuit(ValueError):
    """Raised when active drivers on one bus disagree."""


@dataclass(frozen=True)
class Resolved:
    value: int
    is_z: bool


def bit_switch(enable: int, data: int) -> int | None:
    """Kind 12: enable=0 produces Z; enable=1 actively drives data."""

    if enable not in (0, 1) or data not in (0, 1):
        raise ValueError("Bit Switch inputs must be bits")
    return data if enable else Z


def resolve_bus(*drivers: int | None) -> Resolved:
    """Resolve a one-bit multi-driver net using the game's reviewed rules."""

    active = [driver for driver in drivers if driver is not Z]
    if not active:
        return Resolved(value=0, is_z=True)
    if any(driver != active[0] for driver in active[1:]):
        raise ShortCircuit(f"conflicting active drivers: {active}")
    return Resolved(value=active[0], is_z=False)


def xor2_official_switch_level(a: int, b: int) -> Resolved:
    """Topology decoded from examples/bit_switch/baseline/circuit.data."""

    return resolve_bus(bit_switch(b, 1 - a), bit_switch(1 - b, a))


def xor3_hub(a: int, b: int, c: int) -> Resolved:
    """The reviewed 4-Switch/4-gate XOR3 topology from SchematicHub entry 53."""

    return resolve_bus(
        bit_switch(1 - (a | b), c),
        bit_switch(1 - (a | c), b),
        bit_switch(1 - (b | c), a),
        bit_switch(b & c, a),
    )


def mux(select: int, when_zero: int, when_one: int) -> Resolved:
    """Two mutually exclusive switches form a 5-gate/2-delay 2:1 mux."""

    return resolve_bus(
        bit_switch(1 - select, when_zero),
        bit_switch(select, when_one),
    )


@dataclass(frozen=True)
class Function:
    expression: str
    table: int
    gate_cost: int
    depth: int


def primitive_functions(input_count: int) -> tuple[Function, ...]:
    """Raw inputs/constants and one-delay, one-gate Boolean functions."""

    case_count = 1 << input_count
    table_mask = (1 << case_count) - 1
    values: list[Function] = []
    for index in range(input_count):
        table = sum(((case >> index) & 1) << case for case in range(case_count))
        values.append(Function(f"x{index}", table, 0, 0))
    values.extend((Function("0", 0, 0, 0), Function("1", table_mask, 0, 0)))
    for index in range(input_count):
        source = values[index].table
        values.append(Function(f"NOT(x{index})", table_mask ^ source, 1, 1))
    for left, right in combinations(range(input_count), 2):
        a = values[left].table
        b = values[right].table
        values.extend(
            (
                Function(f"AND(x{left},x{right})", a & b, 1, 1),
                Function(f"OR(x{left},x{right})", a | b, 1, 1),
                Function(f"NAND(x{left},x{right})", table_mask ^ (a & b), 1, 1),
                Function(f"NOR(x{left},x{right})", table_mask ^ (a | b), 1, 1),
            )
        )

    # Keep one cheapest expression for each truth table.
    unique: dict[int, Function] = {}
    for value in values:
        previous = unique.get(value.table)
        if previous is None or (value.gate_cost, value.expression) < (
            previous.gate_cost,
            previous.expression,
        ):
            unique[value.table] = value
    return tuple(unique.values())


def minimum_depth2_switch_cover(
    input_count: int, target: int
) -> tuple[int, tuple[tuple[Function, Function], ...]]:
    """Find a restricted minimum Switch bus for a total Boolean function.

    Each driver has a raw or one-gate enable and data function.  A candidate
    driver is accepted only if it agrees with the target everywhere it is
    enabled.  Therefore all selected drivers are mutually compatible.  Shared
    one-gate functions are charged once, and every Switch costs two gates.

    This is a complete search only for this deliberately restricted family.
    """

    functions = primitive_functions(input_count)
    candidates: list[tuple[int, int, int]] = []
    for enable_index, enable in enumerate(functions):
        for data_index, data in enumerate(functions):
            if enable.table & (data.table ^ target):
                continue
            covered_ones = enable.table & target
            if covered_ones:
                candidates.append((enable_index, data_index, covered_ones))

    best: tuple[int, tuple[int, ...]] | None = None
    for count in range(1, 7):
        for selected in combinations(range(len(candidates)), count):
            covered = 0
            charged: set[int] = set()
            for candidate_index in selected:
                enable_index, data_index, ones = candidates[candidate_index]
                covered |= ones
                if functions[enable_index].gate_cost:
                    charged.add(enable_index)
                if functions[data_index].gate_cost:
                    charged.add(data_index)
            if covered != target:
                continue
            cost = 2 * count + sum(functions[index].gate_cost for index in charged)
            if best is None or cost < best[0]:
                best = (cost, selected)
        if best is not None and 2 * (count + 1) >= best[0]:
            break
    if best is None:
        raise AssertionError("no cover found")
    drivers = tuple(
        (functions[candidates[index][0]], functions[candidates[index][1]])
        for index in best[1]
    )
    return best[0], drivers


def truth_table(input_count: int, function) -> int:
    result = 0
    for case in range(1 << input_count):
        args = tuple((case >> index) & 1 for index in range(input_count))
        value = function(*args)
        if isinstance(value, Resolved):
            value = value.value
        result |= int(value) << case
    return result


def inspect_repository_artifacts() -> None:
    """Check the two circuit artifacts used as structural evidence."""

    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "src"))
    from tc_save_lab.codec import decode_circuit
    from tc_save_lab.pins import positioned_pins

    artifacts = (
        (
            root / "examples/bit_switch/baseline/circuit.data",
            "c8cb464454bf0e17191af926e0564146988dff8183ac157545fe3c2040583a0d",
            6,
            2,
            2,
        ),
        (
            root
            / ".research/hub-entry-53/dependencies/00/XOR7/XOR3/circuit.data",
            "2a82925a48cbf20aeb4cb9d9bca83feb51f56ffb0537ebfcf56fe00677164d69",
            12,
            2,
            4,
        ),
    )
    for path, wanted_sha, gate, delay, switch_count in artifacts:
        payload = path.read_bytes()
        assert hashlib.sha256(payload).hexdigest() == wanted_sha
        circuit = decode_circuit(payload)
        switches = [component for component in circuit.components if component.kind == 12]
        assert (circuit.gate, circuit.delay, len(switches)) == (
            gate,
            delay,
            switch_count,
        )
        for component in switches:
            relative = {
                pin.name: (
                    pin.position[0] - component.position[0],
                    pin.position[1] - component.position[1],
                    pin.direction,
                )
                for pin in positioned_pins(component)
            }
            assert relative == {
                "enable": (0, 1, "input"),
                "in": (-1, 0, "input"),
                "out": (2, 0, "output_tristate"),
            }
        print(
            f"artifact {path.relative_to(root)}: sha256={wanted_sha}, "
            f"gate/delay={gate}/{delay}, switches={switch_count}"
        )


def main() -> None:
    inspect_repository_artifacts()

    assert truth_table(2, xor2_official_switch_level) == truth_table(
        2, lambda a, b: a ^ b
    )
    assert truth_table(3, xor3_hub) == truth_table(3, lambda a, b, c: a ^ b ^ c)
    assert truth_table(3, mux) == truth_table(
        3, lambda select, when_zero, when_one: when_one if select else when_zero
    )

    print("\nbus resolution:")
    for drivers in ((Z, Z), (0, Z), (1, Z), (0, 0), (1, 1), (0, 1)):
        try:
            print(f"  {drivers!r} -> {resolve_bus(*drivers)}")
        except ShortCircuit:
            print(f"  {drivers!r} -> SHORT_CIRCUIT")

    xor2 = truth_table(2, lambda a, b: a ^ b)
    xor3 = truth_table(3, lambda a, b, c: a ^ b ^ c)
    mux_table = truth_table(
        3, lambda select, when_zero, when_one: when_one if select else when_zero
    )
    print("\nrestricted depth-2 switch-cover search:")
    for name, inputs, target in (
        ("XOR2", 2, xor2),
        ("XOR3", 3, xor3),
        ("MUX2", 3, mux_table),
    ):
        cost, drivers = minimum_depth2_switch_cover(inputs, target)
        print(f"  {name}: {cost} gates")
        for enable, data in drivers:
            print(f"    Switch(enable={enable.expression}, data={data.expression})")

    print("\nall assertions passed")


if __name__ == "__main__":
    main()
