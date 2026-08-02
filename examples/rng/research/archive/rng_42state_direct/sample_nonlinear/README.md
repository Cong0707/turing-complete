# RNG 42-state sample-specialized nonlinear audit

## Outcome

No installable candidate was produced and no player save or game process was
touched.  The useful result is a strict boundary on where sample-specific
nonlinearity can begin.

For the 66-cycle protocol with 42 Delay Bits, the fixed gate cost is:

```text
42 Delay Bit * 5 + phase Delay 5 + NOT 1 = 216
```

Therefore the combinational weighted budgets are:

```text
delay 10, gate <= 387: logic <= 171
delay  9, gate <= 430: logic <= 214
```

The known linear accounting `61 XOR + 32 OR = 215` misses the delay-nine
target by exactly one gate.  A nonlinear route is useful only if it shares a
correction across outputs or across ticks; isolated parity replacement does
not save that gate.

## Exact restricted-care resubstitution result

`audit_restricted_resub.py` reconstructs all legal combinational points of the
current checked 61-XOR/47-OR encoded DAG:

```text
256 load points:       (seed=s, q=0)
256 * 65 steady points (seed=0, q=T*A^t*s), t=0..64
total: 16896 distinct (seed,q) points
```

For every XOR node, it enumerates every earlier signal as a wire/NOT source
and every pair of earlier signals under AND, OR, NAND, and NOR.  Equality is
checked as a 16,896-bit truth signature.  Result:

```text
XOR nodes audited:                         61
replaceable by <=1 cheap gate or a wire:   0
minimum count with both XOR inputs high:   4048
maximum count with both XOR inputs high:   4315
```

This closes all node-preserving one-gate nonlinear substitutions in the fixed
DAG, not arbitrary rewrites or arbitrary state encodings.

The independent `agent_care/projection_audit.json` gives a broader local
support check.  On the 16,640 steady points, all 66 distinct rows appearing in
`B`, `C`, or an internal XOR node observe every one of the `2^w` assignments
to their own support (`w=1..4`).  On the 256 load points, all 51 distinct rows
appearing in `T` or the seed labels likewise observe every support assignment.
Consequently no support-preserving truth-table rewrite of those rows can use a
sample don't-care; a useful rewrite must introduce variables outside the old
support or share logic across rows.

`agent_care/care_synth.py` also emitted the exact 64-input partial PLA and a
care-set AIG for future external-don't-care synthesis.  The legacy Espresso
trial on the full 64-output PLA produced no output after several minutes and
was terminated at low memory usage.  This is a tool timeout, not UNSAT and not
a circuit-cost result.

## Low-degree algebraic certificate

`verify_low_degree_rank.py` evaluates every square-free ANF monomial in the 32
natural state bits.  The exact monomial counts through degree three are:

```text
degree 0:    1
degree 1:   32
degree 2:  496
degree 3: 4960
total:     5489
```

Both relevant live sets have full column rank 5,489:

```text
feedback care, A^0(s)..A^63(s): 16384 rows, rank 5489
output care,   A^0(s)..A^64(s): 16640 rows, rank 5489
```

Thus no nonzero Boolean polynomial of algebraic degree at most three vanishes
on either sample.  Any degree-at-most-three circuit that agrees with a linear
target on these points is a global identity, not a sample-only optimization.

Degree four is the sharp transition for these samples.  Degree-at-most-four
monomial evaluations reach full row rank:

```text
feedback care: rank 16384 (first reached after 16385 ordered monomials)
output care:   rank 16640 (first reached after 16644 ordered monomials)
```

So arbitrary sample behavior is algebraically representable at degree four,
but this fact alone says nothing about a cheap circuit.  Starting with affine
signals, degree four needs at least three binary nonlinear gates in a cone
(for example two quadratic products followed by their product).  Three cheap
gates already cost the same as one native XOR.  The only plausible saving is
to amortize those nonlinear nodes over multiple targets or store them as
shared state whose successor is also cheap.

## Recommended exact search formulation

An arbitrary 42-bit encoding should be searched as a bounded sequential
network, not as independent truth-table minimization.

Let `E(x)` be the 42 stored bits for a natural xorshift state.  For each of the
256 test seeds and each required tick, constrain one shared gate DAG as:

```text
load:                  G(seed=s, state=0).feedback = E(s)
steady t=0..64:        G(seed=0, state=E(A^t*s)).output = A^(t+1)*s
steady t=0..63:        G(seed=0, state=E(A^t*s)).feedback = E(A^(t+1)*s)
```

The last feedback value is a don't-care.  Output correctness already forces
`E` to distinguish states needing different outputs.  Gate kinds carry real
weights and delays: XOR/XNOR cost 3 and delay 2; AND/OR/NAND/NOR/NOT cost 1
and delay 1.  Constrain total logic to 214 with path delay at most nine (or
171 with path delay at most ten).

A monolithic encoding has millions of per-sample gate-value variables and
large topology symmetry.  The practical formulation is alternating CEGIS:

1. Fix a small topology containing explicit degree-four shared cones and solve
   the 42 encoding truth columns on a subset of trajectories.
2. Bit-parallel verify all 256 trajectories and add only failing points.
3. With the encoding fixed, use exact weighted resubstitution/set cover to
   delete gates and enforce timing.
4. Admit a nonlinear stored feature only when its readout savings plus its
   successor-update savings exceed its Delay Bit cost of 5.

The rank certificates justify excluding degree-at-most-three sample-specific
templates.  Search should begin with products of two reusable quadratic
features and require each such feature to serve at least two targets or ticks.

## Reproduction

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_42state_direct\sample_nonlinear\audit_restricted_resub.py

.\.venv\Scripts\python.exe `
  .research\rng_42state_direct\sample_nonlinear\verify_low_degree_rank.py `
  --rounds 64 --degree 3

.\.venv\Scripts\python.exe `
  .research\rng_42state_direct\sample_nonlinear\verify_low_degree_rank.py `
  --rounds 65 --degree 4
```

Primary certificates are `restricted_resub_certificate.json`,
`low_degree_rank_feedback64_certificate.json`,
`low_degree_rank_certificate.json`, `degree4_span_feedback64_certificate.json`,
`degree4_span_output65_certificate.json`, and
`agent_care/projection_audit.json`.
