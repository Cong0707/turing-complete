"""Reusable custom-module metadata shared by synthesis, mapping, and packaging."""

from __future__ import annotations

from dataclasses import dataclass

from turingsynth.config import ComponentConfig
from turingsynth.formats.model import Circuit
from turingsynth.ir.logical import LogicNetlist, Port


@dataclass(frozen=True)
class CustomModule:
    config: ComponentConfig
    logical: LogicNetlist
    circuit: Circuit
    payload: bytes

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def top(self) -> str:
        return self.config.top

    @property
    def ports(self) -> tuple[Port, ...]:
        return self.logical.ports

    def port_components(self) -> dict[str, object]:
        result = {
            component.user_label: component
            for component in self.circuit.components
            if component.kind in {79, 81}
        }
        expected = {port.name for port in self.ports}
        if set(result) != expected:
            raise ValueError(
                f"component {self.name!r} Foundry ports differ from HDL ports"
            )
        return result
