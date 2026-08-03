# Byte Adder reachable output phase / timing / permutation 完整封闭

日期：2026-08-04
范围：reachable care PLA 的 512 个 output phase、D6 timing remap、64×2 与 64×13 input permutation、10 个 output grouping，以及本地最佳 BLIF 的 mapped-residual importer / 完整物理回归。
结论：**没有任何 `energy < 560` 结果；本轮没有正式覆盖资格，没有部署。**

## 1. 最终结果

| 搜索族 | summary 记录 | 最佳结果 | `<560` | 本地 artifact 级验证 |
|---|---:|---:|---:|---|
| output phase（untimed） | 512 | `phase 0x086 = 85/9/765` | 0 | 仅 `phase_086` 完整下载；5 个 mapped BLIF importer 通过 |
| output phase（D6） | 2,048 = 512×4 | `phase 0x01e resub8_d6 = 85/9/765` | 0 | 仅 `phase_086` 四个 recipe 完整下载；D6 全部 unmet |
| input permutation 64×2（untimed） | 128 = 64×2 | `perm 22 / phase 0x086 = 86/7/602` | 0 | 仅 `perm_022_phase_086` 完整下载；5 个 mapped BLIF importer 通过 |
| input permutation 64×2（D6） | 512 = 128×4 | `perm 12 / phase 0x086 / dch_d6 = 86/7/602` | 0 | 本地 `perm22/phase086` 四个 recipe 完整下载；D6 全部 unmet |
| input permutation 64×13（untimed） | 832 = 64×13 | `perm 21 / phase 0x09e = 85/7/595` | 0 | 本地同步并列最佳 `perm_022_phase_087`；5 个 mapped BLIF importer 通过 |
| input permutation 64×13（D6） | 3,328 = 832×4 | `perm 22 / phase 0x087 / dch_d6 = 85/7/595` | 0 | 本地 `perm22/phase087` 四个 recipe 完整下载；D6 全部 unmet |
| output grouping | 10 | `all = 86/9/774` | 0 | 只有 summary；无逐 grouping BLIF/log |

七类 summary 合计 7,370 条结果，严格阈值 `energy < 560` 命中数为 0，`delay <= 6` 命中数为 0。

当前最低值为 64×13 搜索中的 `85/7/595`。它显著优于 output-phase 单独搜索的 `85/9/765`，但仍高于 560，因此只能作为已验证的研究产物，不能覆盖正式 Byte Adder。

## 2. 安全边界

本轮执行满足：

- 未启动游戏；
- 未读取或写入正式 Byte Adder save；
- 未写入 `examples/byte_adder/candidate`；
- 未部署 repository candidate；
- 未修改 S1/S2 冻结 manifest 的 46 个文件；
- 未修改前一轮 ABC mapped-residual manifest 的 36 个文件；
- 未重新运行 Espresso 512 phase 枚举或 ABC 批量映射；
- 只对已下载的本地 mapped BLIF 运行 importer 和离线物理 pipeline；
- timing normalization 只写入独立派生目录，原始 mapped BLIF 保持不变。

## 3. 权威输入与 care relation

```text
71625de2b86ea03127415802dbc68f605ac16d69da6d9e8b3ade35db317ec884  .research/byte_adder_root/byte-adder-hybrid-phasefold-g80-d7.json
13052a0b6024940bf11f2b81d93dc4223924973f82e1e7d1808b7007a32d007e  .research/byte_adder_root/abc_residual_current80/metadata.json
1e84f6a3d9d28393cbce99b0eb5fb0f33fb65c39e15ec48a8ecdb798928f0566  .research/byte_adder_root/abc_residual_current80/care_pla/reachable_relation_fr.pla
d7eb0d22a061c68d2caa073cb8ab08abd50ae7443d4b2f0a25655393f9511f5e  .research/turing-complete.genlib
```

独立严格解析结果：

- `.type fr`；
- 21 个输入、9 个输出；
- 23,328 个唯一、完整二进制 care 点；
- 函数冲突 0；
- PI 顺序严格等于 metadata boundary 顺序；
- PO 顺序严格为 `out0..out8`。

真实 boundary arrival：

