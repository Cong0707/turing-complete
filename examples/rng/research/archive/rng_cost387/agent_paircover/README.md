# Fixed Two-Shear 61-XOR Pair-Cover Audit

## Result

Within the fixed two-shear `T`, the exact `61 XOR` depth-two XOR2 network for
`B union C` is unique:

```text
12 required pair targets
+ 15 extra pair nodes
+ 34 final XOR nodes
= 61 XOR
```

Exhaustive search visits 46,561 distinct selected-extra-pair states. There is
exactly one cover at or below the 15-extra-pair budget, and all 34 final rows
have exactly one decomposition under that pair set.

This enumeration is complete even if a weight-two output is initially allowed
to remain in layer two as `(a XOR k) XOR (b XOR k)`. Replacing that final gate
with the direct pair `a XOR b` removes one final XOR and adds one first-layer
XOR, preserving both total XOR count and the number of non-target pair gates.
Every such network therefore canonicalizes to a cover in the exhaustive set.
The unique cover's heavy-row decompositions use all 12 pair-valued targets, so
none can be omitted or moved back to layer two. A unit output moved to layer
two would add a gate; the exact 15-extra-pair lower bound leaves no such slack.

The induced tick-zero equations split the 27 first-layer pair nodes into 13
components. Each component has exactly one feasible root label of weight at
most two. The possible `(seed, state)` mapping atoms of different components
are disjoint, so the global OR optimum is the sum of independent component
minima after accounting for the five fixed direct mappings:

```text
raw mappings before fixed reuse = 52
maximum fixed mapping reuse     = 5
exact OR minimum                = 47
```

The pair set, final decompositions, and pair-node labels are unique. Physical
leaf orientation is not unique; `result.json` records the number of distinct
47-OR mapping sets and one explicit representative.

Therefore `OR <= 38` is impossible for every useful depth-two 61-XOR network
under this fixed `T`. The best candidate remains:

```text
396 / 9 / 66
energy = 235224
```

This is still a scoped result. It does not rule out another state encoding,
more or fewer than 61 XOR gates, extra state bits, depth greater than two, or
different game primitives.

`prove_fixed_t_387_bound.py` separately checks the neighboring 62/63-XOR
budgets in the usual steady-row-deduplicated model. Its result must not be
extended to physical duplicate gates: once an extra XOR is available, two
nodes may carry the same steady row but different tick-zero labels. That case
is irrelevant to the exact 61-XOR proof, since merging any duplicate there
would contradict the strict 61-XOR steady-state lower bound.

## Reproduction

No Z3 call is needed:

```powershell
cd D:\Develop\Other\turing-complete

.\.venv\Scripts\python.exe `
  .research\rng_cost387\agent_paircover\enumerate_and_optimize.py `
  --output .research\rng_cost387\agent_paircover\result.json
```

Expected decisive lines:

```text
cover states: 46561 minimum covers: 1
selected pair set: unique; decompositions: unique
tick-zero label components: 13 all roots unique
cross-component possible mapping overlaps: 0
exact OR minimum: 47
optimal 47-OR mapping sets: 134217728
candidate tuple: 396/9/66
```

Independent existing Z3 cross-check:

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_init_reuse\verify_init_reuse.py `
  --prove-minimum
```

The explicit 47-pair candidate, component labels, leaf orientations, cover,
and metrics are recorded in `result.json`.
