# Active-tradeoff proxy506 exact-cover result

## Outcome

The duplicated candidate on lines 1 and 2 of
`active_tradeoff_smoke_seed20260802021.log` was parsed once and checked with
Glucose42.  It is UNSAT under the 430-gate target.

```text
pruned state bits:             42
active hidden rows:            10 (indices 0..9)
fixed gate cost:               248
automatic logic budget:        182
distinct nontrivial targets:   66
optimistic logic lower bound:  198
optimistic total lower bound:  446
exact cover status:            UNSAT
variables:                     63168
clauses:                       188775
build seconds:                 0.1233
solve seconds:                 1.9159
measured peak working set:     67.04 MiB
```

The exact library is the existing two-level globally shared cover:

* XOR2 group: 3 gates, delay 2;
* verified Switch-XOR3 group: 12 gates, delay 2;
* two groups use a final XOR2;
* three groups use a final Switch-XOR3.

All partitions into at most three blocks of at most three leaves were
enumerated.  There were 371 possible shared pair/triple groups and 697 target
partition options.

## Care-space lower bound

As an additional optimistic test, H and O targets were compared only on the
state space common to cycles 1 through 64.  This deliberately ignores the
H-only tick 0 and O-only tick 65 and therefore can only make sharing easier.

```text
common-care reachable rank:       38
distinct target classes:          70
distinct state-wire classes:      39
distinct non-wire target classes: 66
gate-output lower bound:           66 * 3 = 198
total lower bound:                 248 + 198 = 446
```

Consequently, cross-H/O don't-care sharing cannot bring this candidate below
430 gates, even before pair/triple intermediate-node costs are counted.

## Verification and artifacts

The pruned realization passed 256 seeds with 65 outputs per seed before the
cover instance was built.  No hidden row was pruned for this candidate.

Command:

```powershell
python .research\rng_switch42_synthesis\optimize_pruned38_pysat.py `
  --log .research\rng_switch42_synthesis\active_tradeoff_smoke_seed20260802021.log `
  --candidate all --solver glucose42 --timeout-seconds 120 `
  --output .research\rng_switch42_synthesis\active_tradeoff_smoke_proxy506_cover_glucose42.json
```

Artifacts:

```text
active_tradeoff_smoke_proxy506_cover_glucose42.json
SHA-256 4b7c3c821b82a48b80b68cb76ac13505275a8de3881593dd16b166a087f73e13

pruned38_cover_budget202_parametric_regression.json
SHA-256 a51638f4e673957a1ee07c1ff6fa1d53d99093fd5dcdf08f244ff3ac91c203f8
```

The historical built-in candidate still prunes to 38 states and reproduces
the previous 57-target, budget-202 Glucose42 UNSAT result.
