# v0-v15 `is_late_version` deserialization audit

Target EXE SHA-256:
`c93f5e8e826050c3f92e2b3891d26fcdfc933658614185cb9b2eb6a34c5b8d1c`.

## Conclusion

There is no save-controlled field and no assignment to `1` for
`Component.is_late_version` (`Component + 0x20`) anywhere in the v0-v15
`circuit.data` deserialization path. Every version initializes the field to
zero, the common version dispatcher performs no component post-processing,
and `load_schematic_raw` drops both `is_late_version` and `other_version` when
it rebuilds the board component. A normal or deliberately malformed v0-v15
file therefore cannot set this flag through the supported parser.

## Layout and on-disk schemas

- `.research/save_monger_current/common.nim:425-433` defines the current
  `Component` prefix. `is_late_version` follows the three 64-bit permanent IDs,
  at `+0x20`; `other_version` is at `+0x28`.
- The compiled component copy helper
  `eqcopy___modelZsave95mongerZversionsZv0_u148 @ 0x14018101d` copies source
  byte `+0x20` to destination byte `+0x20` at `0x14018109d-0x1401810a5`.
  This independently confirms the offset and shows that the helper is only a
  copier, not a setter.
- `eqdup...u151 @ 0x1401844ad` similarly copies the byte at
  `0x140184541-0x140184549`; `eqsink...u154 @ 0x140185fc3` copies it at
  `0x140186043-0x14018604b`.
- `eqwasMoved...u142 @ 0x14017d2b3` explicitly clears the byte at
  `0x14017d306`.
- The only versioned boolean added in v12-v15 is `is_immutable`, not
  `is_late_version`: `v12.nim:41`, `v13.nim:29`, `v14.nim:29`, and
  `v15.nim:27`. The v15 serializer likewise writes `is_immutable` at
  `.research/save_monger_current/save_monger.nim:85-111` (line 98) and never
  writes `is_late_version`.

The source constructors that leave all unspecified fields at their zero value
are:

| versions | source constructor |
| --- | --- |
| v0 | `versions/v0.nim:24-40`, constructor at line 34 |
| v1 | `versions/v1.nim:31-49`, constructor at line 43 |
| v2 | `versions/v2.nim:17-38`, constructor at line 32 |
| v3-v5 | each `get_component` starts at line 16, constructor line 31 |
| v6 | `versions/v6.nim:18-41`, constructor at line 35 |
| v7-v11 | each constructor is `Component(kind: kind)` at line 22 |
| v12 | `versions/v12.nim:16-88`, constructor at line 22 |
| v13-v15 | each constructor is at line 10 |

No version file contains the identifier `is_late_version` or assigns
`other_version`.

## Current EXE parser proof

All sixteen compiled `get_component` functions first clear their output
`Component` with `nimZeroMem(..., 0x230)`. The relevant call addresses are:

| version | function | output zeroing |
| --- | --- | --- |
| 0 | `0x140191d10` | `0x140191d80` |
| 1 | `0x140194e72` | `0x140194eee` |
| 2 | `0x140196eff` | `0x140196f87` |
| 3 | `0x14019936f` | `0x1401993f7` |
| 4 | `0x14019b82f` | `0x14019b8b7` |
| 5 | `0x14019dd6f` | `0x14019ddf7` |
| 6 | `0x1401a03bf` | `0x1401a0447` |
| 7 | `0x1401a2a7f` | `0x1401a2b13` |
| 8 | `0x1401a5f3f` | `0x1401a5fd3` |
| 9 | `0x1401a917f` | `0x1401a9213` |
| 10 | `0x1401ac3af` | `0x1401ac443` |
| 11 | `0x1401af64f` | `0x1401af6e3` |
| 12 | `0x1401b29ff` | `0x1401b2a95` (local component also `0x1401b2aa9`) |
| 13 | `0x1401b5e6f` | `0x1401b5f05` (local component also `0x1401b5f19`) |
| 14 | `0x1401b927f` | `0x1401b9315` (local component also `0x1401b9329`) |
| 15 | `0x1401bc87f` | `0x1401bc915` (local component also `0x1401bc929`) |

A Capstone scan of each complete function finds no non-stack `+0x20` access.
For v12-v15, the local component's corresponding stack byte is also never
written after its `0x230` clear. The only parsed boolean at the later component
offset is `is_immutable`.

`parse_state @ 0x1401c05e5` clears its `ParseResult` at `0x1401c065e`, reads
the file's first byte into `ParseResult.version` at `0x1401c06f3-0x1401c06fb`,
and directly dispatches to v0-v15 at `0x1401c076d`, `0x1401c07ba`,
`0x1401c0807`, `0x1401c0854`, `0x1401c08a1`, `0x1401c08ee`,
`0x1401c093b`, `0x1401c0988`, `0x1401c09d5`, `0x1401c0a22`,
`0x1401c0a6f`, `0x1401c0abc`, `0x1401c0b09`, `0x1401c0b56`,
`0x1401c0ba3`, and `0x1401c0bec`. After dispatch it only supplies defaults
for clock speed and custom ID. This matches
`.research/save_monger_current/save_monger.nim:45-83`; there is no separate
legacy-upgrade loop that marks components.

## Board reconstruction drops the field

`load_schematic @ 0x14027e073` calls `parse_state` at `0x14027e147`, then
immediately calls `load_schematic_raw` at `0x14027e1bf`.

In
`.research/rng_primitive_zero_audit/ram_enum_acceptance/deserialize_ui/load_schematic_raw.c`:

- lines 266-284 clear and copy each 560-byte parsed component;
- lines 633-680 prepare the call to `board_add_component`;
- neither parsed `v30[4]` (`+0x20`) nor `v30[5]` (`+0x28`) is used in that
  component loop or passed to the constructor;
- the call is at `0x14027de1c`. Its fourteenth argument is the literal zero
  stored at `0x14027ddb4`, but that argument is the requested board index, not
  either version field.

`board_add_component @ 0x140243dca` clears its 560-byte component temporary at
`0x140243f5b` and again on the construction branch at `0x1402450f9`.
The decompilation in `board_add_component.c:552-872` assigns all supplied
fields but never assigns `v105[4]` (`+0x20`) or `v105[5]` (`+0x28`). The final
component copy therefore preserves zero.

## Explicit `+0x20 = 1` false positives

A whole-EXE scan for an immediate byte write of `1` at displacement `+0x20`
found eight sites. None is a `Component` setter. Four are generic renderer
`Option.some` helpers, two are `some__modelZcampaigns_u9387`, and the remaining
two are:

- `recursive_load__presenterZutilities_u37639 @ 0x14067f85f`, write at
  `0x1406803a4`;
- `recursive_load__presenterZutilities_u35829 @ 0x140681a0b`, write at
  `0x1406820e7`.

The extracted pseudocode proves both recursive-load writes target a 64-byte
heap node allocated with `nimNewObj(64, 8)`, not a 560-byte component. The node
holds two strings at `+0/+16`, a path-prefix boolean at `+32`, children at
`+40`, and another boolean at `+56`; see `000000014067f85f.c:238-263,343-347`
and `0000000140681a0b.c:143-170,250-254`.

Thus no observed immediate-one write can seed the component copy helpers in
the v0-v15 load chain.
