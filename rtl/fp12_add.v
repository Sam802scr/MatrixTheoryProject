
module fp12_add (
    input  wire [11:0] a,
    input  wire [11:0] b,
    output reg  [11:0] result
);

    reg sign_a, sign_b, sign_result;
    reg [5:0] exp_a, exp_b, exp_result;
    reg [5:0] exp_large, exp_small;
    reg [5:0] sig_large, sig_small;
    reg [6:0] sig_a_ext, sig_b_ext, sig_sum;
    reg [6:0] sig_norm;
    reg [5:0] exp_diff;
    reg [4:0] frac_result;

    always @* begin
        sign_a = a[11];
        exp_a  = a[10:5];
        sign_b = b[11];
        exp_b  = b[10:5];

        sig_a_ext = {1'b1, a[4:0]};
        sig_b_ext = {1'b1, b[4:0]};

        if (exp_a >= exp_b) begin
            exp_large = exp_a;
            exp_small = exp_b;
            sig_large = sig_a_ext[5:0];
            sig_small = sig_b_ext[5:0];
            sign_result = sign_a;
        end else begin
            exp_large = exp_b;
            exp_small = exp_a;
            sig_large = sig_b_ext[5:0];
            sig_small = sig_a_ext[5:0];
            sign_result = sign_b;
        end

        exp_diff = exp_large - exp_small;

        if (exp_diff >= 6)
            sig_small = 0;
        else
            sig_small = sig_small >> exp_diff;

        exp_result = exp_large;
        sig_norm = 0;

        if (sign_a == sign_b) begin
            sig_sum = {1'b0, sig_large} + {1'b0, sig_small};

            if (sig_sum[6]) begin
                sig_norm = sig_sum >> 1;
                exp_result = exp_large + 1'b1;
            end else begin
                sig_norm = sig_sum;
            end
        end else begin
            sig_sum = {1'b0, sig_large} - {1'b0, sig_small};
            sig_norm = sig_sum;

            if (sig_norm == 0) begin
                exp_result = 0;
                sign_result = 0;
            end else begin
                while (!sig_norm[5] && exp_result > 1) begin
                    sig_norm = sig_norm << 1;
                    exp_result = exp_result - 1'b1;
                end
            end
        end

        frac_result = sig_norm[4:0];

        if (exp_result == 0)
            result = 12'b0;
        else
            result = {sign_result, exp_result, frac_result};
    end

endmodule
