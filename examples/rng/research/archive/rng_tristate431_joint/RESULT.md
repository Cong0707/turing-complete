# RNG 单侧三态隔离复核

## 结论

固定 `rng_encoded_asic.py` 的 `T/B/C` 与 61 个二输入 XOR DAG，在修正 EARLY
源约束后可满足目标成本：

```text
seed 侧：每个 seed_i 至多属于一个独立 EARLY 网
q 侧：q_j 可扇出到多个独立 Bit Switch 输入

32 EARLY * Bit Switch cost 2 = 64
18 LATE  * OR cost 1         = 18
phase cost                    = 82

32 Delay Bit                 = 160
61 XOR2                      = 183
ready + NOT                  =   6
总成本                        = 431
```

精确 `32 EARLY + 18 LATE` 为 SAT，纯 Python verifier 已重建 32 个装载标签并
验证它们逐位等于 `T(seed)`；稳态 DAG 不变，所以反馈与输出仍分别为 `B(q)` 和
`C(q)`。

这不是当前游戏可直接安装的物理证书。Architecture Input 只有一个 U32 三态输出，
而模型把各 `seed_i` 当作已经可用的 U1 三态源。当前 Splitter32/Splitter8 不传播 Z，
所以无法零成本提供这些 U1 源。SAT 结论的准确含义是：**若存在保持 Z 的 U32-to-U1
seed breakout，则固定 DAG 可达到该成本。**

## 精确 431 证书

EARLY 物理配对：

```text
s0-q22   s1-q23   s2-q19   s3-q20   s4-q26   s5-q22   s6-q28   s7-q29
s8-q25   s9-q31   s10-q27  s11-q28  s12-q29  s13-q30  s14-q31  s15-q24
s16-q16  s17-q17  s18-q18  s19-q2   s20-q25  s21-q21  s22-q27  s23-q23
s24-q24  s25-q30  s26-q26  s27-q15  s28-q16  s29-q0   s30-q1   s31-q2
```

q 侧重复是有意且物理上可隔离的：同一个 q 只连接多个 Switch 输入，各 Switch 输出
属于不同的 EARLY 三态网。32 个 seed 恰好各使用一次。

LATE OR 物理配对：

```text
s15-00008008  s17-00000021  s18-00000042  s18-00004000
s19-00008008  s20-00000108  s21-00000210  s22-00000420
s23-00000840  s24-00001080  s25-00002100  s26-00004200
s27-00000400  s28-00000800  s29-00001000  s30-00002000
s31-00000042  s31-00004000
```

完整机器可读证书位于 `seed_isolated_exact32_late18.json`，其中包含：

- 32 条 EARLY occurrence；
- 18 条 LATE pair、18 条内部 LATE occurrence、12 条最终 LATE occurrence；
- 32 行编码矩阵 `T`；
- 32 个反馈引用 `B` 与 32 个输出引用 `C`；
- 全部 61 个 XOR 的 `output/left/right/depth` 门表。

相同 `(seed,node)` 的 LATE OR 可以扇出，因此 occurrence 数量大于物理 OR 数量。

## 更低模型成本

不固定 EARLY/LATE 个数时，同一模型还得到：

```text
budget 82: 30 EARLY + 22 LATE = 82
budget 81: 30 EARLY + 21 LATE = 81
budget 78: 30 EARLY + 18 LATE = 78
exact EARLY=32, LATE<=18: 32 EARLY + 17 LATE = 81
```

因此 `431` 不是这个条件性代数模型的最小值；它甚至预测 `427/9/66`。这进一步说明
该模型不能单独解释真实榜首，遗漏的 U32 seed breakout 物理成本是决定性边界。没有对
`phase cost <= 77` 给出 UNSAT 证明。

## 时序证书

```text
EARLY seed:  ready Delay 4 + NOT 1 + XOR 2 + XOR 2 = 9
EARLY state: ready Delay 4 + Switch 1 + XOR 2 + XOR 2 = 9
LATE seed:   ready Delay 4 + NOT 1 + OR 1 + <=1 XOR 2 <= 8
LATE state:  q Delay 4 + XOR 2 + OR 1 + XOR 2 = 9
```

每个 LATE OR 的另一输入在装载拍标签严格为零，且 OR 后最多剩一层 XOR。

## Verifier 检查项

`solve_seed_isolated.py --verify-existing` 不依赖 Z3 model 对象，检查：

- JSON 中的 `T/B/C` 与当前固定证书完全一致；
- 61-XOR 门表与当前 DAG 完全一致；
- EARLY/LATE pair 集与 occurrence 实际使用集严格相等；
- seed 侧 pair 唯一，q 侧允许重复；
- LATE 的 base load 标签严格为零；
- 32 个反馈装载标签逐位等于 `T(seed)`；
- phase 计数、预算和四类最长路径。

## 复现

精确 `32+18=82`：

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_tristate431_joint\solve_seed_isolated.py `
  --budget 82 --exact-early 32 --exact-late 18 --timeout-ms 180000 `
  --output .research\rng_tristate431_joint\seed_isolated_exact32_late18.json

.\.venv\Scripts\python.exe `
  .research\rng_tristate431_joint\solve_seed_isolated.py `
  --verify-existing `
  .research\rng_tristate431_joint\seed_isolated_exact32_late18.json
```

模型内 `78`：

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_tristate431_joint\solve_seed_isolated.py `
  --budget 78 --timeout-ms 180000 `
  --output .research\rng_tristate431_joint\seed_isolated_78.json
```

Z3 `max_memory` 固定为 640 MB，低于本任务的 768 MB 单进程上限。本轮没有启动游戏，
没有读取或写入正式存档，也没有修改候选电路。

## SHA-256

```text
BEE824A02F0E9BCEF42010EEBE50AEB980670FC8B802F373462FB0D0ED0772C5  solve_seed_isolated.py
F4068CC868C8B405B7106B6EB6610EE98271DEDCE118610C00B9378E05DD57C3  seed_isolated_exact32_late18.json
AEC3917A071E80625D94D0E5027604334DB7630826A237FA9EFF144177A380C8  seed_isolated_78.json
DD586EE48CD8EEDD21EFA8BC0F0581D30534F8D3264822B6CB801BF45ADD6483  seed_isolated_exact32_max18.json
```
