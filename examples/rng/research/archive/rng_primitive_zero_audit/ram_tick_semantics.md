# RAM mode 2 tick semantics

## 结论

针对当前安装版 `Turing Complete.exe`（SHA-256
`C93F5E8E826050C3F92E2B3891D26FCDFC933658614185CB9B2EB6A34C5B8D1C`）的
只读静态审计得到以下闭合结论：

- `kind=118, settings=(2, 512, 0)` 的计分分支把 RAM 当作非零模式：
  gate cost 为 `buffer_size`，delay cost 为 `512 div (512 + 1) = 0`。
- 运行时 `get_ram_pipeline_depth` 只在 `settings[0] == 1` 时读取
  `settings[1]`；mode 2 严格返回 depth 0。因此 mode 2 没有 512 拍延迟，
  运行语义与 mode 0 的 depth-0 RAM 相同。
- depth 0 的逐 tick pass 直接从 backing RAM 读取，随后按电路拓扑执行写入；
  没有隐藏的一拍 pipeline。
- `mode_refresh` 只重放缓存输出，不写 RAM。真正的状态变化仅发生在
  `mode_run` 的逐 tick pass。
- preorder 会为同一个 RAM 关联的 load/save 人工建立
  `load.output -> save.input` 依赖，使 load 必定先于 save 生成。因此已连接的
  同 RAM、同地址、同 tick 操作是 **读旧值，再写新值**。

这已经足够支持 RNG 的单地址状态回授：`RAM.out -> next_state logic -> RAM.in`。
不存在全局的 kind-54/kind-56 类型优先级；只有被关联到同一 RAM 的 load/save
对享有上述人工依赖。互不关联的普通组件仍按常规 Kahn/LIFO 顺序处理。

## 计分与执行分歧

`get_delay_cost(kind=118)` 的有效逻辑为：

```text
if settings[0] != 0:
    delay = 512 div (settings[1] + 1)
else:
    delay = ceil(log2(log2(buffer_size))) + 6
```

`get_gate_cost(kind=118)` 的有效逻辑为：

```text
if settings[0] != 0:
    gate = buffer_size
else:
    gate = 50 * buffer_size
```

但运行时 helper `get_ram_pipeline_depth @ 0x14021A94F` 为：

```text
if len(settings) > 0 and settings[0] == 1:
    return max(settings[1], 0)
return 0
```

所以 mode 2 同时得到 pipelined 计分和 unpipelined 执行。推荐 RNG 状态 RAM
使用 `word_size=32, buffer_size=4, settings=(2, 512, 0)`，地址固定为 0。

证据：

- `.research/rng_score_bypass/ida/ram/score_delay_component.c:35-89`
- `.research/rng_score_bypass/ida/ram/score_gate_component.c:56-75`
- `.research/rng_primitive_zero_audit/ram_enum_acceptance/deserialize_ui/get_ram_pipeline_depth.c`
- callsites `0x1402DA98A`（preorder allocation）与 `0x14044F1BB`（load codegen）

## Pipeline 逐拍语义

### Depth 0

`0x14044F20A..0x14044F20D` 检查 depth；`depth <= 0` 进入直接路径。
逐 tick pass 生成的核心读取表达式是：

```text
load(<Uwidth>, #DATA_<ram> + address - base)
```

load enable 为真时把该值送到输出，并更新 refresh 使用的 simulation-state
缓存。refresh pass (`context.refresh == 1`) 从缓存读输出，不重新访问 backing
RAM。

关键地址：

- 直接读取表达式：`0x14044EE34..0x14044EFA0`
- depth 分支：`0x14044F1BB..0x14044F20D`
- run value / enable / output：`0x14044F2A8..0x14044F645`
- run 输出缓存：`0x14044F76A..0x14044F832`
- refresh 缓存读取：`0x14044F9F2..0x14044FE4D`

### Depth 大于 0

深度 `d > 0` 时，每拍使用 `d + 1` 个 ring slot：

```text
write ring[(tick + 1) mod (d + 1)] = current request
read  ring[(tick + 2) mod (d + 1)] = delayed request
```

拍 `t` 写入的请求在 `t + d` 输出，严格延迟 `d`。ring 状态零初始化，前
`d` 拍 delayed enable 为 0。mode 2 不进入这条路径，也不会用 512 扩容或
索引 ring。

关键地址：

