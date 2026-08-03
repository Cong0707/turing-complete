# current80 suffix567 exact-cost 9 全 composition 覆盖封闭

日期：2026-08-04

## 结论

对 current80 固定 `suffix567` 接口的 exact weighted-cost 9 搜索，现有 kind shard 已形成
完整、互斥且无遗留 UNKNOWN 的覆盖树：

```text
精确成本分解                 12 / 12
slot0 七类初始分区           84 / 84
原始 job                    114
求解器 UNSAT 输出           108
父级外部 timeout              6
已由子分区完全替代的 timeout   6 / 6
终端 UNSAT 叶               108
SAT / 运行时失败 / 遗留 UNKNOWN  0 / 0 / 0
缺失 / 重复 / orphan / 叶前缀重叠 0 / 0 / 0 / 0
```

因此，在下述固定 source/interface、物理 BUS、递归 delay 和 primitive 编码内，不存在成本 9
的 `S5/S6/S7/C8` 联合 suffix 网络。重复运行同一固定 suffix 的 `79/7` 搜索没有新增覆盖价值，
应停止。

本轮只做离线证据合并与审计；没有生成候选、没有部署，也没有读取或写入正式 Byte Adder
save。正式前沿不因本报告改变。

## 固定契约

所有被接纳记录均精确匹配：

```text
schema             exact-suffix567-shared-phase-v1
interface          s6
outputs            S5,S6,S7,C8
gate_bound         9
max_delay          7
output_deadlines   6,7,7,7
solver             cadical195
physical_nets      true
```

固定 free sources：

```text
a5,b5,a6,b6,a7,b7,C5,
G5,Q5,P5,G6,Q6,P6,G7,Q7,P7,
T,D,G,C7,T5,0,1
```

关键 arrival 为 `C5=4`、`T=3`、`D=4`、`G=2`、`C7=5`、`T5=5`；每个 UNSAT
输出内的完整 `source_arrivals`、deadline、composition 与 `forced_slot_kinds` 都由独立审计器
逐字段复核。

primitive kind 与成本为：

```text
NOT/AND/OR/NAND/NOR  cost=1 delay=1
SWITCH               cost=2 delay=1
XOR                  cost=3 delay=2
```

审计器从当前通用 core 的 AST 读取并核对这些常量，同时检查：

- worker 对 Switch 与 XOR 使用 exact cardinality，而非仅上界；
- shard wrapper 对每个 `slot:KIND` 注入单元子句；
- wrapper 做 slot 范围、kind 成员与重复 slot 冲突检查；
- worker 输出保留实际 `forced_slot_kinds`；
- 既有 `slot0:SWITCH + exact_switches=0` 回归为立即 UNSAT。

## composition 全集

设 `n=components`、`s=exact_switches`、`x=exact_xors`。每个 component 的基础成本为 1，
Switch 再增加 1，XOR 再增加 2，因此：

```text
n + s + 2x = 9
n - s - x >= 0
```

对非负整数解直接枚举，只有以下 12 项。该全集由成本方程生成，不是从现有结果文件反推：

```text
composition  ordinary  Switch  XOR  slot0 kinds  terminal UNSAT  timeout parents
n9_s0_x0         9        0     0       7              31               6
n8_s1_x0         7        1     0       7               7               0
n7_s2_x0         5        2     0       7               7               0
n6_s3_x0         3        3     0       7               7               0
n5_s4_x0         1        4     0       7               7               0
n7_s0_x1         6        0     1       7               7               0
n6_s1_x1         4        1     1       7               7               0
n5_s2_x1         2        2     1       7               7               0
n4_s3_x1         0        3     1       7               7               0
n5_s0_x2         3        0     2       7               7               0
n4_s1_x2         1        1     2       7               7               0
n3_s0_x3         0        0     3       7               7               0
```

每个 composition 的 slot 0 都按 worker 的完整七类 kind 分区：

```text
NOT, AND, OR, NAND, NOR, XOR, SWITCH
```

每个编码 component 恰好选择一种 kind，所以七个子空间互斥且并集等于该 composition 的
全部编码模型。除 `n9_s0_x0` 外，其余 11 个 composition 的 77 个 slot0 shard 全部为
终端 UNSAT。

## n9 ordinary 递归封闭

`n9_s0_x0` 的初始七分区结果为：

```text
slot0 NOT/SWITCH/XOR     UNSAT
slot0 AND/NAND/NOR/OR   外部 300 秒 timeout
```

这四个 timeout 不是终端结论。它们随后按 slot 1 继续完整拆分。因为本 composition 强制
`exact_switches=0` 且 `exact_xors=0`，任一后续 slot 可行的完整 kind 集合恰为五种 ordinary
kind：

```text
NOT, AND, OR, NAND, NOR
```

slot 1 的 `4 x 5 = 20` 个互斥子空间已全部存在：

```text
18 个 UNSAT
2 个 timeout: (NOR,NOR), (NOR,OR)
```

