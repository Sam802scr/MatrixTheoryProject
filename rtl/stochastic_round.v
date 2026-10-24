
module stochastic_round #(
    parameter RAND_WIDTH = 8
)(
    input  wire [RAND_WIDTH-1:0] random_bits,
    input  wire [RAND_WIDTH-1:0] threshold,
    output wire                  round_up
);

    // Round up when the random value is below the threshold.
    assign round_up = (random_bits < threshold);

endmodule
