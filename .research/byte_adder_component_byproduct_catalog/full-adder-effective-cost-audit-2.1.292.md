# Full Adder 7/4 effective-cost audit (Turing Complete 2.1.292)

- Status: `pass`
- JSON SHA256: `e44e31485e7732ca54ad2ba17cdb4d6b8bfc36c124763e8b4820a541c26def12`
- Premise: the `full_adder` level is genuinely accepted and persisted at `7/4`.
- Result: `com_full_adder` becomes effective `7/4` locally and after restart.
- Parent scoring: gate totals and delay scheduling consume the selected runtime cost point; opaque FullAdder arcs therefore use `7/4`.
- Pareto: component tables support multiple nondominated points; here `7/4` strictly dominates the captured `16/8`, so the result is a single point.
- Network boundary: server-supplied frontiers are authoritative on import. Static evidence proves that import path, not the service's private acceptance implementation.
- Current authoritative `80/7`: unchanged because it contains no opaque FullAdder node.

## Eight-stage ripple example

- Shipped header/default `8/4`: `64/32`.
- Captured imported `16/8`: recomputed `128/64`.
- Genuinely accepted `7/4`: recomputed `56/32`.
