"""Convert the reviewed human 87/6 circuit into the 86/6 S7-owner merge DAG.

The transformation is deliberately narrow.  It preserves every paid network
from the source circuit except the three-driver S7 owner:

    old = BUS(SW(n278, n207), SW(Q6, P7), SW(n285, P7))
    U   = OR(n278, AND(Q6, P7))
    new = BUS(SW(U, n207), SW(n285, P7))

The AND(Q6, P7) rail already exists as physical network 258 and remains live
through C8.  On its domain n207 == P7 == 1, so the two old owners can share
one data rail.  One Switch is removed and one OR is added: 87 -> 86 gates.
"""

from __future__ import annotations

from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "source_human87" / "circuit.data"
OUTPUT = HERE / "byte-adder-human86-s7-owner-merge-full.json"
MATERIALIZER = (
    ROOT
    / ".research"
    / "byte_adder_builder_layout_agent"
    / "materialize_factory_dag.py"
)

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

from audit_human_87 import ALL_ROWS, _compile, _evaluate  # noqa: E402
from tc_save_lab.codec import decode_v15  # noqa: E402
from tc_save_lab.pins import I, O, T, positioned_pins  # noqa: E402


OPS = {
    3: ("NOT", 1, 1),
    4: ("AND", 1, 1),
    5: ("AND3", 3, 2),
    6: ("NAND", 1, 1),
    7: ("OR", 1, 1),
    8: ("OR3", 3, 2),
    9: ("NOR", 1, 1),
    10: ("XOR", 3, 2),
    11: ("XNOR", 5, 4),
}


