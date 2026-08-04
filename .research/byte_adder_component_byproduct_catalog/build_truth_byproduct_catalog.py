"""Build a physical-truth byproduct catalog for the verified 80/7 byte adder.

The catalog deliberately separates Boolean value from physical driven/conflict
state.  It covers the minimal legal primitive expansions used before the byte
adder level, records every intermediate signal, and imports every live signal
and Switch driver from the reviewed 80/7 Factory DAG.

This script reads research artifacts only.  It does not read or write a game
save, launch the game, materialize a candidate, or touch Git state.
"""

from __future__ import annotations

import argparse
import base64
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
import importlib.util
import itertools
import json
from pathlib import Path
import sys
from typing import Callable, Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DAG_PATH = ROOT / ".research/byte_adder_root/byte-adder-hybrid-phasefold-g80-d7.json"
COST_PATH = (
    ROOT
    / ".research/byte_adder_component_costs_agent/byte_adder_available_primitives.json"
)
RUNTIME_PATH = HERE / "runtime-evidence-2.1.292.json"
ADVANCED_LIBRARY_PATH = (
    ROOT
    / ".research/byte_adder_boolean_superopt_agent/advanced_adder_cell_library.py"
)
DEFAULT_OUTPUT = HERE / "truth-byproduct-catalog-v1.json"
DEFAULT_REPORT = HERE / "truth-byproduct-catalog-v1.md"

ORDINARY = ("NOT", "AND", "OR", "NAND", "NOR")
OWNER_COSTS: dict[str, int] = {}


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def register_owner(owner: str, cost: int) -> None:
    previous = OWNER_COSTS.setdefault(owner, cost)
    if previous != cost:
        raise RuntimeError(f"owner cost changed for {owner}: {previous} != {cost}")


def owner_gate(owners: Iterable[str]) -> int:
    return sum(OWNER_COSTS[owner] for owner in set(owners))


@dataclass(frozen=True, slots=True)
class Domain:
    name: str
    inputs: tuple[str, ...]
    assignments: tuple[int, ...]
    columns: dict[str, int]
    row_count: int
    mask: int
    byte_count: int
    domain_id: str
    constraint: str


def mask_bytes(value: int, byte_count: int) -> bytes:
    return (value & ((1 << (byte_count * 8)) - 1)).to_bytes(byte_count, "little")


def make_domain(
    name: str,
    inputs: Sequence[str],
    predicate: Callable[[dict[str, int]], bool] | None = None,
    constraint: str = "full Cartesian Boolean domain",
) -> Domain:
    names = tuple(inputs)
    assignments: list[int] = []
    for assignment in range(1 << len(names)):
        row = {item: (assignment >> index) & 1 for index, item in enumerate(names)}
        if predicate is None or predicate(row):
            assignments.append(assignment)
    rows = len(assignments)
    byte_count = (rows + 7) // 8
    columns: dict[str, int] = {}
    for input_index, input_name in enumerate(names):
        packed = bytearray(byte_count)
        for row_index, assignment in enumerate(assignments):
            if (assignment >> input_index) & 1:
                packed[row_index >> 3] |= 1 << (row_index & 7)
        columns[input_name] = int.from_bytes(packed, "little")
    identity = {
        "schema": "tc-packed-domain-v1",
        "name": name,
        "inputs": list(names),
        "row_count": rows,
        "constraint": constraint,
        "columns": {
            input_name: sha256(mask_bytes(columns[input_name], byte_count)).hexdigest()
            for input_name in names
        },
    }
    return Domain(
        name=name,
        inputs=names,
        assignments=tuple(assignments),
        columns=columns,
        row_count=rows,
        mask=(1 << rows) - 1,
        byte_count=byte_count,
        domain_id=sha256(canonical_json(identity)).hexdigest(),
        constraint=constraint,
    )


@dataclass(frozen=True, slots=True)
class Signal:
    value: int
    driven: int
    conflict: int
    arrival: int
    arcs: tuple[tuple[str, int], ...]
    owners: frozenset[str]
    expression: str

    def arc_dict(self) -> dict[str, int]:
        return dict(self.arcs)


def source_signal(domain: Domain, name: str) -> Signal:
    return Signal(
        value=domain.columns[name],
        driven=domain.mask,
        conflict=0,
        arrival=0,
        arcs=((name, 0),),
        owners=frozenset(),
        expression=name,
    )


def constant_signal(domain: Domain, value: bool) -> Signal:
    return Signal(
        value=domain.mask if value else 0,
        driven=domain.mask,
        conflict=0,
        arrival=0,
        arcs=(),
        owners=frozenset(),
        expression="1" if value else "0",
    )


def combine_arcs(signals: Iterable[Signal], extra: int) -> tuple[tuple[str, int], ...]:
    result: dict[str, int] = {}
    for signal in signals:
        for name, depth in signal.arcs:
            result[name] = max(result.get(name, -1), depth + extra)
    return tuple(sorted(result.items()))


def ordinary_signal(
    domain: Domain,
    kind: str,
    left: Signal,
    right: Signal | None,
    owner: str,
    cost: int = 1,
    delay: int = 1,
) -> Signal:
    register_owner(owner, cost)
    lv = left.value
    rv = left.value if right is None else right.value
    if kind == "NOT":
        value = ~lv
        inputs = (left,)
        expression = f"NOT({left.expression})"
    elif kind == "AND":
        value = lv & rv
        inputs = (left, right)
        expression = f"AND({left.expression},{right.expression})"
    elif kind == "OR":
        value = lv | rv
        inputs = (left, right)
        expression = f"OR({left.expression},{right.expression})"
    elif kind == "NAND":
        value = ~(lv & rv)
        inputs = (left, right)
        expression = f"NAND({left.expression},{right.expression})"
    elif kind == "NOR":
        value = ~(lv | rv)
        inputs = (left, right)
        expression = f"NOR({left.expression},{right.expression})"
    elif kind == "XOR":
        value = lv ^ rv
        inputs = (left, right)
        expression = f"XOR({left.expression},{right.expression})"
    elif kind == "XNOR":
        value = ~(lv ^ rv)
        inputs = (left, right)
        expression = f"XNOR({left.expression},{right.expression})"
    else:
        raise ValueError(kind)
    concrete_inputs = tuple(item for item in inputs if item is not None)
    conflict = 0
    for item in concrete_inputs:
        conflict |= item.conflict
    return Signal(
        value=value & domain.mask,
        driven=domain.mask,
        conflict=conflict,
        arrival=max(item.arrival for item in concrete_inputs) + delay,
        arcs=combine_arcs(concrete_inputs, delay),
        owners=frozenset({owner}).union(*(item.owners for item in concrete_inputs)),
        expression=expression,
    )


def switch_signal(
    domain: Domain,
    enable: Signal,
    data: Signal,
    owner: str,
    cost: int = 2,
    delay: int = 1,
) -> Signal:
    """TC Switch: value=e&d, driven=e; an undriven input is read as zero."""

    register_owner(owner, cost)
    return Signal(
        value=(enable.value & data.value) & domain.mask,
        driven=enable.value & domain.mask,
        conflict=(enable.conflict | data.conflict) & domain.mask,
        arrival=max(enable.arrival, data.arrival) + delay,
        arcs=combine_arcs((enable, data), delay),
        owners=frozenset({owner}).union(enable.owners, data.owners),
        expression=f"SW({enable.expression},{data.expression})",
    )


def resolve_bus(domain: Domain, drivers: Sequence[Signal], expression: str) -> Signal:
    ones = 0
    zeros = 0
    driven = 0
    conflict = 0
    owners: frozenset[str] = frozenset()
    for driver in drivers:
        active = driver.driven & domain.mask
        ones |= active & driver.value
        zeros |= active & (~driver.value & domain.mask)
        driven |= active
        conflict |= driver.conflict
        owners = owners.union(driver.owners)
    conflict |= ones & zeros
    return Signal(
        value=ones & domain.mask,
        driven=driven & domain.mask,
        conflict=conflict & domain.mask,
        arrival=max((driver.arrival for driver in drivers), default=0),
        arcs=combine_arcs(drivers, 0),
        owners=owners,
        expression=expression,
    )


def native_signal(
    domain: Domain,
    value: int,
    inputs: Sequence[str],
    owner: str,
    cost: int,
    delay: int,
    expression: str,
    driven: int | None = None,
) -> Signal:
    register_owner(owner, cost)
    return Signal(
        value=value & domain.mask,
        driven=domain.mask if driven is None else driven & domain.mask,
        conflict=0,
        arrival=delay,
        arcs=tuple(sorted((name, delay) for name in inputs)),
        owners=frozenset({owner}),
        expression=expression,
    )


def cofactor_mask(domain: Domain, target: int, variable: str, fixed: int) -> int:
    index = domain.inputs.index(variable)
    assignment_to_row = {
        assignment: row for row, assignment in enumerate(domain.assignments)
    }
    result = 0
    for output_row, assignment in enumerate(domain.assignments):
        selected = (assignment & ~(1 << index)) | (fixed << index)
        source_row = assignment_to_row[selected]
        result |= ((target >> source_row) & 1) << output_row
    return result


def add_label(mapping: dict[int, set[str]], value: int, label: str) -> None:
    mapping[value].add(label)


def local_labels(domain: Domain) -> dict[int, set[str]]:
    labels: dict[int, set[str]] = defaultdict(set)
    add_label(labels, 0, "CONST0")
    add_label(labels, domain.mask, "CONST1")
    for name in domain.inputs:
        value = domain.columns[name]
        add_label(labels, value, name)
        add_label(labels, (~value) & domain.mask, f"~{name}")
    if domain.inputs == ("A", "B"):
        a, b = (domain.columns[name] for name in domain.inputs)
        functions = {
            "G=AND(A,B)": a & b,
            "K=NOR(A,B)": ~(a | b),
            "V=OR(A,B)": a | b,
            "N=NAND(A,B)": ~(a & b),
            "P=XOR(A,B)": a ^ b,
            "Q=XNOR(A,B)": ~(a ^ b),
        }
        for label, value in functions.items():
            add_label(labels, value & domain.mask, label)
        for target_name, target in functions.items():
            for variable in domain.inputs:
                for fixed in (0, 1):
                    add_label(
                        labels,
                        cofactor_mask(domain, target & domain.mask, variable, fixed),
                        f"cofactor:{target_name}|{variable}={fixed}",
                    )
    if domain.inputs == ("A", "B", "C"):
        cols = domain.columns
        for left, right in itertools.combinations(domain.inputs, 2):
            x, y = cols[left], cols[right]
            pair = {
                f"G_{left}{right}": x & y,
                f"K_{left}{right}": ~(x | y),
                f"V_{left}{right}": x | y,
                f"N_{left}{right}": ~(x & y),
                f"P_{left}{right}": x ^ y,
                f"Q_{left}{right}": ~(x ^ y),
            }
            for label, value in pair.items():
                add_label(labels, value & domain.mask, label)
        a, b, c = (cols[name] for name in domain.inputs)
        functions = {
            "AND3": a & b & c,
            "OR3": a | b | c,
            "NAND3": ~(a & b & c),
            "NOR3": ~(a | b | c),
            "SUM=PARITY3": a ^ b ^ c,
            "XNOR3": ~(a ^ b ^ c),
            "CARRY=MAJORITY3": (a & b) | (a & c) | (b & c),
            "CARRYBAR=~MAJORITY3": ~((a & b) | (a & c) | (b & c)),
        }
        for label, value in functions.items():
            add_label(labels, value & domain.mask, label)
        for target_name, target in functions.items():
            for variable in domain.inputs:
                for fixed in (0, 1):
                    add_label(
                        labels,
                        cofactor_mask(domain, target & domain.mask, variable, fixed),
                        f"cofactor:{target_name}|{variable}={fixed}",
                    )
    return labels


class Catalog:
    def __init__(self) -> None:
        self.domains: dict[str, dict[str, object]] = {}
        self.labels: dict[str, dict[int, set[str]]] = {}
        self.masks: dict[str, dict[str, object]] = {}
        self.owner_sets: dict[str, dict[str, object]] = {}
        self.truths: dict[str, dict[str, object]] = {}
        self.producer_ids: set[str] = set()

    def register_domain(
        self, domain: Domain, labels: dict[int, set[str]] | None = None
    ) -> None:
        input_masks = {
            name: self.store_mask(domain, value)
            for name, value in domain.columns.items()
        }
        self.domains[domain.domain_id] = {
            "name": domain.name,
            "inputs": list(domain.inputs),
            "row_count": domain.row_count,
            "byte_count": domain.byte_count,
            "constraint": domain.constraint,
            "input_mask_sha256": input_masks,
        }
        self.labels[domain.domain_id] = labels or {}

    def store_mask(self, domain: Domain, value: int) -> str:
        packed = mask_bytes(value & domain.mask, domain.byte_count)
        digest = sha256(
            b"tc-packed-mask-v1\0"
            + domain.row_count.to_bytes(8, "little")
            + packed
        ).hexdigest()
        self.masks.setdefault(
            digest,
            {
                "row_count": domain.row_count,
                "byte_count": domain.byte_count,
                "ones": (value & domain.mask).bit_count(),
                "little_endian_base64": base64.b64encode(packed).decode("ascii"),
            },
        )
        return digest

    def store_owner_set(self, owners: frozenset[str]) -> str:
        ordered = sorted(owners)
        digest = sha256(canonical_json(ordered)).hexdigest()
        self.owner_sets.setdefault(
            digest,
            {
                "owners": ordered,
                "owner_count": len(ordered),
                "gate": owner_gate(ordered),
            },
        )
        return digest

    def add(
        self,
        domain: Domain,
        signal: Signal,
        producer_id: str,
        source_kind: str,
        role: str,
        physical_owner: str | None,
        incremental_gate: int,
        expansion_id: str | None = None,
        explicit_labels: Iterable[str] = (),
        metadata: dict[str, object] | None = None,
    ) -> str:
        if producer_id in self.producer_ids:
            raise RuntimeError(f"duplicate producer id: {producer_id}")
        self.producer_ids.add(producer_id)
        value_sha = self.store_mask(domain, signal.value)
        driven_sha = self.store_mask(domain, signal.driven)
        conflict_sha = self.store_mask(domain, signal.conflict)
        identity = {
            "schema": "tc-physical-truth-v1",
            "domain_id": domain.domain_id,
            "value_mask_sha256": value_sha,
            "driven_mask_sha256": driven_sha,
            "conflict_mask_sha256": conflict_sha,
        }
        truth_sha = sha256(canonical_json(identity)).hexdigest()
        boolean_sha = sha256(
            canonical_json(
                {
                    "schema": "tc-boolean-projection-v1",
                    "domain_id": domain.domain_id,
                    "value_mask_sha256": value_sha,
                }
            )
        ).hexdigest()
        labels = set(explicit_labels)
        labels.update(self.labels.get(domain.domain_id, {}).get(signal.value, set()))
        record = self.truths.setdefault(
            truth_sha,
            {
                **identity,
                "truth_sha256": truth_sha,
                "boolean_projection_sha256": boolean_sha,
                "fully_driven": signal.driven == domain.mask,
                "conflict_free": signal.conflict == 0,
                "labels": set(),
                "producers": [],
            },
        )
        record["labels"].update(labels)
        owner_set_sha = self.store_owner_set(signal.owners)
        record["producers"].append(
            {
                "producer_id": producer_id,
                "source_kind": source_kind,
                "role": role,
                "expansion_id": expansion_id,
                "gate": owner_gate(signal.owners),
                "delay": signal.arrival,
                "owner_set_sha256": owner_set_sha,
                "owner_count": len(signal.owners),
                "physical_owner": physical_owner,
                "incremental_gate": incremental_gate,
                "input_arc_depths": dict(signal.arcs),
                "expression": signal.expression,
                "metadata": metadata or {},
            }
        )
        return truth_sha

    def add_labels(self, truth_sha: str, labels: Iterable[str]) -> None:
        self.truths[truth_sha]["labels"].update(labels)

    def finalized_truths(self) -> list[dict[str, object]]:
        result = []
        for truth_sha in sorted(self.truths):
            row = self.truths[truth_sha]
            producers = sorted(row["producers"], key=lambda item: item["producer_id"])
            points: dict[tuple[int, int, int], list[str]] = defaultdict(list)
            point_owner_sets: dict[tuple[int, int, int], set[str]] = defaultdict(set)
            point_physical_owners: dict[tuple[int, int, int], set[str]] = defaultdict(set)
            for producer in producers:
                metric = (
                    int(producer["gate"]),
                    int(producer["delay"]),
                    int(producer["owner_count"]),
                )
                points[metric].append(str(producer["producer_id"]))
                point_owner_sets[metric].add(str(producer["owner_set_sha256"]))
                if producer["physical_owner"] is not None:
                    point_physical_owners[metric].add(str(producer["physical_owner"]))
            frontier = []
            for metric in sorted(points):
                if any(
                    other[0] <= metric[0]
                    and other[1] <= metric[1]
                    and other[2] <= metric[2]
                    and other != metric
                    for other in points
                ):
                    continue
                frontier.append(
                    {
                        "gate": metric[0],
                        "delay": metric[1],
                        "owner_count": metric[2],
                        "producer_ids": sorted(points[metric]),
                        "owner_set_sha256s": sorted(point_owner_sets[metric]),
                        "physical_owners": sorted(point_physical_owners[metric]),
                    }
                )
            result.append(
                {
                    **{key: value for key, value in row.items() if key != "producers"},
                    "labels": sorted(row["labels"]),
                    "producer_count": len(producers),
                    "pareto_gate_delay_owners": frontier,
                    "producers": producers,
                }
            )
        return result


@dataclass(frozen=True, slots=True)
class MiniSignal:
    value: int
    arcs: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class MiniOp:
    kind: str
    left: int
    right: int


def mini_apply(
    kind: str, left: MiniSignal, right: MiniSignal, mask: int
) -> MiniSignal:
    if kind == "NOT":
        value = ~left.value
        source_arcs = (left.arcs,)
    elif kind == "AND":
        value = left.value & right.value
        source_arcs = (left.arcs, right.arcs)
    elif kind == "OR":
        value = left.value | right.value
        source_arcs = (left.arcs, right.arcs)
    elif kind == "NAND":
        value = ~(left.value & right.value)
        source_arcs = (left.arcs, right.arcs)
    elif kind == "NOR":
        value = ~(left.value | right.value)
        source_arcs = (left.arcs, right.arcs)
    else:
        raise ValueError(kind)
    arcs = []
    for index in range(len(left.arcs)):
        paths = [row[index] for row in source_arcs if row[index] >= 0]
        arcs.append(max(paths) + 1 if paths else -1)
    return MiniSignal(value & mask, tuple(arcs))


def all_gates_live(ops: Sequence[MiniOp], source_count: int) -> bool:
    needed = {source_count + len(ops) - 1}
    for slot in range(len(ops) - 1, -1, -1):
        absolute = source_count + slot
        if absolute not in needed:
            return False
        op = ops[slot]
        if op.left >= source_count:
            needed.add(op.left)
        if op.kind != "NOT" and op.right >= source_count:
            needed.add(op.right)
    return True


def enumerate_minimal_classes(
    domain: Domain, target: int, gates: int
) -> dict[str, object]:
    base = [
        MiniSignal(domain.columns[name], tuple(0 if name == item else -1 for item in domain.inputs))
        for name in domain.inputs
    ]
    base.extend(
        [
            MiniSignal(0, tuple(-1 for _ in domain.inputs)),
            MiniSignal(domain.mask, tuple(-1 for _ in domain.inputs)),
        ]
    )
    source_count = len(base)
    classes: dict[tuple[object, ...], dict[str, object]] = {}
    raw_count = 0
    stream = sha256()

    def visit(values: list[MiniSignal], ops: list[MiniOp]) -> None:
        nonlocal raw_count
        if len(ops) == gates:
            if values[-1].value != target or not all_gates_live(ops, source_count):
                return
            raw_count += 1
            signature = tuple((op.kind, op.left, op.right) for op in ops)
            stream.update(canonical_json(signature) + b"\n")
            internal = values[source_count:]
            key = (
                tuple(sorted((item.value, item.arcs) for item in internal[:-1])),
                internal[-1].arcs,
            )
            row = classes.setdefault(
                key,
                {
                    "representative": [
                        {"kind": op.kind, "left": op.left, "right": op.right}
                        for op in ops
                    ],
                    "structure_count": 0,
                    "internal_semantics": [
                        {
                            "truth_hex": hex(item.value),
                            "input_arc_depths": {
                                name: depth
                                for name, depth in zip(domain.inputs, item.arcs, strict=True)
                                if depth >= 0
                            },
                        }
                        for item in internal
                    ],
                },
            )
            row["structure_count"] = int(row["structure_count"]) + 1
            return

        available = len(values)
        for left in range(available):
            op = MiniOp("NOT", left, left)
            visit(values + [mini_apply("NOT", values[left], values[left], domain.mask)], ops + [op])
        for kind in ORDINARY[1:]:
            for left in range(available):
                for right in range(left, available):
                    op = MiniOp(kind, left, right)
                    visit(
                        values + [mini_apply(kind, values[left], values[right], domain.mask)],
                        ops + [op],
                    )

    visit(base, [])
    return {
        "gates": gates,
        "raw_live_structure_count": raw_count,
        "semantic_arc_class_count": len(classes),
        "deterministic_structure_stream_sha256": stream.hexdigest(),
        "classes": list(classes.values()),
        "source_count": source_count,
    }


def instantiate_enumerated_classes(
    catalog: Catalog,
    domain: Domain,
    component: str,
    census: dict[str, object],
) -> list[dict[str, object]]:
    rows = []
    source_count = int(census["source_count"])
    for class_index, item in enumerate(census["classes"]):
        expansion_id = f"exhaustive:{component}:class{class_index:04d}"
        values = [source_signal(domain, name) for name in domain.inputs]
        values.extend((constant_signal(domain, False), constant_signal(domain, True)))
        truth_ids = []
        operations = list(item["representative"])
        for slot, operation in enumerate(operations):
            kind = str(operation["kind"])
            left_index = int(operation["left"])
            right_index = int(operation["right"])
            right = None if kind == "NOT" else values[right_index]
            owner = f"{expansion_id}:gate{slot}"
            signal = ordinary_signal(domain, kind, values[left_index], right, owner)
            values.append(signal)
            truth_ids.append(
                catalog.add(
                    domain,
                    signal,
                    producer_id=f"{expansion_id}:node{slot}",
                    source_kind="ordinary-minimal-enumeration",
                    role="main" if slot == len(operations) - 1 else "byproduct",
                    physical_owner=owner,
                    incremental_gate=1,
                    expansion_id=expansion_id,
                    metadata={"component": component, "class_index": class_index},
                )
            )
        if len(values) != source_count + len(operations):
            raise RuntimeError("enumerated source count changed")
        rows.append(
            {
                "expansion_id": expansion_id,
                "structure_count": item["structure_count"],
                "operations": operations,
                "truth_sha256s": truth_ids,
            }
        )
    return rows


class ExplicitExpansion:
    def __init__(
        self, catalog: Catalog, domain: Domain, expansion_id: str, component: str
    ) -> None:
        self.catalog = catalog
        self.domain = domain
        self.expansion_id = expansion_id
        self.component = component
        self.values: dict[str, Signal] = {
            name: source_signal(domain, name) for name in domain.inputs
        }
        self.values["0"] = constant_signal(domain, False)
        self.values["1"] = constant_signal(domain, True)
        self.nodes: list[dict[str, object]] = []

    def gate(self, name: str, kind: str, left: str, right: str | None = None) -> str:
        owner = f"{self.expansion_id}:{name}"
        signal = ordinary_signal(
            self.domain,
            kind,
            self.values[left],
            None if right is None else self.values[right],
            owner,
        )
        self.values[name] = signal
        self.nodes.append(
            {
                "name": name,
                "kind": kind,
                "left": left,
                "right": right,
                "owner": owner,
            }
        )
        return name

    def register(self, outputs: Sequence[str]) -> dict[str, object]:
        truth_ids = []
        output_set = set(outputs)
        for slot, node in enumerate(self.nodes):
            name = str(node["name"])
            truth_ids.append(
                self.catalog.add(
                    self.domain,
                    self.values[name],
                    producer_id=f"{self.expansion_id}:{name}",
                    source_kind="explicit-minimal-expansion",
                    role="main" if name in output_set else "byproduct",
                    physical_owner=str(node["owner"]),
                    incremental_gate=1,
                    expansion_id=self.expansion_id,
                    explicit_labels=(name,),
                    metadata={"component": self.component, "slot": slot},
                )
            )
        return {
            "expansion_id": self.expansion_id,
            "component": self.component,
            "outputs": list(outputs),
            "gate": len(self.nodes),
            "delay": max(self.values[name].arrival for name in outputs),
            "nodes": self.nodes,
            "truth_sha256s": truth_ids,
            "output_arc_depths": {
                name: dict(self.values[name].arcs) for name in outputs
            },
        }


def build_explicit_library(
    catalog: Catalog, bit2: Domain, bit3: Domain
) -> list[dict[str, object]]:
    result = []

    # Ordinary one-gate minima, including all equal-cost NOT aliases.
    for alias, kind in (("not", "NOT"), ("nand-self", "NAND"), ("nor-self", "NOR")):
        cell = ExplicitExpansion(catalog, bit2, f"NOT:{alias}", "NOT")
        cell.gate("OUT", kind, "A", None if kind == "NOT" else "A")
        result.append(cell.register(("OUT",)))
    for component in ("AND", "OR", "NAND", "NOR"):
        cell = ExplicitExpansion(catalog, bit2, f"{component}:native", component)
        cell.gate("OUT", component, "A", "B")
        result.append(cell.register(("OUT",)))

    # Required two-phase XOR and XNOR seeds.
    for target in ("XOR", "XNOR"):
        cell = ExplicitExpansion(catalog, bit2, f"{target}:GKP", target)
        cell.gate("G", "AND", "A", "B")
        cell.gate("K", "NOR", "A", "B")
        cell.gate("P" if target == "XOR" else "Q", "NOR" if target == "XOR" else "OR", "G", "K")
        result.append(cell.register(("P" if target == "XOR" else "Q",)))

        cell = ExplicitExpansion(catalog, bit2, f"{target}:VNP", target)
        cell.gate("V", "OR", "A", "B")
        cell.gate("N", "NAND", "A", "B")
        cell.gate("P" if target == "XOR" else "Q", "AND" if target == "XOR" else "NAND", "V", "N")
        result.append(cell.register(("P" if target == "XOR" else "Q",)))

    # Every choice of the short-arc third input for the two-gate AND3/OR3 tree.
    for component in ("AND3", "OR3"):
        kind = component[:-1]
        for pair in itertools.combinations(bit3.inputs, 2):
            third = next(name for name in bit3.inputs if name not in pair)
            cell = ExplicitExpansion(
                catalog,
                bit3,
                f"{component}:pair-{pair[0]}{pair[1]}",
                component,
            )
            cell.gate("PAIR", kind, pair[0], pair[1])
            cell.gate("OUT", kind, "PAIR", third)
            result.append(cell.register(("OUT",)))

    # Seven-gate full-adder families.  Pair selection exposes the late-input
    # two-gate short arc.  Positive and inverse carry variants have equal cost.
    for pair in itertools.combinations(bit3.inputs, 2):
        late = next(name for name in bit3.inputs if name not in pair)
        pair_tag = "".join(pair)
        for carry_polarity in ("carry", "carrybar"):
            cell = ExplicitExpansion(
                catalog,
                bit3,
                f"FullAdder:GKP:{pair_tag}:{carry_polarity}",
                "FullAdder",
            )
            cell.gate("G", "AND", pair[0], pair[1])
            cell.gate("K", "NOR", pair[0], pair[1])
            cell.gate("P", "NOR", "G", "K")
            cell.gate("T", "AND", "P", late)
            cell.gate("N", "NOR", "P", late)
            cell.gate("SUM", "NOR", "T", "N")
            cell.gate(
                "CARRY" if carry_polarity == "carry" else "CARRYBAR",
                "OR" if carry_polarity == "carry" else "NAND",
                "G",
                "T",
            )
            result.append(
                cell.register(
                    (
                        "SUM",
                        "CARRY" if carry_polarity == "carry" else "CARRYBAR",
                    )
                )
            )

            cell = ExplicitExpansion(
                catalog,
                bit3,
                f"FullAdder:VNP:{pair_tag}:{carry_polarity}",
                "FullAdder",
            )
            cell.gate("V", "OR", pair[0], pair[1])
            cell.gate("N", "NAND", pair[0], pair[1])
            cell.gate("P", "AND", "V", "N")
            cell.gate("NT", "NAND", "P", late)
            cell.gate("W", "OR", "P", late)
            cell.gate("SUM", "AND", "W", "NT")
            cell.gate(
                "CARRY" if carry_polarity == "carry" else "CARRYBAR",
                "NAND" if carry_polarity == "carry" else "AND",
                "N",
                "NT",
            )
            result.append(
                cell.register(
                    (
                        "SUM",
                        "CARRY" if carry_polarity == "carry" else "CARRYBAR",
                    )
                )
            )
    return result


def add_native_profiles(
    catalog: Catalog, bit2: Domain, bit3: Domain, switch_domain: Domain
) -> list[dict[str, object]]:
    profiles = {
        "campaign_imported": {
            "NOT": (1, 1),
            "AND": (1, 1),
            "OR": (1, 1),
            "NAND": (1, 1),
            "NOR": (1, 1),
            "XOR": (3, 2),
            "XNOR": (5, 4),
            "AND3": (3, 2),
            "OR3": (3, 2),
            "Switch": (2, 1),
            "FullAdder": (16, 8),
        },
        "runtime_default_2_1_292": {
            "NOT": (1, 1),
            "AND": (1, 1),
            "OR": (1, 1),
            "NAND": (1, 1),
            "NOR": (1, 1),
            "XOR": (4, 3),
            "XNOR": (4, 3),
            "AND3": (2, 2),
            "OR3": (2, 2),
            "Switch": (2, 1),
            "FullAdder": (8, 4),
        },
    }
    rows = []
    a, b = bit2.columns["A"], bit2.columns["B"]
    a3, b3, c3 = (bit3.columns[name] for name in bit3.inputs)
    bit2_values = {
        "NOT": ~a,
        "AND": a & b,
        "OR": a | b,
        "NAND": ~(a & b),
        "NOR": ~(a | b),
        "XOR": a ^ b,
        "XNOR": ~(a ^ b),
    }
    bit3_values = {
        "AND3": a3 & b3 & c3,
        "OR3": a3 | b3 | c3,
        "SUM": a3 ^ b3 ^ c3,
        "CARRY": (a3 & b3) | (a3 & c3) | (b3 & c3),
    }
    for profile_name, profile in profiles.items():
        for component, (gate, delay) in profile.items():
            owner = f"native:{profile_name}:{component}"
            if component in bit2_values:
                signal = native_signal(
                    bit2,
                    bit2_values[component],
                    ("A",) if component == "NOT" else ("A", "B"),
                    owner,
                    gate,
                    delay,
                    f"native-{component}",
                )
                truth_ids = [
                    catalog.add(
                        bit2,
                        signal,
                        producer_id=owner,
                        source_kind="native-component-score-profile",
                        role="main",
                        physical_owner=owner,
                        incremental_gate=gate,
                        expansion_id=owner,
                        metadata={"profile": profile_name, "component": component},
                    )
                ]
            elif component in ("AND3", "OR3"):
                signal = native_signal(
                    bit3,
                    bit3_values[component],
                    bit3.inputs,
                    owner,
                    gate,
                    delay,
                    f"native-{component}",
                )
                truth_ids = [
                    catalog.add(
                        bit3,
                        signal,
                        producer_id=owner,
                        source_kind="native-component-score-profile",
                        role="main",
                        physical_owner=owner,
                        incremental_gate=gate,
                        expansion_id=owner,
                        metadata={"profile": profile_name, "component": component},
                    )
                ]
            elif component == "Switch":
                e = source_signal(switch_domain, "E")
                d = source_signal(switch_domain, "D")
                signal = switch_signal(switch_domain, e, d, owner, gate, delay)
                truth_ids = [
                    catalog.add(
                        switch_domain,
                        signal,
                        producer_id=owner,
                        source_kind="native-component-score-profile",
                        role="partial-driver-main",
                        physical_owner=owner,
                        incremental_gate=gate,
                        expansion_id=owner,
                        explicit_labels=("SW(E,D)",),
                        metadata={"profile": profile_name, "component": component},
                    )
                ]
            else:
                truth_ids = []
                for output_name in ("SUM", "CARRY"):
                    signal = native_signal(
                        bit3,
                        bit3_values[output_name],
                        bit3.inputs,
                        owner,
                        gate,
                        delay,
                        f"native-FullAdder.{output_name}",
                    )
                    truth_ids.append(
                        catalog.add(
                            bit3,
                            signal,
                            producer_id=f"{owner}:{output_name}",
                            source_kind="native-component-score-profile",
                            role="main",
                            physical_owner=owner,
                            incremental_gate=gate,
                            expansion_id=owner,
                            explicit_labels=(output_name,),
                            metadata={"profile": profile_name, "component": component},
                        )
                    )
            rows.append(
                {
                    "profile": profile_name,
                    "component": component,
                    "gate": gate,
                    "delay": delay,
                    "truth_sha256s": truth_ids,
                }
            )
    return rows


def add_switch_bus_library(
    catalog: Catalog, switch_domain: Domain, bus_domain: Domain, onehot_domain: Domain
) -> list[dict[str, object]]:
    rows = []
    e = source_signal(switch_domain, "E")
    d = source_signal(switch_domain, "D")
    sw = switch_signal(switch_domain, e, d, "Switch:physical")
    sw_truth = catalog.add(
        switch_domain,
        sw,
        "Switch:physical:driver",
        "switch-physical-expansion",
        "partial-driver-main",
        "Switch:physical",
        2,
        "Switch:physical",
        ("SW(E,D)", "partial-driver"),
    )
    boolean = ordinary_signal(switch_domain, "AND", e, d, "Switch:boolean-AND")
    boolean_truth = catalog.add(
        switch_domain,
        boolean,
        "Switch:boolean-AND:out",
        "switch-boolean-projection-only",
        "boolean-main",
        "Switch:boolean-AND",
        1,
        "Switch:boolean-AND",
        ("E&D", "fully-driven"),
    )
    rows.append(
        {
            "name": "single-bit-switch-vs-boolean-and",
            "physical_truth_sha256": sw_truth,
            "boolean_and_truth_sha256": boolean_truth,
            "same_boolean_value": sw.value == boolean.value,
            "same_physical_truth": sw.driven == boolean.driven,
            "conclusion": "AND is cheaper only when Z/driven behavior is irrelevant",
        }
    )

    def bus_case(domain: Domain, tag: str) -> dict[str, object]:
        signals = {name: source_signal(domain, name) for name in domain.inputs}
        left = switch_signal(domain, signals["E0"], signals["D0"], f"{tag}:sw0")
        right = switch_signal(domain, signals["E1"], signals["D1"], f"{tag}:sw1")
        left_sha = catalog.add(
            domain,
            left,
            f"{tag}:driver0",
            "switch-bus-expansion",
            "partial-driver",
            f"{tag}:sw0",
            2,
            tag,
            ("driver0",),
            {"resolved_network_owner": f"{tag}:bus", "driver_index": 0},
        )
        right_sha = catalog.add(
            domain,
            right,
            f"{tag}:driver1",
            "switch-bus-expansion",
            "partial-driver",
            f"{tag}:sw1",
            2,
            tag,
            ("driver1",),
            {"resolved_network_owner": f"{tag}:bus", "driver_index": 1},
        )
        bus = resolve_bus(domain, (left, right), "BUS(SW(E0,D0),SW(E1,D1))")
        bus_sha = catalog.add(
            domain,
            bus,
            f"{tag}:bus",
            "resolved-multidriver-bus",
            "resolved-bus-main",
            f"{tag}:bus",
            0,
            tag,
            ("free-resolved-OR-of-driver-ones",),
        )
        return {
            "name": tag,
            "domain": domain.name,
            "drivers": [left_sha, right_sha],
            "bus": bus_sha,
            "gate": 4,
            "delay": 1,
            "conflict_rows": bus.conflict.bit_count(),
            "undriven_rows": domain.row_count - bus.driven.bit_count(),
            "free_resolution": True,
        }

    rows.append(bus_case(bus_domain, "BUS:unrestricted-two-driver"))
    rows.append(bus_case(onehot_domain, "BUS:mutually-exclusive-two-driver"))
    return rows