- `tick + 2` 索引：`0x140450050..0x1404501B2`
- 写 request：`0x140450489..0x140450C21`
- 读 delayed request：`0x140450F69..0x140451382`
- 输出与缓存：`0x14045143D..0x1404519A0`

## Refresh 与 Run

`generate_source @ 0x14048B0BD` 两次调用 `add_circuit_code`：

1. `refresh=1`、缩进 4，生成在 `def mode_refresh()` 中；
2. `refresh=0`、缩进 12，生成在 `while .tick < burst_target_tick` 中。

调用证据位于 `generate_source.c:7101-7133` 与 `:7150-7177`。pass flag 被
`add_circuit_code` 写入 context `+0x18`。

RAM save 的 kind-56 分支在 `0x140452AEB` 检查该 flag：refresh 为真时直接
跳过，只有 run pass 会在 `0x1404560A4..0x1404567E1` 生成 `store(...)`。
因此暂停、UI refresh 和追帧 refresh 都不会额外推进 RAM 状态。

## 同 tick Load / Save 顺序证明

`connect_to_ram @ 0x1402BABFD` 在构造图时先处理 kind 54：它记录 load 的
输出点；处理 kind 56 时遍历这些待处理 load 点，并通过
`add_wire_pins @ 0x1402B9EE2` 创建人工 wire。该 wire 在普通输入/输出 net map
中表现为严格的 `load.output -> save.input` 有向依赖。

preorder 随后构造拓扑序 `v825[31]/v825[32]`：

1. `is_ready` 仅在组件全部输入端口达到所需 producer 数后返回真；
2. ready 组件进入序列栈；`preorder_pop` 明确取 `len - 1`；
3. 弹出的组件立即追加到 preorder；它的出边随后增加 consumer readiness；
4. consumer 达到全部输入条件后才入栈。

之后 preorder 按 prototype 属性分成三组。kind 54（RAM load）和 kind 56
（RAM save）的 prototype 都满足：

```text
WORD1(proto.qword8) == 0
WORD2(proto.qword8) == 0
```

所以两者都进入中间组 `v277`。代码只排序第一组 `v279` 和第三组 `v275`，
不排序 `v277`，最终严格连接为：

```text
v480 = v279 & v277 & v275
```

`add_circuit_code` 再按 `v480` 顺序发射语句。由于 RAM 专用人工 edge，关联
save 不可能在 load 前 ready；RNG 自身的 save-value 回授数据线又提供第二条
独立依赖。生成代码必为：

```text
let old = load(...)
let next = f(old, ...)
if save_enable { store(..., next) }
```

同址 load 读取的是 store 前的 backing RAM 值。这一结论不依赖 save value
是否直接使用 load output、不依赖组件在存档中的原始索引，也不依赖两个 RAM
虚拟节点恰好以哪一个索引创建。

证据：

- `.research/rng_score_bypass/ida/ram/preorder.c:3540-3883`
- `.research/rng_score_bypass/ida/ram/preorder.c:4332-4477`
- `.research/rng_primitive_zero_audit/ram_tick_semantics/is_ready.c`
- `.research/rng_primitive_zero_audit/ram_tick_semantics/preorder_pop.c`
- `.research/rng_primitive_zero_audit/ram_tick_semantics/seq_concat.c`
- `.research/rng_score_bypass/ida/ram/connect_to_ram.c`
- `.research/rng_primitive_zero_audit/ram_tick_semantics/add_wire_pins.c`
- `.research/rng_primitive_zero_audit/ram_tick_semantics/preorder_sequence/RESULT.md`
- `.research/rng_primitive_zero_audit/ram_tick_semantics/ram_prototypes.json`

## 部署约束

- 加载 mode 2 RAM 后不要点击 RAM 模式下拉项；UI 只提供 0/1，点击会覆盖
  未知值 2。仅打开属性面板不会写回。
- 同一个 RAM 的关联 load/save 已由 preorder 人工 edge 保证读旧后写新；RNG
  仍应保留自然的 `RAM.out -> next_state -> RAM.in` 数据路径，便于结构审计。
- RNG 首拍仍需显式选择外部 seed；随后选择 RAM 旧状态。next state 同时送
  Output 和 RAM.in，即可保持 66 拍协议。
- 本报告是只读静态结论，未启动游戏、未读取或修改正式存档。最终候选仍需
  游戏内编译、首拍/末拍和 leaderboard 三项实测。

mode 2 的反序列化和 UI 保留证据另见：
`.research/rng_primitive_zero_audit/ram_enum_acceptance/deserialize_ui/RESULT.md`。
