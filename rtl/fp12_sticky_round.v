
module fp12_sticky_round #(
    parameter integer R = 18
) (
    input  wire [R-3:0] shifted_y_low,
    input  wire [R-3:0] random_low,
    output wire [R-2:0] sticky_sum,
    output wire         s1_prime,
    output wire         s2_prime
);

    // First stage of eager stochastic rounding.
    // Add the (R-2) low bits of the aligned smaller
    // significand to the (R-2) low random bits.
    //
    // sticky_sum[R-2] is the carry from this addition.
    // sticky_sum[R-3] is the next-highest sum bit.
    //
    // The main adder integration and normalization-dependent
    // correction are implemented separately.

    assign sticky_sum =
        {1'b0, shifted_y_low} + {1'b0, random_low};

    assign s1_prime = sticky_sum[R-2];
    assign s2_prime = sticky_sum[R-3];

endmodule
