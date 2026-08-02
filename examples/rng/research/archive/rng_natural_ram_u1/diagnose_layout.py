"""Report exact conservative wire/component contacts for the natural RAM RNG."""

from __future__ import annotations

import json

from build_candidate import build_candidate
from tc_save_lab.analysis import wire_points
from tc_save_lab.pins import positioned_pins
from tc_save_lab import rng_encoded_asic as encoded
from tc_save_lab import rng_ram_asic as ram_asic


def main() -> None:
    _, candidate, _ = build_candidate()
    footprints = ram_asic._component_footprints(candidate.components)
    access_map = encoded._pin_access_map(candidate.components, footprints)
    pins_by_component = [
        {pin.position for pin in positioned_pins(component, index)}
        for index, component in enumerate(candidate.components)
    ]
    ram_group = {
        index
        for index, component in enumerate(candidate.components)
        if component.kind in {54, 56, 118}
    }
    visible_ram_port_points = set().union(
        *(pins_by_component[index] for index in ram_group)
    )
    contacts = []
    for wire_index, wire in enumerate(candidate.wires):
        points = wire_points(wire)
        endpoints = {points[0], points[-1]}
        permitted = frozenset().union(
            *(access_map.get(endpoint, frozenset({endpoint})) for endpoint in endpoints)
        )
        for component_index, (component, footprint, pins) in enumerate(
            zip(candidate.components, footprints, pins_by_component)
        ):
            bad = []
            for point in points:
                if point not in footprint:
                    continue
                if point in endpoints and point in pins:
                    continue
                if point in permitted:
                    continue
                if component_index in ram_group and point in visible_ram_port_points:
                    continue
                bad.append(point)
            if bad:
                contacts.append(
                    {
                        "wire_index": wire_index,
                        "source": list(points[0]),
                        "sink": list(points[-1]),
                        "component_index": component_index,
                        "component_kind": component.kind,
                        "component_position": list(component.position),
                        "points": [list(point) for point in sorted(set(bad))],
                    }
                )
    print(json.dumps(contacts, indent=2))


if __name__ == "__main__":
    main()
