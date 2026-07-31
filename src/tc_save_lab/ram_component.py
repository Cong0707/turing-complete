"""构造并离线验证 Little Box（小型存储器）的 v15 候选。

``com_ram`` 是本关完成后才解锁的奖励，不能作为本关的解法。本模块只
使用已经可用的 U8 字寄存器、2 位译码器和位与门：一个地址只会打开一个
寄存器的读使能和写使能。这样既保留 test.si 的“先读后写”时序，也避免了
未选中寄存器在 Save 拍被改写。

生成器只写入项目下的 ``examples/ram_component/candidate``，绝不访问正式
游戏存档，也不会启动游戏。
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from .analysis import wire_points
from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .pins import analyze_connectivity, positioned_pins, rotate_offset
from .simulate import _compile
from .sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    SPRITE_NAME_BY_COMPONENT_KIND,
    audit_sprite_geometry,
    sprite_alpha_cells,
)


LEVEL = "ram_component"
REGISTER_KIND = 39
DECODER_KIND = 44
AND_KIND = 4
REGISTER_COUNT = 4
WORD_WIDTH = 8
BOARD_LIMIT = 16

# 368 / 5 is the documented low-energy Pareto point.  It is the four U8
# registers, one decoder and eight bit ANDs, not a forged score header.
EXPECTED_GATE = 368
EXPECTED_DELAY = 5


# (register centre, Load AND centre, Save AND centre).  All rendered alpha
# cells and all routed wire cells are within the campaign's size=16 board.
REGISTER_LAYOUT: tuple[tuple[Point, Point, Point], ...] = (
    ((3, -11), (-10, -12), (-5, -12)),
    ((3, -3), (-10, -4), (-5, -4)),
    ((5, 5), (-8, 4), (-3, 4)),
    ((3, 13), (-10, 12), (-5, 12)),
)
DECODER_POSITION: Point = (10, 11)


# These routes were searched against the current installed PNG alpha masks.
# A wire may cross another wire, but it never crosses another component or a
# non-endpoint pin.  The only opaque cells touched away from endpoints are the
# short, straight port leads needed to leave/enter a Register Word and the
# two-bit level input; _verify_sprite_geometry proves that exception exactly.
# The storage order below is semantic: address wires first, then the eight
# routes for each register in index order. _wire_semantics() follows the same
# order and rejects a reordered or manually edited route table.
WIRE_VERTICES: tuple[tuple[Point, ...], ...] = (
    ((-14, -4), (-12, -4), (-12, -7), (-1, -7), (-1, 2), (1, 2), (1, 10), (9, 10)),
    ((-14, -2), (-12, -2), (-12, -7), (-1, -7), (-1, 2), (1, 2), (1, 10), (8, 10), (8, 11), (9, 11)),
    ((11, 10), (12, 10), (12, 4), (9, 4), (9, -8), (-12, -8), (-12, -13), (-11, -13)),
    ((11, 10), (12, 10), (12, 4), (9, 4), (9, -8), (-7, -8), (-7, -13), (-6, -13)),
    ((-13, -12), (-12, -12), (-12, -11), (-11, -11)),
    ((-13, -9), (-7, -9), (-7, -11), (-6, -11)),
    ((-8, -12), (-7, -12), (-7, -9), (-1, -9), (-1, -12), (2, -12)),
    ((-3, -12), (-1, -12), (-1, -11), (2, -11)),
    ((-10, 1), (-1, 1), (-1, -10), (2, -10)),
    ((4, -11), (7, -11), (7, 1), (10, 1)),
    ((11, 11), (12, 11), (12, 4), (9, 4), (9, -7), (-12, -7), (-12, -5), (-11, -5)),
    ((11, 11), (12, 11), (12, 8), (-5, 8), (-5, -1), (-7, -1), (-7, -5), (-6, -5)),
    ((-13, -12), (-12, -12), (-12, -3), (-11, -3)),
    ((-13, -9), (-7, -9), (-7, -3), (-6, -3)),
    ((-8, -4), (-7, -4), (-7, -1), (-1, -1), (-1, -4), (2, -4)),
    ((-3, -4), (-1, -4), (-1, -3), (2, -3)),
    ((-10, 1), (-1, 1), (-1, -2), (2, -2)),
    ((4, -3), (7, -3), (7, 1), (10, 1)),
    ((11, 12), (12, 12), (12, 8), (-10, 8), (-10, 3), (-9, 3)),
    ((11, 12), (12, 12), (12, 8), (-5, 8), (-5, 3), (-4, 3)),
    ((-13, -12), (-12, -12), (-12, -7), (-7, -7), (-7, 2), (-5, 2), (-5, 7), (-10, 7), (-10, 5), (-9, 5)),
    ((-13, -9), (-7, -9), (-7, 2), (-5, 2), (-5, 5), (-4, 5)),
    ((-6, 4), (-5, 4), (-5, 7), (1, 7), (1, 4), (4, 4)),
    ((-1, 4), (1, 4), (1, 5), (4, 5)),
    ((-10, 1), (1, 1), (1, 6), (4, 6)),
    ((6, 5), (9, 5), (9, 1), (10, 1)),
    ((11, 13), (12, 13), (12, 8), (-12, 8), (-12, 11), (-11, 11)),
    ((11, 13), (12, 13), (12, 8), (-7, 8), (-7, 11), (-6, 11)),
    ((-13, -12), (-12, -12), (-12, -7), (-7, -7), (-7, 2), (-5, 2), (-5, 9), (-12, 9), (-12, 13), (-11, 13)),
    ((-13, -9), (-7, -9), (-7, 2), (-5, 2), (-5, 9), (-7, 9), (-7, 13), (-6, 13)),
    ((-8, 12), (-7, 12), (-7, 15), (-1, 15), (-1, 12), (2, 12)),
    ((-3, 12), (-1, 12), (-1, 13), (2, 13)),
    ((-10, 1), (-5, 1), (-5, 7), (-1, 7), (-1, 14), (2, 14)),
    ((4, 13), (7, 13), (7, 8), (9, 8), (9, 1), (10, 1)),
)


@dataclass(frozen=True)
class RamTick:
    """一拍的可观测三态输出和写回后的四字节状态。"""

    output: int | None
    memory: tuple[int, int, int, int]


@dataclass(frozen=True)
class _RegisterRuntime:
    """由真实网络拓扑证明后的 Little Box 时序模型。"""

    register_count: int = REGISTER_COUNT

    def tick(
        self,
        *,
        load: int,
        save: int,
        address: int,
        value: int,
        memory: tuple[int, int, int, int],
    ) -> RamTick:
        if load not in {0, 1} or save not in {0, 1}:
            raise ValueError("load 和 save 必须是 U1")
        if not 0 <= address < self.register_count:
            raise ValueError("Little Box 地址必须是 U2")
        if not 0 <= value <= 0xFF:
            raise ValueError("Little Box value 必须是 U8")
        if len(memory) != self.register_count or any(not 0 <= item <= 0xFF for item in memory):
            raise ValueError("Little Box 内存状态必须恰好是四个 U8")

        one_hot = tuple(int(index == address) for index in range(self.register_count))
        read_enable = tuple(load & select for select in one_hot)
        write_enable = tuple(save & select for select in one_hot)
        if sum(read_enable) != load or sum(write_enable) != save:
            raise RuntimeError("地址译码没有保持严格 one-hot")

        # test.si 在 Save 状态更新之前检查 Output，因此这里先读取旧状态。
        output = memory[address] if read_enable[address] else None
        next_memory = list(memory)
        for index, enabled in enumerate(write_enable):
            if enabled:
                next_memory[index] = value
        return RamTick(output=output, memory=tuple(next_memory))


def _load_scaffold_components(project_root: Path) -> tuple[Component, ...]:
    path = project_root / "examples" / LEVEL / "scaffold" / "immutable.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    records = []
    for raw_component in record["immutable_components"]:
        component = dict(raw_component)
        component.pop("role", None)
        records.append(component)
    circuit = Circuit.from_dict({"components": records})
    labels = {component.user_label for component in circuit.components}
    if len(circuit.components) != 5 or not all(component.immutable for component in circuit.components):
        raise RuntimeError("Little Box 不可变接口脚手架无效")
    if labels != {"Load", "Save", "Address", "Value", "Output"}:
        raise RuntimeError("Little Box 不可变接口标签发生变化")
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
    """生成只依赖本关前已解锁基础组件的确定性 v15 电路。"""

    immutable = _load_scaffold_components(Path(project_root))
    mutable: list[Component] = [
        _component("decoder", DECODER_KIND, DECODER_POSITION, word_size=1),
    ]
    for index, (register_position, load_and_position, save_and_position) in enumerate(
        REGISTER_LAYOUT
    ):
        mutable.extend(
            (
                _component(
                    f"register-{index}",
                    REGISTER_KIND,
                    register_position,
                    word_size=WORD_WIDTH,
                ),
                _component(f"load-and-{index}", AND_KIND, load_and_position, word_size=1),
                _component(f"save-and-{index}", AND_KIND, save_and_position, word_size=1),
            )
        )
    components = immutable + tuple(mutable)
    permanent_ids = [component.permanent_id for component in components]
    if len(permanent_ids) != len(set(permanent_ids)) or 0 in permanent_ids:
        raise RuntimeError("Little Box 候选含重复或空 permanent_id")
    if len(WIRE_VERTICES) != 2 + REGISTER_COUNT * 8:
        raise RuntimeError("Little Box 静态导线表不完整")
    return Circuit(
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        description=(
            "Codex Little Box ASIC: 四个 U8 Register Word；Decoder2 的 one-hot "
            "分别与 Load / Save 相与。读在写回之前，Load=0 时总线为 Z。"
        ),
        components=components,
        wires=tuple(wire_from_vertices(vertices) for vertices in WIRE_VERTICES),
    )


def _find_component_index(circuit: Circuit, *, label: str | None = None, role: str | None = None) -> int:
    if (label is None) == (role is None):
        raise ValueError("必须且只能按 label 或 role 查找组件")
    if label is not None:
        matches = [
            index for index, component in enumerate(circuit.components) if component.user_label == label
        ]
    else:
        assert role is not None
        permanent_id = stable_permanent_id(f"ram-component/{LEVEL}", role)
        matches = [
            index for index, component in enumerate(circuit.components) if component.permanent_id == permanent_id
        ]
    if len(matches) != 1:
        raise RuntimeError(f"Little Box 无法唯一定位组件 label={label!r}, role={role!r}: {matches}")
    return matches[0]


def _network(compiled: object, component_index: int, pin_name: str) -> int:
    try:
        return compiled.pin_networks[(component_index, pin_name)]  # type: ignore[attr-defined]
    except KeyError as exc:
        raise RuntimeError(f"Little Box 的 pin 未接线: component={component_index}, pin={pin_name}") from exc


def _require_same_network(compiled: object, *pins: tuple[int, str], name: str) -> None:
    networks = {_network(compiled, component_index, pin_name) for component_index, pin_name in pins}
    if len(networks) != 1:
        raise RuntimeError(f"Little Box 网络断开: {name}: {pins!r}")


def _wire_semantics(circuit: Circuit) -> tuple[tuple[str, tuple[int, str], tuple[int, str]], ...]:
    """返回静态导线顺序及其必须连接的端点，供拓扑审计使用。"""

    decoder = _find_component_index(circuit, role="decoder")
    load = _find_component_index(circuit, label="Load")
    save = _find_component_index(circuit, label="Save")
    address = _find_component_index(circuit, label="Address")
    value = _find_component_index(circuit, label="Value")
    output = _find_component_index(circuit, label="Output")
    result: list[tuple[str, tuple[int, str], tuple[int, str]]] = [
        ("address_0", (address, "value0"), (decoder, "select0")),
        ("address_1", (address, "value1"), (decoder, "select1")),
    ]
    for index in range(REGISTER_COUNT):
        register = _find_component_index(circuit, role=f"register-{index}")
        load_and = _find_component_index(circuit, role=f"load-and-{index}")
        save_and = _find_component_index(circuit, role=f"save-and-{index}")
        result.extend(
            (
                (f"decoder_load_{index}", (decoder, f"out{index}"), (load_and, "in0")),
                (f"decoder_save_{index}", (decoder, f"out{index}"), (save_and, "in0")),
                (f"load_{index}", (load, "value"), (load_and, "in1")),
                (f"save_{index}", (save, "value"), (save_and, "in1")),
                (f"load_control_{index}", (load_and, "out"), (register, "load")),
                (f"save_control_{index}", (save_and, "out"), (register, "save")),
                (f"value_{index}", (value, "value"), (register, "in")),
                (f"output_{index}", (register, "out"), (output, "value")),
            )
        )
    if tuple(item[0] for item in result) != _semantic_wire_names():
        raise RuntimeError("Little Box 导线语义表顺序发生变化")
    return tuple(result)


def _semantic_wire_names() -> tuple[str, ...]:
    names = ["address_0", "address_1"]
    for index in range(REGISTER_COUNT):
        names.extend(
            (
                f"decoder_load_{index}",
                f"decoder_save_{index}",
                f"load_{index}",
                f"save_{index}",
                f"load_control_{index}",
                f"save_control_{index}",
                f"value_{index}",
                f"output_{index}",
            )
        )
    return tuple(names)


def _compile_register_runtime(circuit: Circuit) -> _RegisterRuntime:
    """确认真实端点网络实现了译码、读使能和写使能三条路径。"""

    compiled = _compile(circuit)
    semantics = _wire_semantics(circuit)
    if len(circuit.wires) != len(semantics):
        raise RuntimeError("Little Box 导线数量与已审计静态表不一致")
    for wire, (name, source, destination), expected_vertices in zip(
        circuit.wires, semantics, WIRE_VERTICES
    ):
        if tuple(wire_points(wire)) != tuple(wire_points(wire_from_vertices(expected_vertices))):
            raise RuntimeError(f"Little Box 导线 {name} 偏离已审计路径")
        _require_same_network(compiled, source, destination, name=name)

    decoder = _find_component_index(circuit, role="decoder")
    load = _find_component_index(circuit, label="Load")
    save = _find_component_index(circuit, label="Save")
    value = _find_component_index(circuit, label="Value")
    output = _find_component_index(circuit, label="Output")
    for index in range(REGISTER_COUNT):
        register = _find_component_index(circuit, role=f"register-{index}")
        load_and = _find_component_index(circuit, role=f"load-and-{index}")
        save_and = _find_component_index(circuit, role=f"save-and-{index}")
        _require_same_network(
            compiled,
            (decoder, f"out{index}"),
            (load_and, "in0"),
            (save_and, "in0"),
            name=f"地址 {index} 的双路译码",
        )
        _require_same_network(compiled, (load, "value"), (load_and, "in1"), name=f"Load {index}")
        _require_same_network(compiled, (save, "value"), (save_and, "in1"), name=f"Save {index}")
        _require_same_network(compiled, (load_and, "out"), (register, "load"), name=f"读使能 {index}")
        _require_same_network(compiled, (save_and, "out"), (register, "save"), name=f"写使能 {index}")
        _require_same_network(compiled, (value, "value"), (register, "in"), name=f"Value {index}")
        _require_same_network(compiled, (register, "out"), (output, "value"), name=f"Output {index}")
    return _RegisterRuntime()


def _verify_state_timing(runtime: _RegisterRuntime) -> int:
    """穷举地址、旧字节、输入字节、Load 和 Save 的全部局部状态转换。

    四个寄存器完全独立，未寻址的三个位置由互异哨兵值覆盖。因此该局部
    穷举等价覆盖任意完整四字节状态的每一种单拍转移，而无需枚举 2^32
    个彼此无关的状态组合。
    """

    vectors = 0
    for address in range(REGISTER_COUNT):
        sentinels = tuple((0x31 + slot * 0x29) & 0xFF for slot in range(REGISTER_COUNT))
        for old_value in range(256):
            prior_list = list(sentinels)
            prior_list[address] = old_value
            prior = tuple(prior_list)
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
                        expected_memory = list(prior)
                        if save:
                            expected_memory[address] = value
                        expected_output = old_value if load else None
                        if actual.output != expected_output or actual.memory != tuple(expected_memory):
                            raise RuntimeError(
                                "Little Box 状态时序错误："
                                f"address={address}, old={old_value}, value={value}, "
                                f"load={load}, save={save}, actual={actual}"
                            )
                        vectors += 1
    return vectors


def _verify_script_prefix(runtime: _RegisterRuntime) -> list[dict[str, int]]:
    """覆盖 test.si 的前八拍：四次写入以及每次紧随其后的读取。"""

    memory = (0, 0, 0, 0)
    trace: list[dict[str, int]] = []
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


def _component_alpha_cells(component: Component, sprite_root: Path) -> frozenset[Point]:
    try:
        sprite_name = SPRITE_NAME_BY_COMPONENT_KIND[component.kind]
    except KeyError as exc:
        raise RuntimeError(f"Little Box 缺少 kind {component.kind} 的当前精灵映射") from exc
    source = sprite_root / sprite_name
    if not source.is_file():
        raise FileNotFoundError(f"缺少当前组件精灵: {source}")
    return frozenset(
        (
            component.position[0] + rotate_offset(cell, component.rotation)[0],
            component.position[1] + rotate_offset(cell, component.rotation)[1],
        )
        for cell in sprite_alpha_cells(source)
    )


def _verify_board_bounds(circuit: Circuit) -> dict[str, int]:
    """确认布局和每条导线均没有越出 size=16 的可用网格。"""

    points: list[Point] = []
    for index, component in enumerate(circuit.components):
        points.extend(pin.position for pin in positioned_pins(component, index))
    for wire in circuit.wires:
        points.extend(wire_points(wire))
    if DEFAULT_COMPONENT_SPRITE_ROOT.is_dir():
        for component in circuit.components:
            points.extend(_component_alpha_cells(component, DEFAULT_COMPONENT_SPRITE_ROOT))
    if not points:
        raise RuntimeError("Little Box 候选没有任何可审计坐标")
    out_of_bounds = [point for point in points if any(abs(axis) > BOARD_LIMIT for axis in point)]
    if out_of_bounds:
        raise RuntimeError(f"Little Box 越出 size={BOARD_LIMIT} 的关卡范围: {out_of_bounds[:4]}")
    return {
        "limit": BOARD_LIMIT,
        "min_x": min(point[0] for point in points),
        "max_x": max(point[0] for point in points),
        "min_y": min(point[1] for point in points),
        "max_y": max(point[1] for point in points),
    }


def _port_escape_direction(component: Component, pin_name: str) -> Point:
    """返回当前候选中每类端口从精灵内部离开的方向。"""

    if component.kind in {60, 61, 63}:
        direction = (1, 0)
    elif component.kind == 69:
        direction = (-1, 0)
    elif component.kind in {AND_KIND, REGISTER_KIND, DECODER_KIND}:
        direction = (1, 0) if pin_name == "out" or pin_name.startswith("out") else (-1, 0)
    else:
        raise RuntimeError(f"Little Box 未定义 kind {component.kind} pin {pin_name!r} 的引线方向")
    return rotate_offset(direction, component.rotation)


def _expected_port_leads(circuit: Circuit, sprite_root: Path) -> set[tuple[int, int, Point]]:
    """求出每根导线从其端口穿出自身精灵所必经的 alpha 网格。"""

    alpha_by_component = [
        _component_alpha_cells(component, sprite_root) for component in circuit.components
    ]
    pins_at_point: dict[Point, list[tuple[int, str]]] = {}
    for component_index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, component_index):
            pins_at_point.setdefault(pin.position, []).append((component_index, pin.name))

    expected: set[tuple[int, int, Point]] = set()
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        for endpoint in (points[0], points[-1]):
            owners = pins_at_point.get(endpoint, [])
            if len(owners) != 1:
                raise RuntimeError(f"Little Box 导线端点不是唯一 pin: {endpoint} -> {owners}")
            component_index, pin_name = owners[0]
            step = _port_escape_direction(circuit.components[component_index], pin_name)
            point = endpoint
            while point in alpha_by_component[component_index]:
                point = (point[0] + step[0], point[1] + step[1])
                if point in alpha_by_component[component_index]:
                    expected.add((wire_index, component_index, point))
    return expected


def _verify_sprite_geometry(circuit: Circuit) -> dict[str, object] | None:
    if not DEFAULT_COMPONENT_SPRITE_ROOT.is_dir():
        return None
    audit = audit_sprite_geometry(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
    observed = {
        (item.wire_index, item.component_index, item.point) for item in audit.wire_collisions
    }
    expected = _expected_port_leads(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
    if audit.unsupported_component_kinds:
        raise RuntimeError(f"Little Box 有未审计精灵的组件: {audit.unsupported_component_kinds}")
    if audit.component_overlap_cells:
        raise RuntimeError(f"Little Box 元件 alpha 重叠: {audit.component_overlap_cells}")
    if audit.wire_interior_pin_contacts:
        raise RuntimeError(f"Little Box 导线穿过非端点 pin: {audit.wire_interior_pin_contacts}")
    if observed != expected:
        unexpected = sorted(observed - expected)
        missing = sorted(expected - observed)
        raise RuntimeError(
            "Little Box 导线穿过元件实体，且不属于端口的必要直线引线: "
            f"unexpected={unexpected[:4]}, missing={missing[:4]}"
        )
    return {
        "sprite_files": list(audit.sprite_files),
        "alpha_cell_count": audit.alpha_cell_count,
        "port_lead_collision_count": len(expected),
        "unexpected_wire_collision_count": 0,
        "wire_interior_pin_contact_count": 0,
    }


def _verify_no_endpoint_to_wire_body_contact(circuit: Circuit) -> None:
    """拒绝端点落在另一根导线内部的隐式汇接风险。

    正常的 wire-to-wire 交叉仍被允许；这里只禁止一个网络的端点恰好插入
    另一条导线的中段，因为该形状在不同游戏版本中可能被重新解释为接点。
    """

    expanded = [wire_points(wire) for wire in circuit.wires]
    for wire_index, points in enumerate(expanded):
        for endpoint in (points[0], points[-1]):
            for other_index, other_points in enumerate(expanded):
                if wire_index == other_index:
                    continue
                if endpoint in other_points[1:-1]:
                    raise RuntimeError(
                        "Little Box 导线端点落在另一根导线内部，可能产生隐式汇接: "
                        f"wire={wire_index}, other={other_index}, point={endpoint}"
                    )


def verify_ram_component_candidate(circuit: Circuit) -> dict[str, object]:
    """执行格式、组件可用性、网络、时序和安装版精灵几何的离线审计。"""

    if (circuit.gate, circuit.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError("Little Box 候选的目标计分头发生变化")
    kinds = Counter(component.kind for component in circuit.components)
    expected_kinds = {
        AND_KIND: 8,
        REGISTER_KIND: 4,
        DECODER_KIND: 1,
        60: 2,
        61: 1,
        63: 1,
        69: 1,
    }
    if dict(kinds) != expected_kinds:
        raise RuntimeError(f"Little Box 组件集合不是基础四寄存器实现: {dict(kinds)}")
    if 118 in kinds:
        raise RuntimeError("Little Box 不得使用本关尚未解锁的 com_ram")
    if len(circuit.wires) != 2 + REGISTER_COUNT * 8:
        raise RuntimeError("Little Box 导线数目不符合已审计实现")

    board = _verify_board_bounds(circuit)
    _verify_no_endpoint_to_wire_body_contact(circuit)
    connectivity = analyze_connectivity(circuit)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"Little Box 连接审计失败 {field}: {connectivity[field]}")

    runtime = _compile_register_runtime(circuit)
    prefix = _verify_script_prefix(runtime)
    vectors = _verify_state_timing(runtime)
    geometry = _verify_sprite_geometry(circuit)
    return {
        "gate": circuit.gate,
        "delay": circuit.delay,
        "energy": circuit.energy,
        "leaderboard_tuple": [circuit.gate, circuit.delay, circuit.energy],
        "component_count": len(circuit.components),
        "component_kind_counts": {str(kind): count for kind, count in sorted(kinds.items())},
        "wire_count": len(circuit.wires),
        "state_transition_vector_count": vectors,
        "script_prefix": prefix,
        "connectivity": connectivity,
        "board": board,
        "wire_endpoint_interior_contact_count": 0,
        "geometry": geometry,
    }


def write_ram_component_candidate(project_root: Path) -> dict[str, object]:
    """写出可审计候选和元数据，不接触正式存档。"""

    project_root = Path(project_root)
    circuit = build_ram_component_candidate(project_root)
    verification = verify_ram_component_candidate(circuit)
    payload = encode_v15(circuit)
    if decode_v15(payload) != circuit:
        raise RuntimeError("Little Box 候选未通过 v15 编解码往返")

    destination = project_root / "examples" / LEVEL / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    (destination.parent / ".gitkeep").unlink(missing_ok=True)
    metadata = {
        "schema": 2,
        "level": LEVEL,
        "title": "Little Box",
        "title_zh": "小型存储器",
        "strategy": "四个 U8 字寄存器 + Decoder2 + 八个 AND 位门（读写分别门控）",
        "validation_status": "已完成离线网络、时序、v15 往返和安装版 PNG alpha 几何审计；待游戏内验收。",
        "metric_status": "368 gate / 5 delay 是公开样本中的低能耗 Pareto 点，仍以游戏重新计分为准。",
        "format_version": 15,
        "sha256": sha256(payload).hexdigest(),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
