"""Coordinate-free floorplan contracts for timing-driven conductor growth.

The objects in this module intentionally describe logical ownership and timing
only.  Placement and routing stages may add coordinates later, but the
frontier analysis must remain usable without either stage.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from turingsynth.ir.physical import PinRef


class _JsonReport:
    """Provide the same JSON-ready reporting convention as the other IRs."""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)  # type: ignore[arg-type]


@dataclass(frozen=True)
class TimingFact(_JsonReport):
    """Static timing facts at one component's output."""

    component: str
    arrival: int
    required: int
    slack: int
    gate_delay: int
    critical_input_net: str | None = None
    critical_input: PinRef | None = None
    critical_source: PinRef | None = None
    is_critical: bool = False


@dataclass(frozen=True)
class FlowFrame(_JsonReport):
    """Whole-design timing frame used to grow logic away from bus trunks."""

    design_name: str
    target_delay: int
    actual_delay: int
    topological_order: tuple[str, ...]
    facts: tuple[TimingFact, ...]
    net_arrivals: tuple[tuple[str, int], ...]
    net_required: tuple[tuple[str, int], ...]
    critical_outputs: tuple[str, ...]

    def fact_by_component(self) -> dict[str, TimingFact]:
        return {fact.component: fact for fact in self.facts}

    def arrival_by_net(self) -> dict[str, int]:
        return dict(self.net_arrivals)

    def required_by_net(self) -> dict[str, int]:
        return dict(self.net_required)


@dataclass(frozen=True)
class TrunkLane(_JsonReport):
    """One input-derived logical lane at the splitter frontier."""

    index: int
    net: str
    width: int
    source: PinRef
    lineage: tuple[str, ...]
    branch_path: tuple[str, ...] = ()
    arrival: int = 0


@dataclass(frozen=True)
class BusTrunk(_JsonReport):
    """An input bus and the lanes exposed after free splitter expansion."""

    key: str
    input_port: str
    root_nets: tuple[str, ...]
    frontier_nets: tuple[str, ...]
    lanes: tuple[TrunkLane, ...]
    splitters: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConductorTip(_JsonReport):
    """A driven logical endpoint from which a conductor may grow."""

    key: str
    net: str
    source: PinRef
    arrival: int
    trunk_key: str | None = None
    lane_index: int | None = None


@dataclass(frozen=True)
class TapSocket(_JsonReport):
    """A sink request to be attached to a trunk or local conductor."""

    key: str
    net: str
    sink: PinRef
    required: int
    slack: int
    critical: bool = False


@dataclass(frozen=True)
class GrowthCone(_JsonReport):
    """A timing-oriented logic cone grown between I/O conductor frontiers."""

    key: str
    components: tuple[str, ...]
    input_trunks: tuple[str, ...]
    entry_tips: tuple[ConductorTip, ...]
    tap_sockets: tuple[TapSocket, ...]
    output_tips: tuple[ConductorTip, ...]
    critical_delay: int


@dataclass(frozen=True)
class PlannedConductor(_JsonReport):
    """Coordinate-free connection intent consumed by a later router."""

    key: str
    net: str
    tip: ConductorTip
    sockets: tuple[TapSocket, ...]
    timing_priority: int
    critical: bool = False


@dataclass(frozen=True)
class OutputMerge(_JsonReport):
    """An output port and its logical frontier before free maker contraction."""

    key: str
    output_port: str
    root_nets: tuple[str, ...]
    frontier_nets: tuple[str, ...]
    makers: tuple[str, ...] = ()


@dataclass(frozen=True)
class Floorplan(_JsonReport):
    """Top-level BusTrunk -> GrowthCone -> OutputMerge planning contract."""

    design_name: str
    timing: FlowFrame
    input_trunks: tuple[BusTrunk, ...]
    growth_cones: tuple[GrowthCone, ...]
    conductors: tuple[PlannedConductor, ...]
    output_merges: tuple[OutputMerge, ...]
    schema: str = field(default="turingsynth-floorplan-v1", init=False)

