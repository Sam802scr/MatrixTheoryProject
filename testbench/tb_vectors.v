`timescale 1ns/1ps
// Bit-exact check of the three adders against vectors made by reference_model/gen_vectors.py
module tb_vectors;
    reg [79:0] mem [0:199999];
    reg [11:0] a, b, exp_rn, exp_lz, exp_eg;
    reg [17:0] rnd;
    wire [11:0] y_rn, y_lz, y_eg;
    integer i, n, bad_rn, bad_lz, bad_eg;

    fp12_add                  u_rn (.a(a), .b(b), .result(y_rn));
    fp12_add_sr_lazy  #(.R(18)) u_lz (.a(a), .b(b), .random_bits(rnd), .result(y_lz));
    fp12_add_sr_eager #(.R(18)) u_eg (.a(a), .b(b), .random_bits(rnd), .result(y_eg));

    initial begin
        for (i = 0; i < 200000; i = i + 1) mem[i] = 80'bx;
        $readmemh("reference_model/vectors/vec.hex", mem);
        bad_rn = 0; bad_lz = 0; bad_eg = 0; n = 0;
        i = 0;
        while (^mem[i] !== 1'bx) begin
            a = mem[i][79:68]; b = mem[i][67:56]; rnd = mem[i][53:36];
            exp_rn = mem[i][35:24]; exp_lz = mem[i][23:12]; exp_eg = mem[i][11:0];
            #1;
            if (y_rn !== exp_rn) begin bad_rn = bad_rn + 1; if (bad_rn < 6) $display("RN    MISMATCH a=%h b=%h got=%h exp=%h", a, b, y_rn, exp_rn); end
            if (y_lz !== exp_lz) begin bad_lz = bad_lz + 1; if (bad_lz < 6) $display("LAZY  MISMATCH a=%h b=%h r=%h got=%h exp=%h", a, b, rnd, y_lz, exp_lz); end
            if (y_eg !== exp_eg) begin bad_eg = bad_eg + 1; if (bad_eg < 6) $display("EAGER MISMATCH a=%h b=%h r=%h got=%h exp=%h", a, b, rnd, y_eg, exp_eg); end
            n = n + 1; i = i + 1;
        end
        $display("vectors=%0d  mismatches: RN=%0d LAZY=%0d EAGER=%0d", n, bad_rn, bad_lz, bad_eg);
        if (n > 0 && bad_rn == 0 && bad_lz == 0 && bad_eg == 0) $display("PASS tb_vectors");
        else $display("FAIL tb_vectors");
        $finish;
    end
endmodule
