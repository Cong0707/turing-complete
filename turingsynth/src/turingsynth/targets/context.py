"""Foundry and campaign-level target boundaries."""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
import struct
import unicodedata

from turingsynth.config import ProjectConfig
from turingsynth.formats.model import Circuit
from turingsynth.formats.v15 import decode_v15
from turingsynth.ir.logical import LogicNetlist
from turingsynth.ir.physical import PhysicalComponent
from turingsynth.mapping.native import INPUT, OUTPUT, positioned_pins


INT64_MAX = (1 << 63) - 1
CUSTOM_ID_DOMAIN = b"turingsynth/custom-id/v1\0"
PERMANENT_ID_DOMAIN = b"turingsynth/permanent-id/v1\0"


@dataclass(frozen=True)
class TargetContext:
    kind: str
    base_circuit: Circuit
    components: tuple[PhysicalComponent, ...]
    port_component: dict[str, str]
    port_pin: dict[str, str]
    custom_id: int


def _framed(value: str) -> bytes:
    data = unicodedata.normalize("NFC", value).encode("utf-8")
    return struct.pack("<I", len(data)) + data


def stable_id(domain: bytes, logical_key: str, role: str = "") -> int:
    digest = sha256(domain + _framed(logical_key) + _framed(role)).digest()
    value = int.from_bytes(digest[:8], "little") & INT64_MAX
    return value or 1


def stable_custom_id(logical_key: str) -> int:
    return stable_id(CUSTOM_ID_DOMAIN, logical_key)


def stable_permanent_id(logical_key: str, role: str) -> int:
    return stable_id(PERMANENT_ID_DOMAIN, logical_key, role)


def _foundry_context(config: ProjectConfig, netlist: LogicNetlist) -> TargetContext:
    inputs = netlist.input_ports
    outputs = netlist.output_ports
    input_rows = [index * 8 - ((len(inputs) - 1) * 8) // 2 for index in range(len(inputs))]
    output_rows = [index * 8 - ((len(outputs) - 1) * 8) // 2 for index in range(len(outputs))]
    components = []
    port_component: dict[str, str] = {}
    port_pin: dict[str, str] = {}
    role_by_key: dict[str, str] = {}
    for index, (port, row) in enumerate(zip(inputs, input_rows)):
        key = f"port:input:{port.name}"
        components.append(
            PhysicalComponent(
                key=key,
                kind=79,
                word_size=len(port.bits),
                role="input_port",
                affinity=float(index),
                logic_depth=0,
                user_label=port.name,
                settings=(2,),
                ui_order=-2 * (index + 1),
                permanent_id=stable_permanent_id(config.logical_key, key),
                position=None,
            )
        )
        port_component[port.name] = key
        port_pin[port.name] = "in"
    for index, (port, row) in enumerate(zip(outputs, output_rows)):
        key = f"port:output:{port.name}"
        components.append(
            PhysicalComponent(
                key=key,
                kind=81,
                word_size=len(port.bits),
                role="output_port",
                affinity=float(index),
                logic_depth=0,
                user_label=port.name,
                settings=(0,),
                ui_order=-2 * (index + 1),
                permanent_id=stable_permanent_id(config.logical_key, key),
                position=None,
            )
        )
        port_component[port.name] = key
        port_pin[port.name] = "out"
    custom_id = stable_custom_id(config.logical_key)
    return TargetContext(
        kind="foundry",
        base_circuit=Circuit(
            custom_id=custom_id,
            description=config.description,
            design=bytes(512),
        ),
        components=tuple(components),
        port_component=port_component,
        port_pin=port_pin,
        custom_id=custom_id,
    )


def _level_context(config: ProjectConfig, netlist: LogicNetlist) -> TargetContext:
    assert config.template is not None
    base = decode_v15(config.template.read_bytes())
    if base.custom_id:
        raise ValueError("level target template must not be a Foundry Custom circuit")
    if any(not component.immutable for component in base.components):
        raise ValueError("level template must contain only immutable scaffold components")
    by_label = {component.user_label: (index, component) for index, component in enumerate(base.components)}
    if len(by_label) != len(base.components):
        raise ValueError("level template requires unique non-empty component labels")
    components = []
    index_to_key: dict[int, str] = {}
    for index, component in enumerate(base.components):
        key = f"template:{index}:{component.user_label}"
        index_to_key[index] = key
        positioned_pins(component, index)
        components.append(
            PhysicalComponent(
                key=key,
                kind=component.kind,
                word_size=component.word_size,
                role="template",
                affinity=float(index),
                logic_depth=0,
                user_label=component.user_label,
                settings=component.settings,
                ui_order=component.ui_order,
                immutable=True,
                rotation=component.rotation,
                position=component.position,
                permanent_id=component.permanent_id,
            )
        )
    port_component: dict[str, str] = {}
    port_pin: dict[str, str] = {}
    for port in netlist.ports:
        binding = config.port_bindings.get(port.name)
        if binding is None:
            raise ValueError(f"level target has no target.ports binding for {port.name!r}")
        try:
            index, component = by_label[binding.component_label]
        except KeyError as exc:
            raise ValueError(
                f"level template has no component labeled {binding.component_label!r}"
            ) from exc
        pins = {pin.name: pin for pin in positioned_pins(component, index)}
        if binding.pin not in pins:
            raise ValueError(
                f"component {binding.component_label!r} has no pin {binding.pin!r}"
            )
        pin = pins[binding.pin]
        expected_direction = OUTPUT if port.direction == "input" else INPUT
        if pin.direction != expected_direction or pin.width != len(port.bits):
            raise ValueError(
                f"binding {port.name!r} width/direction differs from Verilog port"
            )
        port_component[port.name] = index_to_key[index]
        port_pin[port.name] = binding.pin
        role_by_key[index_to_key[index]] = (
            "input_port" if port.direction == "input" else "output_port"
        )
    components = [
        replace(component, role=role_by_key.get(component.key, component.role))
        for component in components
    ]
    return TargetContext(
        kind="level",
        base_circuit=base,
        components=tuple(components),
        port_component=port_component,
        port_pin=port_pin,
        custom_id=0,
    )


def build_target_context(config: ProjectConfig, netlist: LogicNetlist) -> TargetContext:
    return _foundry_context(config, netlist) if config.target_kind == "foundry" else _level_context(config, netlist)
