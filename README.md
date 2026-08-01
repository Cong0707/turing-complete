# 图灵完备存档实验室

`tc-save-lab` 是一个面向 Turing Complete 2.1.x 的离线存档与电路研究工具。
它可以在不启动游戏的情况下解析、校验、版本管理和原子写入当前格式的电路文件。

`examples/` 是所有主线关卡重制方案的可复现工作区。每个关卡都有独立目录，包含元数据、
原始基线、候选电路和按关卡中文名记录的修改历史。工具研究位于 `docs/组件研究/`，
每个 Markdown 只描述一个工具组件，并在文件内部按日期和提交主题分节。README 只保留
稳定的使用说明。

## 当前能力

- 严格读写 v15 电路容器，并在编码后执行完整往返校验。
- 只读解析 v7、v13 和 v14 旧版关卡电路。
- 为 92 个主线关卡建立独立示例目录并提取不可变端口脚手架。
- 分析导线、端点网络、引脚连接、组合环和单位逻辑深度。
- 使用确定性永久 ID 生成候选电路。
- 对已审查的组合元件执行离线真值表穷举，支持多个独立输入并复用已编译网络。
- 对 foundry 自定义元件执行只读递归门数与依赖完整性分析，不猜测延迟。
- 使用稳定注册 ID 构建现代三格接口的 Codex 自定义元件，并校验有序依赖与依赖环。
- 游戏运行时拒绝写回；正式写回使用同目录原子替换并再次反解析核对。

## 环境准备

```powershell
cd D:\Develop\Other\turing-complete
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
```

运行测试：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

直接运行 `tc-save` 会进入中文交互界面：

```powershell
.\.venv\Scripts\tc-save.exe
```

也可以使用子命令：

```powershell
.\.venv\Scripts\tc-save.exe inspect
.\.venv\Scripts\tc-save.exe analyze-examples
.\.venv\Scripts\tc-save.exe build-known-candidates
.\.venv\Scripts\tc-save.exe analyze-costs
```

预览或直接写入已经通过语义、v15、连通性和当前精灵几何审查的候选：

```powershell
.\.venv\Scripts\tc-save.exe install-reviewed --dry-run
.\.venv\Scripts\tc-save.exe install-reviewed --yes
```

`--dry-run` 只生成写入计划。去掉它后会直接覆盖当前所选槽位，不创建备份或临时副本；
未进入精确摘要白名单的研究候选不会被批量写入。

`tc-foundry` 提供独立的中文交互界面。候选只生成到项目镜像；`deploy --dry-run` 只读检查，
不加 `--dry-run` 并确认后才会部署：

```powershell
.\.venv\Scripts\tc-foundry.exe
.\.venv\Scripts\tc-foundry.exe build not_gate 非门 .research\not_gate.json
.\.venv\Scripts\tc-foundry.exe deploy --dry-run
```

## 存档安全边界

默认正式存档目录为 `%APPDATA%\Turing Complete`。分析、生成和测试只操作本项目中的
`examples/`，不会启动游戏，也不会自动覆盖正式存档。

只有显式执行 `apply`、`apply-direct`、`install-reviewed`，或执行 `tc-foundry deploy` 并确认后，
才会写回候选。写回前工具会检查 `Turing Complete.exe` 未运行，候选必须是可严格解析的
v15 文件。`apply-direct` 与 `install-reviewed` 直接覆盖最终文件，不保留备份副本，符合当前
项目约定。

候选文件中的 `gate` 和 `delay` 是研究阶段的声明值，不等于游戏已经验证的排行榜成绩。
最终成绩、元件可用性和关卡通过状态必须由用户在游戏中验收。

## 现代版本边界

`OVERTRUE`、`LEG` 和完整 `Overture` 架构已经被当前游戏更新破坏，不是本项目的候选基线、
依赖库或性能参考。项目只把相关旧文件作为只读格式与存档来源证据；不得从中复制电路实现、
接口形状、依赖关系或头部成绩来生成现代候选。

所有新自定义元件只面向当前 `2.1.281/v15`，统一生成到 `foundry/codex`，并经过当前格式的
离线结构校验和真值表验证。名称为 `overture_*` 的最新版主线关卡仍可独立重制；关卡名称不
表示可以复用旧 Overture CPU 架构。少数仍能运行的 Overture 元件也必须逐个重新验证，验证
通过前不得作为 Codex 元件依赖。

对架构类、程序类和最终关卡，默认优化路线是直接实现关卡判定所需的 ASIC：组合网络、专用
数据通路、ROM、计数器或有限状态机。除非关卡规则明确强制执行 ISA 程序，否则不投入时间
修复或优化通用处理器；即使必须执行指令，也只构造覆盖测试需求的最小专用机器。

## 目录结构

```text
docs/组件研究/             每个工具组件一个中文名研究文件
examples/<关卡>/baseline/  从当前存档提取的只读研究基线
examples/<关卡>/scaffold/  游戏固定端口与不可变元件
examples/<关卡>/candidate/ 待验收的重制候选
examples/<关卡>/history/   该关卡每次方案修改的中文记录
examples/foundry/codex/    Codex 自定义元件候选与稳定 ID 注册表
src/tc_save_lab/           Python 工具源码
tests/                     离线自动化测试
```

## 当前状态

项目仍处于持续优化阶段。已经生成并穷举验证三批基础组合逻辑候选，但尚未完成全部主线
关卡、真实加权延迟模型、架构程序周期优化和最终正式存档写回。每项结论与限制以
对应组件或关卡的中文 Markdown 记录为准。
