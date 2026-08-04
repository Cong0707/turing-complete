"""Render the exact placed/routed graph as a readable standalone SVG."""

from __future__ import annotations

from html import escape
from pathlib import Path

from turingsynth.formats.model import Component
from turingsynth.formats.wire import wire_points
from turingsynth.ir.physical import PhysicalComponent, PhysicalDesign
from turingsynth.mapping.native import COMPONENTS, component_bounds
from turingsynth.routing.astar import RoutingResult


PALETTE = ("#2563eb", "#0f766e", "#b45309", "#be123c", "#7c3aed", "#0369a1")
ROLE_FILL = {
    "input_port": "#dbeafe",
    "output_port": "#dcfce7",
    "gate": "#f8fafc",
    "maker": "#fef3c7",
    "splitter": "#ccfbf1",
    "constant": "#f3e8ff",
    "template": "#e5e7eb",
}


def _component(value: PhysicalComponent) -> Component:
    assert value.position is not None
    return Component(
        kind=value.kind,
        position=value.position,
        rotation=value.rotation,
        permanent_id=value.permanent_id,
        word_size=value.word_size,
    )


def render_svg(
    design: PhysicalDesign, routing: RoutingResult, destination: Path
) -> None:
    scale = 12
    component_bounds_by_key = {
        component.key: component_bounds(_component(component))
        for component in design.components
    }
    points = [
        point for wire in routing.wires for point in wire_points(wire)
    ]
    minimum_x = min(
        [value[0] for value in component_bounds_by_key.values()]
        + [point[0] for point in points]
    )
    maximum_x = max(
        [value[1] for value in component_bounds_by_key.values()]
        + [point[0] for point in points]
    )
    minimum_y = min(
        [value[2] for value in component_bounds_by_key.values()]
        + [point[1] for point in points]
    )
    maximum_y = max(
        [value[3] for value in component_bounds_by_key.values()]
        + [point[1] for point in points]
    )
    margin = 3
    width = (maximum_x - minimum_x + 1 + margin * 2) * scale
    height = (maximum_y - minimum_y + 1 + margin * 2) * scale

    def xy(point: tuple[int, int]) -> tuple[int, int]:
        return (
            (point[0] - minimum_x + margin) * scale,
            (point[1] - minimum_y + margin) * scale,
        )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<g fill="none" stroke-linecap="round" stroke-linejoin="round">',
    ]
    for wire, routed in zip(routing.wires, routing.edges):
        polyline = " ".join(f"{x},{y}" for x, y in map(xy, wire_points(wire)))
        color = PALETTE[sum(routed.network.encode("utf-8")) % len(PALETTE)]
        lines.append(
            f'<polyline points="{polyline}" stroke="{color}" stroke-width="2" opacity="0.78">'
            f'<title>{escape(routed.network)}</title></polyline>'
        )
    lines.append("</g>")
    for component in design.components:
        left, right, top, bottom = component_bounds_by_key[component.key]
        x, y = xy((left, top))
        box_width = (right - left + 1) * scale
        box_height = (bottom - top + 1) * scale
        fill = ROLE_FILL.get(component.role, "#ffffff")
        spec_name = COMPONENTS[component.kind].name
        title = (
            f"{component.key} | {spec_name} | U{component.word_size} | "
            f"cost {component.gate_cost}/{component.gate_delay}"
        )
        label = component.user_label or f"{spec_name} U{component.word_size}"
        lines.append(
            f'<g><rect x="{x}" y="{y}" width="{box_width}" height="{box_height}" '
            f'rx="2" fill="{fill}" stroke="#111827" stroke-width="1.4">'
            f'<title>{escape(title)}</title></rect>'
            f'<text x="{x + box_width / 2}" y="{y + box_height / 2 + 4}" '
            f'text-anchor="middle" font-family="Consolas, monospace" font-size="9" '
            f'fill="#111827">{escape(label[:24])}</text></g>'
        )
    lines.append("</svg>")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
