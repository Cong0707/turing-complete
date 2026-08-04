# Byte Adder source1-data mixed BUS：完整枚举与资源审计

日期：2026-08-04
证据目录：`.research/byte_adder_source1_data_mixed_restart`
远端执行目录：`/root/congProjects/turing-complete-works/.research/byte_adder_source1_data_mixed_f26ac1c2`

## 结论

在下述**固定模型边界**内，`max_per_coverage=512` 的全 268-target
enumeration-only 已经零截断完成：

- `status = enumerated`
- source1-data 新类的 base coverage 截断数：`0`
- source1-data 新类的 expanded coverage 截断数：`0`
- source1-data enumeration complete：`true`
- 旧 base-data 类与新 source1-data 类的 combined enumeration complete：`true`
- 完整 k512 结果 SHA256：
  `3cf1804d6e47cb803183f18048089b67399e4e72e028bd94349c90a5656be0e9`

这里的“完整”只指**声明模型中的候选枚举、可达性和精确 CNF 形状估计完整**。
它不是 SAT，也不是 UNSAT。完整的 `111,807,926`-clause 模型没有启动
solver；结果中的 `backend = not-run`、`enumerate_only = true` 与
`status = enumerated` 均明确记录了这一点。

## 固定模型边界

| 项目 | 值 |
|---|---:|
| 模式 | `integrated-nc7` |
| 固定 shell | 69 gate |
| high-window gate bound | 33 |
| complete gate bound | 102 |
| delay bound | D5 |
| function universe | `source1-residual`，6,500 functions |
| base BUS driver universe | `base`，270 functions |
| mixed target profile | 268 个保留 base-BUS targets |
| probe rows | 1,024 |
| exact-verification threshold | 8 |
| coverage cap | 512 |
| cost encoding | `producer-tiered` |
| cardinality encoding | `seqcounter` |
| CNF storage declaration | `streaming` |

保留的 mixed driver 类有两个：

1. `source1-enable/base-data`；
2. `source1-enable/source1-data`，其中 enable 和 data 都严格排除 base
   functions。

第二类是本轮新增类；第一类保持冻结旧 all-268 模型的完整语义和全部目标。

## 枚举算法的精确性措施

### 保守 truth-row 倒排索引

`ConservativeTruthRowIndex` 使用 1,024 个确定性 truth rows 过滤明显不可能的
data functions。过滤条件只在真实 enabled row 已经与 target 不一致时排除候选，
因此允许假阳性，不允许假阴性。每个 survivor 随后仍执行完整 packed truth-table
条件：

```text
enable & (data ^ target) == 0
```

完整 k512 的 source1-data 统计为：

| 指标 | 数值 |
|---|---:|
| candidate expanded enables | 872,735 |
| probe survivors / full-mask checks | 5,583,857 |
| probe false positives | 400,057 |
| valid source1-data drivers | 5,183,800 |
| mixed coverages | 167,732 |

即所有 `5,583,857` 个 probe survivor 都重新接受了完整 truth-table 检查；
`400,057` 个假阳性被完整检查拒绝。

旧 `source1-enable/base-data` 类也使用同一保守索引方法，其冻结语义统计保持为：

```text
retained recipes      620,908
valid drivers         400,603
enumeration complete  true
```

### Antichain reduction

两处 dependency-minimal reduction 从二次扫描改成了对有限真子集的精确哈希查询：

- `minimal_dependency_sets()`：一个两-Switch recipe 最多四个依赖；
- `minimal_driver_forms()`：一个 driver 最多两个依赖。

因此分别只需枚举最多 15 个和 3 个非空真子集，语义与原二次参考实现严格相同。

### Sequential-counter 闭式 estimator

`seqcounter_atmost_shape(n, k)` 解析计算 PySAT `CardEnc.atmost(...,
EncType.seqcounter)` 的辅助变量和子句数，不再实际构造数千万条 estimator-only
clauses。闭式已经对 5,252 个 `(n,k)` 点与 PySAT 逐点交叉核验，并在 200 个随机
完整小模型上与实际构造的 producer-tiered CNF 统计完全一致。

## k128 截断审计：不能用于 solve 或完备下界

k128 证据：

```text
result SHA256  1881f430781162879488276cffa852839c7bf4bf02076e56d7db9a2a3b455c43
status         enumerated
exit           0
```

决定性统计：

| 指标 | k128 |
|---|---:|
| source1-data retained recipes | 4,818,097 |
| max base forms / coverage | 21 |
| max expanded forms / coverage | 475 |
| truncated base coverages | 0 |
| truncated expanded coverages | 150 |
| source1-data enumeration complete | `false` |
| combined enumeration complete | `false` |

