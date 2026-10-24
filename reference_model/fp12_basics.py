
import math



def decode_fp12_e6m5(bits):
    """Decode 12-bit E6M5 with subnormal numbers disabled."""
    bits &= 0xFFF

    sign = (bits >> 11) & 1
    exponent = (bits >> 5) & 0b111111
    fraction = bits & 0b11111

    if exponent == 0:
        # Subnormals are disabled; exponent-zero patterns map to zero.
        value = 0.0
    elif exponent == 63:
        if fraction == 0:
            value = float("inf")
        else:
            value = float("nan")
    else:
        value = (1.0 + fraction / 32.0) * (2.0 ** (exponent - 31))

    return -value if sign else value


if __name__ == "__main__":
    test_patterns = [
        0b001111100000,  # +1.0
        0b101111100000,  # -1.0
        0b010000000000,  # +2.0
        0b000000000000,  # +0.0
    ]

    for bits in test_patterns:
        print(f"{bits:012b} -> {decode_fp12_e6m5(bits)}")
