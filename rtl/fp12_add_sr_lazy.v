module fp12_add_sr (
    input  wire [11:0] a,
    input  wire [11:0] b,
    input  wire [17:0] random_bits,
    output reg  [11:0] result
);

    reg sign_a, sign_b, sign_result;
    reg [5:0] exp_a, exp_b, exp_work;
    reg [5:0] sig_a, sig_b;
    reg [31:0] mag_a, mag_b, mag;
    reg [31:0] rem_bits;
    reg [6:0] sig_round;
    reg round_up;
    integer shift_amt;
    integer i;

    always @* begin
        sign_a = a[11];
        sign_b = b[11];
        exp_a = a[10:5];
        exp_b = b[10:5];

        sig_a = {1'b1, a[4:0]};
        sig_b = {1'b1, b[4:0]};

        exp_work = 0;
        sign_result = 0;
        mag_a = 0;
        mag_b = 0;
        mag = 0;
        rem_bits = 0;
        sig_round = 0;
        round_up = 0;
        shift_amt = 0;
        result = 0;

        if (exp_a != 63 && exp_b != 63) begin
            if (exp_a == 0) sig_a = 0;
            if (exp_b == 0) sig_b = 0;

            if (sig_a != 0 || sig_b != 0) begin
                mag_a = {sig_a, 18'd0};
                mag_b = {sig_b, 18'd0};

                if (exp_a >= exp_b) begin
                    exp_work = exp_a;
                    shift_amt = exp_a - exp_b;
                    if (shift_amt >= 32)
                        mag_b = 0;
                    else
                        mag_b = mag_b >> shift_amt;
                end else begin
                    exp_work = exp_b;
                    shift_amt = exp_b - exp_a;
                    if (shift_amt >= 32)
                        mag_a = 0;
                    else
                        mag_a = mag_a >> shift_amt;
                end

                if (sign_a == sign_b) begin
                    mag = mag_a + mag_b;
                    sign_result = sign_a;
                end else if (mag_a >= mag_b) begin
                    mag = mag_a - mag_b;
                    sign_result = sign_a;
                end else begin
                    mag = mag_b - mag_a;
                    sign_result = sign_b;
                end

                if (mag != 0) begin
                    if (mag[24]) begin
                        mag = mag >> 1;
                        exp_work = exp_work + 1'b1;
                    end else begin
                        for (i = 0; i < 24; i = i + 1) begin
                            if (!mag[23] && exp_work > 1) begin
                                mag = mag << 1;
                                exp_work = exp_work - 1'b1;
                            end
                        end
                    end

                    if (exp_work <= 1 && !mag[23]) begin
                        result = 0;
                    end else begin
                        sig_round = {1'b0, mag[23:18]};
                        rem_bits = mag[17:0];

                        round_up = ({14'd0, random_bits} < rem_bits);

                        if (round_up)
                            sig_round = sig_round + 1'b1;

                        if (sig_round[6]) begin
                            sig_round = 7'd32;
                            exp_work = exp_work + 1'b1;
                        end

                        if (exp_work >= 63)
                            result = {sign_result, 6'd63, 5'd0};
                        else if (exp_work == 0)
                            result = 0;
                        else
                            result = {
                                sign_result,
                                exp_work,
                                sig_round[4:0]
                            };
                    end
                end
            end
        end
    end

endmodule