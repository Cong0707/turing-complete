# Arbitrary-T delay-9 Kraft SMT result

## Outcome

Feasibility for an arbitrary invertible 32-bit encoding `T` remains
**unknown**.  No SAT witness and no UNSAT certificate was obtained.

The exact necessary-condition model is

```text
B = T A T^-1
D = T(A+I)
C = A T^-1

4*wt(B_i) + wt(D_i) <= 16
4*wt(C_i) + wt(A_i) <= 16
```

Eliminating the symbolic inverse with `K=A(A+I)` gives the equivalent basis
equations used by the solver:

```text
D A = B D
C D = K
```

Because `K` is invertible, `C D=K` also proves that both `C` and `D` are
invertible.  Every `B` row selects one to three rows of `D`; every `C` row
selects at most two or three rows according to its fixed output Kraft capacity.

## Complete symmetry break

Column permutation of `C` is only a relabelling of the internal q coordinates.
Since invertible `C` has a perfect matching, one may choose such a matching and
permute it onto the diagonal.  Therefore fixing `C_ii=1` for every row is WLOG;
it preserves all row weights and each paired feedback Kraft load.

This symmetry break changed the output-only calibration from timeout to SAT:

| run | result | elapsed | Z3 max memory |
|---|---:|---:|---:|
| output constraints only, diagonal `C` | SAT | 3.397 s | 166.18 MB |
| output + `wt(B_i)<=3`, no `D` caps | unknown (timeout) | 120.147 s | 379.05 MB |

The second run is a strict relaxation of the requested model: it omits
`wt(D_i) <= 16-4*wt(B_i)`.  Since even this weaker problem timed out, the full
model was not launched after the parent task requested search convergence.

Machine-readable run records:

```text
kraft_smt_bv_diag_output.json
kraft_smt_bv_diag_no_seed_caps.json
```

## Strict universal bounds

The independent distance/forest certificate proves necessary facts for every
possible `T`, but they do not yet contradict the Kraft caps:

```text
rows with wt(D)>=2,3,4,5,6  >= 8,8,8,7,2
sum_i wt(D_i)               >= 65
rows with wt(B)<=2          >= 7
rows with wt(B)=3           <= 25
sum_i wt(B_i)               >= 35
```

The key witness is the 15 output rows with `C` capacity two.  Their supports
form a forest; exact pairwise distances among the corresponding fixed `K` rows
force at least seven basis rows `D_i` to have weight at least five.  Their
paired feedback Kraft inequalities then force at least seven `B_i` rows to
have weight at most two.

Certificate artifacts:

```text
kraft_smt_math_distance_bound.py
kraft_smt_math_distance_bound.json
kraft_smt_math_distance_bound.md
```

## Reproduction

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_cycle65_continue\kraft_smt_bv.py `
  --relax output-only --diagonal-c --timeout-ms 30000 --memory-mb 448 `
  --output .research\rng_cycle65_continue\kraft_smt_bv_diag_output.json

.\.venv\Scripts\python.exe `
  .research\rng_cycle65_continue\kraft_smt_bv.py `
  --relax no-seed-caps --diagonal-c --timeout-ms 120000 --memory-mb 400 `
  --output .research\rng_cycle65_continue\kraft_smt_bv_diag_no_seed_caps.json

.\.venv\Scripts\python.exe `
  .research\rng_cycle65_continue\kraft_smt_math_distance_bound.py
```

No command in this work starts the game or reads/writes the live save.
