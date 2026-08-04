"""Structural readability metrics for layered physical layouts."""

from __future__ import annotations

from collections import defaultdict

from turingsynth.ir.physical import PhysicalDesign


def audit_layout_readability(
    design: PhysicalDesign,
    ranks: dict[str, int],
) -> dict[str, object]:
    """Measure whether reconvergent logic cones form compact visual motifs.

    A common consumer should normally sit immediately to the right of its
    producer cone. For the smallest reconvergent case, two same-layer
    producers should be adjacent and the consumer should be vertically
    centered between them. Gate kinds are intentionally irrelevant: the same
    structural rule applies to ordinary gates, phase logic, and Switch owners.
    These metrics describe placement before routing so a maze of wires cannot
    hide a structurally poor layout.
    """

    components = design.component_by_key()
    if any(component.position is None for component in components.values()):
        raise ValueError("readability audit requires a fully placed design")

    predecessors: dict[str, set[str]] = defaultdict(set)
    for net in design.nets:
        for sink in net.sinks:
            predecessors[sink.component].update(
                source.component
                for source in net.sources
                if source.component != sink.component
            )

    layer_order: dict[int, list[str]] = defaultdict(list)
    for key, component in components.items():
        if component.role == "gate":
            layer_order[ranks[key]].append(key)
    layer_index: dict[str, int] = {}
    for rank, keys in layer_order.items():
        keys.sort(
            key=lambda key: (
                components[key].position[1],  # type: ignore[index]
                components[key].position[0],  # type: ignore[index]
                key,
            )
        )
        layer_index.update({key: index for index, key in enumerate(keys)})

    motifs = []
    for consumer_key, producer_keys in predecessors.items():
        consumer = components[consumer_key]
        if consumer.role != "gate" or len(producer_keys) != 2:
            continue
        producers = tuple(sorted(producer_keys))
        if any(components[key].role != "gate" for key in producers):
            continue
        producer_ranks = {ranks[key] for key in producers}
        if len(producer_ranks) != 1:
            continue
        producer_rank = next(iter(producer_ranks))
        if producer_rank >= ranks[consumer_key]:
            continue

        left, right = sorted(producers, key=lambda key: layer_index[key])
        left_y = components[left].position[1]  # type: ignore[index]
        right_y = components[right].position[1]  # type: ignore[index]
        consumer_y = consumer.position[1]  # type: ignore[index]
        intervening = layer_index[right] - layer_index[left] - 1
        doubled_center_error = abs(2 * consumer_y - left_y - right_y)
        motif = {
            "consumer": consumer_key,
            "consumer_kind": consumer.kind,
            "consumer_rank": ranks[consumer_key],
            "producers": [left, right],
            "producer_kinds": [components[left].kind, components[right].kind],
            "producer_rank": producer_rank,
            "intervening_component_count": intervening,
            "producer_vertical_span": abs(right_y - left_y),
            "consumer_center_error": doubled_center_error / 2,
            "adjacent": intervening == 0,
            "centered": doubled_center_error <= 2,
        }
        motif["triangle_ready"] = motif["adjacent"] and motif["centered"]
        motifs.append(motif)

    motifs.sort(
        key=lambda item: (
            -int(item["intervening_component_count"]),
            -float(item["consumer_center_error"]),
            str(item["consumer"]),
        )
    )
    return {
        "schema": "turingsynth-layout-readability-v1",
        "reconvergent_pair_count": len(motifs),
        "adjacent_pair_count": sum(bool(item["adjacent"]) for item in motifs),
        "interleaved_pair_count": sum(not bool(item["adjacent"]) for item in motifs),
        "centered_consumer_count": sum(bool(item["centered"]) for item in motifs),
        "triangle_ready_count": sum(bool(item["triangle_ready"]) for item in motifs),
        "total_intervening_components": sum(
            int(item["intervening_component_count"]) for item in motifs
        ),
        "total_consumer_center_error": sum(
            float(item["consumer_center_error"]) for item in motifs
        ),
        "worst_motifs": motifs[:16],
    }
