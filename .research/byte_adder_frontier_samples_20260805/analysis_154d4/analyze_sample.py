"""Read-only structural and truth audit for the supplied Switch 154/4 sample.

This script intentionally has a fixed input path and writes only beside itself.
It never imports, installs, or rewrites a game save.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[2]
SAMPLE = (
    HERE.parent
    / "raw"
    / "extracted"
    / "Switch 154 4"
    / "circuit.data"
)
OUTPUT = HERE / "audit.json"

sys.path.insert(0, str(REPOSITORY / "turingsynth" / "src"))

from turingsynth.formats.v15 import decode_v15  # noqa: E402
from turingsynth.formats.wire import wire_points  # noqa: E402
from turingsynth.mapping.native import (  # noqa: E402
    COMPONENTS,
    INPUT,
    OUTPUT as PIN_OUTPUT,
    TRISTATE,
    positioned_pins,
)


INPUT_KINDS = {61, 79}
OUTPUT_KINDS = {69, 81}
MAKER_KINDS = {16, 97, 98, 111, 112}
SPLITTER_KINDS = {17, 99, 100, 109, 110}


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left = self.find(left)
        right = self.find(right)
        if left != right:
            self.parent[right] = left


@dataclass(frozen=True)
class Pin:
    component: int
    name: str
    direction: str
    width: int
    root: int | None


def component_cost(kind: int, width: int) -> tuple[int, int]:
    if kind in {3, 4, 6, 7, 9}:
        return width, 1
    if kind == 10:
        return 3 * width, 2
    if kind == 12:
        return 2, 1
    if kind in {18, 19, 20, 21, 22}:
        return width, 1
    if kind == 23:
        return 3 * width, 2
    return 0, 0


def network(circuit):
    union = UnionFind(len(circuit.wires))
    endpoint_owners: dict[tuple[int, int], list[int]] = defaultdict(list)
    endpoints = []
    for index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        pair = (points[0], points[-1])
        endpoints.append(pair)
        endpoint_owners[pair[0]].append(index)
        endpoint_owners[pair[1]].append(index)
    for owners in endpoint_owners.values():
        for index in owners[1:]:
            union.union(owners[0], index)

    root_by_endpoint: dict[tuple[int, int], int] = {}
    wire_indices: dict[int, list[int]] = defaultdict(list)
    for index, pair in enumerate(endpoints):
        root = union.find(index)
        root_by_endpoint[pair[0]] = root
        root_by_endpoint[pair[1]] = root
        wire_indices[root].append(index)

    pins_by_root: dict[int, list[Pin]] = defaultdict(list)
    pins_by_component: dict[int, dict[str, Pin]] = defaultdict(dict)
    unconnected = []
    for index, component in enumerate(circuit.components):
        for positioned in positioned_pins(component, index):
            root = root_by_endpoint.get(positioned.position)
            pin = Pin(
                component=index,
                name=positioned.name,
                direction=positioned.direction,
                width=positioned.width,
                root=root,
            )
            pins_by_component[index][pin.name] = pin
            if root is None:
                unconnected.append(pin)
            else:
                pins_by_root[root].append(pin)
    return pins_by_root, pins_by_component, wire_indices, unconnected


def input_bit_names(circuit, pins_by_component):
    names: dict[tuple[int, str, int], str] = {}
    for index, component in enumerate(circuit.components):
        if component.kind not in INPUT_KINDS:
            continue
        pin = next(iter(pins_by_component[index].values()))
        label = component.user_label.strip() or f"input_{index}"
        if component.word_size == 1:
            names[(index, pin.name, 0)] = "Cin" if "carry" in label.lower() else label
        else:
            for bit in range(component.word_size):
                names[(index, pin.name, bit)] = f"{label}[{bit}]"
    return names


def mask_for_variable(ordinal: int, rows: int) -> int:
    block = 1 << ordinal
    pattern = ((1 << block) - 1) << block
    value = 0
    shift = 0
    while shift < rows:
        value |= pattern << shift
        shift += block * 2
    return value & ((1 << rows) - 1)


def main() -> None:
    payload = SAMPLE.read_bytes()
    circuit = decode_v15(payload)
    pins_by_root, pins_by_component, wire_indices, unconnected = network(circuit)

    inputs = input_bit_names(circuit, pins_by_component)
    ordered_variables = ["A[%d]" % bit for bit in range(8)]
    ordered_variables += ["B[%d]" % bit for bit in range(8)]
    ordered_variables += ["Cin"]
    rows = 1 << len(ordered_variables)
    full_mask = (1 << rows) - 1
    variable_masks = {
        name: mask_for_variable(index, rows)
        for index, name in enumerate(ordered_variables)
    }
    known_functions: dict[str, int] = dict(variable_masks)
    carries = [variable_masks["Cin"]]
    known_functions["C0"] = carries[0]
    for bit in range(8):
        a = variable_masks[f"A[{bit}]"]
        b = variable_masks[f"B[{bit}]"]
        generate = a & b
        kill = ~(a | b) & full_mask
        half_or = a | b
        propagate = a ^ b
        known_functions[f"G{bit}"] = generate
        known_functions[f"K{bit}"] = kill
        known_functions[f"H{bit}"] = half_or
        known_functions[f"P{bit}"] = propagate
        known_functions[f"nG{bit}"] = (~generate) & full_mask
        known_functions[f"nP{bit}"] = (~propagate) & full_mask
        carry = generate | (propagate & carries[-1])
        carries.append(carry)
        known_functions[f"C{bit + 1}"] = carry
        known_functions[f"nC{bit + 1}"] = (~carry) & full_mask
        known_functions[f"S{bit}"] = propagate ^ carries[-2]
        known_functions[f"nS{bit}"] = (~known_functions[f"S{bit}"]) & full_mask
    known_names_by_mask: dict[int, list[str]] = defaultdict(list)
    for name, value in known_functions.items():
        known_names_by_mask[value].append(name)

    drivers_by_root: dict[int, list[Pin]] = defaultdict(list)
    sinks_by_root: dict[int, list[Pin]] = defaultdict(list)
    for root, pins in pins_by_root.items():
        for pin in pins:
            if pin.direction in {PIN_OUTPUT, TRISTATE}:
                drivers_by_root[root].append(pin)
            elif pin.direction == INPUT:
                sinks_by_root[root].append(pin)

    # A component becomes ready after every connected input net is resolved.
    unresolved_inputs: dict[int, set[int]] = {}
    consumers_by_root: dict[int, set[int]] = defaultdict(set)
    for index, component in enumerate(circuit.components):
        roots = {
            pin.root
            for pin in pins_by_component[index].values()
            if pin.direction == INPUT and pin.root is not None
        }
        unresolved_inputs[index] = set(roots)
        for root in roots:
            consumers_by_root[root].add(index)

    # Per bit, a value is represented by (active-one mask, active-zero mask).
    # Ordinary binary sources always cover the full truth table. A Switch can
    # leave rows uncovered (Z); a multi-driver BUS is valid iff no row has both.
    net_values: dict[int, tuple[tuple[int, int], ...]] = {}
    net_arrival: dict[int, int] = {}
    output_values: dict[tuple[int, str], tuple[tuple[int, int], ...]] = {}
    output_arrival: dict[tuple[int, str], int] = {}
    pending_drivers: dict[int, set[tuple[int, str]]] = {
        root: {(pin.component, pin.name) for pin in pins}
        for root, pins in drivers_by_root.items()
    }
    ready = deque(
        index
        for index, component in enumerate(circuit.components)
        if not unresolved_inputs[index]
    )
    evaluated: set[int] = set()
    component_arrival: dict[int, int] = {}

    def binary(bits):
        return tuple((value & full_mask, (~value) & full_mask) for value in bits)

    def input_net(index: int, pin_name: str):
        pin = pins_by_component[index][pin_name]
        if pin.root is None:
            return tuple((0, 0) for _ in range(pin.width))
        return net_values[pin.root]

    def read_logic(values, context):
        """Read a net as a gate input: Z is false, conflicts stay invalid."""
        result = []
        for one, zero in values:
            if one & zero:
                raise ValueError(f"{context} received an active 0/1 conflict")
            result.append(one)
        return tuple(result)

    def publish(index: int, pin_name: str, values, arrival: int) -> None:
        output_values[(index, pin_name)] = tuple(values)
        output_arrival[(index, pin_name)] = arrival
        pin = pins_by_component[index][pin_name]
        if pin.root is None:
            return
        pending_drivers[pin.root].discard((index, pin_name))
        if pending_drivers[pin.root]:
            return
        drivers = drivers_by_root[pin.root]
        width = drivers[0].width
        merged = []
        for bit in range(width):
            ones = 0
            zeroes = 0
            for driver in drivers:
                one, zero = output_values[(driver.component, driver.name)][bit]
                ones |= one
                zeroes |= zero
            merged.append((ones, zeroes))
        net_values[pin.root] = tuple(merged)
        net_arrival[pin.root] = max(
            output_arrival[(driver.component, driver.name)] for driver in drivers
        )
        for consumer in consumers_by_root[pin.root]:
            unresolved_inputs[consumer].discard(pin.root)
            if not unresolved_inputs[consumer] and consumer not in evaluated:
                ready.append(consumer)

    while ready:
        index = ready.popleft()
        if index in evaluated:
            continue
        component = circuit.components[index]
        kind = component.kind
        input_roots = [
            pin.root
            for pin in pins_by_component[index].values()
            if pin.direction == INPUT and pin.root is not None
        ]
        arrival_in = max((net_arrival[root] for root in input_roots), default=0)
        _cost, delay = component_cost(kind, component.word_size)
        arrival = arrival_in + delay
        component_arrival[index] = arrival

        if kind in INPUT_KINDS:
            output_pin = next(
                pin for pin in pins_by_component[index].values()
                if pin.direction in {PIN_OUTPUT, TRISTATE}
            )
            bits = []
            for bit in range(output_pin.width):
                name = inputs[(index, output_pin.name, bit)]
                bits.append(variable_masks[name])
            publish(index, output_pin.name, binary(bits), arrival)
        elif kind in OUTPUT_KINDS:
            pass
        elif kind in SPLITTER_KINDS:
            source = read_logic(input_net(index, "in"), f"splitter {index}")
            offset = 0
            for pin in pins_by_component[index].values():
                if not pin.name.startswith("out"):
                    continue
                publish(index, pin.name, binary(source[offset : offset + pin.width]), arrival)
                offset += pin.width
        elif kind in MAKER_KINDS:
            bits = []
            for pin in pins_by_component[index].values():
                if not pin.name.startswith("in"):
                    continue
                if pin.root is None:
                    bits.extend([0] * pin.width)
                else:
                    bits.extend(read_logic(input_net(index, pin.name), f"maker {index}"))
            publish(index, "out", binary(bits), arrival)
        elif kind == 2:
            publish(index, "out", binary((full_mask,)), arrival)
        elif kind == 3:
            (value,) = read_logic(input_net(index, "in"), f"NOT {index}")
            publish(index, "out", binary(((~value) & full_mask,)), arrival)
        elif kind in {4, 6, 7, 9, 10}:
            left = read_logic(input_net(index, "in0"), f"gate {index}")
            right = read_logic(input_net(index, "in1"), f"gate {index}")
            bits = []
            for a, b in zip(left, right):
                if kind == 4:
                    value = a & b
                elif kind == 6:
                    value = ~(a & b) & full_mask
                elif kind == 7:
                    value = a | b
                elif kind == 9:
                    value = ~(a | b) & full_mask
                else:
                    value = a ^ b
                bits.append(value)
            publish(index, "out", binary(bits), arrival)
        elif kind == 12:
            (enable,) = read_logic(input_net(index, "enable"), f"Switch {index}")
            data = input_net(index, "in")
            values = []
            for data_one, data_zero in data:
                # Game contract used by the project: enabled Z data resolves 0.
                one = enable & data_one
                zero = enable & (~data_one & full_mask)
                values.append((one, zero))
            publish(index, "out", values, arrival)
        else:
            raise ValueError(f"unsupported kind {kind} at component {index}")
        evaluated.add(index)

    if len(evaluated) != len(circuit.components):
        missing = sorted(set(range(len(circuit.components))) - evaluated)
        raise ValueError(f"component DAG did not resolve: {missing}")

    component_rows = []
    for index, component in enumerate(circuit.components):
        spec = COMPONENTS[component.kind]
        gate, delay = component_cost(component.kind, component.word_size)
        inputs_json = {}
        outputs_json = {}
        for pin in pins_by_component[index].values():
            entry = None if pin.root is None else pin.root
            if pin.direction == INPUT:
                inputs_json[pin.name] = entry
            else:
                outputs_json[pin.name] = entry
        component_rows.append(
            {
                "index": index,
                "kind": component.kind,
                "type": spec.name,
                "label": component.user_label,
                "position": list(component.position),
                "rotation": component.rotation,
                "word_size": component.word_size,
                "gate": gate,
                "delay": delay,
                "arrival": component_arrival[index],
                "inputs": inputs_json,
                "outputs": outputs_json,
            }
        )

    net_rows = []
    total_conflicts = 0
    total_z = 0
    for root in sorted(pins_by_root):
        values = net_values.get(root)
        conflict = 0
        z_rows = 0
        signatures = []
        recognized = []
        one_counts = []
        active_zero_counts = []
        z_counts = []
        if values is not None:
            for one, zero in values:
                conflict |= one & zero
                z = ~(one | zero) & full_mask
                z_rows |= z
                signatures.append(hashlib.sha256(one.to_bytes(rows // 8, "little")).hexdigest())
                recognized.append(known_names_by_mask.get(one, []))
                one_counts.append(one.bit_count())
                active_zero_counts.append(zero.bit_count())
                z_counts.append(z.bit_count())
        total_conflicts |= conflict
        total_z |= z_rows
        net_rows.append(
            {
                "root": root,
                "width": pins_by_root[root][0].width,
                "arrival": net_arrival.get(root),
                "drivers": [
                    {"component": pin.component, "pin": pin.name, "tristate": pin.direction == TRISTATE}
                    for pin in drivers_by_root[root]
                ],
                "sinks": [
                    {"component": pin.component, "pin": pin.name}
                    for pin in sinks_by_root[root]
                ],
                "truth_sha256": signatures,
                "recognized_functions": recognized,
                "one_counts": one_counts,
                "active_zero_counts": active_zero_counts,
                "z_counts": z_counts,
                "conflict_rows": conflict.bit_count(),
                "z_rows": z_rows.bit_count(),
                "wire_indices": wire_indices[root],
            }
        )

    # Fixed-candidate bridge audit: the supplied DAG's S0..S3 live cone costs
    # 41 gates. Check whether exactly one additional ordinary gate, using only
    # already-live signals arriving by D2, can publish nC4 at D3.
    def component_cone(target_roots: tuple[int, ...]) -> set[int]:
        live: set[int] = set()
        pending = list(target_roots)
        seen_roots: set[int] = set()
        while pending:
            root = pending.pop()
            if root in seen_roots:
                continue
            seen_roots.add(root)
            for driver in drivers_by_root[root]:
                index = driver.component
                if index in live:
                    continue
                live.add(index)
                pending.extend(
                    pin.root
                    for pin in pins_by_component[index].values()
                    if pin.direction == INPUT and pin.root is not None
                )
        return live

    low_sum_roots = (29, 82, 84, 121)
    low_live = component_cone(low_sum_roots)
    low_roots = sorted(
        root
        for root, drivers in drivers_by_root.items()
        if root in net_values
        and pins_by_root[root][0].width == 1
        and net_arrival[root] <= 2
        and all(driver.component in low_live for driver in drivers)
    )
    # Input/splitter rails are also live even when a free component is shared.
    low_roots.extend(
        root
        for root, drivers in drivers_by_root.items()
        if root in net_values
        and pins_by_root[root][0].width == 1
        and net_arrival[root] <= 2
        and root not in low_roots
        and all(circuit.components[driver.component].kind in INPUT_KINDS | SPLITTER_KINDS for driver in drivers)
    )
    low_roots = sorted(set(low_roots))
    target_nc4 = known_functions["nC4"]
    bridges = []
    for left_index, left_root in enumerate(low_roots):
        left = net_values[left_root][0][0]
        if ((~left) & full_mask) == target_nc4:
            bridges.append({"op": "NOT", "args": [left_root]})
        for right_root in low_roots[left_index:]:
            right = net_values[right_root][0][0]
            candidates = {
                "AND": left & right,
                "OR": left | right,
                "NAND": ~(left & right) & full_mask,
                "NOR": ~(left | right) & full_mask,
            }
            for op, value in candidates.items():
                if value == target_nc4:
                    bridges.append({"op": op, "args": [left_root, right_root]})
    bridge_audit = {
        "target": "nC4@3",
        "base": {
            "outputs": ["S0", "S1", "S2", "S3"],
            "gate": sum(
                component_cost(circuit.components[index].kind, circuit.components[index].word_size)[0]
                for index in low_live
            ),
            "delay": max(net_arrival[root] for root in low_sum_roots),
            "live_components": sorted(low_live),
        },
        "eligible_existing_roots": low_roots,
        "one_gate_matches": bridges,
        "conclusion": "hit" if bridges else "no one-gate bridge in the fixed S0..S3 cone",
    }
    all_scalar_roots_d2 = sorted(
        root
        for root in net_values
        if pins_by_root[root][0].width == 1 and net_arrival[root] <= 2
    )
    component_cone_cache = {
        root: component_cone((root,)) for root in all_scalar_roots_d2
    }
    sample_reuse_matches = []
    for left_index, left_root in enumerate(all_scalar_roots_d2):
        left = net_values[left_root][0][0]
        unary = {"NOT": (~left) & full_mask}
        for op, value in unary.items():
            if value == target_nc4:
                live = low_live | component_cone_cache[left_root]
                sample_reuse_matches.append(
                    {
                        "op": op,
                        "args": [left_root],
                        "total_gate_with_low_sums": sum(
                            component_cost(circuit.components[i].kind, circuit.components[i].word_size)[0]
                            for i in live
                        )
                        + 1,
                        "increment_over_41": sum(
                            component_cost(circuit.components[i].kind, circuit.components[i].word_size)[0]
                            for i in live - low_live
                        )
                        + 1,
                    }
                )
        for right_root in all_scalar_roots_d2[left_index:]:
            right = net_values[right_root][0][0]
            candidates = {
                "AND": left & right,
                "OR": left | right,
                "NAND": ~(left & right) & full_mask,
                "NOR": ~(left | right) & full_mask,
            }
            for op, value in candidates.items():
                if value != target_nc4:
                    continue
                live = (
                    low_live
                    | component_cone_cache[left_root]
                    | component_cone_cache[right_root]
                )
                sample_reuse_matches.append(
                    {
                        "op": op,
                        "args": [left_root, right_root],
                        "total_gate_with_low_sums": sum(
                            component_cost(circuit.components[i].kind, circuit.components[i].word_size)[0]
                            for i in live
                        )
                        + 1,
                        "increment_over_41": sum(
                            component_cost(circuit.components[i].kind, circuit.components[i].word_size)[0]
                            for i in live - low_live
                        )
                        + 1,
                    }
                )
    sample_reuse_matches.sort(
        key=lambda item: (item["total_gate_with_low_sums"], item["op"], item["args"])
    )
    bridge_audit["all_sample_d2_reuse_matches"] = sample_reuse_matches
    bridge_audit["best_all_sample_reuse"] = sample_reuse_matches[:8]
    low_descriptors = []
    for root in sorted(drivers_by_root):
        drivers = drivers_by_root[root]
        if root not in net_values or net_arrival[root] > 3:
            continue
        if pins_by_root[root][0].width != 1:
            continue
        if not all(driver.component in low_live for driver in drivers):
            continue
        one, zero = net_values[root][0]
        driven = one | zero
        low_descriptors.append(
            {
                "root": root,
                "arrival": net_arrival[root],
                "drivers": [
                    {"component": driver.component, "pin": driver.name}
                    for driver in drivers
                ],
                "recognized_functions": known_names_by_mask.get(one, []),
                "active_one_rows": one.bit_count(),
                "active_zero_rows": zero.bit_count(),
                "z_rows": ((~driven) & full_mask).bit_count(),
                "active_one_sha256": hashlib.sha256(
                    one.to_bytes(rows // 8, "little")
                ).hexdigest(),
                "driven_sha256": hashlib.sha256(
                    driven.to_bytes(rows // 8, "little")
                ).hexdigest(),
                "equals_nC4_when_z_reads_zero": one == target_nc4,
                "nC4_truth_distance": (one ^ target_nc4).bit_count(),
                "consumer_components_outside_low_closure": sorted(
                    consumer
                    for consumer in consumers_by_root[root]
                    if consumer not in low_live
                ),
            }
        )
    descriptor_audit = {
        "target": "nC4",
        "target_active_one_rows": target_nc4.bit_count(),
        "descriptor_count": len(low_descriptors),
        "care_domain": {
            "S4_XNOR_P4_nC4": "full low-input domain; XNOR is bijective in nC4 for either P4 value",
            "S5_NAND_nC4_P4": "P4=1 observes every low-input assignment because bit4 is independent",
            "nC6_SW_P45_nC4": "P45=1 observes every low-input assignment because bits4:5 are independent",
            "projected_low_domain": "all 2^9 assignments of A[0:3], B[0:3], Cin",
            "z_contract": "Z may replace logical 0, but cannot replace an nC4 active-one row",
        },
        "descriptors": low_descriptors,
        "equivalent_roots": [
            descriptor["root"]
            for descriptor in low_descriptors
            if descriptor["equals_nC4_when_z_reads_zero"]
        ],
        "conclusion": (
            "equivalent descriptor found"
            if any(d["equals_nC4_when_z_reads_zero"] for d in low_descriptors)
            else "no existing <=D3 descriptor is care-domain equivalent to nC4"
        ),
    }

    def bit_function(prefix: str, bit: int) -> int:
        return known_functions[f"{prefix}{bit}"]

    g = [bit_function("G", bit) for bit in range(8)]
    k = [bit_function("K", bit) for bit in range(8)]
    h = [bit_function("H", bit) for bit in range(8)]
    p = [bit_function("P", bit) for bit in range(8)]
    np = [bit_function("nP", bit) for bit in range(8)]
    ng = [bit_function("nG", bit) for bit in range(8)]
    c = carries
    s = [known_functions[f"S{bit}"] for bit in range(8)]
    u23 = g[3] | (h[3] & h[2])
    rgen234 = g[2] | g[3] | g[4]
    w4_enable = g[4] | u23
    w4_one = h[4] & w4_enable
    n0_c5 = ~(c[2] | rgen234) & full_mask
    nw4 = (~w4_one) & full_mask
    c5_select = c[2] | rgen234
    f60 = p[6] ^ g[5]
    f61 = p[6] ^ h[5]
    c7_when_c5_0 = g[6] | (p[6] & g[5])
    c7_when_c5_1 = g[6] | (p[6] & h[5])
    f70 = p[7] ^ c7_when_c5_0
    f71 = p[7] ^ c7_when_c5_1
    r0_c8 = g[6] | g[7] | (g[5] & h[6])
    w8_enable = g[6] | g[7] | (h[5] & h[6])
    w8_one = h[7] & w8_enable

    named_specs = [
        ("X0=H0*Cin", 24, h[0] & c[0], h[0]),
        ("C1", 44, c[1], full_mask),
        ("C2", 57, c[2], g[1] | g[0] | (h[0] & c[0])),
        ("S3", 121, s[3], (p[3] & ng[2]) | g[2] | (p[2] & c[2])),
        ("RA=A3*(H2|B3)", 417, variable_masks["A[3]"] & (h[2] | variable_masks["B[3]"]), h[2] | variable_masks["B[3]"]),
        ("RB=B3*H2", 141, variable_masks["B[3]"] & h[2], h[2]),
        ("nU23=not(G3|H3*H2)", 181, (~u23) & full_mask, full_mask),
        ("Rgen234=G2|G3|G4", 154, rgen234, rgen234),
        ("W4=H4*(G4|U23)", 156, w4_one, w4_enable),
        ("N0_C5=not(C2|G2|G3|G4)", 401, n0_c5, full_mask),
        ("nW4", 328, nw4, full_mask),
        ("C5_positive_descriptor", 196, c[5], c5_select),
        ("S4", 125, s[4], None),
        ("S5", 219, s[5], full_mask),
        ("F60=P6 xor G5", 200, f60, full_mask),
        ("F61=P6 xor H5", 197, f61, full_mask),
        ("S6", 193, s[6], full_mask),
        ("E0=G5*H6", 313, g[5] & h[6], full_mask),
        ("F0=H5*H6", 315, h[5] & h[6], full_mask),
        ("E1=nG5*nG6", 314, ng[5] & ng[6], full_mask),
        ("F1=K5*nG6", 316, k[5] & ng[6], full_mask),
        ("F70=P7 xor (G6|P6*G5)", 346, f70, full_mask),
        ("F71=P7 xor (G6|P6*H5)", 302, f71, full_mask),
        ("S7", 326, s[7], full_mask),
        ("R0_C8=G6|G7|G5*H6", 384, r0_c8, full_mask),
        ("W8=H7*(G6|G7|H5*H6)", 349, w8_one, w8_enable),
        ("C8_positive_descriptor", 354, c[8], r0_c8 | c[5]),
    ]
    named_contracts = []
    for name, root, expected_one, expected_driven in named_specs:
        actual_one, actual_zero = net_values[root][0]
        actual_driven = actual_one | actual_zero
        row = {
            "name": name,
            "root": root,
            "arrival": net_arrival[root],
            "active_one_mismatch": (actual_one ^ expected_one).bit_count(),
            "active_one_rows": actual_one.bit_count(),
            "active_zero_rows": actual_zero.bit_count(),
            "z_rows": ((~actual_driven) & full_mask).bit_count(),
        }
        if expected_driven is not None:
            row["driven_mismatch"] = (actual_driven ^ expected_driven).bit_count()
        named_contracts.append(row)
    nc5_cover = net_values[401][0][0] | net_values[328][0][0]
    named_contracts.append(
        {
            "name": "N0_C5 | nW4 = nC5 phase cover",
            "roots": [401, 328],
            "arrival": max(net_arrival[401], net_arrival[328]),
            "active_one_mismatch": (nc5_cover ^ ((~c[5]) & full_mask)).bit_count(),
        }
    )
    if any(contract["active_one_mismatch"] for contract in named_contracts):
        raise ValueError("a named architecture equation does not match the fixed sample")
    if any(contract.get("driven_mismatch", 0) for contract in named_contracts):
        raise ValueError("a named descriptor driven-domain equation does not match")

    outputs = {}
    mismatch = {}
    output_arrivals = {}
    for index, component in enumerate(circuit.components):
        if component.kind not in OUTPUT_KINDS:
            continue
        input_pin = next(
            pin for pin in pins_by_component[index].values() if pin.direction == INPUT
        )
        values = net_values[input_pin.root]
        actual = [one for one, _zero in values]
        label = component.user_label
        outputs[label] = [
            hashlib.sha256(value.to_bytes(rows // 8, "little")).hexdigest()
            for value in actual
        ]
        output_arrivals[label] = net_arrival[input_pin.root]
        if "carry" in label.lower():
            mask = 0
            for row in range(rows):
                a = row & 0xFF
                b = (row >> 8) & 0xFF
                cin = (row >> 16) & 1
                if a + b + cin >= 256:
                    mask |= 1 << row
            expected = [mask]
        else:
            expected = []
            for bit in range(component.word_size):
                mask = 0
                for row in range(rows):
                    a = row & 0xFF
                    b = (row >> 8) & 0xFF
                    cin = (row >> 16) & 1
                    if ((a + b + cin) >> bit) & 1:
                        mask |= 1 << row
                expected.append(mask)
        mismatch[label] = [
            (value ^ target).bit_count() for value, target in zip(actual, expected)
        ]

    kind_counts = Counter(
        (component.kind, COMPONENTS[component.kind].name, component.word_size)
        for component in circuit.components
    )
    result = {
        "schema": "switch-154-4-read-only-audit-v1",
        "source": {
            "path": str(SAMPLE),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
        },
        "header": {
            "gate": circuit.gate,
            "delay": circuit.delay,
            "energy": circuit.energy,
            "component_count": len(circuit.components),
            "wire_count": len(circuit.wires),
        },
        "recomputed": {
            "gate": sum(component_cost(c.kind, c.word_size)[0] for c in circuit.components),
            "delay": max(output_arrivals.values()),
            "output_arrivals": output_arrivals,
            "truth_rows": rows,
            "output_mismatch_counts": mismatch,
            "bus_conflict_rows_union": total_conflicts.bit_count(),
            "internal_z_rows_union": total_z.bit_count(),
        },
        "kind_counts": [
            {"kind": kind, "type": name, "word_size": width, "count": count}
            for (kind, name, width), count in sorted(kind_counts.items())
        ],
        "unconnected_pins": [
            {
                "component": pin.component,
                "pin": pin.name,
                "direction": pin.direction,
                "width": pin.width,
            }
            for pin in unconnected
        ],
        "fixed_nC4_bridge_audit": bridge_audit,
        "low_closure_descriptor_audit": descriptor_audit,
        "named_architecture_contracts": named_contracts,
        "components": component_rows,
        "nets": net_rows,
        "output_truth_sha256": outputs,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["header"], ensure_ascii=False))
    print(json.dumps(result["recomputed"], ensure_ascii=False))
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
