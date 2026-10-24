
`timescale 1ns/1ps

module tb_stochastic_round;

    reg  [7:0] random_bits;
    reg  [7:0] threshold;
    wire       round_up;

    stochastic_round dut (
        .random_bits(random_bits),
        .threshold(threshold),
        .round_up(round_up)
    );

    initial begin
        threshold = 8'd128;

        random_bits = 8'd10;
        #1;
        $display("Random=10, round_up=%b (expected 1)", round_up);

        random_bits = 8'd200;
        #1;
        $display("Random=200, round_up=%b (expected 0)", round_up);

        random_bits = 8'd127;
        #1;
        $display("Random=127, round_up=%b (expected 1)", round_up);

        random_bits = 8'd128;
        #1;
        $display("Random=128, round_up=%b (expected 0)", round_up);

        $finish;
    end

endmodule
