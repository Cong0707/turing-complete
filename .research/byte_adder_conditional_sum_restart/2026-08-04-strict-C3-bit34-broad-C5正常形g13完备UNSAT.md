# strict-C3 bit3:4 broad C5 正常形：weighted gate <= 13 完备 UNSAT

## 结论

固定 D7 bit3:4 residual 接口下，`weighted gate <= 13` 的完整 normal-form 搜索为
UNSAT；结合已经独立重放通过的 14 门正见证，该 residual 的精确最小 weighted gate 为
14。

```text
profile            = d7_80
paid sources       = a3,b3,a4,b4,G3,Q3,P3,G4,Q4,P4,C3@3
outputs            = S3@5, S4@7, C5@4
boundary rows      = 16 raw assignments x {Z0,D0,D1} = 48
weighted bound     = ordinary 1 / Switch 2 / XOR 3, gate <= 13
component domain   = n=0..13
normal-form shards = 230
remote terminal    = 230 UNSAT / 0 SAT / 0 UNKNOWN
coverage_complete  = true
all_unsat          = true
```

因此，在冻结的 `66 + residual` D7/80 shell 账本中，不能只替换这个 bit3:4 residual
得到 `79/7`；当前 14 门 residual 在这个局部 paid-source 接口上已经最优。

这不是对所有 Byte Adder 架构的全局 `79/7` 下界。其它 paid-source 选择、跨区域共享、
shell 改写或全局联合综合不在本证明范围内。

## 严格语义

搜索沿用 reviewed physical exact encoder：

- `C3` 在每个 raw assignment 下分别取 `Z0/D0/D1`，不是恒 driven Boolean source；
- ordinary/XOR 门读取 Z 时取 Boolean 0，并始终主动驱动输出；
- Switch enable=0 时输出 Z；
- active BUS 的 0/1 冲突禁止；
- `S3/S4` 每行必须 driven；`C5=1` 必须 driven，`C5=0` 可以 Z；
- 所有抽象 BUS 满足 physical-net driver-set partition；
- 每个 component 必须 live；
- 输出 deadline 固定为 `5/7/4`。

`exact_bit34_joint_sat.py` 及其三个传递 encoder 依赖保持固定，SHA-256 分别为：

```text
a453c4da570a31ff0210789688ac61a9123eb8be52d5f9a3a8121bc34bcc7ab3  exact_bit34_joint_sat.py
5cfd8d5121620393201f51a3db0f7328229253502cf6831ce32f8ea935b5108a  exact_paid_physical_search_core.py
9c671db251d1070b647094833c616501f72f6f6b542b6da35f0856b4f0c29dd6  exact_paid_physical_core.py
a565201bf7e99f6ded6732e70d883cd9a90e5da2e42d72171f11952bb3566ca4  exact_paid_physical_cnf.py
```

## 正常形覆盖

### component 数

每个 component 至少成本 1，所以 `gate <= 13` 必有 `n=0..13`。不 live 的 component
可直接删除；base CNF 已要求全部 component live，因此逐个精确 `n` 覆盖全部有用网络。

### C5 驱动三分

C5 output selector 非空。active-bus 限制给出严格三分：

1. `source`：C5 直接选择一个 paid source 或常量。任何 source 与其它 driver 不能同选，
   所以这一类必为单驱动。
2. `single_kK`：C5 恰选一个 component driver。其 `K` 个 component 祖先排在前，driver
   紧随，其余非祖先排在后；`K=0..n-1`。
3. `multi_dD_kK`：C5 有 `D>=2` 个 driver。普通门或 XOR 一旦被选就排斥其它 driver，
   所以所有 driver 必为 Switch。

对第三类，C5 physical net 与任一 Switch 输入 BUS 若共享 driver pin，driver-set partition
要求两个 BUS 的完整 source set 相等。某个最终 Switch 的输入 BUS 不可能包含自身或拓扑上
更后的最终 Switch，因而最终 driver 之间不能存在直接或间接依赖。

于是可以 WLOG：先拓扑排列所有最终 driver 的 component 祖先，再放 `D` 个互不依赖的
Switch driver，最后放全部非祖先。prefix user clause 要求每个前缀 component 都有一个位于
祖先/driver 区间内的后继；有限 DAG 上这等价于它最终到达某个 driver，不会把非祖先误收进
前缀。

component 基线成本为 `n`，每个 Switch 额外增加 1，所以：

```text
D <= maxSwitch(n) = min(n, 13-n)
```

这给出完整 shard 数：

```text
n0:1   n1:2   n2:4   n3:7   n4:11  n5:16  n6:22
n7:28  n8:31  n9:31  n10:28 n11:22 n12:13 n13:14
sum = 230
```

