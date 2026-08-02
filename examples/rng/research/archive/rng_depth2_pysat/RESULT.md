# RNG 自然态二层混合异或网络精确搜索

## 2026-08-02：完整 cancellation-aware SAT 结论

### 结果

在下列**完整且明确限定**的电路空间内，primitive cost `<= 201` 为
`UNSAT`：

- 状态是自然态 32 位 `xorshift32`；
- 第 1 层允许任意原始输入的 XOR2 或 XOR3；
- 每个输出可以直接使用第 1 层结果，或由原始输入/第 1 层结果再经过
  一个 XOR2 或 XOR3；
- XOR2 成本为 3，公开三态构型 XOR3 成本为 12；
- 第 1 层结果可跨输出共享且只计费一次；
- 线性形式使用位掩码做异或，完整允许公共输入抵消，不是
  cancellation-free 近似。

因此，`55 XOR2 + 3 XOR3 = 201` 只是一个成本分解，不能在这个自然态
depth-2 空间中实现目标矩阵。正式路线不应继续把 201 预算押在“纯
XOR2/XOR3、自然态、二层”这个假设上。

这不是对整个 RNG 关卡的不可行性证明。它不覆盖 Switch/Z 总线、同值多
驱动、非线性门、状态重编码、额外逻辑层或样本特化。

### 精确模型

目标函数逐列运行：

```python
x ^= x >> 13
x ^= x << 17
x ^= x >> 5
```

目标矩阵指纹：

```text
b05c6d821814fb084ee2ade6d742a4b91f9a9f749dcb313836469be43bd7e97f
```

搜索域和最终 CNF：

```text
原始输入                         32
全部候选第 1 层形式            5456
约简后实际引用第 1 层形式      5235
唯一 DNF requirement term     71649
SAT 变量                      324422
SAT 子句                      968092
固定成本（除以 3）                20
可变成本上限（除以 3）            47
```

每个输出门的所有无重复输入组合都被枚举；候选源的位掩码异或必须等于该
输出行。只执行了两种严格保成本约简：

1. 同一输出 arity 下，如果 requirement 是另一项的严格超集，则删除超集。
2. 一个最终 XOR3 项若能增加至多 9 成本的第 1 层形式改为 XOR2，则删除该
   XOR3 项。最终门节省恰好 9，保留旧形式只会使替换成本更宽松，因此不会
   删除成本更优的解。

门成本均为 3 的倍数。`<=201` 不可满足意味着此模型的下一个可能成本至少
为 204。补充边界实验中，同一编码在 204 和 240 也返回 `UNSAT`，即该模型
的真实下界至少为 243；核心任务所需的 201 结论另由两个求解器独立确认。

### 交叉验证

无计时中断的两次独立求解结果：

```text
Glucose 4.2: UNSAT
solve=3.594s, conflicts=1074, decisions=2129, propagations=30499544
峰值工作集=195.53MB

CaDiCaL 1.9.5: UNSAT
solve=29.328s, conflicts=2549, decisions=7857, propagations=179644138
```

小规模自检还完成了：

- 5 位空间的 31 个非零目标，XOR2/XOR3 选项与暴力组合枚举逐项一致；
- 广义加权顺序计数器在 12 个预算、32 个赋值上与直接求和一致，共 384
  组检查。

### 复现

依赖当前 venv 中的 `python-sat`。没有修改项目 requirements。

```powershell
cd D:\Develop\Other\turing-complete

.\.venv\Scripts\python.exe `
  .research\rng_depth2_pysat\search.py --self-test

.\.venv\Scripts\python.exe `
  .research\rng_depth2_pysat\search.py `
  --solve 201 --timeout-s 0 --memory-mb 700 `
  --solver glucose42 `
  --output .research\rng_depth2_pysat\result-201-glucose.json
```

`--timeout-s 0` 表示求解器内部不使用计时中断，本次 `UNSAT` 不是 timeout
或 `UNKNOWN` 的误记。进程工作集由脚本中的 Windows watchdog 限制为
700MB。

### 证据文件

```text
search.py
  SHA256 7A57FC002654EE1490BBE8321C8F0F3F811E1670FF21E667E5A5C1882E2B33AC

result-201-glucose.json
  SHA256 1C6F41BEB1D8C2CCA32D19CD06A3B3FE1F1FEB42ACCCCEDAFF24F6F233812510

glucose-201-exact.log
  SHA256 4B852AC7973724CE2465E72E11944301B406934C72573BA4766F85A24C1F3C07

cadical-201.log
  SHA256 D915FDD1324AA4726F42CE31A3745DACA8E13FFCF065657C1457BFF832767F06

glucose-204.log
  SHA256 69F3B101244E35FC5ECE2A5CD860378C4AA4CEDA33808D2122E79EE65EA46D54

glucose-240.log
  SHA256 E2A5895D93F7E2D9B00A2C4C52667A9BD6409318D066378403CA325A9D981E1D
```

没有生成门表，因为目标预算内不存在可导出的 SAT 解。
