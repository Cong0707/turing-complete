# Active-state frontier v2 search

## Outcome

`search_active_state_frontier_v2.cpp` fixes the incumbent-ordering and active-state
projection errors in `search_active_state_tradeoff.cpp`.  Across 39,123,000
proposals it found several new correct Pareto points, but no two-level
XOR2/Switch-XOR3 cover at `gate <= 430`.

The best default-weight point is:

```text
active_hidden=6
distinct_nontrivial=58
distinct_excess_over_4=14
maximum_support=7
optimistic_total_gate=402
switch_proxy_total=542
X=000,000,001,008,014,002,001,001,014,020,000,001,000,024,000,000,000,010,026,001,008,004,006,000,001,008,004,000,000,000,034,000
D=00001100080,02004840000,02204400000,00802200100,00200022000,02400404000,00000000000,00000000000,00000000000,00000000000
```

This improves the old pruned-38 proxy from `549` to `542`.  Glucose42 proves
the restricted exact cover UNSAT at its actual 202-gate logic budget; see
`frontier_v2_smoke_best_cover_glucose42.json`.

Other useful new tradeoff points include:

```text
active  distinct  excess4  max  optimistic
1       34        27       7    305
2       37        26       7    319
3       45        20       7    348
4       45        23       7    353
5       56        16       9    391
7       53        21       7    392
8       56        21       6    406
9       59        15       7    420
10      60        17       7    428
```

At least one selected representative for every active count 1..10 was proved
UNSAT under the exact two-level library and its automatic `430-fixed` budget.
This does not exclude every emitted Pareto point or a deeper/different library.
The active-0 natural encoding is covered by the existing stronger
`rng_depth2_pysat` exclusion at logic budget 240.

## Fixed defects

1. The old score compared `switch_proxy_total` before the hard lower-bound
   defect.  It therefore preferred the impossible `optimistic=446/proxy=506`
   point over the still-eligible `optimistic=399/proxy=549` point.
2. Annealing could not turn a singleton D row into zero, and random D rows were
   never zero.  Active state count therefore could not fall during the main
   loop.
3. `count(D != 0)` charged unreachable and output-unobservable hidden systems.
   The v2 search iteratively projects the strict-zero reachable/observable
   intersection and packs the retained coordinates.
4. The old proxy deduplicated final functions but charged excess per occurrence.
   V2 computes the proxy over distinct nontrivial functions and reports raw
   occurrence excess separately.
5. Old early exit, final exit, and ordering used three incompatible success
   predicates.  V2 never declares synthesis success; exact cover is required.
6. Candidate output now carries seed/restart/iteration, flushes immediately,
   maintains per-active Pareto sets, and runs a 256-seed x 65-output verifier
   before every published line.
7. The dormant greedy cover no longer constructs empty requirements for
   support 5..9, avoiding its latent `chosen_requirement == -1` access.

The new mutation set also includes explicit state activation/deactivation and
semantics-preserving hidden-basis shears.  Proxy excess weight is the optional
fifth command argument, allowing distinct-focused (`4`) and shallow-focused
(`20`) searches without changing source.

## Reproduction

```powershell
g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wpedantic -Wconversion `
  -o .research\rng_switch42_synthesis\search_active_state_frontier_v2.exe `
  .research\rng_switch42_synthesis\search_active_state_frontier_v2.cpp

.\.research\rng_switch42_synthesis\search_active_state_frontier_v2.exe `
  500000 12 202608020432 20 `
  > .research\rng_switch42_synthesis\frontier_v2_w20_500k_seed202608020432.log

.\.venv\Scripts\python.exe `
  .research\rng_switch42_synthesis\optimize_pruned38_pysat.py `
  --log .research\rng_switch42_synthesis\frontier_v2_selected_shallow.log `
  --candidate all --solver glucose42 --timeout-seconds 40 `
  --output .research\rng_switch42_synthesis\frontier_v2_selected_shallow_cover_glucose42.json
```

Search seeds were `202608020401`, `202608020411..413`, `202608020421..422`,
and `202608020431..432`.  Measured peak working set was 4.59 MiB per search
process.  All emitted candidates reported `verified=256x65`.

No game process was started.  No formal save, `levels.txt`, or shared `src`
file was read or modified by this work.
