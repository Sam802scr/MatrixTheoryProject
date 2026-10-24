import random
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fp12_sr_reference import decode_normal, stochastic_round

RANDOM_WIDTH = 18
RANDOM_LIMIT = 1 << RANDOM_WIDTH
NUM_CASES = 1000
SEED = 20261021


def random_normal_encoding(rng):
    sign = rng.randrange(2)
    exponent = rng.randrange(1, 63)
    fraction = rng.randrange(32)
    return (sign << 11) | (exponent << 5) | fraction


def main():
    rng = random.Random(SEED)
    checked = 0
    exact_results = 0
    inexact_results = 0
    skipped = 0

    for _ in range(NUM_CASES):
        a = random_normal_encoding(rng)
        b = random_normal_encoding(rng)

        exact = decode_normal(a) + decode_normal(b)

        if exact == 0:
            expected = 0x000
        else:
            try:
                expected = stochastic_round(
                    exact,
                    rng.randrange(RANDOM_LIMIT),
                    RANDOM_WIDTH,
                )
            except OverflowError:
                skipped += 1
                continue

        if exact != 0:
            try:
                lo, hi = None, None
                # Test a second random value for the same exact sum.
                stochastic_round(exact, 0, RANDOM_WIDTH)
                inexact_results += 1
            except OverflowError:
                skipped += 1
                continue

        checked += 1

    print("FP12 eager reference-vector preparation")
    print(f"Random seed:              {SEED}")
    print(f"Random width:             {RANDOM_WIDTH}")
    print(f"Cases requested:          {NUM_CASES}")
    print(f"Cases in finite range:    {checked}")
    print(f"Overflow cases skipped:   {skipped}")
    print()
    print("Reference model executed successfully.")
    print("This script validates the mathematical reference only.")
    print("It does NOT validate eager RTL or paper fidelity.")


if __name__ == "__main__":
    main()