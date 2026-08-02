# RAM kind 118 mode 2 acceptance

## Outcome

`kind=118, settings[0]=2` is a deployable static-analysis candidate. The current
binary accepts it through v15 deserialization, preserves it while building the
board, does not rewrite it merely by drawing the ordinary RAM property panel,
and serializes it unchanged on a later save.

This branch does not establish mode 2 tick semantics or its score effect. Those
must be checked in game by the owning task.

## Decisive evidence

- `parse_state @ 0x1401c05e5` routes save version `0xF` to
  `parse_v15 @ 0x1401beb42`.
- `get_component_v15 @ 0x1401bc87f` checks only `kind <= 124`. It reads the
  serialized setting count, appends each raw `u64`, and only appends defaults
  when the sequence is too short. It never validates an existing setting value.
- `load_schematic_raw @ 0x14027c2c6` clamps `word_size` but passes settings
  unchanged to `board_add_component @ 0x140243dca`.
- `board_add_component` appends missing defaults and truncates excess settings
  to the default sequence length. It does not validate individual elements, so
  the first value `2` survives and is stored in component fields `[21:22]`.
- `add_component @ 0x1401c0ff3` writes the setting count and each value as raw
  `u64`, with no enum validation.

## UI behavior

The RAM mode branch begins at `0x14077ded1` and reads `settings[0]` at
`0x14077dfd6`. It constructs only options `0` and `1`. For display, the current
index is clamped with `min(option_count - 1, settings[0])`, so value `2` previews
as the last legal label.

`config_listbox @ 0x1407581cd` initializes its result to `-1` and changes it only
after `igSelectable_Bool` reports a click. The caller checks for a nonnegative
result before `set_setting @ 0x14077e8c2`. Therefore opening the panel is safe.

The depth section reads mode at `0x14076c396` and is shown only when it is
strictly equal to `1`. Mode `2` skips that control, so its separate write at
`0x14076c6f9` cannot occur during ordinary panel drawing.

## Deployment rule

Deploy `kind=118, settings[0]=2` for immediate in-game validation. Do not click
either RAM mode entry after loading; a click intentionally writes legal value
`0` or `1` and destroys the candidate mode.

Machine-readable evidence is in `evidence.json`. Focused UI disassembly is in
`ui_ram_mode.disasm.txt` and `ui_ram_depth.disasm.txt`; the complete routing and
load/save pseudocode is kept alongside this report.

## Scope

No game process was started. No formal save, `levels.txt`, `settings.txt`, token,
or shared `src` file was read or modified. All generated files remain under this
research directory.
