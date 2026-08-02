# Arbitrary-T Kraft: exact distance/forest lower bounds

This note concerns only the zero-initial-state, constant-seed 65-cycle model

```text
B = T A T^-1
D = T(A+I)
C = A T^-1
4 wt(B_i) + wt(D_i) <= 16
4 wt(C_i) + wt(A_i) <= 16.
```

It does not touch or validate a game save.

## Elimination and fixed target basis

Let `K=A(A+I)`.  Direct multiplication gives the inverse-free equations

```text
D A = B D
C D = K.
```

`A`, `A+I`, and `K` all have rank 32.  Consequently `C` and `D` are bases.
Rows 12 through 26 of `A` have weight 5--7, so their output Kraft capacity is
only two `D` rows.  The corresponding 15 rows of `K` have weight 9--12.

## Support forest

For these 15 rows, each row of `C` has support size one or two.  Interpret a
singleton `{u}` as an edge from a distinguished zero vertex to `u`, and a pair
`{u,v}` as an ordinary edge.  Because `C` is invertible, these 15 incidence
vectors are independent.  Their graph is therefore a forest.

Call a `D` row *low* when its Hamming weight is at most four and *high*
otherwise.  No fixed `K` edge can join two low vertices: its label would then
have weight at most eight, whereas every one of the 15 labels has weight at
least nine.  Thus the high vertices cover all 15 forest edges.

If two high-low edges share their high endpoint, XORing their labels eliminates
that endpoint and leaves the XOR of two low vectors, of weight at most eight.
The exact distance-<=8 graph of the 15 labels contains only

```text
(12,16), (12,25), (13,26), (15,19)
```

with distances `8,7,4,7`.  It is triangle-free and has maximum matching three.
Therefore a high vertex has at most two low neighbours, and at most three high
vertices can have two.  If there are `h` high vertices, the forest has at most

```text
high-high edges + high-low edges
<= (h-1) + (h + min(h,3)).
```

For `h<=6` this is at most 14.  Hence **at least seven rows of `D` have weight
at least five**.  Their paired feedback inequalities force **at least seven
rows of `B` to have weight at most two**, and at most 25 rows of `B` can have
weight three.

Repeating the same exact argument at smaller Hamming thresholds gives

```text
# rows wt(D)>=2 : >=8
# rows wt(D)>=3 : >=8
# rows wt(D)>=4 : >=8
# rows wt(D)>=5 : >=7
# rows wt(D)>=6 : >=2
sum_i wt(D_i)   : >=65
```

## Similarity invariants

The verified characteristic/minimal polynomial is

```text
p(x)=x^32+x^21+x^20+x^19+x^18+x^17+x^15+x^14+x^9+x^6+1
    =0x1003ec241.
```

It is irreducible and primitive.  Thus every admissible `B` has the same
polynomial and its directed support graph is strongly connected.  A cycle-space
count gives `sum_i wt(B_i)>=35`: eleven nonzero characteristic-polynomial
coefficients require at least eleven distinct cycle-cover witnesses, while an
`m`-edge strongly connected 32-vertex graph has cycle-space dimension
`m-32+1`.

These are strict universal necessary conditions, but they do **not** yet form a
contradiction with the per-row Kraft inequalities.  They are intended as
sound pruning constraints for the exact SMT search, not as an UNSAT claim.

## Lossless search normalization

Because `C` is invertible, its support graph contains a perfect matching.
Simultaneously permuting the q coordinates (columns of `C`, rows of `D`, and
rows/columns of `B`) can move this matching to the diagonal.  This preserves
all output row weights and merely permutes the paired feedback row loads.
Hence an exact search may assume without loss of generality that every `C_i`
contains column `i`.  Rows 12--26 then choose at most one extra column, while
the other rows choose at most two.  This replaces the full support-subset
symmetry by a much smaller directed-extra-edge representation.

### Singleton propagation

This argument does not actually require normalization.  In arbitrary
coordinates, a singleton `C_i=e_j` makes `C D=K` give `D_j=K_i`.  Every `D`
row has weight at most 12: `B` is invertible, hence every `B_j` is nonzero, and
its feedback Kraft inequality leaves at most 12 seed leaves.  If `wt(D_j)` is
9--12, the same inequality forces `B_j` to be a unit row.  The equation
`D A=B D` then says `D_j A` is another row of `D`.  Iterate until the weight
reaches at most eight or exceeds twelve.

The exact weight trajectories are:

```text
 4:  9,13             impossible
 5:  9,12,17          impossible
12: 12,11,12,16       impossible
13: 11,11,11,13       impossible
14: 10,10,11,14       impossible
15: 10,10,15          impossible
16: 12,12,12,20       impossible
17: 10,15             impossible
18: 10,15             impossible
19:  9,16             impossible
20:  9,16             impossible
21: 11,17             impossible
22: 10,16             impossible
23:  9,13             impossible
24:  9,13             impossible
25:  9,10,8           not rejected by this obstruction
26:  9,13             impossible
```

Thus 14 of the 15 capacity-2 rows must have weight exactly two; only row 25
may remain singleton.  Capacity-3 rows 4 and 5 are also non-singleton.  Along
with the mandatory one entry in every invertible row, this proves
`sum_i wt(C_i)>=48`.

For additional propagation, `A C=C B` gives the general necessary inequality

```text
q_j = floor((16-wt(D_j))/4)
wt((A C)_i) <= sum(q_j for j in supp(C_i)).
```

It follows directly from the Hamming triangle inequality on `(C B)_i` and
`wt(B_j)<=q_j`.

Run the standalone verifier with:

```powershell
.venv\Scripts\python.exe .research\rng_cycle65_continue\kraft_smt_math_distance_bound.py
```

It regenerates `kraft_smt_math_distance_bound.json` and independently checks
all ranks, distances, cliques, matchings, polynomial identities, irreducibility,
primitivity, and stated numeric bounds.
