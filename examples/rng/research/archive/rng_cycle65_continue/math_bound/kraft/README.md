# Fixed two-shear direct-output Kraft certificate

## Result

The fixed two-shear, constant-seed, 65-cycle direct-output model is impossible
at total delay at most 9, independently of its XOR2 gate budget.

Of the 64 required linear targets, 32 fail a necessary single-output timing
condition:

```text
feedback: indices 0..18                         (19 failures)
output:   indices 0..9 and 12,13,14             (13 failures)
total:                                             32 failures
```

Consequently, raising the current 92-XOR2 search limit cannot make this fixed
model feasible at delay 9.

The exact minimum typed-tree arrival is `6` for 10 targets, `8` for 22 targets,
and `10` for the 32 failing targets.  Thus every failure needs one additional
even delay unit beyond the delay-9 budget.

## Exact model

The matrices are reconstructed from the canonical definition in
`.research/rng_constant_seed_math/analyze_constant_seed.py`:

```text
A = xorshift32(right 13, left 17, right 5)
T = right-shear(17) o right-shear(13)
B = T*A*T^-1
C = A*T^-1
D = T*(A+I)

q_next = B*q xor D*seed
y      = C*q xor A*seed
```

The certificate also checks the matrix identities and simulates 65 ticks for
the zero seed, all-one seed, one arbitrary seed, and all 32 basis seeds.

## Timing proof

For any one required output, unfold its combinational XOR2 DAG into a binary
formula tree.  Fanout and reconvergence only duplicate subtrees, so this step
does not weaken the timing restriction or remove any supported input variable.

Let `d` be the number of XOR2 gates from a leaf occurrence to the root.

```text
q leaf:    4 + 2*d <= 9  => d <= 2
seed leaf: 0 + 2*d <= 9  => d <= 4
```

Every full binary tree obeys Kraft equality over all leaf occurrences:

```text
sum(2^-d) = 1
```

Every variable in the target support occurs an odd, hence positive, number of
times in the unfolded XOR formula.  A required q variable therefore consumes
at least `1/4` of the Kraft capacity and a required seed variable consumes at
least `1/16`.  Cancelling duplicate occurrences consume more capacity, never
less.  Thus every target must satisfy

```text
|Q|/4 + |S|/16 <= 1
4*|Q| + |S| <= 16.
```

The exact possible support envelope is:

| q support | maximum seed support |
|---:|---:|
| 0 | 16 |
| 1 | 12 |
| 2 | 8 |
| 3 | 4 |
| 4 | 0 |

`kraft_bound.py` independently enumerates every typed full binary tree through
depth 4 and verifies that this envelope is exact, not merely necessary.  The
same enumeration computes each target's exact minimum formula delay.

## Per-target bounds

For a target containing `q` q variables and `s` seed variables, its transitive
cone needs at least `q+s-1` two-input gates.  This follows because a connected
binary cone with `g` gate vertices can connect at most `g+1` distinct source
vertices.  For timing-feasible support pairs, a formula tree reaches this
bound; for a timing-infeasible pair, no finite gate count helps at delay 9.

Feedback target classes:

| `(q,s)` | count | Kraft numerator `/16` | cone XOR2 lower bound | minimum delay | delay 9 |
|---|---:|---:|---:|---:|---|
| `(4,8)` | 3 | 24 | 11 | 10 | impossible |
| `(4,7)` | 5 | 23 | 10 | 10 | impossible |
| `(4,6)` | 6 | 22 | 9 | 10 | impossible |
| `(3,6)` | 5 | 18 | 8 | 10 | impossible |
| `(2,5)` | 8 | 13 | 6 | 8 | feasible alone |
| `(1,2)` | 5 | 6 | 2 | 6 | feasible alone |

Direct-output target classes:

| `(q,s)` | count | Kraft numerator `/16` | cone XOR2 lower bound | minimum delay | delay 9 |
|---|---:|---:|---:|---:|---|
| `(4,4)` | 10 | 20 | 7 | 10 | impossible |
| `(3,6)` | 2 | 18 | 8 | 10 | impossible |
| `(3,5)` | 1 | 17 | 7 | 10 | impossible |
| `(3,4)` | 2 | 16 | 6 | 8 | feasible alone |
| `(2,7)` | 2 | 15 | 8 | 8 | feasible alone |
| `(2,6)` | 8 | 14 | 7 | 8 | feasible alone |
| `(2,5)` | 2 | 13 | 6 | 8 | feasible alone |
| `(1,3)` | 5 | 7 | 3 | 6 | feasible alone |

The gate lower bounds in this table are single-cone bounds and must not be
summed across targets because gates may be shared.  The impossibility result
does not sum them; one failing required target is already sufficient.

## Reproduction

```powershell
python .research/rng_cycle65_continue/math_bound/kraft/kraft_bound.py `
  --json .research/rng_cycle65_continue/math_bound/kraft/certificate.json
```

The JSON contains all 64 q/seed rows, their support sizes, Kraft numerators,
timing decisions, and individual cone gate lower bounds.
