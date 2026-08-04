# 80/7 primitive-expansion byproduct truth catalog

- Status: `pass`
- Catalog SHA256: `3f877317e2b6ab0e2a418142e5a4bd47bb94f11100ec850bc5780a1d2e76b1c7`
- Physical truth classes: `155`
- Producers: `295`
- Packed masks: `166`

## Exact coverage

- 80/7 replay: `80/7`, `131072` rows, mismatch/conflict/Z = `0/0/0`.
- Current DAG nodes / Switch partial drivers: `82/10`.
- Direct score-improving truth-reuse hits: `0` (search disabled in this audit).
- Embedded minimal-expansion pattern hits: `20`.

## Exhaustive small minima

- `XOR`: lower counts `[0, 0]`, minimal raw/classes `4/2`.
- `XNOR`: lower counts `[0, 0]`, minimal raw/classes `4/2`.
- `AND3`: lower counts `[0]`, minimal raw/classes `3/3`.
- `OR3`: lower counts `[0]`, minimal raw/classes `3/3`.

## Dominance

- `XOR`: always versus runtime default; versus campaign native when any phase sideproduct is consumed
- `XNOR`: always in gate and delay under both evidence profiles
- `AND3/OR3`: always in campaign gate cost; versus runtime default when the pair intermediate or short-arc placement matters
- `FullAdder`: always in gate cost; campaign native is also delay dominated
- `Switch`: only when physical Z/driven ownership is provably irrelevant
- `word NOT/NAND/Switch`: score-neutral; exposes lane owners and byproducts but has no width discount

The JSON is the machine artifact. It retains every value/driven/conflict mask,
truth SHA, producer, owner set, gate/delay/owner Pareto point, input arc depth,
and embedded 80/7 hit. Replacement/optimization search is disabled.
