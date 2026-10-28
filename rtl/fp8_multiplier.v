// FP8 E5M2 x FP8 E5M2 -> FP12 E6M5, EXACT (no rounding) -- paper Sec. III-a
// Policy (mirrors reference_model/sr_mac_ref.py): subnormal inputs = 0, exp==31 -> special (FP12 exp 63).
module fp8_multiplier (
    input  wire [7:0]  a,
    input  wire [7:0]  b,
    output reg  [11:0] p
);
    reg        s;
    reg [4:0]  ea, eb;
    reg [2:0]  ma, mb;
    reg [5:0]  prod;           // 3b x 3b
    reg [5:0]  sig;
    reg [5:0]  e_out;

    always @* begin
        s  = a[7] ^ b[7];
        ea = a[6:2];
        eb = b[6:2];
        ma = {1'b1, a[1:0]};
        mb = {1'b1, b[1:0]};
        prod = ma * mb;                           // 16..49
        sig  = prod[5] ? prod : {prod[4:0], 1'b0}; // normalize to 6 bits
        e_out = ea + eb + 6'd1 + prod[5];          // biased E6M5 exponent, 3..62 for normal inputs
        if (ea == 5'd31 || eb == 5'd31)
            p = {s, 6'd63, 5'd0};
        else if (ea == 5'd0 || eb == 5'd0)
            p = 12'd0;
        else
            p = {s, e_out, sig[4:0]};
    end
endmodule
