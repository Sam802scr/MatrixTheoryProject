`timescale 1ns/1ps
// Runs the full MAC (multiplier + adder + Galois LFSR + accumulator) for all three modes and compares
// the accumulator after every step with the Python golden model.
module tb_mac_vectors;
    reg clk = 0, rst = 1, en = 0;
    reg [7:0] a, b;
    wire [11:0] acc_rn, acc_lz, acc_eg;
    reg [51:0] mem [0:99999];
    integer i, n, bad;
    always #5 clk = ~clk;

    fp_mac #(.MODE(0)) u_rn (.clk(clk), .rst(rst), .en(en), .a(a), .b(b), .acc(acc_rn));
    fp_mac #(.MODE(1)) u_lz (.clk(clk), .rst(rst), .en(en), .a(a), .b(b), .acc(acc_lz));
    fp_mac #(.MODE(2)) u_eg (.clk(clk), .rst(rst), .en(en), .a(a), .b(b), .acc(acc_eg));

    initial begin
        for (i = 0; i < 100000; i = i + 1) mem[i] = 52'bx;
        $readmemh("reference_model/vectors/mac_vec.hex", mem);
        a = 0; b = 0; bad = 0; n = 0;
        repeat (2) @(posedge clk);
        #1 rst = 0;
        i = 0;
        while (^mem[i] !== 1'bx) begin
            a = mem[i][51:44]; b = mem[i][43:36]; en = 1;
            @(posedge clk); #1;
            if (acc_rn !== mem[i][35:24] || acc_lz !== mem[i][23:12] || acc_eg !== mem[i][11:0]) begin
                bad = bad + 1;
                if (bad < 6) $display("step %0d MISMATCH rn %h/%h lazy %h/%h eager %h/%h", i, acc_rn, mem[i][35:24], acc_lz, mem[i][23:12], acc_eg, mem[i][11:0]);
            end
            n = n + 1; i = i + 1;
        end
        $display("MAC steps=%0d mismatches=%0d", n, bad);
        if (n > 0 && bad == 0) $display("PASS tb_mac_vectors"); else $display("FAIL tb_mac_vectors");
        $finish;
    end
endmodule
