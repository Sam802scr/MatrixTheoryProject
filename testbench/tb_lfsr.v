
`timescale 1ns/1ps

module tb_lfsr;

    reg clk = 0;
    reg rst = 1;
    reg enable = 0;

    wire [7:0] random_bits;

    lfsr #(
        .WIDTH(8),
        .SEED(8'hA5)
    ) dut (
        .clk(clk),
        .rst(rst),
        .enable(enable),
        .random_bits(random_bits)
    );

    always #5 clk = ~clk;

    integer i;

    initial begin
        $display("Starting LFSR test");

        #10;
        rst = 0;
        enable = 1;

        for (i = 0; i < 20; i = i + 1) begin
            #10;
            $display("Random bits = %b (%h)",
                     random_bits, random_bits);
        end

        $finish;
    end

endmodule
