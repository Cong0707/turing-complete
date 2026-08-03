module byte_adder(
    input  [7:0] a,
    input  [7:0] b,
    input        cin,
    output [7:0] sum,
    output       cout
);
    assign {cout, sum} = {1'b0, a} + {1'b0, b} + cin;
endmodule

