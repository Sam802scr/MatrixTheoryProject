
from fractions import Fraction
from bisect import bisect_left

EXP_BIAS = 31
MIN_NORMAL = Fraction(1, 2**30)
MAX_EXPONENT = 62
MAX_FRACTION = 31


def decode_normal(bits):
    """Decode a normal finite FP12 E6M5 encoding exactly."""
    bits &= 0xFFF
    sign = (bits >> 11) & 1
    exponent = (bits >> 5) & 0x3F
    fraction = bits & 0x1F

    if exponent == 0 or exponent == 63:
        raise ValueError(f"Unsupported encoding: 0x{bits:03X}")

    value = Fraction(32 + fraction, 32)
    power = exponent - EXP_BIAS
    value *= 2**power if power >= 0 else Fraction(1, 2**(-power))

    return -value if sign else value


def build_finite_values():
    """Build sorted finite normal values plus positive zero."""
    entries = [(Fraction(0), 0x000)]

    for sign in (0, 1):
        for exponent in range(1, MAX_EXPONENT + 1):
            for fraction in range(32):
                bits = (sign << 11) | (exponent << 5) | fraction
                entries.append((decode_normal(bits), bits))

    entries.sort(key=lambda item: item[0])
    return entries


REPRESENTABLE = build_finite_values()
VALUES = [value for value, _ in REPRESENTABLE]
MAX_FINITE = decode_normal(0x7DF)
MIN_FINITE = decode_normal(0x020)


def adjacent_values(exact):
    """Return the lower/upper neighbors and their encodings."""
    index = bisect_left(VALUES, exact)

    if index < len(VALUES) and VALUES[index] == exact:
        bits = REPRESENTABLE[index][1]
        return exact, exact, bits, bits

    if index == 0 or index == len(VALUES):
        raise OverflowError(
            "Exact value is outside the finite reference range."
        )

    lower, lower_bits = REPRESENTABLE[index - 1]
    upper, upper_bits = REPRESENTABLE[index]
    return lower, upper, lower_bits, upper_bits


def stochastic_round(exact, random_value, random_width):
    """
    Mathematical stochastic rounding to adjacent FP12 values.

    Convention:
      threshold = floor(q * 2**random_width)
      choose upper when random_value < threshold.

    Underflow policy for this reference: flush magnitudes below MIN_NORMAL
    to positive zero. This is a modeling assumption, not a claim about
    the paper's exact RTL implementation.
    """
    if random_width < 1:
        raise ValueError("random_width must be positive")

    limit = 1 << random_width
    if not 0 <= random_value < limit:
        raise ValueError("random_value is outside the selected bit width")

    if exact == 0 or abs(exact) < MIN_NORMAL:
        return 0x000

    lower, upper, lower_bits, upper_bits = adjacent_values(exact)

    if lower == upper:
        return lower_bits

    q = (exact - lower) / (upper - lower)
    threshold = (q.numerator * limit) // q.denominator

    return upper_bits if random_value < threshold else lower_bits


def check_probability(exact, random_width):
    """Check observed counts against the documented threshold convention."""
    lower, upper, lower_bits, upper_bits = adjacent_values(exact)

    if lower == upper:
        outcomes = [
            stochastic_round(exact, r, random_width)
            for r in range(1 << random_width)
        ]
        assert all(value == lower_bits for value in outcomes)
        return

    q = (exact - lower) / (upper - lower)
    limit = 1 << random_width
    expected_upper = (q.numerator * limit) // q.denominator

    upper_count = 0
    lower_count = 0

    for r in range(limit):
        result = stochastic_round(exact, r, random_width)
        if result == upper_bits:
            upper_count += 1
        elif result == lower_bits:
            lower_count += 1
        else:
            raise AssertionError(f"Unexpected encoding: 0x{result:03X}")

    assert upper_count == expected_upper, (
        f"width={random_width}: upper count {upper_count}, "
        f"expected {expected_upper}"
    )
    assert lower_count == limit - expected_upper


def run_self_tests():
    one = Fraction(1)
    positive_inexact = one + Fraction(1, 512)
    negative_inexact = -positive_inexact

    # Exact representable values must remain unchanged.
    assert stochastic_round(one, 0, 8) == 0x3E0
    assert stochastic_round(one, 255, 8) == 0x3E0
    assert stochastic_round(-one, 0, 8) == 0xBE0
    assert stochastic_round(-one, 255, 8) == 0xBE0

    # Positive inexact value: 1/16 of an ULP above +1.
    lo, hi, lo_bits, hi_bits = adjacent_values(positive_inexact)
    assert (lo, hi) == (Fraction(1), Fraction(33, 32))
    assert (lo_bits, hi_bits) == (0x3E0, 0x3E1)
    assert (positive_inexact - lo) / (hi - lo) == Fraction(1, 16)

    # Negative inexact value: 15/16 of the interval from -33/32 to -1.
    lo, hi, lo_bits, hi_bits = adjacent_values(negative_inexact)
    assert (lo, hi) == (Fraction(-33, 32), Fraction(-1))
    assert (lo_bits, hi_bits) == (0xBE1, 0xBE0)
    assert (negative_inexact - lo) / (hi - lo) == Fraction(15, 16)

    # Exhaustive checks for small widths; statistical enumeration for r=18.
    for width in (1, 2, 4, 8):
        check_probability(positive_inexact, width)
        check_probability(negative_inexact, width)

    # At r=18, enumerate all possible random integers for this example.
    # 2**18 outcomes is practical for a reference-model test.
    check_probability(positive_inexact, 18)
    check_probability(negative_inexact, 18)

    # Underflow policy: both signs flush to positive zero.
    assert stochastic_round(Fraction(1, 2**31), 0, 8) == 0x000
    assert stochastic_round(Fraction(-1, 2**31), 255, 8) == 0x000

    # Cancellation and signed decoding.
    assert decode_normal(0x3E0) == 1
    assert decode_normal(0xBE0) == -1
    assert decode_normal(0x3E0) + decode_normal(0xBE0) == 0

    # Range boundaries are explicitly represented.
    assert MIN_FINITE == MIN_NORMAL
    assert MAX_FINITE == Fraction(63, 32) * 2**31

    # Out-of-range values must not silently masquerade as normal values.
    try:
        adjacent_values(MAX_FINITE + Fraction(1))
    except OverflowError:
        pass
    else:
        raise AssertionError("Expected overflow-range exception")

    print("FP12 mathematical reference tests")
    print("Exact representable values: PASS")
    print("Positive and negative adjacent values: PASS")
    print("Probability checks at r=1,2,4,8,18: PASS")
    print("Underflow policy: PASS")
    print("Cancellation and signed decoding: PASS")
    print("Finite-range boundary checks: PASS")
    print("PASS: All reference tests passed.")


if __name__ == "__main__":
    run_self_tests()
