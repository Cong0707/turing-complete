"""Graft a physical high-window witness onto the authoritative fixed73 shell.

``build(witness_path)`` is the production entry point consumed by the generic
Factory-DAG materializer.  It accepts only a complete independently verified
S3..S7/C8 witness of cost at most 30 and emits a complete Byte Adder DAG only
after all 131072 rows, BUS conflicts, public-output Z masks, recursive cost,
and the five-step deadline pass.

``build_fixture`` is deliberately separate.  It combines the local S3/S4 and
S7/C8 SAT fixtures with a known slower S5/S6 formula so that parser, physical
BUS materialization, v15 generation, and geometry can be regression-tested
before a complete high-residual witness exists.  Fixture output is never eligible as
a competitive candidate.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORE_PATH = ROOT / ".research/byte_adder_interval_dp_agent/interval_dp.py"
VERIFIER_PATH = HERE / "verify_fixed73_high29_physical_witness.py"
BIT0_WITNESS = (
    ROOT
    / ".research/byte_adder_phase_shortcut_forward/fast_negative_bit0_g11_n9_s2_x0.json"
)
S12_WITNESS = (
    ROOT / ".research/byte_adder_phase_shortcut_restart/s12_g7_d5_exact.json"
)
S34_FIXTURE = (
    ROOT / ".research/byte_adder_phase_shortcut_restart/s34_g11_d5_joint_exact.json"
)

EXACT_COST = {
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 3,
    "SWITCH": 2,
}


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = _load_module(CORE_PATH, "fixed73_high29_factory_core")
verifier = _load_module(VERIFIER_PATH, "fixed73_high29_independent_verifier")


@dataclass(slots=True)
class FixedShell:
    factory: Any
    low_outputs: tuple[int, int, int]
    named: dict[str, int]
    av34: tuple[int, int]
    av56: tuple[int, int]
    fixed_metrics: dict[str, Any]
    low_metrics: dict[str, Any]
    boundary_arrivals: dict[str, int]
    certificates: list[dict[str, str]]


def _portable(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def _assert_output_path(path: Path) -> Path:
    resolved = path.resolve()
    if resolved != HERE and HERE not in resolved.parents:
        raise RuntimeError(f"derived output must stay below {HERE}: {resolved}")
    return resolved


def _certificate(path: Path) -> dict[str, str]:
    return {
        "certificate": _portable(path),
        "certificate_sha256": sha256(path.read_bytes()).hexdigest(),
    }


def _require_int(value: object, label: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise RuntimeError(f"{label} must be an integer >= {minimum}: {value!r}")
    return value


def _read_exact_witness(
    path: Path,
    *,
    expected_sources: tuple[str, ...],
    expected_outputs: int,
    expected_gate: int,
) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("status") != "sat":
        raise RuntimeError(f"fixed witness is not SAT: {path}")
    if tuple(payload.get("free_sources", ())) != expected_sources:
        raise RuntimeError(f"fixed witness source order changed: {path}")
    if _require_int(payload.get("actual_gate"), f"{path.name}.actual_gate") != expected_gate:
        raise RuntimeError(f"fixed witness gate cost changed: {path}")
    network = payload.get("network")
    output_buses = payload.get("output_buses")
    if not isinstance(network, list) or not isinstance(output_buses, list):
        raise RuntimeError(f"fixed witness network is missing: {path}")
    if len(output_buses) != expected_outputs:
        raise RuntimeError(f"fixed witness output count changed: {path}")

    source_count = len(expected_sources)
    switch_sources: set[int] = set()
    used_buses: list[tuple[int, ...]] = []
    gate = 0
    for slot, item in enumerate(network):
        if not isinstance(item, dict):
            raise RuntimeError(f"{path.name} slot {slot} is not an object")
        if item.get("slot") != slot or item.get("source") != source_count + slot:
            raise RuntimeError(f"{path.name} slot/source sequence changed")
        kind = item.get("kind")
        if kind not in EXACT_COST or item.get("cost") != EXACT_COST[kind]:
            raise RuntimeError(f"{path.name} slot {slot} kind/cost changed")
        gate += EXACT_COST[kind]
        available = source_count + slot
        for side in ("left_bus", "right_bus"):
            raw = item.get(side)
            if not isinstance(raw, list):
                raise RuntimeError(f"{path.name} slot {slot} {side} is not a list")
            bus = tuple(raw)
            allow_empty = kind == "NOT" and side == "right_bus"
            if not bus and not allow_empty:
                raise RuntimeError(f"{path.name} slot {slot} has an empty BUS")
            if bus != tuple(sorted(set(bus))) or any(
                isinstance(source, bool)
                or not isinstance(source, int)
                or source < 0
                or source >= available
                for source in bus
            ):
                raise RuntimeError(f"{path.name} slot {slot} has an invalid BUS")
            if len(bus) > 1 and any(
                source < source_count or source not in switch_sources for source in bus
            ):
                raise RuntimeError(f"{path.name} slot {slot} splits a physical BUS")
            if bus:
                used_buses.append(bus)
        if kind == "SWITCH":
            switch_sources.add(source_count + slot)
    for raw in output_buses:
        if not isinstance(raw, list):
            raise RuntimeError(f"{path.name} output BUS is not a list")
        bus = tuple(raw)
        if not bus or bus != tuple(sorted(set(bus))):
            raise RuntimeError(f"{path.name} output BUS is invalid")
        if len(bus) > 1 and any(source not in switch_sources for source in bus):
            raise RuntimeError(f"{path.name} output BUS is not Switch-only")
        used_buses.append(bus)
    for index, left in enumerate(used_buses):
        for right in used_buses[index + 1 :]:
            if set(left).intersection(right) and left != right:
                raise RuntimeError(f"{path.name} physical-net partition changed")
    if gate != expected_gate:
        raise RuntimeError(f"{path.name} recomputed gate cost changed")
    verification = payload.get("verification")
    if not isinstance(verification, dict) or any(
        verification.get(key) != 0
        for key in (
            "mismatch_count",
            "bus_conflict_count",
            "undriven_output_count",
            "physical_net_partition_violation_count",
        )
    ):
        raise RuntimeError(f"{path.name} verification metadata is not clean")
    return payload


def _gate_preserving_driven_output(
    factory: Any, kind: str, left: int, right: int | None = None
) -> int:
    result = factory.gate(kind, left, right)
    if not factory.nodes[result].may_z:
        return result

    if right is None:
        args = (left,)
    elif kind in factory.COMMUTATIVE and right < left:
        args = (right, left)
    else:
        args = (left, right)
    cost, delay = factory.GATE_COST[kind]
    arrival = max(factory.nodes[arg].arrival for arg in args) + delay
    return factory._new(
        ("EXACT_ALWAYS_DRIVEN", kind, *args),
        core.Node(kind, args, cost, delay, arrival, False),
    )


def _bus_preserving_driven_output(
    factory: Any, drivers: Iterable[tuple[int, int]]
) -> int:
    unique = sorted(set(drivers))
    unique = [pair for pair in unique if pair[0] != factory.const0]
    if (
        len(unique) == 1
        and unique[0][0] == factory.const1
        and factory.nodes[unique[0][1]].may_z
    ):
        flat = tuple(item for pair in unique for item in pair)
        arrival = max(factory.nodes[arg].arrival for arg in flat) + 1
        return factory._new(
            ("EXACT_ALWAYS_DRIVEN_BUS", *flat),
            core.Node("BUS", flat, 2, 1, arrival, True),
        )
    return factory.bus(unique)


def materialize_exact_network(
    factory: Any,
    payload: Mapping[str, Any],
    named_sources: Mapping[str, int],
) -> tuple[tuple[int, ...], dict[int, int], dict[int, tuple[int, int]]]:
    """Materialize each exact physical BUS as one complete Factory BUS."""

    source_names = tuple(payload["free_sources"])
    nodes = {
        index: named_sources[name]
        for index, name in enumerate(source_names)
    }
    switches: dict[int, tuple[int, int]] = {}

    def resolve_bus(raw_bus: Iterable[int]) -> int:
        bus = tuple(raw_bus)
        ordinary = [nodes[source] for source in bus if source in nodes]
        drivers = [switches[source] for source in bus if source in switches]
        if len(ordinary) + len(drivers) != len(bus):
            missing = [
                source for source in bus if source not in nodes and source not in switches
            ]
            raise RuntimeError(f"unresolved exact source(s): {missing!r}")
        if drivers:
            if ordinary:
                raise RuntimeError(f"illegal mixed ordinary/Switch BUS: {bus!r}")
            return _bus_preserving_driven_output(factory, drivers)
        if len(ordinary) != 1:
            raise RuntimeError(f"ordinary BUS must contain one source: {bus!r}")
        return ordinary[0]

    for item in payload["network"]:
        source = int(item["source"])
        left = resolve_bus(item["left_bus"])
        kind = str(item["kind"])
        if kind == "SWITCH":
            switches[source] = (left, resolve_bus(item["right_bus"]))
        elif kind == "NOT":
            nodes[source] = _gate_preserving_driven_output(factory, "NOT", left)
        else:
            nodes[source] = _gate_preserving_driven_output(
                factory, kind, left, resolve_bus(item["right_bus"])
            )

    outputs = tuple(resolve_bus(bus) for bus in payload["output_buses"])
    return outputs, nodes, switches


def negative_av_combine(factory: Any, low: tuple[int, int], high: tuple[int, int]):
    low_a, low_v = low
    high_a, high_v = high
    return (
        factory.gate("OR", low_a, high_a),
        factory.bus(((high_a, high_v), (low_v, high_v))),
    )


def negative_av_gray(factory: Any, ncarry: int, transfer: tuple[int, int]) -> int:
    any_kill, valency = transfer
    return factory.bus(((any_kill, valency), (ncarry, valency)))


def negative_pair_sums(
    factory: Any,
    ncarry: int,
    q_low: int,
    p_low: int,
    p_high: int,
    pair_valency: int,
) -> tuple[int, int]:
    """Known nine-gate pair formula; used only by the noncompetitive fixture."""

    phase_or = factory.gate("OR", ncarry, p_low)
    phase_nand = factory.gate("NAND", ncarry, p_low)
    low_sum = factory.gate("NAND", phase_or, phase_nand)
    cross_zero = factory.gate("NOR", q_low, p_high)
    lower = factory.gate("AND", phase_nand, cross_zero)
    upper_phase = factory.gate("AND", p_high, pair_valency)
    selector = factory.gate("OR", ncarry, q_low)
    upper = factory.gate("AND", upper_phase, selector)
    high_sum = factory.gate("OR", lower, upper)
    return low_sum, high_sum


def _serialize(factory: Any, outputs: tuple[int, ...]) -> dict[str, Any]:
    live = sorted(factory.reachable(outputs))
    nodes = []
    for index in live:
        node = factory.nodes[index]
        row = {
            "id": index,
            "op": node.op,
            "args": list(node.args),
            "cost": node.cost,
            "step_delay": node.step_delay,
            "arrival": node.arrival,
            "may_z": node.may_z,
            "label": node.label,
        }
        if node.op == "BUS":
            row["resolved_network"] = f"bus_{index}"
            row["drivers"] = [
                {
                    "enable": node.args[offset],
                    "data": node.args[offset + 1],
                    "owner": f"bus_{index}",
                }
                for offset in range(0, len(node.args), 2)
            ]
        nodes.append(row)
    payload = {
        "outputs": list(outputs),
        "nodes": nodes,
        "live_node_count": len(live),
    }
    payload["sha256"] = sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def _build_fixed_shell() -> FixedShell:
    bit0 = _read_exact_witness(
        BIT0_WITNESS,
        expected_sources=("a", "b", "Cin", "0", "1"),
        expected_outputs=2,
        expected_gate=11,
    )
    s12_payload = _read_exact_witness(
        S12_WITNESS,
        expected_sources=(
            "nC1",
            "G1", "Q1", "P1", "N1",
            "G2", "Q2", "P2", "N2",
            "A12n", "V12n", "nC3",
            "0", "1",
        ),
        expected_outputs=2,
        expected_gate=7,
    )

    factory = core.Factory()
    (s0, nc1), _bit0_nodes, _bit0_switches = materialize_exact_network(
        factory,
        bit0,
        {
            "a": factory.inputs["a0"],
            "b": factory.inputs["b0"],
            "Cin": factory.inputs["cin"],
            "0": factory.const0,
            "1": factory.const1,
        },
    )

    g: dict[int, int] = {}
    q: dict[int, int] = {}
    p: dict[int, int] = {}
    n: dict[int, int] = {}
    for bit in range(1, 8):
        ai = factory.inputs[f"a{bit}"]
        bi = factory.inputs[f"b{bit}"]
        g[bit] = factory.gate("AND", ai, bi)
        q[bit] = factory.gate("NOR", ai, bi)
        p[bit] = factory.gate("NOR", g[bit], q[bit])
        if bit <= 6:
            n[bit] = factory.gate("NAND", ai, bi)

    av12 = negative_av_combine(factory, (q[1], n[1]), (q[2], n[2]))
    nc3 = negative_av_gray(factory, nc1, av12)
    (s1, s2), _s12_nodes, _s12_switches = materialize_exact_network(
        factory,
        s12_payload,
        {
            "nC1": nc1,
            "G1": g[1], "Q1": q[1], "P1": p[1], "N1": n[1],
            "G2": g[2], "Q2": q[2], "P2": p[2], "N2": n[2],
            "A12n": av12[0], "V12n": av12[1], "nC3": nc3,
            "0": factory.const0, "1": factory.const1,
        },
    )

    av34 = negative_av_combine(factory, (q[3], n[3]), (q[4], n[4]))
    av56 = negative_av_combine(factory, (q[5], n[5]), (q[6], n[6]))
    av36 = negative_av_combine(factory, av34, av56)
    nc7 = negative_av_gray(factory, nc3, av36)

    named = {
        "nC3": nc3,
        **{
            name: node
            for bit in range(3, 7)
            for name, node in (
                (f"G{bit}", g[bit]),
                (f"Q{bit}", q[bit]),
                (f"P{bit}", p[bit]),
                (f"N{bit}", n[bit]),
            )
        },
        "G7": g[7], "Q7": q[7], "P7": p[7],
        "A34n": av34[0], "V34n": av34[1],
        "A56n": av56[0], "V56n": av56[1],
        "A36n": av36[0], "V36n": av36[1],
        "nC7": nc7,
        "0": factory.const0, "1": factory.const1,
    }
    if tuple(named) != verifier.SOURCE_NAMES:
        raise RuntimeError("fixed shell paid-source insertion order changed")
    boundary_arrivals = {
        name: factory.nodes[node].arrival for name, node in named.items()
    }
    if boundary_arrivals != verifier.SOURCE_ARRIVALS:
        raise RuntimeError(f"fixed shell paid-source arrivals changed: {boundary_arrivals!r}")

    low_outputs = (s0, s1, s2)
    low_metrics = factory.structural_metrics((*low_outputs, nc3))
    if low_metrics["gate"] != 35 or low_metrics["output_arrivals"] != [4, 4, 5, 3]:
        raise RuntimeError(f"fixed low-prefix contract changed: {low_metrics!r}")
    fixed_outputs = (
        *low_outputs,
        *(named[name] for name in verifier.SOURCE_NAMES if name not in {"0", "1"}),
    )
    fixed_metrics = factory.structural_metrics(fixed_outputs)
    if fixed_metrics["gate"] != 73:
        raise RuntimeError(f"fixed73 accounting changed: {fixed_metrics!r}")
    if fixed_metrics["gate"] - low_metrics["gate"] != 38:
        raise RuntimeError("fixed high paid-state accounting changed")

    return FixedShell(
        factory=factory,
        low_outputs=low_outputs,
        named=named,
        av34=av34,
        av56=av56,
        fixed_metrics=fixed_metrics,
        low_metrics=low_metrics,
        boundary_arrivals=boundary_arrivals,
        certificates=[_certificate(BIT0_WITNESS), _certificate(S12_WITNESS)],
    )


def _bus_semantics(factory: Any, outputs: tuple[int, ...], packed: Mapping[int, Any]):
    live = factory.reachable(outputs)
    result = []
    for index in sorted(live):
        node = factory.nodes[index]
        if node.op != "BUS":
            continue
        signal = packed[index]
        result.append(
            {
                "node": index,
                "driver_count": len(node.args) // 2,
                "arrival": node.arrival,
                "conflict_assignment_count": signal.conflict.bit_count(),
                "z_assignment_count": ((~signal.driven) & core.ALL).bit_count(),
            }
        )
    if any(item["conflict_assignment_count"] for item in result):
        raise RuntimeError(f"internal BUS conflict: {result!r}")
    return result


def _finalize(
    *,
    shell: FixedShell,
    high_outputs: Mapping[str, int],
    review: dict[str, Any],
    witness_path: Path,
    fixture: bool,
    extra_certificates: list[dict[str, str]],
    ledger: dict[str, Any],
    expected_gate_upper_bound: int,
) -> dict[str, Any]:
    outputs = (
        *shell.low_outputs,
        *(high_outputs[name] for name in verifier.OUTPUT_NAMES),
    )
    factory = shell.factory
    metrics = factory.structural_metrics(outputs)
    packed, semantic = factory.evaluate(outputs)
    if metrics["gate"] > expected_gate_upper_bound:
        raise RuntimeError(
            f"complete gate cost {metrics['gate']} exceeds {expected_gate_upper_bound}"
        )
    if not fixture and not verifier.complete_score_within_contract(metrics):
        raise RuntimeError(
            "production candidate misses the <=103/5/515 contract: "
            f"{metrics!r}"
        )
    if semantic["mismatch_union_count"]:
        raise RuntimeError(f"complete truth mismatch: {semantic!r}")
    if semantic["conflict_assignment_count"]:
        raise RuntimeError(f"reachable BUS conflict: {semantic!r}")
    if any(semantic["z_assignment_count_by_output"]):
        raise RuntimeError(f"undriven primary output: {semantic!r}")

    bus_semantics = _bus_semantics(factory, outputs, packed)
    witness_bytes = witness_path.read_bytes()
    certificates = [
        _certificate(witness_path),
        *shell.certificates,
        *extra_certificates,
    ]
    payload = {
        "schema": (
            "byte-adder-fixed73-high-residual-physical-graft-dag-v2"
            if not fixture
            else "byte-adder-fixed73-physical-graft-regression-fixture-dag-v1"
        ),
        "status": "sat",
        "family": (
            "fixed35 negative S0/S1/S2 prefix plus fixed38 high paid state and exact D5 residual"
            if not fixture
            else "noncompetitive fixed73 exact-network materialization regression"
        ),
        "competitive_contract": not fixture,
        "fixture_only": fixture,
        "competitive_score_contract": {
            "max_gate": verifier.MAX_COMPLETE_GATE,
            "max_delay": verifier.MAX_COMPLETE_DELAY,
            "max_energy": verifier.MAX_COMPLETE_ENERGY,
            "energy_equals_gate_times_delay": True,
        },
        "source_witness": {
            "path": _portable(witness_path),
            "sha256": sha256(witness_bytes).hexdigest(),
            "actual_gate": review["structure"]["gate"],
            "output_names": review["witness"]["output_names"],
            "builder_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "verifier_sha256": sha256(VERIFIER_PATH.read_bytes()).hexdigest(),
            "certificates": certificates,
        },
        "witness_review": review,
        "fixed_shell": {
            "low_prefix_metrics": shell.low_metrics,
            "fixed_total_metrics": shell.fixed_metrics,
            "fixed_low_prefix_gate": verifier.FIXED_LOW_PREFIX_GATE,
            "fixed_high_paid_state_gate": verifier.FIXED_HIGH_PAID_STATE_GATE,
            "fixed_total_gate": verifier.FIXED_TOTAL_GATE,
            "boundary_arrivals": shell.boundary_arrivals,
        },
        "ledger": {
            **ledger,
            "expected_gate_upper_bound": expected_gate_upper_bound,
            "structural_interning_or_dead_source_savings": (
                expected_gate_upper_bound - metrics["gate"]
            ),
            "total": metrics["gate"],
        },
        "metrics": metrics,
        "semantic": semantic,
        "physical": {
            "bus_node_count": len(bus_semantics),
            "bus_node_ids": [item["node"] for item in bus_semantics],
            "bus_semantics": bus_semantics,
            "physical_net_partition_violation_count": 0,
            "partial_driver_reuse_possible": False,
            "reason": (
                "the independent verifier proves one complete physical BUS per Switch "
                "driver set, and materialization never exposes a driver pin separately"
            ),
        },
        "test_domain": {
            "variables": core.VARIABLES,
            "rows": core.ASSIGNMENTS,
            "complete_u8_u8_u1": True,
        },
        "factory_dag": _serialize(factory, outputs),
    }
    return json.loads(json.dumps(payload, ensure_ascii=False))


def build(witness_path: Path) -> dict[str, Any]:
    """Production materializer entry point: complete six-output <=30/D5 only."""

    witness_path = witness_path.resolve()
    review = verifier.verify_witness(witness_path, fixture=False)
    witness = json.loads(witness_path.read_text(encoding="utf-8"))
    shell = _build_fixed_shell()
    exact_outputs, _nodes, _switches = materialize_exact_network(
        shell.factory,
        witness,
        shell.named,
    )
    high_outputs = dict(
        zip(verifier.OUTPUT_NAMES, exact_outputs, strict=True)
    )
    residual_gate = int(review["structure"]["gate"])
    return _finalize(
        shell=shell,
        high_outputs=high_outputs,
        review=review,
        witness_path=witness_path,
        fixture=False,
        extra_certificates=[],
        ledger={
            "fixed_shell": verifier.FIXED_TOTAL_GATE,
            "high_exact_residual": residual_gate,
        },
        expected_gate_upper_bound=verifier.FIXED_TOTAL_GATE + residual_gate,
    )


def build_fixture(witness_path: Path) -> dict[str, Any]:
    """Build a complete noncompetitive DAG around the local S7/C8 fixture."""

    witness_path = witness_path.resolve()
    review = verifier.verify_witness(witness_path, fixture=True)
    if review["witness"]["output_names"] != ["S7", "C8"]:
        raise RuntimeError("the regression builder expects the local S7/C8 fixture")
    tail = json.loads(witness_path.read_text(encoding="utf-8"))
    shell = _build_fixed_shell()

    s34 = _read_exact_witness(
        S34_FIXTURE,
        expected_sources=(
            "nC3",
            "G3", "Q3", "P3", "N3",
            "G4", "Q4", "P4", "N4",
            "G5", "Q5", "P5", "N5",
            "G6", "Q6", "P6", "N6",
            "A34n", "V34n", "A56n", "V56n", "A36n", "V36n", "nC7",
            "0", "1",
        ),
        expected_outputs=2,
        expected_gate=11,
    )
    (s3, s4), _s34_nodes, _s34_switches = materialize_exact_network(
        shell.factory,
        s34,
        shell.named,
    )
    nc5 = negative_av_gray(shell.factory, shell.named["nC3"], shell.av34)
    s5, s6 = negative_pair_sums(
        shell.factory,
        nc5,
        shell.named["Q5"],
        shell.named["P5"],
        shell.named["P6"],
        shell.av56[1],
    )
    (s7, c8), _tail_nodes, _tail_switches = materialize_exact_network(
        shell.factory,
        tail,
        shell.named,
    )
    return _finalize(
        shell=shell,
        high_outputs={
            "S3": s3, "S4": s4, "S5": s5,
            "S6": s6, "S7": s7, "C8": c8,
        },
        review=review,
        witness_path=witness_path,
        fixture=True,
        extra_certificates=[_certificate(S34_FIXTURE)],
        ledger={
            "fixed_shell": 73,
            "s34_exact_fixture": 11,
            "nC5_fixture_boundary": 4,
            "s56_known_pair_fixture": 9,
            "s7c8_exact_fixture": int(review["structure"]["gate"]),
        },
        expected_gate_upper_bound=73 + 11 + 4 + 9 + int(review["structure"]["gate"]),
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path = _assert_output_path(path)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    if path.read_bytes() != encoded:
        raise RuntimeError("written Factory DAG changed")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Graft a physical witness onto the authoritative fixed73 shell."
    )
    parser.add_argument("--witness", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--fixture",
        action="store_true",
        help="build the explicit noncompetitive S7/C8 regression fixture",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    payload = build_fixture(args.witness) if args.fixture else build(args.witness)
    _write_json(args.output, payload)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "schema": payload["schema"],
                "competitive_contract": payload["competitive_contract"],
                "metrics": payload["metrics"],
                "semantic": payload["semantic"],
                "sha256": sha256(args.output.read_bytes()).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
