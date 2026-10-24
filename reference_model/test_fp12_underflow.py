
import random

from fp12_basics import decode_fp12_e6m5
from fp12_rounding import round_fp12


def main():
    random.seed(42)

    min_normal = 2.0 ** -30
    value = min_normal / 2
    trials = 1000

    zero_count = 0
    normal_count = 0

    for _ in range(trials):
        bits = round_fp12(value, "stochastic")
        decoded = decode_fp12_e6m5(bits)

        if decoded == 0.0:
            zero_count += 1
        elif decoded == min_normal:
            normal_count += 1
        else:
            print("Unexpected result:", decoded)
            return

    print("Stochastic Underflow Test")
    print("=" * 40)
    print(f"Input: {value:.12e}")
    print(f"Minimum normal: {min_normal:.12e}")
    print(f"Trials: {trials}")
    print(f"Rounded to zero: {zero_count}")
    print(f"Rounded to minimum normal: {normal_count}")
    print(f"Fraction rounded up: {normal_count / trials:.3f}")


if __name__ == "__main__":
    main()
