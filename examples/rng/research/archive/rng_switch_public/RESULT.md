# RNG Bit Switch 公开样本静态研究

日期：2026-08-02

## 结论

`com_switch_bit`（kind `12`）的关键价值不是普通的二选一，而是它的输出在关闭时为
高阻态 `Z`。多个 Switch 可以直接并到同一网络，因而把通常需要一棵 OR/MUX 树的
多路选择压成一个 Switch 层。游戏仍会检查总线冲突：同时启用的驱动若给出不同值，
电路会短路；同时启用但给出相同值则有效。

公开缓存中最有价值的证据是 FermiEnergy 的 XOR3：

```text
4 Bit Switch + 3 NOR + 1 AND = 12 gate / 2 delay
```

它用四个 Switch 直接驱动同一输出总线，在两层延迟内实现三输入奇偶校验。Hub 中的
XOR7 又把这种“允许同值重叠的三态 cover”扩展到 70 路，证明 Switch 不要求 enable
严格 one-hot，只要求所有同时启用的数据一致。

对 RNG 最值得继续验证的两个成本指纹是：

```text
431 - 381 = 50 = 25 * BitSwitch(2 gate)

32 Delay + 61 XOR + ready Delay + NOT = 160 + 183 + 5 + 1 = 349
431 - 349 = 82
若 47 个双模叶子各取 OR(1) 或 Switch(2)：
    s + o = 47
  2*s + o = 82
得到 s = 35, o = 12
```

第二组等式给出一个很具体、但尚未实装证明的 `35 Switch + 12 late OR` 假设。它恰好
能把 seed 控制关键路径从 `10` 压到 `9`，但必须先解决三态 seed 经普通 Splitter 后不再
传播 `Z` 的隔离问题。不能仅按门数相符就写入存档。

## Switch 的精确局部模型

当前项目的引脚定义见 `src/tc_save_lab/pins.py`：

```text
kind 12 Bit Switch
enable: input,          offset ( 0, +1), width 1
in:     input,          offset (-1,  0), width 1
out:    output_tristate,offset (+2,  0), width 1
```

因此最新版的 enable 引脚在元件下侧，与用户在 2.1.281 中观察到的方向一致。
按 `e=1` 表示开启，可写成：

```text
S(e, d) = d  且 is_z = 0，若 e = 1
S(e, d) = Z  且 is_z = 1，若 e = 0
```

对并联在同一总线的 `k` 个 Switch，令活动集合 `A={i | e_i=1}`。安全条件是：

```text
forall i,j: (e_i AND e_j) -> (d_i == d_j)
```

在满足安全条件时，数值部分和高阻标志可写成：

```text
value = OR_i(e_i AND d_i)
is_z  = NOT(OR_i e_i)
```

这里的 `value=0, is_z=1` 仍然是高阻，不应无条件等同于普通逻辑零。架构输出会单独记录
`_is_z`；普通逻辑元件通常使用数值部分，并由自己的普通输出结束 Z 传播。当前可执行文件
的静态分析还确认：普通 Splitter 的输出无条件驱动，只有 Switch 会随 enable 进入 Z。

Switch 的当前计分是 `2 gate / 1 delay`。XOR3 文件头与逐元件推导完全一致，给出了独立
交叉验证。

## 公开 XOR3 的完整拓扑

证据文件：

```text
.research/hub-entry-53/dependencies/00/XOR7/XOR3/circuit.data
SHA-256 2a82925a48cbf20aeb4cb9d9bca83feb51f56ffb0537ebfcf56fe00677164d69
```

设三个输入依次为 `a,b,c`。四个 Switch 的输出全部接到同一网络：

| 分支 | data | enable |
| --- | --- | --- |
| S0 | `c` | `NOR(a,b)` |
| S1 | `a` | `b AND c` |
| S2 | `b` | `NOR(a,c)` |
| S3 | `a` | `NOR(b,c)` |

总线的行为如下：

| `abc` | 活动分支及其驱动 | 总线数值 | `is_z` |
| --- | --- | ---: | ---: |
| `000` | S0=0, S2=0, S3=0 | 0 | 0 |
| `001` | S0=1 | 1 | 0 |
| `010` | S2=1 | 1 | 0 |
| `011` | S1=0 | 0 | 0 |
| `100` | S3=1 | 1 | 0 |
| `101` | 无 | 0 | 1 |
| `110` | 无 | 0 | 1 |
| `111` | S1=1 | 1 | 0 |

数值正好是：

```text
y = a XOR b XOR c
```

`000` 展示了重要的“同值重叠”规则：三个 Switch 同时开启没有问题，因为它们都驱动
零。`101`、`110` 则由内部 Z 的数值部分提供零；经过 Foundry 输出边界后，对外部表现为
普通 XOR3 数值。

