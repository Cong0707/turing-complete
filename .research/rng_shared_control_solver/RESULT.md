# RNG 共享控制模型的 233 门分层判定

日期：2026-08-03

## 结论

`.research/rng_switch_cover_next/search_shared_controls.py` 的 `bound=233`
之所以在 Z3 中返回 `UNKNOWN(timeout)`，不是因为这个边界接近可行点，而是因为原模型
一次性加入了 7356 个控制函数变量和方向选择，掩盖了一个更早就能判定的下界。

对完全相同的无抵消两层分区族，暂时把所有 AND/NOR 控制门视为免费，只保留：

```text
XOR2 数据核                 3 gate
Switch-XOR3 的四只开关      8 gate
AND/NOR 控制                0 gate（仅用于下界）
```

精确加权 MaxSAT 最优值为：

```text
第一层 XOR2              21
末层 XOR2                21
第一层 Switch-XOR3        7
末层 Switch-XOR3         10
Bit Switch               68

42 * 3 + 17 * 8 = 262 gate
```

因此完整模型的成本必然至少为 `262`，已经比 `233` 高 `29` 门；加入非负的
AND/NOR 控制成本只会继续增加。原 `shared_control_233.json` 可以从 `UNKNOWN`
收紧为该受限模型内的严格 `UNSAT`，无需构造完整控制层。

这不是任意多层三态网络的全局下界。允许抵消、Switch 输出继续驱动后续 Switch、
跨总线共享非线性控制或改变状态编码的路线仍然开放。

## 两套独立复核

主求解器 `solve_layered_rc2.py` 使用：

```text
精确一选：sequential-counter CNF
优化器：RC2
SAT 后端：Glucose4
结果：OPTIMUM 262
```

独立复核器 `verify_bound_pb.py` 不导入主求解器，重新生成 xorshift32 矩阵和全部
分区，并使用：

```text
精确一选：pairwise CNF
优化器：RC2Stratified
SAT 后端：Glucose3
结果：OPTIMUM 262
```

两者的矩阵散列均为：

```text
b05c6d821814fb084ee2ade6d742a4b91f9a9f749dcb313836469be43bd7e97f
```

两种最优网表的具体分区可以不同，但成本和宏数量下界一致；这是 MaxSAT 存在多个
等价最优模型的正常现象。

## 复现

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_shared_control_solver\solve_layered_rc2.py `
  --bound 233 `
  --output .research\rng_shared_control_solver\shared_control_bound233.json
```

求解器对该边界返回退出码 `20`，表示模型内不可满足。随后运行独立复核：

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_shared_control_solver\verify_bound_pb.py `
  .research\rng_shared_control_solver\shared_control_bound233.json `
  --output .research\rng_shared_control_solver\independent_verification.json
```

主求解器还可校验输出中的 262 门线性分区见证：

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_shared_control_solver\solve_layered_rc2.py `
  --verify .research\rng_shared_control_solver\shared_control_bound233.json
```

本轮没有启动游戏，没有读取或写入正式存档，也没有生成可冒充可用电路的候选。
