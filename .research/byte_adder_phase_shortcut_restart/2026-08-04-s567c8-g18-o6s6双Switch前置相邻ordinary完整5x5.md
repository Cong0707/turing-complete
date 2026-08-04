# `S5/S6/S7/C8 g18/o6/s6` 双 Switch 前置相邻 ordinary 完整 5x5

## 结论

本轮在冻结的 `fixed 73 + high residual 29`、D5 paid-source 接口上，完整封闭了：

```text
slot:  0    1    2   3   4       5       6   7   8       9       10      11
kind:  NOT, NOR, OR, OR, SWITCH, SWITCH, K1, K2, SWITCH, SWITCH, SWITCH, SWITCH

K1,K2 in {NOT,AND,OR,NAND,NOR}
```

精确模型：

```text
domain       = s34567c8_leaf
rows         = 486
outputs      = S5,S6,S7,C8
gate bound   = 18
max delay    = 5
components   = 12
ordinary     = 6
Switch       = 6
XOR          = 0
```

最终 authoritative physical SAT 结果：

```text
25/25 strict UNSAT
SAT       = 0
UNKNOWN   = 0
timeout   = 0
missing   = 0
invalid   = 0
overlap   = 0
```

完整矩阵如下；行是 `K1`，列是 `K2`：

| `K1 \ K2` | `NOT` | `AND` | `OR` | `NAND` | `NOR` |
|---|---:|---:|---:|---:|---:|
| `NOT`  | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| `AND`  | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| `OR`   | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| `NAND` | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| `NOR`  | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |

因此这 25 个互斥 fixed-kind 片的并集，严格证明上述精确槽序类 UNSAT。

## 为什么该拓扑有新增能力

上一轮已封闭的 terminal-Switch 类为：

```text
NOT,NOR,OR,OR,K1,K2,SWITCH x6
```

其中 `K1/K2` 位于全部 Switch 之前，不能读取 synthesized resolved Switch BUS。本轮把
两只 Switch 移到 `K1/K2` 之前：

- slot6 的输入选择范围包含 slot4/slot5；
- slot7 的输入选择范围包含 slot4/slot5，并额外包含 slot6；
- ordinary 输入 BUS 可以同时选择两只前置 Switch driver；
- 相同 Switch driver 集可以扇出到多个输入，表示同一物理 BUS；
- 不同 BUS 对 component driver 的 partial overlap 仍由 physical-net partition 禁止；
- 后四只 Switch 可以读取 `K1/K2` 的结果。

因此本轮不是上一 terminal-Switch 类的重跑。它允许 ordinary 位于 resolved BUS 之后，
但没有强制某个见证必须实际合并 slot4/slot5。

## 5x5 完备性

每个拓扑 slot 都有 exactly-one kind。六个固定 Switch 槽为 `4,5,8,9,10,11`，
`exact_switches=6` 已占满 Switch quota；`exact_xors=0`。所以 slot6/slot7 在该模型中
只能取五种 ordinary kind：

```text
NOT, AND, OR, NAND, NOR
```

matrix 显式枚举它们的全部 `5x5=25` 个有序对。25 个 fixed-kind 字符串、job 名、
输出文件名和 constraint SHA 全部唯一，约束集合指纹为：

```text
constraint_set_sha256 = ce2d34a25f82342a3814f710e5ef01626bc6785e955a56995dee3b91aa2c3ae0
```

成本恒等式为：

```text
6 ordinary * 1 + 6 Switch * 2 = 18 gates
```

`split_slots=1/shard_count=1/shard_index=0` 只涉及最后一个已固定为 Switch 的槽，分配
完整 suffix universe，不限制 `K1/K2`，也不遗漏任何 ordered pair。

## 无求解正回归

发射前以冻结的 `S7/C8=16 gates @ D5` SAT witness 为来源，在前两只 Switch 后插入
两个 `OR(x,0)` identity，并把后续两个 Switch 输入改接到 identity 输出，得到精确新槽序：

