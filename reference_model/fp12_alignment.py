
def get_fp12_fields(bits):
    """Extract sign, exponent and fraction from an E6M5 FP12 value."""
    bits &= 0xFFF

    sign = (bits >> 11) & 1
    exponent_bits = (bits >> 5) & 0b111111
    fraction = bits & 0b11111

    if exponent_bits == 0 or exponent_bits == 63:
        raise ValueError(
            "This learning example supports normal finite numbers only."
        )

    # E6M5 uses an assumed exponent bias of 31.
    exponent = exponent_bits - 31

    # Six-bit significand: implicit leading 1 followed by 5 fraction bits.
    significand = (1 << 5) | fraction

    return sign, exponent, significand


def align_fp12(a_bits, b_bits):
    """Align two normal finite FP12 significands to a common exponent."""
    sign_a, exp_a, sig_a = get_fp12_fields(a_bits)
    sign_b, exp_b, sig_b = get_fp12_fields(b_bits)

    common_exp = max(exp_a, exp_b)

    # Shift the significand belonging to the smaller exponent right.
    aligned_a = sig_a >> (common_exp - exp_a)
    aligned_b = sig_b >> (common_exp - exp_b)

    return sign_a, aligned_a, sign_b, aligned_b, common_exp



def align_fp12_extended(a_bits, b_bits, extra_bits=3):
    """
    Align normal finite E6M5 significands and report
    discarded bits for each operand.

    This is a learning model, not complete hardware
    guard/round/sticky or stochastic-rounding logic.
    """
    sign_a, exp_a, sig_a = get_fp12_fields(a_bits)
    sign_b, exp_b, sig_b = get_fp12_fields(b_bits)

    common_exp = max(exp_a, exp_b)

    sig_a <<= extra_bits
    sig_b <<= extra_bits

    shift_a = common_exp - exp_a
    shift_b = common_exp - exp_b

    # Record the bits discarded by each right shift.
    discarded_a = (
        sig_a & ((1 << shift_a) - 1) if shift_a > 0 else 0
    )
    discarded_b = (
        sig_b & ((1 << shift_b) - 1) if shift_b > 0 else 0
    )

    aligned_a = sig_a >> shift_a
    aligned_b = sig_b >> shift_b

    sticky_a = int(discarded_a != 0)
    sticky_b = int(discarded_b != 0)

    return (
        sign_a,
        aligned_a,
        sign_b,
        aligned_b,
        common_exp,
        extra_bits,
        discarded_a,
        discarded_b,
        sticky_a,
        sticky_b,
    )

def encode_normal_fp12(value):
    """Encode a positive, exactly representable normal E6M5 value."""
    if value <= 0:
        raise ValueError("Use a positive normal value in this example.")

    import math

    exponent = math.floor(math.log2(value))
    exponent_bits = exponent + 31
    fraction_value = (value / (2 ** exponent) - 1.0) * 32

    if not fraction_value.is_integer():
        raise ValueError("Value is not exactly representable in this helper.")

    fraction = int(fraction_value)

    if not (1 <= exponent_bits <= 62 and 0 <= fraction <= 31):
        raise ValueError("Value is outside the supported normal range.")

    return (exponent_bits << 5) | fraction


if __name__ == "__main__":
    a_bits = encode_normal_fp12(1.0)
    b_bits = encode_normal_fp12(0.25)

    sign_a, sig_a, sign_b, sig_b, common_exp = align_fp12(
        a_bits, b_bits
    )

    print("1.0 and 0.25")
    print("Common exponent:", common_exp)
    print("Aligned significand of 1.0:", sig_a)
    print("Aligned significand of 0.25:", sig_b)
    print("Sum of aligned significands:", sig_a + sig_b)
    print("Expected numerical result:", 1.0 + 0.25)
