
import random
from functools import lru_cache
import math
from fp12_basics import decode_fp12_e6m5


@lru_cache(maxsize=1)
def positive_fp12_values():
    """Return positive finite E6M5 values with subnormals disabled."""
    values = []

    # Exponent zero is excluded: subnormals are disabled.
    # Exponents 1 through 62 are finite normal values.
    for exponent in range(1, 63):
        for fraction in range(32):
            bits = (exponent << 5) | fraction
            value = decode_fp12_e6m5(bits)
            values.append((value, bits))

    # Include zero as a representable value.
    values.append((0.0, 0))

    # Sort by numerical value.
    values.sort(key=lambda item: item[0])

    return values



def round_fp12(value, mode="nearest"):
    """Round a finite value to an E6M5 value."""
    if not math.isfinite(value):
        raise ValueError("This prototype accepts finite values only.")

    sign_bit = 0x800 if value < 0 else 0
    magnitude = abs(value)
    values = positive_fp12_values()

    if magnitude == 0:
        return sign_bit

    lower = None
    upper = None

    for candidate, bits in values:
        if candidate <= magnitude:
            lower = (candidate, bits)
        if candidate >= magnitude:
            upper = (candidate, bits)
            break

    if lower is None or upper is None:
        raise OverflowError("Value is outside the supported FP12 range.")

    if lower[0] == upper[0]:
        return sign_bit | lower[1]

    lo_value, lo_bits = lower
    hi_value, hi_bits = upper

    if mode == "nearest":
        if magnitude - lo_value <= hi_value - magnitude:
            chosen_bits = lo_bits
        else:
            chosen_bits = hi_bits

    elif mode == "stochastic":
        p_lower = (hi_value - magnitude) / (hi_value - lo_value)
        chosen_bits = (
            lo_bits if random.random() < p_lower else hi_bits
        )

    else:
        raise ValueError("mode must be 'nearest' or 'stochastic'")

    return sign_bit | chosen_bits




if __name__ == "__main__":
    random.seed(42)

    value = 1.3
    trials = 100_000

    nearest_bits = round_fp12(value, "nearest")
    nearest_value = decode_fp12_e6m5(nearest_bits)

    lower_value = max(
        decode_fp12_e6m5(bits)
        for bits in range(0x7E0)
        if 0 <= decode_fp12_e6m5(bits) < value
    )

    upper_value = min(
        decode_fp12_e6m5(bits)
        for bits in range(0x7E0)
        if decode_fp12_e6m5(bits) > value
    )

    lower_count = 0
    upper_count = 0
    total = 0.0

    for _ in range(trials):
        bits = round_fp12(value, "stochastic")
        result = decode_fp12_e6m5(bits)

        total += result

        if result == lower_value:
            lower_count += 1
        elif result == upper_value:
            upper_count += 1
        else:
            raise AssertionError("Unexpected rounded value!")

    print("Exact value:", value)
    print("Nearest FP12:", nearest_value)
    print("Lower neighbor:", lower_value)
    print("Upper neighbor:", upper_value)
    print("Trials:", trials)
    print("Lower frequency:", lower_count / trials)
    print("Upper frequency:", upper_count / trials)
    print("Stochastic average:", total / trials)
    print("Average error:", total / trials - value)

    assert abs(lower_count / trials - 0.4) < 0.01
    assert abs(upper_count / trials - 0.6) < 0.01

    print("Statistical checks passed!")