```text
NOT,NOR,OR,OR,SWITCH,SWITCH,OR,OR,SWITCH,SWITCH,SWITCH,SWITCH
```

独立 Python replay 不调用 SAT solver，在全部 486 行上验证：

```text
status                            = verified-positive-regression
actual_gate                       = 18
actual_output_arrivals            = [5,5]
actual_max_delay                  = 5
mismatch_count                    = 0
bus_conflict_count                = 0
undriven_output_count             = 0
physical_net_partition_violation  = 0
active_bus_non_switch_violation   = 0
topology/order/dead/timing errors = 0
```

该正回归只覆盖 `S7/C8`，用于校准新 component order、成本、D5、Z/BUS、physical
partition 和 dead-component 语义；它不是四输出 SAT witness，也不是竞榜候选。

## 非重复性

发射前 preflight 扫描本地相关 JSON：

```text
scanned JSON files       = 68
scanned family files     = 46
Han family files         = 33
old terminal overlap     = 0
all prior-family overlap = 0
Han-family overlap       = 0
```

结构上，本轮是 `components=12/o6/s6`，且 ordinary 槽为 `6,7`；上一轮同分解的
ordinary 槽为 `4,5`，两族 fixed-kind 集为空交。Han 与 root 的 position sweep 是
`components=10/o2/s8`，分解和槽数均不同，也不与本轮 25 片重合。

preflight 最终状态：

```text
status = ready-for-ubuntu-matrix
errors = []
```

无结果基线审计则正确拒绝为：

```text
status       = incomplete
missing_jobs = 25
exit code    = 1
```

这证明缺失结果不会被误记为 UNSAT。

## Ubuntu 运行

唯一发射使用一个 worker：

```text
host                     = new.xem8k5.top
repository               = /root/congProjects/turing-complete-works
wrapper PID at launch    = 38342
first worker PID         = 38344
workers                  = 1
AS limit                 = 1536 MiB
nice                     = 5
CPU allowed              = 0-31
outer timeout per job    = 900 s
stop_on_first_sat        = true
```

启动前远端 `MemAvailable` 约 `16.4 GiB`，并复核 worker 和三项依赖 SHA 与 spec
一致。该 worker 与 Han 的单 worker 共存，没有修改或终止 Han 的进程。

`OR,OR` 被置于队首以优先检查正回归对应 kind pair；它在 `83.375 s` 后 UNSAT。
最终 runner 自然完成并退出：

```text
finished  = true
completed = 25
reused    = 0
SAT       = 0
UNSAT     = 25
timeout   = 0
```

25 个 payload 的 `solve_seconds`：

```text
minimum = 34.604754567029886 s
maximum = 207.33021329698386 s
sum     = 2477.015154790948 s
```

runner 外层 `elapsed_seconds`：

```text
minimum = 34.76919621397974 s
maximum = 207.5025752900401 s
sum     = 2481.7634653111454 s
```

每片均为 `233910 variables / 1735683 clauses`。stderr 为空；完成后 wrapper/worker
均自然退出。

## 严格终态审计

远端 auditor 在结果原生路径上返回：

```text
status                       = unsat-covered
manifest_complete            = true
proof_scope_match            = true
worker_sha_match             = true
auditor_sha_match            = true
dependency_sha_match         = true
positive_regression_match    = true
pairs_seen                   = 25
overlap/missing/invalid      = 0/0/0
unknown_jobs                 = 0
summary.integrity            = true
summary.complete_unsat       = true
summary.errors               = []
```

下载 25 份 payload 和 summary 后，本地重新运行同一 auditor，也独立得到
`unsat-covered`。另一个独立 crosschecker 执行：

```text
basename(summary.output) -> local manifest result directory
```

然后逐项比较 manifest value、Linux basename、terminal state、summary/payload
status、fixed topology、summary output SHA、本地磁盘 SHA、spec SHA 和 worker SHA；
并验证目录恰好只有 25 个预期 JSON。结果：

