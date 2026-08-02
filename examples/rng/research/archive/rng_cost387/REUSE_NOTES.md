# RNG 387 联合搜索复用笔记

范围：只整理离线代数/综合入口，不触碰正式存档。

## 1. 数据约定

- 一个 32 位 GF(2) 线性形式用一个整数位掩码表示。
- `T`、`B`、`C` 都是长度 32 的行数组；数组下标是输出 bit，mask 的 bit `k` 表示依赖输入 bit `k`。
- JSON 可用 8 位十六进制字符串或整数：

```json
{
  "T": ["40022001", "80044002"],
  "B": ["40420002", "80840004"],
  "C": ["00420021", "00840042"]
}
```

真实文件必须每个矩阵各有 32 行。当前固定样本见
`.research/rng_joint_sat/agent_joint/fixed-two-shear.json`。

矩阵约定：

```text
q = T*x
C = A*T^-1
B = T*A*T^-1 = T*C

visible = C*q
q_next = B*q
```

候选必须独立检查：

```text
C*T = A
T*C = B
T*T^-1 = I
```

## 2. 最可复用入口

1. `.research/rng_joint_sat/agent_joint/solve_depth2_pairs.py`
   - 最适合作为任意候选 `T/B/C` 的精确 pair-cover 后端。
   - 输入 JSON 和矩阵键，输出最优 pair 集、逐行 decomposition、`K-1 UNSAT` 证书。
   - 可直接 import `build_problem()`、`solve_exact()`、`choose_decompositions()`。

2. `.research/rng_depth2_network/search_and_verify.py`
   - 可复用矩阵运算、`synthesize()`、逐门语义检查和打印器。
   - `BC_EXTRA_PAIRS` 只包含非目标的额外 pair；完整第一层应为
     `weight-2 target rows | extra pairs`。

3. `.research/rng_init_reuse/verify_init_reuse.py`
   - 当前固定 61-XOR DAG 的 dual-mode 参考实现。
   - `XorGate(output,left,right,depth)` 中各 mask 都是稳态 `q` 线性形式，不是物理元件 ID。
   - `FIRST_SEED_LABELS` 是第一层节点的 tick0 标签证书；`MODE_PAIRS` 是实际 OR 配对证书。
   - 若要只读导入，可照
     `.research/rng_redundant42_search/verify_fixed_topology_exclusion.py`
     的 `importlib.util.spec_from_file_location()` 用法。

## 3. Depth-2 pair-cover 精确模型

对联合目标行集合 `R = distinct(B union C)`：

- weight 1：直通，0 XOR；
- weight 2：必须选为第一层 pair gate，记为 `P0`；
- weight 3：一只 final XOR，三种方案中选一个输入 pair；
- weight 4：一只 final XOR，三种 perfect matching 中选一组两个 pair；
- weight > 4：当前二输入 XOR、深度不超过 2 的模型中不可行。

令 `P` 为最终选中的全部第一层 pair，`F` 为 distinct weight-3/4 目标，则：

```text
XOR = |P| + |F|
    = distinct_non_unit_targets + |P - P0|
```

重复的 `B/C` 行只造一次门，任意 fanout 免费。当前固定 two-shear 的
`B+C` 精确值为：

```text
51 distinct targets
5 unit + 12 pair targets + 34 final targets
27 selected pairs = 12 required + 15 extra
XOR = 27 + 34 = 61
pair budget 26 = UNSAT
```

注意：最优 pair-cover 可能不唯一。对 387 搜索不能只取任意一个最小 XOR
解再优化 OR；不同同成本 pair-cover 的 dual-mode OR 成本可能不同。应联合最小化
`3*XOR + OR`，或至少枚举全部/多组最优 pair-cover 再做 seed-state 覆盖。

## 4. Dual-mode / seed-state 标签约束

一只 mode-pair OR 表示一个关系 `(seed_i, q_j)`：

```text
tick0:  seed_i OR 0   = seed_i
steady: 0 OR q_j      = q_j
```

同一个 `(i,j)` OR 输出可多处扇出，只计一次。一个物理 XOR 输入在 tick0
只能取 `0` 或一个 seed 单位向量，在稳态固定取对应 `q_j`。因此：

