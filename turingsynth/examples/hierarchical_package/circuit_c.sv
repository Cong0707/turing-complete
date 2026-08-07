`include "bus_width.svh"

module circuit_c #(
    parameter integer WIDTH = `TURINGSYNTH_BUS_WIDTH
) (
    input  logic [WIDTH-1:0] A,
    input  logic [WIDTH-1:0] B,
    input  logic [WIDTH-1:0] Mask,
    output logic [WIDTH-1:0] Output
);
    logic [WIDTH-1:0] combined;
    logic [WIDTH-1:0] inverted;

    component_a u_a (
        .left(A),
        .right(B),
        .result(combined)
    );

    component_b u_b (
        .value(combined),
        .result(inverted)
    );

`ifdef TURINGSYNTH_HIERARCHICAL_EXAMPLE
    assign Output = inverted ^ Mask;
`else
    assign Output = inverted;
`endif
endmodule
