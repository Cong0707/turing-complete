# strict-C3 bit3:4：C5 输出驱动完备二分关闭固定 g13/n11/s2/x0

## 结论

本轮精确关闭了 D7 `bit3:4` residual 的一个固定成本分解：

```text
profile          = d7_80
gate bound       = 13
components       = 11
exact Switch     = 2
exact XOR        = 0
ordinary         = 9
deadlines        = S3@5, S4@7, C5@4
boundary rows    = 16 raw assignments × {Z0,D0,D1} = 48
physical nets    = true
all components   = live
```

最终机器账本为：

```text
coverage_complete = true
all_unsat          = true
conclusion         = fixed d7_80 g13/n11/s2/x0 is UNSAT
```

这意味着最直接的 `66 + 13 = 79/7/553` 路线在该固定
`11 components / 2 Switch / 0 XOR` 分解内不存在，因此本轮没有可 graft 的
13 门证书，也没有新的完整候选。

该结论**不是完整 weighted `g <= 13` 下界**。其它 component 数、Switch 数、XOR 数和
成本分解仍未被本报告覆盖。

## 严格接口

付费源保持为：

```text
raw: a3,b3,a4,b4
leaf: G3,Q3,P3,G4,Q4,P4
carry boundary: C3@3
outputs: S3@5, S4@7, C5@4
```

编码继续使用已冻结的 `exact_bit34_joint_sat.py`：

- `C3` 分别检查 `Z0/D0/D1`，不能把 Z0 与主动 D0 混为一种物理状态；
- 普通门读取 Z 为逻辑零并主动驱动输出；
- Switch 关闭时输出 Z；
- 任意 BUS 禁止活动 0/1 冲突；
- `S3/S4` 必须始终主动驱动；
- `C5=0` 时可 Z，`C5=1` 时必须有驱动；
- Switch 输出针脚遵守完整 physical-net source-set partition；
- 每个组件必须 live；
- 普通门、XOR、Switch 成本分别为 `1/3/2`。

冻结 exact encoder SHA-256：

```text
a453c4da570a31ff0210789688ac61a9123eb8be52d5f9a3a8121bc34bcc7ab3
```

执行时的三个传递 core 依赖、文件大小、修改时间以及本地
`CPython 3.13.7 / python-sat 1.9.dev7` 被另行冻结在：

```text
bit34_c5_output_partition_dependency_manifest.json
```

## 为什么 C5 输出只需两个互补分支

基础 CNF 对每个输出都加入非空 selector clause，因此 `C5` 至少选择一个驱动。

`_restrict_active_bus_to_switches` 对以下任一被选驱动与其它驱动加入互斥：

- paid source / 常量；
- 任意非 Switch component 输出，包括普通门和 XOR。

所以当 `C5` 驱动数大于一时，所有驱动都必须是 synthesized Switch 输出。基础实例又固定
`exact_switches=2`，因此 `C5` 的驱动集合只有两类：

```text
1. exactly one driver
2. exactly the two Switch outputs
```

不存在零驱动、三驱动或“普通门/源与 Switch 混合多驱动”的第三类。两份分支账本分别
完整关闭这两类，最终二分账本只在二者都 `coverage_complete=true` 且
`all_unsat=true` 时才给出固定分解 UNSAT。

## 分支 A：两只 Switch 正好组成完整 C5 物理网

### 规范形

令 `k` 为两只 C5 Switch 的普通 component 祖先数。总共有九只普通门，所以：

```text
k ∈ 0..9
```

若最终 C5 net 为 `{SW_A,SW_B}`，则任何包含 `SW_A` 的其它 BUS 都必须拥有完全相同的
driver set。若 `SW_A` 馈入 `SW_B` 的输入，该输入 BUS 与 C5 BUS 在 `SW_A` 上重叠；
physical partition 会要求输入 BUS 同时包含尚不可作为自身输入的 `SW_B`，矛盾。因此
两只 Switch 互不依赖。

任意该类 DAG 都可拓扑重排为：

```text
slots 0 .. k-1 : 全部普通 Switch 祖先
slots k,k+1    : 两只 C5 Switch
remaining      : 所有非祖先普通门
```

