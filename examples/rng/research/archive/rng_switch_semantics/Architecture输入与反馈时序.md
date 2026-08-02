# Architecture Input 与 RNG 反馈总线时序

## 元件与引脚

当前架构关卡的受控输入是 `kind 62 / com_level_input_switched`，不是普通、永久驱动的
Level Input。未旋转时：

```text
control: (+1, -2), U1 input
value:   (+3,  0), U32 output_tristate（本关 word_size=32）
```

`control == 1` 时，运行器调用关卡的 `arch_get_input()`，把返回值写到 `value` 并主动驱动；
其余控制值不调用输入回调，`value` 为 Z。比较是精确的 `== 1`。

RNG 的反馈开关是 `kind 25 / com_switch_word`：

```text
enable: ( 0, +1), U1 input
in:     (-1,  0), U32 input
out:    (+2,  0), U32 output_tristate
```

它同样只在 `enable == 1` 时驱动。当前 RNG 测试脚本的输入来源为：

```text
var initial_seed = 1 + random(0xfffffffe)

def arch_get_input() Int {
    return .initial_seed
}
```

因此每个独立测试产生一个非零 U32 seed；只要输入控制只开启一拍，回调也只调用一次。

## 正确的总线连接

安全的 66-cycle 结构在 word 层直接合并两个三态输出：

```text
Architecture Input.value ----+
                             +---- U32 state Delay.in
Word Switch.out -------------+

state Delay.out -> Splitter -> F(state) -> Maker -> Word Switch.in
                                      +-> Architecture Output.value
```

关键顺序是“先在 U32 层三态汇合，再存入 Delay，最后拆位”。Splitter 不传播 Z，但它位于
主动驱动的 state Delay 之后，所以不需要传播 Z。相反，如果先把 Architecture Input 拆成
32 位再与反馈逐位汇合，Splitter 会把关闭输入的数据面 0 变成主动 0，可能与反馈短路。

## 精确 66-cycle 时序

令 `F` 为关卡规定的 xorshift32，`s0=initial_seed`。控制状态由一个初值为 0、输入恒为 1
的 Bit Delay 产生，记为 `ready`：

| 模拟 tick | tick 开始的 `ready` | Input control / value | Word Switch enable / out | State Delay 旧输出 | Output control / 检查值 | tick 结束捕获 |
| ---: | ---: | --- | --- | --- | --- | --- |
| 0 | 0 | `1` / 主动驱动 `s0` | `0` / Z | `0` | `0` / 不调用检查 | `state=s0`, `ready=1` |
| 1 | 1 | `0` / Z | `1` / 驱动 `F(s0)` | `s0` | `1` / `F(s0)` | `state=F(s0)` |
| 2 | 1 | `0` / Z | `1` / 驱动 `F^2(s0)` | `F(s0)` | `1` / `F^2(s0)` | `state=F^2(s0)` |
| ... | 1 | `0` / Z | `1` / 驱动 `F^t(s0)` | `F^(t-1)(s0)` | `1` / `F^t(s0)` | `state=F^t(s0)` |
| 64 | 1 | `0` / Z | `1` / 驱动 `F^64(s0)` | `F^63(s0)` | `1` / 第 64 个结果 | `state=F^64(s0)` |
| 65 | 1 | `0` / Z | `1` / 驱动 `F^65(s0)` | `F^64(s0)` | `1` / 第 65 个结果，`win` | 不再重要 |

每个 tick 的共享 U32 网都恰好有一个有效驱动：tick 0 是 Architecture Input，tick 1..65
是 Word Switch；从不出现全 Z，也不出现同时驱动。Architecture Output 的 control 直接接
`ready`，所以首拍不会错误提交 `F(0)=0`。

测试脚本的 `count` 初始为 0。前 64 次正确输出分别把它推进到 64；tick 65 的第 65 次
检查进入 `if .count == 64: return win`。因此成绩正好是：

```text
1 个 seed 装载 tick + 65 个输出 tick = 66 cycles
```

## 只读证据

```text
D:\Game\Steam\steamapps\common\Turing Complete\campaign\rng\test.si
SHA-256 B396A9D5BBA76BEC2CEB123478DADC4616B6057894F17775982ED097C62FD50C

src\tc_save_lab\rng_asic.py
SHA-256 C327DE710180D1EC558E5D7CBDB93EFD897E32B754B561AFB539CD24CB2190DB
```

离线复现：

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_switch_semantics\verify_arch_input_timing.py
```

脚本检查 kind、引脚、两个三态源与 U32 Delay 输入的实际共网关系，并对固定 seed 完整
模拟 66 tick、65 个输出。没有启动游戏，也没有读写正式存档。
