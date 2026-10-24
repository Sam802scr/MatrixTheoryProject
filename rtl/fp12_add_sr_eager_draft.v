module fp12_add_sr_eager (
    input  wire [11:0] a,
    input  wire [11:0] b,
    input  wire [17:0] random_bits,
    output reg  [11:0] result
);

    reg sign_a, sign_b, sign_result;
    reg [5:0] exp_a, exp_b, exp_work;
    reg [5:0] sig_a, sig_b;

    reg [31:0] mag_a, mag_b, mag;
    reg [31:0] shifted_a, shifted_b;

    reg [31:0] sticky_a, sticky_b;
    reg [31:0] aligned_a, aligned_b;

    reg [5:0] sig_round;
    reg [6:0] sig_corrected;

    reg round_up_a, round_up_b;
    reg correction;
    reg left_normalized;

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

        shifted_a = 0;
        shifted_b = 0;

        sticky_a = 0;
        sticky_b = 0;

        aligned_a = 0;
        aligned_b = 0;

        sig_round = 0;
        sig_corrected = 0;

        round_up_a = 0;
        round_up_b = 0;
        correction = 0;
        left_normalized = 0;

        shift_amt = 0;
        result = 0;

        if (exp_a != 63 && exp_b != 63) begin
            if (exp_a == 0)
                sig_a = 0;

            if (exp_b == 0)
                sig_b = 0;

            if (sig_a != 0 || sig_b != 0) begin

                mag_a = {sig_a, 18'd0};
                mag_b = {sig_b, 18'd0};

                if (exp_a >= exp_b) begin
                    exp_work = exp_a;
                    shift_amt = exp_a - exp_b;

                    shifted_a = mag_a;
                    shifted_b = mag_b;

                end else begin
                    exp_work = exp_b;
                    shift_amt = exp_b - exp_a;

                    shifted_a = mag_b;
                    shifted_b = mag_a;
                end

                /*
                 * Alignment-stage stochastic rounding.
                 *
                 * This prototype rounds the smaller significand
                 * before the main addition/subtraction.
                 * The full paper-specific Sticky Round and
                 * Round Correction equations still need validation.
                 */

                if (shift_amt >= 32) begin
                    shifted_b = 0;
                end else if (shift_amt > 0) begin
                    sticky_b = shifted_b;
                    shifted_b = shifted_b >> shift_amt;

                    round_up_b =
                        ({14'd0, random_bits} <
                         (sticky_b &
                          ((32'h00000001 << shift_amt) - 1)));

                    if (round_up_b)
                        shifted_b = shifted_b + 1'b1;
                end

                aligned_a = shifted_a;
                aligned_b = shifted_b;

                /*
                 * Main addition or subtraction.
                 * The operands have been aligned before arithmetic.
                 */

                if (sign_a == sign_b) begin
                    mag = aligned_a + aligned_b;
                    sign_result = sign_a;
                end else if (aligned_a >= aligned_b) begin
                    mag = aligned_a - aligned_b;
                    sign_result = sign_a;
                end else begin
                    mag = aligned_b - aligned_a;
                    sign_result = sign_b;
                end

                /*
                 * Normalize the arithmetic result.
                 */

                if (mag != 0) begin
                    if (mag[24]) begin
                        mag = mag >> 1;
                        exp_work = exp_work + 1'b1;
                    end else begin
                        for (i = 0; i < 24; i = i + 1) begin
                            if (!mag[23] && exp_work > 1) begin
                                mag = mag << 1;
                                exp_work = exp_work - 1'b1;
                                left_normalized = 1'b1;
                            end
                        end
                    end

                    /*
                     * Round Correction placeholder.
                     *
                     * A paper-faithful implementation must use
                     * the Sticky Round output bits and the
                     * normalization-dependent correction rule.
                     */

                    sig_round = mag[23:18];

                    correction = 1'b0;

                    if (left_normalized)
                        correction = 1'b0;

                    sig_corrected = {1'b0, sig_round};

                    if (correction)
                        sig_corrected = sig_corrected + 1'b1;

                    if (exp_work <= 1 && !mag[23]) begin
                        result = 0;
                    end else if (exp_work >= 63) begin
                        result = {sign_result, 6'd63, 5'd0};
                    end else if (exp_work == 0) begin
                        result = 0;
                    end else begin
                        result = {
                            sign_result,
                            exp_work,
                            sig_corrected[4:0]
                        };
                    end
                end
            end
        end
    end

endmodule