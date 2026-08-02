# RNG orphan-process recovery, 2026-08-02

## Outcome

No replayable RNG candidate was found in the artifacts created after 00:44.
The useful new result is that the five formerly truncated radius-4/x60 cover
searches are now complete, with no dual-mode solution.  The remaining orphan
Z3 process is also excluded from gate <= 387 by a smaller boundary proof; it
does not need to finish to decide usefulness.

## The three original Python process groups

1. Wrapper PID 26256 / worker PID 20648, started 23:58:19.
   The worker loaded `libz3.dll`.  A read-only memory-string inspection
   recovered its complete stdin program.  It reads the last `score heavy=0`
   blocks in `subspace-707.log` and `subspace-808.log`, then minimizes the
   selected first-layer pair gates for each 42-row depth-two XOR network.
   At inspection time it contained 152 `p707_*` symbols and zero `p808_*`
   symbols, so it was still solving the first case.  Its two greedy totals are
   83 XOR (seed 707) and 79 XOR (seed 808).
2. Wrapper PID 8152 / worker PID 28632, started 00:06:41.  This was the first
   `identity_current_rnbp` run (`n=64, m=64`).  Its partial log ended at t[9]:
   ten additions, 54/64 targets still nonzero, distance sum 237.
3. Wrapper PID 47236 / worker PID 46364, started 00:07:14.  This was the second
   duplicate `identity_current_rnbp` run.  Its partial log ended at t[8]: nine
   additions, 55/64 targets still nonzero, distance sum 241.

The two RNBP groups exited during inspection without a completion marker.  No
process was stopped by this audit.  The Z3 group was left running.

## Decisive 42-state boundary

The 42-state fixed cost is `42*5 + 6 = 216`.  Thus gate <= 387 requires
`3*XOR + OR <= 171`, and even with OR=0 it requires XOR <= 57.

For seed 707 there are 40 final XOR rows, so XOR <= 57 permits at most 17
selected pair gates.  For seed 808 there are 38 finals, hence at most 19 pair
gates.  Direct Z3 checks at exactly those bounds returned:

```text
seed=707 pair_budget=17 finals=40 xor_budget=57 result=unsat 22.536s
seed=808 pair_budget=19 finals=38 xor_budget=57 result=unsat  4.655s
```

Peak solver memory reported about 29.4 MB.  Reproduce with:

```powershell
.\.venv\Scripts\python.exe .research/rng_orphan_recovery/verify_pair_budget.py
```

This excludes both samples before tick-zero OR-label feasibility is even
considered.  The long exact-minimum process therefore cannot yield a <=387
candidate.

## XOR/split synthesis

`rng_xor_split_synthesis` starts from the verified 47 OR + 61 XOR dual-mode
logic (weighted logic area 230).

* Ordinary Yosys/ABC mapping returned 41 NOR + 6 OR + 54 XNOR + 7 XOR.  Under
  the optimistic genlib costs this is still area 230: no reduction.
* The external-don't-care BLIF correctly marks mixed nonzero seed/state inputs
  unreachable, but all successful ABC flows mapped to area 253, level 4.
  `fraig_dc2`, `fraig_resub`, `mfs_area`, `mfs_edges`, and
  `mfs_then_fraig` all have the same 253-area result.  `mfs` made zero
  resubstitutions; the collapse attempt asserted and produced no result.

There is no cheaper or game-ready netlist in this directory.

## Extended-BP logs

All three `RNG2Step` logs are incomplete and have no emitted result circuit:

```text
3H:   109 additions, 16/96 targets nonzero, distance sum 45, elapsed 2787.46s
4H:    43 additions, 55/96 targets nonzero, distance sum 168, elapsed 91.56s
RNBP:  40 additions, 56/96 targets nonzero, distance sum 156, elapsed 99.75s
```

The 3H partial run already exceeds the 61-XOR reference while unfinished.
The other two are merely partial traces, not candidates or lower bounds.

## Completed radius-4/x60 gap

`basis_radius4_x60_complete.json` now records:

```text
bases                       4,481
enumerated cover states 4,676,166
pair covers                   493
decomposition variants        571
truncated cover searches         0
dual-feasible variants           0
status          no_dual_candidate
```

The five old 100k-capped instances completed after 762,145 aggregate states.
They still contain exactly the same 102 covers and add zero new covers.  The
141 decomposition variants in those five cases all fail strict label checks:
138 `direct_target_not_unit`, 3 `pair_exact_target_invalid`.

Evidence SHA-256:

```text
D3DD80DD1CF44DA7FC78DC2A7433768EB45ED32EE386E0379CB7EB07BCF61496  basis_radius4_x60_complete.json
911B363743663348E443D5BA213E1D5777CCB84E7246D377F46FD7F43DA6EAC4  five_completed.json
AEA3548257A22D0094426AF60E056F40BBCDC1986975FCBD933819A0637D89F4  labels_512_4096.json
41E4FBE143E41EDB113C1F488F3389CE14395397BB5643476F9EF11A91C6CC1E  label_failures_512_4096.json
```

This closes the prior five-search truncation caveat for the radius-4,
XOR<=60 canonical depth-two family.  It is not a global proof over arbitrary
state encodings or noncanonical/deeper XOR DAGs.
