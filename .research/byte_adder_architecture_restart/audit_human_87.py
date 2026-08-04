"""Audit and label a physical Byte Adder circuit without searching circuits.

The script evaluates all 131072 input rows once as Python bitsets.  It records
the exact value/driven state of every physical network, labels signals that
match useful adder relations, and emits a topology/arrival/fanout ledger.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from tc_save_lab.codec import decode_v15  # noqa: E402
from tc_save_lab.pins import I, O, T, positioned_pins  # noqa: E402
from tc_save_lab.simulate import (  # noqa: E402
    CONSTANT_KINDS,
    SINK_KINDS,
    SOURCE_KINDS,
    _compile,
)


ROW_COUNT = 256 * 256 * 2
ALL_ROWS = (1 << ROW_COUNT) - 1
DEFAULT_INPUT = Path(__file__).with_name("source_human87") / "circuit.data"
DEFAULT_OUTPUT = Path(__file__).with_name("human-87-audit.json")

KIND_NAMES = {
    1: "OFF",
    2: "ON",
    3: "NOT",
    4: "AND",
    5: "AND3",
    6: "NAND",
    7: "OR",
    8: "OR3",
    9: "NOR",
    10: "XOR",
    11: "XNOR",
    12: "SWITCH",
    16: "MAKER8",
    17: "SPLITTER8",
    61: "INPUT",
    69: "OUTPUT",
}

KIND_COST_DELAY = {
    1: (0, 0),
    2: (0, 0),
    3: (1, 1),
    4: (1, 1),
    5: (3, 2),
    6: (1, 1),
    7: (1, 1),
    8: (3, 2),
    9: (1, 1),
    10: (3, 2),
    11: (5, 4),
    12: (2, 1),
    16: (0, 0),
    17: (0, 0),
    61: (0, 0),
    69: (0, 0),
}


def _pattern(half_period: int) -> int:
    block = "0" * half_period + "1" * half_period
    return int(block * (ROW_COUNT // (2 * half_period)), 2)


def _inputs() -> dict[str, tuple[int, ...]]:
    return {
        "Carry in": (_pattern(1),),
        "B": tuple(_pattern(2 << bit) for bit in range(8)),
        "A": tuple(_pattern(512 << bit) for bit in range(8)),
    }


def _invert(value: int) -> int:
    return (~value) & ALL_ROWS


def _pin_width(circuit, component_index: int, pin_name: str) -> int:
    for pin in positioned_pins(circuit.components[component_index], component_index):
        if pin.name == pin_name:
            return pin.width
    raise KeyError((component_index, pin_name))


def _known_relations(inputs: dict[str, tuple[int, ...]]) -> dict[int, list[str]]:
    a = inputs["A"]
    b = inputs["B"]
    cin = inputs["Carry in"][0]
    relations: dict[str, int] = {"Cin": cin, "nCin": _invert(cin)}
    carry = cin
    for bit in range(8):
        g = a[bit] & b[bit]
        q = _invert(a[bit] | b[bit])
        p = a[bit] ^ b[bit]
        relations.update(
            {
                f"A{bit}": a[bit],
                f"B{bit}": b[bit],
                f"G{bit}": g,
                f"Q{bit}": q,
                f"P{bit}": p,
                f"nP{bit}": _invert(p),
                f"V{bit}": a[bit] | b[bit],
                f"N{bit}": _invert(g),
                f"C{bit}": carry,
                f"nC{bit}": _invert(carry),
                f"S{bit}": p ^ carry,
            }
        )
        carry = g | (p & carry)
    relations["C8"] = carry
    relations["nC8"] = _invert(carry)

    # Adjacent-pair carry descriptors are common in both reviewed 87/6 DAGs.
    for low in range(7):
        high = low + 1
        group_g = (a[high] & b[high]) | (
            (a[high] ^ b[high]) & (a[low] & b[low])
        )
        group_p = (a[high] ^ b[high]) & (a[low] ^ b[low])
        group_k = _invert(group_g | group_p)
        relations[f"G{high}{low}"] = group_g
        relations[f"P{high}{low}"] = group_p
        relations[f"K{high}{low}"] = group_k

    by_value: dict[int, list[str]] = defaultdict(list)
    for name, value in relations.items():
        by_value[value].append(name)
    return dict(by_value)


def _evaluate(circuit, compiled):
    inputs = _inputs()
    values: dict[int, tuple[int, ...]] = {}
    driven: dict[int, tuple[int, ...]] = {}
    resolved: dict[int, int] = defaultdict(int)
    component_arrival: dict[int, int] = {}
    switch_rows: dict[int, dict[str, int]] = {}
    conflict_rows = 0

    def drive(
        component_index: int,
        pin_name: str,
        value: int | Iterable[int],
        masks: int | Iterable[int] | None = None,
    ) -> None:
        nonlocal conflict_rows
        network = compiled.pin_networks.get((component_index, pin_name))
        if network is None:
            return
        width = _pin_width(circuit, component_index, pin_name)
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
            old_values, lanes, old_masks, lane_masks
        ):
            conflict_rows |= (old_value ^ new_value) & old_mask & new_mask
        values[network] = tuple(
            (old_value & old_mask) | (new_value & new_mask)
            for old_value, new_value, old_mask, new_mask in zip(
                old_values, lanes, old_masks, lane_masks
            )
        )
        driven[network] = tuple(
            old_mask | new_mask for old_mask, new_mask in zip(old_masks, lane_masks)
        )
        resolved[network] += 1

    def ready(network: int) -> bool:
        return (
            resolved[network] > 0
            and resolved[network] == compiled.network_driver_counts.get(network, 0)
        )

    def read(component_index: int, pin_name: str) -> tuple[int, ...]:
        network = compiled.pin_networks[(component_index, pin_name)]
        if not ready(network):
            raise RuntimeError(f"network {network} is not ready")
        return tuple(
            value & mask for value, mask in zip(values[network], driven[network])
        )

    pending: set[int] = set()
    for index, component in enumerate(circuit.components):
        if component.kind in SOURCE_KINDS:
            raw = inputs[component.user_label]
            output_pins = [
                pin
                for pin in positioned_pins(component, index)
                if pin.direction in {O, T}
            ]
            if len(output_pins) == 1:
                drive(index, output_pins[0].name, raw)
            else:
                for bit, pin in enumerate(output_pins):
                    drive(index, pin.name, raw[bit])
            component_arrival[index] = 0
        elif component.kind in CONSTANT_KINDS:
            number = component.init_data if component.kind == 46 else int(component.kind == 2)
            drive(index, "out", number)
            component_arrival[index] = 0
        elif component.kind not in SINK_KINDS:
            pending.add(index)

    while pending:
        progressed = False
        for index in tuple(pending):
            component = circuit.components[index]
            input_pins = [
                pin for pin in positioned_pins(component, index) if pin.direction == I
            ]
            input_networks = [compiled.pin_networks[(index, pin.name)] for pin in input_pins]
            if not all(ready(network) for network in input_networks):
                continue
            input_values = {pin.name: read(index, pin.name) for pin in input_pins}
            input_arrivals = []
            for network in input_networks:
                drivers = []
                for source_index, source_component in enumerate(circuit.components):
                    for source_pin in positioned_pins(source_component, source_index):
                        if source_pin.direction not in {O, T}:
                            continue
                        if compiled.pin_networks.get((source_index, source_pin.name)) == network:
                            drivers.append(component_arrival[source_index])
                input_arrivals.extend(drivers)
            delay = KIND_COST_DELAY[component.kind][1]
            component_arrival[index] = max(input_arrivals, default=0) + delay

            if component.kind == 12:
                enable = input_values["enable"][0]
                data = input_values["in"][0]
                drive(index, "out", data, enable)
                switch_rows[index] = {
                    "enable_one": enable.bit_count(),
                    "data_one": data.bit_count(),
                    "active_one": (enable & data).bit_count(),
                }
            elif component.kind == 16:
                drive(index, "out", tuple(input_values[f"in{bit}"][0] for bit in range(8)))
            elif component.kind == 17:
                for bit in range(8):
                    drive(index, f"out{bit}", input_values["in"][bit])
            else:
                left = input_values.get("in0", input_values.get("in", (0,)))[0]
                right = input_values.get("in1", (0,))[0]
                if component.kind == 3:
                    result = _invert(left)
                elif component.kind in {4, 5}:
                    result = left & right
                    if "in2" in input_values:
                        result &= input_values["in2"][0]
                elif component.kind == 6:
                    result = _invert(left & right)
                elif component.kind in {7, 8}:
                    result = left | right
                    if "in2" in input_values:
                        result |= input_values["in2"][0]
                elif component.kind == 9:
                    result = _invert(left | right)
                elif component.kind == 10:
                    result = left ^ right
                elif component.kind == 11:
                    result = _invert(left ^ right)
                else:
                    raise RuntimeError(f"unsupported kind {component.kind}")
                drive(index, "out", result)
            pending.remove(index)
            progressed = True
        if not progressed:
            raise RuntimeError(f"unresolved components: {sorted(pending)}")

    return inputs, values, driven, component_arrival, switch_rows, conflict_rows


def audit(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    circuit = decode_v15(payload)
    compiled = _compile(circuit)
    inputs, values, driven, arrivals, switch_rows, conflict_rows = _evaluate(
        circuit, compiled
    )
    known = _known_relations(inputs)

    network_drivers: dict[int, list[dict[str, object]]] = defaultdict(list)
    network_sinks: dict[int, list[dict[str, object]]] = defaultdict(list)
    for index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, index):
            network = compiled.pin_networks.get((index, pin.name))
            if network is None:
                continue
            record = {
                "component": index,
                "kind": KIND_NAMES.get(component.kind, str(component.kind)),
                "pin": pin.name,
            }
            if pin.direction in {O, T}:
                network_drivers[network].append(record)
            else:
                network_sinks[network].append(record)

    components: list[dict[str, object]] = []
    for index, component in enumerate(circuit.components):
        if component.kind in SINK_KINDS | SOURCE_KINDS:
            continue
        output_records = []
        for pin in positioned_pins(component, index):
            if pin.direction not in {O, T}:
                continue
            network = compiled.pin_networks.get((index, pin.name))
            if network is None:
                continue
            lane_values = values[network]
            lane_masks = driven[network]
            output_records.append(
                {
                    "pin": pin.name,
                    "network": network,
                    "labels": known.get(lane_values[0] & lane_masks[0], []),
                    "value_one": (lane_values[0] & lane_masks[0]).bit_count(),
                    "driven": lane_masks[0].bit_count(),
                    "z": ROW_COUNT - lane_masks[0].bit_count(),
                    "drivers": network_drivers[network],
                    "sinks": network_sinks[network],
                }
            )
        input_records = []
        for pin in positioned_pins(component, index):
            if pin.direction != I:
                continue
            network = compiled.pin_networks[(index, pin.name)]
            lane_value = values[network][0] & driven[network][0]
            input_records.append(
                {
                    "pin": pin.name,
                    "network": network,
                    "labels": known.get(lane_value, []),
                    "drivers": network_drivers[network],
                }
            )
        components.append(
            {
                "index": index,
                "kind": component.kind,
                "kind_name": KIND_NAMES.get(component.kind, str(component.kind)),
                "position": list(component.position),
                "cost": KIND_COST_DELAY[component.kind][0],
                "arrival": arrivals[index],
                "inputs": input_records,
                "outputs": output_records,
                "switch_rows": switch_rows.get(index),
            }
        )

    output_records = []
    for index, component in enumerate(circuit.components):
        if component.kind not in SINK_KINDS:
            continue
        for pin in positioned_pins(component, index):
            if pin.direction != I:
                continue
            network = compiled.pin_networks[(index, pin.name)]
            driver_arrival = max(
                arrivals[driver["component"]] for driver in network_drivers[network]
            )
            output_records.append(
                {
                    "label": component.user_label,
                    "pin": pin.name,
                    "network": network,
                    "arrival": driver_arrival,
                    "drivers": network_drivers[network],
                }
            )

    recomputed_gate = sum(
        KIND_COST_DELAY[component.kind][0]
        for component in circuit.components
        if component.kind in KIND_COST_DELAY
    )
    return {
        "schema": "byte-adder-human-architecture-audit-v1",
        "source": {
            "path": str(path),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest().upper(),
        },
        "declared": {
            "gate": circuit.gate,
            "delay": circuit.delay,
            "energy": circuit.energy,
        },
        "recomputed": {
            "gate": recomputed_gate,
            "delay": max(record["arrival"] for record in output_records),
            "conflict_rows": conflict_rows.bit_count(),
        },
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "outputs": output_records,
        "components": components,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, nargs="?", default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit(args.path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result["recomputed"], ensure_ascii=False))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
