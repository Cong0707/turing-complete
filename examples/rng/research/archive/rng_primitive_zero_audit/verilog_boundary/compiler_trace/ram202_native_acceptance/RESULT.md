# Native acceptance audit for the 202/6/66 RAM RNG

## Verdict

**Rejected for deployment.** In the current native runtime, `kind=118` is a
pinless backing-memory object. It does not own aggregate `load`, `save`,
`address`, `in`, or `out` wire ports after v15 deserialization or board
construction.

A usable RAM access path requires separate serialized components:

- `kind=54`: RAM load port (`enable`, `address`, `out`)
- `kind=56`: RAM store port (`enable`, `address`, `data`)
- `kind=118`: backing RAM, found spatially by the port components

Therefore `src/tc_save_lab/rng_ram_asic.py` cannot realize `202/6/66` as
written. The existing `304/6/66` RAM2 representation, with one each of kinds
54, 56, and 118, has the correct native component boundary.

## Decisive evidence

### 1. The native kind-118 prototype has zero pins

The prototype table dumped from the installed executable has these three pin
sequence lengths:

```text
kind 54: group@96=3, group@112=0, group@128=2
kind 56: group@96=5, group@112=0, group@128=1
kind118: group@96=0, group@112=0, group@128=0
```

The dump is in
`.research/rng_primitive_zero_audit/native_prototypes.json`. It comes from:

```text
D:\Game\Steam\steamapps\common\Turing Complete\Turing Complete.exe
SHA-256 c93f5e8e826050c3f92e2b3891d26fcdfc933658614185cb9b2eb6a34c5b8d1c
prototype table VA 0x1409a7b00
```

The extra entries in the 54/56 sequences include prototype placeholders, but
that does not affect the decisive fact: all three sequences for kind 118 are
empty.

These are not guessed offsets in the dump. `board_add_component.c:365-404`
copies `PROTOTYPES[kind]` into its local prototype object. Its fields at
offsets 96, 112, and 128 are the decompiler variables `v111`, `v112`, and
`v113`; `:672-744` allocates one runtime pin group from `v111 + v112`, and
`:745-809` allocates the other from `v113`. All three being zero therefore
means a kind-118 board component receives no runtime pins.

### 2. v15 loading does not expand kind 118 into port components

`load_schematic_raw.c:274` iterates exactly over the serialized component
sequence, and `load_schematic_raw.c:661` invokes `board_add_component` once for
that current record. There is no second call that inserts RAM ports.

`board_add_component.c` contains special branches for kinds 78, 82, 83, 91,
and 101 (`:231`, `:504`, `:522`), but none for kind 118. The ordinary branch
constructs and appends one board component. Thus a v15 payload containing only
one kind 118 still contains only that pinless RAM object after board loading.

### 3. The compiler starts RAM association from kinds 54/56

`connect_to_ram.c` shows the native direction of association:

- `:155`: only kinds 54 and 56 enter the RAM-port path;
- `:203` and `:229`: separate load/store handling;
- `:349`: each port calls `get_component_at_offset`;
- `:366`: the object found at that offset must be kind 118.

In other words, kind 54/56 searches for and binds to kind 118. Kind 118 does
not synthesize access nodes and does not dispatch load/store code on its own.
The later code generator branches for memory reads and writes are likewise the
kind-54 and kind-56 branches, respectively.

### 4. Real v15 saves serialize the ports independently

The current RV64 v15 sample contains:

```text
kind118 x4
kind 54 x5
kind 56 x3
```

For all eight connected 54/56 components, the decoded wire endpoints land on
their native `enable/address/out` or `enable/address/data` coordinates. Kind
118 has no native endpoint coordinates. The exact per-component positions and
endpoint hit counts are recorded in `evidence.json`.

The live v15 Foundry sample at
`C:\Users\cong\AppData\Roaming\Turing Complete\schematics\foundry\RISCV\MEMORYREGFILE\circuit.data`
is even narrower:

```text
RAM   kind118 at (27,16)
Load  kind 54 at (27, 4) and (27, 2)
Store kind 56 at (27, 6)
```

Every external pin of all three access components has a decoded wire endpoint.
The RAM itself again has none. Its SHA-256 is
`aeca711c1f07082a1d74b016c2c902e7c7cab3341b4460c7bcb5552488fd2b0c`.

The reviewed RAM2 candidate similarly serializes `118 x1`, `54 x1`, `56 x1`,
and all six external port pins have a wire endpoint. This is consistent with
both the real save and compiler evidence.

The binding is spatial, not a serialized `linked_components` relation. The
board loader stores serialized links separately, while preorder clears and
rebuilds a dedicated top-port component-index list by scanning above each kind
118 (`preorder.c:2235-2322`). Therefore empty `linked_components` on the RAM2
triple is expected. Its deltas, Load `-12` and Store `-10` on Y, exactly match
the live Foundry sample.

## Why the local 202 verifier gives a false positive

`src/tc_save_lab/pins.py:147-162` locally invents five aggregate pins for kind
118. Those pins contradict the native prototype table. The 202 builder then
wires directly to the invented pins at
`src/tc_save_lab/rng_ram_asic.py:232-235,252`, while its expected component
counts include kind 118 but no kind 54 or 56 (`:418-430`).

Its functional check is also not a native RAM execution test:
`_ram_delay_surrogate` replaces kind 118 with a kind-55 U32 Delay, rewrites the
invented aggregate wires, and the Python simulator executes that surrogate.
This proves the recurrence assuming an abstract one-cycle state element; it
does not prove that the saved native graph contains a RAM read or write port.

With the real prototype table, the five aggregate wire endpoints have no
component pins to attach to. The recurrence therefore has no native RAM load
or store operation. The exact UI/compiler error code is intentionally not
claimed because this audit did not start the game, but the topology is already
disproved before code generation.

## Reproduction

From the repository root:

```powershell
$env:PYTHONPATH='src'
python .research\rng_primitive_zero_audit\verilog_boundary\compiler_trace\ram202_native_acceptance\audit_native_ram_ports.py
```

Expected final line:

```json
{"kind_118_has_aggregate_wire_ports": false, "kind_54_load_component_required": true, "kind_56_store_component_required": true, "ram202_candidate_native_compile_ready": false}
```

The script is read-only except for regenerating `evidence.json` in this audit
directory. It does not start the game and does not read or modify the formal
RNG save. It reads the related live Foundry `MEMORYREGFILE` sample only as an
additional v15 fixture.
