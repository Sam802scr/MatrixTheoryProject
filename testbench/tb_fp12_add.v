
`timescale 1ns/1ps

module tb_fp12_add;

    reg  [11:0] a, b;
    wire [11:0] result;

    fp12_add dut (
        .a(a),
        .b(b),
        .result(result)
    );

    initial begin
        $display("Starting FP12 adder tests...");

        // E6M5, exponent bias = 31
        // 1.0  = 12'h3E0
        // 0.5  = 12'h3C0
        // 2.0  = 12'h400
        // 1.5  = 12'h3F0
        // -1.0 = 12'hBE0
        // -0.5 = 12'hBC0

        // Test 1: 1.0 + 1.0 = 2.0
        a = 12'h3E0;
        b = 12'h3E0;
        #10;
        $display("1.0 + 1.0 = %h (expected 400)",
                 result);

        // Test 2: 1.0 + 0.5 = 1.5
        a = 12'h3E0;
        b = 12'h3C0;
        #10;
        $display("1.0 + 0.5 = %h (expected 3F0)",
                 result);

        // Test 3: 1.0 + (-1.0) = 0
        a = 12'h3E0;
        b = 12'hBE0;
        #10;
        $display("1.0 + (-1.0) = %h (expected 000)",
                 result);

        // Test 4: -1.0 + (-0.5) = -1.5
        a = 12'hBE0;
        b = 12'hBC0;
        #10;
        $display("-1.0 + (-0.5) = %h (expected BF0)",
                 result);

        $display("Tests completed.");
        $finish;
    end

endmodule
