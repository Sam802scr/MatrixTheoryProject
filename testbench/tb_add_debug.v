
module tb_add_debug;

    reg  [17:0] x, y;
    reg  [17:0] z;

    initial begin
        x = 18'h10000;
        y = 18'h10000;
        z = x + y;
        #1;
        $display("x=%h y=%h z=%h", x, y, z);

        x = 18'h10000;
        y = 18'h08000;
        z = x + y;
        #1;
        $display("x=%h y=%h z=%h", x, y, z);

        $finish;
    end

endmodule
