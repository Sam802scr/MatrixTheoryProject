
module tb_adder;
    reg  [3:0] a, b;
    wire [4:0] sum;

    adder dut (
        .a(a),
        .b(b),
        .sum(sum)
    );

    initial begin
        a = 4'd3;  b = 4'd5;
        #10;
        $display("3 + 5 = %0d", sum);

        a = 4'd15; b = 4'd1;
        #10;
        $display("15 + 1 = %0d", sum);

        $finish;
    end
endmodule
