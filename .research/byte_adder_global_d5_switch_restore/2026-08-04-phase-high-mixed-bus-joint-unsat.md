# Byte Adder D5 高位窗口：source1 mixed BUS 与 base BUS 联合结果

## 结论

本轮没有找到 `<=102/5` 的 SAT 构造，也没有物化 candidate。

本目录中最强的已完成结论，是下面这个明确声明模型内的严格**局部 UNSAT**：

```text
固定 integrated shell                     69 gate
S3..S7/C8 高位窗口上界                    33 gate
-------------------------------------------------
完整计费上界                             102 gate / D5
```

该模型同时包含 source1-residual 函数扩展、base 函数宇宙内所有保留的严格
BUS2 配方，以及针对完整 base BUS2 枚举中全部 268 个 target 的 mixed BUS2
类。这个结果不是任意 Byte Adder 电路的下界，也不覆盖所有 expanded-universe
Switch 拓扑。

主结果：

```text
remote-all268-stream-solve-as6g/result.json
SHA256 f2918c03be90ba93b403e76da745a65ab80a8afb7fa97fdb48c7e77b4df38bd8
status unsat
```

此前 94-target Hub33 network-functions 与 23-target witness-controls 联合 UNSAT
仍作为较窄基线保留：

```text
remote-hub33-network-stream-solve-as6g/result.json
SHA256 97f63fc3cdfc4eea6344b62ce78d3f79d3938cbcaa9d4a478491e80efb1b64fa
status unsat

remote-integrated-g33-mixed-plus-basebus-tiered-as6g/result.json
SHA256 0f8336f6bc11422fe7dae4d94158b833ff05432a59503f2656a1a4c1577b9e9e
status unsat
```

## 精确模型

真值域覆盖 `A[7:0]`、`B[7:0]` 和 `Cin` 的全部
`2^17 = 131072` 组赋值。六个必需输出为 `S3,S4,S5,S6,S7,C8`，截止层为 D5。

付费计数和候选词汇如下：

```text
mode                                      integrated-nc7
固定付费 gate                             69
base 函数                                 270
source1 函数                              6394
新增 source1 函数                         6230
联合函数宇宙                              6500
ordinary 配方                             35700
原始 Hub79 BUS 配方                       18
```

规范的七 gate `S1/S2` 见证已经计入固定的 69 gate。冻结的 `S3/S4`、
`S7/C8` 见证中间函数以及 Hub33 Switch 输入函数仅作为付费候选词汇存在，
并不是免费 source。

### Base BUS2 类

两个 Switch driver 的 `enable,data` 函数都来自 270 函数的 base 宇宙。
每个 driver 在自己 enable 的全部真值行上与目标一致，两个 driver 的
one-coverage 联合覆盖目标，因此重叠行不可能分别驱动 0 和 1。

```text
存在 BUS2 的 target                        268
保留配方                                  11768
单个 coverage 的最大 driver form 数          55
max_per_coverage                            128
发生截断的 coverage                           0
枚举完整                                  true
```

### 定向 mixed BUS2 driver 类

一个 Switch 使用 base enable/base data driver；另一个 Switch 使用 expanded
source1 enable/base data driver。expanded enable 必须在尚未加入 mixed BUS
配方的模型中于 D4 前可达。23-target 基线把产出限制在
`witness-controls` 函数内；最强结果把 target 扩展到后文定义的 94 个
`hub33-network-functions` 去重函数。

```text
scope       one-base-driver + one-source1-enable/base-data-driver
target 数                                    23
D4 可达的 expanded enable                  6030
保留配方                                  64846
单个 coverage 的最大 expanded form 数        99
发生截断的 base/expanded coverage            0 / 0
max_per_coverage                            128
枚举完整                                  true
```

这里的 D4 enable 数量高于 mixed-only 运行，是因为完整 base BUS 配方能够更早
重算一部分付费 source 函数；这些更早的到达时间使更多一 gate source1 enable
可用。权威数据来自最终 `result.json`，而不是运行前 `spec.json` 中的估算值。

## SAT 编码

所有输出共享函数节点；每个 Boolean 函数至多选择一个 producer。ordinary 节点
和 BUS 节点即使被多个输出复用，也只计费一次。

`producer-tiered` 与旧 `expanded/grouped` gate 成本编码严格等价：因为每个
target 函数至多选择一个 producer，函数 materialized literal 支付基础 1 gate，
cost=`c` 的已选配方恰好强制 surcharge tier `2..c`。这样无需为同一 target
的每个 cost-four BUS 配方重复展开三个 surcharge literal。

回归证据：