```text
n2=0  n4=0  n5=0  n16=0 n17=0
n22=1 n25=1 n28=1 n29=1 n31=1 n32=1 n34=1
n36=2 n39=2 n43=1 n44=1 n45=2 n51=1
n56=3 n62=4 n69=5
```

## 4. 当前脚本审查

本次以接手时重新计算的当前脚本 SHA 为准：

```text
bc0a66a2e9e5562ff31817fc09c77e0b91570aa4467911afb109fafebf30fb59  .research/byte_adder_root/search_reachable_output_phases.py
1e08db29989d0db3562e8930d50fd277cb32fb30cc099220c525c5070adc1a70  .research/byte_adder_root/map_reachable_phase_timing_batch.py
ac89959b80ba40d4af6724ece5dd9fddc23963df1821bac66d7d42cf79ed1e9b  .research/byte_adder_root/search_reachable_input_permutations.py
ce00b9f3cdeee472c4a3bcd095ae4675bc9b94908951ab64c2b869c195c848a4  .research/byte_adder_root/map_reachable_permutation_timing_batch.py
aa66533f9d63789e7c30a3a09e6e5b3df257e7b29d99cc1c40f018aee6a4affd  .research/byte_adder_root/search_reachable_output_groupings.py
```

两份 permutation 脚本在 64×13 follow-on 完成后又加入了 `--permutation-start` 与 `permutation_stop` 分片契约，因此当前文件 SHA 与生成下载 summaries 时的版本不同。下载的 64×2/64×13 summaries 没有这两个新字段；本报告不以当前源码字段反推旧产物，而是直接从 summary 的实际 record key 集合证明其均完整覆盖 `permutation_index=0..63`。当前版本的新增分片入口另有正数/非负范围检查，并按 `[start, stop)` 构造精确目录集合。

### 4.1 output phase 极性补回

搜索对每个 care 输出执行：

```python
phased = expected ^ mask
```

对 mask bit 为 1 的输出，BLIF 先生成 `phase_outN` 的 ON-set，再追加：

```blif
.names phase_outN outN
0 1
```

该 `.names` 是显式反相器，因此最终 `outN = NOT(phase_outN)`，恢复原输出极性。`phase_086` 的置位输出为 `out1/out2/out7`。独立审计不仅检查了结构，还在本地 `perm_022_phase_086/input.blif` 上对全部 23,328 个 care 点逐行求值，补回后 mismatch=0。

### 4.2 fail-closed 状态

当前 output-phase 脚本已经具备：

- metadata PI/PO 标签及顺序检查；
- 23,328 个唯一 care 点检查；
- care 函数唯一性检查；
- ABC 前删除旧 `mapped.blif` 与 log；
- ABC return code 与 mapped 文件存在性检查。

当前 timing 脚本已经具备：

- `phase_000..phase_1ff` 完整目录覆盖检查；
- 每个 phase 四个 recipe；
- ABC 前删除旧 mapped/log；
- worker error 与 recipe-level error 同时进入失败退出码；
- `required=6` 的显式记录。

permutation search 继承同一严格 PLA/parser 与 BLIF 极性逻辑，并额外强制 23,328 行、metadata 标签和确定性 permutation；permutation timing 同样检查调用方声明的全部 permutation×mask 候选目录完整覆盖并聚合 recipe errors。该契约已分别在 64×2 和 64×13 搜索上验证。

output-grouping 搜索脚本仍有两个静态弱点：入口未单独强制 23,328 行/metadata 标签，且 ABC 前未删除旧 mapped 输出。本地又没有十组 BLIF/log，因此 grouping 结论严格限制为 summary 组合完整性，不能上升为逐 artifact 或 importer 证明。

## 5. required=6、真实 arrival 与 ABC old parser

timed BLIF 精确追加：

```text
.default_input_arrival 0 0
.default_output_required 6 6
.input_arrival n<ID> <metadata arrival> <metadata arrival>
.output_required out<N> 6 6
```

实际 ABC 命令为：

```text
read_blif -n <timed.blif>
```

独立核对 Berkeley ABC 官方 `src/base/io/io.c`：

```c
fUseNewParser = 1;
case 'n':
    fUseNewParser ^= 1;
...
else if ( fUseNewParser )
    pNtk = Io_Read(...);
else
    pNtk = Io_ReadBlif(...);
```

