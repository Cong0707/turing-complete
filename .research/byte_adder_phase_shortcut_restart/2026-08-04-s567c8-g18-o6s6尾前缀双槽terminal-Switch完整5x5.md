# `S5/S6/S7/C8 g18/o6/s6` 尾前缀双槽 terminal-Switch 完整 5x5

## 结论

本次在冻结的 `s34567c8_leaf` residual 上，封闭了以下 ordinary-front、
terminal-Switch 精确拓扑类：

```text
NOT,NOR,OR,OR,K1,K2,SWITCH,SWITCH,SWITCH,SWITCH,SWITCH,SWITCH

K1,K2 in {NOT,AND,OR,NAND,NOR}
```

`K1/K2` 是有序槽位，因此 5 种 ordinary kind 的笛卡尔积给出 25 个互斥且完备的
fixed-kind 子问题。authoritative physical SAT 模型为：

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

最终结果：

```text
25/25 strict UNSAT
SAT       = 0
UNKNOWN   = 0
missing   = 0
invalid   = 0
overlap   = 0
```

完整 5x5 状态矩阵如下；行是 `K1`，列是 `K2`：

| `K1 \ K2` | `NOT` | `AND` | `OR` | `NAND` | `NOR` |
|---|---:|---:|---:|---:|---:|
| `NOT`  | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| `AND`  | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| `OR`   | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| `NAND` | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| `NOR`  | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |

所以这 25 个 fixed-kind 片的并集严格证明了上述精确拓扑类 UNSAT。

## Wildcard 先导不是证明

同一类曾先以单个 wildcard 约束运行：

```text
NOT,NOR,OR,OR,*,*,SWITCH,SWITCH,SWITCH,SWITCH,SWITCH,SWITCH
```

该次外层运行在约 800 秒后结束，记录为：

```text
state           = timeout
elapsed_seconds = 800.2337316000012
status          = null
output_sha256   = null
result JSON     = missing
```

因此它只能归类为 **UNKNOWN**，不能记作 UNSAT，也不参与本报告的 UNSAT 证明。
对应专用审计正确给出：

```text
status       = incomplete
missing_jobs = 1
```

本报告的完整下界仅来自后续 25 个 fixed-kind 子问题的互斥完备分割。

## 完整性审计

matrix 的约束集合与 worker 指纹为：

```text
constraint_set_sha256 = fd65030d671011c42e3f9f0cee64ddf25332b1ea4822349e6efa67ce1bdf4985
worker SHA256         = c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071
```

专用 auditor 对本地 manifest、25 份结果 payload、约束指纹和 worker 指纹进行核验，
最终状态为：

```text
status              = unsat-covered
manifest_complete   = true
proof_scope_match   = true
worker_sha_match    = true
pairs_seen          = 25
missing_jobs        = 0
invalid_jobs        = 0
unknown_jobs        = 0
overlap_count       = 0
sat_witnesses       = 0
```

最终 runner summary 保存的是 Ubuntu 绝对输出路径。直接在 Windows 上按这个绝对路径
查找文件会产生 25 个假“失配”，所以另用独立 crosschecker 执行以下确定性映射：

```text
basename(summary.output) -> local manifest declared result directory
```

它逐项比较 manifest value、summary value、basename、terminal state、summary status、
payload status、summary output SHA、本地文件 SHA、spec SHA、worker SHA，并验证结果目录
恰好含 25 个预期 JSON。结果为：

```text
status           = verified
jobs_seen        = 25
file_count       = 25
reused           = 6
completed        = 19
mismatch_count   = 0
errors           = []
all_unsat        = true
no_timeout       = true
directory_exact  = true
spec_sha_equal   = true
worker_sha_equal = true
```

## 运行与迁移

最初在 Windows 上以两个 worker 运行 matrix。获得首批结果后，本机可用物理内存曾降到
约 `2166.7 MiB`，随后又降至数百 MiB。为避免继续挤压本机资源，停止本任务的本地
supervisor，并只让一份接近完成的工作自然写出；没有干预其它代理的进程。最终保留了
6 份完整 UNSAT payload。

随后生成同一 25 项约束、同一结果目录的一 worker resume spec，将 spec 和已有 6 份
结果迁移到 Ubuntu 沙箱路径 `/root/congProjects/turing-complete-works`。远端复核 worker
SHA 一致后，以单 worker 完成剩余 19 片。最终 summary：

```text
finished  = true
reused    = 6
completed = 19
status    = 25 x unsat
timeout   = 0
```

25 份结果 payload 中 `solve_seconds` 的统计为：

```text
minimum = 53.503862147044856 s
maximum = 303.2300161000021 s
sum     = 4686.157175524113 s
```

远端 runner 随后自然退出；完成检查时没有残留的本任务 runner/solver。Windows 本地也
没有再启动 solver。

## 对 102/5/510 路径的含义

上游冻结证据为：

```text
S3/S4     = 11 gates @ D5
S7/C8     = 16 gates @ D5
fixed     = 73 gates
```

