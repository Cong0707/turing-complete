# Completed x60 Pair-Cover Audit

## Outcome

The five searches reported as truncated in
`basis_radius4_x60_altcovers.json` were produced by a 100,000-state cap.  All
five finish below 250,000 states.  Completion adds no covers, and a full
radius-four replay still returns `no_dual_candidate`.

This audit only covers the offline, `init_data=0`, single-Architecture-Output
dual-mode model in `search_basis_dualmode.py`.  It did not start or control the
game and did not read or write the live save.

## Exact Five Instances

| Case | Row shears from fixed T | Full states | Covers | New after 100k |
| --- | --- | ---: | ---: | ---: |
| 1 | `(17,22) (18,23) (22,27) (23,28)` | 188413 | 72 | 0 |
| 2 | `(17,22) (18,23) (23,28)` | 188170 | 9 | 0 |
| 3 | `(17,22) (18,23) (22,27)` | 177596 | 9 | 0 |
| 4 | `(17,22) (18,23) (19,24) (24,29)` | 107497 | 9 | 0 |
| 5 | `(17,22) (18,23) (18,31) (23,28)` | 100469 | 3 | 0 |

The five full searches visit 762145 states versus 500000 at the old cap.  The
difference is 262145, exactly matching the global change from 4414021 to
4676166 states.  Both capped and complete runs return the same 102 covers for
these instances.

Every B-row decomposition was exhausted: 141 assignments in total.  No
assignment reaches a beam search:

- 138 fail because a unit steady-state `B` row would have to carry a
  non-unit `T(seed)` tick-zero label.
- 3 fail because an exact two-input pair would have to carry a `T(seed)`
  label of weight greater than two.

These failures are structural for the modeled XOR DAG and do not depend on
`component_limit` or `global_beam`.  Therefore the completed five instances
contain no candidate satisfying `3*XOR + OR <= 221`.

## Full Replay

The completed full search reports:

```text
basis_count                         4481
decomposition_variants_evaluated    571
enumerated_pair_cover_states     4676166
enumerated_pair_cover_count          493
truncated_pair_cover_searches           0
dual_feasible_basis_count                0
status                  no_dual_candidate
```

## Reproduction

Run from the repository root:

```powershell
python .research/rng_cost387/agent_finish_x60/complete_five.py `
  --output .research/rng_cost387/agent_finish_x60/five_completed.json

python .research/rng_cost387/agent_finish_x60/diagnose_labels.py `
  --input .research/rng_cost387/agent_finish_x60/five_completed.json `
  --component-limit 512 --global-beam 4096 `
  --output .research/rng_cost387/agent_finish_x60/label_failures_512_4096.json

python .research/rng_cost387/search_basis_dualmode.py `
  --radius 4 --max-xor 60 --enumerate-cover-xor 60 `
  --cover-state-limit 250000 --cover-solution-limit 10000 `
  --component-limit 512 --global-beam 4096 `
  --decomposition-samples 256 --seed 0x387 `
  --output .research/rng_cost387/agent_finish_x60/basis_radius4_x60_complete.json
```

## Evidence Hashes

```text
Input search_basis_dualmode.py
1A80E2E0B20698E827619C6F6214A27B9250330769F9A22466A5716916FE59F3

Input basis_radius4_x60_altcovers.json
90A4AA98A87409AD0E2D37B2EB283DA69A7EDB78F6BAB1FB2A3D4CA2E2318E55

truncated_100k.json
DAA387291D03063ED77380596AD4A495CF0CAB20B98F99A848A0D5FDF4D5275B

five_completed.json
911B363743663348E443D5BA213E1D5777CCB84E7246D377F46FD7F43DA6EAC4

label_failures_512_4096.json
41E4FBE143E41EDB113C1F488F3389CE14395397BB5643476F9EF11A91C6CC1E

basis_radius4_x60_complete.json
D3DD80DD1CF44DA7FC78DC2A7433768EB45ED32EE386E0379CB7EB07BCF61496
```
