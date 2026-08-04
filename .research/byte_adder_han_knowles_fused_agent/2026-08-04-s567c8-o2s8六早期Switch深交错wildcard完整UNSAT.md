# S5/S6/S7/C8：o2/s8 六早期 Switch 深交错 wildcard 完整 UNSAT

## 结论

在 `fixed 73 + high residual 29` 的 D5 paid-source 接口上，一次 Ubuntu CaDiCaL 完整物理求解严格封闭了：

```text
slot:  0       1       2       3       4       5       6   7       8   9
kind:  SWITCH, SWITCH, SWITCH, SWITCH, SWITCH, SWITCH, K1, SWITCH, K2, SWITCH

K1,K2 ∈ {NOT,AND,OR,NAND,NOR}
```

这是两个深交错 ordinary wildcard 的完整 5x5 ordered matrix，不是局部相位 3x3：

```text
status                = unsat-covered
ordered_pair_count    = 25
unique_assignment     = 25
missing               = 0
invalid               = 0
```

因此该固定 topology 内，六只早期 Switch 可任意组成一条或多条合法 resolved BUS，K1/K2 可选择全部五种普通门 kind，中间 Switch 与最后一只 Switch 可任意布线；仍不存在满足 `S5/S6/S7/C8`、成本 18、D5 的合法网络。特别地，它完整包含了前六只 Switch 拆成两条独立 3-driver BUS 同时喂给 K1，以及 K1 控制或参与中间 Switch、再由 K2 消化其 resolved-BUS 输出的情形。

## wildcard 覆盖为什么完整

权威 CNF 对十个 slot 各自建立：

```text
exactly-one {NOT,AND,OR,NAND,NOR,XOR,SWITCH}
```

本片同时固定：

```text
components     = 10
exact_switches = 8
exact_xors     = 0
gate_bound     = 18
```

slot `0,1,2,3,4,5,7,9` 已经固定为八只 Switch，恰好占满 switch quota。因此 slot6/slot8 两个 `*`：

- 不能是 `SWITCH`；
- 不能是 `XOR`；
- 各自只能且必须是 `{NOT,AND,OR,NAND,NOR}` 之一。

这给出精确的 `5×5=25` 个有序 kind 对。八只 Switch 成本 `8×2=16`，两个普通门成本 `2×1=2`，所以每个 assignment 的真实成本都恰为 18。

## shard 不漏 wildcard

`split_slots=1` 切的是最后一个拓扑 slot：

```text
slot9 = SWITCH
```

它既不是 slot6，也不是 slot8 wildcard。独立重算 width-1 universe：

```text
NOT, AND, OR, NAND, NOR, SWITCH
```

其 SHA256：

```text
0b0c7c64fd44259c23762e70b87484cbb06caad9125d2fd944ecc16ac01666c7
```

`shard_count=1/shard_index=0` 分配全部六个签名；slot9 又被 fixed-kinds 固定为 Switch，所以 shard 只重复 slot9 的固定事实，不限制 slot6/slot8。两个 wildcard 都由同一 exact solver 自由覆盖。

## 完整物理模型

```text
worker = .research/byte_adder_phase_shortcut_restart/physical_exact.py
SHA256 = c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071

domain     = s34567c8_leaf
rows       = 486
outputs    = S5,S6,S7,C8
cost       = 18
delay      = 5
components = 10
o/s/x      = 2/8/0
```

模型完整保留：

- ordinary/Switch 输入 BUS 的自由多源选择；
- Switch 真三态/Z；
- BUS 0/1 conflict 禁止；
- physical-net partition；
- public output 必须 driven；
- 四输出 deadline 5；
- dead-component 禁止；
- primitive 的真实成本与延迟。

所以该 UNSAT 不是单源端口近似，也没有预先固定 early BUS 或 terminal driver 分配。

## Ubuntu 求解与资源记录

```text
solver        = cadical195
status        = UNSAT
variables     = 174812
clauses       = 1340420
solve_seconds = 265.6077585099847
timer_errors  = []
```

外层 run record：

