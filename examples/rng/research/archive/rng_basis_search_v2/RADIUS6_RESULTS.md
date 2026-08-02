# Radius-6 Basis Search Results

## Outcome

No winning candidate was found among every emitted radius-6 basis whose
deterministic greedy cover has at most 60 XOR gates.  For those 1,528 bases,
all pair covers with actual XOR count at most 60 and all tick-zero B-row
decompositions are now structurally closed.  No label beam was reached.

This work was offline only.  It did not start the game or read/write the live
RNG save.

## Legal-State BFS

The search starts from the verified two-shear basis and follows row shears
whose resulting `T`, `B`, and `C` rows all have weight at most four.

| Depth | New legal states | Cumulative states | New records with greedy XOR <= 60 |
| ---: | ---: | ---: | ---: |
| 0 | 1 | 1 | 0 (the x61 origin is always emitted) |
| 1 | 5 | 6 | 0 |
| 2 | 75 | 81 | 5 |
| 3 | 443 | 524 | 27 |
| 4 | 3,957 | 4,481 | 97 |
| 5 | 21,669 | 26,150 | 334 |
| 6 | 142,819 | 168,969 | 1,065 |

The resulting `bfs-r6-x60.jsonl` has 1,529 unique records: the x61 origin,
10 x58 bases, 255 x59 bases, and 1,263 x60 bases.

## Exhaustive Emitted-Frontier Audit

`diagnose.py` re-enumerates every pair cover up to 60 XOR gates, including
x59/x60 alternatives for a greedy-x58 basis and x60 alternatives for a
greedy-x59 basis.  It then enumerates every B-row decomposition assignment.

```text
selected emitted bases                 1,528
pair-cover search states          47,678,374
pair covers                            11,788
  actual XOR 58                            46
  actual XOR 59                         1,089
  actual XOR 60                        10,653
decomposition variants                 16,709
maximum assignments for one cover           4
truncated pair-cover searches                0
beam-dependent or feasible cases             0
```

Every variant fails before component-option or global-beam optimization:

```text
direct_target_not_unit       14,005
pair_exact_target_invalid     2,704
```

Therefore the `component_limit=512` and `global_beam=4096` limits do not
affect this negative result.

## Exact Scope Gaps

This is not a closure of every leaderboard-feasible radius-6 basis.

- The sampler was run with `record_xor=60`.  It did not retain radius-6 bases
  whose greedy cover is 61, 62, or 63, including any such basis that might
  have a non-greedy cover of at most 60 XOR gates.
- Since every invertible tick-zero transform must use all 32 seed bits, OR is
  at least 32.  The target `3*XOR + OR <= 221` therefore still permits x61
  with OR <= 38, x62 with OR <= 35, and x63 with OR = 32.
- The existing `audit-bfs-r5-x61-top200.json` checks only 200 of 1,348
  greedy-x61 records at radius five.  It finds only the origin at
  `61 XOR + 47 OR = 230`; one pair-cover search is truncated.  It is a
  prioritized sample, not a closure.
- BFS is exhaustive only in the graph of structurally legal intermediate
  bases.  A final legal basis reachable only through an intermediate row of
  weight greater than four is outside this graph.
- `walk.cpp` deduplicates states with a 64-bit matrix hash rather than the
  full matrix.  For 168,969 states the birthday-bound collision probability
  is approximately `7.7e-10`; small, but not a formal collision-free proof.

The next complete outer step is to rerun radius six with `record_xor=63`, then
audit actual covers under the per-XOR OR bounds above.  A lower-memory
alternative is to modify the sampler to emit every basis whose exact cover
lower bound is at most 60, even when its greedy cover exceeds 60.

## Reproduction

```powershell
./.research/rng_basis_search_v2/walk.exe bfs 6 60 `
  > .research/rng_basis_search_v2/bfs-r6-x60.jsonl `
  2> .research/rng_basis_search_v2/bfs-r6-x60.log

./.venv/Scripts/python.exe .research/rng_basis_search_v2/diagnose.py `
  .research/rng_basis_search_v2/bfs-r6-x60.jsonl `
  --min-xor 0 --max-xor 60 `
  --cover-state-limit 250000 --cover-solution-limit 2000 `
  --component-limit 512 --global-beam 4096 `
  --output .research/rng_basis_search_v2/diagnose-bfs-r6-x60.json
```

## Evidence Hashes

```text
bfs-r6-x60.jsonl
B7D4D2989366F6F37B27CF6926CD97736900A9024AFB21F3157847BC4C96DC44

bfs-r6-x60.log
D69553ADC90FFC9D256952B76E43B974CBE910DF2897A361C88A429BDB30B3C9

diagnose.py
50D2197BFFDFD7CF38D5AD8BC35B67EA686F9FD3CE4E34D0F75951E875967E19

diagnose-bfs-r6-x60.json
276135EB0672C4FE5F3A05536EF643996EC7CF73A9A6263056483CF56E569F78
```
