# RNG Switch42 proxy v2 cost model

## Result

The old score

```text
198 + 5*active_hidden + 3*distinct_targets + 10*excess_over_4
```

is not a useful approximation of the shared two-level cover.  It reverses the
ordering of the existing current42 and pruned38 points.  Proxy v2 has three
tiers:

1. an O(number of targets) calibrated weight score for the annealing loop;
2. an O(sum support^2) pair-aware score for near-incumbent proposals;
3. an offline multi-start feasible cover over the real restricted-library
   objective.

The newest six-hidden-state `beam6_proxy497` point is the best of the audited
points, but is still 101 gates above the 430 target:

```text
active_hidden=6, fixed=228
targets=53, weights={2:20, 3:6, 4:20, 5:4, 6:2, 7:1}
weight proxy total=566
pair proxy total=562
deterministic greedy total=588
256-restart bounded-pair local cover: logic=303, total=531
```

The `303/531` result is a feasible upper bound in the restricted
XOR2/Switch-XOR3 library.  It is not an optimum or a lower-bound certificate.

## Exact objective

One cost unit is three gates.  For each distinct nontrivial H/O target choose
a partition into at most three blocks, each of size at most three:

```text
pair group cost       = 1 unit  (native XOR2)
triple group cost     = 4 units (Switch-XOR3)
final cost, 1/2/3 groups = 0/1/4 units
```

Pair/triple group costs are paid once globally.  Thus

```text
logic_units = sum(cost of globally used groups)
            + sum(final cost of each selected target partition)
fixed_gate  = 5*(32 + active_hidden) + 32 + 6
total_gate  = fixed_gate + 3*logic_units
```

Inactive hidden columns must be masked before deduplicating and scoring
targets.  Compacting the surviving columns is optional because popcount and
subset relations are unchanged by gaps.

## Tier A formula

Let `cw` be the number of distinct nontrivial projected targets of weight `w`.
The inner-loop estimate, in milli-units, is:

```text
U_A = 9922
    + 984*c2 + 1819*c3 + 1884*c4 + 4421*c5
    + 4748*c6 + 7215*c7 + 10530*c8 + 12377*c9

logic_gate_A = round(3*U_A/1000)
total_gate_A = fixed_gate + logic_gate_A
```

Score unsupported weight above nine before this value.  The implementation is
`weight_estimate()` in `proxy_v2_cost_formula.hpp`.

## Tier B formula

Tier B enumerates all pair subsets of the target supports.  Define:

```text
forced_hits = incidences where a weight-2 target is a subset of a larger target
pair_repeat = sum(max(pair_frequency-1, 0))
pair_ge2    = number of pairs with frequency >= 2
pair_ge3    = number of pairs with frequency >= 3
```

Its milli-unit estimate is:

```text
U_B = 6707
    + 1063*c2 + 1639*c3 + 1756*c4 + 4066*c5
    + 4235*c6 + 6563*c7 + 9425*c8 + 11347*c9
    + 32*forced_hits - 13*pair_repeat + 210*pair_ge2 - 191*pair_ge3
```

Use Tier A for every proposal and Tier B only for close proposals or polishing.
Run the offline cover for every printed global best.

## Calibration

`proxy_v2_cost_dataset_hq.json` contains 305 distinct historical valid states.
Labels use eight coordinate-descent restarts plus bounded top-4 two-target
moves.  A stable hash split produced 245 training and 60 held-out points.

Held-out error against these sharing-aware labels:

```text
model                 MAE             RMSE            Pearson  Spearman
old proxy             22.772 units    26.629 units    0.873    0.816
Tier A weights          3.220 units     4.063 units    0.993    0.987
Tier B pair-aware       3.030 units     3.828 units    0.994    0.990
```

This is about 9.7 gate MAE for Tier A and 9.1 gate MAE for Tier B.  Absolute
estimates remain conservative around the best current region; ranking is the
primary use.

Key calibration points using a 256-restart/top-12 offline run:

```text
point       old    Tier A  Tier B  greedy  local logic/total
beam6       497    566     562     588     303 / 531
current42   506    636     633     656     372 / 620
pruned38    549    628     629     645     384 / 612
```

An independent sibling implementation reported feasible totals `537`, `626`,
and `618` for beam6/current42/pruned38 respectively.  The six-gate improvement
from this evaluator comes from more restarts and bounded pair moves; the close
agreement cross-checks the objective and target construction.

## Reproduction

```powershell
python .research\rng_switch42_synthesis\proxy_v2_cost_eval.py `
  --builtin both --restarts 256 --pair-top-k 12

python .research\rng_switch42_synthesis\proxy_v2_cost_eval.py `
  --line-file .research\rng_switch42_synthesis\active_tradeoff_2m_r4_seed20260802041.log `
  --name candidate --restarts 96 --pair-top-k 8

python .research\rng_switch42_synthesis\proxy_v2_cost_calibrate.py `
  --restarts 8 --pair-top-k 4 `
  --output .research\rng_switch42_synthesis\proxy_v2_cost_dataset_hq.json

g++ -std=c++20 -Wall -Wextra -pedantic -fsyntax-only `
  .research\rng_switch42_synthesis\proxy_v2_cost_formula_smoke.cpp
```

Verification completed:

```text
Python py_compile: PASS
C++20 -fsyntax-only with warnings: PASS
log-line X/D parser reproduces current42 counts: PASS
256-restart calibration is deterministic for the supplied seed: PASS
single-process design: no SAT solver, no dense state simulation, no large matrix
```

The largest persisted calibration dataset is about 252 KB.  Runtime structures
are bounded by at most 74 target option lists and the pair/triple group maps;
they are far below the 1 GB process limit.  Peak RSS was not separately
instrumented, so no stronger measured-memory claim is made.

## Files

```text
proxy_v2_cost_eval.py             offline evaluator and local cover
proxy_v2_cost_calibrate.py        reproducible historical calibration
proxy_v2_cost_formula.hpp         dependency-free C++ Tier A/B functions
proxy_v2_cost_formula_smoke.cpp   compile smoke test
proxy_v2_cost_calibration.json    current42/pruned38 256-restart output
proxy_v2_cost_beam6.json          beam6 256-restart output
proxy_v2_cost_dataset_hq.json     frozen 305-point calibration data
```

SHA-256:

```text
3DF34D485C1E35A50EFC72EEE2A07E0B903BFA27503BD46709F0E7B9DAC3ACB4  proxy_v2_cost_eval.py
0DEDCB3833907316D67A573BA430487EE6C4FE3A3EE64BE7D02AEFEA45DF4AB4  proxy_v2_cost_calibrate.py
2E41590DE94758F1C5DE02C5515F674D4D3BA32F67693E0B37C88A95EBDEA965  proxy_v2_cost_formula.hpp
B4B40C0907214624ECAA0E742738F8CC4ED81B341438DA2AEA53AD4B1CDD9220  proxy_v2_cost_calibration.json
E69F582BF3A4DDC2A19DBF16D228C10709D61F1335AD6F6747BC4D393131D0BD  proxy_v2_cost_dataset_hq.json
```
