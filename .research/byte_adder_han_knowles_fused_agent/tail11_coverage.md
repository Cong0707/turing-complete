# 慢 C7：S7/C8 exact-cost-11 覆盖终态

## 结论与口径

截至 2026-08-04，在 `search_d6_paid_suffix.py --mode tail` 的当前精确模型内，
`S7/C8` 联合尾部的 **exact cost 11 全局 UNSAT**。这里的“全局”只指该模型的全部
合法 kind 分解和每个分片内的全部 CNF 模型，不是全局字节加法器下界。

模型固定以下边界：

- 当前慢 C7 paid-source 接口及其真实到达时间；
- `S7`、`C8` 两路输出 deadline 均为 6；
- 真实三态 Switch、resolved BUS 冲突约束和 physical-net partition；
- 每个 component 必须被后继或输出使用，禁止 dead component；
- 普通门成本 1、Switch 成本 2、XOR 成本 3。

因此，若 `components=n`、Switch 数为 `s`、XOR 数为 `x`，精确成本 11 等价于：

```text
n + s + 2*x = 11
s + x <= n
```

程序化枚举恰好得到 16 种合法分解：

| components | Switch | XOR | 终态 | 证据形式 |
|---:|---:|---:|---|---|
| 4 | 1 | 3 | UNSAT | 完整 CNF：`d6_tail_g11_n4_s1x3.json` |
| 5 | 4 | 1 | UNSAT | 完整 CNF：`d6_tail_g11_n5_s4x1.json` |
| 5 | 2 | 2 | UNSAT | 完整 CNF：`d6_tail_g11_n5_s2x2.json` |
| 5 | 0 | 3 | UNSAT | 完整 CNF：`d6_tail_g11_n5_x3.json` |
| 6 | 5 | 0 | UNSAT | 完整 CNF：`d6_tail_g11_n6_s5.json` |
| 6 | 3 | 1 | UNSAT | 完整 CNF：`d6_tail_g11_n6_s3x1.json` |
| 6 | 1 | 2 | UNSAT | 完整 CNF：`d6_tail_g11_n6_s1x2.json` |
| 7 | 4 | 0 | UNSAT | 完整 CNF：`d6_tail_g11_n7_s4.json` |
| 7 | 2 | 1 | UNSAT | 完整 CNF：`d6_tail_g11_n7_s2x1.json` |
| 7 | 0 | 2 | UNSAT | 完整 CNF：`d6_tail_g11_n7_x2.json` |
| 8 | 3 | 0 | UNSAT | 首批远端完整 CNF |
| 8 | 1 | 1 | UNSAT | 完整 CNF：`d6_tail_g11_n8_s1x1.json` |
| 9 | 2 | 0 | UNSAT | 首批远端完整 CNF |
| 9 | 0 | 1 | UNSAT | 六个 `slot0-kind` 互斥完备分片 |
| 10 | 1 | 0 | UNSAT | 六个 `slot0-kind` 互斥完备分片 |
| 11 | 0 | 0 | UNSAT | 五个 `slot0-kind` 互斥完备分片 |

## 分片完备性

执行快照中的 primitive kind 顺序为：

```text
NOT AND OR NAND NOR XOR SWITCH
```

编码对每个 component 的 kind 使用 `exactly_one`，而 `--slot0-kind K` 添加
`state["kinds"][0][K]` 的单位子句。因此，对同一 `(n,s,x)`，不同首槽 kind 分片
互斥；每个编码模型又必有且仅有一个首槽 kind。

精确 Switch/XOR 基数进一步给出三组完整并集：

| 分解 | 可行且已关闭的 slot0 kind | 被精确基数排除 |
|---|---|---|
| `(9,0,1)` | `NOT,AND,OR,NAND,NOR,XOR` | `SWITCH` |
| `(10,1,0)` | `NOT,AND,OR,NAND,NOR,SWITCH` | `XOR` |
| `(11,0,0)` | `NOT,AND,OR,NAND,NOR` | `XOR,SWITCH` |

`(9,0,1)` 的五个 ordinary 分片采用回收的远端 Glucose42 终态，`XOR` 分片采用
本机证书 `d6_tail_g11_n9_x1_slot0_xor_glucose42.json`。其余 11 个远端分片全部为
`completed/unsat/return_code=0`。这 17 个分片与 13 个完整 CNF 结果合成 30 个被选
证据对象，恰好覆盖全部 16 个成本分解。

历史文件 `d6_tail_g11_n8_s3.json` 是超时 `unknown`，未被计入；该分解由首批远端
完整 CNF 的严格 `UNSAT` 替代。本机另有一个重复的 `slot0=NOT` 严格证书，也未放入
一对一的被选分片集合。

## 证据与审计

首批两个完整 CNF 的原始 spec、依赖快照、日志、runner record、summary 和清单位于：

```text
.research/byte_adder_remote_compute/results/s7_c8_direct_tail11/
```

最后 16 个远端分片及覆盖审计位于：

```text
.research/byte_adder_remote_compute/results/s7_c8_direct_tail11_global_remaining/
```

关键锚点：

```text
executed spec SHA256  ba9c2b24306d682b1f1292fc39f65e29ac7812580172e3d6ca21c9b3edf4ccd8
executed script SHA256 27ec73e2fb3fa40c9e34dc48af8866ef2af3cf84514d301700c0d54ef3627b43
global summary SHA256 ac1e3540ca331a73d1ce953bf5b09048ad71817a0df8bbcdcae14ad84d0445af
remote archive SHA256 0bce967170c833c9c053c243fd40e03b88e478241e3841f67374c16a65e78be6
```

`audit_tail11_coverage.py` 对方程枚举、执行源码契约、两个远端 batch、逐项参数、
output/log 哈希、runner record、stdout、空 stderr 和最终覆盖集合做统一检查。终态：

```text
decomposition_count=16
covered_triple_count=16
selected_evidence_count=30
global_completed_unsat=16
missing=[]
non_unsat=[]
duplicate_partition=[]
errors=[]
```

## 范围限制

该结论只能表述为：**当前 paid-source、真实三态、BUS conflict、physical-net
partition、deadline=6、dead-component 约束的精确模型内，全局 exact-cost-11
S7/C8 joint tail 严格 UNSAT。**

它不是全局字节加法器下界，也不能自动外推为所有 `cost <= 11` 均 UNSAT；更低成本
需要按各自合法 kind 分解另行覆盖。此次工作没有启动游戏、读取或修改正式存档、修改
candidate/metadata，且没有部署任何候选。
