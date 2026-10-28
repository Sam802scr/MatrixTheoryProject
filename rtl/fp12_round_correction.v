// EAGER SR, Round Correction + second rounding stage (paper Fig. 4).
// The normalizer shifts in zeros; when it shifted left (j>=1) those zeros are replaced by the guard bits
// that sit just below the main adder (g = {G,G2}) -- this is the paper's "substitute the LSB with G".
// The carry of  {R,S} + {R1,R2} + (stage-1 carry)  is the round-up bit c.
//   j==0 (carry out)     : {R,S} as produced,            stage-1 carry = S1'
//   j==1 (1-bit shift)   : {R,G},                        stage-1 carry = S2'
//   j==2 (2-bit shift)   : {G,G2},                       stage-1 carry = S3   (far-path subtraction)
//   j>=3 (close path)    : exact result, low bits are 0 -> c = 0
module fp12_round_correction (
    input  wire [3:0] j,          // normalization shift (leading zeros of the P+2 bit sum)
    input  wire [1:0] norm_rs,    // {R,S} from the normalizer
    input  wire [1:0] g,          // {G,G2}: first two bits below the main adder
    input  wire [1:0] r12,        // R1,R2: the two random MSBs
    input  wire       s1, s2, s3,
    output wire       up
);
    reg [1:0] rs;
    reg       cin;
    always @* begin
        case (j)
            4'd0:    begin rs = norm_rs;               cin = s1; end
            4'd1:    begin rs = {norm_rs[1], g[1]};    cin = s2; end
            4'd2:    begin rs = {g[1], g[0]};          cin = s3; end
            default: begin rs = norm_rs;               cin = 1'b0; end
        endcase
    end
    wire [3:0] total = {2'b00, rs} + {2'b00, r12} + {3'b000, cin};
    assign up = total[2];
endmodule
