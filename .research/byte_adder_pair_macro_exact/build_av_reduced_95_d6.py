"""Build a 95/6 mixed Q-phase/A-V Byte Adder.

The starting point is the independently replayed 105/6 reduced A/V witness.
Two local carry nodes that exist only for their following Sum are eliminated:

* ``C4 + S4`` (7 gates) was first replaced by a five-gate formula that reuses
  the already-paid fast ``C5@4`` boundary.  Joint exact synthesis then shares
  the ordinary ``P3&C3`` phase with S3, reducing the combined S3/S4 region
  from eight gates to seven:

  ``T3=P3&C3``

  ``S3=NOR(NOR(P3,C3),T3)``

  ``S4=NOR(P4&C5, NOR(T3,G3|P4))``;

* the private ``AV345 + C6 + S6`` branch (12 gates) was first replaced by a
  nine-gate ``C5 -> S6`` network.  A second exact search then found a
  seven-gate resolved-phase formula using the already-paid fast ``C7@4``:

  ``N=NOR(Q5,P6)``

  ``S6=BUS((C5,N),(G5,N)) OR NOR(Q6,C7)``.

The bit-0 reduced-state fusion remains:

    C1 = V0 & (G0 | Cin)

so Q0/P0 need not be materialized merely to append ``P0 xor Cin``.  For a
valid one-bit reduced state ``G <= V`` and the adjacent carries ``C,C'``:

    S = (V | C) & NAND(C', NAND(G, C))

This research variant additionally replaces the fast bit-3:4 A/V pair by a
cheaper Q-phase front while retaining the C5@4 and C7@4 boundaries::

    A34 = G3 | G4
    N34 = NOR(Q3, Q4)
    V34 = G4 | N34
    C5  = BUS(SW(A34, V34), SW(C3, V34))

    A36 = A34 | A56
    V36 = BUS(SW(N34, V56), SW(G4, V56), SW(A56, V56))
    C7  = BUS(SW(A36, V36), SW(C3, V36))

The original 97/6 middle residual costs 20 gates.  This strict three-state
replacement costs 7 + 11 = 18 gates, for a complete 95-gate, six-step DAG.
Every BUS owns its complete driver set; the resolved V36 net is reused only as
data and is never flattened into a partially shared physical BUS.  No native
adder or mux component is used.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORE_PATH = ROOT / ".research/byte_adder_interval_dp_agent/interval_dp.py"
OUTPUT_PATH = HERE / "byte-adder-av-reduced-g95-d6.json"


def load_core():
    spec = importlib.util.spec_from_file_location("av_reduced105_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(CORE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = load_core()


def av_switch_combine(factory, low, high):
    low_a, low_v = low
    high_a, high_v = high
    any_generate = factory.gate("OR", low_a, high_a)
    valency = factory.bus(((high_a, high_v), (low_v, high_v)))
    return any_generate, valency


def av_switch_gray(factory, carry, transfer):
    any_generate, valency = transfer
    return factory.bus(((any_generate, valency), (carry, valency)))


def reduced_sum(factory, generate, valency, carry_in, carry_out):
    active = factory.gate("OR", valency, carry_in)
    not_both_generate = factory.gate("NAND", generate, carry_in)
    selected_phase = factory.gate("NAND", carry_out, not_both_generate)
    return factory.gate("AND", active, selected_phase)


def shared_s3_s4(factory, p3, p4, g3, c3, c5):
    """Seven ordinary gates; exact joint paid-source S3/S4@6 witness."""

    p3_and_c3 = factory.gate("AND", p3, c3)
    s3 = factory.gate("NOR", factory.gate("NOR", p3, c3), p3_and_c3)
    p4_and_c5 = factory.gate("AND", p4, c5)
    selector = factory.gate("OR", g3, p4)
    residual = factory.gate("NOR", p3_and_c3, selector)
    s4 = factory.gate("NOR", p4_and_c5, residual)
    return s3, s4


def paid_s6_d6(factory, c5, g5, q5, p6, q6, c7):
    """Seven gates; exact paid-source resolved-phase witness for S6@6."""

    selected_phase = factory.gate("NOR", q5, p6)
    lower_active = factory.bus(((c5, selected_phase), (g5, selected_phase)))
    upper_phase = factory.gate("NOR", q6, c7)
    return factory.gate("OR", lower_active, upper_phase)


def serialize(factory, outputs):
    live = sorted(factory.reachable(outputs))
    rows = []
    for index in live:
        node = factory.nodes[index]
        row = {
            "id": index,
            "op": node.op,
            "args": list(node.args),
            "cost": node.cost,
            "step_delay": node.step_delay,
            "arrival": node.arrival,
            "may_z": node.may_z,
            "label": node.label,
        }
        if node.op == "BUS":
            row["resolved_network"] = f"bus_{index}"
            row["drivers"] = [
                {
                    "enable": node.args[offset],
                    "data": node.args[offset + 1],
                    "owner": f"bus_{index}",
                }
                for offset in range(0, len(node.args), 2)
            ]
        rows.append(row)
    payload = {"outputs": list(outputs), "nodes": rows, "live_node_count": len(live)}
    payload["sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def build() -> dict[str, object]:
    factory = core.Factory()
    g = []
    p = [None] * 8
    v = [None] * 8
    for bit in range(8):
        a = factory.inputs[f"a{bit}"]
        b = factory.inputs[f"b{bit}"]
        g.append(factory.gate("AND", a, b))
        if bit != 0:
            q = factory.gate("NOR", a, b)
            p[bit] = factory.gate("NOR", g[bit], q)
        if bit <= 6:
            v[bit] = factory.gate("OR", a, b)

    c0 = factory.inputs["cin"]
    c1 = av_switch_gray(factory, c0, (g[0], v[0]))

    # Local ordinary bit 1; its P&C term is reused by S1.
    t1 = factory.gate("AND", p[1], c1)
    c2 = factory.gate("OR", g[1], t1)

    av12 = av_switch_combine(factory, (g[1], v[1]), (g[2], v[2]))
    c3 = av_switch_gray(factory, c1, av12)

    # Cheap Q-phase [3:4] front.  q3/q4 structurally intern with the leaves
    # already used to form p3/p4, while the now-dead v3/v4 leaves disappear
    # from the reachable DAG.
    q3 = factory.gate("NOR", factory.inputs["a3"], factory.inputs["b3"])
    q4 = factory.gate("NOR", factory.inputs["a4"], factory.inputs["b4"])
    a34 = factory.gate("OR", g[3], g[4])
    n34 = factory.gate("NOR", q3, q4)
    v34 = factory.gate("OR", g[4], n34)
    c5 = factory.bus(((a34, v34), (c3, v34)))

    # The [3:5] C6 branch is deliberately absent.  AV56 remains because it is
    # an input of the fast [3:6] C7 prefix; its A output is shared with S6.
    av56 = av_switch_combine(factory, (g[5], v[5]), (g[6], v[6]))
    a56, v56 = av56

    # Exact strict-three-state C7 backend.  Expanding V34=G4|N34 into two
    # independent enables removes the old V3/V4 leaves without delaying C7.
    a36 = factory.gate("OR", a34, a56)
    v36 = factory.bus(((n34, v56), (g[4], v56), (a56, v56)))
    c7 = factory.bus(((a36, v36), (c3, v36)))

    t7 = factory.gate("AND", p[7], c7)
    c8 = factory.gate("OR", g[7], t7)

    s0 = reduced_sum(factory, g[0], v[0], c0, c1)
    s1 = factory.gate("NOR", t1, factory.gate("NOR", p[1], c1))
    t2 = factory.gate("AND", p[2], c2)
    s2 = factory.gate("NOR", t2, factory.gate("NOR", p[2], c2))
    s3, s4 = shared_s3_s4(factory, p[3], p[4], g[3], c3, c5)
    t5 = factory.gate("AND", p[5], c5)
    s5 = factory.gate("NOR", t5, factory.gate("NOR", p[5], c5))
    s6 = paid_s6_d6(
        factory,
        c5,
        g[5],
        factory.gate("NOR", factory.inputs["a5"], factory.inputs["b5"]),
        p[6],
        factory.gate("NOR", factory.inputs["a6"], factory.inputs["b6"]),
        c7,
    )
    s7 = factory.gate("NOR", t7, factory.gate("NOR", p[7], c7))
    sums = [s0, s1, s2, s3, s4, s5, s6, s7]

    outputs = tuple([*sums, c8])
    metrics = factory.structural_metrics(outputs)
    _packed, semantic = factory.evaluate(outputs)
    deadlines = {
        "C5": factory.nodes[c5].arrival,
        "C7": factory.nodes[c7].arrival,
        **{
            f"S{bit}": factory.nodes[sums[bit]].arrival
            for bit in range(3, 8)
        },
    }
    if metrics["gate"] != 95 or metrics["delay"] != 6:
        raise RuntimeError(f"unexpected metrics: {metrics}")
    if deadlines["C5"] > 4 or deadlines["C7"] > 4:
        raise RuntimeError(f"carry deadline regression: {deadlines}")
    if any(deadlines[f"S{bit}"] > 6 for bit in range(3, 8)):
        raise RuntimeError(f"sum deadline regression: {deadlines}")
    if semantic["mismatch_union_count"]:
        raise RuntimeError(f"truth mismatch: {semantic}")
    if semantic["conflict_assignment_count"]:
        raise RuntimeError(f"BUS conflict: {semantic}")
    if any(semantic["z_assignment_count_by_output"]):
        raise RuntimeError(f"undriven output: {semantic}")

    live = factory.reachable(outputs)
    bus_nodes = [index for index in live if factory.nodes[index].op == "BUS"]
    return {
        "schema": "byte-adder-mixed-q34-av56-shared-s3-s4-s6-dag-v1",
        "status": "sat",
        "family": "97/6 reduced A/V with strict Q34 front and expanded resolved V36",
        "schedule": {
            "carry_edges": [
                "C1<-C0:AV/switch[0]",
                "C2<-C1:GP/ordinary[1]",
                "C3<-C1:AV/switch[1:2]",
                "C5<-C3:mixed-Q/AV-switch[3:4]",
                "C7<-C3:mixed-Q/AV-switch[3:6]",
                "C8<-C7:GP/ordinary[7]",
            ],
            "av_combine": "A=Ah|Al; V=Vh&(Ah|Vl)",
            "bit0_sum": "(V0|C0)&NAND(C1,NAND(G0,C0))",
            "bit3_bit4_sums": "seven-gate joint paid-source formula; C4 removed and P3&C3 shared",
            "bit6_sum": "seven-gate paid-source C7-aware resolved formula; AV345/C6 removed",
            "q34_front": "A34=G3|G4; N34=NOR(Q3,Q4); V34=G4|N34; C5=V34&(A34|C3)",
            "expanded_v36": "V36=BUS((N34,V56),(G4,V56),(A56,V56)); C7=V36&(A34|A56|C3)",
            "deadlines": deadlines,
        },
        "metrics": metrics,
        "semantic": semantic,
        "physical": {
            "bus_nodes": len(bus_nodes),
            "bus_node_ids": bus_nodes,
            "partial_driver_reuse_possible": False,
            "reason": "each BUS owns its complete same-data driver set; V36 is reused only as data",
        },
        "test_domain": {
            "variables": core.VARIABLES,
            "rows": core.ASSIGNMENTS,
            "complete_u8_u8_u1": True,
        },
        "factory_dag": serialize(factory, outputs),
    }


def main() -> int:
    payload = build()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT_PATH.write_bytes(encoded.encode("utf-8"))
    print(
        json.dumps(
            {
                "output": str(OUTPUT_PATH),
                "metrics": payload["metrics"],
                "semantic": payload["semantic"],
                "sha256": hashlib.sha256(encoded.encode()).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
