
import random


def deterministic_round(value, lower, upper):
    """Round to the nearest representable value; ties go to lower."""
    if not lower <= value <= upper:
        raise ValueError("Value must lie between lower and upper.")

    if value - lower <= upper - value:
        return lower
    return upper


def stochastic_round(value, lower, upper):
    """Randomly round with probabilities based on distance."""
    if not lower <= value <= upper:
        raise ValueError("Value must lie between lower and upper.")

    if lower == upper:
        return lower

    p_lower = (upper - value) / (upper - lower)
    return lower if random.random() < p_lower else upper


if __name__ == "__main__":
    value = 1.3
    lower = 1.25
    upper = 1.375
    trials = 100_000

    deterministic_result = deterministic_round(value, lower, upper)

    stochastic_total = 0.0
    stochastic_squared_error = 0.0

    for _ in range(trials):
        result = stochastic_round(value, lower, upper)
        stochastic_total += result
        stochastic_squared_error += (result - value) ** 2

    stochastic_average = stochastic_total / trials
    stochastic_mse = stochastic_squared_error / trials

    print("Exact value:", value)
    print("Deterministic result:", deterministic_result)
    print("Deterministic error:", deterministic_result - value)
    print("Stochastic average:", stochastic_average)
    print("Stochastic average error:", stochastic_average - value)
    print("Stochastic mean squared error:", stochastic_mse)