帮助文本也明确：

```text
-n : toggle using old BLIF parser without hierarchy support
```

因此 `read_blif -n` 的确进入 old BLIF parser，而不是新 parser。官方源码核对地址：<https://github.com/berkeley-abc/abc/blob/master/src/base/io/io.c>。

## 6. 512 output phase 封闭

关键 summary：

```text
cdaa1dbc7908fb13fd68e334c4d3d91b3d9845eba1c014752cde84868cf75359  output_phase_all/summary.json
1c0cc322ccec326c5fb0376140115a9c22b69efe5ab012610f91a969adde3f69  output_phase_all/timing_d6_summary.json
```

验证结果：

- untimed：512/512 mask 恰为 `0..511`，errors=0，care mismatch 全 0；
- untimed 最佳：`phase 0x086 = 85/9/765`；
- D6：512/512 phase、2,048/2,048 recipe 记录；
- recipe 集合精确为 `plain_d6/dch_d6/dc2_d6/resub8_d6`；
- `required=6`；
- worker errors=0，recipe errors=0；
- ABC reported unmet=2,048，met=0；
- D6 最佳仍为 `phase 0x01e / resub8_d6 = 85/9/765`；
- 全部真实递归 delay 至少为 9。

本地仅有 `phase_086` 全套 artifact：

```text
336bacc81b5773f5efd07f73cefd4f7b9d94c1af573e14ae83dde704c334876c  phase_086/input.blif
8c647abb51fc0ee7b41606f1380820dbc20ab8a3cb964e004c03a07cc525885b  phase_086/mapped.blif
```

因此能确认 summary 的 512 组合完整性，但不能声称其余 511 个 phase 已在本机逐文件复算 SHA。

## 7. phase086 importer 与完整物理回归

独立审计器：

```text
6714be18bac06ff53eb192614c3d9171fa40505f3f689afc87642b4eb606bf6a  .research/byte_adder_root/audit_reachable_output_phase_artifacts.py
0a8085fbc2110738eb4edb14651078ed638f6cb7f2cd3586fe014216ba08c23f  output_phase_all/independent_import_audit.json
```

审计器连续两个独立 Python 进程产生相同 JSON 与相同 normalized BLIF SHA。五个本地映射均通过 importer 双构建：

| BLIF | 实际 gate/delay/energy |
|---|---:|
| `mapped.blif` | `85/9/765` |
| `mapped_dch_d6.blif` | `86/9/774` |
| `mapped_resub8_d6.blif` | `86/9/774` |
| `mapped_dc2_d6.blif` | `88/9/792` |
| `mapped_plain_d6.blif` | `88/9/792` |

每项均满足：

- same-process importer JSON byte-identical；
- discovery metrics 与 importer 实测一致；
- fixed BUS slice byte-identical；
- 131,072 行全域 truth table；
- mismatch union=0；
- BUS conflict=0；
- primary output Z=0；
- physical-net partition violation=0；
- mapped/shell/generated dead node=0。

### 7.1 timing annotation normalization

ABC old parser 的 `write_blif` 会在 mapped 输出中保留 timing directive。严格 importer 不接受这些非门级 directive，因此审计流程：

1. 先逐项验证原始 mapped BLIF 的 timing directive 必须精确等于 metadata 与 `required=6`；
2. 原始文件不修改；
3. 仅在 `normalized_for_import` 派生目录删除已经验证过的 timing annotation；
4. importer 同时记录原始 SHA、派生 SHA和被删除的完整 directive 列表。

phase086 派生 SHA：

```text
a4bcd5f1fb86c9f50da30673ffac0787f7585f60aa3d03b0a3cbef24bbee557d  mapped_plain_d6.blif
f554e7041724f0400b4514596c204714f6e92358dd23af51e2d6ff1c160ccfcb  mapped_dch_d6.blif
f4c983160882cb1c1670e3ff41150098cb0b7813f970e07685eb3b396a7ec94c  mapped_dc2_d6.blif
4e1fe288bee71231fca2700bf8ad86bd341ecfdb3d6084103e812485086b4562  mapped_resub8_d6.blif
```

