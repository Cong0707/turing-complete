"""构造并离线验证 Little Box 的合法基础元件候选。

``ram_component`` 自己才解锁 ``com_ram``。把一个原生 RAM 写回该关卡会
在当前游戏中被判为使用未解锁组件，因而即使存档格式正确也不能运行。这里
只使用此关之前已经解锁的 Register Word、Decoder 2 和 AND：

* Decoder 2 根据 U2 地址选择四个寄存器之一；
* ``Load & select`` 只打开被选寄存器的三态输出；
* ``Save & select`` 在输出采样之后写入该寄存器；
* 四个三态输出汇到唯一的关卡输出。

候选刻意不填写未经游戏实测的门数/延迟缓存。游戏在实际运行后会重算
这些字段；离线工具只宣称拓扑、时序和版图已经验证。
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from heapq import heappop, heappush
import json
from pathlib import Path

from .analysis import wire_points
from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point, Wire
from .pins import I, O, T, PositionedPin, analyze_connectivity, positioned_pins, rotate_offset
from .simulate import _compile
from .sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, sprite_alpha_cells


LEVEL = "ram_component"
RAM_BYTES = 4
RAM_WORD_WIDTH = 8
REGISTER_KIND = 39
DECODER_KIND = 44
AND_KIND = 4

# These fields are a score cache in a circuit file, not an authoritative cost
# model.  Do not claim an old native-RAM score for a four-register solution.
HEADER_GATE = 0
HEADER_DELAY = 0
BOARD_MIN = -16
BOARD_MAX = 16

_SPRITE_NAME_BY_KIND = {
    AND_KIND: "com_and_bit.png",
    REGISTER_KIND: "com_register_word.png",
    DECODER_KIND: "com_decoder_2.png",
    60: "com_level_input_1_pin.png",
    61: "com_level_input_word.png",
    63: "com_level_input_2_pin.png",
    69: "com_level_output_word.png",
}


@dataclass(frozen=True)
class RamTick:
    """Little Box 一拍的可观测输出与写回后的四字节状态。"""

    output: int | None
    memory: tuple[int, int, int, int]


@dataclass(frozen=True)
class _RamRuntime:
    """已从真实引脚网络确认连通关系的四寄存器运行器。"""

    register_ids: tuple[int, int, int, int]

    def tick(
        self,
        *,
        load: int,
        save: int,
        address: int,
        value: int,
        memory: tuple[int, int, int, int],
    ) -> RamTick:
        """按 ``test.si`` 的读前写后顺序执行一拍。

        Register Word 的 ``load`` 是三态输出使能，``save`` 是时钟沿写入。
        在这两个控制脚分别接到 ``Load & Decoder`` 和 ``Save & Decoder``
        的前提下，以下模型就是该电路的稳定态与下一状态。
        """

        if load not in {0, 1} or save not in {0, 1}:
            raise ValueError("load 和 save 必须是 U1")
        if not 0 <= address < RAM_BYTES:
            raise ValueError("Little Box 地址必须是 U2")
        if not 0 <= value <= 0xFF:
            raise ValueError("Little Box value 必须是 U8")
        if len(memory) != RAM_BYTES or any(not 0 <= item <= 0xFF for item in memory):
            raise ValueError("Little Box 内存状态必须恰好是四个 U8")

        select = tuple(int(slot == address) for slot in range(RAM_BYTES))
        read_enable = tuple(load & bit for bit in select)
        write_enable = tuple(save & bit for bit in select)
        if sum(read_enable) != load or sum(write_enable) != save:
            raise RuntimeError("Decoder 2 未形成唯一 one-hot 选择")

        # A disabled tri-state register contributes no driver.  A selected
        # register therefore exposes its old value before all Save edges fire.
        driven = [memory[slot] for slot, enabled in enumerate(read_enable) if enabled]
        output = driven[0] if driven else None
        if len(driven) > 1:
            raise RuntimeError("多个 Register Word 同时驱动 Little Box 输出")

        next_memory = list(memory)
        for slot, enabled in enumerate(write_enable):
            if enabled:
                next_memory[slot] = value
        return RamTick(output=output, memory=tuple(next_memory))


@dataclass(frozen=True)
class _Endpoint:
    """路由器使用的引脚或裸连接点。"""

    point: Point
    pin: PositionedPin | None = None


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


def _role_id(role: str) -> int:
    return stable_permanent_id(f"ram-component/{LEVEL}", role)


def _component_alpha_cells(component: Component) -> frozenset[Point]:
    """加载当前安装版精灵，并以其 alpha 单元作为严格障碍物。"""

    try:
        name = _SPRITE_NAME_BY_KIND[component.kind]
    except KeyError as exc:  # pragma: no cover - builder only emits reviewed kinds
        raise RuntimeError(f"Little Box 缺少 kind={component.kind} 的当前精灵映射") from exc
    path = DEFAULT_COMPONENT_SPRITE_ROOT / name
    if not path.is_file():
        raise RuntimeError(f"Little Box 缺少当前组件精灵: {path}")
    return frozenset(
        (
            component.position[0] + rotate_offset(cell, component.rotation)[0],
            component.position[1] + rotate_offset(cell, component.rotation)[1],
        )
        for cell in sprite_alpha_cells(path)
    )


class _LittleBoxRouter:
    """只走板内空白格和自身端口走廊的确定性四向路由器。

    组件精灵的 alpha 还覆盖了部分真实端口。不能简单把整个 alpha 区域封死，
    也不能允许导线从任意方向穿进图形。这里先强制走完端口的水平方向进出
    走廊，再在所有组件外部搜索，因此两种错误都被排除。
    """

    def __init__(self, components: tuple[Component, ...]) -> None:
        self.components = components
        self.footprints = tuple(_component_alpha_cells(component) for component in components)
        self.occupied: dict[Point, set[int]] = defaultdict(set)
        self.pins_at: dict[Point, list[PositionedPin]] = defaultdict(list)
        self.pins_by_key: dict[tuple[int, str], PositionedPin] = {}
        for index, footprint in enumerate(self.footprints):
            for point in footprint:
                self.occupied[point].add(index)
            for pin in positioned_pins(components[index], index):
                self.pins_at[pin.position].append(pin)
                self.pins_by_key[(index, pin.name)] = pin
        self.junctions: set[Point] = set()

        overlap = sorted(point for point, owners in self.occupied.items() if len(owners) > 1)
        if overlap:
            raise RuntimeError(f"Little Box 元件精灵重叠: {overlap[:8]}")

    def pin(self, component_index: int, name: str) -> _Endpoint:
        try:
            pin = self.pins_by_key[(component_index, name)]
        except KeyError as exc:
            raise RuntimeError(f"Little Box 缺少 pin {component_index}:{name}") from exc
        return _Endpoint(pin.position, pin)

    def reserve_junction(self, point: Point) -> _Endpoint:
        if not (BOARD_MIN <= point[0] <= BOARD_MAX and BOARD_MIN <= point[1] <= BOARD_MAX):
            raise RuntimeError(f"Little Box 汇接点越过关卡边界: {point}")
        if point in self.occupied or point in self.pins_at or point in self.junctions:
            raise RuntimeError(f"Little Box 汇接点不是空白单元: {point}")
        self.junctions.add(point)
        return _Endpoint(point)

    def _access_path(self, endpoint: _Endpoint) -> tuple[Point, ...]:
        """返回从真实引脚到图形外一格的唯一合法进出序列。"""

        if endpoint.pin is None:
            return (endpoint.point,)
        component = self.components[endpoint.pin.component_index]
        step = rotate_offset(
            (-1, 0) if endpoint.pin.direction == I else (1, 0),
            component.rotation,
        )
        path = [endpoint.point]
        current = endpoint.point
        # A current sprite is under ten cells wide.  This bound catches a bad
        # pin mapping rather than generating an unbounded route.
        for _ in range(16):
            current = (current[0] + step[0], current[1] + step[1])
            path.append(current)
            if current not in self.footprints[endpoint.pin.component_index]:
                break
        else:  # pragma: no cover - guarded against malformed future sprites
            raise RuntimeError(f"Little Box 引脚走廊无法离开组件: {endpoint.pin}")
        if not (BOARD_MIN <= current[0] <= BOARD_MAX and BOARD_MIN <= current[1] <= BOARD_MAX):
            raise RuntimeError(f"Little Box 引脚走廊越过关卡边界: {endpoint.pin}")
        return tuple(path)

    def _is_free_middle_cell(self, point: Point, allowed_junctions: frozenset[Point]) -> bool:
        if not (BOARD_MIN <= point[0] <= BOARD_MAX and BOARD_MIN <= point[1] <= BOARD_MAX):
            return False
        if point in self.occupied or point in self.pins_at:
            return False
        return point not in self.junctions or point in allowed_junctions

    def route(self, source: _Endpoint, sink: _Endpoint, *, comment: str) -> Wire:
        """在外部空白区域连接两个端点，并固化端口进出方向。"""

        source_path = self._access_path(source)
        sink_path = self._access_path(sink)
        start = source_path[-1]
        target = sink_path[-1]
        allowed_junctions = frozenset(
            endpoint.point for endpoint in (source, sink) if endpoint.pin is None
        )
        if not self._is_free_middle_cell(start, allowed_junctions):
            raise RuntimeError(f"Little Box 源端口外侧不是空白格: {source}")
        if not self._is_free_middle_cell(target, allowed_junctions):
            raise RuntimeError(f"Little Box 目标端口外侧不是空白格: {sink}")

        # State includes direction so bend cost gives stable, compact routes.
        frontier: list[tuple[int, int, int, int, int]] = []
        heappush(frontier, (abs(start[0] - target[0]) + abs(start[1] - target[1]), 0, start[0], start[1], -1))
        costs: dict[tuple[Point, int], int] = {(start, -1): 0}
        previous: dict[tuple[Point, int], tuple[Point, int]] = {}
        final: tuple[Point, int] | None = None
        directions = ((1, 0), (0, 1), (-1, 0), (0, -1))

        while frontier:
            _, cost, x, y, direction_index = heappop(frontier)
            state = ((x, y), direction_index)
            if cost != costs.get(state):
                continue
            if (x, y) == target:
                final = state
                break
            for next_direction, (dx, dy) in enumerate(directions):
                point = (x + dx, y + dy)
                if point not in {start, target} and not self._is_free_middle_cell(
                    point, allowed_junctions
                ):
                    continue
                next_cost = cost + 1 + (
                    4 if direction_index >= 0 and direction_index != next_direction else 0
                )
                next_state = (point, next_direction)
                if next_cost >= costs.get(next_state, 1 << 60):
                    continue
                costs[next_state] = next_cost
                previous[next_state] = state
                heuristic = abs(point[0] - target[0]) + abs(point[1] - target[1])
                heappush(frontier, (next_cost + heuristic, next_cost, point[0], point[1], next_direction))

        if final is None:
            raise RuntimeError(f"Little Box 无法安全布线 {comment}: {source.point} -> {sink.point}")

        middle_reversed: list[Point] = []
        state = final
        while True:
            middle_reversed.append(state[0])
            if state == (start, -1):
                break
            state = previous[state]
        middle = list(reversed(middle_reversed))
        points = list(source_path)
        points.extend(middle[1:])
        points.extend(reversed(sink_path[:-1]))
        if len(points) < 2 or any(first == second for first, second in zip(points, points[1:])):
            raise RuntimeError(f"Little Box 生成了退化导线 {comment}: {points}")
        return wire_from_vertices(tuple(points), comment=comment)


def _role_indices(circuit: Circuit) -> dict[str, int]:
    roles = {
        "decoder": _role_id("decoder"),
        **{f"read-{slot}": _role_id(f"read-{slot}") for slot in range(RAM_BYTES)},
        **{f"write-{slot}": _role_id(f"write-{slot}") for slot in range(RAM_BYTES)},
        **{f"register-{slot}": _role_id(f"register-{slot}") for slot in range(RAM_BYTES)},
    }
    by_id = {component.permanent_id: index for index, component in enumerate(circuit.components)}
    try:
        return {role: by_id[permanent_id] for role, permanent_id in roles.items()}
    except KeyError as exc:
        raise RuntimeError(f"Little Box 缺少受控元件 permanent_id={exc.args[0]}") from exc


def _fixed_index(circuit: Circuit, label: str, kind: int) -> int:
    matches = [
        index
        for index, component in enumerate(circuit.components)
        if component.kind == kind and component.user_label == label
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Little Box 无法唯一找到固定接口 {label!r}: {matches}")
    return matches[0]


def _star(
    router: _LittleBoxRouter,
    *,
    junction: Point,
    endpoints: tuple[_Endpoint, ...],
    name: str,
) -> tuple[Wire, ...]:
    """将一组引脚通过一个专属空白汇接点变成同一网络。"""

    hub = router.reserve_junction(junction)
    return tuple(
        router.route(endpoint, hub, comment=f"{name}/{index}")
        for index, endpoint in enumerate(endpoints)
    )


def build_ram_component_candidate(project_root: Path) -> Circuit:
    """生成只使用已解锁基础组件的确定性 v15 Little Box。"""

    immutable = _load_scaffold_components(Path(project_root))
    row_y = (-10, -3, 4, 11)
    decoder = _component("decoder", DECODER_KIND, (-10, -5), word_size=1)
    reads = tuple(
        _component(f"read-{slot}", AND_KIND, (-6, row_y[slot]), word_size=1)
        for slot in range(RAM_BYTES)
    )
    writes = tuple(
        # x=-1 leaves x=2 clear, which is the Register Word input's only
        # legal left-side escape cell under the current sprite geometry.
        _component(f"write-{slot}", AND_KIND, (-1, row_y[slot]), word_size=1)
        for slot in range(RAM_BYTES)
    )
    registers = tuple(
        _component(
            f"register-{slot}",
            REGISTER_KIND,
            (6, row_y[slot]),
            word_size=RAM_WORD_WIDTH,
        )
        for slot in range(RAM_BYTES)
    )
    components = immutable + (decoder,) + reads + writes + registers
    provisional = Circuit(gate=HEADER_GATE, delay=HEADER_DELAY, components=components)
    roles = _role_indices(provisional)
    load = _fixed_index(provisional, "Load", 60)
    save = _fixed_index(provisional, "Save", 60)
    address = _fixed_index(provisional, "Address", 63)
    value = _fixed_index(provisional, "Value", 61)
    output = _fixed_index(provisional, "Output", 69)
    router = _LittleBoxRouter(provisional.components)

    def pin(role: str, name: str) -> _Endpoint:
        return router.pin(roles[role], name)

    wires: list[Wire] = []
    # Address bit order is little-endian: value0 -> select0, value1 -> select1.
    wires.append(router.route(router.pin(address, "value0"), pin("decoder", "select0"), comment="address-bit-0"))
    wires.append(router.route(router.pin(address, "value1"), pin("decoder", "select1"), comment="address-bit-1"))

    # The same decoder output drives the read and write AND for each slot.
    select_hubs = ((-8, -13), (-8, -1), (-8, 2), (-8, 9))
    for slot, hub in enumerate(select_hubs):
        wires.extend(
            _star(
                router,
                junction=hub,
                endpoints=(
                    pin("decoder", f"out{slot}"),
                    pin(f"read-{slot}", "in0"),
                    pin(f"write-{slot}", "in0"),
                ),
                name=f"select-{slot}",
            )
        )

    # Global Load and Save fan out to the second input of the corresponding ANDs.
    wires.extend(
        _star(
            router,
            junction=(-11, -12),
            endpoints=(
                router.pin(load, "value"),
                *(pin(f"read-{slot}", "in1") for slot in range(RAM_BYTES)),
            ),
            name="load",
        )
    )
    wires.extend(
        _star(
            router,
            junction=(-11, -9),
            endpoints=(
                router.pin(save, "value"),
                *(pin(f"write-{slot}", "in1") for slot in range(RAM_BYTES)),
            ),
            name="save",
        )
    )

    # Each AND independently controls one Register Word.
    for slot in range(RAM_BYTES):
        wires.append(
            router.route(
                pin(f"read-{slot}", "out"),
                pin(f"register-{slot}", "load"),
                comment=f"read-enable-{slot}",
            )
        )
        wires.append(
            router.route(
                pin(f"write-{slot}", "out"),
                pin(f"register-{slot}", "save"),
                comment=f"write-enable-{slot}",
            )
        )

    # The input word is broadcast to all register data inputs; only a selected
    # Save control captures it.  Register outputs legally share one tri-state bus.
    wires.extend(
        _star(
            router,
            junction=(-8, 1),
            endpoints=(
                router.pin(value, "value"),
                *(pin(f"register-{slot}", "in") for slot in range(RAM_BYTES)),
            ),
            name="value",
        )
    )
    wires.extend(
        _star(
            router,
            junction=(-1, 0),
            endpoints=(
                *(pin(f"register-{slot}", "out") for slot in range(RAM_BYTES)),
                router.pin(output, "value"),
            ),
            name="output",
        )
    )

    return Circuit(
        gate=HEADER_GATE,
        delay=HEADER_DELAY,
        description=(
            "Codex Little Box: Decoder 2 选择四个 Register Word；读使能和写使能"
            "分别与地址 one-hot 相与。门数与延迟由当前游戏实际载入后重算。"
        ),
        components=components,
        wires=tuple(wires),
    )


def _assert_networks(circuit: Circuit) -> _RamRuntime:
    """证明每一个实际引脚网络恰好是所设计的那条信号。"""

    compiled = _compile(circuit)
    roles = _role_indices(circuit)
    load = _fixed_index(circuit, "Load", 60)
    save = _fixed_index(circuit, "Save", 60)
    address = _fixed_index(circuit, "Address", 63)
    value = _fixed_index(circuit, "Value", 61)
    output = _fixed_index(circuit, "Output", 69)

    def key(component_index: int, name: str) -> tuple[int, str]:
        return (component_index, name)

    groups: dict[str, set[tuple[int, str]]] = {
        "address-0": {key(address, "value0"), key(roles["decoder"], "select0")},
        "address-1": {key(address, "value1"), key(roles["decoder"], "select1")},
        "load": {key(load, "value")}
        | {key(roles[f"read-{slot}"], "in1") for slot in range(RAM_BYTES)},
        "save": {key(save, "value")}
        | {key(roles[f"write-{slot}"], "in1") for slot in range(RAM_BYTES)},
        "value": {key(value, "value")}
        | {key(roles[f"register-{slot}"], "in") for slot in range(RAM_BYTES)},
        "output": {key(output, "value")}
        | {key(roles[f"register-{slot}"], "out") for slot in range(RAM_BYTES)},
    }
    for slot in range(RAM_BYTES):
        groups[f"select-{slot}"] = {
            key(roles["decoder"], f"out{slot}"),
            key(roles[f"read-{slot}"], "in0"),
            key(roles[f"write-{slot}"], "in0"),
        }
        groups[f"read-enable-{slot}"] = {
            key(roles[f"read-{slot}"], "out"),
            key(roles[f"register-{slot}"], "load"),
        }
        groups[f"write-enable-{slot}"] = {
            key(roles[f"write-{slot}"], "out"),
            key(roles[f"register-{slot}"], "save"),
        }

    expected_pins = set().union(*groups.values())
    actual_pins = set(compiled.pin_networks)
    if actual_pins != expected_pins:
        raise RuntimeError(
            "Little Box 引脚集合不匹配："
            f"missing={sorted(expected_pins - actual_pins)}, extra={sorted(actual_pins - expected_pins)}"
        )
    for name, group in groups.items():
        networks = {compiled.pin_networks[item] for item in group}
        if len(networks) != 1:
            raise RuntimeError(f"Little Box 网络未连通 {name}: {sorted(networks)}")
        network = next(iter(networks))
        actual_group = {item for item, value in compiled.pin_networks.items() if value == network}
        if actual_group != group:
            raise RuntimeError(
                f"Little Box 网络错误合并 {name}: expected={sorted(group)}, actual={sorted(actual_group)}"
            )

    register_ids = tuple(circuit.components[roles[f"register-{slot}"]].permanent_id for slot in range(RAM_BYTES))
    return _RamRuntime(register_ids=register_ids)


def _access_path_for_pin(
    components: tuple[Component, ...],
    footprints: tuple[frozenset[Point], ...],
    pin: PositionedPin,
) -> tuple[Point, ...]:
    component = components[pin.component_index]
    step = rotate_offset((-1, 0) if pin.direction == I else (1, 0), component.rotation)
    path = [pin.position]
    current = pin.position
    for _ in range(16):
        current = (current[0] + step[0], current[1] + step[1])
        path.append(current)
        if current not in footprints[pin.component_index]:
            return tuple(path)
    raise RuntimeError(f"Little Box 端口走廊无法离开组件: {pin}")


def _verify_geometry(circuit: Circuit) -> dict[str, object]:
    """使用当前 PNG alpha 和端口走廊规则审计所有实际导线。"""

    footprints = tuple(_component_alpha_cells(component) for component in circuit.components)
    owner_by_cell: dict[Point, set[int]] = defaultdict(set)
    pins_at: dict[Point, list[PositionedPin]] = defaultdict(list)
    for index, footprint in enumerate(footprints):
        for point in footprint:
            owner_by_cell[point].add(index)
        for pin in positioned_pins(circuit.components[index], index):
            pins_at[pin.position].append(pin)

    overlap = sorted(point for point, owners in owner_by_cell.items() if len(owners) > 1)
    if overlap:
        raise RuntimeError(f"Little Box 元件精灵重叠: {overlap[:8]}")

    wire_body_contacts = 0
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        if any(
            not (BOARD_MIN <= point[0] <= BOARD_MAX and BOARD_MIN <= point[1] <= BOARD_MAX)
            for point in points
        ):
            raise RuntimeError(f"Little Box 导线越过 size=16 边界: wire={wire_index}")

        endpoint_pins: list[PositionedPin] = []
        allowed_contacts: dict[int, set[Point]] = defaultdict(set)
        for endpoint in (points[0], points[-1]):
            matches = pins_at.get(endpoint, [])
            if len(matches) > 1:
                raise RuntimeError(f"Little Box 导线端点落在多个端口: wire={wire_index}, point={endpoint}")
            if matches:
                pin = matches[0]
                endpoint_pins.append(pin)
                allowed_contacts[pin.component_index].update(
                    _access_path_for_pin(circuit.components, footprints, pin)
                )
            elif endpoint in owner_by_cell:
                raise RuntimeError(f"Little Box 导线端点落在元件本体: wire={wire_index}, point={endpoint}")

        for point_index, point in enumerate(points):
            is_endpoint = point_index in {0, len(points) - 1}
            if not is_endpoint and point in pins_at:
                raise RuntimeError(
                    f"Little Box 导线经过非端点引脚: wire={wire_index}, point={point}, "
                    f"pins={[pin.name for pin in pins_at[point]]}"
                )
            for owner in owner_by_cell.get(point, ()):
                if point not in allowed_contacts[owner]:
                    raise RuntimeError(
                        f"Little Box 导线穿过元件本体: wire={wire_index}, component={owner}, point={point}"
                    )
                wire_body_contacts += 1

    return {
        "sprite_files": sorted(set(_SPRITE_NAME_BY_KIND.values())),
        "component_overlap_cell_count": 0,
        "wire_body_contact_count": wire_body_contacts,
        "wire_body_contact_rule": "仅允许导线自身端点沿指定水平方向进出端口精灵",
        "wire_interior_pin_contact_count": 0,
        "board_bounds": [BOARD_MIN, BOARD_MAX],
    }


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
    """执行组件解锁、结构、真实网络、时序和 PNG 版图完整验证。"""

    if (circuit.gate, circuit.delay) != (HEADER_GATE, HEADER_DELAY):
        raise RuntimeError("Little Box 候选不应伪造未经游戏实测的计分缓存")
    kinds = [component.kind for component in circuit.components]
    if 118 in kinds:
        raise RuntimeError("Little Box 候选错误使用了本关才解锁的 com_ram")
    if kinds.count(REGISTER_KIND) != RAM_BYTES or kinds.count(DECODER_KIND) != 1 or kinds.count(AND_KIND) != 8:
        raise RuntimeError("Little Box 基础元件拓扑不是四寄存器 + Decoder2 + 八个 AND")
    registers = [component for component in circuit.components if component.kind == REGISTER_KIND]
    if any(component.word_size != RAM_WORD_WIDTH for component in registers):
        raise RuntimeError("Little Box Register Word 必须全部为 U8")

    connectivity = analyze_connectivity(circuit)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"Little Box 候选连接审计失败 {field}: {connectivity[field]}")

    runtime = _assert_networks(circuit)
    geometry = _verify_geometry(circuit)
    prefix = _verify_script_prefix(runtime)
    vectors = _verify_state_timing(runtime)
    return {
        "score_cache": {"gate": circuit.gate, "delay": circuit.delay, "energy": circuit.energy},
        "metric_status": "未实测；由游戏实际载入和运行后重算",
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "state_transition_vector_count": vectors,
        "script_prefix": prefix,
        "connectivity": connectivity,
        "geometry": geometry,
        "component_inventory": {
            "register_word": RAM_BYTES,
            "decoder_2": 1,
            "and_bit": 8,
            "com_ram": 0,
        },
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
        "schema": 2,
        "level": LEVEL,
        "title": "Little Box",
        "title_zh": "小型存储器",
        "strategy": "Decoder 2 + 8 个 AND + 4 个 Register Word；不使用本关未解锁的 com_ram",
        "format_version": 15,
        "sha256": sha256(payload).hexdigest(),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
