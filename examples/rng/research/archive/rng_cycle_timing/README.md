# RNG cycle timing certificate

Run:

```powershell
python .research/rng_cycle_timing/verify_cycle_contract.py
```

The verifier is read-only. It hashes the installed RNG test/runtime, proves
that the test needs exactly 65 output callbacks, verifies both constant-seed
state equations for 69 deterministic seeds and all 65 outputs, and prints the
gate budget for a 65-cycle design.

For the normal single Architecture Output topology, 65 cycles is the exact
lower bound: the first callback must occur on tick zero and the test wins on
callback 65. A registered output or a hidden seed-load tick restores the old
66-cycle result.

The certificate also records a separate experimental extension. If the game
accepts multiple Architecture Output components, its code-generation template
appears to call `arch_check_output` once for each enabled component before the
single tick increment. That would permit `ceil(65 / m)` cycles with `m`
successive values computed per tick. This has not yet been validated in the
game and must not be treated as a deployable result.
