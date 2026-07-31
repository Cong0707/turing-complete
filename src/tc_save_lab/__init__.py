"""Offline save laboratory for Turing Complete current-format circuits."""

from .codec import (
    FORMAT_VERSION,
    SUPPORTED_READ_VERSIONS,
    decode_circuit,
    decode_v15,
    encode_v15,
)
from .legacy_codec import decode_v7, decode_v13, decode_v14
from .analysis import analyze_circuit, analyze_examples, analyze_file, wire_points
from .pins import analyze_connectivity, positioned_pins, rotate_offset
from .builder import build_known_candidates, build_recipe, wire_from_vertices
from .model import Circuit, Component, Wire
from .simulate import SimulationError, simulate_combinational, verify_single_input_truth_table
from .exact_synthesis import (
    AIG_BASIS,
    NAND_BASIS,
    XAG_BASIS,
    ExactSynthesisResult,
    GateBasis,
    LogicNode,
    LogicNetwork,
    SearchLimitExceeded,
    SignalRef,
    input_truth_table,
    synthesize_exact,
    truth_table_mask,
    truth_table_from_callable,
)

__all__ = [
    "Circuit",
    "Component",
    "FORMAT_VERSION",
    "SUPPORTED_READ_VERSIONS",
    "Wire",
    "decode_circuit",
    "decode_v7",
    "decode_v13",
    "decode_v14",
    "decode_v15",
    "encode_v15",
    "analyze_circuit",
    "analyze_examples",
    "analyze_file",
    "wire_points",
    "analyze_connectivity",
    "positioned_pins",
    "rotate_offset",
    "build_known_candidates",
    "build_recipe",
    "wire_from_vertices",
    "SimulationError",
    "simulate_combinational",
    "verify_single_input_truth_table",
    "AIG_BASIS",
    "NAND_BASIS",
    "XAG_BASIS",
    "ExactSynthesisResult",
    "GateBasis",
    "LogicNode",
    "LogicNetwork",
    "SearchLimitExceeded",
    "SignalRef",
    "input_truth_table",
    "synthesize_exact",
    "truth_table_mask",
    "truth_table_from_callable",
]