重标 component 后，commutative ordinary/XOR gate 的左右 BUS 若不再满足 encoder 的
字典序，只需交换左右输入即可恢复；Switch 的 enable/data 不交换。故 commutative
symmetry breaking 不破坏 WLOG 覆盖。

纯模块 `bit34_broad_c5_normal_form.py` 独立于 PySAT，统一生成 ordered domain、constraint
identity 与 canonical digest。230 个 `(n,shard)` key、name 和 digest 均唯一。

## 回归与独立静态审计

冻结前完成两层轻量回归：

```text
g14 / n12 / multi_d2_k3 fixed witness:
  SAT, actual_gate=14, rows=48, switches=2, xors=0
  mismatch/conflict/undriven/partition = 0/0/0/0
  independent verifier = ok

n=0..2 smoke:
  7/7 UNSAT
  missing/UNKNOWN/SAT/error = 0/0/0/0
  coverage_complete=true, all_unsat=true
```

`byte_adder_builder_verify_restart` 随后只读审计 normal-form 覆盖，独立复算 230 域和全部
digest，结论为 coverage sound、未发现漏洞。审计没有运行重型 SAT，也没有修改 frozen
search/summarizer/spec。

## 远端完整执行

在上传前，远端 `validate-only` 核对 230 ordered values 以及 11 个 required file SHA，
全部匹配。启动时 available RAM 为约 `13.4 GiB`，按批准规则使用 3 worker：

```text
host                    = root@new.xem8k5.top
runner PID observed     = 3997065
workers                 = 3
memory limit            = 4096 MiB/process, scheduled max 12288 MiB
nice                    = 10
solver                  = cadical195
outer timeout           = 21600 s/shard
internal timeout        = 0
stop on first SAT       = true
resume terminal outputs = true
```

原 49 片 fixed `n11/s2/x0` runner 保持运行，未停止、重启或修改；其 solver 为 `nice=5`，
优先级高于 broad 的 `nice=10`。

完整执行时间与求解统计：

```text
started UTC        = 2026-08-03T21:10:58.360129+00:00
finished UTC       = 2026-08-03T21:15:09.845196+00:00
wall seconds       = 251.485067
sum solve seconds  = 571.849215
min/median/max     = 0.001656 / 0.480994 / 50.135833 s
terminal           = 230 UNSAT
SAT/UNKNOWN        = 0/0
finished           = true
stopped_on_sat     = false
```

## 下载与终态核验

全部 230 个 JSON 证书下载到独立目录后，冻结 summarizer 逐片检查：

- `(n,shard)` 与完整 spec 精确一致；
- shard domain 与 constraint identity/digest 重新计算一致；
- search SHA 与 normal-form/exact/core/cnf 五个依赖 SHA 一致；
- 无 missing、unexpected、duplicate、conflict 或 malformed artifact；
- `UNKNOWN` 明确不计 coverage。

结果：

```text
expected/results = 230/230
UNSAT/SAT/UNKNOWN = 230/0/0
errors            = 0
coverage_complete = true
all_unsat         = true
```

独立 transport verifier 又把 remote summary 的 230 个 `output_sha256` 与下载文件逐项比较，
并检查 summary/spec 的 constraint digest，全部零差异。第二份独立终态审计进一步交叉比较
spec、remote summary、complete ledger 与 transport report 的 230-name 集，结论一致。

```text
remote summary SHA-256 = 8fb955bdb4ba28f5c61b9fa3433be1be624a48acb4e341e0c1f688787ec49a1d
complete ledger SHA-256 = 690401468dc5e707d3f5c75ecbdb354c62c5115244250d6d60f6a50b7425f596
transport verify SHA-256 = 9510ba5529debb5e87989062fb37061476e889235aba28f53e439d267cb67e5d
result-set canonical SHA-256 = 500f9a7f14db04c2f355ff174dc078fbeaae92080755a4755cc7075fe696e85d
```

## 可复现命令

