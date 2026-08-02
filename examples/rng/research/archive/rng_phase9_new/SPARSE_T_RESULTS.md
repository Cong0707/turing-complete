# Delay-9 independent initialization: sparse-T results

## Model and target

All state elements start at zero.  Seed loading and steady operation are

```text
tick 0: q = T*s
steady: q' = B*q,  B = T*A*T^-1
output: y = C*q,  C = A*T^-1
```

If every row of `T` has support at most two, seed loading uses at most one XOR
before the fixed state-input OR and the control path remains within delay 9.
The implementation estimate is

```text
gate = 198 + 3 * (XOR_T + XOR_BC)
target gate <= 430  <=>  XOR_T + XOR_BC <= 77
```

No script in this directory imports save-writing code or starts the game.

## Exact structure

An invertible binary matrix with row support at most two is exactly an
unordered rooted forest basis: pair rows are forest edges, and every connected
component has exactly one singleton root.  Conversely every such rooted forest
is invertible.  In a canonical orientation,

```text
T[node]    = e_node                         for a root
T[node]    = e_node xor e_parent[node]      otherwise
T^-1[node] = xor of q coordinates on the root path
```

This is encoded independently by `forest_smt.py` and
`theory/row2_basis_sat.py`.

## Best verified frontier

`sparse-best-bad6.json` is structurally valid (`C*T=A`, `T*C=B`) and has:

```text
T pair rows / init XOR: 18
B/C weight histogram:   wt2=8, wt3=10, wt4=40, wt5=5, wt6=1
heavy rows:              6
linear excess over 4:    7
squared excess over 4:   9
total B/C row weight:    237
```

The heavy rows are `B[21,28,30]` (weight 5), `C[6,10]` (weight 5), and
`C[23]` (weight 6).  `sparse-best-bad6-excess7.json` is only a permutation of
the same 32 T row masks.  Its reported `7` is linear excess while the original
file's `9` is squared excess; it is not a structural improvement.

## Closed local neighborhoods

`local_radius2.cpp` exhausts every replacement of one or two T rows by any
nonzero mask of support at most two, rejecting singular matrices and
recomputing B/C exactly.

```text
one-step invertible:  1,764
two-step attempted:   29,748,096
two-step invertible:  3,248,442
best heavy:           6
best linear excess:   7
best squared excess:  9
```

Thus the current forest is a strict local minimum for feasibility through two
arbitrary sparse-row replacements.  `local-r2.log` and `local-r2.jsonl` contain
the replay output.

The rooted-forest SMT independently proved the full feasible target absent at
parent-change radius 1, 2, and 3 from the same forest.  Radius 4 timed out:

```text
forest-radius1.json: UNSAT, 0.62 s
forest-radius2.json: UNSAT, 1.39 s
forest-radius3.json: UNSAT, 17.57 s
forest-radius4.json: unknown(timeout), 240.07 s
```

A guided relaxed query (`max row <=6`, at most five heavy rows) proved radius 1
UNSAT; radius 2 and 3 timed out at 60 seconds.  The unrestricted structural
bit-vector model timed out at 30 seconds / 480 MB.  None of these timeout
records is an UNSAT claim.

## Gate lower bound

Let `r` be the number of pair rows in T, `u` the number of unit-valued B edge
outputs, and `p` the number of extra first-layer pair gates not already B/C
targets.  C has 32 independent, non-unit rows.  Every forest edge contributes
a distinct B target outside C.  Therefore

```text
XOR_BC >= 32 + r - u + p
XOR_total >= 32 + 2*r - u + p
```

Only eight natural row pairs can yield a unit B edge, so `u<=8`.  It follows
that every `r>=27` basis misses the leaderboard target.  At `r=26`, a candidate
requires at least seven of those eight special unit conditions and essentially
no extra pair cover (`u=7,p=0`, or `u=8,p<=1`).

The exact full-B/C CNF with `r=26,u=8` is UNSAT
(`theory/full-r26-u8.json`, CaDiCaL 1.9.5, about 30 seconds).  The eight
`u=7` omission branches remain open; the first branch and the aggregate
`u>=7` run timed out under several 60-second solver shards.

## Replay

```powershell
g++ -std=c++20 -O3 -DNDEBUG -o `
  .research/rng_phase9_new/local_radius2.exe `
  .research/rng_phase9_new/local_radius2.cpp
./.research/rng_phase9_new/local_radius2.exe `
  .research/rng_phase9_new/sparse-best-bad6-excess7.json `
  .research/rng_phase9_new/local-r2.jsonl `
  2> .research/rng_phase9_new/local-r2.log

./.venv/Scripts/python.exe .research/rng_phase9_new/theory/row2_basis_sat.py `
  --engine pysat --leaderboard-bound --exact-pairs 26 --min-unit-b 8 `
  --pysat-solver cadical195 `
  --output .research/rng_phase9_new/theory/full-r26-u8.json
```

## Missing named artifact

No `feasible_30013_19046662.json` exists in the shared repository.  Seed 30013
was replayed with both saved row orderings, with restart `250000` and `0`, and
with the legacy shear-only executable; none reached a feasible B/C basis or
emitted step 19,046,662.  A source matrix or the exact producing command is
required to reconstruct that named artifact; it must not be fabricated from
the current near-feasible frontier.