### 7.2 完整物理 pipeline

`phase_086/mapped.blif` 的完整离线物理 pipeline 连续两次产物字节稳定：

```text
87d3833a62ada2cd38aa4ca18f3bfc310447f52b703d4501431d077df6772d23  grafted_factory_dag.json
04b7465793a1367184e303c26b922f1e032232c082044ae8b695c7a90ad0e439  materialized/candidate/circuit.data
b488f53c34df360f0157e35fcf79c917df5eabdc13b5cf7371551bcbfe1cca25  materialized/machine_certificate.json
e6d6a6df41ebfcfa05e8a9e7721c46b15f9392e268f29554d12b5ece7fa134a0  independent_audit.json
47d691153ceef82972f787ff6a78686077a8cd0c026a29e4e1c3d515fd71bef8  pipeline_summary.json
```

完整通过：131,072 行、BUS/Z、递归时延、物理网络、dead node、连通性、几何、v15 round-trip、独立物理审计、确定性物理重建、immutable inputs。`com_add=0`，无正式 save/候选写入。

## 8. 64×2 input permutation 封闭

summary：

```text
4142374b59fd409d292dff7e03e907d4c80fba2be1c85a658bef2aa211dc75f4  input_permutation_64x2/summary.json
1efb9b06195199bf1581892a691df4e6aad475abdb5a6a82f85132d368f7c01c  input_permutation_64x2/timing_d6_summary.json
```

组合检查：

- 64 个 permutation 由四个固定候选加 `random.Random(seed)` 序列确定性生成；
- 每个 summary record 的 permutation 向量与输入名称都逐项匹配生成器；
- masks 精确为 `0x000,0x086`；
- search 为 128/128，errors=0；
- timing 为 128/128 candidates、512/512 recipes；
- worker/recipe errors 均为 0；
- timing `required=6`；
- ABC reported unmet=512，met=0；
- search 最佳为 `perm22/phase086 = 86/7/602`；
- timing 的排序首项为 `perm12/phase086/dch_d6 = 86/7/602`，共有多个 602 并列项；
- 所有 summary 结果均无 `<560`。

本地仅下载 `perm_022_phase_086` 全套 artifact：

```text
84c59bef1d4b9402938a48679bfa8de3bdd5fe7959699c5ea4094683fdfe255d  perm_022_phase_086/input.blif
bd8d5f6de44cd66c76481df1124703ed92b509b3446efed4d599096b6c78b884  perm_022_phase_086/mapped.blif
```

### 8.1 独立 importer 审计

```text
c85af71d269f66f1f372ddd8ca9704520b109dfa2665dcb12353079bc925decf  .research/byte_adder_root/audit_reachable_input_permutation_artifacts.py
66f73f9a552946cb70314791bc6ad0ccac0e8d789aa71d705a43a28ced23c0bc  input_permutation_64x2/independent_import_audit.json
```

该审计器不导入 PyEDA、不运行 Espresso/ABC；它独立复刻确定性 permutation 生成规则，严格检查 128+512 summary 组合，并对本地 `input.blif` 的 23,328 个 care 点逐行求值。

五个本地 mapped 文件 importer 双构建全部接受：

| BLIF | 实际 gate/delay/energy |
|---|---:|
| `mapped.blif` | `86/7/602` |
| `mapped_dc2_d6.blif` | `86/7/602` |
| `mapped_dch_d6.blif` | `86/7/602` |
| `mapped_resub8_d6.blif` | `86/7/602` |
| `mapped_plain_d6.blif` | `88/8/704` |

同样全部通过 131,072 行、mismatch/BUS/Z、physical-net、dead-node 与确定性检查。审计 JSON 和四个 normalized timing BLIF 连续两次 SHA 稳定。

### 8.2 perm22/phase086 完整物理 pipeline

完整物理 pipeline 连续两次稳定：

```text
7c3c2bad268b9c77c192a8411c72bcfb57523af37a2f9ce71049833d248de85f  grafted_factory_dag.json
62495b80760565225f3c586fbf30a198e27fbf4a12a8db8c6d4571a6cff71ff4  materialized/candidate/circuit.data
5bd1b080cf4bbc2dbdc0ff847a1fecc3777db489e1d6554b07e6bd07e48de277  materialized/machine_certificate.json
b9589de2712c1976e2135dbea60a36b901e3c15678415f6699b3bd7fb91fe737  independent_audit.json
1c9906fe6fd34b6caf5feed97f3d150616d878f46b783ed5bda06abd9fac1e05  pipeline_summary.json
```

