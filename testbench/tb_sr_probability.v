
`timescale 1ns/1ps

module tb_sr_probability;

    reg clk;
    reg rst;
    reg enable;
    reg [7:0] threshold;

    wire round_up;
    wire [7:0] random_bits;

    integer i;
    integer round_up_count;

    sr_rounding_unit dut (
        .clk(clk),
        .rst(rst),
        .enable(enable),
        .threshold(threshold),
        .round_up(round_up),
        .random_bits(random_bits)
    );

    always #5 clk = ~clk;

    initial begin
        clk = 0;
        rst = 1;
        enable = 0;
        threshold = 8'd8;
        round_up_count = 0;

        // Initialize the LFSR
        repeat (2) @(posedge clk);
        #1;
        rst = 0;
        enable = 1;

        // Count decisions over 1000 cycles
        for (i = 0; i < 1000; i = i + 1) begin
            @(posedge clk);
            #1;

            if (round_up)
                round_up_count = round_up_count + 1;
        end

        $display("RTL Stochastic Rounding Test");
        $display("-----------------------------");
        $display("Cycles: %0d", 1000);
        $display("Threshold: %0d", threshold);
        $display("Round-ups: %0d", round_up_count);
        $display("Observed rate: %0f percent",
                 round_up_count * 100.0 / 1000);

        $finish;
    end

endmodule
