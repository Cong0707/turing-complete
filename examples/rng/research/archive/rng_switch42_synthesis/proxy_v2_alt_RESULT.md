# Active-hidden proxy-v2-alt result

## Outcome

The search did not find a `gate<=430` implementation.  It did find a stable
one-hidden-state proxy improvement over the natural 32-state point:

```text
candidate       active  targets  greedy logic  fixed  greedy total
active1 best         1       35           327    203           530
active3 best         3       35           321    213           534
beam active6         6       53           306    228           534
natural              0       32           336    198           534
pruned38             6       57           393    228           621
old active10        10       66           372    248           620
```

The active1 point was then checked by the exact shared-cover PySAT model at
the real `430-203=227` logic budget.  Two independent solvers agree on UNSAT:

```text
Glucose42   UNSAT   build 0.251 s   solve  11.722 s
CaDiCaL195  UNSAT   build 0.354 s   solve 119.105 s
variables 143952, clauses 433622
```

This exact result excludes only the stated two-level XOR2/Switch-XOR3 library
for this particular active1 state point.  It is not a global RNG impossibility
claim.

## Proxy model

For every distinct nontrivial H/O target, all set partitions into at most
three blocks of at most three leaves are generated.  The greedy solver keeps a
concrete implementable shared cover with these costs:

```text
first-level XOR2 group          3 gates / 1 unit
first-level Switch-XOR3 group  12 gates / 4 units
two-block final XOR2            3 gates / 1 unit
three-block final Switch-XOR3  12 gates / 4 units
fixed cost                      198 + 5*active_hidden
```

First-level groups are shared globally.  Three target orders, global reuse
frequency tie-breaking, and two coordinate-descent passes are tried; the best
valid cover is the proxy value.  It is therefore an upper bound for this
restricted library, not a lower bound and not an exact optimum.

Unlike the earlier `distinct+excess` proxy, the search:

- permits D rows to become zero;
- removes zero hidden rows and columns before target scoring;
- canonicalizes inactive coordinates;
- supports fixed-active-count runs so cooperative encodings cannot simply
  collapse to the natural state;
- mutates X locally as well as by sparse-mask replacement.

## Best candidate

```text
active_hidden=1
distinct_nontrivial=35
weight histogram: w2=2, w3=6, w4=14, w5=3, w6=7, w7=3
greedy groups: pair=28, triple=3, final XOR2=21, final Switch-XOR3=12
greedy logic=327, fixed=203, greedy total=530

X=000,000,000,000,000,000,000,000,
  000,000,000,000,001,000,000,000,
  000,000,000,000,000,000,000,000,
  000,001,000,000,000,000,000,000

D=00142002000,00000000000,00000000000,00000000000,00000000000,
  00000000000,00000000000,00000000000,00000000000,00000000000
```

Two independent `20k iterations x 8 restarts` runs, seeds `20260802083` and
`20260802084`, converged to this same X/D point.  Corrected fixed-k results:

```text
k=1: 530, 530
k=2: 541, 541
k=3: 534, 540
```

The imported active6 beam point evaluates as `306 logic / 534 total` in this
proxy.  Two `30k x 6` local runs (seeds `20260802085` and `20260802086`) did
not improve it.

## Verification

`proxy_v2_alt_verify.py` parses the full X/D rows from the logs and checks:

- strict zero hidden initialization;
- exact reachable-hidden pruning through 42 symbolic powers;
- all 32 rows of the algebraic identity `O*H=A*O`;
- 256 seeds, 65 outputs per seed, against xorshift32.

Four representative candidates passed all checks, each covering 16,640
outputs.  The machine-readable rows, histograms and full projected H/O matrices
are in `proxy_v2_alt_validation.json`.

## Reproduction

```powershell
g++ -std=c++20 -O3 -DNDEBUG -o `
  .research\rng_switch42_synthesis\proxy_v2_alt_search.exe `
  .research\rng_switch42_synthesis\proxy_v2_alt_search.cpp

# iterations, restarts, seed, forced active hidden count
.research\rng_switch42_synthesis\proxy_v2_alt_search.exe `
  20000 8 20260802083 1

.venv\Scripts\python.exe `
  .research\rng_switch42_synthesis\proxy_v2_alt_verify.py `
  --log .research\rng_switch42_synthesis\proxy_v2_alt_fixed_k1_20k_r8_seed20260802083.log `
  --log .research\rng_switch42_synthesis\proxy_v2_alt_fixed_k3_20k_r8_seed20260802083.log `
  --log .research\rng_switch42_synthesis\proxy_v2_alt_beam_audit.log `
  --log .research\rng_switch42_synthesis\proxy_v2_alt_k0_5k_r6_seed20260802081.log `
  --output .research\rng_switch42_synthesis\proxy_v2_alt_validation.json

.venv\Scripts\python.exe `
  .research\rng_switch42_synthesis\optimize_pruned38_pysat.py `
  --log .research\rng_switch42_synthesis\proxy_v2_alt_fixed_k1_20k_r8_seed20260802083.log `
  --candidate last --target-gate-max 430 --timeout-seconds 120 `
  --solver glucose42 `
  --output .research\rng_switch42_synthesis\proxy_v2_alt_k1_exact430_glucose.json
```

Peak measured search working set was about 5.1 MiB.  The game was not
launched, and no save, `levels.txt`, or shared `src` file was modified.

## SHA-256

```text
proxy_v2_alt_search.cpp
f1b60e6ab58be8b094966b3200959d72d0a797fa406e90bb873db86567c3173d

proxy_v2_alt_search.exe
cc68da01d0e7222d500a968cf7c4f4dc29b70aa548bcbd1685ca78f5a58b5825

proxy_v2_alt_verify.py
7fb2eec60540a95af5b7a57e257273da395192c9f507406610768319c6f2cb31

proxy_v2_alt_validation.json
40d5cc43601c1f61e6f6527e724a32d58faebb9b94a298f1b27f157e5abcd082

proxy_v2_alt_k1_exact430_glucose.json
fe989ff0f4c53dd9951c3c54f7fbd38c13edbc1406411f87aec0eca479c63bb7

proxy_v2_alt_k1_exact430_cadical.json
f8f4c6865b7c4ef2ea26bd43802c45ac44cfdd599aad12d27fb58fa1ab2dbdc8
```