指标 `86/7/602`，所有完整物理检查通过，且：

```text
formal_save_read=false
formal_save_written=false
repository_candidate_written=false
game_started=false
```

## 9. 64×13 input permutation 封闭

根线扩展了 64 个确定性 input permutation 与 13 个候选 output phase 的笛卡尔积：

```text
0x086 0x087 0x09e 0x09f 0x0a6 0x0a7 0x0b6
0x0b7 0x0be 0x0bf 0x0c7 0x0de 0x0df
```

关键下载与 follow-on 证据：

```text
0b75e84b2ff03edfbcfefe9f38e79acd096ed923e1828c2875b03f414c165507  input_permutation_64x13/summary.json
28d06a1c9aad07f4aadd35d8f72ee6d8c42a7978dc600d67b58868378fc410a4  input_permutation_64x13/timing_d6_summary.json
96d3e305b6181662f057a70196a3b801c75b5dfaabfaa21de66bd906f663b704  input_permutation_64x13/timing_d6_followon.run.json
003d9b686329882685e9a4c51e7f0a93424b894e9bd22fe9683fd31424faad3f  input_permutation_64x13/timing_d6_followon.log
```

`timing_d6_followon.run.json` 记录 `exit_code=0`、`classification=solver_exit`、`last_phase=timing_batch`；follow-on log 的结尾明确写出 summary 路径与最佳 `perm22/phase087=85/7/595 dch_d6`。

### 9.1 全组合独立审计

独立审计逐条验证：

- 64 个 permutation 均精确匹配确定性生成器；
- 每个 record 的 permutation 向量与 `permuted_input_names` 一致；
- 13 个 mask 精确匹配上述集合；
- search key 集合精确等于 `range(64) × masks`，832/832，无重复、无遗漏；
- timing key 集合精确等于同一 832 候选，每个候选四个 recipe，3,328/3,328；
- search errors=0；timing worker errors=0、recipe errors=0；
- `required=6`，真实 boundary arrival 与 metadata 一致；
- ABC reported unmet=3,328，met=0；
- search 与 timing 中 `delay <= 6` 均为 0；
- search 中 595 并列项 9 个，timing 中 595 并列项 16 个；
- `energy < 560` 命中 0。

全局 untimed 排序首项是 `perm21/phase09e=85/7/595`；其逐文件 artifact 未下载。本地同步的是同为 595 的 `perm_022_phase_087`，并且它是 timing summary 的排序首项。

本地源 artifact：

```text
8573d3ee61cf7bdd8bb2e81b96d5800ec32bac2d344798ccde52a54145dc2e07  perm_022_phase_087/input.blif
7560bf6726356be1f6df77b3e2e4c980a7341bc77c3fed780f829f831644fd4d  perm_022_phase_087/mapped.blif
```

`phase 0x087` 反相 `out0/out1/out2/out7`。本地 `input.blif` 的 BLIF 结构、显式 NOT 补回和全部 23,328 个 care 点逐行求值均通过，mismatch=0。

独立审计：

```text
1019b65880903b9e467dbe0276a399880d22e6b5f1276bfceca15179333eadf8  input_permutation_64x13/independent_import_audit.json
```

同步完成后，默认环境连续两次以及显式不同 `PYTHONHASHSEED` 均产生相同语义与字节稳定的审计 JSON。审计器随后增加了显式 `[permutation_start, permutation_stop)` 契约并重新生成当前 JSON；五个本地 mapped 文件 importer 双构建全部接受：

| BLIF | 实际 gate/delay/energy |
|---|---:|
| `mapped.blif` | `85/7/595` |
| `mapped_dch_d6.blif` | `85/7/595` |
| `mapped_resub8_d6.blif` | `85/7/595` |
| `mapped_dc2_d6.blif` | `87/7/609` |
| `mapped_plain_d6.blif` | `87/8/696` |

