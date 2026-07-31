# Foundry 自定义元件格式

## 2026-08-01 / 提交：核验 v15 Foundry 接口与自定义容器字段

### 研究范围

本记录只读检查当前 v15 存档中的 `schematics/foundry`，没有启动游戏，也没有向正式存档写入
任何文件。样本根目录为：

```text
C:\Users\cong\AppData\Roaming\Turing Complete\schematics\foundry
```

检查对象包括 `diode`、`LEG`、`OVERTRUE`、`Overture` 和 `RISCV` 下的当前
`circuit.data`；同目录的 `circuit_backup_*.data` 仅作为用户备份，不参与结论。其中
`OVERTRUE`、`LEG` 和完整 `Overture` 已确认被当前版本破坏，只用于解释历史二进制字段，
不得作为现代电路实现、依赖关系或性能数据的来源。

### v15 头部字段

当前项目的 `src/tc_save_lab/codec.py` 已按实际 v15 顺序解析：

1. `custom_id: i64`
2. `hub_id: u32`
3. `gate: i64`
4. `delay: i64`
5. `menu_visible: bool`
6. `clock_speed: u64`
7. `dependencies: u16` 个 `i64`
8. `description: string`
9. `sync_state: u8`
10. `score: u16`
11. `player_data: bytes_u16`
12. `hub_description: string`
13. 当 `custom_id != 0` 时，紧跟固定 512 字节 `design`
14. 组件数量、组件记录、导线数量、导线记录

当前 45 个正式 Custom 电路均满足：

```text
custom_id != 0
len(design) == 512
design == 512 个 0x00 字节
hub_id == 0
description == ""
hub_description == ""
sync_state == 0
score == 0
player_data == b""
```

`clock_speed` 不是固定格式常量：绝大多数样本为 `100000`，但存在 `100000000` 和 `10000`
的合法样本。因此生成器应允许调用者显式指定，不能把它作为接口识别条件。`design` 在当前
样本中没有观察到非零语义；为了保持兼容，生成器应始终写入精确 512 字节，默认使用
`bytes(512)`，不要省略字段或写入可变长度数据。

### Foundry 输入和输出接口

当前 v15 自定义电路的接口组件不是 `kind=78`。`kind=78` 是电路内部引用另一个 Custom
电路的实例；Foundry 对外端口为：

```text
kind=79  Foundry 外部输入端（在内部网络中是驱动源）
kind=81  Foundry 外部输出端（在内部网络中是接收端）
```

对 RISCV、diode、Overture 等现代 v15 Foundry 电路的实际导线端点统计，并与
`.research/tc_circuit/tc_circuit/component_info.json` 的 `Input64` / `Output64` 定义交叉核对，
得到以下现代接口族的稳定局部坐标：

```text
kind=79: PinSpec("in", output, ( 3, 0), width=component.word_size)
kind=81: PinSpec("out", input,  (-3, 0), width=component.word_size)
```

旋转沿 `src/tc_save_lab/pins.py::rotate_offset` 的四向变换：

```text
rotation 0: kind79 ( 3, 0), kind81 (-3, 0)
rotation 1: kind79 ( 0, 3), kind81 ( 0,-3)
rotation 2: kind79 (-3, 0), kind81 ( 3, 0)
rotation 3: kind79 ( 0,-3), kind81 ( 0, 3)
```

这里的 `word_size` 决定端口总线宽度，而不改变现代接口的三格端口距离。证据覆盖单比特、
8、16、32 和 64 位接口，也覆盖四种旋转；例如 `RISCV/ALU/BALU` 的 rot1 输入、
`RISCV/MMIO` 的 rot2 输入和 `RISCV/ALU/RIALU` 的 rot1 输出都与上表一致。组件的
`settings` 常见为输入 `(2,)`、输出 `(0,)`，但 Overture 旧样本也出现空元组；它是 UI/端口
元数据，不应单独替代几何端口规则。

### 历史接口形状边界

这里的 `input` / `output` 是相对于**当前 Foundry 电路内部网络**的方向：kind79 将外部输入
值驱动到内部，所以是 `output`；kind81 接收内部信号并交给外部，所以是 `input`。

`kind=79/81` 不是一个跨版本固定形状。正式 foundry 中仍保留的旧目录存在一格端口：

