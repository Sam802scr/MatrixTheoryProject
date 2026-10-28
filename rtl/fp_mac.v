// MAC: FP8 E5M2 x FP8 E5M2 (exact) -> FP12 E6M5 accumulator register, with selectable adder.
//   MODE 0 = round-to-nearest-even, 1 = lazy SR, 2 = eager SR (paper's design)
module fp_mac #(
    parameter MODE  = 2,
    parameter R     = 18,
    parameter STEPS = 18,
    parameter [R-1:0] SEED = 1,
    parameter [R-1:0] MASK = 18'h20400
)(
    input  wire        clk,
    input  wire        rst,      // clears accumulator and reloads LFSR seed
    input  wire        en,
    input  wire [7:0]  a,
    input  wire [7:0]  b,
    output reg  [11:0] acc
);
    wire [11:0]  prod;
    wire [R-1:0] rnd, lfsr_state;
    wire [11:0]  s_rn, s_lazy, s_eager, sum;

    fp8_multiplier u_mul (.a(a), .b(b), .p(prod));
    lfsr_galois #(.W(R), .MASK(MASK), .SEED(SEED), .STEPS(STEPS))
        u_lfsr (.clk(clk), .rst(rst), .en(en), .next_word(rnd), .state(lfsr_state));

    fp12_add                     u_rn    (.a(acc), .b(prod), .result(s_rn));
    fp12_add_sr_lazy  #(.R(R))   u_lazy  (.a(acc), .b(prod), .random_bits(rnd), .result(s_lazy));
    fp12_add_sr_eager #(.R(R))   u_eager (.a(acc), .b(prod), .random_bits(rnd), .result(s_eager));

    assign sum = (MODE == 0) ? s_rn : (MODE == 1) ? s_lazy : s_eager;

    always @(posedge clk) begin
        if (rst)     acc <= 12'd0;
        else if (en) acc <= sum;
    end
endmodule
