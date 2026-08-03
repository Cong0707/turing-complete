module sumtransfer2(
  input  [1:0] a,
  input  [1:0] b,
  input        cin,
  output [1:0] sum,
  output       u,
  output       v
);
  wire [2:0] total = {1'b0, a} + {1'b0, b} + cin;
  wire [2:0] total0 = {1'b0, a} + {1'b0, b};
  wire [2:0] total1 = {1'b0, a} + {1'b0, b} + 1'b1;
  assign sum = total[1:0];
  assign u = total0[2];
  assign v = total1[2];
endmodule
