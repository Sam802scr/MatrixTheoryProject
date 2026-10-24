
`timescale 1ns/1ps

module tb_sr_rounding_unit;

    reg clk, rst, enable;
    reg [7:0] threshold;
    wire round_up;
    wire [7:0] random_bits;

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
        threshold = 8'd128;

        #10;
        rst = 0;
        enable = 1;

        repeat (10) begin
            @(posedge clk);
            #1;
            $display("Random=%h, round_up=%b",
                     random_bits, round_up);
        end

        $finish;
    end

endmodule
