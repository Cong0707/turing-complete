# Q12/Q34 carry-retime cost19 tier0 终态

## 结论

七个无 XOR 的 cost19 分解已经全部离开运行态：

```text
exact UNSAT = 3
exact SAT   = 0
outer UNKNOWN = 4
running     = 0
```

这不是完整 cost19 UNSAT 证明。三个普通门较多的分解得到严格终态 UNSAT；四个
Switch-rich 分解只到达外层 7200 秒 watchdog，`status=null`，必须继续记为 UNKNOWN。

## 精确终态

```text
ordinary  Switch  XOR  components  solve_seconds       status
13        3       0    16          2156.524740245950    exact UNSAT
11        4       0    15          5561.884010576003    exact UNSAT
 9        5       0    14          6725.074518380978    exact UNSAT
```

三个 exact payload 都满足：

- schema `exact-q12-q34-carry-retime-v1`；
- `case_indices == 0..539`，共 540 个相关真值 case；
- `gate_bound=19`、`max_delay=4`、三路 deadline 均为 4；
- `physical_nets=true`；
- solver `cadical195`；
- runner `state=completed`、`status=unsat`、`return_code=0`；
- child 命令显式 `--timeout 0`；
- runner `output_sha256` 与同步后的 exact 文件字节 SHA 一致。

终态审计器会拒绝 timeout、case 缺失、成本分解漂移、参数漂移、非零退出或 SHA 不一致。
审计限制也显式记录：CaDiCaL 本轮没有生成 DRAT proof，因此这是参数、覆盖范围、runner
provenance 与终态分类审计，不冒充独立的 UNSAT proof checker。

## 外层 UNKNOWN

```text
ordinary  Switch  XOR  components  elapsed_seconds      state/status
1         9       0    10          7200.073499958962     timeout/null
3         8       0    11          7200.074489824008     timeout/null
5         7       0    12          7200.073767535971     timeout/null
7         6       0    13          7200.121937580989     timeout/null
```

这些 timeout 没有 exact JSON，未被加入 UNSAT 计数，也不能从相邻分解的 UNSAT 外推。

## 后续优先级

最高价值未决分解是 `c19-n3-s8-x0`：现有 23 门 carry SAT 证书恰为
`n3/s10/x0`，保持三只 ordinary 不变并减少两只 Switch 是结构距离最短的 cost19 路线。
后续若重跑，应换 solver/种子或加入经正回归的对称破除，避免原样重复 7200 秒轨迹。

若 cost19 SAT，现有 graft 路线预期得到 `91 gate / 6 delay / 546 energy`；仍须重新检查
carry 540 case、`C3/C5/C7<=4`、131072 行完整真值、BUS conflict、最终 Z、递归时序、
physical-net partition 和 live constants，不能仅凭局部 witness 宣称完成。

## 规范证据

```text
.research/byte_adder_av_reduced_forward/q12_q34_retime_cost19_tier0_terminal_manifest.json
.research/byte_adder_av_reduced_forward/q12_q34_retime_cost19_tier0_SHA256SUMS.txt
.research/byte_adder_av_reduced_forward/remote-cost19-terminal/
.research/byte_adder_av_reduced_forward/verify_cost19_unsat_terminal.py
.research/byte_adder_av_reduced_forward/exact_q12_q34_carry_retime_sat.py
```
