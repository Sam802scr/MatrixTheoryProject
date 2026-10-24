
`timescale 1ns/1ps

module tb_fp12_accumulator;

reg clk = 0;
reg rst = 1;
reg enable = 0;
reg signed [11:0] addend;

wire signed [11:0] accumulator;

fp12_accumulator dut (
    .clk(clk),
    .rst(rst),
    .enable(enable),
    .addend(addend),
    .accumulator(accumulator)
);

always #5 clk = ~clk;

initial begin
    $monitor("time=%0t rst=%b enable=%b addend=%0d accumulator=%0d",
             $time, rst, enable, addend, accumulator);

    addend = 0;
    #10;
    rst = 0;
    enable = 1;

    addend = 10;
    #10;
    addend = 20;
    #10;
    addend = -5;
    #10;

    enable = 0;
    #10;

    if (accumulator !== 12'sd25)
        $display("FAIL: expected 25");
    else
        $display("PASS: accumulator = 25");

    $finish;
end

endmodule
