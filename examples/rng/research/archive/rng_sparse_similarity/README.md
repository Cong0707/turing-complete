# xorshift32 sparse similarity / Galois certificate

The xorshift32 transition used by the RNG challenge is cyclic.  Taking the
Krylov basis

```text
P = [e0, A*e0, ..., A^31*e0]
q = P^-1*x
```

gives the exact similar transition

```text
B = P^-1*A*P
```

in Galois/column-companion form.  Its characteristic polynomial is

```text
x^32 + x^21 + x^20 + x^19 + x^18 + x^17
     + x^15 + x^14 + x^9 + x^6 + 1
```

Thus 23 rows of `B` are wires and nine rows are two-input XORs.  Every row has
weight at most two, the transition costs exactly nine XOR2 components as this
direct construction, and its combinational depth is one XOR layer.

This does **not** make the complete 65-cycle RNG a nine-XOR circuit.  For this
specific Krylov basis, `P`, `P^-1`, steady output `C=A*P`, and tick-zero load
`P^-1*A` are dense.  The JSON records transparent independent-row upper bounds
for those maps; shared synthesis may reduce them, but they are intentionally
excluded from the nine-XOR recurrence count.

Rebuild the certificate without importing the save writer or game modules:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
.\.venv\Scripts\python.exe `
  .research\rng_sparse_similarity\verify_galois_similarity.py `
  --output .research\rng_sparse_similarity\galois_similarity_certificate.json
```

Verify the persisted result by reconstructing every matrix, checking
Cayley-Hamilton on all 32 basis vectors, and replaying 69 seeds for 65 outputs:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
.\.venv\Scripts\python.exe `
  .research\rng_sparse_similarity\verify_galois_similarity.py `
  --verify-existing .research\rng_sparse_similarity\galois_similarity_certificate.json
```

## Fixed-Galois 65-cycle Kraft family

For the complete constant-seed feedback equation, every basis transform that
keeps this exact Galois `B` has the form

```text
T = Z*P^-1,  Z in GF(2)[B] and Z != 0
D = T*(A+I)
```

The polynomial is primitive, so all nonzero `Z` are invertible.  Row 6 of `B`
has weight two.  The map from the 32 coefficients of `Z` to row 6 of `D` is
invertible, so that `D` row is a lossless 32-bit parameter.  Its Kraft cap is
eight, reducing the exact search to

```text
sum(C(32,k), k=1..8) = 15,033,172
```

parameters.  The C++ enumerator checks the other eight cap-8 rows first and
then all 23 cap-12 rows, using about 128 KiB of lookup tables and constant
enumeration memory:

```powershell
g++ -std=c++20 -O3 -DNDEBUG `
  -o .research\rng_sparse_similarity\kraft_enumeration.exe `
  .research\rng_sparse_similarity\kraft_enumeration.cpp
.research\rng_sparse_similarity\kraft_enumeration.exe `
  .research\rng_sparse_similarity\kraft_enumeration_certificate.json
```
