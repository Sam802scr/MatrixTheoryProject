`timescale 1ns/1ps
module tb_fp_mac_adaptive;
    reg clk, rst, en;
    reg [2:0] r_sel;
    reg [7:0] a, b;
    wire [11:0] acc;

    fp_mac_adaptive #(.MODE(2)) u_mac (
        .clk(clk),
        .rst(rst),
        .en(en),
        .r_sel(r_sel),
        .a(a),
        .b(b),
        .acc(acc)
    );

    always #5 clk = ~clk;

    integer i;
    initial begin
        clk = 0;
        rst = 1;
        en = 0;
        r_sel = 3'd4; // r = 13
        a = 8'd0;
        b = 8'd0;
        #20;
        rst = 0;
        en = 1;

        $display("Testing fp_mac_adaptive accumulation across different r_sel modes...");
        // Accumulate 100 steps in r=13 mode
        r_sel = 3'd4;
        for (i = 0; i < 50; i = i + 1) begin
            a = 8'h38; // 1.0 in FP8 E5M2
            b = 8'h34; // 0.5 in FP8 E5M2
            #10;
        end
        $display("After 50 steps (r=13): acc = %h", acc);

        // Switch adaptively to r=7 mode (r_sel=1)
        r_sel = 3'd1;
        for (i = 0; i < 50; i = i + 1) begin
            a = 8'h38; // 1.0 in FP8 E5M2
            b = 8'h30; // 0.25 in FP8 E5M2
            #10;
        end
        $display("After 50 steps (r=7): acc = %h", acc);

        // Switch adaptively to r=4 mode (r_sel=0)
        r_sel = 3'd0;
        for (i = 0; i < 50; i = i + 1) begin
            a = 8'h38;
            b = 8'h30;
            #10;
        end
        $display("After 50 steps (r=4): acc = %h", acc);

        if (acc != 12'd0) begin
            $display("PASS tb_fp_mac_adaptive");
        end else begin
            $display("FAIL tb_fp_mac_adaptive: accumulator zero");
        end
        $finish;
    end
endmodule
