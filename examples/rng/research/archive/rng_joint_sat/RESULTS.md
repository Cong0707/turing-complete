# RNG init0 单输出联合 SAT/SMT 研究

## 结论

本轮没有得到 `3*XOR+OR <= 221` 的 32 位候选，也没有写正式存档或启动游戏。

新增两条互补、可复跑的求解路径：

1. `joint_weighted_search.py`：对每个给定的 32 位状态基，SAT 同时选择
   depth-2 pair cover、B 输出的 tick0 标签和不同 `(seed,state)` OR，直接约束
   `3*XOR+OR`，不再把 XOR 与 OR 拆成两个互不协调的预算。
2. `symbolic_joint_smt.py`：`T/B/C`、pair 字典、B/C 输出分解、tick0 标签和
   OR 映射全部是符号变量；可选有限 row-shear 基族，或保留任意可逆 `T` 的
   双线性矩阵约束。

两份脚本都只读 `.research` 代数模块，不导入存档写入器。

## 已验证结果

### 4 位完整符号 smoke

缩小变换为 `R1, L2, R1`，pair slots 取全部 `C(4,2)=6`，所以没有截断
第一层 pair 字典。模型独立选择了非平凡矩阵与共享网络：

```text
logic <= 14: SAT，证书为 3 XOR + 5 OR = 14
logic <= 13: UNSAT
```

`symbolic_n4_optimum.json` 的证书由纯 Python 重新检查：

- `C*T=A`、`T*C=B`；
- 每个 B/C 输出的 steady 分解；
- 每个 B 输出的 tick0 标签等于对应 T 行；
- 所有已使用 OR 映射存在；
- 全部 16 个 seed 各重放 9 拍。

这组 `SAT/UNSAT` 边界证明联合编码不是固定 `T` 的伪模型。

### 32 位已知 DAG 回归

用 `--fix-known-dag` 固定独立审计过的 61-XOR 拓扑，但仍由本模型求解所有
pin 标签和 OR 集：

```text
61 XOR + 47 OR = logic 230
166 + 230 = gate 396
```

SAT 用时约 0.1 秒，输出 `weighted_known_dag_230.json`；验证器重新检查矩阵、
逐门 tick0/steady 标签、成本和 6 个边界 seed 的 65 次输出。

### 32 位目标测量

严格限制 Z3 `max_memory=768MB`，未出现 OOM：

| 模型 | 范围 | 构建 | 求解 | 结果 |
|---|---|---:|---:|---|
| 任意符号 `T` | 30 pair slots，logic<=221 | 13.7s | 15.2s | unknown/timeout |
| 有限基族 | root + 5 个 radius-1 可行剪切，30 pair slots | 15.2s | 30.1s | unknown/timeout |
| 固定 root 的候选-pair SAT | 119 个相关 pair，logic<=221 | 0.8s | 15.0s | unknown/timeout |

这些 timeout 不是 UNSAT 证书。特别是任意 `T` 运行只允许最多 30 个第一层
pair；它覆盖当前最相关的 27--29 pair 区间，但不是所有理论上满足 logic 221
的拓扑。

## 当前瓶颈

完整符号模型已把原先每个输出约 41,448 个 support one-hot 选择压缩为：

- 有序且去重的 pair slots；
- 每个输出一个 `kind` 与至多两个 pair selector；
- 按首次出现计数的共享 final gate；
- 约 65K 个 `C*T=A`、`T*C=B` GF(2) 乘积项；
- 1024 个去重 OR 映射。

编码内存可控，但 32 位同时存在三类强对称：状态基、pair 字典、输出分解。
即使去掉矩阵双线性并只留 6 个基，30 秒仍不能判定，说明下一步应做
CEGIS/分层求解，而不是继续单纯延长单体 SMT timeout。

推荐的决定性下一节点：外层生成低 XOR 的 `T/B/C`，中层穷举或 SAT 枚举
pair cover，内层用已有 component 标签算法精确算 OR；只有中层产生新 cover
时才调用联合 SMT。真实目标始终保持：

```text
XOR=59 -> OR<=44
XOR=60 -> OR<=41
XOR=61 -> OR<=38
```

## 复现

快速重放已有证书：

```powershell
.\.venv\Scripts\python.exe .research\rng_joint_sat\verify_artifacts.py
```

重新求 4 位边界：

```powershell
.\.venv\Scripts\python.exe .research\rng_joint_sat\symbolic_joint_smt.py --bits 4 --logic-budget 14
.\.venv\Scripts\python.exe .research\rng_joint_sat\symbolic_joint_smt.py --bits 4 --logic-budget 13
```

32 位有限基族目标运行：

```powershell
.\.venv\Scripts\python.exe .research\rng_joint_sat\symbolic_joint_smt.py `
  --bits 32 --basis-radius 1 --pair-slots 30 --logic-budget 221 `
  --timeout-ms 30000 --memory-mb 768
```

32 位已知网络 smoke：

```powershell
.\.venv\Scripts\python.exe .research\rng_joint_sat\joint_weighted_search.py `
  --radius 0 --fix-known-dag --logic-budget 230 --timeout-ms 30000 `
  --memory-mb 512 --stop-on-sat
```
