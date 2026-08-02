# Public RNG Artifact Search Report

Date: 2026-08-02
Scope: read-only inspection of the Turing Complete challenge workspace and explicitly queried public-artifact services. No formal save, Steam Cloud state, or challenge circuit was written by this investigation.

## Result

No downloadable public RNG schematic matching the current leaderboard target (`431 gates / 9 delay / 66 ticks`) or improving the known local result (`396 / 10 / 66`, score `261360`) was found. The only directly relevant public Hub package that could be fetched is a generic 64-bit xoshiro256** implementation and is far above the target cost. Hub XOR7 data provides only a small XOR3 trade-off clue, not a candidate RNG.

## Local repository and history audit

Read-only path and full-history checks were run over:

- `.research/public_saves_cocca`
- `.research/public_saves_genius`
- `.research/public_saves_mizuchi`
- `.research/rng_public_search`
- `.research/gh0` through `.research/gh11`
- other checked-in Turing Complete clones under `.research` with a `.git` directory

For each repository, all historical paths were enumerated with `git log --all --name-only --pretty=format:` and filtered for `rng`, `random`, and `random number`. No RNG level/save directory was present in current or historical paths. The only matching paths were unrelated ABC SAT headers (`random.h`/`random.hpp`).

## Sourcegraph checks

Sourcegraph SSE endpoint: `https://sourcegraph.com/.api/search/stream` (API version `V3`). Each query was run independently with a 30-second request limit and repository scope restricted to names matching `github.com/.*[Tt]uring.*[Cc]omplete.*`.

| Query | Result |
| --- | --- |
| `context:global type:path file:(^|/)rng(/|$) repo:github.com/.*[Tt]uring.*[Cc]omplete.* count:200` | `matchCount: 0` |
| `context:global type:path file:rng\\.tc$ repo:github.com/.*[Tt]uring.*[Cc]omplete.* count:200` | `matchCount: 0` |
| `context:global type:path file:circuit\\.data$ repo:github.com/.*[Tt]uring.*[Cc]omplete.* count:200` | `matchCount: 0` |

The earlier broad global path query was stopped after it became too wide; it produced no Turing Complete save hit before termination. No broad query is treated as evidence of absence.

## GitHub account checks

GitHub API repository listing was checked for `fermienergy` and `patchouli`. `patchouli` currently exposes only:

- `FAPM`
- `Locale-Emulator` (fork; discontinued)
- `shadowsocks-windows` (fork)

None is a Turing Complete save or RNG schematic repository. Repository searches for `FermiEnergy`, `Patchouli Turing Complete`, `"Turing Complete" RNG`, and `"Random Number Generator" "Turing Complete"` returned no relevant public repository. `grep.app` was unavailable during this run (HTTP 429).

## Schematic Hub evidence

Relevant Hub metadata entries:

- ID `53`, `XOR7/XOR7`, author FermiEnergy. Main schematic is `1190 gates / 3 delay`; its XOR3 dependency is `12 gates / 2 delay`. A two-XOR2 XOR3 reference is `6 gates / 4 delay`, so the package is a structural trade-off clue only and cannot be the `431`-gate RNG.
- ID `150`, `Random Number Generator`, author skyoxZ, xoshiro256**. Extracted into `hub-150-xoshiro256` using `fetch_hub_item.py` (read-only, refuses to overwrite an existing output directory). Analysis: `38 components`, `76 wires`, declared `55427 gates / 3221 delay`; generic 64-bit implementation, not reusable at leaderboard cost.
- ID `156`, `SRNG`, author alex. Analysis: `2200 gates / 518 delay`; unrelated to the target.

Hub 150 evidence hashes:

```text
response.bin       4a99113628734a3bb6a990e542ed25976886a356e33b8a190a5f9765390a9688
package payload    9c79324e51508f345f6958336522926d90ab3054d87f8b31aef2bb08b0735faf
main/circuit.data  2d5d4632b6506b8a844c913b0b0095939e3535c44194314a34bcf5fbbb3776eb
```

## Wiki and web search

The only historical RNG score artifact found was the Alpha-branch page:
`https://turingcomplete.wiki/wiki/Alpha_Branch/High_scores`

It records `72 gates / 6 delay / 64 ticks = 27648` for Random Number Generator. The score first appears in revision `9650` (`2026-01-28T14:22:37Z`, anonymous editor `114.86.18.47`) along with many unrelated level scores. No circuit, attachment, or link is included. Alpha-branch component/cost semantics differ from the current stable game and the result is not directly migratable.

Exact DuckDuckGo searches performed (no save/topology result):

```text
"Patchouli" "Turing Complete"
"FermiEnergy" "Turing Complete"
"Patchouli" "Random Number Generator"
"FermiEnergy" "Random Number Generator"
site:github.com "Turing Complete" rng save
site:github.com TuringComplete rng circuit.data
site:github.com "Turing-Complete-Saves" rng
"431" "9" "66" "Turing Complete"
site:steamcommunity.com "Random Number Generator" "Turing Complete"
site:steamcommunity.com Patchouli "Turing Complete"
site:reddit.com/r/TuringComplete RNG
"红魔馆大图书馆大学"
"复旦大学-集成电路与微纳电子创新学院"
```

## Reproduction and state boundary

The extracted files are confined to `.research/rng_public_artifacts/hub-150-xoshiro256`. The script used for extraction is `.research/rng_public_artifacts/fetch_hub_item.py`; its authentication token is held in memory only and output directories are never overwritten. Formal candidate saves and all existing working-tree modifications belong to other ongoing work and were not changed here.