成本和时序：

```text
gate  = 4*Switch(2) + 3*NOR(1) + 1*AND(1) = 12
delay = max(enable gate 1, direct data 0) + Switch 1 = 2
```

作为比较，两级原生 XOR2 是 `6 gate / 4 delay`。XOR3 多花 `6 gate`，减少 `2 delay`。
这适合只替换关键路径上的三输入奇偶节点，不适合无差别替换。

## XOR7 的三态 cover

证据文件：

```text
.research/hub-entry-53/main/circuit.data
SHA-256 05071730c885863cf9ee6d102822c5be89fd861b366613a4bbf37aeee9103f4f
```

静态连通性还原得到：

```text
70 个 Switch 的 out 全部连接到同一网络
每个 Switch 的 data 来自一个 XOR3
35 个 enable 来自 NOR4
35 个 enable 来自 AND4
```

对七个输入的每个三元素子集 `S`，令补集 `C` 含四个元素。文件中各有两条分支：

```text
Switch(NOR4(C), parity3(S))
Switch(AND4(C), parity3(S))
```

若输入汉明重量不超过 3，至少一个 `NOR4(C)` cover 命中；若重量至少为 4，至少一个
`AND4(C)` cover 命中。补集大小为 4，是偶数，所以补集全为 1 时：

```text
parity7 = parity3(S) XOR parity4(C) = parity3(S)
```

多个 cover 同时命中时，它们都给出相同的总奇偶值，因此不会短路。这是比 one-hot mux
更一般的“共识 cover”。

文件实际成本为：

```text
70*XOR3(12) + 35*NOR4(3) + 35*AND4(3) + 70*Switch(2)
= 840 + 105 + 105 + 140
= 1190 gate
delay = 2 + 1 = 3
```

该文件为每个三元素子集复制了两份相同 XOR3；理论上可以让同一 XOR3 扇出到对应的
NOR/AND 两个 Switch，公开文件没有这样做。因此它证明的是三态 cover 的可行性，不是
XOR7 的门数最优解。

## 其它公开 Switch 模式

### 互补二路选择实现 XOR

证据：

```text
.research/public_saves_mizuchi/bit_switch/Default/circuit.data
SHA-256 f3d323c59390532698f6885b3705023af351c0450bf2d2c1a7da306c8e7b3920
```

拓扑是：

```text
y = BUS(
      Switch(x,     NOT y0),
      Switch(NOT x, y0)
    )
  = x XOR y0
```

两个 enable 互补，所以任何输入下恰好一条分支活动。成本为 `2 Switch + 2 NOT =
6 gate / 2 delay`。它不如原生 XOR 的 `3/2`，但当互补控制或两路数据已经由别处产生时，
可以作为低增量成本的选择器模板。

### 有符号小于的条件选择

证据：

```text
.research/public_saves_mizuchi/byte_less_s/Default/circuit.data
SHA-256 d995141f3b81184d16382f43c6ec1eb79d41cff4a94d238c01919aa58be9558c
```

两个 Switch 共用输出总线：

```text
same_sign = XNOR(signA, signB)
diff_sign = XOR (signA, signB)

signed_less = BUS(
  Switch(same_sign, unsigned_less(A[6:0], B[6:0])),
  Switch(diff_sign, signA)
)
```

`same_sign` 与 `diff_sign` 互补，故无冲突。这说明 Switch 很适合把“条件本身已在计算的
两条数据路径”汇合，而不用在末端增加普通 OR 树。

### one-hot 多路总线

证据：

```text
.research/public_saves_mizuchi/foundry/Overture/Cond/circuit.data
SHA-256 741c1d2c470e6a0cb9bd16a1137c5d96c67f9b1dd5caa76aa1d879964536efca
```

一个三输入 Decoder 产生八条 one-hot enable，八个 Switch 的输出接到同一输出网络：

```text
y = BUS(Switch(e0,f0), ..., Switch(e7,f7))
```

选择层不需要三层 OR，只有一个 Switch 延迟。整个公开元件是 `57 gate / 8 delay`；其中
8 个 Switch 本身占 `16 gate`，其余成本来自 decoder 和八个数据函数。

## RNG 公开样本的负结果

现有两个可直接解码的公开随机数样本都没有使用 Bit Switch 或 Word Switch：

```text
Hub 150, xoshiro256**
.research/rng_public_artifacts/hub-150-xoshiro256/main/circuit.data
2d5d4632b6506b8a844c913b0b0095939e3535c44194314a34bcf5fbbb3776eb
55427 gate / 3221 delay

Hub 156, SRNG
.research/hub-entry-156/main/circuit.data
25133c356d0c3ada93c1059fdffeedc4bc83daa889493a9e6b002ea167d16d0b
2200 gate / 518 delay
```