```powershell
# 14 门固定正见证
.\.venv\Scripts\python.exe .research\byte_adder_conditional_sum_restart\verify_bit34_broad_c5_positive_regression.py `
  --solver glucose42 `
  --output .research\byte_adder_conditional_sum_restart\bit34_broad_c5_positive_g14.json

# 生成并静态验证 230 片远端 spec
python .research\byte_adder_conditional_sum_restart\generate_bit34_broad_c5_remote.py
python .research\byte_adder_conditional_sum_restart\remote_broad_c5_sweep_stop_on_sat.py `
  .research\byte_adder_conditional_sum_restart\bit34_d7_g13_broad_c5_normal_form_workers3.json `
  --validate-only

# 下载后完整汇总
python .research\byte_adder_conditional_sum_restart\summarize_bit34_broad_c5_shards.py `
  --gate-bound 13 `
  --result-directory .research\byte_adder_conditional_sum_restart\remote_results\bit34_d7_g13_broad_c5_normal_form `
  --spec .research\byte_adder_conditional_sum_restart\bit34_d7_g13_broad_c5_normal_form_workers3.json `
  --output .research\byte_adder_conditional_sum_restart\bit34_d7_g13_broad_c5_normal_form_complete.json

# remote summary 与下载证书逐项传输核验
python .research\byte_adder_conditional_sum_restart\verify_bit34_broad_c5_remote_summary.py `
  --summary .research\byte_adder_conditional_sum_restart\bit34-d7-g13-broad-c5-normal-form-workers3-summary.json `
  --spec .research\byte_adder_conditional_sum_restart\bit34_d7_g13_broad_c5_normal_form_workers3.json `
  --result-directory .research\byte_adder_conditional_sum_restart\remote_results\bit34_d7_g13_broad_c5_normal_form `
  --output .research\byte_adder_conditional_sum_restart\bit34_d7_g13_broad_c5_remote_transport_verify.json
```

## 规范证据

```text
9101c36f75779a94b7fa71416d71d98dcbf615d0a240f5c9351e53f0be0fdbbe  bit34_broad_c5_normal_form.py
229987d3f8b2c7422aec777377642c61b777c9e6563a2c47fa8e17a521d20c9a  exact_bit34_broad_c5_normal_form_shard.py
99e7e025046a5821dda7894183d10064fc4b2135c44d17b9f3f87af62cfb5553  bit34_broad_c5_positive_g14.json
3f1d65e72ba057fbb41a68b51d28ba97d09f94971b51f33fdf3948245668d185  bit34_broad_c5_positive_g14_independent_verify.json
a240fb0d21554a50de4062053de7660102255b486dd0d557265162ec6cac74f9  summarize_bit34_broad_c5_shards.py
f797d745cfcd37f443f9eb4fb3b4b655b0453cdffcf9dd447302ae3b01620437  bit34_broad_c5_smoke_n00_n02_complete.json
c428ca6ecd4ed5806a78c9aa0956c749943249c5a665db1578d0d98c98ad83fb  2026-08-04-bit34-broad-C5正常形独立静态覆盖审计.md
2dc756837f3d47423d36a364ca78a3df67760f0e90fb8d71008533ebbdf2a548  remote_broad_c5_sweep_stop_on_sat.py
175443593a1883a505de78a30945bd0a81bb332c14c1dc2c5455645643d65dba  bit34_d7_g13_broad_c5_normal_form_workers3.json
5d49e7c907581eacde96c62904c70ef5c03219e3570be54d7876ba24037b5507  bit34_d7_g13_broad_c5_normal_form_workers3_manifest.json
2f4d2e5be9cbf54a97d0975eb303a770f9782b648714d749231e0a9ac9058005  bit34_d7_g13_broad_c5_remote_validate.json
8fb955bdb4ba28f5c61b9fa3433be1be624a48acb4e341e0c1f688787ec49a1d  bit34-d7-g13-broad-c5-normal-form-workers3-summary.json
690401468dc5e707d3f5c75ecbdb354c62c5115244250d6d60f6a50b7425f596  bit34_d7_g13_broad_c5_normal_form_complete.json
9510ba5529debb5e87989062fb37061476e889235aba28f53e439d267cb67e5d  bit34_d7_g13_broad_c5_remote_transport_verify.json
23020ad2fc4c753a2cb3fd65d30e711d29219aea4f676ba4475a617620f2ba42  2026-08-04-bit34-broad-C5远端230片终态独立审计.md
8afb6fe87352f1fe7eed2bdfd3c6c9ae6f6443f9db78ad1fe0e95a93a4051fbc  bit34_d7_g13_broad_c5_remote_completion_manifest.json
```

完整 230 结果、回归、脚本、审计和传递依赖的逐文件清单为
`bit34_broad_c5_SHA256SUMS.txt`；精确提交路径为
`bit34_broad_c5_submit_files.txt`。共享 append-only 历史因其它任务可能继续追加，不纳入
SHA 清单。

本检查点没有启动游戏，没有读取或修改正式存档，没有修改或部署
`examples/byte_adder/candidate`，也没有暂存或提交 Git。当前已验收候选仍为 `80/7/560`；
本结果是该候选 bit3:4 residual 的局部精确最优性证明，不是新候选。
