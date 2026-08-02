# RNG `Component.is_late_version` reachability audit

Target executable SHA-256:
`c93f5e8e826050c3f92e2b3891d26fcdfc933658614185cb9b2eb6a34c5b8d1c`.

## Outcome

`Component.is_late_version` is a real in-memory zero-cost branch, but it is not
reachable from a v0-v15 `circuit.data` file and is not persistent. There is no
save-only transformation that can deploy it. Do not modify the production RNG
save for this route.

The decisive distinction is:

- Runtime semantics: setting `Component + 0x20` to `1` makes
  `get_gate_cost(Component) @ 0x140276993` return zero immediately.
- Deployability: every supported parser and every normal board-construction
  route produces `+0x20 == 0`; v15 serialization omits the byte entirely.

Even a hypothetical runtime memory write would be lost when the schematic is
saved or serialized into the kind-3 validation request.

## Field layout and cost branch

The recovered current layout is documented in
`.research/save_monger_current/common.nim:425-458`:

```text
Component +0x00  kind
          +0x08  permanent_id
          +0x10  parent_permanent_id
          +0x18  top_level_permanent_id
          +0x20  is_late_version
          +0x28  other_version
          +0x1d8 is_immutable
```

The decompilation in
`.research/rng_score_bypass/ida/get_gate_cost_component.c:27-30,123-128`
checks `a1[32]` before all ordinary component-cost logic. When it equals one,
the function returns its initial zero result.

## Save deserialization cannot set the flag

All sixteen compiled v0-v15 `get_component` functions first clear their output
with `nimZeroMem(..., 0x230)`. None subsequently writes the non-stack byte at
offset `+0x20`, and none of the recovered version sources names
`is_late_version` or `other_version`.

`parse_state @ 0x1401c05e5` dispatches directly on versions 0 through 15 and
then only supplies unrelated defaults. It has no migration or post-processing
pass that marks parsed components as late.

The full per-version call table and instruction addresses are recorded in
`legacy_deserialize/legacy_notes.md`.

## Board construction clears or drops the flag

`load_schematic @ 0x14027e073` calls `parse_state` and then
`load_schematic_raw @ 0x14027c2c6`. The latter copies each parsed 560-byte
component into a temporary, but does not pass `+0x20` or `+0x28` to
`board_add_component @ 0x140243dca`.

`board_add_component` clears its 560-byte result at `0x140243f5b` and again on
the construction branch at `0x1402450f9`. Its signature contains no late
version argument, and its assignments leave both fields zero.

The same constructor boundary is used by the relevant creation paths:

- normal UI component creation;
- schematic load and load-morph application;
- campaign/hub and custom-prototype instantiation;
- clipboard paste.

Component/board copy helpers faithfully propagate an already-existing
`+0x20`, so they do not independently destroy a live value. They also never
create the value. Clipboard paste ultimately reconstructs components through
`board_add_component`, so copied clipboard state cannot seed a persistent one.

## Persistence and server request both omit it

The v15 component serializer in
`.research/save_monger_current/save_monger.nim:85-120` writes the component
kind, placement, IDs, labels, settings, buffer data, `is_immutable`, cost
variant, and linked-component data. It never writes `is_late_version` or
`other_version`.

The compiled serializer
`.research/rng_primitive_zero_audit/ram_enum_acceptance/deserialize_ui/add_component_save_monger.c`
agrees: its only boolean from the late part of `Component` is `a2[472]`, the
`is_immutable` field. `state_to_binary` invokes this same component serializer.

The kind-3 validation request embeds the current schematic and dependencies as
`state_to_binary` blobs. Therefore its wire payload has no independent late
version field. The request tail's local gate/delay/tick qwords are also outside
the serialized kind-3 object, as documented in
`.research/rng_score_bypass/kind3_wire/wire_reader/sub_serializer/kind3_serializer_map.md`.

Consequences:

1. A legal or malformed v0-v15 save cannot initialize the byte to one.
2. Board loading reconstructs it as zero even if a parser-side representation
   somehow contained it.
3. A transient in-memory one is omitted from the next save.
4. The server receives a reserialized schematic without the flag.

## Whole-executable write scan

The apparent immediate writes of `1` to displacement `+0x20` do not target a
`Component`. In particular, the writes at `0x1406803a4` and `0x1406820e7`
belong to two `recursive_load` functions and target a 64-byte file-tree node.
That node contains two strings, booleans, and a child sequence; it is not the
560-byte component structure. Other matches are generic `Option.some` or
unrelated campaign helpers.

## Decision

This route is closed for save editing. It would require an external runtime
memory patch or executable modification, neither of which is a deployable
game-save solution and neither survives the normal validation serialization
boundary. No production save was changed during this audit.

## Evidence

- `legacy_deserialize/legacy_notes.md`: complete v0-v15 parser and false-positive
  write audit.
- `ida/`: focused decompilations for save, load, construction, UI, clipboard,
  morph, and server-request paths.
- `.research/rng_score_bypass/ida/late_version_construct_copy/`: independent
  component-copy and construction decompilations.
- `.research/save_monger_current/save_monger.nim`: recovered v15 format.
- `.research/rng_score_bypass/kind3_wire/wire_reader/sub_serializer/kind3_serializer_map.md`:
  kind-3 request serialization map.
