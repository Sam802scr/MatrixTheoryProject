
import random

# Threshold from our current RTL test
THRESHOLD = 8
NUM_TRIALS = 100_000

round_up_count = 0

for _ in range(NUM_TRIALS):
    random_bits = random.randrange(256)

    if random_bits < THRESHOLD:
        round_up_count += 1

observed_probability = round_up_count / NUM_TRIALS
expected_probability = THRESHOLD / 256

print("Stochastic Rounding Probability Test")
print("-----------------------------------")
print(f"Number of trials:       {NUM_TRIALS}")
print(f"Threshold:              {THRESHOLD}")
print(f"Expected probability:   {expected_probability:.4%}")
print(f"Observed probability:   {observed_probability:.4%}")
print(f"Number of round-ups:    {round_up_count}")
