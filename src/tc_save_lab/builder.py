"""Deterministic circuit construction primitives and reviewed recipes."""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
import json

from .analysis import analyze_examples
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point, Wire
from .pins import analyze_connectivity


DIRECTION_BY_STEP = {
    (1, 0): 0,
    (1, 1): 1,
    (0, 1): 2,
    (-1, 1): 3,
    (-1, 0): 4,
    (-1, -1): 5,
    (0, -1): 6,
    (1, -1): 7,
}


@dataclass(frozen=True)
class Recipe:
    level: str
    declared_gate: int
    declared_delay: int
    build: object


def stable_permanent_id(level: str, name: str) -> int:
    digest = sha256(f"tc-save-lab:{level}:{name}".encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "little") & ((1 << 63) - 1)
    return value or 1


def wire_from_vertices(
    vertices: tuple[Point, ...],
    *,
    color: int = 0,
    comment: str = "",
) -> Wire:
    if len(vertices) < 2:
        raise ValueError("a routed wire needs at least two vertices")
    segments: list[tuple[int, int]] = []
    for start, end in zip(vertices, vertices[1:]):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = max(abs(dx), abs(dy))
        if length == 0:
            continue
        if dx and dy and abs(dx) != abs(dy):
            raise ValueError(f"wire segment is not horizontal, vertical, or 45 degree: {start} -> {end}")
        step = (0 if dx == 0 else dx // abs(dx), 0 if dy == 0 else dy // abs(dy))
        direction = DIRECTION_BY_STEP[step]
        if segments and segments[-1][0] == direction:
            previous_direction, previous_length = segments[-1]
            segments[-1] = (previous_direction, previous_length + length)
        else:
            segments.append((direction, length))
    if not segments:
        raise ValueError("wire route has zero length")
    return Wire(color=color, comment=comment, start=vertices[0], segments=tuple(segments))


def _load_scaffold_components(project_root: Path, level: str) -> tuple[Component, ...]:
    path = project_root / "examples" / level / "scaffold" / "immutable.json"
    data = json.loads(path.read_text("utf-8"))
    records = []
    for component in data["immutable_components"]:
        component = dict(component)
        component.pop("role", None)
        records.append(component)
    return Circuit.from_dict({"components": records}).components


def _triple_input_two_gate(project_root: Path, level: str, kind: int) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(kind, (-5, -1), 0, stable_permanent_id(level, "first")),
        Component(kind, (3, 0), 0, stable_permanent_id(level, "second")),
    )
    wires = (
        wire_from_vertices(((-13, -1), (-7, -1), (-6, -2))),
        wire_from_vertices(((-13, 0), (-6, 0))),
        wire_from_vertices(((-3, -1), (2, -1))),
        wire_from_vertices(((-13, 1), (2, 1))),
        wire_from_vertices(((5, 0), (12, 0))),
    )
    return components, wires


def _xnor(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(4, (-5, -2), 0, stable_permanent_id(level, "and")),
        Component(9, (-5, 2), 0, stable_permanent_id(level, "nor")),
        Component(7, (4, 0), 0, stable_permanent_id(level, "or")),
    )
    wires = (
        wire_from_vertices(((-13, -1), (-11, -3), (-6, -3))),
        wire_from_vertices(((-13, -1), (-11, 1), (-6, 1))),
        wire_from_vertices(((-13, 1), (-11, -1), (-6, -1))),
        wire_from_vertices(((-13, 1), (-11, 3), (-6, 3))),
        wire_from_vertices(((-3, -2), (2, -2), (3, -1))),
        wire_from_vertices(((-3, 2), (2, 2), (3, 1))),
        wire_from_vertices(((6, 0), (12, 0))),
    )
    return components, wires


RECIPES: dict[str, Recipe] = {
    "or_gate_3": Recipe("or_gate_3", 2, 2, lambda root, level: _triple_input_two_gate(root, level, 7)),
    "and_gate_3": Recipe("and_gate_3", 2, 2, lambda root, level: _triple_input_two_gate(root, level, 4)),
    "xnor": Recipe("xnor", 3, 2, _xnor),
}


def build_recipe(project_root: Path, level: str) -> dict[str, object]:
    recipe = RECIPES[level]
    baseline_path = project_root / "examples" / level / "baseline" / "circuit.data"
    baseline = decode_v15(baseline_path.read_bytes())
    components, wires = recipe.build(project_root, level)
    candidate = replace(
        baseline,
        gate=recipe.declared_gate,
        delay=recipe.declared_delay,
        components=components,
        wires=wires,
    )
    connectivity = analyze_connectivity(candidate)
    if connectivity["unsupported_component_kind_counts"]:
        raise ValueError(f"recipe {level} contains unsupported components")
    if connectivity["unconnected_pin_count"]:
        raise ValueError(
            f"recipe {level} has unconnected pins: {connectivity['unconnected_pins']}"
        )
    if connectivity["cycle_component_count"]:
        raise ValueError(f"recipe {level} unexpectedly contains a logic cycle")
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError(f"recipe {level} failed v15 verification")
    destination = project_root / "examples" / level / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    (destination.parent / ".gitkeep").unlink(missing_ok=True)
    return {
        "level": level,
        "path": f"{level}/candidate/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "declared_gate": candidate.gate,
        "declared_delay": candidate.delay,
        "declared_energy": candidate.energy,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "unit_logic_depth": connectivity["unit_logic_depth"],
        "connected_pin_count": connectivity["connected_pin_count"],
    }


def build_known_candidates(project_root: Path) -> dict[str, object]:
    records = [build_recipe(project_root, level) for level in RECIPES]
    analyze_examples(project_root)
    return {"candidate_count": len(records), "candidates": records}
