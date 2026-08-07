"""Cost-neutral scalar-to-word technology mapping."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from turingsynth.config import ProjectConfig
from turingsynth.ir.logical import Bit, Cell, CustomCell, LogicNetlist
from turingsynth.ir.physical import PhysicalComponent, PhysicalDesign, PhysicalNet, PinRef
from turingsynth.library import CustomModule
from turingsynth.mapping.native import GATE_LIBRARY, MAKER_KIND, SPLITTER_KIND
from turingsynth.targets.context import TargetContext, stable_permanent_id


@dataclass
class _Net:
    name: str
    width: int
    source: PinRef
    logic_bits: tuple[Bit, ...]
    sinks: list[PinRef]


class _Mapper:
    def __init__(
        self,
        config: ProjectConfig,
        logical: LogicNetlist,
        target: TargetContext,
        custom_modules: dict[str, CustomModule] | None = None,
    ) -> None:
        self.config = config
        self.logical = logical
        self.target = target
        self.custom_modules = custom_modules or {}
        self.components = {component.key: component for component in target.components}
        self.nets: dict[str, _Net] = {}
        self.bit_source: dict[Bit, str] = {}
        self.bus_source: dict[tuple[Bit, ...], str] = {}
        self.bit_affinity: dict[Bit, float] = {"0": 0.0, "1": 0.0}
        self._counter: defaultdict[str, int] = defaultdict(int)

    def _key(self, prefix: str) -> str:
        value = self._counter[prefix]
        self._counter[prefix] += 1
        return f"{prefix}:{value}"

    def _add_component(
        self,
        key: str,
        *,
        kind: int,
        word_size: int,
        role: str,
        affinity: float,
        logic_depth: int,
        gate_cost: int = 0,
        gate_delay: int = 0,
        custom_id: int = 0,
        custom_word_sizes: tuple[tuple[int, int], ...] = (),
    ) -> str:
        if key in self.components:
            raise ValueError(f"duplicate physical component key {key!r}")
        self.components[key] = PhysicalComponent(
            key=key,
            kind=kind,
            word_size=word_size,
            role=role,
            affinity=affinity,
            logic_depth=logic_depth,
            gate_cost=gate_cost,
            gate_delay=gate_delay,
            permanent_id=stable_permanent_id(self.config.logical_key, key),
            custom_id=custom_id,
            custom_word_sizes=custom_word_sizes,
        )
        return key

    def _add_net(
        self,
        name: str,
        width: int,
        source: PinRef,
        logic_bits: tuple[Bit, ...],
    ) -> str:
        if name in self.nets:
            raise ValueError(f"duplicate physical net {name!r}")
        if width != len(logic_bits):
            raise ValueError(f"net {name!r} width differs from logic-bit tuple")
        self.nets[name] = _Net(name, width, source, logic_bits, [])
        return name

    def _connect(self, net: str, sink: PinRef) -> None:
        if sink not in self.nets[net].sinks:
            self.nets[net].sinks.append(sink)

    def _constant(self, value: str) -> str:
        found = self.bit_source.get(value)
        if found is not None:
            return found
        key = f"constant:{value}"
        self._add_component(
            key,
            kind=2 if value == "1" else 1,
            word_size=1,
            role="constant",
            affinity=0.0,
            logic_depth=0,
        )
        net = self._add_net(
            f"net:{key}", 1, PinRef(key, "out"), (value,)
        )
        self.bit_source[value] = net
        self.bus_source[(value,)] = net
        return net

    def _split_word(
        self,
        source_net: str,
        bits: tuple[Bit, ...],
        *,
        owner: str,
        depth: int,
        affinity: float,
    ) -> None:
        width = len(bits)
        if width in {2, 4, 8}:
            key = self._add_component(
                f"{owner}:split{width}",
                kind=SPLITTER_KIND[width],
                word_size=width,
                role="splitter",
                affinity=affinity,
                logic_depth=depth,
            )
            self._connect(source_net, PinRef(key, "in"))
            for lane, bit in enumerate(bits):
                net = self._add_net(
                    f"net:{key}:lane:{lane}",
                    1,
                    PinRef(key, f"out{lane}"),
                    (bit,),
                )
                self.bit_source[bit] = net
            return
        if width in {32, 64}:
            key = self._add_component(
                f"{owner}:split{width}",
                kind=SPLITTER_KIND[width],
                word_size=width,
                role="splitter",
                affinity=affinity,
                logic_depth=depth,
            )
            self._connect(source_net, PinRef(key, "in"))
            for byte_index in range(width // 8):
                byte_bits = bits[byte_index * 8 : (byte_index + 1) * 8]
                byte_net = self._add_net(
                    f"net:{key}:byte:{byte_index}",
                    8,
                    PinRef(key, f"out{byte_index}"),
                    byte_bits,
                )
                self.bus_source[byte_bits] = byte_net
                self._split_word(
                    byte_net,
                    byte_bits,
                    owner=f"{owner}:byte:{byte_index}",
                    depth=depth,
                    affinity=sum(self.bit_affinity[bit] for bit in byte_bits) / 8,
                )
            return
        if width != 1:
            raise ValueError(
                f"port width {width} cannot be split by current native Maker/Splitter ABI"
            )
        self.bit_source[bits[0]] = source_net

    def _create_ports(self) -> None:
        for port_index, port in enumerate(self.logical.input_ports):
            key = self.target.port_component[port.name]
            pin = self.target.port_pin[port.name]
            bits = tuple(port.bits)
            for lane, bit in enumerate(bits):
                self.bit_affinity[bit] = float(lane) + port_index * 0.01
            net = self._add_net(
                f"net:port:{port.name}", len(bits), PinRef(key, pin), bits
            )
            self.bus_source[bits] = net
            if len(bits) == 1:
                self.bit_source[bits[0]] = net
            else:
                self._split_word(
                    net,
                    bits,
                    owner=f"port:{port.name}",
                    depth=0,
                    affinity=sum(self.bit_affinity[bit] for bit in bits) / len(bits),
                )

    def _topology(self) -> tuple[list[Cell | CustomCell], dict[int, int]]:
        available = {
            bit: 0
            for port in self.logical.input_ports
            for bit in port.bits
            if isinstance(bit, int)
        }
        available.update({"0": 0, "1": 0})
        pending: list[Cell | CustomCell] = [
            *self.logical.cells,
            *self.logical.custom_cells,
        ]
        ordered: list[Cell | CustomCell] = []
        depth: dict[int, int] = {}
        while pending:
            ready = [
                cell
                for cell in pending
                if all(
                    bit in available
                    for bit in (
                        cell.inputs if isinstance(cell, Cell) else cell.input_bits
                    )
                )
            ]
            if not ready:
                raise ValueError("logic netlist has no topological mapping order")
            ready.sort(key=lambda cell: cell.name)
            for cell in ready:
                inputs = cell.inputs if isinstance(cell, Cell) else cell.input_bits
                if isinstance(cell, Cell):
                    outputs = (cell.output,)
                    delay = GATE_LIBRARY[cell.op].delay
                else:
                    try:
                        module = self.custom_modules[cell.module]
                    except KeyError as exc:
                        raise ValueError(
                            f"custom cell {cell.name!r} references unknown module "
                            f"{cell.module!r}"
                        ) from exc
                    outputs = cell.output_bits
                    delay = module.circuit.delay
                value = max((available[bit] for bit in inputs), default=0) + delay
                affinity = max(
                    (self.bit_affinity.get(bit, 0.0) for bit in inputs),
                    default=0.0,
                )
                if isinstance(cell, CustomCell):
                    output_lanes = {
                        output: lane
                        for port in cell.ports
                        if port.direction == "output"
                        for lane, output in enumerate(port.bits)
                    }
                else:
                    output_lanes = {}
                for output in outputs:
                    depth[output] = value
                    available[output] = value
                    self.bit_affinity[output] = affinity + output_lanes.get(output, 0)
                ordered.append(cell)
                pending.remove(cell)
        return ordered, depth

    def _source_for_bit(self, bit: Bit) -> str:
        if bit in {"0", "1"}:
            return self._constant(str(bit))
        try:
            return self.bit_source[bit]
        except KeyError as exc:
            raise ValueError(f"logic bit {bit!r} has no physical scalar source") from exc

    def _operand(
        self,
        bits: tuple[Bit, ...],
        *,
        owner: str,
        operand: int,
        depth: int,
        affinity: float,
    ) -> str:
        found = self.bus_source.get(bits)
        if found is not None:
            return found
        width = len(bits)
        if width == 1:
            return self._source_for_bit(bits[0])
        if width not in {2, 4, 8}:
            raise ValueError(f"internal pack width {width} is unsupported")
        key = self._add_component(
            f"{owner}:maker:{operand}",
            kind=MAKER_KIND[width],
            word_size=width,
            role="maker",
            affinity=affinity,
            logic_depth=depth,
        )
        for lane, bit in enumerate(bits):
            self._connect(self._source_for_bit(bit), PinRef(key, f"in{lane}"))
        net = self._add_net(
            f"net:{key}", width, PinRef(key, "out"), bits
        )
        self.bus_source[bits] = net
        return net

    @staticmethod
    def _chunks(cells: list[Cell], widths: tuple[int, ...]) -> list[list[Cell]]:
        result: list[list[Cell]] = []
        offset = 0
        for width in widths:
            while len(cells) - offset >= width:
                result.append(cells[offset : offset + width])
                offset += width
        result.extend([[cell] for cell in cells[offset:]])
        return result

    def _map_native_group(
        self,
        depth: int,
        op: str,
        group: list[Cell],
    ) -> None:
        spec = GATE_LIBRARY[op]
        width = len(group)
        outputs = tuple(cell.output for cell in group)
        affinity = sum(self.bit_affinity[bit] for bit in outputs) / width
        key = self._key(f"gate:{depth}:{op.lower()}:w{width}")
        self._add_component(
            key,
            kind=spec.scalar_kind if width == 1 else spec.word_kind,
            word_size=width,
            role="gate",
            affinity=affinity,
            logic_depth=depth,
            gate_cost=spec.cost_per_bit * width,
            gate_delay=spec.delay,
        )
        for operand in range(spec.arity):
            operand_bits = tuple(cell.inputs[operand] for cell in group)
            source = self._operand(
                operand_bits,
                owner=key,
                operand=operand,
                depth=depth - spec.delay,
                affinity=affinity,
            )
            pin = "in" if spec.arity == 1 else f"in{operand}"
            self._connect(source, PinRef(key, pin))
        output_net = self._add_net(
            f"net:{key}:out", width, PinRef(key, "out"), outputs
        )
        self.bus_source[outputs] = output_net
        if width == 1:
            self.bit_source[outputs[0]] = output_net
        else:
            self._split_word(
                output_net,
                outputs,
                owner=key,
                depth=depth,
                affinity=affinity,
            )

    def _map_custom_cell(
        self,
        cell: CustomCell,
        depth_by_bit: dict[int, int],
    ) -> None:
        module = self.custom_modules[cell.module]
        child_ports = module.port_components()
        inputs = cell.input_bits
        affinity = max(
            (self.bit_affinity.get(bit, 0.0) for bit in inputs),
            default=0.0,
        )
        output_depth = max(
            (depth_by_bit[bit] for bit in cell.output_bits),
            default=module.circuit.delay,
        )
        key = f"custom:{cell.name}"
        custom_word_sizes = tuple(
            (child_ports[port.name].permanent_id, len(port.bits))
            for port in cell.ports
        )
        self._add_component(
            key,
            kind=78,
            word_size=1,
            role="custom",
            affinity=affinity,
            logic_depth=output_depth,
            gate_cost=module.circuit.gate,
            gate_delay=module.circuit.delay,
            custom_id=module.circuit.custom_id,
            custom_word_sizes=custom_word_sizes,
        )
        for port in cell.ports:
            bits = tuple(port.bits)
            if port.direction == "input":
                input_depth = max(
                    (
                        depth_by_bit.get(bit, 0)
                        if isinstance(bit, int)
                        else 0
                        for bit in bits
                    ),
                    default=0,
                )
                source = self._output_bus(
                    bits,
                    owner=f"{key}:input:{port.name}",
                    depth=input_depth,
                    affinity=affinity,
                )
                self._connect(source, PinRef(key, port.name))
                continue
            output_bits = tuple(bits)
            output_net = self._add_net(
                f"net:{key}:output:{port.name}",
                len(output_bits),
                PinRef(key, port.name),
                output_bits,
            )
            self.bus_source[output_bits] = output_net
            if len(output_bits) == 1:
                self.bit_source[output_bits[0]] = output_net
            else:
                self._split_word(
                    output_net,
                    output_bits,
                    owner=f"{key}:output:{port.name}",
                    depth=output_depth,
                    affinity=affinity,
                )

    def _map_cells(self) -> dict[int, int]:
        ordered, depth_by_bit = self._topology()
        by_depth_op: dict[tuple[int, str], list[Cell]] = defaultdict(list)
        custom_by_depth: dict[int, list[CustomCell]] = defaultdict(list)
        for cell in ordered:
            if isinstance(cell, Cell):
                by_depth_op[(depth_by_bit[cell.output], cell.op)].append(cell)
            else:
                depth = max(
                    (depth_by_bit[bit] for bit in cell.output_bits),
                    default=self.custom_modules[cell.module].circuit.delay,
                )
                custom_by_depth[depth].append(cell)
        depths = sorted(
            {depth for depth, _op in by_depth_op} | set(custom_by_depth)
        )
        order_index = {cell.name: index for index, cell in enumerate(ordered)}
        for depth in depths:
            operations = sorted(
                op for candidate_depth, op in by_depth_op if candidate_depth == depth
            )
            for op in operations:
                cells = by_depth_op[(depth, op)]
                cells.sort(key=lambda cell: (self.bit_affinity[cell.output], cell.name))
                for group in self._chunks(cells, self.config.pack_widths):
                    self._map_native_group(depth, op, group)
            for cell in sorted(
                custom_by_depth.get(depth, ()),
                key=lambda item: order_index[item.name],
            ):
                self._map_custom_cell(cell, depth_by_bit)
        return depth_by_bit

    def _output_bus(
        self, bits: tuple[Bit, ...], *, owner: str, depth: int, affinity: float
    ) -> str:
        found = self.bus_source.get(bits)
        if found is not None:
            return found
        width = len(bits)
        if width in {1, 2, 4, 8}:
            return self._operand(bits, owner=owner, operand=0, depth=depth, affinity=affinity)
        if width in {32, 64}:
            byte_nets = []
            for byte_index in range(width // 8):
                byte_bits = bits[byte_index * 8 : (byte_index + 1) * 8]
                byte_nets.append(
                    self._operand(
                        byte_bits,
                        owner=f"{owner}:byte:{byte_index}",
                        operand=0,
                        depth=depth,
                        affinity=sum(self.bit_affinity.get(bit, 0.0) for bit in byte_bits) / 8,
                    )
                )
            key = self._add_component(
                f"{owner}:maker:{width}",
                kind=MAKER_KIND[width],
                word_size=width,
                role="maker",
                affinity=affinity,
                logic_depth=depth,
            )
            for byte_index, byte_net in enumerate(byte_nets):
                self._connect(byte_net, PinRef(key, f"in{byte_index}"))
            net = self._add_net(f"net:{key}", width, PinRef(key, "out"), bits)
            self.bus_source[bits] = net
            return net
        raise ValueError(f"output width {width} is unsupported")

    def _connect_outputs(self, depth_by_bit: dict[int, int]) -> int:
        output_depths = []
        for port_index, port in enumerate(self.logical.output_ports):
            bits = tuple(port.bits)
            depths = [depth_by_bit.get(bit, 0) if isinstance(bit, int) else 0 for bit in bits]
            depth = max(depths, default=0)
            output_depths.append(depth)
            affinity = (
                sum(self.bit_affinity.get(bit, float(lane)) for lane, bit in enumerate(bits))
                / max(1, len(bits))
            ) + port_index * 0.01
            source = self._output_bus(
                bits, owner=f"output:{port.name}", depth=depth, affinity=affinity
            )
            self._connect(
                source,
                PinRef(self.target.port_component[port.name], self.target.port_pin[port.name]),
            )
        return max(output_depths, default=0)

    def build(self) -> PhysicalDesign:
        self._create_ports()
        depth_by_bit = self._map_cells()
        delay = self._connect_outputs(depth_by_bit)
        all_nets = tuple(
            PhysicalNet(
                name=net.name,
                width=net.width,
                source=net.source,
                sinks=tuple(net.sinks),
                logic_bits=net.logic_bits,
            )
            for net in self.nets.values()
            if net.sinks
        )
        incoming: dict[str, list[PhysicalNet]] = defaultdict(list)
        for net in all_nets:
            for sink in net.sinks:
                incoming[sink.component].append(net)
        components_in_use = {
            key
            for key, component in self.components.items()
            if component.role in {"template", "input_port", "output_port"}
        }
        queue = list(components_in_use)
        while queue:
            component_key = queue.pop()
            for net in incoming.get(component_key, ()):
                if net.source.component not in components_in_use:
                    components_in_use.add(net.source.component)
                    queue.append(net.source.component)
        nets = tuple(
            PhysicalNet(
                name=net.name,
                width=net.width,
                source=net.source,
                sinks=tuple(
                    sink for sink in net.sinks if sink.component in components_in_use
                ),
                logic_bits=net.logic_bits,
            )
            for net in all_nets
            if net.source.component in components_in_use
            and any(sink.component in components_in_use for sink in net.sinks)
        )
        components = tuple(
            component
            for key, component in self.components.items()
            if key in components_in_use or component.role in {"template", "input_port", "output_port"}
        )
        gate = sum(component.gate_cost for component in components)
        design = PhysicalDesign(
            name=self.config.name,
            components=components,
            nets=nets,
            gate=gate,
            delay=delay,
            target_kind=self.target.kind,
            custom_id=self.target.custom_id,
        )
        design.component_by_key()
        return design


def map_to_native(
    config: ProjectConfig,
    logical: LogicNetlist,
    target: TargetContext,
    *,
    custom_modules: dict[str, CustomModule] | None = None,
) -> PhysicalDesign:
    """Map a normalized scalar netlist without changing cost or arrival."""

    return _Mapper(config, logical, target, custom_modules).build()