def _load_materializer():
    spec = importlib.util.spec_from_file_location("human86_materializer", MATERIALIZER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import materializer: {MATERIALIZER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _network_pins(circuit, compiled):
    drivers: dict[int, list[tuple[int, str]]] = defaultdict(list)
    sinks: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, index):
            network = compiled.pin_networks.get((index, pin.name))
            if network is None:
                continue
            target = drivers if pin.direction in {O, T} else sinks
            target[network].append((index, pin.name))
    return drivers, sinks


def build() -> dict[str, Any]:
    materializer = _load_materializer()
    circuit = decode_v15(SOURCE.read_bytes())
    compiled = _compile(circuit)
    inputs, values, driven, _arrivals, _switch_rows, source_conflict = _evaluate(
        circuit, compiled
    )
    if source_conflict:
        raise RuntimeError("source human-87 has a BUS conflict")
    drivers, _sinks = _network_pins(circuit, compiled)

    variable_masks = {
        **{inputs["A"][bit]: f"a{bit}" for bit in range(8)},
        **{inputs["B"][bit]: f"b{bit}" for bit in range(8)},
        inputs["Carry in"][0]: "cin",
    }

    nodes: list[dict[str, Any]] = []
    network_node: dict[int, int] = {}
    next_id = 1

    def add_node(
        op: str,
        args: list[int],
        *,
        cost: int,
        step_delay: int,
        arrival: int,
        may_z: bool,
        label: str = "",
    ) -> int:
        nonlocal next_id
        node_id = next_id
        next_id += 1
        node: dict[str, Any] = {
            "id": node_id,
            "op": op,
            "args": args,
            "cost": cost,
            "step_delay": step_delay,
            "arrival": arrival,
            "may_z": may_z,
            "label": label,
        }
        if op == "BUS":
            owner = f"bus_{node_id}"
            node["resolved_network"] = owner
            node["drivers"] = [
                {"enable": args[index], "data": args[index + 1], "owner": owner}
                for index in range(0, len(args), 2)
            ]
        nodes.append(node)
        return node_id

    # Scalar outputs of campaign inputs and free Splitters are all aliases of
    # the 17 fixed variables.  Map every duplicate physical rail to one node.
    label_node: dict[str, int] = {}
    for label in [*(f"a{i}" for i in range(8)), *(f"b{i}" for i in range(8)), "cin"]:
        label_node[label] = add_node(
            "INPUT", [], cost=0, step_delay=0, arrival=0, may_z=False, label=label
        )
    for network, network_drivers in drivers.items():
        if len(values.get(network, ())) != 1:
            continue
        if not all(circuit.components[index].kind in {17, 61} for index, _ in network_drivers):
            continue
        value = values[network][0] & driven[network][0]
        label = variable_masks.get(value)
        if label is not None and driven[network][0] == ALL_ROWS:
            network_node[network] = label_node[label]

    # Build every scalar paid network in physical dependency order.  S7 is
    # replaced after all of its five required paid rails are available.
    original_s7_network = 281
    progress = True
    while progress:
        progress = False
        for network, network_drivers in sorted(drivers.items()):
            if network in network_node or network == original_s7_network:
                continue
            if len(values.get(network, ())) != 1:
                continue
            ordinary = [
                (index, pin)
                for index, pin in network_drivers
                if circuit.components[index].kind in OPS
            ]
            switches = [
                (index, pin)
                for index, pin in network_drivers
                if circuit.components[index].kind == 12
            ]
            if ordinary:
                if len(ordinary) != 1 or switches:
                    raise RuntimeError(f"network {network} mixes ordinary and tri-state outputs")
                index, _pin = ordinary[0]
                component = circuit.components[index]
                op, cost, delay = OPS[component.kind]
                input_pins = [
                    pin
                    for pin in positioned_pins(component, index)
                    if pin.direction == I
                ]
                input_networks = [compiled.pin_networks[(index, pin.name)] for pin in input_pins]
                if not all(item in network_node for item in input_networks):
                    continue
                args = [network_node[item] for item in input_networks]
                arrival = max(nodes[arg - 1]["arrival"] for arg in args) + delay
                network_node[network] = add_node(
                    op,
                    args,
                    cost=cost,
                    step_delay=delay,
                    arrival=arrival,
                    may_z=False,
                )
                progress = True
            elif switches:
                args: list[int] = []
                ready = True
                for index, _pin in switches:
                    enable_network = compiled.pin_networks[(index, "enable")]
                    data_network = compiled.pin_networks[(index, "in")]
                    if enable_network not in network_node or data_network not in network_node:
                        ready = False
                        break
                    args.extend((network_node[enable_network], network_node[data_network]))
                if not ready:
                    continue
                arrival = max(nodes[arg - 1]["arrival"] for arg in args) + 1
                network_node[network] = add_node(
                    "BUS",
                    args,
                    cost=len(args),
                    step_delay=1,
                    arrival=arrival,
                    may_z=True,
                )
                progress = True

    required_s7_networks = {
        "same_phase": 278,
        "both_one": 258,
        "shared_data": 207,
        "other_enable": 285,
        "p7": 271,
    }
    missing = {
        name: network for name, network in required_s7_networks.items() if network not in network_node
    }
    if missing:
        raise RuntimeError(f"S7 merge rails are not available: {missing}")
    same_phase = network_node[required_s7_networks["same_phase"]]
    both_one = network_node[required_s7_networks["both_one"]]
    shared_data = network_node[required_s7_networks["shared_data"]]
    other_enable = network_node[required_s7_networks["other_enable"]]
    p7 = network_node[required_s7_networks["p7"]]
    u_arrival = max(nodes[same_phase - 1]["arrival"], nodes[both_one - 1]["arrival"]) + 1
    merged_enable = add_node(
        "OR",
        [same_phase, both_one],
        cost=1,
        step_delay=1,
        arrival=u_arrival,
        may_z=False,
        label="human86.s7_merged_enable",
    )
    s7_args = [merged_enable, shared_data, other_enable, p7]
    network_node[original_s7_network] = add_node(
        "BUS",
        s7_args,
        cost=4,
        step_delay=1,
        arrival=max(nodes[arg - 1]["arrival"] for arg in s7_args) + 1,
        may_z=True,
        label="S7",
    )

    maker = next(
        (index, component)
        for index, component in enumerate(circuit.components)
        if component.kind == 16
    )
    maker_index, maker_component = maker
    sum_outputs = [
        network_node[compiled.pin_networks[(maker_index, f"in{bit}")]]
        for bit in range(8)
    ]
    carry_component = next(
        (index, component)
        for index, component in enumerate(circuit.components)
        if component.kind == 69 and component.user_label == "Carry out"
    )
    carry_index, _ = carry_component
    carry_network = compiled.pin_networks[(carry_index, "value")]
    outputs = [*sum_outputs, network_node[carry_network]]

    # Remove nodes outside the nine-output cone and densely renumber them.
    by_id = {node["id"]: node for node in nodes}
    live: set[int] = set()
    stack = list(outputs)
    while stack:
        node_id = stack.pop()
        if node_id in live:
            continue
        live.add(node_id)
        stack.extend(by_id[node_id]["args"])
    retained = [node for node in nodes if node["id"] in live]
    remap = {node["id"]: index + 1 for index, node in enumerate(retained)}
    normalized: list[dict[str, Any]] = []
    for node in retained:
        copied = dict(node)
        copied["id"] = remap[node["id"]]
        copied["args"] = [remap[arg] for arg in node["args"]]
        if copied["op"] == "BUS":
            owner = f"bus_{copied['id']}"
            copied["resolved_network"] = owner
            copied["drivers"] = [
                {
                    "enable": copied["args"][index],
                    "data": copied["args"][index + 1],
                    "owner": owner,
                }
                for index in range(0, len(copied["args"]), 2)
            ]
        normalized.append(copied)
    outputs = [remap[node_id] for node_id in outputs]
    by_id = {node["id"]: node for node in normalized}

    logical = materializer.logical_states(tuple(normalized))
    observed = [
        int(logical[node_id]["bits"]) & int(logical[node_id]["driven"]) & ALL_ROWS
        for node_id in outputs
    ]
    variables = tuple(materializer._variable(index) for index in range(17))
    carry = variables[16]
    expected_sum = []
    for left, right in zip(variables[:8], variables[8:16], strict=True):
        propagate = left ^ right
        expected_sum.append(propagate ^ carry)
        carry = (left & right) | (propagate & carry)
    expected = [*expected_sum, carry]
    mismatch_masks = [left ^ right for left, right in zip(observed, expected, strict=True)]
    mismatch_union = 0
    for value in mismatch_masks:
        mismatch_union |= value
    conflict = 0
    for state in logical.values():
        conflict |= int(state["conflict"])
    z_counts = [
        ((~int(logical[node_id]["driven"])) & ALL_ROWS).bit_count()
        for node_id in outputs
    ]
    output_arrivals = [by_id[node_id]["arrival"] for node_id in outputs]
    gate = sum(int(node["cost"]) for node in normalized)
    delay = max(output_arrivals)
    structural_hash = materializer._structural_sha256(by_id, tuple(outputs))

    factory_dag = {
        "outputs": outputs,
        "nodes": normalized,
        "live_node_count": len(normalized),
    }
    hash_payload = dict(factory_dag)
    factory_dag["sha256"] = hashlib.sha256(
        json.dumps(hash_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    payload = {
        "schema": "byte-adder-human86-s7-owner-merge-v1",
        "status": "sat",
        "source": {
            "path": str(SOURCE),
            "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        },
        "rewrite": {
            "removed": "one S7 Bit Switch",
            "added": "OR(n278, AND(Q6,P7))",
            "old_s7_owner_cost": 6,
            "new_s7_owner_plus_merge_cost": 5,
        },
        "metrics": {
            "gate": gate,
            "delay": delay,
            "energy": gate * delay,
            "output_arrivals": output_arrivals,
            "reachable_nodes": len(normalized),
            "structural_sha256": structural_hash,
        },
        "semantic": {
            "truth_table_rows": 131072,
            "mismatch_count_by_output": [mask.bit_count() for mask in mismatch_masks],
            "mismatch_union_count": mismatch_union.bit_count(),
            "conflict_assignment_count": conflict.bit_count(),
            "z_assignment_count_by_output": z_counts,
            "output_vector_sha256": hashlib.sha256(
                b"".join(value.to_bytes(131072 // 8, "little") for value in observed)
            ).hexdigest(),
            "sequence_domain": None,
        },
        "factory_dag": factory_dag,
    }
    if (gate, delay) != (86, 6):
        raise RuntimeError(f"unexpected score: {gate}/{delay}")
    if mismatch_union or conflict:
        raise RuntimeError(
            f"human86 verification failed: mismatch={mismatch_union.bit_count()} "
            f"conflict={conflict.bit_count()}"
        )
    return payload


def main() -> int:
    payload = build()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.write_text(encoded, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "sha256": hashlib.sha256(encoded.encode()).hexdigest(),
                "metrics": payload["metrics"],
                "semantic": payload["semantic"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
