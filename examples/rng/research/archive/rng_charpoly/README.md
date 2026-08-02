# RNG xorshift32 over GF(2)

`compute_xorshift32_poly.py` is a read-only, standard-library-only
certificate for the exact transition used by the live RNG test script:

```text
x ^= x >> 13
x ^= (x << 17) & 0xffffffff
x ^= x >> 5
```

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe .research/rng_charpoly/compute_xorshift32_poly.py `
  --test-script 'D:\Game\Steam\steamapps\common\Turing Complete\campaign\rng\test.si' `
  --output .research/rng_charpoly/result.json
```

The script obtains the minimal polynomial from the relation for
`e_0, A e_0, ..., A^32 e_0`; the first 32 vectors have rank 32, so `e_0` is
cyclic.  It independently obtains the characteristic polynomial as
`det(x I + A)` using fraction-free polynomial Bareiss elimination.  Both
results must match or the script fails.

The resulting polynomial is

```text
p(x) = x^32 + x^21 + x^20 + x^19 + x^18 + x^17 + x^15 + x^14
       + x^9 + x^6 + 1
```

Its coefficient-bit encoding is `0x1003ec241`.  Rabin checks show that it is
irreducible over GF(2), and `2^32 - 1 = 3 * 5 * 17 * 257 * 65537`; checking
`x^((2^32-1)/q) != 1` for every listed prime factor `q` proves that `p` is
primitive.  Therefore the characteristic and minimal polynomials are both
`p`, the linear map `A` has order `2^32 - 1`, and every nonzero 32-bit seed
has the full nonzero-state period.

The optional live-source check expects SHA-256
`b396a9d5bba76bec2ceb123478dadc4616b6057894f17775982ed097c62fd50c`.
