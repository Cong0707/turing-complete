# RNG radius 14 任意非最小 cover 联合审计

## 结论

radius 14 的 128 个 `x56` 状态编码，在本轮精确模型中全部为 UNSAT。没有找到
无 RAM、真实 XOR2/Switch-Z 成本、可达到 `387/10/66` 的电路证书。

这比此前的 386 个最小 pair cover 审计更强：本模型不预先固定最小 cover，而是在
同一个 CNF 中联合选择所有可能真正参与输出的非最小 pair、低权反馈行的 mediated
实现、每个 XOR 引脚的 seed 标签和方向，以及最终 `(seed,state)` OR 映射并集。

严格预算为：

```text
总门数 = 166 + 3 * XOR2 + OR
3 * XOR2 + OR <= 221
目标 <= 387 / 10 / 66
```

`387/10/66` 的能量为 `255420`，低于公开参考 `431/9/66 = 256014`，因此只要模型
返回 SAT 就足以形成新的正常开关前沿。本轮结果为 `128 UNSAT / 0 SAT / 0 UNKNOWN`。

## 覆盖范围

- 输入：`radius14-x56-neighbors.jsonl` 全部 128 条唯一矩阵；
- weight-3/4 行：枚举全部合法深度二分解；
- B weight-1/2 行：允许 direct 和全部同函数 mediated 实现；
- pair：联合选择全部会被上述实现实际使用的 pair，包括非最小 cover；
- 相位：逐 pair、逐 seed 精确选择标签和两个物理引脚方向；
- OR：对真实使用的 `(seed bit,state bit)` 映射取精确并集；
- XOR2 按 `3 gate / 2 delay`，OR 按 `1 gate / 1 delay`；
- 无拓扑数量上限、无 component/global beam、无抽样、无 RAM。

第一轮 Minisat22 在 60 秒限时内完成 124 条，4 条返回 UNKNOWN。第 42、53、75、117
条随后由 Glucose4 在相同 `mtotalizer` 编码下全部证明 UNSAT，因此最终不存在未决项。

## 证据与复算

关键文件：

```text
.research/rng_x56_or10_exact/joint_mediated_sat.py
.research/rng_x56_or10_exact/consolidate_radius14.py
.research/rng_x56_or10_exact/radius14-joint-mediated-unsat-complete.json
.research/rng_word_residual_search/radius14-x56-neighbors.jsonl
```

统一清单由下列命令生成；脚本会重新计算 128 个 `T_sha256`、检查行号恰好覆盖
`1..128`、拒绝任何 SAT/UNKNOWN 项，并记录每个 CNF 的 SHA-256：

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_x56_or10_exact\consolidate_radius14.py
```

模型还用已知可行的 `61 XOR + 47 OR = 230` 实例做过正向控制，证书回放及
`256 seeds x 65 ticks` 均通过，见 `known-feasible-230-kmt-certificate.json`。

## 边界与下一步

本结论排除的是这 128 个状态编码及所定义的深度二 XOR2/Switch-Z 拓扑，不是对所有
开关电路的全局不可能性证明。下一步不应继续枚举这些编码的 cover，而应改变至少一项：

1. 搜索 radius 14 以外、具有更低联合 `3*XOR+OR` 的状态编码；
2. 允许三层或更深、能够跨输出共享中间节点的 XOR DAG；
3. 使用不同状态维数或合法跨拍重定时；
4. 直接优化联合成本，而不是继续只优化 `x56` 的最小 cover 数。

本轮没有启动游戏、没有读取或修改正式存档、没有使用 RAM。
