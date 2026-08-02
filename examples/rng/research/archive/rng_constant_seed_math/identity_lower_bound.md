# Constant-seed RNG with `T = I`

## Result

For the exact model

```text
q_0       = 0
q_next    = A*q xor (A+I)*s
output    = A*q xor A*s
cycles    = 65
```

with 32 Delay Bits and XOR2 as the only combinational primitive, the static
delay is **at least 12**.  This is tight: explicit circuits in the accompanying
script attain delay 12.

Independently, all 64 feedback/output targets are distinct non-unit linear
forms, so at least 64 XOR2 gates are necessary.  Even combining only these two
very optimistic lower bounds gives

```text
gate   >= 32*5 + 64*3 = 352
delay  >= 12
cycles  = 65
energy >= 352*12*65 = 274560
```

This lower bound is already `18546` above the leader's `256014` and `13200`
above the current verified `261360`.  Therefore the `T=I` direct-next model
cannot improve the current save, regardless of XOR sharing or sample-specific
optimization.

## Exact delay lower bound

Rows 17 and 18 of `A` have weight seven.  Row 17 is

```text
A[17] = 0x40462021
support = {0, 5, 13, 17, 18, 22, 30}
```

The visible target at bit 17 therefore depends on seven independent Delay Bit
outputs and seven independent seed inputs.

Assume static delay at most 11.  A q-to-output path starts after Delay Bit
delay 4, so it can contain at most

```text
floor((11-4)/2) = 3 XOR2 levels.
```

A seed-to-output path can contain at most

```text
floor(11/2) = 5 XOR2 levels.
```

Unfold any shared XOR DAG for this one output into a binary formula.  Every
independent input in its support must occur an odd, hence nonzero, number of
times.  The binary Kraft load is consequently at least

```text
7 * 2^-3 + 7 * 2^-5 = 35/32 > 1,
```

which is impossible for a binary tree.  Sharing or cancellation cannot evade
the proof: unfolding sharing only adds leaf occurrences, and even numbers of
cancelled occurrences only increase the load.  Thus delay 11 or less is
impossible.

This also separates the requested q-depth cases:

- q depth at most 2 is impossible because a depth-two XOR tree has at most
  four independent q leaves, while the witness needs seven.
- q depth at most 3 is feasible, but the witness forces seed depth at least 6;
  the script constructs exactly such a `q=3, seed=6, delay=12` network.
- A smaller explicit delay-12 upper bound uses `q=4, seed=4`.

## Explicit upper bounds

All counts below are checked by propagating exact 64-bit GF(2) labels through
every XOR gate and comparing all 64 targets.

| construction | XOR2 | gate | q depth | seed depth | delay | cycles | energy |
|---|---:|---:|---:|---:|---:|---:|---:|
| two separate `A` networks | 186 | 718 | 5 | 5 | 14 | 65 | 653380 |
| `p=q xor s`, then `y=A*p`, `q_next=y xor s` | 125 | 535 | 5 | 5 | 14 | 65 | 486850 |
| independent asymmetric trees | 512 | 1696 | 3 | 6 | 12 | 65 | 1322880 |
| shared `p/A` output plus balanced feedback | 213 | 799 | 4 | 4 | 12 | 65 | 623220 |

The 125-XOR construction is the useful gate-count upper bound:

```text
32 XOR   p_i = q_i xor s_i
61 XOR   y = A*p using the three xorshift shear stages
32 XOR   q_next_i = y_i xor s_i
```

The 213-XOR construction establishes that delay 12 is attainable: it reuses
the same 32 `p` gates and 61-gate `A*p` output network, but builds each feedback
row as a balanced tree over `q_i` and the required `p_j` values.  It is an
upper-bound certificate, not claimed gate-optimal at delay 12.

## Reproduction

```powershell
cd D:\Develop\Other\turing-complete
.\.venv\Scripts\python.exe `
  .research\rng_constant_seed_math\identity_lower_bound.py `
  --output .research\rng_constant_seed_math\identity_lower_bound.json
```

The script additionally checks 69 deterministic seeds for all 65 outputs and
the invariant `q_t = A^t(seed) xor seed`.

This analysis is deliberately scoped to the direct 65-cycle `T=I` equations
above.  It does not cover a hidden first tick/current-state decoder or another
state encoding `T`.
