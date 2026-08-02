# RNG 一位 MUX 候选（成本口径已否决）

本目录保存原标称 `350 / 10 / 67` RNG 候选的独立生成器、候选电路和离线逻辑证书。
独立运行时计分审计已否决其成本账本，当前状态为：

```text
rejected: U1 MUX runtime cost is 6/3, not 1/3
```

它没有使用 RAM，全部 34 个 Delay Bit 都从 0 开始。逻辑、逐拍和版图证书仍可用于研究，
但这份电路不再是排行榜候选。项目生成器不读取或写入正式存档，也不会启动游戏。

## 核心构造

34 个二层 XOR 使用下式实现：

```text
MUX(select=x, in0=y, in1=NOT y) = x XOR y
```

数据端反相轨由一个 34 边图的精确最小点覆盖决定。证书使用 13 个一级节点反相信号和
3 个直通叶反相信号，共 16 个覆盖点。初始化拍的输出 don't-care 还允许 5 组模式轨同时
服务反馈 `B` 与只读输出 `C`。

## 复现

在仓库根目录运行：

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_u1_mux_frontier\build_and_verify.py

Get-FileHash `
  .research\rng_u1_mux_frontier\candidate.data `
  -Algorithm SHA256
```

预期候选哈希：

```text
b4a8d804f05140d933d082fc3f8d53d9d62d99f9d894e841bbb3fc65b9012bd1
```

生成器会重建 `candidate.data` 和原始 `result.json`，并验证逐拍输出、GF(2) 变换、MUX
真值表、Z 边界、连通性、v15 往返和版图安全。它保留了被否决的旧成本假设，不能再用
其 `350` 文件头判断真实游戏成本。

## 证书边界

- 已离线验证 288 个种子、19296 拍、18720 次有效输出。
- 已用 32 个单位基各推进 65 次，在线性假设下覆盖全部 U32 种子。
- 已证明当前 34 条二层边的反相轨最小点覆盖为 16。
- 已确认候选无多驱动、Z 泄漏、短路、穿元件、穿引脚或元件重叠。
- 当前 `2.1.281` EXE 对已导入 `byte_mux 34 / 3` 应用整数缩放公式后，U1 MUX 为
  `6 gate / 3 delay`，而不是 `1 / 3`。
- 34 个 MUX 因而增加 `34 * (6 - 1) = 170` 门，修正成绩为
  `520 / 10 / 67 = 348400`。
- 修正结果差于已实机验证的 `402 / 9 / 67 = 242406`，不得写入公开候选或声称为前沿。
- 决定性公式、EXE/反编译哈希和只读复现脚本位于
  `.research/rng_u1_mux_runtime_audit/`。

本目录的 `result.json` 是保留错误发生现场的旧证书；最终成本裁决以
`.research/rng_u1_mux_runtime_audit/result.json` 为准。
