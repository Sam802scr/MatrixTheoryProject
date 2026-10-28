// Galois LFSR, default x^18 + x^11 + 1 (primitive, period 2^18-1).
// The paper only says "r-bit Galois LFSR": MASK, SEED and STEPS (LFSR steps per MAC) are OUR assumptions.
// next_word = state after STEPS steps; it is the random word used by the current MAC and is loaded on en.
module lfsr_galois #(
    parameter W     = 18,
    parameter [W-1:0] MASK = 18'h20400,   // bits 17 and 10
    parameter [W-1:0] SEED = 18'd1,
    parameter STEPS = 18
)(
    input  wire         clk,
    input  wire         rst,
    input  wire         en,
    output wire [W-1:0] next_word,
    output reg  [W-1:0] state
);
    function [W-1:0] adv;
        input [W-1:0] s;
        integer k;
        reg [W-1:0] t;
        begin
            t = s;
            for (k = 0; k < STEPS; k = k + 1)
                t = t[0] ? ((t >> 1) ^ MASK) : (t >> 1);
            adv = t;
        end
    endfunction

    assign next_word = adv(state);

    always @(posedge clk) begin
        if (rst)      state <= SEED;
        else if (en)  state <= next_word;
    end
endmodule
