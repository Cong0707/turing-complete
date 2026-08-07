"""Technology-mapped component/net IR before placement and routing."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from turingsynth.formats.model import Point


@dataclass(frozen=True)
class PinRef:
    component: str
    pin: str


@dataclass(frozen=True)
class PhysicalComponent:
    key: str
    kind: int
    word_size: int
    role: str
    affinity: float
    logic_depth: int
    gate_cost: int = 0
    gate_delay: int = 0
    user_label: str = ""
    settings: tuple[int, ...] = ()
    ui_order: int = 0
    immutable: bool = False
    rotation: int = 0
    position: Point | None = None
    permanent_id: int = 0
    custom_id: int = 0
    custom_word_sizes: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class PhysicalNet:
    name: str
    width: int
    source: PinRef
    sinks: tuple[PinRef, ...]
    logic_bits: tuple[int | str, ...] = ()
    additional_sources: tuple[PinRef, ...] = ()

    @property
    def sources(self) -> tuple[PinRef, ...]:
        return (self.source, *self.additional_sources)


@dataclass(frozen=True)
class PhysicalDesign:
    name: str
    components: tuple[PhysicalComponent, ...]
    nets: tuple[PhysicalNet, ...]
    gate: int
    delay: int
    target_kind: str
    custom_id: int = 0

    def component_by_key(self) -> dict[str, PhysicalComponent]:
        result = {component.key: component for component in self.components}
        if len(result) != len(self.components):
            raise ValueError("physical design has duplicate component keys")
        return result

    def with_positions(self, positions: dict[str, Point]) -> "PhysicalDesign":
        missing = {component.key for component in self.components} - set(positions)
        if missing:
            raise ValueError(f"layout omitted components: {sorted(missing)!r}")
        return replace(
            self,
            components=tuple(
                replace(component, position=positions[component.key])
                for component in self.components
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "turingsynth-physical-design-v1",
            "name": self.name,
            "target_kind": self.target_kind,
            "custom_id": self.custom_id,
            "metrics": {"gate": self.gate, "delay": self.delay, "energy": self.gate * self.delay},
            "components": [asdict(component) for component in self.components],
            "nets": [
                {
                    "name": net.name,
                    "width": net.width,
                    "source": asdict(net.source),
                    "additional_sources": [
                        asdict(source) for source in net.additional_sources
                    ],
                    "sinks": [asdict(sink) for sink in net.sinks],
                    "logic_bits": list(net.logic_bits),
                }
                for net in self.nets
            ],
        }
