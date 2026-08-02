# RNG 42-state Switch / sample-specialized repair result

## Outcome

No installable `gate <= 430 / delay <= 9 / ticks = 66` candidate exists in
the audited repair families for the recorded 42-state frontier.  No game
process or player save was opened or changed.

The decisive correction is that this frontier is not a `61 XOR + 32 OR`
linear circuit with only three timing defects.  On the exact live finite-care
sets it has:

```text
feedback H: 39 distinct nontrivial functions
output O:   30 distinct nontrivial functions
H/O functions compatible on their shared 64 steady ticks: 0
minimum distinct pure-XOR final nodes: 69
```

Consequently even before any pair intermediates or parity-5 timing repair:

```text
42 Delay Bit                       210 gate
ready Delay Bit + NOT                6 gate
32 phase OR                         32 gate
69 distinct final XOR * 3          207 gate
minimum                            455 gate
```

This already exceeds 430.  The `61 XOR` number in the frontier's target
accounting cannot materialize its 69 distinct nontrivial H/O functions.

## Exact protocol and tri-state model

`search_switch_sample.py` reconstructs all 256 live seeds and verifies all 65
outputs per seed.  Its care sets are exactly:

```text
output:   256 * 65 steady points                         = 16640
feedback: 256 load points + 256 * 64 steady points       = 16640
```

Both sets contain 16,640 distinct inputs.  Output-state rank is 39; feedback
rank is the full 42.

The Switch model matches reviewed kind-12 behavior:

```text
enable=0: output is Z
enable=1: output actively drives data
all drivers Z: bus remains Z, ordinary data plane reads 0
active 0 and active 1 on one bus: short circuit
```

For a Switch to drive a target bus legally, `enable => data == target` must
hold on every care point.  This condition is checked before set cover; if no
single usable driver exists, no number of such drivers can implement the bus.

## Exhaustive bounded searches

### Primitive and direct Switch search

The exact feedback-care primitive universe has 3,490 distinct signals:

```text
42 raw leaves, constants, and every one-gate
NOT / AND / OR / NAND / NOR result
```

For each of `H[3]`, `H[7]`, and `H[14]`, the script checks 12,176,610
nontrivially enabled `(enable,data)` pairs.  Results:

```text
H[3]  10400300100: 0 legal active Switch drivers
H[7]  04103001000: 0 legal active Switch drivers
H[14] 00400488004: 0 legal active Switch drivers
```

Every bad row also observes all 32 assignments of its five support leaves.
Thus a support-preserving don't-care rewrite cannot change parity-5.

Across every nontrivial H/O target, the following exact replacements are also
absent:

```text
wire or one cheap gate: 0
nested two-cheap-gate formula: 0
```

For each bad target and its complement, the primitive proper-subset and
proper-superset sets are all empty.  Therefore no outer
`AND/OR/NAND/NOR(primitive,primitive)` three-gate depth-two formula equals a
bad row.

### Shared degree-four cancellation

`search_depth2_pairs.cpp` performs a meet-in-the-middle search over:

```text
primitive := raw / constant / one cheap gate
node      := primitive OR one cheap gate(primitive, primitive)
repair    := XOR(node_a, node_b)
```

Each node costs at most 3 gates and 2 delay; the complete repair costs at most
9 gates and 4 delay.  It includes two separately built degree-four nonlinear
nodes, shared primitive inputs, and cancellation of their nonlinear terms.

Exact enumeration:

```text
primitive expressions:             3,530
nodes:                         24,932,390
distinct 128-point signatures:  9,641,582
table storage:                 541,065,216 bytes
candidate left nodes for all three bad rows: 0
```

The 128 points are a deterministic subset of the real feedback care set and
have input rank 42.  This is not a probabilistic rejection: any identity on
all 16,640 points must hold on the selected subset.  Hash/signature collision
can only create a false candidate, not remove one; every subset candidate
would then be verified on all 16,640 points.  There were none.

## Scope

The result closes the recorded 42-state matrix under the most attractive
bounded repairs:

- support-preserving specialization;
- raw/one-gate Switch drivers and any bus made from them;
- one- and two-cheap-gate substitutions for all targets;
- one depth-two three-cheap-gate node for each bad target;
- XOR/XNOR cancellation of two depth-two nonlinear nodes, up to 9 gates and
  4 combinational delay per repair.

It is not a global UNSAT proof for arbitrary 42-state encodings, deeper
Switch controls, a different H/O matrix, or a jointly synthesized sequential
nonlinear state representation.  No candidate was emitted because none in
the audited family can meet the requested score.

## Reproduction

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe `
  .research\rng_switch_sample_special\search_switch_sample.py `
  --output .research\rng_switch_sample_special\certificate.json

.\.venv\Scripts\python.exe `
  .research\rng_switch_sample_special\search_switch_sample.py `
  --verify-existing .research\rng_switch_sample_special\certificate.json

g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -pedantic `
  -o .research\rng_switch_sample_special\search_depth2_pairs.exe `
  .research\rng_switch_sample_special\search_depth2_pairs.cpp

.\.research\rng_switch_sample_special\search_depth2_pairs.exe `
  --output .research\rng_switch_sample_special\depth2_pair_certificate.json
```

## SHA-256

```text
295D1CAE298629EABF6B865AAAD9957A962AE202FFF30D218EFA774908770750  search_switch_sample.py
79668442C1DCB42A2AB81FC020FADA48DFA62B76CA46B2F9B1D6F973BF871A91  certificate.json
482C7BA7A6FC2634E21533316B23582CD92F6D196628A3283388506164FC384F  search_depth2_pairs.cpp
12C29DC0D8112A5EC8AA9E04DDDA533B382F2CCDB3C847B2BEAFC200E858F504  depth2_pair_certificate.json
```
