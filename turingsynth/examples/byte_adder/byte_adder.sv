module byte_adder(
    input  logic [7:0] A,
    input  logic [7:0] B,
    input  logic       Carry_in,
    output logic [7:0] Output,
    output logic       Carry_out
);
    assign {Carry_out, Output} = A + B + Carry_in;
endmodule