若本类存在 `S5/S6/S7/C8 = 18 gates @ D5` 的 SAT 见证，则可与 `S3/S4 = 11`
组成 high residual `29 gates @ D5`，再与 fixed 73 组合成：

```text
102 gates / 5 delay / 510 energy
```

但本类 25/25 均为 UNSAT，因此没有生成 `102/5/510` 完整候选。这个结论只排除当前
精确拓扑路线，不排除其它 `g18` 拓扑获得同一总指标。

## 限定范围

本结论只封闭：

```text
[NOT,NOR,OR,OR,K1,K2,SWITCH x6]
K1,K2 in {NOT,AND,OR,NAND,NOR}
```

它不覆盖：

1. ordinary 与 Switch 交错的拓扑；
2. ordinary 位于 Switch 之后并读取 resolved Switch BUS 的拓扑；
3. 前四个 ordinary 的其它顺序或其它 multiset；
4. 含 XOR 或其它 gate/component 成本分解；
5. paid-source shell 与 residual 接口的联合重写；
6. `S5/S6/S7/C8 g18` 的全部可行拓扑。

因此正确表述是“固定 `NOT,NOR,OR,OR` 前缀、双 ordinary 槽、六只 terminal-Switch
的完整 5x5 类 UNSAT”，不是“`g18` 全局 UNSAT”。

## 证据文件

```text
.research/byte_adder_phase_shortcut_restart/make_s567c8_g18_o6_s6_tailprefix_two_slot.py
.research/byte_adder_phase_shortcut_restart/audit_s567c8_g18_o6_s6_tailprefix_two_slot.py
.research/byte_adder_phase_shortcut_restart/crosscheck_s567c8_g18_o6_s6_tailprefix_matrix.py
.research/byte_adder_phase_shortcut_restart/local_s567c8_g18_o6_s6_tailprefix_wildcard_w1.json
.research/byte_adder_phase_shortcut_restart/local_s567c8_g18_o6_s6_tailprefix_wildcard_w1_audit.json
.research/byte_adder_phase_shortcut_restart/server-runs/local_s567c8_g18_o6_s6_tailprefix_wildcard_w1/sweep-summary.json
.research/byte_adder_phase_shortcut_restart/local_s567c8_g18_o6_s6_tailprefix_matrix_w2.json
.research/byte_adder_phase_shortcut_restart/local_s567c8_g18_o6_s6_tailprefix_matrix_w2_interrupted_summary.json
.research/byte_adder_phase_shortcut_restart/local_s567c8_g18_o6_s6_tailprefix_matrix_resume_w1.json
.research/byte_adder_phase_shortcut_restart/local_s567c8_g18_o6_s6_tailprefix_matrix_resume_w1_audit.json
.research/byte_adder_phase_shortcut_restart/local_s567c8_g18_o6_s6_tailprefix_matrix_resume_w1_crosscheck.json
.research/byte_adder_phase_shortcut_restart/server-runs/local_s567c8_g18_o6_s6_tailprefix_matrix_w2/sweep-summary.json
.research/byte_adder_phase_shortcut_restart/server-results/local_s567c8_g18_o6_s6_tailprefix_matrix_w2/
.research/byte_adder_phase_shortcut_restart/s567c8_g18_o6_s6_tailprefix_matrix_SHA256SUMS.txt
```

核心 SHA-256：

```text
generator         = 139f80c524237fd9af98a71103dfe9a3b07518fa2b696565fbac33f076fdef9a
auditor           = 78fa1fb73878be88b5ae33ab38828454e14e1fcc9e699d9266c8c9903790c218
crosschecker      = 28dee3f62da863b8b95a78d25203432c67379daa48283ea0d01f425c92d51b10
wildcard spec     = 7fd6deb7677cb01df840e399841472515037259112e65f8fb3b639f653da3551
wildcard audit    = a1e00d65c83a118acaf912df4d4bcf5a2c50f0c764374f9604d68fca3e252c3e
wildcard summary  = bae867a6a754d4af7fe7adf06bb3388204809bfed7094bd21f70455a6906ea39
matrix w2 spec    = 1a61f846c7015991b45cc8ea71f621952c259d56ca1f2b706bb6a9c73c02b626
interrupted       = 38f6c1cf2ea08738e7c28b3d0a2e6e5c57096f9005d63c737a51ab202da14b5c
resume w1 spec    = ccf1be55b9464a5d66b2ea511fbeafc09cbbaa1f561d1377863f2a99de9ecd61
final audit       = 36510cc8ac5ee4956859194a0d001f4b37a7520b279e7bc5685455405f728f22
final crosscheck  = 6d1b0b3322f3b65abb0124b380d37167b3136b75885b67023e083b746d5e552c
final summary     = beeb602cd2c1a195132a556ee843e39c54b6b13b92f3d14f4500428e32113b79
```

全部 25 份 result JSON 的逐文件 SHA-256 收录在专用 `SHA256SUMS` manifest 中。

本研究没有启动游戏，没有读取或写入正式/candidate 存档，也没有修改
`physical_exact.py`。
