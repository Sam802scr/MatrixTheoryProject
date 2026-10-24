`timescale 1ns/1ps

module tb_fp12_round_correction;

    reg left_normalized;
    reg normalized_lsb;
    reg guard_bit;
    reg s1_prime;
    reg s2_prime;

    wire corrected_lsb;
    wire correction_bit;

    fp12_round_correction dut (
        .left_normalized(left_normalized),
        .normalized_lsb(normalized_lsb),
        .guard_bit(guard_bit),
        .s1_prime(s1_prime),
        .s2_prime(s2_prime),
        .corrected_lsb(corrected_lsb),
        .correction_bit(correction_bit)
    );

    initial begin
        $display("Round Correction block tests");

        // Case 1: No left normalization
        left_normalized = 0;
        normalized_lsb = 1;
        guard_bit = 0;
        s1_prime = 1;
        s2_prime = 0;
        #1;
        if (corrected_lsb !== 1 || correction_bit !== 1)
            $fatal(1, "Test 1 failed");
        $display("Test 1 PASS");

        // Case 2: Left normalization
        left_normalized = 1;
        normalized_lsb = 0;
        guard_bit = 1;
        s1_prime = 0;
        s2_prime = 1;
        #1;
        if (corrected_lsb !== 1 || correction_bit !== 1)
            $fatal(1, "Test 2 failed");
        $display("Test 2 PASS");

        // Case 3: Left normalization with guard bit zero
        left_normalized = 1;
        normalized_lsb = 1;
        guard_bit = 0;
        s1_prime = 1;
        s2_prime = 0;
        #1;
        if (corrected_lsb !== 0 || correction_bit !== 0)
            $fatal(1, "Test 3 failed");
        $display("Test 3 PASS");

        $display("All Round Correction block tests passed.");
        $finish;
    end

endmodule