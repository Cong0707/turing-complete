# Frontier v2 h1 cancellation-aware independent check

## Outcome

MiniSat 2.2 independently proves the `frontier_v2` active-hidden-1 instance
UNSAT at the 430-gate target.  This confirms the earlier Glucose 4.2 result
without reusing CaDiCaL.

```text
state bits:                     33
active hidden rows:             [0]
distinct non-wire H/O targets:  34
fixed gate cost:                203
raw logic budget:               227
effective 3-gate-unit budget:   225
proved logic lower bound:       228
proved total lower bound:       431
status:                         UNSAT
```

## Independent agreement

The independently generated MiniSat22 record agrees with the Glucose42
record on every structural field:

```text
matrix fingerprint: ccd655b03479439acb1478bc8972ca3b17616f477b133d8ef29c84991804eaec
variables:          379761
clauses:            1133510
primary forms:      5805
DNF terms:          82220
fixed cost units:   25
variable bound:     50
limit:              225
status:             UNSAT
```

Solver measurements:

```text
solver       solve seconds   total seconds   peak working set
glucose42          30.4961         68.8126          258.85 MiB
minisat22          51.0676         89.5111          228.15 MiB
```

The in-process watchdog sampled the actual solver process every 250 ms and
would terminate it with exit code 75 above 700 MiB.  The observed MiniSat22
peak was only 228.15 MiB.  Because the preferred independent solver reached a
decisive result, Glucose3 and MapleChrono were not run.  The known failing
CaDiCaL path was not repeated.

## Reproduction

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_switch42_synthesis\cancellation_cover.py `
  --log .research\rng_switch42_synthesis\frontier_v2_selected_pareto.log `
  --candidate last --target-gate-max 430 `
  --timeout-seconds 120 --memory-mb 700 --solver minisat22 `
  --output .research\rng_switch42_synthesis\frontier_v2_h1_cancellation_minisat22.json
```

The realization was verified for 256 seeds and 65 outputs per seed before the
SAT instance was built.

## Artifacts

```text
frontier_v2_h1_cancellation_minisat22.json
SHA-256 6aa6987107396641f1af68e4aaed4cb70e626b1f8d8d4c985568e77c4e8717e0

frontier_v2_h1_cancellation_minisat22.log
SHA-256 082f8813646ff6fd9eb93bde82b2c8dca9af96335ebf9557a5044d6b0fbe751f

frontier_v2_h1_cancellation_minisat22.err.log
SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```
