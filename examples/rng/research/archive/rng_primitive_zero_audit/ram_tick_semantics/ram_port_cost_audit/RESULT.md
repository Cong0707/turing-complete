# Native RAM port gate-cost audit

## Verdict

For a `kind=118` RAM whose runtime buffer is eight bytes, the native gate
score is:

```text
backing RAM = 8
load port   = 8
store port  = 8
RAM group   = 24
```

The U32 word size of the load/store ports does not make either port cost 32.
Both access ports receive the backing RAM's runtime buffer length in their
`calculated_gate` field, and the generic component scorer returns that field.

This closes both current ledgers:

```text
222 candidate = 47 OR + 126 Bit XOR + 19 U1 Word XOR
              + 5 ready Delay + 1 NOT + 24 RAM group

191 candidate = 47 OR + 57 Bit XOR + 57 U1 Word XOR
              + 5 ready Delay + 1 NOT + 24 RAM group
```

The old research file at
`.research/rng_control_simplify/candidate/circuit.data` still declares
`191/6`, but a read-only native audit computes `191/10/66`. It must not be
deployed until rebuilt with header delay 10. Its native energy is 126060.

## Native evidence

In `score_gate_component.c:82-86`, kinds 54 and 56 return component qword 35:

```c
else if ( *a1 <= 0x76u && (v2 == 54 || v2 == 56) )
{
  gate_cost = *((_QWORD *)a1 + 35);
}
```

During RAM association, `preorder.c:2297-2316` writes the backing RAM buffer
length (`v193[39]`) to qword 35 of every associated access port:

```c
*(_QWORD *)(component + 288) = v193[39];
```

For kind 118 itself, `score_gate_component.c:56-75` returns qword 39 directly
in nonzero mode, which is also the runtime buffer length.

The compile path normalizes serialized buffers of length at most seven to the
component default before this association. Therefore eight bytes is the
smallest serialized length that remains eight at scoring time; it cannot be
replaced by four bytes to obtain a 12-gate RAM group.

## Reproduction

The generic native-score auditor can be run read-only against either topology:

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_primitive_zero_audit\ram_tick_semantics\native_score_check\audit_candidate.py `
  .research\rng_control_simplify\candidate\circuit.data
```

Observed decisive fields for the 191 topology:

```text
declared_header     [191, 6]
native_score        [191, 10, 66]
gate_ledger         RAM=8, load=8, store=8
derived Word XOR    [24, 2]
v15 round trip      true
```

The audit itself did not launch the game or modify the formal save. After the
audit passed, the parent flow checked that no game process existed and
deployed the corrected `191/10` candidate directly. The post-deployment formal
SHA-256 was
`8B3FA9303BE44958651EA90653D045A468FB9DD18E678380136D4B724DCD778D`,
byte-identical to the reviewed candidate.
