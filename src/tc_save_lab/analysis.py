"""Offline geometry and structural metrics for circuit candidates.

This module deliberately does not infer logical connectivity from a wire merely
because it crosses a component bounding box.  Pin geometry is versioned in a
separate library; until that library is loaded, the reported network metrics
are wire-to-wire facts only.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import json

from .binary import FormatError
from .codec import decode_circuit
from .model import Circuit, Point, Wire


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


class _UnionFind:
    def __init__(self, size: int):
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def wire_points(wire: Wire) -> tuple[Point, ...]:
    """Expand a wire path to grid points, including its start and end."""

    points: list[Point] = [wire.start]
    if wire.teleport_end is not None:
        points.append(wire.teleport_end)
        return tuple(points)
    x, y = wire.start
    for direction, length in wire.segments:
        if direction < 0 or direction >= len(DIRECTIONS):
            raise FormatError(f"invalid wire direction {direction}")
        if length < 1:
            raise FormatError(f"invalid wire length {length}")
        dx, dy = DIRECTIONS[direction]
        for _ in range(length):
            x += dx
            y += dy
            points.append((x, y))
    return tuple(points)


def _duplicates(values: list[int]) -> list[int]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _bbox(points: list[Point]) -> dict[str, int] | None:
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return {
        "min_x": min(xs),
        "min_y": min(ys),
        "max_x": max(xs),
        "max_y": max(ys),
        "width": max(xs) - min(xs) + 1,
        "height": max(ys) - min(ys) + 1,
    }


def _wire_metrics(wires: tuple[Wire, ...]) -> dict[str, object]:
    expanded = [wire_points(wire) for wire in wires]
    point_owners: dict[Point, list[int]] = {}
    for index, points in enumerate(expanded):
        for point in set(points):
            point_owners.setdefault(point, []).append(index)

    union_find = _UnionFind(len(wires))
    shared_points = [point for point, owners in point_owners.items() if len(owners) > 1]
    for owners in point_owners.values():
        for index in owners[1:]:
            union_find.union(owners[0], index)

    network_roots = {union_find.find(index) for index in range(len(wires))}
    segment_count = sum(len(wire.segments) for wire in wires)
    total_length = sum(
        sum(length for _, length in wire.segments) for wire in wires
    )
    bend_count = 0
    for wire in wires:
        directions = [direction for direction, _ in wire.segments]
        bend_count += sum(
            left != right for left, right in zip(directions, directions[1:])
        )
    all_points = [point for points in expanded for point in points]
    overlap_points = sum(
        max(0, len(owners) - 1) for owners in point_owners.values()
    )
    return {
        "wire_count": len(wires),
        "segment_count": segment_count,
        "total_length": total_length,
        "maximum_length": max(
            (sum(length for _, length in wire.segments) for wire in wires),
            default=0,
        ),
        "bend_count": bend_count,
        "network_count": len(network_roots),
        "shared_point_count": len(shared_points),
        "overlap_point_count": overlap_points,
        "expanded_point_count": len(set(all_points)),
        "bounding_box": _bbox(all_points),
        "teleport_wire_count": sum(wire.teleport_end is not None for wire in wires),
    }


def analyze_circuit(circuit: Circuit, *, format_version: int = 15) -> dict[str, object]:
    component_ids = [component.permanent_id for component in circuit.components]
    component_points = [component.position for component in circuit.components]
    wire = _wire_metrics(circuit.wires)
    result: dict[str, object] = {
        "format_version": format_version,
        "declared_gate": circuit.gate,
        "declared_delay": circuit.delay,
        "declared_energy_gate_delay": circuit.energy,
        "component_count": len(circuit.components),
        "immutable_component_count": sum(
            component.immutable for component in circuit.components
        ),
        "component_kind_counts": dict(
            sorted(Counter(component.kind for component in circuit.components).items())
        ),
        "unique_permanent_id_count": len(set(component_ids)),
        "duplicate_permanent_ids": _duplicates(component_ids),
        "component_bounding_box": _bbox(component_points),
        "wire": wire,
    }
    return result


def analyze_file(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": str(path),
        "size": len(payload),
        "sha256": sha256(payload).hexdigest(),
        "metrics": analyze_circuit(
            decode_circuit(payload), format_version=payload[0]
        ),
    }


def analyze_examples(project_root: Path) -> dict[str, object]:
    examples = project_root / "examples"
    manifest_path = examples / "manifest.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    generated = 0
    missing = 0
    for level_record in manifest["levels"]:
        level = level_record["level"]
        architecture = level_record.get("architecture")
        if architecture:
            source = examples / "_architectures" / architecture / "baseline" / "circuit.data"
            source_relative = (
                f"_architectures/{architecture}/baseline/circuit.data"
            )
        else:
            source = examples / level / "baseline" / "circuit.data"
            source_relative = f"{level}/baseline/circuit.data"
        baseline_analysis = analyze_file(source) if source.is_file() else None
        if baseline_analysis is not None:
            baseline_analysis["path"] = source_relative
        result: dict[str, object] = {
            "level": level,
            "kind": level_record.get("kind"),
            "scoreable": level_record.get("scoreable"),
            "source": source_relative,
            "baseline": baseline_analysis,
            "candidate": None,
        }
        candidate = (
            examples / "_architectures" / architecture / "candidate" / "circuit.data"
            if architecture
            else examples / level / "candidate" / "circuit.data"
        )
        if candidate.is_file():
            candidate_analysis = analyze_file(candidate)
            candidate_analysis["path"] = str(candidate.relative_to(examples)).replace(
                "\\", "/"
            )
            result["candidate"] = candidate_analysis
        if result["baseline"] is None:
            missing += 1
        else:
            generated += 1
        (examples / level / "metrics.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    summary = {
        "level_count": len(manifest["levels"]),
        "metrics_written": generated,
        "baseline_missing": missing,
    }
    (examples / "metrics-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary
