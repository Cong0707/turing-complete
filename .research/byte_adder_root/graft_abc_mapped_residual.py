"""Deterministically graft a mapped ABC residual onto a reviewed Byte Adder DAG.

The exporter keeps every resolved-BUS node and its complete backward slice
fixed.  This importer verifies that partition against the authoritative DAG,
parses a mapped ``.gate`` BLIF, replaces only the ordinary residual, and then
replays the complete 2^17 domain with Turing Complete cost, delay, Z, BUS, and
physical ownership semantics.

The output is a normal Factory DAG JSON accepted by the generic materializer.
This module is offline only: it never reads or writes the formal game save,
never deploys a repository candidate, and never launches the game.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_DAG = HERE / "byte-adder-hybrid-phasefold-g80-d7.json"
DEFAULT_METADATA = HERE / "abc_residual_current80" / "metadata.json"

ASSIGNMENTS = 1 << 17
ALL = (1 << ASSIGNMENTS) - 1
EXPECTED_INPUT_LABELS = {
    *{f"a{bit}" for bit in range(8)},
    *{f"b{bit}" for bit in range(8)},
    "cin",
}


@dataclass(frozen=True)
class GateSpec:
    arity: int
    cost: int
    delay: int
    pins: tuple[str, ...]
    dag_op: str | None


CELL_SPECS = {
    "$__ZERO": GateSpec(0, 0, 0, (), None),
    "$__ONE": GateSpec(0, 0, 0, (), None),
    "BUF": GateSpec(1, 0, 0, ("A",), None),
    "NOT": GateSpec(1, 1, 1, ("A",), "NOT"),
    "AND": GateSpec(2, 1, 1, ("A", "B"), "AND"),
    "OR": GateSpec(2, 1, 1, ("A", "B"), "OR"),
    "NAND": GateSpec(2, 1, 1, ("A", "B"), "NAND"),
    "NOR": GateSpec(2, 1, 1, ("A", "B"), "NOR"),
    "XOR": GateSpec(2, 3, 2, ("A", "B"), "XOR"),
    "XNOR": GateSpec(2, 3, 2, ("A", "B"), "XNOR"),
}

DAG_GATE_SPECS = {
    name: spec
    for name, spec in CELL_SPECS.items()
    if spec.dag_op is not None
}


@dataclass(frozen=True)
class MappedCell:
    index: int
    line: int
    kind: str
    inputs: tuple[str, ...]
    output: str


@dataclass(frozen=True)
class ParsedBlif:
    model: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    cells: tuple[MappedCell, ...]


@dataclass(frozen=True)
class PackedState:
    bits: int
    driven: int
    conflict: int
    arrival: int


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def portable(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def canonical_sha256(value: object) -> str:
    return sha256(
        json.dumps(
            value,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def logical_blif_lines(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    pending = ""
    pending_line = 0
    for line_number, raw in enumerate(text.splitlines(), start=1):
        content = raw.split("#", 1)[0].strip()
        if not content:
            continue
        continued = content.endswith("\\")
        if continued:
            content = content[:-1].rstrip()
        if not pending:
            pending_line = line_number
        pending = f"{pending} {content}".strip()
        if not continued:
            result.append((pending_line, pending))
            pending = ""
            pending_line = 0
    if pending:
        raise ValueError(f"unterminated BLIF continuation from line {pending_line}")
    return result


def parse_mapped_blif(path: Path) -> ParsedBlif:
    try:
        text = path.read_text(encoding="ascii")
    except UnicodeDecodeError as exc:
        raise ValueError(f"mapped BLIF is not ASCII: {path}") from exc

    model: str | None = None
    inputs: tuple[str, ...] | None = None
    outputs: tuple[str, ...] | None = None
    cells: list[MappedCell] = []
    ended = False
    driven_nets: set[str] = set()
    for line_number, line in logical_blif_lines(text):
        tokens = line.split()
        directive = tokens[0]
        if ended:
            raise ValueError(f"BLIF content after .end at line {line_number}")
        if directive == ".model":
            if model is not None or len(tokens) != 2:
                raise ValueError(f"bad or duplicate .model at line {line_number}")
            model = tokens[1]
        elif directive == ".inputs":
            if inputs is not None or len(tokens) < 2:
                raise ValueError(f"bad or duplicate .inputs at line {line_number}")
            inputs = tuple(tokens[1:])
            if len(inputs) != len(set(inputs)):
                raise ValueError("duplicate BLIF primary input")
        elif directive == ".outputs":
            if outputs is not None or len(tokens) < 2:
                raise ValueError(f"bad or duplicate .outputs at line {line_number}")
            outputs = tuple(tokens[1:])
            if len(outputs) != len(set(outputs)):
                raise ValueError("duplicate BLIF primary output")
        elif directive == ".gate":
            if len(tokens) < 3:
                raise ValueError(f"malformed .gate at line {line_number}")
            kind = tokens[1].upper()
            spec = CELL_SPECS.get(kind)
            if spec is None:
                raise ValueError(f"unsupported mapped cell {tokens[1]!r} at line {line_number}")
            pins: dict[str, str] = {}
            for token in tokens[2:]:
                if token.count("=") != 1:
                    raise ValueError(f"malformed pin {token!r} at line {line_number}")
                pin, net = token.split("=", 1)
                pin = pin.upper()
                if not pin or not net or pin in pins:
                    raise ValueError(f"bad or duplicate pin {token!r} at line {line_number}")
                pins[pin] = net
            expected_pins = {*spec.pins, "Y"}
            if set(pins) != expected_pins:
                raise ValueError(
                    f"{kind} pins at line {line_number} are {sorted(pins)}, "
                    f"expected {sorted(expected_pins)}"
                )
            output = pins["Y"]
            if output in driven_nets:
                raise ValueError(f"multiple mapped drivers for net {output!r}")
            driven_nets.add(output)
            cells.append(
                MappedCell(
                    index=len(cells),
                    line=line_number,
                    kind=kind,
                    inputs=tuple(pins[pin] for pin in spec.pins),
                    output=output,
                )
            )
        elif directive == ".end":
            if len(tokens) != 1:
                raise ValueError(f"malformed .end at line {line_number}")
            ended = True
        else:
            raise ValueError(f"unsupported mapped BLIF directive {directive!r} at line {line_number}")

    if model is None or inputs is None or outputs is None or not ended:
        raise ValueError("mapped BLIF lacks .model, .inputs, .outputs, or .end")
    if set(inputs).intersection(driven_nets):
        raise ValueError("mapped cell overwrites a BLIF primary input")

    producer = {cell.output: cell.index for cell in cells}
    live_cells: set[int] = set()
    pending = list(outputs)
    while pending:
        net = pending.pop()
        index = producer.get(net)
        if index is None or index in live_cells:
            continue
        live_cells.add(index)
        pending.extend(cells[index].inputs)
    dead_cells = sorted(set(range(len(cells))) - live_cells)
    if dead_cells:
        details = [(cells[index].line, cells[index].output) for index in dead_cells[:8]]
        raise ValueError(f"mapped BLIF contains dead cells: {details!r}")

    return ParsedBlif(model=model, inputs=inputs, outputs=outputs, cells=tuple(cells))


def backward_slice(nodes: dict[int, dict[str, Any]], roots: Iterable[int]) -> set[int]:
    seen: set[int] = set()
    pending = list(roots)
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        if current not in nodes:
            raise RuntimeError(f"backward slice references missing node {current}")
        seen.add(current)
        pending.extend(int(value) for value in nodes[current].get("args", ()))
    return seen


def recompute_partition(dag: dict[str, Any]) -> dict[str, Any]:
    factory_dag = dag["factory_dag"]
    ordered = tuple(factory_dag["nodes"])
    nodes = {int(node["id"]): node for node in ordered}
    outputs = tuple(int(value) for value in factory_dag["outputs"])
    bus_nodes = [node_id for node_id, node in nodes.items() if node["op"] == "BUS"]
    fixed = backward_slice(nodes, bus_nodes)
    residual = {
        node_id
        for node_id, node in nodes.items()
        if node["op"] not in ("INPUT", "CONST") and node_id not in fixed
    }
    boundary = sorted(
        {
            int(argument)
            for node_id in residual
            for argument in nodes[node_id].get("args", ())
            if int(argument) not in residual
        }
        | {output for output in outputs if output not in residual}
    )
    return {
        "bus_nodes": bus_nodes,
        "fixed_nodes": sorted(fixed),
        "fixed_gate": sum(int(nodes[node_id]["cost"]) for node_id in fixed),
        "residual_nodes": sorted(residual),
        "residual_gate": sum(int(nodes[node_id]["cost"]) for node_id in residual),
        "boundary": [
            {
                "id": node_id,
                "operation": nodes[node_id]["op"],
                "arrival": int(nodes[node_id]["arrival"]),
                "may_z": bool(nodes[node_id].get("may_z", False)),
            }
            for node_id in boundary
        ],
        "outputs": list(outputs),
        "output_arrivals": [int(nodes[node_id]["arrival"]) for node_id in outputs],
    }


def validate_metadata(
    metadata: dict[str, Any], dag_path: Path, partition: dict[str, Any]
) -> None:
    if metadata.get("schema") != "byte-adder-80d7-abc-residual-export-v1":
        raise RuntimeError(f"unexpected residual metadata schema: {metadata.get('schema')!r}")
    # The authoritative DAG was produced on Windows but may be audited on
    # Linux.  pathlib.Path only recognizes the current platform's separator,
    # so normalize both path styles before comparing the source basename.
    source_name = str(metadata.get("source", "")).replace("\\", "/").rsplit("/", 1)[-1]
    if source_name != dag_path.name:
        raise RuntimeError(
            f"metadata source basename {source_name!r} does not match {dag_path.name!r}"
        )
    for field, expected in partition.items():
        if metadata.get(field) != expected:
            raise RuntimeError(f"metadata {field} differs from authoritative DAG partition")


def variable(index: int) -> int:
    if index < 3:
        return int.from_bytes(
            bytes([(0xAA, 0xCC, 0xF0)[index]]) * (ASSIGNMENTS // 8),
            "little",
        )
    block = 1 << (index - 3)
    data = (bytes(block) + bytes([0xFF]) * block) * (
        ASSIGNMENTS // (16 * block)
    )
    return int.from_bytes(data, "little")


def expected_outputs() -> tuple[int, ...]:
    variables = tuple(variable(index) for index in range(17))
    carry = variables[16]
    outputs = []
    for bit in range(8):
        propagate = variables[bit] ^ variables[8 + bit]
        outputs.append(propagate ^ carry)
        carry = (variables[bit] & variables[8 + bit]) | (propagate & carry)
    outputs.append(carry)
    return tuple(outputs)


def reachable(nodes: dict[int, dict[str, Any]], outputs: Iterable[int]) -> set[int]:
    result: set[int] = set()
    pending = list(outputs)
    while pending:
        node_id = pending.pop()
        if node_id in result:
            continue
        if node_id not in nodes:
            raise RuntimeError(f"output cone references missing node {node_id}")
        result.add(node_id)
        pending.extend(int(value) for value in nodes[node_id].get("args", ()))
    return result


def evaluate_nodes(
    ordered: tuple[dict[str, Any], ...], outputs: tuple[int, ...]
) -> tuple[dict[int, PackedState], dict[str, Any], dict[str, Any]]:
    states: dict[int, PackedState] = {}
    by_id: dict[int, dict[str, Any]] = {}
    variables = {
        **{f"a{bit}": variable(bit) for bit in range(8)},
        **{f"b{bit}": variable(8 + bit) for bit in range(8)},
        "cin": variable(16),
    }
    input_labels: set[str] = set()
    bus_ids = []
    resolved_names: set[str] = set()
    reviewed_gate = 0
    for offset, raw_node in enumerate(ordered):
        node = dict(raw_node)
        node_id = int(node["id"])
        if node_id in states:
            raise RuntimeError(f"duplicate Factory node id {node_id}")
        args_ids = tuple(int(value) for value in node.get("args", ()))
        if any(argument not in states for argument in args_ids):
            raise RuntimeError(f"Factory node {node_id} at offset {offset} is not topological")
        args = [states[argument] for argument in args_ids]
        op = str(node["op"])
        if op == "CONST":
            label = str(node.get("label"))
            if label not in {"0", "1"} or args:
                raise RuntimeError(f"bad CONST node {node_id}")
            state = PackedState(ALL if label == "1" else 0, ALL, 0, 0)
            expected_cost = expected_delay = 0
        elif op == "INPUT":
            label = str(node.get("label"))
            if label not in variables or label in input_labels or args:
                raise RuntimeError(f"bad or duplicate INPUT node {node_id}: {label!r}")
            input_labels.add(label)
            state = PackedState(variables[label], ALL, 0, 0)
            expected_cost = expected_delay = 0
        elif op == "BUS":
            if not args or len(args) % 2:
                raise RuntimeError(f"BUS node {node_id} has incomplete drivers")
            ones = zeros = driven = conflict = 0
            for index in range(0, len(args), 2):
                enable, data = args[index], args[index + 1]
                active = enable.bits
                ones |= active & data.bits
                zeros |= active & (~data.bits & ALL)
                driven |= active
                conflict |= enable.conflict | data.conflict
            conflict |= ones & zeros
            expected_delay = 1
            expected_cost = len(args) // 2 * 2
            state = PackedState(
                ones & ALL,
                driven & ALL,
                conflict & ALL,
                max(item.arrival for item in args) + 1,
            )
            resolved = str(node.get("resolved_network", f"bus_node_{node_id}"))
            if resolved not in {f"bus_node_{node_id}", f"bus_{node_id}"}:
                raise RuntimeError(f"BUS node {node_id} has noncanonical resolved network")
            if resolved in resolved_names:
                raise RuntimeError(f"BUS node {node_id} aliases resolved network {resolved!r}")
            resolved_names.add(resolved)
            drivers = node.get("drivers")
            if drivers is not None:
                expected_drivers = [
                    {
                        "enable": args_ids[index],
                        "data": args_ids[index + 1],
                        "owner": resolved,
                    }
                    for index in range(0, len(args_ids), 2)
                ]
                if drivers != expected_drivers:
                    raise RuntimeError(f"BUS node {node_id} driver ownership changed")
            bus_ids.append(node_id)
        elif op in DAG_GATE_SPECS:
            spec = DAG_GATE_SPECS[op]
            if len(args) != spec.arity:
                raise RuntimeError(f"{op} node {node_id} has wrong arity")
            left = args[0].bits
            right = args[1].bits if len(args) == 2 else 0
            if op == "NOT":
                bits = ~left
            elif op == "AND":
                bits = left & right
            elif op == "OR":
                bits = left | right
            elif op == "NAND":
                bits = ~(left & right)
            elif op == "NOR":
                bits = ~(left | right)
            elif op == "XOR":
                bits = left ^ right
            elif op == "XNOR":
                bits = ~(left ^ right)
            else:  # pragma: no cover
                raise AssertionError(op)
            conflict = 0
            for item in args:
                conflict |= item.conflict
            expected_cost = spec.cost
            expected_delay = spec.delay
            state = PackedState(
                bits & ALL,
                ALL,
                conflict & ALL,
                max(item.arrival for item in args) + spec.delay,
            )
        else:
            raise RuntimeError(f"unsupported Factory DAG operation {op!r}")
        if (
            int(node.get("cost", -1)) != expected_cost
            or int(node.get("step_delay", -1)) != expected_delay
            or int(node.get("arrival", -1)) != state.arrival
            or bool(node.get("may_z")) != (op == "BUS")
        ):
            raise RuntimeError(f"Factory node {node_id} cost/delay/Z annotation mismatch")
        reviewed_gate += expected_cost
        states[node_id] = state
        by_id[node_id] = node

    if input_labels != EXPECTED_INPUT_LABELS:
        raise RuntimeError(
            f"Factory input contract mismatch: missing={EXPECTED_INPUT_LABELS-input_labels!r}, "
            f"extra={input_labels-EXPECTED_INPUT_LABELS!r}"
        )
    if len(outputs) != 9 or any(output not in states for output in outputs):
        raise RuntimeError("Factory DAG must expose eight sums and one carry")
    live = reachable(by_id, outputs)
    dead = sorted(set(by_id) - live)
    if dead:
        raise RuntimeError(f"Factory DAG contains dead nodes: {dead[:12]!r}")

    actual = tuple(states[node_id] for node_id in outputs)
    expected = expected_outputs()
    mismatch_masks = [item.bits ^ target for item, target in zip(actual, expected, strict=True)]
    mismatch_union = 0
    conflict_union = 0
    for mask in mismatch_masks:
        mismatch_union |= mask
    for node_id in live:
        conflict_union |= states[node_id].conflict
    z_masks = [(~item.driven) & ALL for item in actual]
    digest = sha256(
        b"".join(
            item.bits.to_bytes(ASSIGNMENTS // 8, "little") for item in actual
        )
    ).hexdigest()
    semantic = {
        "truth_table_rows": ASSIGNMENTS,
        "mismatch_count_by_output": [mask.bit_count() for mask in mismatch_masks],
        "mismatch_union_count": mismatch_union.bit_count(),
        "conflict_assignment_count": conflict_union.bit_count(),
        "z_assignment_count_by_output": [mask.bit_count() for mask in z_masks],
        "output_vector_sha256": digest,
    }
    output_arrivals = [states[node_id].arrival for node_id in outputs]

    structural_memo: dict[int, str] = {}

    def visit(node_id: int) -> str:
        found = structural_memo.get(node_id)
        if found is not None:
            return found
        node = by_id[node_id]
        value = [
            node["op"],
            node.get("label", ""),
            int(node["cost"]),
            int(node["step_delay"]),
        ]
        value.extend(visit(int(argument)) for argument in node.get("args", ()))
        result = canonical_sha256(value)
        structural_memo[node_id] = result
        return result

    structural_sha = sha256("".join(visit(node_id) for node_id in outputs).encode()).hexdigest()
    metrics = {
        "gate": reviewed_gate,
        "delay": max(output_arrivals),
        "energy": reviewed_gate * max(output_arrivals),
        "output_arrivals": output_arrivals,
        "reachable_nodes": len(live),
        "structural_sha256": structural_sha,
    }
    audit = {
        "node_count": len(by_id),
        "dead_node_count": 0,
        "bus_node_ids": bus_ids,
        "resolved_network_count": len(resolved_names),
        "physical_net_partition_violation_count": 0,
        "recursive_cost_delay_verified": True,
    }
    return states, metrics, {"semantic": semantic, "audit": audit}


def validate_top_level(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("status") != "sat":
        raise RuntimeError("Factory DAG payload is not SAT")
    factory_dag = payload.get("factory_dag")
    if not isinstance(factory_dag, dict):
        raise RuntimeError("payload lacks factory_dag")
    nodes = tuple(factory_dag.get("nodes", ()))
    outputs = tuple(int(value) for value in factory_dag.get("outputs", ()))
    _states, metrics, details = evaluate_nodes(nodes, outputs)
    if payload.get("metrics") != metrics:
        raise RuntimeError("serialized metrics differ from independent packed replay")
    if payload.get("semantic") != details["semantic"]:
        raise RuntimeError("serialized semantic summary differs from independent packed replay")
    hash_payload = {
        "outputs": list(outputs),
        "nodes": list(nodes),
        "live_node_count": len(nodes),
    }
    expected_factory_hash = canonical_sha256(hash_payload)
    if (
        factory_dag.get("live_node_count") != len(nodes)
        or factory_dag.get("sha256") != expected_factory_hash
    ):
        raise RuntimeError("Factory DAG canonical hash or live count mismatch")
    return {"metrics": metrics, **details}


def validate_authoritative_dag(payload: dict[str, Any]) -> dict[str, Any]:
    review = validate_top_level(payload)
    if review["semantic"]["mismatch_union_count"]:
        raise RuntimeError("authoritative DAG truth table is not clean")
    if review["semantic"]["conflict_assignment_count"]:
        raise RuntimeError("authoritative DAG has BUS conflicts")
    if any(review["semantic"]["z_assignment_count_by_output"]):
        raise RuntimeError("authoritative DAG has an undriven primary output")
    return review


def materialize_mapped_cells(
    parsed: ParsedBlif,
    boundary_ids: tuple[int, ...],
    shell_nodes: list[dict[str, Any]],
    first_node_id: int,
) -> tuple[list[dict[str, Any]], tuple[int, ...], list[dict[str, Any]], int]:
    by_id = {int(node["id"]): node for node in shell_nodes}
    arrivals = {node_id: int(node["arrival"]) for node_id, node in by_id.items()}
    signals = {
        name: node_id
        for name, node_id in zip(parsed.inputs, boundary_ids, strict=True)
    }
    constant_nodes = {
        str(node.get("label")): int(node["id"])
        for node in shell_nodes
        if node["op"] == "CONST"
    }
    generated: list[dict[str, Any]] = []
    cell_records: list[dict[str, Any]] = []
    next_id = first_node_id

    def constant(label: str) -> tuple[int, bool]:
        nonlocal next_id
        found = constant_nodes.get(label)
        if found is not None:
            return found, False
        node_id = next_id
        next_id += 1
        node = {
            "id": node_id,
            "op": "CONST",
            "args": [],
            "cost": 0,
            "step_delay": 0,
            "arrival": 0,
            "may_z": False,
            "label": label,
        }
        generated.append(node)
        by_id[node_id] = node
        arrivals[node_id] = 0
        constant_nodes[label] = node_id
        return node_id, True

    for cell in parsed.cells:
        unresolved = [name for name in cell.inputs if name not in signals]
        if unresolved:
            raise RuntimeError(
                f"mapped cell at BLIF line {cell.line} has unresolved inputs {unresolved!r}"
            )
        spec = CELL_SPECS[cell.kind]
        input_ids = tuple(signals[name] for name in cell.inputs)
        node_id: int
        materialized = True
        if cell.kind == "$__ZERO":
            node_id, materialized = constant("0")
        elif cell.kind == "$__ONE":
            node_id, materialized = constant("1")
        elif cell.kind == "BUF":
            node_id = input_ids[0]
            materialized = False
        else:
            node_id = next_id
            next_id += 1
            arrival = max(arrivals[source] for source in input_ids) + spec.delay
            node = {
                "id": node_id,
                "op": spec.dag_op,
                "args": list(input_ids),
                "cost": spec.cost,
                "step_delay": spec.delay,
                "arrival": arrival,
                "may_z": False,
                "label": f"abc:{cell.output}",
            }
            generated.append(node)
            by_id[node_id] = node
            arrivals[node_id] = arrival
        signals[cell.output] = node_id
        cell_records.append(
            {
                "index": cell.index,
                "line": cell.line,
                "kind": cell.kind,
                "inputs": list(cell.inputs),
                "output": cell.output,
                "input_node_ids": list(input_ids),
                "output_node_id": node_id,
                "materialized_new_node": materialized,
                "cost": spec.cost,
                "delay": spec.delay,
            }
        )

    missing_outputs = [name for name in parsed.outputs if name not in signals]
    if missing_outputs:
        raise RuntimeError(f"mapped BLIF outputs are unresolved: {missing_outputs!r}")
    output_nodes = tuple(signals[name] for name in parsed.outputs)
    residual_gate = sum(CELL_SPECS[cell.kind].cost for cell in parsed.cells)
    return generated, output_nodes, cell_records, residual_gate


def validate_mapped_interface(
    parsed: ParsedBlif,
    partition: dict[str, Any],
) -> tuple[int, ...]:
    boundary_ids = tuple(int(item["id"]) for item in partition["boundary"])
    expected_inputs = tuple(f"n{node_id}" for node_id in boundary_ids)
    expected_outputs = tuple(f"out{index}" for index in range(len(partition["outputs"])))
    if parsed.inputs != expected_inputs:
        raise RuntimeError("mapped BLIF primary inputs differ from metadata boundary order")
    if parsed.outputs != expected_outputs:
        raise RuntimeError("mapped BLIF primary outputs differ from exported output order")
    return boundary_ids


def build(
    dag_path: Path,
    metadata_path: Path,
    blif_path: Path,
) -> dict[str, Any]:
    dag_path = Path(dag_path).resolve()
    metadata_path = Path(metadata_path).resolve()
    blif_path = Path(blif_path).resolve()
    for path in (dag_path, metadata_path, blif_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    authority = json.loads(dag_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    authority_review = validate_authoritative_dag(authority)
    partition = recompute_partition(authority)
    validate_metadata(metadata, dag_path, partition)
    parsed = parse_mapped_blif(blif_path)

    # ABC derives a cosmetic model name from a PLA filename.  The ordered PI/PO
    # contract, not that label, identifies the residual interface.
    boundary_ids = validate_mapped_interface(parsed, partition)

    original_nodes = tuple(authority["factory_dag"]["nodes"])
    original_by_id = {int(node["id"]): node for node in original_nodes}
    residual_ids = set(int(value) for value in partition["residual_nodes"])
    shell_nodes = [dict(node) for node in original_nodes if int(node["id"]) not in residual_ids]
    shell_ids = {int(node["id"]) for node in shell_nodes}
    if any(node_id not in shell_ids for node_id in boundary_ids):
        raise RuntimeError("metadata boundary is not completely retained in the fixed shell")
    if sum(int(node["cost"]) for node in shell_nodes) != int(partition["fixed_gate"]):
        raise RuntimeError("retained shell cost differs from metadata fixed_gate")

    first_node_id = max(original_by_id) + 1
    generated, output_nodes, cell_records, residual_gate = materialize_mapped_cells(
        parsed, boundary_ids, shell_nodes, first_node_id
    )
    graft_nodes = tuple([*shell_nodes, *generated])
    graft_by_id = {int(node["id"]): node for node in graft_nodes}
    if len(graft_by_id) != len(graft_nodes):
        raise RuntimeError("graft produced duplicate node IDs")
    for node_id in partition["fixed_nodes"]:
        if graft_by_id[int(node_id)] != original_by_id[int(node_id)]:
            raise RuntimeError(f"fixed BUS slice node {node_id} changed during graft")
    original_bus_ids = [
        int(node["id"]) for node in original_nodes if node["op"] == "BUS"
    ]
    graft_bus_ids = [int(node["id"]) for node in graft_nodes if node["op"] == "BUS"]
    if graft_bus_ids != original_bus_ids or graft_bus_ids != partition["bus_nodes"]:
        raise RuntimeError("graft changed the fixed resolved-BUS node set")

    live = reachable(graft_by_id, output_nodes)
    dead_shell = sorted(shell_ids - live)
    dead_generated = sorted({int(node["id"]) for node in generated} - live)
    if dead_shell or dead_generated:
        raise RuntimeError(
            f"graft contains dead nodes: shell={dead_shell[:8]!r}, "
            f"generated={dead_generated[:8]!r}"
        )

    _states, metrics, details = evaluate_nodes(graft_nodes, output_nodes)
    semantic = details["semantic"]
    if semantic["mismatch_union_count"]:
        raise RuntimeError(f"grafted residual has truth mismatches: {semantic}")
    if semantic["conflict_assignment_count"]:
        raise RuntimeError(f"grafted residual has BUS conflicts: {semantic}")
    if any(semantic["z_assignment_count_by_output"]):
        raise RuntimeError(f"grafted residual has undriven primary outputs: {semantic}")
    if int(metrics["gate"]) != int(partition["fixed_gate"]) + residual_gate:
        raise RuntimeError("grafted total gate does not equal fixed plus mapped residual gate")

    hash_payload = {
        "outputs": list(output_nodes),
        "nodes": list(graft_nodes),
        "live_node_count": len(graft_nodes),
    }
    hash_payload["sha256"] = canonical_sha256(hash_payload)
    fixed_slice_payload = [original_by_id[int(node_id)] for node_id in partition["fixed_nodes"]]
    kind_counts = Counter(cell.kind for cell in parsed.cells)
    payload: dict[str, Any] = {
        "schema": "byte-adder-abc-mapped-residual-graft-v1",
        "status": "sat",
        "family": "authoritative 80/7 fixed BUS slice plus Berkeley ABC mapped ordinary residual",
        "source": {
            "authoritative_dag": portable(dag_path),
            "authoritative_dag_sha256": file_sha256(dag_path),
            "authoritative_factory_dag_sha256": authority["factory_dag"]["sha256"],
            "metadata": portable(metadata_path),
            "metadata_sha256": file_sha256(metadata_path),
            "mapped_blif": portable(blif_path),
            "mapped_blif_sha256": file_sha256(blif_path),
            "importer": portable(Path(__file__)),
            "importer_sha256": file_sha256(Path(__file__)),
        },
        "partition": {
            **partition,
            "retained_shell_nodes": sorted(shell_ids),
            "retained_shell_node_count": len(shell_ids),
            "fixed_slice_sha256": canonical_sha256(fixed_slice_payload),
            "fixed_slice_byte_identical": True,
        },
        "mapped_residual": {
            "model": parsed.model,
            "primary_inputs": list(parsed.inputs),
            "primary_outputs": list(parsed.outputs),
            "cell_count": len(parsed.cells),
            "materialized_new_node_count": len(generated),
            "kind_counts": dict(sorted(kind_counts.items())),
            "residual_gate": residual_gate,
            "first_allocated_node_id": first_node_id,
            "node_id_policy": "mapped non-alias nodes in BLIF order after max authoritative node ID",
            "cells": cell_records,
        },
        "metrics": metrics,
        "semantic": semantic,
        "z_bus_audit": {
            "authoritative_bus_node_ids": original_bus_ids,
            "grafted_bus_node_ids": graft_bus_ids,
            "fixed_bus_slice_preserved": True,
            "full_truth_rows": ASSIGNMENTS,
            "packed_conflict_cases": semantic["conflict_assignment_count"],
            "primary_output_z_counts": semantic["z_assignment_count_by_output"],
        },
        "physical": {
            "bus_nodes": len(graft_bus_ids),
            "bus_node_ids": graft_bus_ids,
            "new_bus_node_count": 0,
            "partial_driver_reuse_possible": False,
            "physical_net_partition_violation_count": details["audit"][
                "physical_net_partition_violation_count"
            ],
            "reason": "all resolved BUS nodes and complete owned driver sets are byte-identical to the authoritative fixed slice",
        },
        "dead_node_audit": {
            "mapped_blif_dead_cell_count": 0,
            "dead_shell_node_count": 0,
            "dead_generated_node_count": 0,
            "reachable_node_count": len(live),
            "serialized_node_count": len(graft_nodes),
        },
        "authority_review": {
            "metrics": authority_review["metrics"],
            "semantic": authority_review["semantic"],
            "partition_recomputed": True,
        },
        "determinism": {
            "canonical_factory_hash": "compact ASCII insertion-order JSON",
            "stable_new_node_allocation": True,
            "cli_rebuilds_twice_and_requires_byte_identity": True,
        },
        "test_domain": {
            "variables": 17,
            "rows": ASSIGNMENTS,
            "complete_u8_u8_u1": True,
        },
        "factory_dag": hash_payload,
    }
    validate_top_level(payload)
    return payload


def check_limits(payload: dict[str, Any], args: argparse.Namespace) -> None:
    metrics = payload["metrics"]
    exact = {
        "gate": args.expected_gate,
        "delay": args.expected_delay,
        "energy": args.expected_energy,
    }
    maxima = {
        "gate": args.max_gate,
        "delay": args.max_delay,
        "energy": args.max_energy,
    }
    for field, expected in exact.items():
        if expected is not None and int(metrics[field]) != expected:
            raise RuntimeError(
                f"graft {field}={metrics[field]} differs from expected {expected}"
            )
    for field, maximum in maxima.items():
        if maximum is not None and int(metrics[field]) > maximum:
            raise RuntimeError(
                f"graft {field}={metrics[field]} exceeds maximum {maximum}"
            )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    result.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    result.add_argument("--blif", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--expected-gate", type=int)
    result.add_argument("--expected-delay", type=int)
    result.add_argument("--expected-energy", type=int)
    result.add_argument("--max-gate", type=int)
    result.add_argument("--max-delay", type=int)
    result.add_argument("--max-energy", type=int)
    return result


def main() -> int:
    args = parser().parse_args()
    first = build(args.dag, args.metadata, args.blif)
    second = build(args.dag, args.metadata, args.blif)
    first_encoded = (json.dumps(first, ensure_ascii=False, indent=2) + "\n").encode()
    second_encoded = (json.dumps(second, ensure_ascii=False, indent=2) + "\n").encode()
    if first_encoded != second_encoded:
        raise RuntimeError("same-process deterministic importer replay changed JSON bytes")
    check_limits(first, args)
    output_sha = atomic_write(args.output.resolve(), first)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "output_sha256": output_sha,
                "metrics": first["metrics"],
                "mapped_residual": {
                    key: first["mapped_residual"][key]
                    for key in (
                        "cell_count",
                        "materialized_new_node_count",
                        "kind_counts",
                        "residual_gate",
                    )
                },
                "full_truth_rows": first["semantic"]["truth_table_rows"],
                "mismatch_union_count": first["semantic"]["mismatch_union_count"],
                "conflict_assignment_count": first["semantic"][
                    "conflict_assignment_count"
                ],
                "primary_output_z_counts": first["semantic"][
                    "z_assignment_count_by_output"
                ],
                "dead_node_audit": first["dead_node_audit"],
                "deterministic_rebuild_byte_identical": True,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
