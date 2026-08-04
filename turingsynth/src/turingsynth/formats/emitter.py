"""Convert a routed physical design into a strict v15 circuit."""

from __future__ import annotations

from dataclasses import replace

from turingsynth.formats.model import Circuit, Component
from turingsynth.formats.v15 import decode_v15, encode_v15
from turingsynth.ir.physical import PhysicalComponent, PhysicalDesign
from turingsynth.routing.astar import RoutingResult
from turingsynth.targets.context import TargetContext


def _component(value: PhysicalComponent) -> Component:
    if value.position is None:
        raise ValueError(f"component {value.key!r} is not placed")
    return Component(
        kind=value.kind,
        position=value.position,
        rotation=value.rotation,
        permanent_id=value.permanent_id,
        user_label=value.user_label,
        settings=value.settings,
        ui_order=value.ui_order,
        word_size=value.word_size,
        immutable=value.immutable,
    )


def emit_v15(
    design: PhysicalDesign,
    routing: RoutingResult,
    target: TargetContext,
    *,
    description: str,
) -> tuple[Circuit, bytes]:
    base_by_id = {
        component.permanent_id: component for component in target.base_circuit.components
    }
    components = []
    for value in design.components:
        original = base_by_id.get(value.permanent_id)
        if original is not None:
            if value.position != original.position:
                raise ValueError("immutable target component position changed")
            components.append(original)
        else:
            components.append(_component(value))
    permanent_ids = [component.permanent_id for component in components]
    if len(permanent_ids) != len(set(permanent_ids)) or any(value <= 0 for value in permanent_ids):
        raise ValueError("generated component permanent IDs are not unique positive integers")
    if target.kind == "level" and target.base_circuit.wires:
        raise ValueError("level target templates with existing wires are not supported yet")
    circuit = replace(
        target.base_circuit,
        custom_id=target.custom_id,
        gate=design.gate,
        delay=design.delay,
        description=description,
        dependencies=(),
        design=bytes(512) if target.kind == "foundry" else b"",
        components=tuple(components),
        wires=routing.wires,
    )
    encoded = encode_v15(circuit)
    if decode_v15(encoded) != circuit:
        raise RuntimeError("v15 round trip changed the emitted circuit")
    return circuit, encoded
