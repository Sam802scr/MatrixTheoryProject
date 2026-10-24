
import random


def stochastic_round(value, lower, upper):
    """Round to one of two neighboring representable values."""
    if not lower <= value <= upper:
        raise ValueError("Value must lie between lower and upper.")

    if lower == upper:
        return lower

    # Probability of choosing the lower value.
    p_lower = (upper - value) / (upper - lower)

    if random.random() < p_lower:
        return lower
    else:
        return upper


if __name__ == "__main__":
    exact_value = 1.3
    lower = 1.25
    upper = 1.375
    trials = 100_000

    lower_count = 0
    upper_count = 0

    for _ in range(trials):
        result = stochastic_round(exact_value, lower, upper)

        if result == lower:
            lower_count += 1
        else:
            upper_count += 1

    print("Exact value:", exact_value)
    print("Lower value:", lower)
    print("Upper value:", upper)
    print("Trials:", trials)
    print("Lower frequency:", lower_count / trials)
    print("Upper frequency:", upper_count / trials)

    average = (
        lower * lower_count + upper * upper_count
    ) / trials

    print("Average rounded value:", average)
