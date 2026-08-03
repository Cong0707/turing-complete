"""只读复原公开仓库中的 legacy v6 Byte Adder 电路。

脚本不会启动游戏、不会写正式存档，也不会修改迁移项目。它只会：

1. 用 turing-complete-migration 的 v6 解析器读取历史文件；
2. 为当前分析器生成接口位置已校正的临时 v15 副本；
3. 以 2^17 位并行真值表重算语义、三态冲突和当前成本/延迟；
4. 输出逐文件清单和 Low-Delay 系列的带语义网络表。

旧版 ``LevelInput8``/``LevelOutput8`` 的针脚离中心只有 1 格，而当前
``Level Input Word``/``Level Output Word`` 的针脚离中心 3 格。直接转换虽能
往返解析，却会让旧导线错开 2 格。因此这里仅在临时副本中平移接口中心，
不改变内部门和导线；这使当前 pin 表可以准确复原旧拓扑。
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from hashlib import sha256
import importlib
import json
from pathlib import Path
import shutil
import sys
from typing import Iterable


PROJECT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = (
    PROJECT
    / "examples"
    / "rng"
    / "research"
    / "archive"
    / "rng_public_search"
)
MIGRATION_SRC = Path(r"D:\Develop\Other\turing-complete-migration\src")
OUTPUT_ROOT = Path(__file__).resolve().parent
V15_ROOT = OUTPUT_ROOT / "temp_v15"
INVENTORY_PATH = OUTPUT_ROOT / "legacy_byte_adder_inventory.json"
TOPOLOGY_PATH = OUTPUT_ROOT / "legacy_low_delay_topologies.json"

sys.path.insert(0, str(MIGRATION_SRC))
sys.path.insert(0, str(PROJECT / "src"))

legacy_v6 = importlib.import_module("turing_complete_migration.legacy_v6")

from tc_save_lab.analysis import wire_points  # noqa: E402
from tc_save_lab.codec import decode_v15  # noqa: E402
from tc_save_lab.pins import I, O, T, positioned_pins, rotate_offset  # noqa: E402


VARIABLES = 17
ASSIGNMENTS = 1 << VARIABLES
ALL = (1 << ASSIGNMENTS) - 1

# 当前 2.1.x 的合法基础元件成本。Splitter/Maker 和关卡接口为 0/0。
# Full Adder 只出现在 Default 历史链中。当前账号 levels.txt 的可导入前沿
# 是 16/8；旧头 88/80 仅说明当年使用过 11/10，不能覆盖当前运行时成本。
# 低延迟两套候选不依赖 Full Adder。
GATE_COST = {
    1: 0,   # Off
    2: 0,   # On
    3: 1,   # Not
    4: 1,   # And
    7: 1,   # Or
    10: 3,  # Xor
    11: 3,  # Xnor
    12: 2,  # Bit Switch
    15: 16, # Full Adder：当前账号已保存前沿
    16: 0,  # Maker8
    17: 0,  # Splitter8
    40: 0,
    60: 0,
    61: 0,
    68: 0,
    69: 0,
}

DELAY_COST = {
    1: 0,
    2: 0,
    3: 1,
    4: 1,
    7: 1,
    10: 2,
    11: 2,
    12: 1,
    15: 8,
    16: 0,
    17: 0,
    40: 0,
    60: 0,
    61: 0,
    68: 0,
    69: 0,
}

CURRENT_KIND_NAMES = {
    1: "Off",
    2: "On",
    3: "Not",
    4: "And",
    7: "Or",
    10: "Xor",
    11: "Xnor",
    12: "BitSwitch",
    15: "FullAdder",
    16: "Maker8",
    17: "Splitter8",
    40: "LevelOutput8Pin",
    60: "LevelInput1",
    61: "LevelInputWord",
    68: "LevelOutput1",
    69: "LevelOutputWord",
}


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
class Signal:
    bits: tuple[int, ...]
    driven: int
    delay: int
    conflict: int = 0


@dataclass(frozen=True)
class Compiled:
    pins: dict[tuple[int, str], object]
    pin_network: dict[tuple[int, str], int]
    network_pins: dict[int, tuple[object, ...]]
    endpoint_non_pin_count: int
    unconnected_inputs: tuple[tuple[int, str], ...]


def variable(index: int) -> int:
    if index < 3:
        byte = (0xAA, 0xCC, 0xF0)[index]
        return int.from_bytes(bytes([byte]) * (ASSIGNMENTS // 8), "little")
    block = 1 << (index - 3)
    data = (bytes(block) + bytes([0xFF]) * block) * (
        ASSIGNMENTS // (16 * block)
    )
    return int.from_bytes(data, "little")


def normal(bits: Iterable[int], delay: int) -> Signal:
    return Signal(tuple(value & ALL for value in bits), ALL, delay)


def zero(width: int = 1) -> Signal:
    return Signal((0,) * width, 0, 0)


def _translated_position(
    position: tuple[int, int], rotation: int, local_delta: tuple[int, int]
) -> tuple[int, int]:
    dx, dy = rotate_offset(local_delta, rotation)
    return (position[0] + dx, position[1] + dy)


def semantic_v15(legacy: object) -> bytes:
    """生成内部拓扑不变、当前接口针脚对齐旧端点的临时 v15。"""

    current = legacy_v6.convert_legacy_circuit(
        legacy,
        strip_level_interfaces=False,
    )
    if len(current.components) != len(legacy.components):
        raise RuntimeError("本数据集不应包含被删除的 legacy 元件")

    components = []
    for old, new in zip(legacy.components, current.components):
        if old.kind == 241:  # old LevelInput8: local output (+1, 0)
            label = "A" if old.permanent_id == 1 else "B"
            new = replace(
                new,
                position=_translated_position(new.position, new.rotation, (-2, 0)),
                user_label=label,
            )
        elif old.kind == 240:
            new = replace(new, user_label="Carry in")
        elif old.kind == 243:  # old LevelOutput8: local input (-1, 0)
            new = replace(
                new,
                kind=legacy_v6.COM_LEVEL_OUTPUT_WORD,
                position=_translated_position(new.position, new.rotation, (2, 0)),
                word_size=8,
                user_label="Output",
            )
        elif old.kind in {80, 81, 242}:
            new = replace(new, user_label="Carry out")
        components.append(new)

    converted = replace(current, components=components)
    data = legacy_v6.write_v15(converted)
    # 双解析器往返，避免只生成“迁移器自己能读”的孤立格式。
    legacy_v6.parse_v15(data)
    decode_v15(data)
    return data


def compile_circuit(circuit: object, legacy: object) -> Compiled:
    endpoints: list[tuple[tuple[int, int], tuple[int, int]]] = []
    owners: dict[tuple[int, int], list[int]] = defaultdict(list)
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        pair = (points[0], points[-1])
        endpoints.append(pair)
        owners[pair[0]].append(wire_index)
        owners[pair[1]].append(wire_index)

    uf = UnionFind(len(circuit.wires))
    for wire_indices in owners.values():
        for wire_index in wire_indices[1:]:
            uf.union(wire_indices[0], wire_index)

    network_by_position = {
        position: uf.find(wire_index)
        for wire_index, pair in enumerate(endpoints)
        for position in pair
    }
    pins: dict[tuple[int, str], object] = {}
    pin_network: dict[tuple[int, str], int] = {}
    network_pins: dict[int, list[object]] = defaultdict(list)
    pin_positions = set()
    unconnected_inputs = []
    for index, component in enumerate(circuit.components):
        component_pins = positioned_pins(component, index)
        if not component_pins:
            raise RuntimeError(f"unsupported current component kind {component.kind}")
        for pin in component_pins:
            # v6 Bit Switch 的 enable/out 分别在本地 (0,-1)/(+1,0)，
            # 2.1.x 则在 (0,+1)/(+2,0)。临时 v15 只承载元件/导线数据；
            # 考古语义必须使用旧针脚，否则会把全部开关误判为断线。
            old_switch_offsets = {"enable": (0, -1), "out": (1, 0)}
            if legacy.components[index].kind == 139 and pin.name in old_switch_offsets:
                dx, dy = rotate_offset(old_switch_offsets[pin.name], component.rotation)
                pin = replace(
                    pin,
                    position=(component.position[0] + dx, component.position[1] + dy),
                )
            # v6 Not 只有一格长，输出在 (+1,0)；当前 Not 输出在
            # (+2,0)。该差异只影响 Low-Delay-parallel 的半字节桥。
            if legacy.components[index].kind == 4 and pin.name == "out":
                dx, dy = rotate_offset((1, 0), component.rotation)
                pin = replace(
                    pin,
                    position=(component.position[0] + dx, component.position[1] + dy),
                )
            pins[(index, pin.name)] = pin
            pin_positions.add(pin.position)
            network = network_by_position.get(pin.position)
            if network is None:
                if pin.direction == I:
                    unconnected_inputs.append((index, pin.name))
                continue
            pin_network[(index, pin.name)] = network
            network_pins[network].append(pin)

    endpoint_non_pin_count = sum(
        endpoint not in pin_positions for pair in endpoints for endpoint in pair
    )
    return Compiled(
        pins=pins,
        pin_network=pin_network,
        network_pins={key: tuple(value) for key, value in network_pins.items()},
        endpoint_non_pin_count=endpoint_non_pin_count,
        unconnected_inputs=tuple(unconnected_inputs),
    )


def resolve(drivers: list[Signal]) -> Signal:
    width = max((len(driver.bits) for driver in drivers), default=1)
    ones = [0] * width
    zeros = [0] * width
    driven = 0
    conflict = 0
    delay = 0
    for driver in drivers:
        delay = max(delay, driver.delay)
        driven |= driver.driven
        conflict |= driver.conflict
        for bit_index in range(width):
            value = driver.bits[bit_index] if bit_index < len(driver.bits) else 0
            ones[bit_index] |= driver.driven & value
            zeros[bit_index] |= driver.driven & (~value & ALL)
    for one, zero_bits in zip(ones, zeros):
        conflict |= one & zero_bits
    return Signal(tuple(ones), driven, delay, conflict)


def evaluate(circuit: object, compiled: Compiled):
    variables = tuple(variable(index) for index in range(VARIABLES))
    outputs: dict[tuple[int, str], Signal] = {}
    networks: dict[int, Signal] = {}

    for index, component in enumerate(circuit.components):
        if component.kind == 61:
            bits = variables[:8] if component.user_label == "A" else variables[8:16]
            outputs[(index, "value")] = normal(bits, 0)
        elif component.kind == 60:
            outputs[(index, "value")] = normal((variables[16],), 0)
        elif component.kind == 1:
            outputs[(index, "out")] = normal((0,), 0)
        elif component.kind == 2:
            outputs[(index, "out")] = normal((ALL,), 0)

    sinks = {40, 68, 69}
    sources = {1, 2, 60, 61}
    pending = {
        index
        for index, component in enumerate(circuit.components)
        if component.kind not in sinks | sources
    }

    while pending:
        progress = False
        for network, pins in compiled.network_pins.items():
            if network in networks:
                continue
            drivers = [pin for pin in pins if pin.direction in {O, T}]
            if not drivers:
                networks[network] = zero(max((pin.width for pin in pins), default=1))
                progress = True
            elif all((pin.component_index, pin.name) in outputs for pin in drivers):
                networks[network] = resolve(
                    [outputs[(pin.component_index, pin.name)] for pin in drivers]
                )
                progress = True

        for index in tuple(pending):
            component = circuit.components[index]
            input_pins = [
                pin
                for (component_index, _), pin in compiled.pins.items()
                if component_index == index and pin.direction == I
            ]
            if not all(
                (index, pin.name) not in compiled.pin_network
                or compiled.pin_network[(index, pin.name)] in networks
                for pin in input_pins
            ):
                continue
            values = {
                pin.name: (
                    networks[compiled.pin_network[(index, pin.name)]]
                    if (index, pin.name) in compiled.pin_network
                    else zero(pin.width)
                )
                for pin in input_pins
            }
            input_delay = max((signal.delay for signal in values.values()), default=0)

            def bit(name: str, offset: int = 0) -> int:
                signal = values[name]
                return signal.bits[offset] if offset < len(signal.bits) else 0

            kind = component.kind
            delay = input_delay + DELAY_COST[kind]
            if kind == 3:
                result = {"out": normal(((~bit("in")) & ALL,), delay)}
            elif kind == 4:
                result = {"out": normal((bit("in0") & bit("in1"),), delay)}
            elif kind == 7:
                result = {"out": normal((bit("in0") | bit("in1"),), delay)}
            elif kind == 10:
                result = {"out": normal((bit("in0") ^ bit("in1"),), delay)}
            elif kind == 11:
                result = {"out": normal(((~(bit("in0") ^ bit("in1"))) & ALL,), delay)}
            elif kind == 12:
                enable = bit("enable") & values["enable"].driven
                result = {
                    "out": Signal((bit("in"),), enable, delay, values["in"].conflict | values["enable"].conflict)
                }
            elif kind == 15:
                left = bit("in0")
                right = bit("in1")
                carry = bit("carry_in")
                result = {
                    "sum": normal((left ^ right ^ carry,), delay),
                    "carry_out": normal(
                        ((left & right) | (left & carry) | (right & carry),),
                        delay,
                    ),
                }
            elif kind == 16:
                result = {
                    "out": normal(
                        tuple(bit(f"in{offset}") for offset in range(8)),
                        delay,
                    )
                }
            elif kind == 17:
                result = {
                    f"out{offset}": normal((bit("in", offset),), delay)
                    for offset in range(8)
                }
            else:
                raise RuntimeError(f"unsupported semantic component kind {kind}")
            outputs.update({(index, name): signal for name, signal in result.items()})
            pending.remove(index)
            progress = True

        if not progress:
            raise RuntimeError(f"evaluation stalled with components {sorted(pending)}")

    for network, pins in compiled.network_pins.items():
        if network in networks:
            continue
        drivers = [pin for pin in pins if pin.direction in {O, T}]
        if not drivers:
            networks[network] = zero(max((pin.width for pin in pins), default=1))
        elif all((pin.component_index, pin.name) in outputs for pin in drivers):
            networks[network] = resolve(
                [outputs[(pin.component_index, pin.name)] for pin in drivers]
            )

    return variables, networks, outputs


def truth_labels(variables: tuple[int, ...]) -> dict[int, list[str]]:
    labels: dict[int, set[str]] = defaultdict(set)

    def add(value: int, label: str) -> None:
        labels[value & ALL].add(label)

    add(0, "0")
    add(ALL, "1")
    a = variables[:8]
    b = variables[8:16]
    cin = variables[16]
    add(cin, "Cin/C0")
    add(~cin, "~Cin")
    carry = cin
    for bit_index, (left, right) in enumerate(zip(a, b)):
        add(left, f"A{bit_index}")
        add(right, f"B{bit_index}")
        add(~left, f"~A{bit_index}")
        add(~right, f"~B{bit_index}")
        propagate = left ^ right
        generate = left & right
        kill = (~(left | right)) & ALL
        add(propagate, f"P{bit_index}")
        add(~propagate, f"~P{bit_index}")
        add(generate, f"G{bit_index}")
        add(kill, f"K{bit_index}")
        add(left | right, f"H{bit_index}")
        add(~generate, f"~G{bit_index}")
        total = propagate ^ carry
        add(total, f"S{bit_index}")
        carry = generate | (propagate & carry)
        add(carry, f"C{bit_index + 1}")
        add(~carry, f"~C{bit_index + 1}")

    for low in range(8):
        interval_p = ALL
        interval_g = 0
        interval_k = ALL
        for high in range(low, 8):
            p = a[high] ^ b[high]
            g = a[high] & b[high]
            k = (~(a[high] | b[high])) & ALL
            interval_g = g | (p & interval_g)
            interval_k = k | (p & interval_k)
            interval_p &= p
            suffix = f"[{high}:{low}]"
            add(interval_p, f"P{suffix}")
            add(interval_g, f"G{suffix}")
            add(interval_k, f"K{suffix}")
            add(~interval_p, f"~P{suffix}")
            add(~interval_g, f"~G{suffix}")
            add(~interval_k, f"~K{suffix}")
    return {value: sorted(names) for value, names in labels.items()}


def short_hash(value: int) -> str:
    data = (value & ALL).to_bytes(ASSIGNMENTS // 8, "little")
    return sha256(data).hexdigest()[:16]


def signal_record(signal: Signal, labels: dict[int, list[str]]) -> dict[str, object]:
    return {
        "width": len(signal.bits),
        "delay": signal.delay,
        "driven_cases": signal.driven.bit_count(),
        "z_cases": ((~signal.driven) & ALL).bit_count(),
        "driven_labels": labels.get(signal.driven & ALL, []),
        "conflict_cases": signal.conflict.bit_count(),
        "bits": [
            {
                "labels": labels.get(value & ALL, []),
                "ones": (value & ALL).bit_count(),
                "sha256_16": short_hash(value),
            }
            for value in signal.bits
        ],
    }


def semantic_audit(circuit: object, legacy: object) -> tuple[dict[str, object], dict[str, object]]:
    compiled = compile_circuit(circuit, legacy)
    variables, networks, outputs = evaluate(circuit, compiled)
    labels = truth_labels(variables)

    output_index = next(
        i for i, component in enumerate(circuit.components)
        if component.user_label == "Output"
    )
    carry_index = next(
        i for i, component in enumerate(circuit.components)
        if component.user_label == "Carry out"
    )
    output_network = compiled.pin_network[(output_index, "value")]
    carry_network = compiled.pin_network[(carry_index, "value")]
    sum_signal = networks[output_network]
    carry_signal = networks[carry_network]

    carry = variables[16]
    expected_sum = []
    for left, right in zip(variables[:8], variables[8:16]):
        propagate = left ^ right
        expected_sum.append(propagate ^ carry)
        carry = (left & right) | (propagate & carry)

    all_conflict = 0
    for signal in networks.values():
        all_conflict |= signal.conflict
    logical_value_ok = (
        sum_signal.bits[:8] == tuple(expected_sum)
        and carry_signal.bits[0] == carry
        and all_conflict == 0
    )
    fully_driven_outputs = sum_signal.driven == ALL and carry_signal.driven == ALL
    gates = sum(GATE_COST.get(component.kind, 0) for component in circuit.components)
    delay = max(sum_signal.delay, carry_signal.delay)
    multi_driver = sum(
        sum(pin.direction in {O, T} for pin in pins) > 1
        for pins in compiled.network_pins.values()
    )
    tristate_buses = sum(
        sum(pin.direction == T for pin in pins) > 1
        for pins in compiled.network_pins.values()
    )
    summary = {
        # Wire.value 在旧版和当前组合语义中都把 Z 读成 0；另外保留
        # fully_driven_outputs，避免把“Z 编码 0”误写成连续驱动。
        "semantic_ok": logical_value_ok,
        "logical_value_ok_with_z_as_zero": logical_value_ok,
        "fully_driven_outputs": fully_driven_outputs,
        "vectors": ASSIGNMENTS,
        "recomputed_current_gate": gates,
        "recomputed_current_delay": delay,
        "recomputed_current_energy": gates * delay,
        "output_delay": sum_signal.delay,
        "carry_delay": carry_signal.delay,
        "output_z_cases": ((~sum_signal.driven) & ALL).bit_count(),
        "carry_z_cases": ((~carry_signal.driven) & ALL).bit_count(),
        "conflict_cases": all_conflict.bit_count(),
        "network_count": len(compiled.network_pins),
        "multi_driver_network_count": multi_driver,
        "multi_switch_bus_count": tristate_buses,
        "unconnected_inputs": [list(item) for item in compiled.unconnected_inputs],
        "endpoint_non_pin_count": compiled.endpoint_non_pin_count,
    }

    network_records = []
    for network, signal in sorted(networks.items()):
        pins = compiled.network_pins.get(network, ())
        drivers = [pin for pin in pins if pin.direction in {O, T}]
        sinks = [pin for pin in pins if pin.direction == I]
        network_records.append(
            {
                "network": network,
                "signal": signal_record(signal, labels),
                "drivers": [
                    {
                        "component": pin.component_index,
                        "kind": CURRENT_KIND_NAMES.get(
                            circuit.components[pin.component_index].kind,
                            str(circuit.components[pin.component_index].kind),
                        ),
                        "pin": pin.name,
                        "tristate": pin.direction == T,
                    }
                    for pin in drivers
                ],
                "sinks": [
                    {
                        "component": pin.component_index,
                        "kind": CURRENT_KIND_NAMES.get(
                            circuit.components[pin.component_index].kind,
                            str(circuit.components[pin.component_index].kind),
                        ),
                        "pin": pin.name,
                    }
                    for pin in sinks
                ],
            }
        )

    component_records = []
    for index, component in enumerate(circuit.components):
        input_records = {}
        output_records = {}
        for (component_index, pin_name), pin in compiled.pins.items():
            if component_index != index:
                continue
            network = compiled.pin_network.get((index, pin_name))
            target = input_records if pin.direction == I else output_records
            target[pin_name] = network
        component_records.append(
            {
                "component": index,
                "kind": component.kind,
                "kind_name": CURRENT_KIND_NAMES.get(component.kind, str(component.kind)),
                "position": list(component.position),
                "rotation": component.rotation,
                "inputs": input_records,
                "outputs": output_records,
                "output_signals": {
                    name: signal_record(signal, labels)
                    for (component_index, name), signal in outputs.items()
                    if component_index == index
                },
            }
        )
    topology = {
        "summary": summary,
        "components": component_records,
        "networks": network_records,
    }
    return summary, topology


def path_key(path: Path) -> str:
    return str(path.relative_to(SOURCE_ROOT)).replace("\\", "/")


def main() -> None:
    if V15_ROOT.exists():
        shutil.rmtree(V15_ROOT)
    V15_ROOT.mkdir(parents=True, exist_ok=True)
    records = []
    topologies = {}
    files = sorted(SOURCE_ROOT.glob("*/schematics/byte_adder/**/circuit*.data"))
    for source in files:
        relative = source.relative_to(SOURCE_ROOT)
        raw = source.read_bytes()
        legacy = legacy_v6.parse_legacy_v6(raw)
        kinds = Counter(component.kind for component in legacy.components)
        customs = [
            {
                "custom_id": component.custom_id,
                "label": component.custom_string,
                "position": list(component.position),
            }
            for component in legacy.components
            if component.kind in {92, 93}
        ]
        record = {
            "path": path_key(source),
            "sha256": sha256(raw).hexdigest(),
            "bytes": len(raw),
            "version": raw[0],
            "legacy_header": {
                "gate": legacy.gate,
                "delay": legacy.delay,
                "score": legacy.score,
                "save_id": legacy.save_id,
                "hub_id": legacy.hub_id,
            },
            "component_count": len(legacy.components),
            "wire_count": len(legacy.wires),
            "declared_dependencies": legacy.dependencies,
            "custom_instances": customs,
            "legacy_kind_counts": {
                f"{kind}:{legacy_v6.legacy_kind_name(kind)}": count
                for kind, count in sorted(kinds.items())
            },
        }
        try:
            converted = semantic_v15(legacy)
            circuit = decode_v15(converted)
            summary, topology = semantic_audit(circuit, legacy)
            record["semantic_audit"] = summary
            # 备份序列已经由 inventory 完整记录；只保留四个主文件的 v15，
            # 避免冻结大量同拓扑/未完成副本。
            if source.name == "circuit.data" and summary["semantic_ok"]:
                destination = V15_ROOT / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(converted)
                changed_internal_ports = sorted(
                    {
                        legacy_v6.legacy_kind_name(component.kind)
                        for component in legacy.components
                        if component.kind in {4, 139}
                    }
                )
                record["temporary_v15"] = {
                    "path": str(destination.relative_to(PROJECT)).replace("\\", "/"),
                    "sha256": sha256(converted).hexdigest(),
                    "bytes": len(converted),
                    "roundtrip_verified": True,
                    "current_game_ready": False,
                    "changed_internal_port_kinds": changed_internal_ports,
                    "port_note": (
                        "仅用于离线考古；头部分数仍是旧值，关卡接口需由当前 campaign 注入，"
                        "v6 Switch/Not 还需按 2.1.x 针脚重新布局"
                        if changed_internal_ports
                        else "仅用于离线考古；头部分数仍是旧值，关卡接口需由当前 campaign 注入"
                    ),
                }
            if (
                source.name == "circuit.data"
                and any(part.startswith("Low-Delay") for part in relative.parts)
            ):
                topologies[path_key(source)] = topology
        except Exception as exc:  # 保留未完成 backup 的考古证据
            record["semantic_error"] = f"{type(exc).__name__}: {exc}"
        records.append(record)
        status = record.get("semantic_audit", {}).get("semantic_ok", False)
        metric = record.get("semantic_audit", {})
        print(
            f"{record['path']}: header={legacy.gate}/{legacy.delay} "
            f"components={len(legacy.components)} wires={len(legacy.wires)} "
            f"semantic={status} current={metric.get('recomputed_current_gate', '-')}/"
            f"{metric.get('recomputed_current_delay', '-')}"
        )

    INVENTORY_PATH.write_text(
        json.dumps(
            {
                "schema": "legacy-byte-adder-inventory-v1",
                "source_root": str(SOURCE_ROOT),
                "file_count": len(records),
                "records": records,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    TOPOLOGY_PATH.write_text(
        json.dumps(
            {
                "schema": "legacy-byte-adder-low-delay-topologies-v1",
                "vectors": ASSIGNMENTS,
                "topologies": topologies,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {INVENTORY_PATH}")
    print(f"wrote {TOPOLOGY_PATH}")


if __name__ == "__main__":
    main()
