
import random

from fp12_rounding import round_fp12
from fp12_basics import decode_fp12_e6m5

value = 1.3
trials = 10000

# Deterministic nearest rounding
nearest_bits = round_fp12(value, mode="nearest")
nearest_value = decode_fp12_e6m5(nearest_bits)

# Stochastic rounding
random.seed(42)
stochastic_values = [
    decode_fp12_e6m5(round_fp12(value, mode="stochastic"))
    for _ in range(trials)
]

mean_stochastic = sum(stochastic_values) / trials

print("Input value:", value)
print("Number of trials:", trials)
print("Nearest rounded value:", nearest_value)
print("Stochastic mean:", mean_stochastic)
print("Nearest error:", nearest_value - value)
print("Stochastic mean error:", mean_stochastic - value)
print("Unique stochastic outputs:", sorted(set(stochastic_values)))
