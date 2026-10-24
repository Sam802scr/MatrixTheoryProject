
import random

from fp12_rounding import round_fp12
from fp12_basics import decode_fp12_e6m5


def main():
    random.seed(42)

    test_values = [
        1.3,
        2.7,
        0.7,
        -1.3,
        -2.7,
        1.0,
        0.0,
    ]

    trials = 1000

    print("FP12 Rounding Validation")
    print("=" * 55)

    for value in test_values:
        errors = []

        for _ in range(trials):
            bits = round_fp12(value, "stochastic")
            rounded = decode_fp12_e6m5(bits)
            errors.append(rounded - value)

        mean_error = sum(errors) / trials
        mse = sum(error ** 2 for error in errors) / trials

        print(f"\nInput: {value}")
        print(f"Mean error: {mean_error:.6f}")
        print(f"MSE: {mse:.8f}")


if __name__ == "__main__":
    main()
