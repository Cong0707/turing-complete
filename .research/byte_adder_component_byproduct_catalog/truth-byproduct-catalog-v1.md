# 80/7 primitive-expansion byproduct truth catalog

- Status: `pass`
- Catalog SHA256: `387fae011a0acc49db710704132d07f7acc74f9cb415a3919ee1cedcc7d4f9a6`
- Physical truth classes: `155`
- Producers: `295`
- Packed masks: `166`

## Exact coverage

- 80/7 replay: `80/7`, `131072` rows, mismatch/conflict/Z = `0/0/0`.
- Current DAG nodes / Switch partial drivers: `82/10`.
- Direct score-improving truth-reuse hits: `0`.
- Embedded minimal-expansion pattern hits: `22`.

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
embedded 80/7 hit, and full-domain direct-reuse replay.
