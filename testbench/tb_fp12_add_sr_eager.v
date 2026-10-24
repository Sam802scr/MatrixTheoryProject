`timescale 1ns/1ps

module tb_fp12_add_sr_eager;

    reg [11:0] a, b;
    reg [17:0] random_bits;
    wire [11:0] result;

    fp12_add_sr_eager dut (
        .a(a),
        .b(b),
        .random_bits(random_bits),
        .result(result)
    );

    initial begin
        $display("Eager rounding RTL smoke test");

        a = 12'h0A9;
        b = 12'hDAD;
        random_bits = 18'd0;
        #10;
        $display("a=%h b=%h random=%d result=%h",
                 a, b, random_bits, result);

        a = 12'h0D6;
        b = 12'hC67;
        random_bits = 18'd100000;
        #10;
        $display("a=%h b=%h random=%d result=%h",
                 a, b, random_bits, result);

        a = 12'h1C4;
        b = 12'hBDA;
        random_bits = 18'd200000;
        #10;
        $display("a=%h b=%h random=%d result=%h",
                 a, b, random_bits, result);

        $display("Smoke test finished; outputs require reference checking.");
        $finish;
    end

endmodule