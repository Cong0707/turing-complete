# 字节加法器布尔网表布线原型

本目录只用于隔离研究，不写 `examples/byte_adder/candidate`，也不写正式存档。

## 结论

现有 `logic_layout.layout_turing_netlist` 的 `_route` 只生成直线或 L 形线，无法保证不穿过同层元件和无关引脚。字节加法器还需要把主线关卡的两个 U8 输入、一个 U1 进位输入、一个 U8 输出和一个 U1 进位输出，桥接到一位布尔网表。

`route_byte_adder.py` 原型补齐以下边界：

- 输入网表沿用 `LogicNetwork -> map_logic_network -> TuringNetlist`。
- 固定 bit 名称为 `A[0..7]`、`B[0..7]`、`Carry in`；输出为 `Output[0..7]`、`Carry out`。
- 保留 `scaffold/immutable.json` 的关卡 I/O，并添加 kind 17 拆分器、kind 16 合并器。
- 使用当前安装版本的精灵 alpha 单元和 `positioned_pins` 建立障碍。
- A* 使用 v15 支持的八方向网格；允许不同导线交叉，但禁止不同网络共用边，禁止经过元件或非端点引脚。
- 写出前检查 v15 往返、全部引脚连通、无多驱动/位宽错误/组合环、真实精灵几何及 131072 个输入向量。

## 可复用 API

```python
network = build_some_logic_network()
netlist = map_logic_network(network)
circuit = build_byte_adder_circuit(PROJECT_ROOT, netlist)
report = verify_byte_adder_circuit(circuit)
payload = encode_v15(circuit)
```

正式化时建议把通用的 `Connection`、`_route_all` 和精灵占用查询移入新的 `tc_save_lab.geometry_router`，把 byte-adder 的桥接层移入 `tc_save_lab.byte_adder_asic`。不要继续扩充 `builder.py` 中手写坐标的 recipe。

## 离线运行

在仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe .\.research\byte_adder_builder_layout_agent\route_byte_adder.py
```

脚本只会生成：

```text
.research/byte_adder_builder_layout_agent/ripple_reference.circuit.data
```

该 ripple 结构只是全链路正确性夹具，不代表排行榜优化结果。

2026-08-03 的实测结果：`79 gate / 18 delay`、87 个元件、170 条导线，
`131072/131072` 输入向量通过；v15 SHA-256 为
`cc2e4e7ae8b53e35bbaab16be69abf43603ca74369e4092b205fffb73ce83a66`。
完整 Python 仿真约 207 秒，观察到的工作集约 25 MiB。

正式存档路径经只读核对为：

```text
C:\Users\cong\AppData\Roaming\Turing Complete\schematics\byte_adder\Default\circuit.data
```

只有候选通过上面全部离线审计后，父任务才应按用户指令直接覆盖该文件。
