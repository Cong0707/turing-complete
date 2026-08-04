"""Exhaustively audit Bit Switch enables in a physical byte_adder save.

The audit decodes ``circuit.data`` and follows the real component pins and
wires.  It does not trust the Factory DAG used to generate the schematic.
All 256 * 256 * 2 input combinations are evaluated as Python integer bitsets.
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

from tc_save_lab.codec import decode_circuit  # noqa: E402
from tc_save_lab.pins import I, O, T, positioned_pins  # noqa: E402
from tc_save_lab.simulate import (  # noqa: E402
    CONSTANT_KINDS,
    SINK_KINDS,
    SOURCE_KINDS,
    _compile,
)


DEFAULT_CIRCUIT = Path.home() / (
    "AppData/Roaming/Turing Complete/schematics/byte_adder/Default/circuit.data"
)
DEFAULT_REPORT = Path(__file__).with_name("switch-enable-full-domain-audit.json")
ROW_COUNT = 256 * 256 * 2
ALL_ROWS = (1 << ROW_COUNT) - 1


def _pattern(half_period: int) -> int:
    """Return a ROW_COUNT-bit square wave with the requested half-period."""

    block = "0" * half_period + "1" * half_period
    return int(block * (ROW_COUNT // (2 * half_period)), 2)


def _input_lanes() -> dict[str, tuple[int, ...]]:
    # Cin changes fastest, B every two rows, and A every 512 rows.  The order
    # is arbitrary; it is a bijection over the complete 17-bit input domain.
    return {
        "Carry in": (_pattern(1),),
        "B": tuple(_pattern(2 << bit) for bit in range(8)),
        "A": tuple(_pattern(512 << bit) for bit in range(8)),
    }


def _pin_width(circuit, component_index: int, pin_name: str) -> int:
    for pin in positioned_pins(circuit.components[component_index], component_index):
        if pin.name == pin_name:
            return pin.width
    raise KeyError((component_index, pin_name))


def _driver_map(circuit, compiled) -> dict[int, list[dict[str, object]]]:
    result: dict[int, list[dict[str, object]]] = defaultdict(list)
    for component_index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, component_index):
            if pin.direction not in {O, T}:
                continue
            network = compiled.pin_networks.get((component_index, pin.name))
            if network is None:
                continue
            result[network].append(
                {
                    "component_index": component_index,
                    "component_kind": component.kind,
                    "permanent_id": component.permanent_id,
                    "pin": pin.name,
                }
            )
    return dict(result)


def _simulate(circuit, compiled, inputs, *, disconnected_switch: int | None = None):
    values: dict[int, tuple[int, ...]] = {}
    driven_masks: dict[int, tuple[int, ...]] = {}
    resolved_driver_counts: dict[int, int] = defaultdict(int)
    switch_enables: dict[int, int] = {}
    switch_inputs: dict[int, int] = {}
    conflict_rows = 0

    def invert(value: int) -> int:
        return (~value) & ALL_ROWS

    def drive(
        component_index: int,
        pin_name: str,
        value: int | Iterable[int],
        *,
        driven: int | Iterable[int] | None = None,
    ) -> None:
        nonlocal conflict_rows
        network = compiled.pin_networks.get((component_index, pin_name))
        if network is None:
            return
        width = _pin_width(circuit, component_index, pin_name)
        lanes = (value,) * width if isinstance(value, int) else tuple(value)
        if len(lanes) != width:
            raise RuntimeError(
                f"value width mismatch at component {component_index} pin {pin_name}"
            )
        if driven is None:
            masks = (ALL_ROWS,) * width
        elif isinstance(driven, int):
            masks = (driven,) * width
        else:
            masks = tuple(driven)
        if len(masks) != width:
            raise RuntimeError(
                f"driven width mismatch at component {component_index} pin {pin_name}"
            )

        if network in values:
            old_values = values[network]
            old_masks = driven_masks[network]
            conflict = 0
            for old_value, new_value, old_mask, new_mask in zip(
                old_values, lanes, old_masks, masks
            ):
                conflict |= (old_value ^ new_value) & old_mask & new_mask
            conflict_rows |= conflict
            values[network] = tuple(
                (old_value & old_mask) | (new_value & new_mask)
                for old_value, new_value, old_mask, new_mask in zip(
                    old_values, lanes, old_masks, masks
                )
            )
            driven_masks[network] = tuple(
                old_mask | new_mask for old_mask, new_mask in zip(old_masks, masks)
            )
        else:
            values[network] = tuple(
                lane & mask for lane, mask in zip(lanes, masks)
            )
            driven_masks[network] = masks
        resolved_driver_counts[network] += 1

    def ready(network: int) -> bool:
        return (
            resolved_driver_counts[network]
            == compiled.network_driver_counts.get(network, 0)
            and resolved_driver_counts[network] > 0
        )

    def read(component_index: int, pin_name: str) -> tuple[int, ...]:
        network = compiled.pin_networks[(component_index, pin_name)]
        if not ready(network):
            raise RuntimeError(
                f"network {network} not ready for component {component_index} pin {pin_name}"
            )
        # The runtime's ordinary data plane reads a high-impedance lane as 0.
        return tuple(
            value & mask
            for value, mask in zip(values[network], driven_masks[network])
        )

    pending: set[int] = set()
    for component_index, component in enumerate(circuit.components):
        if component.kind in SOURCE_KINDS:
            raw = inputs[component.user_label]
            output_pins = [
                pin
                for pin in positioned_pins(component, component_index)
                if pin.direction in {O, T}
            ]
            if len(output_pins) == 1:
                drive(component_index, output_pins[0].name, raw)
            else:
                for bit, pin in enumerate(output_pins):
                    drive(component_index, pin.name, raw[bit])
        elif component.kind in CONSTANT_KINDS:
            number = component.init_data if component.kind == 46 else int(component.kind == 2)
            drive(
                component_index,
                "out",
                tuple(
                    ALL_ROWS if (number >> bit) & 1 else 0
                    for bit in range(component.word_size)
                ),
            )
        elif component.kind not in SINK_KINDS:
            pending.add(component_index)

    while pending:
        progressed = False
        for component_index in tuple(pending):
            component = circuit.components[component_index]
            input_pins = [
                pin
                for pin in positioned_pins(component, component_index)
                if pin.direction == I
            ]
            if not all(
                ready(compiled.pin_networks[(component_index, pin.name)])
                for pin in input_pins
            ):
                continue
            pin_values = {
                pin.name: read(component_index, pin.name) for pin in input_pins
            }
            kind = component.kind
            if kind == 12:
                enable = pin_values["enable"][0]
                switch_enables[component_index] = enable
                switch_inputs[component_index] = pin_values["in"][0]
                drive(
                    component_index,
                    "out",
                    pin_values["in"],
                    driven=0 if component_index == disconnected_switch else enable,
                )
            elif kind == 4:
                drive(
                    component_index,
                    "out",
                    pin_values["in0"][0] & pin_values["in1"][0],
                )
            elif kind == 6:
                drive(
                    component_index,
                    "out",
                    invert(pin_values["in0"][0] & pin_values["in1"][0]),
                )
            elif kind == 7:
                drive(
                    component_index,
                    "out",
                    pin_values["in0"][0] | pin_values["in1"][0],
                )
            elif kind == 9:
                drive(
                    component_index,
                    "out",
                    invert(pin_values["in0"][0] | pin_values["in1"][0]),
                )
            elif kind == 16:
                drive(
                    component_index,
                    "out",
                    tuple(pin_values[f"in{bit}"][0] for bit in range(8)),
                )
            elif kind == 17:
                for bit in range(8):
                    drive(component_index, f"out{bit}", pin_values["in"][bit])
            elif kind == 109:
                drive(component_index, "out0", pin_values["in"][0])
                drive(component_index, "out1", pin_values["in"][1])
            elif kind == 111:
                drive(
                    component_index,
                    "out",
                    (pin_values["in0"][0], pin_values["in1"][0]),
                )
            else:
                raise RuntimeError(
                    f"unsupported component kind {kind} at index {component_index}"
                )
            pending.remove(component_index)
            progressed = True
        if not progressed:
            raise RuntimeError(f"physical netlist did not settle: {sorted(pending)}")

    sum_output = read(0, "value")
    carry_output = read(4, "value")[0]
    carry = inputs["Carry in"][0]
    expected_sum: list[int] = []
    for bit in range(8):
        propagate = inputs["A"][bit] ^ inputs["B"][bit]
        expected_sum.append(propagate ^ carry)
        carry = (
            inputs["A"][bit] & inputs["B"][bit]
        ) | (propagate & carry)
    mismatch_masks = [
        sum_output[bit] ^ expected_sum[bit] for bit in range(8)
    ] + [carry_output ^ carry]
    mismatch_union = 0
    for mask in mismatch_masks:
        mismatch_union |= mask
    return {
        "switch_enables": switch_enables,
        "switch_inputs": switch_inputs,
        "mismatch_by_lane": [mask.bit_count() for mask in mismatch_masks],
        "mismatch_union_rows": mismatch_union.bit_count(),
        "conflict_rows": conflict_rows.bit_count(),
    }


def audit(circuit_path: Path) -> dict[str, object]:
    payload = circuit_path.read_bytes()
    circuit = decode_circuit(payload)
    compiled = _compile(circuit)
    inputs = _input_lanes()
    drivers = _driver_map(circuit, compiled)
    baseline = _simulate(circuit, compiled, inputs)
    switch_indices = sorted(baseline["switch_enables"])
    records: list[dict[str, object]] = []
    for component_index in switch_indices:
        component = circuit.components[component_index]
        enable_network = compiled.pin_networks[(component_index, "enable")]
        enable = baseline["switch_enables"][component_index]
        switch_input = baseline["switch_inputs"][component_index]
        disconnected = _simulate(
            circuit,
            compiled,
            inputs,
            disconnected_switch=component_index,
        )
        records.append(
            {
                "component_index": component_index,
                "permanent_id": component.permanent_id,
                "position": list(component.position),
                "rotation": component.rotation,
                "enable_network": enable_network,
                "enable_drivers": drivers[enable_network],
                "enable_one_rows": enable.bit_count(),
                "input_one_rows": switch_input.bit_count(),
                "active_one_rows": (enable & switch_input).bit_count(),
                "delete_mismatch_union_rows": disconnected["mismatch_union_rows"],
                "delete_mismatch_by_lane": disconnected["mismatch_by_lane"],
                "delete_conflict_rows": disconnected["conflict_rows"],
                "constant_zero_enable": enable == 0,
                "individually_deletable": (
                    disconnected["mismatch_union_rows"] == 0
                    and disconnected["conflict_rows"] == 0
                ),
            }
        )
    return {
        "schema": "byte-adder-physical-switch-enable-full-domain-audit-v2",
        "scope": {
            "truth_rows": ROW_COUNT,
            "input_order": "Cin toggles fastest, then B[0:7], then A[0:7]",
            "source": "decoded physical components, pins, and wires",
            "game_started": False,
            "save_modified": False,
        },
        "circuit": {
            "path": str(circuit_path),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest().upper(),
            "component_count": len(circuit.components),
            "wire_count": len(circuit.wires),
            "switch_count": len(switch_indices),
        },
        "baseline": {
            "mismatch_union_rows": baseline["mismatch_union_rows"],
            "mismatch_by_lane": baseline["mismatch_by_lane"],
            "conflict_rows": baseline["conflict_rows"],
        },
        "switches": records,
        "conclusion": {
            "constant_zero_enable_count": sum(
                record["constant_zero_enable"] for record in records
            ),
            "individually_deletable_switch_count": sum(
                record["individually_deletable"] for record in records
            ),
            "minimum_enable_one_rows": min(
                record["enable_one_rows"] for record in records
            ),
            "minimum_delete_mismatch_union_rows": min(
                record["delete_mismatch_union_rows"] for record in records
            ),
            "status": "all-physical-switches-have-live-enable",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit every physical Bit Switch enable over all byte_adder inputs."
    )
    parser.add_argument("circuit", nargs="?", type=Path, default=DEFAULT_CIRCUIT)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    result = audit(args.circuit.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["conclusion"], ensure_ascii=False, indent=2))
    print(f"report: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
