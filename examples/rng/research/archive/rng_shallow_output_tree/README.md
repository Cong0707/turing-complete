# Shallow-output colored-tree search

## Status

Global status: **OPEN**.

Exact local status around the last record of `deep-5a3307.jsonl`:

- C-row Hamming radius <= 4: **UNSAT**, independently reproduced by Python
  and C++ with identical branch counts.
- C-row Hamming radius <= 5: **UNSAT**.
- Therefore any feasible shallow-output encoding is at least six changed C
  rows from this center.

No game process, user configuration, official save, token, or `levels.txt`
was read or written by these tools.

## Tree reduction

An invertible 32x32 binary matrix with nonzero row weight at most two is the
reduced incidence matrix of a tree on 32 state vertices plus ground.  Give
tree edge `e` the label of C row `e`.  For a state vertex `v`,

```text
T[v] = XOR(A[e] for e on the ground-to-v path)
B[v] = odd non-ground boundary of edges labelled by supp(T[v])
```

This removes matrix inversion from the search.  Removing `r` C rows splits
the center tree into `r+1` components.  All T rows inside component `c` change
by one common XOR offset.  A replacement edge determines the child component
offset, allowing immediate T and B/capacity pruning.

The center has only two heavy T rows:

```text
T[11]: root path labels {29,12}
T[14]: root path label  {16}
```

Every feasible radius-r replacement set must therefore include label 16 and
at least one of labels 12 and 29.  This gives:

```text
radius 4: C(31,3)-C(29,3) = 841 sets
radius 5: C(31,4)-C(29,4) = 7,714 sets
```

For every set the exact search enumerates all labelled component trees using
Prufer shapes and every removed-label permutation.

## Exact evidence

```text
radius 4
  component-tree/label assignments: 2,523,000
  endpoint/offset branches:          5,292,094
  valid leaves:                      0
  Python peak working set:           32.55 MB
  C++ peak working set:               4.39 MB

radius 5
  component-tree/label assignments: 1,199,681,280
  endpoint/offset branches:          2,603,986,081
  valid leaves:                      0
  elapsed:                           447.875 s
  peak working set:                    4.94 MB
```

The T-only control finds a radius-4 tree with maximum T weight four in the
first branch.  It has five invalid B rows with `(row,T-weight,B-weight)`:

```text
(9,4,6) (11,4,8) (14,4,6) (23,4,5) (31,4,6)
```

Thus fitting the state labels in the weight-four ball is not the obstruction;
the decisive difficulty is the self-indexed boundary equation `B=T*C`.

## Reproduction

Build and run the exact C++ search:

```powershell
g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wpedantic `
  .research\rng_shallow_output_tree\search_radius.cpp `
  -o .research\rng_shallow_output_tree\search_radius.exe -lpsapi

.\.research\rng_shallow_output_tree\search_radius.exe `
  .research\rng_shallow_output_encoding\deep-5a3307.jsonl `
  .research\rng_shallow_output_tree\radius5-replay.json 5 900
```

Audit the stored results, algebra, counts, hashes, and 69 seeds x 65 outputs:

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_shallow_output_tree\verify_results.py `
  --center .research\rng_shallow_output_encoding\deep-5a3307.jsonl `
  --output .research\rng_shallow_output_tree\verification.json
```

The global colored-edge SAT prototype is `solve_colored_tree.py`.  Its base
model has 26,521 edge variables and 29,361 used low-weight states.  With the
T-only certificate as a complete phase hint it reproduces the 33-vertex tree
in 0.16 seconds, learns five exact local B-boundary cuts, and then times out
on its second solve after 300 seconds.  Peak working set was 100.32 MB.  This
remains a global OPEN route, not an UNSAT certificate.  Repeating this lazy
timeout is unlikely to help; the next useful model should pre-encode local
boundary patterns or use a radius-six large-neighborhood search.
