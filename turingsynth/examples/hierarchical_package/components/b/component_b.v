`include "bus_width.svh"

module component_b (
    input  wire [`TURINGSYNTH_BUS_WIDTH-1:0] value,
    output wire [`TURINGSYNTH_BUS_WIDTH-1:0] result
);
    assign result = ~value;
endmodule
