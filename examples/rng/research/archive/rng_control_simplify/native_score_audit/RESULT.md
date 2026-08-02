# RNG 191/10/66 候选原生计分独立审计

> **已作废（2026-08-03）**：游戏实测已经确认普通 XOR 与 U1 Word XOR
> 都是 `3 gate / 2 delay`；U2/U3/U4/U8 则是 `6/9/12/24 gate / 2 delay`。
> 本文的 `191/10/66` 同时依赖错误的 U1 计费与 RAM 漏洞，只保留作历史证据，
> 不得作为合法候选、成本上界或后续搜索输入。

## 结论

最终生成器候选与其 `result.json` 已一致：

```text
candidate SHA-256  8B3FA9303BE44958651EA90653D045A468FB9DD18E678380136D4B724DCD778D
header              191 / 10
native score        191 / 10 / 66
energy              126060
components / wires  152 / 338
v15 round trip      byte-identical
```

`191` 门成立，最长原生 delay 精确为 `10`。本审计未启动游戏、未读取或
修改正式存档，只读取研究候选和当前 `levels.txt`。

注意：生成器 `result.json` 的 header、能量和 SHA 均正确，但其中两条局部
`delay_certificate` 文本仍把 U1 Word XOR 写成 `3 delay`，分别声称 B/C
局部路径为 `6/6`。这两条说明文字已过时；当前 native 成本是 `2 delay`，
正确的局部 B/C 路径分别是 `5/4`。该文本不编码进电路计分字段，不影响本
报告确认的 `191/10` 候选。

## Gate ledger

当前 `xor_gate` frontier 是 `3/2/1`。`add_cost(kind=10, (3,2))` 在
`0x14027AEFC` 调用 `stareq * 8`，然后在 `0x14027B008` 将派生点插入
`kind=23`。直接反汇编 `stareq @ 0x14027AD4B` 可见
`0x14027ADA2..0x14027ADD9` 只读取、乘八并写回第一个 qword；第二个
qword delay 不变。因此 Word XOR 基点是 `24/2`。

`get_gate_cost @ 0x14027612C..0x1402761D7` 对余数不超过三的宽度执行：

```text
gate = base_gate * (width div 8) + (width mod 8)
```

所以 `kind=23, word_size=1` 的成本是 `1 gate / 2 delay`，而不是 Bit XOR
的三门，也不是默认表里的三延迟。

```text
47 * kind 7  OR Bit       @ 1 gate = 47
19 * kind 10 XOR Bit      @ 3 gate = 57
57 * kind 23 U1 Word XOR  @ 1 gate = 57
 1 * kind 13 Delay Bit    @ 5 gate =  5
 1 * kind 3  NOT Bit      @ 1 gate =  1
 1 * kind 118 RAM buffer8 @ 8 gate =  8
 1 * kind 54 load         @ 8 gate =  8
 1 * kind 56 store        @ 8 gate =  8
                                      ---
                                      191
```

RAM 字段为 `settings=(2,512,0), buffer_size=8`。非零 mode 的 backing RAM
按 buffer 长度计八门，delay 为 `512 div (512+1) = 0`。RAM 关联阶段在
`preorder.c:2303` 将 backing buffer 长度复制到每个 port 的
`calculated_gate`，因此 U32 load/store 各是八门而不是 32 门；load delay
在 `preorder.c:2310-2315` 复制 RAM delay，store delay 保持
`preorder.c:1132` 的零值。

## Critical path

`preorder.c:4151-4190` 对一个组件的所有输入网取最大 arrival，
`preorder.c:4219-4224` 加该组件 delay，随后 `preorder.c:4230-4268` 将同一
arrival 写到该组件的所有输出网。它不会按 pin 名区分 control 和 value。
因此 `kind=62 Architecture Input` 的 control 到达时间会传播到 value 输出。

候选中唯一的十分 terminal 是 store `idx136`。一条精确关键路径是：

```text
idx2   Constant On                              +0 =  0
idx3   Delay Bit                                +4 =  4
idx4   NOT Bit                                  +1 =  5
idx0   Architecture Input control -> value      +0 =  5
idx5   Splitter Word 4                          +0 =  5
idx7   Splitter Bit 8                           +0 =  5
idx25  OR Bit                                   +1 =  6
idx67  U1 Word XOR                              +2 =  8
idx91  Bit XOR                                  +2 = 10
idx128 Maker Bit 8                              +0 = 10
idx132 Maker Word 4                             +0 = 10
idx136 RAM Store data                           +0 = 10
```

局部 B 数据路径仍是 `OR 1 + Word XOR 2 + Bit XOR 2 = 5`；完整路径前面还
有 `Delay 4 + NOT 1` 的 switched-input control 前缀，所以 header 必须是
`10`，不能写成 `5` 或 `6`。

## 复验

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_control_simplify\native_score_audit\audit.py `
  --output .research\rng_control_simplify\native_score_audit\evidence.json
```

证据文件：

```text
audit.py SHA-256
15B94AC7D57814090E589501AE489409C01B8EB6EEDB308E14A4FA86D2608717

evidence.json SHA-256
53864DBC76395CBF0356DF08B02322595E55764DB5EBFE81BF0BDD799B3E9B58

Turing Complete.exe SHA-256
C93F5E8E826050C3F92E2B3891D26FCDFC933658614185CB9B2EB6A34C5B8D1C
```

关键原生材料：

```text
.research/rng_score_bypass/ida/score_network/add_cost.c
.research/rng_score_bypass/ida/ram/score_gate_core.c
.research/rng_score_bypass/ida/ram/score_gate_component.c
.research/rng_score_bypass/ida/ram/score_delay_core.c
.research/rng_score_bypass/ida/ram/score_delay_component.c
.research/rng_score_bypass/ida/ram/preorder.c
.research/rng_primitive_zero_audit/ram_tick_semantics/native_score_check/set_critical_path.c
.research/rng_primitive_zero_audit/ram_tick_semantics/native_score_check/is_critical.c
```
