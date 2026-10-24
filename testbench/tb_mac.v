
module tb_mac;
    reg  [3:0] a, b;
    reg  [7:0] acc;
    wire [7:0] result;

    mac dut (
        .a(a),
        .b(b),
        .acc(acc),
        .result(result)
    );

    initial begin
        a = 4'd3;
        b = 4'd4;
        acc = 8'd10;
        #10;
        $display("MAC: 10 + (3 * 4) = %0d", result);

        a = 4'd5;
        b = 4'd6;
        acc = 8'd20;
        #10;
        $display("MAC: 20 + (5 * 6) = %0d", result);

        $finish;
    end
endmodule
