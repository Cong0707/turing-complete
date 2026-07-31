"""Reviewed modern Foundry components generated under foundry/codex."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .builder import stable_permanent_id, wire_from_vertices
from .foundry import build_codex_candidate, foundry_input, foundry_output
from .logic_layout import layout_logic_network
from .logic_network import LogicBuilder
from .model import Circuit, Component
from .pins import analyze_connectivity
from .simulate import verify_truth_table


@dataclass(frozen=True)
class CodexRecipe:
    logical_key: str
    display_path: str
    circuit: Circuit
    inputs: dict[str, int]
    outputs: tuple[str, ...]
    expected: object


def _component(key: str, role: str, kind: int, position: tuple[int, int]) -> Component:
    return Component(
        kind=kind,
        position=position,
        rotation=0,
        permanent_id=stable_permanent_id(key, role),
    )


def _half_adder() -> CodexRecipe:
    key = "foundry/codex/half_adder/area"
    components = (
        foundry_input(key, "A", (-12, -3), index=0),
        foundry_input(key, "B", (-12, 3), index=1),
        foundry_output(key, "Sum", (12, -3), index=0),
        foundry_output(key, "Carry", (12, 3), index=1),
        _component(key, "and", 4, (-4, 3)),
        _component(key, "nor-inputs", 9, (-4, -3)),
        _component(key, "nor-sum", 9, (4, -3)),
    )
    wires = (
        wire_from_vertices(((-9, -3), (-6, -3), (-5, -4))),
        wire_from_vertices(((-9, -3), (-8, -3), (-8, 2), (-5, 2))),
        wire_from_vertices(((-9, 3), (-7, 3), (-7, -2), (-5, -2))),
        wire_from_vertices(((-9, 3), (-6, 3), (-5, 4))),
        wire_from_vertices(((-2, -3), (2, -3), (3, -4))),
        wire_from_vertices(((-2, 3), (1, 3), (1, -2), (3, -2))),
        wire_from_vertices(((-2, 3), (9, 3))),
        wire_from_vertices(((6, -3), (9, -3))),
    )
    return CodexRecipe(
        key,
        "半加器/低门数",
        Circuit(gate=3, delay=2, clock_speed=100_000, components=components, wires=wires),
        {"A": 1, "B": 1},
        ("Sum", "Carry"),
        lambda values: {
            "Sum": values["A"] ^ values["B"],
            "Carry": values["A"] & values["B"],
        },
    )


def _full_adder() -> CodexRecipe:
    key = "foundry/codex/full_adder/area"
    components = (
        foundry_input(key, "A", (-18, -8), index=0),
        foundry_input(key, "B", (-18, 0), index=1),
        foundry_input(key, "CarryIn", (-18, 8), index=2),
        foundry_output(key, "Sum", (18, -4), index=0),
        foundry_output(key, "CarryOut", (18, 6), index=1),
        _component(key, "and-ab", 4, (-9, -2)),
        _component(key, "nor-ab", 9, (-9, -8)),
        _component(key, "xor-ab", 9, (-2, -5)),
        _component(key, "and-propagate-carry", 4, (3, 2)),
        _component(key, "nor-propagate-carry", 9, (3, -4)),
        _component(key, "sum", 9, (10, -4)),
        _component(key, "carry", 7, (10, 6)),
    )
    wires = (
        wire_from_vertices(((-15, -8), (-11, -8), (-10, -9))),
        wire_from_vertices(((-15, -8), (-13, -8), (-13, -3), (-10, -3))),
        wire_from_vertices(((-15, 0), (-12, 0), (-12, -7), (-10, -7))),
        wire_from_vertices(((-15, 0), (-11, 0), (-10, -1))),
        wire_from_vertices(((-7, -8), (-5, -8), (-5, -6), (-3, -6))),
        wire_from_vertices(((-7, -2), (-5, -2), (-5, -4), (-3, -4))),
        wire_from_vertices(((-7, -2), (-6, -2), (-6, 5), (9, 5))),
        wire_from_vertices(((0, -5), (1, -5), (2, -5))),
        wire_from_vertices(((0, -5), (1, -5), (1, 1), (2, 1))),
        wire_from_vertices(((-15, 8), (-14, 8), (-14, -3), (2, -3))),
        wire_from_vertices(((-15, 8), (-13, 8), (-13, 3), (2, 3))),
        wire_from_vertices(((5, -4), (8, -4), (9, -5))),
        wire_from_vertices(((5, 2), (7, 2), (7, -3), (9, -3))),
        wire_from_vertices(((5, 2), (6, 2), (6, 7), (9, 7))),
        wire_from_vertices(((12, -4), (15, -4))),
        wire_from_vertices(((12, 6), (15, 6))),
    )
    return CodexRecipe(
        key,
        "全加器/低门数",
        Circuit(gate=7, delay=4, clock_speed=100_000, components=components, wires=wires),
        {"A": 1, "B": 1, "CarryIn": 1},
        ("Sum", "CarryOut"),
        lambda values: {
            "Sum": (values["A"] + values["B"] + values["CarryIn"]) & 1,
            "CarryOut": (values["A"] + values["B"] + values["CarryIn"]) >> 1,
        },
    )


def _parity_gate(*, inverted: bool) -> CodexRecipe:
    name = "xnor" if inverted else "xor"
    display = "同或门" if inverted else "异或门"
    key = f"foundry/codex/{name}/area"
    builder = LogicBuilder()
    left = builder.input("A")
    right = builder.input("B")
    parity = builder.xor(left, right)
    builder.output("Out", ~parity if inverted else parity)
    circuit = layout_logic_network(key, builder.build())
    return CodexRecipe(
        key,
        f"{display}/低门数",
        circuit,
        {"A": 1, "B": 1},
        ("Out",),
        lambda values: {
            "Out": int(not (values["A"] ^ values["B"]))
            if inverted
            else values["A"] ^ values["B"]
        },
    )


CODEX_RECIPES: tuple[CodexRecipe, ...] = (
    _half_adder(),
    _full_adder(),
    _parity_gate(inverted=False),
    _parity_gate(inverted=True),
)


def verify_codex_recipe(recipe: CodexRecipe) -> dict[str, object]:
    connectivity = analyze_connectivity(recipe.circuit)
    for field in (
        "unconnected_pin_count",
        "multi_driver_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise ValueError(f"{recipe.logical_key} failed connectivity check {field}")
    vectors = verify_truth_table(
        recipe.circuit,
        inputs=recipe.inputs,
        output_label=recipe.outputs,
        expected=recipe.expected,
    )
    return {
        "logical_key": recipe.logical_key,
        "gate": recipe.circuit.gate,
        "delay": recipe.circuit.delay,
        "energy": recipe.circuit.energy,
        "vectors": vectors,
        "connectivity": connectivity,
    }


def build_known_codex_library(
    project_root: Path,
    *,
    dependency_roots: tuple[Path, ...] = (),
) -> dict[str, object]:
    results: list[dict[str, object]] = []
    for recipe in CODEX_RECIPES:
        verification = verify_codex_recipe(recipe)
        built = build_codex_candidate(
            project_root,
            recipe.logical_key,
            recipe.display_path,
            recipe.circuit,
            dependency_roots=dependency_roots,
        )
        results.append({**built, "verified_vectors": verification["vectors"]})
    return {"component_count": len(results), "components": results}
