`timescale 1ns/1ps
module tb_fp12_add_sr_adaptive;
    reg [11:0] a, b;
    reg [17:0] rnd_all;
    reg [2:0]  r_sel;
    wire [11:0] y_adapt;
    wire [11:0] y_eager_4, y_eager_7, y_eager_9, y_eager_11, y_eager_13;

    // Instantiate adaptive adder
    fp12_add_sr_adaptive u_adapt (
        .a(a),
        .b(b),
        .random_bits(rnd_all[12:0]),
        .r_sel(r_sel),
        .result(y_adapt)
    );

    // Instantiate dedicated adders for each r configuration
    fp12_add_sr_eager #(.R(4))  u_e4  (.a(a), .b(b), .random_bits(rnd_all[3:0]),   .result(y_eager_4));
    fp12_add_sr_eager #(.R(7))  u_e7  (.a(a), .b(b), .random_bits(rnd_all[6:0]),   .result(y_eager_7));
    fp12_add_sr_eager #(.R(9))  u_e9  (.a(a), .b(b), .random_bits(rnd_all[8:0]),   .result(y_eager_9));
    fp12_add_sr_eager #(.R(11)) u_e11 (.a(a), .b(b), .random_bits(rnd_all[10:0]),  .result(y_eager_11));
    fp12_add_sr_eager #(.R(13)) u_e13 (.a(a), .b(b), .random_bits(rnd_all[12:0]),  .result(y_eager_13));

    integer i, seed, r_idx;
    integer bad_cnt;
    reg [11:0] exp_val;

    initial begin
        seed = 12345;
        bad_cnt = 0;
        $display("===============================================================");
        $display("Testing Adaptive Stochastic Rounding Adder RTL against Dedicated Models");
        $display("===============================================================");

        for (r_idx = 0; r_idx < 5; r_idx = r_idx + 1) begin
            r_sel = r_idx[2:0];
            bad_cnt = 0;
            for (i = 0; i < 5000; i = i + 1) begin
                a = $random(seed);
                b = $random(seed);
                rnd_all = {$random(seed), $random(seed)} & 18'h3FFFF;
                #1;

                case (r_idx)
                    0: exp_val = y_eager_4;
                    1: exp_val = y_eager_7;
                    2: exp_val = y_eager_9;
                    3: exp_val = y_eager_11;
                    4: exp_val = y_eager_13;
                endcase

                if (y_adapt !== exp_val) begin
                    bad_cnt = bad_cnt + 1;
                    if (bad_cnt <= 5) begin
                        $display("MISMATCH r_sel=%0d a=%h b=%h rnd=%h got=%h exp=%h",
                                 r_sel, a, b, rnd_all, y_adapt, exp_val);
                    end
                end
            end

            case (r_idx)
                0: $display("r = 4  (r_sel=0): 5000 vectors checked, mismatches = %0d", bad_cnt);
                1: $display("r = 7  (r_sel=1): 5000 vectors checked, mismatches = %0d", bad_cnt);
                2: $display("r = 9  (r_sel=2): 5000 vectors checked, mismatches = %0d", bad_cnt);
                3: $display("r = 11 (r_sel=3): 5000 vectors checked, mismatches = %0d", bad_cnt);
                4: $display("r = 13 (r_sel=4): 5000 vectors checked, mismatches = %0d", bad_cnt);
            endcase
            if (bad_cnt != 0) begin
                $display("FAIL in r_idx = %0d", r_idx);
                $finish;
            end
        end

        $display("===============================================================");
        $display("ALL 25,000 ADAPTIVE HARDWARE VECTORS PASSED PERFECTLY!");
        $display("===============================================================");
        $finish;
    end
endmodule
