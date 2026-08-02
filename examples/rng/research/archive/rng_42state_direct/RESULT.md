# RNG 42-state direct research result

## Outcome

No implementable `42 Delay Bit + 61 XOR2 + 32 OR + control=6` matrix was
found.  No game process or save file was accessed.

The best verified matrix is a genuinely non-strong linear frontier:

```text
69 seeds x 65 outputs: PASS
O*S = I, O*H = A*O, O*(H*E + E*A) = 0: PASS
H*E = E*A: FAIL (expected; defect rank 7)
support excess above 4: 3
maximum target-row weight: 5
bad rows: H[3], H[7], H[14]
```

It is not a circuit candidate.  A depth-two XOR2 network can depend on at
most four primary leaves, so each weight-five row is a strict obstruction
independent of the 61-XOR gate budget.

## General non-strong model

Number the 42 physical network leaves so the 32 seed ORs inject through
`S=[I32;0]`.  Let the physical output be

```text
O = [I32 | X]
```

and let `D` be the bottom ten rows of the physical feedback matrix.  The most
general feedback matrix satisfying the global quotient equation in this
systematic coordinate choice is

```text
H_bottom = D
H_top    = A*O + X*D
```

Therefore `O*H=A*O` and `O*S=I`.  Starting from zero, the load tick stores
`E=H*S`, and the following 65 enabled output ticks are exactly
`A(seed)..A^65(seed)`.

The old strong-invariant search is the special case

```text
D = [R | R*X]
```

which makes `H=E*O` and `H*E=E*A`.  Freeing all 420 bits of `D` (subject only
to row support) is the added non-strong freedom.  In the recorded frontier,
`H*E+E*A` is nonzero with rank 7, but all 28 nonzero defect rows are invisible
through `O`.

## Exact exclusions

The Boolean SMT model has no fixed `X` or `D` rows.  It enforces:

```text
wt(X_i) <= 3
1 <= wt(D_j) <= 4
wt(H_i) <= 4
O*H = A*O
```

Around the recorded excess-three frontier, bitwise Hamming distance at most
3 is `UNSAT`.  Distance at most 4 is `unknown(timeout)` after 60 seconds.
The unrestricted model is `unknown(timeout)` after 120 seconds.  Both runs
cap Z3 at 768 MB.  Thus only the radius-three result is an exclusion; there
is no global UNSAT claim.

There is also a global combinatorial exclusion of one useful scoped family:
force `X_i=0` on every natural `A` row whose weight is already at most four.
The remaining 15 heavy rows admit only eight hidden-column multisets.  Every
one forces a core group to share one `D` row; exhaustive enumeration of all
41,449 low halves of weight at most four leaves a row of weight at least
seven.  `minimal_x_family_certificate.json` is therefore `UNSAT` for this
minimum-output-support family, but not for arbitrary `X`.

## First-tick output freedom

The finite 66-cycle protocol permits a still broader rank-32 family.  An
abstract quotient map `L=[I|X]` can define `H=E*L`, while the physical output
may be a different sparse matrix `O` satisfying only `O*E=A`.  This exploits
the disabled load-tick output, because `O` and `L` need agree only on the
reachable encoded states.  `search_decoupled_output.cpp` sampled this family;
its fixed run reached feedback support excess 9, not a valid matrix.  That is
a search result, not an exclusion of the decoupled-output family.

## Reproduction

```powershell
python .research/rng_42state_direct/verify_nonstrong_frontier.py `
  --output .research/rng_42state_direct/nonstrong_frontier_certificate.json

python .research/rng_42state_direct/solve_global_semiconjugacy.py `
  --hamming-bound 3 --timeout-ms 30000 --max-memory-mb 768 `
  --output .research/rng_42state_direct/nonstrong_frontier_ball3.json

python .research/rng_42state_direct/solve_global_semiconjugacy.py `
  --timeout-ms 120000 --max-memory-mb 768 `
  --output .research/rng_42state_direct/global_semiconjugacy_result.json

python .research/rng_42state_direct/verify_minimal_x_family.py `
  --verify .research/rng_42state_direct/minimal_x_family_certificate.json

g++ -std=c++20 -O3 -DNDEBUG -o `
  .research/rng_42state_direct/search_decoupled_output.exe `
  .research/rng_42state_direct/search_decoupled_output.cpp
.research/rng_42state_direct/search_decoupled_output.exe 5000000 32 2026080206 `
  > .research/rng_42state_direct/decoupled_seed2026080206.log
```

## SHA-256

```text
b3cf9d1cbd105002f94cae13aed8e42682f1f29c5effb34565990a552ed600d7  verify_nonstrong_frontier.py
921b451145dda80299872e55e529b6003d6d885c4b78bb9a5f21fa6723926990  nonstrong_frontier_certificate.json
12ef714e76ecedc168f5981fbcad7951def5c25e397902495f92a2c218e5b010  solve_global_semiconjugacy.py
684b28901e34e16d16b5a52443ec8e5f5b0160aab707ec8de660b7a7a6c30af4  nonstrong_frontier_ball3.json
af12ee1f13c5cfafabcb81d6fe301fe3e3a8dfe7888977c95dd44b2e595792d2  global_semiconjugacy_result.json
0955b528d1cd3dc023d9b354d5a7b560e7321a1dc545dfffc3cb2f6a57f537e8  search_decoupled_output.cpp
1a6ab42d51aeff2a637e36896aaea551afcc78c44a40531aff2697112031be02  decoupled_seed2026080206.log
131eece7b8a5e01aed30708be73b73ea99bee05be8a763f7a7421535aa373413  verify_minimal_x_family.py
7d8670cb3bf914cc426245c2f4c1cc5c65294d4fb746499d9212645f1969f2dc  minimal_x_family_certificate.json
```