五项全部通过 importer 的 131,072 行全域 truth table、mismatch/BUS/Z、physical-net partition、dead-node、固定 BUS slice 与 same-process JSON byte-identical 检查。

timing mapped BLIF 在验证原始 timing directive 后生成的独立 normalized SHA：

```text
0ae1ae1711d042d595bcca3f775c28471097cb386ddf4432d880b06d18c4df38  mapped_dc2_d6.blif
ae67c9468741080c1f7dd2c2e78584ddb5dd028c347970c722b054f1dbacba13  mapped_dch_d6.blif
875d6c241767bf07b3e82979a191873a7bbb4d0bc9c573a8afb88539934a9861  mapped_plain_d6.blif
c9220733425e108c07f7a5de38fef3653a56a2db03d08b8c20463c3facf5ce70  mapped_resub8_d6.blif
```

### 9.2 perm22/phase087 完整物理 pipeline

`mapped.blif=85/7/595` 的完整离线物理 pipeline 连续两次且跨 hash seed 稳定：

```text
386784c534ac9586ca6fa98bd60947eb387f82a7984dc18a7f6e00796497de7c  grafted_factory_dag.json
b48220901fe4882b85abd4dbd3d6dcc6c32984643535ec33b5a2baa137da0663  materialized/candidate/circuit.data
4321e67dbacfadc27a7c5b00672157bc63e3a7e546916770fa4b0d4463564d7c  materialized/machine_certificate.json
3587f828dfe30a2efa133ef85eccf7c6b30280d5dad4e02a67c28d246b61a665  independent_audit.json
579ba1cfc936f22ac77b4c4e811da2e38d5528b6547d94d698941d5425c2504d  pipeline_summary.json
```

完整通过 131,072 行、BUS/Z、递归时延、物理网络、dead node、连通性、几何、v15 round-trip、独立物理审计、确定性物理重建与 immutable inputs。安全哨兵保持：

```text
formal_save_read=false
formal_save_written=false
repository_candidate_written=false
game_started=false
```

限制：本地只有 `perm_022_phase_087`，不能声称其余 831 个候选或全局 untimed 排序首项 `perm21/phase09e` 已在本机逐文件复算 SHA。

## 10. output grouping summary-only 审计

```text
a02887284cad26e2e754f32c2c48a87c84509971c04d69e588efcb7dafb597c6  .research/byte_adder_root/audit_reachable_output_grouping_summary.py
b64414fce90423954bdb6a77a4bce78bffa9a74264c8b742589b32a90b3a4b45  output_groupings/summary.json
40bbb18376cbd2f3d14ff8c0b09c69945ad46e1a17920cc0e419773c278118a0  output_groupings/independent_summary_audit.json
```

独立检查结果：

- expected/completed=10/10；
- errors=0；
- grouping 名称唯一且精确匹配声明集合；
- 每个 grouping 的 groups 都是 `0..8` 的非空、无重叠、完整分区；
- `group_stats.outputs` 与 groups 逐项一致；
- source PLA、metadata、genlib SHA 与当前文件一致；
- care mismatch 全 0；
- gate/delay/energy 方程全部一致；
- 最佳 `all = 86/9/774`；
- `<560` 命中 0。

限制：本地 group directory 数为 0，所以 `per_group_sha_recomputed=false`、`importer_run=false`。这不是逐 BLIF 验证。

## 11. 冻结链与 repository 状态

既有 manifest 重新逐项验证：

```text
b727596c19c596bb0420aaac94597d77ec4d9c83ba04be5d9a2433708e0841f6  .research/byte_adder_root/abc_mapped_residual_pipeline_SHA256SUMS.txt
  36/36 files pass

dd0e2cdef027fccf3a34d7c8752a545e9f2834b239d5af43f9c2f81ffacef3ef  .research/byte_adder_builder_verify_restart/s1s2_joint_strict_cost9_SHA256SUMS.txt
  46/46 files pass
```

`git status -- examples/byte_adder` 为空；正式 Byte Adder 路径没有被本轮修改。

## 12. 复现命令

phase artifact/importer 审计：

