module tb_fp12_add_sr;
    reg [11:0] a, b;
    reg [17:0] random_bits;
    wire [11:0] result;

    fp12_add_sr dut (
        .a(a),
        .b(b),
        .random_bits(random_bits),
        .result(result)
    );

    initial begin
        // Opposite signs: these cases previously returned wrong signs.
        random_bits = 18'd0;

        a = 12'h0A9; b = 12'hDAD; #10;
        $display("A=0A9 B=DAD result=%03h", result);

        a = 12'h0D6; b = 12'hC67; #10;
        $display("A=0D6 B=C67 result=%03h", result);

        a = 12'h1C4; b = 12'hBDA; #10;
        $display("A=1C4 B=BDA result=%03h", result);

        $finish;
    end
endmodule
