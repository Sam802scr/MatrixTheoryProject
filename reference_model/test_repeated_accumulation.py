
import random
import statistics

from fp12_accumulator import accumulate_fp12
from fp12_basics import decode_fp12_e6m5
from fp12_alignment import encode_normal_fp12

trials = 1000
steps = 1000
product = 0.3
exact_sum = steps * product

# Deterministic nearest rounding
nearest_bits = encode_normal_fp12(0.0 + 1.0)

for _ in range(steps):
    nearest_bits = accumulate_fp12(
        nearest_bits, product, mode="nearest"
    )

nearest_result = decode_fp12_e6m5(nearest_bits)

# Repeat the stochastic experiment with different random sequences
stochastic_results = []

for seed in range(trials):
    random.seed(seed)
    acc_bits = encode_normal_fp12(1.0)

    for _ in range(steps):
        acc_bits = accumulate_fp12(
            acc_bits, product, mode="stochastic"
        )

    stochastic_results.append(decode_fp12_e6m5(acc_bits))

mean_stochastic = sum(stochastic_results) / trials

mean_signed_error = mean_stochastic - (1.0 + exact_sum)
std_dev = statistics.stdev(stochastic_results)

print("Mean signed error:", mean_signed_error)
print("Standard deviation:", std_dev)

print("Initial accumulator: 1.0")
print("Product per step:", product)
print("Accumulation steps:", steps)
print("Exact mathematical result:", 1.0 + exact_sum)
print("Nearest result:", nearest_result)
print("Nearest absolute error:", abs(nearest_result - (1.0 + exact_sum)))
print("Mean stochastic result:", mean_stochastic)
print("Mean stochastic absolute error:", abs(mean_stochastic - (1.0 + exact_sum)))
print("Stochastic result range:", min(stochastic_results), "to", max(stochastic_results))
