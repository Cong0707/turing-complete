# RNG live-test specialization certificate

This directory records the live 2.1.281 RNG protocol without touching the
player save.

Run:

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_test_specialization\verify_rng_contract.py `
  --output .research\rng_test_specialization\contract_certificate.json
```

Decisive results:

- `reset_sim()` seeds the script PRNG with `ctl_test + 1`; `meta.txt` declares
  exactly 256 tests, so the initial seeds are a fixed set indexed by 0..255.
- Generated architecture-input code calls `arch_get_input()` during every
  simulation tick. `rng/test.si` always returns the unchanged
  `.initial_seed`, so the same seed remains available for the whole run.
- Each enabled architecture-output tick invokes `arch_check_output()` once.
  The script wins on the 65th accepted value, which must be
  `F(seed), ..., F^65(seed)` in order.
- The 256 initial seeds have GF(2) rank 32; the first 66 already reach full
  rank. Therefore a linear or affine first-step network cannot exploit the
  fixed sample set: agreement on all tests forces the complete xorshift32
  transform.
- All 16,896 states consisting of each seed and its following 65 outputs are
  distinct. No tested trajectory shares a suffix with another test.

The continuous seed permits the algebraic state change
`q_t = T(x_t xor seed)`, with zero initial state and recurrence
`q' = (T A T^-1) q xor T(A+I) seed`. This removes the protocol need for a
one-shot seed source, but it does not by itself prove a lower-cost circuit;
the transition and output maps still require joint synthesis and game timing
verification.

## Program RAM boundary

The live executable's `com_ram` scoring path was also inspected. With the
normal non-empty settings vector, its gate score is the configured word width,
but its delay is `512 / (settings[0] + 1)`. Every live save sample observed in
this workspace uses `settings[0]` equal to 0 or 1, giving delay 512 or 256.
Consequently a legal observed Program-RAM lookup is far too slow to challenge
the 9/10-delay RNG frontier, even though the 256 test seeds are fixed.

Values above 1 written directly into the setting field have not been validated
by the game and are not treated as a construction.
