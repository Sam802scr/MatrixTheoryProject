
import random
from fp8_basics import encode_fp8_e5m2
from fp12_basics import decode_fp12_e6m5
from fp12_alignment import encode_normal_fp12
from mac_model import mac_step

steps = 1000
trials = 100

# Encode 1.0 and 0.5 as FP8 E5M2.
one = encode_fp8_e5m2(1.0)
half = encode_fp8_e5m2(0.5)

exact_result = 1.0 + steps * 0.5

def run_experiment(mode):
    results = []

    for trial in range(trials):
        random.seed(trial)
        acc = encode_normal_fp12(1.0)

        for _ in range(steps):
            acc = mac_step(acc, one, half, mode=mode)

        results.append(decode_fp12_e6m5(acc))

    return results

nearest_results = run_experiment("nearest")
stochastic_results = run_experiment("stochastic")

print("Exact mathematical result:", exact_result)
print("Nearest mean:", sum(nearest_results) / trials)
print("Stochastic mean:", sum(stochastic_results) / trials)
print("Nearest range:", min(nearest_results), max(nearest_results))
print("Stochastic range:", min(stochastic_results), max(stochastic_results))
