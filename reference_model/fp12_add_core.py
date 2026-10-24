
from fp12_alignment import align_fp12, encode_normal_fp12
from fp12_basics import decode_fp12_e6m5


def add_fp12_core(a_bits, b_bits):
    """
    Learning model for adding normal finite E6M5 FP12 values.

    Uses exact integer significands and exponent scaling.
    Final encoding uses the existing reference encoder.
    """
    sign_a, sig_a, sign_b, sig_b, common_exp = align_fp12(
        a_bits, b_bits
    )

    # Convert both aligned significands to signed integer values.
    signed_a = -sig_a if sign_a else sig_a
    signed_b = -sig_b if sign_b else sig_b

    total = signed_a + signed_b

    if total == 0:
        return 0  # Positive zero for exact cancellation.

    # The significands use a scale factor of 2^5.
    result_value = abs(total) / 32.0 * (2.0 ** common_exp)

    result_bits = encode_normal_fp12(result_value)

    # Set the sign bit for a negative result.
    if total < 0:
        result_bits |= 1 << 11

    return result_bits


if __name__ == "__main__":
    tests = [
        (1.0, 0.25),
        (1.0, -0.25),
        (-1.0, -0.5),
        (1.0, -1.0),
    ]

    for a, b in tests:
        a_bits = encode_normal_fp12(abs(a))
        b_bits = encode_normal_fp12(abs(b))

        if a < 0:
            a_bits |= 1 << 11
        if b < 0:
            b_bits |= 1 << 11

        result_bits = add_fp12_core(a_bits, b_bits)
        result = decode_fp12_e6m5(result_bits)

        print(f"{a} + ({b}) = {result}")
