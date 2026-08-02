# RNG 反馈周期基变换：61 XOR2 证书

## 结论

找到一套不改变 `xorshift32(13,17,5)` 输出序列、但把寄存器反馈路径压到两层 XOR2 的线性构型。

```text
P = I + R17 = P^-1
B = P A P
T = P A
```

物理 XOR 网络分成两个块：

| 块 | 用途 | XOR2 | 最大 XOR 深度 |
|---|---|---:|---:|
| `P` | 首拍 seed 预处理；运行拍输出解码 | 15 | 1 |
| `B` | 首拍编码态形成；运行拍寄存器反馈 | 46 | 2 |
| 合计 | 两块均按多输出共享综合 | **61** | 反馈为 **2** |

运行时反馈路径是 `q -> phase selector -> B -> register`，所以经过至多两层 XOR；Selector/Switch 另计一层。首拍初始化路径是 `seed -> P -> selector -> B -> register`，会经过三层 XOR，但它不在寄存器反馈环内。

本目录只给出矩阵和逐门 SLP 证书，没有修改正式存档，也没有启动游戏。Selector 的具体游戏元件布局、成本和静态延迟仍应在上层电路实现时单独验证。

## 时序等价性

首拍让 `P(seed)` 进入 `B`：

```text
q_1 = B P seed
    = P A P P seed
    = P A seed
```

其后每个输出拍：

```text
output_n = P q_n = A^n seed
q_(n+1)  = B q_n = P A^(n+1) seed
```

这里使用了 `P^2=I`。因此首拍不输出，随后 65 拍依次输出 `A seed` 到 `A^65 seed`，与关卡的自然状态序列完全一致。

`P` 块需要两个相位连接：输入在首拍取 seed、之后取 q；它的输出首拍送到 `B` 输入、之后送到关卡输出。`B` 输入首拍取 `P(seed)`、之后直接取 q。这种连接没有组合环；运行反馈绕过 `P`。

## 门级证书

`P=I+R17` 的 15 个门为：

```text
p_i = u_i XOR u_(i+17),  0 <= i < 15
```

其余 17 个输出直通。

`B` 的行权重分布为：

```text
weight 2: 13 rows
weight 3:  7 rows
weight 4: 12 rows
```

所以二层 XOR2 足够。证书中的 `B` 网络包含：

```text
13 个本身就是 B 输出的第一层 pair
14 个额外第一层 pair
19 个第二层最终输出
= 46 XOR2
```

对固定矩阵 `B`，任一深度不超过二的 XOR2 网络都可规范化为“输入 pair + 最终合并”。每个互异非直通输出至少占一个门；权重 3/4 输出还必须由可用 pair 覆盖。`--prove-minimum` 建立完整的 pair-cover 优化问题并证明额外 pair 的最小数是 14，因此固定 `B` 的 46 门也是最小值。`P` 的 15 个互异权重 2 输出各自至少需要一个门，所以在这两个相位分离块的构型内，`15+46=61` 是精确门数。

这不是对任意状态基、任意带模式选择的全局 61 门最优性证明。

## 自然状态反证

自然矩阵 `A` 的输出行权重为：

```text
weight 3:  5 rows
weight 4: 12 rows
weight 5:  3 rows
weight 6: 10 rows
weight 7:  2 rows
```

两层 XOR2 的一个输出最多依赖 4 个独立输入，因此自然状态下 15 个权重大于 4 的输出严格排除了任何纯 XOR2 两层实现；增加门数也不能消除这个支持度障碍。上述 `P` 基变换正是绕过该反证的关键。

## 证书文件

- `certificate.json`：`A/P/T/B/C` 的全部 32 行十六进制矩阵、61 个门及输出引用。
- `verify_certificate.py`：自包含矩阵、逐门、深度和 65 拍序列验证器。
- `search_short_basis.cpp`：单进程、常量级矩阵内存的短基程序搜索器；保留了未达到 61 门构型的搜索前沿作为路线对照。

标准库验证：

```powershell
python .research/rng_cycle_basis/verify_certificate.py
```

同时重证固定 `B` 的二层 pair 下界：

```powershell
python .research/rng_cycle_basis/verify_certificate.py --prove-minimum
```

预期输出：

```text
Z3: B needs exactly 14 non-output pair nodes
verified: 61 XOR2 total; P=15@d1; B=46@d2
certificate sha256: e2318d3955336538de7b58f45585c5cb4267bc93ad5565842a5838b7736f4fd9
```
