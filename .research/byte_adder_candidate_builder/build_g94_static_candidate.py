"""Build the patchable 94/6 Byte Adder Factory DAG without exhaustive testing.

This module is the engineering bridge between the frozen 95/6 witness builder
and future hand-designed S3/S4 or S5/S6 formula patches.  It performs one fixed
architectural rewrite only::

    old: A34 = G3 OR G4;  Apre = G2 OR A34
    new: X23 = G2 OR G3; Apre = X23 OR G4

``X23`` is already consumed by the reviewed S3/S4 formula, so ``A34`` becomes
dead and the live Factory DAG costs 94 gates at delay 6.

The default command is intentionally static-only: it never starts the game,
never reads or writes a save, never invokes a solver, and never evaluates the
full 2^17 input domain.  ``--full-verify`` exists solely for a later, closed
candidate and must not be used until the lead agent explicitly authorizes it.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Callable, Iterable, Mapping


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORE_PATH = ROOT / ".research/byte_adder_interval_dp_agent/interval_dp.py"
CARRY_WITNESS_PATH = (
    ROOT
    / ".research/byte_adder_av_reduced_forward"
    / "q12_q34_retime_i12_c23_n3_s10_x0_sat.json"
)
S34_WITNESS_PATH = (
    ROOT
    / ".research/byte_adder_av_reduced_forward"
    / "s34_focus_g9_n9_s0_x0.json"
)
DEFAULT_OUTPUT = HERE / "byte-adder-g94-apre-patchable-static.json"
MATERIALIZER_PATH = (
    ROOT
    / ".research/byte_adder_builder_layout_agent"
    / "materialize_factory_dag.py"
)

CARRY_WITNESS_SHA256 = (
    "31d90a0c228aa6fc2bb63710ae4981571de57d7f926d752f84ae271fa256ad04"
)
S34_WITNESS_SHA256 = (
    "26f7da28d1ea31dbd5c2657b4f73c3b9e9a08a6b8f5b2acd6f314d6ffa803fde"
)
BUILTIN_G94_CANONICAL_SHA256 = (
    "0f32d21b3109595dd3473d017ee4e22bd8d0055978b3500e192d7369d5a647d9"
)

ORIGINAL_CARRY_SOURCES = (
    "C1",
    "A12",
    "N12",
    "G2",
    "A34",
    "N34",
    "G4",
    "A56",
    "V56",
)
REASSOCIATED_CARRY_SOURCES = (
    "C1",
    "A12",
    "N12",
    "G2",
    "X23",
    "N34",
    "G4",
    "A56",
    "V56",
)
ORIGINAL_S34_SOURCES = (
    "C1",
    "A12",
    "N12",
    "G2",
    "G3",
    "Q3",
    "P3",
    "G4",
    "Q4",
    "P4",
    "A34",
    "N34",
    "B12",
    "Apre",
    "V34",
    "C3",
    "C5",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


core = load_module("byte_adder_g94_static_core", CORE_PATH)


@dataclass(frozen=True, slots=True)
class PackedWord:
    value: tuple[int, ...]
    driven: int
    conflict: int


class PatchFactory(core.Factory):
    """Factory extension for the materializer's zero-cost Maker/Splitter ABI."""

    def __init__(self) -> None:
        super().__init__()
        self.splitter_metadata: dict[int, dict[str, Any]] = {}
        self.normalizer_owners: dict[str, tuple[int, int]] = {}
        self.normalizer_metadata: dict[int, dict[str, Any]] = {}

    def normalize_scalar(self, raw: int, filler: int, *, owner: str) -> int:
        """Read a may-Z scalar as active ``value & driven`` at zero cost/delay.

        Maker2 reads each scalar lane's data plane and emits an active word;
        Splitter2 then exposes lane 0 as a distinct active scalar network.  The
        filler occupies lane 1 only, but it must already be active and no later
        than ``raw`` so the normalizer preserves ``raw``'s exact arrival.
        """

        if self.nodes[raw].op == "MAKER2" or self.nodes[filler].op == "MAKER2":
            raise RuntimeError("normalize_scalar accepts scalar nodes only")

        if not self.nodes[raw].may_z:
            return raw
        if (
            not owner
            or len(owner) > 128
            or any(
                not (character.isascii() and (character.isalnum() or character in "_.:-"))
                for character in owner
            )
        ):
            raise RuntimeError(f"invalid normalize_scalar owner {owner!r}")
        if self.nodes[filler].may_z:
            raise RuntimeError("Maker2 filler must be fully driven")
        if self.nodes[filler].arrival > self.nodes[raw].arrival:
            raise RuntimeError(
                "Maker2 filler arrives after the partial scalar; zero-delay "
                "normalization would still inherit the later input arrival"
            )
        contract = (raw, filler)
        previous = self.normalizer_owners.get(owner)
        if previous is not None and previous != contract:
            raise RuntimeError(
                f"normalize_scalar owner {owner!r} aliases {previous} and {contract}"
            )
        self.normalizer_owners[owner] = contract
        arrival = self.nodes[raw].arrival
        maker = self._new(
            ("MAKER2", raw, filler),
            core.Node(
                "MAKER2",
                (raw, filler),
                0,
                0,
                arrival,
                False,
                f"normalize-maker:{owner}",
            ),
        )
        splitter = self._new(
            ("SPLITTER2", maker, owner, 0),
            core.Node(
                "SPLITTER2",
                (maker,),
                0,
                0,
                arrival,
                False,
                f"normalize-splitter:{owner}:lane0",
            ),
        )
        self.splitter_metadata[splitter] = {"owner": owner, "lane": 0}
        self.normalizer_metadata[splitter] = {
            "raw": raw,
            "filler": filler,
            "maker": maker,
            "owner": owner,
            "arrival": arrival,
        }
        return splitter

    def structural_hash(self, outputs: tuple[int, ...]) -> str:
        """Hash extended nodes with the same owner-aware form as the materializer."""

        memo: dict[int, str] = {}

        def visit(index: int) -> str:
            found = memo.get(index)
            if found is not None:
                return found
            node = self.nodes[index]
            payload: list[Any] = [node.op, node.label, node.cost, node.step_delay]
            if node.op == "SPLITTER2":
                metadata = self.splitter_metadata.get(index)
                if metadata is None:
                    raise RuntimeError(f"SPLITTER2 {index} lacks structural metadata")
                payload.extend((metadata["owner"], metadata["lane"]))
            payload.extend(visit(argument) for argument in node.args)
            digest = hashlib.sha256(
                json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode()
            ).hexdigest()
            memo[index] = digest
            return digest

        return hashlib.sha256("".join(visit(output) for output in outputs).encode()).hexdigest()

    def evaluate(
        self, outputs: tuple[int, ...]
    ) -> tuple[dict[int, Any], dict[str, object]]:
        """Evaluate scalar gates plus the reviewed Maker2/Splitter2 data plane."""

        live = self.reachable(outputs)
        packed: dict[int, core.PackedSignal | PackedWord] = {}
        input_index = {
            self.inputs[f"a{bit}"]: bit for bit in range(core.BITS)
        } | {
            self.inputs[f"b{bit}"]: core.BITS + bit for bit in range(core.BITS)
        } | {self.inputs["cin"]: 16}

        def scalar(signal: core.PackedSignal | PackedWord, label: str) -> core.PackedSignal:
            if isinstance(signal, PackedWord):
                raise RuntimeError(f"{label} expected a scalar")
            return signal

        def value(index: int) -> core.PackedSignal | PackedWord:
            found = packed.get(index)
            if found is not None:
                return found
            node = self.nodes[index]
            if node.op == "CONST":
                result: core.PackedSignal | PackedWord = core.PackedSignal(
                    core.ALL if node.label == "1" else 0,
                    core.ALL,
                    0,
                )
            elif node.op == "INPUT":
                result = core.PackedSignal(
                    self._variable(input_index[index]), core.ALL, 0
                )
            elif node.op == "BUS":
                ones = zeros = driven = conflict = 0
                for offset in range(0, len(node.args), 2):
                    enable = scalar(value(node.args[offset]), f"BUS {index} enable")
                    data = scalar(value(node.args[offset + 1]), f"BUS {index} data")
                    active = enable.value & enable.driven & core.ALL
                    data_plane = data.value & data.driven & core.ALL
                    ones |= active & data_plane
                    zeros |= active & (~data_plane & core.ALL)
                    driven |= active
                    conflict |= enable.conflict | data.conflict
                conflict |= ones & zeros
                result = core.PackedSignal(
                    ones & core.ALL,
                    driven & core.ALL,
                    conflict & core.ALL,
                )
            elif node.op == "MAKER2":
                lanes = [scalar(value(argument), f"MAKER2 {index}") for argument in node.args]
                conflict = 0
                for lane in lanes:
                    conflict |= lane.conflict
                result = PackedWord(
                    tuple(lane.value & lane.driven & core.ALL for lane in lanes),
                    core.ALL,
                    conflict & core.ALL,
                )
            elif node.op == "SPLITTER2":
                source = value(node.args[0])
                if not isinstance(source, PackedWord) or len(source.value) != 2:
                    raise RuntimeError(f"SPLITTER2 {index} lacks a U2 source")
                metadata = self.splitter_metadata.get(index)
                if metadata is None or metadata["lane"] != 0:
                    raise RuntimeError(f"SPLITTER2 {index} metadata changed")
                result = core.PackedSignal(
                    source.value[0] & source.driven & core.ALL,
                    core.ALL,
                    source.conflict & core.ALL,
                )
            else:
                arguments = [scalar(value(argument), f"{node.op} {index}") for argument in node.args]
                conflict = 0
                for argument in arguments:
                    conflict |= argument.conflict
                left = arguments[0].value
                right = arguments[1].value if len(arguments) == 2 else 0
                if node.op == "NOT":
                    output = ~left
                elif node.op == "AND":
                    output = left & right
                elif node.op == "OR":
                    output = left | right
                elif node.op == "NAND":
                    output = ~(left & right)
                elif node.op == "NOR":
                    output = ~(left | right)
                elif node.op == "XOR":
                    output = left ^ right
                elif node.op == "XNOR":
                    output = ~(left ^ right)
                else:
                    raise AssertionError(node.op)
                result = core.PackedSignal(output & core.ALL, core.ALL, conflict & core.ALL)
            packed[index] = result
            return result

        actual = [scalar(value(index), f"output {index}") for index in outputs]
        variables = [self._variable(index) for index in range(core.VARIABLES)]
        carry = variables[16]
        expected: list[int] = []
        for bit in range(core.BITS):
            propagate = variables[bit] ^ variables[core.BITS + bit]
            expected.append(propagate ^ carry)
            carry = (variables[bit] & variables[core.BITS + bit]) | (
                propagate & carry
            )
        expected.append(carry)
        observed = [signal.value & signal.driven & core.ALL for signal in actual]
        mismatch_masks = [
            value ^ target for value, target in zip(observed, expected, strict=True)
        ]
        conflict = 0
        for index in live:
            conflict |= value(index).conflict
        z_masks = [(~signal.driven) & core.ALL for signal in actual]
        digest_payload = b"".join(
            value.to_bytes(core.ASSIGNMENTS // 8, "little") for value in observed
        )
        report = {
            "truth_table_rows": core.ASSIGNMENTS,
            "mismatch_count_by_output": [mask.bit_count() for mask in mismatch_masks],
            "mismatch_union_count": _or_all(mismatch_masks).bit_count(),
            "conflict_assignment_count": conflict.bit_count(),
            "z_assignment_count_by_output": [mask.bit_count() for mask in z_masks],
            "output_vector_sha256": hashlib.sha256(digest_payload).hexdigest(),
        }
        return packed, report


def _or_all(values: Iterable[int]) -> int:
    result = 0
    for value in values:
        result |= value
    return result


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_frozen_json(path: Path, expected_sha256: str) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    actual = sha256_bytes(raw)
    if actual != expected_sha256:
        raise RuntimeError(
            f"frozen dependency changed: {path}; expected {expected_sha256}, got {actual}"
        )
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise RuntimeError(f"frozen dependency is not an object: {path}")
    return payload, raw


def serialize(factory: Any, outputs: tuple[int, ...]) -> dict[str, Any]:
    """Serialize exactly the legacy Factory subset accepted by the materializer."""

    live = sorted(factory.reachable(outputs))
    rows: list[dict[str, Any]] = []
    for index in live:
        node = factory.nodes[index]
        row: dict[str, Any] = {
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
            owner = f"bus_{index}"
            row["resolved_network"] = owner
            row["drivers"] = [
                {
                    "enable": node.args[offset],
                    "data": node.args[offset + 1],
                    "owner": owner,
                }
                for offset in range(0, len(node.args), 2)
            ]
        elif node.op == "SPLITTER2":
            metadata = factory.splitter_metadata.get(index)
            if metadata is None:
                raise RuntimeError(f"SPLITTER2 {index} lacks owner/lane metadata")
            row.update(metadata)
        rows.append(row)
    payload: dict[str, Any] = {
        "outputs": list(outputs),
        "nodes": rows,
        "live_node_count": len(rows),
    }
    payload["sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def canonical_expression_sha256(factory: Any, outputs: tuple[int, ...]) -> str:
    """Hash Boolean/owner structure independently of Factory node numbering."""

    memo: dict[int, tuple[Any, ...]] = {}
    commutative = {"AND", "OR", "NAND", "NOR", "XOR", "XNOR"}

    def visit(node_id: int) -> tuple[Any, ...]:
        found = memo.get(node_id)
        if found is not None:
            return found
        node = factory.nodes[node_id]
        if node.op in {"INPUT", "CONST"}:
            result: tuple[Any, ...] = (node.op, node.label)
        elif node.op == "BUS":
            pairs = [
                (visit(node.args[offset]), visit(node.args[offset + 1]))
                for offset in range(0, len(node.args), 2)
            ]
            result = ("BUS", tuple(sorted(pairs, key=repr)))
        elif node.op == "SPLITTER2":
            metadata = factory.splitter_metadata.get(node_id)
            if metadata is None:
                raise RuntimeError(f"SPLITTER2 {node_id} lacks metadata")
            result = (
                "SPLITTER2",
                visit(node.args[0]),
                metadata["owner"],
                metadata["lane"],
            )
        else:
            arguments = [visit(argument) for argument in node.args]
            if node.op in commutative:
                arguments.sort(key=repr)
            result = (node.op, tuple(arguments), node.cost, node.step_delay)
        memo[node_id] = result
        return result

    expression = tuple(visit(output) for output in outputs)
    return hashlib.sha256(repr(expression).encode()).hexdigest()


@dataclass(frozen=True)
class RegionResult:
    """Return type for a formula hook.

    ``outputs`` must contain the region's required public output names.
    ``byproducts`` exposes useful intermediate signals to later regions without
    making them outputs of the whole circuit.
    """

    outputs: Mapping[str, int]
    byproducts: Mapping[str, int] = field(default_factory=dict)
    note: str = ""


class BuildContext:
    """Small named-net API offered to S3/S4 and S5/S6 patch modules."""

    def __init__(self, factory: Any, nets: Mapping[str, int]):
        self.factory = factory
        self.nets: dict[str, int] = dict(nets)
        self.node_regions: dict[int, set[str]] = defaultdict(set)
        self.bus_labels: dict[int, set[str]] = defaultdict(set)
        self.lazy: dict[str, Callable[[], int]] = {}

    def add_lazy(self, name: str, provider: Callable[[], int]) -> None:
        if name in self.nets or name in self.lazy:
            raise RuntimeError(f"duplicate lazy net {name}")
        self.lazy[name] = provider

    def get(self, name: str) -> int:
        if name not in self.nets:
            provider = self.lazy.get(name)
            if provider is None:
                raise KeyError(f"unknown named net {name!r}")
            self.define(name, provider(), "lazy")
        return self.nets[name]

    def resolve(self, value: str | int) -> int:
        if isinstance(value, bool):
            raise TypeError("bool is not a valid Factory node id")
        return self.get(value) if isinstance(value, str) else int(value)

    def define(self, name: str, node: int, region: str) -> int:
        if not 0 <= int(node) < len(self.factory.nodes):
            raise RuntimeError(f"{name} refers to invalid Factory node {node}")
        previous = self.nets.get(name)
        if previous is not None and previous != node:
            raise RuntimeError(f"named net {name} changed from {previous} to {node}")
        self.nets[name] = int(node)
        self.node_regions[int(node)].add(region)
        return int(node)

    def gate(
        self,
        name: str,
        op: str,
        left: str | int,
        right: str | int | None = None,
        *,
        region: str,
    ) -> int:
        left_node = self.resolve(left)
        right_node = None if right is None else self.resolve(right)
        node = self.factory.gate(op, left_node, right_node)
        return self.define(name, node, region)

    def bus(
        self,
        name: str,
        drivers: Iterable[tuple[str | int, str | int]],
        *,
        region: str,
    ) -> int:
        resolved = tuple((self.resolve(enable), self.resolve(data)) for enable, data in drivers)
        if not resolved:
            raise RuntimeError(f"patch BUS {name} has no drivers")
        node = self.factory.bus(resolved)
        self.bus_labels[node].add(name)
        return self.define(name, node, region)

    def normalize_scalar(
        self,
        name: str,
        raw: str | int,
        filler: str | int,
        *,
        owner: str,
        region: str,
    ) -> int:
        raw_node = self.resolve(raw)
        filler_node = self.resolve(filler)
        node = self.factory.normalize_scalar(raw_node, filler_node, owner=owner)
        return self.define(name, node, region)

    def absorb(self, region: str, result: RegionResult, required: set[str]) -> None:
        actual = set(result.outputs)
        if actual != required:
            raise RuntimeError(
                f"{region} patch outputs differ: expected {sorted(required)}, got {sorted(actual)}"
            )
        overlap = set(result.outputs) & set(result.byproducts)
        if overlap:
            raise RuntimeError(f"{region} patch duplicates names: {sorted(overlap)}")
        for name, node in result.byproducts.items():
            self.define(name, int(node), region)
        for name, node in result.outputs.items():
            self.define(name, int(node), region)


class StaticWitnessGraft:
    """Materialize a fixed witness while retaining Switch source identities."""

    def __init__(
        self,
        factory: Any,
        source_nodes: Iterable[int],
        network: Iterable[Mapping[str, Any]],
    ) -> None:
        self.factory = factory
        self.source_nodes = tuple(int(node) for node in source_nodes)
        self.source_count = len(self.source_nodes)
        self.network = tuple(dict(item) for item in network)
        self.nodes: dict[int, int] = dict(enumerate(self.source_nodes))
        self.switch_drivers: dict[int, tuple[int, int]] = {}
        self.switch_bus_sets: list[frozenset[int]] = []
        self.slot_arrivals: dict[int, int] = {}
        self.owner_records: list[dict[str, Any]] = []

    def resolve_bus(self, selected: Iterable[int], label: str) -> int:
        selected_tuple = tuple(int(source) for source in selected)
        if not selected_tuple:
            raise RuntimeError(f"empty resolved bus at {label}")
        if len(set(selected_tuple)) != len(selected_tuple):
            raise RuntimeError(f"duplicate witness source on {label}: {selected_tuple}")

        switch_sources: list[int] = []
        direct_nodes: list[int] = []
        for source in selected_tuple:
            if source in self.switch_drivers:
                switch_sources.append(source)
            elif source in self.nodes:
                direct_nodes.append(self.nodes[source])
            else:
                raise RuntimeError(f"unknown or forward witness source {source} at {label}")

        if len(selected_tuple) > 1 and direct_nodes:
            raise RuntimeError(f"active source mixed into multi-driver BUS {label}")
        if direct_nodes:
            if len(direct_nodes) != 1:
                raise RuntimeError(f"multiple direct nodes at {label}")
            return direct_nodes[0]

        driver_set = frozenset(switch_sources)
        for previous in self.switch_bus_sets:
            if driver_set & previous and driver_set != previous:
                raise RuntimeError(
                    f"partial Switch-source owner overlap at {label}: "
                    f"{sorted(driver_set)} vs {sorted(previous)}"
                )
        self.switch_bus_sets.append(driver_set)
        drivers = tuple(self.switch_drivers[source] for source in sorted(driver_set))
        node = self.factory.bus(drivers)
        self.owner_records.append(
            {
                "label": label,
                "switch_sources": sorted(driver_set),
                "factory_bus": node,
                "drivers": [list(pair) for pair in drivers],
            }
        )
        return node

    def build(self) -> None:
        for expected_slot, item in enumerate(self.network):
            slot = int(item["slot"])
            source = int(item["source"])
            if slot != expected_slot or source != self.source_count + slot:
                raise RuntimeError(f"non-canonical witness slot: {item}")
            kind = str(item["kind"])
            left = self.resolve_bus(item["left_bus"], f"slot{slot}.left")
            if kind == "NOT":
                if item["right_bus"]:
                    raise RuntimeError(f"NOT slot {slot} has a right input")
                node = self.factory.gate("NOT", left)
                self.nodes[source] = node
                self.slot_arrivals[source] = self.factory.nodes[node].arrival
            else:
                right = self.resolve_bus(item["right_bus"], f"slot{slot}.right")
                if kind == "SWITCH":
                    self.switch_drivers[source] = (left, right)
                    self.slot_arrivals[source] = (
                        max(
                            self.factory.nodes[left].arrival,
                            self.factory.nodes[right].arrival,
                        )
                        + 1
                    )
                elif kind in {"AND", "OR", "NAND", "NOR", "XOR"}:
                    node = self.factory.gate(kind, left, right)
                    self.nodes[source] = node
                    self.slot_arrivals[source] = self.factory.nodes[node].arrival
                else:
                    raise RuntimeError(f"unsupported witness kind {kind!r}")
            claimed = int(item["depth_upper_bound"])
            if self.slot_arrivals[source] > claimed:
                raise RuntimeError(
                    f"slot {slot} arrival {self.slot_arrivals[source]} exceeds {claimed}"
                )

    def outputs(self, output_buses: Iterable[Iterable[int]]) -> tuple[int, ...]:
        return tuple(
            self.resolve_bus(bus, f"output{index}")
            for index, bus in enumerate(output_buses)
        )


def patch_carry_witness(original: Mapping[str, Any]) -> dict[str, Any]:
    """Apply the single reviewed Apre reassociation to the frozen carry witness."""

    if tuple(original.get("free_sources", ())) != ORIGINAL_CARRY_SOURCES:
        raise RuntimeError("carry witness source ABI changed")
    network = original.get("network")
    if not isinstance(network, list) or len(network) != 13:
        raise RuntimeError("carry witness network shape changed")
    first = network[0]
    expected = {
        "slot": 0,
        "source": 9,
        "kind": "OR",
        "left_bus": [3],
        "right_bus": [4],
        "cost": 1,
        "depth_upper_bound": 3,
    }
    if first != expected:
        raise RuntimeError(f"Apre witness slot changed: {first!r}")

    # Source 4 (A34) must be private to Apre.  Otherwise eliminating it would
    # silently alter a second consumer in the carry network.
    source4_uses: list[str] = []
    for item in network:
        for side in ("left_bus", "right_bus"):
            if 4 in item[side]:
                source4_uses.append(f"slot{item['slot']}.{side}")
    for index, bus in enumerate(original.get("output_buses", ())):
        if 4 in bus:
            source4_uses.append(f"output{index}")
    if source4_uses != ["slot0.right_bus"]:
        raise RuntimeError(f"A34 is no longer private to Apre: {source4_uses}")

    patched = deepcopy(dict(original))
    patched["free_sources"] = list(REASSOCIATED_CARRY_SOURCES)
    patched["network"][0]["left_bus"] = [4]  # X23
    patched["network"][0]["right_bus"] = [6]  # G4
    return patched


def validate_s34_blueprint(witness: Mapping[str, Any]) -> None:
    """Pin the human-readable default formula to the reviewed cost-9 witness."""

    if tuple(witness.get("free_sources", ())) != ORIGINAL_S34_SOURCES:
        raise RuntimeError("S3/S4 witness source ABI changed")
    if witness.get("output_buses") != [[20], [25]]:
        raise RuntimeError("S3/S4 witness outputs changed")
    network = witness.get("network")
    expected = [
        (17, "NAND", [6], [15]),
        (18, "OR", [6], [15]),
        (19, "OR", [3], [4]),
        (20, "AND", [17], [18]),
        (21, "OR", [12], [19]),
        (22, "NOR", [5], [9]),
        (23, "NOR", [8], [16]),
        (24, "AND", [21], [22]),
        (25, "OR", [23], [24]),
    ]
    actual = [
        (
            int(item["source"]),
            str(item["kind"]),
            list(item["left_bus"]),
            list(item["right_bus"]),
        )
        for item in network
    ] if isinstance(network, list) else None
    if actual != expected:
        raise RuntimeError("reviewed S3/S4 formula blueprint changed")
    used_sources = {
        int(source)
        for item in network
        for side in ("left_bus", "right_bus")
        for source in item[side]
        if int(source) < len(ORIGINAL_S34_SOURCES)
    }
    if 10 in used_sources:
        raise RuntimeError("S3/S4 unexpectedly consumes A34; 94/6 rewrite is invalid")


def default_s34(context: BuildContext) -> RegionResult:
    """Reviewed 9-gate S3/S4 region, including the already shared X23 gate."""

    region = "s34"
    n_pc = context.gate("S34.NAND_P3_C3", "NAND", "P3", "C3", region=region)
    o_pc = context.gate("S34.OR_P3_C3", "OR", "P3", "C3", region=region)
    s3 = context.gate("S3", "AND", n_pc, o_pc, region=region)
    b_x = context.gate("S34.OR_B12_X23", "OR", "B12", "X23", region=region)
    low_phase = context.gate("S34.NOR_Q3_P4", "NOR", "Q3", "P4", region=region)
    high_phase = context.gate("S34.NOR_Q4_C5", "NOR", "Q4", "C5", region=region)
    selected = context.gate("S34.SELECTED", "AND", b_x, low_phase, region=region)
    s4 = context.gate("S4", "OR", high_phase, selected, region=region)
    return RegionResult(
        outputs={"S3": s3, "S4": s4},
        byproducts={
            "S34.phase_nand": n_pc,
            "S34.phase_or": o_pc,
            "S34.low_prefix": b_x,
            "S34.low_phase": low_phase,
            "S34.high_phase": high_phase,
            "S34.selected": selected,
        },
        note="cost-9 witness with X23 shared into Apre",
    )


def default_s56(context: BuildContext) -> RegionResult:
    """Current 10-gate S5/S6 region; the intended first patch boundary."""

    region = "s56"
    t5 = context.gate("S56.T5", "AND", "P5", "C5", region=region)
    r5 = context.gate("S56.R5", "NOR", "P5", "C5", region=region)
    s5 = context.gate("S5", "NOR", t5, r5, region=region)
    selected_phase = context.gate(
        "S56.selected_phase", "NOR", "Q5", "P6", region=region
    )
    lower_active = context.bus(
        "S56.lower_active",
        (("C5", selected_phase), ("G5", selected_phase)),
        region=region,
    )
    upper_phase = context.gate(
        "S56.upper_phase", "NOR", "Q6", "C7", region=region
    )
    s6 = context.gate("S6", "OR", lower_active, upper_phase, region=region)
    return RegionResult(
        outputs={"S5": s5, "S6": s6},
        byproducts={
            "S56.P5_and_C5": t5,
            "S56.neither_P5_nor_C5": r5,
            "S56.nonpropagate_selector": selected_phase,
            "S56.lower_active": lower_active,
            "S56.upper_phase": upper_phase,
        },
        note="current 3-gate S5 plus 7-gate S6",
    )


@dataclass(frozen=True)
class FormulaHooks:
    name: str
    build_s34: Callable[[BuildContext], RegionResult]
    build_s56: Callable[[BuildContext], RegionResult]
    source: str = "builtin"


def normalize_region_result(value: Any, region: str) -> RegionResult:
    if isinstance(value, RegionResult):
        return value
    if isinstance(value, Mapping):
        return RegionResult(outputs={str(name): int(node) for name, node in value.items()})
    raise RuntimeError(f"{region} patch must return RegionResult or a mapping")


def load_formula_hooks(path: Path | None) -> FormulaHooks:
    if path is None:
        return FormulaHooks("builtin-g94", default_s34, default_s56)
    resolved = path.resolve()
    module = load_module(f"byte_adder_formula_patch_{sha256_bytes(str(resolved).encode())[:12]}", resolved)
    s34 = getattr(module, "build_s34", default_s34)
    s56 = getattr(module, "build_s56", default_s56)
    if not callable(s34) or not callable(s56):
        raise RuntimeError("patch build_s34/build_s56 attributes must be callable")

    def wrap(function: Callable[[BuildContext], Any], region: str):
        return lambda context: normalize_region_result(function(context), region)

    return FormulaHooks(
        name=str(getattr(module, "PATCH_NAME", resolved.stem)),
        build_s34=wrap(s34, "s34"),
        build_s56=wrap(s56, "s56"),
        source=str(resolved),
    )


def reduced_sum(factory: Any, generate: int, valency: int, cin: int, cout: int) -> int:
    active = factory.gate("OR", valency, cin)
    not_both_generate = factory.gate("NAND", generate, cin)
    selected_phase = factory.gate("NAND", cout, not_both_generate)
    return factory.gate("AND", active, selected_phase)


def av_switch_gray(factory: Any, carry: int, transfer: tuple[int, int]) -> int:
    any_generate, valency = transfer
    return factory.bus(((any_generate, valency), (carry, valency)))


def av_switch_combine(
    factory: Any, low: tuple[int, int], high: tuple[int, int]
) -> tuple[int, int]:
    low_a, low_v = low
    high_a, high_v = high
    any_generate = factory.gate("OR", low_a, high_a)
    valency = factory.bus(((high_a, high_v), (low_v, high_v)))
    return any_generate, valency


def audit_static_dag(
    factory: Any,
    outputs: tuple[int, ...],
    context: BuildContext,
    carry_graft: StaticWitnessGraft,
    creation_regions: Mapping[str, range],
) -> dict[str, Any]:
    live = set(factory.reachable(outputs))
    op_counts: Counter[str] = Counter()
    op_costs: Counter[str] = Counter()
    topological_violations: list[dict[str, Any]] = []
    arrival_violations: list[dict[str, Any]] = []
    bus_rows: list[dict[str, Any]] = []
    normalizer_rows: list[dict[str, Any]] = []
    supported_ops = {
        "INPUT",
        "CONST",
        "NOT",
        "AND",
        "OR",
        "NAND",
        "NOR",
        "XOR",
        "XNOR",
        "BUS",
        "MAKER2",
        "SPLITTER2",
    }
    unsupported: list[dict[str, Any]] = []

    for node_id in sorted(live):
        node = factory.nodes[node_id]
        op_counts[node.op] += 1
        op_costs[node.op] += node.cost
        if node.op not in supported_ops:
            unsupported.append({"node": node_id, "op": node.op})
        if any(argument >= node_id for argument in node.args):
            topological_violations.append(
                {"node": node_id, "args": list(node.args)}
            )
        if node.op in {"INPUT", "CONST"}:
            expected_arrival = 0
        elif node.op == "BUS":
            if len(node.args) % 2:
                raise RuntimeError(f"BUS {node_id} has odd argument count")
            pairs = [
                (node.args[offset], node.args[offset + 1])
                for offset in range(0, len(node.args), 2)
            ]
            if len(pairs) != len(set(pairs)):
                raise RuntimeError(f"BUS {node_id} has duplicate logical drivers")
            expected_arrival = max(
                max(factory.nodes[enable].arrival, factory.nodes[data].arrival) + 1
                for enable, data in pairs
            ) if pairs else 0
            expected_cost = 2 * len(pairs)
            bus_rows.append(
                {
                    "node": node_id,
                    "owner": f"bus_{node_id}",
                    "driver_count": len(pairs),
                    "drivers": [list(pair) for pair in pairs],
                    "cost": node.cost,
                    "arrival": node.arrival,
                    "patch_labels": sorted(context.bus_labels.get(node_id, ())),
                    "complete_owner": node.cost == expected_cost,
                }
            )
            if node.cost != expected_cost or node.step_delay != (1 if pairs else 0):
                raise RuntimeError(f"BUS {node_id} cost/delay contract changed")
        elif node.op == "MAKER2":
            if len(node.args) != 2 or node.cost != 0 or node.step_delay != 0:
                raise RuntimeError(f"MAKER2 {node_id} contract changed")
            expected_arrival = max(
                factory.nodes[argument].arrival for argument in node.args
            )
            if node.may_z:
                raise RuntimeError(f"MAKER2 {node_id} must produce an active word")
        elif node.op == "SPLITTER2":
            metadata = factory.splitter_metadata.get(node_id)
            normalizer = factory.normalizer_metadata.get(node_id)
            if (
                len(node.args) != 1
                or factory.nodes[node.args[0]].op != "MAKER2"
                or node.cost != 0
                or node.step_delay != 0
                or metadata is None
                or metadata.get("lane") != 0
                or normalizer is None
            ):
                raise RuntimeError(f"SPLITTER2 {node_id} contract changed")
            expected_arrival = factory.nodes[node.args[0]].arrival
            if node.may_z:
                raise RuntimeError(f"SPLITTER2 {node_id} must produce an active scalar")
            maker = factory.nodes[node.args[0]]
            raw, filler = maker.args
            if (
                normalizer.get("raw") != raw
                or normalizer.get("filler") != filler
                or normalizer.get("maker") != node.args[0]
                or normalizer.get("owner") != metadata.get("owner")
                or not factory.nodes[raw].may_z
                or factory.nodes[filler].may_z
                or factory.nodes[filler].arrival > factory.nodes[raw].arrival
                or expected_arrival != factory.nodes[raw].arrival
            ):
                raise RuntimeError(f"SPLITTER2 {node_id} zero-delay normalizer changed")
            normalizer_rows.append(
                {
                    "splitter": node_id,
                    "maker": node.args[0],
                    "owner": metadata["owner"],
                    "raw": raw,
                    "filler": filler,
                    "raw_may_z": True,
                    "output_may_z": False,
                    "cost": maker.cost + node.cost,
                    "step_delay": maker.step_delay + node.step_delay,
                    "raw_arrival": factory.nodes[raw].arrival,
                    "output_arrival": node.arrival,
                }
            )
        else:
            expected_arrival = (
                max(factory.nodes[argument].arrival for argument in node.args)
                + node.step_delay
            )
        if node.arrival != expected_arrival:
            arrival_violations.append(
                {
                    "node": node_id,
                    "stored": node.arrival,
                    "recomputed": expected_arrival,
                }
            )

    source_owner_sets = [
        frozenset(record["switch_sources"])
        for record in carry_graft.owner_records
    ]
    partial_source_overlaps: list[dict[str, Any]] = []
    for left_index, left in enumerate(source_owner_sets):
        for right_index in range(left_index + 1, len(source_owner_sets)):
            right = source_owner_sets[right_index]
            if left & right and left != right:
                partial_source_overlaps.append(
                    {
                        "left": sorted(left),
                        "right": sorted(right),
                        "left_record": carry_graft.owner_records[left_index]["label"],
                        "right_record": carry_graft.owner_records[right_index]["label"],
                    }
                )

    live_constants = sorted(
        node_id for node_id in live if factory.nodes[node_id].op == "CONST"
    )
    output_may_z = [bool(factory.nodes[node].may_z) for node in outputs]
    if topological_violations or arrival_violations or unsupported:
        raise RuntimeError("static Factory DAG audit failed")
    if partial_source_overlaps:
        raise RuntimeError(f"carry owner partition failed: {partial_source_overlaps}")
    if live_constants:
        raise RuntimeError(f"unexpected live constants: {live_constants}")

    region_nodes = {
        region: sorted(node for node, regions in context.node_regions.items() if region in regions and node in live)
        for region in sorted({region for regions in context.node_regions.values() for region in regions})
    }
    region_costs = {
        region: sum(factory.nodes[node].cost for node in nodes)
        for region, nodes in region_nodes.items()
    }
    region_max_arrivals = {
        region: max((factory.nodes[node].arrival for node in nodes), default=0)
        for region, nodes in region_nodes.items()
    }
    exclusive_regions: dict[str, list[int]] = {}
    assigned: set[int] = set()
    for region, node_range in creation_regions.items():
        nodes = sorted(set(node_range) & live)
        if assigned & set(nodes):
            raise RuntimeError(f"creation region {region} overlaps a previous region")
        assigned.update(nodes)
        exclusive_regions[region] = nodes
    missing_partition_nodes = sorted(live - assigned)
    if missing_partition_nodes:
        raise RuntimeError(f"live nodes missing from creation partition: {missing_partition_nodes}")
    exclusive_costs = {
        region: sum(factory.nodes[node].cost for node in nodes)
        for region, nodes in exclusive_regions.items()
    }
    if sum(exclusive_costs.values()) != sum(op_costs.values()):
        raise RuntimeError("exclusive creation-region costs do not sum to total cost")
    return {
        "status": "pass",
        "live_nodes": len(live),
        "op_counts": dict(sorted(op_counts.items())),
        "op_costs": dict(sorted(op_costs.items())),
        "total_cost": sum(op_costs.values()),
        "topological_violation_count": len(topological_violations),
        "arrival_violation_count": len(arrival_violations),
        "unsupported_node_count": len(unsupported),
        "live_constants": live_constants,
        "output_may_z": output_may_z,
        "named_regions_nonexclusive": region_nodes,
        "named_region_costs_nonexclusive": region_costs,
        "named_region_max_arrivals": region_max_arrivals,
        "creation_regions_exclusive": exclusive_regions,
        "creation_region_costs_exclusive": exclusive_costs,
        "bus_owner_audit": {
            "status": "pass",
            "factory_bus_count": len(bus_rows),
            "complete_factory_owners": all(row["complete_owner"] for row in bus_rows),
            "partial_witness_source_overlap_count": len(partial_source_overlaps),
            "witness_owner_records": carry_graft.owner_records,
            "factory_owners": bus_rows,
            "identity_note": (
                "equal enable/data pairs in different BUS owners are separate Switch "
                "instances; only witness source identity may prove illegal partial reuse"
            ),
        },
        "normalizer_audit": {
            "status": "pass",
            "contract": "active = value & driven; cost=0; step_delay=0",
            "count": len(normalizer_rows),
            "rows": normalizer_rows,
        },
    }


def layout_contract(
    factory_dag: Mapping[str, Any],
    static_audit: Mapping[str, Any],
    *,
    full_verified: bool,
) -> dict[str, Any]:
    """Describe the deferred physical-layout checks without creating a circuit."""

    rows = factory_dag["nodes"]
    legacy_ops = {
        "INPUT",
        "CONST",
        "NOT",
        "AND",
        "NAND",
        "OR",
        "NOR",
        "XOR",
        "XNOR",
        "BUS",
        "MAKER2",
        "SPLITTER2",
    }
    unsupported = [row["id"] for row in rows if row["op"] not in legacy_ops]
    owner_failures: list[int] = []
    for row in rows:
        if row["op"] != "BUS":
            continue
        owner = row.get("resolved_network")
        drivers = row.get("drivers")
        if (
            owner != f"bus_{row['id']}"
            or not isinstance(drivers, list)
            or any(driver.get("owner") != owner for driver in drivers)
        ):
            owner_failures.append(int(row["id"]))
    return {
        "schema": "byte-adder-factory-layout-readiness-v1",
        "status": (
            "ready-for-research-materialization"
            if full_verified and not unsupported and not owner_failures
            else "layout-interface-ready-semantic-verification-required"
            if not unsupported and not owner_failures
            else "blocked"
        ),
        "materializer": str(MATERIALIZER_PATH.relative_to(ROOT)).replace("\\", "/"),
        "factory_legacy_subset": not unsupported,
        "unsupported_nodes": unsupported,
        "owner_serialization_failures": owner_failures,
        "bus_owner_audit_status": static_audit["bus_owner_audit"]["status"],
        "geometry_status": "not-run-no-circuit-data",
        "required_after_full_verification": [
            "materialize to a derived .research directory without --deploy",
            "audit sprite/body and pin collisions",
            "reject every wire crossing a component body or unrelated pin",
            "allow wire-to-wire crossings only when connectivity remains intended",
            "verify each resolved BUS owner maps to its complete Switch set",
            "recompute physical component cost and critical-path delay",
        ],
        "routing_policy": {
            "wire_wire_crossing_allowed": True,
            "wire_component_body_crossing_allowed": False,
            "wire_unrelated_pin_crossing_allowed": False,
            "partial_switch_owner_reuse_allowed": False,
        },
    }


def build_candidate(
    hooks: FormulaHooks,
    *,
    full_verify: bool = False,
    b12_g1_recode: bool = False,
    hub87_high_graft: bool = False,
) -> dict[str, Any]:
    carry_witness, carry_raw = read_frozen_json(
        CARRY_WITNESS_PATH, CARRY_WITNESS_SHA256
    )
    s34_witness, s34_raw = read_frozen_json(S34_WITNESS_PATH, S34_WITNESS_SHA256)
    validate_s34_blueprint(s34_witness)
    patched_carry = patch_carry_witness(carry_witness)

    factory = PatchFactory()
    creation_regions: dict[str, range] = {
        "factory_inputs_and_constants": range(0, len(factory.nodes))
    }
    phase_start = len(factory.nodes)
    nets: dict[str, int] = {"Cin": factory.inputs["cin"]}
    g: list[int] = []
    q: list[int | None] = [None] * 8
    p: list[int | None] = [None] * 8
    v: list[int | None] = [None] * 8
    for bit in range(8):
        a = factory.inputs[f"a{bit}"]
        b = factory.inputs[f"b{bit}"]
        nets[f"A{bit}"] = a
        nets[f"B{bit}"] = b
        g.append(factory.gate("AND", a, b))
        nets[f"G{bit}"] = g[-1]
        if bit != 0:
            q[bit] = factory.gate("NOR", a, b)
            p[bit] = factory.gate("NOR", g[bit], q[bit])
            nets[f"Q{bit}"] = int(q[bit])
            nets[f"P{bit}"] = int(p[bit])
        if bit == 0 or (bit in (5, 6) and not hub87_high_graft):
            v[bit] = factory.gate("OR", a, b)
            nets[f"V{bit}"] = int(v[bit])
    creation_regions["bit_state_leaves"] = range(phase_start, len(factory.nodes))
    phase_start = len(factory.nodes)

    c0 = nets["Cin"]
    c1 = av_switch_gray(factory, c0, (g[0], int(v[0])))
    t1 = factory.gate("AND", int(p[1]), c1)
    c2 = factory.gate("OR", g[1], t1)
    a12 = factory.gate("OR", g[1], g[2])
    n12 = factory.gate("NOR", int(q[1]), int(q[2]))
    n34 = factory.gate("NOR", int(q[3]), int(q[4]))
    if hub87_high_graft:
        a56 = factory.gate("OR", g[5], g[6])
        v56 = None
    else:
        a56, v56 = av_switch_combine(
            factory,
            (g[5], int(v[5])),
            (g[6], int(v[6])),
        )

    # X23 is built before the carry witness so Factory interning guarantees the
    # S3/S4 formula and Apre consume one physical OR gate.
    x23 = factory.gate("OR", g[2], g[3])
    nets.update(
        {
            "C1": c1,
            "T1": t1,
            "C2": c2,
            "A12": a12,
            "N12": n12,
            "N34": n34,
            "A56": a56,
            "X23": x23,
        }
    )
    if v56 is not None:
        nets["V56"] = v56
    creation_regions["low_shell_and_x23"] = range(phase_start, len(factory.nodes))
    phase_start = len(factory.nodes)

    carry_source_nodes = dict(nets)
    if hub87_high_graft:
        # V56 is used only by the dead high-carry suffix of the frozen witness.
        # A scalar placeholder lets the shared low witness produce C3/C5 while
        # the final live cone omits V5/V6/V56/V36/C7 entirely.
        carry_source_nodes["V56"] = g[5]
    carry_sources = tuple(carry_source_nodes[name] for name in REASSOCIATED_CARRY_SOURCES)
    carry_graft = StaticWitnessGraft(factory, carry_sources, patched_carry["network"])
    carry_graft.build()
    original_c3, original_c5, original_c7 = carry_graft.outputs(
        patched_carry["output_buses"]
    )
    apre = carry_graft.nodes[9]
    v34 = carry_graft.nodes[15]
    original_b12 = carry_graft.resolve_bus((10, 12), "named.B12")

    if b12_g1_recode:
        # Old B12 uses enables C1 and A12=(G1|G2).  Replacing A12 by G1 only
        # removes the G2-only rows.  Every B12 consumer already has an
        # independent G2-containing absorbing path: C3 has G2 directly,
        # C5/C7 have Apre=(G2|G3|G4), and S4 has X23=(G2|G3).
        b12 = factory.bus(((c1, n12), (g[1], n12)))
        c3 = factory.gate("OR", g[2], b12)
        c5 = factory.bus(((apre, v34), (b12, v34)))
        if hub87_high_graft:
            c7 = None
        else:
            v36 = carry_graft.resolve_bus((11, 14, 17), "named.V36")
            c7 = factory.bus(((a56, int(v56)), (apre, v36), (b12, v36)))
    else:
        b12 = original_b12
        c3, c5 = original_c3, original_c5
        c7 = None if hub87_high_graft else original_c7

    # Exact structural assertions make the reassociation independent of node ids.
    def assert_gate(node_id: int, op: str, args: Iterable[int], label: str) -> None:
        node = factory.nodes[node_id]
        if node.op != op or tuple(sorted(node.args)) != tuple(sorted(args)):
            raise RuntimeError(f"{label} structure changed: {node}")

    assert_gate(x23, "OR", (g[2], g[3]), "X23")
    assert_gate(apre, "OR", (x23, g[4]), "Apre")
    assert_gate(v34, "OR", (n34, g[4]), "V34")
    assert_gate(c3, "OR", (g[2], b12), "C3")
    if b12_g1_recode:
        expected_b12_args = tuple(sorted((c1, n12, g[1], n12)))
        actual_b12 = factory.nodes[b12]
        if actual_b12.op != "BUS" or tuple(sorted(actual_b12.args)) != expected_b12_args:
            raise RuntimeError(f"B12 G1 recode structure changed: {actual_b12}")
    nets.update({"Apre": apre, "V34": v34, "B12": b12, "C3": c3, "C5": c5})
    if c7 is not None:
        nets["C7"] = c7
    creation_regions["reassociated_carry_witness"] = range(phase_start, len(factory.nodes))
    phase_start = len(factory.nodes)

    context = BuildContext(factory, nets)
    context.add_lazy("A34", lambda: factory.gate("OR", g[3], g[4]))
    for name, node in nets.items():
        context.node_regions[node].add("fixed_shell")
    context.node_regions[x23].add("shared_apre_s34")
    context.node_regions[apre].add("shared_apre_s34")

    s34_result = normalize_region_result(hooks.build_s34(context), "s34")
    context.absorb("s34", s34_result, {"S3", "S4"})
    creation_regions["s34_patch"] = range(phase_start, len(factory.nodes))
    phase_start = len(factory.nodes)
    if hub87_high_graft:
        region = "hub87_high_graft"
        o5 = context.gate("Hub87.O5", "OR", "P5", "C5", region=region)
        d5 = context.gate("Hub87.D5", "NAND", "P5", "C5", region=region)
        s5 = context.gate("S5", "AND", o5, d5, region=region)

        e6 = context.gate("Hub87.E6", "NOR", "A56", "Q6", region=region)
        f6 = context.gate("Hub87.F6", "NOR", "P6", "Q5", region=region)
        h6 = context.gate("Hub87.H6", "OR", "G5", "C5", region=region)
        s6 = context.bus(
            "S6",
            ((e6, d5), (f6, h6)),
            region=region,
        )

        n56 = context.gate("Hub87.N56", "NOR", "Q5", "Q6", region=region)
        k56 = context.gate("Hub87.K56", "NOR", "G6", n56, region=region)
        r7 = context.gate("Hub87.R7", "NOR", "C5", "A56", region=region)
        j7 = context.gate("Hub87.J7", "NOR", "P7", k56, region=region)
        h7 = context.gate("Hub87.H7", "OR", "A56", "C5", region=region)
        s7 = context.bus(
            "S7",
            ((k56, "P7"), (r7, "P7"), (j7, h7)),
            region=region,
        )

        # J7 is already paid by S7.  Reuse it to obtain the final propagate
        # phase in one gate:
        #   NOR(K56, NOR(P7, K56)) = P7 & ~K56.
        # This removes the private X7=(G7|Q7)=~P7 gate while preserving D6.
        f7 = context.gate("Hub87.F7", "NOR", k56, j7, region=region)
        c8_raw = context.bus(
            "Hub87.C8raw",
            (("G7", "G7"), (f7, h7)),
            region=region,
        )
        c8 = context.normalize_scalar(
            "C8",
            c8_raw,
            "Cin",
            owner="codex.byte_adder.hub87.c8_active",
            region=region,
        )
        s56_result = RegionResult(
            outputs={"S5": s5, "S6": s6},
            byproducts={
                "Hub87.N56": n56,
                "Hub87.K56": k56,
                "Hub87.H7": h7,
            },
            note="Hub87 direct high graft with explicit zero-cost C8 normalization",
        )
        creation_regions["hub87_high_graft"] = range(phase_start, len(factory.nodes))
        phase_start = len(factory.nodes)
    else:
        s56_result = normalize_region_result(hooks.build_s56(context), "s56")
        context.absorb("s56", s56_result, {"S5", "S6"})
        creation_regions["s56_patch"] = range(phase_start, len(factory.nodes))
        phase_start = len(factory.nodes)

        t7 = factory.gate("AND", int(p[7]), int(c7))
        c8 = factory.gate("OR", g[7], t7)
        s7 = factory.gate("NOR", t7, factory.gate("NOR", int(p[7]), int(c7)))

    s0 = reduced_sum(factory, g[0], int(v[0]), c0, c1)
    s1 = factory.gate("NOR", t1, factory.gate("NOR", int(p[1]), c1))
    t2 = factory.gate("AND", int(p[2]), c2)
    s2 = factory.gate("NOR", t2, factory.gate("NOR", int(p[2]), c2))
    context.define("C8", c8, "fixed_shell")
    context.define("S0", s0, "fixed_shell")
    context.define("S1", s1, "fixed_shell")
    context.define("S2", s2, "fixed_shell")
    context.define("S7", s7, "fixed_shell")
    sums = tuple(context.get(f"S{bit}") for bit in range(8))
    outputs = (*sums, c8)
    creation_regions["fixed_output_shell"] = range(phase_start, len(factory.nodes))

    metrics = factory.structural_metrics(outputs)
    arrivals = {
        "C1": factory.nodes[c1].arrival,
        "C2": factory.nodes[c2].arrival,
        "C3": factory.nodes[c3].arrival,
        "C5": factory.nodes[c5].arrival,
        **{f"S{bit}": factory.nodes[node].arrival for bit, node in enumerate(sums)},
        "C8": factory.nodes[c8].arrival,
    }
    if c7 is not None:
        arrivals["C7"] = factory.nodes[c7].arrival
    static_audit = audit_static_dag(
        factory,
        outputs,
        context,
        carry_graft,
        creation_regions,
    )
    dag = serialize(factory, outputs)
    layout = layout_contract(dag, static_audit, full_verified=full_verify)
    canonical_sha256 = canonical_expression_sha256(factory, outputs)

    semantic: dict[str, Any]
    if full_verify:
        packed, semantic = factory.evaluate(outputs)
        if semantic["mismatch_union_count"]:
            raise RuntimeError(f"full truth mismatch: {semantic}")
        if semantic["conflict_assignment_count"]:
            raise RuntimeError(f"full BUS conflict: {semantic}")
        raw_s6 = packed[context.get("S6")]
        if isinstance(raw_s6, PackedWord):
            raise RuntimeError("S6 Factory boundary unexpectedly became a word")
        raw_s6_audit = {
            "node": context.get("S6"),
            "may_z": bool(factory.nodes[context.get("S6")].may_z),
            "z_assignment_count": ((~raw_s6.driven) & core.ALL).bit_count(),
            "driven_assignment_count": raw_s6.driven.bit_count(),
            "data_plane_one_count": (raw_s6.value & raw_s6.driven).bit_count(),
            "active_zero_count": (
                raw_s6.driven & (~raw_s6.value & core.ALL)
            ).bit_count(),
            "conflict_assignment_count": raw_s6.conflict.bit_count(),
        }
        semantic["raw_s6_owner_audit"] = raw_s6_audit
        semantic["final_output_maker8_lane6_contract"] = {
            "normalization": "observed = raw.value & raw.driven; Z contributes zero",
            "active_assignment_count": core.ASSIGNMENTS,
            "data_plane_one_count": raw_s6_audit["data_plane_one_count"],
            "mismatch_assignment_count": semantic["mismatch_count_by_output"][6],
            "conflict_assignment_count": raw_s6_audit["conflict_assignment_count"],
        }
        if hooks.name == "s56-tail9-raw-z-to-final-maker8" and not hub87_high_graft:
            expected_tail9 = {
                "z_assignment_count": 32768,
                "driven_assignment_count": 98304,
                "data_plane_one_count": 65536,
                "active_zero_count": 32768,
                "conflict_assignment_count": 0,
            }
            actual_tail9 = {
                key: raw_s6_audit[key] for key in expected_tail9
            }
            if actual_tail9 != expected_tail9:
                raise RuntimeError(
                    f"tail9 raw S6 distribution changed: {actual_tail9}"
                )
        semantic_mode = "full-131072-complete"
    else:
        semantic = {
            "status": "not-run",
            "reason": "static builder mode; exhaustive verification reserved for a closed candidate",
            "truth_table_rows": 0,
        }
        semantic_mode = "static-only"

    return {
        "schema": "byte-adder-g94-apre-patchable-factory-v1",
        "status": "static-audited" if not full_verify else "sat",
        "formula_hooks": {
            "name": hooks.name,
            "source": hooks.source,
            "s34_note": s34_result.note,
            "s56_note": s56_result.note,
        },
        "rewrite": {
            "before": "A34=OR(G3,G4); Apre=OR(G2,A34)",
            "after": "X23=OR(G2,G3); Apre=OR(X23,G4)",
            "A34_live": "A34" in context.nets and context.nets["A34"] in factory.reachable(outputs),
            "A12_live": a12 in factory.reachable(outputs),
            "b12_g1_recode": b12_g1_recode,
            "hub87_high_graft": hub87_high_graft,
            "X23_node": x23,
            "Apre_node": apre,
        },
        "dependencies": {
            "core": str(CORE_PATH.relative_to(ROOT)).replace("\\", "/"),
            "carry_witness": {
                "path": str(CARRY_WITNESS_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_bytes(carry_raw),
            },
            "s34_blueprint": {
                "path": str(S34_WITNESS_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_bytes(s34_raw),
            },
        },
        "metrics": metrics,
        "arrivals": arrivals,
        "semantic_mode": semantic_mode,
        "semantic": semantic,
        "static_audit": static_audit,
        "canonical_expression_sha256": canonical_sha256,
        "layout_contract": layout,
        "named_nodes": {
            name: {
                "id": node,
                "op": factory.nodes[node].op,
                "args": list(factory.nodes[node].args),
                "cost": factory.nodes[node].cost,
                "arrival": factory.nodes[node].arrival,
                "regions": sorted(context.node_regions.get(node, ())),
            }
            for name, node in sorted(context.nets.items())
            if node in factory.reachable(outputs)
        },
        "test_domain": {
            "variables": core.VARIABLES,
            "rows": core.ASSIGNMENTS if full_verify else 0,
            "complete_u8_u8_u1": bool(full_verify),
        },
        "factory_dag": dag,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the patchable 94/6 Byte Adder Factory DAG"
    )
    parser.add_argument("--patch-module", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-gate", type=int, default=94)
    parser.add_argument("--max-delay", type=int, default=6)
    parser.add_argument(
        "--b12-g1-recode",
        action="store_true",
        help="replace B12's private A12 enable by G1; downstream G2 paths absorb the difference",
    )
    parser.add_argument(
        "--hub87-high-graft",
        action="store_true",
        help="replace V5/V6/V56/V36/C7 and the high output shell by the Hub87 direct macro",
    )
    parser.add_argument(
        "--full-verify",
        action="store_true",
        help="run 131072 rows; reserved for an explicitly authorized closed candidate",
    )
    args = parser.parse_args(argv)

    hooks = load_formula_hooks(args.patch_module)
    payload = build_candidate(
        hooks,
        full_verify=args.full_verify,
        b12_g1_recode=args.b12_g1_recode,
        hub87_high_graft=args.hub87_high_graft,
    )
    metrics = payload["metrics"]
    if metrics["gate"] > args.max_gate:
        raise RuntimeError(f"gate threshold failed: {metrics['gate']} > {args.max_gate}")
    if metrics["delay"] > args.max_delay:
        raise RuntimeError(f"delay threshold failed: {metrics['delay']} > {args.max_delay}")
    if args.patch_module is None and (metrics["gate"], metrics["delay"]) != (94, 6):
        raise RuntimeError(f"built-in 94/6 baseline regressed: {metrics}")
    if args.patch_module is None and payload["rewrite"]["A34_live"]:
        raise RuntimeError("built-in Apre reassociation failed to kill A34")
    if (
        args.patch_module is None
        and payload["canonical_expression_sha256"] != BUILTIN_G94_CANONICAL_SHA256
    ):
        raise RuntimeError(
            "built-in 94/6 recursive structure differs from the independently audited g94 DAG"
        )

    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded.encode("utf-8"))
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "metrics": metrics,
                "arrivals": payload["arrivals"],
                "semantic_mode": payload["semantic_mode"],
                "static_audit": payload["static_audit"]["status"],
                "layout_status": payload["layout_contract"]["status"],
                "sha256": sha256_bytes(encoded.encode()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
