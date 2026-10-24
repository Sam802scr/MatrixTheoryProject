module fp12_round_correction (
    input  wire left_normalized,
    input  wire normalized_lsb,
    input  wire guard_bit,
    input  wire s1_prime,
    input  wire s2_prime,

    output wire corrected_lsb,
    output wire correction_bit
);

    // Figure 4(b): after a left shift, restore the
    // guard bit into the normalized result's LSB.
    assign corrected_lsb =
        left_normalized ? guard_bit : normalized_lsb;

    // Figure 4(a): use S1' without left normalization.
    // Figure 4(b): use S2' after left normalization.
    assign correction_bit =
        left_normalized ? s2_prime : s1_prime;

endmodule