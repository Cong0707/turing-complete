"""构造并离线验证 Little Box 的当前 v15 RAM 候选。

本模块只使用游戏原生 ``com_ram``（kind 118）和地址合成器；不依赖
自定义元件，也不伪造游戏计分字段。RAM 的读出在本拍保存之前完成，
且 ``load == 0`` 时三态输出保持 Z，这与
``campaign/ram_component/test.si`` 的先验检查顺序一致。
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .pins import analyze_connectivity, positioned_pins
from .simulate import _compile
from .sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, audit_sprite_geometry


LEVEL = "ram_component"
RAM_KIND = 118
RAM_BYTES = 4
RAM_WORD_WIDTH = 8
RAM_ADDRESS_WIDTH = 8
EXPECTED_GATE = 368
EXPECTED_DELAY = 5


@dataclass(frozen=True)
class RamTick:
    """Little Box 一拍的可观测输出与写回后的四字节状态。"""

    output: int | None
    memory: tuple[int, int, int, int]


@dataclass(frozen=True)
class _RamRuntime:
    """已把候选电路端点编译成网络映射的轻量运行器。"""

    load_source_network: int
    save_source_network: int
    address0_source_network: int
    address1_source_network: int
    value_source_network: int
    maker_input0_network: int
    maker_input1_network: int
    maker_output_network: int
    ram_load_network: int
    ram_save_network: int
    ram_address_network: int
    ram_input_network: int
    ram_output_network: int
    level_output_network: int

    def tick(
        self,
        *,
        load: int,
        save: int,
        address: int,
        value: int,
        memory: tuple[int, int, int, int],
    ) -> RamTick:
        """运行一拍，并忠实保留游戏的读前写后时序。"""

        if load not in {0, 1} or save not in {0, 1}:
            raise ValueError("load 和 save 必须是 U1")
        if not 0 <= address < RAM_BYTES:
            raise ValueError("Little Box 地址必须是 U2")
        if not 0 <= value <= 0xFF:
            raise ValueError("Little Box value 必须是 U8")
        if len(memory) != RAM_BYTES or any(not 0 <= item <= 0xFF for item in memory):
            raise ValueError("Little Box 内存状态必须恰好是四个 U8")

        network_values = {
            self.load_source_network: load,
            self.save_source_network: save,
            self.address0_source_network: address & 1,
            self.address1_source_network: (address >> 1) & 1,
            self.value_source_network: value,
        }
        # com_maker_bit_2 packs in0 as bit 0 and in1 as bit 1.  The RAM's
        # U8 address input receives that legal narrow bus through zero
        # extension, exactly as the game does for Little Box's U2 address.
        packed_address = (
            network_values[self.maker_input0_network]
            | (network_values[self.maker_input1_network] << 1)
        )
        network_values[self.maker_output_network] = packed_address

        if network_values[self.ram_load_network] != load:
            raise RuntimeError("RAM Load 路径未连接到关卡输入")
        if network_values[self.ram_save_network] != save:
            raise RuntimeError("RAM Save 路径未连接到关卡输入")
        if network_values[self.ram_address_network] != packed_address:
            raise RuntimeError("RAM Address 路径未连接到地址合成器")
        if network_values[self.ram_input_network] != value:
            raise RuntimeError("RAM Value 路径未连接到关卡输入")

        # The test script samples output before applying Save.  A disabled
        # RAM pin has no driver, represented here by None rather than zero.
        output = memory[packed_address] if load == 1 else None
        if self.ram_output_network != self.level_output_network:
            raise RuntimeError("RAM 输出未连接到关卡输出")

        next_memory = list(memory)
        if save == 1:
            next_memory[packed_address] = value
        return RamTick(output=output, memory=tuple(next_memory))


def _load_scaffold_components(project_root: Path) -> tuple[Component, ...]:
    path = project_root / "examples" / LEVEL / "scaffold" / "immutable.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    components = []
    for raw_component in record["immutable_components"]:
        component = dict(raw_component)
        component.pop("role", None)
        components.append(component)
    circuit = Circuit.from_dict({"components": components})
    if len(circuit.components) != 5 or not all(
        component.immutable for component in circuit.components
    ):
        raise RuntimeError("Little Box 不可变接口脚手架无效")
    return circuit.components


def _component(role: str, kind: int, position: Point, **kwargs: object) -> Component:
    return Component(
        kind=kind,
        position=position,
        rotation=0,
        permanent_id=stable_permanent_id(f"ram-component/{LEVEL}", role),
        **kwargs,
    )


def build_ram_component_candidate(project_root: Path) -> Circuit:
    """生成 RAM + U2 地址合成器的确定性 v15 候选。"""

    immutable = _load_scaffold_components(Path(project_root))
    maker = _component("address-maker", 111, (-5, -3), word_size=1)
    ram = _component(
        "little-box-ram",
        RAM_KIND,
        (25, 30),
        word_size=RAM_WORD_WIDTH,
        buffer_size=RAM_BYTES,
        settings=(0, 0, 0),
        init_data=0,
    )
    components = immutable + (maker, ram)

    # Each route exits a source through its actual external edge, then stays
    # outside every component sprite until its destination endpoint.  Wires
    # may cross other wires, but never a component body or a non-endpoint pin.
    wires = (
        wire_from_vertices(((-13, -12), (-12, -12), (-12, -15), (-9, -15), (-9, 15), (10, 15))),
        wire_from_vertices(((-13, -9), (-12, -9), (-12, -14), (-8, -14), (-8, 16), (10, 16))),
        # The compact U2 source draws each output pin one cell inside its
        # opaque sprite.  The game's own hint uses the adjacent one-cell
        # horizontal collar as the only legal escape; the audit below permits
        # exactly those two cells and rejects every other body crossing.
        wire_from_vertices(((-14, -4), (-6, -4))),
        wire_from_vertices(((-14, -2), (-7, -2), (-7, -3), (-6, -3))),
        wire_from_vertices(((-4, -3), (-3, -3), (-3, 17), (10, 17))),
        wire_from_vertices(((-10, 1), (-9, 1), (-9, 18), (10, 18))),
        wire_from_vertices(((41, 15), (45, 15), (45, 5), (9, 5), (9, 1), (10, 1))),
    )
    return Circuit(
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        description=(
            "Codex Little Box RAM ASIC: 原生四字节 RAM，U2 地址经 maker_bit_2 "
            "零扩展到 RAM 地址端口；读在写回之前，Load=0 时输出 Z。"
        ),
        components=components,
        wires=wires,
    )


def _find_component_index(
    circuit: Circuit,
    *,
    kind: int | None = None,
    label: str | None = None,
) -> int:
    matches = [
        index
        for index, component in enumerate(circuit.components)
        if (kind is None or component.kind == kind)
        and (label is None or component.user_label == label)
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Little Box 候选无法唯一找到组件 kind={kind!r}, label={label!r}: {matches}"
        )
    return matches[0]


def _compile_ram_runtime(circuit: Circuit) -> _RamRuntime:
    """从候选真实导线端点提取专用 RAM 运行时网络。"""

    compiled = _compile(circuit)
    load_index = _find_component_index(circuit, kind=60, label="Load")
    save_index = _find_component_index(circuit, kind=60, label="Save")
    address_index = _find_component_index(circuit, kind=63, label="Address")
    value_index = _find_component_index(circuit, kind=61, label="Value")
    output_index = _find_component_index(circuit, kind=69, label="Output")
    maker_index = _find_component_index(circuit, kind=111)
    ram_index = _find_component_index(circuit, kind=RAM_KIND)

    network = compiled.pin_networks
    runtime = _RamRuntime(
        load_source_network=network[(load_index, "value")],
        save_source_network=network[(save_index, "value")],
        address0_source_network=network[(address_index, "value0")],
        address1_source_network=network[(address_index, "value1")],
        value_source_network=network[(value_index, "value")],
        maker_input0_network=network[(maker_index, "in0")],
        maker_input1_network=network[(maker_index, "in1")],
        maker_output_network=network[(maker_index, "out")],
        ram_load_network=network[(ram_index, "load")],
        ram_save_network=network[(ram_index, "save")],
        ram_address_network=network[(ram_index, "address")],
        ram_input_network=network[(ram_index, "in")],
        ram_output_network=network[(ram_index, "out")],
        level_output_network=network[(output_index, "value")],
    )
    expected_links = (
        (runtime.load_source_network, runtime.ram_load_network, "Load"),
        (runtime.save_source_network, runtime.ram_save_network, "Save"),
        (runtime.address0_source_network, runtime.maker_input0_network, "Address bit 0"),
        (runtime.address1_source_network, runtime.maker_input1_network, "Address bit 1"),
        (runtime.maker_output_network, runtime.ram_address_network, "Address maker -> RAM"),
        (runtime.value_source_network, runtime.ram_input_network, "Value"),
        (runtime.ram_output_network, runtime.level_output_network, "Output"),
    )
    for source, destination, name in expected_links:
        if source != destination:
            raise RuntimeError(f"Little Box 候选的 {name} 导线未连通")
    return runtime


def _verify_state_timing(runtime: _RamRuntime) -> int:
    """穷举所有本地 U8 读写转移，另以哨兵值覆盖其余三个地址。"""

    vectors = 0
    for address in range(RAM_BYTES):
        untouched = tuple((0x31 + slot * 0x29) & 0xFF for slot in range(RAM_BYTES))
        for old_value in range(256):
            initial = list(untouched)
            initial[address] = old_value
            prior = tuple(initial)
            for value in range(256):
                for load in (0, 1):
                    for save in (0, 1):
                        actual = runtime.tick(
                            load=load,
                            save=save,
                            address=address,
                            value=value,
                            memory=prior,
                        )
                        expected_output = old_value if load else None
                        expected_memory = list(prior)
                        if save:
                            expected_memory[address] = value
                        if actual.output != expected_output or actual.memory != tuple(expected_memory):
                            raise RuntimeError(
                                "Little Box 状态时序错误："
                                f"address={address}, old={old_value}, value={value}, "
                                f"load={load}, save={save}, actual={actual}"
                            )
                        vectors += 1
    return vectors


def _verify_script_prefix(runtime: _RamRuntime) -> list[dict[str, object]]:
    """覆盖 test.si 前八拍的逐地址写入与紧随其后的读出。"""

    memory = (0, 0, 0, 0)
    trace: list[dict[str, object]] = []
    values = (0x11, 0x22, 0x33, 0x44)
    for address, value in enumerate(values):
        write = runtime.tick(load=0, save=1, address=address, value=value, memory=memory)
        if write.output is not None:
            raise RuntimeError("Save-only 拍不应驱动 Little Box 输出")
        memory = write.memory
        read = runtime.tick(load=1, save=0, address=address, value=0, memory=memory)
        if read.output != value or read.memory != memory:
            raise RuntimeError(f"Little Box 前缀读回失败：address={address}")
        trace.append({"address": address, "value": value, "output": read.output})
    return trace


def verify_ram_component_candidate(circuit: Circuit) -> dict[str, object]:
    """执行结构、真实网络、时序和精灵几何的完整离线验证。"""

    if (circuit.gate, circuit.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError("Little Box 候选的目标计分头发生变化")
    ram_components = [component for component in circuit.components if component.kind == RAM_KIND]
    if len(ram_components) != 1:
        raise RuntimeError("Little Box 候选必须只使用一个原生 RAM")
    ram = ram_components[0]
    if (
        ram.word_size,
        ram.buffer_size,
        ram.settings,
        ram.init_data,
    ) != (RAM_WORD_WIDTH, RAM_BYTES, (0, 0, 0), 0):
        raise RuntimeError("Little Box RAM 配置不是四字节零初始化 U8 RAM")

    connectivity = analyze_connectivity(circuit)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"Little Box 候选连接审计失败 {field}: {connectivity[field]}")
    # maker_bit_2 is U2 while the RAM implementation receives U8 addresses.
    # This is the one documented game-side zero-extension, not a stray wire.
    if connectivity["width_mismatch_network_count"] != 1:
        raise RuntimeError(
            "Little Box 候选应仅保留一条经审计的 U2 -> U8 地址零扩展"
        )

    runtime = _compile_ram_runtime(circuit)
    prefix = _verify_script_prefix(runtime)
    vectors = _verify_state_timing(runtime)

    geometry: dict[str, object] | None = None
    if DEFAULT_COMPONENT_SPRITE_ROOT.is_dir():
        audit = audit_sprite_geometry(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
        allowed_port_leads = {
            (2, 1, (-13, -4)),
            (3, 1, (-13, -2)),
        }
        observed_collisions = {
            (item.wire_index, item.component_index, item.point)
            for item in audit.wire_collisions
        }
        if (
            audit.unsupported_component_kinds
            or audit.component_overlap_cells
            or observed_collisions != allowed_port_leads
            or audit.wire_interior_pin_contacts
        ):
            raise RuntimeError(f"Little Box 候选真实精灵几何审计失败: {audit}")
        geometry = {
            "sprite_files": list(audit.sprite_files),
            "alpha_cell_count": audit.alpha_cell_count,
            "unexpected_wire_collision_count": 0,
            "source_port_lead_contact_count": len(allowed_port_leads),
            "wire_interior_pin_contact_count": len(audit.wire_interior_pin_contacts),
        }

    return {
        "gate": circuit.gate,
        "delay": circuit.delay,
        "energy": circuit.energy,
        "leaderboard_tuple": [circuit.gate, circuit.delay, circuit.energy],
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "state_transition_vector_count": vectors,
        "script_prefix": prefix,
        "connectivity": connectivity,
        "geometry": geometry,
    }


def write_ram_component_candidate(project_root: Path) -> dict[str, object]:
    """写出确定性候选和可审计元数据，不接触正式存档。"""

    project_root = Path(project_root)
    circuit = build_ram_component_candidate(project_root)
    verification = verify_ram_component_candidate(circuit)
    payload = encode_v15(circuit)
    if decode_v15(payload) != circuit:
        raise RuntimeError("Little Box 候选未通过 v15 往返校验")

    destination = project_root / "examples" / LEVEL / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    (destination.parent / ".gitkeep").unlink(missing_ok=True)
    metadata = {
        "schema": 1,
        "level": LEVEL,
        "title": "Little Box",
        "title_zh": "小型存储器",
        "strategy": "一个原生四字节 RAM 加 U2 地址合成器",
        "metric_status": "目标 368 gate / 5 delay，须由游戏载入后重新计分确认",
        "format_version": 15,
        "sha256": sha256(payload).hexdigest(),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