```text
OVERTRUE/ALU、OVERTRUE/COND、OVERTRUE/RegisterPlus：
  kind79 输入常见本地 (+1,0)，kind81 输出常见本地 (-1,0)
LEG/SWT：
  settings=(2,) 的 kind79 采用一格；另一个 settings=(3,) 输入采用三格
```

这说明端口距离属于自定义电路的接口/本体设计，而不是可以由 `kind`、`word_size` 或
`settings` 单独推断的全局常量。当前 `pins.py` 的 kind79/81 映射针对 **新建 Codex 元件的
现代三格模板**；分析旧 `OVERTRUE`/`LEG` 文件时，只能在只读检查中显式提供其历史接口形状，
不能把这些接口复制到新元件，也不能把默认三格结论反推到旧文件。父电路引用 kind78 时，
子电路的接口形状必须与当前已验证接口一致，否则导线虽能通过二进制编解码，游戏加载时仍
可能出现端口错位。

### Custom 实例、ID 与依赖

自定义电路的组件引用记录如下：

```text
kind=78
component.custom_id = 被引用 Foundry 电路的 circuit.custom_id
component.custom_word_sizes = 可选的内部永久 ID/字宽映射
```

父电路头部的 `dependencies` 是直接 kind78 实例引用的 **有序去重列表**：按组件在文件中的
出现顺序记录每个子 `custom_id` 的第一次出现，重复实例不重复写入。它不是排序列表；例如
`RISCV/Controller/MemoryController` 的依赖顺序与其组件扫描顺序相同，而
`RISCV/Controller/JIController` 的依赖顺序也没有按数值排序。

写入前应执行以下不变量检查：

- `custom_id` 在整个 `schematics/foundry` 命名空间内非零且唯一；
- `dependencies` 与直接 kind78 实例 ID 的有序去重结果完全一致；
- 每个 dependency 都能在 foundry 中解析到一个 `circuit.data`；
- 依赖图无环；
- 父电路递归门数等于头部 `gate`（若使用递归成本模型）；
- 自定义电路的 `design` 恰为 512 字节。

### 可复用的构建约定

建议 builder 将 Foundry 电路分成三层：

1. **接口层**：用 kind79/81 创建端口，位置和 rotation 由布局器决定，`word_size` 显式传入；
   Codex 新元件使用当前验证过的现代三格模板。旧架构接口只读，不提供直接迁移路径。
2. **逻辑层**：用普通元件和 kind78 Custom 实例构建网络；kind78 的 `custom_id` 必须引用
   已生成或已导入的子电路。
3. **容器层**：设置非零确定性 `custom_id`、`dependencies`、`gate`、`delay`、
   `clock_speed` 和 `design=bytes(512)`，然后调用 `encode_v15` 做往返校验。

`custom_id` 可以使用项目已有的 SHA-256 截断策略生成正的 63 位整数，但必须在写入目标
foundry 前检查碰撞；组件 `permanent_id` 与电路 `custom_id` 使用不同命名空间，不能混用。
正式输出目录应为：

```text
schematics/foundry/codex/<中文元件名>/circuit.data
```

生成器只应写入项目镜像或用户显式指定的目标；正式存档写回前仍需确认游戏进程未运行，并在
反解析后比较 `Circuit` 语义模型。研究阶段的 `gate`、`delay` 只是候选声明值，最终榜单成绩
必须由游戏重新计分。

### 可复现检查

以下只读脚本可复核本文统计（在项目根目录执行）：

```powershell
$env:PYTHONPATH = "src"
@'
from pathlib import Path
from tc_save_lab.codec import decode_v15

root = Path(r"C:\Users\cong\AppData\Roaming\Turing Complete\schematics\foundry")
files = sorted(root.rglob("circuit.data"))
circuits = [decode_v15(path.read_bytes()) for path in files]
custom = [c for c in circuits if c.custom_id]
assert len(custom) == 45
assert all(len(c.design) == 512 and c.design == bytes(512) for c in custom)
assert sum(x.kind == 79 for c in custom for x in c.components) == 125
assert sum(x.kind == 81 for c in custom for x in c.components) == 124
print("Foundry v15 samples: 45 circuits; design=512 zero bytes; kind79=125; kind81=124")
'@ | .venv\Scripts\python -
```

该检查只读取当前存档并在内存中断言，不会启动游戏，也不会改写任何文件。