由于实际最大 expanded forms 为 `475 > 128`，并且 150 个 expanded coverages
发生截断，k128 只能作为 cap 不足的审计证据，不能用于 SAT solve、UNSAT 证明或
完备下界。

k128 资源记录：

```text
wall       57:37.40
user CPU   3448.45 s
system CPU 4.59 s
peak RSS   3,198,576 KiB
exit       0
```

## k512 零截断完整枚举

k512 把 coverage cap 提升到 512，高于完整枚举观察到的最大值 475：

| 指标 | k512 |
|---|---:|
| all targets | 268 |
| targets with source1-data recipe | 266 |
| expanded enable universe | 6,030 |
| expanded data universe | 6,030 |
| old base-data mixed recipes | 620,908 |
| new source1-data mixed recipes | 4,868,473 |
| combined mixed recipes | 5,489,381 |
| all recipes | 5,536,867 |
| active candidates | 5,347,773 |
| max base forms / coverage | 21 |
| max expanded forms / coverage | 475 |
| truncated base coverages | 0 |
| truncated expanded coverages | 0 |
| source1-data enumeration complete | `true` |
| combined enumeration complete | `true` |

k512 相比 k128 恢复了被 cap 截掉的候选：

```text
additional retained source1-data recipes  50,376
additional active recipes                  50,129
additional exact CNF clauses            1,108,042
targets whose retained count changed            42
```

k512 资源记录：

```text
wall       49:31.01
user CPU   2964.22 s
system CPU 2.73 s
peak RSS   3,217,152 KiB
exit       0
AS limit   6 GiB
nice       5
```

后续远端任务已按新的运行纪律改用 `nice 10`；这一变化不回写或伪装 k512 已完成
证据中的实际 `nice 5`。

## 精确 CNF 形状；完整 solver 未运行

针对 `producer-tiered + seqcounter`，k512 estimator 给出：

| 指标 | 数值 |
|---|---:|
| active recipe variables | 5,347,773 |
| arrival variables | 20,530 |
| auxiliary variables | 5,594,290 |
| producer-cardinality auxiliaries | 5,353,522 |
| cost-cardinality auxiliaries | 240,768 |
| cost group variables | 7,329 |
| cost literals | 7,329 |
| dependency clauses | 73,924,429 |
| cost-link clauses | 15,969,129 |
| **CNF variables** | **10,969,922** |
| **CNF clauses** | **111,807,926** |

这些数值是精确形状统计，但没有把完整 CNF 送入 solver。完整模型禁止在 6 GiB
AS 下直接 solve，依据是冻结旧 all-268 streaming solve 的实测增量：

```text
old clauses                         11,524,738
old enumeration peak                1,456,688 KiB
old streaming solve peak            3,206,844 KiB
incremental solver memory            1,750,156 KiB
measured incremental cost           about 155 bytes/clause
```

把旧模型实测斜率外推到 111.8M clauses，再加 k512 已实测枚举状态，峰值约为
19--20 GiB。即使采用异常乐观的 32 bytes/clause，clause 数据约 3.33 GiB，
再加 3.07 GiB 枚举状态也已经超过 6 GiB hard AS limit。因此完整 streaming
solve 没有启动。

## 输出目标哈希映射与 S4 更正

输出 truth tables 已在 Ubuntu 用正式 helper 重新构造，并与 k512 的 268 个
`mixed_source1_data_bus2_per_target` rows 关联：

```text
mapping artifact SHA256
36e7c27636ea45da98864ee16e3ee2a8ef6432583d83e6e906da9834d5cb02de
```

| 输出 | zero-based index | one-based index | target SHA256 | recipes | valid drivers | coverages |
|---|---:|---:|---|---:|---:|---:|
| S3 | 154 | 155 | `305042da7ed6c69bafd65a205e38c082435feb1cfd794e6ee7c4cb0e362cb71a` | 5,212 | 10,322 | 442 |
| S4 | 164 | 165 | `aa7132ec12519729d20ec9de1aca0cabbc11e0797d194b8ef59fc7977ee2636e` | 57 | 19 | 4 |
| S5 | 177 | 178 | `64c2869f6c42902242640c16e04e9c7210e93cb19829e4c852572ce1bb15ae9c` | 2,268 | 5,665 | 211 |
| S6 | 184 | 185 | `b6c5c31c9168b72ee2b04d863ffa699f2ea34e1b4209d059d367763df9c0b2ad` | 0 | 0 | 0 |
| S7 | 197 | 198 | `55f1587c425fafce9acc17a3246bc96e3566ada66ffc2f1d5690a94b578995e8` | 0 | 0 | 0 |
| C8 | 236 | 237 | `1176fb00af2d4913384f90d90aaa4f34340a00fdb420c11db373bfc9462829cb` | 5,000 | 31,527 | 414 |