```powershell
python .research/byte_adder_root/audit_reachable_output_phase_artifacts.py `
  --phase-dir .research/byte_adder_root/abc_residual_current80/care_pla/output_phase_all `
  --summary .research/byte_adder_root/abc_residual_current80/care_pla/output_phase_all/summary.json `
  --summary .research/byte_adder_root/abc_residual_current80/care_pla/output_phase_all/timing_d6_summary.json `
  --output .research/byte_adder_root/abc_residual_current80/care_pla/output_phase_all/independent_import_audit.json `
  --normalized-dir .research/byte_adder_root/abc_residual_current80/care_pla/output_phase_all/normalized_for_import `
  --expected-care-rows 23328 --expected-phases 512 --required 6 --top 32 --energy-threshold 560
```

permutation artifact/importer 审计：

```powershell
python .research/byte_adder_root/audit_reachable_input_permutation_artifacts.py `
  --candidate-dir .research/byte_adder_root/abc_residual_current80/care_pla/input_permutation_64x2 `
  --search-summary .research/byte_adder_root/abc_residual_current80/care_pla/input_permutation_64x2/summary.json `
  --timing-summary .research/byte_adder_root/abc_residual_current80/care_pla/input_permutation_64x2/timing_d6_summary.json `
  --output .research/byte_adder_root/abc_residual_current80/care_pla/input_permutation_64x2/independent_import_audit.json `
  --normalized-dir .research/byte_adder_root/abc_residual_current80/care_pla/input_permutation_64x2/normalized_for_import `
  --expected-care-rows 23328 --permutation-start 0 --expected-permutations 64 --masks 0x000,0x086 `
  --required 6 --energy-threshold 560
```

64×13 permutation artifact/importer 审计：

```powershell
python .research/byte_adder_root/audit_reachable_input_permutation_artifacts.py `
  --candidate-dir .research/byte_adder_root/abc_residual_current80/care_pla/input_permutation_64x13 `
  --search-summary .research/byte_adder_root/abc_residual_current80/care_pla/input_permutation_64x13/summary.json `
  --timing-summary .research/byte_adder_root/abc_residual_current80/care_pla/input_permutation_64x13/timing_d6_summary.json `
  --output .research/byte_adder_root/abc_residual_current80/care_pla/input_permutation_64x13/independent_import_audit.json `
  --normalized-dir .research/byte_adder_root/abc_residual_current80/care_pla/input_permutation_64x13/normalized_for_import `
  --expected-care-rows 23328 --permutation-start 0 --expected-permutations 64 `
  --masks 0x086,0x087,0x09e,0x09f,0x0a6,0x0a7,0x0b6,0x0b7,0x0be,0x0bf,0x0c7,0x0de,0x0df `
  --required 6 --energy-threshold 560
```

完整物理 pipeline 需要源码导入路径：

```powershell
$env:PYTHONPATH=(Resolve-Path src).Path
python .research/byte_adder_root/run_abc_mapped_residual_pipeline.py `
  --blif <mapped.blif> --output-dir <independent-output-dir> `
  --expected-gate <G> --expected-delay <D> --expected-energy <E> `
  --max-gate <G> --max-delay <D> --max-energy <E>
```

不设置 `PYTHONPATH=src` 时会在加载 `tc_save_lab` 前以 `ModuleNotFoundError` 失败；该失败发生在物化写入前。

## 13. 最终判定

1. 512 output phase summary 与 2,048 个 D6 recipe 组合完整；本地 phase086 的极性、timing、importer 与完整物理路径全部闭合。
2. 64×2 permutation summary 与 512 个 D6 recipe 组合完整；本地 perm22/phase086 在全部 care 点、131,072 行全域语义及完整物理层均闭合。
3. 64×13 permutation summary 的 832 个 search 任务与 3,328 个 D6 recipe 组合完整；本地 perm22/phase087 在全部 care 点、131,072 行全域语义及完整物理层均闭合。
4. output grouping 的十个分区与指标 summary 完整，但因缺少逐组 artifact，只具有 summary-only 证据等级。
5. 七类 summary 共 7,370 条结果，均没有 `energy < 560` 或 `delay <= 6`；最低结果是 `85/7/595`。
6. 不具备正式覆盖资格；没有部署、没有启动游戏、没有改写正式 save 或 repository candidate。
