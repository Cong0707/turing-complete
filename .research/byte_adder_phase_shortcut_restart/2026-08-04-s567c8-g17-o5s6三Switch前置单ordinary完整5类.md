# S5/S6/S7/C8：g17/o5/s6 三只前置 Switch + 单 ordinary 完整五类精确封闭

日期：2026-08-04

## 结论

以下固定相位族在 `s34567c8_leaf` 的 486 个相关输入行、四输出
`S5,S6,S7,C8`、`gate <= 17`、`delay <= 5` 约束下已经完整精确封闭：

```text
NOT,NOR,OR,OR,
SWITCH,SWITCH,SWITCH,
K,
SWITCH,SWITCH,SWITCH

K ∈ {NOT,AND,OR,NAND,NOR}
```

五个互斥分片全部得到终态 `unsat`：

```text
completed = 5
reused    = 0
SAT       = 0
UNSAT     = 5
UNKNOWN   = 0
timeout   = 0
missing   = 0
invalid   = 0
overlap   = 0
```

因此，该固定相位族不能提供原目标的四输出 17-gate D5 tail。若该族曾有
SAT，则与冻结 `73 + S3/S4 11` 组合可得到：

```text
73 + 11 + 17 = 101 gates
delay = 5
energy = 101 * 5 = 505
```

本结论只排除上述五个精确 fixed-kind 序列，不是全局 g17 下界，也不排除
其它 ordinary/Switch 位置、其它 ordinary 前缀、XOR 分解或 paid-shell 联合重写。

## 精确范围与完备性

模型参数：

```text
domain       = s34567c8_leaf
rows         = 486
outputs      = S5,S6,S7,C8
gate bound   = 17
max delay    = 5
components   = 11
ordinary     = 5
Switch       = 6
XOR          = 0
```

成本恒等式：

```text
11 components + 6 Switch + 2*0 XOR = 17 gates
```

唯一变量槽为 zero-based slot 7。五类 ordinary kind 各出现一次，形成完整、
互斥的五分片：

```text
OR, NOT, AND, NAND, NOR
```

执行时优先 `OR`，其余四类随后运行。所有 fixed constraint、job name、输出
路径与 constraint SHA 均唯一。

静态非重复扫描确认：

```text
all scanned prior-family overlap = 0
Han-family overlap               = 0
```

该族为 11 components / o5/s6；当时 Han/root 的相关扫描为 10 components /
o2/s8，上一轮 mid-BUS 与 terminal 类为 12 components / o6/s6，因此 fixed
tuple 严格不同。

## 无 solver 正回归

正回归从冻结的 S7/C8 g16 witness：

```text
tail_s7c8_g16_fixed_kinds_d5.json
```

在前三只 Switch 后插入 `OR(x,0)` identity，并将后续 Switch 的输入改经该
identity。独立重放全部 486 行：

```text
status                            = verified-positive-regression
actual_gate                       = 17
actual_output_arrivals            = [5,5]
actual_max_delay                  = 5
mismatch_count                    = 0
bus_conflict_count                = 0
undriven_output_count             = 0
physical_net_partition_violation  = 0
active_bus_non_switch_violation   = 0
topology/order/dead/timing errors = 0
```

该正回归只校准 `S7/C8` 的新相位顺序、BUS、物理网、成本与时序；它不是
`S5/S6/S7/C8` SAT witness。

## Ubuntu 正式求解

正式矩阵：

```text
spec       = ubuntu_s567c8_g17_o5_s6_midbus3_matrix_w1.json
workers    = 1
AS limit   = 1536 MiB
nice       = 5
CPU set    = 0-31
outer cap  = 900 s/job
solver     = cadical195
stop SAT   = true
```

每片 CNF：

```text
variables = 203234
clauses   = 1531881
```

payload `solve_seconds`：

```text
OR    55.536687311017886 s
NOT   74.25435687002027  s
AND   65.01533866295358  s
NAND  61.00236109999241  s
NOR   66.97656458703568  s

minimum = 55.536687311017886 s
maximum = 74.25435687002027 s
sum     = 322.78530853101984 s
```

runner `elapsed_seconds`：

```text
minimum = 55.67134348599939 s
maximum = 74.42264626099495 s
sum     = 323.5585675999173 s
```

runner stderr 为空，wrapper/worker 均自然退出。

## 严格审计与独立交叉核验

远端 final auditor：

```text
status                    = unsat-covered
manifest_complete         = true
proof_scope_match         = true
worker_sha256_match       = true
auditor_sha256_match      = true
dependency_sha256_match   = true
positive_regression_match = true
missing/invalid/unknown   = 0/0/0
summary.integrity         = true
summary.complete_unsat    = true
summary.errors            = []
```

下载原始 payload 与 finished summary 后，本地重新审计同样得到
`unsat-covered`。

独立 basename/directory crosschecker 未导入 family auditor，结果：

```text
status          = verified
jobs_seen       = 5
kinds_seen      = 5
file_count      = 5
completed       = 5
reused          = 0
mismatch_count  = 0
errors          = []
all_unsat       = true
no_timeout      = true
directory_exact = true
```

## 关键证据 SHA-256

```text
physical_exact.py
c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071

make_s567c8_g17_o5_s6_midbus3_one_slot.py
3da8716e97ebd4af8f3157cd8042b9d9f84baa0295b2444823a575bf69f4b751

audit_s567c8_g17_o5_s6_midbus3_one_slot.py
c48c92871d303fc90341b18398b99de9031222d9652b6597cc1aa5314c2182bf

preflight_s567c8_g17_o5_s6_midbus3_one_slot.py
187916ba9f16f445886b8d6d608bc9dd54cba2a60a0a274dcfd0365805f5888c

crosscheck_s567c8_g17_o5_s6_midbus3_matrix.py
0a8e5f685ff7cf5c1ff1d81d53d8ab222472bba6b7c0e9662bf2cc6231f75f17

verify_s567c8_g17_o5_s6_midbus3_positive_regression.py
c06c9cbf64c61ea0c337af5e52dc63b039cda14647640945cc7b97f54fe64f5b

s567c8_g17_o5_s6_midbus3_positive_s7c8.json
8b233eba5c64661ef0e376309fbbe7ffa66ce72bb38cfc623bfec45a6053f376

ubuntu_s567c8_g17_o5_s6_midbus3_matrix_w1.json
4a7d12316ca69e018dec9c1b97e08f73a024d53796bb1f49cc34d8e149807cdd

remote audit
e00e86dd58d209e6d73028b7ef43e05d5dbb7183d5f7bf07686a76f641ea611f

local audit
e0d7cb0580713a85fa6955ed4f48e3ab9ede4a5301815284d74eaec3bcf1516c

crosscheck result
ce294d7094aa2417371f10e263c9639e541bea4c6e16c6b1c2e48b765f0bb475

final sweep-summary.json
79641773ef0777061408c63a2b80106b8eecec001595768f7ed455d97e5a932c
```

完整逐文件哈希另见：

```text
s567c8_g17_o5_s6_midbus3_SHA256SUMS.txt
```
