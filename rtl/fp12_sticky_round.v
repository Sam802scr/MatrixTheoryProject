// EAGER SR, first rounding stage ("Sticky Round", paper Fig. 3b).
// Adds the (R-2) random LSBs to the (R-2) low bits of the aligned, 2's-complemented smaller operand.
// Only the carries are kept: s1 = carry-out, s2 = carry into the MSB, s3 = carry into bit R-4.
// (s1 is the paper's S1', s2 its S2'.  s3 is needed only for far-path SUBTRACTION, where the result can be
//  normalized by 2 positions; the paper analyses addition only.)  In hardware all three come from ONE carry chain.
module fp12_sticky_round #(parameter R = 18) (
    input  wire [R-3:0] y_low,
    input  wire [R-3:0] rand_low,
    output wire         s1,
    output wire         s2,
    output wire         s3
);
    wire [R-2:0] full = {1'b0, y_low}          + {1'b0, rand_low};
    wire [R-3:0] lo3  = {1'b0, y_low[R-4:0]}   + {1'b0, rand_low[R-4:0]};
    wire [R-4:0] lo4  = {1'b0, y_low[R-5:0]}   + {1'b0, rand_low[R-5:0]};
    assign s1 = full[R-2];
    assign s2 = lo3[R-3];
    assign s3 = lo4[R-4];
endmodule
