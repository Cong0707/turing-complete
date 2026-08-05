"""只读反解用户提供的 Switch 103/5 B 字节加法器样本。

本脚本不会启动游戏，也不会读取或写入正式存档。它使用仓库当前 v15
解析器、真实引脚表和三态 BUS 语义，对 131072 个 A/B/Cin 输入状态做一次
位并行完整重放，并输出逐元件 DAG、网络、arrival、Switch owner 和样本差异。
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tc_save_lab.codec import decode_v15, encode_v15  # noqa: E402
from tc_save_lab.analysis import wire_points  # noqa: E402
from tc_save_lab.pins import I, O, T, analyze_connectivity, positioned_pins  # noqa: E402
from tc_save_lab.simulate import CONSTANT_KINDS, SINK_KINDS, SOURCE_KINDS  # noqa: E402


RAW = HERE.parent / "raw" / "extracted"
SAMPLE_B = RAW / "Switch 103 5 B" / "circuit.data"
SAMPLE_A = RAW / "Switch 103 5 A" / "circuit.data"
INDEPENDENT = ROOT / ".research" / "byte_adder_d5_frontier" / "patchouli103-d5-audit-v1.json"
OUTPUT_JSON = HERE / "audit_103d5b.json"
OUTPUT_DAG = HERE / "完整逻辑DAG.md"
OUTPUT_REPORT = HERE / "反解报告.md"

ROWS = 256 * 256 * 2
ALL = (1 << ROWS) - 1

KIND_NAMES = {
    1: "OFF",
    2: "ON",
    3: "NOT",
    4: "AND",
    5: "AND3",
    6: "NAND",
    7: "OR",
    8: "OR3",
    9: "NOR",
    10: "XOR",
    11: "XNOR",
    12: "SWITCH",
    16: "MAKER8",
    17: "SPLITTER8",
    61: "INPUT",
    69: "OUTPUT",
    109: "SPLITTER2",
    111: "MAKER2",
}

KIND_COST_DELAY = {
    1: (0, 0),
    2: (0, 0),
    3: (1, 1),
    4: (1, 1),
    5: (3, 2),
    6: (1, 1),
    7: (1, 1),
    8: (3, 2),
    9: (1, 1),
    10: (3, 2),
    11: (5, 4),
    12: (2, 1),
    16: (0, 0),
    17: (0, 0),
    61: (0, 0),
    69: (0, 0),
    109: (0, 0),
    111: (0, 0),
}


def pattern(half_period: int) -> int:
    block = "0" * half_period + "1" * half_period
    return int(block * (ROWS // (2 * half_period)), 2)


def input_vectors() -> dict[str, tuple[int, ...]]:
    return {
        "Carry in": (pattern(1),),
        "B": tuple(pattern(2 << bit) for bit in range(8)),
        "A": tuple(pattern(512 << bit) for bit in range(8)),
    }


def inv(value: int) -> int:
    return (~value) & ALL


def pin_width(circuit, component_index: int, pin_name: str) -> int:
    for pin in positioned_pins(circuit.components[component_index], component_index):
        if pin.name == pin_name:
            return pin.width
    raise KeyError((component_index, pin_name))


def known_relations(inputs: dict[str, tuple[int, ...]]) -> dict[int, list[str]]:
    a = inputs["A"]
    b = inputs["B"]
    cin = inputs["Carry in"][0]
    relations: dict[str, int] = {"Cin": cin, "nCin": inv(cin)}
    carry = cin
    for bit in range(8):
        g = a[bit] & b[bit]
        q = inv(a[bit] | b[bit])
        p = a[bit] ^ b[bit]
        relations.update(
            {
                f"A{bit}": a[bit],
                f"B{bit}": b[bit],
                f"G{bit}": g,
                f"Q{bit}": q,
                f"P{bit}": p,
                f"nP{bit}": inv(p),
                f"V{bit}": a[bit] | b[bit],
                f"N{bit}": inv(g),
                f"C{bit}": carry,
                f"nC{bit}": inv(carry),
                f"S{bit}": p ^ carry,
            }
        )
        carry = g | (p & carry)
    relations["C8"] = carry
    relations["nC8"] = inv(carry)

    # 连续区间 carry 描述符，用于识别人类前缀结构。
    for low in range(8):
        group_g = a[low] & b[low]
        group_p = a[low] ^ b[low]
        for high in range(low + 1, 8):
            p = a[high] ^ b[high]
            group_g = (a[high] & b[high]) | (p & group_g)
            group_p &= p
            group_k = inv(group_g | group_p)
            relations[f"G{high}:{low}"] = group_g
            relations[f"P{high}:{low}"] = group_p
            relations[f"K{high}:{low}"] = group_k

    by_value: dict[int, list[str]] = defaultdict(list)
    for name, value in relations.items():
        by_value[value].append(name)
    return {value: sorted(names) for value, names in by_value.items()}


@dataclass(frozen=True)
class EvalResult:
    inputs: dict[str, tuple[int, ...]]
    values: dict[int, tuple[int, ...]]
    driven: dict[int, tuple[int, ...]]
    arrivals: dict[int, int]
    conflict_rows: int


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left = self.find(left)
        right = self.find(right)
        if left != right:
            self.parent[right] = left


@dataclass(frozen=True)
class Compiled:
    pin_networks: dict[tuple[int, str], int]
    network_driver_counts: dict[int, int]
    network_pins: dict[int, list[object]]
    unconnected_pins: tuple[object, ...]


def compile_allow_implicit_zero(circuit) -> Compiled:
    """按 v15 端点规则编译，同时保留 Maker2 的故意悬空零输入。

    人工样本使用 `Maker2.in0` 悬空来注入数值零，并不把它接到 OFF 元件；
    同一对免费元件的 `Splitter2.out0` 也故意不消费。仓库严格 `_compile`
    会拒绝任意悬空 pin，因此这里显式记录而不把它误报成损坏。
    """

    union = UnionFind(len(circuit.wires))
    endpoint_owners: dict[tuple[int, int], list[int]] = defaultdict(list)
    endpoints: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        pair = (points[0], points[-1])
        endpoints.append(pair)
        endpoint_owners[pair[0]].append(index)
        endpoint_owners[pair[1]].append(index)
    for owners in endpoint_owners.values():
        for index in owners[1:]:
            union.union(owners[0], index)

    root_by_endpoint: dict[tuple[int, int], int] = {}
    for index, pair in enumerate(endpoints):
        root = union.find(index)
        root_by_endpoint[pair[0]] = root
        root_by_endpoint[pair[1]] = root

    pin_networks: dict[tuple[int, str], int] = {}
    network_pins: dict[int, list[object]] = defaultdict(list)
    unconnected = []
    for index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, index):
            root = root_by_endpoint.get(pin.position)
            if root is None:
                unconnected.append(pin)
                continue
            pin_networks[(index, pin.name)] = root
            network_pins[root].append(pin)
    driver_counts = {
        network: sum(pin.direction in {O, T} for pin in pins)
        for network, pins in network_pins.items()
    }
    return Compiled(pin_networks, driver_counts, dict(network_pins), tuple(unconnected))


def evaluate(circuit) -> tuple[object, EvalResult]:
    compiled = compile_allow_implicit_zero(circuit)
    inputs = input_vectors()
    values: dict[int, tuple[int, ...]] = {}
    driven: dict[int, tuple[int, ...]] = {}
    resolved: dict[int, int] = defaultdict(int)
    arrivals: dict[int, int] = {}
    conflict_rows = 0

    def drive(
        component_index: int,
        pin_name: str,
        value: int | Iterable[int],
        masks: int | Iterable[int] | None = None,
    ) -> None:
        nonlocal conflict_rows
        network = compiled.pin_networks.get((component_index, pin_name))
        if network is None:
            return
        width = pin_width(circuit, component_index, pin_name)
        lanes = (value,) * width if isinstance(value, int) else tuple(value)
        if masks is None:
            lane_masks = (ALL,) * width
        elif isinstance(masks, int):
            lane_masks = (masks,) * width
        else:
            lane_masks = tuple(masks)
        old_values = values.get(network, (0,) * width)
        old_masks = driven.get(network, (0,) * width)
        if len(lanes) != width or len(lane_masks) != width:
            raise RuntimeError("lane width mismatch")
        for old_value, new_value, old_mask, new_mask in zip(old_values, lanes, old_masks, lane_masks):
            conflict_rows |= (old_value ^ new_value) & old_mask & new_mask
        values[network] = tuple(
            (old_value & old_mask) | (new_value & new_mask)
            for old_value, new_value, old_mask, new_mask in zip(old_values, lanes, old_masks, lane_masks)
        )
        driven[network] = tuple(old_mask | new_mask for old_mask, new_mask in zip(old_masks, lane_masks))
        resolved[network] += 1

    def ready(network: int) -> bool:
        return resolved[network] > 0 and resolved[network] == compiled.network_driver_counts.get(network, 0)

    def read(index: int, pin_name: str) -> tuple[int, ...]:
        network = compiled.pin_networks[(index, pin_name)]
        if not ready(network):
            raise RuntimeError(f"network {network} is not ready")
        return tuple(value & mask for value, mask in zip(values[network], driven[network]))

    pending: set[int] = set()
    for index, component in enumerate(circuit.components):
        if component.kind in SOURCE_KINDS:
            raw = inputs[component.user_label]
            output_pins = [
                pin for pin in positioned_pins(component, index) if pin.direction in {O, T}
            ]
            if len(output_pins) == 1:
                drive(index, output_pins[0].name, raw)
            else:
                for bit, pin in enumerate(output_pins):
                    drive(index, pin.name, raw[bit])
            arrivals[index] = 0
        elif component.kind in CONSTANT_KINDS:
            number = component.init_data if component.kind == 46 else int(component.kind == 2)
            drive(index, "out", number)
            arrivals[index] = 0
        elif component.kind not in SINK_KINDS:
            pending.add(index)

    while pending:
        progressed = False
        for index in tuple(pending):
            component = circuit.components[index]
            input_pins = [pin for pin in positioned_pins(component, index) if pin.direction == I]
            input_networks = [
                compiled.pin_networks[(index, pin.name)]
                for pin in input_pins
                if (index, pin.name) in compiled.pin_networks
            ]
            if not all(ready(network) for network in input_networks):
                continue
            input_values = {
                pin.name: (
                    read(index, pin.name)
                    if (index, pin.name) in compiled.pin_networks
                    else (0,) * pin.width
                )
                for pin in input_pins
            }
            input_arrivals: list[int] = []
            for network in input_networks:
                for source_index, source_component in enumerate(circuit.components):
                    for source_pin in positioned_pins(source_component, source_index):
                        if source_pin.direction not in {O, T}:
                            continue
                        if compiled.pin_networks.get((source_index, source_pin.name)) == network:
                            input_arrivals.append(arrivals[source_index])
            arrivals[index] = max(input_arrivals, default=0) + KIND_COST_DELAY[component.kind][1]

            def bit(name: str, lane: int = 0) -> int:
                return input_values[name][lane]

            kind = component.kind
            if kind == 12:
                enable = bit("enable")
                drive(index, "out", bit("in"), enable)
            elif kind in {16, 111}:
                width = 8 if kind == 16 else 2
                drive(index, "out", tuple(bit(f"in{lane}") for lane in range(width)))
            elif kind in {17, 109}:
                width = 8 if kind == 17 else 2
                for lane in range(width):
                    drive(index, f"out{lane}", bit("in", lane))
            else:
                left = bit("in0")
                right = bit("in1") if "in1" in input_values else 0
                if kind == 3:
                    result = inv(bit("in"))
                elif kind in {4, 5}:
                    result = left & right
                    if "in2" in input_values:
                        result &= bit("in2")
                elif kind == 6:
                    result = inv(left & right)
                elif kind in {7, 8}:
                    result = left | right
                    if "in2" in input_values:
                        result |= bit("in2")
                elif kind == 9:
                    result = inv(left | right)
                elif kind == 10:
                    result = left ^ right
                elif kind == 11:
                    result = inv(left ^ right)
                else:
                    raise RuntimeError(f"unsupported kind {kind}")
                drive(index, "out", result)
            pending.remove(index)
            progressed = True
        if not progressed:
            raise RuntimeError(f"unresolved components: {sorted(pending)}")

    return compiled, EvalResult(inputs, values, driven, arrivals, conflict_rows)


def build_network_records(circuit, compiled, result: EvalResult) -> tuple[dict[int, object], dict[int, object]]:
    known = known_relations(result.inputs)
    drivers: dict[int, list[dict[str, object]]] = defaultdict(list)
    sinks: dict[int, list[dict[str, object]]] = defaultdict(list)
    for index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, index):
            network = compiled.pin_networks.get((index, pin.name))
            if network is None:
                continue
            record = {
                "component": index,
                "kind": KIND_NAMES.get(component.kind, str(component.kind)),
                "pin": pin.name,
                "width": pin.width,
            }
            (drivers if pin.direction in {O, T} else sinks)[network].append(record)

    networks: dict[int, object] = {}
    for network in sorted(set(drivers) | set(sinks)):
        lane_values = result.values.get(network, ())
        lane_masks = result.driven.get(network, ())
        lanes = []
        for lane, (value, mask) in enumerate(zip(lane_values, lane_masks)):
            normalized = value & mask
            lanes.append(
                {
                    "lane": lane,
                    "labels": known.get(normalized, []),
                    "one_rows": normalized.bit_count(),
                    "driven_rows": mask.bit_count(),
                    "z_rows": ROWS - mask.bit_count(),
                }
            )
        networks[network] = {
            "drivers": drivers.get(network, []),
            "sinks": sinks.get(network, []),
            "lanes": lanes,
        }
    return networks, {"drivers": drivers, "sinks": sinks}


def source_ref(network: int, lane: int, networks: dict[int, object]) -> str:
    record = networks[network]
    labels = record["lanes"][lane]["labels"] if lane < len(record["lanes"]) else []
    if labels:
        return "/".join(labels[:4])
    drivers = record["drivers"]
    if not drivers:
        return f"net{network}[{lane}]"
    rendered = []
    for driver in drivers:
        suffix = f".{driver['pin']}" if driver["pin"] != "out" else ""
        rendered.append(f"node{driver['component']}{suffix}")
    return "BUS(" + ",".join(rendered) + ")" if len(rendered) > 1 else rendered[0]


def component_expression(index: int, circuit, compiled, networks: dict[int, object]) -> tuple[list[str], str]:
    component = circuit.components[index]
    inputs = []
    for pin in positioned_pins(component, index):
        if pin.direction != I:
            continue
        network = compiled.pin_networks.get((index, pin.name))
        if network is None:
            inputs.append(f"{pin.name}=0")
            continue
        width = len(networks[network]["lanes"])
        value = (
            "[" + ",".join(source_ref(network, lane, networks) for lane in range(width)) + "]"
            if width > 1
            else source_ref(network, 0, networks)
        )
        inputs.append(f"{pin.name}={value}")
    op = KIND_NAMES.get(component.kind, str(component.kind))
    if component.kind == 12:
        expr = f"SW({inputs[0].split('=',1)[1]},{inputs[1].split('=',1)[1]})"
    elif component.kind in {16, 111}:
        expr = f"PACK({','.join(item.split('=',1)[1] for item in inputs)})"
    elif component.kind in {17, 109}:
        expr = f"SPLIT({inputs[0].split('=',1)[1]})"
    elif len(inputs) == 1:
        expr = f"{op}({inputs[0].split('=',1)[1]})"
    else:
        expr = f"{op}({','.join(item.split('=',1)[1] for item in inputs)})"
    return inputs, expr


def audit_one(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    circuit = decode_v15(payload)
    compiled, evaluated = evaluate(circuit)
    networks, _ = build_network_records(circuit, compiled, evaluated)

    components = []
    for index, component in enumerate(circuit.components):
        input_records, expression = component_expression(index, circuit, compiled, networks)
        output_records = []
        for pin in positioned_pins(component, index):
            if pin.direction not in {O, T}:
                continue
            network = compiled.pin_networks.get((index, pin.name))
            if network is None:
                continue
            output_records.append({"pin": pin.name, "network": network, "lanes": networks[network]["lanes"]})
        components.append(
            {
                "index": index,
                "permanent_id": component.permanent_id,
                "kind": component.kind,
                "kind_name": KIND_NAMES.get(component.kind, str(component.kind)),
                "position": list(component.position),
                "rotation": component.rotation,
                "label": component.user_label,
                "cost": KIND_COST_DELAY.get(component.kind, (0, 0))[0],
                "arrival": evaluated.arrivals.get(index, 0),
                "inputs": input_records,
                "expression": expression,
                "outputs": output_records,
            }
        )

    outputs = []
    truth_mismatch_rows = 0
    a = evaluated.inputs["A"]
    b = evaluated.inputs["B"]
    cin = evaluated.inputs["Carry in"][0]
    expected_carry = cin
    expected_sum = []
    for bit in range(8):
        p = a[bit] ^ b[bit]
        expected_sum.append(p ^ expected_carry)
        expected_carry = (a[bit] & b[bit]) | (p & expected_carry)

    for index, component in enumerate(circuit.components):
        if component.kind not in SINK_KINDS:
            continue
        pin = next(pin for pin in positioned_pins(component, index) if pin.direction == I)
        network = compiled.pin_networks[(index, pin.name)]
        lane_values = evaluated.values[network]
        lane_masks = evaluated.driven[network]
        expected = expected_sum if component.user_label == "Output" else [expected_carry]
        lane_mismatches = []
        for lane, wanted in enumerate(expected):
            actual = lane_values[lane] & lane_masks[lane]
            mismatch = actual ^ wanted
            truth_mismatch_rows |= mismatch
            lane_mismatches.append(mismatch.bit_count())
        driver_arrival = max(
            evaluated.arrivals[driver["component"]] for driver in networks[network]["drivers"]
        )
        outputs.append(
            {
                "component": index,
                "label": component.user_label,
                "network": network,
                "arrival": driver_arrival,
                "lane_mismatch_rows": lane_mismatches,
                "lanes": networks[network]["lanes"],
                "drivers": networks[network]["drivers"],
            }
        )

    kind_counts = Counter(component.kind for component in circuit.components)
    recomputed_gate = sum(KIND_COST_DELAY.get(component.kind, (0, 0))[0] for component in circuit.components)
    switch_components = [component for component in components if component["kind"] == 12]
    switch_output_networks = Counter(
        component["outputs"][0]["network"] for component in switch_components if component["outputs"]
    )
    owner_networks = {
        str(network): networks[network]
        for network, count in switch_output_networks.items()
        if count > 1
    }
    live_logic = [component for component in components if component["cost"]]
    structural_signature = [
        {
            "kind": component["kind_name"],
            "arrival": component["arrival"],
            "inputs": component["inputs"],
            "output_labels": [lane["labels"] for output in component["outputs"] for lane in output["lanes"]],
        }
        for component in live_logic
    ]
    return {
        "source": {
            "path": str(path),
            "bytes": len(payload),
            "sha256": sha256(payload).hexdigest().upper(),
            "canonical_reencode_byte_identical": encode_v15(circuit) == payload,
            "decode_encode_decode_object_identical": decode_v15(encode_v15(circuit)) == circuit,
        },
        "declared": {"gate": circuit.gate, "delay": circuit.delay, "energy": circuit.energy},
        "recomputed": {
            "gate": recomputed_gate,
            "delay": max(output["arrival"] for output in outputs),
            "energy": recomputed_gate * max(output["arrival"] for output in outputs),
            "truth_mismatch_rows": truth_mismatch_rows.bit_count(),
            "bus_conflict_rows": evaluated.conflict_rows.bit_count(),
        },
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "kind_counts": {str(kind): count for kind, count in sorted(kind_counts.items())},
        "connectivity": analyze_connectivity(circuit),
        "outputs": outputs,
        "resolved_switch_owner_networks": owner_networks,
        "networks": {str(network): record for network, record in networks.items()},
        "components": components,
        "structural_signature_sha256": sha256(
            json.dumps(structural_signature, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest().upper(),
    }


def render_dag(b: dict[str, object]) -> str:
    lines = [
        "# Switch 103/5 B 完整逻辑 DAG",
        "",
        "本表按 v15 物理元件索引列出。`arrival` 使用游戏成本：普通门 1、Bit Switch 1、Maker/Splitter 0。",
        "多只 Switch 输出到同一网络时，表达式中的 `BUS(...)` 表示真实三态 resolved owner。",
        "",
        "| idx | 元件 | cost | arrival | 位置 | 输入 | 输出标签 |",
        "|---:|---|---:|---:|---|---|---|",
    ]
    for component in b["components"]:
        if component["kind"] in {61, 69}:
            continue
        outputs = []
        for output in component["outputs"]:
            lane_text = []
            for lane in output["lanes"]:
                label = "/".join(lane["labels"][:5]) or f"net{output['network']}[{lane['lane']}]"
                if lane["z_rows"]:
                    label += f"; Z={lane['z_rows']}"
                lane_text.append(label)
            outputs.append(f"net{output['network']}=" + ", ".join(lane_text))
        expr = str(component["expression"]).replace("|", "\\|")
        out = "; ".join(outputs).replace("|", "\\|")
        lines.append(
            f"| {component['index']} | {component['kind_name']} | {component['cost']} | "
            f"{component['arrival']} | `{tuple(component['position'])}` | `{expr}` | `{out}` |"
        )
    return "\n".join(lines) + "\n"


def compare(a: dict[str, object], b: dict[str, object], independent: dict[str, object]) -> dict[str, object]:
    def owner_summary(item: dict[str, object]) -> list[dict[str, object]]:
        result = []
        for network, record in item["resolved_switch_owner_networks"].items():
            result.append(
                {
                    "network": int(network),
                    "driver_count": len(record["drivers"]),
                    "labels": [lane["labels"] for lane in record["lanes"]],
                    "z_rows": [lane["z_rows"] for lane in record["lanes"]],
                }
            )
        return sorted(result, key=lambda value: value["network"])

    independent_nodes = independent["factory_dag"]["nodes"]
    independent_summary = {
        "metrics": independent["metrics"],
        "semantic": independent["semantic"],
        "operation_counts": dict(sorted(Counter(node["op"] for node in independent_nodes).items())),
        "switch_count": sum(len(node.get("drivers", ())) for node in independent_nodes if node["op"] == "BUS"),
        "ordinary_weighted_gate": sum(node["cost"] for node in independent_nodes if node["op"] != "BUS"),
        "bus_weighted_gate": sum(node["cost"] for node in independent_nodes if node["op"] == "BUS"),
    }
    return {
        "A_vs_B": {
            "same_bytes": a["source"]["sha256"] == b["source"]["sha256"],
            "kind_count_delta_B_minus_A": {
                str(kind): int(b["kind_counts"].get(str(kind), 0)) - int(a["kind_counts"].get(str(kind), 0))
                for kind in sorted({int(value) for value in a["kind_counts"]} | {int(value) for value in b["kind_counts"]})
                if int(b["kind_counts"].get(str(kind), 0)) != int(a["kind_counts"].get(str(kind), 0))
            },
            "structural_signature_equal": a["structural_signature_sha256"] == b["structural_signature_sha256"],
            "A_owner_summary": owner_summary(a),
            "B_owner_summary": owner_summary(b),
            "A_output_arrivals": [output["arrival"] for output in a["outputs"]],
            "B_output_arrivals": [output["arrival"] for output in b["outputs"]],
        },
        "repository_independent_103d5": independent_summary,
    }


def migration_contracts() -> dict[str, object]:
    """固定公式复核 B 的三处结构及其迁移到 84/6 的完整账本。"""

    inputs = input_vectors()
    a = inputs["A"]
    b = inputs["B"]
    cin = inputs["Carry in"][0]
    g = tuple(a[index] & b[index] for index in range(8))
    q = tuple(inv(a[index] | b[index]) for index in range(8))
    v = tuple(a[index] | b[index] for index in range(8))
    n = tuple(inv(g[index]) for index in range(8))
    p = tuple(a[index] ^ b[index] for index in range(8))
    carry = [cin]
    for index in range(8):
        carry.append(g[index] | (p[index] & carry[-1]))

    def owner(drivers: list[tuple[int, int]]) -> tuple[int, int, int]:
        value = 0
        driven = 0
        conflict = 0
        for left, (enable, data) in enumerate(drivers):
            value |= enable & data
            driven |= enable
            for other_enable, other_data in drivers[:left]:
                conflict |= enable & other_enable & (data ^ other_data)
        return value & driven, driven, conflict

    # 当前 84 的低位稀疏轨。
    m0, _m0_driven, _m0_conflict = owner([(a[0], cin), (b[0], cin)])
    c1 = g[0] | m0
    c2, _c2_driven, _c2_conflict = owner(
        [(g[1], v[1]), (g[0], v[1]), (m0, v[1])]
    )
    n23 = inv(q[2] | q[3])
    b23, b23_driven, b23_conflict = owner([(c2, n23), (g[2], n23)])
    c4_current = g[3] | b23

    # 样本 B 的 C4@3 producer。
    w23, w23_driven, w23_conflict = owner([(g[3], v[3]), (v[2], v[3])])
    r23 = g[2] | g[3]
    c4_b, c4_b_driven, c4_b_conflict = owner([(r23, w23), (c2, w23)])

    v45 = inv(q[4] | q[5])
    d45 = g[5] | v45
    k34 = g[3] | g[4]
    g345 = k34 | g[5]
    c6_current, c6_current_driven, c6_current_conflict = owner(
        [(b23, d45), (g345, d45)]
    )
    e45 = g[4] | g[5]
    c6_b, c6_b_driven, c6_b_conflict = owner([(e45, d45), (c4_b, d45)])
    c6_hybrid, c6_hybrid_driven, c6_hybrid_conflict = owner(
        [(e45, d45), (c4_current, d45)]
    )

    np4 = g[4] | q[4]
    u_b = c4_current | np4
    h5 = inv(p[5] | q[4])
    r1_b = inv(e45 | c4_current)
    s5_b, s5_b_driven, s5_b_conflict = owner(
        [(q[4], p[5]), (h5, u_b), (r1_b, p[5])]
    )

    u45 = b23 | k34
    t5 = u45 & h5
    j5 = inv(q[5] | c6_current)
    s5_current = t5 | j5

    def mismatch(actual: int, expected: int) -> int:
        return (actual ^ expected).bit_count()

    def missing_one(expected: int, driven: int) -> int:
        return (expected & ~driven & ALL).bit_count()

    return {
        "truth_rows": ROWS,
        "C4_owner": {
            "sample_B_formula": "W23=BUS(SW(G3,V3),SW(V2,V3)); R23=G2|G3; C4=BUS(SW(R23,W23),SW(C2,W23))",
            "mismatch_rows": mismatch(c4_b, carry[4]),
            "conflict_rows": (w23_conflict | c4_b_conflict).bit_count(),
            "missing_one_rows": missing_one(carry[4], c4_b_driven),
            "raw_z_rows": ROWS - c4_b_driven.bit_count(),
            "current_84_producer": {"gate": 6, "arrival": 4, "parts": "N23 1 + B23 owner 4 + final OR 1"},
            "sample_B_producer": {"gate": 9, "arrival": 3, "parts": "W23 owner 4 + R23 1 + C4 owner 4"},
            "delta_gate": 3,
        },
        "D45_C6_owner": {
            "sample_B_formula": "V45=~(Q4|Q5); D45=G5|V45; E45=G4|G5; C6=BUS(SW(E45,D45),SW(C4,D45))",
            "mismatch_rows_with_B_C4": mismatch(c6_b, carry[6]),
            "conflict_rows_with_B_C4": c6_b_conflict.bit_count(),
            "missing_one_rows_with_B_C4": missing_one(carry[6], c6_b_driven),
            "mismatch_rows_with_current_C4": mismatch(c6_hybrid, carry[6]),
            "conflict_rows_with_current_C4": c6_hybrid_conflict.bit_count(),
            "current_84_core": {"gate": 8, "arrival": 4, "parts": "K34 1 + G345 1 + V45 1 + D45 1 + owner 4"},
            "sample_B_core_if_C4_at_3": {"gate": 7, "arrival": 4, "parts": "E45 1 + V45 1 + D45 1 + owner 4"},
            "sample_B_core_with_current_C4_at_4": {"gate": 7, "arrival": 5, "valid_for_84_high_tail": False},
            "combined_C4_plus_C6": {
                "current_84_gate": 14,
                "sample_B_gate": 16,
                "delta_gate": 2,
                "conclusion": "C6 独看省 1 门，但为取得 C4@3 必须先多付 3 门，整体反而增加 2 门。",
            },
        },
        "S5_three_switch_owner": {
            "sample_B_formula": "S5=BUS(SW(Q4,P5),SW(H5,U),SW(R1,P5)); H5=~(P5|Q4); U=C4|nP4; R1=~(C4|G4|G5)",
            "mismatch_rows": mismatch(s5_b, p[5] ^ carry[5]),
            "conflict_rows": s5_b_conflict.bit_count(),
            "missing_one_rows": missing_one(p[5] ^ carry[5], s5_b_driven),
            "raw_z_rows": ROWS - s5_b_driven.bit_count(),
            "current_84_formula_mismatch_rows": mismatch(s5_current, p[5] ^ carry[5]),
            "current_84_macro": {"gate": 5, "arrival": 6, "parts": "U45,H5,T5,J5,OR"},
            "optimistic_B_marginal_when_U_and_R1_are_already_paid": {
                "gate": 7,
                "arrival_with_current_C4": 6,
                "parts": "H5 1 + three Switch 6",
                "delta_gate": 2,
            },
            "standalone_B_macro_from_paid_G/Q/P/C4": {
                "gate": 11,
                "arrival": 6,
                "parts": "nP4,U,H5,E45,R1 five ordinary + three Switch 6",
                "delta_gate": 6,
            },
        },
        "shared_state_checks": {
            "current_C4_mismatch_rows": mismatch(c4_current, carry[4]),
            "current_C6_mismatch_rows": mismatch(c6_current, carry[6]),
            "current_B23_conflict_rows": b23_conflict.bit_count(),
            "current_C6_conflict_rows": c6_current_conflict.bit_count(),
            "B_negative_reason_identity_mismatch_rows": mismatch(
                inv(c6_hybrid), inv(d45) | r1_b
            ),
        },
        "migration_conclusion": {
            "deterministic_84_to_83_improvement_found": False,
            "reason": "B 的 1 门 C6 局部优势完全依赖 C4@3；连同 B 的 C4 producer 后净增 2 门。三 Switch S5 即使把 U/R1 视为免费共享，仍比当前五门 S5 多 2 门。",
        },
    }


def main() -> int:
    a = audit_one(SAMPLE_A)
    b = audit_one(SAMPLE_B)
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    result = {
        "schema": "byte-adder-frontier-sample-103d5b-audit-v1",
        "sample_B": b,
        "sample_A_summary": {
            key: a[key]
            for key in (
                "source",
                "declared",
                "recomputed",
                "component_count",
                "wire_count",
                "kind_counts",
                "outputs",
                "resolved_switch_owner_networks",
                "structural_signature_sha256",
            )
        },
        "comparison": compare(a, b, independent),
        "migration_to_84d6": migration_contracts(),
    }
    OUTPUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUTPUT_DAG.write_text(render_dag(b), encoding="utf-8", newline="\n")
    print(json.dumps({"B": b["recomputed"], "A": a["recomputed"]}, ensure_ascii=False))
    print(OUTPUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
