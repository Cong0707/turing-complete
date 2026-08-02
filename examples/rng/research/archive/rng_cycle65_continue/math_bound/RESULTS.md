# Fixed two-shear constant-seed direct-output bound

## Result

For the fixed model

```text
feedback = B*q xor D*seed
output   = C*q xor A*seed
T        = (I+R17)(I+R13)
q arrival = 4, seed arrival = 0, XOR2 delay = 2
```

`total delay <= 9` is impossible at **every** XOR2 gate budget.  Therefore the
specific target `delay<=9, XOR2<=92` is UNSAT.  The gate-budget condition is
not needed for this conclusion.

## Per-target Kraft bound

Unfold the cone of one requested signal from a shared/reconvergent XOR DAG
into a binary XOR formula.  A supported primary input has odd, hence nonzero,
leaf multiplicity.  Every root-to-leaf path must obey the arrival limit:

```text
q leaf:    4 + 2*depth <= 9  => depth <= 2
seed leaf: 0 + 2*depth <= 9  => depth <= 4
```

The leaf depths of a binary tree satisfy Kraft equality.  Keeping just one
occurrence of each required input gives the necessary condition

```text
|Q|/4 + |S|/16 <= 1
4*|Q| + |S| <= 16.
```

Sharing cannot evade the condition: unfolding fanout duplicates subtrees,
and reconvergent cancellation adds an even number of leaf occurrences.  Both
operations can only increase Kraft load.

The fixed matrices give 32 violating targets:

```text
feedback[0..18]             19
output[0..9, 12, 13, 14]    13
```

For example, `feedback[0]` has `|Q|=4`, `|S|=8`, so its Kraft load is
`4/4 + 8/16 = 3/2`.  The support argument alone certifies that the maximum
target delay is at least 10.

## Shared-DAG gate bound

This is a supplementary bound; it is not needed after the Kraft obstruction.

1. The 64 complete `(q,seed)` target rows are distinct, non-input forms and
   have GF(2) rank 64.  Thus at least 64 distinct XOR gate outputs are targets.
2. There are 34 distinct target q projections of weight 3 or 4.  At q depth
   at most two, each target's producing gate must combine raw q singletons
   and/or first-level q-pair signals.
3. A first-level q-pair signal must be a pure `q_i xor q_j`: putting seed logic
   into either parent would add another q-path XOR level.  Every complete
   target has nonzero seed support, so these pair gates cannot be any of the
   64 target gates.
4. The exact arbitrary-fanout pair-cover problem has 119 candidate pairs.
   A 27-pair witness covers all 34 heavy rows, while Z3 proves budget 26
   UNSAT.

Hence every delay-nine network in this fixed model would require at least

```text
64 target gates + 27 non-target q-pair gates = 91 XOR2 gates.
```

The pair-cover solver deliberately relaxes seed semantics, target production
order, and all sharing restrictions beyond q depth.  Those relaxations can
only lower its gate count, so 91 is a necessary lower bound.  It does not by
itself refute a 92-gate budget; the per-target Kraft result does.

## Reproduction

Generate a fresh certificate:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
.\.venv\Scripts\python.exe `
  .research\rng_cycle65_continue\math_bound\prove_bound.py `
  --output .research\rng_cycle65_continue\math_bound\certificate.json
```

Rebuild all matrices, rerun the 26-pair UNSAT check, and compare the complete
JSON certificate:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
.\.venv\Scripts\python.exe `
  .research\rng_cycle65_continue\math_bound\prove_bound.py `
  --verify-existing .research\rng_cycle65_continue\math_bound\certificate.json
```

## Strictness scope

The UNSAT result is strict for exact implementation of the stated 64-row
linear map, with `q` and `seed` treated as independent primary variables, in
the fixed two-shear, constant-seed, direct-output, bit-level XOR2 model and
the stated arrival/delay accounting.  It does not exclude a circuit optimized
only for a smaller reachable/sample care set, a different encoding `T`, a
different state architecture, non-XOR2 primitives, or delay 10.  No game
process or live save is accessed.
