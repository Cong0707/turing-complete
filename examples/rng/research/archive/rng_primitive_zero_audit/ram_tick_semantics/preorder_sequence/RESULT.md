# RAM preorder and same-tick semantics

## Conclusion

For a connected RAM load/save pair, mode_run emits kind 54 (load) before kind 56
(save). A same-address read and write in one tick is therefore
**read-before-write / old-value**.

This is stronger than an index-order observation. `connect_to_ram` creates a
synthetic data dependency from the load output pin to the save input pin, so
Kahn traversal cannot make the save ready until the load has been processed.

## Decisive chain

1. `connect_to_ram @ 0x1402BABFD` handles kind 54 at
   `0x1402BB1D1`:
   - constructs rotated `(1, 0)` at `0x1402BB201-0x1402BB26B`;
   - converts it to the load pin point at `0x1402BB2B0`;
   - appends that point to the pending-load list at `0x1402BB2F9`.
2. The kind 56 branch starts at `0x1402BB328`:
   - constructs rotated `(-1, 0)` at `0x1402BB342-0x1402BB3AC`;
   - converts it to the save pin point at `0x1402BB3F1`;
   - iterates every pending load point from `0x1402BB46C`;
   - creates a synthetic wire, resolves `add_wire_pins @ 0x1402B9EE2`
     at `0x1402BB660`, and calls it at `0x1402BB6DA` (context form) or
     `0x1402BB727` (null-context form).
3. Prototype pin mapping in `preorder.c:1994-2049` puts the selected input
   group into the point map with direction byte `1`; `preorder.c:2073-2114`
   puts output group `prototype[16]` into it with direction byte `0`.
   For the native prototypes:
   - kind 54 has input/output counts `prototype[12]=3`,
     `prototype[14]=0`, `prototype[16]=2`;
   - kind 56 has `prototype[12]=5`, `prototype[14]=0`,
     `prototype[16]=1`.
   Thus the `(1,0)` kind-54 point is an output and the `(-1,0)` kind-56
   point is an input.
4. `connect @ 0x1402BCAA9` resolves each wire point to
   `(component_index, port_index, is_input)` and appends that directed pin
   record to the graph. `preorder.c:3186-3219` sends direction `0` to the
   output-net map (`context[50]`) and direction `1` to the input-net map
   (`context[34]`).
5. `is_ready @ 0x1402BD1A4` iterates only the candidate component's input
   pins (`component[6]`), resolves each through `context[34]`, and returns
   false while the processed-output count for that net is below the net's
   required producer count. In the Kahn loop, processing a popped component
   walks `context[50]`, increments that count (`preorder.c:3683-3706`), and
   only then rechecks dependent components (`preorder.c:3710-3777`). Hence
   the artificial wire is a strict load-output -> save-input dependency.

## Traversal and final sequence

- Initial ready candidates are scanned in ascending component index order
  (`preorder.c:3839-3880`).
- The ready sequence is a stack: `pop @ 0x1402BD791`, called at
  `0x1402D4871`. Therefore independent simultaneously-ready candidates use
  LIFO order.
- Each popped ordinary component is immediately appended to the internal
  topological sequence at `0x1402D4BE0`.
- Final classification is `preorder.c:4341-4412`. Static prototype fields
  make both kind 54 and kind 56 enter the middle sequence `v277`; neither
  enters the separately sorted head/tail sequences.
- Only head and tail are sorted (`0x1402D7628`, `0x1402D767B`). Concatenation
  at `0x1402D77B1` and `0x1402D7851` is
  `head + v277 + tail`, so the middle group's Kahn order is preserved exactly.
- The final sequence is written to `PreorderResult` at `0x1402D8414`.

## Codegen consumption

- `process_compile_request.c:421-429` passes that `PreorderResult` sequence
  to `generate_source`; `generate_source.c:1148-1153` stores it unchanged in
  the codegen context.
- mode_run calls `add_circuit_code` at `0x14049FEAA` with the same array.
  `add_circuit_code` reads its length/data at `0x1404415AC` and
  `0x14044164C`, fetches the next component index at `0x140441682`, selects
  `index * 0x230` at `0x1404416D1`, then dispatches by kind at
  `0x1404467E4-0x14044680B`.
- Kind 54 emits from `0x14044C097`; kind 56 emits from `0x140452891`.
  Since the dependency fixes their preorder relation, the generated load
  expression executes before the generated store in mode_run.

## Reproducible artifacts

- `ram_tick_semantics/connect_to_ram.c`
- `ram_tick_semantics/add_wire_pins.c`
- `ram_tick_semantics/connect.c`
- `ram_tick_semantics/is_ready.c`
- `ram_tick_semantics/preorder_pop.c`
- `ram_tick_semantics/generate_source.c`
- `rng_score_bypass/ida/ram/preorder.c`
- `ram_tick_semantics/ram_prototypes.json`

Static analysis only. No game process was started and no save was read or
modified for this result.
