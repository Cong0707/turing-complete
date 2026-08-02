# RNG B/C depth-two XOR exact model

## Canonical form

Treat every GF(2) row as a bit mask over the 32 primary inputs and deduplicate
all rows in the jointly synthesized matrices.  Let:

- `R` be the distinct target rows from `B union C`;
- `P0 = {r in R : wt(r)=2}` be pair-valued target rows;
- `F = {r in R : wt(r) in {3,4}}` be rows requiring a final layer gate;
- `D(r)` be the possible layer-one pair requirements for final row `r`.

For a weight-three row, `D(r)` has three singleton alternatives: choose any
two of the three support bits as a layer-one pair, then XOR it with the third
primary input.  For a weight-four row, `D(r)` has the three perfect matchings
of its support, and each alternative requires both disjoint layer-one pairs.

Introduce one Boolean `x[p]` for every relevant input pair.  The exact model
is:

```text
x[p] = 1                                      for every p in P0
OR over d in D(r) (AND over p in d x[p])      for every r in F

minimize  G = |F| + SUM_p x[p]
```

The equivalent accounting form is:

```text
G = |{r in R : wt(r)>=2}| + SUM_{p not in P0} x[p]
  = distinct non-unit target gates + extra non-target pair gates
```

This counts duplicate `B`/`C` rows once and permits arbitrary fanout.

The restriction is exact for XOR depth at most two, not a heuristic.  Every
useful layer-one gate is the XOR of two primary inputs.  A weight-three final
must be a primary input XOR a disjoint pair; a weight-four final must XOR two
disjoint pairs.  A weight-two target produced in layer two can be moved to
layer one with the same one-gate cost and weakly more sharing opportunity, so
all such targets may be forced into `P0`.  Unit targets are wires.  Rows of
weight greater than four are impossible at depth two.

## Solver encodings

The Z3 implementation in `solve_depth2_pairs.py` uses the formula above
directly.  It binary-searches an at-most pair budget and finally checks that
`optimum-1` is UNSAT, rather than relying only on an optimizer's reported
lower bound.

For CP-SAT, introduce `y[r,d]` for every decomposition alternative:

```text
SUM_d y[r,d] >= 1
y[r,d] <= x[p]                 for every p in d
x[p] = 1                       for p in P0
minimize SUM_p x[p]            (`|F|` is constant)
```

Optional tightening is `x[p] <= required[p] + SUM_(r,d containing p) y[r,d]`.

For plain SAT, use the same `y` variables.  Emit one clause containing every
`y[r,d]`, plus `(not y[r,d] or x[p])` for each required pair.  Unit clauses
force `P0`.  Add a totalizer or sequential-counter encoding of
`SUM x[p] <= K`; incremental or binary search over `K` proves the optimum.
The reverse Tseitin clause for `y <-> AND x` is optional for satisfiability,
but harmless.

## Exact results

Fixed two-shear encoding from `rng_depth2_network/search_and_verify.py`:

| rows | unit | pair targets | finals | selected pairs | extra pairs | XOR optimum |
|---|---:|---:|---:|---:|---:|---:|
| B | 5 | 8 | 19 | 27 | 19 | 46 |
| C | 5 | 12 | 15 | 27 | 15 | 42 |
| B union C | 5 | 12 | 34 | 27 | 15 | **61** |

The joint model uses 119 relevant pair variables.  Separate synthesis would
cost `46+42=88`, so joint target/pair sharing saves 27 XOR gates.

Feasible annealing frontier from `rng_joint_search_resume/frontier-68.json`:

| rows | unit | pair targets | finals | selected pairs | extra pairs | XOR optimum |
|---|---:|---:|---:|---:|---:|---:|
| B | 4 | 8 | 20 | 32 | 24 | 52 |
| C | 3 | 9 | 20 | 29 | 20 | 49 |
| B union C | 4 | 14 | 34 | 38 | 24 | **72** |

The joint model uses 127 relevant pair variables and proves pair budget 37
UNSAT.  Thus the existing greedy `B/C=72` result is already exact.  `T` is
independently exact at 33, so the existing separate total 105 is exact under
phase separation.  Ideal global sharing across `T/B/C` lowers this frontier
to an exact 99 XOR: there are 67 distinct non-unit targets and 32 additional
pairs.  The JSON's lower bound 68 is phase-separated; the global union is 67
because `T` and `B` share row `0x80044002`.  The exact 99 remains above the
fixed two-shear union's 95.

## Reproduction

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_joint_sat\agent_joint\solve_depth2_pairs.py `
  .research\rng_joint_search_resume\frontier-68.json B C
```

The emitted JSON includes selected pair masks, an explicit decomposition for
every final row, and the last UNSAT budget.
