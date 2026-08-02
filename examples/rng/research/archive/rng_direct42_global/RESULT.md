# RNG direct 42-state global search

## Outcome

No implementable 42-Delay candidate was found.  The strongest new exact
result is:

```text
all support-valid semiconjugate matrices within bitwise Hamming distance <=9
of the verified excess-three frontier: UNSAT
```

This improves the previous exact neighborhood exclusion from distance 6 to
distance 9.  The center remains invalid: rows `H[3]`, `H[7]`, and `H[14]`
have weight five, and the center has 69 distinct nontrivial targets, already
above the 60-XOR ceiling implied by `gate<=430` with 42 Delay Bits.

## Verification

The center was independently replayed for all 256 seeds and 65 outputs per
seed.  It satisfies the linear sequence and semiconjugacy equations, but not
the depth-two support constraint:

```text
256 x 65 sequence: PASS
maximum H/O row support: 5
support excess over 4: 3
bad rows: H[3], H[7], H[14]
```

Radius 7 was solved directly.  Radius 8 was partitioned by the exact number
of changed X bits into all nine cases.  Radius 9 was partitioned the same way;
the only hard `5 X + 4 D` case was covered by two exhaustive alternatives:

```text
all X changes inside the 24-row repair closure: UNSAT
at least one X change outside that closure: UNSAT
```

For radius 10, exact partitions `X=0..4` and `X=7..10` are UNSAT.  The
`5 X + 5 D` and `6 X + 4 D` partitions timed out and remain unknown.

## Reproduction

```powershell
python .research/rng_direct42_global/verify_boundary.py
```

The command checks every coverage artifact and rewrites
`boundary_certificate.json`, including SHA-256 hashes.  All work was offline;
no game process, formal save, or user configuration was accessed or changed.