每个前缀普通门被额外要求在后续前缀或两只 Switch 中至少有一个用户；沿 DAG 归纳，所有
前缀门都到达一只 Switch。故 `k=0..9` 十片互斥且并集等于完整 C5-pair 分支。

### 结果

MapleChrono 单一完整运行得到：

```text
10/10 UNSAT
UNKNOWN / missing / SAT = 0 / 0 / 0
variables               = 25647
clauses                 = 204769 .. 204778
solve seconds            = 0.098061 .. 56.643558
sum solve seconds        = 228.981008
```

完整结果：

```text
bit34_d7_g13_n11_s2_x0_c5_pair_cone_maplechrono_complete.json
SHA-256 = 481da1da3a97cf996a62d42e3ede32d607723342cc0e960be4790247dd2a1da7
```

### 14 门正回归

同一 cone 约束被固定到已知 D7 14 门网络的规范重排：

```text
A34 = OR(G3,G4)
N34 = NOR(Q3,Q4)
V34 = OR(G4,N34)
C5  = BUS(SW(A34,V34),SW(C3,V34))
```

随后接回七只普通 sum 门。`k=3` 正回归返回 SAT：

```text
actual gate = 14
rows        = 48
mismatch    = 0
conflict    = 0
undriven    = 0
partition violation = 0
```

这排除了 cone 规范约束误伤已知合法 C5-pair 网络的实现错误。

```text
bit34_c5_pair_cone_positive_g14.json
SHA-256 = 52dd7780608e7f3363f59a2ec57af4f0d3c15ffaa1ce9983b42fdf64c5d121df
```

## 分支 B：C5 exactly one driver

### 规范形

单驱动只能是：

```text
source shard : paid source 或免费常量
component k  : 恰有 k 个 component 祖先，k ∈ 0..10
```

component 分支把全部其它 C5 output selector 置假，并把所有 driver 祖先排在前、driver
紧随、非祖先 component 排在后。source 分支把全部 component output selector 置假；
基础非空约束与 source 多选互斥使它实际恰选一个源或常量。

因此 `source + k0..k10` 十二片互斥且并集等于完整 single-driver 分支。

### 结果与 UNKNOWN 处理

Glucose42 首轮：

```text
source,k0..k8 = UNSAT
k9,k10        = UNKNOWN after 30 s each
```

两项 `UNKNOWN` 没有被当作 UNSAT。随后 MapleChrono 只补算相同 constraint digest 的
`k9/k10`：

```text
k9  = UNSAT, 22.036114 s
k10 = UNSAT, 26.504028 s
```

合并器逐项检查：

- 两个 source artifact 的 SHA-256；
- 搜索脚本 SHA-256；
- exact encoder SHA-256；
- shard domain；
- 每片 constraint digest；
- 是否出现 SAT/UNSAT 冲突。

最终：

```text
12/12 UNSAT
UNKNOWN-only / missing / conflict / SAT = 0 / 0 / 0 / 0
selected solve seconds = 0.083062 .. 26.504028
sum selected solve seconds = 113.125568
```

完整合并账本：

```text
bit34_d7_g13_n11_s2_x0_c5_single_driver_cone_merged_complete.json
SHA-256 = 04b86fa150af61d635c9bd1cf3b8d98347387ac20ef7f366c9283910b2b87fb6
```

## 最终完备账本

最终 summarizer 同时验证两份分支账本、exact encoder 和两个分支脚本的 SHA-256，输出：

```text
coverage_complete = true
all_unsat          = true
errors             = []
conclusion         = fixed d7_80 g13/n11/s2/x0 is UNSAT
```

机器账本：

```text
bit34_d7_g13_n11_s2_x0_c5_output_partition_complete.json
SHA-256 = 0a9b1bca34a0f0bef405f446946379df457c611273ad89ea20bebaafd744e5a5
```

合并器连续重跑时，single-driver merged ledger 与最终 partition ledger 的 SHA 均保持不变。

## 独立静态概念审计

`/root/byte_adder_builder_verify_restart` 未重跑 SAT，只独立审查覆盖论证和 encoder 约束，
结论为 `coverage argument sound`，未发现覆盖漏洞。审计特别确认：

