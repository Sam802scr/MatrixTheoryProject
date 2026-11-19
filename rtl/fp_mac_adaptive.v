// MAC: FP8 E5M2 x FP8 E5M2 (exact) -> FP12 E6M5 accumulator register,
// with Adaptive Stochastic Rounding (ASR) support.
// MODE:
//   0: Round-to-Nearest-Even (RN baseline)
//   1: Fixed 18-bit SR (paper baseline)
//   2: Adaptive SR with dynamic precision r in {4, 7, 9, 11, 13}
module fp_mac_adaptive #(
    parameter MODE  = 2,
    parameter STEPS = 18,
    parameter [17:0] SEED = 18'd1,
    parameter [17:0] MASK = 18'h20400
)(
    input  wire        clk,
    input  wire        rst,      // clears accumulator and reloads LFSR seed
    input  wire        en,
    input  wire [2:0]  r_sel,    // precision select for Adaptive SR (0:4, 1:7, 2:9, 3:11, 4:13)
    input  wire [7:0]  a,
    input  wire [7:0]  b,
    output reg  [11:0] acc
);
    wire [11:0]  prod;
    wire [17:0]  rnd, lfsr_state;
    wire [11:0]  s_rn, s_fixed, s_adapt, sum;

    fp8_multiplier u_mul (.a(a), .b(b), .p(prod));
    lfsr_galois #(.W(18), .MASK(MASK), .SEED(SEED), .STEPS(STEPS))
        u_lfsr (.clk(clk), .rst(rst), .en(en), .next_word(rnd), .state(lfsr_state));

    fp12_add                     u_rn    (.a(acc), .b(prod), .result(s_rn));
    fp12_add_sr_eager #(.R(18))  u_fixed (.a(acc), .b(prod), .random_bits(rnd), .result(s_fixed));
    fp12_add_sr_adaptive         u_adapt (.a(acc), .b(prod), .random_bits(rnd[12:0]), .r_sel(r_sel), .result(s_adapt));

    assign sum = (MODE == 0) ? s_rn : (MODE == 1) ? s_fixed : s_adapt;

    always @(posedge clk) begin
        if (rst)     acc <= 12'd0;
        else if (en) acc <= sum;
    end
endmodule
