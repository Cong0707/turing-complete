"""Extract strict I/O conductor frontiers without performing placement."""

from __future__ import annotations

from collections import defaultdict, deque
import re

from turingsynth.floorplan.timing import analyze_timing
from turingsynth.ir.floorplan import BusTrunk, Floorplan, FlowFrame, OutputMerge, TrunkLane
from turingsynth.ir.physical import PhysicalComponent, PhysicalDesign, PhysicalNet


_PIN_ORDINAL = re.compile(r"^(.*?)(\d+)$")


def _is_free(component: PhysicalComponent, role: str) -> bool:
    return (
        component.role == role
        and component.gate_cost == 0
        and component.gate_delay == 0
    )


def _pin_sort_key(pin: str) -> tuple[str, int, str]:
    match = _PIN_ORDINAL.match(pin)
    if match is None:
        return pin, -1, pin
    return match.group(1), int(match.group(2)), pin


def _net_sort_key(net: PhysicalNet) -> tuple[tuple[str, int, str], str]:
    return _pin_sort_key(net.source.pin), net.name


def _input_trunk(
    input_key: str,
    components: dict[str, PhysicalComponent],
    outgoing: dict[str, list[PhysicalNet]],
    arrivals: dict[str, int],
) -> BusTrunk:
    root_nets = tuple(
        sorted(
            (
                net
                for net in outgoing[input_key]
                if len(net.sources) == 1 and net.source.component == input_key
            ),
            key=lambda net: net.name,
        )
    )
    queue: deque[tuple[PhysicalNet, tuple[str, ...], tuple[str, ...]]] = deque(
        (net, (net.name,), ()) for net in root_nets
    )
    seen: set[str] = set()
    frontier: dict[str, tuple[PhysicalNet, tuple[str, ...], tuple[str, ...]]] = {}
    splitters: set[str] = set()
    while queue:
        net, lineage, branch_path = queue.popleft()
        if net.name in seen:
            continue
        seen.add(net.name)
        free_splitter_sinks = sorted(
            {
                sink.component
                for sink in net.sinks
                if _is_free(components[sink.component], "splitter")
            }
        )
        boundary_sinks = tuple(
            sink
            for sink in net.sinks
            if sink.component not in free_splitter_sinks
        )
        if boundary_sinks or not free_splitter_sinks:
            frontier[net.name] = (net, lineage, branch_path)
        for splitter_key in free_splitter_sinks:
            splitters.add(splitter_key)
            children = sorted(
                (
                    child
                    for child in outgoing[splitter_key]
                    if len(child.sources) == 1
                    and child.source.component == splitter_key
                ),
                key=_net_sort_key,
            )
            for child in children:
                queue.append(
                    (
                        child,
                        (*lineage, child.name),
                        (*branch_path, f"{splitter_key}:{child.source.pin}"),
                    )
                )

    ordered_frontier = sorted(
        frontier.values(),
        key=lambda value: (
            tuple(_pin_sort_key(part.rsplit(":", 1)[-1]) for part in value[2]),
            value[0].name,
        ),
    )
    lanes = tuple(
        TrunkLane(
            index=index,
            net=net.name,
            width=net.width,
            source=net.source,
            lineage=lineage,
            branch_path=branch_path,
            arrival=arrivals[net.name],
        )
        for index, (net, lineage, branch_path) in enumerate(ordered_frontier)
    )
    return BusTrunk(
        key=f"input:{input_key}",
        input_port=input_key,
        root_nets=tuple(net.name for net in root_nets),
        frontier_nets=tuple(lane.net for lane in lanes),
        lanes=lanes,
        splitters=tuple(sorted(splitters)),
    )


def _output_merge(
    output_key: str,
    components: dict[str, PhysicalComponent],
    incoming: dict[str, list[PhysicalNet]],
) -> OutputMerge:
    roots = tuple(sorted(incoming[output_key], key=lambda net: net.name))
    queue: deque[PhysicalNet] = deque(roots)
    seen: set[str] = set()
    makers: set[str] = set()
    frontier: set[str] = set()
    while queue:
        net = queue.popleft()
        if net.name in seen:
            continue
        seen.add(net.name)
        if len(net.sources) != 1:
            frontier.add(net.name)
            continue
        source_component = components[net.source.component]
        if not _is_free(source_component, "maker"):
            frontier.add(net.name)
            continue
        makers.add(source_component.key)
        maker_inputs = tuple(sorted(incoming[source_component.key], key=lambda item: item.name))
        if not maker_inputs:
            frontier.add(net.name)
            continue
        queue.extend(maker_inputs)
    return OutputMerge(
        key=f"output:{output_key}",
        output_port=output_key,
        root_nets=tuple(net.name for net in roots),
        frontier_nets=tuple(sorted(frontier)),
        makers=tuple(sorted(makers)),
    )


def extract_io_frontiers(
    design: PhysicalDesign,
    timing: FlowFrame | None = None,
) -> Floorplan:
    """Build strict input/output frontiers for conductor-first floorplanning.

    A normal high-fanout network is never promoted to an input trunk.  Trunks
    begin only at a component whose declared role is ``input_port`` and may
    expand only through zero-gate, zero-delay ``splitter`` components.  Output
    frontiers apply the exact reverse rule through free ``maker`` components.
    """

    frame = analyze_timing(design) if timing is None else timing
    if frame.design_name != design.name:
        raise ValueError(
            f"timing frame belongs to {frame.design_name!r}, not {design.name!r}"
        )
    components = design.component_by_key()
    timed_components = set(frame.fact_by_component())
    timed_nets = set(frame.arrival_by_net())
    if timed_components != set(components) or timed_nets != {
        net.name for net in design.nets
    }:
        raise ValueError("timing frame does not cover this physical design")
    incoming: dict[str, list[PhysicalNet]] = defaultdict(list)
    outgoing: dict[str, list[PhysicalNet]] = defaultdict(list)
    for net in design.nets:
        for source in net.sources:
            outgoing[source.component].append(net)
        for sink in net.sinks:
            incoming[sink.component].append(net)

    arrivals = frame.arrival_by_net()
    input_trunks = tuple(
        _input_trunk(key, components, outgoing, arrivals)
        for key in sorted(
            key for key, component in components.items() if component.role == "input_port"
        )
    )
    output_merges = tuple(
        _output_merge(key, components, incoming)
        for key in sorted(
            key for key, component in components.items() if component.role == "output_port"
        )
    )
    return Floorplan(
        design_name=design.name,
        timing=frame,
        input_trunks=input_trunks,
        growth_cones=(),
        conductors=(),
        output_merges=output_merges,
    )