1. `C5` non-empty selector 与 multi-driver Switch-only 二分正确；
2. pair 分支两只 Switch 因 physical partition 不能互相依赖；
3. pair `k0..9` 与 single `source+k0..10` 的 normal form 均为 WLOG 完备覆盖；
4. commutative BUS 字典序只需在重标号后交换左右输入，不破坏拓扑规范化；
5. pair、single、combined 三个关键 ledger SHA 与本报告一致。

独立审计文件：

```text
2026-08-04-bit34-C5输出分区独立覆盖审计.md
```

## 复算命令

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'

.\.venv\Scripts\python.exe `
  .research\byte_adder_conditional_sum_restart\exact_bit34_c5_pair_cone_shards.py `
  --solver maplechrono --timeout 120 `
  --output .research\byte_adder_conditional_sum_restart\bit34_d7_g13_n11_s2_x0_c5_pair_cone_maplechrono_complete.json

.\.venv\Scripts\python.exe `
  .research\byte_adder_conditional_sum_restart\exact_bit34_c5_single_driver_cone_shards.py `
  --solver glucose42 --timeout 30 `
  --output .research\byte_adder_conditional_sum_restart\bit34_d7_g13_n11_s2_x0_c5_single_driver_cone_glucose42.json

.\.venv\Scripts\python.exe `
  .research\byte_adder_conditional_sum_restart\exact_bit34_c5_single_driver_cone_shards.py `
  --shard k9 --shard k10 --solver maplechrono --timeout 180 `
  --output .research\byte_adder_conditional_sum_restart\bit34_d7_g13_n11_s2_x0_c5_single_driver_cone_k9_k10_maplechrono.json

.\.venv\Scripts\python.exe `
  .research\byte_adder_conditional_sum_restart\summarize_bit34_c5_single_driver_shards.py `
  .research\byte_adder_conditional_sum_restart\bit34_d7_g13_n11_s2_x0_c5_single_driver_cone_glucose42.json `
  .research\byte_adder_conditional_sum_restart\bit34_d7_g13_n11_s2_x0_c5_single_driver_cone_k9_k10_maplechrono.json `
  --output .research\byte_adder_conditional_sum_restart\bit34_d7_g13_n11_s2_x0_c5_single_driver_cone_merged_complete.json

.\.venv\Scripts\python.exe `
  .research\byte_adder_conditional_sum_restart\summarize_bit34_c5_output_partition.py `
  --pair .research\byte_adder_conditional_sum_restart\bit34_d7_g13_n11_s2_x0_c5_pair_cone_maplechrono_complete.json `
  --single .research\byte_adder_conditional_sum_restart\bit34_d7_g13_n11_s2_x0_c5_single_driver_cone_merged_complete.json `
  --output .research\byte_adder_conditional_sum_restart\bit34_d7_g13_n11_s2_x0_c5_output_partition_complete.json

.\.venv\Scripts\python.exe `
  .research\byte_adder_conditional_sum_restart\verify_bit34_c5_pair_cone_positive_regression.py `
  --output .research\byte_adder_conditional_sum_restart\bit34_c5_pair_cone_positive_g14.json
```

## 不能外推的边界

本报告只关闭：

```text
d7_80 / gate_bound=13 / components=11 / exact_switches=2 / exact_xors=0
```

它不能推出：

- 所有 `gate <= 13` component 数都 UNSAT；
- 其它 Switch/XOR 精确计数组合 UNSAT；
- D6 或 D5 的局部下界；
- `73/7` 或 `85/6` 目标不可达；
- 任何未完成或 `UNKNOWN` 的远端分片可当作 UNSAT。

远端 49 个 `(slot0 kind,slot1 kind)` 分片仍按原 runner 继续，未被停止、重启或修改；其
结果不是本地 C5 输出二分证明成立的前提。

## 待提交文件

精确文件列表写入同目录：

```text
bit34_c5_output_partition_submit_files.txt
bit34_c5_output_partition_SHA256SUMS.txt
```

本轮没有启动游戏，没有读取或修改正式存档，没有修改或部署
`examples/byte_adder/candidate`，也没有暂存或提交 Git。
