# RNG basis search v2

This directory is an offline-only search branch for the single-output,
all-`init_data=0` RNG circuit.  It does not import save-writing code and does
not touch the game process or any formal candidate/save path.

The target metric model is:

```text
gate = 166 + 3 * XOR + OR
delay = 10
cycles = 66
target: gate <= 387, equivalently 3 * XOR + OR <= 221
```

`walk.cpp` performs a reproducible constant-memory walk over state encodings
`q=T*x`.  Every elementary move is a row shear and updates `T`,
`B=T*A*T^-1`, and `C=A*T^-1` incrementally.  It records only encodings whose
`T/B/C` rows all have support at most four and whose deterministic depth-two
`B/C` XOR cover is below the requested threshold.  JSONL records contain all
three matrices for independent replay.  Tick-zero label feasibility and OR
cost are deliberately handled by the Python audit stage, not guessed by this
sampler.

Build and run a small deterministic shard:

```powershell
g++ -std=c++20 -O3 -DNDEBUG -o `
  .research/rng_basis_search_v2/walk.exe `
  .research/rng_basis_search_v2/walk.cpp
./.research/rng_basis_search_v2/walk.exe 0x387 5000000 63 250000 `
  > .research/rng_basis_search_v2/walk-0x387.jsonl `
  2> .research/rng_basis_search_v2/walk-0x387.log
```

The sampler stores only 64-bit hashes of emitted matrices.  It does not retain
the walk history, so memory remains bounded well below the 2 GB task limit.

For an exhaustive legal-state neighborhood instead of annealing, use BFS mode:

```powershell
./.research/rng_basis_search_v2/walk.exe bfs 6 63 `
  > .research/rng_basis_search_v2/bfs-r6.jsonl `
  2> .research/rng_basis_search_v2/bfs-r6.log
```

BFS stores one 64-bit seen hash per encoding and only the current/next state
layer.  The log reports exact layer sizes; label propagation runs only for
states whose greedy steady network has at most the requested XOR count.

Audit the most promising records, including alternate pair covers and tick-zero
labels:

```powershell
./.venv/Scripts/python.exe .research/rng_basis_search_v2/audit.py `
  .research/rng_basis_search_v2/walk-0x387.jsonl `
  --candidate-limit 250 --max-xor 61 `
  --output .research/rng_basis_search_v2/audit-0x387.json
```

The audit recomputes sampler metrics, checks `C*T=A` and `T*C=B`, and replays
65 outputs before accepting any dual-mode result.  A target candidate must
have `3*XOR+OR <= 221`; sampler-reported scores alone are never sufficient.
