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
]
