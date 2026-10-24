
module mac (
    input  wire [3:0] a,
    input  wire [3:0] b,
    input  wire [7:0] acc,
    output wire [7:0] result
);
    wire [7:0] product;

    assign product = a * b;
    assign result  = acc + product;
endmodule
