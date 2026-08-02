# Fixed two-shear direct-output synthesis audit

## Result

The exact direct targets

```text
feedback = B*q xor D*seed
output   = C*q xor A*seed
```

are **UNSAT for delay <= 9**, independently of the XOR gate budget.  Therefore
there is no `XOR <= 92` witness for this fixed `T` under `q arrival=4`,
`seed arrival=0`, and fan-in-two `XOR delay=2`.

There are 24 decisive rows:

- 14 feedback rows have q support weight 4 and nonzero seed support.
- 10 output rows have q support weight 4 and nonzero seed support.
- Every such row has minimum possible arrival 10.

For an output to arrive by 9, its final XOR inputs must arrive by 7.  A signal
arriving by 7 can contain at most two q leaves.  If it contains two q leaves,
it must be the XOR of two raw q leaves and has no seed support.  A four-q target
needs two such inputs, so it necessarily has zero seed support, contradicting
each of the 24 target rows above.

## Existing-artifact audit

- `../rng_joint_sat/agent_joint/fixed-two-shear.json` contains only 32-bit
  `T`, `B`, and `C` matrices.  Its exact 61-XOR result is not a synthesis of
  the 64-bit `Bq+Ds` and `Cq+As` targets.
- `../rng_constant_seed_math/two_shear_direct_mapped.v` is an unconstrained
  area mapping with 83 XOR, 207 XNOR, and 3 NOT cells.  It does not meet or
  model the arrival constraint.
- `../rng_cycle65_fixed/cycle65_fixed_certificate.json` covers phase-labeling
  of one fixed 61-XOR B/C DAG.  The new obstruction applies to every XOR2 DAG
  implementing the direct targets.

## Reproduction

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_cycle65_continue\synth_audit_direct_two_shear.py `
  --output .research\rng_cycle65_continue\synth_audit_direct_two_shear.json
```

The script derives all matrices, checks the defining identities, verifies 65
outputs for each of 256 byte-valued seeds, hashes the audited artifacts, and
emits all 24 timing obstructions.
