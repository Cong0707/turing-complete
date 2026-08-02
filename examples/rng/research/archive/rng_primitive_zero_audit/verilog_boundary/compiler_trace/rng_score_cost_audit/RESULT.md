# RNG 266 vs 304 independent gate-cost audit

Audit target at start of review:

```text
examples/rng/candidate/circuit.data
SHA-256 1FCB434673503E5D9BE165A6BB3D8C2DAB01B68923AD0E9F8E8FAA0B29A8EA55
declared 266 / 6 / 66
137 components, 308 wires
```

Game executable reviewed without launching it:

```text
D:\Game\Steam\steamapps\common\Turing Complete\Turing Complete.exe
SHA-256 C93F5E8E826050C3F92E2B3891D26FCDFC933658614185CB9B2EB6A34C5B8D1C
```

## Decision

For the frozen `1FCB...` candidate, the current binary's gate-cost path gives
**266 gates, not 304**. The entire 38-gate difference is explained by the 19
`kind=23` Word XOR components stored with `word_size=1`:

```text
19 * (incorrect 3 - actual 1) = 38
304 - 38 = 266
```

The old 304 derivation treated those 19 components as ordinary `kind=10` Bit
XORs at 3 gates each. That is not what `get_gate_cost` does for `kind=23` at
width one.

## Decisive binary path

The installed `levels.txt` has the XOR frontier `3/2`. During initialization,
`add_cost(kind=10, (3,2))` propagates that frontier to Word XOR:

1. `add_cost @ 0x14027ADE8` first inserts `(3,2)` for `kind=10`.
2. It calls `stareq * 8 @ 0x14027AD4B` on a copy. Disassembly at
   `0x14027ADA2..0x14027ADD9` multiplies and stores only the first qword (gate),
   leaving delay unchanged. The derived Word XOR base point is `(24,2)`.
3. The `case 0x0A` branch inserts that point for `kind=0x17` at
   `0x14027B008..0x14027B00D`.
4. `get_gate_cost(kind, width, base) @ 0x140275F1B` places `kind=0x17` in the
   byte-piecewise group. For `width % 8 <= 3`, the exact branch at
   `0x14027612C..0x1402761D7` computes:

   ```text
   gate = base * (width div 8) + (width mod 8)
   ```

5. Therefore `kind=23, width=1` is `24*0 + 1 = 1` gate. In fact, the result is
   one for any selected base point, so the conclusion does not depend on
   frontier ordering or a startup sync changing the XOR base.

The independent static score-table extraction from the same executable agrees:
`.research/rng_score_table/component_scores.json` records
`com_xor_word, width=1 -> gate=1`.

Candidate decoding and byte-identical v15 round-trip show exactly 19 such
components, all with `(kind, word_size, cost_gate, cost_delay)=(23,1,-1,0)`.
The component wrapper uses the explicit component word size before calling the
formula (`get_gate_cost_component.c:90-117`); it does not normalize U1 to U8.

## Full difference ledger

Starting from the already game-verified all-Bit-XOR baseline:

```text
396
- 19 * (3 - 1)     U1 Word XOR substitutions
- 32 * 5           remove 32 state Delay Bits
+ 4                mode-2 RAM, buffer_size=4
+ 32 + 32          native U32 load and store ports
= 266
```

The RAM and native-port terms are orthogonal to the 38-gate dispute. The RAM
branch is recovered in `score_gate_component.c`: nonzero `settings[0]` costs
`buffer_size`, hence four gates here.

## Minimal in-game acceptance

For this frozen 266-header artifact, one action is sufficient to distinguish
the disputed outcomes: with the game starting from a closed process, open RNG
and let the level compile, then read the live gate count before running tests.
It should read `266`; `304` would mean the loaded components are not the audited
U1 `kind=23` instances. Do not click the RAM mode dropdown because it would
replace hidden `settings[0]=2`.

Record the circuit SHA before launch so the result is tied to the audited file.
The candidate and formal save were concurrently rewritten at 06:53 to a
`210/6` header (SHA-256 `CAC4F4E764B93A47A00371A9EE0250B793AD59D43ECAD5300DAD45535BB20BAD`)
while this audit was running. That later 210 claim is outside this report; it
does not alter the 266-versus-304 conclusion for `1FCB...`.

