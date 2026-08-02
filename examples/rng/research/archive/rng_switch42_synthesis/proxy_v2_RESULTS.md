# RNG Switch42 proxy-v2 search results

## Outcome

No candidate in this run reaches `gate<=430` in the exact two-level
XOR2/Switch-XOR3 library.  Two new points improve different search metrics:

| candidate | active hidden | targets | old proxy | feasible cover | exact at 430 |
|---|---:|---:|---:|---:|---|
| fixed-k1 | 1 | 35 | 568 | 327 logic / 530 total | UNSAT (Glucose42) |
| beam6 | 6 | 53 | **497** | 303 logic / 531 total | UNSAT (Glucose42 + CaDiCaL) |

The fixed-k1 point is the lowest feasible-cover upper bound found.  The beam6
point is the first fully verified state in this branch below old proxy 506.

## Search audit

Three issues explain why `search_active_state_tradeoff.cpp` stayed at 506:

1. `greedy_xor_count()` is defined but never called by `evaluate()`.
2. Annealing cannot mutate a weight-one D row to zero because removal is
   guarded by `popcount(row)>1`; random D rows are also always nonzero.
3. The old objective counts targets and excess weight but does not measure
   shared pair/triple groups.  It ranks current42 (506) ahead of pruned38
   (549), while the stronger offline covers rank them 620 versus 612.

Proxy v2 masks inactive hidden columns, permits D=0, and uses the actual
restricted-library cover objective offline.  A calibrated target-weight score
and pair-incidence score are available for the hot loop.  On a 60-point held
out set their errors are about 9.7 and 9.1 gates MAE, versus 68.3 gates for the
old proxy.

## Best feasible-cover point

The fixed-k1 search with seeds `20260802083` and `20260802084` independently
converged to the same state:

```text
X=000,000,000,000,000,000,000,000,
  000,000,000,000,001,000,000,000,
  000,000,000,000,000,000,000,000,
  000,001,000,000,000,000,000,000

D=00142002000,00000000000,00000000000,00000000000,00000000000,
  00000000000,00000000000,00000000000,00000000000,00000000000
```

Statistics:

```text
active_hidden=1
fixed_gate=203
distinct_nontrivial=35
weights={2:2, 3:6, 4:14, 5:3, 6:7, 7:3}
feasible_cover=327 logic / 530 total
independent greedy=330 logic / 533 total
verified=256 seeds x 65 outputs
```

The exact model has a logic budget of 227 gates (`75` three-gate units).
Glucose42 proved it UNSAT in 11.72 seconds with 433,622 clauses.  The
certificate already contains the projected H/O rows and the `256x65`
verification record.

## Lowest old-proxy point

The structural column beam found:

```text
X=002,001,020,010,008,002,000,020,
  000,008,000,000,004,000,000,000,
  000,002,001,020,010,008,002,000,
  020,004,008,000,000,000,000,000

D=00000084042,00100440020,00042003000,00204400200,00800300100,
  01001100080,00000000000,00000000000,00000000000,00000000000
```

Statistics:

```text
active_hidden=6
fixed_gate=228
distinct_nontrivial=53
weights={2:20, 3:6, 4:20, 5:4, 6:2, 7:1}
old_proxy=497
best offline cover=303 logic / 531 total
verified=256 seeds x 65 outputs
```

Five beam seeds (`20260802054`, `57`, `58`, `59`, `60`) reproduced this point
or a hidden-column permutation.  Glucose42 and CaDiCaL independently proved
`logic<=202` UNSAT.

## Search coverage and memory

Completed runs include a `100k x 4` annealing batch, one `20k x 3` smoke
batch, five medium structural-beam seeds, and two fixed-k seed sweeps for
`k=1..3`.  The annealing batch did not beat the natural-state fractional score;
the structural beam supplied the useful candidates.

The C++ proxy searches use only target option lists and pair/triple maps.  The
alternate C++ search reported about 4 MiB peak working set.  The Python cost
calibration was not separately instrumented for peak RSS; its largest stored
dataset is 252 KiB and it uses no SAT solver or dense simulation matrix.  No
proxy process remains running, and no observed run approached the 1 GB limit.

## Evidence

```text
proxy_v2_alt_k1_exact430_glucose.json
  FE989FF0F4C53DD9951C3C54F7FBD38C13EDBC1406411F87AEC0ECA479C63BB7

proxy_v2_beam_proxy497_exact_glucose42.json
  C4A1B6A8D599920DC39C5A42A3A110FB39C310C04EE1BC4153A5E9D175F250F7

proxy_v2_beam_proxy497_exact_cadical.json
  6B1714218304678F76EA9305EA0EAA7FD47DDEBA966BE0BAB7D8B0974DA53937
```

Implementation and calibration details are in `proxy_v2_cost_REPORT.md`,
`proxy_v2_cost_eval.py`, `proxy_v2_cost_formula.hpp`,
`proxy_v2_alt_search.cpp`, `proxy_v2_search.cpp`, and
`proxy_v2_cost_audit.py`.

No game process, save, `levels.txt`, or shared source file was touched.
