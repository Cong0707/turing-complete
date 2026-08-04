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
class LogicNetlist:
    top: str
    ports: tuple[Port, ...]
    cells: tuple[Cell, ...]
    source_files: tuple[str, ...] = ()

    @property
    def input_ports(self) -> tuple[Port, ...]:
        return tuple(port for port in self.ports if port.direction == "input")

    @property
    def output_ports(self) -> tuple[Port, ...]:
        return tuple(port for port in self.ports if port.direction == "output")

    def validate(self) -> None:
        if not self.top:
            raise ValueError("logic netlist has no top module")
        if len({port.name for port in self.ports}) != len(self.ports):
            raise ValueError("logic netlist has duplicate port names")
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
            if any(bit not in CONSTANTS and not isinstance(bit, int) for bit in cell.inputs):
                raise ValueError(f"cell {cell.name!r} contains an unsupported constant")
        available = set(input_bits)
        pending = list(self.cells)
        while pending:
            next_pending = [
                cell
                for cell in pending
                if any(isinstance(bit, int) and bit not in available for bit in cell.inputs)
            ]
            if len(next_pending) == len(pending):
                names = ", ".join(cell.name for cell in next_pending[:8])
                raise ValueError(f"logic netlist is cyclic or undriven near: {names}")
            for cell in pending:
                if cell not in next_pending:
                    available.add(cell.output)
            pending = next_pending
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
            "schema": "turingsynth-logic-netlist-v1",
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
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "LogicNetlist":
        if value.get("schema") != "turingsynth-logic-netlist-v1":
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
                        sorted((str(key), str(raw)) for key, raw in item.get("attributes", {}).items())
                    ),
                )
                for item in value["cells"]
            ),
        )
        result.validate()
        return result
