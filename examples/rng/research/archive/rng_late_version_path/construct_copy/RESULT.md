# `Component.is_late_version` construction and persistence audit

## Result

`Component.is_late_version` is byte offset `+0x20`; `is_immutable` is the
separate byte at `+0x1D8` (`common.nim:425-467`).  A normal RNG XOR component
cannot obtain `is_late_version = 1` from a v15 save, any older save version,
native/custom prototypes, clipboard paste, campaign/immutable loading, or
load morphing.

The route is not deployable through save editing.  Every persistent load path
reconstructs a zero-initialized Component, and the save format has no field
from which `+0x20` could be restored.

## Construction

- `board_add_component.c:550-552` zeroes all 560 bytes with
  `nimZeroMem(v105, 560)` before assigning serialized/prototype fields.
- Its argument list has no late-version argument, and no subsequent byte write
  targets offset `+0x20`.
- Both kind 78 custom lookup and native prototype lookup flow into this same
  construction (`board_add_component.c:229-244,360-405`).
- UI creation reads prototype `+472` (`is_immutable`) and passes it to
  `board_add_component`, but never reads prototype `+32`
  (`add_ui_component.c:174-219`).

Therefore a newly placed normal RNG XOR has `is_late_version = 0`.

## Copy and clipboard

- Component `eqcopy`, `eqdup`, and `eqsink` each perform only
  `dst[+32] = src[+32]` (`component_eqcopy.c:22-30`,
  `component_eqdup.c:31-40`, `component_eqsink.c:16-24`).  They preserve an
  already-existing value but cannot synthesize `1`.
- Clipboard copy first uses full Component copy and then a 560-byte `qmemcpy`,
  so an in-memory value can exist in the clipboard cache
  (`copy_selection_to_clipboard.c:462-487`).
- Clipboard paste extracts `+472` and other public fields, but not `+32`, then
  calls `board_add_component` (`add_clipboard_to_board.c:652-698`).  The pasted
  Component is consequently zero at `+0x20`; the later copy at lines 702-710
  copies that newly reconstructed Component, not the clipboard source.

## Save, load, and upgrade

- The v15 serializer writes `is_immutable` but no `is_late_version`
  (`save_monger.nim:85-135`).
- The v15 reader constructs `Component(kind: kind)`, which zero-initializes
  omitted fields, and reads only `is_immutable` (`versions/v15.nim:4-27`).
- No file under `versions/v0.nim` through `versions/v15.nim` references
  `is_late_version`; older formats cannot encode it either.
- `load_schematic` performs `parse_state` and then `load_schematic_raw`
  (`load_schematic.c:49-55`).  The raw loader expands serialized fields and
  calls `board_add_component`, without a `+0x20` input
  (`load_schematic_raw.c:625-678`).
- Both campaign and immutable/file branches ultimately call this same
  `load_schematic` (`load_level_model.c:795-799,964-990,1087`).
- `apply_load_morph` copies an old 560-byte Component for inspection, but
  rebuilds the result via `board_add_component`
  (`apply_load_morph.c:795-804,850-888`), again resetting `+0x20`.

Even if memory somehow contained `1`, saving omits it and reloading resets it.

## False-positive setters

The two immediate `+0x20 = 1` stores in `recursive_load` at
`0x14067F85F`/`0x140681A0B` belong to the manual-entry tree.  The external
caller of the latter is `get_manual_entry_unlocked_pages @ 0x1406835ED`
(`late-construct-decompile2.log:231-243`).  They are not Component loaders or
setters and cannot affect RNG components.

## Final decision

There is no save-editable path to set `Component.is_late_version` for RNG XOR.
In-memory copy helpers only preserve a value that must already exist; clipboard
paste, save/reload, and old-version morphing all erase it.  Close this route.
