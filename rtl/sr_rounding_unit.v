
module sr_rounding_unit (
    input wire clk,
    input wire rst,
    input wire enable,
    input wire [7:0] threshold,
    output wire round_up,
    output wire [7:0] random_bits
);

    lfsr #(
        .WIDTH(8),
        .SEED(8'hA5)
    ) random_generator (
        .clk(clk),
        .rst(rst),
        .enable(enable),
        .random_bits(random_bits)
    );

    stochastic_round #(
        .RAND_WIDTH(8)
    ) rounding_decision (
        .random_bits(random_bits),
        .threshold(threshold),
        .round_up(round_up)
    );

endmodule
