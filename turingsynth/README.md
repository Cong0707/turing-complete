# TuringSynth

TuringSynth 是一个以 Verilog/SystemVerilog 为输入、以当前 Turing Complete `v15` 电路为
输出的独立逻辑综合与物理实现工具链。它取代“为每张地图手写一份 Python 坐标生成器”的旧
工作流。Python 仍可用于生成 Verilog，但这类脚本必须放在仓库顶层的
`verilog-generators/`，不能绕过本编译器直接写地图。

## 设计原则

- **Yosys 是唯一 HDL 前端**：源代码先综合为可保存、可复查的标准单元 JSON。
- **阶段合同明确**：前端、IR、原生映射、布局、布线、v15 输出和审计各自位于独立子目录。
- **打包不改变分数**：Maker/Splitter 仅用于免费重组线路；不会补零凑宽，也不会隐藏门数或延迟。
- **地图供人阅读**：DAG 从左到右分层，相关位按稳定 affinity 排列，元件紧凑但保留间隔。
- **线路供人追踪**：优先短路、少折返、少交叉；禁止导线穿过元件、无关引脚或复用已有边。
- **CI 先于写入游戏**：Yosys 形式等价、真实成本/到达、物理网络、几何和 v15 往返全部通过后才产出。
- **不启动游戏、不修改存档**：编译器只生成 `build/05-output/circuit.data`。

## 目录

```text
compile.py                 稳定主入口，只负责驱动流水线
src/turingsynth/frontend/  Verilog -> Yosys JSON -> 规范化标量 IR
src/turingsynth/ir/        阶段间稳定数据结构
src/turingsynth/mapping/   游戏原生元件 ABI、成本和零成本向量打包
src/turingsynth/layout/    DAG 分层、紧凑放置、bit affinity 排序
src/turingsynth/routing/   fanout hub、A* 短路由、交叉/折返惩罚
src/turingsynth/formats/   独立 v15 模型、Snappy 编解码和电路写出
src/turingsynth/targets/   Foundry 自定义元件与主线关卡模板
src/turingsynth/audit/     形式等价、时序、连通性、几何和成本审计
src/turingsynth/render/    精确布局 SVG 人工预览
examples/                  人工编写的 Verilog 示例
tests/                     单元测试
build/                     唯一、一次性的当前构建目录
```

## 安装

Windows PowerShell：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
```

YoWASP Yosys 被固定到 `0.67.0.0.post1190`，无需本机另装 Linux、MSYS2 或原生 Yosys。

## 构建

```powershell
.\.venv\Scripts\python.exe .\compile.py .\examples\byte_adder\project.toml
```

也可以安装后使用：

```powershell
turingsynth .\examples\byte_adder\project.toml
```

编译器根目录下只能存在一个 `build/`。每次运行开始时直接删除并重建它，不创建同级临时目录、
日期目录、哈希目录或历史构建副本。失败时 `build/FAILED.txt` 说明中止阶段；下一次运行仍完整
覆盖 `build/`。

成功产物：

```text
build/report.json                 总证书
build/01-yosys/netlist.json       Yosys 原始网表
build/01-yosys/normalized.json    规范化逻辑 IR
build/02-mapping/physical.json    原生元件和逻辑网络
build/03-layout/placed.json       带坐标的物理 IR
build/04-routing/report.json      线长、折点、折返和交叉指标
build/05-output/circuit.data      可复制的 v15 地图或 Foundry 元件
build/05-output/circuit.json      无损 JSON 视图
build/05-output/layout.svg        人工检查图
build/06-audit/formal.json        Yosys 形式等价证书
build/06-audit/physical.json      成本、时序、网络和几何证书
```

## project.toml

Foundry 自定义元件：

```toml
[project]
name = "字节加法器"
top = "byte_adder"
sources = ["byte_adder.sv"]

[target]
kind = "foundry"
logical_key = "foundry/codex/verilog/byte_adder"
description = "Verilog 编译的字节加法器"

[compile]
pack_widths = [8, 4, 2]

[layout]
horizontal_clearance = 5
vertical_clearance = 3
```

`horizontal_clearance` 的有效最小值是 `5`。这恰好在相邻元件边界之间留下四列：前级输出
两格直线引出、共享转向/主干通道和后级输入短桩；继续压缩会封死连续 Splitter 输出的正交
出口。该间距只改变坐标，不增加门数或逻辑延迟。

`vertical_clearance` 的有效最小值是 `3`，在同列相邻元件之间保留两行正交绕行空间。

主线关卡地图使用只包含不可变脚手架的 v15 模板，并逐端口绑定：

```toml
[target]
kind = "level"
template = "scaffold.circuit.data"

[target.ports.A]
component_label = "A"
pin = "value"

[target.ports.Output]
component_label = "Output"
pin = "value"
```

`level` 模板当前必须没有既有导线且所有组件均为 immutable，防止编译器在未知旧电路上叠加
网络。输出仍只进入 `build/`，不会直接覆盖正式存档。

## 当前原生映射

| 操作 | 标量元件 | 字元件 | 成本/位 | 延迟 |
|---|---:|---:|---:|---:|
| NOT | kind 3 | kind 18 | 1 | 1 |
| AND | kind 4 | kind 20 | 1 | 1 |
| NAND | kind 6 | kind 21 | 1 | 1 |
| OR | kind 7 | kind 19 | 1 | 1 |
| NOR | kind 9 | kind 22 | 1 | 1 |
| XOR | kind 10 | kind 23 | 3 | 2 |

同一操作、同一逻辑到达层的门按 `8/4/2/1` 精确分组。例如 15 个 OR 会成为
`U8 + U4 + U2 + U1` 四组，不会用一个填充位把真实 15 门写成 16 门。输入恰好是同一连续总线时
直接接字门；只有离散标量才使用免费 Maker。字门输出通过免费 Splitter 恢复标量扇出。

## 当前边界

`0.1` 严格支持组合逻辑和 `1/2/4/8/32/64` 位顶层端口。寄存器、RAM、三态 Verilog、黑盒、
多时钟和 `x/z` 目前会显式失败，而不是用错误元件继续生成。后续处理器支持将在现有 IR 上新增：

1. 时序 IR 与时钟域合同；
2. kind 39 等寄存器 technology profile；
3. RAM/ROM 目标与初始化文件；
4. 处理器级层次布局、模块边界和可折叠总线；
5. 目标关卡的禁用元件清单与多套成本 profile。

这些扩展不会改变 `compile.py -> build/`、阶段目录和审计证书的外部合同。

## CI

```powershell
python -m unittest discover -s tests -v
python compile.py examples/byte_adder/project.toml
```

任何未知单元、成本不一致、时序不一致、组合环、多驱动、组件重叠、导线穿件、导线接触无关
引脚、导线边重叠、物理网络碎裂或 v15 往返变化都会使构建非零退出。
