"""Normalized bit-level logic IR produced by the Yosys frontend."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, TypeAlias


Bit: TypeAlias = int | str
CONSTANTS = frozenset({"0", "1"})


@dataclass(frozen=True)
class Port:
    name: str
    direction: str
    bits: tuple[Bit, ...]
    signed: bool = False


@dataclass(frozen=True)
class Cell:
    name: str
    op: str
    inputs: tuple[Bit, ...]
    output: int
    attributes: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class CellPort:
    name: str
    direction: str
    bits: tuple[Bit, ...]


@dataclass(frozen=True)
class CustomCell:
    name: str
    module: str
    ports: tuple[CellPort, ...]
    attributes: tuple[tuple[str, str], ...] = ()

    @property
    def input_bits(self) -> tuple[Bit, ...]:
        return tuple(
            bit
            for port in self.ports
            if port.direction == "input"
            for bit in port.bits
        )

    @property
    def output_bits(self) -> tuple[int, ...]:
        return tuple(
            bit
            for port in self.ports
            if port.direction == "output"
            for bit in port.bits
            if isinstance(bit, int)
        )


@dataclass(frozen=True)
class LogicNetlist:
    top: str
    ports: tuple[Port, ...]
    cells: tuple[Cell, ...]
    source_files: tuple[str, ...] = ()
    custom_cells: tuple[CustomCell, ...] = ()

    @property
    def input_ports(self) -> tuple[Port, ...]:
        return tuple(port for port in self.ports if port.direction == "input")

    @property
    def output_ports(self) -> tuple[Port, ...]:
        return tuple(port for port in self.ports if port.direction == "output")

    @staticmethod
    def _bad_bits(bits: tuple[Bit, ...]) -> tuple[Bit, ...]:
        return tuple(
            bit
            for bit in bits
            if bit not in CONSTANTS and not isinstance(bit, int)
        )

    def validate(self) -> None:
        if not self.top:
            raise ValueError("logic netlist has no top module")
        if len({port.name for port in self.ports}) != len(self.ports):
            raise ValueError("logic netlist has duplicate port names")
        if any(port.direction not in {"input", "output"} for port in self.ports):
            raise ValueError("logic netlist contains an unsupported top-level port direction")
        input_bits = {
            bit
            for port in self.input_ports
            for bit in port.bits
            if isinstance(bit, int)
        }
        output_drivers: dict[int, str] = {}
        for cell in self.cells:
            if cell.output in output_drivers or cell.output in input_bits:
                raise ValueError(
                    f"bit {cell.output} has multiple drivers: "
                    f"{output_drivers.get(cell.output, 'input port')} and {cell.name}"
                )
            output_drivers[cell.output] = cell.name
            if self._bad_bits(cell.inputs):
                raise ValueError(f"cell {cell.name!r} contains an unsupported constant")
        for cell in self.custom_cells:
            if len({port.name for port in cell.ports}) != len(cell.ports):
                raise ValueError(f"custom cell {cell.name!r} has duplicate port names")
            for port in cell.ports:
                if port.direction not in {"input", "output"}:
                    raise ValueError(
                        f"custom cell {cell.name!r} has unsupported port direction"
                    )
                if self._bad_bits(port.bits):
                    raise ValueError(
                        f"custom cell {cell.name!r} contains an unsupported constant"
                    )
                if port.direction == "output" and any(
                    not isinstance(bit, int) for bit in port.bits
                ):
                    raise ValueError(
                        f"custom cell {cell.name!r} drives a constant output"
                    )
            for bit in cell.output_bits:
                if bit in output_drivers or bit in input_bits:
                    raise ValueError(
                        f"bit {bit} has multiple drivers: "
                        f"{output_drivers.get(bit, 'input port')} and {cell.name}"
                    )
                output_drivers[bit] = cell.name

        available: set[Bit] = set(input_bits) | set(CONSTANTS)
        pending: list[Cell | CustomCell] = [*self.cells, *self.custom_cells]
        while pending:
            ready = []
            for cell in pending:
                inputs = cell.inputs if isinstance(cell, Cell) else cell.input_bits
                if all(bit in available for bit in inputs):
                    ready.append(cell)
            if not ready:
                names = ", ".join(cell.name for cell in pending[:8])
                raise ValueError(f"logic netlist is cyclic or undriven near: {names}")
            for cell in ready:
                if isinstance(cell, Cell):
                    available.add(cell.output)
                else:
                    available.update(cell.output_bits)
                pending.remove(cell)
        undriven = sorted(
            bit
            for port in self.output_ports
            for bit in port.bits
            if isinstance(bit, int) and bit not in available
        )
        if undriven:
            raise ValueError(f"output bits are undriven: {undriven[:8]!r}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "turingsynth-logic-netlist-v2",
            "top": self.top,
            "source_files": list(self.source_files),
            "ports": [asdict(port) for port in self.ports],
            "cells": [
                {
                    "name": cell.name,
                    "op": cell.op,
                    "inputs": list(cell.inputs),
                    "output": cell.output,
                    "attributes": dict(cell.attributes),
                }
                for cell in self.cells
            ],
            "custom_cells": [
                {
                    "name": cell.name,
                    "module": cell.module,
                    "ports": [asdict(port) for port in cell.ports],
                    "attributes": dict(cell.attributes),
                }
                for cell in self.custom_cells
            ],
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "LogicNetlist":
        if value.get("schema") not in {
            "turingsynth-logic-netlist-v1",
            "turingsynth-logic-netlist-v2",
        }:
            raise ValueError("unsupported logic-netlist schema")
        result = cls(
            top=str(value["top"]),
            source_files=tuple(str(item) for item in value.get("source_files", ())),
            ports=tuple(
                Port(
                    name=str(item["name"]),
                    direction=str(item["direction"]),
                    bits=tuple(item["bits"]),
                    signed=bool(item.get("signed", False)),
                )
                for item in value["ports"]
            ),
            cells=tuple(
                Cell(
                    name=str(item["name"]),
                    op=str(item["op"]),
                    inputs=tuple(item["inputs"]),
                    output=int(item["output"]),
                    attributes=tuple(
                        sorted(
                            (str(key), str(raw))
                            for key, raw in item.get("attributes", {}).items()
                        )
                    ),
                )
                for item in value["cells"]
            ),
            custom_cells=tuple(
                CustomCell(
                    name=str(item["name"]),
                    module=str(item["module"]),
                    ports=tuple(
                        CellPort(
                            name=str(port["name"]),
                            direction=str(port["direction"]),
                            bits=tuple(port["bits"]),
                        )
                        for port in item.get("ports", ())
                    ),
                    attributes=tuple(
                        sorted(
                            (str(key), str(raw))
                            for key, raw in item.get("attributes", {}).items()
                        )
                    ),
                )
                for item in value.get("custom_cells", ())
            ),
        )
        result.validate()
        return result
