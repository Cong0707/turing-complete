"""Generate the deterministic SHA-256 inventory for the 23-kind audit."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
OUTPUT = HERE / "byte_adder_23kind_dynamic_SHA256SUMS.txt"

REPORT = "2026-08-04-\u5b57\u8282\u52a0\u6cd5\u566823-kind\u987a\u5e8f\u57df\u52a8\u6001\u526f\u4ea7\u7269\u5ba1\u8ba1.md"

FILES: tuple[tuple[str, Path], ...] = (
    ("audit_23kind_dynamic_byproducts.py", HERE / "audit_23kind_dynamic_byproducts.py"),
    (
        "byte_adder_23kind_dynamic_byproduct_audit.json",
        HERE / "byte_adder_23kind_dynamic_byproduct_audit.json",
    ),
    (REPORT, HERE / REPORT),
    (
        "audit_byte_adder_delayline_sequence.py",
        HERE / "audit_byte_adder_delayline_sequence.py",
    ),
    (
        "byte_adder_delayline_sequence_audit.json",
        HERE / "byte_adder_delayline_sequence_audit.json",
    ),
    (
        "audit_delayline_autonomous_phases.py",
        HERE / "audit_delayline_autonomous_phases.py",
    ),
    (
        "delayline_autonomous_phase_audit.json",
        HERE / "delayline_autonomous_phase_audit.json",
    ),
    ("synthesize_warmup_residuals.py", HERE / "synthesize_warmup_residuals.py"),
    (
        "warmup_residual_intake/summary.json",
        HERE / "warmup_residual_intake" / "summary.json",
    ),
    ("audit_warmup_phase_pareto.py", HERE / "audit_warmup_phase_pareto.py"),
    (
        "warmup_phase_residual_pareto_audit.json",
        HERE / "warmup_phase_residual_pareto_audit.json",
    ),
    (
        "warmup_residual_intake/all9/espresso.stderr.log",
        HERE / "warmup_residual_intake" / "all9" / "espresso.stderr.log",
    ),
    (
        "warmup_residual_intake/all9/espresso_so.pla",
        HERE / "warmup_residual_intake" / "all9" / "espresso_so.pla",
    ),
    (
        "../byte_adder_component_byproduct_catalog/component-catalog-v1.json",
        RESEARCH / "byte_adder_component_byproduct_catalog" / "component-catalog-v1.json",
    ),
    (
        "../byte_adder_component_byproduct_catalog/truth-byproduct-catalog-v1.json",
        RESEARCH / "byte_adder_component_byproduct_catalog" / "truth-byproduct-catalog-v1.json",
    ),
    (
        "../byte_adder_root/byte-adder-hybrid-phasefold-g80-d7.json",
        RESEARCH / "byte_adder_root" / "byte-adder-hybrid-phasefold-g80-d7.json",
    ),
    (
        "D:/Game/Steam/steamapps/common/Turing Complete/campaign/byte_adder/test.si",
        Path(
            r"D:\Game\Steam\steamapps\common\Turing Complete"
            r"\campaign\byte_adder\test.si"
        ),
    ),
    (
        "generate_byte_adder_23kind_dynamic_sha256s.py",
        HERE / "generate_byte_adder_23kind_dynamic_sha256s.py",
    ),
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    labels = [label for label, _ in FILES]
    if len(labels) != len(set(labels)):
        raise RuntimeError("duplicate SHA-256 inventory label")

    missing = [str(path) for _, path in FILES if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing inventory inputs:\n" + "\n".join(missing))

    lines = [f"{digest(path)}  {label}" for label, path in FILES]
    OUTPUT.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    print(f"wrote {OUTPUT} ({len(lines)} entries, LF, UTF-8)")


if __name__ == "__main__":
    main()
