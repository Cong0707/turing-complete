"""Generate and verify the current-version ASIC for Circumference."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component
from .pins import analyze_connectivity, positioned_pins


VALID_RADII = range(1, 42)


@dataclass(frozen=True)
class GateNode:
    name: str
    operation: str
    inputs: tuple[str, ...]


# ABC maps this network to area 31 and delay 5 under the reviewed TC model:
# simple one-bit gates cost 1/1, while XNOR costs 3/2.
NODES: tuple[GateNode, ...] = (
    GateNode("not-b2", "not", ("b2",)),
    GateNode("not-b0", "not", ("b0",)),
    GateNode("not-b4", "not", ("b4",)),
    GateNode("b1-b0-nand", "nand", ("b1", "b0")),
    GateNode("b1-b0-or", "or", ("b1", "b0")),
    GateNode("y2", "and", ("b1-b0-nand", "b1-b0-or")),
    GateNode("b3-not-b4-and", "and", ("b3", "not-b4")),
    GateNode("carry-a", "nand", ("not-b2", "b1-b0-nand")),
    GateNode("carry-b", "nand", ("b3-not-b4-and", "carry-a")),
    GateNode("b2-b1-and", "and", ("b2", "b1")),
    GateNode("group-or", "or", ("b3", "b2-b1-and")),
    GateNode("high-nor-a", "nor", ("not-b4", "group-or")),
    GateNode("high-nor-b", "nor", ("b5", "high-nor-a")),
    GateNode("y6", "nand", ("carry-b", "high-nor-b")),
    GateNode("b3-b4-xnor", "xnor", ("b3", "b4")),
    GateNode("middle-and", "and", ("carry-a", "group-or")),
    GateNode("y5", "xnor", ("b3-b4-xnor", "middle-and")),
    GateNode("top-and", "and", ("b4", "group-or")),
    GateNode("y7", "or", ("b5", "top-and")),
    GateNode("lower-or", "or", ("b3", "carry-a")),
    GateNode("lower-nand-a", "nand", ("b3", "b2-b1-and")),
    GateNode("lower-nand-b", "nand", ("middle-and", "lower-nand-a")),
    GateNode("y4", "and", ("lower-or", "lower-nand-b")),
    GateNode("b1-not-b0-and", "and", ("b1", "not-b0")),
    GateNode("y3", "xnor", ("not-b2", "b1-not-b0-and")),
)


OPERATION_KIND = {
    "not": 3,
    "and": 4,
    "nand": 6,
    "or": 7,
    "nor": 9,
    "xnor": 11,
}
OPERATION_COST = {
    "not": (1, 1),
    "and": (1, 1),
    "nand": (1, 1),
    "or": (1, 1),
    "nor": (1, 1),
    "xnor": (3, 2),
}


POSITIONS = {
    "not-b2": (-30, -24),
    "not-b0": (-30, -16),
    "not-b4": (-30, -8),
    "b1-b0-nand": (-30, 0),
    "b1-b0-or": (-30, 8),
    "b2-b1-and": (-30, 16),
    "b3-b4-xnor": (-30, 24),
    "y2": (-17, -20),
    "b3-not-b4-and": (-17, -12),
    "carry-a": (-17, -4),
    "group-or": (-17, 4),
    "b1-not-b0-and": (-17, 12),
    "lower-nand-a": (-17, 20),
    "carry-b": (-4, -20),
    "high-nor-a": (-4, -12),
    "middle-and": (-4, -4),
    "top-and": (-4, 4),
    "lower-or": (-4, 12),
    "y3": (-4, 20),
    "high-nor-b": (9, -12),
    "y7": (9, -4),
    "lower-nand-b": (9, 12),
    "y6": (22, -12),
    "y5": (22, -4),
    "y4": (22, 12),
}


OUTPUT_SIGNALS = ("zero", "b0", "y2", "y3", "y4", "y5", "y6", "y7")


def _apply(operation: str, values: tuple[int, ...]) -> int:
    if operation == "not":
        return 1 ^ values[0]
    if operation == "and":
        return values[0] & values[1]
    if operation == "nand":
        return 1 ^ (values[0] & values[1])
    if operation == "or":
        return values[0] | values[1]
    if operation == "nor":
        return 1 ^ (values[0] | values[1])
    if operation == "xnor":
        return 1 ^ (values[0] ^ values[1])
    raise ValueError(f"unsupported operation {operation!r}")


def evaluate_network(radius: int) -> int:
    """Evaluate the six-input network, including its domain-external values."""

    if not 0 <= radius < 64:
        raise ValueError("radius must fit in six bits")
    values = {f"b{bit}": (radius >> bit) & 1 for bit in range(6)}
    values["zero"] = 0
    for node in NODES:
        values[node.name] = _apply(
            node.operation,
            tuple(values[name] for name in node.inputs),
        )
    return sum(values[name] << bit for bit, name in enumerate(OUTPUT_SIGNALS))


def circumference(radius: int) -> int:
    """Return the level result and reject values outside the tested contract."""

    if radius not in VALID_RADII:
        raise ValueError("Circumference only tests integer radii from 1 through 41")
    return evaluate_network(radius)


def network_metrics() -> dict[str, object]:
    depths = {f"b{bit}": 0 for bit in range(6)}
    depths["zero"] = 0
    gate = 0
    for node in NODES:
        cost, delay = OPERATION_COST[node.operation]
        gate += cost
        depths[node.name] = max(depths[name] for name in node.inputs) + delay
    output_depths = {name: depths[name] for name in OUTPUT_SIGNALS}
    return {
        "gate": gate,
        "delay": max(output_depths.values()),
        "energy": gate * max(output_depths.values()),
        "physical_gate_component_count": len(NODES),
        "output_depths": output_depths,
    }


def _pin(component: Component, name: str) -> tuple[int, int]:
    return next(pin.position for pin in positioned_pins(component) if pin.name == name)


def _route(source: tuple[int, int], sink: tuple[int, int]):
    if source == sink:
        raise ValueError(f"cannot route a zero-length connection at {source}")
    if source[0] == sink[0] or source[1] == sink[1]:
        return wire_from_vertices((source, sink))
    track_x = sink[0] - 2 if source[0] < sink[0] else sink[0] + 2
    return wire_from_vertices((source, (track_x, source[1]), (track_x, sink[1]), sink))


def build_circumference_asic() -> Circuit:
    key = "architecture/codex-circumference"

    def component(role: str, kind: int, position: tuple[int, int], **kwargs) -> Component:
        return Component(
            kind=kind,
            position=position,
            rotation=0,
            permanent_id=stable_permanent_id(key, role),
            **kwargs,
        )

    level_input = component("level-input", 62, (-48, 0), word_size=8, user_label="radius")
    input_enable = component("input-enable", 2, (-50, -2))
    splitter = component("splitter", 17, (-41, 0), word_size=8)
    maker = component("maker", 16, (35, 0), word_size=8)
    level_output = component("level-output", 70, (48, 0), word_size=8, user_label="result")
    output_enable = component("output-enable", 2, (44, -2))
    gates = {
        node.name: component(node.name, OPERATION_KIND[node.operation], POSITIONS[node.name])
        for node in NODES
    }
    components = (
        level_input,
        input_enable,
        splitter,
        maker,
        level_output,
        output_enable,
        *(gates[node.name] for node in NODES),
    )

    drivers = {f"b{bit}": _pin(splitter, f"out{bit}") for bit in range(6)}
    # radius <= 41, so splitter bit 6 is a free physical constant zero.
    drivers["zero"] = _pin(splitter, "out6")
    drivers.update({name: _pin(gate, "out") for name, gate in gates.items()})

    wires = [
        _route(_pin(input_enable, "out"), _pin(level_input, "control")),
        _route(_pin(level_input, "value"), _pin(splitter, "in")),
        _route(_pin(output_enable, "out"), _pin(level_output, "control")),
        _route(_pin(maker, "out"), _pin(level_output, "value")),
    ]
    for node in NODES:
        gate = gates[node.name]
        input_names = ("in",) if node.operation == "not" else ("in0", "in1")
        wires.extend(
            _route(drivers[source], _pin(gate, pin_name))
            for source, pin_name in zip(node.inputs, input_names)
        )
    wires.extend(
        _route(drivers[source], _pin(maker, f"in{bit}"))
        for bit, source in enumerate(OUTPUT_SIGNALS)
    )

    metrics = network_metrics()
    return Circuit(
        gate=int(metrics["gate"]),
        delay=int(metrics["delay"]),
        description="Codex Circumference ASIC: exact 1..41 mapping to radius * 6",
        components=components,
        wires=tuple(wires),
    )


def verify_circumference_asic(circuit: Circuit | None = None) -> dict[str, object]:
    candidate = build_circumference_asic() if circuit is None else circuit
    for radius in VALID_RADII:
        actual = evaluate_network(radius)
        if actual != radius * 6:
            raise RuntimeError(
                f"circumference ASIC failed radius {radius}: {actual} != {radius * 6}"
            )
    metrics = network_metrics()
    if (candidate.gate, candidate.delay) != (metrics["gate"], metrics["delay"]):
        raise RuntimeError("circumference circuit header does not match the reviewed network")
    connectivity = analyze_connectivity(candidate)
    unexpected_unconnected = [
        pin
        for pin in connectivity["unconnected_pins"]
        if not (pin["kind"] == 17 and pin["name"] == "out7" and pin["direction"] == "output")
    ]
    if unexpected_unconnected or connectivity["unconnected_pin_count"] != 1:
        raise RuntimeError(
            "circumference ASIC has unexpected unconnected pins: "
            f"{connectivity['unconnected_pins']}"
        )
    for field in (
        "unsupported_component_kind_counts",
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(
                f"circumference ASIC failed connectivity check {field}: {connectivity[field]}"
            )
    return {
        **metrics,
        "tested_radius_min": min(VALID_RADII),
        "tested_radius_max": max(VALID_RADII),
        "tested_vector_count": len(VALID_RADII),
        "connectivity": connectivity,
    }


def write_circumference_asic(project_root: Path) -> dict[str, object]:
    candidate = build_circumference_asic()
    verification = verify_circumference_asic(candidate)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("circumference ASIC failed v15 round-trip verification")
    destination = project_root / "examples" / "circumference" / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    metadata = {
        "schema": 1,
        "level": "circumference",
        "title": "Circumference",
        "strategy": "current-v15 domain-specialized ASIC",
        "deployment_target": "schematics/architecture/CODEX-CIRCUMFERENCE/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