```text
Hub79 no-new-BUS: 143/D5 UNSAT, 144/D5 SAT
Hub79 full BUS2:  102/D5 UNSAT, recipes/candidates = 5221/5038

Hub79 full BUS2 grouped CNF: 540521 vars / 1127341 clauses / 31.78 s
Hub79 full BUS2 tiered CNF:    69946 vars /  186191 clauses /  4.26 s
```

为避免在 7M-clause 扩域模型上同时保留 Python CNF 和 solver 内部副本，后续
mapper 支持把完全相同的子句按原顺序直接送入 solver。streaming 与 materialized
做了两类等价回归：

```text
integrated/no-BUS 33/D5:
  两者均 UNSAT
  30089 vars / 113856 clauses / 348 cost literals
  三项均与独立 shape estimator 完全一致

Hub79 no-new-BUS 144/D5:
  两者均 SAT，且得到相同 75-node witness
  144 gate / D5，完整 2^17 重放和 BUS conflict 检查通过
```

streaming 只改变子句存放位置，不改变变量分配、子句集合、cost 编码或 solver。

23-target 基线的联合高位窗口求解规模：

```text
配方 / active candidate                    112332 / 96822
cost literal                               7325
CNF variable / clause                      467883 / 1907290
solver                                     cadical195
solver result                              UNSAT
solver section                             47.21 s
远端 wall time                             4:50.73
远端 maximum RSS                           1799416 KiB
```

## 核验

下载后重新核对了结果文件以及八个脚本、电路和见证依赖的哈希。base BUS 与
mixed BUS 枚举都报告零 coverage 截断，实测最大 form 数也均小于
`max_per_coverage=128`。配方账本严格对齐：

```text
35700 ordinary + 18 original + 11768 base BUS + 64846 mixed BUS = 112332
```

较早的 1536 MiB 远端运行以 `std::bad_alloc` 和 exit 134 终止，没有生成
`result.json`，只能分类为 `unknown-resource-limit`，不能视为 UNSAT。随后
4 GiB mixed-only 运行证明了不含独立新 base BUS2 的更窄模型 UNSAT；最终
6 GiB 联合运行正常完成，exit 0 且 stderr 为空。

精确输入快照与上传 bundle 分开保留：

```text
evidence-input-snapshot-a4c621db/
remote-tiered-bundle.tar
bundle SHA256 a4c621dbaaca525de604f931fd7cfff902480d415cd67fe69736367b740ca015
```

## Hub33 network-functions 扩域与精确 UNSAT

在上述 23-target 结论之后，又定义了一个更贴合公开 Hub33 切片的定向 profile。
它取全部 Hub33 resolved `net` 函数和真实 Switch `enable/data` 别名，与
`S3..S7/C8`、`C5..C8/nC5..nC8` 及已有 witness controls 合并后按真值函数
去重。Hub33 导出的 84 个 distinct 函数全部被覆盖，最终得到 94 个 mixed
target。

只枚举结果：

```text
remote-hub33-network-enumerate-as6g/result.json
SHA256 1b0f11db379d7029b4bd9a4cde1676a1c76c27acbc5be7f38ae328b494077a7a
status                                    enumerated
mixed target                              94
存在 mixed 配方的 target                  93
D4 可达的 expanded enable                6030
mixed raw dependency set                 1015663
保留 mixed 配方                           353377
base/expanded 最大 form 数                21 / 103
base/expanded coverage 截断               0 / 0
mixed 枚举完整                            true

总配方 / active candidate                400863 / 360408
cost literal                              7329
预测 CNF variable / clause               995191 / 7013427
wall time                                 15:31.63
maximum RSS                               1321624 KiB
exit                                      0
stderr                                    empty
```

独立 base BUS2 仍为 `11768` 条配方、268 个 target、最大 55 forms、零截断。
94 个 target 中唯一没有 mixed 配方的是常量 0；它已经是免费 source，枚举器按
定义跳过 `target == 0`，因此 `93/94` 不是 coverage 缺口。
完整配方账本再次严格对齐：

```text
35700 ordinary + 18 original + 11768 base BUS + 353377 mixed BUS = 400863
```

上述 enumeration-only 文件只证明枚举完整性并给出精确 CNF 规模估算，
**自身不证明 SAT 或 UNSAT**。
枚举使用的 mapper SHA256 为
`e0e4c3fd12b58eaf2f0a392e40407c6d3c560ce0e1384269298e1e63b7078fd5`。

随后在相同 94-target 函数宇宙和 driver 类上运行 streaming 精确求解：