交接文本中的 S4 字符串
`aa7132ec125179d20ec9de1aca0cabbc11e0797d194b8ef59fc7977ee2636e`
只有 62 个十六进制字符，属于抄录错误，不能作为 SHA256 filter。正式重建后的
64 字符值是表中 `aa7132ec12519729...`，对应 zero-based index 164 / one-based
index 165。

## 单目标 shard 的证明边界

后续候选 hunt 允许保持旧 `source1-enable/base-data` 类的完整 all-268 profile，
同时只让新 `source1-enable/source1-data` 类命中一个声明 target。

- shard 为 SAT：构造使用的每条 recipe 都属于完整模型，因而 SAT witness 对完整
  模型全局有效；
- shard 为 UNSAT：只排除该受限 target 集合，不能外推为完整 268-target 新类的
  UNSAT；
- 多个单-target UNSAT 也不能直接合并为全局 UNSAT。

完整模型按“实际选中的 source1-data target 集合”分片在逻辑上可以做到互斥完备，
但成本 33、每个 BUS cost 4 仍允许至多 8 个 target，组合数
`sum(C(266,r), r=0..8)` 不可执行。当前单-target shard 只用于寻找全局有效的 SAT
候选，而不是建立全局下界。

截至本报告固定 k512 证据时，完整 111.8M-clause solve 从未运行。单目标 S4
受限候选片使用独立 run/spec/result 目录，不改变本报告的 enumeration-only 结论。

## 回归验证

本地与 Ubuntu 均通过以下精确性测试：

```text
source1-data 小域 brute-force 等价             250 cases
indexed old base-data vs full scan              250 cases
driver-form antichain                           500 cases
dependency-set antichain                        500 cases
seqcounter CardEnc matrix                     5,252 points
完整 estimator vs 实际 CardEnc                  200 random models
```

此外，后续 SHA256 filter 的独立测试验证了大小写归一、重复去除、精确选取以及非法/
不在 profile 中的 hash 拒绝；这些是 k512 完成后新增的 shard 工具测试，不属于
k512 执行输入。

## 核心证据与 SHA256

### k512 执行输入

```text
29fe5f40166844c3e30e83c7e22b9005712ef43f34ff00900f9ad9b4f7d5df16  search_phase_high_global_map.py
f26ac1c29ae9b9ea3aa1e553e9c808caa9f62afcd47ed2613818ee6a29c5ecdf  search_hub79_global_function_map.py
c967312c05285b8e121b1f5702d1715d07ffc89251f8c346b205d866fcfbde8e  hub33_high_function_library.py
bc9ec5cf68ad6ea56c9f482ffa08298e33d1c37c579c2ed62ad3b2f3d8de6e73  test_source1_data_mixed.py
61e4d1862086270704389d1ee0199f221e8ff51707b8cd860349df69af441f82  remote_all268_enumerate_k512_as6g_run.sh
f13744cc3a63697e65713fdd27d2c902f72262a3b63760face0f7b31c0cd5d63  remote_all268_enumerate_k512_as6g_spec.json
```

执行输入清单：

```text
K512_INPUT_SHA256SUMS.txt
SHA256 4804674b288df5a8fcd49be88d93c54d7df1665905fb5f7f40a78e32844e4307
```

精确文件内容另保存在
`evidence-k512-input-snapshot-29fe5f40/`。其中六个执行文件均再次按原清单逐项
核验成功；当前用于单-target shard 的工作源码与这份历史执行快照严格分离。

### k512 结果

```text
3cf1804d6e47cb803183f18048089b67399e4e72e028bd94349c90a5656be0e9  remote-all268-enumerate-k512-as6g/result.json
5234ab4ceb84246763fdc51ebae208e3d9413e5e8e58c6185d6cbac53db2cbac  remote-all268-enumerate-k512-as6g/stdout.log
5344c1e8ab48209edc89336263a73e41deef362cfdbafe7510d473546c422700  remote-all268-enumerate-k512-as6g/stderr.log
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  remote-all268-enumerate-k512-as6g/exit_code.txt
```

### k128 截断证据

```text
1881f430781162879488276cffa852839c7bf4bf02076e56d7db9a2a3b455c43  remote-all268-enumerate-k128-as6g/result.json
8601824d9fa89e3ac7d56b9f9e623b037db759faa958fe12f29a7276264d516c  remote-all268-enumerate-k128-as6g/stdout.log
04cf735a975c79375d25975b6c4675c215b1781db3109433f1cfd4812d58c41b  remote-all268-enumerate-k128-as6g/stderr.log
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  remote-all268-enumerate-k128-as6g/exit_code.txt
```

更完整的输入、运行、日志、资源摘要与报告哈希由同目录的精确 SHA256 manifest
统一固定。
