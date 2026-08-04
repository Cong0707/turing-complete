# S5/S6/S7/C8：g16/o4/s6 固定 all-Switch tail 精确封闭

日期：2026-08-04

## 结论

以下单一 fixed-kind 拓扑在 `s34567c8_leaf` 的 486 个相关输入行、四输出
`S5,S6,S7,C8`、`gate <= 16`、`delay <= 5` 约束下得到终态 `unsat`：

```text
NOT,NOR,OR,OR,
SWITCH,SWITCH,SWITCH,SWITCH,SWITCH,SWITCH
```

严格归类：

```text
completed = 1
reused    = 0
SAT       = 0
UNSAT     = 1
UNKNOWN   = 0
timeout   = 0
missing   = 0
invalid   = 0
```

因此，该固定拓扑不能提供原目标的四输出 16-gate D5 tail。若其为 SAT，
与冻结 `73 + S3/S4 11` 组合本可得到：

```text
73 + 11 + 16 = 100 gates
delay = 5
energy = 100 * 5 = 500
```

本结论只排除这一条 fixed-kind 序列，不是全局 g16 下界；它不排除其它
ordinary/Switch 顺序、其它 ordinary kinds、XOR 分解或 paid-shell 联合重写。

## 精确范围

```text
domain       = s34567c8_leaf
rows         = 486
outputs      = S5,S6,S7,C8
gate bound   = 16
max delay    = 5
components   = 10
ordinary     = 4
Switch       = 6
XOR          = 0
```

成本恒等式：

```text
10 components + 6 Switch + 2*0 XOR = 16 gates
```

研究 JSON 的结构化扫描在创建本 spec 前确认：

```text
gate=16 and outputs=S5,S6,S7,C8 prior hit count = 0
all scanned prior fixed-family overlap          = 0
Han-family overlap                              = 0
```

该族与 root/Han 的 g17/g18 position/decomposition 扫描在 gate、components
或 quota 上均不同。

## 无 solver 正回归

冻结文件 `tail_s7c8_g16_fixed_kinds_d5.json` 是同一精确拓扑的 S7/C8
witness。正回归没有修改网络，而是独立重建 486 行 truth、重新执行所有门和
高阻态 BUS，并检查物理网、liveness、成本与时序：

```text
status                            = verified-positive-regression
actual_gate                       = 16
actual_output_arrivals            = [5,5]
actual_max_delay                  = 5
mismatch_count                    = 0
bus_conflict_count                = 0
undriven_output_count             = 0
physical_net_partition_violation  = 0
active_bus_non_switch_violation   = 0
topology/order/dead/timing errors = 0
```

该证据只校准 S7/C8；它不是四输出 SAT witness。

## Ubuntu 正式求解

```text
spec       = ubuntu_s567c8_g16_o4_s6_all_switch_tail_w1.json
workers    = 1
AS limit   = 1536 MiB
nice       = 5
CPU set    = 0-31
outer cap  = 900 s
solver     = cadical195
stop SAT   = true
```

终态 payload：

```text
status          = unsat
variables       = 174696
clauses         = 1340194
solve_seconds   = 79.2113160280278
runner elapsed  = 79.4775896309875
```

runner stderr 为空，wrapper/worker 自然退出。

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

下载 payload 和 finished summary 后，本地重新审计同样得到
`unsat-covered`。

独立 basename/SHA/directory crosschecker 结果：

```text
status          = verified
jobs_seen       = 1
file_count      = 1
completed       = 1
reused          = 0
mismatch_count  = 0
errors          = []
no_timeout      = true
directory_exact = true
```

## 关键证据 SHA-256

```text
physical_exact.py
c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071

make_s567c8_g16_o4_s6_all_switch_tail.py
7da94c4e065a08aec55c77bbbbb560c97f30aee2c06032348d5e3d60d2f8de50

audit_s567c8_g16_o4_s6_all_switch_tail.py
e5cdff31250d4620d8fb17be01a72a10ca20809205649102ee69afb65641a4aa

preflight_s567c8_g16_o4_s6_all_switch_tail.py
ea2ef372c166f9a6181421c2e4d37acd4786efe5437a44fd8131cb2c56eef5c1

crosscheck_s567c8_g16_o4_s6_all_switch_tail.py
c4862a7d06595518c20b86b01bebdd1a231f3ac7bec5186f5e866574616a23af

verify_s567c8_g16_o4_s6_all_switch_tail_positive_regression.py
7af0dd5de7a49b553fd7c7eca20236f6645568f6316dc5acc592072bff9294be

s567c8_g16_o4_s6_all_switch_tail_positive_s7c8.json
8b0712579649754262c4b06d6fab59c7397e52f8df5f17cd5407eb0b32c1a5b5

ubuntu_s567c8_g16_o4_s6_all_switch_tail_w1.json
954db3c9be747c413e698a8351931ae9ff643e752cfd1d4e61cb927e31cddcf8

remote audit
aaa187a151814b692b5f06245987f185ee312a25134eb2dabfc636e411ecb254

local audit
be141cf674061e25d9db815c8eec05de9ac0b381913228865e3f99854076615b

crosscheck result
ebb1bfc399e7a7c331da3720b136023b5f86fb19bd10b53fda45e7b7a52797e3

final sweep-summary.json
60eb20d7a3db73ee30259b1fa50f01907e470fcf619f3b8ff6c068abf09795d6

result payload
8ab7194bb3ff97a68cf090efc440b96ad7013567a2dbca201492345742b9aeae
```

完整逐文件哈希另见：

```text
s567c8_g16_o4_s6_all_switch_tail_SHA256SUMS.txt
```
