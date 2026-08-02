# 恒定 Seed、T=I 的深度边界

## 结论

研究对象固定为 32 个 Delay Bit、64 个原始输入 `(q,s)` 和纯二输入 XOR：

```text
F = A*q XOR (A+I)*s
Y = A*q XOR A*s
```

其中 `F` 是 32 位反馈，`Y` 是 32 位可见输出。`q_0=0`，Architecture Input
每拍保持同一个 seed，因此第一拍已经可输出 `A*s`，总周期为 65，不需要 ready Delay
或 NOT。

得到的严格边界如下：

| 条件 | 结果 |
|---|---:|
| `q -> 任一 F/Y` 的 XOR 深度 `<=2` | 不可能 |
| `q -> 任一 F/Y` 的 XOR 深度 `<=3` | 至少 80 个 XOR2 |
| 三层下界对应 gate | 至少 `160 + 80*3 = 400` |
| 三层下界对应 delay | 至少 `4 + 3*2 = 10` |
| 三层下界对应 energy | 至少 `400*10*65 = 260000` |
| 榜一参考 | `431*9*66 = 256014` |

即使假设 80 门下界恰好可达、seed 路径完全不增加延迟、Splitter/Maker/Architecture
I/O 全部免费，能耗仍比参考榜一高 `3986`。因此 **恒定 seed、`T=I`、32 Delay Bit、
纯 XOR2 这条路线不能超越 `256014`**。

深度大于等于 4 也不会翻转结论。64 个互异目标本身至少需要 64 个 XOR，故即使不计
任何中间门：

```text
gate  >= 160 + 64*3 = 352
delay >= 4 + 4*2    = 12
energy >= 352*12*65 = 274560
```

## 两层严格反证

自然 xorshift32 矩阵 `A` 的行权重为：

```text
weight 3:  5 rows
weight 4: 12 rows
weight 5:  3 rows
weight 6: 10 rows
weight 7:  2 rows
```

重行是位 `12..26`，共 15 行。每个 `F_i` 和 `Y_i` 的 q 投影都是同一个 `A_i`，
因此共有 30 个目标依赖 5 至 7 个不同 q 位。

二输入 XOR 的两层锥最多包含四个 q 叶子。seed-only 子网可以任意深，但它不能增加两层
q 锥能覆盖的 q 叶子数；重叠或抵消也不能产生第五个独立 q 输入。因此深度二在任意门数下
都不可能。

## 三层 80-XOR 下界

### 1. 64 个目标门

64 个 `(F,Y)` 行向量互异、都不是输入单位向量，并且 GF(2) 秩为 64。等价地，
`(q,s) -> (F,Y)` 是可逆线性变换，因为：

```text
s = F XOR Y
q = A^-1 * (Y XOR A*s)
```

所以每个目标都必须由一个不同的 XOR 输出产生，先有 64 门下界。

### 2. 重目标的父节点图

30 个重目标的 q 支持度大于 4，所以其 q 深度必为 3；它们不能再作为任何目标的父节点，
否则会形成四层 q 路径。

为了给下界最大限度放宽，定义可免费作为重目标父节点的集合 `E`：

```text
64 个原始输入 + 34 个轻目标 = 98 个信号
```

轻目标是否真的已经按正确拓扑顺序生成、深度是否真的不超过 2 都不检查，这只会让假想电路
更强。固定矩阵穷举得到两个证书：

```text
任意两个 E 信号的 XOR 都不是重目标
30*98 = 2940 个 H XOR e 全部互异
```

第二条意味着：任一非目标中间信号 `n` 最多只能与一个 `e in E` 配成某个重目标。
排序后的 2940 个 64 位值 SHA-256 为：

```text
6753e612cea828f27fc92ecf3a87c84539e10b8f8fd5bccf0057d622425aec14
```

现在把每个重目标的最终 XOR 看成一条边，两个父信号是端点，边标签是该重目标向量。
30 个重目标是 64 个目标基的一部分，彼此线性独立。若图中存在环，沿环 XOR 所有边标签，
每个端点出现两次而抵消，便得到非空重目标子集 XOR 为零，矛盾。因此该图是森林。

若有 `h` 个非目标中间节点：

```text
E--E 边数 = 0
N--E 边数 <= h
N--N 森林边数 <= h-1
```

要容纳 30 条重目标边，必须：

```text
30 <= h + (h-1)
h >= 16
```

合并 64 个目标门，得到严格下界：

```text
XOR2 >= 64 + 16 = 80
```

该证明允许任意扇出、任意 seed-only 深度、任意 XOR 抵消，并把所有轻目标提前免费开放；
所以不是特定 DAG 或贪心算法的下界。

## 294-XOR 可行上界

证书还构造了一份逻辑级上界，用于确认三层约束本身可满足：

```text
seed-only A*s：canonical 61 XOR
seed-only (A+I)*s：32 XOR
逐行 q/seed 合并：201 XOR
总计：294 XOR
```

逐行合并把每个 `A_i` 的 q 支持拆成：

```text
最多 4 位的共享 q-only 子树
剩余 0..3 位分别与 A*s、(A+I)*s 合并
最后并行生成 Y_i、F_i
```

逐门检查结果：

| 指标 | 数值 |
|---|---:|
| XOR2 | 294 |
| q XOR 深度 | 3 |
| seed XOR 深度 | 7 |
| 总 XOR 深度 | 7 |
| gate | `160 + 294*3 = 1042` |
| 预测 delay | `max(4+3*2, 7*2) = 14` |
| cycles | 65 |
| 预测 energy | `1042*14*65 = 948220` |

脚本从每个门的两个已存在父节点重建 64 位 GF(2) 标签，检查 64 个目标完全匹配；另对
69 个 seed 各运行 65 拍，检查 `Y=A^(t+1)s` 和 `q=A^(t+1)s XOR s`。这只是逻辑证书，
没有做物理布局，也没有写入正式存档。

## 复现

```powershell
python D:\Develop\Other\turing-complete\.research\rng_constant_seed_math\identity_depth_bounds.py

python D:\Develop\Other\turing-complete\.research\rng_constant_seed_math\identity_depth_bounds.py `
  --json D:\Develop\Other\turing-complete\.research\rng_constant_seed_math\identity_depth_certificate.json
```

产物 SHA-256：

```text
3999bf22f90d4fce60204f498dc59c512a5a70bf575f78ee6499ed7751c41c7a  identity_depth_bounds.py
b8240486bc1dfb2d5e31b364e27d1a9b2dab37aba6cb326be4d084999e808d20  identity_depth_certificate.json
```

JSON 固化全部 294 个门的父节点、64 位语义标签、q/seed/总深度、输出节点、成本和摘要。
