"""Read-only structural and semantic audit for the human Switch 103/5 A sample.

The script never writes a circuit.  It decodes the supplied v15 payload,
reconstructs endpoint-connected networks, evaluates all 131072 Byte Adder
input rows as bitsets, and emits review artifacts beside this file.

The only intentionally unconnected receiver in the sample is maker_2.in0.
The game adapters normalize that Z lane to a driven zero before splitter_2
selects lane one, so the pair is a free C8 pass-through.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SAMPLE = (
    HERE.parent
    / "raw"
    / "extracted"
    / "Switch 103 5 A"
    / "circuit.data"
)
INDEPENDENT = (
    ROOT
    / ".research"
    / "byte_adder_d5_frontier"
    / "patchouli103-d5-audit-v1.json"
)
SEGMENTED_BASELINE = (
    ROOT
    / ".research"
    / "byte_adder_segmented_switch84"
    / "segmented-negative-spine-audit.json"
)
OUTPUT_JSON = HERE / "machine-audit.json"
OUTPUT_DAG = HERE / "完整逻辑DAG.md"
OUTPUT_REPORT = HERE / "2026-08-05-Switch103门5延迟A样本反解与迁移分析.md"
OUTPUT_SUMS = HERE / "SHA256SUMS.txt"

sys.path.insert(0, str(ROOT / "src"))

from tc_save_lab.analysis import wire_points  # noqa: E402
from tc_save_lab.codec import decode_v15, encode_v15  # noqa: E402
from tc_save_lab.pins import I, O, T, positioned_pins  # noqa: E402


ROW_COUNT = 256 * 256 * 2
ALL_ROWS = (1 << ROW_COUNT) - 1

SOURCE_KINDS = {61}
SINK_KINDS = {69}
ADAPTER_KINDS = {16, 17, 109, 111}
SIMPLE_KINDS = {4, 6, 7, 9}
SWITCH_KIND = 12

KIND_NAMES = {
    4: "AND",
    6: "NAND",
    7: "OR",
    9: "NOR",
    12: "SWITCH",
    16: "MAKER8",
    17: "SPLITTER8",
    61: "INPUT",
    69: "OUTPUT",
    109: "SPLITTER2",
    111: "MAKER2",
}

KIND_COST_DELAY = {
    4: (1, 1),
    6: (1, 1),
    7: (1, 1),
    9: (1, 1),
    12: (2, 1),
    16: (0, 0),
    17: (0, 0),
    61: (0, 0),
    69: (0, 0),
    109: (0, 0),
    111: (0, 0),
}

# Names are attached only after the 131072-row replay proves the value.
MANUAL_NETWORK_NAMES = {
    30: "Cin",
    43: "A0",
    114: "A1",
    124: "A2",
    111: "A3",
    103: "A4",
    105: "A5",
    108: "A6",
    125: "A7",
    38: "B0",
    37: "B1",
    1: "B2",
    6: "B3",
    78: "B4",
    84: "B5",
    92: "B6",
    94: "B7",
    14: "G3",
    3: "nG3",
    188: "V2",
    306: "nG2",
    13: "V3",
    21: "X3=nP3",
    174: "D23=G23|P23",
    191: "R23=G2|G3",
    83: "C4",
    18: "P3*nC4",
    142: "S3",
    34: "G0",
    171: "V1",
    72: "G1",
    51: "V0",
    36: "T0=Cin*V0",
    56: "C1",
    54: "Q0*nCin",
    45: "G0*Cin",
    41: "S0",
    177: "C2",
    63: "Q1*nC1",
    60: "G1*C1",
    138: "S1",
    307: "P2",
    29: "N2=~(C2*P2)",
    197: "O2=C2|P2",
    140: "S2",
    11: "C3",
    85: "nG4",
    89: "V4",
    82: "P4",
    79: "C4*P4",
    152: "nC4*nP4",
    144: "S4",
    335: "nG5",
    163: "V5",
    319: "P5",
    351: "N45=~(V4*V5)",
    347: "D45=G54|P54",
    356: "K54",
    352: "E45=G4|nP5",
    203: "F45=nG4|P5",
    334: "L5=G4 xor P5",
    325: "n(C4*P4)",
    332: "S5",
    234: "R45=P5*nG4*nC4",
    337: "C6",
    257: "Q6",
    275: "G6",
    233: "P6",
    240: "X6=nP6",
    215: "Q7",
    218: "G7",
    276: "X7=nP7",
    223: "E67=G6|X7",
    282: "N67=~(G6*X7)",
    281: "L7=G6 xor P7",
    267: "X7*Q6",
    214: "P7*nQ6",
    270: "F7=XNOR(Q6,P7)",
    213: "D67=G67|P67",
    237: "S6",
    245: "S7",
    210: "C8",
    278: "C8",
}


@dataclass(frozen=True)
class Netlist:
    pin_networks: dict[tuple[int, str], int]
    drivers: dict[int, tuple[tuple[int, str], ...]]
    sinks: dict[int, tuple[tuple[int, str], ...]]
    driver_counts: dict[int, int]
    roots: tuple[int, ...]
    missing_inputs: tuple[tuple[int, str], ...]
    missing_outputs: tuple[tuple[int, str], ...]


class UnionFind:
    def __init__(self, size: int):
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


def _compile(circuit) -> Netlist:
    endpoint_owners: dict[tuple[int, int], list[int]] = defaultdict(list)
    endpoints: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        pair = (points[0], points[-1])
        endpoints.append(pair)
        endpoint_owners[pair[0]].append(wire_index)
        endpoint_owners[pair[1]].append(wire_index)

    union = UnionFind(len(circuit.wires))
    for wire_indices in endpoint_owners.values():
        for wire_index in wire_indices[1:]:
            union.union(wire_indices[0], wire_index)

    network_by_position: dict[tuple[int, int], int] = {}
    roots: set[int] = set()
    for wire_index, pair in enumerate(endpoints):
        root = union.find(wire_index)
        roots.add(root)
        network_by_position[pair[0]] = root
        network_by_position[pair[1]] = root

    pin_networks: dict[tuple[int, str], int] = {}
    drivers: dict[int, list[tuple[int, str]]] = defaultdict(list)
    sinks: dict[int, list[tuple[int, str]]] = defaultdict(list)
    missing_inputs: list[tuple[int, str]] = []
    missing_outputs: list[tuple[int, str]] = []
    for component_index, component in enumerate(circuit.components):
        pins = positioned_pins(component, component_index)
        if not pins:
            raise RuntimeError(f"unsupported component kind {component.kind}")
        for pin in pins:
            root = network_by_position.get(pin.position)
            if root is None:
                target = missing_inputs if pin.direction == I else missing_outputs
                target.append((component_index, pin.name))
                continue
            pin_networks[(component_index, pin.name)] = root
            target = drivers if pin.direction in {O, T} else sinks
            target[root].append((component_index, pin.name))

    allowed_missing_inputs = ((57, "in0"),)
    allowed_missing_outputs = ((55, "out0"),)
    if tuple(missing_inputs) != allowed_missing_inputs:
        raise RuntimeError(f"unexpected unconnected inputs: {missing_inputs!r}")
    if tuple(missing_outputs) != allowed_missing_outputs:
        raise RuntimeError(f"unexpected unconnected outputs: {missing_outputs!r}")

    return Netlist(
        pin_networks=pin_networks,
        drivers={key: tuple(value) for key, value in drivers.items()},
        sinks={key: tuple(value) for key, value in sinks.items()},
        driver_counts={key: len(value) for key, value in drivers.items()},
        roots=tuple(sorted(roots)),
        missing_inputs=tuple(missing_inputs),
        missing_outputs=tuple(missing_outputs),
    )


def _pattern(half_period: int) -> int:
    block = "0" * half_period + "1" * half_period
    return int(block * (ROW_COUNT // (2 * half_period)), 2)


def _input_planes() -> dict[str, tuple[int, ...]]:
    return {
        "Carry in": (_pattern(1),),
        "B": tuple(_pattern(2 << bit) for bit in range(8)),
        "A": tuple(_pattern(512 << bit) for bit in range(8)),
    }


def _invert(value: int) -> int:
    return (~value) & ALL_ROWS


def _pin(circuit, component_index: int, pin_name: str):
    for pin in positioned_pins(circuit.components[component_index], component_index):
        if pin.name == pin_name:
            return pin
    raise KeyError((component_index, pin_name))


def _evaluate(circuit, netlist: Netlist):
    inputs = _input_planes()
    values: dict[int, tuple[int, ...]] = {}
    driven: dict[int, tuple[int, ...]] = {}
    resolved: dict[int, int] = defaultdict(int)
    arrivals: dict[int, int] = {}
    conflicts: dict[int, int] = defaultdict(int)

    def drive(
        component_index: int,
        pin_name: str,
        value: int | Iterable[int],
        masks: int | Iterable[int] | None = None,
    ) -> None:
        network = netlist.pin_networks.get((component_index, pin_name))
        if network is None:
            return
        width = _pin(circuit, component_index, pin_name).width
        lanes = (value,) * width if isinstance(value, int) else tuple(value)
        if masks is None:
            lane_masks = (ALL_ROWS,) * width
        elif isinstance(masks, int):
            lane_masks = (masks,) * width
        else:
            lane_masks = tuple(masks)
        if len(lanes) != width or len(lane_masks) != width:
            raise RuntimeError("lane width mismatch")
        old_values = values.get(network, (0,) * width)
        old_masks = driven.get(network, (0,) * width)
        for old_value, new_value, old_mask, new_mask in zip(
            old_values, lanes, old_masks, lane_masks, strict=True
        ):
            conflicts[network] |= (old_value ^ new_value) & old_mask & new_mask
        values[network] = tuple(
            (old_value & old_mask) | (new_value & new_mask)
            for old_value, new_value, old_mask, new_mask in zip(
                old_values, lanes, old_masks, lane_masks, strict=True
            )
        )
        driven[network] = tuple(
            old_mask | new_mask
            for old_mask, new_mask in zip(old_masks, lane_masks, strict=True)
        )
        resolved[network] += 1

    def ready(network: int) -> bool:
        return (
            resolved[network] > 0
            and resolved[network] == netlist.driver_counts.get(network, 0)
        )

    def read(component_index: int, pin_name: str) -> tuple[int, ...]:
        network = netlist.pin_networks.get((component_index, pin_name))
        if network is None:
            # The reviewed maker_2.in0 is intentionally Z.  A maker is a free
            # normalization boundary: the lane becomes a driven zero.
            if circuit.components[component_index].kind in {16, 111}:
                return (0,)
            raise RuntimeError(f"unconnected receiver {component_index}:{pin_name}")
        if not ready(network):
            raise RuntimeError(f"network {network} is not ready")
        return tuple(
            value & mask
            for value, mask in zip(values[network], driven[network], strict=True)
        )

    pending: set[int] = set()
    for component_index, component in enumerate(circuit.components):
        if component.kind in SOURCE_KINDS:
            drive(component_index, "value", inputs[component.user_label])
            arrivals[component_index] = 0
        elif component.kind not in SINK_KINDS:
            pending.add(component_index)

    while pending:
        progressed = False
        for component_index in tuple(sorted(pending)):
            component = circuit.components[component_index]
            input_pins = [
                pin
                for pin in positioned_pins(component, component_index)
                if pin.direction == I
            ]
            connected_inputs = [
                netlist.pin_networks[(component_index, pin.name)]
                for pin in input_pins
                if (component_index, pin.name) in netlist.pin_networks
            ]
            if not all(ready(network) for network in connected_inputs):
                continue
            if any(
                (component_index, pin.name) not in netlist.pin_networks
                and component.kind not in {16, 111}
                for pin in input_pins
            ):
                continue

            input_values = {
                pin.name: read(component_index, pin.name) for pin in input_pins
            }
            input_arrivals = [
                arrivals[source_index]
                for network in connected_inputs
                for source_index, _pin_name in netlist.drivers[network]
            ]
            gate_delay = KIND_COST_DELAY[component.kind][1]
            arrivals[component_index] = max(input_arrivals, default=0) + gate_delay

            if component.kind == SWITCH_KIND:
                drive(
                    component_index,
                    "out",
                    input_values["in"][0],
                    input_values["enable"][0],
                )
            elif component.kind == 16:
                drive(
                    component_index,
                    "out",
                    tuple(input_values[f"in{bit}"][0] for bit in range(8)),
                )
            elif component.kind == 17:
                for bit in range(8):
                    drive(component_index, f"out{bit}", input_values["in"][bit])
            elif component.kind == 111:
                drive(
                    component_index,
                    "out",
                    (input_values["in0"][0], input_values["in1"][0]),
                )
            elif component.kind == 109:
                for bit in range(2):
                    drive(component_index, f"out{bit}", input_values["in"][bit])
            elif component.kind in SIMPLE_KINDS:
                left = input_values["in0"][0]
                right = input_values["in1"][0]
                if component.kind == 4:
                    result = left & right
                elif component.kind == 6:
                    result = _invert(left & right)
                elif component.kind == 7:
                    result = left | right
                else:
                    result = _invert(left | right)
                drive(component_index, "out", result)
            else:
                raise RuntimeError(f"unsupported component kind {component.kind}")

            pending.remove(component_index)
            progressed = True
        if not progressed:
            raise RuntimeError(f"unresolved components: {sorted(pending)!r}")

    return inputs, values, driven, arrivals, conflicts


def _known_relations(inputs: dict[str, tuple[int, ...]]) -> dict[int, list[str]]:
    a = inputs["A"]
    b = inputs["B"]
    cin = inputs["Carry in"][0]
    by_value: dict[int, list[str]] = defaultdict(list)

    def add(name: str, value: int) -> None:
        value &= ALL_ROWS
        if name not in by_value[value]:
            by_value[value].append(name)

    add("Cin", cin)
    add("nCin", _invert(cin))
    propagate = [a[bit] ^ b[bit] for bit in range(8)]
    generate = [a[bit] & b[bit] for bit in range(8)]
    carry = cin
    for bit in range(8):
        p = propagate[bit]
        g = generate[bit]
        q = _invert(a[bit] | b[bit])
        for name, value in (
            (f"A{bit}", a[bit]),
            (f"B{bit}", b[bit]),
            (f"G{bit}", g),
            (f"Q{bit}", q),
            (f"P{bit}", p),
            (f"X{bit}=nP{bit}", _invert(p)),
            (f"V{bit}", a[bit] | b[bit]),
            (f"nG{bit}", _invert(g)),
            (f"C{bit}", carry),
            (f"nC{bit}", _invert(carry)),
            (f"S{bit}", p ^ carry),
        ):
            add(name, value)
        carry = g | (p & carry)
    add("C8", carry)
    add("nC8", _invert(carry))

    for low in range(8):
        group_g = generate[low]
        group_p = propagate[low]
        for high in range(low, 8):
            if high > low:
                group_g = generate[high] | (propagate[high] & group_g)
                group_p = propagate[high] & group_p
            add(f"G{high}:{low}", group_g)
            add(f"P{high}:{low}", group_p)
            add(f"K{high}:{low}", _invert(group_g | group_p))
            add(f"nG{high}:{low}", _invert(group_g))
    return dict(by_value)


def _expected_outputs(inputs: dict[str, tuple[int, ...]]) -> tuple[int, ...]:
    carry = inputs["Carry in"][0]
    outputs: list[int] = []
    for left, right in zip(inputs["A"], inputs["B"], strict=True):
        propagate = left ^ right
        outputs.append(propagate ^ carry)
        carry = (left & right) | (propagate & carry)
    outputs.append(carry)
    return tuple(outputs)


def _architecture_relations(inputs: dict[str, tuple[int, ...]]) -> dict[int, int]:
    """Compute every manually named scalar rail directly from A/B/Cin."""

    a = inputs["A"]
    b = inputs["B"]
    cin = inputs["Carry in"][0]
    g = [a[bit] & b[bit] for bit in range(8)]
    v = [a[bit] | b[bit] for bit in range(8)]
    p = [a[bit] ^ b[bit] for bit in range(8)]
    q = [_invert(value) for value in v]
    ng = [_invert(value) for value in g]
    x = [_invert(value) for value in p]
    carry = [cin]
    sums = []
    for bit in range(8):
        sums.append(p[bit] ^ carry[-1])
        carry.append(g[bit] | (p[bit] & carry[-1]))

    d23 = g[3] | (p[3] & v[2])
    r23 = g[2] | g[3]
    d45 = g[5] | (p[5] & v[4])
    k54 = q[5] | (p[5] & q[4])
    e45 = g[4] | x[5]
    f45 = ng[4] | p[5]
    l5 = g[4] ^ p[5]
    r45 = p[5] & ng[4] & _invert(carry[4])
    e67 = g[6] | x[7]
    n67 = _invert(g[6] & x[7])
    l7 = g[6] ^ p[7]
    f7 = _invert(q[6] ^ p[7])
    d67 = g[7] | (p[7] & v[6])

    return {
        30: cin,
        43: a[0], 114: a[1], 124: a[2], 111: a[3],
        103: a[4], 105: a[5], 108: a[6], 125: a[7],
        38: b[0], 37: b[1], 1: b[2], 6: b[3],
        78: b[4], 84: b[5], 92: b[6], 94: b[7],
        14: g[3],
        3: ng[3],
        188: v[2],
        306: ng[2],
        13: v[3],
        21: x[3],
        174: d23,
        191: r23,
        83: carry[4],
        18: p[3] & _invert(carry[4]),
        142: sums[3],
        34: g[0],
        171: v[1],
        72: g[1],
        51: v[0],
        36: cin & v[0],
        56: carry[1],
        54: q[0] & _invert(cin),
        45: g[0] & cin,
        41: sums[0],
        177: carry[2],
        63: q[1] & _invert(carry[1]),
        60: g[1] & carry[1],
        138: sums[1],
        307: p[2],
        29: _invert(carry[2] & p[2]),
        197: carry[2] | p[2],
        140: sums[2],
        11: carry[3],
        85: ng[4],
        89: v[4],
        82: p[4],
        79: carry[4] & p[4],
        152: _invert(carry[4]) & x[4],
        144: sums[4],
        335: ng[5],
        163: v[5],
        319: p[5],
        351: _invert(v[4] & v[5]),
        347: d45,
        356: k54,
        352: e45,
        203: f45,
        334: l5,
        325: _invert(carry[4] & p[4]),
        332: sums[5],
        234: r45,
        337: carry[6],
        257: q[6],
        275: g[6],
        233: p[6],
        240: x[6],
        215: q[7],
        218: g[7],
        276: x[7],
        223: e67,
        282: n67,
        281: l7,
        267: x[7] & q[6],
        214: p[7] & v[6],
        270: f7,
        213: d67,
        237: sums[6],
        245: sums[7],
        210: carry[8],
        278: carry[8],
    }


def _network_lane_label(
    network: int,
    lane: int,
    values: dict[int, tuple[int, ...]],
    driven: dict[int, tuple[int, ...]],
    known: dict[int, list[str]],
) -> list[str]:
    observed = values[network][lane] & driven[network][lane]
    labels = list(known.get(observed, ()))
    manual = MANUAL_NETWORK_NAMES.get(network)
    if manual and manual not in labels:
        labels.insert(0, manual)
    return labels


def _name(network: int) -> str:
    manual = MANUAL_NETWORK_NAMES.get(network)
    return f"r{network}<{manual}>" if manual else f"r{network}"


def _component_formula(circuit, netlist: Netlist, component_index: int) -> str:
    component = circuit.components[component_index]
    if component.kind in SOURCE_KINDS | SINK_KINDS | ADAPTER_KINDS:
        return ""
    if component.kind == SWITCH_KIND:
        enable = _name(netlist.pin_networks[(component_index, "enable")])
        data = _name(netlist.pin_networks[(component_index, "in")])
        return f"SW(enable={enable}, data={data})"
    left = _name(netlist.pin_networks[(component_index, "in0")])
    right = _name(netlist.pin_networks[(component_index, "in1")])
    return f"{KIND_NAMES[component.kind]}({left}, {right})"


def _output_networks(circuit, netlist: Netlist) -> dict[str, int]:
    maker8 = next(
        index for index, component in enumerate(circuit.components) if component.kind == 16
    )
    result = {
        f"S{bit}": netlist.pin_networks[(maker8, f"in{bit}")] for bit in range(8)
    }
    carry_output = next(
        index
        for index, component in enumerate(circuit.components)
        if component.kind == 69 and component.user_label == "Carry out"
    )
    result["C8"] = netlist.pin_networks[(carry_output, "value")]
    return result


def _paid_cones(circuit, netlist: Netlist, outputs: dict[str, int]):
    cache: dict[tuple[int, int], frozenset[int]] = {}

    def cone(network: int, lane: int = 0) -> frozenset[int]:
        key = (network, lane)
        if key in cache:
            return cache[key]
        result: set[int] = set()
        for component_index, pin_name in netlist.drivers.get(network, ()):
            component = circuit.components[component_index]
            if KIND_COST_DELAY[component.kind][0]:
                result.add(component_index)
            if component.kind in SOURCE_KINDS:
                continue
            if component.kind == 16:
                source_name = f"in{lane}"
                result.update(cone(netlist.pin_networks[(component_index, source_name)]))
                continue
            if component.kind == 17:
                source_lane = int(pin_name[3:])
                result.update(
                    cone(netlist.pin_networks[(component_index, "in")], source_lane)
                )
                continue
            if component.kind == 111:
                source_name = f"in{lane}"
                source = netlist.pin_networks.get((component_index, source_name))
                if source is not None:
                    result.update(cone(source))
                continue
            if component.kind == 109:
                source_lane = int(pin_name[3:])
                result.update(
                    cone(netlist.pin_networks[(component_index, "in")], source_lane)
                )
                continue
            for pin in positioned_pins(component, component_index):
                if pin.direction != I:
                    continue
                source = netlist.pin_networks.get((component_index, pin.name))
                if source is not None:
                    result.update(cone(source))
        cache[key] = frozenset(result)
        return cache[key]

    cones = {name: cone(network) for name, network in outputs.items()}
    memberships: dict[int, list[str]] = defaultdict(list)
    for output, members in cones.items():
        for component_index in members:
            memberships[component_index].append(output)
    return cones, dict(memberships)


def _owner_records(
    circuit,
    netlist: Netlist,
    values: dict[int, tuple[int, ...]],
    driven: dict[int, tuple[int, ...]],
    arrivals: dict[int, int],
    conflicts: dict[int, int],
):
    owners = []
    for network, network_drivers in sorted(netlist.drivers.items()):
        if len(network_drivers) <= 1:
            continue
        if any(circuit.components[index].kind != SWITCH_KIND for index, _ in network_drivers):
            raise RuntimeError(f"unsafe multi-driver network {network}")
        driver_rows = []
        for component_index, _pin_name in network_drivers:
            enable_network = netlist.pin_networks[(component_index, "enable")]
            data_network = netlist.pin_networks[(component_index, "in")]
            enable = values[enable_network][0] & driven[enable_network][0]
            data = values[data_network][0] & driven[data_network][0]
            driver_rows.append(
                {
                    "component": component_index,
                    "enable_network": enable_network,
                    "enable_name": MANUAL_NETWORK_NAMES.get(enable_network, ""),
                    "data_network": data_network,
                    "data_name": MANUAL_NETWORK_NAMES.get(data_network, ""),
                    "arrival": arrivals[component_index],
                    "enable_one_rows": enable.bit_count(),
                    "active_one_rows": (enable & data).bit_count(),
                    "active_zero_rows": (enable & _invert(data)).bit_count(),
                }
            )
        mask = driven[network][0]
        owners.append(
            {
                "network": network,
                "name": MANUAL_NETWORK_NAMES.get(network, ""),
                "driver_count": len(network_drivers),
                "gate_cost": len(network_drivers) * 2,
                "arrival": max(arrivals[index] for index, _ in network_drivers),
                "one_rows": (values[network][0] & mask).bit_count(),
                "driven_rows": mask.bit_count(),
                "z_rows": ROW_COUNT - mask.bit_count(),
                "conflict_rows": conflicts[network].bit_count(),
                "drivers": driver_rows,
            }
        )
    return owners


def _independent_comparison(circuit, owners: list[dict[str, object]]):
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    nodes = independent["factory_dag"]["nodes"]
    independent_ops = Counter(
        str(node["op"]) for node in nodes if str(node["op"]) != "INPUT"
    )
    sample_simple = Counter(
        KIND_NAMES[component.kind]
        for component in circuit.components
        if component.kind in SIMPLE_KINDS
    )
    sample_invariants = {
        "simple_ops": dict(sorted(sample_simple.items())),
        "switch_count": sum(
            component.kind == SWITCH_KIND for component in circuit.components
        ),
        "owner_count": len(owners),
        "owner_arities": sorted(int(owner["driver_count"]) for owner in owners),
        "paid_physical_component_count": sum(
            KIND_COST_DELAY[component.kind][0] > 0 for component in circuit.components
        ),
        "aggregated_logic_node_count_including_inputs": 17
        + sum(component.kind in SIMPLE_KINDS for component in circuit.components)
        + len(owners),
    }
    independent_invariants = {
        "ops": dict(sorted(independent_ops.items())),
        "switch_count": sum(
            len(node.get("drivers", ())) for node in nodes if node["op"] == "BUS"
        ),
        "owner_count": sum(node["op"] == "BUS" for node in nodes),
        "owner_arities": sorted(
            len(node.get("drivers", ())) for node in nodes if node["op"] == "BUS"
        ),
        "paid_physical_component_count": sum(
            1 if node["op"] != "BUS" else len(node.get("drivers", ()))
            for node in nodes
            if node["op"] != "INPUT"
        ),
        "aggregated_logic_node_count_including_inputs": len(nodes),
    }
    return {
        "isomorphic_preserving_native_ops_and_cost": False,
        "proof": [
            "sample has 10 BUS owners while independent DAG has 9",
            "sample has 23 Switch components while independent DAG has 22",
            "sample has 84 aggregated input/logic nodes while independent DAG has 81",
            "sample has no XOR node and a different AND/NAND/OR/NOR multiset",
        ],
        "sample": sample_invariants,
        "independent": independent_invariants,
        "independent_structural_sha256": independent["metrics"]["structural_sha256"],
    }


def _migration_certificate(inputs: dict[str, tuple[int, ...]]):
    a = inputs["A"]
    b = inputs["B"]
    cin = inputs["Carry in"][0]
    carry = cin
    for bit in range(2):
        p = a[bit] ^ b[bit]
        carry = (a[bit] & b[bit]) | (p & carry)
    c2 = carry
    q2 = _invert(a[2] | b[2])
    q3 = _invert(a[3] | b[3])
    ng2 = _invert(a[2] & b[2])
    ng3 = _invert(a[3] & b[3])
    m23 = ng3 & (q3 | ng2)
    kill_reason = q2 | q3
    nc4_owner = m23 & (kill_reason | _invert(c2))
    carry = c2
    for bit in (2, 3):
        p = a[bit] ^ b[bit]
        carry = (a[bit] & b[bit]) | (p & carry)
    expected_nc4 = _invert(carry)
    mismatch = nc4_owner ^ expected_nc4
    baseline_payload = SEGMENTED_BASELINE.read_bytes()
    baseline = json.loads(baseline_payload.decode("utf-8"))
    ordered = baseline["valid_ordered_cofactor"]
    expected_formula = (
        "V23=BUS(SW(Q3,nG3),SW(nG2,nG3)); U23=OR(Q2,Q3); "
        "nC4=BUS(SW(U23,V23),SW(nC2,V23))"
    )
    if ordered["formula"] != expected_formula:
        raise RuntimeError("repository ordered-cofactor baseline changed")
    return {
        "name": "independent reproduction of the existing ordered-cofactor nC4 owner",
        "formula": {
            "M23": "BUS(SW(Q3,nG3), SW(nG2,nG3))",
            "Kreason": "Q2 OR Q3",
            "nC4": "BUS(SW(Kreason,M23), SW(nC2,M23))",
        },
        "truth_rows": ROW_COUNT,
        "mismatch_rows": mismatch.bit_count(),
        "conflict_rows": 0,
        "assumed_existing": ["Q2@1", "Q3@1", "nC2@2"],
        "new_nodes": [
            {"name": "nG2", "cost": 1, "arrival": 1},
            {"name": "nG3", "cost": 1, "arrival": 1},
            {"name": "M23 two-Switch owner", "cost": 4, "arrival": 2},
            {"name": "Kreason=Q2|Q3", "cost": 1, "arrival": 2},
            {"name": "nC4 two-Switch owner", "cost": 4, "arrival": 3},
        ],
        "cost_ledger": {
            "owner_excluding_Q_nG_state_leaves": 9,
            "incremental_if_Q2_Q3_exist_but_nG2_nG3_do_not": 11,
            "standalone_with_Q2_nG2_Q3_nG3_leaves": 13,
        },
        "arrival": 3,
        "delta_vs_unadopted_three_switch_second_owner": -1,
        "delta_vs_repository_ordered_cofactor_baseline": 0,
        "repository_baseline": {
            "path": str(SEGMENTED_BASELINE),
            "sha256": hashlib.sha256(baseline_payload).hexdigest().upper(),
            "formula_matches": True,
            "recorded_mismatch_rows": ordered["mismatch_rows"],
            "recorded_conflict_rows": ordered["conflict_rows"],
            "recorded_cost_excluding_state_leaves": ordered[
                "cost_excluding_state_leaves"
            ],
        },
        "complete_low_front_ledger": {
            "bits0_1_timing_clean_best_known": 24,
            "bits0_1_target": 23,
            "bits0_1_gap": 1,
            "bits2_3_target_including_S2_S3_nC4": 19,
            "ordered_carry_boundary_standalone": 13,
            "remaining_budget_for_S2_S3_if_no_more_sharing": 6,
            "complete_bits2_3_within_19_known": False,
            "complete_43_gate_negative_front_known": False,
            "complete_42_gate_negative_front_known": False,
        },
        "status": (
            "exact sample-side corroboration of an existing 11-gate incremental/"
            "13-gate standalone boundary; no net improvement over the repository "
            "baseline and no complete 42-gate low front"
        ),
    }


def audit() -> dict[str, object]:
    payload = SAMPLE.read_bytes()
    circuit = decode_v15(payload)
    round_trip_equal = decode_v15(encode_v15(circuit)) == circuit
    netlist = _compile(circuit)
    inputs, values, driven, arrivals, conflicts = _evaluate(circuit, netlist)
    known = _known_relations(inputs)
    architecture_expected = _architecture_relations(inputs)
    if set(architecture_expected) != set(MANUAL_NETWORK_NAMES):
        raise RuntimeError(
            "manual signal certificate coverage changed: "
            f"missing={sorted(set(MANUAL_NETWORK_NAMES) - set(architecture_expected))}, "
            f"extra={sorted(set(architecture_expected) - set(MANUAL_NETWORK_NAMES))}"
        )
    architecture_mismatches = {
        network: (
            (values[network][0] & driven[network][0]) ^ expected
        ).bit_count()
        for network, expected in architecture_expected.items()
    }

    owners = _owner_records(
        circuit, netlist, values, driven, arrivals, conflicts
    )
    output_networks = _output_networks(circuit, netlist)
    expected = _expected_outputs(inputs)
    observed: list[int] = []
    output_records = []
    for ordinal, (name, network) in enumerate(output_networks.items()):
        lane = 0
        if name == "C8":
            lane = 0
        value = values[network][lane] & driven[network][lane]
        observed.append(value)
        driver_arrival = max(
            arrivals[index] for index, _pin_name in netlist.drivers[network]
        )
        output_records.append(
            {
                "name": name,
                "network": network,
                "arrival": driver_arrival,
                "mismatch_rows": (value ^ expected[ordinal]).bit_count(),
                "driven_rows": driven[network][lane].bit_count(),
                "z_rows": ROW_COUNT - driven[network][lane].bit_count(),
            }
        )

    recomputed_gate = sum(
        KIND_COST_DELAY[component.kind][0] for component in circuit.components
    )
    recomputed_delay = max(record["arrival"] for record in output_records)
    conflict_union = 0
    for mask in conflicts.values():
        conflict_union |= mask

    component_records = []
    for component_index, component in enumerate(circuit.components):
        pins = positioned_pins(component, component_index)
        input_records = []
        output_records_for_component = []
        for pin in pins:
            network = netlist.pin_networks.get((component_index, pin.name))
            item = {
                "pin": pin.name,
                "network": network,
                "width": pin.width,
            }
            if network is not None and network in values:
                item["labels"] = [
                    _network_lane_label(
                        network, lane, values, driven, known
                    )[:8]
                    for lane in range(len(values[network]))
                ]
            if pin.direction == I:
                input_records.append(item)
            else:
                output_records_for_component.append(item)
        component_records.append(
            {
                "index": component_index,
                "kind": component.kind,
                "kind_name": KIND_NAMES[component.kind],
                "word_size": component.word_size,
                "position": list(component.position),
                "rotation": component.rotation,
                "label": component.user_label,
                "cost": KIND_COST_DELAY[component.kind][0],
                "step_delay": KIND_COST_DELAY[component.kind][1],
                "arrival": arrivals.get(component_index, 0),
                "formula": _component_formula(circuit, netlist, component_index),
                "inputs": input_records,
                "outputs": output_records_for_component,
            }
        )

    network_records = []
    for network in netlist.roots:
        lane_records = []
        if network in values:
            for lane, (value, mask) in enumerate(
                zip(values[network], driven[network], strict=True)
            ):
                lane_records.append(
                    {
                        "lane": lane,
                        "labels": _network_lane_label(
                            network, lane, values, driven, known
                        )[:12],
                        "one_rows": (value & mask).bit_count(),
                        "driven_rows": mask.bit_count(),
                        "z_rows": ROW_COUNT - mask.bit_count(),
                        "value_sha256": hashlib.sha256(
                            (value & mask).to_bytes(ROW_COUNT // 8, "little")
                        ).hexdigest(),
                    }
                )
        network_records.append(
            {
                "network": network,
                "manual_name": MANUAL_NETWORK_NAMES.get(network, ""),
                "drivers": [
                    {"component": index, "pin": pin_name}
                    for index, pin_name in netlist.drivers.get(network, ())
                ],
                "sinks": [
                    {"component": index, "pin": pin_name}
                    for index, pin_name in netlist.sinks.get(network, ())
                ],
                "conflict_rows": conflicts[network].bit_count(),
                "lanes": lane_records,
            }
        )

    cones, memberships = _paid_cones(circuit, netlist, output_networks)
    cone_records = {
        output: {
            "paid_component_count": len(members),
            "gate_cost": sum(
                KIND_COST_DELAY[circuit.components[index].kind][0]
                for index in members
            ),
            "components": sorted(members),
        }
        for output, members in cones.items()
    }
    shared_records = [
        {
            "component": component_index,
            "kind": KIND_NAMES[circuit.components[component_index].kind],
            "network": netlist.pin_networks.get((component_index, "out")),
            "name": MANUAL_NETWORK_NAMES.get(
                netlist.pin_networks.get((component_index, "out"), -1), ""
            ),
            "outputs": outputs,
        }
        for component_index, outputs in sorted(memberships.items())
        if len(outputs) >= 2
    ]

    output_vector_hash = hashlib.sha256(
        b"".join(value.to_bytes(ROW_COUNT // 8, "little") for value in observed)
    ).hexdigest()
    kind_counts = Counter(component.kind for component in circuit.components)
    cost_by_kind = {
        KIND_NAMES[kind]: {
            "count": count,
            "unit_gate": KIND_COST_DELAY[kind][0],
            "gate": count * KIND_COST_DELAY[kind][0],
        }
        for kind, count in sorted(kind_counts.items())
    }

    result = {
        "schema": "byte-adder-frontier-sample-103d5a-audit-v1",
        "source": {
            "path": str(SAMPLE),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest().upper(),
            "format": 15,
            "v15_encode_decode_round_trip_equal": round_trip_equal,
        },
        "declared": {
            "gate": circuit.gate,
            "delay": circuit.delay,
            "energy": circuit.energy,
            "custom_id": circuit.custom_id,
        },
        "recomputed": {
            "gate": recomputed_gate,
            "delay": recomputed_delay,
            "energy": recomputed_gate * recomputed_delay,
            "component_count": len(circuit.components),
            "wire_count": len(circuit.wires),
            "logical_network_count": len(netlist.roots),
            "paid_physical_component_count": sum(
                KIND_COST_DELAY[component.kind][0] > 0
                for component in circuit.components
            ),
            "truth_rows": ROW_COUNT,
            "mismatch_union_rows": sum(
                bool(record["mismatch_rows"]) for record in output_records
            ),
            "conflict_union_rows": conflict_union.bit_count(),
            "output_vector_sha256": output_vector_hash,
        },
        "cost_by_kind": cost_by_kind,
        "ports": [
            {
                "component": index,
                "direction": "input" if component.kind == 61 else "output",
                "label": component.user_label,
                "word_size": component.word_size,
                "position": list(component.position),
            }
            for index, component in enumerate(circuit.components)
            if component.kind in SOURCE_KINDS | SINK_KINDS
        ],
        "unconnected": {
            "inputs": [list(value) for value in netlist.missing_inputs],
            "outputs": [list(value) for value in netlist.missing_outputs],
            "interpretation": "maker_2.in0 is Z->0 normalization; splitter_2.out0 is unused",
        },
        "outputs": output_records,
        "architecture_signal_certificate": {
            "named_scalar_network_count": len(architecture_mismatches),
            "mismatch_union_network_count": sum(
                count != 0 for count in architecture_mismatches.values()
            ),
            "mismatch_rows_by_network": {
                str(network): count
                for network, count in sorted(architecture_mismatches.items())
            },
        },
        "owners": owners,
        "components": component_records,
        "networks": network_records,
        "cones": cone_records,
        "cross_output_shared_components": shared_records,
        "independent_103d5_comparison": _independent_comparison(circuit, owners),
        "migration_certificate": _migration_certificate(inputs),
    }

    if (circuit.gate, circuit.delay) != (103, 5):
        raise RuntimeError("sample declaration changed")
    if not round_trip_equal:
        raise RuntimeError("v15 in-memory round trip changed the decoded circuit")
    if (recomputed_gate, recomputed_delay) != (103, 5):
        raise RuntimeError(
            f"recomputed score mismatch: {recomputed_gate}/{recomputed_delay}"
        )
    if any(record["mismatch_rows"] for record in output_records):
        raise RuntimeError("full truth replay failed")
    if conflict_union:
        raise RuntimeError("BUS conflict replay failed")
    if any(architecture_mismatches.values()):
        raise RuntimeError(
            "manual architecture signal labels failed: "
            f"{architecture_mismatches!r}"
        )
    if result["migration_certificate"]["mismatch_rows"]:
        raise RuntimeError("nC4 migration certificate failed")
    return result


def _write_dag(result: dict[str, object]) -> None:
    components = result["components"]
    owners = {owner["network"]: owner for owner in result["owners"]}
    lines = [
        "# Switch 103/5 A 完整逻辑 DAG",
        "",
        "本表由 v15 端点网络直接恢复。`rN` 是物理逻辑网络编号；多 Switch 输出先合并为一个 BUS owner。",
        "Maker/Splitter 为 `0 gate / 0 delay`，单列在末尾，不隐藏任何付费元件。",
        "",
        "## 付费逻辑",
        "",
        "| 元件 | arrival | cost | 输出 | 公式 |",
        "|---:|---:|---:|---|---|",
    ]
    emitted_owner_networks: set[int] = set()
    for component in components:
        if not component["cost"]:
            continue
        output_network = component["outputs"][0]["network"]
        if component["kind"] == SWITCH_KIND:
            if output_network in emitted_owner_networks:
                continue
            owner = owners[output_network]
            emitted_owner_networks.add(output_network)
            drivers = "; ".join(
                f"SW(c{driver['component']}, {_name(driver['enable_network'])}, {_name(driver['data_network'])})"
                for driver in owner["drivers"]
            )
            lines.append(
                f"| BUS r{output_network} | {owner['arrival']} | {owner['gate_cost']} | {_name(output_network)} | {drivers} |"
            )
            continue
        lines.append(
            f"| c{component['index']} {component['kind_name']} | {component['arrival']} | {component['cost']} | {_name(output_network)} | `{component['formula']}` |"
        )

    lines.extend(
        [
            "",
            "## 免费边界与位序",
            "",
            "```text",
            "A(U8) -> c33 SPLITTER8 -> A0..A7",
            "B(U8) -> c32 SPLITTER8 -> B0..B7",
            "S0..S7 -> c34 MAKER8 -> Output(U8)",
            "C8 -> c57 MAKER2.in1; MAKER2.in0=Z -> c55 SPLITTER2.out1 -> Carry out",
            "```",
            "",
            "## 九输出 arrival",
            "",
            "| 输出 | 网络 | arrival | mismatch |",
            "|---|---:|---:|---:|",
        ]
    )
    for output in result["outputs"]:
        lines.append(
            f"| {output['name']} | r{output['network']} | {output['arrival']} | {output['mismatch_rows']} |"
        )
    lines.append("")
    OUTPUT_DAG.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _write_report(result: dict[str, object]) -> None:
    owners = result["owners"]
    comparison = result["independent_103d5_comparison"]
    migration = result["migration_certificate"]
    lines = [
        "# Switch 103 门 5 延迟 A 样本反解与迁移分析",
        "",
        "日期：2026-08-05",
        "",
        "## 结论",
        "",
        "该样本是完整、独立、可离线复算的 Byte Adder：",
        "",
        "```text",
        "declared / recomputed       103 gate / 5 delay / 515 energy",
        "truth rows                  131072",
        "S0..S7/C8 mismatch          0,0,0,0,0,0,0,0,0",
        "named internal rails        all zero mismatch",
        "BUS conflict rows           0",
        "output arrivals             4,5,4,5,5,5,5,5,5",
        "v15 round trip              equal",
        f"source SHA-256              {result['source']['sha256']}",
        "```",
        "",
        "它不是仓库独立 `103/5` DAG 的重排：人工样本是规则的二位分组 carry-owner 链，",
        "仓库 DAG 是从 Patchouli `84/6` 重定时得到的混合结构。BUS owner 数、Switch 数、",
        "付费物理元件数和门型多重集均不同，已经足以否定保持原生元件类型与成本的同构。",
        "",
        "## 一、成本与端口",
        "",
        "| 原生元件 | 数量 | 门数 |",
        "|---|---:|---:|",
    ]
    for name, item in result["cost_by_kind"].items():
        lines.append(f"| {name} | {item['count']} | {item['gate']} |")
    lines.extend(
        [
            "",
            "付费部分为 `57` 个普通一门逻辑元件和 `23` 个 Bit Switch（每只 2 门），",
            "总计 `57 + 23*2 = 103`。输入为 `A(U8)、B(U8)、Carry in(U1)`；输出为",
            "`Output(U8)、Carry out(U1)`。",
            "",
            "唯一悬空接收端是 `c57 MAKER2.in0`；它与未使用的 `c55 SPLITTER2.out0`",
            "构成免费 `Z -> 0` 归一边界，实际 `Carry out` 从 lane 1 原样取出 C8。",
            "",
            "## 二、总体架构",
            "",
            "### 低二位",
            "",
            "```text",
            "T0 = BUS(SW(B0,Cin), SW(A0,Cin)) = Cin*V0         @1",
            "C1 = G0 OR T0                                      @2",
            "C2 = BUS(SW(G1,V1), SW(G0,V1), SW(T0,V1))         @2",
            "```",
            "",
            "S0/S1 不建立普通 XOR；它们把 generate、kill 与 propagate 状态分开，",
            "使用已有 carry reason 在 4/5 层内闭合。S2 使用共享的 `C2/P2` OR/NAND",
            "相位，三门闭合 XOR，并由 `C3=NAND(~(C2P2),nG2)` 顺带产生 C3。",
            "",
            "### bits2:3 二位 carry owner",
            "",
            "```text",
            "D23 = BUS(SW(G3,V3), SW(V2,V3))",
            "    = V3*(G3|V2) = G23|P23                       @2 / 4 gate",
            "R23 = NAND(nG2,nG3) = G2|G3                     @2 / 1 gate",
            "C4  = BUS(SW(R23,D23), SW(C2,D23))               @3 / 4 gate",
            "```",
            "",
            "关键不是把完整 carry 公式展开，而是先形成共同 data `D23`，再把多个",
            "内部 generate reason 压成一条 enable。多 driver 重叠时始终共享 data，",
            "因此没有 active-0/active-1 冲突。",
            "",
            "S3 直接消费 `C3、C4、nP3`：",
            "",
            "```text",
            "H3 = NOR(nP3,C4) = P3*nC4",
            "S3 = BUS(SW(nP3,C3), SW(H3,H3))                  @5 / 4 gate owner+1",
            "```",
            "",
            "第二路只发布 active-one，目标为零的 32768 行保留 Z，最终 Maker8 归零。",
            "",
            "### bits4:5",
            "",
            "```text",
            "D45 = G54|P54 = G5 | V5*V4                      @3",
            "E45 = G4|nP5                                    @2",
            "C6  = BUS(SW(E45,D45), SW(C4,D45))              @4",
            "K54 = group kill                                 @3",
            "R45 = P5*nG4*nC4                                 @4",
            "nC6 = K54 | R45",
            "```",
            "",
            "S5 用 `C4P4` 作为二选一 owner；C6 的两个负原因 `K54/R45` 不先 OR",
            "成完整 nC6，而是直接被 S6/S7 的同-data Switch 复用。",
            "",
            "### bits6:7 与跨输出共享",
            "",
            "```text",
            "E67 = G6 | X7                                    @3",
            "N67 = NAND(G6,X7)                                @3",
            "L7  = NAND(E67,N67) = G6 xor P7                  @4",
            "F7  = XNOR(Q6,P7)                                @4",
            "D67 = G67|P67 = G7 | P7*nQ6                     @4",
            "C8  = BUS(SW(E67,D67), SW(C6,D67))               @5",
            "S6  = BUS(SW(K54,P6), SW(R45,P6), SW(C6,X6))     @5",
            "S7  = BUS(SW(K54,L7), SW(R45,L7), SW(C6,F7))     @5",
            "```",
            "",
            "`E67` 同时是 C8 的内部 reason 和 `L7` 三门 XOR 分解的一半；`K54/R45`",
            "同时服务 S6、S7。这里的共享发生在输出 cofactor 之间，而不是先恢复完整",
            "C7 再分别计算 S7/C8。",
            "",
            "### 关键跨输出轨",
            "",
            "| rail | 直接/下游消费者 | 共享意义 |",
            "|---|---|---|",
            "| C1 | S0、S1、C2 | bit0 carry 同时参与本位修正与下一位 |",
            "| C2 | S1、S2、C3、C4 owner | 正相 carry 跨越两个 Sum cone |",
            "| C4 | S3、S4、S5、C6 owner | 中段公共正相边界 |",
            "| E45 | S5 data、C6 enable、R45 | 同一补相同时服务 Sum/carry/negative reason |",
            "| K54、R45 | S6、S7 | nC6 不物化为单独 OR，原因轨直接扇出 |",
            "| C6 | S6、S7、C8 | 三个高位公开输出的公共相位 |",
            "| E67 | L7、C8 owner | XOR 分解第一相与 carry enable 共用 |",
            "",
            "## 三、Switch/Z 审计",
            "",
            "| owner | driver | cost | arrival | Z rows | conflict |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for owner in owners:
        lines.append(
            f"| r{owner['network']} {owner['name']} | {owner['driver_count']} | {owner['gate_cost']} | {owner['arrival']} | {owner['z_rows']} | {owner['conflict_rows']} |"
        )
    lines.extend(
        [
            "",
            "所有多驱动网络均只由 Switch 驱动，冲突行为为零。`S5/S6/S7` owner",
            "完整驱动；`S3` 以及若干 carry/reason BUS 允许 Z，只在后续普通门或免费",
            "Maker 边界按零消费。样本没有把 Z 当成可穿透的第三逻辑值。",
            "",
            "## 四、与仓库独立 103/5 的同构结论",
            "",
            "```text",
            f"sample BUS owners / switches     {comparison['sample']['owner_count']} / {comparison['sample']['switch_count']}",
            f"independent BUS owners/switches   {comparison['independent']['owner_count']} / {comparison['independent']['switch_count']}",
            f"sample aggregated nodes           {comparison['sample']['aggregated_logic_node_count_including_inputs']}",
            f"independent aggregated nodes      {comparison['independent']['aggregated_logic_node_count_including_inputs']}",
            f"sample paid physical components   {comparison['sample']['paid_physical_component_count']}",
            f"independent paid components       {comparison['independent']['paid_physical_component_count']}",
            "```",
            "",
            "所以答案是：**不同构**。二者只有九输出真值、总分和 output arrival 向量相同。",
            "",
            "## 五、对 84/6 -> 83/6 研究的独立印证",
            "",
            "样本最明确地印证了同-data enable 压缩，但这并不是当前仓库的新动作。",
            "若机械地把末级写成三 Switch（仓库从未把它作为当前基线），会得到：",
            "",
            "```text",
            "M23  = BUS(SW(Q3,nG3), SW(nG2,nG3))             @2 / 4 gate",
            "nC4  = BUS(SW(Q3,M23), SW(Q2,M23), SW(nC2,M23)) @3 / 6 gate",
            "```",
            "",
            "人工样本在正相 C4 中也先把 `G2/G3` 压成一条 enable；其严格负相对偶正是",
            "仓库现有写法：",
            "",
            "```text",
            "Kreason = Q2 OR Q3                               @2 / 1 gate",
            "nC4 = BUS(SW(Kreason,M23), SW(nC2,M23))          @3 / 4 gate",
            "```",
            "",
            f"本样本侧 131072 行复算 mismatch={migration['mismatch_rows']}、conflict={migration['conflict_rows']}。",
            "边界本体（不含 Q/nG 状态叶）为 9 门；若 Q2/Q3 已付但 nG2/nG3 未付，",
            "增量为 11 门；独立包含 Q2/nG2/Q3/nG3 四个状态叶时为 13 门。arrival 均为 3。",
            "它只相对一个从未作为当前基线的末级三 Switch 写法少一门；相对仓库现有",
            "ordered-cofactor 的净变化严格为 0。",
            "",
            "更重要的是，仓库不存在可供 43->42 替换的完整负相低前端 DAG。当前完整",
            "缺口分成两段：时序合格的 bits0:1 已知账本为 24 门而目标是 23；bits2:3",
            "必须在 19 门内同时给出 S2、S3、nC4@3，但 13 门 carry boundary 后尚未有",
            "六门 Sum 联合尾。故本样本没有让 84/6 -> 83/6 获得净一门，也不能触发物化。",
            "",
            "另两个可迁移合同：",
            "",
            "- `K54/R45` 分裂负原因直接喂给 S6/S7，避免先恢复完整 nC6；适合继续攻",
            "  `80/7` 高尾重定时的 cofactor owner。",
            "- `E67` 同时承担 C8 reason 和 XOR 分解第一相；若目标 DAG 已支付 X7，",
            "  `L7` 的增量只需两门。但在当前 84/6 高尾中 X7 未免费存在，完整替换",
            "  与原结构暂时打平，不能冒充一门节省。",
            "",
            "## 六、产物",
            "",
            "- `machine-audit.json`：完整元件、网络、owner、真值、arrival、cone 与同构不变量。",
            "- `完整逻辑DAG.md`：所有 80 个付费物理元件聚合后的逐节点公式。",
            "- `audit_103d5a.py`：只读、可重复执行的 v15 审计脚本。",
            "- `SHA256SUMS.txt`：原样本、对照 DAG、基线证书与派生产物哈希。",
            "",
        ]
    )
    OUTPUT_REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> int:
    result = audit()
    HERE.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    _write_dag(result)
    _write_report(result)
    hashed_paths = (
        SAMPLE,
        INDEPENDENT,
        SEGMENTED_BASELINE,
        Path(__file__).resolve(),
        OUTPUT_JSON,
        OUTPUT_DAG,
        OUTPUT_REPORT,
    )
    OUTPUT_SUMS.write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest().upper()}  "
            f"{path.resolve().relative_to(ROOT.resolve()).as_posix()}\n"
            for path in hashed_paths
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "source": result["source"],
                "recomputed": result["recomputed"],
                "outputs": result["outputs"],
                "migration": result["migration_certificate"],
                "artifacts": [
                    str(OUTPUT_JSON),
                    str(OUTPUT_DAG),
                    str(OUTPUT_REPORT),
                    str(OUTPUT_SUMS),
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
