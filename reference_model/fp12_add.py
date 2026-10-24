
from fp12_basics import decode_fp12_e6m5


def encode_fp12_e6m5(value):
    """Temporary encoder using nearest representable FP12 value."""
    import math

    sign = 1 if value < 0 else 0
    x = abs(value)

    if x == 0:
        return sign << 11

    candidates = []
    for bits in range(0x7E0):
        decoded = decode_fp12_e6m5(bits)
        if math.isfinite(decoded):
            candidates.append((decoded, bits))

    _, best_bits = min(
        candidates,
        key=lambda item: (abs(item[0] - x), item[1] & 1)
    )

    return (sign << 11) | best_bits


def add_fp12(a_bits, b_bits):
    """Numerical prototype: decode, add, and re-encode."""
    a = decode_fp12_e6m5(a_bits)
    b = decode_fp12_e6m5(b_bits)
    return encode_fp12_e6m5(a + b)



if __name__ == "__main__":
    tests = [
        (1.0, 0.5),    # Different positive values
        (1.0, 1.0),    # Same positive values
        (2.0, -1.0),   # Positive plus negative
        (-1.0, -0.5),  # Two negative values
        (1.0, -1.0),   # Cancellation to zero
        (0.5, 0.25),   # Smaller values
    ]

    for a, b in tests:
        a_bits = encode_fp12_e6m5(a)
        b_bits = encode_fp12_e6m5(b)

        result_bits = add_fp12(a_bits, b_bits)
        result = decode_fp12_e6m5(result_bits)

        print(f"{a} + ({b}) = {result}")
