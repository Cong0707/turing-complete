# RAM mode 2 tick semantics

## Result

For a RAM component with `settings=[2,512,0]`, the current native runtime uses
zero execution pipeline depth and zero scored RAM delay:

```text
get_ram_pipeline_depth(settings[0] == 2) = 0
scored delay = 512 div (512 + 1) = 0
```

The load/save code generator has no deferred-write phase. A load emits an
immediate `load(...)`, and a save emits an immediate `store(...)`. The
preorder builder creates a synthetic dependency from every load linked to a
RAM to its linked save. Therefore a connected same-RAM pair is strict:

```text
RAM load -> RAM save
same-address same-tick result -> read-before-write / old value
```

There is no global `kind=54` before `kind=56` (or reverse) rule. Both native
prototypes have `word1_proto_qword8=0` and `word2_proto_qword8=0`, so both are
placed in the same unsorted middle group `v277` by `preorder.c:4367-4396`.
The final sequence is `sorted(v279) & v277 & sorted(v275)` at
`preorder.c:4472-4486`.

Within that group, readiness is determined by input dependencies. The ready
list is popped from its final element (LIFO), and no type-level priority exists
in `is_ready @ 0x1402BD1A4`. Instead, `connect_to_ram @ 0x1402BABFD` records
kind-54 load output points, then the kind-56 branch creates synthetic wires
from those outputs to the save input. `is_ready` sees those wires through the
ordinary input-net map, so the save cannot become ready until each linked load
has been processed. Independent components not linked to the same RAM still
follow ordinary Kahn/LIFO ordering, but connected RAM load/save pairs do not.

For the RNG recurrence under consideration, `save.data` is also computed from
`load.output`. Both the explicit data path and the RAM-specific synthetic edge
force the topology

```text
RAM load -> recurrence logic -> RAM save
```

and therefore guarantee old-value read semantics for the state update. This is
the safe topology for the candidate build.

## Decisive addresses

- `get_ram_pipeline_depth @ 0x14021A94F`: only mode `1` returns
  `settings[1]`; every other mode returns `0`.
- `kind=54` entry `0x14044C097`; pipeline branch `0x14044F20D`; mode 2 takes
  the depth-zero path beginning at `0x14044F213`.
- Depth-zero load emission: `0x14044EE34-0x14044EFE2` and
  `0x14044F2A8-0x14044F40B`.
- Load output-cache store: `0x14044F679-0x14044F8B6`. Refresh reads this cache
  and does not reread RAM.
- `kind=56` entry `0x140452891`; refresh skips the branch at
  `0x140452AEB/0x140452AF2`.
- Save inputs: enable `0x14045600E`, address `0x1404552ED`, data
  `0x14045627A`; immediate generated store `0x14045631E`.
- `connect_to_ram @ 0x1402BABFD`: kind-54 branch `0x1402BB1D1` appends its
  output point at `0x1402BB2F9`; kind-56 branch `0x1402BB328` iterates those
  points and creates synthetic wires via `add_wire_pins @ 0x1402B9EE2`, called
  at `0x1402BB6DA/0x1402BB727`.
- Kahn pop `0x1402D4871`, ordinary-component append `0x1402D4BE0`; only the
  head/tail groups are sorted at `0x1402D7628/0x1402D767B`.
- mode_run consumes the resulting sequence through
  `add_circuit_code @ 0x14049FEAA` without reordering it.

## Evidence

- `ram_prototypes.json`: direct native prototype dump for kinds `54` and `56`.
- `preorder_pop.c`: LIFO ready-list pop.
- `is_ready.c`: dependency-only readiness check.
- `connect_to_ram.c`, `add_wire_pins.c`, and `connect.c`: synthetic
  load-output to save-input dependency construction.
- `preorder_sequence/RESULT.md`: complete directed-pin mapping, Kahn traversal,
  final concatenation, and codegen-consumption proof.
- `D:/Develop/Other/turing-complete/.research/rng_score_bypass/ida/ram/preorder.c`:
  classification and final concatenation.
- `ram_codegen_load_region_44ee00_452700.txt`: load branch disassembly.
- `ram_codegen_save_branch_452700_456b00.txt`: save branch disassembly.
- `D:/Develop/Other/turing-complete/.research/rng_primitive_zero_audit/ram_enum_acceptance/deserialize_ui/RESULT.md`:
  serialization/UI acceptance of mode `2`.

## Deployment constraint

`[2,512,0]` is ready for immediate candidate construction and in-game
validation. Do not select an item in the RAM mode dropdown after loading the
schematic: that UI writes mode `0` or `1` back over the hidden value `2`.
