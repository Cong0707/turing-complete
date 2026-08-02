# RNG 42 维冗余状态搜索

## 结论

本轮没有找到可实装的 `42 Delay Bit + 61 XOR2 + 32 OR + ready Delay/NOT`
候选，也没有修改正式存档。

已完成的严格结果：

1. 固定当前 `rng_init_reuse` 的 base `B` 输出连接，只把任意一级 pair 门改成
   存储叶的整个局部族不可能满足“一颗 seed 只进入一颗 OR 叶”。
2. 在秩 32 强不变量参数化中，把 10 个冗余行限定为自然第一阶段
   `u_i=x_i XOR x_(i+13)`：`C(19,10)=92378` 个集合全部枚举；184 个通过支持度
   必要条件的集合全部由 Z3 证明 `UNSAT`。
3. 另取 500 个任意二项冗余字典和 500 个权重 2 到 4 的稀疏冗余字典；它们均已
   先通过支持度必要条件，随后全部由 Z3 证明 `UNSAT`，没有 `unknown`。

第 3 项是确定性样本排除，不是整个稀疏行空间的全局反证。任意 10 个二项行的全局
布尔模型在 120 秒、约 80 MB 峰值内返回 `unknown(timeout)`，因此不能写成 UNSAT。

## 精确模型

将 42 个网络叶重编号为：

```text
0..31: tick0 = seed_i, steady = q_i
32..41: tick0 = 0,      steady = q_i
S = [I32; 0]
```

搜索使用下面的秩 32 强不变量参数化：

```text
X: 32x10
R: 10x32
O = [I32 | X]
E = [A + X*R; R]
H = E*O
```

它自动满足：

```text
H*S = E
O*E = A
H*E = E*A
```

所以任何通过门级约束的模型都会在首拍装入 `E*seed`，随后永久输出精确的
`A(seed)..A^65(seed)`。每个 `H/O` 行必须支持至多 4 个叶，之后还必须对全部互异
目标行做深度二 pair-cover，并满足共享 XOR 数不超过 61。

本轮所有被排除的参数化在 pair-cover 之前就已失败，因此结论不依赖门数估算。

## 固定拓扑反证

对每个现有一级 pair `r`，令 `F_r` 为它在 32 个 base `B` 输出中的扇出影响列。
存储集合任意变化时，每个可能叶对 base 输出的列只能是：

```text
aux_r: F_r
q_i:   expanded_B_col(i) XOR XOR {F_r | r 被存储且包含 q_i}
```

把 27 个 `F_r` 全部纳入，并独立枚举每个 `q_i` 的所有局部模式，是对任何全局存储
集合的过近似。合并后只有 60 个不同叶列；`T` 的列 17 到 31 一个也不在其中：

```text
00020011 00040022 00080044 00100088 00200110
00400220 00800440 01000880 02001100 04002200
08004400 10008800 20011000 40022001 80044002
```

每个 seed 位只允许进入一个叶，因此这 15 个 seed 列无法形成。该反证允许存储任意
数量的 27 个 pair，不只 10 个；但它只覆盖 base 输出连接保持不变的局部族。

## 最近前沿

`nearest_invalid_certificate.json` 是本轮最近的具体矩阵：

```text
69 seeds x 65 outputs: PASS
H*S=E, O*E=A, H*E=E*A: PASS
support excess over 4: 18
maximum H/O row weight: 6
bad H rows: 13
```

它在完整线性时序上正确，但权重 6 的行严格不能由两层 XOR2 产生，因此不是候选，
不能写入存档，也不能声称 `delay<=9` 或 `XOR<=61`。

## 复现

固定拓扑证书：

```powershell
python .research/rng_redundant42_search/verify_fixed_topology_exclusion.py `
  --output .research/rng_redundant42_search/fixed_topology_certificate.json
```

自然一级行的完整枚举与 Z3：

```powershell
g++ -std=c++20 -O3 -DNDEBUG -o `
  .research/rng_redundant42_search/search_rank32_factor.exe `
  .research/rng_redundant42_search/search_rank32_factor.cpp
.research/rng_redundant42_search/search_rank32_factor.exe | `
  Set-Content .research/rng_redundant42_search/rank32_frontier.txt
python .research/rng_redundant42_search/solve_rank32_factor.py `
  --frontier .research/rng_redundant42_search/rank32_frontier.txt `
  --timeout-ms 10000 --output .research/rng_redundant42_search/rank32_z3_result.json
```

确定性稀疏字典样本：

```powershell
g++ -std=c++20 -O3 -DNDEBUG -o `
  .research/rng_redundant42_search/walk_pair_dictionaries.exe `
  .research/rng_redundant42_search/walk_pair_dictionaries.cpp
.research/rng_redundant42_search/walk_pair_dictionaries.exe 2000000 20260801 500 2 | `
  Set-Content .research/rng_redundant42_search/pair_dictionary_frontier.txt
.research/rng_redundant42_search/walk_pair_dictionaries.exe 5000000 424242 500 4 | `
  Set-Content .research/rng_redundant42_search/sparse_dictionary_frontier.txt
python .research/rng_redundant42_search/solve_rank32_factor.py `
  --pair-frontier .research/rng_redundant42_search/pair_dictionary_frontier.txt `
  --timeout-ms 2000 --output .research/rng_redundant42_search/pair_z3_result.json
python .research/rng_redundant42_search/solve_rank32_factor.py `
  --pair-frontier .research/rng_redundant42_search/sparse_dictionary_frontier.txt `
  --timeout-ms 2000 --output .research/rng_redundant42_search/sparse_z3_result.json
```

最近无效前沿的完整时序复核：

```powershell
python .research/rng_redundant42_search/build_nearest_frontier.py `
  --log .research/rng_redundant42_search/pair_local_search_seed70042.log `
  --output .research/rng_redundant42_search/nearest_invalid_certificate.json
```

## 核心文件 SHA-256

```text
aa221e8ee5e68790f4c73f9ac91e2afae16609cfbde664243ffc58e5ff443fcc  fixed_topology_certificate.json
9a510a6a078dc653588c664d3b7e411feef0ac3827244275cef3b08b255a3aab  rank32_z3_result.json
6a859945cdf8f97bedf6d92172c6e8d6841beb33feaa765c025c58bdc676b0a9  pair_z3_result.json
ebc7b9ab5d469c1e510946ce03e6f373b06a5b77efef0f7c20e8d4cba93445b2  sparse_z3_result.json
73e718427bd5baff1995006983a295ed59595ed03fe00a72b1fca1cdd51ddff3  nearest_invalid_certificate.json
```