```text
remote-hub33-network-stream-solve-as6g/result.json
SHA256 97f63fc3cdfc4eea6344b62ce78d3f79d3938cbcaa9d4a478491e80efb1b64fa
status                                    unsat
cnf_storage                               streaming
cost literal                              7329
CNF variable / clause                     995191 / 7013427
solver                                    cadical195
solver section                            110.10 s
solver restarts / conflicts               19 / 1185
remote wall time                          15:17.68
remote maximum RSS                        2267148 KiB
exit                                      0
stderr                                    empty
```

精确求解重新枚举出的全部统计与 enumeration-only JSON 逐字段一致；实际
`cost_literal_count`、`cnf_variables`、`cnf_clauses` 也分别与独立 estimator 的
`7329`、`995191`、`7013427` 完全一致。下载后再次核对结果 SHA、输入脚本 SHA、
配方账本、零截断状态和 run spec，交叉审计通过。求解使用的输入 SHA256：

```text
phase mapper    c21415fe042de9513efbe66fdf38cac2311f7352b8813f105a3067b8583d4936
global core     f7f46b84a265cd7deb8a028b812a82f20e8a9de3067ad96bb3d7cad7d8388b2e
Hub33 library   c967312c05285b8e121b1f5702d1715d07ffc89251f8c346b205d866fcfbde8e
```

上述 streaming 输入也保存在独立快照中：

```text
evidence-streaming-input-snapshot-c21415fe/
```

本报告、各层结果、失败证据、run spec、输入快照、回归 JSON、witness 和 Hub33
电路的完整 137-file 哈希清单见 `SHA256SUMS.txt`。

## All-268 mixed target 规模与精确 UNSAT

在 94-target 精确 UNSAT 后，将 mixed target 扩展到完整 base BUS2 枚举中所有
268 个 target。driver 类型保持不变，仍然是一个 base enable/base data driver
加一个 source1 enable/base data driver；这一步没有扩展 data 位置或 source 层级。

```text
remote-all268-enumerate-as6g/result.json
SHA256 41505d38bd54bd7b1aa7eb8afbf3974f2dfab9e26456e09d0970041fb92041fd
status                                    enumerated
mixed target                              268
存在 mixed 配方的 target                  266
D4 可达的 expanded enable                6030
mixed raw dependency set                 1764556
保留 mixed 配方                           620908
base/expanded 最大 form 数                21 / 103
base/expanded coverage 截断               0 / 0
mixed 枚举完整                            true

总配方 / active candidate                668394 / 622880
cost literal                              7329
预测 CNF variable / clause               1520136 / 11524738
wall time                                 22:10.80
maximum RSS                               1456688 KiB
exit                                      0
stderr                                    empty
```

独立 base BUS2 仍为 268 target、`11768` 条配方、最大 55 forms、零截断。
配方账本严格对齐：

```text
35700 ordinary + 18 original + 11768 base BUS + 620908 mixed BUS = 668394
```

这个 enumeration-only 文件自身仍不证明 SAT 或 UNSAT；它只证明所声明 268
target/driver 类的枚举未被 `max_per_coverage=128` 截断，并给出精确 CNF sizing。

随后用相同输入和 streaming CNF 完成精确求解：

```text
remote-all268-stream-solve-as6g/result.json
SHA256 f2918c03be90ba93b403e76da745a65ab80a8afb7fa97fdb48c7e77b4df38bd8
status                                    unsat
cnf_storage                               streaming
cost literal                              7329
CNF variable / clause                     1520136 / 11524738
solver                                    cadical195
solver section                            184.60 s
solver restarts / conflicts               25 / 1417
remote wall time                          27:05.09
remote maximum RSS                        3206844 KiB
exit                                      0
stderr                                    empty
```

精确求解重新枚举出的所有统计与独立 enumeration-only JSON 逐字段一致；实际
`cost_literal_count`、`cnf_variables`、`cnf_clauses` 与 estimator 的对应值完全
一致。下载后对结果 SHA、三份输入脚本 SHA、配方账本、零截断状态和 run spec
再次交叉核验，全部通过。

## 严格边界

该 UNSAT 结果**不覆盖**：

- 把新增 source1 函数作为 mixed BUS target，或 268 个 base-BUS target 以外的
  其他 target；
- mixed driver 的 data 位置使用 source1 函数；
- 同一个 BUS 同时使用两个 mixed/expanded driver；
- source2 或不受限的 ordinary-function closure；
- 把多输出 Hub33 Custom activation 作为一个付费 bundle；
- 本 function-map 模型以外的任意物理高位窗口网络。

因此，这些结果不能支持修改正式存档，也不能声称全局 `102/5` 下界。
source1-data 位置、同一 BUS 的两个 mixed driver 和 source2-enable 属于仍未
覆盖的维度，应分别做最小增量。不能把当前 all-268、
source1-enable/base-data driver 模型的 UNSAT 外推到这些更宽模型。
