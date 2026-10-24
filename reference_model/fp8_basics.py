
import math


def decode_fp8_e5m2(bits):
    sign = (bits >> 7) & 1
    exponent = (bits >> 2) & 0b11111
    fraction = bits & 0b11

    if exponent == 0:
        value = (fraction / 4.0) * (2.0 ** (1 - 15))
    elif exponent == 31:
        if fraction == 0:
            value = float("inf")
        else:
            value = float("nan")
    else:
        value = (1.0 + fraction / 4.0) * (2.0 ** (exponent - 15))

    return -value if sign else value


def encode_fp8_e5m2(value):
    """Encode a Python float as FP8 E5M2 using round-to-nearest-even."""
    if math.isnan(value):
        return 0b01111101
    if math.isinf(value):
        return (0b10000000 if value < 0 else 0) | 0b01111100

    sign = 1 if math.copysign(1.0, value) < 0 else 0
    x = abs(value)

    if x == 0:
        return sign << 7

    # Search all positive finite FP8 encodings and select the nearest.
    # Ties are resolved by choosing the encoding with an even LSB.
    candidates = []
    for bits in range(0b01111100):
        decoded = decode_fp8_e5m2(bits)
        if math.isfinite(decoded):
            candidates.append((decoded, bits))

    best_value, best_bits = min(
        candidates,
        key=lambda item: (abs(item[0] - x), item[1] & 1)
    )

    # Overflow: values beyond the finite range map to infinity.
    if x > decode_fp8_e5m2(0b01111011):
        return (sign << 7) | 0b01111100

    return (sign << 7) | best_bits


if __name__ == "__main__":
    test_values = [1.0, -1.0, 2.0, 0.0, 0.5, 1.5]

    for value in test_values:
        bits = encode_fp8_e5m2(value)
        recovered = decode_fp8_e5m2(bits)
        print(f"{value:5} -> {bits:08b} -> {recovered}")

def multiply_fp8(a_bits, b_bits):
    """Functional prototype: multiply decoded FP8 operands.

    Keep the product as a Python value; do not round it
    back to FP8 before accumulation.
    """
    a = decode_fp8_e5m2(a_bits)
    b = decode_fp8_e5m2(b_bits)

    return a * b

a = encode_fp8_e5m2(1.5)
b = encode_fp8_e5m2(1.5)

product = multiply_fp8(a, b)

print("A:", decode_fp8_e5m2(a))
print("B:", decode_fp8_e5m2(b))
print("Product before accumulator rounding:", product)