```text
start_utc        = 2026-08-04T00:16:44Z
end_utc          = 2026-08-04T00:21:10Z
wall_seconds     = 266
wrapper_pid      = 170977
exit_code        = 0
classification   = solver_exit
watchdog_seconds = 900
as_limit_kib     = 6291456
nice             = 5
```

`classification=solver_exit` 且 wall/solve 差小于 2 秒，证明这是 solver 正常严格终态，不是 watchdog 截断或 UNKNOWN 冒充 UNSAT。

三件下载证据均保留 Ubuntu LF 原始字节：

```text
result:
.research/byte_adder_han_knowles_fused_agent/remote-results/s567c8_g18_o2s8_interleave_s6_o_s_o_s1_cadical195.json
SHA256 = 5ec01ba249868845942b4c01693195fc4d676a241ae1841e208c37bc046616a8

log:
.research/byte_adder_han_knowles_fused_agent/remote-results/s567c8_g18_o2s8_interleave_s6_o_s_o_s1_cadical195.log
SHA256 = ea5ee72b19ece3040bc0173f2faa5550e9e94699340c8d3d4a9c03b50338dd76

run record:
.research/byte_adder_han_knowles_fused_agent/remote-results/s567c8_g18_o2s8_interleave_s6_o_s_o_s1_cadical195.run.json
SHA256 = d9c49c815e4d2028c679266471289018fe65a1f99cfea7e7d6f3b9c8e01ee4f4
```

log 去掉 `output/sha256` 两字段后与 result JSON 逐字段相同；log 内嵌 result SHA 也与下载后的实际磁盘 SHA 相同。

## Manifest 与独立审计

覆盖 manifest：

```text
.research/byte_adder_han_knowles_fused_agent/s567c8_interleave_s6_o_s_o_s1_wildcard_manifest.json
SHA256 = d057056a0dd9b5810b6b7a8ca3ab79da422e06d7197b547bede45d7f2fe7c73c
```

独立 auditor：

```text
.research/byte_adder_han_knowles_fused_agent/audit_s567c8_interleave_s6_o_s_o_s1_wildcard.py
SHA256 = 297e30e82fe5d359c8b08d4a7ad8fc4276f4205c0f41e5bb6970097cc983170b
```

审计结果：

```text
.research/byte_adder_han_knowles_fused_agent/s567c8_interleave_s6_o_s_o_s1_wildcard_audit.json
SHA256 = 7d4313a5d9ddd1836f3ff82720f5fc816acd3700de0e29679eea2d536d1ab96f
```

auditor 独立校验：

- result/log/run 三文件的实际磁盘 SHA 与 LF 字节；
- log summary 与 result JSON 重合；
- worker 与全部 live dependency SHA；
- schema/domain/486 rows/四输出/成本/时序/decomposition；
- solver、变量/子句、UNSAT 与 timer_errors；
- run record 的 PID、资源限制、正常 solver_exit 与 wall/solve 一致；
- suffix universe 与 shard 全分配；
- 25 个 ordinary kind pair 与 25 个完整 assignment；
- 每个 assignment 的 fixed slots、exact switch/XOR count 与成本 18。

audit 和 manifest 连续两次重放 SHA 完全相同。

重放命令：

```powershell
cd D:\Develop\Other\turing-complete
.\.venv\Scripts\python.exe `
  .research\byte_adder_han_knowles_fused_agent\audit_s567c8_interleave_s6_o_s_o_s1_wildcard.py
```

## 范围边界

本证据只封闭：

```text
SWITCH,SWITCH,SWITCH,SWITCH,SWITCH,SWITCH,K1,SWITCH,K2,SWITCH
K1,K2 ∈ {NOT,AND,OR,NAND,NOR}
```

它不覆盖 ordinary 位于其他 slot、其他 o/s/x decomposition、XOR、其他成本，或全部 cost-18 topology。因此只能把该固定位置族记为完整局部下界，不能外推为 high residual 29 的全局不可能性。

本轮未启动游戏，未读取或写入正式存档，未修改或部署 candidate/metadata，也未提交 Git。