```text
status          = verified
jobs_seen       = 25
pairs_seen      = 25
file_count      = 25
completed       = 25
reused          = 0
mismatch_count  = 0
errors          = []
all_unsat       = true
no_timeout      = true
directory_exact = true
```

## 对 102/5/510 路径的含义

若本类存在 `S5/S6/S7/C8=18@D5` SAT witness，则可与冻结的 `S3/S4=11@D5`
组成 high residual 29，再接 fixed 73，得到：

```text
102 gates / 5 delay / 510 energy
```

但本类 25/25 UNSAT，所以没有生成或 graft `102/5/510` 完整候选。这个局部下界
只排除当前精确 Switch 相位族，不排除其它 g18 拓扑获得 `102/5/510`，也不排除其它
D5/D6 结构得到任何 `<560` 候选。

## 严格范围

本结论只封闭：

```text
[NOT,NOR,OR,OR,SWITCH,SWITCH,K1,K2,SWITCH,SWITCH,SWITCH,SWITCH]
K1,K2 in {NOT,AND,OR,NAND,NOR}
```

它不覆盖：

1. 其它 ordinary/Switch 槽位相位；
2. 前四 ordinary 的其它顺序或 multiset；
3. 含 XOR 或其它 gate/component 分解；
4. paid-source shell 与 residual 接口联合重写；
5. 全部 `S5/S6/S7/C8 g18` 或 high residual 29 拓扑；
6. D6 下的其它成本/能耗组合。

所以正确表述是“双 Switch 前置、相邻双 ordinary、四 terminal-Switch 的完整 5x5 类
UNSAT”，不是“g18 全局 UNSAT”。timeout、缺失 JSON、null/nonterminal status、SHA
漂移或 summary 不一致在 auditor 中始终归类为 UNKNOWN/incomplete。

## 证据与核心 SHA-256

```text
worker             = c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071
generator          = 981896c214954d53e8fbbcdb6e8db052eced442c5cd2308a9d580f63fc1a4fd2
auditor            = a937599876fb29738cf743e85ad79b02ac2a961d4b800e08960140677ad65633
preflight script   = ad39a367ec3f8502952f377f9732789f7c61afcfc76888a6ed106af3167af2ac
crosschecker       = f76c5ac30d5cd6ebc57664e28b9e92a3918dca934f0c26582144678956ab835e
positive script    = 9ef2736a2736e74495d0ca0fe50c8a4a9b013cdc161c82209220d0b89ff7f5d3
positive artifact  = f2dc25a6c90c0e8b8c4b3e83bbff0f328fcad6a3162d2e59a74f9d627721a7bf
spec               = 4d66477cb41f2e4d49bd77b99e93e7fa394f520f60a182b9a31386a244a4ed7c
preflight          = 2fc379a3cc552b76834ba4ccccde901a9177b8e079d776117d07261553d1cd3e
preflight audit    = 4974097c2ef6989cdbf55796060030d88e418f632d761749bc33993530f32e80
remote final audit = c6d0bcb7e23866ca24ca59d8fdb5540141e3781ac6e929291cba1ef4be495594
local final audit  = 8c31b4a0d8fbb152b9811b82d311f2cbcd3c9b8bef6e86ffe85f9fe5c16d833e
crosscheck result  = 4b7fa0d800a4bf35894995e95f4bbea10d11ba2379268c9514ffc2d6eee9b4d5
runner summary     = b3443a9cb25b6b20ac66a3d211b83219cd58ff50febd33d28e4376920cc631f3
```

全部 25 份 payload 的逐文件 SHA 收录于本族专用 `SHA256SUMS` manifest。

本轮没有启动游戏，没有读取或写入正式/candidate 存档，没有修改
`physical_exact.py`，没有改共享 history，也没有执行 Git stage/commit/push。
