`include "bus_width.svh"

module component_a (
    input  logic [`TURINGSYNTH_BUS_WIDTH-1:0] left,
    input  logic [`TURINGSYNTH_BUS_WIDTH-1:0] right,
    output logic [`TURINGSYNTH_BUS_WIDTH-1:0] result
);
    always_comb begin
        result = left & right;
    end
endmodule
