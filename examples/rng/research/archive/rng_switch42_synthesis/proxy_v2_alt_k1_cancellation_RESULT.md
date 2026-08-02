# Active1 cancellation-aware exact cover

## Result

The final active1 candidate from
`proxy_v2_alt_fixed_k1_20k_r8_seed20260802083.log` is UNSAT at total gate
430 in the cancellation-aware depth-two XOR2/Switch-XOR3 model.

Unlike the earlier disjoint-partition cover, this model permits final-gate
sources to overlap and cancel over GF(2).  The result therefore closes the
wider cancellation-aware depth-two library for this candidate, not just set
partitions.

```text
state_bits=33
active_hidden=1
fixed_gate=203
raw_logic_budget=227
effective_logic_budget=225
proved_logic_lower_bound=228
proved_total_lower_bound=431
targets=35
weights={2:2, 3:6, 4:14, 5:3, 6:7, 7:3}
verified=256 seeds x 65 outputs
```

The effective budget is 225 because every logic cost is a multiple of three
gates.  UNSAT at 225 proves that at least 228 logic gates are required, so the
candidate needs at least `203+228=431` total gates in this model.

## Independent solvers

Both solvers used the same generated encoding:

```text
variables=355333
clauses=1060491
primary_forms=5683
dnf_terms=69775
fixed_cost_units=26
variable_bound_units=49
```

Results:

```text
solver       status  build_s  solve_s  total_s  peak_working_set_mib
Glucose42    UNSAT    39.410   26.258   65.670       256.473
Minisat22    UNSAT    36.504   43.297   79.802       216.648
```

Both runs stayed well below the requested 700 MiB process limit and completed
before the 120-second solve timeout.

## Reproduction

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_switch42_synthesis\cancellation_cover.py `
  --log .research\rng_switch42_synthesis\proxy_v2_alt_fixed_k1_20k_r8_seed20260802083.log `
  --candidate last `
  --target-gate-max 430 `
  --timeout-seconds 120 `
  --memory-mb 700 `
  --solver glucose42 `
  --output .research\rng_switch42_synthesis\proxy_v2_alt_k1_cancellation_glucose42.json

.\.venv\Scripts\python.exe `
  .research\rng_switch42_synthesis\cancellation_cover.py `
  --log .research\rng_switch42_synthesis\proxy_v2_alt_fixed_k1_20k_r8_seed20260802083.log `
  --candidate last `
  --target-gate-max 430 `
  --timeout-seconds 120 `
  --memory-mb 700 `
  --solver minisat22 `
  --output .research\rng_switch42_synthesis\proxy_v2_alt_k1_cancellation_minisat22.json
```

## SHA-256

```text
cancellation_cover.py
ECAE0D6001BA757DE0F13D95BC9B11FF8B7A5C2B405D7F08E79A54984D225450

proxy_v2_alt_k1_cancellation_glucose42.json
6C4482F77B20390404C7591EA13EBBF554B82997995A08C93A303DECD314E8C6

proxy_v2_alt_k1_cancellation_minisat22.json
26BA1E0667A86B8D80AF594A07E9640DDA1130D2E100DFB09DC00D6CC57CE68D

proxy_v2_alt_k1_cancellation_glucose42.log
0BA89B8FFFF9C49D7AC8D707DAA7AA74B7B7C0F935F300F55ECDB930257F5467

proxy_v2_alt_k1_cancellation_minisat22.log
1B0AE1E47B6797C6476904A9F7B0F598A7C84A00E9CCE93306618129617BA41D
```

No game process, save, `levels.txt`, or shared source file was touched.
