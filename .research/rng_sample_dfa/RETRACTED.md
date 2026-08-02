# RETRACTED：固定样本 DFA 路线撤回

## 撤回原因

服务端重算 `campaign/rng/test.si` 时会重新随机生成 32 位 seed。本目录早期实验把一次本地
运行捕获到的 256 个 seed 当作固定测试全集，因此所得 care set、PLA、DFA 状态数和
Espresso 结果只描述那一次本地样本，不能覆盖服务端的全部 `2^32` seed，也不能作为合法
排行榜候选的正确性证书。

以下文件统一标记为 **RETRACTED**，仅保留用于说明错误路线和复现实验，不得用于生成正式
存档或声称通过服务端重算：

- `analyze_sample_dfa.py`
- `run_espresso_audit.py`
- `counter_output_care.pla`
- `counter_output_v0_care.pla`
- `deleted_state_q17_care.pla`
- `certificate.json`
- `certificate-bit0.json`
- `certificate-counter-v0.json`
- `certificate-low-fanout.json`
- `espresso_audit.json`

替代证据为 `full_space_linear_audit.py` 与 `full-space-linear-certificate.json`。替代审计只处理
GF(2) 线性恒等式，并在全部 32 个单位基 seed 上复核；这对线性映射等价于覆盖全部
`2^32` 输入。

## 边界

替代审计证明的是线性、周期线性以及分离形式

```text
y(phase, seed) = XOR_i g_i(phase) * M_i(seed)
```

的下界。它不排除一般非线性、带数据状态或利用真实高阻态互斥驱动的电路。
