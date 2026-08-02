# Constant-seed, 65-cycle research

Research-only workspace for the zero-initial-state model

```text
q_next = B*q xor D*seed
output = C*q xor A*seed
```

with `q` leaf arrival 4, seed leaf arrival 0, XOR2 delay 2, total delay at
most 9, and at most 92 XOR2 gates.

Nothing in this directory reads or writes the live game save.

## Strict fixed-encoding result

`delay <= 9` is impossible for this fixed encoding at every XOR2 gate budget.
Unfolding any output DAG into a binary formula gives the necessary Kraft bound

```text
q_weight / 4 + seed_weight / 16 <= 1
4*q_weight + seed_weight <= 16
```

because a `q` leaf arriving at 4 can traverse at most two XOR2 gates before
delay 9, while a seed leaf arriving at 0 can traverse at most four.  Nineteen
feedback targets and thirteen output targets violate the bound.  For example,
feedback bit 0 has four independent q leaves and eight independent seed
leaves, giving Kraft load `4/4 + 8/16 = 3/2`.

Sharing cannot evade the proof: unfold sharing into repeated formula leaves.
Every required independent leaf must occur an odd, hence nonzero, number of
times; cancellation only increases the unfolded leaf count.

Reproduce and write the research certificate:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
.\.venv\Scripts\python.exe `
  .research\rng_cycle65_continue\verify_two_shear_kraft.py `
  --output .research\rng_cycle65_continue\two_shear_kraft_certificate.json
```

Verify the saved certificate by rebuilding all matrices and replaying 69 seeds
for 65 outputs each:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
.\.venv\Scripts\python.exe `
  .research\rng_cycle65_continue\verify_two_shear_kraft.py `
  --verify-existing .research\rng_cycle65_continue\two_shear_kraft_certificate.json
```

The independent `math_bound/prove_bound.py` certificate also proves a
supplementary 91-XOR lower bound for that fixed map (64 distinct target gates
plus an exact 27-pair q-cover).  The Kraft obstruction is stronger because it
rules out delay 9 at every gate budget.

## Finite encoding-family result

`verify_phase_free_or.py` exhaustively checks all 250,047 ordered products of
three choices from

```text
I, I+R1..I+R31, I+L1..I+L31.
```

No member satisfies all 64 Kraft conditions.  The best member is the same
two-shear encoding above, with 32 violating targets and maximum load 24/16.
The same verifier checks the 256 fixed test seeds and shows that, conditioned
on any raw seed bit being one, the observed `q=x xor seed` states span all of
GF(2)^32.  Therefore no nonzero linear encoded-state bit is mutually exclusive
with a raw seed bit across the actual tests; a phase-free OR cannot simply be
treated as XOR for any raw `(seed_i,q_j)` pair.

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_cycle65_continue\verify_phase_free_or.py `
  --output .research\rng_cycle65_continue\phase_free_or_certificate.json
```

## Arbitrary encoding status

`kraft_smt_exact.py` and the newer pure-QF_BV `kraft_smt_bv.py` eliminate the
symbolic inverse and model an arbitrary invertible encoding through the
equivalent sparse-basis equations

```text
D*A = B*D
C*D = A*(A+I).
```

The exact model additionally imposes all feedback/output Kraft capacities.
The QF_BV output-only calibration is SAT in 3.40 seconds.  Adding the exact
similarity equation while still omitting the D/seed feedback caps ends in
`unknown(timeout)` after 120 seconds at 379.05 MB peak memory; the full model
was therefore not extended.

`kraft_smt_math_distance_bound.py` proves universal pruning bounds, including
at least seven D rows of weight at least five, at least two of weight at least
six, total D row weight at least 65, and total B row weight at least 35.  The
bounds do not contradict each other, so arbitrary `T` remains open.  Non-XOR2
primitives, nonlinear care-set circuits, and different state architectures
also remain open; none of the finite-family results may be generalized to
them.