两个剩余 timeout 又分别按 slot 2 的同一五种 ordinary kind 完整拆分：

```text
(NOR,NOR,*)  5 / 5 UNSAT
(NOR,OR,*)   5 / 5 UNSAT
```

因此 n9 树的终端叶为：

```text
slot0 直接 UNSAT                 3
slot1 直接 UNSAT                18
slot2 细分后 UNSAT              10
合计终端 UNSAT                  31
已替代父 timeout                 6
遗留 timeout / UNKNOWN           0
```

审计器从根的七类 slot0 分区递归遍历：遇到 UNSAT 即收口；遇到 timeout 则用 composition
剩余 exact kind 计数独立推导应有子集合，并要求实际 children 与该集合严格相等。全部 114
个 region key 被访问一次，没有 orphan；108 个终端前缀两两不存在祖先关系，故不存在由父叶
与子叶造成的覆盖重叠。

## 证据完整性

独立审计覆盖 362 个输入证据文件：

```text
编码与 wrapper 依赖        6
sweep specs               10
sweep summaries           10
per-job records          114
UNSAT outputs            108
logs（含 6 个空 timeout） 114
合计                      362
```

逐项验证包括：

- summary 中的 spec SHA 与磁盘 spec 相同；
- 10 份 summary 的 wrapper SHA 均等于当前 wrapper SHA；
- summary result 与对应 per-job record JSON 完全相同；
- record command 精确等于 spec arguments 按 value 展开后的命令；
- composition、连续 forced prefix、固定 solver 参数与输出路径一致；
- 108 份 output/log 的实际 SHA 与 record 一致；
- log 归一化换行后严格等于 output JSON 加其 `sha256=` 行；
- 6 个 timeout 没有伪造 output，log 为空且 SHA 为标准空文件 SHA；
- 没有 `sat`、worker `unknown`、非预期 return code 或缺失文件。

核心哈希：

```text
7acd366220b5cee91ad921e37e1c97b0e3b8f892a442b9f8518763a8783b5fad
  audit_suffix567_g9_exact_cost9_coverage.py

3a494f6676b18a7824694d11b4ef622a3dd08f210c520dbc6d828905c026f691
  independent_coverage_audit.json

d5bf1d11ca9accd4d02ff7ffd69d7d9dd2109aeae4c5f8516b45e6fa035c8c6b
  exact_suffix567_kind_shard.py
```

完整 365 项冻结集合由同目录 `suffix567_g9_exact_cost9_coverage_SHA256SUMS.txt` 记录；其中
362 项为输入证据，另含独立审计器、审计器输出与本报告，manifest 自身按惯例不包含自身。
全局 `examples/byte_adder/history/字节加法器.md` 会持续追加后续研究，因此刻意不纳入冻结
manifest，避免后续正常记录使本证明清单失效。

## 确定性复验

在仓库根目录使用项目虚拟环境：

```powershell
$script = '.research\byte_adder_builder_verify_restart\suffix567_g9_exact_cost9_coverage\audit_suffix567_g9_exact_cost9_coverage.py'

$env:PYTHONHASHSEED = '1'
.\.venv\Scripts\python.exe $script --output audit.seed1.json

$env:PYTHONHASHSEED = '777'
.\.venv\Scripts\python.exe $script --output audit.seed777.json

Get-FileHash audit.seed1.json -Algorithm SHA256
Get-FileHash audit.seed777.json -Algorithm SHA256
```

两次独立进程实测 SHA 均为：

```text
3a494f6676b18a7824694d11b4ef622a3dd08f210c520dbc6d828905c026f691
```

生成正式 audit 与 manifest：

```powershell
$dir = '.research\byte_adder_builder_verify_restart\suffix567_g9_exact_cost9_coverage'
.\.venv\Scripts\python.exe "$dir\audit_suffix567_g9_exact_cost9_coverage.py" `
  --output "$dir\independent_coverage_audit.json" `
  --report "$dir\2026-08-04-suffix567-exact-cost9全composition覆盖封闭.md" `
  --manifest "$dir\suffix567_g9_exact_cost9_coverage_SHA256SUMS.txt"
```

## 严格边界

本结论只封闭当前 `suffix567` 固定 source shell、`s6` interface、物理 BUS 编码、D7 deadline
和 exact weighted-cost 9。它不能外推为全局 `79/7` 下界，也不覆盖：

- 改变 upstream paid/free source shell；
- 跨 suffix 边界的联合重综合；
- 改变 primitive 库、BUS 语义或 delay 模型；
- 其它全局拓扑、placement 或共享结构。

本审计独立验证 composition 枚举、分区并集/互斥性、命令契约与证据哈希，不重新执行这些
重型 SAT 作业。UNSAT 判定继承现有 CaDiCaL 195 输出；现有证据没有 DRAT/LRAT 证书或第二
求解器交叉证明。若后续需要 proof-carrying 下界，应另行保存可独立检查的 UNSAT proof，
而不是重复相同的 timeout/slot-kind 搜索。
