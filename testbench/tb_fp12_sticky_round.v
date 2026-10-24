
`timescale 1ns/1ps

module tb_fp12_sticky_round;

    localparam R = 18;

    reg  [R-3:0] shifted_y_low;
    reg  [R-3:0] random_low;

    wire [R-2:0] sticky_sum;
    wire s1_prime;
    wire s2_prime;

    fp12_sticky_round #(.R(R)) dut (
        .shifted_y_low(shifted_y_low),
        .random_low(random_low),
        .sticky_sum(sticky_sum),
        .s1_prime(s1_prime),
        .s2_prime(s2_prime)
    );

    initial begin
        $display("Sticky Round block tests");

        // Test 1: zero plus zero
        shifted_y_low = 16'd0;
        random_low    = 16'd0;
        #1;
        if (sticky_sum !== 17'd0)
            $fatal(1, "Test 1 failed");
        $display("Test 1 PASS");

        // Test 2: ordinary addition, no overflow
        shifted_y_low = 16'd5;
        random_low    = 16'd3;
        #1;
        if (sticky_sum !== 17'd8)
            $fatal(1, "Test 2 failed");
        $display("Test 2 PASS");

        // Test 3: maximum 16-bit value plus one
        shifted_y_low = 16'hFFFF;
        random_low    = 16'd1;
        #1;
        if (sticky_sum !== 17'h10000)
            $fatal(1, "Test 3 failed");
        $display("Test 3 PASS");

        // Test 4: verify the two upper output bits
        if (s1_prime !== sticky_sum[R-2] ||
            s2_prime !== sticky_sum[R-3])
            $fatal(1, "Test 4 failed");
        $display("Test 4 PASS");

        $display("All Sticky Round block tests passed.");
        $finish;
    end

endmodule
