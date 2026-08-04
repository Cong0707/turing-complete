"""Static timing analysis for coordinate-free physical designs."""

from __future__ import annotations

from collections import defaultdict

from turingsynth.ir.floorplan import FlowFrame, TimingFact
from turingsynth.ir.physical import (
    PhysicalComponent,
    PhysicalDesign,
    PhysicalNet,
    PinRef,
)


def _validate_design(
    design: PhysicalDesign,
) -> tuple[dict[str, PhysicalComponent], dict[str, PhysicalNet]]:
    components = design.component_by_key()
    nets: dict[str, PhysicalNet] = {}
    for net in design.nets:
        if net.name in nets:
            raise ValueError(f"physical design has duplicate net name {net.name!r}")
        nets[net.name] = net
        for ref in (*net.sources, *net.sinks):
            if ref.component not in components:
                raise ValueError(
                    f"net {net.name!r} references missing component {ref.component!r}"
                )
    if design.delay < 0:
        raise ValueError("physical design delay cannot be negative")
    return components, nets


def _topological_order(design: PhysicalDesign) -> tuple[str, ...]:
    components, _nets = _validate_design(design)
    predecessors: dict[str, set[str]] = {key: set() for key in components}
    successors: dict[str, set[str]] = {key: set() for key in components}
    for net in design.nets:
        for source in net.sources:
            for sink in net.sinks:
                predecessors[sink.component].add(source.component)
                successors[source.component].add(sink.component)

    indegree = {key: len(values) for key, values in predecessors.items()}
    ready = sorted(key for key, count in indegree.items() if count == 0)
    order: list[str] = []
    while ready:
        key = ready.pop(0)
        order.append(key)
        for successor in sorted(successors[key]):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
        ready.sort()
    if len(order) != len(components):
        blocked = sorted(key for key, count in indegree.items() if count)
        raise ValueError(f"physical timing graph contains a cycle near {blocked[:8]!r}")
    return tuple(order)


def _critical_input(
    component: str,
    incoming_nets: tuple[PhysicalNet, ...],
    component_arrival: dict[str, int],
    net_arrival: dict[str, int],
) -> tuple[str | None, PinRef | None, PinRef | None]:
    if not incoming_nets:
        return None, None, None
    critical_net = min(
        incoming_nets,
        key=lambda net: (-net_arrival[net.name], net.name),
    )
    sink = min(
        (ref for ref in critical_net.sinks if ref.component == component),
        key=lambda ref: ref.pin,
    )
    source = min(
        critical_net.sources,
        key=lambda ref: (-component_arrival[ref.component], ref.component, ref.pin),
    )
    return critical_net.name, sink, source


def analyze_timing(design: PhysicalDesign) -> FlowFrame:
    """Calculate arrival, required time, slack, and each critical input.

    Timing facts are measured at component outputs.  A sink component consumes
    the maximum arrival of all sources on each incoming physical net, then adds
    its own ``gate_delay``.  Required times use the mapped design delay as the
    common output horizon, making non-critical output cones retain visible
    positive slack.
    """

    components, nets = _validate_design(design)
    order = _topological_order(design)
    incoming: dict[str, list[PhysicalNet]] = defaultdict(list)
    outgoing: dict[str, list[PhysicalNet]] = defaultdict(list)
    for net in design.nets:
        for sink in net.sinks:
            incoming[sink.component].append(net)
        for source in net.sources:
            outgoing[source.component].append(net)

    component_arrival: dict[str, int] = {}
    net_arrival: dict[str, int] = {}
    for key in order:
        input_arrival = max(
            (net_arrival[net.name] for net in incoming[key]),
            default=0,
        )
        component_arrival[key] = input_arrival + components[key].gate_delay
        for net in outgoing[key]:
            if all(source.component in component_arrival for source in net.sources):
                net_arrival[net.name] = max(
                    component_arrival[source.component] for source in net.sources
                )

    missing_net_arrivals = sorted(set(nets) - set(net_arrival))
    if missing_net_arrivals:
        raise ValueError(
            f"timing analysis could not resolve nets {missing_net_arrivals[:8]!r}"
        )

    output_keys = tuple(
        sorted(key for key, component in components.items() if component.role == "output_port")
    )
    if output_keys:
        actual_delay = max(component_arrival[key] for key in output_keys)
    else:
        terminal_keys = tuple(sorted(key for key in components if not outgoing[key]))
        actual_delay = max(
            (component_arrival[key] for key in terminal_keys),
            default=0,
        )

    horizon = design.delay
    component_required = {key: horizon for key in components}
    net_required = {name: horizon for name in nets}
    for key in reversed(order):
        constraints = [
            net_required[net.name]
            for net in outgoing[key]
        ]
        if constraints:
            component_required[key] = min(component_required[key], *constraints)
        for net in incoming[key]:
            sink_constraint = component_required[key] - components[key].gate_delay
            net_required[net.name] = min(net_required[net.name], sink_constraint)

    facts = []
    for key in order:
        critical_net, critical_input, critical_source = _critical_input(
            key,
            tuple(incoming[key]),
            component_arrival,
            net_arrival,
        )
        required = component_required[key]
        arrival = component_arrival[key]
        slack = required - arrival
        facts.append(
            TimingFact(
                component=key,
                arrival=arrival,
                required=required,
                slack=slack,
                gate_delay=components[key].gate_delay,
                critical_input_net=critical_net,
                critical_input=critical_input,
                critical_source=critical_source,
                is_critical=slack == 0,
            )
        )

    return FlowFrame(
        design_name=design.name,
        target_delay=design.delay,
        actual_delay=actual_delay,
        topological_order=order,
        facts=tuple(facts),
        net_arrivals=tuple(sorted(net_arrival.items())),
        net_required=tuple(sorted(net_required.items())),
        critical_outputs=tuple(
            key
            for key in output_keys
            if component_required[key] - component_arrival[key] == 0
        ),
    )