Hub 150 的组件集合中没有 kind `12`、`25`；Hub 156 只有 Add、Mul、Rol 和 Constant 等
高级元件。它们不能提供榜首 `431/9/66` 的 Switch 反馈拓扑。

对 `.research` 内当前解析器支持的 v7/v13/v14/v15 `circuit.data` 做了逐文件、低内存扫描：

```text
成功解码：205
含 kind 12 的文件副本：10
去重后：6 个
```

六个唯一电路就是：公开 XOR3、XOR7、bit_switch、byte_less_s、Overture Cond，以及一个
大型旧 ALU。没有发现额外的 LFSR/xorshift Switch 电路。此结论不覆盖当前解析器未支持的
v0-v6 文件，不能外推为“所有历史存档都不存在”。

## 对 431/9/66 的可检验假设

### 假设 A：35 个早期三态叶子加 12 个 late OR

当前 396 方案的 47 个双模叶子为：

```text
leaf(seed_i, q_j) = seed_i OR q_j
```

若把一个叶子改为三态汇合：

```text
leaf(seed_i, q_j) = BUS(
  ArchitectureInput(seed_i, enabled when NOT ready),
  Switch(ready, q_j)
)
```

则 load 拍只有 seed 驱动，steady 拍只有 q 驱动。与 OR 相比，该叶子多 `1 gate`，但 seed
侧不再经过 OR：

```text
seed 控制路径：ready Delay 4 + NOT 1 + 两层 XOR 4 = 9
q 数据路径：   q Delay 4     + Switch 1 + 两层 XOR 4 = 9
```

如果 35 个处于两层 XOR 关键路径的叶子使用 Switch，另外 12 个只在较晚位置使用 OR，
成本正好是 `431`。这是目前与“Switch 很重要”及榜首门数同时吻合度最高的局部模型。

尚未解决的硬约束：一个 U32 Architecture Input 的 Z 不能经普通 Splitter 复制成多个彼此
隔离的三态网络。不同 `(seed_i,q_j)` 叶子若直接共用 seed 网络，会把不同 q 状态短接。
只有找到真实传播 Z 的复制边界、改变状态编码使配对形成可布线匹配，或支付额外 Switch
重新隔离，假设 A 才能实装。

### 假设 B：25 个 Switch 的另一种状态编码

公开 `381/11/66` 到 `431/9/66` 的差额恰为 25 个 Bit Switch。它可能表示 25 个三态选择
节点通过状态重编码换掉两层关键延迟，但不能由成本差直接推出拓扑。尤其不能简单在 381
方案上追加 25 个 Switch；追加元件通常只会增加路径。

### XOR3 不能单独解释榜首

`.research/rng_xor3_retime/RESULTS.md` 已对规范 61-XOR DAG 的局部 XOR3 替换和同步 retiming
做过严格检查：达到反馈组合周期 `P<=6` 至少需要 11 个 XOR3，`P<=5` 至少需要 17 个，
远高于“替换 5 次即可解释成本”的猜测。因此公开 XOR3 是重要原语，但若要匹配榜首，
还必须改变状态编码、共享结构或使用三态 cover，而不能只优化原规范 DAG。

## 建议纳入下一轮模型的约束

1. 每条网络显式维护 `(value,is_z)`，不能再把关闭的输入只建模为常量 0。
2. 对每个多驱动总线加入 `e_i AND e_j -> d_i == d_j`，逐拍检查短路。
3. 普通 Splitter/Maker/逻辑门输出强制 `is_z=0`；只有已核对的 Switch/架构 I/O 能传播 Z。
4. 搜索 `35 Switch + 12 OR` 时，12 个 OR 必须位于 seed 控制到输出不超过一个后续 XOR 的
   late 位置，否则关键路径仍为 10。
5. 每个三态 seed/q 汇合必须有独立网络；把 source fan-out 和 electrical isolation 分开计数。
6. 对重编码搜索同时优化 `Switch 数、OR 数、XOR/XOR3 数、最长路径`，不要只最小化 XOR。
7. 完整候选在写入前仍需验证：一个 Architecture Output、65 项输出序列、首拍 seed 读取、
   全零 Delay 初态、所有多驱动逐拍一致，以及导线不穿元件或引脚。

## 证据边界

本轮仅进行低内存静态读取和小规模真值表/连通性还原；没有启动游戏，没有读取或写入正式
存档，没有修改现有候选、源码或 README，也没有进行网络抓取。报告中的 `431` 构型都是
可检验假设，不是已恢复的榜首电路。
