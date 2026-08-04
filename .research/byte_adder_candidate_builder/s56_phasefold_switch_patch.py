"""Hand-derived 93/6 S5/S6 phase-fold patch.

The S6 BUS is intentionally allowed to be Z only on rows whose correct S6
value is zero.  The campaign's fixed Maker8 output wrapper reads those scalar
Z lanes as zero and emits an active U8 word at zero gate/delay cost.
"""

PATCH_NAME = "s56-phasefold-shared-data-switch-g93-d6"


def build_s56(context):
    region = "s56-phasefold-switch"

    # S5 = P5 XOR C5. T5 is also the carry contribution reused by S6.
    t5 = context.gate("phasefold.T5", "AND", "P5", "C5", region=region)
    r5 = context.gate("phasefold.R5", "NOR", "P5", "C5", region=region)
    s5 = context.gate("S5", "NOR", t5, r5, region=region)

    # Let C6 = G5 | T5 and C7 = G6 | P6*C6. Then:
    #   NAND(P6,C7) & (G5 | P6 | T5) == P6 XOR C6 == S6.
    # The two Switches share the same data, so overlapping enables cannot
    # conflict. A true S6 always enables at least one driver.
    data = context.gate(
        "phasefold.S6_data", "NAND", "P6", "C7", region=region
    )
    early_enable = context.gate(
        "phasefold.S6_early_enable", "OR", "G5", "P6", region=region
    )
    s6 = context.bus(
        "S6_raw_zero_z",
        ((early_enable, data), (t5, data)),
        region=region,
    )
    return {"S5": s5, "S6": s6}
