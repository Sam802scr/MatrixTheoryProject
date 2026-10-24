
import random
from fp12_rounding import round_fp12
from fp12_basics import decode_fp12_e6m5


def evaluate(value, mode, trials):
    errors = []

    for _ in range(trials):
        bits = round_fp12(value, mode)
        rounded = decode_fp12_e6m5(bits)
        errors.append(rounded - value)

    mean_error = sum(errors) / trials
    mse = sum(error * error for error in errors) / trials

    return mean_error, mse


if __name__ == "__main__":
    random.seed(42)

    value = 1.3
    trials = 1_000

    det_bias, det_mse = evaluate(value, "nearest", trials)
    sr_bias, sr_mse = evaluate(value, "stochastic", trials)

    print("Exact value:", value)
    print("Trials:", trials)
    print()
    print("Deterministic nearest rounding")
    print("Mean error:", det_bias)
    print("MSE:", det_mse)
    print()
    print("Stochastic rounding")
    print("Mean error:", sr_bias)
    print("MSE:", sr_mse)
