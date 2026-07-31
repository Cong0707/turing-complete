"""Lossless in-memory model for current Turing Complete circuit files."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


Point = tuple[int, int]
LinkedComponent = tuple[int, int, str, int, int]
SelectedProgram = tuple[str, str]
CustomWordSize = tuple[int, int]


@dataclass(frozen=True)
class Component:
    kind: int
    position: Point
    rotation: int
    permanent_id: int
    user_label: str = ""
    custom_string: str = ""
    settings: tuple[int, ...] = ()
    buffer_size: int = 0
    ui_order: int = 0
    word_size: int = 1
    immutable: bool = False
    cost_gate: int = -1
    cost_delay: int = 0
    little_endian: bool = False
    init_data: int = 0
    linked_components: tuple[LinkedComponent, ...] = ()
    selected_programs: tuple[SelectedProgram, ...] = ()
    custom_id: int = 0
    custom_word_sizes: tuple[CustomWordSize, ...] = ()


@dataclass(frozen=True)
class Wire:
    color: int
    comment: str
    start: Point
    segments: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class Circuit:
    custom_id: int = 0
    hub_id: int = 0
    gate: int = 0
    delay: int = 0
    menu_visible: bool = True
    clock_speed: int = 10_000_000
    dependencies: tuple[int, ...] = ()
    description: str = ""
    sync_state: int = 0
    score: int = 0
    player_data: bytes = b""
    hub_description: str = ""
    design: bytes = b""
    components: tuple[Component, ...] = ()
    wires: tuple[Wire, ...] = ()

    @property
    def energy(self) -> int:
        return self.gate * self.delay

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["player_data"] = self.player_data.hex()
        result["design"] = self.design.hex()
        result["format_version"] = 15
        result["component_count"] = len(self.components)
        result["wire_count"] = len(self.wires)
        result["energy"] = self.energy
        return result

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Circuit":
        ignored = {"format_version", "component_count", "wire_count", "energy"}
        data = {key: item for key, item in value.items() if key not in ignored}
        data["player_data"] = bytes.fromhex(data.get("player_data", ""))
        data["design"] = bytes.fromhex(data.get("design", ""))
        data["dependencies"] = tuple(data.get("dependencies", ()))
        data["components"] = tuple(_component_from_dict(item) for item in data.get("components", ()))
        data["wires"] = tuple(_wire_from_dict(item) for item in data.get("wires", ()))
        return cls(**data)


def _component_from_dict(value: dict[str, Any]) -> Component:
    data = dict(value)
    data["position"] = tuple(data["position"])
    for key in ("settings", "linked_components", "selected_programs", "custom_word_sizes"):
        data[key] = tuple(tuple(item) if isinstance(item, list) else item for item in data.get(key, ()))
    return Component(**data)


def _wire_from_dict(value: dict[str, Any]) -> Wire:
    data = dict(value)
    data["start"] = tuple(data["start"])
    data["segments"] = tuple(tuple(item) for item in data["segments"])
    return Wire(**data)
