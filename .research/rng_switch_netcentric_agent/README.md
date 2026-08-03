# RNG 无向物理网联合综合研究

本目录只包含离线研究脚本与证书，不启动游戏、不读取或写入正式存档。2026-08-03 用户验收 `402/9/67` 后，主任务已转向 Byte Adder；本目录的 RNG 搜索因此冻结在下述检查点。

`SHA256SUMS.txt` 是冻结时全部 `.py`、`.json` 和本 README 的按文件名排序哈希清单；运行缓存 `__pycache__` 不属于提交内容。

## 物理模型

旧的 directed-BUS 表达允许同一输出端子进入两个不同 BUS，例如：

```text
BUS(a, b)
BUS(a, c)
```

真实导线会把它们合并为同一个无向网 `{a,b,c}`。`netcentric.py` 与本目录的新求解器都按以下规则处理：

- 每个元件输出端子只属于一个物理网；
- 同网的所有驱动在任何有效行都不得同时驱动不同的 0/1；
- Switch 的关闭输出为 Z，BUS 解析同时跟踪值、驱动掩码和冲突；
- 一个网被组合门读取后，当前或未来门不能再向该网增加驱动，以排除隐藏的组合环；
- SAT 证书必须再经过独立物理网重放，不能把 directed-BUS SAT 直接当作可布线电路。

`alias_counterexample.json` 记录了旧模型的最小反例，`test_netcentric.py` 的 3 项测试覆盖端子别名、冲突与真实 12 门双输出 Switch 宏。

## 已确认结论

### 基础下界

- 原始输入 XOR2 最小为 `3 gate / 2 delay`。
- 免费正反双轨下，`delay <= 1` 的 XOR2 最小为 4 门。
- 三输入 parity 在 reviewed library 中 5 门 UNSAT，6 门两级 XOR 可行。
- 三个两两 XOR 最小为 `9 gate / 2 delay`。
- 两个不相交 dual pair 在 `delay <= 2` 下 7 门 UNSAT、8 门 SAT。
- 旧联合 V 宏 11 门 UNSAT，12 门真实物理网 SAT。

### V 锥闭合边界

- `components <= 6`：更宽松的 directed-BUS/all-dual 模型已经 UNSAT。
- `components = 7`：满足 `7 + 2*xors + switches <= 14` 的组成已经分区闭合为 UNSAT。
- `components = 8`：**只闭合了 `xors = 0` 子空间**，不能写成“c8 全闭合”。
- 通过等成本、等延迟恒等式 `XOR(a,b) = NOR(AND(a,b), NOR(a,b))` 映射出的 c10/c12/c14 分区仍有 `unknown`；目前只有 `c10/s4/output-driver=(1,4)` 为 UNSAT。

### 15 门普通门上界

`ordinary-v-c15-fixed-witness.json` 是五个三门 XOR 组成的 15 门、深度 4 上界。`verify_ordinary_v.py` 完全不导入 CNF 编码器，逐一重放 64 组输入并独立计算目标、门数和最长路径；`ordinary-v-c15-fixed-witness.verify.json` 的结果是：

```text
valid = true
gate_count = 15
output_depths = [4, 4]
row_mismatches = []
unused_gate_sources = []
```

无引导的 14 门普通门搜索仍为 `unknown`，不能据此宣称 14 门 UNSAT。

### 固定 402 的 zero-lane 相位修复

固定 61-XOR 外壳中，允许没有 direct 用途的 Word Switch lane 在稳态接常量 0 后，精确成本仍为：

```text
29 gate correction: UNSAT
30 gate correction: SAT
total: 443/9/66
```

单个 late correction cell 在所有可达 load/steady 行上的最小值是 2 门：

```text
pulse  = AND(lane, not_ready)
result = OR(pulse, base)
```

该 `443/9/66` 已被用户验收的 `402/9/67` 完全支配，只保留为下界证据，不应继续物化。

## 固定 402 mode 宏的冻结检查点

`search_mode_macro_joint.py` 使用真实可达输入域：

- load：状态寄存器输出全 0，所选 Seed 端子有效；
- steady：Seed 端子为 Z，所选状态位任意且有效。

共享 steady-only `q5` 的两个 one-mode 宏 `00000021` 与 `00000420` 具有统一目标形状：加载期分别输出独立 Seed 位，稳态输出两个共享一个状态位的 XOR。当前结果如下：

| 分区 | 结果 | 说明 |
| --- | --- | --- |
| 4 槽、成本 `<=7` | UNSAT | 精确无向物理网 Z3 |
| 5 槽、成本 `<=7` | UNSAT | 精确无向物理网 Z3 |
| 6 槽、成本 `<=7` | UNSAT | 精确无向物理网 Z3 |
| 7 槽、成本 `<=7` | UNSAT | 成本约束强制全为普通门；专用单驱动 CNF 在 0.54 秒闭合 |
| 3 槽、成本 `<=7` | 未闭合 | 宽搜被主动终止，尚未完成按 XOR/Switch 数量分区 |
| 4 槽、成本 `<=8` | SAT | 当前两个 `OR+XOR` 宏的 8 门、深度 3 基准 |

8 门基准已经由 `verify_synthesis.py` 独立重放：16 个填充场景全部匹配，两个输出均全驱动，物理深度 3，无冲突、无未来依赖错误。

另三组共享 steady-only 位的 4+4 宏对与上述目标在变量重命名下同构：

```text
00000084 / 00001080  (q7)
00002100 / 00000108  (q8)
00000210 / 00004200  (q9)
```

因此已经闭合的 4 至 7 槽结论可按重命名转移；3 槽缺口仍然存在。本检查点没有找到小于 8 门的可生成物理网，也没有修改 402 电路。

## 复现

在项目根目录和现有 venv 中运行：

```powershell
.\.venv\Scripts\python.exe .research\rng_switch_netcentric_agent\verify_ordinary_v.py `
  .research\rng_switch_netcentric_agent\ordinary-v-c15-fixed-witness.json `
  --output .research\rng_switch_netcentric_agent\ordinary-v-c15-fixed-witness.verify.json

.\.venv\Scripts\python.exe .research\rng_switch_netcentric_agent\verify_synthesis.py `
  .research\rng_switch_netcentric_agent\mode-pair-q5-baseline8.json `
  --output .research\rng_switch_netcentric_agent\mode-pair-q5-baseline8.verify.json

.\.venv\Scripts\python.exe .research\rng_switch_netcentric_agent\search_mode_macro_ordinary_cnf.py `
  --nodes 00000021,00000420 --slots 7 --max-delay 3 `
  --output .research\rng_switch_netcentric_agent\mode-pair-q5-bound7-s7-ordinary-cnf.json
```

继续研究时应先闭合 3 槽的 8 种 `XOR/Switch/普通门` 成本组成，再决定是否扩大宏边界；不要恢复 directed-BUS 放宽，也不要把任何 `unknown` 写成 UNSAT。
