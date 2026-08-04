# HISTORY

## 2026-08-04

- 生成并独立验收严格 fully-driven `10/3/30` FullAdder：真实 v15 roundtrip、pin mapping、
  两个 tri-state driver 的单一 Sum owner、8 行真值、时序、成本、几何和连通性均通过。
- 完成 FullAdder `gate<=9,delay<=3` 的 90 分片物理闭包：strict 与 Z-false 两种输出策略、
  paid `1..9`、normalizer `0..4`，结果 `90/90 UNSAT`，独立清单审计通过。
- 证明 `7/4` 与 `10/3` 同时保留在 client/saved-level frontier；记录默认 minimum-gate
  选择 `7/4`、minimum-delay 选择 `10/3`，禁止单实例拼接虚构 `7/3`。
- 增加任意多输出 truth-tuple exact physical wrapper，支持逐输出 arrival、Switch/BUS、
  Maker/Splitter normalizer、physical owner，并用已知 `10/3` 正回归校准。
- 完成权威 `80/7` bit0 `(SUM=0x96,MAJ=0xe8)`、`SUM<=4/MAJ<=2`、`gate<=9`
  的 45 分片 strict physical connected-cut 闭包：`45/45 UNSAT`，独立审计通过；结论明确
  限定为局部 cut，不外推为全局 `79/7` 下界。
- 完成 FullAdder D1 结构枚举：65 个一层 ordinary instance、25 个 raw Switch pair 与
  direct/normalized BUS 均不能产生三输入 parity，证书状态 `verified_unreachable`。
- 找到并独立 replay `17/2` FullAdder 物理上界：5 ordinary、6 Switch、2 normalizer；
  mismatch/conflict/undriven/partition/dead-component 全零。六个 `gate=16` 重点 composition
  为 UNSAT，但尚非完整闭包，未宣称 `17/2` gate 最小。
- 总报告：`2026-08-04-FullAdder-10-3与双前沿及局部闭包审计.md`。
- 全部操作限于 `.research`；未启动游戏、未改正式状态、未 stage/commit/push。