def load_advanced_library():
    spec = importlib.util.spec_from_file_location(
        "byproduct_advanced_library", ADVANCED_LIBRARY_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ADVANCED_LIBRARY_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def exact_full_adder_proof(timeout_ms: int) -> dict[str, object]:
    advanced = load_advanced_library()
    rows = []
    for a, b, c in itertools.product((0, 1), repeat=3):
        rows.append({"A": a, "B": b, "C": c})
    domain = advanced.Domain("full-adder-3-input", ("A", "B", "C"), tuple(rows))
    sum_target = domain.target(lambda row: row["A"] ^ row["B"] ^ row["C"])
    carry_target = domain.target(
        lambda row: row["A"] + row["B"] + row["C"] >= 2
    )
    result = advanced.exact_ordinary(
        domain, (sum_target, carry_target), 4, 7, timeout_ms
    )
    if result.get("status") != "sat" or result.get("gate") != 7:
        raise RuntimeError(f"full-adder exact proof failed: {result}")
    result["interpretation"] = (
        "the solver checked gate counts 1..6 UNSAT before finding this 7-gate SAT witness"
    )
    result["scope"] = (
        "shared NOT/AND/OR/NAND/NOR DAG, free constants, both SUM and CARRY, delay<=4"
    )
    return result


def build_word_profiles() -> list[dict[str, object]]:
    bit_expansions = {
        "NOT": (1, 1),
        "AND": (1, 1),
        "OR": (1, 1),
        "NAND": (1, 1),
        "NOR": (1, 1),
        "XOR": (3, 2),
        "XNOR": (3, 2),
        "AND3": (2, 2),
        "OR3": (2, 2),
        "Switch": (2, 1),
        "FullAdder-parallel-lanes": (7, 4),
    }
    native_word_available = {"NOT", "NAND", "Switch"}
    rows = []
    for width in (1, 2, 4, 8):
        for component, (lane_gate, delay) in bit_expansions.items():
            rows.append(
                {
                    "component": component,
                    "width": width,
                    "lane_expansion_gate": lane_gate * width,
                    "delay": delay,
                    "lane_owner_count": width,
                    "native_word_available_before_byte_adder": component
                    in native_word_available,
                    "native_word_gate_if_available": (
                        2 * width if component == "Switch" else width
                    )
                    if component in native_word_available
                    else None,
                    "same_enable_group": component == "Switch",
                    "truth_representation": (
                        "bit template instantiated independently per lane; Maker/Splitter adaptation is 0/0"
                    ),
                }
            )
    rows.append(
        {
            "component": "FullAdder-ripple-word",
            "widths": [1, 2, 4, 8],
            "gate_formula": "7*w",
            "carry_out_delay_formula_all_inputs_at_0": "2*w+2",
            "late_carry_short_arc_per_stage": 2,
            "note": "G/K/P pair phase is precomputed; each carry input reaches SUM/CARRY through a two-gate short arc",
        }
    )
    rows.append(
        {
            "component": "free-maker-splitter",
            "widths": [2, 4, 8],
            "gate": 0,
            "delay": 0,
            "normal_signal_behavior": "free bundle/unbundle and fanout adaptation",
            "z_caveat": "Maker/Splitter adaptation reads undriven data as zero and restores a driven word; it is not a free independent tristate driver",
        }
    )
    return rows


def build_cost_models(cost_payload: dict[str, object], runtime: dict[str, object]) -> dict[str, object]:
    imported = {}
    for item in cost_payload["globally_unlocked_native_primitives"]:
        name = item["name"]
        if name in {
            "com_not_bit",
            "com_and_bit",
            "com_and_3_bit",
            "com_nand_bit",
            "com_or_bit",
            "com_or_3_bit",
            "com_nor_bit",
            "com_xor_bit",
            "com_xnor_bit",
            "com_switch_bit",
            "com_full_adder",
            "com_not_word",
            "com_nand_word",
            "com_switch_word",
            "com_splitter_bit_2",
            "com_splitter_bit_4",
            "com_splitter_bit_8",
            "com_maker_bit_2",
            "com_maker_bit_4",
            "com_maker_bit_8",
        }:
            imported[name] = {
                "kind": item["kind"],
                "cost_source": item["cost_source"],
                "costs": item["costs"],
            }
    runtime_rows = {
        int(item["kind"]): {
            "gate": int(item["default_gate"]),
            "delay": int(item["default_delay"]),
        }
        for item in runtime["score_table"]["rows"]
    }
    return {
        "campaign_imported_frontier_evidence": imported,
        "runtime_default_2_1_292_selected_kinds": {
            str(kind): runtime_rows[kind]
            for kind in (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18, 21, 25)
        },
        "evidence_rule": (
            "campaign imported scores govern an unlocked saved frontier; runtime defaults are retained separately and are not silently substituted"
        ),
    }


def arithmetic_labels(domain: Domain) -> dict[int, set[str]]:
    labels: dict[int, set[str]] = defaultdict(set)
    for name in domain.inputs:
        add_label(labels, domain.columns[name], name)
        add_label(labels, (~domain.columns[name]) & domain.mask, f"~{name}")
    carry = domain.columns["cin"]
    add_label(labels, carry, "C0")
    for bit in range(8):
        a = domain.columns[f"a{bit}"]
        b = domain.columns[f"b{bit}"]
        g = a & b
        k = ~(a | b) & domain.mask
        v = (a | b) & domain.mask
        n = ~(a & b) & domain.mask
        p = (a ^ b) & domain.mask
        q = (~p) & domain.mask
        t = p & carry
        sum_n = ~(p | carry) & domain.mask
        sum_v = (p | carry) & domain.mask
        next_carry = (g | t) & domain.mask
        sum_value = (p ^ carry) & domain.mask
        for label, value in {
            f"G{bit}": g,
            f"K{bit}": k,
            f"V{bit}": v,
            f"N{bit}": n,
            f"P{bit}": p,
            f"Q{bit}": q,
            f"T{bit}=P{bit}&C{bit}": t,
            f"sumN{bit}=NOR(P{bit},C{bit})": sum_n,
            f"sumV{bit}=OR(P{bit},C{bit})": sum_v,
            f"S{bit}": sum_value,
            f"C{bit + 1}": next_carry,
        }.items():
            add_label(labels, value, label)
        carry = next_carry
    return labels


def expected_adder_outputs(domain: Domain) -> tuple[int, ...]:
    values = [0] * 9
    for row, assignment in enumerate(domain.assignments):
        inputs = {
            name: (assignment >> index) & 1
            for index, name in enumerate(domain.inputs)
        }
        a = sum(inputs[f"a{bit}"] << bit for bit in range(8))
        b = sum(inputs[f"b{bit}"] << bit for bit in range(8))
        total = a + b + inputs["cin"]
        for bit in range(8):
            values[bit] |= ((total >> bit) & 1) << row
        values[8] |= ((total >> 8) & 1) << row
    return tuple(values)


def node_references(node: dict[str, object]) -> list[int]:
    if node["op"] == "INPUT":
        return []
    if node["op"] == "BUS":
        return [
            int(value)
            for driver in node["drivers"]
            for value in (driver["enable"], driver["data"])
        ]
    return [int(value) for value in node["args"]]


def replay_dag(
    domain: Domain,
    dag: dict[str, object],
    substitutions: dict[int, int] | None = None,
) -> dict[str, object]:
    substitutions = substitutions or {}
    nodes = {int(node["id"]): node for node in dag["nodes"]}

    def canonical(node_id: int) -> int:
        seen = set()
        while node_id in substitutions:
            if node_id in seen:
                raise RuntimeError("substitution cycle")
            seen.add(node_id)
            node_id = substitutions[node_id]
        return node_id

    outputs = [canonical(int(node_id)) for node_id in dag["outputs"]]
    reachable: set[int] = set()

    def visit(node_id: int) -> None:
        node_id = canonical(node_id)
        if node_id in reachable:
            return
        reachable.add(node_id)
        for reference in node_references(nodes[node_id]):
            visit(canonical(reference))

    for output in outputs:
        visit(output)

    signals: dict[int, Signal] = {}
    driver_signals: dict[tuple[int, int], Signal] = {}
    for node_id in sorted(reachable):
        node = nodes[node_id]
        op = str(node["op"])
        if op == "INPUT":
            signal = source_signal(domain, str(node["label"]))
        elif op == "BUS":
            drivers = []
            for index, driver in enumerate(node["drivers"]):
                enable = signals[canonical(int(driver["enable"]))]
                data = signals[canonical(int(driver["data"]))]
                driver_signal = switch_signal(
                    domain,
                    enable,
                    data,
                    f"80d7:bus{node_id}:switch{index}",
                )
                drivers.append(driver_signal)
                driver_signals[(node_id, index)] = driver_signal
            signal = resolve_bus(domain, drivers, f"BUS{node_id}")
        else:
            references = [canonical(value) for value in node_references(node)]
            left = signals[references[0]]
            right = None if op == "NOT" else signals[references[1]]
            signal = ordinary_signal(
                domain, op, left, right, f"80d7:node{node_id}", int(node["cost"]), int(node["step_delay"])
            )
        signals[node_id] = signal
        if not substitutions and signal.arrival != int(node["arrival"]):
            raise RuntimeError(
                f"arrival mismatch at node {node_id}: {signal.arrival} != {node['arrival']}"
            )
    output_signals = [signals[node_id] for node_id in outputs]
    expected = expected_adder_outputs(domain)
    mismatch_by_output = [
        (signal.value ^ target).bit_count()
        for signal, target in zip(output_signals, expected, strict=True)
    ]
    conflict_union = 0
    for node_id in reachable:
        conflict_union |= signals[node_id].conflict
    gate = sum(int(nodes[node_id]["cost"]) for node_id in reachable)
    serialized = {
        "outputs": outputs,
        "nodes": [
            {
                "id": node_id,
                "op": nodes[node_id]["op"],
                "args": [canonical(value) for value in node_references(nodes[node_id])],
                "cost": nodes[node_id]["cost"],
            }
            for node_id in sorted(reachable)
        ],
    }
    return {
        "signals": signals,
        "driver_signals": driver_signals,
        "reachable": reachable,
        "outputs": outputs,
        "gate": gate,
        "delay": max(signal.arrival for signal in output_signals),
        "mismatch_count_by_output": mismatch_by_output,
        "mismatch_union_count": sum(mismatch_by_output),
        "conflict_assignment_count": conflict_union.bit_count(),
        "z_assignment_count_by_output": [
            (domain.mask & ~signal.driven).bit_count() for signal in output_signals
        ],
        "structural_sha256": sha256(canonical_json(serialized)).hexdigest(),
    }


def add_current_dag(
    catalog: Catalog, domain: Domain, payload: dict[str, object]
) -> tuple[dict[str, object], dict[int, str]]:
    dag = payload["factory_dag"]
    replay = replay_dag(domain, dag)
    if replay["gate"] != 80 or replay["delay"] != 7:
        raise RuntimeError("80/7 metric replay failed")
    if replay["mismatch_union_count"] or replay["conflict_assignment_count"]:
        raise RuntimeError("80/7 full-domain replay failed")
    if any(replay["z_assignment_count_by_output"]):
        raise RuntimeError("80/7 output is undriven")
    node_truths: dict[int, str] = {}
    node_map = {int(node["id"]): node for node in dag["nodes"]}
    for node_id in sorted(replay["reachable"]):
        node = node_map[node_id]
        signal = replay["signals"][node_id]
        truth_sha = catalog.add(
            domain,
            signal,
            producer_id=f"80d7:node:{node_id}",
            source_kind="verified-80d7-node",
            role="primary-output" if node_id in replay["outputs"] else "intermediate",
            physical_owner=(
                str(node.get("resolved_network"))
                if node["op"] == "BUS"
                else (None if node["op"] == "INPUT" else f"node_{node_id}")
            ),
            incremental_gate=int(node["cost"]),
            expansion_id="verified-80d7",
            explicit_labels=(str(node.get("label", "")),) if node.get("label") else (),
            metadata={
                "node_id": node_id,
                "op": node["op"],
                "args": node["args"],
                "may_z": bool(node["may_z"]),
            },
        )
        node_truths[node_id] = truth_sha
    for (node_id, index), signal in sorted(replay["driver_signals"].items()):
        node = node_map[node_id]
        catalog.add(
            domain,
            signal,
            producer_id=f"80d7:bus:{node_id}:driver:{index}",
            source_kind="verified-80d7-switch-driver",
            role="partial-driver",
            physical_owner=f"80d7:bus{node_id}:switch{index}",
            incremental_gate=2,
            expansion_id="verified-80d7",
            explicit_labels=(f"BUS{node_id}.driver{index}",),
            metadata={
                "node_id": node_id,
                "driver_index": index,
                "driver": node["drivers"][index],
                "resolved_network_owner": str(node["resolved_network"]),
            },
        )
    output_names = [f"S{bit}" for bit in range(8)] + ["C8"]
    for name, node_id in zip(output_names, replay["outputs"], strict=True):
        catalog.add_labels(node_truths[node_id], (name,))
    return (
        {
            "rows": domain.row_count,
            "gate": replay["gate"],
            "delay": replay["delay"],
            "mismatch_count_by_output": replay["mismatch_count_by_output"],
            "mismatch_union_count": replay["mismatch_union_count"],
            "conflict_assignment_count": replay["conflict_assignment_count"],
            "z_assignment_count_by_output": replay["z_assignment_count_by_output"],
            "source_structural_sha256": payload["metrics"]["structural_sha256"],
            "replay_structural_sha256": replay["structural_sha256"],
            "node_count": len(replay["signals"]),
            "switch_driver_count": len(replay["driver_signals"]),
        },
        node_truths,
    )


def same_args(node: dict[str, object], left: int, right: int) -> bool:
    return sorted(int(value) for value in node["args"]) == sorted((left, right))


def detect_patterns(
    catalog: Catalog,
    domain: Domain,
    dag: dict[str, object],
    replay: dict[str, object],
    node_truths: dict[int, str],
) -> list[dict[str, object]]:
    nodes = {int(node["id"]): node for node in dag["nodes"]}
    signals: dict[int, Signal] = replay["signals"]
    users: dict[int, list[int]] = defaultdict(list)
    for node_id, node in nodes.items():
        for reference in node_references(node):
            users[reference].append(node_id)
    patterns: list[dict[str, object]] = []
    xor_phases = []
    for node_id, node in nodes.items():
        if node["op"] not in {"NOR", "AND", "OR", "NAND"} or len(node["args"]) != 2:
            continue
        left_id, right_id = (int(value) for value in node["args"])
        left, right = nodes[left_id], nodes[right_id]
        candidates = [
            ("GKP-XOR", "NOR", {"AND", "NOR"}, "P"),
            ("GKP-XNOR", "OR", {"AND", "NOR"}, "Q"),
            ("VNP-XOR", "AND", {"OR", "NAND"}, "P"),
            ("VNP-XNOR", "NAND", {"OR", "NAND"}, "Q"),
        ]
        for family, final_op, pair_ops, main_label in candidates:
            if node["op"] != final_op or {left["op"], right["op"]} != pair_ops:
                continue
            if sorted(left["args"]) != sorted(right["args"]):
                continue
            input_ids = tuple(int(value) for value in left["args"])
            expected = (
                signals[input_ids[0]].value ^ signals[input_ids[1]].value
                if main_label == "P"
                else ~(signals[input_ids[0]].value ^ signals[input_ids[1]].value)
            ) & domain.mask
            mismatch = (signals[node_id].value ^ expected).bit_count()
            if mismatch:
                raise RuntimeError(f"detected phase mismatch at {node_id}")
            side_nodes = (left_id, right_id)
            external_users = {
                side: sorted(user for user in users[side] if user != node_id)
                for side in side_nodes
            }
            row = {
                "pattern": family,
                "input_nodes": list(input_ids),
                "sideproduct_nodes": list(side_nodes),
                "main_node": node_id,
                "current_gate": sum(int(nodes[item]["cost"]) for item in (*side_nodes, node_id)),
                "main_arrival": signals[node_id].arrival,
                "external_sideproduct_users": external_users,
                "native_collapse_preserves_live_sideproducts": not any(external_users.values()),
                "full_domain_rows": domain.row_count,
                "mismatch_count": mismatch,
                "truth_sha256s": [node_truths[item] for item in (*side_nodes, node_id)],
                "classification": "current DAG already contains a minimal primitive expansion",
            }
            patterns.append(row)
            xor_phases.append({**row, "phase_pair_nodes": side_nodes, "phase_main": node_id})

    # Same-operator two-gate trees expose all native AND3/OR3 dominance hits.
    for node_id, node in nodes.items():
        if node["op"] not in {"AND", "OR"}:
            continue
        for child_position, child_id in enumerate(int(value) for value in node["args"]):
            child = nodes[child_id]
            if child["op"] != node["op"]:
                continue
            third = int(node["args"][1 - child_position])
            input_ids = [int(value) for value in child["args"]] + [third]
            expected = signals[input_ids[0]].value
            for input_id in input_ids[1:]:
                expected = (
                    expected & signals[input_id].value
                    if node["op"] == "AND"
                    else expected | signals[input_id].value
                )
            mismatch = (signals[node_id].value ^ expected).bit_count()
            if mismatch:
                raise RuntimeError("AND3/OR3 tree mismatch")
            patterns.append(
                {
                    "pattern": f"{node['op']}3-two-gate-tree",
                    "input_nodes": input_ids,
                    "pair_sideproduct_node": child_id,
                    "main_node": node_id,
                    "current_gate": int(child["cost"]) + int(node["cost"]),
                    "main_arrival": signals[node_id].arrival,
                    "short_arc_input_node": third,
                    "short_arc_gate_depth": 1,
                    "output_primary_input_arc_depths": dict(signals[node_id].arcs),
                    "full_domain_rows": domain.row_count,
                    "mismatch_count": mismatch,
                    "truth_sha256s": [node_truths[child_id], node_truths[node_id]],
                    "classification": "two-gate tree dominates campaign-imported native 3-input gate",
                }
            )

    # Match complete seven-gate G/K/P full-adder expansions in the live DAG.
    for phase in xor_phases:
        if phase["pattern"] != "GKP-XOR":
            continue
        side = phase["phase_pair_nodes"]
        g_id = next(item for item in side if nodes[item]["op"] == "AND")
        k_id = next(item for item in side if nodes[item]["op"] == "NOR")
        p_id = int(phase["phase_main"])
        for t_id, t_node in nodes.items():
            if t_node["op"] != "AND" or p_id not in t_node["args"]:
                continue
            late = int(t_node["args"][0] if int(t_node["args"][1]) == p_id else t_node["args"][1])
            n_nodes = [
                item
                for item, candidate in nodes.items()
                if candidate["op"] == "NOR" and same_args(candidate, p_id, late)
            ]
            for n_id in n_nodes:
                sum_nodes = [
                    item
                    for item, candidate in nodes.items()
                    if candidate["op"] == "NOR" and same_args(candidate, t_id, n_id)
                ]
                carry_nodes = [
                    (item, candidate["op"])
                    for item, candidate in nodes.items()
                    if candidate["op"] in {"OR", "NAND"}
                    and same_args(candidate, g_id, t_id)
                ]
                for sum_id in sum_nodes:
                    for carry_id, carry_op in carry_nodes:
                        x, y = (signals[item].value for item in phase["input_nodes"])
                        c = signals[late].value
                        expected_sum = (x ^ y ^ c) & domain.mask
                        expected_carry = ((x & y) | (x & c) | (y & c)) & domain.mask
                        if carry_op == "NAND":
                            expected_carry = (~expected_carry) & domain.mask
                        mismatch = (
                            (signals[sum_id].value ^ expected_sum).bit_count()
                            + (signals[carry_id].value ^ expected_carry).bit_count()
                        )
                        if mismatch:
                            raise RuntimeError("full-adder pattern mismatch")
                        all_nodes = [g_id, k_id, p_id, t_id, n_id, sum_id, carry_id]
                        patterns.append(
                            {
                                "pattern": "FullAdder-GKP-7gate-" + ("carry" if carry_op == "OR" else "carrybar"),
                                "input_nodes": [*phase["input_nodes"], late],
                                "nodes": all_nodes,
                                "sideproduct_nodes": [g_id, k_id, p_id, t_id, n_id],
                                "sum_node": sum_id,
                                "carry_node": carry_id,
                                "current_gate": sum(int(nodes[item]["cost"]) for item in all_nodes),
                                "output_arrivals": [signals[sum_id].arrival, signals[carry_id].arrival],
                                "late_input_short_arcs": {"SUM": 2, "CARRY": 2},
                                "late_node_arrival": signals[late].arrival,
                                "late_node_primary_input_arc_depths": dict(signals[late].arcs),
                                "output_primary_input_arc_depths": {
                                    "SUM": dict(signals[sum_id].arcs),
                                    "CARRY": dict(signals[carry_id].arcs),
                                },
                                "full_domain_rows": domain.row_count,
                                "mismatch_count": mismatch,
                                "truth_sha256s": [node_truths[item] for item in all_nodes],
                                "classification": "current DAG already contains a 7-gate FullAdder expansion",
                            }
                        )

    for node_id, node in nodes.items():
        if node["op"] != "BUS":
            continue
        signal = signals[node_id]
        patterns.append(
            {
                "pattern": "two-Switch-resolved-BUS",
                "bus_node": node_id,
                "physical_owner": node["resolved_network"],
                "drivers": node["drivers"],
                "gate": node["cost"],
                "arrival": signal.arrival,
                "conflict_rows": signal.conflict.bit_count(),
                "undriven_rows": domain.row_count - signal.driven.bit_count(),
                "truth_sha256": node_truths[node_id],
                "classification": "resolved BUS is a free OR of active driver ones after paying its Switch owners",
            }
        )
    return patterns


def direct_reuse_search(
    domain: Domain,
    dag: dict[str, object],
    baseline: dict[str, object],
    node_truths: dict[int, str],
) -> list[dict[str, object]]:
    nodes = {int(node["id"]): node for node in dag["nodes"]}
    signals: dict[int, Signal] = baseline["signals"]
    users: dict[int, list[int]] = defaultdict(list)
    for node_id, node in nodes.items():
        for reference in node_references(node):
            users[reference].append(node_id)
    output_set = set(int(value) for value in dag["outputs"])

    ancestor_cache: dict[int, set[int]] = {}

    def ancestors(node_id: int) -> set[int]:
        if node_id not in ancestor_cache:
            result = set()
            for reference in node_references(nodes[node_id]):
                result.add(reference)
                result.update(ancestors(reference))
            ancestor_cache[node_id] = result
        return ancestor_cache[node_id]

    hits = []
    for target, target_node in nodes.items():
        if target_node["op"] == "INPUT":
            continue
        for source in nodes:
            if source == target or target in ancestors(source):
                continue
            if signals[source].value != signals[target].value:
                continue
            if any(source >= consumer for consumer in users[target]):
                continue
            if target in output_set and source not in nodes:
                continue
            result = replay_dag(domain, dag, {target: source})
            if result["gate"] >= baseline["gate"]:
                continue
            if result["delay"] > 7 or result["mismatch_union_count"]:
                continue
            if result["conflict_assignment_count"] or any(result["z_assignment_count_by_output"]):
                continue
            hits.append(
                {
                    "target_node": target,
                    "source_node": source,
                    "target_truth_sha256": node_truths[target],
                    "source_truth_sha256": node_truths[source],
                    "same_physical_truth": (
                        signals[source].driven == signals[target].driven
                        and signals[source].conflict == signals[target].conflict
                    ),
                    "new_gate": result["gate"],
                    "saved_gate": int(baseline["gate"]) - int(result["gate"]),
                    "new_delay": result["delay"],
                    "full_domain_rows": domain.row_count,
                    "mismatch_union_count": result["mismatch_union_count"],
                    "conflict_assignment_count": result["conflict_assignment_count"],
                    "z_assignment_count_by_output": result["z_assignment_count_by_output"],
                    "replacement_structural_sha256": result["structural_sha256"],
                    "scope": "abstract Factory DAG rewire only; no candidate was materialized",
                }
            )
    return sorted(hits, key=lambda item: (-item["saved_gate"], item["target_node"], item["source_node"]))


def dominance_rows() -> list[dict[str, object]]:
    return [
        {
            "component": "XOR",
            "expansion": "G/K/P or V/N/P",
            "expanded": [3, 2],
            "campaign_native": [3, 2],
            "runtime_default_native": [4, 3],
            "strict_when": "always versus runtime default; versus campaign native when any phase sideproduct is consumed",
            "byproducts": ["G,K", "V,N"],
        },
        {
            "component": "XNOR",
            "expansion": "G/K/Q or V/N/Q",
            "expanded": [3, 2],
            "campaign_native": [5, 4],
            "runtime_default_native": [4, 3],
            "strict_when": "always in gate and delay under both evidence profiles",
            "byproducts": ["G,K", "V,N"],
        },
        {
            "component": "AND3/OR3",
            "expansion": "two-gate tree with any selected pair first",
            "expanded": [2, 2],
            "campaign_native": [3, 2],
            "runtime_default_native": [2, 2],
            "strict_when": "always in campaign gate cost; versus runtime default when the pair intermediate or short-arc placement matters",
            "byproducts": ["selected pair result", "one-gate short arc from the third input"],
        },
        {
            "component": "FullAdder",
            "expansion": "seven ordinary gates, GKP and VNP phase families",
            "expanded": [7, 4],
            "campaign_native": [16, 8],
            "runtime_default_native": [8, 4],
            "strict_when": "always in gate cost; campaign native is also delay dominated",
            "byproducts": ["G/K/P/T/N", "V/N/P/NT/W", "carry or carrybar", "two-gate late-input arcs"],
        },
        {
            "component": "Switch",
            "expansion": "Boolean AND(E,D)",
            "expanded": [1, 1],
            "campaign_native": [2, 1],
            "runtime_default_native": [2, 1],
            "strict_when": "only when physical Z/driven ownership is provably irrelevant",
            "not_dominated_when": "a partial driver or resolved multidriver BUS is required",
        },
        {
            "component": "word NOT/NAND/Switch",
            "expansion": "per-lane bit components plus free Maker/Splitter",
            "strict_when": "score-neutral; exposes lane owners and byproducts but has no width discount",
            "z_caveat": "Maker/Splitter normalization is not an independent free Z driver",
        },
    ]


def report_markdown(payload: dict[str, object], catalog_sha: str) -> str:
    current = payload["current_80d7"]
    exhaustive = payload["primitive_library"]["exhaustive_minima"]
    lines = [
        "# 80/7 primitive-expansion byproduct truth catalog",
        "",
        f"- Status: `{payload['status']}`",
        f"- Catalog SHA256: `{catalog_sha}`",
        f"- Physical truth classes: `{payload['summary']['truth_class_count']}`",
        f"- Producers: `{payload['summary']['producer_count']}`",
        f"- Packed masks: `{payload['summary']['packed_mask_count']}`",
        "",
        "## Exact coverage",
        "",
        f"- 80/7 replay: `{current['replay']['gate']}/{current['replay']['delay']}`, `{current['replay']['rows']}` rows, mismatch/conflict/Z = `0/0/0`.",
        f"- Current DAG nodes / Switch partial drivers: `{current['replay']['node_count']}/{current['replay']['switch_driver_count']}`.",
        f"- Direct score-improving truth-reuse hits: `{len(current['score_improving_direct_reuse_hits'])}`.",
        f"- Embedded minimal-expansion pattern hits: `{len(current['embedded_expansion_hits'])}`.",
        "",
        "## Exhaustive small minima",
        "",
    ]
    for name, row in exhaustive.items():
        lines.append(
            f"- `{name}`: lower counts `{row['lower_gate_structure_counts']}`, minimal raw/classes `{row['minimal']['raw_live_structure_count']}/{row['minimal']['semantic_arc_class_count']}`."
        )
    lines.extend(
        [
            "",
            "## Dominance",
            "",
        ]
    )
    for row in payload["dominance"]:
        lines.append(f"- `{row['component']}`: {row['strict_when']}")
    lines.extend(
        [
            "",
            "The JSON is the machine artifact. It retains every value/driven/conflict mask,",
            "truth SHA, producer, owner set, gate/delay/owner Pareto point, input arc depth,",
            "embedded 80/7 hit, and full-domain direct-reuse replay.",
            "",
        ]
    )
    return "\n".join(lines)


def build(timeout_ms: int) -> dict[str, object]:
    dag_payload = json.loads(DAG_PATH.read_text(encoding="utf-8"))
    cost_payload = json.loads(COST_PATH.read_text(encoding="utf-8"))
    runtime_payload = json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
    if dag_payload["metrics"]["structural_sha256"] != "ba31029a5b3fa05c180a1f6ce23d90140dbaed75b4dd22bd19b7090ed3e1d15f":
        raise RuntimeError("authoritative 80/7 DAG anchor changed")

    bit2 = make_domain("bit2-full", ("A", "B"))
    bit3 = make_domain("bit3-full", ("A", "B", "C"))
    switch_domain = make_domain("switch-full", ("E", "D"))
    bus_domain = make_domain("two-switch-bus-full", ("E0", "E1", "D0", "D1"))
    onehot_domain = make_domain(
        "two-switch-bus-mutually-exclusive-enables",
        ("E0", "E1", "D0", "D1"),
        predicate=lambda row: not (row["E0"] and row["E1"]),
        constraint="E0 and E1 are mutually exclusive; D0/D1 are free",
    )
    input_names = tuple(
        [item for bit in range(8) for item in (f"a{bit}", f"b{bit}")] + ["cin"]
    )
    full80 = make_domain("verified-80d7-u8-u8-cin", input_names)

    catalog = Catalog()
    for domain, labels in (
        (bit2, local_labels(bit2)),
        (bit3, local_labels(bit3)),
        (switch_domain, local_labels(switch_domain)),
        (bus_domain, local_labels(bus_domain)),
        (onehot_domain, local_labels(onehot_domain)),
        (full80, arithmetic_labels(full80)),
    ):
        catalog.register_domain(domain, labels)
        for input_name in domain.inputs:
            catalog.add(
                domain,
                source_signal(domain, input_name),
                f"{domain.name}:input:{input_name}",
                "domain-input",
                "input",
                None,
                0,
                None,
            )

    exhaustive: dict[str, object] = {}
    enumerated_expansions: dict[str, list[dict[str, object]]] = {}
    bit2_targets = {
        "XOR": bit2.columns["A"] ^ bit2.columns["B"],
        "XNOR": ~(bit2.columns["A"] ^ bit2.columns["B"]) & bit2.mask,
    }
    for component, target in bit2_targets.items():
        lower = [enumerate_minimal_classes(bit2, target, gates) for gates in (1, 2)]
        minimal = enumerate_minimal_classes(bit2, target, 3)
        if any(item["raw_live_structure_count"] for item in lower) or not minimal["raw_live_structure_count"]:
            raise RuntimeError(f"bad exact minimum for {component}")
        enumerated_expansions[component] = instantiate_enumerated_classes(
            catalog, bit2, component, minimal
        )
        exhaustive[component] = {
            "lower_gate_structure_counts": [item["raw_live_structure_count"] for item in lower],
            "minimal": {key: value for key, value in minimal.items() if key != "classes"},
            "semantic_classes": enumerated_expansions[component],
            "proof_scope": "complete live ordinary DAG enumeration over inputs plus free constants",
        }
    a3, b3, c3 = (bit3.columns[name] for name in bit3.inputs)
    for component, target in (("AND3", a3 & b3 & c3), ("OR3", a3 | b3 | c3)):
        lower = [enumerate_minimal_classes(bit3, target, 1)]
        minimal = enumerate_minimal_classes(bit3, target, 2)
        if any(item["raw_live_structure_count"] for item in lower) or not minimal["raw_live_structure_count"]:
            raise RuntimeError(f"bad exact minimum for {component}")
        enumerated_expansions[component] = instantiate_enumerated_classes(
            catalog, bit3, component, minimal
        )
        exhaustive[component] = {
            "lower_gate_structure_counts": [item["raw_live_structure_count"] for item in lower],
            "minimal": {key: value for key, value in minimal.items() if key != "classes"},
            "semantic_classes": enumerated_expansions[component],
            "proof_scope": "complete live ordinary DAG enumeration over inputs plus free constants",
        }

    explicit = build_explicit_library(catalog, bit2, bit3)
    native_profiles = add_native_profiles(catalog, bit2, bit3, switch_domain)
    switch_bus = add_switch_bus_library(
        catalog, switch_domain, bus_domain, onehot_domain
    )
    fa_exact = exact_full_adder_proof(timeout_ms)

    current_replay_summary, node_truths = add_current_dag(catalog, full80, dag_payload)
    baseline = replay_dag(full80, dag_payload["factory_dag"])
    embedded = detect_patterns(
        catalog,
        full80,
        dag_payload["factory_dag"],
        baseline,
        node_truths,
    )
    direct_hits = direct_reuse_search(
        full80, dag_payload["factory_dag"], baseline, node_truths
    )

    truths = catalog.finalized_truths()
    producer_count = sum(int(row["producer_count"]) for row in truths)
    payload = {
        "schema": "tc-primitive-expansion-physical-byproduct-catalog-v1",
        "status": "pass",
        "scope": {
            "challenge": "Byte Adder",
            "authoritative_dag": "80/7/560",
            "truth_model": "packed value + driven + conflict; ordinary gates read Z as zero",
            "catalog_rule": "every intermediate signal, including unnamed and partial-driver signals, is retained",
            "candidate_or_save_modified": False,
            "game_launched": False,
        },
        "dependencies": {
            str(path.relative_to(ROOT)).replace("\\", "/"): file_sha256(path)
            for path in (DAG_PATH, COST_PATH, RUNTIME_PATH, ADVANCED_LIBRARY_PATH)
        },
        "cost_models": build_cost_models(cost_payload, runtime_payload),
        "summary": {
            "domain_count": len(catalog.domains),
            "truth_class_count": len(truths),
            "producer_count": producer_count,
            "packed_mask_count": len(catalog.masks),
            "owner_set_count": len(catalog.owner_sets),
            "embedded_expansion_hit_count": len(embedded),
            "score_improving_direct_reuse_hit_count": len(direct_hits),
        },
        "domains": catalog.domains,
        "packed_masks": catalog.masks,
        "owner_sets": catalog.owner_sets,
        "truth_classes": truths,
        "primitive_library": {
            "exhaustive_minima": exhaustive,
            "explicit_required_seeds": explicit,
            "native_score_profile_producers": native_profiles,
            "switch_and_bus": switch_bus,
            "full_adder_exact_minimum": fa_exact,
            "word_variants": build_word_profiles(),
        },
        "current_80d7": {
            "replay": current_replay_summary,
            "embedded_expansion_hits": embedded,
            "score_improving_direct_reuse_hits": direct_hits,
            "replacement_claim": (
                "only entries in score_improving_direct_reuse_hits are direct current-node replacements; embedded hits describe already-expanded cells"
            ),
        },
        "dominance": dominance_rows(),
        "claims": {
            "small_XOR_XNOR_AND3_OR3_minima_exhaustive": True,
            "full_adder_7gate_minimum_z3_exact": True,
            "all_80d7_nodes_and_switch_drivers_extracted": True,
            "full_131072_row_80d7_replay": True,
            "direct_reuse_hits_full_domain_replayed": True,
            "word_variants_parametric_not_full_truth_expanded": True,
            "physical_layout_or_materialization_claimed_for_reuse_hits": False,
        },
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--fa-timeout-ms", type=int, default=60_000)
    args = parser.parse_args()

    payload = build(args.fa_timeout_ms)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded.encode("utf-8"))
    digest = sha256(encoded.encode("utf-8")).hexdigest()
    report = report_markdown(payload, digest)
    args.report.write_bytes(report.encode("utf-8"))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(args.output),
                "output_sha256": digest,
                "report": str(args.report),
                "report_sha256": sha256(report.encode("utf-8")).hexdigest(),
                "summary": payload["summary"],
                "current_80d7_replay": payload["current_80d7"]["replay"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
