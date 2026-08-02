# RNG RAM candidate native score and submission audit

## Verdict

The current formal RNG candidate is internally consistent at:

```text
SHA-256 B8D3A056277AE8DC2BDE12A2ABB4D232BB57D5B036EA81565D0528EF07C75ECA
header 222 / 10
predicted leaderboard tuple 222 / 10 / 66
137 components / 308 wires
```

The native gate score is **222** and the native critical-path delay is **10**.
The earlier `6` and transient `5` delay headers were both underestimates. The
client-side kind-3 submission path accepts this tuple as an improvement over
the saved `396 / 10 / 66` result, provided the level is actually run so that
the simulation tick is not `-1`. Final server acceptance still requires the
normal in-game validation and submission.

This audit did not launch the game. The formal file was updated concurrently
by the parent task; this branch only added reproducible research artifacts.

## Native gate ledger

The installed XOR frontier is `3 / 2`. `add_cost(kind=10, (3,2))` derives the
Word XOR base point by calling `stareq * 8` at `0x14027AD4B`. The native code at
`0x14027ADA2..0x14027ADD9` multiplies and stores only pair qword 0 (gate), so
the derived pair is `(24,2)`, not `(24,16)` and not the static default
`(32,3)`.

For `kind=23, word_size=1`, the byte-piecewise gate formula returns one gate,
while `score_delay_core.c` returns the derived base delay unchanged: two.

```text
47 * OR Bit            =  47
42 * XOR Bit (3 gate)  = 126
19 * U1 Word XOR       =  19
 1 * ready Delay Bit   =   5
 1 * NOT Bit           =   1
 1 * RAM, 8-byte buf   =   8
 1 * associated load   =   8
 1 * associated store  =   8
                              ---
native gate total         222
```

The backing RAM, load port, and store port each use the associated backing
buffer length. They do not use the ports' U32 width. The old `266` derivation
incorrectly charged both ports as 32 gates. The later `210` total was correct
only for the superseded four-byte-buffer snapshot; the current reviewed RAM
buffer is eight bytes, so its three-part RAM group costs 24 gates.

## Native delay path

The decisive behavior is in `preorder.c:4151-4268`: for each ordinary
component, native preorder takes the maximum arrival over all input nets, adds
the component delay, and propagates the result to every output net. Therefore
the switched Architecture Input (`kind=62`) propagates its `control` arrival
to its `value` output. Its external data value is not an independent timing
boundary that can discard the ready-control path.

One exact critical path in the current formal file is:

```text
idx 2   Constant 1                                  +0 =  0
idx 3   ready Delay Bit                             +4 =  4
idx 4   NOT ready                                   +1 =  5
idx 0   switched Architecture Input (control->value)+0 =  5
idx 5/8 word and byte splitters                     +0 =  5
idx 38  OR Bit                                      +1 =  6
idx 75  XOR Bit                                     +2 =  8
idx 99  XOR Bit                                     +2 = 10
idx 118/122 makers                                  +0 = 10
idx 1   Architecture Output                         +0 = 10
```

The pure RAM steady-state combinational path is only
`OR 1 + XOR 2 + XOR 2 = 5`, but it is not the whole-circuit maximum. The
ready-control prefix adds `Delay 4 + NOT 1`, giving the native score of 10.
This also explains the already observed `396 / 10 / 66` baseline.

RAM mode 2 remains zero-delay:

```text
settings = (2, 512, 0)
pipeline depth = 0
RAM scored delay = 512 div (512 + 1) = 0
load delay = 0
store delay = 0
```

## Submission gate

The RNG level is `kind=architecture`, which maps to native schematic type 3.
It does not hit the type-5/type-6 preview exclusions in
`complete_current_level.c`. For type 3:

1. The simulation tick must not be `-1`.
2. `complete_level()` compares `gate * delay * (tick + 1)` with the saved best.
3. A strict improvement replaces the architecture frontier with one tuple and
   makes `complete_level()` return true.
4. `complete_current_level.c:887-893` then enqueues the sole kind-3 request.

For the current state:

```text
saved best = 396 * 10 * 66 = 261360
candidate  = 222 * 10 * 66 = 146520
improvement over saved best = 114840
public rank-1 reference      = 256014
margin below rank 1          = 109494
```

All 137 components are mutable and use automatic cost fields
`(cost_gate,cost_delay)=(-1,0)`. There are no custom components. The RAM data
is only eight bytes, far below the validation buffer cap. No additional local
compile verdict, immutable rejection, global leaderboard-frontier comparison,
or client validation filter was found on this path.

The request serializes the actual schematic and validation information; the
local gate/delay/tick tail fields are not authoritative wire fields. Thus the
hidden RAM mode-2 behavior must still pass the server's normal validation in
the game. Do not click the RAM mode dropdown because that overwrites hidden
`settings[0]=2` with visible mode 0 or 1.

## Reproduction

Run the focused read-only audit against the currently installed formal file:

```powershell
.\.venv\Scripts\python.exe `
  .research\rng_primitive_zero_audit\ram_tick_semantics\native_score_check\audit_candidate.py `
  --output .research\rng_primitive_zero_audit\ram_tick_semantics\native_score_check\evidence.json
```

The captured `evidence.json` verifies the exact SHA, byte-identical v15
round-trip, component/wire counts, automatic cost fields, full gate ledger,
weighted critical path, current progress frontiers, and header/native-score
agreement.

Supporting native artifacts:

```text
.research/rng_score_bypass/ida/score_network/add_cost.c
.research/rng_score_bypass/ida/ram/score_gate_component.c
.research/rng_score_bypass/ida/ram/score_delay_core.c
.research/rng_score_bypass/ida/ram/score_delay_component.c
.research/rng_score_bypass/ida/ram/preorder.c
.research/rng_score_bypass/ida/score_network/complete_level.c
.research/rng_score_bypass/ida/score_network/complete_current_level.c
.research/rng_switch_semantics/2026-08-02-U1异或后的开关外壳复核.md
```

## Superseded transient headers

During the concurrent audit, the same topology passed briefly through
`222/6` (`84476F2C...`) and `222/5` (`4F3AF040...`). Both were corrected after
the switched-input control dependency was recovered. The accepted audit
snapshot is `B8D3A056...`, `222/10`.