- 第一层 pair XOR 的 tick0 标签是两个可选 seed 单位向量之 XOR，weight 至多 2；
- 第二层 XOR 的 tick0 标签由两个 fanin 标签异或，weight 至多 4；
- 每个反馈输出物理节点稳态标签必须是 `B[row]`，tick0 标签必须恰为 `T[row]`；
- `C` 的 tick0 标签无需指定，因为 tick0 的 Level Output 应被 ready 关闭；
- 所有 `B/C` 稳态目标仍必须由同一 DAG 覆盖；
- steady gate 必须逐门满足 `left XOR right == output`。

当前 Z3 模型的变量含义：

- `mapping[i][j]`：是否购买/使用唯一 OR 配对 `(seed_i,q_j)`；
- 第一层每个物理 pin：至多选一个 seed bit；
- B 的第二层 raw `q_j` fanin：每个消费位置至多选一个 seed bit；
- 目标函数：最小化 distinct `mapping[i][j]`，允许相同 OR 配对任意扇出。

固定验证器还有一个候选搜索时必须显式保留的前提：若某个 `B[row]` 是
直通单位向量，则当前实现只适用于对应 `T[row]` 也是单位向量。现有候选在
row 27..31 满足此条件；不要把该分支直接用于任意新 `T` 而不加检查。

`verify_init_reuse.py --prove-minimum` 只证明固定 `T`、固定 61-XOR DAG、
固定 32 个状态坐标下最少 47 个 OR，不是全局下界。

## 5. 387 成本边界

在 32 Delay Bit、共享 XOR DAG、mode-pair OR、ready Delay Bit + NOT 的模型下：

```text
score = 32*5 + 3*XOR + OR + 6
      = 166 + 3*XOR + OR

delay = 4 + 1 + 2*2 = 9
cycles = 1 load + 65 output = 66
```

要达到 `score <= 387`：

```text
3*XOR + OR <= 221
```

| XOR | OR 上限 |
|---:|---:|
| 61 | 38 |
| 60 | 41 |
| 59 | 44 |
| 58 | 47 |

`387/9/66` 的 energy 为 `229878`。任何新增 selector/control 元件必须另计，
不能藏进上式。

## 6. 推荐联合搜索顺序

1. 生成可逆 `T`，计算 `C=A*T^-1`、`B=T*C` 并验证矩阵恒等式。
2. 先拒绝 `B+C` 中 zero row 或 weight > 4 的候选。
3. 用 pair-cover 精确模型生成一张或多张低成本稳态 DAG。
4. 对每张 DAG 联合求 tick0 标签与 distinct `(seed_i,q_j)` OR 数；约束 32 个
   B 输出标签等于 T 行。
5. 用真实目标 `166 + 3*XOR + OR` 排序，不要只按 XOR 排序。
6. 对命中候选逐门验证 steady/tick0 双标签，再验证 65 次输出与编码态不变量。
7. 最后才进入物理布局与游戏验收；离线模型不证明禁用 Level Input 的 OR
   语义、ready tick0 关闭或无交叉短路布局。

## 7. 复跑命令

```powershell
.\.venv\Scripts\python.exe .research\rng_depth2_network\search_and_verify.py
.\.venv\Scripts\python.exe .research\rng_depth2_network\search_and_verify.py --prove-minimum
.\.venv\Scripts\python.exe .research\rng_depth2_network\search_and_verify.py --matrices --gates

.\.venv\Scripts\python.exe `
  .research\rng_joint_sat\agent_joint\solve_depth2_pairs.py `
  .research\rng_joint_sat\agent_joint\fixed-two-shear.json B C

.\.venv\Scripts\python.exe .research\rng_init_reuse\verify_init_reuse.py
.\.venv\Scripts\python.exe .research\rng_init_reuse\verify_init_reuse.py --pairs --gates
.\.venv\Scripts\python.exe .research\rng_init_reuse\verify_init_reuse.py --prove-minimum
```

`solve_depth2_pairs.py` 加 `--output <path.json>` 可写出 exact 证书。稳定结论应
看最小计数和 `proved_unsat_pair_budget`，不应假定某一组具体 pair 列表唯一。
