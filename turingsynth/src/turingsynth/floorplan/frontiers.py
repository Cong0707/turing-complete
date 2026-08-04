"""Extract strict I/O conductor frontiers without performing placement."""

from __future__ import annotations

from collections import defaultdict, deque
import re

from turingsynth.floorplan.timing import analyze_timing
from turingsynth.ir.floorplan import (
    BusTrunk,
    ConductorTip,
    Floorplan,
    FlowFrame,
    GrowthCone,
    OutputMerge,
    PlannedConductor,
    TapSocket,
    TrunkLane,
)
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


def _planned_conductors(
    design: PhysicalDesign,
    frame: FlowFrame,
    input_trunks: tuple[BusTrunk, ...],
) -> tuple[PlannedConductor, ...]:
    arrivals = frame.arrival_by_net()
    required = frame.required_by_net()
    facts = frame.fact_by_component()
    trunk_lane_by_net = {
        lane.net: (trunk.key, lane.index)
        for trunk in input_trunks
        for lane in trunk.lanes
    }
    result = []
    for net in sorted(design.nets, key=lambda item: item.name):
        trunk_lane = trunk_lane_by_net.get(net.name)
        tips = tuple(
            ConductorTip(
                key=f"{net.name}:driver:{index}",
                net=net.name,
                source=source,
                arrival=arrivals[net.name],
                trunk_key=trunk_lane[0] if trunk_lane is not None else None,
                lane_index=trunk_lane[1] if trunk_lane is not None else None,
            )
            for index, source in enumerate(net.sources)
        )
        sockets = tuple(
            TapSocket(
                key=f"{net.name}:sink:{index}",
                net=net.name,
                sink=sink,
                required=required[net.name],
                slack=max(0, required[net.name] - arrivals[net.name]),
                critical=(
                    required[net.name] <= arrivals[net.name]
                    or facts[sink.component].critical_input_net == net.name
                ),
            )
            for index, sink in enumerate(net.sinks)
        )
        critical = any(socket.critical for socket in sockets)
        result.append(
            PlannedConductor(
                key=f"conductor:{net.name}",
                net=net.name,
                tips=tips,
                sockets=sockets,
                timing_priority=(
                    frame.target_delay * 2
                    - min(frame.target_delay, required[net.name])
                    + (frame.target_delay if critical else 0)
                ),
                critical=critical,
            )
        )
    return tuple(result)


def _growth_cones(
    design: PhysicalDesign,
    frame: FlowFrame,
    input_trunks: tuple[BusTrunk, ...],
    output_merges: tuple[OutputMerge, ...],
    conductors: tuple[PlannedConductor, ...],
    incoming: dict[str, list[PhysicalNet]],
) -> tuple[GrowthCone, ...]:
    components = design.component_by_key()
    conductor_by_net = {conductor.net: conductor for conductor in conductors}
    net_by_name = {net.name: net for net in design.nets}
    order = {key: index for index, key in enumerate(frame.topological_order)}
    input_frontiers = {
        net: trunk.key
        for trunk in input_trunks
        for net in trunk.frontier_nets
    }
    facts = frame.fact_by_component()
    result = []
    for merge in output_merges:
        stack = list(merge.frontier_nets)
        seen_nets: set[str] = set()
        cone_components: set[str] = set()
        while stack:
            net_name = stack.pop()
            if net_name in seen_nets:
                continue
            seen_nets.add(net_name)
            net = net_by_name[net_name]
            for source in net.sources:
                component = components[source.component]
                if component.role != "gate":
                    continue
                if component.key in cone_components:
                    continue
                cone_components.add(component.key)
                for predecessor in incoming[component.key]:
                    if predecessor.name in input_frontiers:
                        seen_nets.add(predecessor.name)
                    else:
                        stack.append(predecessor.name)

        entry_nets = {
            net.name
            for net in design.nets
            if any(sink.component in cone_components for sink in net.sinks)
            and any(source.component not in cone_components for source in net.sources)
        }
        cone_conductors = tuple(
            conductor_by_net[name]
            for name in sorted(seen_nets | entry_nets)
            if name in conductor_by_net
        )
        entry_tips = tuple(
            tip
            for name in sorted(entry_nets)
            for tip in conductor_by_net[name].tips
        )
        output_tips = tuple(
            tip
            for name in merge.frontier_nets
            for tip in conductor_by_net[name].tips
        )
        tap_sockets = tuple(
            socket
            for conductor in cone_conductors
            for socket in conductor.sockets
            if socket.sink.component in cone_components
        )
        ordered_components = tuple(
            sorted(cone_components, key=lambda key: (order[key], key))
        )
        result.append(
            GrowthCone(
                key=f"cone:{merge.key}",
                components=ordered_components,
                input_trunks=tuple(
                    sorted(
                        {
                            input_frontiers[name]
                            for name in entry_nets
                            if name in input_frontiers
                        }
                    )
                ),
                entry_tips=entry_tips,
                tap_sockets=tap_sockets,
                output_tips=output_tips,
                critical_delay=max(
                    (facts[key].arrival for key in cone_components),
                    default=0,
                ),
            )
        )
    return tuple(result)


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
    conductors = _planned_conductors(design, frame, input_trunks)
    growth_cones = _growth_cones(
        design,
        frame,
        input_trunks,
        output_merges,
        conductors,
        incoming,
    )
    return Floorplan(
        design_name=design.name,
        timing=frame,
        input_trunks=input_trunks,
        growth_cones=growth_cones,
        conductors=conductors,
        output_merges=output_merges,
    )
