# RNG 自然态两层核心下界

日期：2026-08-02

## 结论

固定 `32 Delay + U32 Word Switch + ready/NOT = 230 gate` 后，榜一
`431/9/66` 只剩 `201 gate / 4 delay`。若组合核直接计算自然态
`xorshift32`，并只允许普通 XOR2 与已公开验证的 Switch-XOR3，即使允许
首层形式在末层任意抵消，组合核也至少需要：

```text
216 gate
```

所以这类完整 RNG 至少为 `230 + 216 = 446 gate`，不能解释 `431/9/66`。
这不是任意 Switch 网络的全局下界；它不覆盖联合状态编码、相位复用，或不封装为
XOR3 的一般多层三态网络。

## 证明骨架

自然变换的输出支持度分布为：

```text
weight 3:  5
weight 4: 12
weight 5:  3
weight 6: 10
weight 7:  2
```

十个 weight-6 输出在 GF(2) 上线性无关。设其中 `k` 个不用末级 XOR3，
那么它们只能是两个首层 XOR3 形式的 XOR2。`m` 个首层三元形式的两两差
最多张成 `m-1` 维，因此 `m >= k+1`。

两个 weight-7 输出都必须使用末级 XOR3。它们的支持集只相交一位，所以只用
一个首层三元形式无法同时补足两者，首层 XOR3 至少有两个。结合剩余
`10-k` 个 weight-6 末级 XOR3，可得相关 XOR3 总数的完整分支下界。

另外，12 个 weight-4 与 3 个 weight-5 输出都必须有末级门。只要仍有一个
weight-5 使用末级 XOR2，就还必须付至少一个首层 XOR2 生成三元加二元分解中的
二元源。

旧版证明在这里漏计了 5 个 weight-3 输出。已经计费的首层 XOR3 至多直接产出
其中同样数量的输出；剩余输出各自至少还要一个末级门。为保持下界乐观，每个
只按最便宜的 `3 gate` XOR2 计费。于是 `k=0..4` 的最小值依次为
`225, 216, 216, 216, 216`，后续分支只会更高。对 `k=0..10` 及所有额外
末级 XOR3 分支逐项取最小值，修正后的最优下界为：

```text
13 Switch-XOR3 + 20 XOR2
= 13*12 + 20*3
= 216 gate
```

## 复现

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_public_hunt\prove_natural_depth2_lower_bound.py
```

证书输出：

```text
.research/rng_public_hunt/natural-depth2-lower-bound.json
```

脚本会重建关卡矩阵、核对十个 weight-6 行的秩、核对两个 weight-7 行的
交集，并枚举全部成本分支。本轮未启动游戏、未接触正式存档、未使用 RAM。
