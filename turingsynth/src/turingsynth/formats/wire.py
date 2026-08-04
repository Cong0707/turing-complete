"""Deterministic v15 wire construction and expansion."""

from __future__ import annotations

from .model import Point, Wire


DIRECTIONS: tuple[Point, ...] = (
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1),
    (0, -1),
    (1, -1),
)
DIRECTION_BY_STEP = {step: index for index, step in enumerate(DIRECTIONS)}


def wire_from_vertices(
    vertices: tuple[Point, ...], *, color: int = 0, comment: str = ""
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
            raise ValueError(f"non-octilinear wire segment: {start} -> {end}")
        step = (
            0 if dx == 0 else dx // abs(dx),
            0 if dy == 0 else dy // abs(dy),
        )
        direction = DIRECTION_BY_STEP[step]
        if segments and segments[-1][0] == direction:
            previous_direction, previous_length = segments[-1]
            segments[-1] = (previous_direction, previous_length + length)
        else:
            segments.append((direction, length))
    if not segments:
        raise ValueError("wire route has zero length")
    return Wire(color=color, comment=comment, start=vertices[0], segments=tuple(segments))


def wire_points(wire: Wire) -> tuple[Point, ...]:
    points = [wire.start]
    x, y = wire.start
    for direction, length in wire.segments:
        dx, dy = DIRECTIONS[direction]
        for _ in range(length):
            x += dx
            y += dy
            points.append((x, y))
    return tuple(points)
