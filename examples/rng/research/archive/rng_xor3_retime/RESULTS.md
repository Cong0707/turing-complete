# RNG XOR3 / retiming 研究结论

## 结论

排行榜的两项公开前沿与“标准 61-XOR DAG 中恰好做 5 次
`2 XOR2 -> 1 XOR3`，再复制 2 / 4 个 Delay Bit”的成本指纹完全一致：

```text
381 + 5*(12 - 2*3) + 2*5 = 421
381 + 5*(12 - 2*3) + 4*5 = 431
```

但该结构解释在严格时序模型中不成立。对标准 61-XOR xorshift32 DAG、
局部相邻 XOR2 链替换和任意同步 Leiserson-Saxe retiming：

| 目标 | 反馈组合周期 | 最少 XOR3 | 最有利总 gate 下界 | 指定额外 Delay Bit 后 |
|---|---:|---:|---:|---:|
| `421/10` | `P <= 6` | 11 | 447 | 457（额外 2 个） |
| `431/9` | `P <= 5` | 17 | 483 | 503（额外 4 个） |

因此这两个公开点都不可能来自该 canonical DAG 的“5 XOR3 + retiming”方案。
完整模型还放宽了主输出相位；更严格的逐拍输出要求不会推翻这个否定。

具体可实现的最小替换见证也远超目标成本：`P=6` 为 11 XOR3、59 个存活
XOR 节点、32 个状态寄存器、474 gate；`P=5` 为 `17 / 59 / 32 / 528`。

## 严格证据

- `retiming_exact/verify_certificate.py` 从移位定义重建 61 门 DAG，并用 32 个
  GF(2) 基向量验证完整映射。
- 两个自环及五个互不共享替换位置的五节点环，独立给出 `P=6` 至少 7 个、
  `P=5` 至少 17 个 XOR3 的可检查下界。
- `retiming_exact/solve_z3.py` 加入全部条件边、整数 retiming 标号及零寄存器
  路径到达时间。环平均放宽的最优值是 `9 / 17`，完整 retiming 的最优值是
  `11 / 17`。
- 标准 DAG 只有 `a17 -> b17`、`a18 -> b18` 两条单消费者链能直接实现
  `+6 gate` 的净替换。其它旁路通常保留 parent，成本为 `+9`；多个旁路共同
  删除共享 parent 时，每组两个替换合计至少 `+15`。

复现：

```powershell
.\.venv\Scripts\python.exe .research\rng_xor3_retime\retiming_exact\verify_certificate.py
.\.venv\Scripts\python.exe .research\rng_xor3_retime\retiming_exact\solve_z3.py --prove-p6-minimum --output .research\rng_xor3_retime\retiming_exact\z3_result.json
```

第二条在本机约 55 秒，单个求解进程工作集约 64 MB。

## 尚未证明的范围

`depth2_mixed/search_depth2_mixed.py` 建模自然状态下任意深度不超过 2 的
XOR2/XOR3 DAG，允许一级形式重叠、抵消、共享以及一级节点直接作为输出。
当前版本已修复初版遗漏的 weight-3 直出/跨层共享问题；在其限定模型中候选空间完备。

但 `--solve 233 --timeout-ms 30000` 的实际结果是 `unknown`，不是 `unsat`；当前脚本
已让 `unknown` 打印求解器原因并以状态码 2 退出，避免被批处理误当成证明成功。
该脚本会枚举约 4.82 亿个源对、保留约 62.3 万个原始选项，旧进程实测约
410 MB private memory，已接近 500 MB 限制。因此当前不能把它写成对任意自然态
深度二重综合的否定，更不能外推到任意状态编码、跨拍可重配置逻辑或全新顺序网络。

## 产物摘要

```text
c90067254213f1405694091a3adbe3c0e69d5bc76b3544aaa506433762386805  retiming_exact/verify_certificate.py
431cf566e1c780c0b6f03142cb2787b7f03ad0a10a9eb1e6e71faad19c9082a3  retiming_exact/certificate.json
a88f847f48a9349b832498bb15bcdd9f6619d2e4e13cacdf91b452d3f97449d8  retiming_exact/solve_z3.py
ba3be829dd6c112b089b6e25bc7a5351fa92c33fa59ff331a79f4f31da5958d2  retiming_exact/z3_result.json
e7e588ac2364378b45bdcd3dc076cf929d59815a6f857c5672e5e9edf2aa2802  depth2_mixed/search_depth2_mixed.py
```

本目录只包含研究脚本、证书和说明；未生成或覆盖正式候选存档，也未启动游戏。
