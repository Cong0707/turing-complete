"""Generate and verify the current-version ASIC solution for The Maze."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component
from .pins import analyze_connectivity


MAZES: tuple[tuple[int, ...], ...] = (
    (0b1111111111111111111111111, 0b1000100000001010001000001, 0b1110111110111010111011101, 0b1000100010000010000010101, 0b1011101111101110111010101, 0b1010101010000000101010001, 0b1010101011111011101110111, 0b1000000000000010000000001, 0b1111111111111111111111111),
    (0b1111111111111111111111111, 0b1000101000000010000000001, 0b1010001011101110111011101, 0b1010100000100010100010101, 0b1010101110111010111110101, 0b1010100010001010101010001, 0b1111101111111010101010111, 0b1000000000100000001000001, 0b1111111111111111111111111),
    (0b1111111111111111111111111, 0b1000000000100000000010001, 0b1011111110111011111111101, 0b1010101000100010001000001, 0b1010101110101110101111101, 0b1000101010000000100010001, 0b1011101010111110111010111, 0b1000001000000010100000001, 0b1111111111111111111111111),
    (0b1111111111111111111111111, 0b1000001000000010000000001, 0b1010111111101010111011111, 0b1010000010001000100000001, 0b1010111010111011111111101, 0b1010100010001010100000001, 0b1010101110101010111011101, 0b1010100000101000100000101, 0b1111111111111111111111111),
    (0b1111111111111111111111111, 0b1000000000000000000000001, 0b1111101011111011101110111, 0b1000101000100000100010101, 0b1110111011101110101110101, 0b1000100000101000101010101, 0b1011101111111011101011101, 0b1000000000100000100000001, 0b1111111111111111111111111),
    (0b1111111111111111111111111, 0b1010000000100000001000001, 0b1011101111111011111110101, 0b1000001000101010100010101, 0b1110101011101010101011101, 0b1010100010000010001000001, 0b1010111010111110111011101, 0b1000100000000000001010001, 0b1111111111111111111111111),
    (0b1111111111111111111111111, 0b1010000000001000100010001, 0b1010101111101110111010101, 0b1000101000000010000000101, 0b1110111111111111101111101, 0b1000100000000000000010001, 0b1010101110111010101111101, 0b1010001000100010101000001, 0b1111111111111111111111111),
    (0b1111111111111111111111111, 0b1000000000000000100000001, 0b1111101110111110111010101, 0b1000001000100000000010101, 0b1110111011111011111010101, 0b1000100000001000100010101, 0b1111101110111111101011101, 0b1000000010100000001010001, 0b1111111111111111111111111),
)

DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))
EXPECTED_CYCLES = (347, 161, 263, 207, 167, 373, 325, 123)


def _wall(maze: tuple[int, ...], x: int, y: int) -> int:
    return (maze[y] >> (25 - x)) & 1


def simulate_maze(maze: tuple[int, ...], *, limit: int = 4096) -> int:
    """Run q_next=NOR(q, wall), output={q, q_next} from the level start."""

    x, y, rotation, state = 24, 7, 3, 0
    seen: set[tuple[int, int, int, int]] = set()
    for cycle in range(limit):
        if (x, y, rotation) == (2, 1, 0):
            return cycle
        snapshot = (x, y, rotation, state)
        if snapshot in seen:
            raise RuntimeError(f"maze ASIC entered a loop at {snapshot}")
        seen.add(snapshot)

        dx, dy = DIRECTIONS[rotation]
        wall = _wall(maze, x + dx, y + dy)
        next_state = int(not state and not wall)
        command = next_state | (state << 1)
        state = next_state

        if command == 0:
            rotation = (rotation + 3) % 4
        elif command == 1:
            next_x, next_y = x + dx, y + dy
            if not _wall(maze, next_x, next_y):
                x, y = next_x, next_y
        elif command == 2:
            rotation = (rotation + 1) % 4
    raise RuntimeError(f"maze ASIC did not finish within {limit} cycles")


def build_maze_asic() -> Circuit:
    key = "architecture/codex-maze"
    component = lambda role, kind, position, **kwargs: Component(
        kind=kind,
        position=position,
        rotation=0,
        permanent_id=stable_permanent_id(key, role),
        **kwargs,
    )
    components = (
        component("level-input", 62, (-24, 0), word_size=8),
        component("level-output", 70, (30, 0), word_size=8),
        component("input-enable", 2, (-28, -2)),
        component("output-enable", 2, (25, -5)),
        component("state-next-nor", 9, (-12, 0)),
        component("state-delay", 13, (-3, 0), init_data=0),
        component("command-maker", 16, (18, 0)),
        *(component(f"zero-bit-{bit}", 1, (14, bit - 3)) for bit in range(2, 8)),
    )
    wires = (
        wire_from_vertices(((-27, -2), (-23, -2))),
        wire_from_vertices(((26, -5), (27, -5), (29, -3), (29, -2))),
        wire_from_vertices(((-21, 0), (-15, 0), (-13, -2), (-13, -1))),
        wire_from_vertices(((0, 0), (0, 5), (-15, 5), (-15, 3), (-13, 1))),
        wire_from_vertices(((-10, 0), (-6, 0))),
        wire_from_vertices(((-10, 0), (-8, -2), (16, -2), (17, -3))),
        wire_from_vertices(((0, 0), (2, 0), (4, -2), (17, -2))),
        *(wire_from_vertices(((15, bit - 3), (17, bit - 3))) for bit in range(2, 8)),
        wire_from_vertices(((19, 0), (27, 0))),
    )
    return Circuit(
        gate=6,
        delay=5,
        description="Codex maze ASIC: q_next = NOR(q, wall), command = {q, q_next}",
        components=components,
        wires=wires,
    )


def verify_maze_asic(circuit: Circuit | None = None) -> dict[str, object]:
    candidate = build_maze_asic() if circuit is None else circuit
    cycles = tuple(simulate_maze(maze) for maze in MAZES)
    if cycles != EXPECTED_CYCLES:
        raise RuntimeError(f"maze cycle regression: {cycles!r}")
    connectivity = analyze_connectivity(candidate)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"maze ASIC failed connectivity check {field}: {connectivity[field]}")
    if connectivity["width_mismatch_network_count"] != 1:
        raise RuntimeError(
            "maze ASIC must keep exactly one runtime-confirmed U8-to-U1 truncation"
        )
    return {
        "gate": candidate.gate,
        "delay": candidate.delay,
        "cycles": list(cycles),
        "maximum_cycles": max(cycles),
        "leaderboard_tuple": [candidate.gate, candidate.delay, max(cycles)],
        "energy": candidate.gate * candidate.delay * max(cycles),
        "connectivity": connectivity,
    }


def write_maze_asic(project_root: Path) -> dict[str, object]:
    candidate = build_maze_asic()
    verification = verify_maze_asic(candidate)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("maze ASIC failed v15 round-trip verification")
    destination = project_root / "examples" / "maze" / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    metadata = {
        "schema": 1,
        "level": "maze",
        "title": "The Maze",
        "strategy": "current-v15 ASIC",
        "deployment_target": "schematics/architecture/CODEX-MAZE/circuit.data",
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
