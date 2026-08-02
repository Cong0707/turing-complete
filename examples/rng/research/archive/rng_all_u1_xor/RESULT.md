# RNG 全 U1 Word XOR 候选审计结果

> **已作废（2026-08-03）**：游戏实测已经确认 U1 Word XOR 是
> `3 gate / 2 delay`，不是本文采用的 `1 gate / 2 delay`。此外本候选依赖
> RAM 漏洞。`153/10/66` 不是真实合法成绩，本文只保留作历史追溯。

## 结论

当前 `191/10/66` 研究拓扑剩余的 19 个 `kind=10` Bit XOR 可以全部替换为
`kind=23, word_size=1` Word XOR。替换后的候选通过完整离线功能、结构、布局和
原生计分审计，可作为下一份实机验收候选：

```text
score               153 / 10 / 66
energy              100980
candidate SHA-256   D75DE7D8600BECAE4AB8D83FA704BFFC69AAF385759FFAC1A3D05F8CFC0BFE20
payload bytes       14728
components / wires  152 / 338
```

本研究没有启动游戏，也没有读取后再覆盖正式 `circuit.data`；所有新产物均位于
`.research/rng_all_u1_xor`。

## 变更边界

生成器以 SHA-256
`8B3FA9303BE44958651EA90653D045A468FB9DD18E678380136D4B724DCD778D`
的 `191/10` 候选拓扑为基础，并在运行时断言：

- 恰好 19 个组件发生变化；
- 每处变化严格为 `kind=10 -> kind=23, word_size=1`；
- permanent ID、位置、旋转、成本覆盖字段和其余序列化字段不变；
- 338 条导线逐对象完全不变。

两种组件在 U1 下都有相同的三针脚几何：`in0=(-1,-1)`、`in1=(-1,+1)`、
`out=(+2,0)`，针脚宽度均为一位。最终组件计数中 `kind=10` 为零，
`kind=23` 为 76，且全部 `word_size=1`。

## 功能与结构验证

生成器对全部 256 个 RNG test ID 各执行 66 ticks，总计 16,896 ticks。每个 seed
均通过 seed-load、内部 RAM 状态和随后 65 个输出的参考递推校验；第一个 seed 的
输出前缀保持：

```text
48669548 e3b830cf bc6e3466
```

其余检查结果：

```text
v15 decode/encode byte-identical       pass
unsupported component kinds            0
unconnected pins                       0
multi-driver / undriven / sinkless      0 / 0 / 0
width mismatches                        0
combinational-cycle components          0
conservative wire-component contacts    0
wire-interior pin contacts              0
component-footprint overlaps            0 (RAM group exception tracked separately)
live-sprite internal wire collisions    0
live-sprite unsupported kinds           0
```

Live sprite 审计仍记录架构 I/O 可达区域 7 处、RAM 可见端点 3 处，以及精灵 alpha
footprint 的 124 个重叠 cell；它们与 `191/10` 基线完全相同，分别属于端口接入和
RAM 组合件，不是导线穿件或非法端口接触。内部导线碰撞为零。

## 原生计分

只读审计从当前 `levels.txt` 取得 `xor_gate = 3/2/1`。原生 `add_cost` 从 Bit XOR
派生 Word XOR 基点 `24 gate / 2 delay`；`get_gate_cost` 对 `word_size=1` 返回
`1 gate`，delay 仍为 `2`。因此 19 处替换各省两门而不增加 delay：

```text
47 * OR Bit              @ 1 = 47
76 * U1 Word XOR         @ 1 = 76
 1 * Delay Bit           @ 5 =  5
 1 * NOT Bit             @ 1 =  1
RAM backing buffer=8         =  8
RAM Load calculated_gate=8   =  8
RAM Store calculated_gate=8  =  8
                              ---
                              153
```

原生 arrival 分析得到唯一的十分 terminal 为 RAM Store `component_index=136`。
关键路径后半段现在是：

```text
ready Delay 4 -> NOT 1 -> Architecture Input control/value shell 0
-> OR Bit 1 -> U1 Word XOR 2 -> U1 Word XOR 2 -> makers 0 -> RAM Store 0
= 10
```

因此序列化 header `153/10` 与原生重算值完全一致；能量为
`153 * 10 * 66 = 100980`。

## 产物与复验

```text
.research/rng_all_u1_xor/build_candidate.py
  50E1395798AEA450EB91858E6D883B5B4C9741B66DB64D41F2AED7C147764CEC
.research/rng_all_u1_xor/candidate/circuit.data
  D75DE7D8600BECAE4AB8D83FA704BFFC69AAF385759FFAC1A3D05F8CFC0BFE20
.research/rng_all_u1_xor/candidate/result.json
  7ED845D8712B133801B2F2B7D510D727BB0A07B07307DD49F127D76EA010F0BF
.research/rng_all_u1_xor/native_score_audit/audit.py
  FC8FF86F4D5A8357C8889596B1BDC2F67D1E74E907AB302F46931D9B305C5AA9
.research/rng_all_u1_xor/native_score_audit/evidence.json
  32B63201538EB77A08FB69E9BD077161F3B8A16346F8B5E3AAC21E3713FC9BA6
```

复验命令：

```powershell
.\.venv\Scripts\python.exe .research\rng_all_u1_xor\build_candidate.py
.\.venv\Scripts\python.exe `
  .research\rng_all_u1_xor\native_score_audit\audit.py `
  --output .research\rng_all_u1_xor\native_score_audit\evidence.json
```

全量构建期间观察到的本任务最高 Python 工作集约 381 MB，低于 1 GB 限制。
